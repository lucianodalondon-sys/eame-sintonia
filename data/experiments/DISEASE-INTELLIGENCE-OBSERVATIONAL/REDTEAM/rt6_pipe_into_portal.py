#!/usr/bin/env python3
"""RT6-E2. If someone piped this tool's output into meeting-intelligence-snapshot's case
shape tomorrow, WHICH FIELDS go wrong? Name them, with the vocabularies that collide."""
import os, sys, json, collections, datetime as dt
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "engine"))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
import di_report

snap = json.load(open(os.path.join(REPO, "italia-portale", "client",
                                   "meeting-intelligence-snapshot.json"), encoding="utf-8"))
cases = snap["CASES"]
fields = collections.Counter()
vocab = collections.defaultdict(collections.Counter)
for c in cases:
    for k, v in c.items():
        fields[k] += 1
        if isinstance(v, str):
            vocab[k][v] += 1
print(f"case fields: {len(fields)}   cases: {len(cases)}")

sheet, loaded, cells, adama = di_report.run(dt.date(2026, 9, 6))
cell = cells[0]
have = set()
def flat(o, p=""):
    if isinstance(o, dict):
        for k, v in o.items():
            yield from flat(v, f"{p}.{k}" if p else k)
    else:
        yield p
have = set(flat(cell))
print(f"observational cell leaf fields: {len(have)}")

# the fields the portal case needs and where they could come from
NEED = ["ID", "ARCHETYPE", "CROP", "TARGET", "GEOGRAPHY", "GEOGRAPHIC_SCOPE", "STATUS",
        "OPPORTUNITY_STATE", "COMMERCIAL_PRIORITY", "WHY_COMMERCIAL_CODES",
        "EXTERNAL_MATERIAL_READY", "WHY_NOW_CODES", "ACTION_CHAIN_LINKS", "SIGNAL_DATE",
        "SIGNAL_CURRENCY", "COMMERCIAL_TIMING_BASIS", "WINDOW_TYPE", "WINDOW_DEFINED",
        "WINDOW_OPEN_NOW", "WINDOW_STATE", "PEST_STAGE_STATE",
        "ACTION_RECOMMENDATION_STATE", "THRESHOLD_STATE", "NEED_DIRECTION",
        "PORTFOLIO_MATCHES", "PRODUCT_LINK_STATE", "COMMERCIAL_PRODUCT_COUNT",
        "COMMERCIAL_MAGNITUDE", "COMMERCIAL_MAGNITUDE_DIMENSIONS", "SIGNAL_CONFIDENCE",
        "CONFIDENCE", "OPPORTUNITY_SCORE", "PUBLICATION_STATE", "CLAIM_GEOGRAPHY",
        "CLAIM_GEOGRAPHY_HOLDS", "ACTION_BY_DEPARTMENT", "EVIDENCE_IDS", "TRAIL_STATE"]
SRC = {
 "ID": "FABRICATED (the tool has no opportunity id; an OPP_ id would be minted here)",
 "ARCHETYPE": "FABRICATED - the only archetype that fits is O1_FIELD_PRESSURE, and there "
              "are 17 of them already; the tool has no archetype concept",
 "CROP": "cell.crop.canonical_id = CROP_OLIVE  (portal namespace matches)",
 "TARGET": "cell.problem.canonical_id = PEST_BACTROCERA_OLEAE; portal namespace is "
           "ISSUE_* (ISSUE_OLIVE_FLY) - NAMESPACE MISMATCH",
 "GEOGRAPHY": "cell.province, but the portal field holds REGION_* ids",
 "STATUS": "NO SAFE SOURCE - see the vocabulary collision below",
 "OPPORTUNITY_STATE": "FABRICATED - the tool never decides an opportunity exists",
 "COMMERCIAL_PRIORITY": "NO SAFE SOURCE - see below",
 "SIGNAL_DATE": "observation.last_observation (real)",
 "SIGNAL_CURRENCY": "derivable from as_of - last_observation (real)",
 "WINDOW_*": "FABRICATED - the tool has no window concept at all",
 "PEST_STAGE_STATE": "FABRICATED - the tool reads a count, not a stage",
 "ACTION_RECOMMENDATION_STATE": "FABRICATED - the source's recommendation is never read",
 "THRESHOLD_STATE": "observation.source_band is the SOURCE's band; the portal field means "
                    "'the source declared a threshold' - NOT THE SAME CLAIM",
 "NEED_DIRECTION": "FABRICATED - the tool never reads a need",
 "PORTFOLIO_MATCHES": "adama.portfolio_evidence has 3 NOT_FOUND products; the portal field "
                      "is a list of MATCHES, so 3 non-matches would land in a match list",
 "PRODUCT_LINK_STATE": "NO_CONFIRMED_MATCH_CURRENT_READING (safe, if not compressed to NO)",
 "COMMERCIAL_MAGNITUDE": "FABRICATED",
 "COMMERCIAL_MAGNITUDE_DIMENSIONS": "drupes_sampled / n_visits / n_sites would be dropped "
                                    "in here and read as market size",
 "OPPORTUNITY_SCORE": "FABRICATED - the tool emits no score",
 "CLAIM_GEOGRAPHY_HOLDS": "the tool's own CANNOT_CONCLUDE forbids exactly this claim",
 "ACTION_BY_DEPARTMENT": "FABRICATED - the tool emits no department action",
 "EVIDENCE_IDS": "provenance.source_files + hashes (real, but a different id space)",
}
print("\nFIELD-BY-FIELD, WHAT WOULD FILL IT:")
for f in NEED:
    k = f if f in SRC else ("WINDOW_*" if f.startswith("WINDOW_") else None)
    print(f"  {f:34s} {SRC.get(k, 'FABRICATED') if k else 'FABRICATED'}")

print("\nTHE TWO VOCABULARY COLLISIONS THAT DO THE DAMAGE")
print(f"  portal STATUS values             : {dict(vocab['STATUS'])}")
print(f"  tool attention_class values      : "
      f"{sorted(set(c['attention']['attention_class'] for c in cells))} "
      f"(closed set: INVESTIGATE, MONITOR, NO_ESCALATION, UNKNOWN)")
print("  -> no portal STATUS means 'we could not compare'. The nearest neighbours of")
print("     INVESTIGATE are VALIDATE_NOW and ACT_NOW; of MONITOR is WATCH; of")
print("     NO_ESCALATION there is NONE. A mechanical map promotes INVESTIGATE.")
print(f"\n  portal COMMERCIAL_PRIORITY values: {dict(vocab['COMMERCIAL_PRIORITY'])}")
print("  tool ADAMA_RELEVANCE values      : ['YES', 'NO', 'UNKNOWN']")
print("  -> COMMERCIAL_PRIORITY HAS NO VALUE MEANING 'NO'. Its floor is TO_VALIDATE.")
print("     An ADAMA_RELEVANCE=NO case cannot be represented as NO in that field;")
print("     the least-committal landing is TO_VALIDATE, which reads as a live item.")
print(f"     TO_VALIDATE is already the modal value: {vocab['COMMERCIAL_PRIORITY']['TO_VALIDATE']}"
      f" of {len(cases)} cases.")
print(f"\n  portal PUBLICATION_STATE values  : {dict(vocab['PUBLICATION_STATE'])}")
print("  tool quality.observation_publishable / historical_comparison_publishable are TWO")
print("  gates; the portal has ONE field. The 7 provinces with no publishable history")
print("  would arrive carrying a publishable observation and lose the second gate.")
