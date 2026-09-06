import json, os, re, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def P(*a): return os.path.join(ROOT, *a)
def rd(p): return [json.loads(l) for l in open(P(p), encoding='utf-8') if l.strip()]

M = rd('manifests/arpav-docs-manifest.verified.jsonl')
ann = [(r, r['source_url'].split('/annate-agrarie/')[1].split('/@@')[0])
       for r in M if 'annate-agrarie' in r['source_url']]

def info(path):
    b = open(path, 'rb').read()
    out = {}
    for key in (b'Title', b'CreationDate', b'ModDate', b'Producer', b'Creator', b'Subject'):
        m = re.search(rb'/' + key + rb'\s*\((.{0,160}?)\)\s*[/>]', b, re.S)
        if m:
            v = m.group(1)
            if v.startswith(b'\xfe\xff'):
                try: v = v.decode('utf-16-be', 'replace')
                except Exception: v = repr(v)
            else:
                v = v.decode('latin-1', 'replace')
            out[key.decode()] = v.replace('\n', ' ')[:70]
    # XMP
    m = re.search(rb'<dc:title>.{0,400}?</dc:title>', b, re.S)
    if m:
        t = re.findall(rb'>([^<>]{2,90})<', m.group(0))
        t = [x.decode('utf-8', 'replace').strip() for x in t if x.strip()]
        if t: out['xmp:title'] = ' | '.join(t)[:70]
    return out

print("%-32s | %-24s | %s" % ("slug (CMS claim)", "CreationDate in PDF", "Title / xmp:title in PDF"))
print("-" * 110)
seen = collections.Counter()
for r, s in ann:
    i = info(P(r['raw_path']))
    cd = i.get('CreationDate', 'ABSENT')
    ti = i.get('Title') or i.get('xmp:title') or 'ABSENT'
    seen[cd[:10]] += 1
    print("%-32s | %-24s | %s" % (s[:32], cd[:24], ti))
print()
print("distinct CreationDate prefixes among the 26 annate:", len(seen))
print("bytes range:", min(r['bytes'] for r, _ in ann), "-", max(r['bytes'] for r, _ in ann))
print("distinct byte sizes:", len({r['bytes'] for r, _ in ann}), "of", len(ann))

# vine bulletins (C7)
vb = [r for r in M if 'peronospora-vite' in r['source_url']]
print()
print("=== C7 vine bulletins ===")
for r in vb:
    i = info(P(r['raw_path']))
    print("  ", r['source_url'].split('/')[-3], "| title:", r['document_title'],
          "| published_at:", r['published_at'], "| bytes:", r['bytes'])
    print("      PDF info:", json.dumps(i, ensure_ascii=False))
