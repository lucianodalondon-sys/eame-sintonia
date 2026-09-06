import zipfile, re, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
p=r'C:/disease-local-collection-italy/pilot-disease-local-collection/raw/F3b/ARPAV_OpenData_Dati_LR11_1994-2024.zip'
z=zipfile.ZipFile(p)
for n in ['Breda_di_Piave_-_Via_Bovon.csv','Follina.csv','Conegliano.csv']:
    raw=z.read(n).decode('latin-1')
    print('##########',n)
    blocks=raw.split('ARPAV Centro Meteorologico di Teolo')
    print('  blocks:',len(blocks))
    b=None
    for bl in blocks:
        if 'Precipitazione (mm) somma' in bl: b=bl; break
    if b is None: b=blocks[1] if len(blocks)>1 else raw
    par=re.search(r'Parametro (.+?);',b)
    print('  first block param:',par.group(1) if par else '?')
    rows=re.findall(r'^(\d{4});(.*)$',b,re.M)
    print('  rows:',len(rows))
    for y,v in rows[:12]:
        print('   ',y,'|',v[:80])
