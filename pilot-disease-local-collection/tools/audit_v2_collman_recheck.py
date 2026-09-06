"""Independent re-check of the L2 collection-manifest finding.

Does NOT trust the other auditor. Recomputes every number from the files.
Read-only: touches nothing under raw/ or manifests/.
"""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def P(*a): return os.path.join(ROOT, *a)

C = json.load(open(P('manifests/collection-manifest.json'), encoding='utf-8'))

print("=== 1. MANIFEST AS IT STANDS NOW ===")
print("BUILT_AT :", C['BUILT_AT'])
for k in ('RAW_FILES_TOTAL_ON_DISK', 'RAW_FILES_SOURCE_DOCUMENTS',
          'RAW_FILES_TOOLING_SCRIPTS_EXCLUDED',
          'RAW_FILES_QUARANTINED_FAILED_CAPTURES'):
    print(f"{k:38}", C[k])
print("gzip key present as GZIP     :", 'DAILY_BYTES_ON_DISK_GZIP' in C)
print("gzip key present as GZIPPED  :", 'DAILY_BYTES_ON_DISK_GZIPPED' in C)
print("DAILY_BYTES_ON_DISK_GZIPPED  :", C.get('DAILY_BYTES_ON_DISK_GZIPPED'))
print("RECON_AGENTS S/R/N           :", C['RECON_AGENTS_STARTED'], '/',
      C['RECON_AGENTS_RETURNED'], '/', C['RECON_AGENTS_NOT_COMPLETED'])

print()
print("=== 2. WALK THE DISK MYSELF ===")
q = sum(len(f) for _, _, f in os.walk(P('raw/_failed-captures')))
n = sum(len(f) for _, _, f in os.walk(P('raw')))
tab = P('raw/F4-arpav-rest/tabella')
gz = [f for f in os.listdir(tab) if f.endswith('.json.gz')]
b = sum(os.path.getsize(os.path.join(tab, f)) for f in gz)
print("files under raw/_failed-captures :", q, " -> manifest says",
      C['RAW_FILES_QUARANTINED_FAILED_CAPTURES'],
      "MATCH" if q == C['RAW_FILES_QUARANTINED_FAILED_CAPTURES'] else "MISMATCH")
print("files under raw/                 :", n, " -> manifest says",
      C['RAW_FILES_TOTAL_ON_DISK'],
      "MATCH" if n == C['RAW_FILES_TOTAL_ON_DISK'] else "MISMATCH")
print(".json.gz in tabella/             :", len(gz), "files,", b, "bytes -> manifest says",
      C.get('DAILY_BYTES_ON_DISK_GZIPPED'),
      "MATCH" if b == C.get('DAILY_BYTES_ON_DISK_GZIPPED') else "MISMATCH")
R = json.load(open(P('manifests/daily-series-recount.json'), encoding='utf-8'))
print("recount daily_bytes_compressed   :", R['daily_bytes_compressed'],
      "MATCH" if R['daily_bytes_compressed'] == b else "MISMATCH")

print()
print("=== 3. DO THE PARTS ADD UP TO THE WHOLE? ===")
parts = (C['RAW_FILES_SOURCE_DOCUMENTS'] + C['RAW_FILES_TOOLING_SCRIPTS_EXCLUDED']
         + C['RAW_FILES_QUARANTINED_FAILED_CAPTURES'])
print(f"{C['RAW_FILES_SOURCE_DOCUMENTS']} docs + "
      f"{C['RAW_FILES_TOOLING_SCRIPTS_EXCLUDED']} tooling + "
      f"{C['RAW_FILES_QUARANTINED_FAILED_CAPTURES']} quarantined = {parts}"
      f"  vs TOTAL {C['RAW_FILES_TOTAL_ON_DISK']}",
      "OK" if parts == C['RAW_FILES_TOTAL_ON_DISK'] else "DOES NOT ADD UP")

print()
print("=== 4. ARE THE 182 REALLY HTML SHELLS, AND ARE THEY DOUBLE-COUNTED? ===")
rows = [json.loads(l) for l in open(P('manifests/raw-file-inventory.jsonl'), encoding='utf-8') if l.strip()]
print("raw-file-inventory rows:", len(rows))
qrows = [r for r in rows if r['raw_path'].startswith('raw/_failed-captures/')]
others = [r for r in rows if not r['raw_path'].startswith('raw/_failed-captures/')]
print("  inventory rows in quarantine  :", len(qrows))
print("  distinct sha256 among them    :", len({r['sha256'] for r in qrows}))
print("  quarantine hashes ALSO seen outside quarantine:",
      len({r['sha256'] for r in qrows} & {r['sha256'] for r in others}))

magic = {}
for r in qrows:
    fp = P(r['raw_path'].replace('/', os.sep))
    with open(fp, 'rb') as fh:
        head = fh.read(16)
    if head[:5] in (b'<!DOC', b'<!doc') or head[:5] == b'<html' or head[:6] == b'<?xml ':
        k = 'HTML/XML-ish'
    elif head[:4] == b'%PDF':
        k = 'PDF'
    else:
        k = repr(head[:8])
    magic[k] = magic.get(k, 0) + 1
print("  magic-byte classes of the 182 :", magic)

print()
print("=== 5. IS THE QUARANTINED FAILURE COUNTED AS PRESERVED ANYWHERE? ===")
for name, key in (('arpav-docs-manifest.verified.jsonl', None),
                  ('arpav-monthly-manifest.verified.jsonl', None)):
    p = P('manifests', name)
    if not os.path.exists(p):
        print(f"  {name}: ABSENT")
        continue
    rs = [json.loads(l) for l in open(p, encoding='utf-8') if l.strip()]
    bad = [r for r in rs if '_failed-captures' in json.dumps(r)]
    print(f"  {name}: {len(rs)} rows, rows pointing into _failed-captures: {len(bad)}")

print()
print("=== 6. RECON SUMMARY FILE ===")
p = P('manifests/recon/_recon-summary.json')
print("  _recon-summary.json exists  :", os.path.exists(p))
print("  _recount-summary.json exists:", os.path.exists(P('manifests/recon/_recount-summary.json')))
if os.path.exists(p):
    S = json.load(open(p, encoding='utf-8'))
    print("  started/returned/not_completed:", S['agents_started'], S['agents_returned_result'], S['agents_not_completed'])
    print("  manifest agrees:",
          (S['agents_started'], S['agents_returned_result'], S['agents_not_completed'])
          == (C['RECON_AGENTS_STARTED'], C['RECON_AGENTS_RETURNED'], C['RECON_AGENTS_NOT_COMPLETED']))

print()
print("=== 7. TIMESTAMPS: WAS THE MANIFEST REBUILT AFTER THE FINDING? ===")
import datetime
for f in ('manifests/collection-manifest.json', 'tools/build_collection_manifest.py',
          'tools/audit_l2_collman.py', 'manifests/raw-file-inventory.jsonl'):
    t = datetime.datetime.fromtimestamp(os.path.getmtime(P(f)), datetime.timezone.utc)
    print(" ", t.strftime('%Y-%m-%dT%H:%M:%SZ'), f)
