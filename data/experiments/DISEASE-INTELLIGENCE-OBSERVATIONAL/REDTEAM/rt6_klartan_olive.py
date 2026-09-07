#!/usr/bin/env python3
"""RT6-C3. Direct test of the NO. Do KLARTAN / MAVRIK objects in the handoff carry
CROP_OLIVE, and what does IT-LBL-1932 actually say?"""
import os, re, json, collections
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
s = open(os.path.join(REPO, "italia-portale", "client", "italy-handoff-v21.js"),
         encoding="utf-8", errors="replace").read()

# the file is a JS assignment; try to find and parse the JSON payload
m = re.search(r'=\s*(\{.*\})\s*;?\s*$', s, re.S)
payload = None
try:
    payload = json.loads(m.group(1)) if m else None
except Exception as e:
    print("direct json.loads failed:", str(e)[:120])
if payload is None:
    # try the whole file minus a leading assignment
    i = s.find("{")
    for end in (s.rfind("}"),):
        try:
            payload = json.loads(s[i:end+1])
            break
        except Exception as e:
            print("second attempt failed:", str(e)[:120])
print("payload parsed:", type(payload).__name__ if payload is not None else None)
if isinstance(payload, dict):
    print("keys:", list(payload)[:30])
    # find the string table
    for k, v in payload.items():
        if isinstance(v, list) and v and all(isinstance(x, str) for x in v[:20]):
            print(f"  candidate string table {k!r}: {len(v)} strings, e.g. {v[:5]}")

def deref(x, tbl):
    if isinstance(x, str) and x.startswith("\u0000"):
        try:
            return tbl[int(x[1:])]
        except Exception:
            return x
    return x

# balanced object extractor
def enclosing(idx):
    depth, j = 0, idx
    while j > 0:
        if s[j] == '}': depth += 1
        elif s[j] == '{':
            if depth == 0: break
            depth -= 1
        j -= 1
    depth, k = 0, idx
    while k < len(s):
        if s[k] == '{': depth += 1
        elif s[k] == '}':
            if depth == 0: break
            depth -= 1
        k += 1
    return s[j:k+1]

print("\n=== objects whose text contains KLARTAN or MAVRIK AND an olive token ===")
hits = 0
for m2 in re.finditer(r'KLARTAN|MAVRIK', s, re.I):
    o = enclosing(m2.start())
    if re.search(r'CROP_OLIVE|"OLIVE"|"OLIVO"|OLIVE_FLY', o):
        hits += 1
        if hits <= 3:
            print("  ", o[:500].replace("\n", " "))
print(f"  total KLARTAN/MAVRIK objects also carrying an olive token: {hits}")

print("\n=== IT-LBL-1932, the olive label-row object the engine cannot see ===")
i = s.find('"IT-LBL-1932"')
o = enclosing(i)
print("  ", o[:900])
try:
    d = json.loads(o)
    print("\n  parsed keys:", sorted(d))
except Exception as e:
    print("  (not standalone-parseable:", str(e)[:80], ")")

print("\n=== how many IT-LBL-* objects carry CROP_OLIVE ? ===")
lbl_olive = set()
for m3 in re.finditer(r'"(IT-LBL-\d+)"', s):
    o = enclosing(m3.start())
    if "CROP_OLIVE" in o or '"OLIVO"' in o:
        lbl_olive.add(m3.group(1))
alll = set(re.findall(r'"(IT-LBL-\d+)"', s))
print(f"  distinct IT-LBL ids in the file        : {len(alll)}")
print(f"  IT-LBL ids in an object with olive     : {len(lbl_olive)} -> {sorted(lbl_olive)[:12]}")
print(f"  the engine reports product_label_matches_for_olive = 0 (hardcoded literal)")
