#!/usr/bin/env python3
"""
CERT-V2 / STEP 2 — INVENTORY OF GATES A..J.

The static half (what each gate asks, what it reads, what it emits, what it depends on) is
read off ENGINE/gates.py. The dynamic half (whether it can actually fail) is NOT asserted
here: it is joined in from MUTANTS/*.json, so the verdict column cannot drift away from the
evidence that produced it.

A gate is INVALID if any of these hold:
  T1  it reads back its own argument
  T2  it compares against text it produced itself
  T3  its predicate is arithmetically incapable of returning False
  T4  its predicate is arithmetically incapable of returning True
  T5  it depends on a path outside the repository
  T6  it passes when its own evidence is destroyed  (settled by mutation, not by reading)

Out: p2_gate_inventory.json, p2_gate_inventory.md
"""
import json, os, glob, collections

HERE = os.path.dirname(os.path.abspath(__file__))
MUT = os.path.join(HERE, "MUTANTS")

GATES = {
 "A_OUTCOME_IS_OBSERVED": dict(
    QUESTION="is the published number an OBSERVATION, or could a model output reach it?",
    INPUT="four inadmissible inputs offered to the shipped module: evidence_role MODELLED_RISK, "
          "FORECAST, CONTEXT, and a variable absent from the case's survey schema",
    OUTPUT="PASS iff all four are REFUSED and every live output carries "
           "EVIDENCE_ROLE == OFFICIAL_OBSERVATION",
    SOURCE="ENGINE/gates.py:33-52 -> current_pressure.assert_outcome_admissible -> "
           "contracts.EvidenceRole.GROUND_TRUTH_ADMISSIBLE",
    PROPERTY="a predictor cannot be served as an outcome",
    SHOULD_FAIL_WHEN="the refusals are removed, or an inadmissible role is accepted",
    POSITIVE_CONTROL="the shipped run: four REFUSED",
    NEGATIVE_CONTROL="M01 removes the check; M02 launders the role; M28 stamps the output "
                     "while leaving the refusals in place",
    EXTERNAL_DEPENDENCY="none",
    HISTORY="was a self-certifying constant until 2026-09-06; rewritten twice"),

 "B_NOT_SOLD_AS_FORECAST": dict(
    QUESTION="is the time cutoff real, i.e. does removing it change what gets published?",
    INPUT="rows dated after AS_OF; and a counterfactual run at AS_OF + 30 days",
    OUTPUT="PASS iff future rows exist, some fall inside the window, and moving AS_OF forward "
           "changes at least one province cell",
    SOURCE="ENGINE/gates.py:63-84",
    PROPERTY="no observation dated after the cutoff reaches a published cell",
    SHOULD_FAIL_WHEN="the upper bound of the window is removed",
    POSITIVE_CONTROL="15 future rows exist, 15 inside the window, 18 cells move",
    NEGATIVE_CONTROL="M03 removes the upper bound of the window entirely",
    EXTERNAL_DEPENDENCY="none",
    HISTORY="v1 tested CUTOFF_LABEL == 'NOWCAST', which Cutoff.label() cannot fail to return. "
            "v2 counted future rows. v3 (shipped) counts cells that move when AS_OF advances."),

 "C_REGIONAL_NOT_NATIONAL": dict(
    QUESTION="is the province the unit, and does the province unit change the answer?",
    INPUT="the live output's keys; and the walk-forward class of every province-season",
    OUTPUT="PASS iff no key above the province exists AND provinces of one region disagree in "
           "at least one season-cell",
    SOURCE="ENGINE/gates.py:92-110",
    PROPERTY="a national figure would not be equivalent",
    SHOULD_FAIL_WHEN="geography is collapsed, or every province always agrees",
    POSITIVE_CONTROL="18-19 disagreeing season-cells",
    NEGATIVE_CONTROL="M04 collapses to one national key; M05 gives every fact one province",
    EXTERNAL_DEPENDENCY="none",
    HISTORY="v1 was any('ITALY' in key), which could only fail if the API renamed a province"),

 "D_UNKNOWN_IS_VISIBLE": dict(
    QUESTION="does UNKNOWN survive to the output instead of being rendered as zero or hidden?",
    INPUT="the STATE of every province in the live output",
    OUTPUT="PASS iff at least one province in EACH case is UNKNOWN",
    SOURCE="ENGINE/gates.py:113-118",
    PROPERTY="Missing.NEVER_ZERO — 'we did not look' is never 'there is nothing there'",
    SHOULD_FAIL_WHEN="UNKNOWN cells are hidden, or published as a zero-valued class",
    POSITIVE_CONTROL="one UNKNOWN province in each case today",
    NEGATIVE_CONTROL="M06 hides UNKNOWN; M07 publishes every UNKNOWN but one as VALUE 0.0 "
                     "with the class LOWER_THAN_USUAL",
    EXTERNAL_DEPENDENCY="none",
    HISTORY="unchanged since it was written"),

 "E_REPRODUCIBLE": dict(
    QUESTION="is the output replayable?",
    INPUT="two runs of the definition in the SAME process, one from a cached row set and one "
          "from a fresh load",
    OUTPUT="PASS iff the two JSON dumps are byte-identical",
    SOURCE="ENGINE/gates.py:121-125",
    PROPERTY="the same inputs give the same answer",
    SHOULD_FAIL_WHEN="anything non-deterministic enters the output",
    POSITIVE_CONTROL="byte-identical re-run",
    NEGATIVE_CONTROL="M08 adds a nonce; M09 shuffles file order per call; M27 fixes a "
                     "DIFFERENT file order and holds it, which is what another machine does",
    EXTERNAL_DEPENDENCY="none, and that is the limit: both runs are in one process on one "
                        "filesystem",
    HISTORY="unchanged"),

 "F_LABEL_NOT_PARAMETER_ARTEFACT": dict(
    QUESTION="does the published class survive its own parameters?",
    INPUT="a 135-point grid over window, min_sites, baseline depth and thresholds",
    OUTPUT="PASS iff ANY case reaches mean label stability >= 0.80",
    SOURCE="ENGINE/gates.py:128-133 -> current_pressure.sensitivity",
    PROPERTY="the label is a property of the data, not of the settings",
    SHOULD_FAIL_WHEN="the class starts tracking a parameter",
    POSITIVE_CONTROL="olive 0.92",
    NEGATIVE_CONTROL="M10 makes the current-season value a function of the window",
    EXTERNAL_DEPENDENCY="none",
    HISTORY="unchanged. NOTE the predicate is any(), not all(): the vine case sits at 0.596 "
            "and the gate passes on the olive alone."),

 "G_DISCRIMINATES_BETWEEN_SEASONS": dict(
    QUESTION="does the statement separate seasons, or does it describe the archive?",
    INPUT="the walk-forward class of every province-season since 2007",
    OUTPUT="PASS iff the dominant class share is <= 0.75 in BOTH cases",
    SOURCE="ENGINE/gates.py:136-146",
    PROPERTY="a class that is nearly constant carries no information",
    SHOULD_FAIL_WHEN="one class dominates",
    POSITIVE_CONTROL="M12 balances the classes and the gate passes, so it is not incapable "
                     "of passing",
    NEGATIVE_CONTROL="M11 gives every season-cell the same class",
    EXTERNAL_DEPENDENCY="none",
    HISTORY="FAILS on the shipped data (vine 0.806) because of the pilot's own effect-size "
            "floor. The pilot declined to rewrite it after seeing it fail, and said so."),

 "H_REFRESHABLE_WITHOUT_RESEARCH": dict(
    QUESTION="can this be refreshed without a research project, and is the data current?",
    INPUT="three LIVE HTTP probes (two real, one deliberate negative control) plus "
          "DATA_LATENCY_DAYS from the live output",
    OUTPUT="PASS iff the negative control trips, both real probes are reachable and non-null, "
           "row counts held or grew, and latency <= 21 days in both cases",
    SOURCE="ENGINE/gates.py:156-200 -> ENGINE/automation_probe.fetch",
    PROPERTY="the source is alive, answers with values, and the archive is current",
    SHOULD_FAIL_WHEN="the source dies, answers with nulls, or the archive goes stale",
    POSITIVE_CONTROL="2/2 reachable, control tripped, latency 2 days",
    NEGATIVE_CONTROL="M13 all-null response; M14 dead endpoint; M15 archive frozen 400 days; "
                     "M16 the clock moves one year and the archive does not",
    EXTERNAL_DEPENDENCY="LIVE NETWORK. agroambiente.info.regione.toscana.it must answer for "
                        "this gate to be evaluable at all. AND the reference date is the "
                        "hardcoded constant gates.evaluate(as_of=2026-09-06).",
    HISTORY="v1 required delta_rows == 0, which is backwards. v2 read a cached file. "
            "v3 (shipped) re-probes live and reads latency."),

 "I_GENERALIZES": dict(
    QUESTION="does the pipeline run end-to-end on a case it has never seen?",
    INPUT="CASES/FRUMENTO-SEPTORIA-TOSCANA, hash-checked, run through run_case.season_outcomes",
    OUTPUT="PASS iff >= 5 seasons come out and the series is not constant",
    SOURCE="ENGINE/gates.py:209-236",
    PROPERTY="the engine is a tool, not a fit to two cases",
    SHOULD_FAIL_WHEN="the unseen case is missing, corrupted, or decodes to a constant",
    POSITIVE_CONTROL="14 seasons, 9 distinct values",
    NEGATIVE_CONTROL="M17 breaks the sha256; M18 makes the series constant",
    EXTERNAL_DEPENDENCY="none any more — the arbiter moved this out of /tmp/WHEAT4 into git",
    HISTORY="v1 was a hardcoded PASS constant. v2 read /tmp. v3 (shipped) reads the repo."),

 "J_NOT_DUPLICATE": dict(
    QUESTION="does the portal already ship this capability?",
    INPUT="the portal's meeting-intelligence snapshot",
    OUTPUT="PARTIALLY_OVERLAPS -> recorded as NOT_TESTABLE; or FAIL if the file is unreadable",
    SOURCE="ENGINE/gates.py:238-265",
    PROPERTY="the capability is not a duplicate of something already shipped",
    SHOULD_FAIL_WHEN="the portal already covers the cell",
    POSITIVE_CONTROL="none exists: see T4 below",
    NEGATIVE_CONTROL="M19 points it at the copy that IS in the repository",
    EXTERNAL_DEPENDENCY="A HARDCODED ABSOLUTE PATH: "
                        "/home/user/eame-sintonia/italia-portale/client/"
                        "meeting-intelligence-snapshot.json — while a byte-identical copy is "
                        "tracked in this repository at italia-portale/client/"
                        "meeting-intelligence-snapshot.json",
    HISTORY="was NOT_TESTABLE, then answered in the fifth red-team round"),
}

# T1..T5 are settled by reading the shipped source; T6 is settled by the mutation runs.
STATIC_DEFECTS = {
 "A_OUTCOME_IS_OBSERVED": [],
 "B_NOT_SOLD_AS_FORECAST": [],
 "C_REGIONAL_NOT_NATIONAL": [],
 "D_UNKNOWN_IS_VISIBLE": [],
 "E_REPRODUCIBLE": [],
 "F_LABEL_NOT_PARAMETER_ARTEFACT": [
    "SCOPE: the predicate is any(), so one stable case carries the gate while the other sits "
    "at 0.596. It certifies 'a label somewhere is stable', not 'the label is stable'."],
 "G_DISCRIMINATES_BETWEEN_SEASONS": [],
 "H_REFRESHABLE_WITHOUT_RESEARCH": [
    "T5: requires a live third-party endpoint. Offline, the gate cannot be evaluated at all.",
    "FROZEN CLOCK: latency is compared against a hardcoded AS_OF, so the freshness "
    "certification never expires."],
 "I_GENERALIZES": [],
 "J_NOT_DUPLICATE": [
    "T5: reads a hardcoded absolute path under /home/user that no other machine has, while a "
    "byte-identical copy is tracked in this repository. Same defect class the arbiter used to "
    "overturn gate I, repeated in the same commit.",
    "T4: the predicate is arithmetically incapable of returning PASS. jv is either "
    "(FAIL, 'inventory not readable') or ('PARTIALLY_OVERLAPS', ...), and PARTIALLY_OVERLAPS "
    "is not in (PASS, FAIL, NOT_TESTABLE), so the VERDICT is FAIL or NOT_TESTABLE and never "
    "PASS. A gate that cannot pass is as broken as one that cannot fail."],
}

LETTER = {k[0]: k for k in GATES}


def main():
    muts = collections.defaultdict(list)
    for p in sorted(glob.glob(os.path.join(MUT, "*.json"))):
        m = json.load(open(p))
        muts[m["TARGET_GATE"]].append(m)

    rows, invalid, tautological = [], [], []
    for g, meta in GATES.items():
        letter = g[0]
        mine = muts.get(letter, [])
        killed = [m for m in mine if m.get("OUTCOME") == "KILLED"]
        survived = [m for m in mine if m.get("OUTCOME") == "SURVIVED"]
        other = [m for m in mine if m.get("OUTCOME") not in ("KILLED", "SURVIVED")]
        already = [m for m in mine if m.get("OUTCOME") == "ALREADY_FAILING"]
        poscontrol = [m for m in mine if m.get("OUTCOME") == "POSITIVE_CONTROL_OK"]
        defects = list(STATIC_DEFECTS.get(g, []))
        if survived:
            defects.append("T6: survives a mutation that destroys its own property -> " +
                           "; ".join(f"{m['ID']} ({m['PROPERTY_DESTROYED']})" for m in survived))
        valid = not defects
        if not valid:
            invalid.append(g)
        if any(d.startswith("T3") or d.startswith("T4") for d in defects):
            tautological.append(g)
        rows.append({"GATE_ID": g, **meta,
                     "MUTATIONS_RUN": [m["ID"] for m in mine],
                     "MUTATIONS_KILLED": [m["ID"] for m in killed],
                     "MUTATIONS_SURVIVED": [m["ID"] for m in survived],
                     "OTHER_OUTCOMES": {m["ID"]: m.get("OUTCOME") for m in other},
                     # a gate that is ALREADY FAILING on the shipped data has demonstrated it
                     # can fail; if a positive control also shows it can pass, both halves of
                     # its range are exercised and it does not need a kill on top.
                     "HAS_A_REAL_NEGATIVE_CONTROL": bool(killed) or bool(already and poscontrol),
                     "CAN_IT_PASS": (True if (killed or poscontrol) else
                                     None if not mine else "SEE_DEFECTS"),
                     "IS_ALREADY_FAILING_ON_SHIPPED_DATA": bool(already),
                     "DEFECTS": defects,
                     "VALID": valid})

    allm = [m for v in muts.values() for m in v]
    targeted = [m for m in allm if m["TARGET_GATE"] != "ANY"]
    crosscut = [m for m in allm if m["TARGET_GATE"] == "ANY"]
    out = {"GATES_TOTAL": len(GATES),
           "VALID_GATES": sum(1 for r in rows if r["VALID"]),
           "INVALID_GATES": len(invalid), "INVALID": invalid,
           "TAUTOLOGICAL_GATES": len(tautological), "TAUTOLOGICAL": tautological,
           "GATES_WITH_REAL_NEGATIVE_CONTROL": sum(1 for r in rows
                                                   if r["HAS_A_REAL_NEGATIVE_CONTROL"]),
           "MUTATION_TESTS": len(allm),
           "MUTATIONS_CAUGHT": sum(1 for m in targeted if m.get("OUTCOME") == "KILLED"),
           "MUTATIONS_NOT_CAUGHT": sum(1 for m in targeted if m.get("OUTCOME") == "SURVIVED"),
           "CROSS_CUTTING_MUTATIONS": {m["ID"]: {"what": m["PROPERTY_DESTROYED"],
                                                 "outcome": m.get("OUTCOME"),
                                                 "detected_by": m.get("DETECTED_BY")}
                                       for m in sorted(crosscut, key=lambda x: x["ID"])},
           "GATES": rows}
    json.dump(out, open(os.path.join(HERE, "p2_gate_inventory.json"), "w"), indent=1,
              default=str)

    md = ["# CERT-V2 · Step 2 — gate inventory A–J", "",
          f"Gates: {out['GATES_TOTAL']}  ·  valid: {out['VALID_GATES']}  ·  "
          f"invalid: {out['INVALID_GATES']}  ·  incapable of passing or failing: "
          f"{out['TAUTOLOGICAL_GATES']}", "",
          f"Mutations run: {out['MUTATION_TESTS']}  ·  targeted kills: "
          f"{out['MUTATIONS_CAUGHT']}  ·  targeted survivals: {out['MUTATIONS_NOT_CAUGHT']}",
          "",
          "| gate | can it fail? | mutations killed | mutations survived | defects |",
          "|---|---|---|---|---|"]
    for r in rows:
        md.append(f"| {r['GATE_ID']} | {'yes' if r['HAS_A_REAL_NEGATIVE_CONTROL'] else 'NO'} "
                  f"| {', '.join(r['MUTATIONS_KILLED']) or '—'} "
                  f"| {', '.join(r['MUTATIONS_SURVIVED']) or '—'} "
                  f"| {'; '.join(r['DEFECTS'])[:300] or '—'} |")
    md += ["", "## Cross-cutting mutations (no single gate claims these)", "",
           "| id | property destroyed | detected by the suite? | which gate noticed |",
           "|---|---|---|---|"]
    for mid, m in out["CROSS_CUTTING_MUTATIONS"].items():
        verdict = {"DETECTED_BY_SUITE": "yes",
                   "UNDETECTED_BY_SUITE": "NO",
                   "SUITE_CRASHED_NO_VERDICT": "no verdict — the suite raised"}.get(
                       m["outcome"], m["outcome"])
        md.append(f"| {mid} | {m['what']} | {verdict} | "
                  f"{', '.join(m['detected_by'] or []) or '—'} |")
    open(os.path.join(HERE, "p2_gate_inventory.md"), "w", encoding="utf-8").write(
        "\n".join(md) + "\n")

    print("\n".join(md))


if __name__ == "__main__":
    main()
