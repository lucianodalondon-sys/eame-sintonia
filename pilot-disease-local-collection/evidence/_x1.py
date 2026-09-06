import json,re,sys
for f in ['F3b-le-reti-di-misura.json','F3b-agrometeo-monitoraggio.json','F3b-agrometeo-datiindici.json']:
    d=json.load(open(f,encoding='utf-8'))
    print('=====',f,'| title:',d.get('title'))
    s=json.dumps(d,ensure_ascii=False)
    for m in re.finditer(r'"plaintext"\s*:\s*"((?:[^"\\]|\\.)*)"',s):
        t=json.loads('"'+m.group(1)+'"')
        t=' '.join(t.split())
        if len(t)>25: print('   TXT:',t[:500])
    seen=set()
    for m in re.finditer(r'"(?:url|href|@id)"\s*:\s*"([^"]+)"',s):
        u=m.group(1)
        if u in seen: continue
        seen.add(u)
        if any(k in u.lower() for k in ['.pdf','.csv','.xls','.zip','resolveuid','stazion','rete','misura']):
            print('   LNK:',u)
