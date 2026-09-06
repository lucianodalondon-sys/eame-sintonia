import json, os
ROOT = r"C:\disease-local-collection-italy\pilot-disease-local-collection"
inv = []
with open(os.path.join(ROOT, "manifests", "raw-file-inventory.jsonl"), encoding="utf-8") as f:
    for ln in f:
        ln = ln.strip()
        if ln:
            inv.append(json.loads(ln))

TOOL_EXT = {".py", ".sh", ".ps1", ".bat", ".log"}
src = [r for r in inv
       if "_failed-captures" not in r["raw_path"] and r["ext"] not in TOOL_EXT]
print("rows that are neither quarantine nor tooling-ext:", len(src))
print("  distinct sha256 among them:", len(set(r["sha256"] for r in src)))
print("  headline RAW_FILES_SOURCE_DOCUMENTS = 1674, RAW_DISTINCT_BY_SHA256 = 1644")
print("  duplicates implied:", len(src) - len(set(r["sha256"] for r in src)),
      "(headline RAW_DUPLICATE_CONTENT = 29)")
