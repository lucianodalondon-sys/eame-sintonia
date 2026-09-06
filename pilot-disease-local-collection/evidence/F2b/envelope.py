import json, sys
d = json.load(open(sys.argv[1], encoding='utf-8'))
print('top keys', list(d.keys()))
p = d.get('page', d)
print('page keys:')
for k, v in p.items():
    if isinstance(v, (list, dict)):
        print('   ', k, type(v).__name__, 'len=', len(v))
    else:
        print('   ', k, '=', v)
ents = p.get('entities') or []
if ents:
    e = ents[0]
    print('entity top keys', list(e.keys()))
    at = e.get('attributes', {})
    print('attribute keys count', len(at))
    print('attr sample', list(at.keys())[:60])
