import os, re, json, hashlib, collections

ROOT = r"C:\disease-local-collection-italy\pilot-disease-local-collection"
mine = json.load(open(os.path.join(ROOT, "tools", "_mine_hashes.json")))

pdfs = []
for r in mine:
    p = os.path.join(ROOT, r["path"].replace("/", os.sep))
    try:
        head = open(p, 'rb').read(5)
    except Exception:
        continue
    if head == b"%PDF-":
        pdfs.append(r)
print("files whose magic bytes are %PDF- :", len(pdfs))
print("  by front:")
for k, v in collections.Counter(r["path"].split("/")[1] for r in pdfs).most_common():
    print("      %-30s %d" % (k, v))

RX = [re.compile(rb"/ID\s*\[[^\]]*\]"), re.compile(rb"/ModDate\s*\([^)]*\)"),
      re.compile(rb"/CreationDate\s*\([^)]*\)"), re.compile(rb"/Producer\s*\([^)]*\)")]

norm = {}
for r in pdfs:
    p = os.path.join(ROOT, r["path"].replace("/", os.sep))
    b = open(p, 'rb').read()
    for rx in RX:
        b = rx.sub(b"", b)
    norm[r["path"]] = hashlib.sha256(b).hexdigest()

print()
print("distinct RAW sha among PDFs        :", len(set(r["sha256"] for r in pdfs)))
print("distinct NORMALIZED sha among PDFs :", len(set(norm.values())))

byn = collections.defaultdict(list)
for p, h in norm.items():
    byn[h].append(p)
raw_by = collections.defaultdict(list)
for r in pdfs:
    raw_by[r["sha256"]].append(r["path"])

extra = 0
print()
print("=== groups identical AFTER normalization but NOT byte-identical ===")
for h, v in byn.items():
    if len(v) > 1:
        rawset = set(next(r["sha256"] for r in pdfs if r["path"] == p) for p in v)
        if len(rawset) > 1:
            extra += 1
            print("  normalized-dup group, %d files, %d distinct raw sha:" % (len(v), len(rawset)))
            for p in sorted(v):
                print("       ", p)
if extra == 0:
    print("  (none) -> normalization exposed NO additional duplicate PDFs")

print()
print("=== same byte-length but different sha256 (near-dup candidates) ===")
bysz = collections.defaultdict(list)
for r in pdfs:
    bysz[r["bytes"]].append(r)
n = 0
for sz, v in sorted(bysz.items()):
    if len(v) > 1 and len(set(x["sha256"] for x in v)) > 1:
        n += 1
        print("  size %d bytes, %d files, %d distinct sha:" % (sz, len(v), len(set(x["sha256"] for x in v))))
        for x in sorted(v, key=lambda z: z["path"]):
            print("       ", x["sha256"][:12], x["path"])
if n == 0:
    print("  (none)")
