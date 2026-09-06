import json, os, hashlib, random
from collections import defaultdict

root = r"C:\disease-local-collection-italy\pilot-disease-local-collection"
inv = os.path.join(root, "manifests", "raw-file-inventory.jsonl")

rows = []
with open(inv, encoding="utf-8") as f:
    for ln in f:
        ln = ln.strip()
        if ln:
            rows.append(json.loads(ln))

by_dir = defaultdict(list)
for r in rows:
    by_dir[r["raw_path"].replace("\\", "/").split("/")[1]].append(r)

# the four categories the other auditor said were absent from the inventory
targets = ["F8-arpav-agrometeo-docs", "_failed-captures",
           "F7-arpav-bollettino-mese", "F4-arpav-rest"]

random.seed(7)
ok = bad = missing = 0
print("category                       rows  sampled  hash_ok  hash_MISMATCH  bytes_MISMATCH")
for t in targets:
    grp = by_dir.get(t, [])
    smp = random.sample(grp, min(12, len(grp)))
    g_ok = g_bad = g_byte = 0
    for r in smp:
        p = os.path.join(root, r["raw_path"].replace("/", os.sep))
        if not os.path.exists(p):
            missing += 1
            continue
        h = hashlib.sha256()
        with open(p, "rb") as fh:
            for chunk in iter(lambda: fh.read(1 << 20), b""):
                h.update(chunk)
        real = h.hexdigest()
        if real == r["sha256"]:
            g_ok += 1; ok += 1
        else:
            g_bad += 1; bad += 1
            print("   MISMATCH", r["raw_path"], "inv=", r["sha256"][:16], "real=", real[:16])
        if os.path.getsize(p) != r["bytes"]:
            g_byte += 1
            print("   BYTES OFF", r["raw_path"], "inv=", r["bytes"], "real=", os.path.getsize(p))
    print("%-30s %5d %8d %8d %14d %15d" % (t, len(grp), len(smp), g_ok, g_bad, g_byte))

print()
print("TOTAL re-hashed ok:", ok, " mismatched:", bad, " missing on disk:", missing)

# does the inventory carry any self-declared timestamp / as-of field?
keys = set()
for r in rows:
    keys.update(r.keys())
print()
print("fields present in inventory rows:", sorted(keys))
timeish = [k for k in keys if any(w in k.lower() for w in ("time", "date", "as_of", "asof", "stamp", "when", "run"))]
print("timestamp-ish fields:", timeish if timeish else "NONE -- inventory has no as-of stamp")
