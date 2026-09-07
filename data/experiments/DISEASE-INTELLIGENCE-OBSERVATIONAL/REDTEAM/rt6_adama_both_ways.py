#!/usr/bin/env python3
"""RT6-B. Count the triples and the objects myself. Is the NO too strong, too weak, or
measured at all?"""
import os, sys, re, json, collections
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "engine"))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
import di_adama

V = os.path.join(REPO, "italia-portale", "client", "italy-label-verdicts.js")
H = os.path.join(REPO, "italia-portale", "client", "italy-handoff-v21.js")
sv = open(V, encoding="utf-8").read()

print("=== 1. COUNT THE TRIPLES MYSELF ===")
lv = di_adama.read_label_verdicts()
print(f"  VERIFIED parsed by the engine : {len(lv['VERIFIED'])}")
print(f"  NOT_FOUND parsed by the engine: {len(lv['NOT_FOUND'])}")
print(f"  total                         : {len(lv['VERIFIED'])+len(lv['NOT_FOUND'])}  "
      f"(docstring claims 19)")
print(f"  source file self-reports      : verifiedCount/notFoundCount computed in JS")
# independent count straight off the source text
vblock = sv.split("const VERIFIED = [")[1].split("];")[0]
nblock = sv.split("const NOT_FOUND = [")[1].split("];")[0]
print(f"  independent line count        : VERIFIED={vblock.count('[')} "
      f"NOT_FOUND={nblock.count('[')}")
olive_v = [t for t in lv["VERIFIED"] if t[0] == "Olive"]
olive_n = [t for t in lv["NOT_FOUND"] if t[0] == "Olive"]
print(f"  Olive rows: VERIFIED={len(olive_v)}  NOT_FOUND={len(olive_n)} -> {olive_n}")
prods = sorted({t[2] for t in lv["VERIFIED"]} | {t[2] for t in lv["NOT_FOUND"]})
print(f"  distinct products adjudicated anywhere in the audit: {len(prods)} -> {prods}")

print("\n=== 2. THE DENOMINATOR THE TOOL NEVER PRINTS ===")
cat = os.path.join(REPO, "italia-portale", "client", "italy-catalog.js")
cs = open(cat, encoding="utf-8").read()
cat_ids = sorted(set(re.findall(r'CATPRD_[A-Z0-9_]+', cs)))
print(f"  products in italy-catalog.js       : {len(cat_ids)}")
print(f"  products adjudicated by the audit  : {len(prods)}")
print(f"  products checked for Olive x OFF   : {len(olive_n)}")
print(f"  the sentence says '3 product(s) were checked' and never says 3 OF WHAT")

print("\n=== 3. IS product_label_matches_for_olive MEASURED OR ASSERTED? ===")
src = open(os.path.join(HERE, "..", "engine", "di_adama.py"), encoding="utf-8").read()
for i, line in enumerate(src.splitlines(), 1):
    if "product_label_matches_for_olive" in line:
        print(f"  di_adama.py:{i}  {line.strip()}")
print("  -> it is a literal in a dict. No code counts it. The rendered sentence "
      "'0 product-label matches for the crop' is an ASSERTION rendered as a MEASUREMENT.")

print("\n=== 4. IS olive_objects=11 A COUNT OF THE FILE, OR OF WHAT THE REGEX CAN SEE? ===")
s = open(H, encoding="utf-8", errors="replace").read()
print(f"  file size                                  : {len(s):,} chars")
print(f"  raw occurrences of the key \"CROP\"          : {s.count(chr(34)+'CROP'+chr(34)):,}")
wh = di_adama.read_wider_handoff()
print(f"  objects the FLAT regex can see              : {wh['objects_carrying_a_CROP']:,}")
print(f"  -> the regex is {chr(123)}[^{chr(123)}{chr(125)}]*\"CROP\"...{chr(125)} : it cannot "
      f"match any object containing a nested object or array.")
print(f"  coverage of the key by the regex            : "
      f"{100.0*wh['objects_carrying_a_CROP']/max(1,s.count(chr(34)+'CROP'+chr(34))):.1f}%")
print(f"  olive_objects reported                      : {wh['olive_objects']}")
print(f"  olive_objects_by_kind                       : {wh['olive_objects_by_kind']}")
print(f"  crop tokens searched                        : ('OLIVE','OLIVO')")
for tok in ('"CROP": "OLIVE"', '"CROP":"OLIVE"', 'CROP_OLIVE', 'OLIVO', 'Olivo', 'olive'):
    print(f"    literal {tok!r:22s} occurrences in the file: {s.lower().count(tok.lower()):,}")
print(f"  mentions_of_the_fly                         : {wh['mentions_of_the_fly']}")

print("\n=== 5. THE TOKEN THE UPSTREAM REFUSED TO USE ===")
print("  upstream verdict() returns, for a NOT_FOUND row: 'NO_CONFIRMED_MATCH_CURRENT_READING'")
print(f"  upstream STRENGTH labels: "
      f"{re.findall(chr(39)+'([A-Z_]+)'+chr(39)+': .label.:', sv)}")
print("  the engine compresses that to the single token: "
      f"{di_adama.relevance('Olive','Olive Fruit Fly')['relevance']!r}")
print("  the string 'NO' does not appear as a verdict value anywhere in the source file: "
      f"{not re.search(chr(39)+'NO'+chr(39), sv)}")

print("\n=== 6. THE REGION CARD TRUNCATES THE CAVEAT ===")
ad = di_adama.relevance("Olive", "Olive Fruit Fly")
full = ad["reason"]
print(f"  full reason length            : {len(full)} chars")
print(f"  region card prints reason[:200]:")
print(f"    ...{full[:200][-60:]!r}")
print(f"  CUT OFF, never shown at region level ({len(full)-200} chars):")
print(f"    {full[200:]!r}")
key = "ABSENCE IN OUR READING IS NOT ABSENCE IN THE WORLD"
print(f"  does the region card contain {key!r}? {key in full[:200]}")
key2 = "scoped to the products actually adjudicated, not to the portfolio"
print(f"  does the region card contain the scoping clause? {key2 in full[:200]}")
