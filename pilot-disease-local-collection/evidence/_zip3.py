import zipfile, re, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
p=r'C:/disease-local-collection-italy/pilot-disease-local-collection/raw/F3b/ARPAV_OpenData_Dati_LR11_1994-2024.zip'
z=zipfile.ZipFile(p)
txt=z.read('AAA-LEGGIMI.txt').decode('latin-1')
print('===== AAA-LEGGIMI.txt (%d chars) ====='%len(txt))
print(txt[:7000])
print()
for f in ['Conegliano.csv','Valdobbiadene_-_Bigolino.csv','Farra_di_Soligo.csv']:
    raw=z.read(f).decode('latin-1')
    print('=====',f)
    for m in re.finditer(r'^(Stazione|Coordinata|Quota|Parametro|Valori dal).*$',raw,re.M):
        print('   ',m.group(0).rstrip(';'))
