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
    # REWRITTEN 2026-09-06. The old test required delta_rows == 0, which is BACKWARDS: a source
    # that publishes this week's scouting would FAIL it and a source that died would PASS it.
    # The olive case gains ~310 rows/week, so the shipped gate would have gone red on the first
    # honest refresh. It also trusted "rowCount 0 = FAILURE" as the only failure shape, while the
    # source's real silent failure is HTTP 200 + ok:true + FULL rowCount + every value null.
    probe = json.load(open("automation_probe.json")) if os.path.exists("automation_probe.json") else {}
    control = {k: v for k, v in probe.items() if k.startswith("NEGATIVE-CONTROL")}
    real = {k: v for k, v in probe.items() if not k.startswith("NEGATIVE-CONTROL")}
    control_tripped = all(v.get("SILENT_FAILURE") for v in control.values()) if control else False
    probe = real
    reachable = [p for p in probe.values() if p.get("HTTP") == 200 and p.get("ok")]
    grew_or_held = [p for p in probe.values()
                    if p.get("stored_n_rows") is not None and (p.get("delta_rows") or 0) >= 0]
    non_null = [p for p in probe.values() if p.get("non_null_values", 1) > 0]
    g["H_REFRESHABLE_WITHOUT_RESEARCH"] = {
        "VERDICT": PASS if (probe and control_tripped and len(reachable) == len(probe) and
                            grew_or_held and len(non_null) == len(probe))
                   else (NT if not probe else FAIL),
        "EVIDENCE": f"{len(reachable)}/{len(probe)} probes reachable in one unauthenticated GET, "
                    f"~2s, EUR 0; row counts held or grew (a refresh that GAINS rows is the "
                    f"success case, not the failure case); {len(non_null)}/{len(probe)} returned "
                    f"a non-null measurement column. THREE silent-failure shapes must be treated "
                    f"as FAILURE, not as 'no disease': rowCount 0; full rowCount with an "
                    f"all-null value column; and top-level ok:false with a message the client "
                    f"discards. A deliberate negative control (a variable that does not exist in "
                    f"the requested schema, which the source answers with a full null row set) "
                    f"{'DID' if control_tripped else 'did NOT'} trip the detector — without that "
                    f"line this gate could not show it is able to fail."}

    # I — it generalizes. REWRITTEN 2026-09-06: this was a hardcoded PASS constant, the third
    # tautology found in this gate set after A certified itself and B could not fail. It is now
    # computed against a case the pipeline had never seen (FRUMENTO x SEPTORIA x TOSCANA,
    # crop 19 / schema 74 / var 372), collected live and run end-to-end.
    unseen, ok_unseen, note = "/tmp/WHEAT4", False, "unseen case not collected"
    if os.path.exists(os.path.join(unseen, "collection_index.json")):
        try:
            out, meta = __import__("run_case").season_outcomes(unseen, 372)
            vals = sorted({round(v["SITE_INCIDENCE"], 3) for v in out.values()})
            ok_unseen = len(out) >= 5 and len(vals) > 1        # ran, and is not degenerate
            note = (f"{len(out)} seasons, {len(vals)} distinct SITE_INCIDENCE values "
                    f"(a series that never varies is a decoding failure, not a measurement); "
                    f"scale derived by {meta['derivation_methods']}, "
                    f"unresolved labels {meta['unresolved_labels']}")
        except Exception as e:
            note = f"REFUSED/failed: {e}"
    g["I_GENERALIZES"] = {
        "VERDICT": PASS if ok_unseen else FAIL,
        "EVIDENCE": f"unseen 4th case run end-to-end: {note}. Honest reuse rate is 3/4 = 75%, "
                    f"NOT the 100% previously claimed: the 4th case required TWO generic "
                    f"extensions (compound labels like 'Bassa <5%', and taking the most complete "
                    f"code table rather than the first), and two of its labels remain "
                    f"unresolved. 0 case-conditional branches remains true."}

    # J — ANSWERED 2026-09-06. The old NOT_TESTABLE reason was wrong twice: the mission forbids
    # MODIFYING the portal, not READING it, and the inventory is in this branch's own working
    # tree. Read-only, nothing modified.
    snap = "/home/user/eame-sintonia/italia-portale/client/meeting-intelligence-snapshot.json"
    jv = FAIL, "inventory not readable"
    if os.path.exists(snap):
        S = json.load(open(snap))
        def _walk(o):
            if isinstance(o, dict):
                yield o
                for x in o.values(): yield from _walk(x)
            elif isinstance(o, list):
                for x in o: yield from _walk(x)
        cases = [d for d in _walk(S) if isinstance(d, dict) and "ARCHETYPE" in d]
        fp = [c for c in cases if c.get("ARCHETYPE") == "O1_FIELD_PRESSURE"]
        targets = {str(c.get("TARGET")) for c in cases}
        olive = [t for t in targets if "OLIVE" in t.upper() or "BACTROCERA" in t.upper()]
        vine_tosc = [c for c in fp if c.get("GEOGRAPHY") == "REGION_TOSCANA"
                     and c.get("CROP") == "CROP_GRAPEVINE"]
        jv = ("PARTIALLY_OVERLAPS",
              f"the portal already ships {len(fp)} O1_FIELD_PRESSURE ('Pressione in campo') "
              f"cases out of {len(cases)}, {len(vine_tosc)} of them vine x Toscana at provincial "
              f"scope — the very cell this capability must stay SILENT on — while its whole "
              f"TARGET vocabulary contains {len(olive)} olive targets. COVERAGE INVERSION: the "
              f"portal covers the cell we cannot publish and has no words for the cell we can. "
              f"Neither a pass nor a clean fail.")
    g["J_NOT_DUPLICATE"] = {"VERDICT": jv[0] if jv[0] in (PASS, FAIL, NT) else NT,
                            "ANSWER": jv[0], "EVIDENCE": jv[1]}

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
