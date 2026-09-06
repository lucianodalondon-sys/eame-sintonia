# INDEPENDENT: what does the ARPAV sensor catalogue OFFER for leaf wetness,
# station by station, vs what we actually hold. Tests source-gap vs fetch-failure.
import json, os, re, glob, gzip
from collections import defaultdict

ROOT = r'C:\disease-local-collection-italy\pilot-disease-local-collection'
cat = json.load(open(os.path.join(ROOT, 'raw', 'F4-arpav-rest',
                                  'meteo_sensori_dispenser.json'), encoding='utf-8'))['data']

# stations we actually hold BFOGL for (from raw payloads)
held = json.load(open(os.path.join(ROOT, 'tools', '_v3_bfogl_dates.json')))
heldyears = {s: sorted({d[:4] for d in v}) for s, v in held.items()}

# which codseq did we actually download files for?
codseq_files = defaultdict(set)
for f in sorted(glob.glob(os.path.join(ROOT, 'raw', 'F4-arpav-rest', 'tabella', '*.json.gz'))):
    b = os.path.basename(f)
    cs, yr = b.split('_')[0], b.split('_')[1].split('.')[0]
    codseq_files[int(cs)].add(int(yr))

bf = [c for c in cat if 'bagnatura' in (c.get('descrizione') or '').lower()]
print("catalogue entries whose descrizione mentions 'bagnatura':", len(bf))
print("distinct stations offering it in ALL of Veneto            :",
      len({c['statnm'] for c in bf}))

print()
print("=== the 14 stations we hold, vs the catalogue string ===")
print("%-30s %10s  %-14s %-14s %s" % ('station', 'codseq', 'catalogue', 'preserved', 'delta'))
bad = 0
for s in sorted(held):
    ent = [c for c in bf if c['statnm'] == s]
    if not ent:
        print("%-30s  NO CATALOGUE ENTRY MATCHED" % s); bad += 1; continue
    e = ent[0]
    cy = sorted(re.findall(r'\b(19|20)\d{2}\b', e['descrizione_annate']))
    cy = sorted(set(re.findall(r'\b((?:19|20)\d{2})\b', e['descrizione_annate'])))
    py = heldyears[s]
    extra_cat = sorted(set(cy) - set(py))     # offered but NOT preserved -> real miss
    extra_held = sorted(set(py) - set(cy))    # preserved but not offered
    d = ''
    if extra_cat:  d += ' OFFERED-BUT-MISSING=' + ','.join(extra_cat)
    if extra_held: d += ' HELD-NOT-OFFERED=' + ','.join(extra_held)
    if extra_cat: bad += 1
    print("%-30s %10d  %s..%s(%2d) %s..%s(%2d)%s" %
          (s, e['codseq'], cy[0], cy[-1], len(cy), py[0], py[-1], len(py), d))
print()
print("stations where the catalogue offered a year we did NOT preserve:", bad)

print()
print("=== raw catalogue string for Breda ===")
for c in bf:
    if c['statnm'].startswith('Breda'):
        print("  statnm      :", c['statnm'])
        print("  codseq      :", c['codseq'])
        print("  descrizione :", c['descrizione'])
        print("  annate      :", c['descrizione_annate'])

print()
print("=== control: catalogue string for a full-span neighbour ===")
for c in bf:
    if c['statnm'] == 'Conegliano':
        print("  ", c['codseq'], '|', c['descrizione_annate'])

print()
print("=== did we request/download any file for Breda BFOGL before 2016? ===")
bre = [c for c in bf if c['statnm'].startswith('Breda')][0]['codseq']
print("Breda BFOGL codseq:", bre, "-> file years on disk:", sorted(codseq_files[bre]))

# does the planned job list contain the 6 missing station-years?
jobs = json.load(open(os.path.join(ROOT, 'manifests', 'arpav-jobs.json'), encoding='utf-8'))
if isinstance(jobs, dict):
    jl = jobs.get('jobs') or jobs.get('data') or []
else:
    jl = jobs
print("planned jobs total:", len(jl))
bj = [j for j in jl if j.get('codseq') == bre]
print("planned jobs for Breda BFOGL:", len(bj), "years:", sorted(j.get('anno') for j in bj))
