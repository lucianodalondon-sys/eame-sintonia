import json, sys, glob

for fn in sorted(glob.glob('term_*.json')):
    d = json.load(open(fn, encoding='utf-8'))
    print('=====', fn, len(d))
    for k, v in d.items():
        al = v.get('allegati')
        f = v.get('file') or {}
        if al or (f and f.get('name')):
            print(' -', v['type'], '|', (v.get('title') or v.get('name'))[:70])
            print('   id=', v['id'], 'slug=', v.get('slug'))
            print('   file=', json.dumps(f, ensure_ascii=False))
            print('   allegati=', json.dumps(al, ensure_ascii=False)[:400])
