import json, os, glob, gzip
from collections import defaultdict

ROOT = r'C:\disease-local-collection-italy\pilot-disease-local-collection'

print("=== A. how the daily manifest labels every Breda BFOGL line ===")
n = 0
for line in open(os.path.join(ROOT, 'manifests', 'arpav-daily-manifest.jsonl'),
                 encoding='utf-8'):
    r = json.loads(line)
    if r.get('codseq') == 300011272:
        n += 1
        print("  %d rows=%-5s exp=%-4s missing=%-4s %-20s first=%s http=%s pres=%s" %
              (r['anno'], r['rows'], r['expected_days'], r['missing_days'],
               r['completeness'], (r.get('first_date') or '')[:10],
               r['http_status'], r['preservation']))
print("  Breda BFOGL manifest lines:", n)
print("  any line for a year < 2016?",
      any(json.loads(l).get('codseq') == 300011272 and json.loads(l)['anno'] < 2016
          for l in open(os.path.join(ROOT, 'manifests', 'arpav-daily-manifest.jsonl'),
                        encoding='utf-8')))

print()
print("=== B. did the Breda STATION exist before 2016 (other sensors)? ===")
# codseqst for Breda = 300004120 ; find all its sensors in the catalogue
cat = json.load(open(os.path.join(ROOT, 'raw', 'F4-arpav-rest',
                                  'meteo_sensori_dispenser.json'), encoding='utf-8'))['data']
for c in cat:
    if c.get('codseqst') == 300004120:
        print("  codseq=%-10d %-28s %s" %
              (c['codseq'], c['descrizione'], c['descrizione_annate']))

print()
print("=== C. what other sensors did WE preserve for the Breda station? ===")
per = defaultdict(lambda: [set(), set()])
for f in sorted(glob.glob(os.path.join(ROOT, 'raw', 'F4-arpav-rest',
                                       'tabella', '*.json.gz'))):
    with gzip.open(f, 'rt', encoding='utf-8') as fh:
        d = json.load(fh)
    for r in (d.get('data') or []):
        if r.get('nome_stazione', '').startswith('Breda'):
            per[r['tipo']][0].add(r['dataora'][:10])
            per[r['tipo']][1].add(os.path.basename(f))
for t, (days, fs) in sorted(per.items()):
    ds = sorted(days)
    print("  %-9s files=%2d days=%5d  %s .. %s" % (t, len(fs), len(ds), ds[0], ds[-1]))

print()
print("=== D. is 2026 truncated for EVERY station, not just Breda? ===")
held = json.load(open(os.path.join(ROOT, 'tools', '_v3_bfogl_dates.json')))
for s in sorted(held):
    y26 = sorted(d for d in held[s] if d.startswith('2026'))
    print("  %-30s 2026 days=%3d  last=%s" %
          (s, len(y26), y26[-1] if y26 else 'NONE'))
