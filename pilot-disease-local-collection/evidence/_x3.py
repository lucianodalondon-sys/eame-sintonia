import json,re
d=json.load(open('F3b-agrometeo-datiindici.json',encoding='utf-8'))
for k,v in d.get('blocks',{}).items():
    if v.get('@type')=='slate' and 'mappa' in json.dumps(v,ensure_ascii=False):
        print(json.dumps(v,ensure_ascii=False,indent=1)[:3000])
