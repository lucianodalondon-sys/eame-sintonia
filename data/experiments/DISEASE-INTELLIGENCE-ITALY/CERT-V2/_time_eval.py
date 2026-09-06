import os,sys,time,datetime as dt
HERE=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,os.path.join(HERE,"..","ENGINE")); sys.path.insert(0,os.path.join(HERE,"..","CASES"))
t=time.time(); import gates; print("import %.1fs"%(time.time()-t))
t=time.time(); r=gates.evaluate(); print("evaluate %.1fs"%(time.time()-t))
print({k:v["VERDICT"] for k,v in r["GATES"].items()})
