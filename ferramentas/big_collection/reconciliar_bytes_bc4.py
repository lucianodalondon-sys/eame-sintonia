#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RECONCILIAR OS BYTES DA MICRO REAL DA BC4 — pelo dono dos bytes, sem tocar na Sala.

    py ferramentas/big_collection/reconciliar_bytes_bc4.py --origem=<pasta> [--aplicar]

O QUE ACONTECEU (medido, 24/09/2026 00:53-01:00, bot 8eec2e2a)
--------------------------------------------------------------
A micro real pousou na Sala real (127.0.0.1:54330/sala_italia) 4 observacoes
(raw_asset 1406-1409) e 4 derivados (derived_artifact 909-912). As LINHAS estao
certas; os BYTES ficaram na arvore do bot (`XX/…` e `NAO_SEI/derivados/…`),
porque a linha instalada nao tinha a raiz operacional do armazem. Os caminhos
na Sala sao RELATIVOS a raiz do armazem.

O QUE ISTO FAZ
--------------
Para cada uma das 8 linhas: le da Sala (so SELECT, com
default_transaction_read_only) o `storage_path` e o `sha256`; le os bytes da
`--origem` (a arvore do bot, ou a copia C:/bc4/micro/bytes-copia); confere o
sha256; e escreve-os na raiz operacional (`SINTONIA_ARMAZEM_RAIZ`, a mesma que o
orquestrador passa a exigir) pelo `ArmazemLocal.enviar` — o dono dos bytes —,
no MESMO caminho relativo. Nenhuma linha da Sala muda: o caminho que a Sala ja
guarda passa a responder na raiz certa.

    NAO SE REESCREVE HISTORIA: `XX` e `NAO_SEI` ficam no caminho, porque foi
    assim que aquelas corridas nasceram (sem pais declarado). E verdade.

Recusa fechado: sha256 diferente, byte ausente, ou ficheiro ja presente na raiz
com OUTRO conteudo. Sem `--aplicar` so diz o que faria.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "scripts" / "micro_coleta"))
import _gavetas  # noqa: E402,F401
import micro_coleta as MC  # noqa: E402
from guarda.preservar_coleta import (ArmazemLocal, VARIAVEL_DA_RAIZ,  # noqa: E402
                                     raiz_do_armazem_local)

RAW_IDS = (1406, 1407, 1408, 1409)
DERIVED_IDS = (909, 910, 911, 912)


def linhas(consulta=MC.sql) -> list[dict]:
    r = consulta("select 'raw', r.id, so.storage_path, so.sha256 from raw_asset r"
                 " join storage_object so on so.id = r.storage_object_id"
                 " where r.id in (%s)" % ",".join(map(str, RAW_IDS)))
    d = consulta("select 'derived', d.id, d.storage_path, d.sha256 from derived_artifact d"
                 " where d.id in (%s)" % ",".join(map(str, DERIVED_IDS)))
    return [{"TABELA": t, "ID": int(i), "CAMINHO": c, "SHA256": s} for t, i, c, s in r + d]


def plano(origem: Path, raiz: str, consulta=MC.sql) -> list[dict]:
    out = []
    for l in linhas(consulta):
        fonte = origem / l["CAMINHO"]
        destino = Path(raiz) / l["CAMINHO"]
        if not fonte.is_file():
            out.append({**l, "ACCAO": "RECUSA", "PORQUE": "byte ausente na origem"})
            continue
        dados = fonte.read_bytes()
        if hashlib.sha256(dados).hexdigest() != l["SHA256"]:
            out.append({**l, "ACCAO": "RECUSA", "PORQUE": "sha256 da origem != sha256 da Sala"})
            continue
        if destino.is_file():
            igual = hashlib.sha256(destino.read_bytes()).hexdigest() == l["SHA256"]
            out.append({**l, "ACCAO": "JA_LA" if igual else "RECUSA",
                        "PORQUE": "" if igual else "destino ja existe com OUTRO conteudo"})
            continue
        out.append({**l, "ACCAO": "COPIAR", "BYTES": len(dados)})
    return out


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    origem = next((Path(a.split("=", 1)[1]) for a in argv if a.startswith("--origem=")), None)
    if origem is None:
        print(__doc__)
        return 2
    # o dono decide a raiz: OPERACIONAL exige a variavel e recusa a arvore
    raiz = raiz_do_armazem_local("OPERACIONAL", os.environ)
    p = plano(origem, raiz)
    recusas = [x for x in p if x["ACCAO"] == "RECUSA"]
    aplicar = "--aplicar" in argv and not recusas and len(p) == len(RAW_IDS) + len(DERIVED_IDS)
    if aplicar:
        armazem = ArmazemLocal(raiz)
        for x in p:
            if x["ACCAO"] == "COPIAR":
                armazem.enviar(x["CAMINHO"], (origem / x["CAMINHO"]).read_bytes(), None)
                x["ACCAO"] = "COPIADO"
    print(json.dumps({"RAIZ": raiz, VARIAVEL_DA_RAIZ: os.environ.get(VARIAVEL_DA_RAIZ),
                      "ORIGEM": str(origem), "LINHAS": p, "APLICADO": aplicar,
                      "SALA_ESCRITA": 0}, ensure_ascii=False, indent=1))
    return 1 if recusas else 0


if __name__ == "__main__":
    raise SystemExit(main())
