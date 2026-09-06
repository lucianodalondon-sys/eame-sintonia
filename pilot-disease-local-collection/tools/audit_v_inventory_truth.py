"""Is the regenerated raw-file-inventory.jsonl actually TRUE, or just complete?

1. Recompute sha256 + bytes for a stratified sample (all F8, plus a spread of
   every other front) and compare against the inventory row.
2. Test whether the headline document totals CAN be reconciled from this file
   alone, i.e. whether a reader has a rule to separate real captures from the
   182 quarantined HTML shells.
Read-only.
"""
import hashlib
import json
import os
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INV = os.path.join(ROOT, "manifests", "raw-file-inventory.jsonl")

rows = [json.loads(l) for l in open(INV, encoding="utf-8") if l.strip()]
by_path = {r["raw_path"]: r for r in rows}

# ---------- 1. recompute hashes on a stratified sample ----------
by_front = defaultdict(list)
for r in rows:
    by_front[r["front"]].append(r)

sample = []
for front, rs in sorted(by_front.items()):
    rs = sorted(rs, key=lambda r: r["raw_path"])
    if front in ("F8-arpav-agrometeo-docs",):
        sample.extend(rs)                      # all 46 – these back claim C5
    else:
        step = max(1, len(rs) // 12)
        sample.extend(rs[::step][:12])

mismatch_sha, mismatch_bytes, unreadable = [], [], []
for r in sample:
    p = os.path.join(ROOT, r["raw_path"].replace("/", os.sep))
    try:
        b = open(p, "rb").read()
    except Exception as e:
        unreadable.append((r["raw_path"], str(e)))
        continue
    if len(b) != r["bytes"]:
        mismatch_bytes.append((r["raw_path"], r["bytes"], len(b)))
    want = hashlib.sha256(b).hexdigest() if b else "EMPTY_FILE_NO_HASH"
    if want != r["sha256"]:
        mismatch_sha.append((r["raw_path"], r["sha256"][:12], want[:12]))

print("=== 1. hash re-verification of a stratified sample ===")
print("   files sampled                 :", len(sample))
print("   sha256 MISMATCH               :", len(mismatch_sha))
print("   byte-length MISMATCH          :", len(mismatch_bytes))
print("   unreadable                    :", len(unreadable))
for m in (mismatch_sha + mismatch_bytes + unreadable)[:10]:
    print("     ", m)

# ---------- 2. can headline totals be reconciled from this file alone? ----------
print()
print("=== 2. reconciling document totals from the inventory alone ===")
quarantine = [r for r in rows if r["front"] == "_failed-captures"]
live = [r for r in rows if r["front"] != "_failed-captures"]
print(f"   rows total                    : {len(rows)}")
print(f"   rows under _failed-captures   : {len(quarantine)}  (known-bad HTML shells)")
print(f"   rows NOT quarantined          : {len(live)}")
print("   -> is 'front' a usable rule? every quarantined path starts raw/_failed-captures:",
      all(r["raw_path"].startswith("raw/_failed-captures/") for r in quarantine))
print("   -> any NON-quarantine row living under _failed-captures/:",
      sum(1 for r in live if r["raw_path"].startswith("raw/_failed-captures/")))

print()
print("   extension mix per document front (live vs quarantined):")
for front in ("F8-arpav-agrometeo-docs", "F7-arpav-bollettino-mese", "_failed-captures"):
    c = Counter(r["ext"] for r in by_front[front])
    print(f"     {front:28s} n={len(by_front[front]):4d}  {dict(c)}")

# do the quarantined shells collide with anything real?
live_sha = {r["sha256"] for r in live}
q_sha = {r["sha256"] for r in quarantine}
print()
print("   quarantined sha256 that also appear among live files:", len(live_sha & q_sha))
print("   distinct sha256 among the 182 quarantined            :", len(q_sha))

# ---------- 3. the 29 flagged duplicates: where do they sit? ----------
print()
print("=== 3. the 29 SAME_CONTENT_DIFFERENT_URL rows ===")
dupes = [r for r in rows if r["dedup"] == "SAME_CONTENT_DIFFERENT_URL"]
print("   by front:", dict(Counter(r["front"] for r in dupes)))
print("   any duplicate inside F7/F8/F4-arpav-rest (the headline fronts)?",
      dict(Counter(r["front"] for r in dupes
                   if r["front"] in ("F7-arpav-bollettino-mese",
                                     "F8-arpav-agrometeo-docs",
                                     "F4-arpav-rest"))) or "none")
empt = [r for r in rows if r["dedup"] == "EMPTY_FILE_NOT_ZERO"]
print("   EMPTY_FILE_NOT_ZERO rows:", [(r["raw_path"], r["bytes"]) for r in empt])

# ---------- 4. F7 completeness vs its own inventory ----------
print()
print("=== 4. is F7 still IN_PROGRESS? ===")
mi = [json.loads(l) for l in open(os.path.join(ROOT, "manifests", "arpav-monthly-inventory.jsonl"), encoding="utf-8") if l.strip()]
mm = [json.loads(l) for l in open(os.path.join(ROOT, "manifests", "arpav-monthly-manifest.jsonl"), encoding="utf-8") if l.strip()]
print("   monthly inventoried :", len(mi))
print("   monthly manifest    :", len(mm))
print("   F7 files on disk    :", len(by_front["F7-arpav-bollettino-mese"]))
