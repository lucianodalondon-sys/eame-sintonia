import gzip, hashlib, os, json, collections

ROOT = r"C:\disease-local-collection-italy\pilot-disease-local-collection"
D = os.path.join(ROOT, "raw", "F4-arpav-rest", "tabella")

files = sorted(os.listdir(D))
outer, inner = {}, {}
for fn in files:
    p = os.path.join(D, fn)
    raw = open(p, 'rb').read()
    outer[fn] = hashlib.sha256(raw).hexdigest()
    try:
        dec = gzip.decompress(raw)
    except Exception as e:
        print("GZ FAIL", fn, e)
        continue
    inner[fn] = hashlib.sha256(dec).hexdigest()

print("daily .json.gz files      :", len(files))
print("distinct OUTER sha256     :", len(set(outer.values())))
print("distinct INNER sha256     :", len(set(inner.values())))
print("files that failed to gunzip:", len(files) - len(inner))
print()
byi = collections.defaultdict(list)
for fn, h in inner.items():
    byi[h].append(fn)
dups = {h: v for h, v in byi.items() if len(v) > 1}
print("INNER payloads appearing in >1 file:", len(dups))
print("files involved                     :", sum(len(v) for v in dups.values()))
print("redundant inner copies             :", sum(len(v) - 1 for v in dups.values()))
print()
for h, v in sorted(dups.items(), key=lambda kv: -len(kv[1]))[:25]:
    print("  %s x %d" % (h[:12], len(v)))
    for fn in sorted(v)[:8]:
        print("        ", fn, os.path.getsize(os.path.join(D, fn)), "bytes")

json.dump({"outer": outer, "inner": inner},
          open(os.path.join(ROOT, "tools", "_mine_gz.json"), "w"))
