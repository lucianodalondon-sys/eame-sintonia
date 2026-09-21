#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A LINHAGEM DE CADA CANDIDATA — CANDIDATE_ID -> SOURCE_ID -> TASK_ID -> estado.

    QUEM PERGUNTA «O QUE ACONTECEU A CAND-0179?» TEM DE TER UMA RESPOSTA
    NUM SITIO SO.

Medido no PASSO 1: a ligacao vivia partida em quatro ficheiros. A candidata
(FONTES-CANDIDATAS.json) nao sabe o seu SOURCE_ID (0 de 241 preenchidos); o
SOURCE_ID nasce em SOURCE-ID-ALLOCATION-V1.json ou em CANDIDATE-TO-SOURCE-
MATCH-V1.json; a tarefa vive em LIFECYCLE-QUEUE-V1.json pelo SOURCE_ID; e o
estado no livro. Nenhum deles guarda o CANDIDATE_ID ao lado do TASK_ID.

Este ficheiro NAO e uma quinta verdade: e uma JUNCAO derivada dos quatro,
recalculada do disco sempre que corre, e reprova se um SOURCE_ID aparecer com
duas candidatas (a mesma fonte com dois numeros seria o pior erro da casa; o
inverso — um numero com duas candidatas — e o que este ficheiro vigia).
"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))
import lifecycle as LC     # noqa: E402
import ready_split as RS   # noqa: E402

CUR = RAIZ / "curadoria"
CANDIDATAS = RAIZ / "candidatas" / "FONTES-CANDIDATAS.json"
ALLOC = CUR / "SOURCE-ID-ALLOCATION-V1.json"
MATCH = CUR / "CANDIDATE-TO-SOURCE-MATCH-V1.json"
FILA = CUR / "LIFECYCLE-QUEUE-V1.json"
CONTRATOS = CUR / "italy_contracts_curator.json"
SAIDA = CUR / "CANDIDATE-LINEAGE-V1.json"


def _ler(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def calcular() -> dict:
    cands = _ler(CANDIDATAS)["CANDIDATAS"]
    sid_de: dict[str, tuple[str, str]] = {}
    for n in _ler(ALLOC)["NOVAS"]:
        sid_de[n["CANDIDATE_ID"]] = (n["SOURCE_ID"], "ALLOCATION")
    for m in _ler(MATCH)["MATCHES"]:
        sid_de.setdefault(m["CANDIDATE_ID"], (m["MATCHED_SOURCE_ID"], "ATLAS_MATCH"))
    tarefas = defaultdict(list)
    for t in _ler(FILA)["TAREFAS"]:
        tarefas[t["SOURCE_ID"]].append({"TASK_ID": t["TASK_ID"], "TASK_TYPE": t["TASK_TYPE"],
                                        "STATUS": t["STATUS"]})
    contratos = {c["SOURCE_ID"]: c.get("SOURCE_CONTRACT_HASH") for c in _ler(CONTRATOS)["FONTES"]}
    est = LC.snapshot()

    linhas, por_sid = [], defaultdict(list)
    for c in cands:
        cid = c["CANDIDATA_ID"]
        sid, via = sid_de.get(cid, (None, None))
        if sid:
            por_sid[sid].append(cid)
        linhas.append({
            "CANDIDATE_ID": cid, "URL": c["URL"], "TIPO": c["TIPO"],
            "SOURCE_ID": sid, "SOURCE_ID_VIA": via,
            "CONTRACT_HASH": contratos.get(sid) if sid else None,
            "TASKS": tarefas.get(sid, []) if sid else [],
            "ESTADO_NO_LIVRO": est.get(sid) if sid else None,
            "READY_RULE": RS.regua_de(sid) if sid and est.get(sid) == LC.READY_FOR_COLLECTION else None,
        })

    colisoes = {s: cs for s, cs in por_sid.items() if len(cs) > 1}
    return {
        "DATASET": "CANDIDATE-LINEAGE-V1",
        "LEI": ("juncao derivada de candidatas + alocacao + match + fila + livro; "
                "recalculada do disco. Um SOURCE_ID com duas candidatas REPROVA."),
        "GERADO_EM": datetime.now(timezone.utc).isoformat(),
        "CANDIDATAS": len(linhas),
        "COM_SOURCE_ID": sum(1 for l in linhas if l["SOURCE_ID"]),
        "COM_TAREFA": sum(1 for l in linhas if l["TASKS"]),
        "POR_ESTADO": dict(Counter(l["ESTADO_NO_LIVRO"] or "SEM_LIVRO" for l in linhas)),
        "SOURCE_ID_COM_DUAS_CANDIDATAS": colisoes,
        "LINHAS": linhas,
    }


def main() -> int:
    r = calcular()
    SAIDA.write_text(json.dumps(r, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("CANDIDATAS %d · COM_SOURCE_ID %d · COM_TAREFA %d" % (r["CANDIDATAS"], r["COM_SOURCE_ID"], r["COM_TAREFA"]))
    print("POR_ESTADO %s" % json.dumps(r["POR_ESTADO"], ensure_ascii=False))
    if r["SOURCE_ID_COM_DUAS_CANDIDATAS"]:
        print("REPROVADO: SOURCE_ID com duas candidatas: %s" % r["SOURCE_ID_COM_DUAS_CANDIDATAS"])
        return 2
    print("escrito: %s" % SAIDA.relative_to(RAIZ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
