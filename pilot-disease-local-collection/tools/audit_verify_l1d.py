import json, os, collections
ROOT = r"C:\disease-local-collection-italy\pilot-disease-local-collection"
inv = []
with open(os.path.join(ROOT, "manifests", "raw-file-inventory.jsonl"), encoding="utf-8") as f:
    for ln in f:
        ln = ln.strip()
        if ln:
            inv.append(json.loads(ln))

q = [r for r in inv if "_failed-captures" in r["raw_path"]]
nq = [r for r in inv if "_failed-captures" not in r["raw_path"]]
print("inventory total rows      :", len(inv))
print("quarantine rows IN inventory:", len(q))
print("  their dedup labels      :", dict(collections.Counter(r["dedup"] for r in q)))
print("  their front labels      :", dict(collections.Counter(r["front"] for r in q)))
print("  their ext labels        :", dict(collections.Counter(r["ext"] for r in q)))

allsha = set(r["sha256"] for r in inv)
nqsha = set(r["sha256"] for r in nq)
qsha = set(r["sha256"] for r in q)
print()
print("distinct sha256 over ALL inventory rows      :", len(allsha))
print("distinct sha256 EXCLUDING quarantine         :", len(nqsha))
print("distinct sha256 contributed ONLY by quarantine:", len(qsha - nqsha))
print("quarantine sha256 also present outside        :", len(qsha & nqsha))

cm = json.load(open(os.path.join(ROOT, "manifests", "collection-manifest.json"), encoding="utf-8"))
print()
print("headline RAW_FILES_TOTAL_ON_DISK             :", cm["RAW_FILES_TOTAL_ON_DISK"])
print("headline RAW_FILES_SOURCE_DOCUMENTS          :", cm["RAW_FILES_SOURCE_DOCUMENTS"])
print("headline RAW_FILES_QUARANTINED_FAILED_CAPTURES:", cm["RAW_FILES_QUARANTINED_FAILED_CAPTURES"])
print("headline RAW_DISTINCT_BY_SHA256              :", cm["RAW_DISTINCT_BY_SHA256"])
print("  -> matches all-rows distinct?  ", cm["RAW_DISTINCT_BY_SHA256"] == len(allsha))
print("  -> matches ex-quarantine distinct?", cm["RAW_DISTINCT_BY_SHA256"] == len(nqsha))

# what does the headline say about the docs / monthly corpora?
for k in sorted(cm):
    if any(t in k for t in ["DOC", "ANNAT", "MONTH", "BOLLET", "PDF", "QUARANT", "FAILED", "F8", "F7"]):
        v = cm[k]
        if isinstance(v, (str, int, float)):
            print("  %-46s %s" % (k, str(v)[:150]))
