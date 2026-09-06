"""Inventory and preserve documents from a Plone/Volto site via its REST API.

Two modes:
  inventory <root...>   walk the folder tree, HEAD every File, write an inventory JSONL
  preserve  <inventory> download each inventoried file, hash it, write a manifest

RAW FIRST. Nothing is interpreted here: the manifest records the URL, the bytes,
the sha256 and the preservation state exactly as observed. Files that fail are
recorded as NOT_PRESERVED, never as absent.

Dedup is by sha256: the same PDF under two URLs is ONE document
(SAME_CONTENT_DIFFERENT_URL), not two.
"""
import hashlib, json, os, sys, time, urllib.error, urllib.parse, urllib.request
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36')
SLEEP = 0.25
B_SIZE = 500


def _req(url, method='GET'):
    return urllib.request.Request(url, method=method, headers={
        'User-Agent': UA, 'Accept': 'application/json'})


def get_json(url):
    sep = '&' if '?' in url else '?'
    with urllib.request.urlopen(_req(f'{url}{sep}b_size={B_SIZE}'), timeout=120) as r:
        return json.loads(r.read())


def head(url):
    try:
        with urllib.request.urlopen(_req(url, 'HEAD'), timeout=90) as r:
            return r.status, r.headers.get('Content-Length'), r.headers.get('Content-Type')
    except urllib.error.HTTPError as e:
        return e.code, None, None
    except Exception as e:
        return f'ERR {type(e).__name__}', None, None


def walk(url, depth, max_depth, seen, files, folders):
    if depth > max_depth or url in seen:
        return
    seen.add(url)
    try:
        d = get_json(url)
    except Exception as e:
        folders.append({'url': url, 'error': repr(e)[:150]})
        return
    items = d.get('items') or []
    folders.append({'url': url, 'title': d.get('title'), 'items_total': d.get('items_total'),
                    'returned': len(items), 'truncated': (d.get('items_total') or 0) > len(items)})
    for it in items:
        t, iid = it.get('@type'), it.get('@id')
        if t == 'File':
            files.append({'api_url': iid, 'title': it.get('title'),
                          'effective': it.get('effective'), 'modified': it.get('modified')})
        elif it.get('is_folderish') or t in ('Folder', 'Subsite', 'Document'):
            # listings do not always carry is_folderish, so trust @type too
            walk(iid, depth + 1, max_depth, seen, files, folders)
    time.sleep(SLEEP)


def cmd_inventory(out_path, roots, max_depth):
    files, folders, seen = [], [], set()
    for r in roots:
        walk(r, 0, max_depth, seen, files, folders)
    print(f'folders visited={len(folders)} files found={len(files)}', flush=True)
    trunc = [f for f in folders if f.get('truncated')]
    if trunc:
        print(f'WARNING truncated listings={len(trunc)} (raise B_SIZE)', flush=True)
        for f in trunc:
            print('   TRUNCATED', f['items_total'], f['url'], flush=True)
    for i, f in enumerate(files, 1):
        pub = f['api_url'].replace('/api/', '/', 1)
        f['public_url'] = pub
        # Volto serves the SPA shell for a bare .pdf URL; only @@download/file
        # returns the real bytes. Always use it, whatever the extension.
        f['download_url'] = pub + '/@@download/file'
        st, cl, ct = head(f['download_url'])
        f['head_status'] = st
        f['content_length'] = int(cl) if cl and str(cl).isdigit() else 'NOT_KNOWN'
        f['content_type'] = ct or 'NOT_KNOWN'
        if i % 25 == 0:
            print(f'  head {i}/{len(files)}', flush=True)
        time.sleep(SLEEP)
    with open(out_path, 'w', encoding='utf-8') as fh:
        for f in files:
            fh.write(json.dumps(f, ensure_ascii=False) + '\n')
    known = [f['content_length'] for f in files if isinstance(f['content_length'], int)]
    print(f'inventory -> {out_path}')
    print(f'files={len(files)} with_size={len(known)} total=%.1f MB' % (sum(known) / 1_048_576))


def cmd_preserve(inv_path, out_dir, manifest_path, source_id, authority):
    os.makedirs(out_dir, exist_ok=True)
    files = [json.loads(l) for l in open(inv_path, encoding='utf-8') if l.strip()]
    done_urls, hashes = set(), {}
    if os.path.exists(manifest_path):
        for l in open(manifest_path, encoding='utf-8'):
            try:
                r = json.loads(l)
            except Exception:
                continue
            if r.get('preservation') == 'PRESERVED':
                done_urls.add(r['source_url'])
                hashes.setdefault(r['sha256'], r['local_item_id'])
    todo = [f for f in files if f['download_url'] not in done_urls]
    print(f'files={len(files)} already={len(done_urls)} todo={len(todo)}', flush=True)
    ok = fail = dup = 0
    with open(manifest_path, 'a', encoding='utf-8') as mf:
        for i, f in enumerate(todo, 1):
            url = f['download_url']
            name = urllib.parse.unquote(url.rstrip('/').split('/')[-1]) or 'file'
            name = ''.join(c if c.isalnum() or c in '._-' else '_' for c in name)[:120]
            rec = {
                'local_item_id': f'{source_id}-{i:04d}-{name}',
                'source_id': source_id, 'source_authority': authority,
                'source_url': url, 'api_url': f['api_url'],
                'document_title': f.get('title'),
                'published_at': f.get('effective') or 'NOT_DECLARED',
                'modified_at': f.get('modified') or 'NOT_DECLARED',
                'captured_at': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
                'access_method': 'DIRECT_DOWNLOAD',
            }
            try:
                with urllib.request.urlopen(_req(url), timeout=180) as r:
                    raw = r.read()
                    rec['http_status'] = r.status
                    rec['media_type'] = r.headers.get('Content-Type') or 'NOT_KNOWN'
                rec['bytes'] = len(raw)
                rec['sha256'] = hashlib.sha256(raw).hexdigest()
                if rec['sha256'] in hashes:
                    rec['dedup'] = 'SAME_CONTENT_DIFFERENT_URL'
                    rec['duplicate_of'] = hashes[rec['sha256']]
                    dup += 1
                else:
                    rec['dedup'] = 'DISTINCT_DOCUMENT'
                    hashes[rec['sha256']] = rec['local_item_id']
                path = os.path.join(out_dir, f'{rec["sha256"][:12]}_{name}')
                with open(path, 'wb') as g:
                    g.write(raw)
                rec['raw_path'] = os.path.relpath(path, ROOT).replace('\\', '/')
                rec['preservation'] = 'PRESERVED'
                ok += 1
            except Exception as e:
                rec['preservation'] = 'NOT_PRESERVED'
                rec['error'] = repr(e)[:200]
                fail += 1
            mf.write(json.dumps(rec, ensure_ascii=False) + '\n')
            mf.flush()
            if i % 20 == 0 or i == len(todo):
                print(f'  {i}/{len(todo)} ok={ok} dup={dup} fail={fail}', flush=True)
            time.sleep(SLEEP)
    print(f'DONE ok={ok} dup={dup} fail={fail}', flush=True)


if sys.argv[1] == 'inventory':
    cmd_inventory(sys.argv[2], sys.argv[4:], int(sys.argv[3]))
elif sys.argv[1] == 'preserve':
    cmd_preserve(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6])
