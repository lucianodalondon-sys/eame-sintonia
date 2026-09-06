#!/usr/bin/env python3
"""
payload.py — monta o que o CASCO consome. O casco nunca abre PDF nem CSV.

Le o COLLECTION_PACKAGE (coleta) e os INTELLIGENCE_OBJECTS (inteligencia) e
devolve um unico JSON enxuto para a interface. Se um campo nao existe na fonte,
ele viaja como NOT_KNOWN / NOT_PRESENT / NOT_PROVED ate a tela — a interface nao
tem permissao de inventar o que a coleta nao trouxe.
"""
import argparse, datetime, json, os, sys
from collections import Counter

CANON = "/tmp/claude-0/-home-user-eame-sintonia/113d92e8-e962-52b2-b6d1-c8c3e286096e/scratchpad/canonical"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pacote", default="v1/dados/COLLECTION-PACKAGE.json")
    ap.add_argument("--objetos", default="v1/dados/INTELLIGENCE-OBJECTS.json")
    ap.add_argument("--versoes", default="pilot-label-intelligence/registry/IT-REGISTRO-VERSOES.json")
    ap.add_argument("--doses", default="pilot-label-intelligence/demo/IT-DOSES.json")
    ap.add_argument("--pares", default=f"{CANON}/data/samples/IT-ROTULOS-V1/IT-ROTULOS-PARES-V3.json")
    ap.add_argument("--hoje", required=True)
    ap.add_argument("--out", default="v1/dados/CASCO-PAYLOAD.json")
    a = ap.parse_args()

    pkg = json.load(open(a.pacote, encoding="utf-8"))
    io_ = json.load(open(a.objetos, encoding="utf-8"))
    vs = json.load(open(a.versoes, encoding="utf-8"))
    hoje = datetime.date.fromisoformat(a.hoje)

    # usos por produto (reuso apontado)
    usos = {}
    TAB = {"GEOMETRIC_TABLE", "MERGED_COLUMN_TABLE"}
    for x in json.load(open(a.pares, encoding="utf-8"))["PAIRS"]:
        usos.setdefault(x["REGISTRATION_ID"], []).append({
            "crop": x["CROP"], "target": x["TARGET"],
            "crop_raw": x.get("CROP_AS_WRITTEN"), "target_raw": x.get("TARGET_AS_WRITTEN"),
            "page": x.get("PAGE") or "NOT_PRESERVED",
            "route": x.get("ROUTE"),
            "evidence": "TABLE_GEOMETRY" if x.get("ROUTE") in TAB else "TEXT_INFERENCE",
            "quote": "NOT_PRESERVED",
        })

    # doses por produto, ja deduplicadas
    doses = {}
    if os.path.exists(a.doses):
        for lab in json.load(open(a.doses, encoding="utf-8"))["LABELS"]:
            seen, out = set(), []
            for r in (lab.get("ROWS") or []):
                k = (r.get("CROP"), r.get("TARGET"), r.get("DOSE_CONCENTRATION"),
                     r.get("DOSE_PER_HECTARE"))
                if k in seen:
                    continue
                seen.add(k)
                out.append({
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
            "label_effective": i["LABEL_EFFECTIVE_AT"], "captured_at": i["CAPTURED_AT"],
            "snapshot": i["REGISTRY_SNAPSHOT_ID"], "snapshot_sha": i["REGISTRY_SNAPSHOT_SHA256"],
            "source_url": i["SOURCE_URL"], "run": i["COLLECTION_RUN_ID"],
            "states": i["READ_STATES"],
            "uses": usos.get(reg, []),
            "doses": dz.get("rows", []),
            "dose_state": dz.get("state", "NOT_ATTEMPTED"),
            "text_chars": i["TEXT_CHARS"],
        })

    objetos = io_["OBJECTS_LIST"]
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
