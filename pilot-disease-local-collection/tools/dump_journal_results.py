"""Write each completed workflow-agent result to its own JSON file.

Agents that never produced a result are listed as NOT_COMPLETED — a stopped
agent is not an agent that found nothing.
"""
import json, os, sys

journal, outdir = sys.argv[1], sys.argv[2]
os.makedirs(outdir, exist_ok=True)

started = 0
results = []
for line in open(journal, encoding='utf-8'):
    line = line.strip()
    if not line:
        continue
    try:
        r = json.loads(line)
    except Exception:
        continue
    t = r.get('type')
    if t == 'started':
        started += 1
    elif t == 'result':
        results.append(r)

fronts = []
for r in results:
    res = r.get('result')
    if not isinstance(res, dict):
        continue
    front = res.get('front') or 'unknown'
    fronts.append(front)
    path = os.path.join(outdir, f'{front}.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    print('wrote', path)

summary = {
    'agents_started': started,
    'agents_returned_result': len(results),
    'agents_not_completed': started - len(results),
    'fronts_with_result': sorted(fronts),
    'note': ('Agents without a result were STOPPED when the session ended. '
             'NOT_COMPLETED means no structured result was delivered; it does '
             'NOT mean the front is empty. Raw material some of them wrote to '
             'disk is inventoried separately by hash_raw_tree.py.'),
}
with open(os.path.join(outdir, '_recon-summary.json'), 'w', encoding='utf-8') as f:
    json.dump(summary, f, ensure_ascii=False, indent=1)
print(json.dumps(summary, ensure_ascii=False, indent=1))
