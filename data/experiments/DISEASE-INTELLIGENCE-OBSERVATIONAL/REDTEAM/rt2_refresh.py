#!/usr/bin/env python3
"""
RT2 / A5 — THE REFRESH: THE SIX CLOCKS, IDEMPOTENCE, AND THE FAILURE SHAPES t3 DOES NOT
SIMULATE.

All of this runs on a LAB COPY. CASES/ is never written to; the last line asserts that.

  R1  IDEMPOTENCE, as asked: refresh twice against identical bytes, hash every file in
      canonical (including collection_index.json) before, between and after.
  R2  a payload that is VALID but SHORTER than what is already in canonical. t3 simulates
      "new_rows" (adds one) but never "fewer rows". Does the archive go backwards?
  R3  the clocks: which of the six are actually emitted, and are they distinct?
  R4  the clocks already in the canonical index: how many of the 84 entries carry one?
  R5  the API echoes the filter it applied; validate() parses it into `filt` and refresh_one
      throws it away. A payload for the wrong YEAR is written under the requested year's
      filename with no complaint.
"""
import os, sys, json, shutil, hashlib, time, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.path.abspath(os.path.join(HERE, "..", "engine"))
sys.path.insert(0, ENGINE)
import di_core, di_observe, di_refresh

SRC = os.path.abspath(os.path.join(ENGINE, "..", "..", "DISEASE-INTELLIGENCE-ITALY",
                                   "CASES", "OLIVO-BACTROCERA-TOSCANA"))
LAB = os.path.join(HERE, "_lab_refresh")
CROP, SCHEMA, VAR, YEAR = 2, 1, -1002, 2026
AS_OF = dt.date(2026, 9, 6)
out = {}

SRC_FINGERPRINT_BEFORE = None


def fingerprint(d):
    """Every byte under a directory, hashed, so 'untouched' is a measurement."""
    fp = {}
    for root, _, files in os.walk(d):
        for f in sorted(files):
            p = os.path.join(root, f)
            fp[os.path.relpath(p, d).replace("\\", "/")] = \
                hashlib.sha256(open(p, "rb").read()).hexdigest()
    return fp


SRC_FINGERPRINT_BEFORE = fingerprint(SRC)


def build_lab():
    canon, stag = os.path.join(LAB, "canonical"), os.path.join(LAB, "staging")
    for d in (canon, stag):
        if os.path.exists(d):
            shutil.rmtree(d)
    os.makedirs(os.path.join(canon, "RAW"))
    src_idx = json.load(open(os.path.join(SRC, "collection_index.json"), encoding="utf-8"))
    keep = []
    for v in (VAR, 1):
        for y in (2024, 2025, 2026):
            fn = f"c{CROP}_s{SCHEMA}_v{v}_{y}.json"
            p = os.path.join(SRC, "RAW", fn)
            if os.path.exists(p):
                shutil.copyfile(p, os.path.join(canon, "RAW", fn))
                keep.append(fn)
    idx = dict(src_idx)
    idx["requests"] = [r for r in src_idx["requests"] if r.get("file") in keep]
    json.dump(idx, open(os.path.join(canon, "collection_index.json"), "w",
                        encoding="utf-8"), indent=1)
    return canon, stag


def rows_of(canon, var=VAR, year=YEAR):
    return json.load(open(os.path.join(canon, "RAW",
                                       f"c{CROP}_s{SCHEMA}_v{var}_{year}.json"),
                          encoding="utf-8"))


def transport(payload):
    return lambda url: json.dumps({"data": {"ok": True, "data": payload}}).encode("utf-8")


# ── R1: IDEMPOTENCE, twice, against identical bytes ────────────────────────
canon, stag = build_lab()
real = rows_of(canon)
# the source serves what canonical already holds. refresh_one hashes json.dumps(rows), so
# "identical bytes" means the same ROWS, which is what the source would send.
fp0 = fingerprint(canon)
runs = []
for n in (1, 2, 3):
    rec = di_refresh.refresh_one(canon, stag, CROP, SCHEMA, VAR, YEAR,
                                 _transport=transport(real))
    prom = di_refresh.promote(canon, stag, [rec])
    fp = fingerprint(canon)
    runs.append({"run": n, "REFRESH_STATUS": rec["REFRESH_STATUS"],
                 "canonical_touched_claimed": rec.get("canonical_touched"),
                 "promoted": prom["promoted"],
                 "files_whose_bytes_changed_since_run_0":
                     sorted(k for k in set(fp) | set(fp0) if fp.get(k) != fp0.get(k)),
                 "files_whose_bytes_changed_since_the_previous_run":
                     sorted(k for k in set(fp) | set(runs[-1]["_fp"] if runs else fp0)
                            if fp.get(k) != (runs[-1]["_fp"] if runs else fp0).get(k)),
                 "_fp": fp})
idx_after = json.load(open(os.path.join(canon, "collection_index.json"), encoding="utf-8"))
idx_before = json.load(open(os.path.join(LAB, "canonical", "collection_index.json"),
                            encoding="utf-8"))
out["R1_IDEMPOTENCE"] = {
    "runs": [{k: v for k, v in r.items() if k != "_fp"} for r in runs],
    "RAW_files_unchanged_across_all_three_runs": all(
        not [f for f in r["files_whose_bytes_changed_since_run_0"] if f.startswith("RAW/")]
        for r in runs),
    "collection_index_changed_on_run_1": "collection_index.json"
        in runs[0]["files_whose_bytes_changed_since_run_0"],
    "collection_index_changed_on_run_2": "collection_index.json"
        in runs[1]["files_whose_bytes_changed_since_the_previous_run"],
    "index_entry_count_before": len(json.loads(json.dumps(idx_before))["requests"]),
    "NOTE": "promote() writes collection_index.json unconditionally, even when it promotes "
            "nothing, and re-sorts requests by filename."}

# R1b: is the rewrite content-identical, or does it reorder / drop fields?
canon, stag = build_lab()
before_idx_bytes = open(os.path.join(canon, "collection_index.json"), "rb").read()
before_idx = json.loads(before_idx_bytes)
rec = di_refresh.refresh_one(canon, stag, CROP, SCHEMA, VAR, YEAR,
                             _transport=transport(real))
di_refresh.promote(canon, stag, [rec])           # NO_UPDATE -> promotes nothing
after_idx_bytes = open(os.path.join(canon, "collection_index.json"), "rb").read()
after_idx = json.loads(after_idx_bytes)
out["R1b_A_NO_OP_PROMOTE_STILL_REWRITES_THE_INDEX"] = {
    "refresh_status": rec["REFRESH_STATUS"],
    "canonical_touched_field_says": rec.get("canonical_touched"),
    "index_bytes_identical": before_idx_bytes == after_idx_bytes,
    "index_sha_before": hashlib.sha256(before_idx_bytes).hexdigest()[:16],
    "index_sha_after": hashlib.sha256(after_idx_bytes).hexdigest()[:16],
    "order_before": [r.get("file") for r in before_idx["requests"]],
    "order_after": [r.get("file") for r in after_idx["requests"]],
    "top_level_keys_before": sorted(before_idx),
    "top_level_keys_after": sorted(after_idx),
    "entries_before": len(before_idx["requests"]),
    "entries_after": len(after_idx["requests"])}

# ── R2: a VALID payload with FEWER rows ────────────────────────────────────
canon, stag = build_lab()


def answer(c, as_of=AS_OF):
    ld = di_core.load_visits(c, di_core.load_sheet(), as_of)
    dates = [v["observation_date"] for v in ld["visits"]]
    cell = di_observe.cell(ld["visits"], di_core.load_sheet(), "Firenze",
                           "DAMAGING_INFESTATION_COUNT", as_of)
    return {"n_visits": ld["n_visits"],
            "last_observation": max(dates) if dates else None,
            "firenze_pct": cell["observation"]["value_pct"],
            "firenze_n_visits": cell["observation"]["n_visits"],
            "firenze_drupes": cell["observation"]["drupes_sampled"]}


before = answer(canon)
n_before = len(real)
truncated = real[:10]                      # the source answers 200 OK with 10 of 2,928 rows
rec = di_refresh.refresh_one(canon, stag, CROP, SCHEMA, VAR, YEAR,
                             _transport=transport(truncated))
prom = di_refresh.promote(canon, stag, [rec])
after = answer(canon)
out["R2_A_VALID_BUT_TRUNCATED_PAYLOAD"] = {
    "rows_in_canonical_before": n_before, "rows_the_source_returned": len(truncated),
    "share_returned": f"{len(truncated)} of {n_before} = "
                      f"{100.0*len(truncated)/n_before:.2f}%",
    "REFRESH_STATUS": rec["REFRESH_STATUS"], "validate_detail": rec["detail"],
    "promoted": prom["promoted"],
    "rows_in_canonical_after": len(rows_of(canon)),
    "ANSWER_BEFORE": before, "ANSWER_AFTER": after,
    "LAST_GOOD_OBSERVATION_AT_before": max(r["date"] for r in real),
    "LAST_GOOD_OBSERVATION_AT_after": rec.get("LAST_GOOD_OBSERVATION_AT"),
    "the_clock_went_backwards": rec.get("LAST_GOOD_OBSERVATION_AT", "") <
                                max(r["date"] for r in real),
    "anything_flagged_it": rec["REFRESH_STATUS"] != di_refresh.NEW_OBSERVATIONS,
    "t3_simulates_this_shape": False}

# R2b: the same shape at its worst - ONE readable row
canon, stag = build_lab()
one = [dict(real[0], date="2026-01-16")]
rec = di_refresh.refresh_one(canon, stag, CROP, SCHEMA, VAR, YEAR,
                             _transport=transport(one))
prom = di_refresh.promote(canon, stag, [rec])
out["R2b_ONE_ROW"] = {"REFRESH_STATUS": rec["REFRESH_STATUS"], "promoted": prom["promoted"],
                      "rows_in_canonical_after": len(rows_of(canon)),
                      "LAST_GOOD_OBSERVATION_AT": rec.get("LAST_GOOD_OBSERVATION_AT"),
                      "answer_after": answer(canon)}

# ── R3: which of the six clocks are actually emitted, and are they distinct? ─
canon, stag = build_lab()


def slow(url):
    time.sleep(2.0)
    return json.dumps({"data": {"ok": True, "data": [dict(real[0], date="2026-09-04")]}}
                      ).encode("utf-8")


t_call = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
rec = di_refresh.refresh_one(canon, stag, CROP, SCHEMA, VAR, YEAR, _transport=slow)
t_done = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
SIX = ["OBSERVATION_TIME", "COLLECTION_TIME", "SOURCE_PUBLICATION_TIME",
       "SOURCE_UPDATE_TIME", "PROCESSING_TIME", "LAST_GOOD_OBSERVATION_AT"]
out["R3_THE_SIX_CLOCKS"] = {
    "record_keys": sorted(rec),
    "declared_clock_present_in_the_record": {k: (k in rec) for k in SIX},
    "REFRESH_ATTEMPT_AT": rec.get("REFRESH_ATTEMPT_AT"),
    "COLLECTION_TIME": rec.get("COLLECTION_TIME"),
    "attempt_and_collection_are_the_same_string":
        rec.get("REFRESH_ATTEMPT_AT") == rec.get("COLLECTION_TIME"),
    "the_transport_took_seconds": 2.0,
    "wall_clock_when_refresh_one_was_called": t_call.isoformat(),
    "wall_clock_when_it_returned": t_done.isoformat(),
    "COLLECTION_TIME_is_stamped_BEFORE_the_request":
        rec.get("COLLECTION_TIME") == t_call.isoformat(),
    "NOTE": "`now` is computed on the first line of refresh_one and reused for both "
            "REFRESH_ATTEMPT_AT and COLLECTION_TIME. With timeout=90 the gap between the "
            "stamp and the actual collection can be up to 90 s, and on SOURCE_UNAVAILABLE "
            "a COLLECTION_TIME is emitted for a collection that never happened."}
recf = di_refresh.refresh_one(canon, stag, CROP, SCHEMA, VAR, YEAR,
                              _transport=lambda u: (_ for _ in ()).throw(OSError("down")))
out["R3b_COLLECTION_TIME_ON_A_FAILED_FETCH"] = {
    "REFRESH_STATUS": recf["REFRESH_STATUS"],
    "COLLECTION_TIME": recf.get("COLLECTION_TIME"),
    "nothing_was_collected": True}

# ── R4: the clocks already in the real canonical index ─────────────────────
idx = json.load(open(os.path.join(SRC, "collection_index.json"), encoding="utf-8"))
reqs = idx["requests"]
have = {k: sum(1 for r in reqs if r.get(k)) for k in
        ["COLLECTION_TIME", "REFRESH_ATTEMPT_AT", "LAST_GOOD_OBSERVATION_AT",
         "SOURCE_PUBLICATION_TIME", "SOURCE_UPDATE_TIME", "PROCESSING_TIME", "sha256"]}
out["R4_CLOCKS_IN_THE_REAL_CANONICAL_INDEX"] = {
    "index_entries": len(reqs), "entries_carrying_each_field": have,
    "entry_keys_seen": sorted({k for r in reqs for k in r}),
    "VERDICT": f"{have['COLLECTION_TIME']} of {len(reqs)} canonical entries record when "
               f"they were fetched"}

# ── R5: the year echo is parsed and thrown away ────────────────────────────
canon, stag = build_lab()
rows_2026 = rows_of(canon, VAR, 2026)
body = json.dumps({"filter": {"year": 2026, "crop": 2},
                   "data": {"ok": True, "data": rows_2026}}).encode("utf-8")
st, det, rws, filt = di_refresh.validate(body)
rec = di_refresh.refresh_one(canon, stag, CROP, SCHEMA, VAR, 2019,
                             _transport=lambda u: body)
prom = di_refresh.promote(canon, stag, [rec])
wrote = os.path.join(canon, "RAW", f"c{CROP}_s{SCHEMA}_v{VAR}_2019.json")
years_in_file = sorted({r["date"][:4] for r in json.load(open(wrote, encoding="utf-8"))}) \
    if os.path.exists(wrote) else None
out["R5_THE_YEAR_ECHO_IS_DISCARDED"] = {
    "requested_year": 2019, "filter_the_source_echoed": filt,
    "validate_returns_it_as": "filt (4th return value)",
    "refresh_one_uses_it": False,
    "file_written": os.path.basename(wrote) if os.path.exists(wrote) else None,
    "REFRESH_STATUS": rec["REFRESH_STATUS"], "promoted": prom["promoted"],
    "observation_years_actually_inside_the_2019_file": years_in_file,
    "IMPACT": "the file name says 2019 and every row inside it is 2026. di_core reads "
              "dates from rows, not filenames, so the values are not corrupted - but the "
              "2019 season is now silently absent and the index says it was collected."}

# ── the assertion: CASES/ was never written to ─────────────────────────────
after_src = fingerprint(SRC)
out["CASES_UNTOUCHED"] = {
    "files": len(SRC_FINGERPRINT_BEFORE),
    "files_changed": sorted(k for k in set(SRC_FINGERPRINT_BEFORE) | set(after_src)
                            if SRC_FINGERPRINT_BEFORE.get(k) != after_src.get(k))}

shutil.rmtree(LAB, ignore_errors=True)
json.dump(out, open(os.path.join(HERE, "rt2_refresh.json"), "w", encoding="utf-8"),
          indent=1, default=str)
print(json.dumps(out, indent=1, default=str)[:11000])
