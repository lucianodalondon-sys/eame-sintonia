"""Remediation: relabel the quarantined failed captures.

RED TEAM FINDING (CONFIRMED / HIGH, reproduced twice):
  All 182 rows in the two FAILED-*.jsonl manifests carried
  "preservation": "PRESERVED" and "dedup": "DISTINCT_DOCUMENT" for fetches that
  returned the site's HTML application shell instead of the document, with a
  raw_path pointing at the good-download folder where the file no longer is.
  A consumer unioning manifests/*.jsonl on preservation == "PRESERVED" would
  pick up 182 phantom documents.

  That is a direct LEI ZERO breach: a failed fetch labelled as preserved.

This script rewrites those rows to the truth. It does NOT delete anything: the
bytes stay in raw/_failed-captures/ and the rows stay in the manifest, now
correctly labelled COLLECTION_FAILED with a working quarantine path.
"""
import hashlib, json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M = os.path.join(ROOT, 'manifests')

TARGETS = {
    'FAILED-arpav-docs-manifest-htmlshells.jsonl': 'raw/_failed-captures/F8-html-shells-2026-09-06',
    'FAILED-arpav-monthly-manifest-htmlshells.jsonl': 'raw/_failed-captures/F7-html-shells-2026-09-06',
}

REASON = ('The URL promised a PDF but the server returned the Plone/Volto HTML '
          'application shell. The document itself was NEVER captured. '
          'DISCOVERED != COLLECTED. Superseded by a re-download using '
          '/@@download/file, recorded in the matching non-FAILED manifest.')


def magic(path):
    try:
        with open(path, 'rb') as f:
            head = f.read(64)
    except Exception:
        return 'FILE_MISSING'
    low = head.lstrip().lower()
    if low.startswith(b'<!doctype html') or low.startswith(b'<html'):
        return 'html'
    if head.startswith(b'%PDF-'):
        return 'pdf'
    return 'unknown'


for name, qdir in TARGETS.items():
    path = os.path.join(M, name)
    if not os.path.exists(path):
        print(f'{name}: NOT FOUND, skipped')
        continue
    rows = [json.loads(l) for l in open(path, encoding='utf-8') if l.strip()]
    qabs = os.path.join(ROOT, qdir.replace('/', os.sep))
    on_disk = set(os.listdir(qabs)) if os.path.isdir(qabs) else set()
    fixed = relinked = 0
    for r in rows:
        old = r.get('raw_path', '')
        fname = old.rsplit('/', 1)[-1] if old else ''
        newpath = f'{qdir}/{fname}' if fname in on_disk else 'NOT_KNOWN'
        if newpath != 'NOT_KNOWN':
            relinked += 1
            r['actual_format_on_disk'] = magic(os.path.join(ROOT, newpath.replace('/', os.sep)))
        else:
            r['actual_format_on_disk'] = 'FILE_NOT_FOUND_AT_EXPECTED_QUARANTINE_PATH'
        r['preservation'] = 'COLLECTION_FAILED'
        r['not_preserved_reason'] = REASON
        r['dedup'] = 'NOT_APPLICABLE_FAILED_CAPTURE'
        r['expected_format'] = 'pdf'
        r['quarantined_path'] = newpath
        r['raw_path_original_claim'] = old
        r['raw_path'] = newpath
        r['counts_as_preserved_document'] = False
        fixed += 1
    with open(path, 'w', encoding='utf-8') as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
    kinds = {}
    for r in rows:
        kinds[r['actual_format_on_disk']] = kinds.get(r['actual_format_on_disk'], 0) + 1
    print(f'{name}: {fixed} rows relabelled COLLECTION_FAILED, '
          f'{relinked} raw_path re-pointed to quarantine, formats={kinds}')

# sanity: nothing anywhere should now claim PRESERVED for a quarantined file
tot = 0
for fn in os.listdir(M):
    if not fn.endswith('.jsonl'):
        continue
    for l in open(os.path.join(M, fn), encoding='utf-8'):
        if '"preservation": "PRESERVED"' in l:
            tot += 1
print(f'\nrows still claiming PRESERVED across all manifests = {tot}')
