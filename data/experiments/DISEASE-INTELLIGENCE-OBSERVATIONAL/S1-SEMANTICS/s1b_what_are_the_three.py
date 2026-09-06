#!/usr/bin/env python3
"""S1b — if Totale is not Attiva + Dannosa, what is it?

Tested by counting, not by translating. Joined on (id_field, date), which S1 proved unique."""
import json, os, glob, collections
HERE = os.path.dirname(os.path.abspath(__file__))
OLIVE = os.path.abspath(os.path.join(HERE, "..", "..", "DISEASE-INTELLIGENCE-ITALY",
                                     "CASES", "OLIVO-BACTROCERA-TOSCANA"))
def load(var):
    m = {}
    for fn in sorted(glob.glob(os.path.join(OLIVE, "RAW", f"*_v{var}_*.json"))):
        for r in json.load(open(fn, encoding="utf-8")):
            v = r.get("val")
            try: v = None if v in (None, "") else float(str(v).replace(",", "."))
            except ValueError: v = None
            m[(r.get("id_field"), r.get("date"))] = v
    return m
A, D, T, X = load(-1001), load(-1002), load(-1003), load(1)
k = [q for q in (set(A) & set(D) & set(T) & set(X))
     if None not in (A[q], D[q], T[q], X[q])]
n = len(k)
def pct(f): return f"{sum(1 for q in k if f(q))/n:.4%}"
print(f"visits with all four readable: {n:,}\n")
print("RELATION BETWEEN THE THREE SERVER-COMPUTED COLUMNS")
print(f"  Attiva + Dannosa  >  Totale : {pct(lambda q: A[q]+D[q] >  T[q])}")
print(f"  Attiva + Dannosa  == Totale : {pct(lambda q: A[q]+D[q] == T[q])}")
print(f"  Attiva + Dannosa  <  Totale : {pct(lambda q: A[q]+D[q] <  T[q])}")
print(f"  max(Attiva,Dannosa) == Totale: {pct(lambda q: max(A[q],D[q]) == T[q])}")
print(f"  Totale >= max(Attiva,Dannosa): {pct(lambda q: T[q] >= max(A[q],D[q]))}")
print(f"  Totale <= Attiva + Dannosa   : {pct(lambda q: T[q] <= A[q]+D[q])}")
d = collections.Counter(A[q]+D[q]-T[q] for q in k)
print(f"\n  distribution of (Attiva+Dannosa) - Totale, top 10: {d.most_common(10)}")
print(f"  negative differences (A+D < T): {sum(v for x,v in d.items() if x<0):,}")
print("\nIMPOSSIBLE VALUES (a count cannot be negative, and cannot exceed the sample)")
for nm, m in (("Attiva",A),("Dannosa",D),("Totale",T),("Tot",X)):
    vals=[m[q] for q in k]
    print(f"  {nm:8s} negative={sum(1 for v in vals if v<0):>5}  "
          f"exceeds Tot={sum(1 for q in k if m[q] > X[q]):>5}  "
          f"of {n:,}")
print(f"\n  visits where the sample size Tot == 0 : {sum(1 for q in k if X[q]==0):,}"
      f"  ({sum(1 for q in k if X[q]==0)/n:.2%})")
print(f"  visits where Tot == 100              : {sum(1 for q in k if X[q]==100):,}")
bad=[q for q in k if A[q]<0 or D[q]<0 or T[q]<0 or X[q]<=0 or T[q]>X[q]]
print(f"\n  visits failing at least one sanity rule: {len(bad):,} ({len(bad)/n:.2%})")
yr=collections.Counter(q[1][:4] for q in bad)
print(f"  by year: {sorted(yr.items())}")
