"""Cross-check: collector's stored window_coverage_pct vs my raw recomputation."""
import json, os

base = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
rc = json.load(open(os.path.join(base, "manifests", "daily-series-recount.json"), encoding="utf-8"))

lw = rc["leaf_wetness"]
print("leaf_wetness entries:", len(lw))
print("fields of entry 0:", sorted(lw[0].keys()))
print()

# my independently recomputed day counts (from audit_v2_c4_independent.py)
mine = {204: 4263, 197: 4263, 184: 4263, 186: 4261, 183: 4261, 189: 4259,
        196: 4257, 187: 4256, 100: 4255, 185: 4249, 188: 4248, 195: 4245,
        102: 4236, 577: 3312}
W = 4263

ge994 = ge993 = 0
print(f"{'st':>4}  {'stored_days':>11} {'my_days':>8}  {'stored_pct':>10} {'my_exact_pct':>13}  match  name")
for e in sorted(lw, key=lambda x: -x.get("window_coverage_pct", 0)):
    st = e.get("codice_stazione") or e.get("station") or e.get("codice")
    days = e.get("window_days_present") or e.get("days_in_window") or e.get("window_days")
    pct = e.get("window_coverage_pct")
    myd = mine.get(st)
    myp = 100.0 * myd / W if myd is not None else float("nan")
    ok = "OK" if myd == days else "MISMATCH"
    if pct is not None and pct >= 99.4:
        ge994 += 1
    if pct is not None and pct >= 99.3:
        ge993 += 1
    print(f"{st:>4}  {str(days):>11} {str(myd):>8}  {pct:10} {myp:13.6f}  {ok:8} {e.get('nome_stazione','')}")

print()
print("using collector's STORED (2dp-rounded) pct:")
print("   >= 99.4 :", ge994, "of", len(lw))
print("   >= 99.3 :", ge993, "of", len(lw))
print()
print("station 102 exact from raw: 4236/4263 =", repr(100.0 * 4236 / 4263))
print("round(99.366643, 2) =", round(100.0 * 4236 / 4263, 2))
