import json, collections, calendar

ROOT = r"C:/disease-local-collection-italy/pilot-disease-local-collection"
M = [json.loads(l) for l in open(ROOT + "/manifests/arpav-daily-manifest.jsonl", encoding="utf-8")]
pf = {(f["codseq"], f["year"]): f for f in json.load(open(r"C:/disease-local-collection-italy/audit-scratch/l3_perfile.json", encoding="utf-8"))}

print("=== manifest expected_days vs true calendar days ===")
bad = []
for m in M:
    cal = 366 if calendar.isleap(m["anno"]) else 365
    if m["expected_days"] != cal:
        bad.append((m["codseq"], m["anno"], m["expected_days"], cal))
print("rows where expected_days != calendar days:", len(bad))
for b in bad[:10]:
    print("  ", b)

print()
print("=== does any FULL label sit on a file that is actually short? ===")
wrong = []
for m in M:
    f = pf[(m["codseq"], m["anno"])]
    cal = f["calendar_days"]
    full = (f["distinct_dates"] == cal)
    if m["completeness"] == "FULL" and not full:
        wrong.append((m["codseq"], m["anno"], f["distinct_dates"], cal))
    if m["completeness"] != "FULL" and full:
        wrong.append(("PARTIAL-but-full", m["codseq"], m["anno"], f["distinct_dates"], cal))
print("mislabelled rows:", len(wrong))
for w in wrong[:10]:
    print("  ", w)

print()
print("=== ARPAV sensor catalogue: what years does it advertise for BFOGL? ===")
cat = json.load(open(ROOT + "/raw/F4-arpav-rest/meteo_sensori_dispenser.json", encoding="utf-8"))
print("catalogue top type:", type(cat).__name__)
if isinstance(cat, dict):
    print("keys:", list(cat.keys()))
    rows = cat.get("data") or []
else:
    rows = cat
print("catalogue rows:", len(rows))
print("sample row:", json.dumps(rows[0], ensure_ascii=False)[:800])
keys = set()
for r in rows[:50]:
    keys |= set(r.keys())
print("row keys seen:", sorted(keys))
