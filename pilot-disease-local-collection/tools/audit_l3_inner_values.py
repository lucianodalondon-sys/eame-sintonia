import json, gzip, collections, os

ROOT = r"C:/disease-local-collection-italy/pilot-disease-local-collection"
TAB = ROOT + "/raw/F4-arpav-rest/tabella/"
pf = json.load(open(r"C:/disease-local-collection-italy/audit-scratch/l3_perfile.json", encoding="utf-8"))

print("=== sample raw 'valore' per sensor type ===")
seen = {}
for f in pf:
    t = f["tipo"][0]
    if t in seen:
        continue
    doc = json.loads(gzip.open(TAB + f["file"], "rb").read().decode("utf-8"))
    seen[t] = doc["data"][0]
    print("  {:<8} unit={!r:<8} valore={!r}".format(t, doc["data"][0].get("unitnm"), doc["data"][0].get("valore")))

print()
print("=== do composite values hide nulls inside? scanning ALL 1038 files ===")
inner_null = collections.Counter()
inner_rows = collections.Counter()
scalar_bad = collections.Counter()
subkeys = collections.defaultdict(collections.Counter)
for f in pf:
    t = f["tipo"][0]
    doc = json.loads(gzip.open(TAB + f["file"], "rb").read().decode("utf-8"))
    for r in doc["data"]:
        v = r["valore"]
        inner_rows[t] += 1
        s = v.strip() if isinstance(v, str) else v
        if isinstance(s, str) and s.startswith("{"):
            try:
                o = json.loads(s)
            except Exception:
                scalar_bad[t] += 1
                continue
            for kk, vv in o.items():
                subkeys[t][kk] += 1
                if vv is None or (isinstance(vv, str) and vv.strip() in ("", "-", "null", "NaN")):
                    inner_null[(t, kk)] += 1
        else:
            try:
                float(s)
            except Exception:
                scalar_bad[t] += 1

print("rows per sensor type:", dict(inner_rows))
print("composite sub-keys seen:", {k: dict(v) for k, v in subkeys.items()})
print("NULL/empty sub-fields inside composite values:", dict(inner_null))
print("rows whose valore is neither a number nor parseable JSON:", dict(scalar_bad))
