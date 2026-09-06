#!/usr/bin/env python3
"""
RT6 / J — the set of verdicts gate J can return, established by executing its own code.

ENGINE/gates.py 238-265, reproduced faithfully:
    jv = FAIL, "inventory not readable"
    if os.path.exists(snap):
        ... counts fp / cases / olive / vine_tosc ...
        jv = ("PARTIALLY_OVERLAPS", "...")
    g["J_NOT_DUPLICATE"] = {"VERDICT": jv[0] if jv[0] in (PASS, FAIL, NT) else NT, ...}

jv[0] is assigned from exactly two literals: "FAIL" and "PARTIALLY_OVERLAPS". PASS is never
written. The counted numbers are put in EVIDENCE and never enter the verdict, so the portal
could ship ZERO overlapping cases and gate J would still return NOT_TESTABLE.

This script executes both branches and records the outcome, and re-derives the portal counts
the certification quotes.

Out: rt6_gate_j_verdict_space.json
"""
import os, sys, json, re

HERE = os.path.dirname(os.path.abspath(__file__))
CERT = os.path.dirname(HERE)
REPO = os.path.abspath(os.path.join(CERT, "..", "..", "..", ".."))
PASS, FAIL, NT = "PASS", "FAIL", "NOT_TESTABLE"

HARD = "/home/user/eame-sintonia/italia-portale/client/meeting-intelligence-snapshot.json"
REPOCOPY = os.path.join(REPO, "italia-portale", "client", "meeting-intelligence-snapshot.json")

out = {"HARDCODED_PATH": HARD,
       "HARDCODED_PATH_EXISTS_ON_THIS_CHECKOUT": os.path.exists(HARD),
       "HARDCODED_PATH_RESOLVES_TO": os.path.abspath(HARD),
       "IN_REPO_COPY": REPOCOPY, "IN_REPO_COPY_EXISTS": os.path.exists(REPOCOPY)}


def gate_j(snap):
    """gates.py's own gate-J body, character for character on the logic."""
    jv = FAIL, "inventory not readable"
    counts = None
    if os.path.exists(snap):
        S = json.load(open(snap, encoding="utf-8"))

        def _walk(o):
            if isinstance(o, dict):
                yield o
                for x in o.values():
                    yield from _walk(x)
            elif isinstance(o, list):
                for x in o:
                    yield from _walk(x)
        cases = [d for d in _walk(S) if isinstance(d, dict) and "ARCHETYPE" in d]
        fp = [c for c in cases if c.get("ARCHETYPE") == "O1_FIELD_PRESSURE"]
        targets = {str(c.get("TARGET")) for c in cases}
        olive = [t for t in targets if "OLIVE" in t.upper() or "BACTROCERA" in t.upper()]
        vine_tosc = [c for c in fp if c.get("GEOGRAPHY") == "REGION_TOSCANA"
                     and c.get("CROP") == "CROP_GRAPEVINE"]
        counts = {"n_cases": len(cases), "n_O1_FIELD_PRESSURE": len(fp),
                  "n_vine_x_Toscana_field_pressure": len(vine_tosc),
                  "n_olive_TARGETS_in_whole_vocabulary": len(olive)}
        jv = ("PARTIALLY_OVERLAPS", "…")
    verdict = jv[0] if jv[0] in (PASS, FAIL, NT) else NT
    return {"jv0": jv[0], "VERDICT": verdict, "COUNTS": counts}


out["BRANCH_file_absent"] = gate_j(os.path.join(HERE, "__no_such_file__.json"))
out["BRANCH_file_present_repo_copy"] = gate_j(REPOCOPY)
out["BRANCH_the_shipped_gate_takes_on_this_checkout"] = gate_j(HARD)

lits = set(re.findall(r"jv\s*=\s*\(?\s*(FAIL|PASS|NT|\"[A-Z_]+\"|'[A-Z_]+')",
                      open(os.path.join(CERT, "..", "ENGINE", "gates.py"),
                           encoding="utf-8").read()))
out["LITERALS_EVER_ASSIGNED_TO_jv0"] = sorted(lits)
out["REACHABLE_VERDICTS"] = sorted({out["BRANCH_file_absent"]["VERDICT"],
                                    out["BRANCH_file_present_repo_copy"]["VERDICT"]})
out["CAN_GATE_J_RETURN_PASS"] = PASS in out["REACHABLE_VERDICTS"]
out["CONSEQUENCE"] = (
    "gates.evaluate() sets DESERVES_FUTURE_INTEGRATION = YES_SCOPED only when n_fail == 0 and "
    "n_pass >= 8. Gate J can only ever contribute a FAIL or a NOT_TESTABLE, never a PASS, so "
    "the headline can never be reached with J readable-and-overlapping AND any other gate "
    "failing. The 'analysis' inside gate J — 17 of 43, 3 vine cells, 0 olive targets — is "
    "computed and then discarded: the verdict is a function of os.path.exists() alone.")

# what the committed artefact says versus what this checkout produces
gj = json.load(open(os.path.join(CERT, "..", "ENGINE", "gates.json"), encoding="utf-8"))
out["COMMITTED_gates.json"] = {
    "J_VERDICT": gj["GATES"]["J_NOT_DUPLICATE"]["VERDICT"],
    "J_ANSWER": gj["GATES"]["J_NOT_DUPLICATE"].get("ANSWER"),
    "PASS": gj["PASS"], "FAIL": gj["FAIL"], "NOT_TESTABLE": gj["NOT_TESTABLE"],
    "DESERVES_FUTURE_INTEGRATION": gj["DESERVES_FUTURE_INTEGRATION"]}
out["WHAT_THIS_CHECKOUT_WOULD_PRODUCE_FOR_J"] = out["BRANCH_the_shipped_gate_takes_on_this_checkout"]["VERDICT"]

json.dump(out, open(os.path.join(HERE, "rt6_gate_j_verdict_space.json"), "w"),
          indent=1, default=str)
print(json.dumps(out, indent=1, default=str))
