import json, os, datetime
from collections import Counter

root = r"C:\disease-local-collection-italy\pilot-disease-local-collection"
inv = os.path.join(root, "manifests", "raw-file-inventory.jsonl")

rows = []
with open(inv, encoding="utf-8") as f:
    for ln in f:
        ln = ln.strip()
        if ln:
            rows.append(json.loads(ln))

inv_paths = set(r["raw_path"].replace("\\", "/") for r in rows)
print("rows in raw-file-inventory.jsonl:", len(rows))
print("distinct raw_path in inventory  :", len(inv_paths))

disk = set()
for dp, dn, fn in os.walk(os.path.join(root, "raw")):
    for n in fn:
        p = os.path.join(dp, n)
        rel = os.path.relpath(p, root).replace("\\", "/")
        disk.add(rel)
print("files on disk under raw/        :", len(disk))

only_disk = sorted(disk - inv_paths)
only_inv = sorted(inv_paths - disk)
print("on disk but NOT in inventory    :", len(only_disk))
print("   by top dir:", dict(Counter(p.split('/')[1] for p in only_disk)))
for p in only_disk[:20]:
    print("   +", p)
print("in inventory but NOT on disk     :", len(only_inv))
for p in only_inv[:20]:
    print("   -", p)

print()
print("--- mtimes (UTC) ---")
for rel in ["manifests/raw-file-inventory.jsonl", "manifests/collection-manifest.json",
            "manifests/arpav-docs-manifest.jsonl", "manifests/arpav-geo-manifest.jsonl",
            "manifests/arpav-monthly-manifest.jsonl", "manifests/daily-series-recount.json"]:
    p = os.path.join(root, rel)
    if os.path.exists(p):
        print("%-52s %sZ" % (rel, datetime.datetime.utcfromtimestamp(os.path.getmtime(p)).isoformat()))
