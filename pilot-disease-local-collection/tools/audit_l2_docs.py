import json, os, hashlib, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def P(*a): return os.path.join(ROOT, *a)

def rd(p):
    out = []
    for ln in open(P(p), encoding='utf-8'):
        ln = ln.strip()
        if ln:
            out.append(json.loads(ln))
    return out

def magic(path):
    try:
        with open(path, 'rb') as f:
            h = f.read(8)
    except OSError:
        return 'MISSING'
    if h.startswith(b'%PDF'): return 'PDF'
    if h[:1] in (b'<',) or h.lower().startswith(b'<!doc') or h.lower().startswith(b'<html'): return 'HTML'
    if h.startswith(b'PK'): return 'ZIP/OOXML'
    return 'OTHER:' + repr(h[:6])

for label, inv, man, rawdir in [
    ("MONTHLY", 'manifests/arpav-monthly-inventory.jsonl', 'manifests/arpav-monthly-manifest.jsonl', 'raw/F7-arpav-bollettino-mese'),
    ("DOCS", 'manifests/arpav-docs-inventory.jsonl', 'manifests/arpav-docs-manifest.jsonl', 'raw/F8-arpav-agrometeo-docs'),
]:
    I = rd(inv); M = rd(man)
    print("=" * 70)
    print(label)
    print("  INVENTORIED (discovered) lines:", len(I))
    print("  MANIFEST (preserved) lines:", len(M))
    d = P(rawdir)
    files = sorted(os.listdir(d)) if os.path.isdir(d) else []
    print("  files physically in", rawdir, ":", len(files))
    # magic byte census over everything on disk
    cen = collections.Counter(magic(os.path.join(d, f)) for f in files)
    print("  magic-byte census on disk:", dict(cen))
    # manifest rows -> file present? sha matches? magic ok?
    ok = shabad = miss = notpdf = 0
    badlist = []
    for r in M:
        p = P(r['raw_path'])
        if not os.path.exists(p):
            miss += 1; badlist.append(('MISSING', r['raw_path'])); continue
        m = magic(p)
        if m != 'PDF':
            notpdf += 1; badlist.append((m, r['raw_path'], r.get('media_type')))
        h = hashlib.sha256(open(p, 'rb').read()).hexdigest()
        if h != r['sha256']:
            shabad += 1; badlist.append(('SHA_MISMATCH', r['raw_path']))
        else:
            ok += 1
    print("  manifest rows with file present AND sha256 verified:", ok)
    print("  manifest rows whose file is MISSING:", miss)
    print("  manifest rows with sha256 mismatch:", shabad)
    print("  manifest rows whose bytes are NOT a PDF:", notpdf)
    for b in badlist[:10]: print("     ", b)
    # inventory URLs not preserved
    iu = {r['download_url'] for r in I}
    mu = {r['source_url'] for r in M}
    print("  inventory download_urls:", len(iu), " manifest source_urls:", len(mu))
    print("  inventoried but NOT in manifest:", len(iu - mu))
    print("  in manifest but NOT inventoried:", len(mu - iu))
    print("  preservation values in manifest:", collections.Counter(r.get('preservation') for r in M))
    print("  distinct sha256 in manifest:", len({r['sha256'] for r in M}))
    print("  files on disk not referenced by any manifest row:",
          len({f for f in files} - {os.path.basename(r['raw_path']) for r in M}))
