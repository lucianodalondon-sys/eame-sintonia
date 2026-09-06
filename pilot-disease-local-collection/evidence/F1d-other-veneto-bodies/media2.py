import json, sys
for f in sys.argv[1:]:
    d = json.load(open(f, encoding='utf-8'))
    print("=====", f, "items:", len(d))
    for x in d:
        print("  ", (x.get('date') or '')[:10], x.get('mime_type'), x.get('source_url'))
