#!/usr/bin/env python3
"""RT6-K. The Olive x Olive Fruit Fly case is safe because the ANSWER is NO, not because
the DESIGN forbids the combination. Show what the same renderer prints when the pair is
one the same repository adjudicates YES. Nothing is invented: the YES comes from
italy-label-verdicts.js, the cell is the real Lucca cell."""
import os, sys, datetime as dt
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "engine"))
import di_report, di_adama, di_render

sheet, loaded, cells, adama_no = di_report.run(dt.date(2026, 9, 6))
lucca = next(c for c in cells if c["province"] == "Lucca")

print("=== is there any code path that forbids ADAMA_RELEVANCE=YES + INVESTIGATE? ===")
for f in ("di_adama.py", "di_render.py"):
    t = open(os.path.join(HERE, "..", "engine", f), encoding="utf-8").read()
    print(f"  {f}: mentions of 'YES' next to a guard/raise: "
          f"{'raise' in t or 'assert' in t}  "
          f"attention_class reads adama['relevance']: "
          f"{'adama[' in t and 'relevance' in t}")
print("  di_adama.attention_class() branches on: quality.observation_publishable,")
print("  analysis.historical_state, analysis.observed_trend. It NEVER branches on")
print("  adama['relevance'] - it only copies it into the output dict.\n")

for pair in [("Grapevine", "Flavescenza Dorata"), ("Wheat", "Cereal Aphids"),
             ("Maize", "Diabrotica")]:
    a = di_adama.relevance(*pair)
    print(f"  relevance{pair} -> {a['relevance']}  "
          f"({len(a['portfolio_evidence']['verified_triples_for_this_pair'])} verified "
          f"triples: "
          f"{[t[2] for t in a['portfolio_evidence']['verified_triples_for_this_pair']]})")

print("\n=== THE CARD THE RENDERER WOULD PRINT for a YES pair on a rising province ===")
print("=== (real Lucca cell + real Grapevine x Flavescenza Dorata verdict) ===")
a = di_adama.relevance("Grapevine", "Flavescenza Dorata")
at = di_adama.attention_class(lucca, a)
txt = di_render.render_province(lucca, a, at)
i = [n for n, l in enumerate(txt.splitlines()) if "RELEV" in l][0]
for l in txt.splitlines()[i:i+4]:
    print("  |", l)
print("\n  attention_class returned:", at)
print("\n  A Market Development reader sees, under one heading:")
print("    ADAMA RELEVANCE: YES  +  two named products on an official label  +  INVESTIGATE")
print("    on a province whose reading is rising. Nothing in the engine prevents that")
print("    combination; the Olive case avoids it only because the verdict happens to be NO.")
