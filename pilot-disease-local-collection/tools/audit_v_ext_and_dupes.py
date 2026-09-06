"""Two follow-ups on the regenerated inventory.

A) The real F8/F7 documents carry NO extension while the 182 quarantined HTML
   shells carry '.pdf'. Check the magic bytes on both sides so we know which
   set is really PDF, and whether a reader filtering the inventory by ext
   would land on the wrong pile.
B) The 2 SAME_CONTENT_DIFFERENT_URL rows inside F4-arpav-rest: are they among
   the 1038 daily .gz series files (which would dent claim C6), or elsewhere?
Read-only.
"""
import json
import os
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INV = os.path.join(ROOT, "manifests", "raw-file-inventory.jsonl")
rows = [json.loads(l) for l in open(INV, encoding="utf-8") if l.strip()]


def magic(rel, n=5):
    p = os.path.join(ROOT, rel.replace("/", os.sep))
    with open(p, "rb") as f:
        return f.read(n)


print("=== A) magic bytes: real documents vs quarantined shells ===")
for front in ("F8-arpav-agrometeo-docs", "F7-arpav-bollettino-mese", "_failed-captures"):
    rs = [r for r in rows if r["front"] == front]
    mags = Counter(magic(r["raw_path"]) for r in rs)
    exts = Counter(r["ext"] for r in rs)
    print(f"  {front}")
    print(f"     n={len(rs)}  ext={dict(exts)}")
    print(f"     magic={dict(mags)}")
    print(f"     sample name: {rs[0]['raw_path'].split('/')[-1]!r}")

pdf_ext_rows = [r for r in rows if r["ext"] == ".pdf"]
real_pdf_rows = [r for r in rows if magic(r["raw_path"])[:4] == b"%PDF"]
print()
print("  rows whose EXT is .pdf                  :", len(pdf_ext_rows))
print("     ...of those, actually %PDF on disk   :",
      sum(1 for r in pdf_ext_rows if magic(r["raw_path"])[:4] == b"%PDF"))
print("     ...of those, under _failed-captures  :",
      sum(1 for r in pdf_ext_rows if r["front"] == "_failed-captures"))
print("  rows that are REALLY %PDF on disk       :", len(real_pdf_rows))
print("     by front:", dict(Counter(r["front"] for r in real_pdf_rows)))

print()
print("=== B) the 2 duplicate-content rows inside F4-arpav-rest ===")
dupes = [r for r in rows
         if r["dedup"] == "SAME_CONTENT_DIFFERENT_URL" and r["front"] == "F4-arpav-rest"]
for r in dupes:
    print("   dup path      :", r["raw_path"])
    print("   duplicate_of  :", r["duplicate_of"])
    print("   bytes/sha     :", r["bytes"], r["sha256"][:16])
    print("   is it a daily tabella .gz?",
          r["raw_path"].startswith("raw/F4-arpav-rest/tabella/") and r["raw_path"].endswith(".json.gz"))
    print()

tab = [r for r in rows if r["raw_path"].startswith("raw/F4-arpav-rest/tabella/")]
print("   tabella/ files on disk        :", len(tab))
print("   tabella/ distinct sha256      :", len({r["sha256"] for r in tab}))
print("   tabella/ rows flagged as dup  :",
      sum(1 for r in tab if r["dedup"] == "SAME_CONTENT_DIFFERENT_URL"))
print("   (claim C6 asserts 1038 distinct sha256 among the daily files)")
