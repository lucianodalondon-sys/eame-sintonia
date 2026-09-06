#!/usr/bin/env python3
"""RT3-E6. The refresh path, driven with a patched urllib.request.urlopen, against a COPY.

Never touches CASES/. Builds REDTEAM/_lab/<scenario>/ as a byte copy of VITE-OIDIO-TOSCANA,
runs the SHIPPED CASES/collect_generic.py against the copy with the network replaced, then
asks the SHIPPED load_rows() what it believes afterwards.

Scenarios
  A  GOOD      the source replays exactly the rows already archived
  B  NULLS     HTTP 200, ok:true, FULL rowCount, every `val` null (the source's real silent
               failure shape, per collect_generic's own comment)
  C  DOWN      urlopen raises (network/DNS/500)
  D  PARTIAL   a GOOD refresh of only the last 2 years, the way an operator would run it

Questions asked after each: does the last good observation survive? is the hash chain intact?
is there any record that a refresh was attempted, or that it failed?
"""
import sys, os, json, glob, io, shutil, runpy, hashlib, datetime as dt, collections, traceback

HERE = os.path.dirname(os.path.abspath(__file__))
ENG = os.path.abspath(os.path.join(HERE, "..", "..", "ENGINE"))
CAS = os.path.abspath(os.path.join(HERE, "..", "..", "CASES"))
LAB = os.path.join(HERE, "_lab")
SRC = os.path.join(CAS, "VITE-OIDIO-TOSCANA")
COLLECTOR = os.path.join(CAS, "collect_generic.py")
CROP, SCHEMA, VAR = 3, 8, 39
sys.path.insert(0, ENG)
sys.path.insert(0, CAS)
import current_pressure as cp
import urllib.request

ORIG_IDX = json.load(open(os.path.join(SRC, "collection_index.json")))
ORIG_FILTER = {"survey_code": {"data": ORIG_IDX.get("codes") or []},
               "survey_var": {"data": [dict(v, id_survey_schema=SCHEMA)
                                       for v in (ORIG_IDX.get("vars") or [])]}}
YEARS = sorted({r["year"] for r in ORIG_IDX["requests"]})
Y0, Y1 = YEARS[0], YEARS[-1]


def stored_rows(var, year, case_dir=SRC):
    p = os.path.join(case_dir, "RAW", f"c{CROP}_s{SCHEMA}_v{var}_{year}.json")
    if not os.path.exists(p):
        return None
    return json.loads(open(p, "rb").read().decode("utf-8"))


class FakeResp(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def make_urlopen(mode):
    def _open(url, timeout=None):
        import urllib.parse as up
        q = up.parse_qs(up.urlparse(str(url)).query)
        var = int(q["survey_var"][0]); year = int(q["year"][0])
        rows = stored_rows(var, year)
        if mode == "DOWN":
            raise OSError("simulated: [Errno -3] Temporary failure in name resolution")
        if rows is None:
            body = {"data": {"ok": True, "rowCount": 0, "data": []}, "filter": ORIG_FILTER}
        elif mode == "GOOD":
            body = {"data": {"ok": True, "rowCount": len(rows), "data": rows},
                    "filter": ORIG_FILTER}
        elif mode == "NULLS":
            nulled = [dict(r, val=None) for r in rows]
            body = {"data": {"ok": True, "rowCount": len(rows), "data": nulled},
                    "filter": ORIG_FILTER}
        else:
            raise AssertionError(mode)
        return FakeResp(json.dumps(body, ensure_ascii=False).encode("utf-8"))
    return _open


def audit(case_dir, label):
    """What does the SHIPPED reader believe about this case directory now?"""
    a = {"SCENARIO": label}
    idxp = os.path.join(case_dir, "collection_index.json")
    idx = json.load(open(idxp, encoding="utf-8"))
    reqs = idx["requests"]
    by_file = {r["file"]: r.get("sha256") for r in reqs if r.get("file")}
    on_disk = sorted(os.path.basename(f) for f in glob.glob(os.path.join(case_dir, "RAW", "*.json")))
    ok = mism = 0
    mism_names = []
    for b in on_disk:
        if b not in by_file or not by_file[b]:
            continue
        h = hashlib.sha256(open(os.path.join(case_dir, "RAW", b), "rb").read()).hexdigest()
        if h == by_file[b]:
            ok += 1
        else:
            mism += 1; mism_names.append(b)
    unindexed = [b for b in on_disk if b not in by_file]
    a["INDEX"] = {
        "N_REQUESTS": len(reqs),
        "N_WITH_FILE": sum(1 for r in reqs if r.get("file")),
        "N_ok_false": sum(1 for r in reqs if r.get("ok") is False),
        "N_REFUSED_WRITE": sum(1 for r in reqs if r.get("REFUSED_WRITE")),
        "TOP_LEVEL_KEYS": sorted(idx.keys()),
        "HAS_ANY_TIMESTAMP_FIELD": sorted(
            k for k in idx.keys()
            if any(t in k.upper() for t in ("TIME", "DATE", "AT", "COLLECT", "REFRESH", "STAMP"))),
        "REQUEST_KEYS_SEEN": sorted({k for r in reqs for k in r.keys()}),
    }
    a["HASH_CHAIN"] = {"N_FILES_ON_DISK": len(on_disk), "N_VERIFIED_OK": ok,
                       "N_MISMATCH": mism, "MISMATCHED": mism_names[:6],
                       "N_ON_DISK_BUT_UNINDEXED_SO_UNCHECKED": len(unindexed),
                       "UNINDEXED_SAMPLE": unindexed[:6]}
    try:
        rows, scale, meta = cp.load_rows(case_dir, VAR)
        readable = [r for r in rows if cp.read_value(r, scale, meta["VALUE_MODE"]) is not None]
        last = max((r["_d"] for r in readable), default=None)
        a["LOAD_ROWS"] = {"RESULT": "OK", "N_ROWS": len(rows), "N_READABLE": len(readable),
                          "VALUE_MODE": meta["VALUE_MODE"],
                          "LAST_READABLE_OBSERVATION": last.isoformat() if last else None}
        as_of = dt.date(2026, 9, 6)
        r = cp.current_pressure(case_dir, VAR, as_of, _pre=(rows, scale, meta))
        st = collections.Counter(v["STATE"] for v in r["PROVINCES"].values())
        a["CURRENT_PRESSURE"] = {"RESULT": "OK", "DATA_LATENCY_DAYS": r["DATA_LATENCY_DAYS"],
                                 "STATES": dict(st),
                                 "N_PUBLISHED_CLASSES": sum(
                                     n for s, n in st.items()
                                     if s in (cp.HIGHER, cp.TYPICAL, cp.LOWER))}
    except Exception as e:
        a["LOAD_ROWS"] = {"RESULT": f"{type(e).__name__}: {e}"}
        a["CURRENT_PRESSURE"] = {"RESULT": "not reached"}
    return a


OUT = {"BASELINE_UNTOUCHED_COPY": None, "SCENARIOS": {}}

shutil.rmtree(LAB, ignore_errors=True)
os.makedirs(LAB)

base = os.path.join(LAB, "BASE")
shutil.copytree(SRC, base)
OUT["BASELINE_UNTOUCHED_COPY"] = audit(base, "untouched copy of the shipped case")

for label, mode, yrange in (("A_GOOD", "GOOD", (Y0, Y1)),
                            ("B_NULLS", "NULLS", (Y0, Y1)),
                            ("C_DOWN", "DOWN", (Y0, Y1)),
                            ("D_PARTIAL_GOOD_LAST_2_YEARS", "GOOD", (Y1 - 1, Y1))):
    d = os.path.join(LAB, label)
    shutil.copytree(SRC, d)
    saved = urllib.request.urlopen
    urllib.request.urlopen = make_urlopen(mode)
    old_argv, old_out = sys.argv, sys.stdout
    sys.argv = ["collect_generic.py", d, str(CROP), str(SCHEMA),
                f"{yrange[0]}-{yrange[1]}", str(VAR)]
    cap = io.StringIO()
    sys.stdout = cap
    err = None
    try:
        runpy.run_path(COLLECTOR, run_name="__main__")
    except Exception:
        err = traceback.format_exc()[-900:]
    finally:
        sys.stdout = old_out
        sys.argv = old_argv
        urllib.request.urlopen = saved
    a = audit(d, label)
    a["COLLECTOR_STDOUT"] = cap.getvalue().strip().splitlines()[-6:]
    a["COLLECTOR_RAISED"] = err
    a["YEARS_REQUESTED"] = list(yrange)
    OUT["SCENARIOS"][label] = a

json.dump(OUT, open(os.path.join(HERE, "rt3_e6_refresh_lab.json"), "w"), indent=1, default=str)

b = OUT["BASELINE_UNTOUCHED_COPY"]
print("BASELINE  files=%s verified=%s mismatch=%s unchecked=%s | load=%s last_obs=%s latency=%s classes=%s"
      % (b["HASH_CHAIN"]["N_FILES_ON_DISK"], b["HASH_CHAIN"]["N_VERIFIED_OK"],
         b["HASH_CHAIN"]["N_MISMATCH"], b["HASH_CHAIN"]["N_ON_DISK_BUT_UNINDEXED_SO_UNCHECKED"],
         b["LOAD_ROWS"]["RESULT"], b["LOAD_ROWS"].get("LAST_READABLE_OBSERVATION"),
         b["CURRENT_PRESSURE"].get("DATA_LATENCY_DAYS"),
         b["CURRENT_PRESSURE"].get("N_PUBLISHED_CLASSES")))
print()
for k, a in OUT["SCENARIOS"].items():
    print("=" * 76)
    print(k, " years", a["YEARS_REQUESTED"])
    print("  index   : requests=%s with_file=%s ok_false=%s REFUSED_WRITE=%s"
          % (a["INDEX"]["N_REQUESTS"], a["INDEX"]["N_WITH_FILE"],
             a["INDEX"]["N_ok_false"], a["INDEX"]["N_REFUSED_WRITE"]))
    print("  hash    : on_disk=%s verified=%s MISMATCH=%s UNCHECKED(unindexed)=%s %s"
          % (a["HASH_CHAIN"]["N_FILES_ON_DISK"], a["HASH_CHAIN"]["N_VERIFIED_OK"],
             a["HASH_CHAIN"]["N_MISMATCH"], a["HASH_CHAIN"]["N_ON_DISK_BUT_UNINDEXED_SO_UNCHECKED"],
             a["HASH_CHAIN"]["MISMATCHED"]))
    print("  load    :", a["LOAD_ROWS"]["RESULT"],
          "| last_readable_obs =", a["LOAD_ROWS"].get("LAST_READABLE_OBSERVATION"))
    print("  publish :", a["CURRENT_PRESSURE"].get("RESULT"),
          "| latency =", a["CURRENT_PRESSURE"].get("DATA_LATENCY_DAYS"),
          "| classes =", a["CURRENT_PRESSURE"].get("N_PUBLISHED_CLASSES"),
          a["CURRENT_PRESSURE"].get("STATES"))
    print("  timestamp fields in index:", a["INDEX"]["HAS_ANY_TIMESTAMP_FIELD"] or "NONE")
    print("  stdout  :", a["COLLECTOR_STDOUT"])
