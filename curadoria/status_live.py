#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""STATUS LIVE DO SOURCE CURATOR — o que alimenta «IT — SOURCES STATUS LIVE».

    UM PAINEL QUE MENTE E PIOR DO QUE NAO TER PAINEL.

Tudo aqui e derivado do livro e da fila no instante da chamada. Nada e
carimbado: se uma fonte degradou ha um segundo, o numero muda agora.

`*_TODAY` conta transicoes do dia UTC corrente lidas do livro — nao um
contador que alguem incrementa e esquece de zerar.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))

import fila as F                     # noqa: E402
import interface_collection as IC    # noqa: E402
import lifecycle as LC               # noqa: E402

SAIDA = RAIZ / "curadoria" / "SOURCE-CURATOR-STATUS-LIVE.json"
LOTES = RAIZ / "curadoria" / "READY-BATCHES-V1.json"

# Importacao tardia para evitar ciclo: supervisor importa fila, nao status_live.
def _estado_servico() -> dict:
    """Le o estado do servico derivado do PID real. Nunca levanta excecao."""
    try:
        from supervisor import ler_estado_servico  # noqa: E402
        return ler_estado_servico()
    except Exception:
        return {"SOURCE_CURATOR_SERVICE": "UNKNOWN", "WORKER_ALIVE": False}


def status() -> dict:
    livro = LC._ler_bruto()["TRANSICOES"]
    hoje = datetime.now(timezone.utc).date().isoformat()
    do_dia = [t for t in livro if t["OBSERVED_AT"][:10] == hoje]

    # ⚠️ PROMOCOES != FONTES PROMOVIDAS. Uma fonte reparada e promovida DUAS
    # vezes no mesmo dia (antes de degradar, e depois do canario do reparo).
    # Medido: 19 promocoes para 18 fontes distintas. Publicar o numero de
    # promocoes debaixo de um nome que diz «fontes» faz o painel contradizer
    # o READY_TOTAL ao lado — e quem le acredita no maior.
    #
    #     CONTAR PELA UNIDADE SEMANTICA CERTA.
    promocoes = [t for t in do_dia if t["NEW_STATE"] == LC.READY_FOR_COLLECTION]
    promovidas = promocoes
    fontes_promovidas_hoje = {t["SOURCE_ID"] for t in promocoes}
    reparadas = [t for t in promocoes if t["PREVIOUS_STATE"] == LC.REPAIRING]
    falhadas = [t for t in do_dia if t["NEW_STATE"] == LC.CONTRACTED_CANARY_FAILED]
    descobertas = [t for t in do_dia if t["NEW_STATE"] == LC.DISCOVERED]
    canarios = [t for t in do_dia if t["NEW_STATE"] in
                (LC.READY_FOR_COLLECTION, LC.CONTRACTED_CANARY_FAILED)]

    ultima = livro[-1] if livro else {}
    ult_prom = promovidas[-1]["SOURCE_ID"] if promovidas else "NENHUMA"
    bloqueios = [t for t in livro if t["NEW_STATE"] in LC.PARADOS]

    q = F._ler()["TAREFAS"]
    em_curso = [t for t in q if t["STATUS"] == F.IN_PROGRESS]

    lotes = json.loads(LOTES.read_text(encoding="utf-8")) if LOTES.exists() \
        else {"LOTES": []}
    entregues = {s for l in lotes["LOTES"] for s in l["SOURCE_IDS"]}

    m = IC.metricas_operacionais()
    _estado_servico_snapshot = _estado_servico()
    return {
        "GERADO_EM": LC.agora(),

        # Derivado do PID real — nao hardcoded.
        # SOURCE_CURATOR_RUNNING mantido por compatibilidade; o campo canonico
        # e SOURCE_CURATOR_SERVICE (RUNNING / STOPPED / BLOCKED).
        **_estado_servico_snapshot,
        "SOURCE_CURATOR_RUNNING": _estado_servico_snapshot.get("WORKER_ALIVE",
                                                                False),

        "READY_TOTAL": m["READY"],
        # READY_LEGACY (regua antiga) != READY_CURRENT (gate de detalhe).
        # Um painel que some os dois num numero esconde que regua promoveu.
        "READY_LEGACY": m["READY_LEGACY"],
        "READY_CURRENT": m["READY_CURRENT"],
        "READY_TODAY": len(fontes_promovidas_hoje),
        "PROMOTIONS_TODAY": len(promocoes),
        "DISCOVERED_TODAY": len(descobertas),
        "CANARIES_TODAY": len(canarios),
        "FAILED_TODAY": len(falhadas),
        "REPAIRED_TODAY": len(reparadas),

        "QUEUE_PENDING": m["QUEUE_PENDING"],
        "QUEUE_ELIGIBLE_NOW": m["QUEUE_ELIGIBLE_NOW"],
        "QUEUE_WAITING_RETRY": m["QUEUE_WAITING_RETRY"],

        "CURRENT_SOURCE": em_curso[0]["SOURCE_ID"] if em_curso else "NENHUMA",
        "CURRENT_TASK": em_curso[0]["TASK_TYPE"] if em_curso else "OCIOSO",
        "LAST_COMPLETED_SOURCE": ultima.get("SOURCE_ID", "NENHUMA"),
        "LAST_PROMOTED_SOURCE": ult_prom,
        "LAST_BLOCK_REASON": (bloqueios[-1]["REASON"][:140]
                              if bloqueios else "NENHUM"),

        "READY_BATCHES_CREATED": len(lotes["LOTES"]),
        "READY_SOURCES_WAITING_FOR_COLLECTION": len(entregues),

        "POR_ESTADO": {k: v for k, v in LC.metricas().items() if v},
    }


def main() -> int:
    s = status()
    SAIDA.write_text(json.dumps(s, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(s, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
