import os,sys,json,datetime as dt
HERE=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,os.path.join(HERE,"..","ENGINE")); sys.path.insert(0,os.path.join(HERE,"..","CASES"))
import current_pressure as cp
AS=dt.date(2026,9,6)
CASES=[("OLIVE",os.path.join(HERE,"..","CASES","OLIVO-BACTROCERA-TOSCANA"),-1002),
       ("VINE", os.path.join(HERE,"..","CASES","VITE-OIDIO-TOSCANA"),39)]
real=cp._window_value
def states(case,var,pre,patch):
    global real
    if patch: cp._window_value=patch
    r=cp.current_pressure(case,var,AS,_pre=pre)
    cp._window_value=real
    return {p:(v.get("STATE"),v.get("VALUE"),v.get("n_visits")) for p,v in r["PROVINCES"].items()}

# A: unbound EVERY window (what I did first)
allw=lambda rows,scale,lo,hi,mode="ORDINAL": real(rows,scale,lo,dt.date(2100,1,1),mode)
# B: unbound ONLY the current window (hi == AS_OF): this is the cutoff and nothing else
def curonly(rows,scale,lo,hi,mode="ORDINAL"):
    return real(rows,scale,lo,dt.date(2100,1,1) if hi==AS else hi,mode)

tot_a=tot_b=tot=0
for nm,case,var in CASES:
    pre=cp.load_rows(case,var)
    base=states(case,var,pre,None)
    a=states(case,var,pre,allw)
    b=states(case,var,pre,curonly)
    ca=[p for p in base if base[p]!=a[p]]; cb=[p for p in base if base[p]!=b[p]]
    sa=[p for p in base if base[p][0]!=a[p][0]]; sb=[p for p in base if base[p][0]!=b[p][0]]
    fut=[r for r in pre[0] if r["_d"]>AS]
    vals={cp.read_value(r,pre[1],pre[2]["VALUE_MODE"]) for r in fut}
    print(f"{nm}: future rows={len(fut)} their decoded values={sorted(v for v in vals if v is not None)}")
    print(f"   A unbound EVERY window : cells changed {len(ca)}/{len(base)}  STATE changed {len(sa)} {sa}")
    print(f"   B unbound ONLY current : cells changed {len(cb)}/{len(base)}  STATE changed {len(sb)} {sb}")
    tot_a+=len(sa); tot_b+=len(sb); tot+=len(base)
print(f"\nTOTAL over both cases: A={tot_a}/{tot} state changes | B={tot_b}/{tot} state changes")
