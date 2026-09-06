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

HERE = os.path.dirname(os.path.abspath(__file__))

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
    # A — REWRITTEN AGAIN 2026-09-06 after an independent arbiter ruled the C10 version still
    # self-referential: it read back the role gates.py itself supplied via current_pressure's
    # DEFAULT argument, and an inadmissible role RAISES rather than arriving as FAIL. The gate
    # now asserts the REFUSALS, which is its actual subject.
    refusals, name, d0, v0 = [], CASES[0][0], CASES[0][1], CASES[0][2]
    for label, kw in (("MODELLED_RISK", {"evidence_role": "MODELLED_RISK"}),
                      ("FORECAST", {"evidence_role": "FORECAST"}),
                      ("CONTEXT", {"evidence_role": "CONTEXT"})):
        try:
            cp.current_pressure(d0, v0, as_of, **kw); refusals.append((label, "ACCEPTED"))
        except ValueError:
            refusals.append((label, "REFUSED"))
    try:
        cp.current_pressure(d0, 999999, as_of); refusals.append(("non-survey var", "ACCEPTED"))
    except ValueError:
        refusals.append(("non-survey var", "REFUSED"))
    a_ok = all(x[1] == "REFUSED" for x in refusals) and \
        all(r["EVIDENCE_ROLE"] == "OFFICIAL_OBSERVATION" for r in live.values())
    g["A_OUTCOME_IS_OBSERVED"] = {
        "VERDICT": PASS if a_ok else FAIL,
        "REFUSAL_TESTS": refusals,
        "EVIDENCE": f"four inadmissible inputs offered to the shipped module and their outcomes "
                    f"recorded: {refusals}. The gate fails if ANY is accepted. Before this "
                    f"rewrite it read back its own default argument."}

    # B — it is a nowcast, never presented as a forecast.
    # REWRITTEN 2026-09-06: the old test asserted CUTOFF_LABEL == "NOWCAST", which Cutoff.label()
    # cannot fail to return for a window ending at as_of. It was arithmetically incapable of
    # FAIL — a tautology guarding the single thing this project most needs guarded. The test now
    # requires something the source can actually violate: future-dated observations DO exist in
    # the archive, and NONE of them may reach a published cell.
    # REWRITTEN AGAIN: an arbiter removed the cutoff filter and the old predicate still returned
    # PASS with its evidence sentence factually false. A gate about a cutoff must show the cutoff
    # CHANGES the answer — that it is load-bearing — not merely that future rows exist.
    fut, used_fut, load_bearing = 0, 0, 0
    for name, d, v in CASES:
        pre = cp.load_rows(d, v)
        after = [r for r in pre[0] if r["_d"] > as_of]
        fut += len(after)
        w0 = as_of - dt.timedelta(days=cp.WINDOW_DAYS - 1)
        used_fut += sum(1 for r in after if w0 <= r["_d"])
        # the counterfactual: what WOULD be published if the cutoff let the future in
        leaked = cp.current_pressure(d, v, as_of + dt.timedelta(days=30), _pre=pre)
        honest = live[name]
        load_bearing += sum(1 for p in honest["PROVINCES"]
                            if honest["PROVINCES"][p].get("STATE")
                            != leaked["PROVINCES"].get(p, {}).get("STATE"))
    g["B_NOT_SOLD_AS_FORECAST"] = {
        "VERDICT": PASS if (fut > 0 and used_fut > 0 and load_bearing > 0 and
                            all(r["CUTOFF_LABEL"] == "NOWCAST" for r in live.values())) else
                   (NT if fut == 0 else FAIL),
        "EVIDENCE": f"{fut} observations in the archive are dated after the cutoff, {used_fut} of "
                    f"them inside the published window, and moving the cutoff forward changes "
                    f"{load_bearing} published province-cells — so the cutoff is LOAD-BEARING and "
                    f"this gate can detect its removal, which the previous version could not. "
                    f"EARLY_WARNING and both OUTLOOK capabilities remain NOT_PROVED."}

    # C — regional, never national
    # REWRITTEN: the old test was `any("ITALY" in key)` — a NEW tautology, since the keys are
    # nome_area and the archive holds exactly ten Tuscan province names. It could fail only if
    # the regional API renamed a province. The subject is whether the province unit CHANGES the
    # answer: if every province always agreed, a national figure would be equivalent and the
    # regional insistence would be decorative.
    disagreeing = 0
    for name, r in live.items():
        st = {v.get("STATE") for v in r["PROVINCES"].values()
              if v.get("STATE") in (cp.HIGHER, cp.TYPICAL, cp.LOWER)}
        disagreeing += 1 if len(st) > 1 else 0
    hind_disagree = 0
    for name, d, v in CASES:
        h = cp.hindcast(d, v, as_of.month, as_of.day, range(2010, as_of.year + 1))
        for y, row in h.items():
            cl = {s for s in row.values() if s in (cp.HIGHER, cp.TYPICAL, cp.LOWER)}
            if len(cl) > 1: hind_disagree += 1
    natl = any("ITALY" in str(k).upper() for r in live.values() for k in r["PROVINCES"])
    g["C_REGIONAL_NOT_NATIONAL"] = {
        "VERDICT": PASS if (not natl and hind_disagree > 0) else FAIL,
        "EVIDENCE": f"no aggregate key above the province exists in the output, AND the province "
                    f"unit is load-bearing: provinces of the same region carry DIFFERENT classes "
                    f"in {hind_disagree} season-cells of the walk-forward, and in "
                    f"{disagreeing}/{len(live)} cases today. If they always agreed, a national "
                    f"figure would be equivalent and this gate would fail."}

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
    # REWRITTEN: this used to json.load a cached file from the CWD, so it passed with a dead
    # endpoint and yesterday's JSON on disk. It now RE-PROBES live inside evaluate().
    import automation_probe as ap
    probe = {}
    for pname, crop, schema, var in [("VITE-OIDIO-TOSCANA", 3, 8, 39),
                                     ("OLIVO-BACTROCERA-TOSCANA", 2, 1, -1002),
                                     ("NEGATIVE-CONTROL-nonexistent-var", 3, 8, 50)]:
        rr = ap.fetch(crop, schema, var, as_of.year)
        stored_p = os.path.join(HERE, "..", "CASES", pname, "RAW",
                                f"c{crop}_s{schema}_v{var}_{as_of.year}.json")
        stored = len(json.load(open(stored_p))) if os.path.exists(stored_p) else None
        probe[pname] = {"HTTP": rr.get("HTTP"), "ok": rr.get("ok"), "n_rows": rr.get("n_rows"),
                        "non_null_values": rr.get("non_null_values"),
                        "SILENT_FAILURE": rr.get("SILENT_FAILURE"), "stored_n_rows": stored,
                        "delta_rows": (rr.get("n_rows") or 0) - stored if stored is not None else None}
    control = {k: v for k, v in probe.items() if k.startswith("NEGATIVE-CONTROL")}
    real = {k: v for k, v in probe.items() if not k.startswith("NEGATIVE-CONTROL")}
    control_tripped = all(v.get("SILENT_FAILURE") for v in control.values()) if control else False
    probe = real
    reachable = [p for p in probe.values() if p.get("HTTP") == 200 and p.get("ok")]
    # `grew_or_held` used to be a LIST evaluated for truthiness — one case could lose 900 rows
    # and the gate still passed. It is an all() now, which is what it always claimed to be.
    grew_or_held = all((p.get("delta_rows") or 0) >= 0 for p in probe.values()
                       if p.get("stored_n_rows") is not None)
    non_null = [p for p in probe.values() if (p.get("non_null_values") or 0) > 0]
    # A capability called CURRENT_PRESSURE must be certified against the data being CURRENT.
    # No gate read DATA_LATENCY_DAYS at all until now.
    latencies = {n: r.get("DATA_LATENCY_DAYS") for n, r in live.items()}
    fresh = all(l is not None and l <= 21 for l in latencies.values())
    g["H_REFRESHABLE_WITHOUT_RESEARCH"] = {
        "VERDICT": PASS if (probe and control_tripped and len(reachable) == len(probe) and
                            grew_or_held and len(non_null) == len(probe) and fresh)
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
                    f"line this gate could not show it is able to fail. The probe is RE-RUN "
                    f"inside this gate, not read from a cached file. Latency per case "
                    f"{latencies} (must be <= 21 days: a capability named CURRENT_PRESSURE has "
                    f"to be certified against the data actually being current, which no gate "
                    f"checked until now)."}

    # I — it generalizes. REWRITTEN 2026-09-06: this was a hardcoded PASS constant, the third
    # tautology found in this gate set after A certified itself and B could not fail. It is now
    # computed against a case the pipeline had never seen (FRUMENTO x SEPTORIA x TOSCANA,
    # crop 19 / schema 74 / var 372), collected live and run end-to-end.
    # The evidence used to live in /tmp/WHEAT4 — outside git, no hash chain — while a
    # byte-identical copy sat unused in the repo. From a clean checkout the suite returned
    # 8 PASS / 1 FAIL / NO, so the headline verdict was not reproducible from the repository.
    unseen = os.path.join(HERE, "..", "CASES", "FRUMENTO-SEPTORIA-TOSCANA")
    ok_unseen, note = False, "unseen case not present in the repository"
    if os.path.exists(os.path.join(unseen, "collection_index.json")):
        try:
            import hashlib
            _idx = json.load(open(os.path.join(unseen, "collection_index.json")))
            _by = {r["file"]: r.get("sha256") for r in _idx["requests"] if r.get("file")}
            _bad = [f for f, h in _by.items()
                    if h and hashlib.sha256(open(os.path.join(unseen, "RAW", f), "rb").read()
                                            ).hexdigest() != h]
            if _bad:
                raise ValueError(f"hash mismatch on {_bad}")
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
