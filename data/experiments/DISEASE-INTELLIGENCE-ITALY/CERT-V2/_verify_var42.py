import os,sys,json,datetime as dt
HERE=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,os.path.join(HERE,"..","ENGINE")); sys.path.insert(0,os.path.join(HERE,"..","CASES"))
import current_pressure as cp, run_case
VI=os.path.join(HERE,"..","CASES","VITE-OIDIO-TOSCANA")
idx=json.load(open(os.path.join(VI,"collection_index.json")))
for var in (39,42):
    codes=[c for c in (idx.get('codes') or []) if c['id_survey_var']==var]
    scale,unres,hows=run_case.build_scale(idx.get('codes') or [],var)
    name=next((v['name'] for v in idx['vars'] if v['id_survey_var']==var),'?')
    print(f"var {var}  '{name}'  mode={cp.value_mode(idx,var)}  codes={len(codes)}  resolved={len(scale)}  unresolved={len(unres)}  how={hows}")
    for c in codes[:8]:
        r=run_case.derive_rank(c['name'])
        print(f"    code {c['id_survey_code']:>5}  '{c['name'][:44]:44s}' -> rank {r}")
    print()
