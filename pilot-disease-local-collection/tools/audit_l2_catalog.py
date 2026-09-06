import json, re, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def P(*a): return os.path.join(ROOT, *a)

sens = json.load(open(P('raw/F4-arpav-rest/meteo_sensori_dispenser.json'), encoding='utf-8'))['data']
print("catalogue sensors:", len(sens))

cat = set()
no_annate = 0
sensor_years = {}
for s in sens:
    da = s.get('descrizione_annate')
    if not da:
        no_annate += 1
        sensor_years[s['codseq']] = set()
        continue
    ys = {int(m.group(0)) for m in re.finditer(r'\b(?:19|20)\d{2}\b', da)}
    sensor_years[s['codseq']] = ys
    for y in ys:
        cat.add((s['codseq'], y))
print("sensors with NO descrizione_annate:", no_annate)
print("catalogue-declared (sensor,year) pairs:", len(cat))
print("distinct sensors with >=1 declared year:", len({c for c, _ in cat}))

tab = P('raw/F4-arpav-rest/tabella')
files = sorted(os.listdir(tab))
print("files in tabella/:", len(files))
disk = set()
bad = []
for f in files:
    m = re.fullmatch(r'(\d+)_(\d{4})\.json\.gz', f)
    if not m:
        bad.append(f)
        continue
    disk.add((int(m.group(1)), int(m.group(2))))
print("parsed (sensor,year) on disk:", len(disk), "unparsed names:", len(bad), bad[:5])

print()
print("=== SET DIFFERENCE BOTH WAYS (whole catalogue) ===")
print("A) catalogue-declared but NOT on disk:", len(cat - disk))
print("B) on disk but NOT catalogue-declared:", len(disk - cat))
for x in sorted(disk - cat)[:40]:
    print("   B:", x)

json.dump({"cat": sorted("%d_%d" % t for t in cat),
           "disk": sorted("%d_%d" % t for t in disk),
           "sensor_years": {str(k): sorted(v) for k, v in sensor_years.items()}},
          open(P('tools', '_l2_sets.json'), 'w'), indent=0)
print("wrote tools/_l2_sets.json")
