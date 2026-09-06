import json, collections
for f in ['F3b-api-storici-20004-2010.json','F3b-api-meteogrammi.json']:
    d=json.load(open(f,encoding='utf-8'))
    rows=d.get('data') or []
    print('=====',f,'success:',d.get('success'),'N:',len(rows))
    if rows:
        print('  keys:',sorted(rows[0].keys()))
        print('  sample:',json.dumps(rows[0],ensure_ascii=False)[:400])
        if 'provincia' in rows[0]:
            print('  by prov:',dict(collections.Counter(r['provincia'] for r in rows)))
