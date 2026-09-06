"""Scope which Treviso-area station/sensor/year combinations exist, per ARPAV's
own declared catalogue. Counts only — no downloads."""
import json, re, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, 'raw', 'F4-arpav-rest')

st = {s['codseqst']: s for s in json.load(
    open(os.path.join(RAW, 'meteo_stazioni_dispenser.json'), encoding='utf-8'))['data']}
se = json.load(open(os.path.join(RAW, 'meteo_sensori_dispenser.json'), encoding='utf-8'))['data']

WANTED = ('Bagnatura fogliare', 'Precipitazione', 'Temperatura aria a 2m',
          'Umidità relativa a 2m', 'Radiazione solare globale')

tv = {c for c, s in st.items() if s['provincia'] == 'TV'}
bfogl_tv = {x['codseqst'] for x in se
            if x['codseqst'] in tv and x['descrizione'] == 'Bagnatura fogliare'}

print('estacoes TV                     =', len(tv))
print('estacoes TV com bagnatura       =', len(bfogl_tv))
for c in sorted(bfogl_tv, key=lambda c: st[c]['nome_stazione']):
    print('   ', c, st[c]['nome_stazione'])

jobs = []
for x in se:
    if x['codseqst'] not in bfogl_tv:
        continue
    if x['descrizione'] not in WANTED:
        continue
    years = sorted({int(y) for y in re.findall(r'\b(20\d\d)\b', x['descrizione_annate'] or '')})
    for y in years:
        jobs.append((x['codseqst'], x['codseq'], x['descrizione'], y))

print()
print('combinacoes estacao x sensor x ano =', len(jobs))
if jobs:
    print('anos                               =', min(j[3] for j in jobs), '->', max(j[3] for j in jobs))
print('estimativa de bytes (~78KB cada)   = %.1f MB' % (len(jobs) * 78_000 / 1_048_576))

with open(os.path.join(ROOT, 'manifests', 'arpav-jobs.json'), 'w', encoding='utf-8') as f:
    json.dump([{'codseqst': a, 'codseq': b, 'sensore': c, 'anno': d,
                'stazione': st[a]['nome_stazione']} for a, b, c, d in jobs],
              f, ensure_ascii=False, indent=1)
print('job list ->', os.path.join(ROOT, 'manifests', 'arpav-jobs.json'))
