import hashlib, os, json, collections

ROOT = r"C:\disease-local-collection-italy\pilot-disease-local-collection"
RAW = os.path.join(ROOT, "raw")

rows = []
for dirpath, dirnames, filenames in os.walk(RAW):
    for fn in filenames:
        p = os.path.join(dirpath, fn)
        try:
            h = hashlib.sha256(open(p, 'rb').read()).hexdigest()
        except Exception as e:
            print("ERR", p, e)
            continue
        rel = os.path.relpath(p, ROOT).replace("\\", "/")
        rows.append((rel, h, os.path.getsize(p)))

print("TOTAL files under raw/ :", len(rows))
print("TOTAL distinct sha256  :", len(set(h for _, h, _ in rows)))
print("redundant byte-copies  :", len(rows) - len(set(h for _, h, _ in rows)))

json.dump([{"path": r, "sha256": h, "bytes": b} for r, h, b in rows],
          open(os.path.join(ROOT, "tools", "_mine_hashes.json"), "w"), indent=0)

byh = collections.defaultdict(list)
for r, h, b in rows:
    byh[h].append(r)
dups = {h: v for h, v in byh.items() if len(v) > 1}
print()
print("sha256 present in >1 raw file:", len(dups))
print("total files involved         :", sum(len(v) for v in dups.values()))
print("redundant copies             :", sum(len(v) - 1 for v in dups.values()))
print()
for h, v in sorted(dups.items(), key=lambda kv: -len(kv[1])):
    print("  %s x %d" % (h[:12], len(v)))
    for p in sorted(v):
        print("       ", p)
