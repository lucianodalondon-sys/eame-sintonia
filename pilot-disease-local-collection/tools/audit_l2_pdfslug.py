import json, os, re, zlib, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def P(*a): return os.path.join(ROOT, *a)
def rd(p): return [json.loads(l) for l in open(P(p), encoding='utf-8') if l.strip()]

M = rd('manifests/arpav-docs-manifest.verified.jsonl')
bn = [os.path.basename(r['raw_path']) for r in M]
print("docs raw_path basenames -- all end in '_file'?:",
      all(b.endswith('_file') for b in bn), " sample:", bn[:3])
print("so the season label lives ONLY in the manifest row, which was built from the CMS URL")

ann = [r for r in M if 'annate-agrarie' in r['source_url']]
print()
print("annate rows:", len(ann))
slugs = [r['source_url'].split('/annate-agrarie/')[1].split('/@@')[0] for r in ann]
print("distinct annata slugs:", len(set(slugs)))
print("distinct sha256 among annate:", len({r['sha256'] for r in ann}))

def raw_years(path):
    b = open(path, 'rb').read()
    txt = []
    for m in re.finditer(rb'stream\r?\n', b):
        s = m.end()
        e = b.find(b'endstream', s)
        if e < 0: continue
        try:
            txt.append(zlib.decompress(b[s:e]))
        except Exception:
            pass
        if len(txt) > 40: break
    blob = b' '.join(txt)
    # PDF text operators often split chars; strip parens content
    show = b' '.join(re.findall(rb'\((.*?)\)', blob[:400000]))
    ys = collections.Counter(int(y) for y in re.findall(rb'\b(?:19|20)\d{2}\b', show))
    return ys, len(blob)

print()
print("%-34s %-30s %s" % ("slug (CMS/catalogue claim)", "top years found in PDF text", "note"))
bad = []
for r, s in zip(ann, slugs):
    ys, blen = raw_years(P(r['raw_path']))
    want = set(int(y) for y in re.findall(r'(?:19|20)\d{2}', s))
    top = ys.most_common(4)
    hit = bool(want & set(ys)) if ys else None
    if ys and not hit: bad.append((s, top))
    print("%-34s %-30s %s" % (s[:34], str(top)[:30],
          ("OK" if hit else ("NO_YEAR_MATCH" if ys else "NO_TEXT_EXTRACTED"))))
print()
print("annate whose PDF text contains NO year from its own slug:", len(bad), bad)
