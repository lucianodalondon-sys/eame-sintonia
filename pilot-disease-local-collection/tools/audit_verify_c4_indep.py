# Independent recomputation of C4 from RAW gz files only.
# Does NOT read any manifest. Read-only.
import gzip, json, os, datetime, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TAB = os.path.join(ROOT, "raw", "F4-arpav-rest", "tabella")

W0 = datetime.date(2014, 3, 1)
W1 = datetime.date(2025, 10, 31)

# window length two independent ways
n_iter = 0
d = W0
while d <= W1:
    n_iter += 1
    d += datetime.timedelta(days=1)
n_sub = (W1 - W0).days + 1
print("window days by iteration :", n_iter)
print("window days by subtraction:", n_sub)
print()

# scan every preserved gz file, collect BFOGL days per station
days_bfogl = collections.defaultdict(set)      # station -> set of dates in window (row present)
days_bfogl_val = collections.defaultdict(set)  # station -> set of dates in window with non-null value
days_anysensor = collections.defaultdict(set)  # station -> set of dates in window, ANY sensor
names = {}
files = sorted(os.listdir(TAB))
nfiles = 0
for fn in files:
    if not fn.endswith(".json.gz"):
        continue
    nfiles += 1
    with gzip.open(os.path.join(TAB, fn), "rt", encoding="utf-8", errors="replace") as fh:
        obj = json.load(fh)
    for r in obj.get("data") or []:
        tipo = r.get("tipo")
        code = r.get("codice_stazione")
        nm = r.get("nome_stazione")
        if nm:
            names[code] = nm
        dt = (r.get("dataora") or "")[:10]
        try:
            dd = datetime.date(int(dt[0:4]), int(dt[5:7]), int(dt[8:10]))
        except Exception:
            continue
        if not (W0 <= dd <= W1):
            continue
        days_anysensor[code].add(dd)
        if tipo == "BFOGL":
            days_bfogl[code].add(dd)
            if r.get("valore") not in (None, "", "null"):
                days_bfogl_val[code].add(dd)

print("gz files opened:", nfiles)
print("stations with any BFOGL row (all time in window):", len(days_bfogl))
print()

TH = 99.4
rows = []
for code in days_bfogl:
    n = len(days_bfogl[code])
    rows.append((names.get(code, "?"), code, n, 100.0 * n / n_iter, len(days_bfogl_val[code]), len(days_anysensor[code])))
rows.sort(key=lambda r: -r[3])

print(f"{'station':<32}{'code':>6}{'days':>7}{'exact_pct':>13}{'2dp':>9}{'1dp':>8}  ge99.4_exact  ge99.4_after_1dp_round")
for nm, code, n, pct, nval, nany in rows:
    r1 = round(pct, 1)
    print(f"{nm:<32}{code:>6}{n:>7}{pct:>13.6f}{round(pct,2):>9.2f}{r1:>8.1f}"
          f"{'  YES' if pct >= TH else '  no ':>14}{'  YES' if r1 >= TH else '  no':>24}")

exact = sum(1 for r in rows if r[3] >= TH)
rounded = sum(1 for r in rows if round(r[3], 1) >= TH)
print()
print(f"stations >= 99.4% on the EXACT value            : {exact} of {len(rows)}")
print(f"stations >= 99.4% after rounding to 1 decimal FIRST: {rounded} of {len(rows)}")
print()

# focus on any station that flips between the two
for nm, code, n, pct, nval, nany in rows:
    if (pct >= TH) != (round(pct, 1) >= TH):
        need = -(-int(TH * n_iter) // 100)
        # smallest integer k with 100*k/n_iter >= 99.4
        k = 0
        while 100.0 * k / n_iter < TH:
            k += 1
        print(f"FLIPS ON ROUNDING: {nm} (code {code})")
        print(f"  days held           : {n} / {n_iter}")
        print(f"  exact pct           : {100.0*n/n_iter!r}")
        print(f"  days needed for true 99.4%: {k}   -> short by {k-n}")
        print(f"  BFOGL days with a non-null value: {nval}")
        print(f"  days with ANY sensor row       : {nany}")
