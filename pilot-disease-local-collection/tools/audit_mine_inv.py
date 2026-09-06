import json, os, collections

ROOT = r"C:\disease-local-collection-italy\pilot-disease-local-collection"
mine = json.load(open(os.path.join(ROOT, "tools", "_mine_hashes.json")))
mine_map = {r["path"]: r["sha256"] for r in mine}

inv = [json.loads(l) for l in open(os.path.join(ROOT, "manifests", "raw-file-inventory.jsonl"), encoding="utf-8") if l.strip()]
print("inventory rows:", len(inv), " my files:", len(mine))

inv_map = {r["raw_path"]: r["sha256"] for r in inv}
print("paths in inventory not on disk:", len(set(inv_map) - set(mine_map)))
print("files on disk not in inventory:", len(set(mine_map) - set(inv_map)))
mismatch = [p for p in set(inv_map) & set(mine_map) if inv_map[p] != mine_map[p]]
print("sha mismatches inventory vs me:", len(mismatch))
for p in mismatch[:10]:
    print("   ", p)

print()
print("dedup flag tally:")
for k, v in collections.Counter(r["dedup"] for r in inv).most_common():
    print("   %-32s %d" % (k, v))

# my own independent set of redundant copies (2nd+ occurrence in inventory order)
seen = set()
my_redundant = []
for r in inv:
    if r["sha256"] in seen:
        my_redundant.append(r)
    else:
        seen.add(r["sha256"])
print()
print("redundant copies computed by me (2nd+ occurrence, inventory order):", len(my_redundant))

flagged = [r for r in inv if r["dedup"] != "DISTINCT_DOCUMENT"]
print("rows flagged non-DISTINCT_DOCUMENT                              :", len(flagged))
print("flagged set == my redundant set?", set(r["raw_path"] for r in flagged) == set(r["raw_path"] for r in my_redundant))

# does duplicate_of point at a real earlier file with the same sha?
bad = []
for r in flagged:
    tgt = r.get("duplicate_of")
    if tgt is None or tgt not in inv_map:
        bad.append((r["raw_path"], tgt, "TARGET_MISSING"))
    elif inv_map[tgt] != r["sha256"]:
        bad.append((r["raw_path"], tgt, "SHA_DIFFERS"))
print("flagged rows whose duplicate_of is broken:", len(bad))
for b in bad[:10]:
    print("   ", b)
