#!/usr/bin/env python3
"""RT6-C. The 42 objects the flat regex cannot see. Do any of them carry an olive crop?
And what is the real product denominator the sentence '3 product(s) were checked' omits?"""
import os, re, json, collections
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
H = os.path.join(REPO, "italia-portale", "client", "italy-handoff-v21.js")
s = open(H, encoding="utf-8", errors="replace").read()

flat = re.findall(r'\{[^{}]*"CROP"\s*:\s*"([^"]*)"[^{}]*\}', s)
allv = re.findall(r'"CROP"\s*:\s*"([^"]*)"', s)
print(f'occurrences of the key "CROP"      : {len(allv)}')
print(f'seen by the engine (flat objects)  : {len(flat)}')
print(f'INVISIBLE to the engine            : {len(allv)-len(flat)}')
cf, ca = collections.Counter(flat), collections.Counter(allv)
print("\nvalues seen by the engine:", dict(cf.most_common()))
print("\nALL values of the key, however nested:", dict(ca.most_common()))
missed = ca - cf
print("\nVALUES THE ENGINE NEVER COUNTED (all - flat):", dict(missed.most_common()))
oliv = [v for v in allv if v.upper() in ("OLIVE", "OLIVO")]
print(f"\nolive-valued CROP keys, all objects nested or not : {len(oliv)}")
print(f"olive objects the engine reports                  : 11")

print("\n--- other olive namespaces in the same file, which the engine does not read ---")
for pat in (r'"CROP_ID"\s*:\s*"CROP_OLIVE"', r'CROP_OLIVE', r'ISSUE_OLIVE[A-Z_]*',
            r'"PRODUCT_ID"\s*:\s*"CATPRD_[A-Z0-9_]+"'):
    m = re.findall(pat, s)
    print(f"  {pat:44s} {len(m):5d}  distinct={len(set(m))}")
iss = collections.Counter(re.findall(r'"(ISSUE_[A-Z0-9_]+)"', s))
print("  ISSUE_ tokens containing OLIVE:",
      {k: v for k, v in iss.items() if "OLIV" in k or "BACTRO" in k or "MOSCA" in k})

print("\n--- the product denominator ---")
cat = open(os.path.join(REPO, "italia-portale", "client", "italy-catalog.js"),
           encoding="utf-8", errors="replace").read()
print(f"  italy-catalog.js size {len(cat):,}")
for pat in (r'CATPRD_[A-Z0-9_]+', r'"PRODUCT_NAME"\s*:\s*"([^"]+)"',
            r'PRODUCT_NAME:\s*[\'"]([^\'"]+)', r'id:\s*[\'"]([^\'"]+)'):
    m = re.findall(pat, cat)
    print(f"  catalog {pat[:34]:36s} {len(m):4d} distinct={len(set(m))}")
snap = open(os.path.join(REPO, "italia-portale", "client",
                         "meeting-intelligence-snapshot.json"), encoding="utf-8").read()
cp = sorted(set(re.findall(r'"(CATPRD_[A-Z0-9_]+)"', snap)))
print(f"  distinct CATPRD_ ids in the portal snapshot: {len(cp)}")
ch = sorted(set(re.findall(r'"(CATPRD_[A-Z0-9_]+)"', s)))
print(f"  distinct CATPRD_ ids in the handoff        : {len(ch)}")
print(f"  the audit adjudicated 10 product names; the Olive x OFF pair used 3 of them.")
print(f"  '3 product(s) were checked' therefore has an unprinted denominator of at least "
      f"{len(set(cp)|set(ch))} catalogue products.")
