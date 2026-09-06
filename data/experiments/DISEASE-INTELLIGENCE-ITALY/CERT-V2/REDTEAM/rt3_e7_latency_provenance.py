#!/usr/bin/env python3
"""RT3-E7. What is DATA_LATENCY_DAYS actually made of? Proved by corrupting COPIES, not by
reading the source. And what happens to gate H's 'latency <= 21 days' as real time passes?

Copies live under REDTEAM/_lat/. CASES/ is never touched.
"""
import sys, os, json, glob, shutil, time, datetime as dt, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ENG = os.path.abspath(os.path.join(HERE, "..", "..", "ENGINE"))
CAS = os.path.abspath(os.path.join(HERE, "..", "..", "CASES"))
sys.path.insert(0, ENG)
sys.path.insert(0, CAS)
import current_pressure as cp

SRC = os.path.join(CAS, "VITE-OIDIO-TOSCANA")
VAR = 39
AS_OF = dt.date(2026, 9, 6)
LAT = os.path.join(HERE, "_lat")
OUT = {}


def latency_of(case_dir, as_of=AS_OF):
    try:
        r = cp.current_pressure(case_dir, VAR, as_of)
        st = collections.Counter(v["STATE"] for v in r["PROVINCES"].values())
        return {"DATA_LATENCY_DAYS": r["DATA_LATENCY_DAYS"], "STATES": dict(st),
                "N_CLASSED": sum(n for s, n in st.items()
                                 if s in (cp.HIGHER, cp.TYPICAL, cp.LOWER))}
    except Exception as e:
        return {"RAISED": f"{type(e).__name__}: {str(e)[:180]}"}


def newcopy(tag):
    d = os.path.join(LAT, tag)
    shutil.rmtree(d, ignore_errors=True)
    shutil.copytree(SRC, d)
    return d


def reindex(d):
    """Re-record sha256 for every RAW file so the hash guard does not mask the experiment."""
    import hashlib
    p = os.path.join(d, "collection_index.json")
    idx = json.load(open(p, encoding="utf-8"))
    for r in idx["requests"]:
        if r.get("file"):
            fp = os.path.join(d, "RAW", r["file"])
            if os.path.exists(fp):
                r["sha256"] = hashlib.sha256(open(fp, "rb").read()).hexdigest()
    json.dump(idx, open(p, "w", encoding="utf-8"), indent=1)


shutil.rmtree(LAT, ignore_errors=True)
os.makedirs(LAT)

# ---------------------------------------------------------------- 0. control
d0 = newcopy("C0_control")
OUT["C0_control"] = latency_of(d0)

# ---------------------------------------------------------------- 1. AS_OF sweep, archive frozen
sweep = {}
for k in (0, 7, 21, 22, 30, 60, 180, 365, 730):
    a = AS_OF + dt.timedelta(days=k)
    r = latency_of(d0, a)
    sweep[f"AS_OF+{k}d = {a.isoformat()}"] = {
        "DATA_LATENCY_DAYS": r.get("DATA_LATENCY_DAYS"),
        "GATE_H_FRESH_PREDICATE (latency<=21)":
            (r.get("DATA_LATENCY_DAYS") is not None and r["DATA_LATENCY_DAYS"] <= 21),
        "N_CLASSED": r.get("N_CLASSED"), "STATES": r.get("STATES")}
OUT["AS_OF_SWEEP_ARCHIVE_FROZEN"] = sweep

# ---------------------------------------------------------------- 2. backdate every file's mtime
d1 = newcopy("C1_backdated_mtime")
old = time.time() - 5 * 365 * 86400
for f in glob.glob(os.path.join(d1, "RAW", "*.json")) + [os.path.join(d1, "collection_index.json")]:
    os.utime(f, (old, old))
OUT["C1_backdated_mtime_5_years"] = {
    "MTIME_NOW": dt.datetime.fromtimestamp(
        os.path.getmtime(os.path.join(d1, "RAW",
                                      os.path.basename(sorted(glob.glob(os.path.join(d1, "RAW", "*.json")))[-1]))
                         )).date().isoformat(),
    **latency_of(d1),
    "INTERPRETATION": "if latency is unchanged, file mtime is NOT an input"}

# ---------------------------------------------------------------- 3. empty the value column
files = sorted(glob.glob(os.path.join(SRC, "RAW", f"*_v{VAR}_*.json")))
last_file = os.path.basename(files[-1])
d2 = newcopy("C2_val_column_nulled_latest_year")
p = os.path.join(d2, "RAW", last_file)
rows = json.loads(open(p, "rb").read().decode("utf-8"))
n_before = sum(1 for r in rows if r.get("val") not in (None, ""))
open(p, "w", encoding="utf-8").write(json.dumps([dict(r, val=None) for r in rows],
                                                ensure_ascii=False))
reindex(d2)
OUT["C2_val_column_nulled_latest_year"] = {
    "FILE": last_file, "N_ROWS": len(rows), "N_NON_NULL_BEFORE": n_before,
    "N_NON_NULL_AFTER": 0, **latency_of(d2),
    "INTERPRETATION": "rows and dates untouched; only readability removed"}

# ---------------------------------------------------------------- 4. delete the latest year file
d3 = newcopy("C3_latest_year_file_deleted")
os.remove(os.path.join(d3, "RAW", last_file))
OUT["C3_latest_year_file_deleted"] = {"REMOVED": last_file, **latency_of(d3)}

# ---------------------------------------------------------------- 5. backdate the OBSERVATION dates
d4 = newcopy("C4_observation_dates_shifted_back_400d")
p = os.path.join(d4, "RAW", last_file)
rows = json.loads(open(p, "rb").read().decode("utf-8"))
sh = []
for r in rows:
    try:
        r["date"] = (dt.date.fromisoformat(r["date"]) - dt.timedelta(days=400)).isoformat()
    except Exception:
        pass
    sh.append(r)
open(p, "w", encoding="utf-8").write(json.dumps(sh, ensure_ascii=False))
reindex(d4)
OUT["C4_observation_dates_shifted_back_400d"] = {"FILE": last_file, **latency_of(d4)}

# ---------------------------------------------------------------- 6. one fresh row rescues it
d5 = newcopy("C5_one_single_fresh_row_added")
p = os.path.join(d5, "RAW", last_file)
rows = json.loads(open(p, "rb").read().decode("utf-8"))
sh = []
for r in rows:
    try:
        r["date"] = (dt.date.fromisoformat(r["date"]) - dt.timedelta(days=400)).isoformat()
    except Exception:
        pass
    sh.append(r)
tmpl = dict(sh[0])
tmpl["date"] = AS_OF.isoformat()
sh.append(tmpl)
open(p, "w", encoding="utf-8").write(json.dumps(sh, ensure_ascii=False))
reindex(d5)
OUT["C5_one_single_fresh_row_added"] = {
    "FILE": last_file, "N_ROWS_AT_AS_OF": 1, "PROVINCE_OF_THAT_ROW": tmpl.get("nome_area"),
    **latency_of(d5),
    "INTERPRETATION": "ONE readable row anywhere in the region resets the freshness badge"}

# ---------------------------------------------------------------- 7. future-dated rows
d6 = newcopy("C6_future_dated_rows")
p = os.path.join(d6, "RAW", last_file)
rows = json.loads(open(p, "rb").read().decode("utf-8"))
fut = [dict(r, date=(AS_OF + dt.timedelta(days=90)).isoformat()) for r in rows[:50]]
open(p, "w", encoding="utf-8").write(json.dumps(rows + fut, ensure_ascii=False))
reindex(d6)
OUT["C6_future_dated_rows_added"] = {"N_FUTURE_ROWS_ADDED": 50, **latency_of(d6),
                                     "INTERPRETATION": "latency must not go negative"}

# ------------------------------------------- 8. is latency per-province or region-wide?
d7 = newcopy("C7_only_one_province_is_fresh")
for f in glob.glob(os.path.join(d7, "RAW", f"*_v{VAR}_*.json")):
    rows = json.loads(open(f, "rb").read().decode("utf-8"))
    out = []
    for r in rows:
        if r.get("nome_area") != "Siena":
            try:
                r["date"] = (dt.date.fromisoformat(r["date"]) - dt.timedelta(days=900)).isoformat()
            except Exception:
                pass
        out.append(r)
    open(f, "w", encoding="utf-8").write(json.dumps(out, ensure_ascii=False))
reindex(d7)
OUT["C7_only_Siena_kept_current"] = {
    **latency_of(d7),
    "INTERPRETATION": "one published DATA_LATENCY_DAYS covers the whole region; if it stays "
                      "small while 9 of 10 provinces are 900 days stale, the badge is a "
                      "region-wide maximum-freshness, not a per-cell one"}

json.dump(OUT, open(os.path.join(HERE, "rt3_e7_latency_provenance.json"), "w"), indent=1, default=str)
print(json.dumps(OUT, indent=1, default=str))
shutil.rmtree(LAT, ignore_errors=True)
