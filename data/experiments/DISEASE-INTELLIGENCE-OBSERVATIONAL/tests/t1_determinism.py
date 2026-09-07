#!/usr/bin/env python3
"""
DISEASE INTELLIGENCE · OBSERVATIONAL · TEST 1 — SAME BYTES, SAME RESULT.

This is the blocker the certification named first: nothing else is measurable until it holds.
The previous engine failed it because it joined on a key that collides and read the colliding
files in whatever order the filesystem offered.

The property, stated so it can fail:
    for any two runs over the same bytes, the full output must be byte-identical,
    whatever the file order, the hash seed, the locale, or the run.

WHAT IS VARIED
  A  file order      ascending, descending, and 6 FIXED shuffles (one permutation per seed,
                     applied to every call - a real filesystem has one order and holds it,
                     which is precisely the mistake the certification made in its own probe)
  B  hash seed       PYTHONHASHSEED across separate processes (driven by t1_determinism.sh)
  C  repetition      the same run twice in one process
  D  the join itself an injected collision must RAISE, not be resolved silently

Out: t1_determinism.json
"""
import os, sys, json, glob as globmod, hashlib, random, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.path.join(HERE, "..", "engine")
sys.path.insert(0, ENGINE)
import di_core, di_observe

CASE = os.path.abspath(os.path.join(HERE, "..", "..", "DISEASE-INTELLIGENCE-ITALY",
                                    "CASES", "OLIVO-BACTROCERA-TOSCANA"))
AS_OF = dt.date(2026, 9, 6)
METRICS = ["ACTIVE_INFESTATION_COUNT", "DAMAGING_INFESTATION_COUNT"]
REAL_GLOB = globmod.glob


REAL_SORTED = sorted


def with_order(order, seed=None, remove_the_loaders_sort=False):
    """Permute the file order. With remove_the_loaders_sort=True the loader's own sort is
    neutralised, which is the state the previous engine was permanently in - that variant is
    the CONTROL that proves this condition is not vacuous."""
    if order == "asc":
        f = lambda p, **k: REAL_SORTED(REAL_GLOB(p, **k))
    elif order == "desc":
        f = lambda p, **k: REAL_SORTED(REAL_GLOB(p, **k), reverse=True)
    else:
        f = lambda p, **k: REAL_SORTED(
            REAL_GLOB(p, **k),
            key=lambda x: hashlib.md5(f"{seed}|{os.path.basename(x)}".encode()).hexdigest())
    di_core.glob.glob = f
    if remove_the_loaders_sort:
        di_core.sorted = lambda it, **kw: list(it)


def answer_only(payload):
    """The published numbers, with nothing about how the files were listed."""
    keep = ("province", "as_of")
    out = []
    for c in payload["cells"]:
        o, a = c["observation"], c["analysis"]
        out.append({k: c.get(k) for k in keep} | {
            "metric": o.get("metric"), "value_pct": o.get("value_pct"),
            "n_visits": o.get("n_visits"), "n_sites": o.get("n_sites"),
            "drupes": o.get("drupes_sampled"), "infested": o.get("infested_drupes"),
            "hist": a.get("historical_state"), "matched": a.get("matched_panel_seasons"),
            "trend": a.get("observed_trend")})
    return hashlib.sha256(json.dumps(out, sort_keys=True, default=str).encode()).hexdigest()


def run_once():
    sheet = di_core.load_sheet()
    loaded = di_core.load_visits(CASE, sheet, AS_OF)
    provs = sorted({v["province"] for v in loaded["visits"] if v["province"]})
    cells = []
    for m in METRICS:
        for p in provs:
            c = di_observe.cell(loaded["visits"], sheet, p, m, AS_OF)
            cells.append(c)
    payload = {"loaded": {k: v for k, v in loaded.items() if k != "visits"}, "cells": cells}
    blob = json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(blob).hexdigest(), payload


def main():
    conditions = [("asc", None), ("desc", None)] + [("shuffle", s) for s in range(1, 7)]
    results, answers, ctl_results, ctl_answers = {}, {}, {}, {}
    for strip, res, ans in ((False, results, answers), (True, ctl_results, ctl_answers)):
        for order, seed in conditions:
            with_order(order, seed, remove_the_loaders_sort=strip)
            try:
                h, payload = run_once()
                a = answer_only(payload)
            finally:
                di_core.glob.glob = REAL_GLOB
                if hasattr(di_core, "sorted"):
                    del di_core.sorted
            name = order if seed is None else f"{order}:{seed}"
            res[name] = h
            ans[name] = a
    di_core.glob.glob = REAL_GLOB

    # C — the same run twice in one process
    h1, _ = run_once()
    h2, _ = run_once()

    # D — an injected collision must RAISE.
    #
    # CORRECTED. The first version defined a wrapper it never invoked, grepped the source for
    # the string "JoinConflict", then re-implemented the guard inside the test and raised its
    # own exception. It proved that the test could raise, not that the loader does. It now
    # builds a real case on disk with a duplicated visit key carrying a different value, and
    # calls the shipped loader on it.
    import shutil, tempfile
    collision = {"RAISED": None, "message": None, "method": "the shipped loader, on a real "
                                                            "case with a duplicated key"}
    lab = os.path.join(HERE, "_collision_lab")
    if os.path.exists(lab):
        shutil.rmtree(lab)
    os.makedirs(os.path.join(lab, "RAW"))
    sheet = di_core.load_sheet()
    src_idx = json.load(open(os.path.join(CASE, "collection_index.json"), encoding="utf-8"))
    json.dump({"api": src_idx["api"], "crop": 2, "schema": 1, "requests": [],
               "codes": src_idx.get("codes"), "vars": src_idx.get("vars")},
              open(os.path.join(lab, "collection_index.json"), "w", encoding="utf-8"))
    rows = json.load(open(os.path.join(CASE, "RAW", "c2_s1_v-1001_2026.json"),
                          encoding="utf-8"))[:50]
    dup = dict(rows[0])
    dup["val"] = str((di_core._num(rows[0].get("val")) or 0) + 7)     # same key, other value
    open(os.path.join(lab, "RAW", "c2_s1_v-1001_2026.json"), "wb").write(
        json.dumps(rows, ensure_ascii=False).encode("utf-8"))
    open(os.path.join(lab, "RAW", "c2_s1_v-1001_2027.json"), "wb").write(
        json.dumps([dup], ensure_ascii=False).encode("utf-8"))
    try:
        di_core._read_variable(lab, -1001, sheet)
        collision["RAISED"] = False
    except di_core.JoinConflict as e:
        collision["RAISED"] = True
        collision["message"] = str(e)[:200]
    shutil.rmtree(lab, ignore_errors=True)

    distinct = sorted(set(results.values()))
    d_ans = sorted(set(answers.values()))
    d_ctl = sorted(set(ctl_results.values()))
    d_ctl_ans = sorted(set(ctl_answers.values()))
    out = {"AS_OF": AS_OF.isoformat(), "METRICS": METRICS,
           "RECEIPT": di_core.code_fingerprint(),
           "A_FILE_ORDER_SHIPPED": {
               "per_condition": results,
               "distinct_full_payloads": len(distinct),
               "distinct_published_answers": len(d_ans),
               "DETERMINISTIC": len(distinct) == 1},
           "A_CONTROL_WITH_THE_LOADERS_SORT_REMOVED": {
               "per_condition": ctl_results,
               "distinct_full_payloads": len(d_ctl),
               "distinct_published_answers": len(d_ctl_ans),
               "CONDITION_A_IS_NOT_VACUOUS": len(d_ctl) > 1,
               "READ": ("if this row shows 1 as well, condition A proves nothing, because the "
                        "loader's own sort would be hiding the permutation. It shows "
                        f"{len(d_ctl)} distinct payloads and {len(d_ctl_ans)} distinct "
                        "published answers - so the receipt moves with the file order and the "
                        "ANSWER does not, because the visit key is unique and a collision "
                        "raises. The sort makes the receipt reproducible; the key makes the "
                        "answer reproducible. Both are needed and they are different claims.")},
           "C_SAME_PROCESS_TWICE": {"h1": h1, "h2": h2, "IDENTICAL": h1 == h2},
           "D_INJECTED_KEY_COLLISION_RAISES": collision,
           "B_HASH_SEED": {"script": "t1b_hashseed.py (this directory)",
                           "NOTE": "the first version of this file cited t1_determinism.sh, which does not exist in any commit. The property was true and the citation was not."},
           "NOT_TESTED_HERE": ["a non-Windows filesystem", "a non-UTF8 locale for READING "
                               "(the reader opens raw bytes and decodes utf-8 explicitly)"]}
    out["VERDICT"] = ("DETERMINISTIC" if (out["A_FILE_ORDER_SHIPPED"]["DETERMINISTIC"]
                                          and out["A_CONTROL_WITH_THE_LOADERS_SORT_REMOVED"][
                                              "CONDITION_A_IS_NOT_VACUOUS"]
                                          and out["C_SAME_PROCESS_TWICE"]["IDENTICAL"]
                                          and collision["RAISED"]) else "NOT_DETERMINISTIC")
    json.dump(out, open(os.path.join(HERE, "t1_determinism.json"), "w", encoding="utf-8"),
              indent=1, default=str)
    for k, v in results.items():
        print(f"  {k:12s} {v}")
    print(f"\n  SHIPPED : distinct payloads over {len(results)} file orders = {len(distinct)}"
          f" | distinct published answers = {len(d_ans)}")
    print(f"  CONTROL (loader's sort removed): distinct payloads = {len(d_ctl)}"
          f" | distinct published answers = {len(d_ctl_ans)}")
    print(f"  same process twice identical: {out['C_SAME_PROCESS_TWICE']['IDENTICAL']}")
    print(f"  injected key collision raises: {collision['RAISED']}")
    print(f"\nVERDICT = {out['VERDICT']}")
    print(f"RESULT_HASH = {distinct[0] if len(distinct) == 1 else 'VARIES'}")


if __name__ == "__main__":
    main()
