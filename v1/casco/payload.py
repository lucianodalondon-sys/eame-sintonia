#!/usr/bin/env python3
"""
payload.py — monta o que o CASCO consome. O casco nunca abre PDF nem CSV.

Le o COLLECTION_PACKAGE (coleta) e os INTELLIGENCE_OBJECTS (inteligencia) e
devolve um unico JSON enxuto para a interface. Se um campo nao existe na fonte,
ele viaja como NOT_KNOWN / NOT_PRESENT / NOT_PROVED ate a tela — a interface nao
tem permissao de inventar o que a coleta nao trouxe.
"""
import argparse, csv, datetime, hashlib, json, os, sys
from collections import Counter

# A lista de pares vinha de sintonia/canonical, que nao esta neste repositorio e
# nao esta acessivel a esta sessao. `v1/fonte/pares_reconstruir.py` a remonta a
# partir de EXCLUSAO.json + CASCO-PAYLOAD.json, e `v1/fonte/pares_conferir.py`
# prova que a esteira chega ao mesmo lugar: R-10 identico nas 2928 chaves e os
# 2926 pares publicados identicos nos 9 campos. Medido tambem no fim da linha —
# o HTML remontado por este caminho tem o sha256 7e4ea2a7b445fafa..., o mesmo
# que o arbitro do red team 3 julgou.
PARES = "v1/dados/IT-ROTULOS-PARES-RECONSTRUIDO.json"


def limpa(v):
    """O CSV oficial imprime "-" para celula vazia: isso e ausencia declarada."""
    v = str(v or "").strip()
    return "NOT_PRESENT" if v in ("-", "", "--") else v


def iso(s):
    s = (s or "").strip()
    if not s or s == "-":
        return "NOT_PRESENT"
    try:
        return datetime.datetime.strptime(s, "%d/%m/%Y").date().isoformat()
    except ValueError:
        return "NOT_PARSED"


def linha_do_registro(snapshots, snapshot_id, reg):
    """Le a linha bruta do produto no instantaneo oficial vigente.

    Um produto Revocato ou Scaduto sai do conjunto ATIVO, nao do arquivo. A
    ferramenta tinha a linha inteira em disco e mesmo assim escrevia
    "todos os campos abaixo sao NOT_KNOWN por falta de coleta". Nao era falta
    de coleta: era a ficha nao ter ido buscar o que ja estava coletado.
    """
    caminho = os.path.join(snapshots, snapshot_id + ".csv")
    if not os.path.exists(caminho):
        return None
    alvo = reg.strip().lstrip("0")
    with open(caminho, encoding="utf-8-sig", errors="replace", newline="") as fh:
        for r in csv.DictReader(fh, delimiter=";"):
            if (r.get("num_registrazione") or "").strip().lstrip("0") == alvo:
                return r
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pacote", default="v1/dados/COLLECTION-PACKAGE.json")
    ap.add_argument("--objetos", default="v1/dados/INTELLIGENCE-OBJECTS.json")
    ap.add_argument("--versoes", default="pilot-label-intelligence/registry/IT-REGISTRO-VERSOES.json")
    ap.add_argument("--doses", default="pilot-label-intelligence/demo/IT-DOSES.json")
    ap.add_argument("--pares", default=PARES)
    ap.add_argument("--exclusao", default="v1/dados/EXCLUSAO.json")
    ap.add_argument("--snapshots", default="pilot-label-intelligence/registry/snapshots")
    ap.add_argument("--teto", default="v1/dados/TETO-DOSE.json")
    ap.add_argument("--cultura", default="v1/dados/DOSES-CULTURA-CHECK.json")
    ap.add_argument("--alvoliteral", default="v1/dados/ALVO-LITERAL.json")
    ap.add_argument("--hoje", required=True)
    ap.add_argument("--out", default="v1/dados/CASCO-PAYLOAD.json")
    a = ap.parse_args()

    pkg = json.load(open(a.pacote, encoding="utf-8"))
    io_ = json.load(open(a.objetos, encoding="utf-8"))
    vs = json.load(open(a.versoes, encoding="utf-8"))
    hoje = datetime.date.fromisoformat(a.hoje)

    # EXCLUSAO NAO E PERMISSAO. O leitor de uso reusado nao modela escopo
    # negativo: em 002983 e 013405 ele leu "Pomodoro (ad esclusione di Pomodoro
    # ciliegino)" e publicou CILIEGIO como cultura AUTORIZADA. v1/coleta/exclusao.py
    # reconcilia cada par contra o PDF oficial; aqui o veredito dele e obedecido.
    exc = json.load(open(a.exclusao, encoding="utf-8")) if os.path.exists(a.exclusao) else None
    if exc is None:
        raise SystemExit("EXCLUSAO.json ausente: sem ele o casco publicaria exclusao "
                         "como permissao. Rode v1/coleta/exclusao.py antes.")
    veredito = exc["VERDICT"]
    # A GUARDA do vinculo par<->veredito. Sem ela o casco confiava numa posicao.
    with open(a.pares, "rb") as _fh:
        _sha = hashlib.sha256(_fh.read()).hexdigest()
    if _sha != exc.get("PAIRS_SHA256"):
        raise SystemExit(
            f"EXCLUSAO.json foi calculado sobre outro arquivo de pares "
            f"(sha256 {exc.get('PAIRS_SHA256','?')[:12]} vs {_sha[:12]}). Os vereditos de "
            f"exclusao sao gravados por posicao: aplica-los a outra lista faria a retirada cair "
            f"no par errado. Rode v1/coleta/exclusao.py de novo.")
    # So janela de ESCOPO DE CULTURA vai para a tela: as de compatibilidade de
    # calda e de numero de tratamentos nao dizem nada sobre cultura autorizada.
    janelas_por_reg = {r: v.get("EXCLUSION_WINDOWS_CROP_SCOPE", [])
                       for r, v in exc["LABELS"].items()}
    retirado_por_reg = {}
    for w in exc["RETIRADOS"]:
        retirado_por_reg.setdefault(w["REGISTRATION_ID"], []).append(w)
    # a retirada precisa da URL oficial do documento, como toda outra afirmacao
    _url = {i["REGISTRATION_ID"]: i["PDF_URL"] for i in pkg["ITEMS"]}
    for _r, _ws in retirado_por_reg.items():
        for _w in _ws:
            _w["LABEL_URL"] = _url.get(_r, "NOT_KNOWN")

    # usos por produto (reuso apontado)
    usos = {}
    TAB = {"GEOMETRIC_TABLE", "MERGED_COLUMN_TABLE"}
    ordem = {}
    trio = exc.get("VERDICT_KEY_TRIPLE", {})
    for x in json.load(open(a.pares, encoding="utf-8"))["PAIRS"]:
        reg = x["REGISTRATION_ID"]
        i = ordem[reg] = ordem.get(reg, -1) + 1
        chave = f"{reg}#{i}"
        esperado = trio.get(chave)
        if esperado and esperado != [x["CROP"], x["TARGET"]]:
            raise SystemExit(
                f"vinculo de exclusao desalinhado em {chave}: EXCLUSAO.json diz "
                f"{esperado} e a lista de pares traz {[x['CROP'], x['TARGET']]}")
        est = veredito.get(chave, "NOT_CHECKED")
        if est == "CROP_ONLY_INSIDE_EXCLUSION":
            continue                      # nao entra na lista de usos autorizados
        usos.setdefault(reg, []).append({
            "crop": x["CROP"], "target": x["TARGET"],
            "crop_raw": x.get("CROP_AS_WRITTEN"), "target_raw": x.get("TARGET_AS_WRITTEN"),
            "page": x.get("PAGE") or "NOT_PRESERVED",
            "route": x.get("ROUTE"),
            "evidence": "TABLE_GEOMETRY" if x.get("ROUTE") in TAB else "TEXT_INFERENCE",
            "quote": "NOT_PRESERVED",
            "exclusion_check": est,
        })

    # TETO POR CULTURA escrito fora da tabela (R-12) e CONFERENCIA DA CULTURA
    # da linha contra os fios desenhados (R-11). Sem os dois a tela publica
    # dose acima do que o proprio rotulo autoriza e dose atribuida a cultura
    # errada — os dois erros foram medidos, nao supostos.
    teto = json.load(open(a.teto, encoding="utf-8")) if os.path.exists(a.teto) else None
    cultura = json.load(open(a.cultura, encoding="utf-8")) if os.path.exists(a.cultura) else None
    if teto is None or cultura is None:
        raise SystemExit("TETO-DOSE.json e/ou DOSES-CULTURA-CHECK.json ausentes: sem eles o "
                         "casco publica dose acima do teto do rotulo e dose de outra cultura. "
                         "Rode v1/inteligencia/teto_dose.py e v1/inteligencia/cultura_validar.py")
    vc = cultura["VERDICT"]
    alv = json.load(open(a.alvoliteral, encoding="utf-8")) if os.path.exists(a.alvoliteral) else None
    va = alv["VERDICT"] if alv else {}

    # doses por produto, ja deduplicadas
    doses = {}
    if os.path.exists(a.doses):
        for lab in json.load(open(a.doses, encoding="utf-8"))["LABELS"]:
            seen, out = set(), []
            for _i, r in enumerate(lab.get("ROWS") or []):
                k = (r.get("CROP"), r.get("TARGET"), r.get("DOSE_CONCENTRATION"),
                     r.get("DOSE_PER_HECTARE"))
                if k in seen:
                    continue
                seen.add(k)
                out.append({
                    "crop_check": vc.get(f'{lab["REGISTRATION_ID"]}#{_i}', "NOT_CHECKED"),
                    "target_literal": va.get(f'{lab["REGISTRATION_ID"]}#{_i}', "TARGET_TEXT_NOT_CHECKED"),
                    "crop": r.get("CROP"), "target": r.get("TARGET"),
                    "crop_inherited": bool(r.get("CROP_INHERITED")),
                    "dose_conc": r.get("DOSE_CONCENTRATION"),
                    "unit_conc": r.get("DOSE_CONCENTRATION_UNIT"),
                    "dose_ha": r.get("DOSE_PER_HECTARE"),
                    "unit_ha": r.get("DOSE_PER_HECTARE_UNIT"),
                    "dose_ha_inherited": bool(r.get("DOSE_PER_HECTARE_INHERITED")),
                    "max_app": r.get("MAX_APPLICATIONS"),
                    "max_app_inherited": bool(r.get("MAX_APPLICATIONS_INHERITED")),
                    "interval": r.get("APPLICATION_INTERVAL"),
                    "page": r.get("SOURCE_PAGE"),
                    "quote": r.get("SOURCE_QUOTE"),
                    "rule_check": r.get("DOSE_RULE_CHECK", "NOT_CHECKED"),
                    "needs_review": bool(r.get("NEEDS_REVIEW")),
                    "rejected": r.get("DOSE_PER_HECTARE_REJECTED"),
                })
            doses[lab["REGISTRATION_ID"]] = {"rows": out, "state": lab.get("PARSE_STATE")}

    produtos = []
    for i in pkg["ITEMS"]:
        reg = i["REGISTRATION_ID"]
        try:
            dte = (datetime.date.fromisoformat(i["EXPIRY_RAW"]) - hoje).days
        except Exception:
            dte = "NOT_KNOWN"
        dz = doses.get(reg, {})
        produtos.append({
            "reg": reg, "name": i["PRODUCT_NAME_RAW"], "holder": i["HOLDER_RAW"],
            "status": i["STATUS_RAW"], "actives": i["ACTIVE_INGREDIENTS_RAW"],
            "formulation": i["FORMULATION_RAW"], "activity": i["ACTIVITY_RAW"],
            "registered_at": i["REGISTERED_AT"], "expiry": i["EXPIRY_RAW"], "dte": dte,
            "pdf_url": i["PDF_URL"], "pdf_sha": i["PDF_SHA256"], "pdf_bytes": i["PDF_BYTES"],
            "label_effective": i["LABEL_EFFECTIVE_AT"],
            "label_valid_from": i.get("LABEL_VALID_FROM", "NOT_CHECKED"),
            "label_valid_to": i.get("LABEL_VALID_TO", "NOT_CHECKED"),
            "label_validity_quote": i.get("LABEL_VALIDITY_QUOTE", "NOT_PRESENT"),
            "captured_at": i["CAPTURED_AT"],
            "snapshot": i["REGISTRY_SNAPSHOT_ID"], "snapshot_sha": i["REGISTRY_SNAPSHOT_SHA256"],
            "source_url": i["SOURCE_URL"], "run": i["COLLECTION_RUN_ID"],
            "states": i["READ_STATES"],
            "ceilings": teto["CEILINGS"].get(reg, []),
            "label_dose_notes_not_read": reg in teto["OTHER_DOSE_NOTES_NOT_READ"],
            "uses": usos.get(reg, []),
            "uses_retirados": retirado_por_reg.get(reg, []),
            "exclusion_windows": janelas_por_reg.get(reg, []),
            "doses": dz.get("rows", []),
            "dose_state": dz.get("state", "NOT_ATTEMPTED"),
            "text_chars": i["TEXT_CHARS"],
        })

    objetos = io_["OBJECTS_LIST"]

    # Um evento pode falar de registro que JA NAO esta no conjunto ativo — foi
    # revogado, venceu, ou saiu. Sem uma ficha para ele, o card cita um produto
    # que a ferramenta nao abre, e o usuario fica sem versao, titular e validade.
    ESTADOS = ("LABEL_DISCOVERED", "LABEL_DOWNLOADED", "TEXT_EXTRACTED", "LABEL_READ",
               "USE_ROWS_STRUCTURED", "DOSE_STRUCTURED", "PHI_STRUCTURED", "NEEDS_REVIEW")
    tem = {p["reg"] for p in produtos}
    faltando = {}
    for o in objetos:
        r = o.get("REGISTRATION_ID")
        if r and r not in tem:
            faltando.setdefault(r, o)
    for r, o in faltando.items():
        linha = linha_do_registro(a.snapshots, pkg["REGISTRY_SNAPSHOT_ID"], r)
        if linha is None:
            # Aqui sim: o registro nao esta no instantaneo vigente. NOT_KNOWN
            # por ausencia de linha, e a ficha diz isso e nao outra coisa.
            produtos.append({
                "reg": r, "name": o.get("PRODUCT_NAME") or "NOT_KNOWN",
                "holder": o.get("HOLDER") or "NOT_KNOWN",
                "status": "NOT_IN_SNAPSHOT",
                "actives": "NOT_KNOWN", "formulation": "NOT_KNOWN", "activity": "NOT_KNOWN",
                "registered_at": "NOT_KNOWN", "expiry": "NOT_KNOWN", "dte": "NOT_KNOWN",
                "pdf_url": "NOT_KNOWN", "pdf_sha": "NOT_KNOWN", "pdf_bytes": "NOT_KNOWN",
                "label_effective": "NOT_KNOWN",
                "captured_at": o.get("CAPTURED_AT", "NOT_KNOWN"),
                "snapshot": pkg["REGISTRY_SNAPSHOT_ID"],
                "snapshot_sha": pkg["REGISTRY_SNAPSHOT_SHA256"],
                "source_url": o.get("SOURCE_URL", "NOT_KNOWN"),
                "run": pkg["COLLECTION_RUN_ID"],
                "states": {k: False for k in ESTADOS},
                "uses": [], "uses_retirados": [], "exclusion_windows": [],
                "doses": [], "dose_state": "NOT_ATTEMPTED",
                "text_chars": "NOT_KNOWN",
                "out_of_active_set": True,
                "registry_row_read": False,
                "out_of_active_set_note": (
                    "este registro aparece no historico oficial mas NAO tem linha no "
                    "instantaneo vigente. Nao ha o que ler: os campos sao NOT_KNOWN por "
                    "ausencia de linha, nao por opiniao da ferramenta"),
            })
            continue
        venc = iso(linha.get("data_scadenza_autorizzazione"))
        try:
            dte = (datetime.date.fromisoformat(venc) - hoje).days
        except Exception:
            dte = "NOT_KNOWN"
        produtos.append({
            "reg": r,
            "name": limpa(linha.get("denominazione_prodotto")),
            "holder": limpa(linha.get("ragione_sociale")),
            "status": limpa(linha.get("stato_amministrativo")),
            "actives": limpa(linha.get("sostanze_attive")),
            "formulation": limpa(linha.get("descrizione_formulazione")),
            "activity": limpa(linha.get("attivita")),
            "registered_at": iso(linha.get("data_registrazione")),
            "expiry": venc, "dte": dte,
            "hazard": limpa(linha.get("indicazioni_di_pericolo")),
            "revoke_reason": limpa(linha.get("motivo_della revoca")),
            "revoke_decree": limpa(linha.get("data_decreto_revoca")),
            "revoke_effective": iso(linha.get("data_decorrenza_revoca")),
            # O ROTULO deste produto nao foi baixado. Isto e diferente de nao
            # existir: e NOT_COLLECTED, e a ficha tem de dizer qual dos dois e.
            "pdf_url": "NOT_COLLECTED", "pdf_sha": "NOT_COLLECTED",
            "pdf_bytes": "NOT_COLLECTED", "label_effective": "NOT_COLLECTED",
            # A data de captura e de um ARTEFATO. Para estes tres nao houve
            # captura de rotulo nenhuma: copiar a data do primeiro produto do
            # pacote seria atribuir a eles um ato que nao aconteceu.
            "captured_at": "NOT_COLLECTED",
            "registry_row_captured_at": pkg["ITEMS"][0]["CAPTURED_AT"] if pkg["ITEMS"] else "NOT_KNOWN",
            "snapshot": pkg["REGISTRY_SNAPSHOT_ID"],
            "snapshot_sha": pkg["REGISTRY_SNAPSHOT_SHA256"],
            "source_url": pkg["ITEMS"][0]["SOURCE_URL"] if pkg["ITEMS"] else "NOT_KNOWN",
            "run": pkg["COLLECTION_RUN_ID"],
            "states": dict({k: False for k in ESTADOS}, LABEL_DISCOVERED=False),
            "ceilings": [], "label_dose_notes_not_read": False,
            "uses": [], "uses_retirados": [], "exclusion_windows": [],
            "doses": [], "dose_state": "NOT_ATTEMPTED",
            "text_chars": "NOT_COLLECTED",
            "out_of_active_set": True,
            "registry_row_read": True,
            "out_of_active_set_note": (
                "este registro NAO esta no conjunto ativo do instantaneo vigente — o "
                "estado administrativo dele e \"" + limpa(linha.get("stato_amministrativo")) +
                "\". Sair do conjunto ativo nao e sair do arquivo: os campos de registro "
                "abaixo foram LIDOS da linha oficial deste produto no instantaneo "
                + pkg["REGISTRY_SNAPSHOT_ID"] + ". O que nao existe aqui e o ROTULO: "
                "nenhum PDF foi baixado para ele, entao uso, dose e PHI ficam "
                "NOT_COLLECTED — por falta de coleta, nao por ausencia no registro"),
        })
    # versoes do registro para a timeline
    versoes = [{"date": v["SNAPSHOT_DATE"], "id": v["VERSION_ID"], "sha": v["SHA256"],
                "bytes": v["BYTES"], "url": v["SOURCE_URL"],
                "republished": v.get("REPUBLISHED_UNCHANGED_ON", []),
                "adama_active": v["ADAMA_ACTIVE"], "total": v["PRODUCTS_TOTAL"]}
               for v in vs["VERSIONS"]]

    cov = pkg["COVERAGE"]
    payload = {
        "TOOL": "SINTONIA — LABEL INTELLIGENCE",
        "VERSION": "V1",
        "COUNTRY": "IT",
        "BUILT_AT": a.hoje,
        # A DATA DO DADO NAO E A DATA DO BUILD. O cabecalho dizia "dados de
        # 2026-09-06", que e o dia em que a ferramenta foi montada; o
        # instantaneo oficial mais novo e de 2026-08-31, e a mudanca mais nova
        # dentro dele e mais antiga ainda. Tres datas diferentes, uma so
        # impressa: era a errada.
        "DATA_DATE": versoes[-1]["date"] if versoes else "NOT_KNOWN",
        "DATA_SNAPSHOT_ID": pkg["REGISTRY_SNAPSHOT_ID"],
        "NEWEST_CHANGE_AT": max((o.get("DETECTED_AT") or "" for o in objetos
                                 if o.get("PROOF_STATE") == "PROVED"), default="") or "NOT_KNOWN",
        "RUN": pkg["COLLECTION_RUN_ID"],
        "RULESET_VERSION": io_["RULESET_VERSION"],
        "SOURCE_AUTHORITY": pkg["SOURCE_AUTHORITY"],
        "LICENSE": pkg["LICENSE"],
        "coverage": cov,
        "coverage_note": pkg["COVERAGE_NOTE"],
        "products": produtos,
        "objects": objetos,
        "versions": versoes,
        "history": {
            "snapshots": vs["SNAPSHOTS_DOWNLOADED"],
            "distinct": vs["DISTINCT_DOCUMENTS"],
            "window": f'{versoes[0]["date"]}..{versoes[-1]["date"]}',
            "raw_field_diffs": vs["FIELD_DIFFS_WITHOUT_NORMALISATION"],
            "normalised_field_diffs": vs["FIELD_DIFFS_WITH_NORMALISATION"],
            "noise": vs["SERIALIZATION_NOISE_SUPPRESSED"],
            "noise_pct": vs["NOISE_SHARE"],
            "true_changes": vs["CHANGE_EVENTS_REGULATORY"],
            "text_only": vs["CHANGE_EVENTS_TEXT_ONLY"],
        },
        "exclusion": {
            "rule": exc["RULE_ID"],
            "labels_checked": exc["LABELS_CHECKED"],
            "labels_with_crop_scope_exclusion": exc["LABELS_WITH_CROP_SCOPE_EXCLUSION"],
            "labels_with_any_marker": exc["LABELS_WITH_ANY_EXCLUSION_MARKER"],
            "prefix_match_only": exc["PAIRS_CROP_NAME_PREFIX_MATCH_ONLY"],
            "pairs_checked": exc["PAIRS_CHECKED"],
            "retirados": exc["PARES_RETIRADOS"],
            "name_not_in_label_text": exc["PAIRS_CROP_NAME_NOT_IN_LABEL_TEXT"],
            "markers": exc["MARCADOR_OCORRENCIAS"],
            "marker_dropped": exc["MARCADOR_DESCARTADO"],
            "list": exc["RETIRADOS"],
        },
        "reconciliation": (json.load(open("v1/BASELINE-RAW.json", encoding="utf-8"))
                           .get("RECONCILIATION_WITH_PUBLISHED")
                           if os.path.exists("v1/BASELINE-RAW.json") else
                           {"STATE": "NOT_CHECKED"}),
        "ceiling": {k: v for k, v in teto.items() if k != "CEILINGS"},
        "crop_check": {k: v for k, v in cultura.items() if k not in ("VERDICT", "CONTRADICTED")},
        "crop_check_list": cultura["CONTRADICTED"],
        "target_literal": ({k: v for k, v in alv.items() if k not in ("VERDICT", "NOT_FOUND")}
                           if alv else {"STATE": "NOT_CHECKED"}),
        "by_type": io_["BY_TYPE"],
        "by_proof": io_["BY_PROOF_STATE"],
        "by_window": io_["BY_TIME_WINDOW"],
    }
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(payload, open(a.out, "w", encoding="utf-8"), ensure_ascii=False,
              separators=(",", ":"))
    print(f'  produtos {len(produtos)} | objetos {len(objetos)} | versoes {len(versoes)}',
          file=sys.stderr)
    print(f'  {os.path.getsize(a.out)/1024:.0f} KB -> {a.out}', file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
