#!/usr/bin/env python3
"""
GENERIC internal-consistency test: do independently-monitored provinces agree on which
seasons were bad? One code path for every case.

WARRANT CORRECTED 2026-09-06. This module used to assert that "panel composition, observer
identity and visit intensity are province-specific and cannot manufacture cross-province
agreement". That sentence was FALSE and was the only justification offered for treating the
pairs as independent. Measured: one organisation (unipi) supplies rows in all 10 provinces of
both vine cases; ota and aprol each appear in 10/10 provinces of the olive case. A single
organisation's scoring drift is therefore common to every province and CAN in principle
manufacture the agreement this test measures.

The independence claim is now DEMONSTRATED per case instead of asserted, by removing the
shared organisation and re-running:
    OIDIO        all orgs 27/36 rho +0.245  ->  drop unipi     6/6  rho +0.537
    BACTROCERA   all orgs 36/36 rho +0.770  ->  drop ota+aprol 36/36 rho +0.731
Both re-run here from the frozen RAW. The calibration case (peronospora) uses an older index
layout and was NOT re-run, so no leave-one-org-out number is claimed for it.
The conclusion survives in both cases tested. The warrant did not.

Note that dropping the shared organisation costs power in the vine case (36 pairs -> 6), so the
survival there is weaker evidence than the olive case's, where all 36 pairs remain.
"""
import json,sys,os,glob,collections,itertools,random,importlib.util
from statistics import mean,pstdev
s=importlib.util.spec_from_file_location('rc',os.path.join(os.path.dirname(os.path.abspath(__file__)),'run_case.py'))
rc=importlib.util.module_from_spec(s); s.loader.exec_module(rc)

def rank(v):
    o=sorted(range(len(v)),key=lambda i:v[i]); r=[0]*len(v)
    for p,i in enumerate(o): r[i]=p
    return r
def pear(x,y):
    mx,my=mean(x),mean(y); sx,sy=pstdev(x),pstdev(y)
    return None if sx==0 or sy==0 else sum((a-mx)*(b-my) for a,b in zip(x,y))/(len(x)*sx*sy)
def spear(a,b): return pear([float(x) for x in rank(a)],[float(x) for x in rank(b)])

def by_province(d,var,minsites=8):
    idx=json.load(open(os.path.join(d,"collection_index.json")))
    scale,_,_=rc.build_scale(idx["codes"] or [],var)
    per=collections.defaultdict(dict)
    for fn in sorted(glob.glob(os.path.join(d,"RAW",f"*_v{var}_*.json"))):
        y=int(os.path.basename(fn)[:-5].split("_")[-1])
        prov=collections.defaultdict(lambda: collections.defaultdict(list))
        for r in json.load(open(fn)):
            v=r.get("val")
            if v is None: continue
            sc=scale.get(str(v))
            if sc is not None: val=sc["ordinal"]
            else:
                try: val=float(str(v).replace(",","."))
                except Exception: continue
            prov[r.get("nome_area")][r["id_field"]].append(val)
        for p,sites in prov.items():
            if p and len(sites)>=minsites:
                per[p][y]=mean(max(v) for v in sites.values())
    return per

if __name__=="__main__":
    d,var=sys.argv[1],int(sys.argv[2])
    P=by_province(d,var)
    provs=sorted([p for p in P if len(P[p])>=10])
    print(f"=== {os.path.basename(d)} var {var}: province agreement, {len(provs)} provinces with >=10 seasons")
    rs=[]
    for a,b in itertools.combinations(provs,2):
        sh=sorted(set(P[a])&set(P[b]))
        if len(sh)>=8:
            r=spear([P[a][y] for y in sh],[P[b][y] for y in sh])
            if r is not None: rs.append((a,b,r,len(sh)))
    if not rs: print("  insufficient overlap"); raise SystemExit
    rs.sort(key=lambda x:-x[2])
    for a,b,r,n in rs[:4]: print(f"   {a[:14]:14s} vs {b[:14]:14s} n={n:2d} rho={r:+.3f}")
    if len(rs)>4:
        print(f"   ... {len(rs)-4} more")
        for a,b,r,n in rs[-2:]: print(f"   {a[:14]:14s} vs {b[:14]:14s} n={n:2d} rho={r:+.3f}")
    vals=[r for _,_,r,_ in rs]
    print(f"   PAIRS={len(rs)}  positive={sum(1 for v in vals if v>0)}/{len(vals)}  mean rho={mean(vals):+.3f}")
    obs=mean(vals); rng=random.Random(5); ge=0; N=3000
    for _ in range(N):
        Q={}
        for p in provs:
            ys=list(P[p]); vv=[P[p][y] for y in ys]; rng.shuffle(vv); Q[p]=dict(zip(ys,vv))
        sim=[]
        for a,b in itertools.combinations(provs,2):
            sh=sorted(set(Q[a])&set(Q[b]))
            if len(sh)>=8:
                r=spear([Q[a][y] for y in sh],[Q[b][y] for y in sh])
                if r is not None: sim.append(r)
        if sim and mean(sim)>=obs: ge+=1
    print(f"   permutation p (years shuffled within province, {N} draws) = {(ge+1)/(N+1):.5f}")
