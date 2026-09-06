#!/usr/bin/env python3
"""
Toscana AgroAmbiente collector — recounts from the API, inherits no number.

Two things this must not do:
  1. Trust HTTP 200. The API returns 200 + ok:true + rowCount:0 for difesa=0. Every
     response is checked for rowCount and the row count is recorded per request.
  2. Trust a hard-coded code->label map. The previous session recorded
     49=nessuna/50=bassa/51=media/52=alta; the API's own filter block says
     50=media and 51=bassa. Codes are therefore re-read from the API PER YEAR and
     stored alongside the data, so a later relabelling by the source is visible.
"""
import json, os, sys, time, urllib.request, urllib.parse, hashlib

ROOT = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(ROOT, "RAW"); os.makedirs(RAW, exist_ok=True)
API = "https://agroambiente.info.regione.toscana.it/agro18/api/dati/get_aedita_data"

# crop 3 = Vite. Schemas discovered from the API's own filter block.
SCHEMAS = {4: "Fenologia", 5: "Lobesia", 6: "Botrite", 7: "Peronospora",
           8: "Oidio", 9: "AltriInsetti", 59: "Acari", 77: "BlackRot", 87: "Halyomorpha"}
# vars discovered per schema at runtime
YEARS = list(range(2006, 2027))
REGIMES = ["all", "bio", "integrato", "integrato_volontario"]

def fetch(params, tries=4):
    q = urllib.parse.urlencode(params)
    for i in range(tries):
        try:
            with urllib.request.urlopen(f"{API}?{q}", timeout=120) as r:
                return json.load(r)
        except Exception as e:
            if i == tries - 1:
                return {"_error": str(e)[:200]}
            time.sleep(4 * (i + 1))

def unwrap(js):
    """Returns (ok, rowCount, rows, filter_block). Never assumes 200 means data."""
    if not isinstance(js, dict) or "_error" in js:
        return False, None, [], None
    d = js.get("data")
    fb = js.get("filter")
    if isinstance(d, dict):
        return bool(d.get("ok")), d.get("rowCount"), (d.get("data") or []), fb
    if isinstance(d, list):
        return True, len(d), d, fb
    return False, None, [], fb

def vars_for(schema, year=2023):
    js = fetch({"tipo_elab": "elab_pivot", "year": year, "crop": 3,
                "survey_schema": schema, "difesa": "all", "week": "all"})
    fb = js.get("filter") if isinstance(js, dict) else None
    if not fb: return [], []
    vs = [v for v in fb.get("survey_var", {}).get("data", []) if v["id_survey_schema"] == schema]
    codes = fb.get("survey_code", {}).get("data", [])
    return vs, codes

if __name__ == "__main__":
    only = sys.argv[1] if len(sys.argv) > 1 else None
    index = {"api": API, "crop": 3, "requests": [], "schemas": {}}
    for sch, name in SCHEMAS.items():
        if only and only != name: continue
        vs, codes = vars_for(sch)
        index["schemas"][name] = {
            "id": sch,
            "vars": [{"id": v["id_survey_var"], "name": v["var_name"],
                      "widget": v["widget"], "description": v.get("description")} for v in vs],
            "codes": [{"code": c["id_survey_code"], "var": c["id_survey_var"],
                       "order_n": c.get("order_n"), "label": c["name"]} for c in codes],
        }
        print(f"\n=== {name} (schema {sch}) — {len(vs)} vars", flush=True)
        for v in vs:
            vid = v["id_survey_var"]
            for regime in REGIMES:
                for y in YEARS:
                    p = {"tipo_elab": "elab_pivot", "year": y, "crop": 3,
                         "survey_schema": sch, "survey_var": vid,
                         "difesa": regime, "week": "all", "cultivar": "all",
                         "area": "all", "accesso": "all", "user_access": "all"}
                    js = fetch(p)
                    ok, rc, rows, _ = unwrap(js)
                    rec = {"schema": name, "schema_id": sch, "var_id": vid,
                           "var_name": v["var_name"], "regime": regime, "year": y,
                           "ok": ok, "rowCount": rc, "n_rows": len(rows)}
                    index["requests"].append(rec)
                    if rows:
                        fn = f"{name}_v{vid}_{regime}_{y}.json"
                        blob = json.dumps(rows, ensure_ascii=False)
                        open(os.path.join(RAW, fn), "w").write(blob)
                        rec["file"] = fn
                        rec["sha256"] = hashlib.sha256(blob.encode()).hexdigest()
            tot = sum(r["n_rows"] for r in index["requests"] if r["var_id"] == vid)
            print(f"   var {vid:4d} {v['var_name']:26s} total rows across all years/regimes = {tot}", flush=True)
        json.dump(index, open(os.path.join(ROOT, "collection_index.json"), "w"), indent=1)
    json.dump(index, open(os.path.join(ROOT, "collection_index.json"), "w"), indent=1)
    n_ok = sum(1 for r in index["requests"] if r["n_rows"] > 0)
    n_zero = sum(1 for r in index["requests"] if r["ok"] and r["n_rows"] == 0)
    print(f"\nrequests={len(index['requests'])}  with_rows={n_ok}  "
          f"HTTP-ok-but-ZERO-rows={n_zero}  (the trap: ok=true is not data)")
