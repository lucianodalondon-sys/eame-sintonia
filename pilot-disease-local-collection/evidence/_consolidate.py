import json, csv, sys, re
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
EV=r'C:/disease-local-collection-italy/pilot-disease-local-collection/evidence/'
RAW=r'C:/disease-local-collection-italy/pilot-disease-local-collection/raw/F3b/'

elenco=json.load(open(EV+'F3b-elenco-stazioni-parsed.json',encoding='utf-8'))
matrix=json.load(open(EV+'F3b-station-sensor-matrix.json',encoding='utf-8'))
bfy=json.load(open(EV+'F3b-bfogl-firstyear.json',encoding='utf-8'))

# bfogl first year keyed by codice_stazione
bf={}
for k,v in bfy.items():
    m=re.match(r"\((\d+), '(.*?)', '(.*?)', '(.*?)'\)",k)
    if m: bf[m.group(1)]=dict(firstyear=v, comune=m.group(4))

rows=[]
for e in elenco:
    cod=e['codice_sirav']
    api=matrix.get(str(cod)) if cod else None
    b=bf.get(str(cod)) if cod else None
    rows.append(dict(
        codice_sirav=cod or '',
        tipo_masterplan=e['tipo'],
        nome_masterplan=e['nome'],
        quota_m_masterplan=e['quota_m'] if e['quota_m'] is not None else '',
        provincia_sigla=e['prov'],
        nome_api=api['nome'] if api else '',
        codseqst_api=api['codseqst'] if api else '',
        latitudine_api=api['lat'] if api else '',
        longitudine_api=api['lon'] if api else '',
        altitudine_api=api['alt'] if api else '',
        comune_api=b['comune'] if b else '',
        sensori_ultimi60gg=','.join(sorted(set(api['sens']))) if api else '',
        bagnatura_fogliare='YES' if api and 'BFOGL' in api['sens'] else ('NO' if api else 'NOT_IN_60d_API'),
        bfogl_primo_anno_endpoint=b['firstyear'] if b else '',
    ))
out=RAW+'ARPAV_station_catalogue_MERGED.csv'
with open(out,'w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0].keys()),delimiter=';')
    w.writeheader(); w.writerows(rows)
print('WROTE',out,'rows',len(rows))

matched=sum(1 for r in rows if r['codseqst_api'])
print('MasterPlan rows matched to live API station:',matched,'/',len(rows))
tv=[r for r in rows if r['provincia_sigla']=='TV']
print('TV rows:',len(tv),'| TV with BFOGL:',sum(1 for r in tv if r['bagnatura_fogliare']=='YES'))
print('ALL rows with BFOGL=YES:',sum(1 for r in rows if r['bagnatura_fogliare']=='YES'))

# also dump BFOGL-only catalogue
bfrows=[r for r in rows if r['bagnatura_fogliare']=='YES']
out2=RAW+'ARPAV_leaf_wetness_BFOGL_stations.csv'
with open(out2,'w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0].keys()),delimiter=';')
    w.writeheader(); w.writerows(bfrows)
print('WROTE',out2,'rows',len(bfrows))

# altitude discrepancies
disc=[r for r in rows if r['altitudine_api']!='' and r['quota_m_masterplan']!='' and float(r['altitudine_api'])!=float(r['quota_m_masterplan'])]
print('ALTITUDE DISCREPANCIES MasterPlan vs API:',len(disc))
for r in disc[:20]:
    print('   %-6s %-38s masterplan=%s api=%s'%(r['codice_sirav'],r['nome_masterplan'],r['quota_m_masterplan'],r['altitudine_api']))
