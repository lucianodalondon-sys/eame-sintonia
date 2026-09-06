import zipfile, re
p=r'C:/disease-local-collection-italy/pilot-disease-local-collection/raw/F3b/ARPAV_OpenData_Dati_LR11_1994-2024.zip'
z=zipfile.ZipFile(p)
print('===== AAA-LEGGIMI.txt =====')
print(z.read('AAA-LEGGIMI.txt').decode('latin-1')[:6000])
print()
for f in ['Conegliano.csv','Valdobbiadene_-_Bigolino.csv','Farra_di_Soligo.csv']:
    raw=z.read(f).decode('latin-1')
    print('=====',f)
    for m in re.finditer(r'^(Stazione|Coordinata|Quota|Parametro|Valori dal).*$',raw,re.M):
        print('   ',m.group(0).rstrip(';'))
