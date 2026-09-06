import zipfile, re, sys, json, collections
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
p=r'C:/disease-local-collection-italy/pilot-disease-local-collection/raw/F3b/ARPAV_OpenData_Dati_LR11_1994-2024.zip'
z=zipfile.ZipFile(p)
names=[n for n in z.namelist() if n.lower().endswith('.csv')]

def isnum(v):
    v=v.strip()
    return v!='' and v!='>>' and re.fullmatch(r'-?\d+(?:[.,]\d+)?',v) is not None

def blocks(raw):
    # split into (param, rows) using 'Parametro X' markers
    idx=[(m.start(),m.group(1)) for m in re.finditer(r'^Parametro (.+?);',raw,re.M)]
    out=[]
    for i,(s,par) in enumerate(idx):
        e=idx[i+1][0] if i+1<len(idx) else len(raw)
        seg=raw[s:e]
        rows=re.findall(r'^(\d{4});(.*)$',seg,re.M)
        out.append((par,rows))
    return out

res={}
for n in names:
    raw=z.read(n).decode('latin-1')
    bs=blocks(raw)
    per={}
    for par,rows in bs:
        first=None
        for y,v in rows:
            if any(isnum(x) for x in v.split(';')):
                first=int(y); break
        if first is not None:
            per[par]=min(per.get(par,9999),first)
    prec=per.get('Precipitazione (mm) somma')
    res[n]=dict(first_year_precip=prec, first_year_any=min(per.values()) if per else None, params=len(per))
print('CSV files:',len(names))
prec=[v['first_year_precip'] for v in res.values() if v['first_year_precip']]
print('with precipitation block:',len(prec))
print('DISTRIBUTION first_year_precip:',dict(sorted(collections.Counter(prec).items())))
print('EARLIEST:',min(prec),'LATEST:',max(prec))
print()
for k in ['Conegliano.csv','Valdobbiadene_-_Bigolino.csv','Farra_di_Soligo.csv','Follina.csv','Vittorio_Veneto.csv',
          'Breda_di_Piave_-_Via_Bovon.csv','Volpago_del_Montello.csv','Maser.csv','Castelfranco_Veneto.csv',
          'Gaiarine.csv','Oderzo.csv','Roncade.csv','Villorba.csv','Vazzola_-_Tezze.csv','Zero_Branco.csv',
          'Ponte_di_Piave.csv','Mogliano_Veneto.csv','Treviso.csv']:
    print('  %-34s %s'%(k,res.get(k,'NOT_IN_ZIP')))
json.dump(res,open(r'C:/disease-local-collection-italy/pilot-disease-local-collection/evidence/F3b-zip-station-firstyear.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
