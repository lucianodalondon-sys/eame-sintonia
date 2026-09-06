"""Remediation: mark the pre-verification manifests as superseded.

RED TEAM FINDING (CONFIRMED): a consumer unioning manifests/*.jsonl on
preservation == "PRESERVED" counts the same document twice, because
arpav-docs-manifest.jsonl and arpav-docs-manifest.verified.jsonl describe the
same 46 documents (same for the 347 monthly ones).

Nothing is deleted. Each row of the pre-verification manifest gains
`superseded_by`, so any union query can drop them with one filter.
"""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M = os.path.join(ROOT, 'manifests')

PAIRS = [
    ('arpav-docs-manifest.jsonl', 'arpav-docs-manifest.verified.jsonl'),
    ('arpav-monthly-manifest.jsonl', 'arpav-monthly-manifest.verified.jsonl'),
]

for base, verified in PAIRS:
    bp, vp = os.path.join(M, base), os.path.join(M, verified)
    if not (os.path.exists(bp) and os.path.exists(vp)):
        print(f'{base}: pair incomplete, skipped')
        continue
    rows = [json.loads(l) for l in open(bp, encoding='utf-8') if l.strip()]
    for r in rows:
        r['superseded_by'] = verified
        r['counts_as_preserved_document'] = False
        r['note'] = ('Pre-verification snapshot. The authoritative row for this '
                     'document is the one in ' + verified + ', which additionally '
                     'carries content_verified from the file magic bytes. Kept so '
                     'the collection history stays auditable; do NOT count both.')
    with open(bp, 'w', encoding='utf-8') as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
    print(f'{base}: {len(rows)} rows marked superseded_by {verified}')

# recount what a safe union query now yields
count = 0
per_file = {}
for fn in sorted(os.listdir(M)):
    if not fn.endswith('.jsonl'):
        continue
    n = 0
    for l in open(os.path.join(M, fn), encoding='utf-8'):
        try:
            r = json.loads(l)
        except Exception:
            continue
        if r.get('preservation') == 'PRESERVED' and r.get('counts_as_preserved_document') is not False:
            n += 1
    if n:
        per_file[fn] = n
        count += n
print()
print('SAFE UNION — rows that are PRESERVED and not superseded/failed:')
for k, v in per_file.items():
    print(f'  {k:52} {v}')
print(f'  {"TOTAL DISTINCT PRESERVED ARTIFACTS":52} {count}')
