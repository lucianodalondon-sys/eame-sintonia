import json, os, collections

ROOT = r"C:\disease-local-collection-italy\pilot-disease-local-collection"
mine = json.load(open(os.path.join(ROOT, "tools", "_mine_hashes.json")))
by_path = {r["path"]: r["sha256"] for r in mine}

byh = collections.defaultdict(list)
for r in mine:
    byh[r["sha256"]].append(r["path"])
dupgroups = {h: v for h, v in byh.items() if len(v) > 1}
dupfiles = set(p for v in dupgroups.values() for p in v)

def sel(pred):
    return [p for p in by_path if pred(p)]

daily = sel(lambda p: p.startswith("raw/F4-arpav-rest/tabella/"))
f8 = sel(lambda p: p.startswith("raw/F8-arpav-agrometeo-docs/"))
f7 = sel(lambda p: p.startswith("raw/F7-arpav-bollettino-mese/"))
quar = sel(lambda p: p.startswith("raw/_failed-captures/"))
recon = sel(lambda p: p.startswith(("raw/F1", "raw/F2", "raw/F3", "raw/F4/", "raw/F5", "raw/F6")))

for name, s in [("F4-arpav-rest/tabella (daily)", daily), ("F8 docs", f8),
                ("F7 monthly", f7), ("_failed-captures", quar), ("recon fronts F1/F2/F3/F4//F5/F6", recon)]:
    n = len(s)
    d = len(set(by_path[p] for p in s))
    print("%-34s files=%-6d distinct_sha=%-6d internal_redundant=%d  in_a_global_dupgroup=%d"
          % (name, n, d, n - d, len(set(s) & dupfiles)))

print()
print("=== cross-set byte-identity ===")
sets = {"daily": daily, "F8": f8, "F7": f7, "quarantine": quar, "recon": recon}
h = {k: set(by_path[p] for p in v) for k, v in sets.items()}
keys = list(sets)
for i in range(len(keys)):
    for j in range(i + 1, len(keys)):
        a, b = keys[i], keys[j]
        common = h[a] & h[b]
        print("  %-10s n %-10s -> %d shared sha256" % (a, b, len(common)))
        for c in sorted(common)[:6]:
            print("        ", c[:12],
                  [p for p in sets[a] if by_path[p] == c][:2],
                  [p for p in sets[b] if by_path[p] == c][:2])

print()
print("=== .py scripts + quarantine exclusion (their corrected total) ===")
keep = [r for r in mine if not r["path"].startswith("raw/_failed-captures/")
        and not r["path"].endswith(".py")]
print("files excluding quarantine and .py :", len(keep))
print("distinct sha256 of those           :", len(set(r["sha256"] for r in keep)))
print("redundant among those              :", len(keep) - len(set(r["sha256"] for r in keep)))
print("quarantine file count              :", len(quar))
print(".py file count under raw/          :", len([r for r in mine if r["path"].endswith(".py")]))
