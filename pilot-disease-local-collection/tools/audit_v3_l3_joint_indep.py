"""Independent re-derivation of L3 joint-coverage finding.

Reads ONLY raw/F4-arpav-rest/tabella/*.json.gz. Does not read any manifest,
does not reuse any prior audit script. Builds per (station, sensor-type) the
set of calendar days actually present in the preserved payloads, then
intersects the four variables a grape-disease model needs.
"""
import gzip, json, os, sys, datetime, collections

TAB = os.path.join(os.path.dirname(__file__), "..", "raw", "F4-arpav-rest", "tabella")
TAB = os.path.abspath(TAB)

# station -> tipo -> set(date)
present = collections.defaultdict(lambda: collections.defaultdict(set))
# same, but only days whose 'valore' is non-null / non-empty
withval = collections.defaultdict(lambda: collections.defaultdict(set))
codes = collections.defaultdict(set)
files = sorted(os.listdir(TAB))
nrows = 0
nfiles = 0
badfiles = []

for fn in files:
    if not fn.endswith(".json.gz"):
        continue
    nfiles += 1
    p = os.path.join(TAB, fn)
    try:
        with gzip.open(p, "rt", encoding="utf-8") as fh:
            d = json.load(fh)
    except Exception as e:
        badfiles.append((fn, repr(e)))
        continue
    rows = d.get("data") or []
    for r in rows:
        nrows += 1
        st = r.get("nome_stazione")
        tp = r.get("tipo")
        dt = (r.get("dataora") or "")[:10]
        if not st or not tp or not dt:
            continue
        present[st][tp].add(dt)
        codes[st].add(r.get("codice_stazione"))
        v = r.get("valore")
        if v is not None and v != "" and v != "null":
            withval[st][tp].add(dt)

print("files scanned:", nfiles, "rows:", nrows, "unreadable:", len(badfiles))
if badfiles:
    print("BAD:", badfiles[:5])

# ---- window ----
W0 = datetime.date(2014, 3, 1)
W1 = datetime.date(2025, 10, 31)
window = set()
d = W0
while d <= W1:
    window.add(d.isoformat())
    d += datetime.timedelta(days=1)
print("window days:", len(window), W0, "..", W1)

BF = "BFOGL"
stations = sorted(s for s in present if BF in present[s])
print("stations with any", BF, "preserved:", len(stations))
print()

QUAD = ["BFOGL", "TARIA2M", "UMID2M", "PREC"]
# what sensor types exist at all?
alltipi = collections.Counter()
for s in present:
    for t in present[s]:
        alltipi[t] += 1
print("sensor types across all stations:", dict(alltipi))
print()

hdr = f"{'station':34s}" + "".join(f"{t:>9s}" for t in QUAD) + f"{'ALL4':>9s}{'ALL4_pct':>10s}{'BF_pct':>9s}"
print(hdr)
rows_out = []
for s in stations:
    sets = {t: (present[s].get(t, set()) & window) for t in QUAD}
    inter = set.intersection(*[sets[t] for t in QUAD]) if all(sets.values()) else set()
    if not all(sets.values()):
        inter = set()
        # explicit: a variable with zero days in window makes the joint zero
    pct = 100.0 * len(inter) / len(window)
    bfp = 100.0 * len(sets[BF]) / len(window)
    rows_out.append((s, {t: len(sets[t]) for t in QUAD}, len(inter), pct, bfp))
    print(f"{s[:34]:34s}" + "".join(f"{len(sets[t]):9d}" for t in QUAD) +
          f"{len(inter):9d}{pct:9.2f}%{bfp:8.2f}%")

print()
for thr in (99.4, 99.0, 95.0):
    nb = sum(1 for r in rows_out if r[4] >= thr)
    na = sum(1 for r in rows_out if r[3] >= thr)
    print(f"stations with BFOGL >= {thr:5.2f} pct : {nb} of {len(rows_out)}")
    print(f"stations with ALL4  >= {thr:5.2f} pct : {na} of {len(rows_out)}")

# ---- Oderzo / Breda close-up ----
print()
for target in ("Oderzo", "Breda di Piave - Via Bovon", "Castelfranco Veneto", "Ponte di Piave"):
    m = [s for s in present if s.startswith(target)]
    for s in m:
        print("==", s, "codice_stazione:", sorted(codes[s]))
        for t in sorted(present[s]):
            ds = sorted(present[s][t])
            inw = sorted(set(ds) & window)
            print(f"   {t:9s} total_days={len(ds):5d} first={ds[0]} last={ds[-1]}"
                  f"  in_window={len(inw):5d}")
json.dump({"rows": [(r[0], r[1], r[2], r[3], r[4]) for r in rows_out]},
          open(os.path.join(os.path.dirname(__file__), "_v3_l3.json"), "w"), indent=1)
