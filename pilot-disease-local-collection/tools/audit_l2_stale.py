import json, os, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def P(*a): return os.path.join(ROOT, *a)
def rd(p): return [json.loads(l) for l in open(P(p), encoding='utf-8') if l.strip()]

RI = rd('manifests/raw-file-inventory.jsonl')
inv = {r['raw_path'].replace('\\', '/') for r in RI}

allf = set()
for root, dirs, fs in os.walk(P('raw')):
    for f in fs:
        allf.add(os.path.relpath(os.path.join(root, f), ROOT).replace('\\', '/'))

missing = allf - inv
extra = inv - allf
print("files on disk under raw/:", len(allf))
print("rows in raw-file-inventory.jsonl:", len(RI))
print("on disk but NOT in the inventory:", len(missing))
print("  by top dir:", dict(collections.Counter(p.split('/')[1] for p in missing)))
print("in the inventory but NOT on disk:", len(extra), sorted(extra)[:10])

# dedup field
print()
print("dedup values:", dict(collections.Counter(r.get('dedup') for r in RI)))
print("distinct sha256 in inventory:", len({r['sha256'] for r in RI}))
