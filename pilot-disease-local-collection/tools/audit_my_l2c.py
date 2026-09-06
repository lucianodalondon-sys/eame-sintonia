import json,os,hashlib
from collections import Counter
rows=[json.loads(l) for l in open('manifests/arpav-docs-manifest.verified.jsonl',encoding='utf-8')]
sh=[r['sha256'] for r in rows]
print("rows:",len(rows),"distinct sha256:",len(set(sh)),"distinct raw_path:",len(set(r['raw_path'] for r in rows)))
print("distinct source_url:",len(set(r['source_url'] for r in rows)))
dup=[k for k,v in Counter(sh).items() if v>1]
print("DUPLICATE sha256:",dup if dup else "NONE -> 46 distinct documents")
orph='7585ef9aca2caf7b89634f53c8bbe1b73d6c0e326bb01a7cedbcef56a28d8222'
print("orphan sha appears in docs manifest N times:",sh.count(orph))
# re-hash ALL 46 files on disk myself
d='raw/F8-arpav-agrometeo-docs'
disk={}
bad=[]
for f in sorted(os.listdir(d)):
    b=open(os.path.join(d,f),'rb').read()
    disk[hashlib.sha256(b).hexdigest()]=f
    if b[:5]!=b'%PDF-': bad.append((f,b[:20]))
print("files on disk:",len(os.listdir(d)),"distinct sha on disk:",len(disk))
print("NOT-a-PDF on disk:",bad if bad else "NONE - all 46 have %PDF- magic")
print("disk shas == manifest shas:", set(disk)==set(sh))
# is the orphan sha present anywhere else in the whole package's inventories?
for mf in ['manifests/raw-file-inventory.jsonl','manifests/arpav-monthly-manifest.verified.jsonl',
           'manifests/FAILED-arpav-docs-manifest-htmlshells.jsonl','manifests/arpav-docs-inventory.jsonl']:
    n=0; paths=[]
    for l in open(mf,encoding='utf-8'):
        if orph in l:
            n+=1
            try: paths.append(json.loads(l).get('raw_path') or json.loads(l).get('path'))
            except: pass
    print(f"  orphan sha in {os.path.basename(mf)}: {n} line(s) {paths}")
