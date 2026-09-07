#!/usr/bin/env python3
"""
RT2 / A5b — TWO SHARPER VERSIONS OF THE REFRESH ATTACK.

  R1c  the first no-op promote against the REAL canonical index bytes. rt2_refresh.py built
       its lab index with json.dump(indent=1) and filenames that happened to be sorted, so
       it could not see a reordering. This copies the real file byte-for-byte first.

  R2c  the truncation that does NOT go silent. A payload that keeps only the rows reading
       zero passes every gate, so the tool publishes a number that is WRONG rather than
       publishing nothing.

  R6   the real archive's Dec/Jan mass, so the year-crossing defect can be scored on this
       case rather than in the abstract.
"""
import os, sys, json, shutil, hashlib, collections, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.path.abspath(os.path.join(HERE, "..", "engine"))
sys.path.insert(0, ENGINE)
import di_core, di_observe, di_refresh

SRC = os.path.abspath(os.path.join(ENGINE, "..", "..", "DISEASE-INTELLIGENCE-ITALY",
                                   "CASES", "OLIVO-BACTROCERA-TOSCANA"))
LAB = os.path.join(HERE, "_lab_refresh2")
CROP, SCHEMA, YEAR = 2, 1, 2026
AS_OF = dt.date(2026, 9, 6)
METRIC = "ACTIVE_INFESTATION_COUNT"
sheet = di_core.load_sheet()
out = {}


def build(var):
    canon, stag = os.path.join(LAB, "canonical"), os.path.join(LAB, "staging")
    for d in (canon, stag):
        if os.path.exists(d):
            shutil.rmtree(d)
    os.makedirs(os.path.join(canon, "RAW"))
    for v in (var, 1):
        for y in range(2006, 2027):
            fn = f"c{CROP}_s{SCHEMA}_v{v}_{y}.json"
            p = os.path.join(SRC, "RAW", fn)
            if os.path.exists(p):
                shutil.copyfile(p, os.path.join(canon, "RAW", fn))
    # the REAL index, copied byte for byte
    shutil.copyfile(os.path.join(SRC, "collection_index.json"),
                    os.path.join(canon, "collection_index.json"))
    return canon, stag


def transport(payload):
    return lambda url: json.dumps({"data": {"ok": True, "data": payload}}).encode("utf-8")


# ── R1c: no-op promote against the real index bytes ────────────────────────
canon, stag = build(-1001)
real_rows = json.load(open(os.path.join(canon, "RAW", f"c{CROP}_s{SCHEMA}_v-1001_{YEAR}.json"),
                           encoding="utf-8"))
before = open(os.path.join(canon, "collection_index.json"), "rb").read()
rec = di_refresh.refresh_one(canon, stag, CROP, SCHEMA, -1001, YEAR,
                             _transport=transport(real_rows))
prom = di_refresh.promote(canon, stag, [rec])
after = open(os.path.join(canon, "collection_index.json"), "rb").read()
jb, ja = json.loads(before), json.loads(after)
out["R1c_NO_OP_PROMOTE_ON_THE_REAL_INDEX"] = {
    "REFRESH_STATUS": rec["REFRESH_STATUS"],
    "canonical_touched_field_says": rec["canonical_touched"],
    "promoted": prom["promoted"],
    "index_bytes_identical": before == after,
    "index_bytes_before": len(before), "index_bytes_after": len(after),
    "sha_before": hashlib.sha256(before).hexdigest()[:16],
    "sha_after": hashlib.sha256(after).hexdigest()[:16],
    "entries_before": len(jb["requests"]), "entries_after": len(ja["requests"]),
    "first_five_files_before": [r.get("file") for r in jb["requests"]][:5],
    "first_five_files_after": [r.get("file") for r in ja["requests"]][:5],
    "entry_order_changed": [r.get("file") for r in jb["requests"]]
                           != [r.get("file") for r in ja["requests"]],
    "same_set_of_entries": {r.get("file") for r in jb["requests"]}
                           == {r.get("file") for r in ja["requests"]},
    "any_entry_lost_a_field": sorted(
        {k for r in jb["requests"] for k in r} - {k for r in ja["requests"] for k in r})}

# is the SECOND no-op a true no-op? (once sorted, it should be stable)
b2 = open(os.path.join(canon, "collection_index.json"), "rb").read()
rec2 = di_refresh.refresh_one(canon, stag, CROP, SCHEMA, -1001, YEAR,
                              _transport=transport(real_rows))
di_refresh.promote(canon, stag, [rec2])
a2 = open(os.path.join(canon, "collection_index.json"), "rb").read()
out["R1c_SECOND_NO_OP_IS_STABLE"] = {"identical": b2 == a2,
                                     "REFRESH_STATUS": rec2["REFRESH_STATUS"]}

# ── R2c: a truncation that publishes a WRONG number instead of nothing ─────
canon, stag = build(-1001)


def read(c, prov="Siena"):
    ld = di_core.load_visits(c, sheet, AS_OF)
    cell = di_observe.cell(ld["visits"], sheet, prov, METRIC, AS_OF)
    return {"value_pct": cell["observation"]["value_pct"],
            "infested": cell["observation"].get("infested_drupes"),
            "drupes": cell["observation"]["drupes_sampled"],
            "n_visits": cell["observation"]["n_visits"],
            "band": (cell["observation"].get("source_band") or {}).get("meaning"),
            "publishable": cell["quality"]["observation_publishable"],
            "trend": cell["analysis"]["observed_trend"],
            "last_observation": cell["observation"]["last_observation"]}


b_siena, b_pisa = read(canon, "Siena"), read(canon, "Pisa")
# the source answers 200 OK, ok:true, with only the rows whose value is zero
zeros = [r for r in real_rows if di_core._num(r.get("val")) == 0.0]
rec = di_refresh.refresh_one(canon, stag, CROP, SCHEMA, -1001, YEAR,
                             _transport=transport(zeros))
prom = di_refresh.promote(canon, stag, [rec])
a_siena, a_pisa = read(canon, "Siena"), read(canon, "Pisa")
out["R2c_A_TRUNCATION_THAT_PUBLISHES_A_WRONG_NUMBER"] = {
    "rows_in_the_real_2026_payload": len(real_rows),
    "rows_the_source_returned": len(zeros),
    "share": f"{len(zeros)} of {len(real_rows)} = {100.0*len(zeros)/len(real_rows):.1f}%",
    "REFRESH_STATUS": rec["REFRESH_STATUS"], "validate_detail": rec["detail"],
    "promoted": prom["promoted"],
    "SIENA_BEFORE": b_siena, "SIENA_AFTER": a_siena,
    "PISA_BEFORE": b_pisa, "PISA_AFTER": a_pisa,
    "anything_refused_it": rec["REFRESH_STATUS"] != di_refresh.NEW_OBSERVATIONS,
    "t3_simulates_this_shape": False}

# ── R6: the real archive's winter mass ─────────────────────────────────────
bymonth = collections.Counter()
byyearmonth = collections.Counter()
tot = 0
for fn in sorted(os.listdir(os.path.join(SRC, "RAW"))):
    if "_v-1001_" not in fn:
        continue
    for r in json.load(open(os.path.join(SRC, "RAW", fn), encoding="utf-8")):
        bymonth[r["date"][5:7]] += 1
        byyearmonth[r["date"][:7]] += 1
        tot += 1
dec_jan = bymonth["12"] + bymonth["01"]
out["R6_THE_REAL_ARCHIVES_WINTER_MASS"] = {
    "rows_in_the_ACTIVE_variable": tot,
    "rows_by_month": dict(sorted(bymonth.items())),
    "december_plus_january": f"{dec_jan} of {tot} = {100.0*dec_jan/tot:.3f}%",
    "VERDICT": "the year-crossing window defect is arithmetically real but this archive "
               "carries almost nothing in the crossing window, so on THIS case it is "
               "unreachable in practice"}

shutil.rmtree(LAB, ignore_errors=True)
json.dump(out, open(os.path.join(HERE, "rt2_refresh2.json"), "w", encoding="utf-8"),
          indent=1, default=str)
print(json.dumps(out, indent=1, default=str)[:8000])
