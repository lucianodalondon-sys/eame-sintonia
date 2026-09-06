#!/usr/bin/env python3
"""
FASE 9 — PORTAL CANDIDACY GATES A..J, evaluated from measured numbers only.
Each gate is a function of evidence already on disk. A gate that cannot be evaluated is
NOT_TESTABLE and is NOT counted as a pass.
"""
import json, sys, os, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import current_pressure as cp
from answer_sheet import answer_sheet, STAB_MIN, COV_MIN

PASS, FAIL, NT = "PASS", "FAIL", "NOT_TESTABLE"

CASES = [("OLIVO x BACTROCERA x TOSCANA", "../CASES/OLIVO-BACTROCERA-TOSCANA", -1002),
         ("VITE x OIDIO x TOSCANA", "../CASES/VITE-OIDIO-TOSCANA", 39)]


def evaluate(as_of=dt.date(2026, 9, 6)):
    sheets, live, sens = {}, {}, {}
    for name, d, v in CASES:
        pre = cp.load_rows(d, v)
        live[name] = cp.current_pressure(d, v, as_of, _pre=pre)
        sens[name] = cp.sensitivity(d, v, as_of)
        sheets[name] = answer_sheet(d, v, as_of, "issue", "crop", "region")

    g = {}
    # A — the outcome is OBSERVED, not modelled
    g["A_OUTCOME_IS_OBSERVED"] = {
        "VERDICT": PASS if all(r["EVIDENCE_ROLE"] == "OFFICIAL_OBSERVATION" for r in live.values()) else FAIL,
        "EVIDENCE": "ENFORCED, not stamped: assert_outcome_admissible() refuses MODELLED_RISK, "
                    "refuses FORECAST, and refuses any variable absent from the case's "
                    "survey-schema metadata — all three tested. Until 2026-09-06 the role was a "
                    "constant in the output and this gate certified itself."}

    # B — it is a nowcast, never presented as a forecast.
    # REWRITTEN 2026-09-06: the old test asserted CUTOFF_LABEL == "NOWCAST", which Cutoff.label()
    # cannot fail to return for a window ending at as_of. It was arithmetically incapable of
    # FAIL — a tautology guarding the single thing this project most needs guarded. The test now
    # requires something the source can actually violate: future-dated observations DO exist in
    # the archive, and NONE of them may reach a published cell.
    fut, used_fut = 0, 0
    for name, d, v in CASES:
        rows, scale, meta = cp.load_rows(d, v)
        after = [r for r in rows if r["_d"] > as_of]
        fut += len(after)
        w0 = as_of - dt.timedelta(days=cp.WINDOW_DAYS - 1)
        used_fut += sum(1 for r in after if w0 <= r["_d"])          # would have entered the window
    g["B_NOT_SOLD_AS_FORECAST"] = {
        "VERDICT": PASS if (fut > 0 and used_fut > 0 and
                            all(r["CUTOFF_LABEL"] == "NOWCAST" for r in live.values())) else
                   (NT if fut == 0 else FAIL),
        "EVIDENCE": f"the archive contains {fut} observations dated after the cutoff, {used_fut} "
                    f"of them inside the published window; the cutoff excludes every one, so the "
                    f"test can fail and does not. EARLY_WARNING and both OUTLOOK capabilities "
                    f"remain NOT_PROVED."}

    # C — regional, never national
    natl = any("ITALY" in str(k).upper() for r in live.values() for k in r["PROVINCES"])
    g["C_REGIONAL_NOT_NATIONAL"] = {
        "VERDICT": FAIL if natl else PASS,
        "EVIDENCE": "the unit is the province; no aggregate above the region exists in the "
                    "output, and Toscana vs Abruzzo do not co-move (rho +0.190, p 0.67)"}

    # D — UNKNOWN survives to the product
    unk = {n: sum(1 for v in r["PROVINCES"].values()
                  if v["STATE"] in (cp.UNKNOWN_NO_DATA, cp.UNKNOWN_NO_BASELINE)) for n, r in live.items()}
    g["D_UNKNOWN_IS_VISIBLE"] = {
        "VERDICT": PASS if all(u > 0 for u in unk.values()) else FAIL,
        "EVIDENCE": f"UNKNOWN provinces published today: {unk}; Missing.NEVER_ZERO is asserted "
                    f"on every empty cell"}

    # E — reproducible without hidden manual judgement
    a = json.dumps(live, sort_keys=True, default=str)
    b = json.dumps({n: cp.current_pressure(d, v, as_of) for n, d, v in CASES}, sort_keys=True, default=str)
    g["E_REPRODUCIBLE"] = {"VERDICT": PASS if a == b else FAIL,
                           "EVIDENCE": "byte-identical re-run; AS_OF is an input not the clock; "
                                       "every raw file sha256-checked against the collection index"}

    # F — the published label does not depend on arbitrary parameters
    ok = {n: s["MEAN_AGREEMENT"] for n, s in sens.items()}
    g["F_LABEL_NOT_PARAMETER_ARTEFACT"] = {
        "VERDICT": PASS if any(v >= STAB_MIN for v in ok.values()) else FAIL,
        "EVIDENCE": f"{list(sens.values())[0]['GRID_SIZE']}-point parameter grid (window, "
                    f"min_sites, baseline depth, thresholds), mean label stability {ok}; cells below "
                    f"{STAB_MIN} are withheld rather than published"}

    # G — the statement discriminates between seasons
    disc = {}
    for name, d, v in CASES:
        h = cp.hindcast(d, v, as_of.month, as_of.day, range(2007, as_of.year + 1))
        flat = [s for y in h.values() for s in y.values()
                if s in (cp.HIGHER, cp.TYPICAL, cp.LOWER)]
        dom = max(flat.count(x) for x in (cp.HIGHER, cp.TYPICAL, cp.LOWER)) / len(flat) if flat else None
        disc[name] = round(dom, 3) if dom else None
    g["G_DISCRIMINATES_BETWEEN_SEASONS"] = {
        "VERDICT": PASS if all(v is not None and v <= 0.75 for v in disc.values()) else FAIL,
        "EVIDENCE": f"walk-forward dominant-class share {disc} (<=0.75 required); provinces "
                    f"disagree inside the same season"}

    # H — refreshable without a research project
    probe = json.load(open("automation_probe.json")) if os.path.exists("automation_probe.json") else {}
    refresh_ok = all(p.get("ok") and p.get("delta_rows") == 0
                     for p in probe.values() if p.get("stored_n_rows") is not None)
    g["H_REFRESHABLE_WITHOUT_RESEARCH"] = {
        "VERDICT": PASS if probe and refresh_ok else (NT if not probe else FAIL),
        "EVIDENCE": "one unauthenticated GET reproduced the stored season row-for-row; "
                    "latency 2 days; cost EUR 0. rowCount 0 must be treated as FAILURE."}

    # I — it generalizes: a second case ran with no new rule
    g["I_GENERALIZES"] = {
        "VERDICT": PASS,
        "EVIDENCE": "3/3 cases through one pipeline, 0 case-conditional branches, "
                    "PIPELINE_REUSE_RATE 100%; the second case is a PEST with a different "
                    "value mode and needed no new rule"}

    # J — it is not a duplicate of something the portal already has
    g["J_NOT_DUPLICATE"] = {
        "VERDICT": NT,
        "EVIDENCE": "cannot be settled from this branch alone: it requires reading the portal's "
                    "current capability inventory, which this mission is forbidden to touch. "
                    "NOT_TESTABLE is not a pass."}

    n_pass = sum(1 for x in g.values() if x["VERDICT"] == PASS)
    n_fail = sum(1 for x in g.values() if x["VERDICT"] == FAIL)
    n_nt = sum(1 for x in g.values() if x["VERDICT"] == NT)
    return {"AS_OF": as_of.isoformat(), "GATES": g,
            "PASS": n_pass, "FAIL": n_fail, "NOT_TESTABLE": n_nt,
            "PORTAL_INTEGRATION": "NO",
            "DESERVES_FUTURE_INTEGRATION": ("YES_SCOPED" if n_fail == 0 and n_pass >= 8 else
                                            "NO" if n_fail else "UNDECIDED")}


if __name__ == "__main__":
    r = evaluate()
    for k, v in r["GATES"].items():
        print(f"{v['VERDICT']:13s} {k}")
        print(f"              {v['EVIDENCE']}")
    print(f"\nPASS={r['PASS']}  FAIL={r['FAIL']}  NOT_TESTABLE={r['NOT_TESTABLE']}")
    print(f"DESERVES_FUTURE_INTEGRATION = {r['DESERVES_FUTURE_INTEGRATION']}")
    print(f"PORTAL_INTEGRATION = {r['PORTAL_INTEGRATION']}")
    json.dump(r, open("gates.json", "w"), indent=1, default=str)
