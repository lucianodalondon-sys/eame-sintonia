import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def P(*a): return os.path.join(ROOT, *a)

for m in ['manifests/FAILED-arpav-docs-manifest-htmlshells.jsonl',
          'manifests/FAILED-arpav-monthly-manifest-htmlshells.jsonl']:
    rows = [json.loads(l) for l in open(P(m), encoding='utf-8') if l.strip()]
    ex = sum(1 for r in rows if os.path.exists(P(r['raw_path'])))
    print(m)
    print("   rows:", len(rows), " raw_path exists:", ex, " DANGLING:", len(rows) - ex)
    print("   sample raw_path:", rows[0]['raw_path'])
    print("   preservation values:", sorted({r.get('preservation') for r in rows}))
    print("   media_type values:", sorted({r.get('media_type') for r in rows}))
    print("   any 'failed'/'quarantine' key?:",
          [k for k in rows[0].keys() if 'fail' in k.lower() or 'quar' in k.lower() or 'valid' in k.lower()])
