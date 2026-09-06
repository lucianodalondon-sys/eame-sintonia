import json, sys, re, collections

items = []
for f in sys.argv[1:]:
    d = json.load(open(f, encoding='utf-8'))
    items.extend(d)
print("TOTAL media items loaded:", len(items))

byyear = collections.Counter()
bull = []
for it in items:
    url = it.get('source_url') or ''
    date = (it.get('date') or '')[:10]
    title = ((it.get('title') or {}).get('rendered') or '')
    mime = it.get('mime_type') or ''
    m = re.search(r'/uploads/(\d{4})/(\d{2})/', url)
    y = m.group(1) if m else 'NO_UPLOAD_YEAR'
    byyear[y] += 1
    name = url.rsplit('/', 1)[-1]
    if re.search(r'bollettin', name, re.I):
        bull.append((y, date, mime, name, url))

print("\nUPLOAD-PATH YEAR distribution (all 'bollettino' search hits):")
for y, c in sorted(byyear.items()):
    print("  ", y, c)

print("\nItems whose FILENAME contains 'bollettin':", len(bull))
byy2 = collections.Counter(b[0] for b in bull)
print("  by upload-path year:", sorted(byy2.items()))
print("  by wp 'date' year:", sorted(collections.Counter(b[1][:4] for b in bull).items()))
print("\n--- filename-bollettino items, oldest upload path first ---")
for b in sorted(bull):
    print("  ", b[0], b[1], b[2], "|", b[3])
