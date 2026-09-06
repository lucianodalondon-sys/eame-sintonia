#!/usr/bin/env python3
"""
GENERIC collector — the SAME code for every case. No case-specific branch anywhere.
If a case needs a special rule here, that is a PIPELINE_REUSE failure and must be recorded.
"""
import json, os, sys, time, urllib.request, urllib.parse, hashlib
API = "https://agroambiente.info.regione.toscana.it/agro18/api/dati/get_aedita_data"

def fetch(p, tries=4):
    q = urllib.parse.urlencode(p)
    for i in range(tries):
        try:
            with urllib.request.urlopen(f"{API}?{q}", timeout=120) as r:
                return json.load(r)
        except Exception as e:
            if i == tries - 1: return {"_error": str(e)[:160]}
            time.sleep(3 * (i + 1))

def unwrap(js):
    if not isinstance(js, dict) or "_error" in js: return False, None, [], None
    d = js.get("data"); fb = js.get("filter")
    if isinstance(d, dict): return bool(d.get("ok")), d.get("rowCount"), (d.get("data") or []), fb
    if isinstance(d, list): return True, len(d), d, fb
    return False, None, [], fb

if __name__ == "__main__":
    outdir, crop, schema, years = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
    vars_ = [int(v) for v in sys.argv[5].split(",")]
    y0, y1 = [int(x) for x in years.split("-")]
    raw = os.path.join(outdir, "RAW"); os.makedirs(raw, exist_ok=True)
    idx = {"api": API, "crop": crop, "schema": schema, "requests": [], "codes": None, "vars": None}
    for v in vars_:
        for y in range(y0, y1 + 1):
            js = fetch({"tipo_elab": "elab_pivot", "year": y, "crop": crop,
                        "survey_schema": schema, "survey_var": v, "difesa": "all",
                        "week": "all", "cultivar": "all", "area": "all",
                        "accesso": "all", "user_access": "all"})
            ok, rc, rows, fb = unwrap(js)
            # FIXED 2026-09-06. This used to latch on the first response carrying a
            # survey_code KEY, which for a case whose archive starts after 2006 is the EMPTY
            # table of a year with no data — after which the pipeline had no scale at all and
            # run_case.py fell back to treating CODE IDS as magnitudes. Latch on the first
            # response that actually has ROWS.
            # Take the MOST COMPLETE table seen, not the first one. The source's code table is
            # year-dependent (crop3/schema8 grows 16 codes in 2006 to 74 in 2025), so latching
            # any single year freezes a scale the later years have outgrown.
            cand = (fb or {}).get("survey_code") or {}
            if cand.get("data") and len(cand["data"]) > len(idx["codes"] or []):
                idx["codes"] = cand["data"]
                idx["vars"] = [x for x in (fb.get("survey_var") or {}).get("data") or []
                               if x["id_survey_schema"] == schema]
            rec = {"var": v, "year": y, "ok": ok, "rowCount": rc, "n_rows": len(rows)}
            if rows:
                fn = f"c{crop}_s{schema}_v{v}_{y}.json"
                blob = json.dumps(rows, ensure_ascii=False)
                open(os.path.join(raw, fn), "w").write(blob)
                rec["file"] = fn; rec["sha256"] = hashlib.sha256(blob.encode()).hexdigest()
            idx["requests"].append(rec)
        tot = sum(r["n_rows"] for r in idx["requests"] if r["var"] == v)
        print(f"  var {v}: {tot} rows across {y0}-{y1}", flush=True)
    json.dump(idx, open(os.path.join(outdir, "collection_index.json"), "w"), indent=1)
    nz = sum(1 for r in idx["requests"] if r["ok"] and r["n_rows"] == 0)
    print(f"requests={len(idx['requests'])} with_rows={sum(1 for r in idx['requests'] if r['n_rows'])} "
          f"HTTP-ok-ZERO-rows={nz}")
