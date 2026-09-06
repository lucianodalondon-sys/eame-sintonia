import json, re, os
rows=[json.loads(l) for l in open('manifests/arpav-docs-manifest.verified.jsonl',encoding='utf-8')]
print("manifest rows:", len(rows))
# categorise strictly by the URL PATH SEGMENT, not by the title
def cat(r):
    u=r['source_url']
    m=re.search(r'/file-e-allegati/([^/]+)/', u)
    return m.group(1) if m else 'NO_FOLDER_SEGMENT'
from collections import Counter
c=Counter(cat(r) for r in rows)
for k,v in sorted(c.items(), key=lambda x:-x[1]):
    print(f"  {v:3d}  folder={k}")
print()
for r in rows:
    print(f"[{cat(r):28s}] {r['bytes']:9d}  {r['document_title'][:70]}")
    print(f"      {r['source_url']}")
