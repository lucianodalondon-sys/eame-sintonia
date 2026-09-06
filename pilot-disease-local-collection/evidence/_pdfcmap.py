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

cmaps = [d for d in decomp if d and b'beginbfchar' in d or (d and b'beginbfrange' in d)]
print('CMAP STREAMS FOUND:', len(cmaps))
for i, c in enumerate(cmaps):
    print('--- cmap', i, 'len', len(c))
    print(c[:600].decode('latin-1'))
