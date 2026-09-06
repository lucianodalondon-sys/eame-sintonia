"""Recount the handoff's per-variable table (files / rows / stations / years)
straight from the gz payloads, and expose which stations do NOT actually span
the advertised year range for each variable."""
import gzip, json, os, collections

TAB = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "raw",
                                   "F4-arpav-rest", "tabella"))
per = collections.defaultdict(lambda: collections.defaultdict(list))
files = collections.Counter()
rows = collections.Counter()
empty = []

for fn in sorted(os.listdir(TAB)):
    if not fn.endswith(".json.gz"):
        continue
    with gzip.open(os.path.join(TAB, fn), "rt", encoding="utf-8") as fh:
        d = json.load(fh)
    dat = d.get("data") or []
    if not dat:
        empty.append(fn)
        continue
    tp = dat[0]["tipo"]
    files[tp] += 1
    rows[tp] += len(dat)
    for r in dat:
        per[tp][r["nome_stazione"]].append(r["dataora"][:4])

print("files with zero rows:", empty if empty else "none")
print()
print(f"{'code':9s}{'files':>7s}{'rows':>9s}{'stations':>10s}  yr_range")
for tp in ["PREC", "BFOGL", "TARIA2M", "UMID2M", "RADSOL"]:
    st = per[tp]
    ys = [y for v in st.values() for y in v]
    late = {s: max(v) for s, v in st.items() if max(v) != "2026"}
    early = {s: min(v) for s, v in st.items() if min(v) != "2010"}
    print(f"{tp:9s}{files[tp]:7d}{rows[tp]:9d}{len(st):10d}  {min(ys)}-{max(ys)}")
    print(f"          station last year != 2026 : {late if late else 'none'}")
    print(f"          station first year != 2010: {early if early else 'none'}")
print()
print("total files:", sum(files.values()), "total rows:", sum(rows.values()))
