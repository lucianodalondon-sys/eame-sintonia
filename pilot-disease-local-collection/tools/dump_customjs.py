import json, sys, re

d = json.load(open(sys.argv[1], encoding='utf-8'))
for bid, b in (d.get('blocks') or {}).items():
    if b.get('@type') != 'customJavascript':
        continue
    print('=== block', bid)
    for k, v in b.items():
        if isinstance(v, str) and len(v) > 60:
            print(f'--- field {k} ({len(v)} chars)')
            print(v[:6000])
        elif not isinstance(v, (dict, list)):
            print(f'   {k} = {v}')
    blob = json.dumps(b, ensure_ascii=False)
    urls = sorted(set(re.findall(r'https?://[^\s"\'\\)]+', blob)))
    rest = sorted(set(re.findall(r'REST/v1/[A-Za-z0-9_]+', blob)))
    print('URLS:', urls[:40])
    print('REST:', rest[:40])
