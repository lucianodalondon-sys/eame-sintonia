#!/usr/bin/env python3
"""
CERT-V2 / STEP 6 — AN EMPTY REFRESH IS NOT A ZERO, AND A FILE DATE IS NOT AN OBSERVATION DATE.

The arbiter's last finding was that a null refresh could overwrite the good archive with every
alarm silent. collect_generic.py was then given a REFUSED_WRITE guard. This file does not read
that guard; it RUNS the shipped collector, unchanged, against canned responses, on a small
case built from real bytes, and then asks load_rows() what it believes afterwards.

FOUR SCENARIOS, all through the real code path (runpy on CASES/collect_generic.py):
  A  GOOD_REFRESH    rows with readable values arrive for a new season
  B  EMPTY_REFRESH   HTTP 200, ok:true, FULL row count, every `val` null
  C  NETWORK_ERROR   the endpoint raises
  D  PARTIAL_REFRESH only one of the archived years is re-requested

AFTER EACH, the questions the mission asks by name:
  LAST_GOOD_OBSERVATION_AT   is the newest readable observation still there?
  REFRESH_ATTEMPT_AT         does anything record WHEN the refresh was tried?
  REFRESH_STATUS             does anything record that it FAILED?
  SOURCE_OBSERVED_AT         is latency measured from the evidence, or from the file?
  FILE_WRITTEN_AT            does the file mtime leak into any published number?
  HASH_CHAIN                 are the surviving raw files still hash-checked?

Out: p6_refresh_and_clock.json   (+ REFRESH-LAB/, a small versioned case built from real bytes)
"""
import json, os, sys, io, glob, shutil, hashlib, runpy, datetime as dt, time

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.path.join(HERE, "..", "ENGINE")
CASEDIR = os.path.join(HERE, "..", "CASES")
LAB = os.path.join(HERE, "REFRESH-LAB")
sys.path.insert(0, ENGINE)
sys.path.insert(0, CASEDIR)
import current_pressure as cp

SRC_CASE = os.path.join(CASEDIR, "FRUMENTO-SEPTORIA-TOSCANA")
CROP, SCHEMA, VAR = 19, 74, 372
KEEP_YEARS = [2023, 2024, 2025]
AS_OF = dt.date(2026, 9, 6)


def build_lab():
    """A small case made of REAL bytes: three seasons of the wheat archive, its real code
    table, and a correctly-hashed index. Small enough to version, real enough to test."""
    case = os.path.join(LAB, "CASE")
    if os.path.exists(case):
        shutil.rmtree(case)
    os.makedirs(os.path.join(case, "RAW"))
    src_idx = json.load(open(os.path.join(SRC_CASE, "collection_index.json")))
    idx = {"api": src_idx["api"], "crop": CROP, "schema": SCHEMA, "requests": [],
           "codes": src_idx.get("codes"), "vars": src_idx.get("vars")}
    for y in KEEP_YEARS:
        fn = f"c{CROP}_s{SCHEMA}_v{VAR}_{y}.json"
        src = os.path.join(SRC_CASE, "RAW", fn)
        if not os.path.exists(src):
            continue
        rows = json.load(open(src))
        blob = json.dumps(rows, ensure_ascii=False)
        open(os.path.join(case, "RAW", fn), "w").write(blob)
        idx["requests"].append({"var": VAR, "year": y, "ok": True, "rowCount": len(rows),
                                "n_rows": len(rows), "file": fn,
                                "sha256": hashlib.sha256(blob.encode()).hexdigest()})
    json.dump(idx, open(os.path.join(case, "collection_index.json"), "w"), indent=1)
    return case


def canned(shape, template_rows):
    """Build the three response shapes the source really produces."""
    if shape == "GOOD":
        rows = []
        for r in template_rows[:200]:
            q = dict(r)
            q["date"] = "2026-05-20"
            q["val"] = r.get("val") or "1599"
            rows.append(q)
        return {"data": {"ok": True, "rowCount": len(rows), "data": rows},
                "filter": {}}
    if shape == "EMPTY":
        rows = []
        for r in template_rows[:200]:
            q = dict(r)
            q["date"] = "2026-05-20"
            q["val"] = None
            rows.append(q)
        return {"data": {"ok": True, "rowCount": len(rows), "data": rows}, "filter": {}}
    raise ValueError(shape)


class FakeResp(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def run_collector(case, years, shape):
    """Run the SHIPPED collector with urlopen replaced. Nothing in CASES/ is edited."""
    import urllib.request
    tmpl = json.load(open(os.path.join(case, "RAW",
                                       f"c{CROP}_s{SCHEMA}_v{VAR}_{KEEP_YEARS[-1]}.json")))
    real = urllib.request.urlopen

    def fake(url, timeout=None):
        if shape == "ERROR":
            raise OSError("simulated endpoint failure")
        return FakeResp(json.dumps(canned(shape, tmpl)).encode())
    urllib.request.urlopen = fake
    argv = sys.argv
    sys.argv = ["collect_generic.py", case, str(CROP), str(SCHEMA),
                f"{years[0]}-{years[-1]}", str(VAR)]
    out = io.StringIO()
    so = sys.stdout
    sys.stdout = out
    try:
        runpy.run_path(os.path.join(CASEDIR, "collect_generic.py"), run_name="__main__")
    except SystemExit:
        pass
    finally:
        sys.stdout = so
        sys.argv = argv
        urllib.request.urlopen = real
    return out.getvalue()


def inspect(case, label):
    """What does the pipeline believe about this case now?"""
    idx = json.load(open(os.path.join(case, "collection_index.json")))
    raws = sorted(os.path.basename(p) for p in glob.glob(os.path.join(case, "RAW", "*.json")))
    listed = {r["file"] for r in idx["requests"] if r.get("file")}
    unhashed = [f for f in raws if f not in listed]
    rec = {"LABEL": label,
           "RAW_FILES_ON_DISK": raws,
           "FILES_LISTED_IN_INDEX": sorted(listed),
           "RAW_FILES_NO_LONGER_HASH_CHECKED": unhashed,
           "INDEX_REQUEST_KEYS": sorted({k for r in idx["requests"] for k in r}),
           "REFUSED_WRITE_RECORDS": [r for r in idx["requests"] if r.get("REFUSED_WRITE")],
           "HAS_REFRESH_ATTEMPT_AT": any("attempt" in k.lower()
                                         for r in idx["requests"] for k in r),
           "HAS_REFRESH_STATUS_FIELD": any(k.lower() in ("refresh_status", "status")
                                           for r in idx["requests"] for k in r),
           "HAS_COLLECTED_AT": any(k.lower().endswith("_at")
                                   for r in idx["requests"] for k in r)}
    try:
        rows, scale, meta = cp.load_rows(case, VAR)
        readable = [r for r in rows if cp.read_value(r, scale, meta["VALUE_MODE"]) is not None]
        last_good = max((r["_d"] for r in readable), default=None)
        last_any = max((r["_d"] for r in rows), default=None)
        rec.update({
            "LOAD_ROWS": "OK", "n_rows": len(rows), "n_readable": len(readable),
            "LAST_GOOD_OBSERVATION_AT": last_good.isoformat() if last_good else None,
            "LATEST_ROW_DATE_ANY": last_any.isoformat() if last_any else None,
            "HASHES_VERIFIED": len(meta["hashes"])})
        r = cp.current_pressure(case, VAR, AS_OF)
        rec["DATA_LATENCY_DAYS"] = r.get("DATA_LATENCY_DAYS")
        rec["PUBLISHED_STATES"] = {p: v.get("STATE") for p, v in r["PROVINCES"].items()}
        rec["N_CLASSED"] = sum(1 for v in r["PROVINCES"].values()
                               if v.get("STATE") in (cp.HIGHER, cp.TYPICAL, cp.LOWER))
    except Exception as e:
        rec["LOAD_ROWS"] = f"REFUSED: {type(e).__name__}: {str(e)[:200]}"
    return rec


def main():
    os.makedirs(LAB, exist_ok=True)
    out = {"AS_OF": AS_OF.isoformat(), "SCENARIOS": []}

    # ── baseline ───────────────────────────────────────────────────────────────────
    case = build_lab()
    base = inspect(case, "0_BASELINE_before_any_refresh")
    out["SCENARIOS"].append(base)

    # ── A good refresh of a NEW season ────────────────────────────────────────────
    case = build_lab()
    log = run_collector(case, [2026, 2026], "GOOD")
    a = inspect(case, "A_GOOD_REFRESH_new_season")
    a["COLLECTOR_STDOUT"] = log.strip().splitlines()
    out["SCENARIOS"].append(a)

    # ── B empty refresh: full rowcount, every value null ──────────────────────────
    case = build_lab()
    log = run_collector(case, [2026, 2026], "EMPTY")
    b = inspect(case, "B_EMPTY_REFRESH_full_rowcount_all_null")
    b["COLLECTOR_STDOUT"] = log.strip().splitlines()
    out["SCENARIOS"].append(b)

    # ── C network error ───────────────────────────────────────────────────────────
    case = build_lab()
    log = run_collector(case, [2026, 2026], "ERROR")
    c = inspect(case, "C_NETWORK_ERROR")
    c["COLLECTOR_STDOUT"] = log.strip().splitlines()
    out["SCENARIOS"].append(c)

    # ── D partial refresh: only the newest archived year is re-requested ──────────
    case = build_lab()
    log = run_collector(case, [KEEP_YEARS[-1], KEEP_YEARS[-1]], "EMPTY")
    d = inspect(case, "D_PARTIAL_REFRESH_only_one_archived_year_and_it_comes_back_empty")
    d["COLLECTOR_STDOUT"] = log.strip().splitlines()
    out["SCENARIOS"].append(d)

    # ── the clock: is latency measured from the evidence or from the file? ────────
    case = build_lab()
    victim = sorted(glob.glob(os.path.join(case, "RAW", "*.json")))[-1]
    old = dt.datetime(2001, 1, 1).timestamp()
    os.utime(victim, (old, old))
    before = cp.current_pressure(case, VAR, AS_OF).get("DATA_LATENCY_DAYS")
    now = time.time()
    os.utime(victim, (now, now))
    after = cp.current_pressure(case, VAR, AS_OF).get("DATA_LATENCY_DAYS")
    out["FILE_MTIME_DOES_NOT_LEAK"] = {
        "file": os.path.basename(victim),
        "latency_with_mtime_2001": before, "latency_with_mtime_now": after,
        "IDENTICAL": before == after,
        "READ": "if these differ, the freshness badge is reading the filesystem instead of "
                "the evidence."}

    # ── the clock: is AS_OF a constant? ──────────────────────────────────────────
    import gates as G
    import inspect as _i
    sig = _i.signature(G.evaluate)
    default_as_of = sig.parameters["as_of"].default
    lat_now = cp.current_pressure(case, VAR, AS_OF).get("DATA_LATENCY_DAYS")
    lat_plus_year = cp.current_pressure(case, VAR, AS_OF + dt.timedelta(days=365)).get(
        "DATA_LATENCY_DAYS")
    out["THE_CLOCK"] = {
        "gates.evaluate_default_as_of": str(default_as_of),
        "IS_A_HARDCODED_CONSTANT": isinstance(default_as_of, dt.date),
        "latency_at_that_constant": lat_now,
        "latency_one_year_later_same_archive": lat_plus_year,
        "READ": "gate H certifies DATA_LATENCY_DAYS <= 21. With as_of frozen at a constant in "
                "the source, the suite reports the same latency forever: on this archive it "
                "would still say the source is fresh in 2027, 2030 and 2040. Nothing in the "
                "suite reads a real clock, and nothing compares the archive to today."}

    # ── verdicts ─────────────────────────────────────────────────────────────────
    good_survives = all(
        s.get("LAST_GOOD_OBSERVATION_AT") == base.get("LAST_GOOD_OBSERVATION_AT")
        for s in (b, c, d))
    refused = bool(b.get("REFUSED_WRITE_RECORDS"))
    chain_broken = {s["LABEL"]: s["RAW_FILES_NO_LONGER_HASH_CHECKED"]
                    for s in out["SCENARIOS"] if s.get("RAW_FILES_NO_LONGER_HASH_CHECKED")}
    has_clock = any(s.get("HAS_REFRESH_ATTEMPT_AT") or s.get("HAS_REFRESH_STATUS_FIELD")
                    or s.get("HAS_COLLECTED_AT") for s in out["SCENARIOS"])

    out["VERDICT"] = {
        "EMPTY_REFRESH_IS_REFUSED_A_WRITE": refused,
        "LAST_GOOD_OBSERVATION_SURVIVES_EVERY_FAILURE": good_survives,
        "HASH_CHAIN_BROKEN_BY_REFRESH": chain_broken,
        "ANY_REFRESH_CLOCK_FIELD_EXISTS": has_clock,
        "FILE_MTIME_DOES_NOT_LEAK_INTO_LATENCY": out["FILE_MTIME_DOES_NOT_LEAK"]["IDENTICAL"],
        "AS_OF_IS_A_HARDCODED_CONSTANT": out["THE_CLOCK"]["IS_A_HARDCODED_CONSTANT"],
        "REFRESH_FAIL_CLOSED": "PASS" if (refused and good_survives and not chain_broken)
                               else "FAIL",
        "LATENCY_TRUTHFUL": "PASS" if (out["FILE_MTIME_DOES_NOT_LEAK"]["IDENTICAL"]
                                       and not out["THE_CLOCK"]["IS_A_HARDCODED_CONSTANT"])
                            else "FAIL"}

    json.dump(out, open(os.path.join(HERE, "p6_refresh_and_clock.json"), "w"),
              indent=1, default=str)

    for s in out["SCENARIOS"]:
        print(f"--- {s['LABEL']}")
        print(f"    raw_on_disk={len(s['RAW_FILES_ON_DISK'])} listed_in_index={len(s['FILES_LISTED_IN_INDEX'])} "
              f"NO_LONGER_HASH_CHECKED={s['RAW_FILES_NO_LONGER_HASH_CHECKED']}")
        print(f"    refused_write={len(s['REFUSED_WRITE_RECORDS'])} "
              f"last_good={s.get('LAST_GOOD_OBSERVATION_AT')} "
              f"n_readable={s.get('n_readable')} latency={s.get('DATA_LATENCY_DAYS')} "
              f"classed={s.get('N_CLASSED')}")
    print("\nFILE_MTIME_DOES_NOT_LEAK:", json.dumps(out["FILE_MTIME_DOES_NOT_LEAK"]))
    print("THE_CLOCK:", json.dumps({k: v for k, v in out["THE_CLOCK"].items() if k != "READ"}))
    print("\nVERDICT:", json.dumps({k: v for k, v in out["VERDICT"].items()}, indent=1))


if __name__ == "__main__":
    main()
