import json, os, gzip, collections, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def P(*a): return os.path.join(ROOT, *a)
def rd(p): return [json.loads(l) for l in open(P(p), encoding='utf-8') if l.strip()]

MAN = rd('manifests/arpav-daily-manifest.jsonl')
bf = [r for r in MAN if 'agnatura' in r['sensore']]

# sample payload
s = json.loads(gzip.decompress(open(P(bf[0]['raw_path']), 'rb').read()).decode('utf-8'))
print("sample leaf-wetness payload keys:", list(s.keys()))
print("meta:", json.dumps(s.get('meta'), ensure_ascii=False)[:300])
print("first 2 data rows:", json.dumps(s['data'][:2], ensure_ascii=False))

# unit: is it in the payload or only in the catalogue?
units = set()
for r in bf[:40]:
    d = json.loads(gzip.decompress(open(P(r['raw_path']), 'rb').read()).decode('utf-8'))
    for row in d['data'][:3]:
        for k, v in row.items():
            if 'unit' in k.lower() or 'misura' in k.lower():
                units.add((k, v))
print("unit-ish fields found inside payloads:", units)

# C4 window recount, from the FILES
W0 = datetime.date(2014, 3, 1); W1 = datetime.date(2025, 10, 31)
NDAYS = (W1 - W0).days + 1
print()
print("=== C4 window %s..%s = %d days ===" % (W0, W1, NDAYS))
per = collections.defaultdict(set)
for r in bf:
    d = json.loads(gzip.decompress(open(P(r['raw_path']), 'rb').read()).decode('utf-8'))
    for row in d['data']:
        ds = str(row.get('dataora') or '')[:10]
        try:
            dt = datetime.date(int(ds[:4]), int(ds[5:7]), int(ds[8:10]))
        except Exception:
            continue
        if W0 <= dt <= W1:
            per[r['stazione']].add(dt)
ge = 0
for st in sorted(per, key=lambda k: -len(per[k])):
    pct = 100.0 * len(per[st]) / NDAYS
    if pct >= 99.4: ge += 1
    print("  %-42s %5d/%d  %6.2f%%" % (st[:42], len(per[st]), NDAYS, pct))
print("stations >= 99.4%%: %d of %d" % (ge, len(per)))

print()
print("=== station-geo.json / geo manifest ===")
g = json.load(open(P('manifests/station-geo.json'), encoding='utf-8'))
for k in g:
    v = g[k]
    print("  %s : %s" % (k, len(v) if isinstance(v, (list, dict)) else v))
GM = rd('manifests/arpav-geo-manifest.jsonl')
print("geo manifest rows:", len(GM))
for r in GM:
    print("   ", r.get('local_item_id'), r.get('raw_path'), r.get('bytes'), r.get('preservation'))
