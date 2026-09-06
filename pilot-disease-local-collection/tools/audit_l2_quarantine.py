import json, os, hashlib, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def P(*a): return os.path.join(ROOT, *a)

def rd(p):
    return [json.loads(l) for l in open(P(p), encoding='utf-8') if l.strip()]

def magic(path):
    with open(path, 'rb') as f:
        h = f.read(8)
    if h.startswith(b'%PDF'): return 'PDF'
    if h.lower().startswith(b'<') : return 'HTML'
    if h.startswith(b'\x1f\x8b'): return 'GZIP'
    if h.startswith(b'{') or h.startswith(b'['): return 'JSON'
    return 'OTHER:' + repr(h[:6])

q = P('raw/_failed-captures')
print("=== QUARANTINE raw/_failed-captures ===")
qfiles = []
for root, dirs, fs in os.walk(q):
    for f in fs:
        qfiles.append(os.path.join(root, f))
print("files quarantined:", len(qfiles))
print("magic census:", dict(collections.Counter(magic(f) for f in qfiles)))
qsha = {hashlib.sha256(open(f, 'rb').read()).hexdigest() for f in qfiles}
print("distinct sha256 in quarantine:", len(qsha))
sub = collections.Counter(os.path.relpath(os.path.dirname(f), q) for f in qfiles)
print("subdirs:", dict(sub))

FD = rd('manifests/FAILED-arpav-docs-manifest-htmlshells.jsonl')
FM = rd('manifests/FAILED-arpav-monthly-manifest-htmlshells.jsonl')
print()
print("FAILED docs manifest rows:", len(FD), "preservation:",
      collections.Counter(r.get('preservation') for r in FD))
print("FAILED monthly manifest rows:", len(FM), "preservation:",
      collections.Counter(r.get('preservation') for r in FM))
print("FAILED docs sample:", json.dumps(FD[0], ensure_ascii=False)[:600])

# does the good manifest share any sha with the failed one?
GD = rd('manifests/arpav-docs-manifest.jsonl')
GM = rd('manifests/arpav-monthly-manifest.jsonl')
gd = {r['sha256'] for r in GD}; fd = {r['sha256'] for r in FD}
gm = {r['sha256'] for r in GM}; fm = {r['sha256'] for r in FM}
print()
print("sha overlap GOOD-docs vs FAILED-docs:", len(gd & fd))
print("sha overlap GOOD-monthly vs FAILED-monthly:", len(gm & fm))
print("distinct sha in FAILED-docs:", len(fd), " in FAILED-monthly:", len(fm))

# raw-file-inventory
RI = rd('manifests/raw-file-inventory.jsonl')
print()
print("=== raw-file-inventory.jsonl ===")
print("rows:", len(RI))
print("keys:", list(RI[0].keys()))
paths = [r.get('path') or r.get('raw_path') for r in RI]
print("distinct paths:", len(set(paths)))
inq = [p for p in paths if '_failed-captures' in p.replace('\\', '/')]
print("rows pointing INTO _failed-captures:", len(inq))
top = collections.Counter(p.replace('\\', '/').split('/')[1] if p.replace('\\','/').startswith('raw/') else p.replace('\\','/').split('/')[0] for p in paths)
print("rows by top raw/ subdir:", dict(top))

# count actual files on disk under raw/
allf = []
for root, dirs, fs in os.walk(P('raw')):
    for f in fs:
        allf.append(os.path.relpath(os.path.join(root, f), ROOT).replace('\\', '/'))
print("actual files under raw/ RIGHT NOW:", len(allf))
print("inventory rows:", len(RI), "-> difference:", len(allf) - len(RI))
