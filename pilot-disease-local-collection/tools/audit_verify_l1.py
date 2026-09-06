import json, os, collections
ROOT = r"C:\disease-local-collection-italy\pilot-disease-local-collection"

def load(p):
    rows = []
    with open(os.path.join(ROOT, "manifests", p), encoding="utf-8") as f:
        for ln in f:
            ln = ln.strip()
            if ln:
                rows.append(json.loads(ln))
    return rows

for name in ["FAILED-arpav-docs-manifest-htmlshells.jsonl",
             "FAILED-arpav-monthly-manifest-htmlshells.jsonl"]:
    rows = load(name)
    keys = collections.Counter()
    for r in rows:
        keys.update(r.keys())
    exists = sum(1 for r in rows
                 if os.path.exists(os.path.join(ROOT, r["raw_path"].replace("/", os.sep))))
    print("=== " + name)
    print("  rows:", len(rows))
    print("  ALL KEYS:", sorted(keys))
    print("  raw_path exists on disk:", exists, " DANGLING:", len(rows) - exists)
    print("  preservation:", dict(collections.Counter(r.get("preservation") for r in rows)))
    print("  dedup       :", dict(collections.Counter(r.get("dedup") for r in rows)))
    print("  media_type  :", dict(collections.Counter(r.get("media_type") for r in rows)))
    print("  http_status :", dict(collections.Counter(r.get("http_status") for r in rows)))
    blob = json.dumps(rows).lower()
    for tok in ["fail", "supersed", "quarant", "shell", "invalid",
                "not_preserved", "collection_failed"]:
        print("   token %-18s present in row data: %s" % (tok, tok in blob))
    print()
