#!/usr/bin/env python3
"""
RT6 / ADAMA · part 2 — is the PRODUCT_LINK_STATE stamped on the shipped cases supported by the
label audit that is supposed to govern it?

italy-label-verdicts.js says, in its own header:
    "The presentation layer APPLIES these verdicts. It must never research, infer or promote a
     product relationship on its own."
and its verdict() default is LABEL_CHECK_NEEDED — never a promotion.

meeting-intelligence-snapshot.json ships 43 cases, each with a PRODUCT_LINK_STATE. This script
re-derives each case's verdict through the handoff's own key() function and compares.

Read-only. Nothing under italia-portale/ is written.

Out: rt6_adama_link_state.json
"""
import os, sys, json, re, collections

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
CLIENT = os.path.join(REPO, "italia-portale", "client")
src = open(os.path.join(CLIENT, "italy-label-verdicts.js"), encoding="utf-8").read()
labels = open(os.path.join(CLIENT, "meeting-labels.js"), encoding="utf-8").read()
S = json.load(open(os.path.join(CLIENT, "meeting-intelligence-snapshot.json"), encoding="utf-8"))


def arr(name):
    m = re.search(name + r"\s*=\s*\[(.*?)\n\s*\];", src, re.S)
    return [[x.strip().strip("'\"") for x in t.split("',")]
            for t in re.findall(r"\[([^\]]+)\]", m.group(1))]


VER, NF = arr("VERIFIED"), arr("NOT_FOUND")


def toks(block):
    m = re.search(r'F\["' + block + r'"\] = \{(.*?)\n  \};', labels, re.S)
    return {k: v for k, v in re.findall(r'"([A-Z_]+)": \["[^"]*", "([^"]*)"\]', m.group(1))}


CROP, ISSUE = toks("CROP"), toks("TARGET")
# generous synonyms, declared: the portal's issue vocabulary and the audit's do not join on
# exact strings, so the comparison is made as forgiving as possible in the AUDIT's favour.
SYN = {"grape moth": "grapevine moth", "corn borer": "european corn borer",
       "scaphoideus": "flavescenza dorata"}


def norm(s):
    s = (s or "").strip().lower()
    return SYN.get(s, s)


V = {(norm(c), norm(i), norm(p)) for c, i, p in VER}
N = {(norm(c), norm(i), norm(p)) for c, i, p in NF}


def verdict(crop, issue, product):
    k = (norm(crop), norm(issue), norm(product))
    if k in N:
        return "NO_CONFIRMED_MATCH_CURRENT_READING"
    if k in V:
        return "VERIFIED_LABEL_MATCH"
    return "LABEL_CHECK_NEEDED"


def walk(o):
    if isinstance(o, dict):
        yield o
        for x in o.values():
            yield from walk(x)
    elif isinstance(o, list):
        for x in o:
            yield from walk(x)


cases = [d for d in walk(S) if isinstance(d, dict) and "ARCHETYPE" in d]
rows, agree, disagree, unjoinable = [], 0, 0, 0
for c in cases:
    crop = CROP.get(c.get("CROP"))
    issue = ISSUE.get(c.get("TARGET"))
    prods = c.get("MATCHED_COMMERCIAL_PRODUCT_NAMES") or []
    vs = [verdict(crop, issue, re.sub(r"[^A-Za-z0-9 ]", "", p)) for p in prods]
    best = ("VERIFIED_LABEL_MATCH" if "VERIFIED_LABEL_MATCH" in vs else
            "LABEL_CHECK_NEEDED" if "LABEL_CHECK_NEEDED" in vs else
            "NO_CONFIRMED_MATCH_CURRENT_READING" if vs else "NO_PRODUCT_NAMED")
    stamped = c.get("PRODUCT_LINK_STATE")
    row = {"ID": c["ID"], "ARCHETYPE": c.get("ARCHETYPE"), "CROP_TOKEN": c.get("CROP"),
           "TARGET_TOKEN": c.get("TARGET"), "n_products_named": len(prods),
           "PRODUCTS": prods, "STAMPED": stamped, "HANDOFF_SAYS": best}
    rows.append(row)
    if best == stamped:
        agree += 1
    elif best == "NO_PRODUCT_NAMED":
        unjoinable += 1
    else:
        disagree += 1

out = {
 "AUDIT_DATE": re.search(r"AUDIT_DATE:\s*'([^']+)'", src).group(1),
 "HANDOFF_RULE_QUOTED":
     "The presentation layer APPLIES these verdicts. It must never research, infer or promote "
     "a product relationship on its own.  /  The default is LABEL_CHECK_NEEDED - never a "
     "promotion.  (italia-portale/client/italy-label-verdicts.js lines 3-4 and 50)",
 "n_cases": len(cases),
 "STAMPED_PRODUCT_LINK_STATE": dict(collections.Counter(c.get("PRODUCT_LINK_STATE")
                                                        for c in cases)),
 "RE_DERIVED_THROUGH_THE_HANDOFF": dict(collections.Counter(r["HANDOFF_SAYS"] for r in rows)),
 "n_cases_where_the_two_AGREE": agree,
 "n_cases_where_the_two_DISAGREE": disagree,
 "n_cases_with_NO_product_named_at_all_yet_still_stamped": unjoinable,
 "cases_stamped_VERIFIED_LABEL_MATCH_that_the_handoff_does_not_verify":
     [r for r in rows if r["STAMPED"] == "VERIFIED_LABEL_MATCH"
      and r["HANDOFF_SAYS"] != "VERIFIED_LABEL_MATCH"],
 "SYNONYMS_ALLOWED_IN_THE_AUDITS_FAVOUR": SYN,
 "PORTAL_ISSUE_TOKENS": sorted(set(ISSUE.values())),
 "AUDIT_ISSUE_STRINGS": sorted({i for _, i, _ in VER + NF}),
 "ISSUE_VOCABULARIES_THAT_DO_NOT_JOIN_EVEN_WITH_SYNONYMS":
     sorted({norm(i) for i in ISSUE.values()} - {norm(i) for _, i, _ in VER + NF}),
 "WHAT_THE_PORTALS_OWN_AUDIT_SAYS": {
     "italia-portale/audit/blocks/case.spec.json:360":
         "italy-app-model.js currently does not read window.ITALY_LABEL_VERDICTS at all; the "
         "strength classes reach it laundered through D.CASES[i].productLinks.",
     "italia-portale/audit/blocks/case.spec.json:33":
         "Measured: this yields 12 verified + 7 rejected links against 166 products, versus 80 "
         "links today.",
     "italia-portale/audit/blocks/archive.spec.json:304":
         "italy-app-model.js does not read window.ITALY_LABEL_VERDICTS at all."},
 "ROWS": rows}

json.dump(out, open(os.path.join(HERE, "rt6_adama_link_state.json"), "w"),
          indent=1, default=str, ensure_ascii=False)
print(json.dumps({k: v for k, v in out.items() if k != "ROWS"},
                 indent=1, default=str, ensure_ascii=False)[:6000])
