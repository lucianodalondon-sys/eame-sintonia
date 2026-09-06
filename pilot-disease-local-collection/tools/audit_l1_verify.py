import json, collections, os, sys

ROOT = r"C:\disease-local-collection-italy\pilot-disease-local-collection"
INV = os.path.join(ROOT, "manifests", "raw-file-inventory.jsonl")

rows = []
bad = 0
with open(INV, "r", encoding="utf-8") as f:
    for ln in f:
        ln = ln.strip()
        if not ln:
            continue
        try:
            rows.append(json.loads(ln))
        except Exception:
            bad += 1

print("inventory rows parsed :", len(rows))
print("unparseable lines     :", bad)
print("distinct raw_path     :", len({r["raw_path"] for r in rows}))
print("distinct sha256       :", len({r["sha256"] for r in rows}))
print("by dedup field        :", dict(collections.Counter(r.get("dedup") for r in rows)))
print()

ext = collections.Counter(r.get("ext") for r in rows)
print("ALL rows by extension:")
for e, n in ext.most_common():
    print("  %-12s %d" % (e, n))
print()

dd = [r for r in rows if r.get("dedup") == "DISTINCT_DOCUMENT"]
ext_dd = collections.Counter(r.get("ext") for r in dd)
print("DISTINCT_DOCUMENT rows by extension (total %d):" % len(dd))
for e, n in ext_dd.most_common():
    print("  %-12s %d" % (e, n))
print()

py_all = [r for r in rows if r.get("ext") == ".py"]
py_dd = [r for r in py_all if r.get("dedup") == "DISTINCT_DOCUMENT"]
print("*** .py rows in inventory        :", len(py_all))
print("*** .py rows DISTINCT_DOCUMENT   :", len(py_dd))
print("*** .py rows NOT distinct_doc    :", len(py_all) - len(py_dd))
print()
print("first 8 .py rows:")
for r in py_all[:8]:
    print("   %-55s %7d %s" % (r["raw_path"], r["bytes"], r["dedup"]))
print("   ... (%d .py rows total)" % len(py_all))
print()

# the "scraped evidence artefact" bucket the other auditor named
art_exts = {".txt", ".js", ".htm", ".html"}
art = [r for r in rows if r.get("ext") in art_exts]
art_dd = [r for r in art if r.get("dedup") == "DISTINCT_DOCUMENT"]
print("artefact exts (.txt/.js/.htm/.html) all rows      :", len(art),
      dict(collections.Counter(r["ext"] for r in art)))
print("artefact exts DISTINCT_DOCUMENT                   :", len(art_dd),
      dict(collections.Counter(r["ext"] for r in art_dd)))
print()

print("CORRECTED counts:")
print("  all rows minus .py                  :", len(rows) - len(py_all))
print("  DISTINCT_DOCUMENT minus .py         :", len(dd) - len(py_dd))
print("  .gz DISTINCT_DOCUMENT               :", ext_dd.get(".gz", 0))
print("  .pdf DISTINCT_DOCUMENT              :", ext_dd.get(".pdf", 0))
