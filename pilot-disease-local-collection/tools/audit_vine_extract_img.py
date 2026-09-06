import re, sys, os, zlib

def extract(path, outdir):
    d = open(path, 'rb').read()
    base = os.path.basename(path)
    # find image xobject dicts
    for m in re.finditer(rb'<<([^<>]|<<[^>]*>>)*?/Subtype\s*/Image.*?>>\s*stream\r?\n', d, re.S):
        dict_txt = d[m.start():m.end()]
        print("  IMAGE DICT:", dict_txt[:400])
        start = m.end()
        end = d.find(b'endstream', start)
        blob = d[start:end]
        # trim trailing EOL
        while blob[-1:] in (b'\n', b'\r'):
            blob = blob[:-1]
        out = os.path.join(outdir, base + '.img.jpg')
        open(out, 'wb').write(blob)
        print("  wrote %s  (%d bytes)  jpeg_magic=%s" % (out, len(blob), blob[:3] == b'\xff\xd8\xff'))
    # content stream: find placement operators
    for m in re.finditer(rb'/(Im\d+|Xi?\d*)\s+Do', d):
        pass

def contentstreams(path):
    d = open(path, 'rb').read()
    txts = []
    for m in re.finditer(rb'stream\r?\n', d):
        start = m.end()
        end = d.find(b'endstream', start)
        blob = d[start:end]
        try:
            t = zlib.decompress(blob)
        except Exception:
            continue
        if b' Do' in t or b'cm' in t or b'Tj' in t or b'TJ' in t:
            txts.append(t)
    return txts

for p in sys.argv[1:]:
    print("=" * 70)
    print(os.path.basename(p))
    extract(p, os.path.dirname(os.path.abspath(__file__)))
    for t in contentstreams(p):
        s = t.decode('latin-1')
        # print lines mentioning image placement
        for line in s.split('\n'):
            if ' Do' in line or ' cm' in line:
                print("  CONTENT:", line.strip()[:200])
        print("  --- content stream length %d bytes ---" % len(t))
