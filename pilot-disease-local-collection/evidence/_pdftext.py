import re, zlib, sys

path = sys.argv[1]
data = open(path, 'rb').read()
print('FILE BYTES:', len(data))
print('HEADER:', data[:8])
print('PAGE_OBJ_COUNT:', len(re.findall(rb'/Type\s*/Page[^s]', data)))
m = re.search(rb'/Count\s+(\d+)', data)
print('FIRST /Count:', m.group(1) if m else None)

streams = re.findall(rb'stream\r?\n(.*?)endstream', data, re.S)
print('STREAMS:', len(streams))

out = []
ok = 0
for s in streams:
    try:
        d = zlib.decompress(s)
        ok += 1
    except Exception:
        continue
    out.append(d)
print('DECOMPRESSED:', ok)

blob = b'\n'.join(out)
open(path + '.streams.bin', 'wb').write(blob)

texts = []
for m in re.finditer(rb'\((?:\\.|[^\\()])*\)', blob):
    raw = m.group(0)[1:-1]
    raw = raw.replace(b'\\(', b'(').replace(b'\\)', b')').replace(b'\\\\', b'\\')
    texts.append(raw.decode('latin-1'))
txt = ' '.join(texts)
with open(path + '.text.txt', 'w', encoding='utf-8') as f:
    f.write(txt)
print('EXTRACTED TEXT CHARS:', len(txt))
print('--- first 3000 ---')
print(txt[:3000])
