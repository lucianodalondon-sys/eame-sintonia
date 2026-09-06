import json
hits=[]
for f in ['F3b-gaia-layers-list.json','F3b-gaia-layers-2.json','F3b-gaia-layers-3.json']:
    d=json.load(open(f,encoding='utf-8'))
    for o in d['objects']:
        t=((o.get('title') or '')+' '+(o.get('alternate') or '')+' '+(o.get('abstract') or '')).lower()
        if any(k in t for k in ['meteo','agromet','bagnatur','telemis','pluviom','termometr','anemom','stazioni meteo','clima']):
            hits.append((o.get('alternate'),o.get('title'),(o.get('abstract') or '')[:150]))
print('HITS:',len(hits))
for a,t,ab in hits: print(' -',a,'|',t,'|',ab.replace('\n',' '))
