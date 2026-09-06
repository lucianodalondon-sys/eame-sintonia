#!/usr/bin/env python3
"""RT4 probe 8 — two closing measurements.

  I1  how many published/certified cells carry the ISSUE string 'SEPTORIA' while being computed
      from id_survey_var 372, which the source's own schema names 'Intensita Oidio'?
  I2  run_case.py:9-13 rejects the source's own `order_n` as unreliable and derives the ladder
      from label TEXT instead. Test that claim against every code table in the three cases:
      would sorting by order_n have produced the correct order?
"""
import json, os, sys, glob, collections

HERE = os.path.dirname(os.path.abspath(__file__))
CASESD = os.path.abspath(os.path.join(HERE, "..", "..", "CASES"))
CERT = os.path.abspath(os.path.join(HERE, ".."))
TOSCANA = os.path.abspath(os.path.join(HERE, "..", "..", "TOSCANA"))
sys.path.insert(0, CASESD)
from run_case import derive_rank, build_scale

TRUE = {
    372: ["Nessuna", "5 - lieve", "10 - media", "25 - grave", "50 - gravissina", "75 - completa"],
    382: ["Nessuna", "5 - lieve", "10 - media", "25 - grave", "50 - gravissima", "75 - completa"],
    383: ["Nessuna", "5 - lieve", "10 - media", "25 - grave", "50 - gravissima", "90 - completa"],
    384: ["Nessuna", "Bassa <10%", "Media 10-25%", "Alta >25%"],
    385: ["Nessuna", "Bassa <5%", "Media 5-25%", "Alta >25%"],
    386: ["Nessuna", "Bassa <5%", "Media 5-25%", "Alta >25%"],
    371: ["No", "Parte bassa", "Parte alta", "Penultima foglia", "Ultima foglia", "Spiga"],
    381: ["No", "Terzultima foglia", "Penultima foglia", "Ultima foglia", "Spiga"],
    39: ["nessuna", "bassa", "media", "alta"],
    40: ["nessuna", "1-5%", "5-10%", ">10%"],
}


def main():
    res = {}

    # ---------- I1 the SEPTORIA cells ----------
    p4 = os.path.join(CERT, "p4_cell_state_by_date.json")
    i1 = {"FILE": p4, "EXISTS": os.path.exists(p4)}
    if os.path.exists(p4):
        D = json.load(open(p4, encoding="utf-8"))
        per = D.get("PER_CELL") or D
        sept = [k for k in per if isinstance(k, str) and "SEPTORIA" in k]
        n_dates = sum(len(per[k]) for k in sept if isinstance(per[k], dict))
        i1.update({
            "CELL_KEYS_CONTAINING_SEPTORIA": sorted(sept),
            "N_CELL_KEYS": len(sept),
            "N_TOTAL_CELL_KEYS": len([k for k in per if isinstance(k, str) and "|" in k]),
            "N_CELL_DATE_STATES_UNDER_THOSE_KEYS": n_dates,
        })
        # every record that carries ISSUE == SEPTORIA
        def walk(o):
            if isinstance(o, dict):
                yield o
                for v in o.values():
                    yield from walk(v)
            elif isinstance(o, list):
                for v in o:
                    yield from walk(v)
        recs = [d for d in walk(D) if isinstance(d, dict) and d.get("ISSUE") == "SEPTORIA"]
        i1["N_RECORDS_WITH_ISSUE_SEPTORIA"] = len(recs)
        i1["THEIR_CROP_AND_REGION"] = sorted({(r.get("REGION"), r.get("CROP")) for r in recs})
        i1["STATES_THEY_CARRY"] = dict(collections.Counter(r.get("STATE") for r in recs))
    idxf = json.load(open(os.path.join(CASESD, "FRUMENTO-SEPTORIA-TOSCANA",
                                       "collection_index.json")))
    i1["VAR_372_NAME_IN_SOURCE_SCHEMA"] = next(
        v["name"] for v in idxf["vars"] if v["id_survey_var"] == 372)
    i1["WHERE_THE_STRING_SEPTORIA_IS_ASSIGNED"] = (
        "CERT-V2/p4_date_and_floor.py:38  ('TOSCANA', 'WHEAT', 'SEPTORIA', "
        "CASES/FRUMENTO-SEPTORIA-TOSCANA, 372) -- a hand-typed literal, not read from the source")
    res["I1_ISSUE_LABEL"] = i1

    # ---------- I2 order_n ----------
    i2 = {}
    for case in ("VITE-OIDIO-TOSCANA", "FRUMENTO-SEPTORIA-TOSCANA"):
        idx = json.load(open(os.path.join(CASESD, case, "collection_index.json")))
        byvar = collections.defaultdict(list)
        for c in idx["codes"]:
            byvar[c["id_survey_var"]].append(c)
        for var, entries in sorted(byvar.items()):
            truth = TRUE.get(var)
            by_order_n = [c["name"] for c in sorted(entries, key=lambda c: c["order_n"])]
            scale, unres, _ = build_scale(idx["codes"], var)
            by_ladder = [scale[str(c["id_survey_code"])]["label"]
                         for c in sorted(entries, key=lambda c: c["order_n"])
                         if str(c["id_survey_code"]) in scale]
            i2[f"{case} :: var {var}"] = {
                "ORDER_N_SEQUENCE": [(c["order_n"], c["name"]) for c in
                                     sorted(entries, key=lambda c: c["order_n"])],
                "ORDER_N_MATCHES_TRUE_ORDER": (by_order_n == truth) if truth else "NOT_ORDINAL_VAR",
                "WORD_LADDER_COVERS": f"{len(scale)}/{len(entries)}",
                "WORD_LADDER_DROPS": unres,
                "ORDER_N_COVERS": f"{len(entries)}/{len(entries)}",
            }
    ok = [k for k, v in i2.items() if v["ORDER_N_MATCHES_TRUE_ORDER"] is True]
    bad = [k for k, v in i2.items() if v["ORDER_N_MATCHES_TRUE_ORDER"] is False]
    i2["_SUMMARY"] = {
        "N_ORDINAL_CODE_TABLES_IN_THE_THREE_CASES": len(ok) + len(bad),
        "ORDER_N_GIVES_THE_CORRECT_ORDER_IN": len(ok),
        "ORDER_N_WRONG_IN": len(bad), "WRONG_ONES": bad,
        "TOTAL_LABELS": sum(int(v["WORD_LADDER_COVERS"].split("/")[1])
                            for k, v in i2.items() if k != "_SUMMARY"),
        "LABELS_THE_WORD_LADDER_RESOLVES": sum(int(v["WORD_LADDER_COVERS"].split("/")[0])
                                               for k, v in i2.items() if k != "_SUMMARY"),
    }
    res["I2_ORDER_N"] = i2

    # the counter-example run_case.py cites: peronospora leaf, media=3 below bassa=5.
    # is that code table in ANY of the three cases?
    found = {}
    for case in ("VITE-OIDIO-TOSCANA", "FRUMENTO-SEPTORIA-TOSCANA", "OLIVO-BACTROCERA-TOSCANA"):
        idx = json.load(open(os.path.join(CASESD, case, "collection_index.json")))
        for c in (idx.get("codes") or []):
            if c["name"].strip().lower() in ("media", "bassa"):
                found.setdefault(case, []).append((c["id_survey_var"], c["name"], c["order_n"]))
    res["I2b_THE_CITED_COUNTEREXAMPLE"] = {
        "CLAIM_IN_run_case.py_LINES_9_13": "order_n is unreliable (peronospora leaf: media=3 ranks below bassa=5)",
        "media_AND_bassa_ENTRIES_IN_THE_THREE_CASES": found,
        "IS_THE_CITED_INVERSION_PRESENT_IN_ANY_OF_THE_THREE_CASES": any(
            any(n.lower() == "media" and o < 4 for _, n, o in v) for v in found.values()),
        "NOTE": ("the counter-example that justifies discarding order_n comes from a "
                 "peronospora variable in DISEASE-INTELLIGENCE-ITALY/TOSCANA, not from any of "
                 "the three cases this engine is certified on"),
    }
    # look for it in TOSCANA/collection_index.json if present
    tci = os.path.join(TOSCANA, "collection_index.json")
    if os.path.exists(tci):
        t = json.load(open(tci))
        inv = [(c["id_survey_var"], c["name"], c["order_n"]) for c in (t.get("codes") or [])
               if c["name"].strip().lower() in ("media", "bassa", "alta", "nessuna")]
        res["I2b_THE_CITED_COUNTEREXAMPLE"]["TOSCANA_CASE_CODE_TABLE"] = sorted(inv)

    json.dump(res, open(os.path.join(HERE, "rt4_08_issue_label_and_order_n.json"), "w",
                        encoding="utf-8"), indent=1, ensure_ascii=False, default=str)
    print(json.dumps(res, indent=1, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
