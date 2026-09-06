import re, sys

for path in sys.argv[1:]:
    raw = open(path, 'rb').read()
    print("=====", path)
    i = raw.find(b'/Encrypt')
    if i < 0:
        print("  no /Encrypt")
    else:
        print("  /Encrypt ref ctx:", raw[i:i + 40].decode('latin-1', 'replace'))
    for key in [b'/Filter/Standard', b'/Filter /Standard', b'/V ', b'/R ', b'/P ', b'/Length ', b'/CF', b'/StmF', b'/EncryptMetadata']:
        j = raw.find(key)
        if j >= 0:
            print("  ", key.decode(), "->", raw[j:j + 60].decode('latin-1', 'replace').replace('\n', ' '))
    # image geometry
    dims = re.findall(rb'/Subtype\s*/Image(.{0,300}?)>>', raw, re.S)
    got = []
    for d in dims[:8]:
        w = re.search(rb'/Width\s+(\d+)', d)
        h = re.search(rb'/Height\s+(\d+)', d)
        f = re.search(rb'/Filter\s*/(\w+)', d)
        cs = re.search(rb'/ColorSpace\s*/?(\w+)', d)
        got.append((w.group(1).decode() if w else '?', h.group(1).decode() if h else '?',
                    f.group(1).decode() if f else '?', cs.group(1).decode() if cs else '?'))
    print("  first images (W,H,Filter,ColorSpace):", got)
    print()
