import json,re,hashlib,os
from collections import Counter
rows=[json.loads(l) for l in open('manifests/arpav-docs-manifest.verified.jsonl',encoding='utf-8')]
def cat(r):
    u=r['source_url']
    if '/file-e-allegati/annate-agrarie/' in u: return 'ANNATA'
    if '/file-e-allegati/peronospora-vite/' in u: return 'VINE_SLOT'
    if '/fitosanitari/fas-rapporti/' in u: return 'FAS'
    return 'OTHER'
c=Counter(cat(r) for r in rows)
print("MY CATEGORISATION:", dict(c), "total", sum(c.values()))
print("26+17+2 =", 26+17+2, " files on disk:", len(os.listdir('raw/F8-arpav-agrometeo-docs')))
print()
for r in rows:
    if cat(r)=='OTHER':
        p=r['raw_path']
        d=open(p,'rb').read()
        h=hashlib.sha256(d).hexdigest()
        print("ORPHAN ROW:")
        print("  title      :", r['document_title'])
        print("  raw_path   :", p, "exists:", os.path.exists(p))
        print("  bytes man  :", r['bytes'], " bytes disk:", len(d))
        print("  sha man    :", r['sha256'])
        print("  sha recomp :", h, "MATCH" if h==r['sha256'] else "*** MISMATCH ***")
        print("  magic      :", d[:8])
        print("  is real pdf:", d[:5]==b'%PDF-')
        print("  trailer    :", d[-32:])
        print("  preservation:", r['preservation'], "| verified:", r.get('content_verified'), "| http:", r['http_status'])
