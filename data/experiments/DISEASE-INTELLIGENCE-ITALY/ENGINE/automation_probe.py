#!/usr/bin/env python3
"""FASE 6 — AUTOMATION, measured not asserted. Can this refresh without a research project?
One probe, identical for every case: re-request the CURRENT season and compare to what is stored."""
import json, sys, os, time, urllib.request, hashlib, datetime as dt, collections
API = "https://agroambiente.info.regione.toscana.it/agro18/api/dati/get_aedita_data"

def fetch(crop, schema, var, year, timeout=90):
    import urllib.parse
    url = API + "?" + urllib.parse.urlencode({
        "tipo_elab": "elab_pivot", "year": year, "crop": crop, "survey_schema": schema,
        "survey_var": var, "difesa": "all", "week": "all", "cultivar": "all",
        "area": "all", "accesso": "all", "user_access": "all"})
    t0 = time.time()
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            body = r.read()
        js = json.loads(body)
        d = js.get("data") if isinstance(js, dict) else js
        rows = d.get("data") if isinstance(d, dict) else (d if isinstance(d, list) else [])
        ok = (d.get("ok") if isinstance(d, dict) else True)
        return {"HTTP": 200, "ok": bool(ok), "n_rows": len(rows), "bytes": len(body),
                "seconds": round(time.time() - t0, 2), "rows": rows,
                "sha256": hashlib.sha256(body).hexdigest()}
    except Exception as e:
        return {"HTTP": None, "ok": False, "error": f"{type(e).__name__}: {e}",
                "seconds": round(time.time() - t0, 2), "rows": []}

if __name__ == "__main__":
    cases = [("VITE-OIDIO-TOSCANA", 3, 8, 39), ("OLIVO-BACTROCERA-TOSCANA", 2, 1, -1002),
             ("VITE-PERONOSPORA-TOSCANA", 3, 8, 50)]
    year = int(sys.argv[1]) if len(sys.argv) > 1 else 2026
    rep = {}
    for name, crop, schema, var in cases:
        r = fetch(crop, schema, var, year)
        stored = None
        p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                         "CASES", name, "RAW", f"c{crop}_s{schema}_v{var}_{year}.json")
        if os.path.exists(p): stored = len(json.load(open(p)))
        dates = sorted({x.get("date") for x in r["rows"] if x.get("date")})
        rep[name] = {"crop": crop, "schema": schema, "var": var, "year": year,
                     "HTTP": r.get("HTTP"), "ok": r["ok"], "n_rows": r.get("n_rows"),
                     "seconds": r["seconds"], "bytes": r.get("bytes"),
                     "stored_n_rows": stored, "delta_rows": (r.get("n_rows") or 0) - stored if stored is not None else None,
                     "latest_observation": dates[-1] if dates else None,
                     "error": r.get("error")}
        print(f"{name:28s} HTTP={r.get('HTTP')} ok={r['ok']} rows={r.get('n_rows')} "
              f"stored={stored} latest={dates[-1] if dates else None} {r['seconds']}s")
    json.dump(rep, open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     "automation_probe.json"), "w"), indent=1)
