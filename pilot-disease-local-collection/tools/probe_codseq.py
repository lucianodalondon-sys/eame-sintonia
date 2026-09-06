"""Ask meteo_storici_tabella for specific codseq values taken from ARPAV's own
dispenser sensor catalogue. Read-only. Prints exactly what came back."""
import json, sys, urllib.request, urllib.parse

BASE = 'https://api.arpa.veneto.it/REST/v1/meteo_storici_tabella'
UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36')


def probe(codseq, anno):
    url = f'{BASE}?{urllib.parse.urlencode({"codseq": codseq, "anno": anno})}'
    req = urllib.request.Request(url, headers={
        'User-Agent': UA, 'Referer': 'https://www.arpa.veneto.it/',
        'Accept': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            raw = r.read()
            status = r.status
    except Exception as e:
        return {'codseq': codseq, 'anno': anno, 'error': repr(e)[:160]}
    try:
        d = json.loads(raw)
    except Exception:
        return {'codseq': codseq, 'anno': anno, 'status': status,
                'bytes': len(raw), 'nonjson': raw[:120].decode('utf-8', 'replace')}
    rows = d.get('data') or []
    out = {'codseq': codseq, 'anno': anno, 'status': status, 'bytes': len(raw),
           'success': d.get('success'), 'rows': len(rows)}
    if rows:
        out['sensor'] = rows[0].get('nome_sensore')
        out['station'] = rows[0].get('nome_stazione')
        out['unit'] = rows[0].get('unitnm')
        out['tipo'] = rows[0].get('tipo')
        out['first'] = f"{rows[0].get('dataora')}={rows[0].get('valore')}"
        out['last'] = f"{rows[-1].get('dataora')}={rows[-1].get('valore')}"
    return out


targets = json.loads(sys.argv[1])
anni = sys.argv[2].split(',')
for t in targets:
    for a in anni:
        print(json.dumps(probe(t, a), ensure_ascii=False))
