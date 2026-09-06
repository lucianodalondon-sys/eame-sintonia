import json, re, collections

ROOT = r"C:/disease-local-collection-italy/pilot-disease-local-collection"
pf = json.load(open(r"C:/disease-local-collection-italy/audit-scratch/l3_perfile.json", encoding="utf-8"))
cat = json.load(open(ROOT + "/raw/F4-arpav-rest/meteo_sensori_dispenser.json", encoding="utf-8"))["data"]
byseq = {r["codseq"]: r for r in cat}

have = collections.defaultdict(set)
tipo, name = {}, {}
for f in pf:
    have[f["codseq"]].add(f["year"])
    tipo[f["codseq"]] = f["tipo"][0] if f["tipo"] else "?"
    name[f["codseq"]] = f["station"][0] if f["station"] else "?"

print("=== catalogue-advertised years vs preserved years, ALL 1038-file sensors ===")
tot_missing = 0
missing_rows = []
for seq in sorted(have, key=lambda s: (tipo[s], name[s])):
    r = byseq.get(seq)
    if r is None:
        print("SENSOR NOT IN CATALOGUE:", seq, name[seq], tipo[seq]); continue
    yrs = set(int(y) for y in re.findall(r"\b(19|20)\d{2}\b|\b(\d{4})\b", r["descrizione_annate"]) for y in [] ) # placeholder
    yrs = set(int(y) for y in re.findall(r"\d{4}", r["descrizione_annate"]))
    miss = sorted(yrs - have[seq])
    if miss:
        tot_missing += len(miss)
        missing_rows.append((name[seq], tipo[seq], seq, miss, sorted(yrs)[:3], sorted(yrs)[-1]))
print("sensors in our set:", len(have))
print("sensors with catalogue years NOT preserved:", len(missing_rows), " total missing (sensor,year) slots:", tot_missing)
for m in missing_rows[:40]:
    print("  {:<28} {:<8} seq={} missing_years={}".format(m[0], m[1], m[2], m[3]))

print()
print("=== BFOGL sensors: catalogue string vs preserved ===")
for seq in sorted(have):
    if tipo[seq] != "BFOGL":
        continue
    r = byseq.get(seq)
    yrs = sorted(set(int(y) for y in re.findall(r"\d{4}", r["descrizione_annate"])))
    print("{:<30} seq={} catalogue={}..{} ({} yrs)  preserved={}..{} ({} yrs)  extra_in_cat={}".format(
        name[seq], seq, min(yrs), max(yrs), len(yrs), min(have[seq]), max(have[seq]), len(have[seq]),
        sorted(set(yrs) - have[seq])))
print()
print("Breda raw catalogue string:")
for seq in sorted(have):
    if tipo[seq] == "BFOGL" and "Breda" in name[seq]:
        print("  ", byseq[seq]["descrizione_annate"])
