#!/usr/bin/env python3
"""RT6-I. The inverse error. Two questions:
 (a) is the attention class ordered the same way as the measurement, or against it?
 (b) does the matched-panel suppression ever hide an ABOVE_HISTORICAL behind NO_ESCALATION?"""
import os, sys, json, statistics, datetime as dt
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "engine"))
import di_core, di_observe, di_adama

CASE = os.path.abspath(os.path.join(HERE, "..", "..", "DISEASE-INTELLIGENCE-ITALY",
                                    "CASES", "OLIVO-BACTROCERA-TOSCANA"))
sheet = di_core.load_sheet()
adama = di_adama.relevance("Olive", "Olive Fruit Fly")
RANK = {"UNKNOWN": 0, "NO_ESCALATION": 1, "MONITOR": 2, "INVESTIGATE": 3}

def spearman(a, b):
    def r(x):
        s = sorted(range(len(x)), key=lambda i: x[i])
        rk = [0.0] * len(x)
        for pos, i in enumerate(s):
            rk[i] = pos + 1.0
        return rk
    ra, rb = r(a), r(b)
    n = len(a); ma, mb = sum(ra)/n, sum(rb)/n
    num = sum((x-ma)*(y-mb) for x, y in zip(ra, rb))
    den = (sum((x-ma)**2 for x in ra) * sum((y-mb)**2 for y in rb)) ** 0.5
    return num/den if den else 0.0

dates = [dt.date(2026, 9, 6), dt.date(2026, 8, 23), dt.date(2026, 8, 9),
         dt.date(2026, 7, 26), dt.date(2026, 7, 12), dt.date(2025, 9, 6),
         dt.date(2024, 9, 6), dt.date(2023, 9, 6)]
metrics = ["ACTIVE_INFESTATION_COUNT", "DAMAGING_INFESTATION_COUNT"]
hidden_above, total_cells, no_esc = [], 0, 0
print(f"{'as_of':12s} {'metric':28s} {'rho(rate,attn)':>15s}  {'INV':>3s} {'MON':>3s} "
      f"{'NOESC':>5s} {'UNK':>3s}  hidden_ABOVE")
for as_of in dates:
    loaded = di_core.load_visits(CASE, sheet, as_of)
    provs = sorted({v["province"] for v in loaded["visits"] if v["province"]})
    for M in metrics:
        cs = [di_observe.cell(loaded["visits"], sheet, p, M, as_of) for p in provs]
        ats = [di_adama.attention_class(c, adama)["attention_class"] for c in cs]
        pub = [(c, a) for c, a in zip(cs, ats)
               if c["quality"]["observation_publishable"]]
        rates = [c["observation"]["value_pct"] for c, _ in pub]
        ranks = [RANK[a] for _, a in pub]
        rho = spearman(rates, ranks) if len(pub) > 2 else float("nan")
        cnt = {k: ats.count(k) for k in ("INVESTIGATE", "MONITOR", "NO_ESCALATION", "UNKNOWN")}
        hid = [c["province"] for c, a in zip(cs, ats)
               if a == "NO_ESCALATION"
               and c["analysis"]["historical_state_unmatched"] == "ABOVE_HISTORICAL"]
        hidden_above += hid
        total_cells += len(cs)
        no_esc += cnt["NO_ESCALATION"]
        print(f"{as_of.isoformat():12s} {M:28s} {rho:15.3f}  {cnt['INVESTIGATE']:3d} "
              f"{cnt['MONITOR']:3d} {cnt['NO_ESCALATION']:5d} {cnt['UNKNOWN']:3d}  {hid}")

print(f"\ncells examined                              : {total_cells}")
print(f"cells filed NO_ESCALATION                   : {no_esc} "
      f"({100.0*no_esc/total_cells:.1f}%)")
print(f"NO_ESCALATION cells whose UNMATCHED history "
      f"said ABOVE_HISTORICAL : {len(hidden_above)} {sorted(set(hidden_above))}")
print("rho > 0 means the attention class rises with the reading; rho < 0 means it falls.")
