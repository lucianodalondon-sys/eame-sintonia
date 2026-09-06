"""Probe the ARPAV meteo_storici REST family. Read-only. Reports exactly what came back."""
import json, sys, urllib.request, urllib.parse

BASE = 'https://api.arpa.veneto.it/REST/v1/'
UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36')


def get(path, **params):
    url = BASE + path
    if params:
        url += '?' + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={
        'User-Agent': UA,
        'Referer': 'https://www.arpa.veneto.it/',
        'Accept': 'application/json',
    })
    with urllib.request.urlopen(req, timeout=90) as r:
        raw = r.read()
    return r.status, raw, url


def main():
    anno = sys.argv[1] if len(sys.argv) > 1 else '2015'
    coordcd = sys.argv[2] if len(sys.argv) > 2 else '23'
    needle = sys.argv[3] if len(sys.argv) > 3 else 'Conegliano'

    st, raw, url = get('meteo_storici', coordcd=coordcd, anno=anno)
    print(f'[stations] {st} {len(raw)}B {url}')
    stations = json.loads(raw)['data']
    print(f'[stations] count={len(stations)}')
    hits = [s for s in stations if needle.lower() in (s.get('nome_stazione') or '').lower()]
    for h in hits:
        print('  HIT', h['codseq'], h['nome_stazione'], h['comune'], h['provincia'],
              h['latitudine'], h['longitudine'], 'alt', h['altitude'], 'tipo', h['tipo'])
    if not hits:
        print('  NO STATION MATCHED', needle)
        return

    codseq = hits[0]['codseq']
    st, raw, url = get('meteo_storici_tabella', codseq=codseq, anno=anno)
    print(f'[daily] {st} {len(raw)}B {url}')
    d = json.loads(raw)
    rows = d.get('data') or []
    print(f'[daily] success={d.get("success")} rows={len(rows)}')
    if rows:
        print('[daily] first row keys:', list(rows[0].keys()))
        print('[daily] first:', json.dumps(rows[0], ensure_ascii=False)[:300])
        print('[daily] last :', json.dumps(rows[-1], ensure_ascii=False)[:300])

    st, raw, url = get('meteo_storici_totali', codseq=codseq, anno=anno)
    print(f'[totals] {st} {len(raw)}B {url}')
    print('[totals]', raw[:300].decode('utf-8', 'replace'))


main()
