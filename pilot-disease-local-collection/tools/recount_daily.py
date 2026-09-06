"""Recount the preserved ARPAV daily series by OPENING every file.

Nothing here is inherited from a report. Every number is computed from the
bytes on disk.

Key distinction kept explicit:
  CATALOG_AVAILABILITY  = the years ARPAV's own catalogue declares
  ACTUAL_DATA_PRESERVED = the days actually present in the files we hold

A year listed by the catalogue but short of its days is a real source gap. A
missing day is NOT a zero and is never filled.
"""
import gzip, json, os, re
from collections import defaultdict
from datetime import date, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, 'raw', 'F4-arpav-rest')
TAB = os.path.join(RAW, 'tabella')
OUT = os.path.join(ROOT, 'manifests', 'daily-series-recount.json')

WIN_START, WIN_END = date(2014, 3, 1), date(2025, 10, 31)


def days_in_year(y):
    return 366 if (y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)) else 365


stations = {s['codseqst']: s for s in json.load(
    open(os.path.join(RAW, 'meteo_stazioni_dispenser.json'), encoding='utf-8'))['data']}
sensors = json.load(open(os.path.join(RAW, 'meteo_sensori_dispenser.json'), encoding='utf-8'))['data']
sensor_by_codseq = {s['codseq']: s for s in sensors}

# catalogue-declared years, straight from ARPAV's descrizione_annate
catalog_years = {}
for s in sensors:
    catalog_years[s['codseq']] = sorted(
        {int(y) for y in re.findall(r'\b(20\d\d)\b', s.get('descrizione_annate') or '')})

files = sorted(f for f in os.listdir(TAB) if f.endswith('.json.gz'))
print(f'daily files on disk = {len(files)}')

per_file = []
per_sensor_type = defaultdict(lambda: {'files': 0, 'rows': 0, 'stations': set(), 'years': set()})
per_series = defaultdict(lambda: {'years_preserved': set(), 'rows': 0, 'days_in_window': set()})
total_rows = total_bytes = 0
empty_years = []

for fn in files:
    path = os.path.join(TAB, fn)
    total_bytes += os.path.getsize(path)
    with gzip.open(path, 'rb') as g:
        raw = g.read()
    d = json.loads(raw)
    rows = d.get('data') or []
    codseq, anno = fn[:-8].split('_')
    codseq, anno = int(codseq), int(anno)
    meta = sensor_by_codseq.get(codseq, {})
    st = stations.get(meta.get('codseqst'), {})
    dates = set()
    nonnull = 0
    for r in rows:
        dt = (r.get('dataora') or '')[:10]
        if dt:
            dates.add(dt)
        if r.get('valore') not in (None, '', 'null'):
            nonnull += 1
    sensor_name = rows[0].get('nome_sensore') if rows else meta.get('descrizione', 'NOT_KNOWN')
    unit = rows[0].get('unitnm') if rows else 'NOT_KNOWN'
    tipo = rows[0].get('tipo') if rows else 'NOT_KNOWN'
    expected = days_in_year(anno)
    rec = {
        'file': fn, 'codseq': codseq, 'anno': anno,
        'codseqst': meta.get('codseqst', 'NOT_KNOWN'),
        'stazione': st.get('nome_stazione', 'NOT_KNOWN'),
        'provincia': st.get('provincia', 'NOT_KNOWN'),
        'sensore': sensor_name, 'tipo': tipo, 'unit': unit,
        'rows': len(rows), 'distinct_dates': len(dates), 'nonnull_values': nonnull,
        'expected_days': expected, 'missing_days': expected - len(dates),
        'first_date': min(dates) if dates else 'NOT_KNOWN',
        'last_date': max(dates) if dates else 'NOT_KNOWN',
        'state': ('EMPTY_NOT_ZERO' if not rows else
                  'FULL_YEAR' if len(dates) >= expected else 'PARTIAL_SOURCE_GAP'),
    }
    if not rows:
        empty_years.append(f'{codseq}/{anno}')
    per_file.append(rec)
    total_rows += len(rows)
    k = tipo if tipo != 'NOT_KNOWN' else sensor_name
    per_sensor_type[k]['files'] += 1
    per_sensor_type[k]['rows'] += len(rows)
    per_sensor_type[k]['stations'].add(meta.get('codseqst'))
    per_sensor_type[k]['years'].add(anno)
    s = per_series[codseq]
    s['years_preserved'].add(anno)
    s['rows'] += len(rows)
    for dt in dates:
        y, m, dd = int(dt[:4]), int(dt[5:7]), int(dt[8:10])
        try:
            dobj = date(y, m, dd)
        except ValueError:
            continue
        if WIN_START <= dobj <= WIN_END:
            s['days_in_window'].add(dt)

print(f'DAILY_FILES            = {len(files)}')
print(f'DAILY_ROWS             = {total_rows}')
print(f'DAILY_BYTES_COMPRESSED = {total_bytes} ({total_bytes/1_048_576:.1f} MB)')
print(f'EMPTY_YEAR_FILES       = {len(empty_years)}  (EMPTY_NOT_ZERO)')
print()
print(f'{"sensor tipo":16} {"files":>6} {"rows":>9} {"stations":>9} {"years":>6}  span')
for k in sorted(per_sensor_type, key=lambda k: -per_sensor_type[k]['rows']):
    v = per_sensor_type[k]
    ys = sorted(v['years'])
    print(f'{k:16} {v["files"]:6d} {v["rows"]:9d} {len(v["stations"]):9d} {len(ys):6d}  {ys[0]}-{ys[-1]}')

# ---- leaf wetness, measured not assumed ----
print()
print('=== BAGNATURA FOGLIARE (leaf wetness) — measured ===')
win_days = (WIN_END - WIN_START).days + 1
bf = [r for r in per_file if r['tipo'] == 'BFOGL']
bf_series = sorted({r['codseq'] for r in bf})
print(f'LEAF_WETNESS_SENSOR_SERIES_PRESERVED = {len(bf_series)}')
print(f'LEAF_WETNESS_STATIONS_PRESERVED      = {len({r["codseqst"] for r in bf})}')
print(f'LEAF_WETNESS_FILES                   = {len(bf)}')
print(f'LEAF_WETNESS_ROWS                    = {sum(r["rows"] for r in bf)}')
if bf:
    print(f'LEAF_WETNESS_YEARS_PRESERVED         = {min(r["anno"] for r in bf)}-{max(r["anno"] for r in bf)}')
    print(f'LEAF_WETNESS_UNITS_SEEN              = {sorted({r["unit"] for r in bf})}')
print(f'WINDOW {WIN_START}..{WIN_END} = {win_days} days')
print()
print(f'{"station":32} {"catalog years":>14} {"preserved":>10} {"days in window":>15} {"cover%":>7} {"short years"}')
leaf_rows = []
for cs in bf_series:
    meta = sensor_by_codseq.get(cs, {})
    st = stations.get(meta.get('codseqst'), {})
    rows_for = [r for r in per_file if r['codseq'] == cs]
    cat = catalog_years.get(cs, [])
    pres = sorted({r['anno'] for r in rows_for})
    dw = len(per_series[cs]['days_in_window'])
    short = [f'{r["anno"]}({r["missing_days"]})' for r in sorted(rows_for, key=lambda r: r['anno'])
             if r['missing_days'] > 0]
    name = st.get('nome_stazione', 'NOT_KNOWN')
    print(f'{name[:32]:32} {(str(cat[0]) + "-" + str(cat[-1])) if cat else "NOT_KNOWN":>14} '
          f'{(str(pres[0]) + "-" + str(pres[-1])) if pres else "NONE":>10} {dw:15d} {100*dw/win_days:6.1f}% '
          f'{",".join(short) if short else "none"}')
    leaf_rows.append({
        'codseq': cs, 'codseqst': meta.get('codseqst'), 'stazione': name,
        'provincia': st.get('provincia'),
        'catalog_years': cat, 'years_preserved': pres,
        'days_in_window_2014_2025': dw, 'window_days': win_days,
        'window_coverage_pct': round(100 * dw / win_days, 2),
        'short_years_missing_days': short,
    })

summary = {
    'measured_at_note': 'every number computed by opening the preserved files',
    'daily_files': len(files), 'daily_rows': total_rows,
    'daily_bytes_compressed': total_bytes,
    'empty_year_files_not_zero': empty_years,
    'sensor_types': {k: {'files': v['files'], 'rows': v['rows'],
                         'stations': len(v['stations']),
                         'years': sorted(v['years'])} for k, v in per_sensor_type.items()},
    'leaf_wetness': leaf_rows,
    'window': {'start': str(WIN_START), 'end': str(WIN_END), 'days': win_days},
    'per_file': per_file,
}
with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(summary, f, ensure_ascii=False, indent=1)
print()
print('recount ->', OUT)
