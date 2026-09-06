#!/usr/bin/env python3
"""
DISEASE INTELLIGENCE · OBSERVATIONAL · TEST 3 — CAN THIS FEED ITSELF WITHOUT BREAKING ITSELF?

Six scenarios, all through the real refresh code, on a COPY of a real case. The canonical
archive under CASES/ is never written to. Five scenarios use a canned transport so they are
reproducible offline; the sixth makes one real request, so the answer to "is the endpoint
alive" is measured rather than assumed.

The property: after any refresh, good or bad, the canonical archive must still produce the
same answer it produced before, unless genuinely new observations arrived.

Out: t3_refresh.json
"""
import os, sys, json, shutil, hashlib, glob, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "engine"))
import di_core, di_observe, di_refresh

SRC = os.path.abspath(os.path.join(HERE, "..", "..", "DISEASE-INTELLIGENCE-ITALY",
                                   "CASES", "OLIVO-BACTROCERA-TOSCANA"))
LAB = os.path.join(HERE, "REFRESH-LAB")
CROP, SCHEMA, VAR, YEAR = 2, 1, -1002, 2026
AS_OF = dt.date(2026, 9, 6)


def build_lab():
    """A small canonical case made of real bytes: three seasons of the olive archive."""
    canon = os.path.join(LAB, "canonical")
    stag = os.path.join(LAB, "staging")
    for d in (canon, stag):
        if os.path.exists(d):
            shutil.rmtree(d)
    os.makedirs(os.path.join(canon, "RAW"))
    src_idx = json.load(open(os.path.join(SRC, "collection_index.json"), encoding="utf-8"))
    idx = {"api": src_idx["api"], "crop": CROP, "schema": SCHEMA,
           "codes": src_idx.get("codes"), "vars": src_idx.get("vars"),
           "DENOMINATOR_VAR": 1, "requests": []}
    for v in (VAR, 1):
        for y in (2024, 2025, 2026):
            fn = f"c{CROP}_s{SCHEMA}_v{v}_{y}.json"
            p = os.path.join(SRC, "RAW", fn)
            if not os.path.exists(p):
                continue
            blob = open(p, "rb").read()
            open(os.path.join(canon, "RAW", fn), "wb").write(blob)
            idx["requests"].append({"file": fn, "var": v, "year": y,
                                    "sha256": hashlib.sha256(blob).hexdigest(),
                                    "LAST_GOOD_OBSERVATION_AT": "recorded at build time"})
    json.dump(idx, open(os.path.join(canon, "collection_index.json"), "w",
                        encoding="utf-8"), indent=1)
    return canon, stag


def answer(canon):
    """What the canonical archive says right now, as one hash plus the readable facts."""
    sheet = di_core.load_sheet()
    try:
        loaded = di_core.load_visits(canon, sheet, AS_OF)
    except Exception as e:
        return {"RAISED": f"{type(e).__name__}: {str(e)[:120]}"}
    dates = [v["observation_date"] for v in loaded["visits"]]
    return {"n_visits": loaded["n_visits"],
            "n_usable": loaded["n_visits_usable_for_rates"],
            "last_observation": max(dates) if dates else None,
            "hash": hashlib.sha256(json.dumps(
                {k: v for k, v in loaded.items() if k != "visits"},
                sort_keys=True, default=str).encode()).hexdigest()[:16]}


def canned(kind, real_rows):
    def t(url):
        if kind == "network_error":
            raise OSError("simulated: the endpoint did not answer")
        if kind == "identical":
            return json.dumps({"data": {"ok": True, "data": real_rows}}).encode("utf-8")
        if kind == "all_null":
            rows = [dict(r, val=None) for r in real_rows]
            return json.dumps({"data": {"ok": True, "data": rows}}).encode("utf-8")
        if kind == "not_ok":
            return json.dumps({"data": {"ok": False, "message": "season not started",
                                        "data": []}}).encode("utf-8")
        if kind == "garbage":
            return b"<html>503 Service Unavailable</html>"
        if kind == "new_rows":
            extra = dict(real_rows[0], date="2026-09-05", id_field=999999, val="1")
            return json.dumps({"data": {"ok": True,
                                        "data": real_rows + [extra]}}).encode("utf-8")
        raise ValueError(kind)
    return t


def main():
    canon, stag = build_lab()
    before = answer(canon)
    real_rows = json.load(open(os.path.join(canon, "RAW",
                                            f"c{CROP}_s{SCHEMA}_v{VAR}_{YEAR}.json"),
                               encoding="utf-8"))
    out = {"BEFORE": before, "SCENARIOS": []}

    for kind in ("identical", "all_null", "not_ok", "garbage", "network_error", "new_rows"):
        rec = di_refresh.refresh_one(canon, stag, CROP, SCHEMA, VAR, YEAR,
                                     _transport=canned(kind, real_rows))
        prom = di_refresh.promote(canon, stag, [rec])
        after = answer(canon)
        out["SCENARIOS"].append({
            "SCENARIO": kind, "REFRESH_STATUS": rec["REFRESH_STATUS"],
            "REFRESH_ATTEMPT_AT": rec["REFRESH_ATTEMPT_AT"],
            "LAST_GOOD_OBSERVATION_AT": rec.get("LAST_GOOD_OBSERVATION_AT", "UNKNOWN"),
            "detail": rec.get("detail"), "promoted": prom["promoted"],
            "index_entries_after": prom["index_entries_after"],
            "AFTER": after,
            "CANONICAL_UNCHANGED": after["hash"] == before["hash"],
            "STILL_READABLE": "RAISED" not in after})
        if kind == "new_rows":
            out["NEW_ROWS_CHANGED_THE_ANSWER"] = after["hash"] != before["hash"]
        else:
            # restore for the next scenario so each is measured against the same start
            canon, stag = build_lab()

    # one real request, so "is the endpoint alive" is measured
    live = di_refresh.fetch(CROP, SCHEMA, VAR, YEAR)
    if live["ok"]:
        st, det, rows, _ = di_refresh.validate(live["body"])
        out["LIVE_PROBE"] = {"reachable": True, "seconds": live["seconds"],
                             "validation": st, "detail": det}
    else:
        out["LIVE_PROBE"] = {"reachable": False, "error": live.get("error")}

    bad = [s for s in out["SCENARIOS"]
           if s["SCENARIO"] != "new_rows" and not (s["CANONICAL_UNCHANGED"]
                                                   and s["STILL_READABLE"])]
    out["VERDICT"] = {
        "every_bad_refresh_left_canonical_intact_and_readable": not bad,
        "failures": [s["SCENARIO"] for s in bad],
        "an_identical_refresh_is_a_no_op":
            out["SCENARIOS"][0]["REFRESH_STATUS"] == di_refresh.NO_UPDATE,
        "genuinely_new_rows_do_change_the_answer":
            out.get("NEW_ROWS_CHANGED_THE_ANSWER"),
        "the_six_outcomes_are_distinguished": sorted(
            {s["REFRESH_STATUS"] for s in out["SCENARIOS"]}),
        "SAFE_REFRESH": ("YES" if (not bad and out.get("NEW_ROWS_CHANGED_THE_ANSWER"))
                         else "NOT_YET")}

    json.dump(out, open(os.path.join(HERE, "t3_refresh.json"), "w", encoding="utf-8"),
              indent=1, default=str)
    print(f"BEFORE  {before}\n")
    for s in out["SCENARIOS"]:
        print(f"  {s['SCENARIO']:15s} -> {s['REFRESH_STATUS']:19s} "
              f"canonical_unchanged={str(s['CANONICAL_UNCHANGED']):5s} "
              f"readable={str(s['STILL_READABLE']):5s} promoted={s['promoted']} "
              f"index={s['index_entries_after']}")
    print(f"\n  live probe: {out['LIVE_PROBE']}")
    print(f"\nVERDICT: {json.dumps(out['VERDICT'], indent=1)}")


if __name__ == "__main__":
    main()
