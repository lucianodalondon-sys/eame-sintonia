"""Summarise the recon agents that completed, focusing on what they PROVED.

A probe with a real HTTP status is evidence. A document listed as
downloaded=false is DISCOVERED, not COLLECTED, and is reported as such.
"""
import json, os, glob
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, 'manifests', 'recon')

for path in sorted(glob.glob(os.path.join(D, '*.json'))):
    if os.path.basename(path).startswith('_'):
        continue
    r = json.load(open(path, encoding='utf-8'))
    docs = r.get('documents') or []
    dl = [d for d in docs if d.get('downloaded')]
    print('=' * 74)
    print(r.get('front'))
    print('  SUMMARY:', (r.get('summary') or '')[:400])
    probes = r.get('probes') or []
    st = Counter(str(p.get('http_status')) for p in probes)
    vd = Counter(str(p.get('verdict')) for p in probes)
    print(f'  probes={len(probes)} statuses={dict(st)}')
    print(f'  verdicts={dict(vd)}')
    print(f'  index_pages={len(r.get("index_pages") or [])}')
    print(f'  documents: DISCOVERED={len(docs)} DOWNLOADED={len(dl)}  (DISCOVERED != COLLECTED)')
    for m in (r.get('measurements') or []):
        print(f'    {m.get("name")} = {m.get("value")}')
    for b in (r.get('blockers') or []):
        print(f'    BLOCKER [{b.get("kind")}] {b.get("url")} :: {(b.get("detail") or "")[:120]}')
    for n in (r.get('not_known') or [])[:8]:
        print(f'    NOT_KNOWN: {n[:150]}')
