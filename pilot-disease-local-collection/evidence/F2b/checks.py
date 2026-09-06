import json, re, sys, time
from probe import adv, get

# 1) crop context of the OIDIO bulletin parent
st, n, d = adv({"sys_title": {"type": "TEXT", "value": "BCE 21 del 3.04.2026"}}, size=5)
print("### BCE 21 2026 hits:", d['page']['entitiesCount'])
for e in d['page']['entities']:
    a = e['attributes']
    txt = re.sub('<[^>]+>', ' ', a.get('sys_description') or '')
    txt = re.sub(r'\s+', ' ', txt)
    print(' title:', a.get('sys_title'))
    print(' path :', a.get('sys_full_path'))
    print(' desc :', txt[:700])
    print(' alleg:', [x.get('dyn_str_autobind_allegati_name')
                      for x in (a.get('mul_association_allegati') or [])])

# 2) enumerate newsletter/bollettino folders via full path
print("\n### distinct sys_full_path prefixes containing 'Bollettino' or 'Newsletter'")
folders = {}
for probe_val in ["Bollettino", "Newsletter"]:
    page = 1
    while True:
        st, n, d = adv({"sys_full_path": {"type": "TEXT", "value": probe_val}},
                       page=page, size=50)
        ents = d['page']['entities']
        if page == 1:
            print(' total for', probe_val, '=', d['page'].get('entitiesCount'))
        if not ents:
            break
        for e in ents:
            p = e['attributes'].get('sys_full_path') or ''
            parts = [x for x in p.split('/') if x]
            key = '/'.join(parts[:2])
            folders[key] = folders.get(key, 0) + 1
        page += 1
        if page > 24:
            break
        time.sleep(0.15)
for k, v in sorted(folders.items(), key=lambda x: -x[1]):
    print('  %5d  %s' % (v, k))
