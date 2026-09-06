import json,re
d=json.load(open('F3b-agrometeo-datiindici.json',encoding='utf-8'))
s=json.dumps(d,ensure_ascii=False)
print('--- ALL URLS in dati-e-indici ---')
for u in sorted(set(re.findall(r'"([^"]*(?:https?://|/)[^"]{4,200})"',s))):
    if '@' in u and u.endswith(('actions','breadcrumbs','navigation','subsite','types','workflow','contextnavigation')): continue
    print('  ',u)
print()
print('--- blocks ---')
b=d.get('blocks',{})
for k,v in b.items():
    print(' ',v.get('@type'), json.dumps(v,ensure_ascii=False)[:400])
