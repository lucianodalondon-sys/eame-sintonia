#!/usr/bin/env python3
"""
consolidar.py — junta as camadas num unico artefato que a demo consome.

Nao e um segundo dono dos dados. Cada campo carrega de onde veio, e as camadas
reusadas de sintonia/canonical sao apontadas por commit + caminho, nunca copiadas
como se fossem nossas.

    CAMADA                      DONO
    registro + validade         Ministero della Salute (PROD_FTS_6, esta missao)
    historico do registro       Ministero, instantaneos semanais (esta missao)
    rotulo: URL, sha, data      sintonia/canonical @ bdb57cf (reuso)
    verificacao de versao       esta missao
    cultura x alvo              sintonia/canonical @ bdb57cf (reuso)
    dose                        esta missao (nao existia em lugar nenhum)
"""
import argparse, csv, json, os, sys, datetime
from collections import defaultdict

CANON = "sintonia/canonical @ bdb57cf7379a4b8b94b3ef117fb3da469fca0764"
INACTIVE = {"Revocato", "Scaduto"}


def dt(s):
    s = (s or "").strip()
    if not s or s == "-":
        return None
    try:
        return datetime.datetime.strptime(s, "%d/%m/%Y").date()
    except ValueError:
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--registro", required=True, help="CSV oficial mais recente")
    ap.add_argument("--registro-url", required=True)
    ap.add_argument("--versoes", default="pilot-label-intelligence/registry/IT-REGISTRO-VERSOES.json")
    ap.add_argument("--reverificacao", default="pilot-label-intelligence/labels/IT-ROTULOS-REVERIFICACAO.json")
    ap.add_argument("--pares", required=True, help="IT-ROTULOS-PARES-V3.json de canonical")
    ap.add_argument("--doses", default=None, help="IT-DOSES.json desta missao, se ja existir")
    ap.add_argument("--hoje", required=True)
    ap.add_argument("--out", default="pilot-label-intelligence/demo/IT-LABEL-INTELLIGENCE.json")
    a = ap.parse_args()

    hoje = datetime.date.fromisoformat(a.hoje)

    # ---- registro oficial: o universo e a verdade sobre status e validade
    rows = list(csv.DictReader(open(a.registro, encoding="utf-8", errors="replace"),
                               delimiter=";"))
    prod = {}
    for r in rows:
        if "ADAMA" not in (r.get("ragione_sociale") or "").upper():
            continue
        if (r.get("stato_amministrativo") or "").strip() in INACTIVE:
            continue
        reg = (r.get("num_registrazione") or "").strip()
        exp = dt(r.get("data_scadenza_autorizzazione"))
        prod[reg] = {
            "REGISTRATION_ID": reg,
            "PRODUCT": (r.get("denominazione_prodotto") or "").strip(),
            "HOLDER": (r.get("ragione_sociale") or "").strip(),
            "STATUS": (r.get("stato_amministrativo") or "").strip(),
            "ACTIVE_INGREDIENTS": [s.strip() for s in
                                   (r.get("sostanze_attive") or "").split("|") if s.strip()],
            "FORMULATION": (r.get("descrizione_formulazione") or "").strip() or "NOT_PRESENT",
            "REGULATORY_CATEGORY": (r.get("attivita") or "").strip() or "NOT_PRESENT",
            "REGISTERED_AT": (r.get("data_registrazione") or "").strip() or "NOT_PRESENT",
            "EXPIRY": exp.isoformat() if exp else "NOT_PRESENT",
            "DAYS_TO_EXPIRY": (exp - hoje).days if exp else "NOT_KNOWN",
            "REGISTRY_SOURCE": a.registro_url,
            # camadas preenchidas abaixo
            "LABEL": {"STATE": "NOT_KNOWN"},
            "USE_ROWS": [],
            "DOSE_ROWS": [],
            "REGISTRY_CHANGES": [],
        }

    # ---- historico do registro: eventos reais entre versoes oficiais
    versoes = {}
    if os.path.exists(a.versoes):
        v = json.load(open(a.versoes, encoding="utf-8"))
        versoes = {
            "SNAPSHOTS_DOWNLOADED": v["SNAPSHOTS_DOWNLOADED"],
            "DISTINCT_DOCUMENTS": v["DISTINCT_DOCUMENTS"],
            "WINDOW": f'{v["VERSIONS"][0]["SNAPSHOT_DATE"]}..{v["VERSIONS"][-1]["SNAPSHOT_DATE"]}',
            "CHANGE_EVENTS_REGULATORY": v["CHANGE_EVENTS_REGULATORY"],
            "CHANGE_EVENTS_TEXT_ONLY": v["CHANGE_EVENTS_TEXT_ONLY"],
            "VERSION_IDENTITY_METHOD": v["VERSION_IDENTITY_METHOD"],
        }
        for e in v["CHANGE_EVENTS"]:
            p = prod.get(e["REGISTRATION_ID"])
            if p is not None:
                p["REGISTRY_CHANGES"].append(e)

    # ---- rotulo: linha de base reusada + verificacao desta missao
    rever = {}
    if os.path.exists(a.reverificacao):
        rv = json.load(open(a.reverificacao, encoding="utf-8"))
        rever = {"BASELINE": rv["BASELINE_SOURCE"], "OBSERVED_AT": rv["OBSERVED_AT"],
                 "BASELINE_CAPTURED_AT": rv.get("BASELINE_CAPTURED_AT"),
                 "LABELS_CHECKED": rv["LABELS_CHECKED"],
                 "DOCUMENT_UNCHANGED": rv["DOCUMENT_UNCHANGED"],
                 "DOCUMENT_CHANGED": rv["DOCUMENT_CHANGED"],
                 "CHECK_FAILED": rv["CHECK_FAILED"]}
        for it in rv["ITEMS"]:
            p = prod.get(it["REGISTRATION_ID"])
            if p is None:
                continue
            p["LABEL"] = {
                "STATE": it["CHECK_STATE"],
                "URL": it["LABEL_URL"],
                "SHA256": it.get("CURRENT_SHA256"),
                "BASELINE_SHA256": it["BASELINE_SHA256"],
                "BYTES": it.get("CURRENT_BYTES", "NOT_KNOWN"),
                "EFFECTIVE_AT": it["LABEL_EFFECTIVE_AT"],
                "BASELINE_CAPTURED_AT": it["BASELINE_CAPTURED_AT"],
                "OBSERVED_AT": it["OBSERVED_AT"],
                "DOCUMENT_CHANGED": it["DOCUMENT_CHANGED"],
                "SOURCE_OWNER": CANON,
            }

    # ---- cultura x alvo: reuso puro, nao recalculado
    #
    # Os 2.928 pares NAO sao todos da mesma forca. Saem de seis rotas de
    # extracao diferentes, e apresentar todas iguais na tela seria vender
    # inferencia como linha de tabela. A rota vira classe de evidencia:
    #
    #   TABLE_GEOMETRY  a linha existe na tabela, com pagina e faixa y
    #   TEXT_INFERENCE  o par foi montado a partir de prosa ou de lista
    #
    # Nenhuma das duas e falsa. So nao sao a mesma coisa, e o cliente tem
    # direito de saber qual esta olhando.
    TABELA = {"GEOMETRIC_TABLE", "MERGED_COLUMN_TABLE"}
    pares = json.load(open(a.pares, encoding="utf-8"))
    for pr in pares["PAIRS"]:
        p = prod.get(pr["REGISTRATION_ID"])
        if p is None:
            continue
        rota = pr.get("ROUTE")
        pag = pr.get("PAGE")
        p["USE_ROWS"].append({
            "CROP": pr["CROP"], "TARGET": pr["TARGET"],
            "CROP_AS_WRITTEN": pr.get("CROP_AS_WRITTEN"),
            "TARGET_AS_WRITTEN": pr.get("TARGET_AS_WRITTEN"),
            "SOURCE_PAGE": pag if pag else "NOT_PRESERVED",
            "ROUTE": rota,
            "EVIDENCE_CLASS": "TABLE_GEOMETRY" if rota in TABELA else "TEXT_INFERENCE",
            "PROVENANCE": pr.get("PROVENANCE"),
            "OWNER": CANON,
        })

    # ---- dose: trabalho novo desta missao
    doses = {}
    if a.doses and os.path.exists(a.doses):
        dz = json.load(open(a.doses, encoding="utf-8"))
        for lab in dz["LABELS"]:
            p = prod.get(lab["REGISTRATION_ID"])
            if p is None:
                continue
            p["DOSE_ROWS"] = lab.get("ROWS", [])
            p["DOSE_PARSE_STATE"] = lab.get("PARSE_STATE")
        doses = {"LABELS_ATTEMPTED": dz.get("LABELS_ATTEMPTED"),
                 "LABELS_WITH_ROWS": dz.get("LABELS_WITH_ROWS"),
                 "TOTAL_DOSE_ROWS": dz.get("TOTAL_DOSE_ROWS")}

    lista = sorted(prod.values(), key=lambda p: p["PRODUCT"])
    tabela_n = sum(1 for p in lista for u in p["USE_ROWS"]
                   if u["EVIDENCE_CLASS"] == "TABLE_GEOMETRY")
    texto_n = sum(1 for p in lista for u in p["USE_ROWS"]
                  if u["EVIDENCE_CLASS"] == "TEXT_INFERENCE")
    sem_pag = sum(1 for p in lista for u in p["USE_ROWS"]
                  if u["SOURCE_PAGE"] == "NOT_PRESERVED")
    com_uso = [p for p in lista if p["USE_ROWS"]]
    venc = lambda d: [p for p in lista if isinstance(p["DAYS_TO_EXPIRY"], int)
                      and 0 <= p["DAYS_TO_EXPIRY"] <= d]

    out = {
        "DATASET": "IT-LABEL-INTELLIGENCE",
        "COUNTRY": "IT",
        "HOLDER": "ADAMA",
        "BUILT_AT": a.hoje,
        "O_QUE_ISTO_E": "camada de consulta do piloto de label intelligence, montada por juncao",
        "O_QUE_ISTO_NAO_E": ("nao e um novo dono dos dados. cultura x alvo e reuso de "
                             + CANON + "; registro e validade sao do Ministero"),
        "LAYER_OWNERSHIP": {
            "REGISTRY": "Ministero della Salute — PROD_FTS_6 (esta missao)",
            "REGISTRY_HISTORY": "Ministero — instantaneos semanais (esta missao)",
            "LABEL_DOCUMENT": CANON + " (linha de base) + verificacao desta missao",
            "CROP_X_TARGET": CANON,
            "DOSE": "esta missao — nao existia em nenhuma ref",
        },
        "TOTAL_ADAMA_PRODUCTS": len(lista),
        "PRODUCTS_WITH_USE_ROWS": len(com_uso),
        "PRODUCTS_WITHOUT_USE_ROWS": len(lista) - len(com_uso),
        "TOTAL_USE_ROWS": sum(len(p["USE_ROWS"]) for p in lista),
        "USE_ROWS_FROM_TABLE_GEOMETRY": tabela_n,
        "USE_ROWS_FROM_TEXT_INFERENCE": texto_n,
        "USE_ROWS_WITHOUT_PAGE": sem_pag,
        "USE_ROWS_EVIDENCE_NOTE": ("os pares vem de seis rotas de extracao. Os de "
                                   "TABLE_GEOMETRY tem pagina e faixa y no documento; "
                                   "os de TEXT_INFERENCE foram montados de prosa ou "
                                   "lista e uma parte nao preservou pagina. Nenhum "
                                   "par carrega citacao literal — a casa nao gravou "
                                   "SOURCE_QUOTE nesta versao do parser."),
        "TOTAL_DOSE_ROWS": sum(len(p["DOSE_ROWS"]) for p in lista),
        "EXPIRING_30": len(venc(30)), "EXPIRING_90": len(venc(90)),
        "EXPIRING_180": len(venc(180)),
        "REGISTRY_HISTORY": versoes,
        "LABEL_VERSION_CHECK": rever,
        "DOSE_RUN": doses,
        "PRODUCTS": lista,
    }
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(out, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"  produtos {len(lista)} | com uso lido {len(com_uso)} | "
          f"pares {out['TOTAL_USE_ROWS']} (tabela {tabela_n} / texto {texto_n}) | "
          f"doses {out['TOTAL_DOSE_ROWS']}", file=sys.stderr)
    print(f"  vencendo 30/90/180: {out['EXPIRING_30']}/{out['EXPIRING_90']}/{out['EXPIRING_180']}",
          file=sys.stderr)
    print(f"  escrito {a.out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
