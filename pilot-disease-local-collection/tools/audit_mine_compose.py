import json, os, collections

ROOT = r"C:\disease-local-collection-italy\pilot-disease-local-collection"
mine = json.load(open(os.path.join(ROOT, "tools", "_mine_hashes.json")))
byh = collections.defaultdict(list)
for r in mine:
    byh[r["sha256"]].append(r["path"])
dups = {h: sorted(v) for h, v in byh.items() if len(v) > 1}

print("dup groups:", len(dups), " files:", sum(len(v) for v in dups.values()),
      " redundant:", sum(len(v) - 1 for v in dups.values()))
print()
print("=== decomposition of the 29 redundant copies ===")
cross, within = 0, 0
for h, v in dups.items():
    fronts = set(p.split("/")[1] for p in v)
    if len(fronts) > 1:
        cross += len(v) - 1
    else:
        within += len(v) - 1
print("redundant copies spanning >1 front (true cross-front) :", cross)
print("redundant copies inside a SINGLE front               :", within)

print()
print("=== the group the finding described (vine bulletin + 2 dispensers) ===")
named = ["6d12bcb5", "806c34243f0f", "94073958760a"]
tot = 0
for h, v in dups.items():
    if any(h.startswith(n) for n in named):
        tot += len(v) - 1
        print("  %s x %d -> %d redundant" % (h[:12], len(v), len(v) - 1))
print("  redundant copies accounted for by the finding's narrative:", tot, "of 29")

print()
print("=== raw/F3b/bfogl_by_year/ (largest undescribed block) ===")
bf = [r for r in mine if r["path"].startswith("raw/F3b/bfogl_by_year/")]
print("files:", len(bf), " distinct sha256:", len(set(r["sha256"] for r in bf)),
      " redundant:", len(bf) - len(set(r["sha256"] for r in bf)))
g = collections.defaultdict(list)
for r in bf:
    g[r["sha256"]].append(os.path.basename(r["path"]).replace("meteo_storici_20004_", "").replace(".json", ""))
for h, yrs in sorted(g.items(), key=lambda kv: sorted(kv[1])[0]):
    print("   %s -> years %s" % (h[:12], ",".join(sorted(yrs))))
