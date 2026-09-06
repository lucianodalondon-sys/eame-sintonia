import json, re, glob, subprocess, datetime, os

ts = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
VINE_RE = re.compile(r'vite|vigne|viticol|vitivinic|uva|uve|vendemmia|vitigni|'
                     r'flavescenza|vitat', re.I)
FALSE_RE = re.compile(r'vitello|vitelli', re.I)

vd = json.load(open('term_vite.json', encoding='utf-8'))
tot = len(vd)
fp = [v for v in vd.values() if FALSE_RE.search((v.get('title') or '') +
                                                (v.get('name') or '') +
                                                (v.get('path') or ''))]
print('term_vite union entities:', tot)
print('proven substring false positives (vitello/veal):', len(fp))
for v in fp:
    print('   -', (v.get('title') or v.get('name')), '|', v.get('path'))

od = json.load(open('term_oidio.json', encoding='utf-8'))
cereal = [v for v in od.values()
          if 'Colture Erbacee' in (v.get('path') or '')]
print('\nterm_oidio union entities:', len(od))
print(' under /Newsletter/Bollettino Colture Erbacee (cereal):', len(cereal))
vine_oidio = [v for v in od.values() if VINE_RE.search((v.get('title') or '') +
                                                       (v.get('name') or ''))]
print(' vine-titled oidio entities:', len(vine_oidio))
for v in vine_oidio:
    print('   -', (v.get('title') or v.get('name'))[:80])

man = {
    'front': 'F2b-vagri-vite',
    'collected_at_utc': ts,
    'site': 'https://www.venetoagricoltura.org',
    'platform': 'Regione Veneto myPortal (Angular SPA), ipa=AVPISP, rootPortal=true',
    'api_base': 'https://www.venetoagricoltura.org/myportal/AVPISP/api',
    'downloads': json.load(open('downloads.json', encoding='utf-8')),
    'vine_posts': json.load(open('vineprobe.json', encoding='utf-8'))['posts'],
    'vine_pdfs': json.load(open('vineprobe.json', encoding='utf-8'))['pdfs'],
    'counts': json.load(open('counts.json', encoding='utf-8')),
}
out = (r'C:\disease-local-collection-italy\pilot-disease-local-collection'
       r'\manifests\F2b-vagri-vite.json')
os.makedirs(os.path.dirname(out), exist_ok=True)
json.dump(man, open(out, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
print('\nmanifest written:', out, os.path.getsize(out), 'bytes at', ts)
