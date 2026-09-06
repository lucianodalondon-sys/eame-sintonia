import re, sys, html

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
path = sys.argv[1]
h = open(path, encoding="utf-8", errors="replace").read()
h = re.sub(r"(?is)<script.*?</script>", " ", h)
h = re.sub(r"(?is)<style.*?</style>", " ", h)
h = re.sub(r"(?is)<!--.*?-->", " ", h)
t = re.sub(r"(?s)<[^>]+>", "\n", h)
t = html.unescape(t)
lines = [re.sub(r"\s+", " ", x).strip() for x in t.split("\n")]
lines = [x for x in lines if x]
out = []
prev = None
for x in lines:
    if x != prev:
        out.append(x)
    prev = x
print("\n".join(out))
