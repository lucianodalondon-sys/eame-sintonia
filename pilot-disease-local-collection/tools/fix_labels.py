"""Remediation of two labelling defects the red team confirmed.

(1) INVENTED DENOMINATOR FOR 2026.
    All 60 files for year 2026 carried expected_days = 365 and the state
    PARTIAL_SOURCE_GAP. Capture ran 2026-09-06; the source's own last published
    day is 2026-07-31. So 117 of those "missing" days had not happened yet, and
    calling the rest a SOURCE GAP names a cause that was never established.
    Fixed to: expected_days = days elapsed at capture, and the state split into
      YEAR_IN_PROGRESS_PUBLICATION_LAG   (elapsed but not yet published)
      NOT_YET_EXISTING                   (days after the capture date)

(2) MISLEADING ext FIELD IN raw-file-inventory.jsonl.
    ext came from the filename. 181 of the 224 rows with ext == ".pdf" are the
    quarantined HTML shells (saved under .pdf names), and 393 real PDFs have no
    extension at all (saved as <hash>_file). Fixed by adding actual_format read
    from the file's magic bytes, so nobody filters by extension and gets the
    wrong set.
"""
import json, os
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M = os.path.join(ROOT, 'manifests')
CAPTURE_DATE = date(2026, 9, 6)          # the day this collection ran


def days_in_year(y):
    return 366 if (y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)) else 365


# ---------------------------------------------------------------- (1) 2026
path = os.path.join(M, 'daily-series-provenance.jsonl')
rows = [json.loads(l) for l in open(path, encoding='utf-8') if l.strip()]
fixed = 0
for r in rows:
    if r['YEAR'] != CAPTURE_DATE.year:
        continue
    elapsed = (CAPTURE_DATE - date(r['YEAR'], 1, 1)).days + 1
    calendar = days_in_year(r['YEAR'])
    r['EXPECTED_DAYS_ORIGINAL_CLAIM'] = r['EXPECTED_DAYS']
    r['EXPECTED_DAYS'] = elapsed
    r['DAYS_ELAPSED_AT_CAPTURE'] = elapsed
    r['DAYS_NOT_YET_EXISTING'] = calendar - elapsed
    r['MISSING_DAYS'] = elapsed - r['DISTINCT_DATES']
    r['COMPLETENESS'] = 'YEAR_IN_PROGRESS_PUBLICATION_LAG'
    r['COMPLETENESS_NOTE'] = (
        f'Year in progress. Source last published {r["LAST_DATE"][:10]}; capture ran '
        f'{CAPTURE_DATE}. {r["MISSING_DAYS"]} elapsed days are not yet published '
        f'(publication lag, cause NOT_ESTABLISHED as a source gap); '
        f'{calendar - elapsed} further days of {r["YEAR"]} had not happened yet.')
    fixed += 1
with open(path, 'w', encoding='utf-8') as f:
    for r in rows:
        f.write(json.dumps(r, ensure_ascii=False) + '\n')
print(f'(1) daily-series-provenance.jsonl: {fixed} rows for {CAPTURE_DATE.year} relabelled')
from collections import Counter
print('    completeness now:', dict(Counter(r['COMPLETENESS'] for r in rows)))

# report the worst non-in-progress shortfalls, which the red team flagged
past = [r for r in rows if r['YEAR'] != CAPTURE_DATE.year]
past.sort(key=lambda r: r['DISTINCT_DATES'] / r['EXPECTED_DAYS'])
print(f'    completed-year files: {len(past)}')
for band, lo, hi in (('below 50%', 0, .50), ('50-95%', .50, .95)):
    sel = [r for r in past if lo <= r['DISTINCT_DATES'] / r['EXPECTED_DAYS'] < hi]
    print(f'    {band}: {len(sel)}')
    for r in sel:
        pct = 100 * r['DISTINCT_DATES'] / r['EXPECTED_DAYS']
        print(f'       {r["STATION_NAME"][:28]:30} {r["VARIABLE_CODE"]:8} {r["YEAR"]} '
              f'{r["DISTINCT_DATES"]:3d}/{r["EXPECTED_DAYS"]} = {pct:5.1f}%')

# ---------------------------------------------------------------- (2) ext
inv = os.path.join(M, 'raw-file-inventory.jsonl')
rows = [json.loads(l) for l in open(inv, encoding='utf-8') if l.strip()]


def magic_of(rel):
    p = os.path.join(ROOT, rel.replace('/', os.sep))
    try:
        with open(p, 'rb') as f:
            head = f.read(64)
    except Exception:
        return 'FILE_MISSING'
    low = head.lstrip().lower()
    if low.startswith(b'<!doctype html') or low.startswith(b'<html'):
        return 'html'
    if head.startswith(b'%PDF-'):
        return 'pdf'
    if head.startswith(b'\x1f\x8b'):
        return 'gzip'
    if head.startswith(b'PK\x03\x04'):
        return 'zip'
    if head.lstrip()[:1] in (b'{', b'['):
        return 'json'
    if low.startswith(b'<?xml'):
        return 'xml'
    if not head:
        return 'EMPTY'
    return 'other/text'


counts = {}
mismatch = 0
for r in rows:
    a = magic_of(r['raw_path'])
    r['actual_format'] = a
    ext = (r.get('ext') or '').lstrip('.')
    r['ext_matches_content'] = (ext == a) or (ext == 'gz' and a == 'gzip') or (ext == 'NONE')
    if ext and ext != 'NONE' and not r['ext_matches_content']:
        mismatch += 1
    counts[a] = counts.get(a, 0) + 1
with open(inv, 'w', encoding='utf-8') as f:
    for r in rows:
        f.write(json.dumps(r, ensure_ascii=False) + '\n')
print()
print(f'(2) raw-file-inventory.jsonl: actual_format added to {len(rows)} rows')
print(f'    by real content: {dict(sorted(counts.items(), key=lambda kv: -kv[1]))}')
print(f'    rows where the filename extension LIES about the content: {mismatch}')
real_pdf = sum(1 for r in rows if r['actual_format'] == 'pdf')
ext_pdf = sum(1 for r in rows if r.get('ext') == '.pdf')
ext_pdf_really_html = sum(1 for r in rows if r.get('ext') == '.pdf' and r['actual_format'] == 'html')
print(f'    real PDFs on disk: {real_pdf}   rows named .pdf: {ext_pdf}   '
      f'of those actually HTML: {ext_pdf_really_html}')
