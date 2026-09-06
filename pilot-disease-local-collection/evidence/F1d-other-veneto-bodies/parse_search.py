import json, sys
for f in sys.argv[1:]:
    d = json.load(open(f, encoding='utf-8'))
    print("=====", f, "items_total=", d.get('items_total'))
    for it in d.get('items', []):
        print("  ", it.get('@type'), "|", (it.get('title') or '')[:95], "|", it.get('@id'))
