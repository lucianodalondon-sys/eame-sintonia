#!/usr/bin/env python3
"""RT1 - THE SOURCE PUBLISHES ITS OWN FORMULA.

The same endpoint the archive was built from returns, in filter.survey_var.data, a
`calculated_field` SQL expression for each server-computed variable. Print it verbatim,
and diff the live variable metadata against the archived collection_index.json the
semantic sheet cites as its evidence.
"""
import os, sys, json, difflib
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "engine"))
sys.path.insert(0, HERE)
import di_refresh
import rt1_lib as L

OUT = os.path.join(HERE, "FETCH", "live_vars_2026.json")


def main():
    if os.path.exists(OUT):
        live = json.load(open(OUT, encoding="utf-8"))
    else:
        r = di_refresh.fetch(2, 1, -1003, 2026, timeout=90)
        js = json.loads(r["body"].decode("utf-8"))
        live = js["filter"]["survey_var"]["data"]
        json.dump(live, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"live variable metadata: {len(live)} variables for crop 2 / schema 1\n")

    print("=" * 76)
    print("THE SERVER-SIDE FORMULA, VERBATIM, AS THE SOURCE SERVES IT TODAY")
    print("=" * 76)
    for v in live:
        if v.get("id_survey_var") not in (-1001, -1002, -1003):
            continue
        j = json.loads(v["json"]) if v.get("json") else {}
        cf = (j.get("calculated_field") or {}).get("value")
        print(f"\n  id_survey_var {v['id_survey_var']}  var_name {v['var_name']!r}  "
              f"description {v.get('description')!r}")
        if cf:
            print("  calculated_field:")
            for line in cf.replace("+", "\n      +").splitlines():
                if line.strip():
                    print(f"    {line.strip()}")
        print(f"  style: {json.dumps(j.get('style'), ensure_ascii=False)}")
    print()

    print("=" * 76)
    print("LIVE METADATA vs THE ARCHIVED collection_index.json THE SHEET CITES")
    print("=" * 76)
    arch = json.load(open(os.path.join(L.CASE, "collection_index.json"),
                          encoding="utf-8"))["vars"]
    by_arch = {v["id_survey_var"]: v for v in arch}
    for v in live:
        vid = v.get("id_survey_var")
        a = by_arch.get(vid)
        if a is None:
            continue
        for field in ("var_name", "description", "json"):
            lv, av = v.get(field), a.get(field)
            if lv == av:
                continue
            print(f"\n  var {vid} field {field!r} DIFFERS")
            print(f"    archived: {str(av)[:300]}")
            print(f"    live    : {str(lv)[:300]}")
    print()

    print("=" * 76)
    print("THE COLOUR LEGEND: what the sheet copied vs what the source serves now")
    print("=" * 76)
    sheet = json.load(open(os.path.join(HERE, "..", "S1-SEMANTICS",
                                        "SOURCE-SEMANTIC-SHEET.json"), encoding="utf-8"))
    print("  SHEET SOURCE_ACTION_BANDS:")
    for b in sheet["SOURCE_ACTION_BANDS"]["BANDS"]:
        print(f"    from {b['from_pct']} to {b['to_pct']}  {b['label']!r}  {b['colour']}")
    for v in live:
        j = json.loads(v["json"]) if v.get("json") else {}
        st = j.get("style")
        if not st:
            continue
        print(f"  LIVE style for var {v['id_survey_var']} ({v['var_name']}):")
        for b in st:
            print(f"    value >= {b['value']}  {b['label']!r}  {b['color']}")
    print()
    print("  variables that carry NO style at all in the live metadata: "
          f"{[v['id_survey_var'] for v in live if not (json.loads(v['json']) if v.get('json') else {}).get('style')]}")


if __name__ == "__main__":
    main()
