import json, hashlib, os, collections, re, zlib

ROOT = r'C:\disease-local-collection-italy\pilot-disease-local-collection'
D = os.path.join(ROOT, 'raw', 'F8-arpav-agrometeo-docs')

R = [json.loads(l) for l in open(os.path.join(ROOT, 'manifests', 'arpav-docs-manifest.verified.jsonl'), encoding='utf-8')]

print('=== [1] recompute sha256 of the 46 preserved doc files ===')
disk = {}
for f in sorted(os.listdir(D)):
    b = open(os.path.join(D, f), 'rb').read()
    disk[f] = (hashlib.sha256(b).hexdigest(), len(b), b[:5])
print('files on disk:', len(disk))
print('distinct sha256 on disk:', len({v[0] for v in disk.values()}))
notpdf = [(f, v[2]) for f, v in disk.items() if v[2][:4] != b'%PDF']
print('files whose magic bytes are NOT %PDF:', len(notpdf), notpdf[:5])

mism = []
for r in R:
    f = os.path.basename(r['raw_path'])
    if f not in disk:
        print('MANIFEST ROW WITH NO FILE:', f)
        continue
    if disk[f][0] != r['sha256'] or disk[f][1] != r['bytes']:
        mism.append((f, r['sha256'], disk[f][0], r['bytes'], disk[f][1]))
print('manifest sha256/bytes mismatch vs disk:', len(mism))
for m in mism[:5]:
    print('   ', m)

print()
print('=== [2] same PDF at two URLs? compare PDF internals ===')


def pdf_fingerprint(path):
    b = open(path, 'rb').read()
    # /ID array from trailer is the PDF's own document identifier
    ids = re.findall(rb'/ID\s*\[\s*<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>', b)
    npages = len(re.findall(rb'/Type\s*/Page[^s]', b))
    cd = re.findall(rb'/CreationDate\s*\(([^)]*)\)', b)
    md = re.findall(rb'/ModDate\s*\(([^)]*)\)', b)
    ti = re.findall(rb'/Title\s*\(([^)]*)\)', b)
    return dict(id=(ids[0][0].decode() if ids else None), pages=npages,
                creation=(cd[0].decode('latin1') if cd else None),
                mod=(md[0].decode('latin1') if md else None),
                title=(ti[0].decode('latin1') if ti else None), size=len(b))


fps = {}
for r in R:
    f = os.path.basename(r['raw_path'])
    fp = pdf_fingerprint(os.path.join(D, f))
    fps[f] = fp

byid = collections.defaultdict(list)
for f, fp in fps.items():
    if fp['id']:
        byid[fp['id']].append(f)
dupid = {k: v for k, v in byid.items() if len(v) > 1}
print('PDF /ID shared by >1 preserved file:', len(dupid))
title_of = {os.path.basename(r['raw_path']): r['document_title'] for r in R}
url_of = {os.path.basename(r['raw_path']): r['source_url'] for r in R}
for k, v in dupid.items():
    print('  /ID', k[:20], '->', [(f, title_of[f], fps[f]['size']) for f in v])

# same size+pages+creationdate but different bytes
bykey = collections.defaultdict(list)
for f, fp in fps.items():
    bykey[(fp['pages'], fp['creation'], fp['title'])].append(f)
for k, v in bykey.items():
    if len(v) > 1:
        print('  SAME pages/creation/title:', k, [(f, title_of[f], fps[f]['size'], disk[f][0][:12]) for f in v])

print()
print('=== [3] titles / seasons for the Annate agrarie claim ===')
ann = [r for r in R if 'nnata' in r['document_title'] or 'annate-agrarie' in r['source_url']]
print('rows that look like Annate agrarie:', len(ann))
seasons = []
for r in ann:
    m = re.search(r'(\d{4}(?:-\d{2,4})?)', r['document_title'])
    seasons.append(m.group(1) if m else 'NOMATCH:' + r['document_title'])
print('distinct season tokens:', len(set(seasons)))
cc = collections.Counter(seasons)
for k, v in sorted(cc.items()):
    print('   ', k, v, '<-- REPEATED' if v > 1 else '')
print()
for r in sorted(ann, key=lambda x: x['document_title']):
    print('   ', r['document_title'], '|', fps[os.path.basename(r['raw_path'])]['size'], '|', os.path.basename(r['raw_path']))

print()
print('=== [4] all 46 titles + urls ===')
for r in sorted(R, key=lambda x: x['source_url']):
    print('   ', r['document_title'], '||', r['source_url'].replace('https://www.arpa.veneto.it/temi-ambientali/agrometeo/file-e-allegati/', ''))
