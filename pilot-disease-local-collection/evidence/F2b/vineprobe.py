import json, glob, urllib.request, urllib.error, re

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36")
SITE = "https://www.venetoagricoltura.org"
API = SITE + "/myportal/AVPISP/api"

VINE_RE = re.compile(
    r'trittico|vitivinicol|vendemmial|vendemmia|vigneti|viticolt|flavescenza|'
    r'uve|vitate|germoplasma viticolo|vitigni|prosecco|vino', re.I)

union = {}
for fn in sorted(glob.glob('term_*.json')):
    term = fn[5:-5]
    for k, v in json.load(open(fn, encoding='utf-8')).items():
        union.setdefault(k, dict(v, terms=[]))
        union[k]['terms'].append(term)


def probe(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            b = r.read()
            return str(r.status), len(b), r.headers.get('Content-Type', '')
    except urllib.error.HTTPError as e:
        try:
            b = e.read()
        except Exception:
            b = b''
        return str(e.code), len(b), e.headers.get('Content-Type', '') if e.headers else ''
    except Exception as e:
        return 'ERR:' + type(e).__name__, 0, str(e)[:60]


vine = {}
for k, v in union.items():
    t = (v.get('title') or v.get('name') or '')
    if v.get('type') in ('rve_immagine', 'myp_tags', 'myp_tags_advanced'):
        continue
    if VINE_RE.search(t) or VINE_RE.search(v.get('path') or ''):
        vine[k] = v

print("VINE-MATCHED ENTITIES:", len(vine))
results = {'posts': [], 'pdfs': []}

for k, v in sorted(vine.items(), key=lambda x: (x[1].get('firstPublishedAt') or '')):
    can = v.get('canonical')
    row = {'id': k, 'title': v.get('title') or v.get('name'), 'type': v.get('type'),
           'canonical': can, 'terms': sorted(set(v['terms'])),
           'firstPublishedAt': v.get('firstPublishedAt'),
           'path': v.get('path')}
    if can:
        u = SITE + can
        st, n, ct = probe(u)
        row['url'] = u
        row['http'] = st
        row['bytes'] = n
        row['ctype'] = ct
        print('POST', st, n, u, flush=True)
    results['posts'].append(row)
    for a in (v.get('allegati') or []):
        uu = a.get('dyn_str_association_allegati_uuid')
        nm = a.get('dyn_str_autobind_allegati_name')
        if not uu:
            continue
        du = API + "/content/download?id=" + uu
        st, n, ct = probe(du)
        results['pdfs'].append({'uuid': uu, 'name': nm, 'url': du, 'http': st,
                                'bytes': n, 'ctype': ct,
                                'parent_title': row['title'],
                                'parent_url': row.get('url')})
        print('   PDF', st, n, ct[:30], '|', nm, flush=True)

json.dump(results, open('vineprobe.json', 'w', encoding='utf-8'), indent=1,
          ensure_ascii=False)
print('posts', len(results['posts']), 'pdfs', len(results['pdfs']))
