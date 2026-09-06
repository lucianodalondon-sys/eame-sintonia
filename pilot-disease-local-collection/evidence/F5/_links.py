import re, sys, html

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
path = sys.argv[1]
filt = sys.argv[2].lower() if len(sys.argv) > 2 else ""
h = open(path, encoding="utf-8", errors="replace").read()
print("BYTES", len(h))
# anchors with text
anchors = re.findall(r'<a\b[^>]*href="([^"]+)"[^>]*>(.*?)</a>', h, re.S | re.I)
seen = set()
for href, txt in anchors:
    href = html.unescape(href)
    t = re.sub(r"<[^>]+>", " ", txt)
    t = html.unescape(t)
    t = re.sub(r"\s+", " ", t).strip()
    key = (href, t)
    if key in seen:
        continue
    seen.add(key)
    blob = (href + " " + t).lower()
    if filt and filt not in blob:
        continue
    print(href, "|", t[:160])
