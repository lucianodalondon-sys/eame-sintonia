"""Disk truth: hash every preserved file under raw/ and report dedup state.

This does not trust any narrative. It walks the filesystem, hashes the bytes,
and records what is actually there. Dedup is by sha256:
  DISTINCT_DOCUMENT          first time this content is seen
  SAME_CONTENT_DIFFERENT_URL identical bytes already preserved elsewhere
Empty files are flagged EMPTY_FILE_NOT_ZERO — an empty artefact is a failed
capture, not a measurement of zero.
"""
import hashlib, json, os, sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, 'raw')
OUT = os.path.join(ROOT, 'manifests', 'raw-file-inventory.jsonl')


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


seen = {}
rows = []
by_front = defaultdict(lambda: {'files': 0, 'bytes': 0, 'distinct': 0, 'dupes': 0, 'empty': 0})

for dirpath, dirnames, filenames in os.walk(RAW):
    for fn in sorted(filenames):
        p = os.path.join(dirpath, fn)
        rel = os.path.relpath(p, ROOT).replace('\\', '/')
        front = rel.split('/')[1] if rel.startswith('raw/') and '/' in rel[4:] else 'raw'
        size = os.path.getsize(p)
        digest = sha256_of(p) if size else 'EMPTY_FILE_NO_HASH'
        if size == 0:
            state = 'EMPTY_FILE_NOT_ZERO'
            by_front[front]['empty'] += 1
        elif digest in seen:
            state = 'SAME_CONTENT_DIFFERENT_URL'
            by_front[front]['dupes'] += 1
        else:
            state = 'DISTINCT_DOCUMENT'
            seen[digest] = rel
            by_front[front]['distinct'] += 1
        by_front[front]['files'] += 1
        by_front[front]['bytes'] += size
        rows.append({
            'raw_path': rel, 'front': front, 'bytes': size, 'sha256': digest,
            'dedup': state, 'duplicate_of': seen.get(digest) if state == 'SAME_CONTENT_DIFFERENT_URL' else None,
            'ext': os.path.splitext(fn)[1].lower() or 'NONE',
        })

with open(OUT, 'w', encoding='utf-8') as f:
    for r in rows:
        f.write(json.dumps(r, ensure_ascii=False) + '\n')

total_bytes = sum(r['bytes'] for r in rows)
print(f'RAW_FILES_ON_DISK      = {len(rows)}')
print(f'RAW_BYTES_ON_DISK      = {total_bytes} ({total_bytes/1_048_576:.1f} MB)')
print(f'DISTINCT_BY_SHA256     = {len(seen)}')
print(f'DUPLICATE_CONTENT      = {sum(1 for r in rows if r["dedup"] == "SAME_CONTENT_DIFFERENT_URL")}')
print(f'EMPTY_FILES_NOT_ZERO   = {sum(1 for r in rows if r["dedup"] == "EMPTY_FILE_NOT_ZERO")}')
print()
print(f'{"front":26} {"files":>6} {"distinct":>9} {"dupes":>6} {"empty":>6} {"MB":>8}')
for k in sorted(by_front):
    v = by_front[k]
    print(f'{k:26} {v["files"]:6d} {v["distinct"]:9d} {v["dupes"]:6d} {v["empty"]:6d} {v["bytes"]/1_048_576:8.1f}')
print()
ext = defaultdict(int)
for r in rows:
    ext[r['ext']] += 1
print('by extension:', dict(sorted(ext.items(), key=lambda kv: -kv[1])[:12]))
print('inventory ->', OUT)
