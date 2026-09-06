"""Build the full-provenance manifest for the preserved daily meteo series.

One row per preserved file, carrying everything the handoff requires:
LOCAL_ITEM_ID, SOURCE_ID, SOURCE_AUTHORITY, SOURCE_URL, CAPTURED_AT,
MEDIA_TYPE, BYTES, SHA256, RAW_PATH, ACCESS_METHOD, plus station identity
(id, name, comune, lat, lon, altitude), sensor identity, unit and year.

Values are carried through as RAW: units are not converted and the stored
'valore' shape is not reinterpreted.
"""
import json, os
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M = os.path.join(ROOT, 'manifests')

daily = {}
for line in open(os.path.join(M, 'arpav-daily-manifest.jsonl'), encoding='utf-8'):
    r = json.loads(line)
    daily[(r['codseq'], int(r['anno']))] = r

recount = json.load(open(os.path.join(M, 'daily-series-recount.json'), encoding='utf-8'))
geo = json.load(open(os.path.join(M, 'station-geo.json'), encoding='utf-8'))
geo_by_cst = {g['codseqst']: g for g in geo['stations_with_coordinates']}

VALUE_SHAPE = {
    'BFOGL':   'scalar string, percentage of time wet ("% T")',
    'PREC':    'scalar string, mm',
    'RADSOL':  'scalar string, MJ/m2',
    'TARIA2M': 'JSON object encoded as a string: {"MINIMO":..,"MEDIO":..,"MASSIMO":..} in degC',
    'UMID2M':  'JSON object encoded as a string: {"MINIMO":..,"MASSIMO":..} in % (NO median field)',
}

out_path = os.path.join(M, 'daily-series-provenance.jsonl')
rows = []
missing_manifest = []
with open(out_path, 'w', encoding='utf-8') as out:
    for f in recount['per_file']:
        key = (f['codseq'], f['anno'])
        d = daily.get(key)
        if not d:
            missing_manifest.append(key)
            continue
        g = geo_by_cst.get(f['codseqst'], {})
        rec = {
            'LOCAL_ITEM_ID': d['local_item_id'],
            'SOURCE_ID': d['source_id'],
            'SOURCE_AUTHORITY': d['source_authority'],
            'SOURCE_URL': d['source_url'],
            'CAPTURED_AT': d['captured_at'],
            'MEDIA_TYPE': d.get('media_type', 'application/json'),
            'BYTES': d.get('bytes'),
            'SHA256': d.get('sha256'),
            'RAW_PATH': d.get('raw_path'),
            'RAW_ENCODING': 'gzip (original API response byte-for-byte inside)',
            'ACCESS_METHOD': 'PUBLIC_API',
            'STATION_ID': f['codseqst'],
            'STATION_CODE': g.get('codice_stazione', 'NOT_KNOWN'),
            'STATION_NAME': f['stazione'],
            'COMUNE': g.get('comune', 'NOT_KNOWN'),
            'PROVINCIA': f['provincia'],
            'LAT': g.get('latitudine', 'NOT_KNOWN'),
            'LON': g.get('longitudine', 'NOT_KNOWN'),
            'ALTITUDE_M': g.get('altitude', 'NOT_KNOWN'),
            'SENSOR_ID': f['codseq'],
            'VARIABLE': f['sensore'],
            'VARIABLE_CODE': f['tipo'],
            'UNIT': f['unit'],
            'RAW_VALUE_SHAPE': VALUE_SHAPE.get(f['tipo'], 'NOT_KNOWN'),
            'YEAR': f['anno'],
            'ROWS': f['rows'],
            'DISTINCT_DATES': f['distinct_dates'],
            'ROWS_WITH_VALUE': f['nonnull_values'],
            'EXPECTED_DAYS': f['expected_days'],
            'MISSING_DAYS': f['missing_days'],
            'FIRST_DATE': f['first_date'],
            'LAST_DATE': f['last_date'],
            'COMPLETENESS': f['state'],
            'PRESERVATION': d.get('preservation'),
        }
        rows.append(rec)
        out.write(json.dumps(rec, ensure_ascii=False) + '\n')

print(f'provenance rows written = {len(rows)}')
print(f'rows in recount         = {len(recount["per_file"])}')
print(f'missing from manifest   = {len(missing_manifest)}')
print(f'PRESERVED               = {sum(1 for r in rows if r["PRESERVATION"] == "PRESERVED")}')
print(f'distinct sha256         = {len({r["SHA256"] for r in rows})}')
print(f'stations with LAT/LON   = {sum(1 for r in rows if r["LAT"] != "NOT_KNOWN")}/{len(rows)}')
print('variables:', dict(Counter(r['VARIABLE_CODE'] for r in rows)))
print('completeness:', dict(Counter(r['COMPLETENESS'] for r in rows)))
print('->', os.path.relpath(out_path, ROOT))
