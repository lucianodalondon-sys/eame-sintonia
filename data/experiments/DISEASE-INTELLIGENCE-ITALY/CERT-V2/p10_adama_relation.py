#!/usr/bin/env python3
"""
CERT-V2 / STEP 10 — ADAMA_PRODUCT_RELATION FOR THE ONE CELL THAT QUALIFIES.

This tool measures disease pressure. It may not promote what it measures into a commercial
opportunity. After a cell is detected, the regulatory owner is asked about the same
COUNTRY x CROP x ISSUE, and only three answers are allowed: PROVED, NOT_FOUND, UNKNOWN.

The handoff already exists in this branch and is versioned:
  italia-portale/client/italy-label-verdicts.js
  applied 2026-09-02, from a reading of 163 official Italian product labels.

Two errors are forbidden and this file guards against both:
  - turning NOT_FOUND into "we did not check"
  - turning NOT_FOUND into "ADAMA has nothing for this crop"
The claim must stay exactly as wide as what was measured: a PRODUCT x CROP x ISSUE triple.
A product registered for the crop is not a product registered for the problem.

Out: p10_adama_relation.json
"""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
JS = os.path.join(REPO, "italia-portale", "client", "italy-label-verdicts.js")


def parse_triples(src, name):
    """Read the VERIFIED / NOT_FOUND arrays out of the shipped handoff, without executing it."""
    m = re.search(name + r"\s*=\s*\[(.*?)\n\s*\];", src, re.S)
    if not m:
        return []
    return [[x.strip().strip("'\"") for x in t.split("',")]
            for t in re.findall(r"\[([^\]]+)\]", m.group(1))]


def norm(t):
    return [s.strip().strip("'\"") for s in t]


def main():
    if not os.path.exists(JS):
        raise SystemExit(f"handoff not found at {JS}")
    src = open(JS, encoding="utf-8").read()
    verified = [norm(t) for t in parse_triples(src, "VERIFIED")]
    not_found = [norm(t) for t in parse_triples(src, "NOT_FOUND")]
    audit_date = (re.search(r"AUDIT_DATE:\s*'([^']+)'", src) or [None, None])[1]
    scope_note = (re.search(r"SCOPE_NOTE:\s*'([^']+)'", src) or [None, None])[1]
    absence = (re.search(r"ABSENCE_RULE:\s*'([^']+)'", src) or [None, None])[1]
    default = "LABEL_CHECK_NEEDED" if "return 'LABEL_CHECK_NEEDED'" in src else None

    CELL = {"COUNTRY": "ITALY", "CROP": "Olive", "ISSUE": "Olive Fruit Fly",
            "AGRONOMIC_NAME": "Bactrocera oleae, damaging infestation",
            "REGION": "Toscana", "DATE": "2026-09-06"}

    hits_nf = [t for t in not_found if t[0].lower() == "olive"
               and t[1].lower() == "olive fruit fly"]
    hits_v = [t for t in verified if t[0].lower() == "olive"
              and t[1].lower() == "olive fruit fly"]
    crop_any_v = [t for t in verified if t[0].lower() == "olive"]
    crop_any_nf = [t for t in not_found if t[0].lower() == "olive"]

    if hits_v:
        state = "PROVED"
    elif hits_nf:
        state = "NOT_FOUND"
    else:
        state = "UNKNOWN"

    out = {
      "CELL": CELL,
      "HANDOFF": {"FILE": "italia-portale/client/italy-label-verdicts.js",
                  "IN_GIT": True, "AUDIT_DATE": audit_date,
                  "AUDIT_SOURCE": "reading of 163 official Italian product labels",
                  "SCOPE_NOTE": scope_note, "ABSENCE_RULE": absence,
                  "DEFAULT_FOR_ANYTHING_NOT_LISTED": default,
                  "n_VERIFIED": len(verified), "n_NOT_FOUND": len(not_found)},
      "ADAMA_PRODUCT_RELATION": state,
      "EXACTLY_WHAT_WAS_ADJUDICATED": {
          "TRIPLES_MARKED_NOT_FOUND": hits_nf,
          "TRIPLES_MARKED_VERIFIED": hits_v,
          "SCOPE": "three named products were checked against the Olive x Olive Fruit Fly pair "
                   "and none of the three was found on a label for it, in that reading. The "
                   "handoff's own rule governs the sentence: ABSENCE IN OUR READING is not "
                   "ABSENCE IN THE WORLD."},
      "WHAT_THIS_DOES_NOT_SAY": [
          "It does not say the pair was not checked. It was, on 2026-09-02, and the answer is "
          "recorded in the repository.",
          "It does not say ADAMA has no olive product. The handoff adjudicates PRODUCT x CROP "
          "x ISSUE triples, not portfolios, and anything not listed defaults to "
          f"{default} — not to absence.",
          "It does not say ADAMA has no product for this PROBLEM. Only the three named "
          "products were adjudicated for this pair. A fourth product is UNKNOWN, not absent.",
          "A product registered for OLIVE is not a product registered for OLIVE FRUIT FLY. "
          f"The handoff lists {len(crop_any_v)} verified and {len(crop_any_nf)} not-found "
          "triples on the olive crop; the crop and the problem are separate questions."],
      "COMMERCIAL_CONSEQUENCE_STATED_PLAINLY":
          "The only cell that passes the agronomic publication gate on 2026-09-06 is the one "
          "cell where our own reading of the labels did not find a product to sell against the "
          "problem. That is not a reason to soften either number.",
      "PERMITTED_OUTPUT_STATES_OF_THIS_TOOL": [
          "DISEASE_PRESSURE_SIGNAL", "RADAR_SIGNAL", "EXPLORATORY_SIGNAL",
          "INSUFFICIENT_EVIDENCE", "NO_SIGNAL"],
      "FORBIDDEN_OUTPUT_STATES": ["COMMERCIAL_OPPORTUNITY", "any recommended commercial action"],
      "WHAT_THIS_CELL_IS_TODAY": "DISEASE_PRESSURE_SIGNAL (agronomic), with "
                                 "ADAMA_PRODUCT_RELATION = NOT_FOUND for the three adjudicated "
                                 "products and UNKNOWN for the rest of the portfolio. It is "
                                 "NOT a commercial opportunity and this tool may not make it one."}

    json.dump(out, open(os.path.join(HERE, "p10_adama_relation.json"), "w"),
              indent=1, default=str)
    print(json.dumps({k: v for k, v in out.items()
                      if k not in ("WHAT_THIS_DOES_NOT_SAY",)}, indent=1)[:2200])
    print("\nWHAT_THIS_DOES_NOT_SAY:")
    for s in out["WHAT_THIS_DOES_NOT_SAY"]:
        print("  -", s)


if __name__ == "__main__":
    main()
