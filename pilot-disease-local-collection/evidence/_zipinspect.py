import zipfile, io, csv, re
p=r'C:/disease-local-collection-italy/pilot-disease-local-collection/raw/F3b/ARPAV_OpenData_Dati_LR11_1994-2024.zip'
z=zipfile.ZipFile(p)
names=z.namelist()
print('ENTRIES:',len(names))
for n in names[:25]: print('  ',n, z.getinfo(n).file_size)
print('...')
# any Conegliano / Valdobbiadene
hits=[n for n in names if re.search(r'conegli|valdobb|farra|soligo',n,re.I)]
print('NAME HITS:',hits)
# show one file content
tgt=hits[0] if hits else names[0]
raw=z.read(tgt)
print('=== SAMPLE FILE:',tgt,'bytes',len(raw))
print(raw[:1500].decode('latin-1'))
