import urllib.request as u, json, time, os, collections
UA={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'}
outdir=r'C:/disease-local-collection-italy/pilot-disease-local-collection/raw/F3b/bfogl_by_year'
os.makedirs(outdir,exist_ok=True)
log=[]
firstyear={}
peryear={}
for y in range(2010,2027):
    url='https://api.arpa.veneto.it/REST/v1/meteo_storici?coordcd=20004&anno=%d'%y
    try:
        r=u.urlopen(u.Request(url,headers=UA),timeout=60)
        b=r.read(); st=r.status
    except Exception as e:
        log.append((url,'ERR',str(e))); print(y,'ERROR',e); continue
    open(os.path.join(outdir,'meteo_storici_20004_%d.json'%y),'wb').write(b)
    d=json.loads(b.decode('utf-8'))
    rows=d.get('data') or []
    peryear[y]=len(rows)
    log.append((url,st,len(b),len(rows)))
    for rw in rows:
        k=(rw['codice_stazione'],rw['nome_stazione'],rw['provincia'],rw.get('comune'))
        if k not in firstyear: firstyear[k]=y
    print(y,'http',st,'bytes',len(b),'stations',len(rows))
    time.sleep(0.3)
print()
print('STATIONS PER YEAR:',peryear)
print('DISTINCT STATIONS EVER (2010-2026):',len(firstyear))
print()
print('EARLIEST YEAR WITH BFOGL DATA (per this endpoint), TREVISO:')
for k,v in sorted(firstyear.items(), key=lambda x:(x[0][2],x[0][1])):
    if k[2]=='TREVISO':
        print('  cod=%-5s %-32s comune=%-24s firstyear=%s'%(k[0],k[1],k[3],v))
print()
print('EARLIEST YEAR overall distribution:',dict(collections.Counter(firstyear.values())))
json.dump({str(k):v for k,v in firstyear.items()},open(r'C:/disease-local-collection-italy/pilot-disease-local-collection/evidence/F3b-bfogl-firstyear.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
json.dump(log,open(r'C:/disease-local-collection-italy/pilot-disease-local-collection/evidence/F3b-yearsweep-log.json','w',encoding='utf-8'),indent=1)
