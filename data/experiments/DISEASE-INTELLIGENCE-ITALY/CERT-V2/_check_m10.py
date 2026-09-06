import os,sys,json,datetime as dt
HERE=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,os.path.join(HERE,"..","ENGINE")); sys.path.insert(0,os.path.join(HERE,"..","CASES"))
import current_pressure as cp
AS=dt.date(2026,9,6); VI=os.path.join(HERE,"..","CASES","VITE-OIDIO-TOSCANA")
print("base   :", cp.sensitivity(VI,39,AS)["MEAN_AGREEMENT"])
real=cp._window_value
calls={"n":0,"perturbed":0}
def patched(rows,scale,lo,hi,mode="ORDINAL"):
    v=real(rows,scale,lo,hi,mode); calls["n"]+=1
    if v is None: return v
    if hi.year>=2026:
        step=((hi-lo).days//7)%3
        v["INCIDENCE"]=round(min(1.0,max(0.0,v["INCIDENCE"]+(step-1)*0.30)),4); calls["perturbed"]+=1
    return v
cp._window_value=patched
print("mutated:", cp.sensitivity(VI,39,AS)["MEAN_AGREEMENT"], "calls",calls)
