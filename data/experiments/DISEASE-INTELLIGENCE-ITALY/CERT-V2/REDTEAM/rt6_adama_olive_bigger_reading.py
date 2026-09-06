#!/usr/bin/env python3
"""
RT6 / ADAMA · part 3 — the certification anchored ADAMA_PRODUCT_RELATION on the SMALLER of two
readings of the SAME 163 labels, and never asked the bigger one.

italy-app-model.js says, in its own words (lines ~103950 and ~108200):
  "The audit read 163 labels and published 236 relationships. The V2.1 label reader read the
   same labels and published 2.030 crop x target pairs, each carrying the sentence from the
   label that joins them."
  "seenRel ... veniva riempita soltanto dai 19 verdetti dell'audit storico ... quindi
   strengthFor rispondeva 'l'audit ha guardato e non ha trovato' su righe che la lettura piu
   completa aveva trovato"
  "WHEN TWO READINGS DISAGREE, THE ONE THAT READ MORE LABELS WINS."

CERT-V2/p10_adama_relation.py reads ONLY italy-label-verdicts.js (19 triples). This script asks
the 2.030-pair corpus the same question about Olive x Olive Fruit Fly.

Read-only.  Out: rt6_adama_olive_bigger_reading.json
"""
import os, sys, json, re, collections

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
CLIENT = os.path.join(REPO, "italia-portale", "client")
src = open(os.path.join(CLIENT, "italy-handoff-v21.js"), encoding="utf-8",
           errors="replace").read()

i = src.index('"productRelationships"')
j = src.index("[", i)
depth, k, instr, esc = 0, j, False, False
while k < len(src):
    c = src[k]
    if instr:
        if esc:
            esc = False
        elif c == "\\":
            esc = True
        elif c == '"':
            instr = False
    else:
        if c == '"':
            instr = True
        elif c == "[":
            depth += 1
        elif c == "]":
            depth -= 1
            if depth == 0:
                break
    k += 1
rel = json.loads(src[j:k + 1])

out = {"SOURCE_FILE": "italia-portale/client/italy-handoff-v21.js",
       "ARRAY": "productRelationships",
       "n_label_use_pairs": len(rel),
       "n_pairs_in_the_small_audit_italy_label_verdicts_js": 19}

olive_crop = [r for r in rel if "CROP_OLIVE" in (r.get("CROP_IDS") or [])
              or "OLIV" in str(r.get("CROP_ON_LABEL", "")).upper()]


def istext(r, *keys):
    return " ".join(str(r.get(k) or "") for k in keys).upper()


FLY = ("BACTROCERA", "MOSCA DELL'OLIVA", "MOSCA DELL OLIVA", "MOSCA DELLE OLIVE",
       "MOSCA OLEARIA", "DACUS", "OLIVE FRUIT FLY", "MOSCA DELL'OLIVO")
fly = [r for r in rel
       if any(f in istext(r, "TARGET_AS_WRITTEN", "TARGET_ON_LABEL") for f in FLY)]
olive_fly = [r for r in olive_crop
             if any(f in istext(r, "TARGET_AS_WRITTEN", "TARGET_ON_LABEL") for f in FLY)]

out["OLIVE"] = {
    "n_pairs_on_the_OLIVE_crop": len(olive_crop),
    "distinct_products_with_an_OLIVE_pair": sorted({str(r.get("PRODUCT_NAME"))
                                                    for r in olive_crop}),
    "distinct_targets_written_on_those_OLIVE_labels":
        sorted({str(r.get("TARGET_AS_WRITTEN") or r.get("TARGET_ON_LABEL"))
                for r in olive_crop}),
    "n_pairs_naming_the_OLIVE_FRUIT_FLY_on_any_crop": len(fly),
    "n_pairs_OLIVE_crop_AND_olive_fruit_fly": len(olive_fly),
    "OLIVE_x_OLIVE_FRUIT_FLY_ROWS":
        [{"PRODUCT_NAME": r.get("PRODUCT_NAME"), "CROP_ON_LABEL": r.get("CROP_ON_LABEL"),
          "TARGET_AS_WRITTEN": r.get("TARGET_AS_WRITTEN"),
          "TARGET_ON_LABEL": r.get("TARGET_ON_LABEL"),
          "REGISTRATION_NUMBER": r.get("REGISTRATION_NUMBER"),
          "ID": r.get("ID"), "PROVENANCE": r.get("PROVENANCE")}
         for r in olive_fly]}

# the three products the certification named
NAMED = ["KLARTAN 20 EW", "KLARTAN SMART", "MAVRIK SMART"]
out["THE_THREE_PRODUCTS_THE_CERTIFICATION_NAMED"] = {
    p: {"n_pairs_anywhere_in_the_2030_corpus":
        sum(1 for r in rel if str(r.get("PRODUCT_NAME", "")).upper() == p),
        "crops_it_is_paired_with":
            sorted({str(r.get("CROP_ON_LABEL")) for r in rel
                    if str(r.get("PRODUCT_NAME", "")).upper() == p})}
    for p in NAMED}
out["PRODUCTS_IN_THE_2030_CORPUS"] = len({r.get("PRODUCT_NAME") for r in rel})

out["READ_PLAINLY"] = (
    "Both readings come from the same 163 official Italian labels. The small one (19 triples) "
    "says NO_CONFIRMED_MATCH_CURRENT_READING for three named products on Olive x Olive Fruit "
    "Fly. The large one is in the same repository and the portal's own model says it wins when "
    "the two disagree. CERT-V2/p10_adama_relation.py never opens it.")

json.dump(out, open(os.path.join(HERE, "rt6_adama_olive_bigger_reading.json"), "w",
                    encoding="utf-8"), indent=1, default=str, ensure_ascii=False)
print(json.dumps(out, indent=1, default=str, ensure_ascii=False)[:5000])
