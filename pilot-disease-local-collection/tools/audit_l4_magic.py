"""L4 AUDIT — independent magic-byte check of F8 docs, F7 monthly and the quarantine.

Read-only.
"""
import os, json, hashlib, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def kind(b):
    if b[:5] == b'%PDF-':
        return 'pdf'
    if b[:2] == b'PK':
        return 'zip'
    head = b[:600].lstrip().lower()
    if head[:9] == b'<!doctype' or head[:5] == b'<html' or b'<html' in head:
        return 'HTML_SHELL'
    if b[:1] in (b'{', b'['):
        return 'json'
    return 'other:' + repr(b[:8])


def scan(d):
    c = collections.Counter()
    shas = {}
    for f in sorted(os.listdir(d)):
        p = os.path.join(d, f)
        if not os.path.isfile(p):
            continue
        b = open(p, 'rb').read()
        c[kind(b)] += 1
        shas[f] = hashlib.sha256(b).hexdigest()
    return c, shas


for rel in ['raw/F8-arpav-agrometeo-docs',
            'raw/F7-arpav-bollettino-mese',
            'raw/_failed-captures/F8-html-shells-2026-09-06',
            'raw/_failed-captures/F7-html-shells-2026-09-06']:
    d = os.path.join(ROOT, rel.replace('/', os.sep))
    if not os.path.isdir(d):
        print(rel, 'MISSING')
        continue
    c, shas = scan(d)
    print('%-50s %s   files=%d  distinct_sha=%d' % (rel, dict(c), len(shas), len(set(shas.values()))))

# cross-check: does any GOOD F8 file share a sha with a quarantined shell?
good = scan(os.path.join(ROOT, 'raw', 'F8-arpav-agrometeo-docs'))[1]
bad = scan(os.path.join(ROOT, 'raw', '_failed-captures', 'F8-html-shells-2026-09-06'))[1]
inter = set(good.values()) & set(bad.values())
print('\nsha overlap good-F8 vs quarantined-F8 :', len(inter))

# cross-check the manifests
man = [json.loads(l) for l in open(os.path.join(ROOT, 'manifests', 'arpav-docs-manifest.jsonl'),
                                   encoding='utf-8') if l.strip()]
fail = [json.loads(l) for l in open(
    os.path.join(ROOT, 'manifests', 'FAILED-arpav-docs-manifest-htmlshells.jsonl'),
    encoding='utf-8') if l.strip()]
print('sha overlap docs-manifest vs FAILED-manifest :',
      len(set(r['sha256'] for r in man) & set(r['sha256'] for r in fail)))
print('local_item_id overlap                        :',
      len(set(r['local_item_id'] for r in man) & set(r['local_item_id'] for r in fail)))
print('title overlap (same 46 documents re-fetched) :',
      len(set(r['document_title'] for r in man) & set(r['document_title'] for r in fail)))

# verify every current F8 file really is a PDF and matches the verified manifest
ver = [json.loads(l) for l in open(
    os.path.join(ROOT, 'manifests', 'arpav-docs-manifest.verified.jsonl'), encoding='utf-8') if l.strip()]
ok = pdf = shaok = 0
for r in ver:
    p = os.path.join(ROOT, r['raw_path'].replace('/', os.sep))
    b = open(p, 'rb').read()
    k = kind(b)
    if k == 'pdf':
        pdf += 1
    if hashlib.sha256(b).hexdigest() == r['sha256'] and len(b) == r['bytes']:
        shaok += 1
    if r.get('content_verified') == 'CONTENT_OK' and k == r.get('actual_format'):
        ok += 1
print('\nverified manifest rows            :', len(ver))
print('  really %%PDF- on disk            :', pdf)
print('  sha256+bytes reproduced          :', shaok)
print('  CONTENT_OK and format agrees     :', ok)
print('  %%%%EOF present                    :',
      sum(1 for r in ver if b'%%EOF' in open(
          os.path.join(ROOT, r['raw_path'].replace('/', os.sep)), 'rb').read()[-4096:]))
