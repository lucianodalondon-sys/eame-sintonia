import json,re
for f in ['F3b-search-anagrafica-title.json','F3b-search-title-stazioni.json']:
    d=json.load(open(f,encoding='utf-8'))
    print('=====',f,'total',d.get('items_total'))
    for it in d['items']:
        t=it.get('title','') or ''
        u=it.get('@id','')
        if f.endswith('stazioni.json'):
            if not any(k in (t+u).lower() for k in ['meteo','anagraf','agro','telemisura','rete','rilevamento']): continue
        print('  ',it.get('@type'),'|',t[:75],'|',u)

d=json.load(open('F3b-geoportale.json',encoding='utf-8'))
s=json.dumps(d,ensure_ascii=False)
print()
print('===== GEOPORTALE title:',d.get('title'))
for u in sorted(set(re.findall(r'https?://[^"\\ ]{10,160}',s))):
    if 'arpa.veneto.it/api/dati-ambientali/geoportale/@' in u: continue
    print('  URL:',u)
for m in re.finditer(r'"plaintext"\s*:\s*"((?:[^"\\]|\\.)*)"',s):
    t=' '.join(json.loads('"'+m.group(1)+'"').split())
    if len(t)>30: print('  TXT:',t[:300])
