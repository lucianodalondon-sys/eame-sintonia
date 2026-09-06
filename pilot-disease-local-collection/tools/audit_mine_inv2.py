import json, os, hashlib

ROOT = r"C:\disease-local-collection-italy\pilot-disease-local-collection"
mine = json.load(open(os.path.join(ROOT, "tools", "_mine_hashes.json")))
mine_map = {r["path"]: (r["sha256"], r["bytes"]) for r in mine}
inv = [json.loads(l) for l in open(os.path.join(ROOT, "manifests", "raw-file-inventory.jsonl"), encoding="utf-8") if l.strip()]
inv_map = {r["raw_path"]: r["sha256"] for r in inv}

seen = set()
my_red = set()
for r in inv:
    if r["sha256"] in seen:
        my_red.add(r["raw_path"])
    else:
        seen.add(r["sha256"])

scdu = set(r["raw_path"] for r in inv if r["dedup"] == "SAME_CONTENT_DIFFERENT_URL")
print("SAME_CONTENT_DIFFERENT_URL rows :", len(scdu))
print("my redundant (2nd+ occurrence)  :", len(my_red))
print("exact same set?                 :", scdu == my_red)
print("flagged but not redundant       :", sorted(scdu - my_red))
print("redundant but not flagged       :", sorted(my_red - scdu))

print()
p = "raw/F4/probe-getXmlSensore-1209-2015.csv"
row = [r for r in inv if r["raw_path"] == p][0]
print("the one sha mismatch:")
print("   inventory row :", json.dumps(row))
print("   on disk sha   :", mine_map[p][0], " bytes:", mine_map[p][1])
print("   inventory sha of EMPTY file equals sha256 of b'' ?",
      row["sha256"] == hashlib.sha256(b"").hexdigest())
print("   sha256 of b''  =", hashlib.sha256(b"").hexdigest())
