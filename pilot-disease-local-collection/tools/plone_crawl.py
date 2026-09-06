"""Walk a Plone/Volto folder tree through its real REST API and list what is
actually there. No guessing: every path printed came back from the API.

Usage: py plone_crawl.py <api_folder_url> [max_depth] [--files-only]
"""
import json, sys, urllib.request, urllib.parse

UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36')


def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': 'application/json'})
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.loads(r.read())


def walk(url, depth, max_depth, seen, out):
    if depth > max_depth or url in seen:
        return
    seen.add(url)
    try:
        d = get(url)
    except Exception as e:
        out.append(('ERROR', depth, url, repr(e)[:100]))
        return
    items = d.get('items') or []
    for it in items:
        t = it.get('@type')
        iid = it.get('@id')
        title = it.get('title')
        out.append((t, depth, iid, title))
        if it.get('is_folderish') and t in ('Folder', 'Document', 'Subsite'):
            walk(iid, depth + 1, max_depth, seen, out)


root = sys.argv[1]
max_depth = int(sys.argv[2]) if len(sys.argv) > 2 else 2
files_only = '--files-only' in sys.argv

out = []
walk(root, 0, max_depth, set(), out)
for t, depth, iid, title in out:
    if files_only and t != 'File':
        continue
    print(f'{"  " * depth}[{t}] {title} | {iid}')
print(f'--- total entries: {len(out)}')
