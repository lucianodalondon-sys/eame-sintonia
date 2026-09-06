import re, sys, zlib

for path in sys.argv[1:]:
    raw = open(path, 'rb').read()
    print("=====", path, "| bytes:", len(raw))
    print("  header:", raw[:8].decode('latin-1', 'replace'))
    print("  /Type/Page count:", len(re.findall(rb'/Type\s*/Page[^s]', raw)))
    print("  /Image XObjects:", len(re.findall(rb'/Subtype\s*/Image', raw)))
    print("  /Font objects:", len(re.findall(rb'/Type\s*/Font', raw)))
    print("  ToUnicode CMaps:", len(re.findall(rb'/ToUnicode', raw)))
    print("  /Encrypt present:", b'/Encrypt' in raw)
    # try to read metadata / Info strings and object streams for readable words
    words = set()
    for m in re.finditer(rb'stream\r?\n', raw):
        s = m.end()
        e = raw.find(b'endstream', s)
        if e < 0:
            continue
        try:
            d = zlib.decompress(raw[s:e])
        except Exception:
            continue
        for w in re.findall(rb'[A-Za-z\xc0-\xff]{5,}', d):
            words.add(w.decode('latin-1', 'replace'))
    interesting = sorted(w for w in words if re.search(
        r'perono|oidio|botri|flavesc|scapho|tignol|vite|vigne|grappol|bollett|fitosan|veneto|regione|infezion|trattam|plasmo|erysip|BBCH|giallum|lobesia',
        w, re.I))
    print("  readable domain words found in streams:", interesting[:40] if interesting else "NONE")
    print("  total distinct >=5-letter tokens in streams:", len(words))
    print()
