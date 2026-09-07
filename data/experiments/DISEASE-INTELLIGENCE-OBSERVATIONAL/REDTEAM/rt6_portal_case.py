#!/usr/bin/env python3
"""RT6-E. Print the field skeleton of one O1_FIELD_PRESSURE case and locate any
olive / Bactrocera case. This is the socket this tool's output would be plugged into."""
import os, json, collections
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
d = json.load(open(os.path.join(REPO, "italia-portale", "client",
                                "meeting-intelligence-snapshot.json"), encoding="utf-8"))
cases = d["CASES"]
print("TOTAL_CASES:", d["TOTAL_CASES"], " len(CASES):", len(cases))
print("BY_STATUS:", d["BY_STATUS"])
print("BY_COMMERCIAL_PRIORITY:", d["BY_COMMERCIAL_PRIORITY"])
fp = [c for c in cases if c.get("ARCHETYPE") == "O1_FIELD_PRESSURE"]
print(f"\nO1_FIELD_PRESSURE cases: {len(fp)} of {len(cases)}")
print("  their STATUS:", collections.Counter(c["STATUS"] for c in fp))
print("  their COMMERCIAL_PRIORITY:", collections.Counter(c["COMMERCIAL_PRIORITY"] for c in fp))
c = fp[0]
print("\nFIELD SKELETON of", c.get("OPP_ID"))
for k, v in c.items():
    s = json.dumps(v, ensure_ascii=False)
    print(f"  {k:34s} {s[:150]}")

oli = [x for x in cases if "oliv" in json.dumps(x, ensure_ascii=False).lower()
       or "bactrocera" in json.dumps(x, ensure_ascii=False).lower()]
print(f"\ncases mentioning olive/Bactrocera anywhere: {len(oli)} of {len(cases)}")
for x in oli[:6]:
    print(f"  {x.get('OPP_ID')} {x.get('ARCHETYPE')} {x.get('STATUS')} "
          f"{x.get('COMMERCIAL_PRIORITY')} | {str(x.get('TITLE') or x.get('HEADLINE'))[:70]}")
