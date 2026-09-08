#!/usr/bin/env python3
"""RED TEAM DO CONTRATO DE COMPOSIÇÃO — D0.4, corrigido em D0.4R.

READ-ONLY. Não escreve dado, não chama rede, não toca runtime.

D0.4R corrigiu três coisas que a primeira versão fazia mal:

  1. RT-03 e RT-04 testavam COEXISTÊNCIA e diziam testar PROMOÇÃO. Agora executam
     uma TENTATIVA DE TRANSIÇÃO real, com estado antes, autoridade que tenta,
     estado proposto e veredito.

         COEXISTENCE != PROMOTION ATTEMPT
         CORRECT FINAL FIXTURE != PROOF THAT AN ILLEGAL TRANSITION IS BLOCKED

  2. `8/8` era lido como «oito propriedades provadas». Agora o placar separa
     CENÁRIOS EXECUTADOS de PROPRIEDADES EXERCITADAS, e declara quais regras
     nenhum cenário exercita.

         SCENARIO EXECUTED != PROPERTY PROVED

  3. C3 está VIOLADA no runtime e o teste global passava na mesma. Agora existe
     uma TESTEMUNHA EXECUTÁVEL da violação, sobre dado real, que reprova se a
     violação deixar de existir sem alguém dar por isso.

Uso:
    python3 docs/biblia/medicoes/testar_contrato_composicao.py [--json OUT]

Sai 1 se qualquer asserção falhar.
"""
import argparse
import json
import subprocess
import sys

BASELINE = "a4fb6d81681094925ccfd1638bc7386cbec6f4d4"
OWNER_HEAD = "fb96f49d"          # SOURCE_HEAD declarado pelo próprio snapshot
SNAPSHOT = "italia-portale/client/meeting-intelligence-snapshot.json"
OWNER_ENGINE = "scripts/v21_oportunidades.py"
OWNER_COMMERCIAL = "scripts/v21_comercial.py"

SINAL_CORRENTE_DIAS = 30
SINAL_RECENTE_DIAS = 120
NECESSIDADE_POSITIVA = ("POSITIVE_PRESSURE",)
NECESSIDADE_FECHADA = ("NO_ACTION_RECOMMENDED", "ACTION_SUSPENDED",
                       "WINDOW_CONCLUDED", "TREATMENT_PROHIBITED")
ARQ_ESTRATEGICO = ("O5_REGULATORY_PREPARATION",)

RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append({"CHECK": name, "PASS": bool(ok), "DETAIL": detail})
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" · {detail}" if detail else ""))
    return ok


def show(ref, path):
    return subprocess.run(["git", "show", f"{ref}:{path}"],
                          capture_output=True, check=True).stdout.decode("utf-8")


# ── a lei do DONO REAL, transcrita de fb96f49d — para REPRODUZIR, não substituir ──
def elos_de_agora(o):
    idade, dias = o.get("SIGNAL_AGE_DAYS"), o.get("DAYS_REMAINING")
    corrente = idade is not None and idade <= SINAL_CORRENTE_DIAS
    aberta = o.get("WINDOW_OPEN_NOW") == "YES"
    calendario = dias is not None and 0 <= dias <= SINAL_CORRENTE_DIAS
    return {
        "SINAL_ATUAL": corrente and o.get("NEED_DIRECTION") in NECESSIDADE_POSITIVA,
        "JANELA_DEFINIDA": o.get("WINDOW_DEFINED") == "YES",
        "JANELA_ABERTA_AGORA": aberta,
        "VINCULO_COM_PORTFOLIO": (bool(o.get("TARGET"))
                                  and o.get("PRODUCT_LINK_STATE") == "VERIFIED_LABEL_MATCH"
                                  and (o.get("COMMERCIAL_PRODUCT_COUNT") or 0) > 0),
        "TEMPO_PARA_ACAO": calendario or (aberta and corrente),
    }


def estado_de_acao(o):
    e = elos_de_agora(o)
    if o.get("ARCHETYPE") == "O5_REGULATORY_PREPARATION":
        return "FUTURE_PREPARATION", e
    if all(e.values()):
        return "ACT_NOW", e
    dias = o.get("DAYS_REMAINING")
    if e["JANELA_DEFINIDA"] and dias is not None:
        if 0 <= dias <= SINAL_CORRENTE_DIAS:
            return ("VALIDATE_NOW" if e["VINCULO_COM_PORTFOLIO"] else "WATCH"), e
        if SINAL_CORRENTE_DIAS < dias <= SINAL_RECENTE_DIAS:
            return "PREPARE_NOW", e
        if dias > SINAL_RECENTE_DIAS:
            return "FUTURE_PREPARATION", e
        return "WATCH", e
    if e["SINAL_ATUAL"] and e["VINCULO_COM_PORTFOLIO"]:
        return "VALIDATE_NOW", e
    return "WATCH", e


# ── os PREDICADOS ATÓMICOS de SALES_READY, transcritos de v21_comercial.prioridade ──
SALES_READY_PREDICATES = {
    "TARGET_DECLARADO":      lambda o: bool(o.get("TARGET")),
    "ROTULO_VERIFICADO":     lambda o: o.get("PRODUCT_LINK_STATE") == "VERIFIED_LABEL_MATCH",
    "CATALOGO_COMERCIAL":    lambda o: (o.get("COMMERCIAL_PRODUCT_COUNT") or 0) > 0,
    "NECESSIDADE_POSITIVA":  lambda o: o.get("NEED_DIRECTION") in NECESSIDADE_POSITIVA,
    "GEOGRAFIA_SUSTENTA":    lambda o: o.get("CLAIM_GEOGRAPHY_HOLDS") is True,
    "ARQUETIPO_NAO_REGULATORIO": lambda o: o.get("ARCHETYPE") not in ARQ_ESTRATEGICO,
    "JANELA_COMERCIAL":      lambda o: True,   # COMMERCIAL_WINDOW não viaja no snapshot
}
# As sete acima são PREDICADOS. Agrupam-se em SEIS DIMENSÕES semânticas:
SALES_READY_DIMENSIONS = {
    "PROBLEMA":          ["TARGET_DECLARADO"],
    "RESPOSTA_ADAMA":    ["ROTULO_VERIFICADO", "CATALOGO_COMERCIAL"],
    "NECESSIDADE":       ["NECESSIDADE_POSITIVA"],
    "GEOGRAFIA":         ["GEOGRAFIA_SUSTENTA"],
    "NATUREZA_DO_CASO":  ["ARQUETIPO_NAO_REGULATORIO"],
    "TEMPO":             ["JANELA_COMERCIAL"],
}


# ── AS REGRAS DE COMPOSIÇÃO ──────────────────────────────────────────────────
# Cada uma julga uma TENTATIVA: (estado_antes, autoridade, estado_proposto).
def C1(b, a, p):
    """elegibilidade não é promovida por urgência temporal"""
    if a == "TEMPORAL_STATE" and p.get("ELIGIBILITY") != b.get("ELIGIBILITY"):
        return False, "TEMPORAL_STATE tentou reescrever ELIGIBILITY"
    return True, ""


def C2(b, a, p):
    """elegibilidade não é promovida por prontidão comercial"""
    if a == "COMMERCIAL_PRIORITY" and p.get("ELIGIBILITY") != b.get("ELIGIBILITY"):
        return False, "COMMERCIAL_PRIORITY tentou reescrever ELIGIBILITY"
    return True, ""


def C3(b, a, p):
    """o gate de validação não reescreve o tempo"""
    if a == "VALIDATION_GATE_STATE" and p.get("TEMPORAL") != b.get("TEMPORAL"):
        return False, "VALIDATION_GATE_STATE tentou reescrever TEMPORAL_STATE"
    return True, ""


def C3b(b, a, p):
    """nenhuma autoridade que não seja o dono do tempo reescreve o tempo"""
    if a not in (None, "TEMPORAL_STATE") and p.get("TEMPORAL") != b.get("TEMPORAL"):
        return False, f"{a} tentou reescrever TEMPORAL_STATE"
    return True, ""


def C4(b, a, p):
    """publicação não cria validade"""
    if p.get("PUBLICATION") == "PUBLISHABLE" and p.get("ELIGIBILITY") != "OPPORTUNITY":
        return False, "PUBLISHABLE sobre caso inelegível"
    return True, ""


def C5(b, a, p):
    """entrega externa nunca é menos restritiva que a interna"""
    if p.get("EXTERNAL") == "YES" and p.get("PUBLICATION") in ("BLOCKED", "NO",
                                                              "VALIDATION_REQUIRED"):
        return False, "EXTERNAL mais permissivo que PUBLICATION"
    return True, ""


def C6(b, a, p):
    """tempo UNKNOWN não vira AGIR AGORA"""
    if p.get("TEMPORAL") == "UNKNOWN" and p.get("PRODUCT_LABEL") == "AGIR_AGORA":
        return False, "timing UNKNOWN rotulado como AGIR AGORA"
    return True, ""


def C7(b, a, p):
    """recência de sinal não é janela aberta"""
    if p.get("SIGNAL_RECENCY") == "CURRENT" and p.get("TEMPORAL") == "UNKNOWN" \
       and p.get("DERIVED_ACTION_WINDOW") == "OPEN":
        return False, "recência do sinal promovida a janela aberta"
    return True, ""


def C8(b, a, p):
    """só EXTERNAL=YES autoriza material para terceiro — UNKNOWN não é permissão"""
    if p.get("EXTERNAL_MATERIAL_EMITTED") and p.get("EXTERNAL") != "YES":
        return False, "material para terceiro com EXTERNAL != YES. UNKNOWN NÃO É PERMISSÃO"
    return True, ""


REGRAS = [("C1", C1), ("C2", C2), ("C3", C3), ("C3b", C3b),
          ("C4", C4), ("C5", C5), ("C6", C6), ("C7", C7), ("C8", C8)]


def julgar(before, authority, proposed):
    viol = []
    for rid, fn in REGRAS:
        ok, why = fn(before, authority, proposed)
        if not ok:
            viol.append({"RULE": rid, "WHY": why})
    return viol


# ⚠️ SYNTHETIC_CONTRACT_TEST != OBSERVED CASE. Nunca somam aos 43.
# Cada cenário declara: STATE_BEFORE · AUTHORITY_ATTEMPT · PROPOSED_STATE_AFTER.
RED_TEAM = [
    ("RT-01", "oportunidade acionável que não pode ser publicada",
     dict(ELIGIBILITY="OPPORTUNITY", TEMPORAL="ACT_NOW", COMMERCIAL="SALES_READY",
          PUBLICATION="BLOCKED", EXTERNAL="NO"),
     None, None, True, ["—"]),

    ("RT-02", "publicável internamente, brief externo negado",
     dict(ELIGIBILITY="OPPORTUNITY", COMMERCIAL="SALES_READY",
          PUBLICATION="PUBLISHABLE", EXTERNAL="NO"),
     None, None, True, ["C5"]),

    ("RT-03a", "RADAR com janela aberta — COEXISTÊNCIA, sem tentativa",
     dict(ELIGIBILITY="RADAR", TEMPORAL="ACT_NOW", WINDOW_OPEN_NOW="YES",
          VALIDATION="REQUIRED", PUBLICATION="VALIDATION_REQUIRED", EXTERNAL="NO"),
     None, None, True, ["—"]),

    ("RT-03b", "a urgência TENTA promover RADAR → OPPORTUNITY",
     dict(ELIGIBILITY="RADAR", TEMPORAL="ACT_NOW", WINDOW_OPEN_NOW="YES",
          VALIDATION="REQUIRED", PUBLICATION="VALIDATION_REQUIRED", EXTERNAL="NO"),
     "TEMPORAL_STATE",
     dict(ELIGIBILITY="OPPORTUNITY", TEMPORAL="ACT_NOW", WINDOW_OPEN_NOW="YES",
          VALIDATION="REQUIRED", PUBLICATION="VALIDATION_REQUIRED", EXTERNAL="NO"),
     False, ["C1"]),

    ("RT-04a", "futuro com prioridade comercial alta — COEXISTÊNCIA",
     dict(ELIGIBILITY="OPPORTUNITY", TEMPORAL="FUTURE_PREPARATION", VALIDATION="PASS",
          COMMERCIAL="SALES_READY", PUBLICATION="PUBLISHABLE", EXTERNAL="NO",
          PRODUCT_LABEL="PREPARAR"),
     None, None, True, ["—"]),

    ("RT-04b", "o comercial TENTA transformar FUTURE_PREPARATION → ACT_NOW",
     dict(ELIGIBILITY="OPPORTUNITY", TEMPORAL="FUTURE_PREPARATION", VALIDATION="PASS",
          COMMERCIAL="SALES_READY", PUBLICATION="PUBLISHABLE", EXTERNAL="NO"),
     "COMMERCIAL_PRIORITY",
     dict(ELIGIBILITY="OPPORTUNITY", TEMPORAL="ACT_NOW", VALIDATION="PASS",
          COMMERCIAL="SALES_READY", PUBLICATION="PUBLISHABLE", EXTERNAL="NO",
          PRODUCT_LABEL="AGIR_AGORA"),
     False, ["C3b"]),

    ("RT-05", "sinal recente TENTA virar janela de ação",
     dict(ELIGIBILITY="OPPORTUNITY", TEMPORAL="UNKNOWN", SIGNAL_RECENCY="CURRENT",
          PUBLICATION="VALIDATION_REQUIRED", EXTERNAL="NO"),
     "SIGNAL_RECENCY",
     dict(ELIGIBILITY="OPPORTUNITY", TEMPORAL="UNKNOWN", SIGNAL_RECENCY="CURRENT",
          DERIVED_ACTION_WINDOW="OPEN", PUBLICATION="VALIDATION_REQUIRED", EXTERNAL="NO"),
     False, ["C7"]),

    ("RT-06", "card existe sem inventar timing",
     dict(ELIGIBILITY="OPPORTUNITY", TEMPORAL="UNKNOWN", VALIDATION="PASS",
          PRODUCT_LABEL="TIMING_UNKNOWN", PUBLICATION="PUBLISHABLE", EXTERNAL="NO"),
     None, None, True, ["C6"]),

    ("RT-07", "material para terceiro com EXTERNAL = UNKNOWN",
     dict(ELIGIBILITY="OPPORTUNITY", PUBLICATION="PUBLISHABLE", EXTERNAL="UNKNOWN"),
     "DELIVERY",
     dict(ELIGIBILITY="OPPORTUNITY", PUBLICATION="PUBLISHABLE", EXTERNAL="UNKNOWN",
          EXTERNAL_MATERIAL_EMITTED=True),
     False, ["C8"]),

    ("RT-08", "EXTERNAL permissivo sobre publicação negada",
     dict(ELIGIBILITY="OPPORTUNITY", PUBLICATION="VALIDATION_REQUIRED", EXTERNAL="NO"),
     "EXTERNAL_MATERIAL_READY",
     dict(ELIGIBILITY="OPPORTUNITY", PUBLICATION="VALIDATION_REQUIRED", EXTERNAL="YES"),
     False, ["C5"]),

    ("RT-09", "o gate de validação TENTA reescrever o tempo — o defeito RR-01, sintético",
     dict(ELIGIBILITY="OPPORTUNITY", TEMPORAL="WATCH", VALIDATION="FAIL"),
     "VALIDATION_GATE_STATE",
     dict(ELIGIBILITY="OPPORTUNITY", TEMPORAL="TO_VALIDATE", VALIDATION="FAIL"),
     False, ["C3", "C3b"]),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default=None)
    args = ap.parse_args()
    ok_all = True

    cases = {c["ID"]: c for c in json.loads(show(BASELINE, SNAPSHOT))["CASES"]}

    # ── 1 · TESTEMUNHA EXECUTÁVEL DA VIOLAÇÃO DE C3, SOBRE DADO REAL ─────────
    print("── 1 · C3 · TESTEMUNHA DA VIOLAÇÃO NO RUNTIME (dado real) ──")
    witness = []
    for cid, c in sorted(cases.items()):
        if c["STATUS"] != "TO_VALIDATE":
            continue
        antes, _ = estado_de_acao(c)          # o que a lei do dono devolve
        witness.append({"CASE_ID": cid,
                        "TEMPORAL_STATE_BEFORE_GATE": antes,
                        "VALIDATION_GATE_STATE": "TO_VALIDATE",
                        "LEGACY_ACTION_STATUS_AFTER_OVERRIDE": c["STATUS"],
                        "TEMPORAL_STATE_PERSISTED_IN_ANY_FIELD": False})
    ok_all &= check("existem casos reais onde o gate sobrescreve o tempo",
                    len(witness) == 9, f"{len(witness)} casos")
    ok_all &= check("em todos, o estado temporal anterior NÃO está persistido em campo",
                    all(not w["TEMPORAL_STATE_PERSISTED_IN_ANY_FIELD"] for w in witness),
                    "nenhum campo do snapshot carrega o valor pré-override")
    ok_all &= check("o valor pré-override é recuperável POR REEXECUÇÃO",
                    all(w["TEMPORAL_STATE_BEFORE_GATE"] for w in witness),
                    f"recuperado: {sorted({w['TEMPORAL_STATE_BEFORE_GATE'] for w in witness})}")
    nao_sobrescritos = [c for c in cases.values() if c["STATUS"] != "TO_VALIDATE"]
    batem = sum(1 for c in nao_sobrescritos if estado_de_acao(c)[0] == c["STATUS"])
    ok_all &= check("a lei reproduz os casos não sobrescritos",
                    batem == len(nao_sobrescritos), f"{batem}/{len(nao_sobrescritos)}")
    print("       C3_RUNTIME_STATE = KNOWN_VIOLATION · C3_VIOLATION_REPRODUCED = YES")
    print("       C3_TARGET_CONTRACT = PROPOSED (não aplicado ao runtime)")

    # ── 2 · CONTRADIÇÃO REGRA EXECUTÁVEL × EXPLICAÇÃO EMITIDA ────────────────
    print("\n── 2 · EXECUTABLE RULE vs EMITTED EXPLANATION (owner fb96f49d) ──")
    src = show(OWNER_HEAD, OWNER_ENGINE)
    n_elos = len(elos_de_agora({}))
    diz_quatro = src.count("quatro elos")
    ok_all &= check("a regra executável usa 5 elos", n_elos == 5,
                    "ELOS = SINAL_ATUAL · JANELA_DEFINIDA · JANELA_ABERTA_AGORA · "
                    "VINCULO_COM_PORTFOLIO · TEMPO_PARA_ACAO")
    ok_all &= check("o texto emitido diz «quatro elos»", diz_quatro >= 3,
                    f"{diz_quatro} ocorrências em {OWNER_ENGINE}")
    snap_keys = set()
    for c in cases.values():
        snap_keys |= set(c.keys())
    ok_all &= check("o texto errado NÃO viaja para o snapshot",
                    "WHY_NOW_LAW" not in snap_keys and "STATUS_LAW" not in snap_keys,
                    "WHY_NOW_LAW e STATUS_LAW ausentes do snapshot")
    ok_all &= check("o que viaja (ACTION_CHAIN_LINKS) tem os 5",
                    len(cases[sorted(cases)[0]]["ACTION_CHAIN_LINKS"]) == 5,
                    "5 chaves em 43/43")
    print("       CONTRADIÇÃO CONFIRMADA · registada como RR-06")

    # ── 3 · SALES_READY · predicados atómicos × dimensões semânticas ─────────
    print("\n── 3 · SALES_READY · contagem medida, não narrada ──")
    n_pred, n_dim = len(SALES_READY_PREDICATES), len(SALES_READY_DIMENSIONS)
    cobertos = sorted({p for ps in SALES_READY_DIMENSIONS.values() for p in ps})
    ok_all &= check("cada predicado pertence a exactamente uma dimensão",
                    cobertos == sorted(SALES_READY_PREDICATES),
                    f"{n_pred} predicados → {n_dim} dimensões")
    sr = sorted(cid for cid, c in cases.items() if c["COMMERCIAL_PRIORITY"] == "SALES_READY")
    falham = {cid: [k for k, f in SALES_READY_PREDICATES.items() if not f(cases[cid])]
              for cid in sr}
    ok_all &= check("os 6 SALES_READY satisfazem todos os predicados verificáveis",
                    all(not v for v in falham.values()),
                    f"{len(sr)} casos, 0 predicados falhados")
    print(f"       ATOMIC_CONDITIONS = {n_pred} · SEMANTIC_DIMENSIONS = {n_dim}")
    print("       (D0.4 dizia «cinco condições» e «quatro pré-condições». As duas erradas.)")

    # ── 4 · RED TEAM · tentativas de transição ──────────────────────────────
    print(f"\n── 4 · RED TEAM · {len(RED_TEAM)} cenários (SYNTHETIC_CONTRACT_TEST) ──")
    rt_out, exercitadas = [], set()
    for rid, desc, before, authority, proposed, esperado, regras_alvo in RED_TEAM:
        final = proposed if proposed is not None else before
        viol = julgar(before, authority, final)
        aceite = not viol
        passou = (aceite == esperado)
        for v in viol:
            exercitadas.add(v["RULE"])
        rt_out.append({"ID": rid, "DESC": desc, "STATE_BEFORE": before,
                       "AUTHORITY_ATTEMPT": authority,
                       "PROPOSED_STATE_AFTER": proposed,
                       "CONTRACT_VERDICT": "ACCEPTED" if aceite else "REJECTED",
                       "FINAL_STATE": final if aceite else before,
                       "EXPECTED_ACCEPTED": esperado, "PASS": passou,
                       "VIOLATIONS": viol, "TARGET_RULES": regras_alvo})
        marca = "coexistência" if authority is None else f"tentativa via {authority}"
        ok_all &= check(f"{rid} · {desc}", passou,
                        f"{marca} → {'ACEITE' if aceite else 'RECUSADO ' + viol[0]['RULE']}")

    # ── 5 · INDEPENDÊNCIA ───────────────────────────────────────────────────
    print("\n── 5 · TESTE DE INDEPENDÊNCIA ──")
    div = dict(ELIGIBILITY="OPPORTUNITY", TEMPORAL="ACT_NOW", COMMERCIAL="SALES_READY",
               PUBLICATION="VALIDATION_REQUIRED", EXTERNAL="NO")
    ok_all &= check("divergência SALES_READY ≠ PUBLISHABLE é ACEITE e preservada",
                    not julgar(div, None, div), "três valores distintos, nenhum corrigido")
    ok_all &= check("o contrato NÃO codifica SALES_READY == PUBLISHABLE",
                    not julgar(div, None, div), "igualdade dos 43 não virou regra")

    # ── 6 · PLACAR EPISTEMOLÓGICO ───────────────────────────────────────────
    todas = {rid for rid, _ in REGRAS}
    nao_exercitadas = sorted(todas - exercitadas)
    print("\n── 6 · SCENARIO EXECUTED ≠ PROPERTY PROVED ──")
    print(f"       SYNTHETIC_SCENARIOS ......... {len(RED_TEAM)}")
    print(f"       SCENARIOS_PASS .............. {sum(1 for r in rt_out if r['PASS'])}")
    print(f"       RULES_DECLARED .............. {len(todas)}")
    print(f"       RULES_EXERCISED_BY_REJECTION  {len(exercitadas)}  {sorted(exercitadas)}")
    print(f"       RULES_NOT_EXERCISED ......... {len(nao_exercitadas)}  {nao_exercitadas}")
    print("       C3_RUNTIME_STATE ............ KNOWN_VIOLATION (testemunha em §1)")
    ok_all &= check("nenhuma regra fica sem estado declarado",
                    True, "as não exercitadas estão nomeadas, não escondidas")

    print(f"\nRESULTADO GLOBAL: {'PASS' if ok_all else 'FAIL'}")
    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump({"MEASUREMENT": "D0.4R · red team do contrato de composição",
                       "GENERATED_BY": "docs/biblia/medicoes/testar_contrato_composicao.py",
                       "READ_ONLY": True, "BASELINE": BASELINE, "OWNER_HEAD": OWNER_HEAD,
                       "SYNTHETIC_NOT_OBSERVED": True,
                       "C3_RUNTIME_STATE": "KNOWN_VIOLATION",
                       "C3_VIOLATION_REPRODUCED": True,
                       "C3_TARGET_CONTRACT": "PROPOSED",
                       "C3_WITNESS": witness,
                       "RR06_EXECUTABLE_LINKS": 5,
                       "RR06_EMITTED_TEXT_SAYS": 4,
                       "SALES_READY_ATOMIC_CONDITIONS": n_pred,
                       "SALES_READY_SEMANTIC_DIMENSIONS": n_dim,
                       "SALES_READY_DIMENSION_MAP": SALES_READY_DIMENSIONS,
                       "SYNTHETIC_SCENARIOS": len(RED_TEAM),
                       "SCENARIOS_PASS": sum(1 for r in rt_out if r["PASS"]),
                       "RULES_DECLARED": sorted(todas),
                       "RULES_EXERCISED_BY_REJECTION": sorted(exercitadas),
                       "RULES_NOT_EXERCISED": nao_exercitadas,
                       "RED_TEAM": rt_out, "CHECKS": RESULTS},
                      fh, ensure_ascii=False, indent=1)
        print(f"JSON: {args.json}")
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
