import os,sys,json,datetime as dt
HERE=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,os.path.join(HERE,"..","ENGINE")); sys.path.insert(0,os.path.join(HERE,"..","CASES"))
import current_pressure as cp
AS=dt.date(2026,9,6)
OL=os.path.join(HERE,"..","CASES","OLIVO-BACTROCERA-TOSCANA")
VI=os.path.join(HERE,"..","CASES","VITE-OIDIO-TOSCANA")
for nm,case,var in (("OLIVE",OL,-1002),("VINE",VI,39)):
    pre=cp.load_rows(case,var)
    nulls=sum(1 for r in pre[0] if r.get("val") in (None,""))
    base=cp.current_pressure(case,var,AS,_pre=pre)
    real=cp.read_value
    cp.read_value=lambda r,s,m,_r=real:(0.0 if _r(r,s,m) is None else _r(r,s,m))
    mut=cp.current_pressure(case,var,AS,_pre=pre)
    cp.read_value=real
    ch=[p for p in base["PROVINCES"] if base["PROVINCES"][p]!=mut["PROVINCES"].get(p)]
    stch=[p for p in base["PROVINCES"] if base["PROVINCES"][p].get("STATE")!=mut["PROVINCES"].get(p,{}).get("STATE")]
    print(f"M07 {nm}: null_vals={nulls}/{len(pre[0])} cells_changed={len(ch)} STATE_changed={len(stch)} {stch}")
    for p in ch[:3]:
        print("   ",p,"base",{k:base['PROVINCES'][p].get(k) for k in ('STATE','VALUE','n_sites')},
                    "mut",{k:mut['PROVINCES'][p].get(k) for k in ('STATE','VALUE','n_sites')})
print()
# M10 as written: is the perturbation constant across the grid?
for w in (14,21,28,35,42):
    span=w-1
    print(f"  window={w} span={span} span%7={span%7} shift={((span%7)-3)*0.12:+.2f}")
