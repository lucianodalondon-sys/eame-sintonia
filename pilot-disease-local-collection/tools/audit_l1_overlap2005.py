import os, re, subprocess, difflib, collections

D = r'C:\disease-local-collection-italy\pilot-disease-local-collection\raw\F8-arpav-agrometeo-docs'
pairs = {
    'TITLE "Annata agraria 2004-05"': '43f16a311441_file',
    'TITLE "annata agraria 2005"': '9ebef6b56e99_file',
    'TITLE "Annata agraria 2000-01"': '7f24860c40b2_file',
    'TITLE "Annata agraria 2003-04"': 'c12a48e9b65d_file',
}
txt = {}
for k, f in pairs.items():
    out = subprocess.run(['pdftotext', '-layout', os.path.join(D, f), '-'], capture_output=True)
    t = out.stdout.decode('latin1', 'replace')
    txt[k] = t
    print('=' * 78)
    print(k, '  file:', f, '  chars:', len(t))
    # which calendar years does the body actually talk about, by month-year pairs
    my = re.findall(r'(?i)(gennaio|febbraio|marzo|aprile|maggio|giugno|luglio|agosto|settembre|ottobre|novembre|dicembre)\s+(19\d\d|20\d\d)', t)
    c = collections.Counter(y for m, y in my)
    print('   month+year mentions by year:', dict(sorted(c.items())))
    print('   all 4-digit years, counted:', dict(sorted(collections.Counter(re.findall(r'\b(19\d\d|20\d\d)\b', t)).items())))
    hdr = re.sub(r'\s+', ' ', t[:400]).strip()
    print('   header:', hdr[:200])

print()
print('=' * 78)
a = re.sub(r'\s+', ' ', txt['TITLE "Annata agraria 2004-05"'])
b = re.sub(r'\s+', ' ', txt['TITLE "annata agraria 2005"'])
print('overlap test between the 2004-05 doc and the 2005 doc')
print('  len a =', len(a), ' len b =', len(b))
print('  difflib ratio (quick) =', round(difflib.SequenceMatcher(None, a[:20000], b[:20000]).quick_ratio(), 3))
# shared long sentences
sa = {s.strip() for s in re.split(r'[.;]\s', a) if len(s.strip()) > 60}
sb = {s.strip() for s in re.split(r'[.;]\s', b) if len(s.strip()) > 60}
sh = sa & sb
print('  long sentences (>60 chars) shared verbatim:', len(sh))
for s in list(sh)[:5]:
    print('     ', s[:150])
