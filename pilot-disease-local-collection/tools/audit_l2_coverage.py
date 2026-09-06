import json, re, os, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def P(*a): return os.path.join(ROOT, *a)

sens = json.load(open(P('raw/F4-arpav-rest/meteo_sensori_dispenser.json'), encoding='utf-8'))['data']
stat = json.load(open(P('raw/F4-arpav-rest/meteo_stazioni_dispenser.json'), encoding='utf-8'))['data']
jobs = json.load(open(P('manifests/arpav-jobs.json'), encoding='utf-8'))

prov = {st['codseqst']: st.get('provincia') for st in stat}
name = {st['codseqst']: st.get('nome_stazione') for st in stat}
print("stations in catalogue:", len(stat))
print("stations by province:", collections.Counter(st.get('provincia') for st in stat))

# leaf wetness sensors region-wide
bf = [s for s in sens if 'agnatura' in (s.get('descrizione') or '')]
print()
print("region-wide sensors whose descrizione contains 'agnatura':", len(bf))
print("  labels:", collections.Counter(s['descrizione'] for s in bf))
bf_st = {s['codseqst'] for s in bf}
print("  distinct stations with a leaf-wetness sensor (region-wide):", len(bf_st))
print("  by province:", collections.Counter(prov.get(c) for c in bf_st))

bf_tv = {c for c in bf_st if prov.get(c) == 'TV'}
print()
print("TREVISO stations with a leaf-wetness sensor declared by catalogue:", len(bf_tv))

job_st = {j['codseqst'] for j in jobs}
job_bf_st = {j['codseqst'] for j in jobs if 'agnatura' in j['sensore']}
print("TREVISO stations with leaf wetness PRESERVED (from jobs):", len(job_bf_st))
print("declared-TV-BF stations NOT preserved:", sorted((bf_tv - job_bf_st)))
for c in sorted(bf_tv - job_bf_st):
    print("   ", c, name.get(c))
print("preserved-BF stations NOT in declared TV set:", sorted(job_bf_st - bf_tv))

# how many catalogue (sensor,year) does the region-wide leaf wetness declare
yrs = lambda s: {int(m.group(0)) for m in re.finditer(r'\b(?:19|20)\d{2}\b', s.get('descrizione_annate') or '')}
print()
print("region-wide leaf-wetness (sensor,year) declared:", sum(len(yrs(s)) for s in bf))
print("TV leaf-wetness (sensor,year) declared:", sum(len(yrs(s)) for s in bf if prov.get(s['codseqst']) == 'TV'))
print("leaf-wetness files preserved:", sum(1 for j in jobs if 'agnatura' in j['sensore']))

# 5 sensor types x 14 stations grid
print()
print("=== in-scope station x sensor-type grid ===")
grid = collections.defaultdict(set)
for j in jobs:
    grid[j['codseqst']].add(j['sensore'])
types = sorted({j['sensore'] for j in jobs})
for c in sorted(job_st):
    have = grid[c]
    print("  ", name.get(c), "->", len(have), "of", len(types), "missing:", sorted(set(types) - have))

# region-wide totals for the 5 variables
print()
print("=== region-wide catalogue totals for the 5 collected variables ===")
tot_sens = 0
tot_pairs = 0
for t in types:
    m = [s for s in sens if s['descrizione'] == t]
    p = sum(len(yrs(s)) for s in m)
    tot_sens += len(m)
    tot_pairs += p
    print("  %-30s sensors=%4d  declared (sensor,year)=%5d" % (t, len(m), p))
print("  TOTAL sensors=%d declared pairs=%d ; preserved files=%d" % (tot_sens, tot_pairs, len(jobs)))
