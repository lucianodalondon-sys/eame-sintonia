import re, zlib, sys

path = sys.argv[1]
data = open(path, 'rb').read()
streams = re.findall(rb'stream\r?\n(.*?)endstream', data, re.S)
decomp = []
for s in streams:
    try:
        decomp.append(zlib.decompress(s))
    except Exception:
        decomp.append(None)

# build cmaps keyed by CMapName
cmaps = {}
for d in decomp:
    if not d or b'begincmap' not in d:
        continue
    nm = re.search(rb'/CMapName\s*/?([A-Za-z0-9_.+-]+)', d)
    if not nm:
        continue
    name = nm.group(1).decode('latin-1')
    mp = {}
    for m in re.finditer(rb'<([0-9a-fA-F]+)>\s*<([0-9a-fA-F]+)>\s*<([0-9a-fA-F]+)>', d):
        lo = int(m.group(1), 16); hi = int(m.group(2), 16); dst = int(m.group(3), 16)
        for k in range(lo, hi + 1):
            mp[k] = chr(dst + (k - lo))
    for m in re.finditer(rb'<([0-9a-fA-F]+)>\s*<([0-9a-fA-F]{4,})>(?!\s*<)', d):
        pass
    cmaps[name] = mp
print('CMAPS:', {k: len(v) for k, v in cmaps.items()})

content = [d for d in decomp if d and (b'Tf' in d and (b'Tj' in d or b'TJ' in d))]
print('CONTENT STREAMS:', len(content))

def unescape(b):
    out = bytearray(); i = 0
    while i < len(b):
        c = b[i]
        if c == 0x5c and i + 1 < len(b):
            n = b[i+1]
            mapping = {0x6e: 10, 0x72: 13, 0x74: 9, 0x62: 8, 0x66: 12, 0x28: 40, 0x29: 41, 0x5c: 92}
            if n in mapping:
                out.append(mapping[n]); i += 2; continue
            if 0x30 <= n <= 0x37:
                j = i + 1; oct_s = b''
                while j < len(b) and 0x30 <= b[j] <= 0x37 and len(oct_s) < 3:
                    oct_s += bytes([b[j]]); j += 1
                out.append(int(oct_s, 8) & 0xFF); i = j; continue
            out.append(n); i += 2; continue
        out.append(c); i += 1
    return bytes(out)

pages = []
for cs in content:
    cur = None
    buf = []
    pos = 0
    tok = re.compile(rb'/([A-Za-z0-9_.+-]+)\s+[\d.]+\s+Tf|\((?:\\.|[^\\()])*\)|<([0-9a-fA-F\s]+)>|\bTd\b|\bTD\b|\bT\*\b|\bTJ\b|\bTj\b|\bET\b', re.S)
    for m in tok.finditer(cs):
        s = m.group(0)
        if s.endswith(b'Tf'):
            cur = m.group(1).decode('latin-1')
        elif s.startswith(b'('):
            raw = unescape(s[1:-1])
            mp = cmaps.get(cur, {})
            if mp:
                buf.append(''.join(mp.get(ch, '�') for ch in raw))
            else:
                buf.append(raw.decode('latin-1'))
        elif s in (b'Td', b'TD', b'T*'):
            buf.append('\n')
    pages.append(''.join(buf))

txt = '\n<<<PAGEBREAK>>>\n'.join(pages)
outp = path + '.decoded.txt'
open(outp, 'w', encoding='utf-8').write(txt)
print('WROTE', outp, len(txt), 'chars')
print(txt[:4000])
