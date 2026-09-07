#!/usr/bin/env python3
"""RT6-C4. Resolve the handoff's string table and read IT-LBL-1932 in full.
This is the single object that decides whether 'product_label_matches_for_olive = 0'
is a fact or a guess."""
import os, re, json
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
raw = open(os.path.join(REPO, "italia-portale", "client", "italy-handoff-v21.js"),
           encoding="utf-8", errors="replace").read()

i = raw.find("var P = [")
j = raw.find("];", i)
tbl = json.loads(raw[i + len("var P = "): j + 1])
print(f"string table P: {len(tbl):,} entries")

def deref(x):
    if isinstance(x, str) and len(x) > 1 and x[0] == "\u0000":
        try:
            return tbl[int(x[1:])]
        except Exception:
            return x
    if isinstance(x, list):
        return [deref(y) for y in x]
    return x

k = raw.find('"ID":"IT-LBL-1932"')
d, s2 = 0, k
while s2 > 0:
    if raw[s2] == '}': d += 1
    elif raw[s2] == '{':
        if d == 0: break
        d -= 1
    s2 -= 1
d, e2 = 0, k
while e2 < len(raw):
    if raw[e2] == '{': d += 1
    elif raw[e2] == '}':
        if d == 0: break
        d -= 1
    e2 += 1
obj = json.loads(raw[s2:e2 + 1])
print("\nIT-LBL-1932, fully resolved:")
for kk in sorted(obj):
    print(f"  {kk:28s} {json.dumps(deref(obj[kk]), ensure_ascii=False)[:220]}")

print("\n=== every object in the file with CROP_ON_LABEL, resolved ===")
n = 0
for m in re.finditer(r'"CROP_ON_LABEL"', raw):
    d, a = 0, m.start()
    while a > 0:
        if raw[a] == '}': d += 1
        elif raw[a] == '{':
            if d == 0: break
            d -= 1
        a -= 1
    d, b = 0, m.start()
    while b < len(raw):
        if raw[b] == '{': d += 1
        elif raw[b] == '}':
            if d == 0: break
            d -= 1
        b += 1
    try:
        o = json.loads(raw[a:b + 1])
    except Exception:
        continue
    n += 1
    col = deref(o.get("CROP_ON_LABEL"))
    if str(col).upper() in ("OLIVO", "OLIVE"):
        print(f"  #{n} ID={o.get('ID')} CROP_ON_LABEL={col} "
              f"PRODUCT={deref(o.get('PRODUCT_NAME') or o.get('PRODUCT') or o.get('PRODUCT_ID'))} "
              f"ISSUE={deref(o.get('ISSUE_IDS'))} "
              f"ISSUE_ON_LABEL={deref(o.get('ISSUE_ON_LABEL'))} "
              f"LINK={o.get('LINK_STRENGTH')}")
print(f"  objects carrying CROP_ON_LABEL at all: {n}")
