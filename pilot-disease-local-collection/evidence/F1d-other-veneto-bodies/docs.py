import re, sys, html
for f in sys.argv[1:]:
    h = open(f, encoding='utf-8', errors='replace').read()
    hrefs = [html.unescape(x) for x in re.findall(r'href="([^"]+)"', h)]
    docs = [x for x in hrefs if re.search(r'\.(pdf|doc|docx|xls|xlsx|zip)(/|\?|$)', x, re.I)]
    seen = []
    for x in docs:
        if x not in seen:
            seen.append(x)
    print("=====", f, "| href", len(hrefs), "| doc-links", len(docs), "| unique", len(seen))
    for x in seen:
        # print the filename part for readability
        m = re.search(r'/([^/]+\.(?:pdf|docx?|xlsx?|zip))(?:/|\?|$)', x, re.I)
        print("   ", (m.group(1) if m else '?'), "<<", x)
