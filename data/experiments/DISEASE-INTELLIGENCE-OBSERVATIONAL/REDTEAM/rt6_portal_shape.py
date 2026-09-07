#!/usr/bin/env python3
"""RT6-D. Count the commercial shape of the EXISTING portal snapshot, so the target this
tool must not become is a number, not an adjective."""
import os, json, collections, re
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
P = os.path.join(REPO, "italia-portale", "client", "meeting-intelligence-snapshot.json")
raw = open(P, encoding="utf-8").read()
d = json.loads(raw)
print("top-level keys:", list(d)[:40])

# find the case list
def walk(o, path="$"):
    if isinstance(o, dict):
        yield path, o
        for k, v in o.items():
            yield from walk(v, f"{path}.{k}")
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from walk(v, f"{path}[]")

objs = [(p, o) for p, o in walk(d) if isinstance(o, dict)]
print("total dict objects in snapshot:", len(objs))

def count_field(field):
    c = collections.Counter()
    holders = 0
    for p, o in objs:
        if field in o:
            holders += 1
            v = o[field]
            if isinstance(v, (str, int, float, bool)) or v is None:
                c[str(v)] += 1
            else:
                c["<complex>"] += 1
    return holders, c

for f in ("OPP_ID", "opp_id", "id", "ARCHETYPE", "archetype", "STATUS", "status",
          "COMMERCIAL_PRIORITY", "commercial_priority", "PRIORITY"):
    h, c = count_field(f)
    if h:
        print(f"\nfield {f!r}: on {h} objects")
        for k, n in c.most_common(12):
            print(f"    {k[:60]:60s} {n}")

print("\n--- raw token counts over the whole file ---")
for tok in ("OPP_", "O1_FIELD_PRESSURE", "ACT_NOW", "SALES_READY", "COMMERCIAL_PRIORITY",
            "COMMERCIAL_OPPORTUNITY", "CONTACT_NOW", "MONITOR", "INVESTIGATE",
            "ADAMA_RELEVANCE", "archetype", "ARCHETYPE"):
    print(f"  {tok:26s} {raw.count(tok)}")

# distinct OPP ids
opps = sorted(set(re.findall(r'"(OPP_[A-Z0-9_\-]+)"', raw)))
print(f"\ndistinct OPP_ ids: {len(opps)}  e.g. {opps[:8]}")
archs = collections.Counter(re.findall(r'"(O\d+_[A-Z_]+)"', raw))
print(f"archetype tokens: {dict(archs.most_common(12))}")
