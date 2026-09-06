import re, zlib, sys, collections
path = sys.argv[1]
data = open(path,'rb').read()
streams = re.findall(rb'stream\r?\n(.*?)endstream', data, re.S)
dec=[]
for s in streams:
    try: dec.append(zlib.decompress(s))
    except Exception: dec.append(None)
print('streams',len(streams),'ok',sum(1 for d in dec if d))
for i,d in enumerate(dec):
    if d is None:
        print(' stream',i,'FAILED len',len(streams[i]), streams[i][:40])
tfs=collections.Counter()
for d in dec:
    if not d: continue
    for m in re.finditer(rb'/([A-Za-z0-9_.+-]+)\s+[\d.]+\s+Tf', d):
        tfs[m.group(1).decode('latin-1')]+=1
print('Tf names:',dict(tfs))
# font objects in raw pdf
print('Font resource dicts:')
for m in re.finditer(rb'/Font\s*<<(.{0,600}?)>>', data, re.S):
    print('  ', m.group(1)[:400].decode('latin-1').replace('\n',' '))
print('ToUnicode refs:', re.findall(rb'/ToUnicode\s+(\d+)\s+0\s+R', data)[:20])
print('BaseFont:', set(re.findall(rb'/BaseFont\s*/([A-Za-z0-9_.+-]+)', data)))
# cmap names
for d in dec:
    if d and b'begincmap' in d:
        nm=re.search(rb'/CMapName\s*/?([A-Za-z0-9_.+-]+)',d)
        nbf=len(re.findall(rb'beginbfchar',d)); nbr=len(re.findall(rb'beginbfrange',d))
        print('cmap',nm.group(1) if nm else '?','bfchar',nbf,'bfrange',nbr,'len',len(d))
