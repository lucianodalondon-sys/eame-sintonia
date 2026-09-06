import os,sys,json,datetime as dt
HERE=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,os.path.join(HERE,"..","ENGINE")); sys.path.insert(0,os.path.join(HERE,"..","CASES"))
import current_pressure as cp
AS=dt.date(2026,9,6)
VI=os.path.join(HERE,"..","CASES","VITE-OIDIO-TOSCANA")
pre=cp.load_rows(VI,39)
fut=[r for r in pre[0] if r["_d"]>AS]
print("rows dated AFTER as_of in the archive:",len(fut),"dates:",sorted({r['_d'].isoformat() for r in fut}))
honest=cp.current_pressure(VI,39,AS,_pre=pre)
real=cp._window_value
cp._window_value=lambda rows,scale,lo,hi,mode="ORDINAL": real(rows,scale,lo,dt.date(2100,1,1),mode)
mut=cp.current_pressure(VI,39,AS,_pre=pre)
cp._window_value=real
# do future rows reach a published cell in the mutant?
byp={}
for r in fut: byp.setdefault(r.get("nome_area"),[]).append(r)
print("\nprovinces holding future-dated rows:",{k:len(v) for k,v in byp.items()})
ch=[p for p in honest["PROVINCES"] if honest["PROVINCES"][p].get("STATE")!=mut["PROVINCES"].get(p,{}).get("STATE")]
print("province cells whose STATE changes when the cutoff is removed:",len(ch),ch)
for p in list(byp)[:5]:
    print(f"  {p}: honest n_visits={honest['PROVINCES'].get(p,{}).get('n_visits')} val={honest['PROVINCES'].get(p,{}).get('VALUE')}"
          f" | no-cutoff n_visits={mut['PROVINCES'].get(p,{}).get('n_visits')} val={mut['PROVINCES'].get(p,{}).get('VALUE')}")
print("\nCUTOFF_LABEL honest:",honest["CUTOFF_LABEL"],"| mutant:",mut["CUTOFF_LABEL"])
print("WINDOW honest:",honest["WINDOW"])
