"""Summarise a workflow journal: which agents finished, and what they returned.

Prints only what the journal records. An agent with no completion record is
reported as NOT_COMPLETED, never as "returned nothing".
"""
import json, sys

path = sys.argv[1]
rows = []
for line in open(path, encoding='utf-8'):
    line = line.strip()
    if not line:
        continue
    try:
        rows.append(json.loads(line))
    except Exception:
        pass

print(f'journal entries: {len(rows)}')
kinds = {}
for r in rows:
    k = r.get('type') or r.get('kind') or r.get('event') or '?'
    kinds[k] = kinds.get(k, 0) + 1
print('entry kinds:', kinds)
print()

for r in rows:
    label = r.get('label') or r.get('agentLabel') or r.get('id') or '?'
    k = r.get('type') or r.get('kind') or r.get('event') or '?'
    res = r.get('result')
    if res is None:
        res = r.get('output') or r.get('value')
    if isinstance(res, dict):
        front = res.get('front') or ''
        docs = len(res.get('documents') or [])
        probes = len(res.get('probes') or [])
        idx = len(res.get('index_pages') or [])
        meas = len(res.get('measurements') or [])
        blk = len(res.get('blockers') or [])
        print(f'[{k}] {label} | front={front} probes={probes} index={idx} docs={docs} meas={meas} blockers={blk}')
    elif isinstance(res, str):
        print(f'[{k}] {label} | text {len(res)} chars')
    else:
        print(f'[{k}] {label} | result={type(res).__name__}')
