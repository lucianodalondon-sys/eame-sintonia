#!/usr/bin/env python3
"""
RT6 / ADAMA — is the product relationship invented, overstated or understated?

Read-only. Nothing under italia-portale/ is written.

Four questions:
  1. What does italy-label-verdicts.js actually adjudicate, and what is its default?
  2. Is "ADAMA_PRODUCT_RELATION = NOT_FOUND" too strong for what the handoff says?
  3. Is it too weak — does the evidence support a wider claim?
  4. Where in this repository does a disease-pressure signal become a commercial opportunity,
     a recommendation or a product suggestion — and where is "no product" read as
     "this cell does not matter"?

Out: rt6_adama_portfolio.json
"""
import os, sys, json, re, collections

HERE = os.path.dirname(os.path.abspath(__file__))
CERT = os.path.dirname(HERE)
REPO = os.path.abspath(os.path.join(CERT, "..", "..", "..", ".."))
CLIENT = os.path.join(REPO, "italia-portale", "client")
JS = os.path.join(CLIENT, "italy-label-verdicts.js")
SNAP = os.path.join(CLIENT, "meeting-intelligence-snapshot.json")
CAT = os.path.join(CLIENT, "italy-catalog.js")

out = {}
src = open(JS, encoding="utf-8").read()


def arr(name):
    m = re.search(name + r"\s*=\s*\[(.*?)\n\s*\];", src, re.S)
    return [[x.strip().strip("'\"") for x in t.split("',")]
            for t in re.findall(r"\[([^\]]+)\]", m.group(1))] if m else []


VER, NF = arr("VERIFIED"), arr("NOT_FOUND")
strength = sorted(set(re.findall(r"^\s{4}([A-Z_]+):\s*\{ label:", src, re.M)))
returned = sorted(set(re.findall(r"return '([A-Z_]+)'", src)))

out["1_WHAT_THE_HANDOFF_ADJUDICATES"] = {
    "UNIT": "a PRODUCT x CROP x ISSUE triple; key(crop, issue, product) joined by '|'",
    "NOT_a_product": "a product alone has no verdict; KLARTAN 20 EW is only adjudicated "
                     "against Olive|Olive Fruit Fly",
    "NOT_a_pair": "a crop x issue pair alone has no verdict either",
    "NOT_a_portfolio": "no statement is made about a portfolio",
    "n_VERIFIED_triples": len(VER), "n_NOT_FOUND_triples": len(NF),
    "n_triples_total": len(VER) + len(NF),
    "distinct_products_adjudicated": sorted({t[2] for t in VER + NF}),
    "distinct_crop_x_issue_pairs_adjudicated": sorted({f"{t[0]}|{t[1]}" for t in VER + NF}),
    "DEFAULT_FOR_ANYTHING_ELSE": re.search(r"return '([A-Z_]+)';\s*\n\s*\}", src).group(1),
    "STRENGTH_LEVELS_DEFINED": strength,
    "STRENGTH_LEVELS_verdict_CAN_RETURN": returned,
    "STRENGTH_LEVEL_NEVER_RETURNED": sorted(set(strength) - set(returned)),
    "SEMANTIC_RULE_IN_THE_FILE": re.search(r"ABSENCE_RULE:\s*'([^']+)'", src).group(1)}

# 2 ── the vocabulary the certification substituted
out["2_IS_NOT_FOUND_TOO_STRONG"] = {
    "WORD_THE_HANDOFF_USES": "NO_CONFIRMED_MATCH_CURRENT_READING",
    "WORD_THE_CERTIFICATION_USES": "NOT_FOUND",
    "p10_ALLOWED_VOCABULARY": ["PROVED", "NOT_FOUND", "UNKNOWN"],
    "MAPPING_APPLIED_BY_p10": "NO_CONFIRMED_MATCH_CURRENT_READING -> NOT_FOUND",
    "WHAT_IS_LOST": "the qualifier CURRENT_READING. The handoff's own header says a product "
                    "missing from this reading is NOT evidence that ADAMA has no product; the "
                    "substituted word carries the opposite everyday sense.",
    "MITIGATION_PRESENT_IN_p10": "the JSON's WHAT_THIS_DOES_NOT_SAY block restores the "
                                 "qualifier in prose, in four sentences, below the field."}

# 3 ── the denominator: how big is "the rest of the portfolio"?
csrc = open(CAT, encoding="utf-8").read()
cat = json.loads(csrc[csrc.index("{"):csrc.rindex("}") + 1])
cat_names = sorted({i["name"] for i in cat["ITEMS"]})
adjudicated = {t[2] for t in VER + NF}
out["3_IS_IT_TOO_WEAK_THE_PORTFOLIO_DENOMINATOR"] = {
    "products_in_the_shipped_ADAMA_Italy_catalog_layer": len(cat_names),
    "catalog_RESEARCH_BASELINE_total": cat["RESEARCH_BASELINE"]["TOTAL"],
    "distinct_products_the_label_audit_adjudicated_ANYWHERE": len(adjudicated),
    "of_those_present_in_the_catalog_layer": sorted(adjudicated & set(cat_names)),
    "of_those_absent_from_the_catalog_layer": sorted(adjudicated - set(cat_names)),
    "products_adjudicated_against_Olive_x_Olive_Fruit_Fly":
        sorted({t[2] for t in NF if t[0] == "Olive" and t[1] == "Olive Fruit Fly"}),
    "olive_triples_marked_VERIFIED": [t for t in VER if t[0].lower() == "olive"],
    "olive_triples_marked_NOT_FOUND": [t for t in NF if t[0].lower() == "olive"],
    "SO_THE_UNKNOWN_REMAINDER_IS":
        f"{len(cat_names)} catalog products minus the {len(adjudicated)} adjudicated anywhere "
        f"= {len(cat_names) - len(adjudicated & set(cat_names))} catalog products never tested "
        f"against ANY crop x issue, plus every product not in this catalog layer at all "
        f"(the catalog file itself records a gap against its own research baseline of "
        f"{cat['RESEARCH_BASELINE']['TOTAL']}).",
    "WIDER_CLAIM_THE_EVIDENCE_DOES_SUPPORT":
        "inside this reading, the olive crop has 0 VERIFIED triples of any kind — not merely "
        "0 for the fruit fly. The certification states this correctly but files it under "
        "WHAT_THIS_DOES_NOT_SAY rather than as a finding."}

# 4 ── where a field-pressure signal becomes an opportunity
S = json.load(open(SNAP, encoding="utf-8"))


def walk(o):
    if isinstance(o, dict):
        yield o
        for x in o.values():
            yield from walk(x)
    elif isinstance(o, list):
        for x in o:
            yield from walk(x)


cases = [d for d in walk(S) if isinstance(d, dict) and "ARCHETYPE" in d]
fp = [c for c in cases if c.get("ARCHETYPE") == "O1_FIELD_PRESSURE"]


def chain(c, link):
    return ((c.get("WHY_NOW_CHAIN") or {}).get(link) or {}).get("OK")


linked = [c for c in fp if chain(c, "VINCULO_COM_PORTFOLIO") is True]
unlinked = [c for c in fp if chain(c, "VINCULO_COM_PORTFOLIO") is False]
out["4_SIGNAL_TO_OPPORTUNITY_IN_THE_PORTAL"] = {
    "FILE": "italia-portale/client/meeting-intelligence-snapshot.json",
    "n_cases_total": len(cases),
    "n_O1_FIELD_PRESSURE": len(fp),
    "every_case_ID_starts_with": sorted({c["ID"].split("_")[0] for c in cases}),
    "commercial_fields_carried_by_a_FIELD_PRESSURE_case":
        sorted(k for k in fp[0] if "COMMERCIAL" in k or "OPPORTUNITY" in k
               or "PORTFOLIO" in k or "PRODUCT" in k or "ACTION" in k),
    "OPPORTUNITY_STATE_distribution": dict(collections.Counter(
        c.get("OPPORTUNITY_STATE") for c in fp)),
    "COMMERCIAL_PRIORITY_distribution": dict(collections.Counter(
        c.get("COMMERCIAL_PRIORITY") for c in fp)),
    "PRODUCT_LINK_STATE_distribution": dict(collections.Counter(
        c.get("PRODUCT_LINK_STATE") for c in fp)),
    "n_field_pressure_cases_naming_at_least_one_commercial_product":
        sum(1 for c in fp if c.get("MATCHED_COMMERCIAL_PRODUCT_NAMES")),
    "distinct_products_named_on_field_pressure_cases": sorted(
        {p for c in fp for p in (c.get("MATCHED_COMMERCIAL_PRODUCT_NAMES") or [])}),
    "ACTION_RECOMMENDATION_STATE_distribution": dict(collections.Counter(
        c.get("ACTION_RECOMMENDATION_STATE") for c in fp))}

out["4b_IS_NO_PRODUCT_READ_AS_THIS_CELL_DOES_NOT_MATTER"] = {
    "MECHANISM": "WHY_NOW_CHAIN has five links; VINCULO_COM_PORTFOLIO ('link to the "
                 "portfolio') is one of them. A case with no portfolio link fails that link "
                 "and collects the code SEM_VINCULO_COM_PORTFOLIO.",
    "n_field_pressure_cases_with_portfolio_link_TRUE": len(linked),
    "n_field_pressure_cases_with_portfolio_link_FALSE": len(unlinked),
    "OPPORTUNITY_SCORE_when_linked": sorted(c.get("OPPORTUNITY_SCORE") for c in linked),
    "OPPORTUNITY_SCORE_when_not_linked": sorted(c.get("OPPORTUNITY_SCORE") for c in unlinked),
    "COMMERCIAL_PRIORITY_when_not_linked": dict(collections.Counter(
        c.get("COMMERCIAL_PRIORITY") for c in unlinked)),
    "n_cases_carrying_the_code_SEM_VINCULO_COM_PORTFOLIO":
        sum(1 for c in cases if "SEM_VINCULO_COM_PORTFOLIO" in (c.get("WHY_NOW_CODES") or [])),
    "LABEL_SHOWN_TO_THE_USER_FOR_A_MISSING_PRODUCT":
        "COMMERCIAL_PRODUCT_MISSING -> 'Nessun prodotto del catalogo su questa coppia' / "
        "'No catalogue product on this pair'  (italia-portale/client/meeting-labels.js:183)"}

json.dump(out, open(os.path.join(HERE, "rt6_adama_portfolio.json"), "w"),
          indent=1, default=str, ensure_ascii=False)
print(json.dumps(out, indent=1, default=str, ensure_ascii=False))
