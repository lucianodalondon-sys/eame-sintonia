#!/usr/bin/env python3
"""RT6-A. G10 says 'the output contains no commercial action vocabulary'.
Apply G10's OWN word list, with G10's OWN method (uppercase substring), to the three
things a user actually receives: the shipped OUT json, the layer-3 object, and the
rendered human text. G10 itself tests none of them."""
import os, sys, json, io, datetime as dt
HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.path.join(HERE, "..", "engine")
sys.path.insert(0, ENGINE)
import di_report, di_render, di_adama

BANNED = ("ACT_NOW", "SALES_READY", "BUY", "SELL", "OPPORTUNITY",
          "CONTACT_NOW", "COMMERCIAL_OPPORTUNITY")           # verbatim from t2_gates.g10


def g10_on(text, label):
    T = text.upper()
    hits = {w: T.count(w) for w in BANNED if w in T}
    print(f"  {label:52s} {'FAIL' if hits else 'PASS'}  {hits}")
    return hits


sheet, loaded, cells, adama = di_report.run(dt.date(2026, 9, 6))

print("WHAT G10 ACTUALLY TESTS (bare di_observe.cell, no adama, no attention):")
bare = [{k: v for k, v in c.items() if k not in ("adama", "attention", "provenance")}
        for c in cells]
g10_on(json.dumps(bare, default=str), "bare cells (== t2_gates.cells())")

print("\nWHAT THE USER ACTUALLY GETS:")
outp = os.path.join(HERE, "..", "OUT", "report_ACTIVE_INFESTATION_COUNT_2026-09-06.json")
if os.path.exists(outp):
    g10_on(open(outp, encoding="utf-8").read(), "OUT/report_...json (the shipped artifact)")
g10_on(json.dumps(cells, default=str), "full cells incl. adama + attention")
g10_on(json.dumps(adama, default=str), "the layer-3 ADAMA object alone")

region = di_render.render_region(cells, adama)
prov = "\n".join(di_render.render_province(c, adama, c["attention"]) for c in cells)
g10_on(region, "rendered REGION text (di_render.render_region)")
g10_on(prov, "rendered PROVINCE text x10 (di_render.render_province)")
g10_on(region + prov, "the whole human reading a person reads")

print("\nWHERE THE WORDS ARE:")
for i, line in enumerate((region + "\n" + prov).splitlines()):
    if any(w in line.upper() for w in BANNED):
        print(f"  render line {i}: {line.strip()[:140]}")
        break
print("  di_adama.relevance()['FORBIDDEN_OUTPUTS_NOT_EMITTED'] =",
      adama["FORBIDDEN_OUTPUTS_NOT_EMITTED"])
