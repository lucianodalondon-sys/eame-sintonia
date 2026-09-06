import os, hashlib, json
q = 'raw/_failed-captures'
tot = 0
shells = 0
qsh = set()
for root, _, fs in os.walk(q):
    for f in fs:
        p = os.path.join(root, f)
        b = open(p, 'rb').read()
        tot += 1
        qsh.add(hashlib.sha256(b).hexdigest())
        if b[:5] != b'%PDF-':
            shells += 1
print("quarantined files:", tot, " non-PDF (html shells):", shells, " distinct sha:", len(qsh))
good = {json.loads(l)['sha256'] for l in open('manifests/arpav-docs-manifest.verified.jsonl', encoding='utf-8')}
ov = qsh & good
print("overlap quarantined sha vs 46 preserved sha:", len(ov), "-> NO double-count" if not ov else "*** DOUBLE COUNT ***")
