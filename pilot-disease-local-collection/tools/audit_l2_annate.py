import json, os, re, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def P(*a): return os.path.join(ROOT, *a)
def rd(p): return [json.loads(l) for l in open(P(p), encoding='utf-8') if l.strip()]

INV = rd('manifests/arpav-docs-inventory.jsonl')
MAN = rd('manifests/arpav-docs-manifest.verified.jsonl')

print("=== docs inventory: what kinds ===")
def kind(u):
    if 'annate-agrarie' in u: return 'ANNATA'
    if '/fas' in u.lower() or 'fas' in u.lower().split('/')[-1]: return 'FAS?'
    return 'OTHER'
print(collections.Counter(kind(r['download_url']) for r in INV))
print()
for r in INV:
    print("  INV", kind(r['download_url']), "|", r.get('title'), "|", r['download_url'].split('/file-e-allegati/')[-1][:80])
