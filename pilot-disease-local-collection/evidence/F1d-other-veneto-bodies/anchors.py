import re, sys, html
f = sys.argv[1]
needle = sys.argv[2] if len(sys.argv) > 2 else 'viticol'
h = open(f, encoding='utf-8', errors='replace').read()
i = h.lower().find(needle.lower())
print("FILE", f, "| needle", needle, "| found at", i)
if i < 0:
    sys.exit()
seg = h[max(0, i - 500): i + 9000]
for m in re.finditer(r'<a\s[^>]*href="([^"]+)"[^>]*>(.*?)</a>', seg, re.S | re.I):
    url = html.unescape(m.group(1))
    label = re.sub(r'<[^>]+>', '', m.group(2))
    label = re.sub(r'\s+', ' ', html.unescape(label)).strip()
    if not label:
        continue
    print("   LINK |", label[:70].encode('ascii', 'replace').decode(), "->", url[:150])
