import re, json, collections
p=r'C:/disease-local-collection-italy/pilot-disease-local-collection/raw/F3b/ARPAV_MasterPlan_Allegato1_Elenco_Stazioni.pdf.decoded.txt'
t=open(p,encoding='utf-8').read()
pages=t.split('===PAGE===')
HDR=re.compile(r'ARPAV MasterPlan rete di monitoraggio idro-nivo-agro-mete o ALLEGATO 1 . ELENCO DELLE STAZIONI \d+ dicembre 2024 codice SIRAV tipo nome stazione quota m s\.l\.m\. provincia')
body=[]
for pg in pages:
    f=' '.join(pg.split())
    f=HDR.sub('',f).strip()
    body.append(f)
flat=' '.join(body)
TIPI=r'(?:BSL IDRO-Q|NIVOIDROMET|IDROMET-Q|NIVOMET|IDROMET|IDRO-Q|METEO|AGRO|NIVO|IDRO)'
pat=re.compile(r'(?:(\d{1,4})\s+)?('+TIPI+r')\s+(.+?)\s+(?:(-?\d{1,4}(?:,\d+)?)\s+)?(BL|TV|VI|VR|PD|RO|VE|UD)(?=\s|$)')
rows=[]
for m in pat.finditer(flat):
    rows.append(dict(codice_sirav=m.group(1), tipo=m.group(2), nome=m.group(3).strip(),
                     quota_m=m.group(4), prov=m.group(5)))
print('TOTAL ROWS PARSED:',len(rows))
print('rows WITHOUT code:',sum(1 for r in rows if r['codice_sirav'] is None))
print('rows WITHOUT quota:',sum(1 for r in rows if r['quota_m'] is None))
codes=[r['codice_sirav'] for r in rows if r['codice_sirav']]
dup=[c for c,n in collections.Counter(codes).items() if n>1]
print('codes:',len(codes),'unique:',len(set(codes)),'dups:',dup)
print('BY TIPO:',dict(collections.Counter(r['tipo'] for r in rows)))
print('BY PROV:',dict(collections.Counter(r['prov'] for r in rows)))
tv=[r for r in rows if r['prov']=='TV']
print()
print('TREVISO TOTAL:',len(tv),'| by tipo:',dict(collections.Counter(r['tipo'] for r in tv)))
for r in tv:
    print('  SIRAV %-5s %-12s %-45s %6s m' % (r['codice_sirav'],r['tipo'],r['nome'],r['quota_m']))
json.dump(rows,open(r'C:/disease-local-collection-italy/pilot-disease-local-collection/evidence/F3b-elenco-stazioni-parsed.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
