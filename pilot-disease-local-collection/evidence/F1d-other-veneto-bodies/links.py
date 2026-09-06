import re, sys, collections
f = sys.argv[1]
h = open(f, encoding='utf-8', errors='replace').read()
print("FILE", f, "bytes", len(h.encode('utf-8', 'replace')))
t = re.search(r'<title[^>]*>(.*?)</title>', h, re.S | re.I)
print("TITLE:", (t.group(1).strip()[:140] if t else 'NO_TITLE'))
hrefs = re.findall(r'href="([^"]+)"', h)
print("total href:", len(hrefs))
# years literally visible in visible text
text = re.sub(r'<script.*?</script>', ' ', h, flags=re.S | re.I)
text = re.sub(r'<style.*?</style>', ' ', text, flags=re.S | re.I)
text = re.sub(r'<[^>]+>', ' ', text)
yrs = collections.Counter(re.findall(r'\b(19[89]\d|20[0-3]\d)\b', text))
print("YEARS in visible text:", sorted(yrs.items()))
docs = [x for x in hrefs if re.search(r'\.(pdf|doc|docx|xls|xlsx|zip)(\?|$)', x, re.I)]
print("DOC-LIKE links:", len(docs))
seen = []
for x in docs:
    if x not in seen:
        seen.append(x)
for x in seen[:60]:
    print("   DOC", x)
inter = [x for x in hrefs if re.search(r'bollettin|fitosanit|viticol|difesa|archiv|annat|vite', x, re.I)]
s2 = []
for x in inter:
    if x not in s2:
        s2.append(x)
print("INTERESTING links:", len(s2))
for x in s2[:80]:
    print("   INT", x)
