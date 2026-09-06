"""Count preserved documents from a manifest, by folder and by declared season.

Seasons are taken from the source's OWN title (e.g. "Annata agraria 2000-01"),
never inferred from a filename guess. A title that carries no year is
NOT_KNOWN, not dropped.
"""
import json, os, re, sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
man = sys.argv[1]
rows = [json.loads(l) for l in open(os.path.join(ROOT, man), encoding='utf-8') if l.strip()]

ok = [r for r in rows if r.get('preservation') == 'PRESERVED']
bad = [r for r in rows if r.get('preservation') != 'PRESERVED']
print(f'manifest rows      = {len(rows)}')
print(f'PRESERVED          = {len(ok)}')
print(f'NOT_PRESERVED      = {len(bad)}')
print(f'bytes              = {sum(r.get("bytes", 0) for r in ok)} '
      f'({sum(r.get("bytes",0) for r in ok)/1_048_576:.1f} MB)')
digests = {r['sha256'] for r in ok if r.get('sha256')}
print(f'DISTINCT_BY_SHA256 = {len(digests)}')
print(f'SAME_CONTENT_DIFFERENT_URL = {sum(1 for r in ok if r.get("dedup") == "SAME_CONTENT_DIFFERENT_URL")}')
print()

groups = defaultdict(list)
for r in ok:
    # group by the folder segment right under file-e-allegati / fitosanitari
    u = r['source_url']
    parts = u.split('/')
    key = parts[-2] if len(parts) > 2 else 'root'
    groups[key].append(r)
for k in sorted(groups):
    print(f'  {k:34} {len(groups[k]):4d} files  {sum(x.get("bytes",0) for x in groups[k])/1_048_576:6.1f} MB')

print()
annate = [r for r in ok if 'annate-agrarie' in r['source_url']]
print(f'ANNATE_DOCUMENTS_PRESERVED = {len(annate)}')
seasons = {}
for r in annate:
    t = r.get('document_title') or ''
    m = re.search(r'(\d{4})\s*-\s*(\d{2})\b', t)
    if m:
        s = f'{m.group(1)}-{m.group(2)}'
    else:
        m2 = re.search(r'\b(20\d\d|19\d\d)\b', t)
        s = m2.group(1) if m2 else 'NOT_KNOWN'
    seasons.setdefault(s, []).append(r)
print(f'ANNATE_DISTINCT_SEASONS    = {len(seasons)}')
print('  seasons:', ', '.join(sorted(seasons)))
multi = {k: v for k, v in seasons.items() if len(v) > 1}
if multi:
    print('  SEASONS WITH MORE THAN ONE FILE (possible DISTINCT_VERSION or duplicate):')
    for k, v in sorted(multi.items()):
        for r in v:
            print(f'     {k}  {r["sha256"][:12]}  {r["bytes"]:>9}  {r["source_url"]}')
nk = seasons.get('NOT_KNOWN', [])
if nk:
    print('  NOT_KNOWN titles:')
    for r in nk:
        print(f'     {r.get("document_title")} | {r["source_url"]}')

print()
vine = [r for r in ok if 'peronospora-vite' in r['source_url']]
print(f'PERONOSPORA_VITE_FOLDER_FILES_PRESERVED = {len(vine)}')
for r in vine:
    print(f'   {r.get("document_title")!r:34} {r["bytes"]:>8}B  published={r.get("published_at")}  {r["source_url"]}')
