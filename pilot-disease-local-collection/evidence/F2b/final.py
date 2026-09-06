import json, re, time
from probe import adv

# A) DIFESA FITOSANITARIA publications folder
print("### /ServiziOnLine/Pubblicazioni/DIFESA FITOSANITARIA")
rows = {}
page = 1
total = None
while True:
    st, n, d = adv({"sys_full_path": {"type": "TEXT", "value": "DIFESA FITOSANITARIA"}},
                   page=page, size=50)
    if total is None:
        total = d['page'].get('entitiesCount')
        print(" entitiesCount =", total)
    ents = d['page']['entities']
    if not ents:
        break
    for e in ents:
        a = e['attributes']
        rows[e['id']] = (a.get('sys_title') or e.get('name'), e.get('type'),
                         a.get('sys_canonical_url'), a.get('sys_full_path'))
    page += 1
    if page > 20:
        break
    time.sleep(0.15)
for k, v in sorted(rows.items(), key=lambda x: (x[1][3] or '')):
    print('  -', v[1], '|', (v[0] or '')[:75], '|', v[2])

# B) vine post date range
vp = json.load(open('vineprobe.json', encoding='utf-8'))
ds = [p['firstPublishedAt'] for p in vp['posts'] if p.get('firstPublishedAt')]
ds.sort()
print("\n### vine post firstPublishedAt (CMS publish date) range")
print(" n =", len(ds), " min =", ds[0], " max =", ds[-1])
print(" NOTE: this is the CMS publication timestamp, not the document's own year.")

# years literally present in vine post titles
yrs = {}
for p in vp['posts']:
    for y in re.findall(r'\b(19[89]\d|20[0-4]\d)\b', p['title'] or ''):
        yrs[y] = yrs.get(y, 0) + 1
print(" years literally in vine post TITLES:", dict(sorted(yrs.items())))

# C) trittico series specifically
print("\n### TRITTICO VITIVINICOLO series posts")
for p in sorted(vp['posts'], key=lambda x: x.get('firstPublishedAt') or ''):
    if re.search(r'trittico', p['title'] or '', re.I):
        print('  ', (p.get('firstPublishedAt') or '')[:10], '| http', p.get('http'),
              p.get('bytes'), '|', (p['title'] or '')[:72])
        print('     ', p.get('url'))

print("\n### PDF probe summary")
print(" total pdfs probed:", len(vp['pdfs']))
ok = [x for x in vp['pdfs'] if x['http'] == '200']
print(" http 200:", len(ok), " total bytes:", sum(x['bytes'] for x in ok))
print(" non-200:", [(x['http'], x['name']) for x in vp['pdfs'] if x['http'] != '200'])
