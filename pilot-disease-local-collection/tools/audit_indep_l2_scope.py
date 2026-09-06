"""Independent re-derivation of the catalogue-declared vs preserved ratio.

Written from scratch for the verification pass. Does NOT read any prior
auditor's script or cached output. Read-only: touches raw/ and manifests/
for reading only.
"""
import json
import re
import os
import gzip
import collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SENS = os.path.join(ROOT, "raw", "F4-arpav-rest", "meteo_sensori_dispenser.json")
STAT = os.path.join(ROOT, "raw", "F4-arpav-rest", "meteo_stazioni_dispenser.json")
TAB = os.path.join(ROOT, "raw", "F4-arpav-rest", "tabella")

sens = json.load(open(SENS, encoding="utf-8"))["data"]
stat = json.load(open(STAT, encoding="utf-8"))["data"]

# ---- 1. catalogue-declared (codseq, year) pairs -------------------------
declared = set()
years_by_sensor = {}
for r in sens:
    ys = [int(y) for y in re.findall(r"\b(\d{4})\b", r["descrizione_annate"])]
    ys = [y for y in ys if 1980 <= y <= 2030]
    years_by_sensor[r["codseq"]] = ys
    for y in ys:
        declared.add((r["codseq"], y))

print("catalogue sensor records            :", len(sens))
print("catalogue distinct codseq           :", len({r["codseq"] for r in sens}))
print("catalogue-declared (codseq,year)    :", len(declared))

# ---- 2. what is actually on disk ---------------------------------------
ondisk = set()
bad = []
for fn in os.listdir(TAB):
    m = re.fullmatch(r"(\d+)_(\d{4})\.json\.gz", fn)
    if not m:
        bad.append(fn)
        continue
    ondisk.add((int(m.group(1)), int(m.group(2))))
print("files in tabella/                   :", len(os.listdir(TAB)))
print("filenames not matching codseq_year  :", len(bad), bad[:5])
print("distinct (codseq,year) on disk      :", len(ondisk))

A = declared - ondisk
B = ondisk - declared
print("A) declared but NOT on disk         :", len(A))
print("B) on disk but NOT declared         :", len(B), sorted(B)[:10])
print("preserved / declared                : %d/%d = %.4f%%"
      % (len(ondisk), len(declared), 100.0 * len(ondisk) / len(declared)))

# ---- 3. restricted to the 5 variables actually collected ---------------
held_codseq = {c for c, y in ondisk}
vars_held = collections.Counter()
by_codseq = {r["codseq"]: r for r in sens}
for c in held_codseq:
    vars_held[by_codseq[c]["descrizione"]] += 1
print("\ndistinct descrizione among HELD sensors:")
for k, v in sorted(vars_held.items()):
    print("   %-32s held sensors=%d" % (k, v))

collected_vars = set(vars_held)
tot_s = tot_p = 0
print("\nregion-wide catalogue for exactly those variables:")
for v in sorted(collected_vars):
    ss = [r for r in sens if r["descrizione"] == v]
    pairs = sum(len(years_by_sensor[r["codseq"]]) for r in ss)
    tot_s += len(ss)
    tot_p += pairs
    print("   %-32s sensors=%4d declared(sensor,year)=%5d" % (v, len(ss), pairs))
print("   TOTAL sensors=%d declared pairs=%d ; preserved files=%d -> %.2f%%"
      % (tot_s, tot_p, len(ondisk), 100.0 * len(ondisk) / tot_p))

# ---- 4. leaf wetness specifically --------------------------------------
LW = "Bagnatura fogliare"
lw = [r for r in sens if r["descrizione"] == LW]
lw_pairs = sum(len(years_by_sensor[r["codseq"]]) for r in lw)
lw_held = {(c, y) for c, y in ondisk if by_codseq[c]["descrizione"] == LW}
print("\nleaf wetness region-wide: sensors=%d declared pairs=%d ; preserved=%d -> %.2f%%"
      % (len(lw), lw_pairs, len(lw_held), 100.0 * len(lw_held) / lw_pairs))

# provinces of leaf-wetness stations, via the station catalogue
st_by_codseqst = {}
for s in stat:
    st_by_codseqst[s.get("codseq", s.get("codseqst"))] = s
prov = collections.Counter()
prov_held = collections.Counter()
held_lw_codseq = {c for c, y in lw_held}
for r in lw:
    s = st_by_codseqst.get(r["codseqst"], {})
    p = s.get("provincia") or s.get("provnm") or s.get("siglaprov") or "?"
    prov[p] += 1
    if r["codseq"] in held_lw_codseq:
        prov_held[p] += 1
print("leaf-wetness stations by province (declared / held):")
for p in sorted(prov):
    print("   %-20s declared=%3d held=%3d" % (p, prov[p], prov_held.get(p, 0)))
print("distinct leaf-wetness sensors declared:", len({r['codseq'] for r in lw}),
      " held:", len(held_lw_codseq))
