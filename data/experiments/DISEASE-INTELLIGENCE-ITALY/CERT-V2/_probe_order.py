import os,sys,json,random,glob as gm,datetime as dt
HERE=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,os.path.join(HERE,"..","ENGINE")); sys.path.insert(0,os.path.join(HERE,"..","CASES"))
import current_pressure as cp
OL=os.path.join(HERE,"..","CASES","OLIVO-BACTROCERA-TOSCANA")
VI=os.path.join(HERE,"..","CASES","VITE-OIDIO-TOSCANA")
AS=dt.date(2026,9,6); real=gm.glob
seed=int(sys.argv[1])
rnd=random.Random(seed)
cp.glob.glob=lambda p,**k:(lambda L:(rnd.shuffle(L),L)[1])(list(real(p,**k)))
s=cp.sensitivity(OL,-1002,AS)
c=0
for d,v in ((OL,-1002),(VI,39)):
    h=cp.hindcast(d,v,AS.month,AS.day,range(2010,AS.year+1))
    for y,row in h.items():
        cl={x for x in row.values() if x in (cp.HIGHER,cp.TYPICAL,cp.LOWER)}
        if len(cl)>1: c+=1
h=cp.hindcast(OL,-1002,AS.month,AS.day,range(2007,AS.year+1))
flat=[x for y in h.values() for x in y.values() if x in (cp.HIGHER,cp.TYPICAL,cp.LOWER)]
dom=round(max(flat.count(x) for x in (cp.HIGHER,cp.TYPICAL,cp.LOWER))/len(flat),3)
print(json.dumps({"seed":seed,"GATE_F":s["MEAN_AGREEMENT"],"GATE_C_disagreeing":c,"GATE_G_olive_dom":dom}))
