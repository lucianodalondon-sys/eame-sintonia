#!/usr/bin/env python3
"""RT5 · accusation 8. Minimal perturbation: how few infested drupes change a
published province verdict?

The counting rule is a step function of sixteen or seventeen sign comparisons,
and some of those comparisons are decided in the fourth decimal place. This finds,
for each speaking province, the SMALLEST change to the real data that flips the
published class: add (or remove) k infested drupes at one single visit inside the
current 28-day window, re-run the tool end to end, and report the smallest k that
works. The perturbation is monotone in k, so a binary search is exact."""
import os, sys, json, datetime as dt
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rt5_lib as L

AS_OF = dt.date(2026, 9, 6)
M = "ACTIVE_INFESTATION_COUNT"
idx, raw = L.get_index(M)
P = L.PARAMS
lo, hi = L.win(AS_OF, P["WINDOW_DAYS"])
BASE = {c["province"]: c["historical_state"] for c in L.all_cells(idx, AS_OF)}


def verdict(prov):
    return L.cell(idx, prov, AS_OF)["historical_state"]


def probe(prov, visit, k):
    """Set this visit's infested count to (original + k), clamped to [0, denominator]."""
    orig = visit[M]
    new = min(visit["den"], max(0.0, orig + k))
    visit[M] = new
    try:
        return verdict(prov)
    finally:
        visit[M] = orig


out = {}
for prov in ("Firenze", "Siena", "Arezzo"):
    pub = BASE[prov]
    cur = idx.pooled(prov, lo, hi, as_of=AS_OF)
    cands = [v for v in idx.slice(prov, lo, hi)
             if v["usable"] and v[M] is not None and v["den"]]
    best = None
    for direction in (+1, -1):
        for v in cands:
            head = int(v["den"] - v[M]) if direction > 0 else int(v[M])
            if head <= 0:
                continue
            if probe(prov, v, direction * head) == pub:
                continue                      # even the maximum move does nothing
            a, b = 1, head                    # smallest k that flips
            while a < b:
                mid = (a + b) // 2
                if probe(prov, v, direction * mid) != pub:
                    b = mid
                else:
                    a = mid + 1
            got = probe(prov, v, direction * a)
            cand = {"k_drupes": a, "direction": "add" if direction > 0 else "remove",
                    "id_field": v["id_field"], "date": v["date"].isoformat(),
                    "comune": v["comune"],
                    "visit_original_count": v[M], "visit_denominator": v["den"],
                    "new_verdict": got}
            if best is None or a < best["k_drupes"]:
                best = cand
    tot = cur["drupes_sampled"]
    inf = cur["infested_drupes"]
    out[prov] = {"published": pub, "infested_drupes_in_window": inf,
                 "drupes_sampled_in_window": tot, "minimal_perturbation": best}
    if best:
        print(f"{prov:10s} published {pub}")
        print(f"           {best['direction']} {best['k_drupes']} infested drupe(s) at one "
              f"visit (grove {best['id_field']}, {best['date']}, {best['comune']}, "
              f"which recorded {best['visit_original_count']:.0f} of "
              f"{best['visit_denominator']:.0f})")
        print(f"           -> verdict becomes {best['new_verdict']}")
        print(f"           that is {best['k_drupes']} drupe(s) against {inf} infested "
              f"and {tot:,} sampled in the published window\n")
    else:
        print(f"{prov:10s} published {pub}: NO single-visit change of any size flips it\n")

# which single matched season is decided by the narrowest margin?
print("NARROWEST SEASON MARGINS (matched panel, published configuration)")
det = json.load(open(os.path.join(HERE, "rt5_02_signtest.json")))
for prov in ("Firenze", "Siena", "Arezzo"):
    rows = sorted(det[prov]["per_season"], key=lambda r: abs(r["now"] - r["then"]))
    print(f"  {prov}:")
    for r in rows[:3]:
        print(f"    {r['season']}  now {r['now']:.4f}% vs then {r['then']:.4f}%  "
              f"margin {abs(r['now']-r['then']):.4f} pp  "
              f"({r['inf_now']}/{r['n_now']} vs {r['inf_then']}/{r['n_then']}, "
              f"two-proportion p = {r['p_two_prop']:.3f})")

json.dump(out, open(os.path.join(HERE, "rt5_08_fragility.json"), "w"), indent=1)
print("\nwrote rt5_08_fragility.json")
