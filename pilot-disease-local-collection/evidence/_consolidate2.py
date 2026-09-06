import json, csv, sys, re, unicodedata
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
EV=r'C:/disease-local-collection-italy/pilot-disease-local-collection/evidence/'
RAW=r'C:/disease-local-collection-italy/pilot-disease-local-collection/raw/F3b/'
elenco=json.load(open(EV+'F3b-elenco-stazioni-parsed.json',encoding='utf-8'))
matrix=json.load(open(EV+'F3b-station-sensor-matrix.json',encoding='utf-8'))
bfy=json.load(open(EV+'F3b-bfogl-firstyear.json',encoding='utf-8'))
PROV={'TREVISO':'TV','BELLUNO':'BL','VICENZA':'VI','VERONA':'VR','PADOVA':'PD','ROVIGO':'RO','VENEZIA':'VE','UDINE':'UD'}

def norm(s):
    s=unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower()
    return re.sub(r'[^a-z0-9]','',s)

bf={}
for k,v in bfy.items():
    m=re.match(r"\((\d+), '(.*?)', '(.*?)', '(.*?)'\)",k)
    if m: bf[m.group(1)]=dict(firstyear=v,comune=m.group(4))

# 1) PURE MasterPlan catalogue
f1=RAW+'ARPAV_MasterPlan_Allegato1_ElencoStazioni_2024-12-01.csv'
with open(f1,'w',newline='',encoding='utf-8') as f:
    w=csv.writer(f,delimiter=';'); w.writerow(['codice_SIRAV','tipo','nome_stazione','quota_m_slm','provincia'])
    for e in elenco: w.writerow([e['codice_sirav'] or '',e['tipo'],e['nome'],e['quota_m'] if e['quota_m'] is not None else '',e['prov']])
print('WROTE',f1,'rows',len(elenco))

# 2) PURE live API catalogue
f2=RAW+'ARPAV_API_live_stations_sensors_60d.csv'
apirows=[]
for cod,v in matrix.items():
    b=bf.get(cod)
    apirows.append(dict(codice_stazione=cod,codseqst=v['codseqst'],nome_stazione=v['nome'],
        comune=b['comune'] if b else '',provincia=v['prov'],prov_sigla=PROV.get(v['prov'],''),
        latitudine_WGS84=v['lat'],longitudine_WGS84=v['lon'],altitudine_m=v['alt'],
        sensori_ultimi_60_giorni=','.join(sorted(set(v['sens']))),
        bagnatura_fogliare='YES' if 'BFOGL' in v['sens'] else 'NO',
        bfogl_primo_anno_disponibile_endpoint=b['firstyear'] if b else ''))
apirows.sort(key=lambda r:(r['provincia'],r['nome_stazione']))
with open(f2,'w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=list(apirows[0].keys()),delimiter=';'); w.writeheader(); w.writerows(apirows)
print('WROTE',f2,'rows',len(apirows))
print('  BFOGL=YES in live API catalogue:',sum(1 for r in apirows if r['bagnatura_fogliare']=='YES'))
print('  TREVISO rows:',sum(1 for r in apirows if r['provincia']=='TREVISO'),
      '| TV BFOGL:',sum(1 for r in apirows if r['provincia']=='TREVISO' and r['bagnatura_fogliare']=='YES'))

# 3) CONSERVATIVE join: require same code AND same province AND fuzzy name match
joined=0; altdisc=[]
for e in elenco:
    cod=e['codice_sirav']
    if not cod: continue
    v=matrix.get(cod)
    if not v: continue
    if PROV.get(v['prov'])!=e['prov']: continue
    a,b2=norm(e['nome']),norm(v['nome'])
    if not (a==b2 or a.startswith(b2[:8]) or b2.startswith(a[:8])): continue
    joined+=1
    try:
        if float(v['alt'])!=float(str(e['quota_m']).replace(',','.')): altdisc.append((cod,e['nome'],e['quota_m'],v['alt']))
    except Exception: pass
print()
print('CONSERVATIVE JOIN (code+province+name):',joined,'of',len(elenco),'MasterPlan rows')
print('ALTITUDE DISCREPANCIES among joined:',len(altdisc))
for r in altdisc: print('   SIRAV %-5s %-38s masterplan=%s api=%s'%r)
