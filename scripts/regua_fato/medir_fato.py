#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""REGUA-DO-TIPO-DE-FATO · o classificador `leis/tipo_do_fato.py` contra os rotulos.

    py scripts/regua_fato/medir_fato.py                 # GABARITO (dentro da amostra)
    py scripts/regua_fato/medir_fato.py --cega          # PROVA CEGA (so depois de o classificador estar congelado)

Sem rede. Por tipo: precisao (quando o classificador o diz, o rotulo concorda) e recall; cobertura
(quantos saem de NAO_SEI); a matriz rotulo -> classificador. Escreve MEDICAO-FATO-<CONJUNTO>-V1.json.
"""
import json
import sys
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
AQUI = Path(__file__).parent
sys.path.insert(0, str(RAIZ / "leis"))
import tipo_do_fato as TF  # noqa: E402

TEXTOS = Path.home() / "sintonia-gabarito" / "REGUA-FATO-V1" / "textos"
PRONTO_MINIMO, PRONTO_PRECISAO = 10, 0.90


def main():
    cega = "--cega" in sys.argv
    nome = "PROVA-CEGA" if cega else "GABARITO"
    rot = json.loads((AQUI / "rotulos" / ("rotulos-cega.json" if cega else "rotulos-gabarito.json")).read_text(encoding="utf-8"))
    m, linhas = Counter(), []
    for x in rot:
        r = TF.tipo_do_fato((TEXTOS / (x["ID"] + ".txt")).read_text(encoding="utf-8"))
        m[(x["AGRO_FACT_KIND"], r["agro_fact_kind"])] += 1
        linhas.append({"ID": x["ID"], "ROTULO": x["AGRO_FACT_KIND"], "CLASSIFICADOR": r["agro_fact_kind"],
                       "BASE": r["agro_fact_kind_basis"][:240]})
    por_tipo = {}
    for k in TF.TIPOS:
        if k == TF.NAO_SEI:
            continue
        tp = m[(k, k)]
        ditos = sum(v for (a, b), v in m.items() if b == k)
        ouro = sum(v for (a, b), v in m.items() if a == k)
        prec = round(tp / ditos, 3) if ditos else None
        por_tipo[k] = {"OURO": ouro, "DITOS": ditos, "CERTOS": tp, "PRECISAO": prec,
                       "RECALL": round(tp / ouro, 3) if ouro else None,
                       "ESTADO": ("NAO MEDIDO (<%d exemplos)" % PRONTO_MINIMO if ouro < PRONTO_MINIMO
                                  else "PRONTO" if prec is not None and prec >= PRONTO_PRECISAO else "NAO PRONTO")}
    ditos = [l for l in linhas if l["CLASSIFICADOR"] != TF.NAO_SEI]
    certos = sum(1 for l in ditos if l["CLASSIFICADOR"] == l["ROTULO"])
    out = {"DATASET": "MEDICAO-FATO-%s-V2" % nome, "MEDIDO_DENTRO_DA_AMOSTRA": not cega, "ITENS": len(rot),
           "COBERTURA": {"SAEM_DE_NAO_SEI": len(ditos), "DE": len(rot)},
           "PRECISAO_GLOBAL_QUANDO_DIZ": {"CERTOS": certos, "DITOS": len(ditos),
                                          "PRECISAO": round(certos / len(ditos), 3) if ditos else None},
           "POR_TIPO": por_tipo,
           "MATRIZ_ROTULO_CLASSIFICADOR": {"%s->%s" % k: v for k, v in sorted(m.items())},
           "ERROS": [l for l in ditos if l["CLASSIFICADOR"] != l["ROTULO"]],
           "LINHAS": linhas}
    (AQUI / ("MEDICAO-FATO-%s-V2.json" % nome)).write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n",
                                                          encoding="utf-8")
    print(json.dumps({k: out[k] for k in ("ITENS", "COBERTURA", "PRECISAO_GLOBAL_QUANDO_DIZ", "POR_TIPO")},
                     ensure_ascii=False, indent=1))
    for e in out["ERROS"]:
        print("ERRO", e["ID"], e["ROTULO"], "->", e["CLASSIFICADOR"], "|", e["BASE"][:160])


if __name__ == "__main__":
    main()
