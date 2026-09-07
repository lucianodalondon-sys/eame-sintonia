#!/usr/bin/env python3
"""RT6-F. Every field a reader is given, for all TEN provinces, plus a recomputation of
the attention rule from the printed rule alone."""
import os, sys, json, datetime as dt
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "engine"))
import di_report, di_adama, di_render

sheet, loaded, cells, adama = di_report.run(dt.date(2026, 9, 6))
print(f"{'PROV':14s} {'rate%':>8s} {'inf/samp':>13s} {'band':>6s} {'vis':>4s} {'sites':>5s} "
      f"{'orgs':>4s} {'HIST':>17s} {'m.seas':>6s} {'TREND':>19s} {'pub':>3s} {'histpub':>7s} "
      f"{'ATTN':>13s}")
rows = []
for c in sorted(cells, key=lambda x: -(x["observation"].get("value_pct") or -1)):
    o, a, q = c["observation"], c["analysis"], c["quality"]
    at = c["attention"]
    rows.append((c["province"], o["value_pct"], a["historical_state"],
                 a["matched_panel_seasons"], a["observed_trend"],
                 q["observation_publishable"], q["historical_comparison_publishable"],
                 at["attention_class"]))
    print(f"{c['province']:14s} {o['value_pct']:8.4f} "
          f"{str(o['infested_drupes'])+'/'+str(o['drupes_sampled']):>13s} "
          f"{o['source_band']['meaning']:>6s} {o['n_visits']:4d} {o['n_sites']:5d} "
          f"{o['n_orgs']:4d} {a['historical_state']:>17s} {a['matched_panel_seasons']:6d} "
          f"{a['observed_trend']:>19s} {str(q['observation_publishable'])[:3]:>3s} "
          f"{str(q['historical_comparison_publishable'])[:5]:>7s} "
          f"{at['attention_class']:>13s}")

print("\n--- unmatched vs matched historical state (what was suppressed) ---")
for c in cells:
    a = c["analysis"]
    print(f"  {c['province']:14s} matched={a['historical_state']:>17s}  "
          f"unmatched={a['historical_state_unmatched']:>17s}  "
          f"pctl={a.get('percentile_against_own_history')}  "
          f"baseline_n={a['baseline_n']}  matched_seasons={a['matched_panel_seasons']}  "
          f"overlap_median={a['panel_overlap_with_baseline_seasons']['median_groves_shared']}")

print("\n--- CAN A READER RECOMPUTE THE ATTENTION CLASS? ---")
# the rule text as printed, re-implemented from the printed words only
def recompute_from_printed_rule(c):
    a, q = c["analysis"], c["quality"]
    if not q["observation_publishable"]:
        return "UNKNOWN"
    if a["historical_state"] == "ABOVE_HISTORICAL" or a["observed_trend"] == "INCREASING_OBSERVED":
        return "INVESTIGATE"
    if a["historical_state"] in ("TYPICAL", "BELOW_HISTORICAL"):
        return "MONITOR"
    return "NO_ESCALATION"
ok = 0
for c in cells:
    mine, theirs = recompute_from_printed_rule(c), c["attention"]["attention_class"]
    ok += mine == theirs
    if mine != theirs:
        print(f"  MISMATCH {c['province']}: recomputed {mine} vs emitted {theirs}")
print(f"  recomputed {ok} of {len(cells)} correctly from the printed rule "
      f"(inputs needed: historical_state, observed_trend, observation_publishable)")
print("  BUT: is every input the rule needs actually PRINTED in the province card?")
txt = di_render.render_province(cells[0], adama, cells[0]["attention"])
for needed in ("ABOVE_HISTORICAL", "INCREASING_OBSERVED", "observation_publishable"):
    print(f"    the literal token {needed!r} appears in a province card: "
          f"{needed in txt or needed.lower() in txt.lower()}")
print("\n  NO_ESCALATION reachable? provinces whose matched state is INSUFFICIENT_DATA "
      "and trend is not INCREASING:")
print("   ", [c["province"] for c in cells
              if c["quality"]["observation_publishable"]
              and c["analysis"]["historical_state"] not in ("TYPICAL", "BELOW_HISTORICAL",
                                                            "ABOVE_HISTORICAL")
              and c["analysis"]["observed_trend"] != "INCREASING_OBSERVED"])
print("  attention class distribution:",
      {k: sum(1 for c in cells if c["attention"]["attention_class"] == k)
       for k in ("INVESTIGATE", "MONITOR", "NO_ESCALATION", "UNKNOWN")})
