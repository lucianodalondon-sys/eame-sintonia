import re
d = open(r'C:\disease-local-collection-italy\pilot-disease-local-collection\evidence\F2b\build.js',
         'r', encoding='utf-8', errors='replace').read()
for kw in ['advancedSearch(', 'CONTAINS', 'contains"', 'operator', 'sys_search', 'searchText',
           'queryString', 'dateRange']:
    ms = list(re.finditer(re.escape(kw), d))
    print('#####', kw, len(ms))
    seen = set()
    for m in ms:
        t = d[max(0, m.start()-230):m.end()+230].replace('\n', ' ')
        if t in seen:
            continue
        seen.add(t)
        print('---', t[:430])
        if len(seen) >= 5:
            break
