import os,sys,json,datetime as dt
HERE=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,os.path.join(HERE,"..","ENGINE")); sys.path.insert(0,os.path.join(HERE,"..","CASES"))
import current_pressure as cp
OL=os.path.join(HERE,"..","CASES","OLIVO-BACTROCERA-TOSCANA")
s=cp.sensitivity(OL,-1002,dt.date(2026,9,6))
scale=cp.load_rows(OL,-1002)[1]
print(json.dumps({"seed":os.environ.get("PYTHONHASHSEED"),"F":s["MEAN_AGREEMENT"],
 "scale":{k:v["ordinal"] for k,v in sorted(scale.items())}}))
