#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PROVA-TETO sobre o PLANO do MICRO (sem rede).

    py ferramentas/integra_onda2/prova_teto_micro.py --lote <LOTE-MICRO.json> [--saida <plano.json>] [--json <resultado.json>]

Faz o plano do runbook SO para as fontes do lote (`micro_coleta.plano(ids)`) e confere-o com a prova
independente do teto D38 (`provas/prova_teto_dominio.verificar_plano`), no PIOR CASO: cada fonte PRONTA
gasta 5 pedidos (robots + indice + 3 materias). O plano do MICRO nao traz previsao por dominio; o pior
caso e o limite que o transporte deixa sair. Sai 0 = PASS, 1 = FAIL, 2 = NAO_SEI.
"""
import argparse
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for p in ("scripts/micro_coleta", "provas", ""):
    sys.path.insert(0, os.path.join(RAIZ, p) if p else RAIZ)
PIOR_CASO_POR_FONTE = 5


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--lote", required=True)
    ap.add_argument("--saida")
    ap.add_argument("--json")
    a = ap.parse_args(argv)
    os.chdir(RAIZ)
    import micro_coleta as M
    import prova_teto_dominio as T
    with open(a.lote, encoding="utf-8") as f:
        ids = [x["SOURCE_ID"] for x in json.load(f)["LOTE"]]
    plano = M.plano(ids)
    if a.saida:
        with open(a.saida, "w", encoding="utf-8") as f:
            json.dump(plano, f, ensure_ascii=False, indent=1)
    with open("regras/italy_contracts_onboarded.json", encoding="utf-8") as f1, \
            open("regras/italy_contracts.mjs", encoding="utf-8") as f2:
        ind = T.indices_dos_contratos(f1.read(), f2.read())
    prontas = [l["SOURCE_ID"] for l in plano["LINHAS"] if l.get("ESTADO") == "PRONTA"]
    prev = {}
    for s in prontas:
        if s in ind:
            d = T.dominio_registavel(ind[s])
            prev[d] = prev.get(d, 0) + PIOR_CASO_POR_FONTE
    r = T.verificar_plano({"PEDIDOS_POR_DOMINIO": prev}, prontas, ind)
    r.update({"BASE": "pior caso: %d pedidos por fonte PRONTA" % PIOR_CASO_POR_FONTE, "LOTE": ids,
              "PRONTAS": prontas,
              "BLOQUEADAS": {l["SOURCE_ID"]: l.get("FALTA") for l in plano["LINHAS"] if l.get("ESTADO") != "PRONTA"}})
    if not prontas:
        r["ESTADO"] = "NAO_SEI"
    if a.json:
        with open(a.json, "w", encoding="utf-8") as f:
            json.dump(r, f, ensure_ascii=False, indent=1)
    print("PROVA_TETO_MICRO=%s · prontas=%d de %d · previstos=%s" % (r["ESTADO"], len(prontas), len(ids), prev))
    for s, falta in r["BLOQUEADAS"].items():
        print("  BLOQUEADA  %s  %s" % (s, falta))
    return {"PASS": 0, "FAIL": 1}.get(r["ESTADO"], 2)


if __name__ == "__main__":
    sys.exit(main())
