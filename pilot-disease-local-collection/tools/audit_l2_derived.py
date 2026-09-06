import json, os
from collections import Counter

root = r"C:\disease-local-collection-italy\pilot-disease-local-collection"
rows = []
with open(os.path.join(root, "manifests", "raw-file-inventory.jsonl"), encoding="utf-8") as f:
    for ln in f:
        ln = ln.strip()
        if ln:
            rows.append(json.loads(ln))

cm = json.load(open(os.path.join(root, "manifests", "collection-manifest.json"), encoding="utf-8"))

quar = [r for r in rows if r["raw_path"].replace("\\", "/").split("/")[1] == "_failed-captures"]
script_ext = {".py", ".ps1", ".sh", ".bat", ".cmd"}
tooling = [r for r in rows if r["ext"] in script_ext and r not in quar]
tooling = [r for r in rows if r["ext"] in script_ext
           and r["raw_path"].replace("\\", "/").split("/")[1] != "_failed-captures"]
src = [r for r in rows
       if r["raw_path"].replace("\\", "/").split("/")[1] != "_failed-captures"
       and r["ext"] not in script_ext]

dup = [r for r in rows if r.get("dedup") != "DISTINCT_DOCUMENT"]
empty = [r for r in rows if r["bytes"] == 0]
src_bytes = sum(r["bytes"] for r in src)

def cmp(label, mine, key):
    theirs = cm.get(key, "<absent>")
    flag = "MATCH" if mine == theirs else "*** DIFFERS ***"
    print("%-42s recomputed=%-12s manifest=%-12s %s" % (label, mine, theirs, flag))

print("inventory rows:", len(rows))
print()
cmp("total files", len(rows), "RAW_FILES_TOTAL_ON_DISK")
cmp("source documents", len(src), "RAW_FILES_SOURCE_DOCUMENTS")
cmp("tooling scripts excluded", len(tooling), "RAW_FILES_TOOLING_SCRIPTS_EXCLUDED")
cmp("quarantined failed captures", len(quar), "RAW_FILES_QUARANTINED_FAILED_CAPTURES")
cmp("source bytes", src_bytes, "RAW_BYTES_SOURCE_DOCUMENTS")
cmp("duplicate content rows", len(dup), "RAW_DUPLICATE_CONTENT")
cmp("empty files", len(empty), "RAW_EMPTY_FILES_NOT_ZERO")
print()
print("partition check 1674+56+182 =", len(src) + len(tooling) + len(quar), "vs rows", len(rows))
print("dedup values:", dict(Counter(r.get("dedup") for r in rows)))
print()
print("distinct sha256 over all rows:", len(set(r["sha256"] for r in rows)))
