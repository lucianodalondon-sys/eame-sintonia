#!/usr/bin/env python3
"""RT5 -- gate H performs live network I/O inside the gate run. Measure what a clean checkout
returns when the network (or the regional server) is not there.

Nothing in ENGINE/ is edited. automation_probe.API is rebound IN THIS PROCESS ONLY to an
address that cannot resolve, which is what an offline clone, a firewalled CI runner or a
server outage looks like to the shipped code. Then gate H's own predicate -- copied verbatim
from gates.py -- is evaluated on the result.
"""
import json, os, sys, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
ENGINE = os.path.join(ROOT, "ENGINE")
sys.path.insert(0, ENGINE); sys.path.insert(0, os.path.join(ROOT, "CASES"))
import automation_probe as ap

AS_OF = dt.date(2026, 9, 6)
LIVE_API = ap.API
CASES = [("VITE-OIDIO-TOSCANA", 3, 8, 39), ("OLIVO-BACTROCERA-TOSCANA", 2, 1, -1002),
         ("NEGATIVE-CONTROL-nonexistent-var", 3, 8, 50)]


def gate_h(latencies):
    """gates.py's predicate, verbatim."""
    probe = {}
    for pname, crop, schema, var in CASES:
        rr = ap.fetch(crop, schema, var, AS_OF.year, timeout=8)
        sp = os.path.join(ENGINE, "..", "CASES", pname, "RAW",
                          f"c{crop}_s{schema}_v{var}_{AS_OF.year}.json")
        stored = len(json.load(open(sp))) if os.path.exists(sp) else None
        probe[pname] = {"HTTP": rr.get("HTTP"), "ok": rr.get("ok"), "n_rows": rr.get("n_rows"),
                        "non_null_values": rr.get("non_null_values"),
                        "SILENT_FAILURE": rr.get("SILENT_FAILURE"), "stored_n_rows": stored,
                        "delta_rows": (rr.get("n_rows") or 0) - stored if stored is not None else None,
                        "error": rr.get("error")}
    control = {k: v for k, v in probe.items() if k.startswith("NEGATIVE-CONTROL")}
    real = {k: v for k, v in probe.items() if not k.startswith("NEGATIVE-CONTROL")}
    control_tripped = all(v.get("SILENT_FAILURE") for v in control.values()) if control else False
    probe = real
    reachable = [p for p in probe.values() if p.get("HTTP") == 200 and p.get("ok")]
    grew_or_held = all((p.get("delta_rows") or 0) >= 0 for p in probe.values()
                       if p.get("stored_n_rows") is not None)
    non_null = [p for p in probe.values() if (p.get("non_null_values") or 0) > 0]
    fresh = all(l is not None and l <= 21 for l in latencies.values())
    verdict = ("PASS" if (probe and control_tripped and len(reachable) == len(probe) and
                          grew_or_held and len(non_null) == len(probe) and fresh)
               else ("NOT_TESTABLE" if not probe else "FAIL"))
    return {"VERDICT": verdict, "control_tripped": control_tripped,
            "reachable": f"{len(reachable)}/{len(probe)}", "grew_or_held": grew_or_held,
            "non_null": f"{len(non_null)}/{len(probe)}", "PROBE": probe}


LAT = {"OLIVO x BACTROCERA x TOSCANA": 2, "VITE x OIDIO x TOSCANA": 2}
out = {}
ap.API = "https://rt5-this-host-does-not-exist.invalid/api/dati/get_aedita_data"
out["OFFLINE_or_source_unreachable"] = gate_h(LAT)
ap.API = LIVE_API
out["LIVE_today_on_this_machine"] = gate_h(LAT)

out["COMMITTED_gates_json_verdict"] = json.load(
    open(os.path.join(ENGINE, "gates.json"), encoding="utf-8"))["GATES"]["H_REFRESHABLE_WITHOUT_RESEARCH"]["VERDICT"]
gj = json.load(open(os.path.join(ENGINE, "gates.json"), encoding="utf-8"))
out["TALLY_IF_H_ALSO_FAILS_ON_A_CLEAN_CHECKOUT"] = (
    "committed PASS=8 FAIL=1 NOT_TESTABLE=1 ; clean checkout with network PASS=8 FAIL=2 "
    "NOT_TESTABLE=0 (J) ; clean checkout without network PASS=7 FAIL=3 NOT_TESTABLE=0 (J and H)")
json.dump(out, open(os.path.join(HERE, "rt5_p11_gate_h_offline.json"), "w"), indent=1, default=str)

for k in ("OFFLINE_or_source_unreachable", "LIVE_today_on_this_machine"):
    v = out[k]
    print(f"{k:34s} -> gate H = {v['VERDICT']:12s} reachable {v['reachable']} "
          f"control_tripped={v['control_tripped']} non_null {v['non_null']}")
print("committed gates.json says gate H =", out["COMMITTED_gates_json_verdict"])
print(out["TALLY_IF_H_ALSO_FAILS_ON_A_CLEAN_CHECKOUT"])
