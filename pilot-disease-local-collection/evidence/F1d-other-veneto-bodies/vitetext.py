import re, sys
for f in sys.argv[1:]:
    h = open(f, encoding='utf-8', errors='replace').read()
    t = re.sub(r'<script.*?</script>', ' ', h, flags=re.S | re.I)
    t = re.sub(r'<style.*?</style>', ' ', t, flags=re.S | re.I)
    t = re.sub(r'<[^>]+>', ' ', t)
    t = re.sub(r'&nbsp;?', ' ', t)
    t = re.sub(r'\s+', ' ', t)
    print("=====", f, "| visible chars:", len(t))
    for m in re.finditer(r'(?i)(vite|viticol|riservat|login|accedi|area\s+soci)', t):
        s = max(0, m.start() - 110)
        print("   ...", t[s:m.end() + 130].strip().encode('ascii', 'replace').decode())
    print()
