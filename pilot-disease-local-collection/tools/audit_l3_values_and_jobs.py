import json, gzip, glob, os, collections

ROOT = r"C:/disease-local-collection-italy/pilot-disease-local-collection"
pf = json.load(open(r"C:/disease-local-collection-italy/audit-scratch/l3_perfile.json", encoding="utf-8"))
J = json.load(open(ROOT + "/manifests/arpav-jobs.json", encoding="utf-8"))

print("=== jobs vs preserved files ===")
jobkeys = set((j["codseq"], j["anno"]) for j in J)
filekeys = set((f["codseq"], f["year"]) for f in pf)
print("jobs rows:", len(J), " distinct job keys:", len(jobkeys))
print("raw file keys:", len(filekeys))
print("planned but NOT preserved:", sorted(jobkeys - filekeys)[:10], "count", len(jobkeys - filekeys))
print("preserved but NOT planned:", sorted(filekeys - jobkeys)[:10], "count", len(filekeys - jobkeys))
print("planned BFOGL jobs (by sensore name):", sum(1 for j in J if j["sensore"] == "Bagnatura fogliare"))
print("distinct sensore names in jobs:", collections.Counter(j["sensore"] for j in J))

print()
print("=== sha256 duplicates among preserved daily files ===")
inv = [json.loads(l) for l in open(ROOT + "/manifests/raw-file-inventory.jsonl", encoding="utf-8")]
print("inventory rows:", len(inv))
k0 = list(inv[0].keys()); print("inventory keys:", k0)

import hashlib
sh = {}
for p in sorted(glob.glob(ROOT + "/raw/F4-arpav-rest/tabella/*.json.gz")):
    h = hashlib.sha256(open(p, "rb").read()).hexdigest()
    sh.setdefault(h, []).append(os.path.basename(p))
print("daily files hashed:", sum(len(v) for v in sh.values()), " distinct sha256:", len(sh))
dups = {h: v for h, v in sh.items() if len(v) > 1}
print("duplicate-hash groups:", len(dups))
for h, v in list(dups.items())[:5]:
    print("  ", h[:16], v)

print()
print("=== BFOGL value sanity (a value present is not necessarily an observation) ===")
vals = collections.Counter()
nonnum = collections.Counter()
lo = hi = None
neg = 0; over100 = 0; zero = 0
n = 0
for f in pf:
    if f["tipo"] != ["BFOGL"]:
        continue
    p = ROOT + "/raw/F4-arpav-rest/tabella/" + f["file"]
    doc = json.loads(gzip.open(p, "rb").read().decode("utf-8"))
    for r in doc["data"]:
        v = r["valore"]; n += 1
        try:
            x = float(v)
        except Exception:
            nonnum[repr(v)] += 1
            continue
        if lo is None or x < lo: lo = x
        if hi is None or x > hi: hi = x
        if x < 0: neg += 1
        if x > 100: over100 += 1
        if x == 0: zero += 1
        vals[x] += 1
print("BFOGL rows scanned:", n)
print("non-numeric valore:", dict(nonnum))
print("min:", lo, " max:", hi)
print("negative values:", neg, " >100:", over100, " exactly 0:", zero)
print("10 most common values:", vals.most_common(10))
