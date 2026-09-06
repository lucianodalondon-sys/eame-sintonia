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
        top_ok = js.get("ok") if isinstance(js, dict) else None
        d = js.get("data") if isinstance(js, dict) else js
        rows = (d.get("data") or []) if isinstance(d, dict) else (d if isinstance(d, list) else [])
        ok = (d.get("ok") if isinstance(d, dict) else True)
        msg = (d.get("message") if isinstance(d, dict) else None) or (
              js.get("message") if isinstance(js, dict) else None)
        non_null = sum(1 for r in rows if isinstance(r, dict) and r.get("val") not in (None, ""))
        # THREE silent-failure shapes, all of which arrive as HTTP 200. Any of them must be read
        # as FAILURE, never as "no disease":
        #   1. rowCount 0                                        (the difesa/tipo_elab trap)
        #   2. full rowCount, every value null                   (a variable that is not in this
        #      schema, or a measurement column the source dropped)
        #   3. top-level ok:false carrying a human message       (season not started, bad crop)
        failure = None
        if top_ok is False or ok is False:
            failure = f"SOURCE_SAID_NOT_OK: {msg or 'no message'}"
        elif not rows:
            failure = "ZERO_ROWS_WITH_HTTP_200"
        elif non_null == 0:
            failure = "FULL_ROWCOUNT_BUT_EVERY_VALUE_NULL"
        return {"HTTP": 200, "ok": bool(ok) and failure is None, "n_rows": len(rows),
                "non_null_values": non_null, "top_level_ok": top_ok, "server_message": msg,
                "SILENT_FAILURE": failure, "bytes": len(body),
                "seconds": round(time.time() - t0, 2), "rows": rows,
                "sha256": hashlib.sha256(body).hexdigest()}
    except Exception as e:
        return {"HTTP": None, "ok": False, "error": f"{type(e).__name__}: {e}",
                "seconds": round(time.time() - t0, 2), "rows": []}

if __name__ == "__main__":
    # The third entry is a deliberate NEGATIVE CONTROL, and it is the most useful line in this
    # probe. var 50 does not exist in crop 3 / schema 8, and the source answers HTTP 200 +
    # ok:true + the schema's FULL row skeleton with every value null. It shipped for a while as
    # a passing probe. It must trip the detector on every run; if it ever stops tripping, the
    # detector is broken, not the source.
    cases = [("VITE-OIDIO-TOSCANA", 3, 8, 39), ("OLIVO-BACTROCERA-TOSCANA", 2, 1, -1002),
             ("NEGATIVE-CONTROL-nonexistent-var", 3, 8, 50)]
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
                     "stored_n_rows": stored, "non_null_values": r.get("non_null_values"),
                     "SILENT_FAILURE": r.get("SILENT_FAILURE"), "server_message": r.get("server_message"),
                     "delta_rows": (r.get("n_rows") or 0) - stored if stored is not None else None,
                     "latest_observation": dates[-1] if dates else None,
                     "error": r.get("error")}
        print(f"{name:28s} HTTP={r.get('HTTP')} ok={r['ok']} rows={r.get('n_rows')} "
              f"non_null={r.get('non_null_values')} stored={stored} "
              f"latest={dates[-1] if dates else None} {r['seconds']}s"
              + (f"  <-- {r['SILENT_FAILURE']}" if r.get("SILENT_FAILURE") else ""))
    json.dump(rep, open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     "automation_probe.json"), "w"), indent=1)
