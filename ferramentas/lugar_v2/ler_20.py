#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EXTRATOR-LUGAR-V2 · 20 mudancas lidas a mao: TODAS as de valor + as de SO_BASE por sorteio (semente fixa).
Mostra antes/depois e o trecho; o veredito e escrito a mao no relatorio."""
import json, random, sys

o = sys.argv[1]
L = json.load(open(o + "/CLASSIFICACAO.json", encoding="utf-8"))["LISTAS"]
valor = [(k, x) for k, v in L.items() if not k.endswith("SO_BASE") for x in v]
so_base = [(k, x) for k, v in L.items() if k.endswith("SO_BASE") for x in v]
random.seed(20260926)
escolha = valor + random.sample(so_base, 20 - len(valor))
out = []
for i, (k, x) in enumerate(escolha, 1):
    a, d = x["ANTES"], x["DEPOIS"]
    out.append({"N": i, "GRUPO": k, "SOURCE_ID": x["SOURCE_ID"], "SHA256": x["SHA256"],
                "ANTES": a, "DEPOIS": d})
    print("%2d %-44s %-10s | %s -> %s" % (i, k, x["SOURCE_ID"], str(a["VALOR"])[:30], str(d["VALOR"])[:40]))
    if k.endswith("SO_BASE"):
        ba, bd = str(a["BASE"]), str(d["BASE"])
        j = next((n for n in range(min(len(ba), len(bd))) if ba[n] != bd[n]), min(len(ba), len(bd)))
        print("      antes : …%s" % ba[max(0, j - 40):j + 110])
        print("      depois: …%s" % bd[max(0, j - 40):j + 110])
    else:
        print("      depois: %s" % str(d["BASE"])[:260])
json.dump(out, open(o + "/LIDOS-A-MAO-20.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
