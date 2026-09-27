#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EXTRATOR-LUGAR-V2 · as mudancas antes x depois, por tipo: GANHA / PERDE / TROCA de valor / SO_BASE. So leitura."""
import collections, json, sys

NS = "NAO SEI"
o = sys.argv[1]
A = {x["SHA256"]: x for x in json.load(open(o + "/antes.json", encoding="utf-8"))["ITENS"]}
D = {x["SHA256"]: x for x in json.load(open(o + "/depois.json", encoding="utf-8"))["ITENS"]}
vazio = lambda v: v in (NS, "", None) or str(v).startswith(NS)
out = collections.OrderedDict()
listas = collections.defaultdict(list)
for campo in ("LOCAL_DO_FATO", "DATA_DO_FATO"):
    for grupo in ("FORA_DA_SALA", "SALA"):
        c = collections.Counter()
        for s, a in A.items():
            if a["NA_SALA"] != (grupo == "SALA"):
                continue
            va, vd = a["PREVISTO"][campo], D[s]["PREVISTO"][campo]
            if (va["VALOR"], va["BASE"]) == (vd["VALOR"], vd["BASE"]):
                continue
            if vazio(va["VALOR"]) and not vazio(vd["VALOR"]):
                k = "GANHA"
            elif not vazio(va["VALOR"]) and vazio(vd["VALOR"]):
                k = "PERDE"
            elif va["VALOR"] != vd["VALOR"]:
                k = "TROCA"
            else:
                k = "SO_BASE"
            c[k] += 1
            listas[(campo, grupo, k)].append({"SHA256": s[:16], "SOURCE_ID": a["SOURCE_ID"], "ANTES": va, "DEPOIS": vd})
        out["%s · %s" % (campo, grupo)] = dict(c)
json.dump({"RESUMO": out, "LISTAS": {" · ".join(k): v for k, v in listas.items()}},
          open(o + "/CLASSIFICACAO.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1))
for k, v in listas.items():
    if k[2] in ("GANHA", "PERDE", "TROCA"):
        for x in v[:12]:
            print(" · ".join(k), x["SOURCE_ID"], "|", str(x["ANTES"]["VALOR"])[:40], "->", str(x["DEPOIS"]["VALOR"])[:40], "|", str(x["DEPOIS"]["BASE"])[:150])
