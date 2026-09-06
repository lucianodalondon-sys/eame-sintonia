import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def P(*a): return os.path.join(ROOT, *a)

C = json.load(open(P('manifests/collection-manifest.json'), encoding='utf-8'))

# 1. quarantined count
q = 0
for r, d, f in os.walk(P('raw/_failed-captures')):
    q += len(f)
print("collection-manifest RAW_FILES_QUARANTINED_FAILED_CAPTURES :", C['RAW_FILES_QUARANTINED_FAILED_CAPTURES'])
print("actual files under raw/_failed-captures                    :", q)

# 2. total files on disk
n = 0
for r, d, f in os.walk(P('raw')):
    n += len(f)
print()
print("collection-manifest RAW_FILES_TOTAL_ON_DISK :", C['RAW_FILES_TOTAL_ON_DISK'])
print("actual files under raw/                     :", n)

# 3. daily gz bytes
tab = P('raw/F4-arpav-rest/tabella')
b = sum(os.path.getsize(os.path.join(tab, f)) for f in os.listdir(tab))
R = json.load(open(P('manifests/daily-series-recount.json'), encoding='utf-8'))
print()
print("collection-manifest DAILY_BYTES_ON_DISK_GZIP :", C['DAILY_BYTES_ON_DISK_GZIP'])
print("recount daily_bytes_compressed               :", R['daily_bytes_compressed'])
print("actual sum of .gz sizes in tabella/          :", b)

# 4. monthly
mm = sum(1 for l in open(P('manifests/arpav-monthly-manifest.jsonl'), encoding='utf-8') if l.strip())
md = len(os.listdir(P('raw/F7-arpav-bollettino-mese')))
mi = sum(1 for l in open(P('manifests/arpav-monthly-inventory.jsonl'), encoding='utf-8') if l.strip())
print()
print("collection-manifest MONTHLY_BULLETINS_DISCOVERED :", C['MONTHLY_BULLETINS_DISCOVERED'], " inventory lines:", mi)
print("collection-manifest MONTHLY_BULLETINS_PRESERVED  :", C['MONTHLY_BULLETINS_PRESERVED'],
      " manifest lines NOW:", mm, " files on disk NOW:", md)

# 5. recon summary
p = P('manifests/recon/_recon-summary.json')
print()
print("recon summary file:", os.path.basename(p), "exists:", os.path.exists(p))
if os.path.exists(p):
    print(json.dumps(json.load(open(p, encoding='utf-8')), ensure_ascii=False, indent=1))
print("RECON_AGENTS_* in collection-manifest:",
      C['RECON_AGENTS_STARTED'], "/", C['RECON_AGENTS_RETURNED'], "/", C['RECON_AGENTS_NOT_COMPLETED'])
