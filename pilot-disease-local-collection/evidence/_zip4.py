import zipfile, re, sys, json
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
p=r'C:/disease-local-collection-italy/pilot-disease-local-collection/raw/F3b/ARPAV_OpenData_Dati_LR11_1994-2024.zip'
z=zipfile.ZipFile(p)
names=[n for n in z.namelist() if n.lower().endswith('.csv')]
print('CSV STATION FILES:',len(names))
res={}
for n in names:
    raw=z.read(n).decode('latin-1')
    # first data row: year;value... with at least one non-empty numeric value
    first=None
    for m in re.finditer(r'^(\d{4});(.*)$',raw,re.M):
        y=int(m.group(1)); vals=[v for v in m.group(2).split(';') if v.strip()!='']
        if vals:
            first=y if first is None else min(first,y)
    q=re.search(r'Quota della stazione\s+(-?\d+)\s*m',raw)
    cx=re.search(r'Coordinata X\s+(\d+)',raw); cy=re.search(r'Coordinata Y\s+(\d+)',raw)
    res[n]=dict(first_year_with_values=first, quota=q.group(1) if q else None,
                gb_x=cx.group(1) if cx else None, gb_y=cy.group(1) if cy else None)
yrs=[v['first_year_with_values'] for v in res.values() if v['first_year_with_values']]
print('EARLIEST first-data-year across all station CSVs:',min(yrs),'| latest:',max(yrs))
import collections
print('distribution:',dict(sorted(collections.Counter(yrs).items())))
print()
for k in ['Conegliano.csv','Valdobbiadene_-_Bigolino.csv','Farra_di_Soligo.csv','Follina.csv','Vittorio_Veneto.csv','Volpago_del_Montello.csv','Maser.csv','Castelfranco_Veneto.csv']:
    if k in res: print('  %-32s %s'%(k,res[k]))
    else: print('  %-32s NOT_IN_ZIP'%k)
print()
print('stations with first year 1994:',sum(1 for v in res.values() if v['first_year_with_values']==1994))
json.dump(res,open(r'C:/disease-local-collection-italy/pilot-disease-local-collection/evidence/F3b-zip-station-firstyear.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
# check bagnatura present anywhere
allparams=set()
for n in names[:30]:
    raw=z.read(n).decode('latin-1')
    for m in re.finditer(r'^Parametro (.+?);',raw,re.M): allparams.add(m.group(1))
print()
print('PARAMETERS PRESENT IN ZIP (sample of 30 files):')
for a in sorted(allparams): print('   -',a)
