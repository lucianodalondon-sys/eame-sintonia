"""Robustness attacks on the L3 joint-coverage finding.

1. Are 'present days' also 'days with a value'? (if not, joint is even lower)
2. Does any station name hide two different codice_stazione (merge artefact)?
3. Does the conclusion survive a growing-season-only window (Apr 1 - Sep 30)?
4. Decompose: how many stations does the JOINT requirement actually cost,
   versus how many were already short on leaf wetness alone?
"""
import gzip, json, os, datetime, collections

TAB = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "raw",
                                   "F4-arpav-rest", "tabella"))
present = collections.defaultdict(lambda: collections.defaultdict(set))
withval = collections.defaultdict(lambda: collections.defaultdict(set))
codes = collections.defaultdict(collections.Counter)
nullrows = collections.Counter()
dupday = collections.Counter()

for fn in sorted(os.listdir(TAB)):
    if not fn.endswith(".json.gz"):
        continue
    with gzip.open(os.path.join(TAB, fn), "rt", encoding="utf-8") as fh:
        d = json.load(fh)
    for r in d.get("data") or []:
        st, tp = r.get("nome_stazione"), r.get("tipo")
        dt = (r.get("dataora") or "")[:10]
        if not (st and tp and dt):
            continue
        if dt in present[st][tp]:
            dupday[(st, tp)] += 1
        present[st][tp].add(dt)
        codes[st][r.get("codice_stazione")] += 1
        v = r.get("valore")
        if v is None or v == "" or v == "null" or v == "{}":
            nullrows[(st, tp)] += 1
        else:
            withval[st][tp].add(dt)

QUAD = ["BFOGL", "TARIA2M", "UMID2M", "PREC"]
stations = sorted(s for s in present if "BFOGL" in present[s])

print("=== 1. rows with empty/null 'valore' among the 14 leaf-wetness stations ===")
tot = sum(n for (s, t), n in nullrows.items() if s in stations)
print("null/empty valore rows:", tot)
print("days present but without a value, per station/tipo:")
anygap = False
for s in stations:
    for t in QUAD:
        g = len(present[s][t]) - len(withval[s][t])
        if g:
            anygap = True
            print(f"   {s:30s} {t:8s} {g}")
if not anygap:
    print("   (none - present-day == valued-day everywhere)")

print()
print("=== 2. station-name -> codice_stazione (merge artefact check) ===")
bad = [(s, dict(codes[s])) for s in stations if len(codes[s]) != 1]
print("stations whose name maps to >1 codice_stazione:", bad if bad else "NONE")
print("duplicate (station,tipo,day) rows:", sum(dupday.values()) or "NONE")

print()
print("=== 3. windows ===")


def daysin(a, b):
    out, d = set(), a
    while d <= b:
        out.add(d.isoformat())
        d += datetime.timedelta(days=1)
    return out


def season(y0, y1, m0, d0, m1, d1):
    out = set()
    for y in range(y0, y1 + 1):
        out |= daysin(datetime.date(y, m0, d0), datetime.date(y, m1, d1))
    return out


windows = {
    "FULL 2014-03-01..2025-10-31": daysin(datetime.date(2014, 3, 1),
                                          datetime.date(2025, 10, 31)),
    "GROWING Apr1-Sep30 2014-2025": season(2014, 2025, 4, 1, 9, 30),
    "GROWING Mar15-Oct15 2014-2025": season(2014, 2025, 3, 15, 10, 15),
}

for wname, W in windows.items():
    print(f"\n--- {wname}  ({len(W)} days) ---")
    bf_ok = joint_ok = 0
    fails_bf, fails_joint = [], []
    for s in stations:
        sets = {t: present[s].get(t, set()) & W for t in QUAD}
        inter = set.intersection(*sets.values()) if all(sets.values()) else set()
        bfp = 100.0 * len(sets["BFOGL"]) / len(W)
        jp = 100.0 * len(inter) / len(W)
        if bfp >= 99.4:
            bf_ok += 1
        else:
            fails_bf.append((s, round(bfp, 2)))
        if jp >= 99.4:
            joint_ok += 1
        else:
            fails_joint.append((s, round(jp, 2), len(inter)))
    print(f"  BFOGL alone >=99.4%: {bf_ok}/14   fails: {fails_bf}")
    print(f"  ALL4 joint  >=99.4%: {joint_ok}/14   fails: {fails_joint}")

print()
print("=== 4. decomposition on the FULL window: who does the JOIN actually cost? ===")
W = windows["FULL 2014-03-01..2025-10-31"]
need = 0.994 * len(W)
print(f"  99.4% of {len(W)} days = {need:.2f}  -> need >= {int(-(-need//1))} days")
for s in stations:
    sets = {t: present[s].get(t, set()) & W for t in QUAD}
    inter = set.intersection(*sets.values())
    bf, jn = len(sets["BFOGL"]), len(inter)
    tag = ("ok->ok" if bf >= need and jn >= need else
           "OK->FAIL (cost of the join)" if bf >= need else
           "FAIL->FAIL (already short on leaf wetness alone)")
    print(f"  {s:30s} BFOGL={bf:5d} ALL4={jn:5d} lost_to_join={bf-jn:4d}  {tag}")
