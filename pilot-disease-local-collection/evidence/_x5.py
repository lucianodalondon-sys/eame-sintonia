import json, collections
d=json.load(open('F3b-api-meteo60gg-bfogl-20004.json',encoding='utf-8'))
rows=d['data']
print('success:',d.get('success'),'N rows:',len(rows))
print('keys:',sorted(rows[0].keys()))
prov=collections.Counter(r['provincia'] for r in rows)
print('BY PROVINCE:',dict(prov))
print()
print('--- TREVISO province BFOGL stations ---')
for r in sorted(rows,key=lambda x:x['nome_stazione']):
    if r['provincia']=='TREVISO':
        print(f"  codice_stazione={r['codice_stazione']} codseqst={r['codseqst']} {r['nome_stazione']!r} lat={r['latitudine']} lon={r['longitudine']} alt={r['altitude']}")
print()
print('--- name match Conegliano / Valdobbiadene / Vittorio / Follina / Farra ---')
for r in rows:
    n=r['nome_stazione'].lower()
    if any(k in n for k in ['conegli','valdobb','vittorio','follina','farra','pieve di soligo','soligo','refrontolo','miane','cison','sernaglia','susegana','col san martino']):
        print('  ',r)
