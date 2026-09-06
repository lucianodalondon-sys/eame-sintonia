#!/usr/bin/env python3
"""RT3-E3. Gate B claims: 'moving the cutoff forward changes N published province-cells --
so the cutoff is LOAD-BEARING and this gate can detect its removal.'

Two independent attacks, both run against the SHIPPED engine, nothing in ENGINE/ modified:

  ATTACK 1 (CONFOUND). Moving AS_OF forward 30 days moves the window's LOWER bound forward
  30 days as well. Decompose the gate's own number: recount the changed cells with every
  future-dated row DELETED from the data. Whatever changes then is caused by the window
  sliding, not by the upper cutoff.

  ATTACK 2 (THE GATE CANNOT FAIL). Monkeypatch current_pressure._window_value so the upper
  bound `hi` is unbounded -- the cutoff is REMOVED -- and re-evaluate gate B's exact
  predicate. A gate that says it 'can detect its removal' must return FAIL here.
"""
import sys, os, json, copy, datetime as dt, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ENG = os.path.abspath(os.path.join(HERE, "..", "..", "ENGINE"))
CAS = os.path.abspath(os.path.join(HERE, "..", "..", "CASES"))
sys.path.insert(0, ENG)
import current_pressure as cp

AS_OF = dt.date(2026, 9, 6)
CASES = [("OLIVO x BACTROCERA x TOSCANA", os.path.join(CAS, "OLIVO-BACTROCERA-TOSCANA"), -1002),
         ("VITE x OIDIO x TOSCANA", os.path.join(CAS, "VITE-OIDIO-TOSCANA"), 39)]

OUT = {"AS_OF": AS_OF.isoformat()}
ORIG_WINDOW_VALUE = cp._window_value


def gate_b_predicate(as_of, window_value_impl, label):
    """gates.py lines 63-84, transcribed verbatim in logic, with _window_value swappable."""
    cp._window_value = window_value_impl
    try:
        fut, used_fut, load_bearing = 0, 0, 0
        detail = {}
        live = {}
        for name, d, v in CASES:
            pre = cp.load_rows(d, v)
            live[name] = cp.current_pressure(d, v, as_of, _pre=pre)
        for name, d, v in CASES:
            pre = cp.load_rows(d, v)
            after = [r for r in pre[0] if r["_d"] > as_of]
            fut += len(after)
            w0 = as_of - dt.timedelta(days=cp.WINDOW_DAYS - 1)
            used_fut += sum(1 for r in after if w0 <= r["_d"])
            leaked = cp.current_pressure(d, v, as_of + dt.timedelta(days=30), _pre=pre)
            honest = live[name]
            changed = [p for p in honest["PROVINCES"]
                       if honest["PROVINCES"][p].get("STATE")
                       != leaked["PROVINCES"].get(p, {}).get("STATE")]
            load_bearing += len(changed)
            detail[name] = {"n_future_rows": len(after), "changed_cells": changed,
                            "honest": {p: x.get("STATE") for p, x in honest["PROVINCES"].items()},
                            "leaked": {p: x.get("STATE") for p, x in leaked["PROVINCES"].items()}}
        verdict = ("PASS" if (fut > 0 and used_fut > 0 and load_bearing > 0 and
                              all(r["CUTOFF_LABEL"] == "NOWCAST" for r in live.values()))
                   else ("NOT_TESTABLE" if fut == 0 else "FAIL"))
        return {"LABEL": label, "fut": fut, "used_fut": used_fut,
                "load_bearing": load_bearing, "VERDICT": verdict, "DETAIL": detail}
    finally:
        cp._window_value = ORIG_WINDOW_VALUE


# ---------------------------------------------------------------- shipped baseline
OUT["B0_SHIPPED"] = gate_b_predicate(AS_OF, ORIG_WINDOW_VALUE, "shipped engine, unmodified")

# ---------------------------------------------------------------- ATTACK 1: confound
# Recount the gate's own diff with every future-dated row physically removed. Any cell that
# still changes is changed by the window's LOWER bound moving, not by the upper cutoff.
a1 = {}
for name, d, v in CASES:
    pre = cp.load_rows(d, v)
    rows_all = pre[0]
    rows_nofuture = [r for r in rows_all if r["_d"] <= AS_OF]
    pre_nf = (rows_nofuture, pre[1], pre[2])

    honest = cp.current_pressure(d, v, AS_OF, _pre=pre)
    leaked = cp.current_pressure(d, v, AS_OF + dt.timedelta(days=30), _pre=pre)
    # same forward move, but the future simply does not exist in the archive
    slid_only = cp.current_pressure(d, v, AS_OF + dt.timedelta(days=30), _pre=pre_nf)

    def diff(a, b):
        return [p for p in a["PROVINCES"]
                if a["PROVINCES"][p].get("STATE") != b["PROVINCES"].get(p, {}).get("STATE")]

    gate_diff = diff(honest, leaked)
    slide_diff = diff(honest, slid_only)
    cutoff_only_diff = diff(slid_only, leaked)   # same window, future present vs absent
    a1[name] = {
        "N_FUTURE_ROWS": len(rows_all) - len(rows_nofuture),
        "N_ROWS_TOTAL": len(rows_all),
        "GATE_B_CHANGED_CELLS  (honest vs as_of+30, future present)": gate_diff,
        "WINDOW_SLIDE_ALONE_CHANGED_CELLS (honest vs as_of+30, future DELETED)": slide_diff,
        "ATTRIBUTABLE_TO_UPPER_CUTOFF (as_of+30 with vs without future rows)": cutoff_only_diff,
        "N_GATE": len(gate_diff), "N_SLIDE_ALONE": len(slide_diff),
        "N_CUTOFF_ONLY": len(cutoff_only_diff),
        "N_PROVINCES": len(honest["PROVINCES"]),
    }
OUT["A1_CONFOUND_DECOMPOSITION"] = a1

# ---------------------------------------------------------------- ATTACK 2: remove the cutoff
FAR = dt.date(9999, 12, 31)


def window_value_hi_unbounded(rows, scale, lo, hi, mode="ORDINAL"):
    """Identical to the shipped _window_value except the UPPER bound is gone."""
    return ORIG_WINDOW_VALUE(rows, scale, lo, FAR, mode)


OUT["A2_CUTOFF_REMOVED_ALL_WINDOWS"] = gate_b_predicate(
    AS_OF, window_value_hi_unbounded,
    "hi unbounded in EVERY window (current AND baseline) -- cutoff removed")


def window_value_hi_unbounded_current_only(rows, scale, lo, hi, mode="ORDINAL"):
    """Remove the cutoff ONLY for the current window; baselines keep their own upper bound.
    The current window is the one whose hi is the as_of the caller passed."""
    if hi.year >= 2026:
        return ORIG_WINDOW_VALUE(rows, scale, lo, FAR, mode)
    return ORIG_WINDOW_VALUE(rows, scale, lo, hi, mode)


OUT["A2b_CUTOFF_REMOVED_CURRENT_WINDOW_ONLY"] = gate_b_predicate(
    AS_OF, window_value_hi_unbounded_current_only,
    "hi unbounded only for the CURRENT window (baselines untouched)")

# ------------------------------------------- does removing the cutoff change published cells?
eff = {}
for name, d, v in CASES:
    pre = cp.load_rows(d, v)
    honest = cp.current_pressure(d, v, AS_OF, _pre=pre)
    cp._window_value = window_value_hi_unbounded_current_only
    try:
        nocut = cp.current_pressure(d, v, AS_OF, _pre=pre)
    finally:
        cp._window_value = ORIG_WINDOW_VALUE
    ch = [p for p in honest["PROVINCES"]
          if honest["PROVINCES"][p].get("STATE") != nocut["PROVINCES"].get(p, {}).get("STATE")]
    eff[name] = {"CHANGED_CELLS_WHEN_CUTOFF_REMOVED": ch, "N_CHANGED": ch and len(ch) or 0,
                 "N_PROVINCES": len(honest["PROVINCES"]),
                 "honest": {p: x.get("STATE") for p, x in honest["PROVINCES"].items()},
                 "no_cutoff": {p: x.get("STATE") for p, x in nocut["PROVINCES"].items()},
                 "honest_sites": {p: x.get("n_sites") for p, x in honest["PROVINCES"].items()},
                 "no_cutoff_sites": {p: x.get("n_sites") for p, x in nocut["PROVINCES"].items()}}
OUT["A3_REAL_EFFECT_OF_REMOVING_CUTOFF_TODAY"] = eff

json.dump(OUT, open(os.path.join(HERE, "rt3_e3_gate_b_attack.json"), "w"), indent=1, default=str)

print("=" * 78)
for k in ("B0_SHIPPED", "A2_CUTOFF_REMOVED_ALL_WINDOWS", "A2b_CUTOFF_REMOVED_CURRENT_WINDOW_ONLY"):
    r = OUT[k]
    print(f"{r['VERDICT']:13s} {k}")
    print(f"              {r['LABEL']}")
    print(f"              fut={r['fut']} used_fut={r['used_fut']} load_bearing={r['load_bearing']}")
print("=" * 78)
for n, r in a1.items():
    print(n)
    print(f"   future rows {r['N_FUTURE_ROWS']} of {r['N_ROWS_TOTAL']}")
    print(f"   gate B counts changed cells      : {r['N_GATE']} of {r['N_PROVINCES']}")
    print(f"   window SLIDE alone explains      : {r['N_SLIDE_ALONE']} of {r['N_PROVINCES']}")
    print(f"   attributable to the UPPER CUTOFF : {r['N_CUTOFF_ONLY']} of {r['N_PROVINCES']}")
print("=" * 78)
for n, r in eff.items():
    print(f"{n}: removing the cutoff TODAY changes {r['N_CHANGED']} of {r['N_PROVINCES']} cells "
          f"{r['CHANGED_CELLS_WHEN_CUTOFF_REMOVED']}")
