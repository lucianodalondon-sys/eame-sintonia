#!/usr/bin/env python3
"""
DISEASE INTELLIGENCE · OBSERVATIONAL · TEST 5 — IS ANY OF THIS WORTH READING?

Correctness is not usefulness. This file takes the WHOLE population - every province, both
metrics, at the pilot date - so there is no cherry-pick to hide, and asks of each cell the
eight questions the mission listed. Then it scores value by a rule written down BEFORE the
answers were looked at, and prints the rule beside every score.

THE RULE
  HIGH    the observation is publishable AND it says something a reader did not already know:
          either a matched historical comparison that is not TYPICAL, or a named direction of
          change over windows that have already ended, or a reading outside the source's own
          green band
  MEDIUM  publishable, with a matched historical comparison, and it is TYPICAL - a confirmed
          "nothing unusual" is worth something, but less
  LOW     publishable observation only: no comparable history and no named direction. It says
          what was found and nothing more
  UNKNOWN the observation itself is not publishable

Out: t5_value.json, t5_value.md
"""
import os, sys, json, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "engine"))
import di_core, di_observe, di_adama

CASE = os.path.abspath(os.path.join(HERE, "..", "..", "DISEASE-INTELLIGENCE-ITALY",
                                    "CASES", "OLIVO-BACTROCERA-TOSCANA"))
AS_OF = dt.date(2026, 9, 6)
METRICS = ["ACTIVE_INFESTATION_COUNT", "DAMAGING_INFESTATION_COUNT"]

RULE = ("HIGH: publishable AND (a matched historical class that is not TYPICAL, OR a named "
        "direction of change, OR a reading outside the source's green band). "
        "MEDIUM: publishable, matched history available, and TYPICAL. "
        "LOW: publishable observation only. "
        "UNKNOWN: the observation is not publishable.")


def score(c):
    a, q, o = c["analysis"], c["quality"], c["observation"]
    if not q["observation_publishable"]:
        return "UNKNOWN", "the observation itself is not publishable"
    band = (o.get("source_band") or {}).get("meaning")
    named = a["observed_trend"] in ("INCREASING_OBSERVED", "DECREASING_OBSERVED")
    hist = q["historical_comparison_publishable"]
    if (hist and a["historical_state"] != "TYPICAL") or named or band not in ("green", "none"):
        why = []
        if hist and a["historical_state"] != "TYPICAL":
            why.append(f"matched history says {a['historical_state']}")
        if named:
            why.append(f"a named direction: {a['observed_trend']}")
        if band not in ("green", "none"):
            why.append(f"outside the green band: {band}")
        return "HIGH", "; ".join(why)
    if hist:
        return "MEDIUM", "matched history available and it says TYPICAL"
    return "LOW", "an observation with no comparable history and no named direction"


def eight_questions(c, adama):
    o, a, q = c["observation"], c["analysis"], c["quality"]
    return {
        "A_WHAT_WAS_OBSERVED": (
            None if o.get("value_pct") is None else
            f"{o['value_pct']}% of sampled drupes ({o['infested_drupes']} of "
            f"{o['drupes_sampled']}), source band "
            f"{(o.get('source_band') or {}).get('label')}"),
        "B_HOW_MANY_OBSERVATIONS": (
            f"{o.get('n_visits', 0)} visits to {o.get('n_sites', 0)} groves by "
            f"{o.get('n_orgs', 0)} organisations"),
        "C_HOW_RECENT": {"window": o.get("window"),
                         "last_observation": o.get("last_observation"),
                         "as_of": c["as_of"]},
        "D_AGAINST_ITS_OWN_HISTORY": {"state": a["historical_state"],
                                      "reason": a["historical_reason"],
                                      "matched_seasons": a["matched_panel_seasons"]},
        "E_AGAINST_OTHER_PROVINCES": "computed at the region level, not here",
        "F_OBSERVED_CHANGE": {"trend": a["observed_trend"],
                              "reason": a["observed_trend_reason"]},
        "G_ANOMALY": ("NOT_DEFINED: this build has no anomaly definition it can defend, so it "
                      "publishes none"),
        "H_PUBLISHABLE": {"observation": q["observation_publishable"],
                          "historical_comparison": q["historical_comparison_publishable"],
                          "reason": q["publishable_reason"]},
        "I_ADAMA_RELEVANCE": {"relevance": adama["relevance"],
                              "attention_class": c["attention"]["attention_class"]},
        "WHY_DM_MIGHT_CARE": why_dm(c),
        "WHAT_WE_CANNOT_CONCLUDE": [
            "that this will rise or fall - there is no forecast in this tool",
            "anything about groves nobody visited",
            "that there is a commercial opportunity",
        ] + ([] if a["matched_panel_seasons"] >= c["params"]["MIN_BASELINE_SEASONS"] else
             ["how this compares with this province's own past: the groves monitored now are "
              "not the ones monitored then"]),
    }


def why_dm(c):
    a, o, q = c["analysis"], c["observation"], c["quality"]
    if not q["observation_publishable"]:
        return None
    if a["observed_trend"] == "INCREASING_OBSERVED":
        return (f"observed infestation in {c['province']} rose across three windows that have "
                f"already ended, ending at {o['value_pct']}% of {o['drupes_sampled']} sampled "
                f"drupes; its own history is "
                f"{'comparable' if q['historical_comparison_publishable'] else 'NOT comparable'}")
    if q["historical_comparison_publishable"] and a["historical_state"] == "BELOW_HISTORICAL":
        return (f"{c['province']} reads below its own matched history in "
                f"{a.get('matched_seasons_now_is_lower_than_then')} of "
                f"{a['matched_panel_seasons']} comparable seasons")
    if q["historical_comparison_publishable"] and a["historical_state"] == "ABOVE_HISTORICAL":
        return (f"{c['province']} reads above its own matched history in "
                f"{a.get('matched_seasons_now_is_higher_than_then')} of "
                f"{a['matched_panel_seasons']} comparable seasons")
    return None


def main():
    sheet = di_core.load_sheet()
    loaded = di_core.load_visits(CASE, sheet, AS_OF)
    provs = sorted({v["province"] for v in loaded["visits"] if v["province"]})
    adama = di_adama.relevance("Olive", "Olive Fruit Fly")

    rows, md = [], ["# Value test — the whole population, no cherry-pick", "",
                    f"as_of {AS_OF} · {len(provs)} provinces × {len(METRICS)} metrics = "
                    f"{len(provs) * len(METRICS)} cells", "", f"RULE: {RULE}", ""]
    for m in METRICS:
        for p in provs:
            c = di_observe.cell(loaded["visits"], sheet, p, m, AS_OF)
            c["adama"] = adama
            c["attention"] = di_adama.attention_class(c, adama)
            v, why = score(c)
            rows.append({"province": p, "metric": m, "VALUE": v, "why": why,
                         "questions": eight_questions(c, adama)})
    counts = {}
    for r in rows:
        counts[r["VALUE"]] = counts.get(r["VALUE"], 0) + 1

    md.append("| province | metric | value | why | reading | history | trend |")
    md.append("|---|---|---|---|---|---|---|")
    for r in rows:
        q = r["questions"]
        md.append(f"| {r['province']} | {r['metric'].replace('_INFESTATION_COUNT','')} "
                  f"| **{r['VALUE']}** | {r['why']} | {q['A_WHAT_WAS_OBSERVED']} "
                  f"| {q['D_AGAINST_ITS_OWN_HISTORY']['state']} "
                  f"({q['D_AGAINST_ITS_OWN_HISTORY']['matched_seasons']} seasons) "
                  f"| {q['F_OBSERVED_CHANGE']['trend']} |")
    md += ["", f"**Distribution over the whole population: {counts}**", "",
           "## The cells a Market Development reader could act on", ""]
    acted = [r for r in rows if r["questions"]["WHY_DM_MIGHT_CARE"]]
    for r in acted:
        md.append(f"- **{r['province']} · {r['metric'].replace('_INFESTATION_COUNT','')}** — "
                  f"{r['questions']['WHY_DM_MIGHT_CARE']}")
    md += ["", f"{len(acted)} of {len(rows)} cells produce a sentence a reader could act on.",
           "", "## What none of them supports", "",
           "- any forecast", "- any statement about groves nobody visited",
           "- any commercial action: ADAMA_RELEVANCE for Olive x Olive Fruit Fly is "
           f"{adama['relevance']}"]

    out = {"AS_OF": AS_OF.isoformat(), "RULE": RULE, "POPULATION": len(rows),
           "DISTRIBUTION": counts,
           "CELLS_PRODUCING_AN_ACTIONABLE_SENTENCE": len(acted),
           "ROWS": rows}
    json.dump(out, open(os.path.join(HERE, "t5_value.json"), "w", encoding="utf-8"),
              indent=1, default=str)
    open(os.path.join(HERE, "t5_value.md"), "w", encoding="utf-8").write("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
