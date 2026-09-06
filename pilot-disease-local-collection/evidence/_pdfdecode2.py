import re, zlib, sys

path = sys.argv[1]
data = open(path, 'rb').read()

# font resource -> ToUnicode obj number
res2uni = {}
for m in re.finditer(rb'(\d+)\s+0\s+obj\s*<<\s*/BaseFont[^>]*?/ToUnicode\s+(\d+)\s+0\s+R', data, re.S):
    res2uni[int(m.group(1))] = int(m.group(2))
print('font obj -> tounicode obj:', res2uni)

streams = re.findall(rb'stream\r?\n(.*?)endstream', data, re.S)
dec = []
for s in streams:
    try: dec.append(zlib.decompress(s))
    except Exception: dec.append(None)

cmapsbyname = {}
for d in dec:
    if not d or b'begincmap' not in d: continue
    nm = re.search(rb'/CMapName\s*/?R?(\d+)', d)
    if not nm: continue
    num = int(nm.group(1))
    mp = {}
    for m in re.finditer(rb'<([0-9a-fA-F]+)>\s*<([0-9a-fA-F]+)>\s*<([0-9a-fA-F]+)>', d):
        lo=int(m.group(1),16); hi=int(m.group(2),16); dst=int(m.group(3),16)
        for k in range(lo,hi+1): mp[k]=chr(dst+(k-lo))
    cmapsbyname[num]=mp
print('cmap objs:', {k:len(v) for k,v in cmapsbyname.items()})

# resource name /R8 -> font obj 8 (same number per the resource dicts observed)
fontres = {}
for fobj, uobj in res2uni.items():
    fontres['R%d' % fobj] = cmapsbyname.get(uobj, {})
print('resource -> cmap size:', {k:len(v) for k,v in fontres.items()})

def unescape(b):
    out=bytearray(); i=0
    mp={0x6e:10,0x72:13,0x74:9,0x62:8,0x66:12,0x28:40,0x29:41,0x5c:92}
    while i<len(b):
        c=b[i]
        if c==0x5c and i+1<len(b):
            n=b[i+1]
            if n in mp: out.append(mp[n]); i+=2; continue
            if 0x30<=n<=0x37:
                j=i+1; o=b''
                while j<len(b) and 0x30<=b[j]<=0x37 and len(o)<3:
                    o+=bytes([b[j]]); j+=1
                out.append(int(o,8)&0xFF); i=j; continue
            out.append(n); i+=2; continue
        out.append(c); i+=1
    return bytes(out)

content=[d for d in dec if d and b'Tf' in d and (b'Tj' in d or b'TJ' in d)]
tok=re.compile(rb'/([A-Za-z0-9_.+-]+)\s+[\d.]+\s+Tf|\((?:\\.|[^\\()])*\)|(-?[\d.]+)\s+(-?[\d.]+)\s+(?:Td|TD)|\bT\*|\bTJ|\bTj|\bBT|\bET', re.S)

pages=[]
for cs in content:
    cur=None; parts=[]
    for m in tok.finditer(cs):
        s=m.group(0)
        if s.endswith(b'Tf'):
            cur=m.group(1).decode('latin-1')
        elif s.startswith(b'('):
            raw=unescape(s[1:-1])
            mp=fontres.get(cur)
            if mp: parts.append(''.join(mp.get(ch,'') for ch in raw))
            else: parts.append(raw.decode('latin-1'))
        elif s.endswith(b'Td') or s.endswith(b'TD') or s==b'T*':
            parts.append('\n')
    pages.append(''.join(parts))

txt='\n===PAGE===\n'.join(pages)
txt=re.sub(r'\n{3,}','\n\n',txt)
out=path+'.decoded.txt'
open(out,'w',encoding='utf-8').write(txt)
print('WROTE',out,len(txt))
print(txt[:5000])
