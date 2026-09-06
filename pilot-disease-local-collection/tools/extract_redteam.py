"""Extract red-team findings and their independent verification verdicts."""
import json, os, sys

journal = sys.argv[1]
rows = []
for line in open(journal, encoding='utf-8'):
    line = line.strip()
    if not line:
        continue
    try:
        rows.append(json.loads(line))
    except Exception:
        pass

lenses, verdicts = [], []
for r in rows:
    if r.get('type') != 'result':
        continue
    res = r.get('result')
    if not isinstance(res, dict):
        continue
    if 'findings' in res:
        lenses.append(res)
    elif 'verdict' in res:
        verdicts.append(res)

print(f'lenses returned  = {len(lenses)}')
print(f'verify verdicts  = {len(verdicts)}')
print()

n = 0
for L in lenses:
    print('=' * 78)
    print('LENS:', L.get('lens'))
    for f in L.get('findings') or []:
        n += 1
        print(f'\n  [{n}] {f.get("verdict")} / {f.get("severity")}')
        print(f'      ATTACKS : {f.get("claim_attacked")}')
        print(f'      FINDING : {(f.get("finding") or "")[:600]}')
        print(f'      CORRECT : {f.get("corrected_value")}')
    for s in L.get('claims_that_survived') or []:
        print(f'\n  SURVIVED: {s.get("claim")}')
        print(f'      my number: {s.get("my_number")}')

print()
print('=' * 78)
print('INDEPENDENT VERIFICATION')
tally = {}
for v in verdicts:
    k = v.get('verdict')
    tally[k] = tally.get(k, 0) + 1
    print(f'  [{k} / {v.get("severity")}] reproduced={v.get("reproduced")}')
    print(f'      corrected: {(v.get("corrected_statement") or "")[:400]}')
print()
print('verdict tally:', tally)

out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'manifests', 'red-team-result.json')
with open(out, 'w', encoding='utf-8') as f:
    json.dump({'lenses': lenses, 'verifications': verdicts,
               'verdict_tally': tally}, f, ensure_ascii=False, indent=1)
print('->', out)
