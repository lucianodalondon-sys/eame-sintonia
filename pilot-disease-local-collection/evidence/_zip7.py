import zipfile, re, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
p=r'C:/disease-local-collection-italy/pilot-disease-local-collection/raw/F3b/ARPAV_OpenData_Dati_LR11_1994-2024.zip'
z=zipfile.ZipFile(p)
raw=z.read('Breda_di_Piave_-_Via_Bovon.csv').decode('latin-1')
blocks=raw.split('ARPAV Centro Meteorologico di Teolo')
def isval(v):
    v=v.strip()
    return v!='' and v!='>>' and re.fullmatch(r'-?\d+(?:[.,]\d+)?',v) is not None
for i,b in enumerate(blocks):
    par=re.search(r'Parametro (.+?);',b)
    if not par:
        print(i,'NO PARAM BLOCK, len',len(b), repr(b[:120]))
        continue
    rows=re.findall(r'^(\d{4});(.*)$',b,re.M)
    first=None
    for y,v in rows:
        if any(isval(x) for x in v.split(';')):
            first=int(y); break
    print(i,'|',par.group(1)[:60],'| rows',len(rows),'| first real year:',first)
    if first==1994:
        for y,v in rows[:3]: print('      ',y,'|',v[:100])
