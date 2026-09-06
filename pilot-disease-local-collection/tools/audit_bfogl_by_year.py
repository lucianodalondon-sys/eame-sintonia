import json, glob, os, hashlib, collections, re

D = r"C:\disease-local-collection-italy\pilot-disease-local-collection\raw\F3b\bfogl_by_year"
files = sorted(glob.glob(os.path.join(D, "*.json")))
print("files:", len(files))

byhash = collections.OrderedDict()
allkeys = set()
meas_rows = 0
total_rows = 0
top_keys = set()

for f in files:
    b = open(f, "rb").read()
    h = hashlib.sha256(b).hexdigest()
    j = json.loads(b)
    top_keys |= set(j.keys()) if isinstance(j, dict) else {"<not-dict>"}
    data = j.get("data") if isinstance(j, dict) else j
    yr = re.search(r"_(\d{4})\.json$", f).group(1)
    ks = set()
    for r in data:
        ks |= set(r.keys())
        total_rows += 1
        # a measurement needs a timestamp AND a value
        if ("dataora" in r or "data" in r or "timestamp" in r) and ("valore" in r or "value" in r):
            meas_rows += 1
    allkeys |= ks
    byhash.setdefault(h, {"years": [], "rows": len(data), "keys": sorted(ks)})
    byhash[h]["years"].append(yr)

print("distinct contents:", len(byhash))
for h, v in byhash.items():
    has_meas = ("dataora" in v["keys"] or "data" in v["keys"]) and ("valore" in v["keys"])
    print(f"  {h[:12]} years={v['years']} rows={v['rows']:3d} is_measurement={has_meas}")

print("union of row keys:", sorted(allkeys))
print("top-level keys seen:", sorted(top_keys))
print("total rows across all 17 files:", total_rows)
print("rows that are measurements (timestamp+value):", meas_rows)

# distinct stations across the union
st = set()
prov = collections.Counter()
tipi = collections.Counter()
for f in files:
    j = json.load(open(f, encoding="utf-8"))
    for r in j["data"]:
        st.add(r["codice_stazione"])
        prov[r.get("provincia")] += 1
        tipi[r.get("tipo")] += 1
print("distinct codice_stazione across all 17 files:", len(st))
print("tipo values:", dict(tipi))
print("provincia distribution (row-counts):", dict(prov))
