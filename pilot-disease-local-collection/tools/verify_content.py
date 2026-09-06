"""Verify that each preserved file is really the document it claims to be.

A .pdf URL that returned an HTML app shell is NOT a preserved PDF. This walks a
manifest, reads the first bytes of every file, and classifies:

  CONTENT_OK              magic bytes match the declared/expected type
  CONTENT_TYPE_MISMATCH   e.g. an HTML shell served for a .pdf URL -> NOT_PRESERVED
  CONTENT_UNKNOWN         could not classify

Files that fail verification are demoted: DISCOVERED != COLLECTED.
"""
import json, os, sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MAGIC = [
    (b'%PDF-', 'pdf'),
    (b'PK\x03\x04', 'zip'),
    (b'\x1f\x8b', 'gzip'),
    (b'{', 'json'),
    (b'[', 'json'),
    (b'<?xml', 'xml'),
    (b'\xd0\xcf\x11\xe0', 'ole/msoffice'),
]


def classify(head):
    low = head[:200].lstrip().lower()
    if low.startswith(b'<!doctype html') or low.startswith(b'<html'):
        return 'html'
    for sig, name in MAGIC:
        if head.startswith(sig):
            return name
    return 'unknown'


def expected_from_url(url):
    u = url.lower().split('?')[0]
    for ext in ('.pdf', '.zip', '.csv', '.xls', '.xlsx', '.xml', '.json', '.doc', '.docx'):
        if ext in u:
            return ext.lstrip('.')
    return 'unknown'


man_path = os.path.join(ROOT, sys.argv[1])
rows = [json.loads(l) for l in open(man_path, encoding='utf-8') if l.strip()]
out_path = man_path.replace('.jsonl', '.verified.jsonl')

counts = Counter()
bad = []
with open(out_path, 'w', encoding='utf-8') as out:
    for r in rows:
        if r.get('preservation') != 'PRESERVED':
            r['content_verified'] = 'NOT_APPLICABLE'
            counts['not_preserved'] += 1
            out.write(json.dumps(r, ensure_ascii=False) + '\n')
            continue
        p = os.path.join(ROOT, r['raw_path'])
        try:
            with open(p, 'rb') as f:
                head = f.read(4096)
        except Exception as e:
            r['content_verified'] = 'CONTENT_UNKNOWN'
            r['verify_error'] = repr(e)[:120]
            counts['unreadable'] += 1
            out.write(json.dumps(r, ensure_ascii=False) + '\n')
            continue
        actual = classify(head)
        exp = expected_from_url(r['source_url'])
        r['actual_format'] = actual
        r['expected_format'] = exp
        if exp != 'unknown' and actual != exp:
            r['content_verified'] = 'CONTENT_TYPE_MISMATCH'
            r['preservation'] = 'NOT_PRESERVED'
            r['not_preserved_reason'] = (
                f'URL promised {exp} but bytes are {actual}; '
                'the document itself was NOT captured (DISCOVERED != COLLECTED)')
            counts['mismatch'] += 1
            bad.append(r)
        else:
            r['content_verified'] = 'CONTENT_OK'
            counts['ok'] += 1
        out.write(json.dumps(r, ensure_ascii=False) + '\n')

print(f'manifest: {sys.argv[1]}  rows={len(rows)}')
for k, v in counts.most_common():
    print(f'  {k:16} {v}')
print(f'verified manifest -> {os.path.relpath(out_path, ROOT)}')
if bad:
    print(f'\n--- {len(bad)} files DEMOTED to NOT_PRESERVED (content mismatch) ---')
    seen_dir = Counter()
    for r in bad:
        seen_dir[r['source_url'].rsplit('/', 2)[-2]] += 1
    for k, v in seen_dir.most_common(20):
        print(f'  {k:40} {v}')
    print('  example:', bad[0]['source_url'])
