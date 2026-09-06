import json, re, os, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def P(*a): return os.path.join(ROOT, *a)

sens = json.load(open(P('raw/F4-arpav-rest/meteo_sensori_dispenser.json'), encoding='utf-8'))['data']
stat = json.load(open(P('raw/F4-arpav-rest/meteo_stazioni_dispenser.json'), encoding='utf-8'))['data']
jobs = json.load(open(P('manifests/arpav-jobs.json'), encoding='utf-8'))

sensor_years = {}
sensor_meta = {}
for s in sens:
    ys = {int(m.group(0)) for m in re.finditer(r'\b(?:19|20)\d{2}\b', s.get('descrizione_annate') or '')}
    sensor_years[s['codseq']] = ys
    sensor_meta[s['codseq']] = s

prov = {st['codseqst']: st.get('provincia') for st in stat}

print("=== JOB SCOPE ===")
print("jobs:", len(jobs))
job_sensors = {j['codseq'] for j in jobs}
job_st = {j['codseqst'] for j in jobs}
print("distinct sensors in jobs:", len(job_sensors))
print("distinct stations in jobs:", len(job_st))
print("distinct sensor labels in jobs:", collections.Counter(j['sensore'] for j in jobs))
print("provinces of job stations:", collections.Counter(prov.get(s) for s in job_st))

print()
print("=== CATALOGUE vs JOBS, restricted to the sensors actually in scope ===")
job_years = collections.defaultdict(set)
for j in jobs:
    job_years[j['codseq']].add(j['anno'])

missing_total = 0
extra_total = 0
detail = []
for cs in sorted(job_sensors):
    cy = sensor_years[cs]
    jy = job_years[cs]
    miss = cy - jy
    extra = jy - cy
    missing_total += len(miss)
    extra_total += len(extra)
    if miss or extra:
        detail.append((cs, sensor_meta[cs]['statnm'], sensor_meta[cs]['descrizione'],
                       sorted(miss), sorted(extra)))
print("in-scope sensors:", len(job_sensors))
print("catalogue-declared (sensor,year) for in-scope sensors:",
      sum(len(sensor_years[c]) for c in job_sensors))
print("job (sensor,year) pairs:", sum(len(job_years[c]) for c in job_sensors))
print("declared-but-not-requested:", missing_total)
print("requested-but-not-declared:", extra_total)
for d in detail[:60]:
    print("  ", d)

# disk
tab = P('raw/F4-arpav-rest/tabella')
disk = set()
for f in os.listdir(tab):
    m = re.fullmatch(r'(\d+)_(\d{4})\.json\.gz', f)
    if m:
        disk.add((int(m.group(1)), int(m.group(2))))
jobset = {(j['codseq'], j['anno']) for j in jobs}
print()
print("jobs set size:", len(jobset), "disk set size:", len(disk))
print("jobs not on disk:", len(jobset - disk), sorted(jobset - disk)[:20])
print("on disk not in jobs:", len(disk - jobset), sorted(disk - jobset)[:20])
