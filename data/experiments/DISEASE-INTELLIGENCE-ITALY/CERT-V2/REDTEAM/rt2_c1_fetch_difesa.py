#!/usr/bin/env python3
"""RT2-C1 — collect the DEFENCE REGIME stratum the pilot threw away.

CASES/collect_generic.py calls the source with difesa="all" for every case, so the archive on
disk carries no regime at all. The source itself offers the stratum:
    all | bio (Biologico) | integrato (Integrato) | integrato_volontario
and it is a real server-side filter (2025 var -1002: all=3553, bio=644, integrato=1897,
integrato_volontario=0, and a bogus value returns 0 rows with ok=true).

Bactrocera oleae is the case where the regime matters most: an organic grove has spinosad bait
and kaolin, an integrated grove has the full insecticide set. Pooling the two and then comparing
seasons is only valid if the mix is constant. This script downloads the id_survey membership of
each regime per season so the mix can be measured.

Writes CERT-V2/REDTEAM/DIFESA/difesa_map.json. Read-only against the source; nothing in
CASES/ or ENGINE/ is touched.
"""
import json, os, sys, time, urllib.request, urllib.parse

API = "https://agroambiente.info.regione.toscana.it/agro18/api/dati/get_aedita_data"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "DIFESA")
CROP, SCHEMA, VAR = 2, 1, -1002
REGIMES = ("bio", "integrato", "integrato_volontario")


def fetch(year, difesa, tries=3):
    p = {"tipo_elab": "elab_pivot", "year": year, "crop": CROP, "survey_schema": SCHEMA,
         "survey_var": VAR, "difesa": difesa, "week": "all", "cultivar": "all",
         "area": "all", "accesso": "all", "user_access": "all"}
    for i in range(tries):
        try:
            with urllib.request.urlopen(API + "?" + urllib.parse.urlencode(p), timeout=120) as r:
                js = json.load(r)
            d = js.get("data") or {}
            return bool(d.get("ok")), d.get("rowCount"), (d.get("data") or [])
        except Exception as e:
            if i == tries - 1:
                return False, None, []
            time.sleep(4 * (i + 1))


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    m = {}
    for y in range(2006, 2027):
        row = {}
        for reg in REGIMES:
            ok, rc, rows = fetch(y, reg)
            ids = [str(r["id_survey"]) for r in rows if isinstance(r, dict) and r.get("id_survey")]
            row[reg] = {"ok": ok, "rowCount": rc, "n": len(ids), "ids": ids}
            print(f"  {y} {reg:22s} ok={ok} n={len(ids)}", flush=True)
            time.sleep(1)
        m[str(y)] = row
    json.dump(m, open(os.path.join(OUT, "difesa_map.json"), "w"), indent=0)
    print("written", os.path.join(OUT, "difesa_map.json"))
