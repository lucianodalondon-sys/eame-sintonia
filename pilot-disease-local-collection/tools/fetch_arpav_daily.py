"""Preserve ARPAV daily historical series for the Treviso/Prosecco stations.

RAW FIRST: every response is stored byte-for-byte (gzip-wrapped) and hashed
before anything is interpreted. The manifest records what was actually
received, including short years — a year with fewer rows than days is a real
gap in the source, NOT a zero, and is recorded as such.

Read-only against the API. Resumable: already-preserved items are skipped.
"""
import gzip, hashlib, json, os, sys, time, urllib.error, urllib.request, urllib.parse
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'raw', 'F4-arpav-rest', 'tabella')
MANIFEST = os.path.join(ROOT, 'manifests', 'arpav-daily-manifest.jsonl')
JOBS = os.path.join(ROOT, 'manifests', 'arpav-jobs.json')

BASE = 'https://api.arpa.veneto.it/REST/v1/meteo_storici_tabella'
UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36')
SLEEP = 0.35


def days_in_year(y):
    return 366 if (y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)) else 365


def already_done():
    done = set()
    if os.path.exists(MANIFEST):
        with open(MANIFEST, encoding='utf-8') as f:
            for line in f:
                try:
                    r = json.loads(line)
                except Exception:
                    continue
                if r.get('preservation') == 'PRESERVED':
                    done.add((r['codseq'], r['anno']))
    return done


def fetch(codseq, anno):
    url = f'{BASE}?{urllib.parse.urlencode({"codseq": codseq, "anno": anno})}'
    req = urllib.request.Request(url, headers={
        'User-Agent': UA, 'Referer': 'https://www.arpa.veneto.it/',
        'Accept': 'application/json'})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.status, r.read(), url


def main():
    os.makedirs(OUT, exist_ok=True)
    jobs = json.load(open(JOBS, encoding='utf-8'))
    done = already_done()
    todo = [j for j in jobs if (j['codseq'], j['anno']) not in done]
    print(f'jobs={len(jobs)} already={len(done)} todo={len(todo)}', flush=True)

    ok = fail = 0
    with open(MANIFEST, 'a', encoding='utf-8') as mf:
        for i, j in enumerate(todo, 1):
            codseq, anno = j['codseq'], j['anno']
            rec = {
                'local_item_id': f'ARPAV-DAILY-{codseq}-{anno}',
                'source_id': 'ARPAV-REST-meteo_storici_tabella',
                'source_authority': 'ARPAV - Agenzia Regionale per la Prevenzione e Protezione Ambientale del Veneto',
                'access_method': 'PUBLIC_API',
                'codseqst': j['codseqst'], 'codseq': codseq, 'anno': anno,
                'stazione': j['stazione'], 'sensore': j['sensore'],
                'captured_at': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
            }
            try:
                status, raw, url = fetch(codseq, anno)
                rec['source_url'] = url
                rec['http_status'] = status
                rec['bytes'] = len(raw)
                rec['sha256'] = hashlib.sha256(raw).hexdigest()
                rec['media_type'] = 'application/json'
                d = json.loads(raw)
                rows = d.get('data') or []
                rec['api_success'] = d.get('success')
                rec['rows'] = len(rows)
                rec['expected_days'] = days_in_year(int(anno))
                rec['missing_days'] = rec['expected_days'] - len(rows)
                rec['completeness'] = 'FULL' if rec['missing_days'] == 0 else (
                    'EMPTY_NOT_ZERO' if len(rows) == 0 else 'PARTIAL_SOURCE_GAP')
                if rows:
                    rec['unit'] = rows[0].get('unitnm')
                    rec['tipo'] = rows[0].get('tipo')
                    rec['first_date'] = rows[0].get('dataora')
                    rec['last_date'] = rows[-1].get('dataora')
                    rec['aggiornamento'] = rows[0].get('aggiornamento')
                else:
                    rec['unit'] = rec['tipo'] = 'NOT_KNOWN'
                    rec['first_date'] = rec['last_date'] = 'NOT_KNOWN'
                path = os.path.join(OUT, f'{codseq}_{anno}.json.gz')
                with gzip.open(path, 'wb') as g:
                    g.write(raw)
                rec['raw_path'] = os.path.relpath(path, ROOT).replace('\\', '/')
                rec['preservation'] = 'PRESERVED'
                ok += 1
            except Exception as e:
                rec['preservation'] = 'NOT_PRESERVED'
                rec['error'] = repr(e)[:200]
                rec['rows'] = 'NOT_KNOWN'
                rec['completeness'] = 'FETCH_FAILED_NOT_ZERO'
                fail += 1
            mf.write(json.dumps(rec, ensure_ascii=False) + '\n')
            mf.flush()
            if i % 25 == 0 or i == len(todo):
                print(f'  {i}/{len(todo)} ok={ok} fail={fail}', flush=True)
            time.sleep(SLEEP)
    print(f'DONE ok={ok} fail={fail}', flush=True)


main()
