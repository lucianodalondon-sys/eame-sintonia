import json, glob, urllib.request, urllib.parse, time

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36")
BASE = "https://www.venetoagricoltura.org/myportal/AVPISP"

union = {}
for fn in sorted(glob.glob('term_*.json')):
    term = fn[5:-5]
    d = json.load(open(fn, encoding='utf-8'))
    for k, v in d.items():
        union.setdefault(k, dict(v, terms=set()))
        union[k]['terms'].add(term)

print("TOTAL UNION ENTITIES ACROSS VINE TERMS:", len(union))

# attachments referenced by content items
refs = {}
for k, v in union.items():
    for a in (v.get('allegati') or []):
        uu = a.get('dyn_str_association_allegati_uuid')
        nm = a.get('dyn_str_autobind_allegati_name')
        if uu:
            refs.setdefault(uu, {'name': nm, 'parents': []})
            refs[uu]['parents'].append({
                'title': v.get('title') or v.get('name'),
                'canonical': v.get('canonical'),
                'terms': sorted(v['terms'])})

# direct allegato entities
allegati = {k: v for k, v in union.items() if v.get('type') == 'rve_allegato'}
print("rve_allegato entities in union:", len(allegati))
print("attachment uuids referenced by contents:", len(refs))

json.dump({'refs': refs,
           'allegati': {k: {kk: vv for kk, vv in v.items() if kk != 'terms'}
                        for k, v in allegati.items()}},
          open('inventory.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)

print('\n--- rve_allegato with file ---')
for k, v in allegati.items():
    f = v.get('file') or {}
    print(k, '|', f.get('mimeType'), '|', f.get('length'), '|', f.get('name'),
          '| path=', (v.get('path') or '')[:110], '| terms=', sorted(v['terms']))

print('\n--- content items (non-allegato, non-image) ---')
for k, v in sorted(union.items(), key=lambda x: (x[1].get('firstPublishedAt') or '')):
    if v.get('type') in ('rve_allegato', 'rve_immagine', 'myp_tags', 'myp_tags_advanced'):
        continue
    print((v.get('firstPublishedAt') or '')[:10], '|', v.get('type'), '|',
          (v.get('title') or v.get('name') or '')[:80], '| terms=', sorted(v['terms']),
          '| n_alleg=', len(v.get('allegati') or []), '|', v.get('canonical'))
