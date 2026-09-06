"""Province-level TV denominator: is "within Treviso the collection is
complete" true for Treviso, or only for the 14 leaf-wetness stations?
Read-only.
"""
import json, re, os, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sens = json.load(open(os.path.join(ROOT, "raw/F4-arpav-rest/meteo_sensori_dispenser.json"),
                      encoding="utf-8"))["data"]
stat = json.load(open(os.path.join(ROOT, "raw/F4-arpav-rest/meteo_stazioni_dispenser.json"),
                      encoding="utf-8"))["data"]
TAB = os.path.join(ROOT, "raw/F4-arpav-rest/tabella")

st = {s["codseqst"]: s for s in stat}
ondisk = set()
for fn in os.listdir(TAB):
    m = re.fullmatch(r"(\d+)_(\d{4})\.json\.gz", fn)
    ondisk.add((int(m.group(1)), int(m.group(2))))
held_cs = {c for c, y in ondisk}
years = {r["codseq"]: [int(y) for y in re.findall(r"\b(\d{4})\b", r["descrizione_annate"])
                       if 1980 <= int(y) <= 2030] for r in sens}

print("stations per province in catalogue:",
      dict(collections.Counter(s["provincia"] for s in stat)))

TV = {s["codseqst"] for s in stat if s["provincia"] == "TV"}
print("\nTV stations in catalogue        :", len(TV))
held_stations = {r["codseqst"] for r in sens if r["codseq"] in held_cs}
print("TV stations held                :", len(held_stations & TV), "of", len(TV))

tv_sens = [r for r in sens if r["codseqst"] in TV]
tv_pairs = sum(len(years[r["codseq"]]) for r in tv_sens)
print("TV sensors declared (all vars)  :", len(tv_sens))
print("TV (sensor,year) declared       :", tv_pairs, " held:", len(ondisk),
      " -> %.2f%%" % (100.0 * len(ondisk) / tv_pairs))

print("\nTV province level, per collected variable:")
print("  %-30s %9s %7s %9s %7s" % ("variable", "TVdecl.sen", "held", "TVdecl.yr", "held.yr"))
for v in sorted({r["descrizione"] for r in sens if r["codseq"] in held_cs}):
    ds = [r for r in tv_sens if r["descrizione"] == v]
    dp = sum(len(years[r["codseq"]]) for r in ds)
    hs = [r for r in ds if r["codseq"] in held_cs]
    hp = len([1 for c, y in ondisk
              if next(x for x in sens if x["codseq"] == c)["descrizione"] == v])
    print("  %-30s %9d %7d %9d %7d   %s"
          % (v, len(ds), len(hs), dp, hp,
             "COMPLETE" if (len(hs) == len(ds) and hp == dp) else "PARTIAL"))

# how many TV stations have leaf wetness at all
lw_tv = {r["codseqst"] for r in sens
         if r["descrizione"] == "Bagnatura fogliare" and r["codseqst"] in TV}
print("\nTV stations declaring leaf wetness:", len(lw_tv),
      "| held:", len(lw_tv & held_stations))
print("TV stations WITHOUT leaf wetness  :", len(TV - lw_tv), "(none of these collected:",
      len((TV - lw_tv) & held_stations) == 0, ")")
