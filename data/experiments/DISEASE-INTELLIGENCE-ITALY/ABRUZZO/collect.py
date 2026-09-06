#!/usr/bin/env python3
"""
Abruzzo AgroAmbiente — a SECOND Italian instance of the same platform and the same schema
as Toscana. Collected to test whether the Toscana 31-May relationship replicates WITHIN
Italy on an independent region.

It is much thinner than Toscana (~500 observations/season vs ~2,000, and only 2020-2026),
so it cannot carry a full horizon curve: with a minimum training set of 5, seven seasons
leave about two scoreable years. What it CAN do is test the DIRECTION of the relationship
independently, which is reported as exactly that and nothing more.
"""
import json, os, time, urllib.request, urllib.parse, hashlib
ROOT = os.path.dirname(os.path.abspath(__file__)); RAW = os.path.join(ROOT, "RAW")
os.makedirs(RAW, exist_ok=True)
API = "https://agroambiente.regione.abruzzo.it/api/dati/get_aedita_data"
YEARS = list(range(2018, 2027))
VARS = [34, 36, 333]

def fetch(p, tries=4):
    q = urllib.parse.urlencode(p)
    for i in range(tries):
        try:
            with urllib.request.urlopen(f"{API}?{q}", timeout=120) as r:
                return json.load(r)
        except Exception as e:
            if i == tries - 1: return {"_error": str(e)[:160]}
            time.sleep(3 * (i + 1))

idx = {"api": API, "requests": []}
codes = None
for v in VARS:
    for y in YEARS:
        js = fetch({"tipo_elab": "elab_pivot", "year": y, "crop": 3, "survey_schema": 7,
                    "survey_var": v, "difesa": "all", "week": "all", "cultivar": "all",
                    "area": "all", "accesso": "all", "user_access": "all"})
        d = js.get("data") if isinstance(js, dict) else None
        rows = d if isinstance(d, list) else ((d or {}).get("data") or [])
        rc = (d or {}).get("rowCount") if isinstance(d, dict) else len(rows)
        rec = {"var": v, "year": y, "rowCount": rc, "n_rows": len(rows)}
        if codes is None and isinstance(js, dict) and js.get("filter", {}).get("survey_code"):
            codes = js["filter"]["survey_code"]["data"]
        if rows:
            fn = f"Peronospora_v{v}_all_{y}.json"
            blob = json.dumps(rows, ensure_ascii=False)
            open(os.path.join(RAW, fn), "w").write(blob)
            rec["file"] = fn; rec["sha256"] = hashlib.sha256(blob.encode()).hexdigest()
        idx["requests"].append(rec)
        print(f"  v{v} {y}: {len(rows)} rows", flush=True)
idx["survey_codes"] = codes
json.dump(idx, open(os.path.join(ROOT, "collection_index.json"), "w"), indent=1)
nz = sum(1 for r in idx["requests"] if r["n_rows"] == 0)
print(f"requests={len(idx['requests'])} zero-row={nz}")
