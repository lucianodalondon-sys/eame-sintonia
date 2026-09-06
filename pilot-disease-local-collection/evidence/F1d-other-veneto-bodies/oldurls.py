import json, sys, re
items = []
for f in sys.argv[1:]:
    items.extend(json.load(open(f, encoding='utf-8')))
rows = []
for it in items:
    url = it.get('source_url') or ''
    d = (it.get('date') or '')[:10]
    if re.search(r'bollettin', url.rsplit('/', 1)[-1], re.I):
        rows.append((d, url))
rows.sort()
# oldest 4 and a 2022/2023/2024 sample
pick = rows[:4] + [r for r in rows if r[0].startswith(('2022-04', '2023-04', '2024-04'))][:3]
for d, u in pick:
    print(d, u)
