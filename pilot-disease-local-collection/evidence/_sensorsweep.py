import urllib.request as u, json, time, os, collections
UA={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'}
outdir=r'C:/disease-local-collection-italy/pilot-disease-local-collection/raw/F3b/sensors_60gg'
os.makedirs(outdir,exist_ok=True)
SENS={18:'TEMP Temperatura aria',19:'UMID Umidita relativa',20:'PRESS Pressione',22:'RADSOL Radiazione solare',
      23:'PREC Precipitazione',10001:'PORT Portata',20004:'BFOGL Bagnatura fogliare',20005:'LIVIDRO Livello idrometrico',
      20008:'TSUOLO Temperatura suolo',20026:'DVENTO Direzione vento',20027:'RAFF Raffica vento',
      20036:'VVENTO Velocita vento',20058:'FREAT Freatimetria',20066:'ET0 Evapotraspirazione'}
allst={}
probes=[]
for cd,label in SENS.items():
    url='https://api.arpa.veneto.it/REST/v1/meteo_60gg?coordcd=%d'%cd
    try:
        r=u.urlopen(u.Request(url,headers=UA),timeout=60); b=r.read(); st=r.status
    except Exception as e:
        probes.append((url,'ERR',str(e))); print(cd,label,'ERROR',e); continue
    open(os.path.join(outdir,'meteo_60gg_coordcd_%d.json'%cd),'wb').write(b)
    d=json.loads(b.decode('utf-8')); rows=d.get('data') or []
    probes.append((url,st,len(b),len(rows)))
    print('%-8s %-32s http=%s bytes=%-7s stations=%s'%(cd,label,st,len(b),len(rows)))
    for rw in rows:
        k=rw['codice_stazione']
        e=allst.setdefault(k,dict(nome=rw['nome_stazione'],prov=rw['provincia'],lat=rw['latitudine'],
                                  lon=rw['longitudine'],alt=rw['altitude'],codseqst=rw['codseqst'],sens=[]))
        e['sens'].append(label.split()[0])
    time.sleep(0.3)
print()
print('DISTINCT STATIONS SEEN ACROSS ALL SENSORS (last 60 days):',len(allst))
print('BY PROVINCE:',dict(collections.Counter(v['prov'] for v in allst.values())))
print()
for target in ['Conegliano','Valdobbiadene','Farra di Soligo','Follina','Vittorio','Mogliano']:
    for k,v in allst.items():
        if target.lower() in v['nome'].lower():
            print('  %-28s cod=%-5s codseqst=%-10s lat=%s lon=%s alt=%s  SENSORS(60d)=%s'%(
                v['nome'],k,v['codseqst'],v['lat'],v['lon'],v['alt'],','.join(sorted(set(v['sens'])))))
json.dump(allst,open(r'C:/disease-local-collection-italy/pilot-disease-local-collection/evidence/F3b-station-sensor-matrix.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
json.dump(probes,open(r'C:/disease-local-collection-italy/pilot-disease-local-collection/evidence/F3b-sensorsweep-log.json','w',encoding='utf-8'),indent=1)
print()
print('--- ALL TREVISO stations with their 60d sensor sets ---')
for k,v in sorted(allst.items(),key=lambda x:x[1]['nome']):
    if v['prov']=='TREVISO':
        print('  cod=%-5s %-34s alt=%-7s lat=%-12s lon=%-12s %s'%(k,v['nome'],v['alt'],v['lat'],v['lon'],','.join(sorted(set(v['sens'])))))
