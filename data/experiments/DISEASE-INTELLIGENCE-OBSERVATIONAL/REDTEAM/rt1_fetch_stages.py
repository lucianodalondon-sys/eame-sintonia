#!/usr/bin/env python3
"""RT1 - fetch the never-collected stage variables from the live API.

Writes ONLY into REDTEAM/FETCH/. Touches nothing in the case archive.
Usage: py rt1_fetch_stages.py [year ...]
"""
import os, sys, json, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "engine"))
import di_refresh

OUT = os.path.join(HERE, "FETCH")
STAGE_VARS = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 21]
NAMES = {2: "u/Uova", 3: "l1v", 4: "l1m", 5: "l2v", 6: "l2m", 7: "l3v", 8: "l3m",
         9: "pv", 10: "pm", 11: "fu/fori di uscita", 21: "ps/punture sterili"}


def main(years):
    os.makedirs(OUT, exist_ok=True)
    log = []
    for y in years:
        for v in STAGE_VARS:
            fn = os.path.join(OUT, f"c2_s1_v{v}_{y}.json")
            if os.path.exists(fn):
                log.append({"year": y, "var": v, "status": "ALREADY_ON_DISK"})
                continue
            r = di_refresh.fetch(2, 1, v, y, timeout=120)
            if not r["ok"]:
                log.append({"year": y, "var": v, "status": "SOURCE_UNAVAILABLE",
                            "error": r["error"]})
                print(f"{y} v{v:>3} {NAMES[v]:20s} UNAVAILABLE {r['error']}")
                continue
            status, detail, rows, filt = di_refresh.validate(r["body"])
            n_read = detail.get("n_readable") if isinstance(detail, dict) else None
            log.append({"year": y, "var": v, "name": NAMES[v], "status": status,
                        "detail": detail, "seconds": r["seconds"]})
            if status == "OK":
                json.dump(rows, open(fn, "w", encoding="utf-8"), ensure_ascii=False)
            print(f"{y} v{v:>3} {NAMES[v]:20s} {status:12s} rows="
                  f"{len(rows) if rows else 0:>6} readable={n_read} {r['seconds']}s")
            time.sleep(0.5)
    json.dump(log, open(os.path.join(OUT, "fetch_log.json"), "w", encoding="utf-8"),
              indent=1, ensure_ascii=False)


if __name__ == "__main__":
    ys = [int(a) for a in sys.argv[1:]] or [2025, 2026]
    main(ys)
