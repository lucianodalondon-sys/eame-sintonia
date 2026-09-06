import json, re, collections, os
CLIENT = r"C:\cert-v2-disease-pressure\italia-portale\client"
src = open(os.path.join(CLIENT, "italy-handoff-v21.js"), encoding="utf-8", errors="replace").read()
i = src.index('"productRelationships"'); j = src.index("[", i)
d, k, ins, esc = 0, j, False, False
while k < len(src):
    c = src[k]
    if ins:
        if esc: esc = False
        elif c == "\\": esc = True
        elif c == '"': ins = False
    else:
        if c == '"': ins = True
        elif c == "[": d += 1
        elif c == "]":
            d -= 1
            if d == 0: break
    k += 1
rel = json.loads(src[j:k + 1])
print("n", len(rel))
print("distinct CROP_ON_LABEL:", sorted({str(r.get("CROP_ON_LABEL")) for r in rel}))
print()
print("distinct CROP_IDS:", sorted({c for r in rel for c in (r.get("CROP_IDS") or [])}))
print()
tg = sorted({str(r.get("TARGET_AS_WRITTEN")) for r in rel})
print("n distinct TARGET_AS_WRITTEN", len(tg))
print("targets matching mosc|bact|dac|fly|olea:", [t for t in tg if re.search(r"mosc|bact|dac|fly|olea", t, re.I)])
print()
print("OLIVO rows:", [{kk: r.get(kk) for kk in ("PRODUCT_NAME", "CROP_ON_LABEL", "TARGET_AS_WRITTEN", "TARGET_ON_LABEL", "REGISTRATION_NUMBER")}
                      for r in rel if "OLIV" in str(r.get("CROP_ON_LABEL", "")).upper()])
