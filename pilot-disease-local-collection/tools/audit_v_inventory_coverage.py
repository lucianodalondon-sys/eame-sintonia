"""Independent check: does manifests/raw-file-inventory.jsonl cover every file under raw/?

Read-only. Walks raw/ itself, builds the set of paths, and diffs against the
inventory's raw_path set. Normalises separators so Windows backslashes and
POSIX slashes compare equal.
"""
import json
import os
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "raw")
INV = os.path.join(ROOT, "manifests", "raw-file-inventory.jsonl")


def norm(p):
    return p.replace("\\", "/").strip().lstrip("./")


# --- walk the tree ---
on_disk = set()
for dirpath, dirnames, filenames in os.walk(RAW):
    for fn in filenames:
        full = os.path.join(dirpath, fn)
        rel = os.path.relpath(full, ROOT)
        on_disk.add(norm(rel))

# --- read the inventory ---
inv_rows = 0
inv_paths = []
bad = 0
for line in open(INV, encoding="utf-8"):
    line = line.strip()
    if not line:
        continue
    inv_rows += 1
    try:
        d = json.loads(line)
    except Exception:
        bad += 1
        continue
    inv_paths.append(norm(d.get("raw_path", "")))

inv_set = set(inv_paths)

print("inventory rows (non-blank lines):", inv_rows)
print("inventory unmalformed paths     :", len(inv_paths))
print("inventory DISTINCT paths        :", len(inv_set))
print("inventory duplicate path rows   :", len(inv_paths) - len(inv_set))
print("files on disk under raw/        :", len(on_disk))
print()

missing = on_disk - inv_set          # on disk, not described
dangling = inv_set - on_disk         # described, not on disk

print("=== on disk but NOT in inventory ===  total:", len(missing))
for folder, n in Counter(p.split("/")[1] if p.count("/") > 1 else "(root)"
                         for p in missing).most_common():
    print(f"   {folder:35s} {n}")
print()
print("=== in inventory but NOT on disk (dangling) ===  total:", len(dangling))
for folder, n in Counter(p.split("/")[1] if p.count("/") > 1 else "(root)"
                         for p in dangling).most_common():
    print(f"   {folder:35s} {n}")
print()

# Per-folder side-by-side, so a partial front is visible
disk_by = Counter(p.split("/")[1] if p.count("/") > 1 else "(root)" for p in on_disk)
inv_by = Counter(p.split("/")[1] if p.count("/") > 1 else "(root)" for p in inv_set)
print("=== per-folder: disk vs inventory ===")
print(f"   {'folder':35s} {'disk':>6} {'inv':>6} {'delta':>6}")
for folder in sorted(set(disk_by) | set(inv_by)):
    d, i = disk_by[folder], inv_by[folder]
    flag = "" if d == i else "   <-- MISMATCH"
    print(f"   {folder:35s} {d:6d} {i:6d} {i - d:6d}{flag}")

# Are the specific fronts the other auditor named present at all?
print()
print("=== fronts the prior finding said were absent ===")
for front in ("F8-arpav-agrometeo-docs", "F7-arpav-bollettino-mese",
              "_failed-captures", "F4-arpav-rest/geo"):
    n_inv = sum(1 for p in inv_set if p.startswith("raw/" + front))
    n_disk = sum(1 for p in on_disk if p.startswith("raw/" + front))
    print(f"   {front:35s} disk={n_disk:5d}  inventory={n_inv:5d}")
