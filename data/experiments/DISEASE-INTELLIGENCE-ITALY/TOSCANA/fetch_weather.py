#!/usr/bin/env python3
"""
Tuscan daily weather from NASA POWER (MERRA-2).

PROVENANCE, DECLARED: this is NOT ERA5. open-meteo's ERA5 archive rate-limited every
attempt in this session (HTTP 429 on all retries across three runs), so the provider was
changed rather than the work stalled. NASA POWER serves MERRA-2 reanalysis. Each written
file carries a _provenance block saying so, because a result computed on MERRA-2 is not
interchangeable with the ERA5-based Veneto and Andalucia work.

Points sit inside the Tuscan provinces that actually appear in the AgroAmbiente vine data
(nome_area), not generic Tuscany.
"""
import json, urllib.request, time, os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
OUTD = os.path.join(ROOT, "WEATHER"); os.makedirs(OUTD, exist_ok=True)
PTS = [("SIENA_CHIANTI", 43.42, 11.33), ("FIRENZE_CHIANTI", 43.55, 11.30),
       ("AREZZO_VALDICHIANA", 43.32, 11.78), ("GROSSETO_MAREMMA", 42.77, 11.11),
       ("LIVORNO_BOLGHERI", 43.20, 10.60), ("PISA_COLLINE", 43.55, 10.65),
       ("LUCCA_COLLINE", 43.87, 10.50), ("PISTOIA", 43.93, 10.92)]
FILL = -999.0

for name, la, lo in PTS:
    dest = os.path.join(OUTD, f"era5_{name}.json")   # filename kept for reader compatibility
    if os.path.exists(dest):
        print(name, "present", flush=True); continue
    url = ("https://power.larc.nasa.gov/api/temporal/daily/point?"
           "parameters=PRECTOTCORR,T2M,T2M_MIN,T2M_MAX,RH2M&community=AG"
           f"&longitude={lo}&latitude={la}&start=19900101&end=20260930&format=JSON")
    for i in range(1, 7):
        try:
            with urllib.request.urlopen(url, timeout=300) as r:
                js = json.load(r)
            p = js["properties"]["parameter"]
            days = sorted(p["T2M"].keys())
            def col(k): return [None if p[k][d] <= -900 else p[k][d] for d in days]
            out = {"latitude": la, "longitude": lo,
                   "_point": {"name": name, "lat": la, "lon": lo},
                   "_provenance": {"source": "NASA POWER", "model": "MERRA-2 reanalysis",
                                   "class": "REANALYSIS", "is_not": "ERA5",
                                   "api": "power.larc.nasa.gov",
                                   "why_not_era5": "open-meteo ERA5 archive returned HTTP 429 on every attempt"},
                   "daily": {"time": [f"{d[:4]}-{d[4:6]}-{d[6:8]}" for d in days],
                             "precipitation_sum": col("PRECTOTCORR"),
                             "temperature_2m_mean": col("T2M"),
                             "temperature_2m_min": col("T2M_MIN"),
                             "temperature_2m_max": col("T2M_MAX"),
                             "relative_humidity_2m_mean": col("RH2M")}}
            nn = sum(1 for x in out["daily"]["precipitation_sum"] if x is None)
            json.dump(out, open(dest, "w"))
            print(f"{name} OK days={len(days)} nulls={nn} {days[0]}..{days[-1]}", flush=True)
            break
        except Exception as e:
            print(name, "attempt", i, ":", str(e)[:70], flush=True); time.sleep(30)
    time.sleep(6)
print("WEATHER COLLECTION DONE")
