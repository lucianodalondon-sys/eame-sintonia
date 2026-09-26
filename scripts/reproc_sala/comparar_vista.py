#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""REPROC-SALA-PLANO — a vista `sala_de_espera_atual` ANTES e DEPOIS, campo a campo.

    py scripts/reproc_sala/comparar_vista.py vista-antes.json vista-depois.json comparacao.json

Por campo: quantas linhas sabem o valor (≠ NAO SEI) antes e depois, e cada mudança dividida em
NAO SEI → valor · valor → NAO SEI · valor → outro valor · só a base mudou. A lista inteira vai
para o JSON, para ler à mão.
"""
import json
import sys

NAO_SEI = "NAO SEI"
CAMPOS = (("published_at", "published_at_basis"), ("source_location", "source_location_basis"),
          ("fact_time", "fact_time_basis"), ("fact_location", "fact_location_basis"))


def _ler(p):
    with open(p, encoding="utf-8") as fh:
        return {(l["run_id"], l["ordem"]): l for l in (json.loads(fh.read().strip() or "null") or [])}


def main(antes_p, depois_p, saida_p):
    antes, depois = _ler(antes_p), _ler(depois_p)
    fora = {"LINHAS_ANTES": len(antes), "LINHAS_DEPOIS": len(depois),
            "SO_ANTES": sorted(map(list, set(antes) - set(depois))),
            "SO_DEPOIS": sorted(map(list, set(depois) - set(antes))),
            "CAMPOS": {}, "MUDANCAS": []}
    for campo, base in CAMPOS:
        c = {"SABE_ANTES": 0, "SABE_DEPOIS": 0, "NAO_SEI_PARA_VALOR": 0, "VALOR_PARA_NAO_SEI": 0,
             "VALOR_PARA_OUTRO": 0, "SO_A_BASE": 0}
        for k in sorted(set(antes) & set(depois)):
            a, d = antes[k], depois[k]
            c["SABE_ANTES"] += a[campo] != NAO_SEI
            c["SABE_DEPOIS"] += d[campo] != NAO_SEI
            if a[campo] != d[campo]:
                tipo = ("NAO_SEI_PARA_VALOR" if a[campo] == NAO_SEI else
                        "VALOR_PARA_NAO_SEI" if d[campo] == NAO_SEI else "VALOR_PARA_OUTRO")
            elif a[base] != d[base]:
                tipo = "SO_A_BASE"
            else:
                continue
            c[tipo] += 1
            fora["MUDANCAS"].append({"RUN_ID": k[0], "ORDEM": k[1], "SOURCE_ID": d["source_id"],
                                     "CAMPO": campo, "TIPO": tipo, "ANTES": a[campo],
                                     "DEPOIS": d[campo], "BASE_DEPOIS": (d[base] or "")[:300]})
        fora["CAMPOS"][campo] = c
    with open(saida_p, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(fora, fh, ensure_ascii=False, indent=1)
    print("   campo            sabe antes -> depois · NAO SEI->valor · valor->NAO SEI · valor->outro · so a base")
    for campo, c in fora["CAMPOS"].items():
        print("   %-16s %4d -> %-4d · %14d · %14d · %12d · %9d" % (
            campo, c["SABE_ANTES"], c["SABE_DEPOIS"], c["NAO_SEI_PARA_VALOR"],
            c["VALOR_PARA_NAO_SEI"], c["VALOR_PARA_OUTRO"], c["SO_A_BASE"]))
    print("   linhas %d -> %d · mudancas %d" % (len(antes), len(depois), len(fora["MUDANCAS"])))
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:4]))
