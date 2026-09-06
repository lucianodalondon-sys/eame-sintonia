import json, hashlib, os, collections

ROOT = r'C:\disease-local-collection-italy\pilot-disease-local-collection'

# hash every file under raw/ myself (ground truth), excluding nothing
allfiles = []
for dp, dn, fn in os.walk(os.path.join(ROOT, 'raw')):
    for f in fn:
        p = os.path.join(dp, f)
        rel = os.path.relpath(p, ROOT).replace('\\', '/')
        b = open(p, 'rb').read()
        allfiles.append((rel, hashlib.sha256(b).hexdigest(), len(b), os.path.splitext(f)[1].lower()))

print('TOTAL files under raw/ :', len(allfiles))
print('TOTAL distinct sha256  :', len({x[1] for x in allfiles}))
print('redundant byte-copies  :', len(allfiles) - len({x[1] for x in allfiles}))
print()

def part(pred, label):
    s = [x for x in allfiles if pred(x)]
    print('%-52s files=%5d distinct_sha=%5d' % (label, len(s), len({x[1] for x in s})))
    return s

q = part(lambda x: x[0].startswith('raw/_failed-captures/'), 'quarantined failed captures (HTML shells)')
tools = part(lambda x: x[3] == '.py', "collector's own .py tool scripts")
f8 = part(lambda x: x[0].startswith('raw/F8-'), 'F8 ARPAV agrometeo docs (PDF)')
f7 = part(lambda x: x[0].startswith('raw/F7-'), 'F7 monthly bulletins (download IN PROGRESS)')
daily = part(lambda x: x[0].startswith('raw/F4-arpav-rest/tabella/'), 'F4 daily API responses (.json.gz)')
recon = part(lambda x: x[0].split('/')[1].startswith(('F1', 'F2', 'F3', 'F5', 'F6')), 'recon fronts F1/F2/F3/F5/F6')

print()
print('--- CORRECTED HEADLINE NUMBERS -----------------------------------')
keep = [x for x in allfiles
        if not x[0].startswith('raw/_failed-captures/') and x[3] != '.py']
print('files under raw/ that are neither quarantine nor tool script:', len(keep))
print('  ...of which distinct by sha256                            :', len({x[1] for x in keep}))
print('  ...redundant copies inside that set                       :', len(keep) - len({x[1] for x in keep}))
print()
print('DISTINCT DAILY SERIES (station x sensor x year), recomputed  :',
      len({x[0] for x in daily}), 'files /', len({x[1] for x in daily}), 'distinct sha256')
print('DISTINCT PRESERVED SOURCE DOCUMENTS (F8 PDFs), recomputed    :', len({x[1] for x in f8}))
print('  ...but rows claiming PRESERVED for those 46 docs           : 92 (46 real + 46 quarantined shells)')
print()

# does any F8 pdf also live in a recon folder (same document counted on two fronts)?
f8sha = {x[1] for x in f8}
rsha = collections.defaultdict(list)
for x in recon:
    rsha[x[1]].append(x[0])
inter = f8sha & set(rsha)
print('F8 documents that ALSO exist byte-identical in a recon folder:', len(inter))
for s in inter:
    print('   ', s[:12], [y[0] for y in f8 if y[1] == s], rsha[s])

# cross-front duplicates inside recon
c = collections.Counter(x[1] for x in recon)
d = {k: v for k, v in c.items() if v > 1}
print()
print('recon-front byte-identical duplicates: %d hashes, %d files, %d redundant copies'
      % (len(d), sum(d.values()), sum(v - 1 for v in d.values())))
byfronts = collections.Counter()
for k in d:
    fronts = tuple(sorted({y[0].split('/')[1] for y in recon if y[1] == k}))
    byfronts[fronts] += 1
for k, v in byfronts.most_common():
    print('   ', v, 'hash(es) shared across fronts', k)
