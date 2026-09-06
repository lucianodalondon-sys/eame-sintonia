import json, os, hashlib, collections
ROOT = r"C:\disease-local-collection-italy\pilot-disease-local-collection"

def load(p):
    rows = []
    with open(os.path.join(ROOT, "manifests", p), encoding="utf-8") as f:
        for ln in f:
            ln = ln.strip()
            if ln:
                rows.append(json.loads(ln))
    return rows

bad = load("FAILED-arpav-docs-manifest-htmlshells.jsonl")
good = load("arpav-docs-manifest.verified.jsonl")

# 1. do the FAILED raw_paths collide with any REAL file that exists?
goodpaths = set(r["raw_path"] for r in good)
coll = [r["raw_path"] for r in bad if r["raw_path"] in goodpaths]
print("FAILED raw_path colliding with a good manifest raw_path:", len(coll))

# 2. hash every real file on disk in F8 and in the F8 quarantine
def hashdir(rel):
    d = os.path.join(ROOT, rel.replace("/", os.sep))
    out = {}
    if not os.path.isdir(d):
        print("  (missing dir " + rel + ")")
        return out
    for fn in sorted(os.listdir(d)):
        fp = os.path.join(d, fn)
        if os.path.isfile(fp):
            b = open(fp, "rb").read()
            out[fn] = (hashlib.sha256(b).hexdigest(), b[:5])
    return out

live = hashdir("raw/F8-arpav-agrometeo-docs")
quar = hashdir("raw/_failed-captures/F8-html-shells-2026-09-06")
print("live F8 files on disk:", len(live),
      "magic:", dict(collections.Counter(v[1] for v in live.values())))
print("quarantined F8 files :", len(quar),
      "magic:", dict(collections.Counter(v[1] for v in quar.values())))

live_h = set(v[0] for v in live.values())
quar_h = set(v[0] for v in quar.values())
print("live/quarantine sha256 overlap:", len(live_h & quar_h))

# 3. KEY TEST: do the FAILED manifest sha256 match the QUARANTINED bytes?
bad_h = set(r["sha256"] for r in bad)
good_h = set(r["sha256"] for r in good)
print("FAILED manifest sha256 that match a quarantined file :", len(bad_h & quar_h), "/", len(bad_h))
print("FAILED manifest sha256 that match a LIVE (real) file  :", len(bad_h & live_h))
print("good  manifest sha256 that match a LIVE (real) file   :", len(good_h & live_h), "/", len(good_h))

# 4. raw-file-inventory: does it contain any quarantined file / any FAILED sha?
inv = load("raw-file-inventory.jsonl")
print("raw-file-inventory rows:", len(inv))
k = "path" if "path" in inv[0] else list(inv[0].keys())[0]
invpaths = [r.get("path") or r.get("raw_path") or "" for r in inv]
print("inventory rows mentioning _failed-captures:",
      sum(1 for p in invpaths if "_failed-captures" in p))
invsha = set(r.get("sha256") for r in inv)
print("inventory sha256 that are FAILED-manifest shells:", len(invsha & bad_h))
print("inventory sha256 that are good F8 docs          :", len(invsha & good_h))
