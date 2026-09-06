"""INDEPENDENT check: do the two documents that both declare year 2005 really
cover the same year, or are they different scopes that merely share a number?

Compares 'Annata agraria 2004-05' (43f16a311441) vs 'annata agraria 2005'
(9ebef6b56e99). Read-only.
"""
import re, subprocess, os
from collections import Counter

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
D = os.path.join(ROOT, 'raw', 'F8-arpav-agrometeo-docs')

A = ('TITLE "Annata agraria 2004-05"', os.path.join(D, '43f16a311441_file'))
B = ('TITLE "annata agraria 2005"', os.path.join(D, '9ebef6b56e99_file'))

MONTHS = ('gennaio febbraio marzo aprile maggio giugno luglio agosto '
          'settembre ottobre novembre dicembre').split()
MRE = '|'.join(MONTHS)


def text(p):
    o = subprocess.run(['pdftotext', p, '-'], capture_output=True)
    return o.stdout.decode('latin-1', 'replace')


def norm(s):
    s = s.replace('’', "'").replace('�', 'e')
    s = re.sub(r'[^a-z0-9 ]+', ' ', s.lower())
    return re.sub(r'\s+', ' ', s).strip()


def sentences(t):
    flat = re.sub(r'\s+', ' ', t)
    return [norm(s) for s in re.split(r'(?<=[.!?])\s+', flat)]


docs = {}
for label, p in (A, B):
    t = text(p)
    flat = re.sub(r'\s+', ' ', t)
    yrs = Counter(re.findall(r'\b(?:19|20)\d{2}\b', flat))
    my = Counter(y for _, y in re.findall(r'\b(%s)\s+((?:19|20)\d{2})\b' % MRE, flat, re.I))
    docs[label] = dict(text=t, flat=flat, sents=sentences(t), yrs=yrs, my=my)
    print('=' * 78)
    print(label)
    print('  chars                :', len(t))
    print('  all 4-digit years    :', dict(yrs.most_common(8)))
    print('  "<month> <year>" hits:', dict(my))
    print('  header               :', flat[:150])

sa = set(s for s in docs[A[0]]['sents'] if len(s) > 60)
sb = set(s for s in docs[B[0]]['sents'] if len(s) > 60)
shared = sa & sb
print()
print('=' * 78)
print('long sentences (>60 chars):  A=%d  B=%d  shared verbatim=%d'
      % (len(sa), len(sb), len(shared)))
for s in sorted(shared):
    print('   SHARED:', s[:150])

# looser: shared 8-word shingles, to catch reflow/typo differences
def shingles(sents, n=8):
    out = set()
    for s in sents:
        w = s.split()
        for i in range(len(w) - n + 1):
            out.add(' '.join(w[i:i + n]))
    return out

ga, gb = shingles(docs[A[0]]['sents']), shingles(docs[B[0]]['sents'])
inter = ga & gb
print()
print('8-word shingles: A=%d B=%d shared=%d  (%.1f%% of A, %.1f%% of B)'
      % (len(ga), len(gb), len(inter),
         100.0 * len(inter) / max(1, len(ga)), 100.0 * len(inter) / max(1, len(gb))))
for s in sorted(inter)[:12]:
    print('   ', s)

# does either doc cover months outside Jan-Nov 2005?
print()
for label in (A[0], B[0]):
    print(label, '-> months named with a year:', dict(docs[label]['my']))
