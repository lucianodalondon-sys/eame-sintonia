import json, hashlib, os, urllib.request

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36")
API = "https://www.venetoagricoltura.org/myportal/AVPISP/api"
OUT = r"C:\disease-local-collection-italy\pilot-disease-local-collection\raw\F2b"
os.makedirs(OUT, exist_ok=True)

# 6 samples: 4 vine-disease documents, 1 vine season report, 1 falsification control
SAMPLES = [
    ("69442384a4809a008b19c1e6", "La_Flavescenza_dorata_in_Veneto.pdf",
     "vine flavescenza dorata monograph 1994-2004 (DIFESA FITOSANITARIA)"),
    ("6a6b1a0f0b00000000000000", "PLACEHOLDER", "skip"),
]

if __name__ == "__main__":
    vp = json.load(open('vineprobe.json', encoding='utf-8'))
    want = [
        "La Flavescenza dorata in Veneto.pdf",
        "3_FORNASIERO Diego FITOSANTARIO RV pubblicabili.pdf",
        "Report sulle Previsioni vendemmiali 2026.pdf (1)",
        "Report sulle Previsioni vendemmiali 2025.pdf",
        "1_RECH Francesco ARPAV.pdf",
    ]
    picked = []
    seen = set()
    for w in want:
        for p in vp['pdfs']:
            if p['name'] == w and p['uuid'] not in seen:
                picked.append(p)
                seen.add(p['uuid'])
                break
    # 6th: falsification control - an OIDIO pdf from Bollettino Colture Erbacee
    picked.append({'uuid': '69ce74fb6180d9008de5f0ed', 'name': 'OIDIO.pdf',
                   'url': API + '/content/download?id=69ce74fb6180d9008de5f0ed',
                   'parent_title': 'Bollettino Colture Erbacee 2026 BCE 21 020426 '
                                   '(CONTROL: cereal, not vine)'})
    man = []
    for p in picked:
        url = p['url']
        fn = "".join(c if c.isalnum() or c in '._-' else '_' for c in p['name'])
        dest = os.path.join(OUT, fn)
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=180) as r:
            data = r.read()
            status = r.status
            ct = r.headers.get('Content-Type', '')
        open(dest, 'wb').write(data)
        sha = hashlib.sha256(data).hexdigest()
        magic = data[:5].decode('latin-1')
        man.append({'url': url, 'name': p['name'], 'raw_path': dest,
                    'http_status': str(status), 'bytes': len(data), 'sha256': sha,
                    'content_type': ct, 'magic': magic,
                    'parent_title': p.get('parent_title'),
                    'parent_url': p.get('parent_url')})
        print(status, len(data), magic, sha[:16], fn, flush=True)
    json.dump(man, open('downloads.json', 'w', encoding='utf-8'), indent=1,
              ensure_ascii=False)
