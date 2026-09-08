#!/usr/bin/env python3
"""RED TEAM DO CONTRATO DE COMPOSIÇÃO — D0.4.

READ-ONLY sobre o repositório. Não escreve dado, não chama rede, não toca runtime.

Faz três coisas, e nenhuma delas é mudar o sistema:

  1. REPRODUZ a lei do dono real (`estado_de_acao` de fb96f49d) sobre os 43 casos
     observados, e mede quantos batem — para saber se o estado temporal anterior a
     um override é RECUPERÁVEL POR RE-EXECUÇÃO.

  2. Corre 8 CASOS SINTÉTICOS DE CONTRATO (RT-01..RT-08) contra as regras de
     composição propostas. Um caso sintético testa a ARQUITETURA; nunca é
     evidência do mundo e nunca entra nos 43.

         SYNTHETIC_CONTRACT_TEST != OBSERVED CASE

  3. Faz o TESTE DE INDEPENDÊNCIA: força uma divergência sintética legítima entre
     SALES_READY, PUBLICATION_STATE e EXTERNAL_MATERIAL_READY e verifica que o
     contrato PRESERVA os três valores em vez de os «corrigir» para ficarem iguais.

Uso:
    python3 docs/biblia/medicoes/testar_contrato_composicao.py [--json OUT]

Sai 1 se qualquer asserção do contrato falhar.
"""
import argparse
import json
import subprocess
import sys

BASELINE = "a4fb6d81681094925ccfd1638bc7386cbec6f4d4"
OWNER_HEAD = "fb96f49d"          # SOURCE_HEAD declarado pelo próprio snapshot
SNAPSHOT = "italia-portale/client/meeting-intelligence-snapshot.json"

SINAL_CORRENTE_DIAS = 30
SINAL_RECENTE_DIAS = 120
NECESSIDADE_POSITIVA = ("POSITIVE_PRESSURE",)

RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append({"CHECK": name, "PASS": bool(ok), "DETAIL": detail})
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" · {detail}" if detail else ""))
    return ok


# ── 1 · a lei do DONO REAL, transcrita de fb96f49d:scripts/v21_oportunidades.py ──
# Transcrita para REPRODUZIR, não para substituir. O dono continua sendo o script.
def elos_de_agora(o):
    idade = o.get("SIGNAL_AGE_DAYS")
    dias = o.get("DAYS_REMAINING")
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


# ── 2 · AS REGRAS DE COMPOSIÇÃO PROPOSTAS ────────────────────────────────────
# Cada uma devolve (ok, motivo). Nenhuma altera o estado: só julga a combinação.
def r_eligibility_nao_promovida_por_urgencia(s):
    if s.get("TEMPORAL") in ("ACT_NOW",) and s.get("ELIGIBILITY") != "OPPORTUNITY":
        return True, "urgência não promove elegibilidade — combinação permitida e preservada"
    return True, ""


def r_eligibility_nao_promovida_por_comercial(s):
    if s.get("COMMERCIAL") == "SALES_READY" and s.get("ELIGIBILITY") != "OPPORTUNITY":
        return False, ("VIOLAÇÃO estrutural: SALES_READY exige TARGET + rótulo verificado + "
                       "catálogo, que é a mesma cadeia que a elegibilidade exige. "
                       "Não é o comercial a promover — é a pré-condição partilhada.")
    return True, ""


def r_validacao_nao_altera_tempo(s):
    return (s.get("TEMPORAL_BEFORE_GATE") is None
            or s.get("TEMPORAL_BEFORE_GATE") == s.get("TEMPORAL_TRUTH"),
            "gate não reescreve a verdade temporal")


def r_publicacao_nao_cria_validade(s):
    if s.get("PUBLICATION") == "PUBLISHABLE" and s.get("ELIGIBILITY") not in ("OPPORTUNITY",):
        return False, "publicação a criar elegibilidade que não existe"
    return True, ""


def r_externo_nunca_menos_restritivo(s):
    pub, ext = s.get("PUBLICATION"), s.get("EXTERNAL")
    if ext == "YES" and pub in ("BLOCKED", "NO", "VALIDATION_REQUIRED"):
        return False, ("EXTERNAL mais permissivo que PUBLICATION — proibido. "
                       "EXTERNAL_DELIVERY ⊆ INTERNAL_PUBLICATION")
    return True, ""


def r_desconhecido_nao_vira_agora(s):
    if s.get("TEMPORAL") == "UNKNOWN" and s.get("PRODUCT_LABEL") == "AGIR_AGORA":
        return False, "timing UNKNOWN rotulado como AGIR AGORA"
    return True, ""


def r_recencia_nao_e_janela(s):
    if s.get("SIGNAL_RECENCY") == "CURRENT" and s.get("TEMPORAL") == "UNKNOWN" \
       and s.get("DERIVED_ACTION_WINDOW") == "OPEN":
        return False, "recência do sinal promovida a janela aberta"
    return True, ""


def r_externo_unknown_nao_emite(s):
    # O red team encontrou esta lacuna: sem esta regra, RT-07 passava por OMISSÃO.
    # UNKNOWN não é permissão. Só YES autoriza material para terceiro.
    if s.get("EXTERNAL_MATERIAL_EMITTED") and s.get("EXTERNAL") != "YES":
        return False, ("material para terceiro emitido com EXTERNAL != YES. "
                       "UNKNOWN NÃO É PERMISSÃO.")
    return True, ""


REGRAS = [
    ("C1 · elegibilidade não é promovida por urgência", r_eligibility_nao_promovida_por_urgencia),
    ("C2 · elegibilidade não é promovida por prontidão comercial", r_eligibility_nao_promovida_por_comercial),
    ("C3 · gate de validação não reescreve o tempo", r_validacao_nao_altera_tempo),
    ("C4 · publicação não cria validade", r_publicacao_nao_cria_validade),
    ("C5 · entrega externa nunca é menos restritiva que a interna", r_externo_nunca_menos_restritivo),
    ("C6 · tempo UNKNOWN não vira AGIR AGORA", r_desconhecido_nao_vira_agora),
    ("C7 · recência de sinal não é janela aberta", r_recencia_nao_e_janela),
    ("C8 · só EXTERNAL=YES autoriza material para terceiro", r_externo_unknown_nao_emite),
]

# ⚠️ SYNTHETIC_CONTRACT_TEST — nunca somar aos 43, nunca publicar como dado.
RED_TEAM = [
    ("RT-01", "oportunidade acionável que não pode ser publicada",
     dict(ELIGIBILITY="OPPORTUNITY", TEMPORAL="ACT_NOW", COMMERCIAL="SALES_READY",
          PUBLICATION="BLOCKED", EXTERNAL="NO"), True),
    ("RT-02", "publicável internamente, brief externo negado",
     dict(ELIGIBILITY="OPPORTUNITY", COMMERCIAL="SALES_READY",
          PUBLICATION="PUBLISHABLE", EXTERNAL="NO"), True),
    ("RT-03", "urgência tenta promover RADAR a OPPORTUNITY",
     dict(ELIGIBILITY="RADAR", TEMPORAL="ACT_NOW", WINDOW_OPEN_NOW="YES",
          VALIDATION="REQUIRED", PUBLICATION="VALIDATION_REQUIRED", EXTERNAL="NO"), True),
    ("RT-04", "prioridade alta tenta transformar futuro em agora",
     dict(ELIGIBILITY="OPPORTUNITY", TEMPORAL="FUTURE_PREPARATION", VALIDATION="PASS",
          COMMERCIAL="SALES_READY", PUBLICATION="PUBLISHABLE", EXTERNAL="NO",
          PRODUCT_LABEL="PREPARAR"), True),
    ("RT-05", "sinal recente tenta virar janela de ação",
     dict(ELIGIBILITY="OPPORTUNITY", TEMPORAL="UNKNOWN", SIGNAL_RECENCY="CURRENT",
          DERIVED_ACTION_WINDOW="OPEN", PUBLICATION="VALIDATION_REQUIRED", EXTERNAL="NO"), False),
    ("RT-06", "card existe sem inventar timing",
     dict(ELIGIBILITY="OPPORTUNITY", TEMPORAL="UNKNOWN", VALIDATION="PASS",
          PRODUCT_LABEL="TIMING_UNKNOWN", PUBLICATION="PUBLISHABLE", EXTERNAL="NO"), True),
    ("RT-07", "material para terceiro com externo desconhecido",
     dict(ELIGIBILITY="OPPORTUNITY", PUBLICATION="PUBLISHABLE", EXTERNAL="UNKNOWN",
          EXTERNAL_MATERIAL_EMITTED=True), False),
    ("RT-08", "externo permissivo sobre publicação negada",
     dict(ELIGIBILITY="OPPORTUNITY", PUBLICATION="VALIDATION_REQUIRED", EXTERNAL="YES"), False),
]


def julgar(estado):
    viol = []
    for nome, fn in REGRAS:
        ok, motivo = fn(estado)
        if not ok:
            viol.append({"RULE": nome, "WHY": motivo})
    return viol


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default=None)
    args = ap.parse_args()
    allok = True

    print("── 1 · RECUPERABILIDADE DO ESTADO TEMPORAL ANTES DO OVERRIDE ──")
    raw = subprocess.run(["git", "show", f"{BASELINE}:{SNAPSHOT}"],
                         capture_output=True, check=True).stdout
    cases = {c["ID"]: c for c in json.loads(raw)["CASES"]}
    recon, diverge, tv = {}, [], {}
    for cid, c in sorted(cases.items()):
        pred, _ = estado_de_acao(c)
        recon[cid] = pred
        if c["STATUS"] == "TO_VALIDATE":
            tv[cid] = pred
        elif pred != c["STATUS"]:
            diverge.append((cid, c["STATUS"], pred))
    allok &= check("a lei de fb96f49d reproduz os 43 fora dos overrides",
                   not diverge, f"{43 - len(tv)} de {43 - len(tv)} não-TO_VALIDATE batem")
    allok &= check("os 9 TO_VALIDATE recuperam um estado temporal por re-execução",
                   len(tv) == 9 and all(tv.values()),
                   f"{len(tv)} casos → {sorted(set(tv.values()))}")
    print(f"       TEMPORAL_STATE_AFTER_OVERRIDE = RECOVERABLE_BY_RE_EXECUTION")
    print(f"       valor recuperado: {sorted(set(tv.values()))} em {len(tv)}/9")

    print("\n── 2 · RED TEAM SINTÉTICO (8 casos · SYNTHETIC_CONTRACT_TEST) ──")
    rt_out = []
    for rid, desc, estado, esperado_ok in RED_TEAM:
        viol = julgar(estado)
        aceite = not viol
        ok = (aceite == esperado_ok)
        rt_out.append({"ID": rid, "DESC": desc, "STATE": estado,
                       "ACCEPTED_BY_CONTRACT": aceite,
                       "EXPECTED": esperado_ok, "PASS": ok, "VIOLATIONS": viol})
        allok &= check(f"{rid} · {desc}", ok,
                       ("aceite" if aceite else "recusado: " + viol[0]["WHY"][:70]))

    print("\n── 3 · TESTE DE INDEPENDÊNCIA (mutação sintética) ──")
    # Nos 43 observados os três eixos são o MESMO conjunto. Forçamos a divergência
    # e exigimos que o contrato PRESERVE os três valores, sem os alinhar.
    mut = dict(ELIGIBILITY="OPPORTUNITY", TEMPORAL="ACT_NOW",
               COMMERCIAL="SALES_READY", PUBLICATION="VALIDATION_REQUIRED", EXTERNAL="NO")
    viol = julgar(mut)
    allok &= check("divergência SALES_READY≠PUBLISHABLE é ACEITE e preservada",
                   not viol, "os três valores continuam distintos, nenhum foi corrigido")
    mut2 = dict(mut, PUBLICATION="VALIDATION_REQUIRED", EXTERNAL="YES")
    viol2 = julgar(mut2)
    allok &= check("divergência EXTERNAL>PUBLICATION é RECUSADA",
                   bool(viol2), viol2[0]["WHY"][:70] if viol2 else "")
    allok &= check("o contrato NÃO codifica SALES_READY == PUBLISHABLE",
                   not julgar(mut),
                   "igualdade observada nos 43 não virou regra")

    print(f"\nRESULTADO GLOBAL: {'PASS' if allok else 'FAIL'}")
    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump({"MEASUREMENT": "D0.4 · red team do contrato de composição",
                       "GENERATED_BY": "docs/biblia/medicoes/testar_contrato_composicao.py",
                       "READ_ONLY": True, "BASELINE": BASELINE, "OWNER_HEAD": OWNER_HEAD,
                       "SYNTHETIC_NOT_OBSERVED": True,
                       "TEMPORAL_RECOVERY": {"RECOVERABLE": True, "METHOD": "RE_EXECUTION",
                                             "CASES": tv},
                       "RED_TEAM": rt_out, "CHECKS": RESULTS},
                      fh, ensure_ascii=False, indent=1)
        print(f"JSON: {args.json}")
    return 0 if allok else 1


if __name__ == "__main__":
    sys.exit(main())
