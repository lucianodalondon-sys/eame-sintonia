import os,sys,json,copy,datetime as dt,collections
HERE=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,os.path.join(HERE,"..","ENGINE")); sys.path.insert(0,os.path.join(HERE,"..","CASES"))
import current_pressure as cp, run_case
VI=os.path.join(HERE,"..","CASES","VITE-OIDIO-TOSCANA")
AS=dt.date(2026,9,6)
idx=json.load(open(os.path.join(VI,"collection_index.json")))
ids42=[str(c['id_survey_code']) for c in idx['codes'] if c['id_survey_var']==42]
rows,scale39,meta=cp.load_rows(VI,39)
scale42,unres,hows=run_case.build_scale(idx['codes'],42)
mut=copy.deepcopy(rows)
for i,r in enumerate(mut): r['val']=ids42[i%len(ids42)]   # every visit reports a product
meta42=dict(meta); meta42['VALUE_MODE']='ORDINAL'
# assert_outcome_admissible reads the index from disk; var 42 IS a declared survey var
try:
    out=cp.current_pressure(VI,42,AS,_pre=(mut,scale42,meta42))
    st={p:v.get('STATE') for p,v in out['PROVINCES'].items()}
    print("EVIDENCE_ROLE :",out['EVIDENCE_ROLE'])
    print("VALUE_MODE    :",out['VALUE_MODE'],"| CUTOFF:",out['CUTOFF_LABEL'],"| latency:",out['DATA_LATENCY_DAYS'])
    print("scale42 resolved",len(scale42),"of",len(ids42),"| unresolved:",unres)
    print("STATES        :",json.dumps(st))
    print("classed       :",sum(1 for s in st.values() if s in (cp.HIGHER,cp.TYPICAL,cp.LOWER)),"of",len(st))
    print("VALUES        :",json.dumps({p:v.get('VALUE') for p,v in out['PROVINCES'].items()}))
except Exception as e:
    print("REFUSED:",type(e).__name__,e)
