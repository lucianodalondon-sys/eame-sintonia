#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SEMEAR O LIFECYCLE a partir do que a missao 04 ja tinha provado.

    NAO SE INVENTA ESTADO. IMPORTA-SE O QUE JA FOI MEDIDO.

`READY-FOR-COLLECTION-V1.json` ja carrega, por fonte, o desfecho do contrato,
do canario e do gate de rota. Este script traduz esses desfechos para
transicoes do livro, preservando a razao e a evidencia originais.

⚠️ O QUE ELE NAO FAZ: nao promove nada que o canario nao tenha passado, e
nao re-corre rede. E uma IMPORTACAO de historia, nao uma nova medicao — o
carimbo `EVIDENCE_REF` aponta para o ficheiro da missao 04, de proposito,
para que ninguem confunda isto com prova de hoje.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))

import fila as F          # noqa: E402
import lifecycle as LC    # noqa: E402

READY = RAIZ / "curadoria" / "READY-FOR-COLLECTION-V1.json"

# O estado da missao 04 -> o caminho de transicoes que o produz.
# Cada fonte passa por CANARY_PENDING porque foi, de facto, por la que passou.
CAMINHO = {
    "READY_FOR_COLLECTION": [
        (LC.CANARY_PENDING, "contrato valido, aguardava canario"),
        (LC.READY_FOR_COLLECTION, "canario resolveu contra a rede real"),
    ],
    "CONTRACT_READY_ROUTE_BLOCKED": [
        (LC.CANARY_PENDING, "contrato valido, aguardava canario"),
        (LC.CONTRACT_READY_ROUTE_BLOCKED,
         "canario passou e a rota esta em Disallow no robots vivo"),
    ],
    "CONTRACTED_CANARY_FAILED": [
        (LC.CANARY_PENDING, "contrato valido, aguardava canario"),
        (LC.CONTRACTED_CANARY_FAILED, "canario nao trouxe item com identidade"),
    ],
}


def main() -> int:
    d = json.loads(READY.read_text(encoding="utf-8"))
    ref = "MISSAO-04:curadoria/READY-FOR-COLLECTION-V1.json@%s" % \
          d["SOURCE_CURATOR_HEAD"][:12]

    ja = LC.snapshot()
    novas, saltadas = 0, 0
    for f in d["FONTES"]:
        sid, estado = f["SOURCE_ID"], f["STATE"]
        if sid in ja:
            saltadas += 1
            continue
        for novo, porque in CAMINHO[estado]:
            LC.registar(sid, novo, porque, evidence_ref=ref)
        novas += 1

        # As bloqueadas por robots NAO geram trabalho: insistir no que a
        # politica barra nao e persistencia, e contorno.
        if estado == "CONTRACTED_CANARY_FAILED":
            F.enfileirar(sid, F.CANARY, priority=40,
                         motivo="canario falhou na missao 04 — tentar de novo")

    print("SEMEADAS   = %d" % novas)
    print("JA_EXISTIAM= %d" % saltadas)
    print("FONTES     = %s" % json.dumps(
        {k: v for k, v in LC.metricas().items() if v}, ensure_ascii=False))
    print("FILA       = %s" % json.dumps(F.metricas(), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
