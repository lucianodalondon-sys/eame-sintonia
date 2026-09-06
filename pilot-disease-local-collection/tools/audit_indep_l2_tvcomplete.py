"""Attack the two soft spots in the reported finding:
   (a) is it 78 STATIONS or 78 SENSORS for leaf wetness?
   (b) is "within Treviso the collection is complete" true for all 5 vars,
       or only for leaf wetness?
Read-only.
"""
import json, re, os, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sens = json.load(open(os.path.join(ROOT, "raw/F4-arpav-rest/meteo_sensori_dispenser.json"),
                      encoding="utf-8"))["data"]
stat = json.load(open(os.path.join(ROOT, "raw/F4-arpav-rest/meteo_stazioni_dispenser.json"),
                      encoding="utf-8"))["data"]
TAB = os.path.join(ROOT, "raw/F4-arpav-rest/tabella")

ondisk = set()
for fn in os.listdir(TAB):
    m = re.fullmatch(r"(\d+)_(\d{4})\.json\.gz", fn)
    ondisk.add((int(m.group(1)), int(m.group(2))))

years = {r["codseq"]: [int(y) for y in re.findall(r"\b(\d{4})\b", r["descrizione_annate"])
                       if 1980 <= int(y) <= 2030] for r in sens}
by_cs = {r["codseq"]: r for r in sens}

# station province lookup
print("station record keys:", sorted(stat[0].keys()))
st = {}
for s in stat:
    key = s.get("codseq", s.get("codseqst"))
    st[key] = s

LW = "Bagnatura fogliare"
lw = [r for r in sens if r["descrizione"] == LW]
print("\n(a) leaf wetness: sensor records=%d distinct codseq=%d distinct codseqst(station)=%d distinct statnm=%d"
      % (len(lw), len({r['codseq'] for r in lw}), len({r['codseqst'] for r in lw}),
         len({r['statnm'] for r in lw})))
dup = [k for k, v in collections.Counter(r["codseqst"] for r in lw).items() if v > 1]
print("    stations carrying >1 leaf-wetness sensor:", len(dup))

# (b) per-variable Treviso completeness
held_cs = {c for c, y in ondisk}
tv_stations = {r["codseqst"] for r in sens if r["codseq"] in held_cs}
print("\n(b) distinct stations behind the 1038 held files:", len(tv_stations))

print("\n    per-variable, restricted to those same stations (the TV set):")
print("    %-30s %8s %8s %8s %8s" % ("variable", "decl.sen", "held.sen", "decl.yr", "held.yr"))
for v in sorted({by_cs[c]["descrizione"] for c in held_cs}):
    ds = [r for r in sens if r["descrizione"] == v and r["codseqst"] in tv_stations]
    dpairs = sum(len(years[r["codseq"]]) for r in ds)
    hs = [r for r in ds if r["codseq"] in held_cs]
    hpairs = len([1 for c, y in ondisk if by_cs[c]["descrizione"] == v])
    flag = "" if (len(hs) == len(ds) and hpairs == dpairs) else "   <-- NOT COMPLETE"
    print("    %-30s %8d %8d %8d %8d%s" % (v, len(ds), len(hs), dpairs, hpairs, flag))

# exact leaf-wetness TV pair check
lw_tv = [r for r in lw if r["codseqst"] in tv_stations]
lw_tv_pairs = {(r["codseq"], y) for r in lw_tv for y in years[r["codseq"]]}
lw_held = {(c, y) for c, y in ondisk if by_cs[c]["descrizione"] == LW}
print("\n    leaf-wetness TV declared pairs=%d held=%d  declared-not-held=%d held-not-declared=%d"
      % (len(lw_tv_pairs), len(lw_held), len(lw_tv_pairs - lw_held), len(lw_held - lw_tv_pairs)))

# which TV stations lack the solar sensor entirely?
SOL = "Radiazione solare globale"
sol_tv = {r["codseqst"] for r in sens if r["descrizione"] == SOL and r["codseqst"] in tv_stations}
print("    TV stations that declare a solar sensor: %d of %d" % (len(sol_tv), len(tv_stations)))
