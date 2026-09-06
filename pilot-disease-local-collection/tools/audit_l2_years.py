import json, os, re, gzip, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def P(*a): return os.path.join(ROOT, *a)
def rd(p): return [json.loads(l) for l in open(P(p), encoding='utf-8') if l.strip()]

MAN = rd('manifests/arpav-daily-manifest.jsonl')
bf = [r for r in MAN if 'agnatura' in r['sensore']]
print("leaf-wetness manifest rows:", len(bf))
print("units declared:", collections.Counter(r.get('unit') for r in bf))
print("tipo:", collections.Counter(r.get('tipo') for r in bf))
print("year span:", min(r['anno'] for r in bf), "-", max(r['anno'] for r in bf))
print("rows total (manifest field):", sum(r['rows'] for r in bf))
print()
print("=== leaf wetness: files and ROWS per year (from the manifest) ===")
per = collections.defaultdict(lambda: [0, 0])
for r in bf:
    per[r['anno']][0] += 1
    per[r['anno']][1] += r['rows']
for y in sorted(per):
    n, rw = per[y]
    print("  %d  files=%2d  rows=%6d  (14 stations would be 14 files)" % (y, n, rw))

print()
print("=== 2026 reality check ===")
y26 = [r for r in bf if r['anno'] == 2026]
print("2026 leaf-wetness files:", len(y26))
for r in sorted(y26, key=lambda r: r['stazione'])[:20]:
    print("   %-40s rows=%4d expected_days=%s missing=%s last=%s %s" %
          (r['stazione'][:40], r['rows'], r.get('expected_days'), r.get('missing_days'),
           str(r.get('last_date'))[:10], r.get('completeness')))

print()
print("=== expected_days across ALL 1038, by year ===")
ed = collections.defaultdict(collections.Counter)
for r in MAN:
    ed[r['anno']][r.get('expected_days')] += 1
for y in sorted(ed):
    print("  ", y, dict(ed[y]))

print()
print("=== station-geo.json ===")
g = json.load(open(P('manifests/station-geo.json'), encoding='utf-8'))
print("type:", type(g), "len:", len(g))
if isinstance(g, dict):
    print("keys sample:", list(g.keys())[:5])
    body = g.get('stations') or g
    print("n entries:", len(body))
print(json.dumps(g, ensure_ascii=False)[:400])
