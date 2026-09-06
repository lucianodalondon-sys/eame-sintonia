import json
d=json.load(open('F3b-agrometeo60giorni.json',encoding='utf-8'))
for k,v in d.get('blocks',{}).items():
    t=v.get('@type')
    s=json.dumps(v,ensure_ascii=False)
    print('---',t,len(s))
    if t not in ('title','slate','richtext'):
        print(s[:4000])
