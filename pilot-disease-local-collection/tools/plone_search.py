"""Search a Plone/Volto site via its real @search REST endpoint.

Usage: py plone_search.py <site_api_base> <term> [b_size]
Prints only what the API actually returned.
"""
import json, sys, urllib.request, urllib.parse

UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36')


def search(base, term, size=100):
    q = urllib.parse.urlencode({
        'SearchableText': term,
        'b_size': size,
        'sort_on': 'effective',
        'sort_order': 'descending',
    })
    url = f'{base.rstrip("/")}/@search?{q}&metadata_fields=effective&metadata_fields=modified'
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': 'application/json'})
    with urllib.request.urlopen(req, timeout=90) as r:
        return r.status, json.loads(r.read()), url


base = sys.argv[1]
term = sys.argv[2]
size = int(sys.argv[3]) if len(sys.argv) > 3 else 100
status, d, url = search(base, term, size)
items = d.get('items') or []
print(f'TERM="{term}" http={status} items_total={d.get("items_total")} returned={len(items)}')
print(f'URL={url}')
for it in items:
    eff = (it.get('effective') or '')[:10]
    print(f'  [{it.get("@type")}] {eff} | {it.get("title")} | {it.get("@id")}')
