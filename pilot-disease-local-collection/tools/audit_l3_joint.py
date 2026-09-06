import json, collections, datetime as dt, re

ROOT = r"C:/disease-local-collection-italy/pilot-disease-local-collection"
pf = json.load(open(r"C:/disease-local-collection-italy/audit-scratch/l3_perfile.json", encoding="utf-8"))
cat = json.load(open(ROOT + "/raw/F4-arpav-rest/meteo_sensori_dispenser.json", encoding="utf-8"))["data"]
byseq = {r["codseq"]: r for r in cat}

A, B = dt.date(2014, 3, 1), dt.date(2025, 10, 31)
WINS = set((A + dt.timedelta(i)).isoformat() for i in range((B - A).days + 1))

# station -> sensor -> set(dates)
S = collections.defaultdict(lambda: collections.defaultdict(set))
name = {}
seqs = collections.defaultdict(dict)
for f in pf:
    k = f["station_code"][0]
    name[k] = f["station"][0]
    S[k][f["tipo"][0]] |= set(f["dates"])
    seqs[k][f["tipo"][0]] = f["codseq"]

print("=== catalogue string for Oderzo temperature / humidity (did the sensor stop?) ===")
for tp in ("TARIA2M", "UMID2M", "BFOGL", "PREC"):
    seq = seqs[196].get(tp)
    if seq:
        print("  {:<8} seq={} -> {}".format(tp, seq, byseq[seq]["descrizione_annate"]))

print()
print("=== which sensors each leaf-wetness station actually has ===")
for k in sorted(S, key=lambda x: name[x]):
    print("  {:<30} {}".format(name[k], sorted(S[k].keys())))

print()
print("=== JOINT coverage inside the claimed window 2014-03-01..2025-10-31 ===")
print("(a disease model needs leaf wetness AND temperature AND humidity AND rain on the SAME day)")
print("{:<30} {:>7} {:>7} {:>7} {:>7} {:>9} {:>8}".format(
    "station", "BFOGL", "TARIA", "UMID", "PREC", "ALL4", "ALL4_pct"))
res = []
for k in sorted(S, key=lambda x: name[x]):
    b = S[k].get("BFOGL", set()) & WINS
    t = S[k].get("TARIA2M", set()) & WINS
    u = S[k].get("UMID2M", set()) & WINS
    p = S[k].get("PREC", set()) & WINS
    allf = b & t & u & p
    pct = 100.0 * len(allf) / len(WINS)
    res.append((name[k], len(b), len(t), len(u), len(p), len(allf), pct))
    print("{:<30} {:>7} {:>7} {:>7} {:>7} {:>9} {:>7.2f}%".format(name[k], len(b), len(t), len(u), len(p), len(allf), pct))
print()
print("window days:", len(WINS))
print("stations with BFOGL >= 99.4 pct :", sum(1 for r in res if 100.0 * r[1] / len(WINS) >= 99.4), "of", len(res))
print("stations with ALL4 >= 99.4 pct  :", sum(1 for r in res if r[6] >= 99.4), "of", len(res))
print("stations with ALL4 >= 95   pct  :", sum(1 for r in res if r[6] >= 95.0), "of", len(res))
