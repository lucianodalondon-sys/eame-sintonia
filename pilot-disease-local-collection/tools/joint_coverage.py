"""Joint coverage: how many days does a station have ALL the variables a grape
downy-mildew model needs, on the SAME day?

RED TEAM FINDING (CONFIRMED / HIGH):
  The 99.x% figures published per variable are per-variable. Requiring leaf
  wetness AND air temperature AND relative humidity AND rain on the same day
  cuts the usable station count. Oderzo advertises 99.86% leaf wetness but its
  temperature and humidity sensors stop on 2024-01-28.

This recomputes joint coverage from the preserved files, per station, inside the
window 2014-03-01 .. 2025-10-31, and also reports the per-variable last date so
a truncated sensor is visible instead of hidden behind a union.
"""
import gzip, json, os
from collections import defaultdict
from datetime import date, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TAB = os.path.join(ROOT, 'raw', 'F4-arpav-rest', 'tabella')
M = os.path.join(ROOT, 'manifests')

CORE = ['BFOGL', 'TARIA2M', 'UMID2M', 'PREC']          # what a mildew model needs
PLUS = CORE + ['RADSOL']
WIN_START, WIN_END = date(2014, 3, 1), date(2025, 10, 31)
WIN_DAYS = (WIN_END - WIN_START).days + 1

prov = [json.loads(l) for l in open(os.path.join(M, 'daily-series-provenance.jsonl'), encoding='utf-8') if l.strip()]
byfile = {r['LOCAL_ITEM_ID']: r for r in prov}

# station -> variable -> set of dates (inside window) ; and overall last date
dates = defaultdict(lambda: defaultdict(set))
lastdate = defaultdict(dict)
names = {}
for r in prov:
    st, var = r['STATION_ID'], r['VARIABLE_CODE']
    names[st] = r['STATION_NAME']
    path = os.path.join(TAB, os.path.basename(r['RAW_PATH']))
    with gzip.open(path, 'rb') as g:
        rows = json.loads(g.read()).get('data') or []
    for row in rows:
        s = (row.get('dataora') or '')[:10]
        if not s:
            continue
        y, mo, d = int(s[:4]), int(s[5:7]), int(s[8:10])
        try:
            dt = date(y, mo, d)
        except ValueError:
            continue
        prev = lastdate[st].get(var)
        if prev is None or s > prev:
            lastdate[st][var] = s
        if WIN_START <= dt <= WIN_END:
            dates[st][var].add(s)

out = []
print(f'window {WIN_START} .. {WIN_END} = {WIN_DAYS} days')
print()
hdr = f'{"station":32} {"BFOGL":>7} {"TARIA":>7} {"UMID":>7} {"PREC":>7} | {"JOINT4":>7} {"joint%":>7} | last T/RH'
print(hdr)
print('-' * len(hdr))
for st in sorted(names, key=lambda s: names[s]):
    per = {v: len(dates[st].get(v, set())) for v in PLUS}
    have = [dates[st].get(v) for v in CORE]
    joint = set.intersection(*[h for h in have if h]) if all(have) else set()
    pct = 100 * len(joint) / WIN_DAYS
    lt = lastdate[st].get('TARIA2M', 'NONE')
    lh = lastdate[st].get('UMID2M', 'NONE')
    flag = '  <<' if pct < 99.4 else ''
    print(f'{names[st][:32]:32} {per["BFOGL"]:7d} {per["TARIA2M"]:7d} {per["UMID2M"]:7d} '
          f'{per["PREC"]:7d} | {len(joint):7d} {pct:6.2f}% | {lt} / {lh}{flag}')
    out.append({
        'station_id': st, 'station_name': names[st],
        'per_variable_days_in_window': per,
        'joint4_days_in_window': len(joint),
        'window_days': WIN_DAYS,
        'joint4_coverage_pct': round(pct, 2),
        'last_date_TARIA2M': lt, 'last_date_UMID2M': lh,
        'last_date_BFOGL': lastdate[st].get('BFOGL', 'NONE'),
        'last_date_PREC': lastdate[st].get('PREC', 'NONE'),
        'last_date_RADSOL': lastdate[st].get('RADSOL', 'NO_SENSOR'),
        'joint4_variables': CORE,
    })

for thr in (99.4, 99.3, 99.0, 95.0):
    n = sum(1 for o in out if o['joint4_coverage_pct'] >= thr)
    print(f'stations with JOINT4 >= {thr}%: {n} of {len(out)}')
print()
for thr in (99.4, 99.3):
    n = sum(1 for o in out if 100 * o['per_variable_days_in_window']['BFOGL'] / WIN_DAYS >= thr)
    print(f'stations with LEAF WETNESS ALONE >= {thr}%: {n} of {len(out)}')

p = os.path.join(M, 'joint-coverage.json')
with open(p, 'w', encoding='utf-8') as f:
    json.dump({
        'note': ('Per-variable coverage is NOT usable coverage. JOINT4 is the count of '
                 'days inside the window on which leaf wetness, air temperature, '
                 'relative humidity AND rain are all present at that station.'),
        'window': {'start': str(WIN_START), 'end': str(WIN_END), 'days': WIN_DAYS},
        'stations': out}, f, ensure_ascii=False, indent=1)
print('\n->', os.path.relpath(p, ROOT))
