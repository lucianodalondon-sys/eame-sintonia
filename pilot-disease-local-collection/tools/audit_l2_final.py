import json, os, collections, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def P(*a): return os.path.join(ROOT, *a)
def rd(p): return [json.loads(l) for l in open(P(p), encoding='utf-8') if l.strip()]

M = rd('manifests/arpav-docs-manifest.verified.jsonl')
def cat(u):
    if 'annate-agrarie' in u: return 'ANNATA'
    if 'fas-rapporti' in u: return 'FAS'
    if 'peronospora-vite' in u: return 'VINE_SLOT'
    return 'UNCATEGORISED'
c = collections.Counter(cat(r['source_url']) for r in M)
print("docs manifest by category:", dict(c), " total:", sum(c.values()))
C = json.load(open(P('manifests/collection-manifest.json'), encoding='utf-8'))
acc = C['ANNATE_DOCUMENTS_PRESERVED'] + C['FAS_REPORTS_PRESERVED'] + C['VINE_BULLETIN_SLOT_FILES_PRESERVED']
print("collection-manifest accounts for:", C['ANNATE_DOCUMENTS_PRESERVED'], "+",
      C['FAS_REPORTS_PRESERVED'], "+", C['VINE_BULLETIN_SLOT_FILES_PRESERVED'], "=", acc,
      "of", len(M), "-> unaccounted:", len(M) - acc)
for r in M:
    if cat(r['source_url']) == 'UNCATEGORISED':
        print("   UNACCOUNTED:", r['document_title'][:80], "|", r['raw_path'], "|", r['bytes'], "bytes")

print()
print("=== FINAL SNAPSHOT", datetime.datetime.now(datetime.timezone.utc).isoformat(), "===")
mi = len(rd('manifests/arpav-monthly-inventory.jsonl'))
mm = len(rd('manifests/arpav-monthly-manifest.jsonl'))
md = len(os.listdir(P('raw/F7-arpav-bollettino-mese')))
print("MONTHLY  DISCOVERED (inventory) :", mi)
print("MONTHLY  PRESERVED  (manifest)  :", mm)
print("MONTHLY  files on disk          :", md)
print("MONTHLY  gap  DISCOVERED-PRESERVED = %d  -> IN_PROGRESS, not FAILED" % (mi - mm))
print("MONTHLY  rows with preservation!=PRESERVED:",
      sum(1 for r in rd('manifests/arpav-monthly-manifest.jsonl') if r.get('preservation') != 'PRESERVED'))
