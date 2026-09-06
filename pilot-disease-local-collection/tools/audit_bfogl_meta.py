import json, glob, os, re
D = r"C:\disease-local-collection-italy\pilot-disease-local-collection\raw\F3b\bfogl_by_year"
for f in sorted(glob.glob(os.path.join(D, "*.json"))):
    j = json.load(open(f, encoding="utf-8"))
    print(os.path.basename(f), "| success=", j.get("success"),
          "| meta=", json.dumps(j.get("meta"), ensure_ascii=False)[:300])
