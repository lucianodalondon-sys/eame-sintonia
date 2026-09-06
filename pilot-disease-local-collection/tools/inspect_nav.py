import json, sys

path = sys.argv[1]
d = json.load(open(path, encoding='utf-8'))
print('KEYS:', [k for k in d.keys()][:25])
items = d.get('items') or []
print('items_total:', d.get('items_total'), 'len(items):', len(items))
for it in items:
    print('  ', it.get('@type'), '|', it.get('title'), '|', it.get('@id'))
