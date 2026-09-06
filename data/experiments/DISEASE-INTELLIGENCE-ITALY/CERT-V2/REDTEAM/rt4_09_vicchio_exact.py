#!/usr/bin/env python3
"""RT4 probe 9 — the Vicchio mislabel, corrected and swept properly.

Probe 6 reassigned every id_field==5082 row labelled Siena (46 rows), but 16 of those are
legitimately Siena: id_field 5082 also carries GAIOLE IN CHIANTI, admin_code 52013. Only the
30 rows whose admin_code is 48049 (VICCHIO, province of Firenze) are mislabelled. Redone here
with that exact filter, and swept over every week of every season the mislabel exists.
"""
import json, os, sys, copy, collections, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "ENGINE")))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "CASES")))
import current_pressure as cp

VITE = os.path.abspath(os.path.join(HERE, "..", "..", "CASES", "VITE-OIDIO-TOSCANA"))


def main():
    pre = cp.load_rows(VITE, 39)
    rows_fixed = copy.deepcopy(pre[0])
    n = 0
    for r in rows_fixed:
        if (r.get("id_field") == 5082 and str(r.get("admin_code")) == "48049"
                and r.get("nome_area") == "Siena"):
            r["nome_area"] = "Firenze"
            n += 1
    res = {"ROWS_CORRECTED": n,
           "DATES_OF_THOSE_ROWS": sorted({r.get("date") for r in pre[0]
                                          if r.get("id_field") == 5082
                                          and str(r.get("admin_code")) == "48049"
                                          and r.get("nome_area") == "Siena"})}

    # dense sweep: every 7 days, 1 April - 31 October, every season 2021..2026
    val_diff, state_diff, checked = {}, {}, 0
    for y in range(2021, 2027):
        d0 = dt.date(y, 4, 1)
        while d0 <= dt.date(y, 10, 31):
            a = cp.current_pressure(VITE, 39, d0, _pre=pre)
            b = cp.current_pressure(VITE, 39, d0, _pre=(rows_fixed, pre[1], pre[2]))
            for p in set(a["PROVINCES"]) | set(b["PROVINCES"]):
                checked += 1
                ca, cb = a["PROVINCES"].get(p, {}), b["PROVINCES"].get(p, {})
                if ca.get("STATE") != cb.get("STATE"):
                    state_diff[f"{d0}/{p}"] = [ca.get("STATE"), cb.get("STATE")]
                if ca.get("VALUE") != cb.get("VALUE") or ca.get("n_sites") != cb.get("n_sites"):
                    val_diff[f"{d0}/{p}"] = {
                        "VALUE": [ca.get("VALUE"), cb.get("VALUE")],
                        "n_sites": [ca.get("n_sites"), cb.get("n_sites")],
                        "STATE": [ca.get("STATE"), cb.get("STATE")]}
            d0 += dt.timedelta(days=7)
    res["CELLS_CHECKED"] = checked
    res["CELLS_WHOSE_VALUE_OR_n_sites_CHANGED"] = len(val_diff)
    res["CELLS_WHOSE_PUBLISHED_CLASS_CHANGED"] = len(state_diff)
    res["CLASS_CHANGES"] = state_diff
    res["VALUE_CHANGES"] = val_diff
    res["TODAY_2026_09_06"] = {
        "CHANGED": [p for p in cp.current_pressure(VITE, 39, dt.date(2026, 9, 6), _pre=pre)["PROVINCES"]
                    if json.dumps(cp.current_pressure(VITE, 39, dt.date(2026, 9, 6), _pre=pre)
                                  ["PROVINCES"][p], sort_keys=True, default=str)
                    != json.dumps(cp.current_pressure(VITE, 39, dt.date(2026, 9, 6),
                                                      _pre=(rows_fixed, pre[1], pre[2]))
                                  ["PROVINCES"][p], sort_keys=True, default=str)]}
    json.dump(res, open(os.path.join(HERE, "rt4_09_vicchio_exact.json"), "w", encoding="utf-8"),
              indent=1, ensure_ascii=False, default=str)
    print(json.dumps(res, indent=1, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
