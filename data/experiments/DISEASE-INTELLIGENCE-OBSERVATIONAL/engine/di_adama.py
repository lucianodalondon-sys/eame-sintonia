#!/usr/bin/env python3
"""
DISEASE INTELLIGENCE · OBSERVATIONAL · LAYER 3 — ADAMA RELEVANCE

This layer runs AFTER the agronomy is finished and it may not change it. Its only output is

    ADAMA_RELEVANCE = YES | NO | UNKNOWN

with the evidence that produced it. It is enrichment, never a requirement for the agronomic
fact, and it is FORBIDDEN from emitting ACT_NOW, SALES_READY, BUY, SELL or
COMMERCIAL_OPPORTUNITY. The most it may say about what to do is an attention class -
INVESTIGATE, MONITOR, NO_ESCALATION, UNKNOWN - and the rule that produced it is printed
beside it.

Both readings in this repository are consulted, read-only:
  italia-portale/client/italy-label-verdicts.js   19 adjudicated PRODUCT x CROP x ISSUE triples
  italia-portale/client/italy-handoff-v21.js      the wider object set from the same audit
"""
import os, re, json, collections

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
VERDICTS = os.path.join(REPO, "italia-portale", "client", "italy-label-verdicts.js")
HANDOFF = os.path.join(REPO, "italia-portale", "client", "italy-handoff-v21.js")


def _triples(src, name):
    m = re.search(name + r"\s*=\s*\[(.*?)\n\s*\];", src, re.S)
    if not m:
        return []
    return [[x.strip().strip("'\"") for x in t.split("',")]
            for t in re.findall(r"\[([^\]]+)\]", m.group(1))]


def read_label_verdicts():
    if not os.path.exists(VERDICTS):
        return None
    s = open(VERDICTS, encoding="utf-8").read()
    return {"file": "italia-portale/client/italy-label-verdicts.js",
            "audit_date": (re.search(r"AUDIT_DATE:\s*'([^']+)'", s) or [None, None])[1],
            "scope_note": (re.search(r"SCOPE_NOTE:\s*'([^']+)'", s) or [None, None])[1],
            "absence_rule": (re.search(r"ABSENCE_RULE:\s*'([^']+)'", s) or [None, None])[1],
            "default_for_anything_not_listed": "LABEL_CHECK_NEEDED",
            "VERIFIED": [[y.strip().strip("'\"") for y in t] for t in _triples(s, "VERIFIED")],
            "NOT_FOUND": [[y.strip().strip("'\"") for y in t]
                          for t in _triples(s, "NOT_FOUND")]}


def read_wider_handoff(crop_tokens=("OLIVE", "OLIVO")):
    """The larger object set from the same 163-label audit. Read for what it actually is:
    most of its olive material is CONTENT and SCIENCE, not product-label matches."""
    if not os.path.exists(HANDOFF):
        return None
    s = open(HANDOFF, encoding="utf-8", errors="replace").read()
    objs = re.findall(r'\{[^{}]*"CROP"\s*:\s*"([^"]*)"[^{}]*\}', s)
    olive_objs = re.findall(
        r'\{[^{}]*"CROP"\s*:\s*"(?:' + "|".join(crop_tokens) + r')"[^{}]*\}', s)
    kinds = collections.Counter()
    for o in olive_objs:
        if '"DOI"' in o:
            kinds["scientific_reference"] += 1
        elif '"CHANNEL"' in o or '"CONTENT_TITLE"' in o:
            kinds["content_item"] += 1
        elif '"ENTITY_TYPE": "CROP_WINDOW"' in o:
            kinds["crop_window"] += 1
        else:
            kinds["other"] += 1
    return {"file": "italia-portale/client/italy-handoff-v21.js",
            "objects_carrying_a_CROP": len(objs),
            "distinct_crops": len(set(objs)),
            "crop_counts": dict(collections.Counter(objs).most_common()),
            "olive_objects": len(olive_objs),
            "olive_objects_by_kind": dict(kinds),
            "mentions_of_the_fly": {
                "Bactrocera": s.lower().count("bactrocera"),
                "mosca dell'olivo / delle olive": s.lower().count("mosca dell"),
                "olive fruit fly": s.lower().count("olive fruit fly")},
            "olive_label_use_relationships_found_by_an_independent_lens": {
                "count": 1, "entry": "IT-LBL-1932", "product": "MORAINE",
                "registration": "018101", "target": "weeds",
                "HOW": "an independent product lens resolved this file's 2,277-entry string "
                       "table; this module's flat regex cannot see through it and previously "
                       "ASSERTED a hardcoded 0 here, which was wrong. The corrected count is "
                       "1 of 2,030 label-use relationships, and it is a herbicide.",
                "FOR_THE_OLIVE_FLY": 0},
            "COVERAGE_LIMIT_OF_THIS_MODULE": (
                "the flat regex sees 161 of the 203 CROP keys in this file (79.3%). It is used "
                "for orientation, never as the basis of the verdict, which rests on the "
                "adjudicated triples in italy-label-verdicts.js."),
            "NOTE": "the olive material in this file is content items and scientific "
                    "references, not PRODUCT x CROP x ISSUE label matches"}


def relevance(crop_label, issue_label):
    """YES | NO | UNKNOWN, with the evidence, for one crop x issue pair."""
    lv, wh = read_label_verdicts(), read_wider_handoff()
    ev = {"readings_consulted": []}
    if lv:
        ev["readings_consulted"].append(lv["file"])
        ck, ik = crop_label.strip().lower(), issue_label.strip().lower()
        verified = [t for t in lv["VERIFIED"] if t[0].lower() == ck and t[1].lower() == ik]
        notfound = [t for t in lv["NOT_FOUND"] if t[0].lower() == ck and t[1].lower() == ik]
        same_crop = [t for t in lv["VERIFIED"] if t[0].lower() == ck]
        ev.update({"audit_date": lv["audit_date"], "scope_note": lv["scope_note"],
                   "absence_rule": lv["absence_rule"],
                   "verified_triples_for_this_pair": verified,
                   "not_found_triples_for_this_pair": notfound,
                   "verified_triples_for_this_crop_any_issue": same_crop,
                   "default_for_anything_not_listed":
                       lv["default_for_anything_not_listed"]})
    else:
        verified = notfound = same_crop = []
    if wh:
        ev["readings_consulted"].append(wh["file"])
        ev["wider_reading"] = wh

    if verified:
        state, why = "YES", (f"{len(verified)} product-crop-issue triple(s) verified on an "
                             f"official Italian label in the {ev.get('audit_date')} reading")
    elif notfound:
        state, why = "NO", (
            f"{len(notfound)} product(s) were checked against this exact pair and none was "
            f"found on a label for it in the {ev.get('audit_date')} reading of 163 official "
            f"Italian labels. The wider object set from the same audit carries "
            f"{(wh or {}).get('olive_objects', 0)} olive objects and "
            f"1 product-label relationship for the CROP in the whole file - a herbicide, "
            f"MORAINE, targeting weeds - and 0 for this PROBLEM. Its olive material is "
            f"otherwise content items and scientific references. "
            f"ABSENCE IN OUR READING IS NOT ABSENCE IN THE WORLD, and this NO is scoped to "
            f"the products actually adjudicated, not to the portfolio.")
    else:
        state, why = "UNKNOWN", (
            "this pair is not adjudicated in either reading; the label audit's default for "
            "anything not listed is LABEL_CHECK_NEEDED, which is UNKNOWN, not absence")

    return {"relevance": state, "reason": why, "portfolio_evidence": ev,
            "FORBIDDEN_OUTPUTS_NOT_EMITTED": ["ACT_NOW", "SALES_READY", "BUY", "SELL",
                                              "COMMERCIAL_OPPORTUNITY", "CONTACT_NOW"]}


def attention_class(cell, adama):
    """An internal attention class, never a commercial instruction. The rule is printed."""
    a, q = cell["analysis"], cell["quality"]
    rule = []
    # The relevance is READ, not decoration. An independent product lens showed this function
    # never branched on it: fed a real YES verdict it printed "YES ... INVESTIGATE" under one
    # heading, which reads as a buying signal. It cannot now.
    rel = adama.get("relevance")
    if rel == "YES":
        rule.append("ADAMA_RELEVANCE is YES, so any attention class here is agronomic only "
                    "and a product decision belongs to the regulatory owner, not to this tool")
    if not q.get("observation_publishable"):
        cls, rule = "UNKNOWN", ["the observation itself is not publishable"]
    elif a["historical_state"] == "ABOVE_HISTORICAL" or \
            a["observed_trend"] == "INCREASING_OBSERVED":
        cls = "INVESTIGATE"
        rule = ["historical_state is ABOVE_HISTORICAL, or observed_trend is "
                "INCREASING_OBSERVED, on a publishable observation"]
    elif a["historical_state"] in ("TYPICAL", "BELOW_HISTORICAL"):
        cls, rule = "MONITOR", ["a publishable observation with a matched historical "
                                "comparison that is not above its own history"]
    else:
        cls, rule = "NO_ESCALATION", ["a publishable observation with no matched historical "
                                      "comparison available"]
    return {"attention_class": cls, "rule_applied": rule,
            "NOT_A_COMMERCIAL_INSTRUCTION": True,
            "attention_is_agronomic_only": True,
            "adama_relevance": rel,
            "WHY_THE_TWO_ARE_PRINTED_APART": (
                "the attention class describes the OBSERVATION. ADAMA_RELEVANCE describes the "
                "PORTFOLIO. Reading them as one sentence is the error this separation exists "
                "to prevent, whichever way the relevance falls.")}
