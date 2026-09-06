"""Preserve the ARPAV station registry WITH coordinates, for the stations whose
series we hold.

Source: https://api.arpa.veneto.it/REST/v1/meteo_storici?coordcd=<type>&anno=<y>
This is the endpoint ARPAV's own 'Dati meteorologici ultimi anni' page calls;
the coordcd values below are the ones hard-coded in that page's script.

Only stations already present in our preserved series are reported as covered.
A station without published coordinates is COORDS_NOT_PUBLISHED, never guessed.
"""
import hashlib, json, os, urllib.request, urllib.parse
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, 'raw', 'F4-arpav-rest')
OUT = os.path.join(RAW, 'geo')
UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36')

# coordcd values taken verbatim from the ARPAV page script (pulsanti table)
COORDCD = {'PREC': 23, 'TEMP': 18, 'UMID': 19, 'RADSOL': 22}
ANNI = [2015, 2024]

os.makedirs(OUT, exist_ok=True)
recount = json.load(open(os.path.join(ROOT, 'manifests', 'daily-series-recount.json'), encoding='utf-8'))
our_stations = {r['codseqst'] for r in recount['per_file'] if isinstance(r['codseqst'], int)}
print('stations in our preserved series =', len(our_stations))

geo = {}
manifest = []
for name, cd in COORDCD.items():
    for anno in ANNI:
        url = ('https://api.arpa.veneto.it/REST/v1/meteo_storici?'
               + urllib.parse.urlencode({'coordcd': cd, 'anno': anno}))
        req = urllib.request.Request(url, headers={
            'User-Agent': UA, 'Referer': 'https://www.arpa.veneto.it/',
            'Accept': 'application/json'})
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                raw = r.read()
                status = r.status
        except Exception as e:
            manifest.append({'source_url': url, 'preservation': 'NOT_PRESERVED',
                             'error': repr(e)[:150]})
            print(f'  {name}/{anno} FAILED {e!r}'[:120])
            continue
        path = os.path.join(OUT, f'meteo_storici_{name}_{anno}.json')
        with open(path, 'wb') as f:
            f.write(raw)
        manifest.append({
            'local_item_id': f'ARPAV-GEO-{name}-{anno}',
            'source_id': 'ARPAV-REST-meteo_storici',
            'source_authority': 'ARPAV',
            'source_url': url, 'http_status': status, 'bytes': len(raw),
            'sha256': hashlib.sha256(raw).hexdigest(),
            'media_type': 'application/json',
            'raw_path': os.path.relpath(path, ROOT).replace('\\', '/'),
            'access_method': 'PUBLIC_API',
            'captured_at': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
            'preservation': 'PRESERVED',
        })
        for s in json.loads(raw).get('data', []):
            cs = s.get('codice_stazione')
            geo.setdefault(cs, {
                'codice_stazione': cs, 'nome_stazione': s.get('nome_stazione'),
                'comune': s.get('comune'), 'provincia': s.get('provincia'),
                'latitudine': s.get('latitudine'), 'longitudine': s.get('longitudine'),
                'altitude': s.get('altitude'), 'seen_as': [],
            })
            geo[cs]['seen_as'].append(f'{name}/{anno}')
        print(f'  {name}/{anno} {status} {len(raw)}B stations={len(json.loads(raw).get("data", []))}')

# join: our stations are keyed by codseqst; the geo feed keys by codice_stazione
stations_disp = {s['codseqst']: s for s in json.load(
    open(os.path.join(RAW, 'meteo_stazioni_dispenser.json'), encoding='utf-8'))['data']}
joined, missing = [], []
for cst in sorted(our_stations):
    disp_name = stations_disp.get(cst, {}).get('nome_stazione', 'NOT_KNOWN')
    code = None
    if '(' in disp_name and disp_name.rstrip().endswith(')'):
        try:
            code = int(disp_name.rsplit('(', 1)[1].rstrip(')'))
        except ValueError:
            code = None
    g = geo.get(code)
    if g and g.get('latitudine') is not None:
        joined.append({'codseqst': cst, 'dispenser_name': disp_name, **g})
    else:
        missing.append({'codseqst': cst, 'dispenser_name': disp_name,
                        'codice_stazione': code if code is not None else 'NOT_KNOWN',
                        'coords': 'COORDS_NOT_PUBLISHED_IN_THIS_FEED'})

with open(os.path.join(ROOT, 'manifests', 'station-geo.json'), 'w', encoding='utf-8') as f:
    json.dump({'stations_with_coordinates': joined,
               'stations_without_coordinates': missing,
               'geo_feed_station_count': len(geo)}, f, ensure_ascii=False, indent=1)
with open(os.path.join(ROOT, 'manifests', 'arpav-geo-manifest.jsonl'), 'w', encoding='utf-8') as f:
    for m in manifest:
        f.write(json.dumps(m, ensure_ascii=False) + '\n')

print()
print(f'STATIONS_WITH_COORDINATES    = {len(joined)}')
print(f'STATIONS_WITHOUT_COORDINATES = {len(missing)}')
for j in joined:
    print(f'  {j["codseqst"]} {j["nome_stazione"]:26} {j["comune"]:22} '
          f'lat={j["latitudine"]:.5f} lon={j["longitudine"]:.5f} alt={j["altitude"]}')
for m in missing:
    print('  MISSING', m)
