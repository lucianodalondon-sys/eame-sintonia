#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LOTES DE ENTREGA — fontes provadas, empacotadas para a Collection.

    O LOTE E UMA FORMA DE ENTREGA, NAO UM PORTAO.

O worker NAO para porque «ja tenho 10 prontas». Fecha o lote e continua.
Uma fonte entra num lote uma unica vez: o lote regista quem ja foi
entregue, para que o seguinte traga so o que e novo.

⚠️ O QUE UM LOTE NAO E: nao e integracao. Enquanto a reconciliacao
pos-Big-Collection nao terminar, o lote fica GUARDADO na linha do Curator.
Guardar nao e entregar, e dize-lo evita que alguem leia um ficheiro cheio
de fontes como se ja estivessem na Collection.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))

import interface_collection as IC    # noqa: E402
import lifecycle as LC               # noqa: E402

LOTES = RAIZ / "curadoria" / "READY-BATCHES-V1.json"
CARACT = RAIZ / "curadoria" / "SOURCE-CHARACTERIZATION-V1.json"
ALLOC = RAIZ / "curadoria" / "SOURCE-ID-ALLOCATION-V1.json"


def _nomes() -> dict:
    n = {}
    if ALLOC.exists():
        for x in json.loads(ALLOC.read_text(encoding="utf-8"))["NOVAS"]:
            n[x["SOURCE_ID"]] = {"NAME": x.get("NOME") or x.get("NAME", "NAO SEI"),
                                 "CANDIDATE_ID": x.get("CANDIDATE_ID")}
    return n


def _ler() -> dict:
    if LOTES.exists():
        return json.loads(LOTES.read_text(encoding="utf-8"))
    return {"DATASET": "READY-BATCHES-V1",
            "LEI": ("lotes guardados na linha do Curator. GUARDADO != "
                    "INTEGRADO: nada aqui entrou na Collection oficial."),
            "PROXIMO": 1, "LOTES": []}


def fechar_lote() -> dict:
    """Fecha um lote com o que esta READY e ainda nao foi entregue."""
    d = _ler()
    ja = {s for l in d["LOTES"] for s in l["SOURCE_IDS"]}
    nomes = _nomes()

    novas = [r for r in IC.ready_sources() if r["SOURCE_ID"] not in ja]
    if not novas:
        return {"CRIADO": False, "PORQUE": "nenhuma fonte READY nova desde o ultimo lote",
                "READY_JA_ENTREGUES": len(ja)}

    bid = "READY-BATCH-%03d" % d["PROXIMO"]
    fontes = []
    for r in novas:
        n = nomes.get(r["SOURCE_ID"], {})
        fontes.append({
            "SOURCE_ID": r["SOURCE_ID"],
            "SOURCE_NAME": n.get("NAME", "NAO SEI"),
            "COUNTRY": "IT",
            "TERRITORY": r["TERRITORY"],
            "SOURCE_TYPE": r["CAPABILITY"],
            "CAPABILITY": r["CAPABILITY"],
            "CONTRACT_VERSION": r["CONTRACT_VERSION"],
            "ROUTE_VERSION": r["ROUTE_VERSION"],
            "LAST_CANARY_AT": r["LAST_SUCCESSFUL_CANARY_AT"],
            "LAST_VALIDATED_AT": r["LAST_VALIDATED_AT"],
            "HEALTH": r["HEALTH"],
            "PROVENANCE_REF": r["EVIDENCE_REF"],
            "CADENCE": r["CADENCE"],
            # a regua viaja com a fonte: um lote com LEGACY dentro diz-o
            "READY_RULE": r.get("READY_RULE", "NAO SEI"),
        })

    lote = {"READY_BATCH_ID": bid,
            "READY_BATCH_CREATED_AT": LC.agora(),
            "READY_BATCH_COUNT": len(fontes),
            "ESTADO": "GUARDADO_NA_LINHA_DO_CURATOR",
            "PORQUE_NAO_INTEGRADO": ("a reconciliacao pos-Big-Collection ainda "
                                     "corre em source-curator-integration-v1"),
            "SOURCE_IDS": [f["SOURCE_ID"] for f in fontes],
            "FONTES": fontes}
    d["LOTES"].append(lote)
    d["PROXIMO"] += 1
    d["READY_BATCHES_CREATED"] = len(d["LOTES"])
    d["READY_SOURCES_WAITING_FOR_COLLECTION"] = len(ja) + len(fontes)
    LOTES.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    return {"CRIADO": True, **{k: lote[k] for k in
            ("READY_BATCH_ID", "READY_BATCH_CREATED_AT", "READY_BATCH_COUNT")}}


def main() -> int:
    r = fechar_lote()
    print(json.dumps(r, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
