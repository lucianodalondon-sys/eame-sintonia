import os,sys,json,glob,collections,datetime as dt
from statistics import median
HERE=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,os.path.join(HERE,"..","ENGINE")); sys.path.insert(0,os.path.join(HERE,"..","CASES"))
import current_pressure as cp
OL=os.path.join(HERE,"..","CASES","OLIVO-BACTROCERA-TOSCANA")
AS=dt.date(2026,9,6); W=cp.WINDOW_DAYS

def rows_for(var):
    out=[]
    for fn in sorted(glob.glob(os.path.join(OL,"RAW",f"*_v{var}_*.json"))):
        for r in json.load(open(fn)):
            d=r.get("date")
            if not d: continue
            try: r["_d"]=dt.date.fromisoformat(d)
            except ValueError: continue
            out.append(r)
    return out

# --- A2: attiva (-1001) vs dannosa (-1002) on the SAME visit ---
att={r["id_survey"]:r.get("val") for r in rows_for(-1001)}
dan=rows_for(-1002)
def num(v):
    try: return float(v) if v not in (None,"") else None
    except ValueError: return None
both=0; live_but_zero_damage=0
for r in dan:
    a,d=num(att.get(r["id_survey"])),num(r.get("val"))
    if a is None or d is None: continue
    both+=1
    if a>0 and d==0: live_but_zero_damage+=1
print(f"A2  visits with BOTH variables readable: {both}")
print(f"    attiva>0 while dannosa==0        : {live_but_zero_damage}  ({live_but_zero_damage/max(1,both):.1%})")

# published today vs attiva today, per province
lo,hi=AS-dt.timedelta(days=W-1),AS
byp=collections.defaultdict(lambda:[0,0,0,0])   # sites_dan, pos_dan, sites_att, pos_att
sd=collections.defaultdict(dict); sa=collections.defaultdict(dict)
for r in dan:
    if lo<=r["_d"]<=hi and num(r.get("val")) is not None:
        sd[r["nome_area"]].setdefault(r["id_field"],[]).append(num(r["val"]))
for r in rows_for(-1001):
    if lo<=r["_d"]<=hi and num(r.get("val")) is not None:
        sa[r["nome_area"]].setdefault(r["id_field"],[]).append(num(r["val"]))
print("    province      dannosa_incidence  attiva_incidence  (sites)")
for p in sorted(set(sd)|set(sa)):
    a=sd.get(p,{}); b=sa.get(p,{})
    fi=lambda m: (sum(1 for v in m.values() if max(v)>0)/len(m)) if m else None
    print(f"      {p:14s} {str(round(fi(a),3) if a else None):8s}          {str(round(fi(b),3) if b else None):8s}   ({len(a)}/{len(b)})")

# --- A5: does the baseline compare the same groves? ---
print()
pre=cp.load_rows(OL,-1002)
rows=pre[0]
def panel(y):
    l,h=cp._shift_year(lo,y),cp._shift_year(hi,y)
    m=collections.defaultdict(set)
    for r in rows:
        if l<=r["_d"]<=h and cp.read_value(r,pre[1],pre[2]["VALUE_MODE"]) is not None:
            m[r["nome_area"]].add(r["id_field"])
    return m
cur=panel(2026)
print("A5  shared groves between the 2026 window panel and each prior season")
print("    province       n_2026  median_shared  seasons_with_>=8_shared")
for p in sorted(cur):
    sh=[len(cur[p] & panel(y).get(p,set())) for y in range(2006,2026)]
    print(f"      {p:14s} {len(cur[p]):5d}  {median(sh):13.1f}  {sum(1 for x in sh if x>=8):5d} of 20")
