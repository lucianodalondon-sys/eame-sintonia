import zipfile, re, sys, json, collections
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
p=r'C:/disease-local-collection-italy/pilot-disease-local-collection/raw/F3b/ARPAV_OpenData_Dati_LR11_1994-2024.zip'
z=zipfile.ZipFile(p)
names=[n for n in z.namelist() if n.lower().endswith('.csv')]
def isval(v):
    v=v.strip()
    return v!='' and v!='>>' and re.fullmatch(r'-?\d+(?:[.,]\d+)?',v) is not None
res={}
for n in names:
    raw=z.read(n).decode('latin-1')
    first=None
    for m in re.finditer(r'^(\d{4});(.*)$',raw,re.M):
        y=int(m.group(1))
        if any(isval(v) for v in m.group(2).split(';')):
            first=y if first is None else min(first,y)
    q=re.search(r'Quota della stazione\s+(-?\d+)\s*m',raw)
    cx=re.search(r'Coordinata X\s+(\d+)',raw); cy=re.search(r'Coordinata Y\s+(\d+)',raw)
    res[n]=dict(first_year_with_real_values=first,quota=q.group(1) if q else None,
                gb_x=cx.group(1) if cx else None,gb_y=cy.group(1) if cy else None)
yrs=[v['first_year_with_real_values'] for v in res.values() if v['first_year_with_real_values']]
print('CSV files:',len(names),'| with any real value:',len(yrs),'| none:',len(names)-len(yrs))
print('EARLIEST:',min(yrs),' LATEST:',max(yrs))
print('DISTRIBUTION:',dict(sorted(collections.Counter(yrs).items())))
print()
for k in ['Conegliano.csv','Valdobbiadene_-_Bigolino.csv','Farra_di_Soligo.csv','Follina.csv','Vittorio_Veneto.csv',
          'Volpago_del_Montello.csv','Maser.csv','Castelfranco_Veneto.csv','Breda_di_Piave_-_Via_Bovon.csv',
          'Gaiarine.csv','Oderzo.csv','Roncade.csv','Villorba.csv','Vazzola_-_Tezze.csv','Zero_Branco.csv',
          'Ponte_di_Piave.csv','Mogliano_Veneto.csv','Treviso.csv']:
    print('  %-34s %s'%(k,res.get(k,'NOT_IN_ZIP')))
print()
print('STATIONS WITH FIRST REAL YEAR == 1994:',sum(1 for v in yrs if v==1994))
json.dump(res,open(r'C:/disease-local-collection-italy/pilot-disease-local-collection/evidence/F3b-zip-station-firstyear.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
