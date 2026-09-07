#!/usr/bin/env python3
"""RT6-C2. Does the handoff contain any object that ties an ADAMA product to the olive
crop or to the olive fly? If yes, the engine's '0 product-label matches' is a claim it
did not test. If no, the NO survives on this axis."""
import os, re, json, collections
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
s = open(os.path.join(REPO, "italia-portale", "client", "italy-handoff-v21.js"),
         encoding="utf-8", errors="replace").read()

# balanced-brace object extractor around every occurrence of an olive token
def objects_around(tokens, radius_guard=200000):
    hits = []
    for t in tokens:
        for m in re.finditer(re.escape(t), s):
            i = m.start()
            # walk back to the opening brace of the innermost enclosing object
            depth, j = 0, i
            while j > 0:
                if s[j] == '}':
                    depth += 1
                elif s[j] == '{':
                    if depth == 0:
                        break
                    depth -= 1
                j -= 1
            depth, k = 0, i
            while k < len(s):
                if s[k] == '{':
                    depth += 1
                elif s[k] == '}':
                    if depth == 0:
                        break
                    depth -= 1
                k += 1
            hits.append(s[j:k+1])
    return hits

objs = objects_around(['"CROP_OLIVE"', '"ISSUE_OLIVE_FLY"'])
print(f"enclosing objects around CROP_OLIVE / ISSUE_OLIVE_FLY: {len(objs)}")
kinds = collections.Counter()
prodlinked = []
for o in objs:
    keys = set(re.findall(r'"([A-Z_]+)"\s*:', o))
    et = re.search(r'"ENTITY_TYPE"\s*:\s*"([^"]+)"', o)
    kinds[et.group(1) if et else ("has_DOI" if '"DOI"' in o else
          "has_CHANNEL" if '"CHANNEL"' in o else "unlabelled")] += 1
    if re.search(r'CATPRD_|"PRODUCT_NAME"|"REGISTRATION_NUMBER"|LABEL_USE', o):
        prodlinked.append(o)
print("  by ENTITY_TYPE / shape:", dict(kinds.most_common()))
print(f"\nOBJECTS THAT TIE OLIVE TO A PRODUCT / LABEL / REGISTRATION: {len(prodlinked)}")
for o in prodlinked[:5]:
    print("   ", o[:400].replace("\n", " "))

print("\n--- does any CATPRD product appear within 2000 chars of an olive token? ---")
near = 0
for m in re.finditer(r'CROP_OLIVE|ISSUE_OLIVE_FLY|"OLIVE"|"OLIVO"', s):
    w = s[max(0, m.start()-2000):m.start()+2000]
    if "CATPRD_" in w:
        near += 1
print(f"  olive tokens with a CATPRD_ id within +-2000 chars: {near} "
      f"of {len(re.findall(r'CROP_OLIVE|ISSUE_OLIVE_FLY|\"OLIVE\"|\"OLIVO\"', s))}")

print("\n--- the three ADAMA olive products, searched by name in the handoff ---")
for p in ("KLARTAN 20 EW", "KLARTAN SMART", "MAVRIK SMART", "KLARTAN", "MAVRIK",
          "tau-fluvalinate", "TAU_FLUVALINATE", "TAU-FLUVALINATE"):
    print(f"  {p:20s} {s.upper().count(p.upper()):4d} occurrences in italy-handoff-v21.js")
