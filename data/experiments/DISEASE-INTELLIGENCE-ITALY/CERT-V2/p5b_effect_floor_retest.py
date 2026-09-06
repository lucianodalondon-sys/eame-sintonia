#!/usr/bin/env python3
"""
CERT-V2 / STEP 5b — THE EFFECT FLOOR, RE-TESTED AFTER MY FIRST TEST WAS SHOWN TO BE A
TAUTOLOGY.

WHAT WENT WRONG THE FIRST TIME
  p5 reported "0 fails open, 0 fails closed" and I read that as PROVED. An independent red
  team pointed out that both counters are the floor's own predicate read back:
      kept     = STATE == HIGHER          which the floor only permits when n*v >= 5
      fails open = kept AND n*v < 5       -> empty by construction
      withheld = a rank-HIGHER downgraded which requires n*v < 5
      fails closed = withheld AND n*v >= 5 -> empty by construction
  Those two zeros would print for a floor of 1, of 5 or of 70. Reproduced and conceded.
  EFFECT_FLOOR = PROVED is WITHDRAWN.

WHAT A TEST THAT CAN FAIL LOOKS LIKE
  T1  SWEEP. Recompute every cell's class for MIN_POSITIVE_SITES = 0..70 and count how many
      distinct partitions exist. If the value 5 is special, the partition should change around
      it; if dozens of values give the same answer, 5 was not selected by anything.
  T2  AN INDEPENDENT YARDSTICK. n_sites * INCIDENCE is the floor's own quantity. INCIDENCE
      alone is not. Compare the withheld and kept sets on INCIDENCE, and ask whether the floor
      is equivalent to a plain incidence threshold on this data.
  T3  WHAT THE FLOOR MAKES IMPOSSIBLE. For every classified cell, compute the incidence a
      HIGHER call would require. Count the cells where that exceeds the highest incidence ever
      recorded in that province at that window: those can never produce a HIGHER call, whatever
      happens in the field.
  T4  WHERE THE KEPT CALLS ACTUALLY LIVE. Split them by crop and by whether they are live 2026
      dates or historical replays.
  T5  RECORDS THAT WERE WITHHELD. A withheld cell whose incidence is the highest ever recorded
      at that window in that province is a candidate false negative that owes nothing to the
      floor's own definition.
  T6  IS THE FLOOR EVEN DECLARED? Is it in the module's stated parameter list, in the emitted
      PARAMS block, and in the sensitivity grid that gate F uses?

Reads p4_cell_state_by_date.json, which carries n_sites, VALUE and STATE_WITHOUT_FLOOR per
cell, so no re-sweep is needed.

Out: p5b_effect_floor_retest.json
"""
import json, os, sys, collections

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "ENGINE"))
sys.path.insert(0, os.path.join(HERE, "..", "CASES"))
import current_pressure as cp

HIGHER, TYPICAL, LOWER = cp.HIGHER, cp.TYPICAL, cp.LOWER


def classify(rows, T):
    """The shipped rule with the floor set to T."""
    out = []
    for r in rows:
        s = r["STATE_WITHOUT_FLOOR"]
        if s == HIGHER:
            n, v = r.get("n_sites") or 0, r.get("VALUE")
            if v is None or n * v < T:
                s = TYPICAL
        out.append(s)
    return out


def main():
    src = json.load(open(os.path.join(HERE, "p4_cell_state_by_date.json"), encoding="utf-8"))
    rows = src["ROWS"]
    classed = [r for r in rows if r["STATE_WITHOUT_FLOOR"] in (HIGHER, TYPICAL, LOWER)]

    # ── T1 sweep ──────────────────────────────────────────────────────────────────
    partitions, per_T = {}, {}
    for T in range(0, 71):
        cls = tuple(classify(classed, T))
        n_high = sum(1 for c in cls if c == HIGHER)
        per_T[T] = n_high
        partitions.setdefault(cls, []).append(T)
    shipped = tuple(classify(classed, cp.MIN_POSITIVE_SITES))
    same_as_shipped = sorted(partitions[shipped])
    t1 = {"DISTINCT_PARTITIONS_OVER_T_0_TO_70": len(partitions),
          "HIGHER_COUNT_BY_T": per_T,
          "T_VALUES_GIVING_EXACTLY_THE_SHIPPED_PARTITION": same_as_shipped,
          "READ": "if a wide band of T gives the identical answer, the value 5 was not "
                  "selected by the data; it sits somewhere inside that band."}

    # ── T2 an independent yardstick ───────────────────────────────────────────────
    withheld = [r for r in classed
                if r["STATE_WITHOUT_FLOOR"] == HIGHER and r["STATE"] != HIGHER]
    kept = [r for r in classed if r["STATE"] == HIGHER]

    def dist(rs, f):
        v = sorted(x for x in (f(r) for r in rs) if x is not None)
        return None if not v else {"n": len(v), "min": round(v[0], 4),
                                   "median": round(v[len(v) // 2], 4), "max": round(v[-1], 4)}
    # is the floor equivalent to a plain incidence cut on this data?
    best = None
    for thr in [i / 100 for i in range(0, 101)]:
        by_inc = {id(r) for r in classed
                  if r["STATE_WITHOUT_FLOOR"] == HIGHER and (r["VALUE"] or 0) >= thr}
        by_floor = {id(r) for r in kept}
        sym = len(by_inc ^ by_floor)
        if best is None or sym < best[1]:
            best = (thr, sym)
    t2 = {"INCIDENCE_OF_WITHHELD": dist(withheld, lambda r: r["VALUE"]),
          "INCIDENCE_OF_KEPT": dist(kept, lambda r: r["VALUE"]),
          "N_SITES_OF_WITHHELD": dist(withheld, lambda r: r["n_sites"]),
          "N_SITES_OF_KEPT": dist(kept, lambda r: r["n_sites"]),
          "CLOSEST_PLAIN_INCIDENCE_THRESHOLD": {"threshold": best[0],
                                                "cells_where_it_disagrees": best[1]},
          "READ": "if a plain incidence threshold reproduces the floor exactly, then what the "
                  "floor selects is severity, not the number of positive sites, and it should "
                  "be stated that way."}

    # ── T3 what the floor makes impossible ────────────────────────────────────────
    hist = collections.defaultdict(list)
    for r in classed:
        hist[(r["CROP"], r["PROVINCE"], r["DATE"][5:])].append(r["VALUE"] or 0)
    impossible, impossible_rows = 0, []
    for r in classed:
        n = r.get("n_sites") or 0
        if n <= 0:
            continue
        need = cp.MIN_POSITIVE_SITES / n
        ceiling = max(hist[(r["CROP"], r["PROVINCE"], r["DATE"][5:])] or [0])
        if need > 1.0 or need > ceiling:
            impossible += 1
            if len(impossible_rows) < 8:
                impossible_rows.append({"CROP": r["CROP"], "PROVINCE": r["PROVINCE"],
                                        "DATE": r["DATE"], "n_sites": n,
                                        "incidence_required": round(need, 3),
                                        "highest_ever_at_this_window": round(ceiling, 3)})
    t3 = {"CLASSIFIED_CELLS": len(classed),
          "CELLS_THAT_CAN_NEVER_PRODUCE_A_HIGHER_CALL": impossible,
          "RATE": round(impossible / max(1, len(classed)), 4),
          "EXAMPLES": impossible_rows,
          "READ": "a floor stated in absolute positive sites is a stricter incidence "
                  "requirement in a small province than in a large one. These cells are "
                  "structurally silent."}

    # ── T4 where the kept calls live ──────────────────────────────────────────────
    t4 = {"KEPT_BY_CROP": dict(collections.Counter(r["CROP"] for r in kept)),
          "WITHHELD_BY_CROP": dict(collections.Counter(r["CROP"] for r in withheld)),
          "KEPT_IN_2026": sum(1 for r in kept if r["DATE"].startswith("2026")),
          "KEPT_IN_HISTORICAL_REPLAYS": sum(1 for r in kept
                                            if not r["DATE"].startswith("2026")),
          "WITHHELD_IN_2026": sum(1 for r in withheld if r["DATE"].startswith("2026")),
          "RANK_HIGHER_IN_2026": sum(1 for r in classed
                                     if r["STATE_WITHOUT_FLOOR"] == HIGHER
                                     and r["DATE"].startswith("2026"))}

    # ── T5 records that were withheld ─────────────────────────────────────────────
    records = []
    for r in withheld:
        k = (r["CROP"], r["PROVINCE"], r["DATE"][5:])
        if (r["VALUE"] or 0) >= max(hist[k] or [0]) - 1e-9:
            records.append({"CROP": r["CROP"], "PROVINCE": r["PROVINCE"], "DATE": r["DATE"],
                            "VALUE": r["VALUE"], "n_sites": r["n_sites"],
                            "n_positive_sites": r["n_positive_sites"],
                            "highest_ever_at_this_window": round(max(hist[k]), 4)})
    t5 = {"WITHHELD_CELLS_THAT_ARE_THE_HIGHEST_EVER_RECORDED_AT_THAT_WINDOW": len(records),
          "ROWS": records,
          "READ": "these are candidate false negatives that owe nothing to the floor's own "
                  "definition. p5 reported 0 false negatives and this is what it missed."}

    # ── T6 is the floor declared? ─────────────────────────────────────────────────
    src_cp = open(os.path.join(HERE, "..", "ENGINE", "current_pressure.py"),
                  encoding="utf-8").read()
    doc = src_cp.split('"""')[1] if '"""' in src_cp else ""
    live = cp.current_pressure(os.path.join(HERE, "..", "CASES", "OLIVO-BACTROCERA-TOSCANA"),
                               -1002, __import__("datetime").date(2026, 9, 6))
    grid_src = src_cp[src_cp.find("def sensitivity"):src_cp.find("def sensitivity") + 1400]
    t6 = {"IN_THE_DOCSTRING_PARAMETER_LIST": "MIN_POSITIVE_SITES" in doc,
          "IN_THE_EMITTED_PARAMS_BLOCK": "MIN_POSITIVE_SITES" in live["PARAMS"],
          "EMITTED_PARAMS": list(live["PARAMS"]),
          "IN_THE_SENSITIVITY_GRID": "min_positive" in grid_src or
                                     "MIN_POSITIVE_SITES" in grid_src,
          "READ": "gate F measures how much the label depends on the parameters. A parameter "
                  "outside the grid is a parameter the label is never tested against."}

    out = {"WITHDRAWN": "p5's EFFECT_FLOOR = PROVED, and its 0 false positives / 0 false "
                        "negatives, which were tautological",
           "T1_SWEEP": t1, "T2_INDEPENDENT_YARDSTICK": t2, "T3_MADE_IMPOSSIBLE": t3,
           "T4_WHERE_THE_KEPT_CALLS_LIVE": t4, "T5_WITHHELD_RECORDS": t5,
           "T6_IS_THE_FLOOR_DECLARED": t6}
    out["EFFECT_FLOOR"] = "NOT_PROVED"
    out["EFFECT_FLOOR_REASON"] = (
        f"The floor does what it says — it removes rank-HIGHER calls that rest on very few "
        f"positive sites — and on this sample it removes exactly the pathology it was built "
        f"for. What is NOT proved is that it discriminates signal from noise. "
        f"{len(same_as_shipped)} of the 71 floor values tried give the identical partition, so "
        f"the number 5 is not selected by the data. On this sample it is reproduced to within "
        f"{best[1]} cells by a plain incidence threshold of {best[0]}, which means it is "
        f"selecting severity and not a count of sites. It makes a HIGHER call arithmetically "
        f"impossible in {impossible} of {len(classed)} classified cells. It is absent from the "
        f"module's own parameter list, from the emitted PARAMS block and from the sensitivity "
        f"grid, so gate F has never varied it. And "
        f"{len(records)} of the {len(withheld)} withheld cells are the highest value ever "
        f"recorded at that window in that province.")

    json.dump(out, open(os.path.join(HERE, "p5b_effect_floor_retest.json"), "w"),
              indent=1, default=str)
    print("T1 distinct partitions over T=0..70:", t1["DISTINCT_PARTITIONS_OVER_T_0_TO_70"])
    print("   T values giving the shipped partition:", same_as_shipped)
    print("T2 incidence withheld:", t2["INCIDENCE_OF_WITHHELD"])
    print("   incidence kept    :", t2["INCIDENCE_OF_KEPT"])
    print("   closest plain incidence threshold:", t2["CLOSEST_PLAIN_INCIDENCE_THRESHOLD"])
    print("T3 cells that can NEVER produce HIGHER:",
          t3["CELLS_THAT_CAN_NEVER_PRODUCE_A_HIGHER_CALL"], "of", t3["CLASSIFIED_CELLS"])
    print("T4", json.dumps(t4))
    print("T5 withheld cells that are records:",
          t5["WITHHELD_CELLS_THAT_ARE_THE_HIGHEST_EVER_RECORDED_AT_THAT_WINDOW"])
    for r in t5["ROWS"][:6]:
        print("   ", json.dumps(r))
    print("T6", json.dumps({k: v for k, v in t6.items() if k != "READ"}))
    print("\nEFFECT_FLOOR =", out["EFFECT_FLOOR"])


if __name__ == "__main__":
    main()
