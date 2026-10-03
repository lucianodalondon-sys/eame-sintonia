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
# A prova da ultima corrida do motor de descoberta (curadoria/descobrir.py).
DISCOVERY_PROOF = RAIZ / "curadoria" / "DISCOVERY-PROOF-V1.json"

# Importacao tardia para evitar ciclo: supervisor importa fila, nao status_live.
def _estado_servico() -> dict:
    """Le o estado do servico derivado do PID real. Nunca levanta excecao."""
    try:
        from supervisor import ler_estado_servico  # noqa: E402
        return ler_estado_servico()
    except Exception:
        return {"SOURCE_CURATOR_SERVICE": "UNKNOWN", "WORKER_ALIVE": False}


def _nivel_da_fila() -> dict:
    """Mede e ESCREVE o sinal (DISCOVERY-SIGNAL-V1.json) a cada volta. Se a
    medicao falhar, o painel diz NAO SEI em vez de herdar o numero anterior."""
    try:
        import nivel_da_fila as NIVEL  # noqa: E402
        r = NIVEL.escrever()
        return {"CANDIDATE_BACKLOG": r["CANDIDATE_BACKLOG"],
                "CANDIDATE_LOW_WATERMARK": r["CANDIDATE_LOW_WATERMARK"],
                "DISCOVERY_SIGNAL": r["DISCOVERY_SIGNAL"]}
    except Exception as e:
        return {"CANDIDATE_BACKLOG": "NAO SEI", "CANDIDATE_LOW_WATERMARK": "NAO SEI",
                "DISCOVERY_SIGNAL": "NAO SEI: %s" % type(e).__name__}


def _status_discovery() -> dict:
    """Os quatro campos da descoberta, LIDOS da prova da ultima corrida.

    Enxerto de candidate-bridge-v1 (63b71421) sem os literais: la, o ramo
    `except` devolvia CANDIDATES_TOTAL = 0 e READY_LEGACY = 18 escritos a
    mao — um zero que parece medicao e um 18 que nao acompanha o livro. Aqui
    nao ha numero que nao venha do ficheiro; sem ficheiro e NUNCA, ficheiro
    ilegivel e «NAO SEI: <Excecao>». A idade da corrida vai ao lado.

    A descoberta nao e um servico com processo: e uma corrida que deixa uma
    prova. DISCOVERY_SERVICE diz isso — NOT_RUN ou RAN — e nunca ACTIVE.
    """
    try:
        if not DISCOVERY_PROOF.exists():
            return {"DISCOVERY_SERVICE": "NOT_RUN",
                    "LAST_DISCOVERY_RUN": "NUNCA",
                    "LAST_DISCOVERY_RUN_AGE_H": "NUNCA",
                    "CANDIDATES_NEW": "NUNCA",
                    "DEDUP_REJECTED": "NUNCA"}
        p = json.loads(DISCOVERY_PROOF.read_text(encoding="utf-8"))
        corrida = p["CORRIDA_EM"]
        idade_h = round((datetime.now(timezone.utc)
                         - datetime.fromisoformat(corrida)).total_seconds() / 3600, 1)
        return {"DISCOVERY_SERVICE": "RAN",
                "LAST_DISCOVERY_RUN": corrida,
                "LAST_DISCOVERY_RUN_AGE_H": idade_h,
                "CANDIDATES_NEW": p["NOVEL_CANDIDATES"],
                "DEDUP_REJECTED": p["DUPLICATES_REJECTED"]}
    except Exception as e:  # noqa: BLE001 — o painel nao rebenta, diz NAO SEI
        nao_sei = "NAO SEI: %s" % type(e).__name__
        return {"DISCOVERY_SERVICE": nao_sei,
                "LAST_DISCOVERY_RUN": nao_sei,
                "LAST_DISCOVERY_RUN_AGE_H": nao_sei,
                "CANDIDATES_NEW": nao_sei,
                "DEDUP_REJECTED": nao_sei}


def _rendimento() -> dict:
    """Area «SOURCE CURATOR — RENDIMENTO» do painel. SAUDE != PRODUCAO.

    Deriva da telemetria (ZERO LLM). Defensiva: se algo falhar, o painel de
    SAUDE continua a funcionar — um erro aqui NUNCA pode partir a escrita de
    status do servico vivo.
    """
    try:
        from telemetria_do_curador import metricas  # noqa: E402
        m = metricas()
        j24 = m["JANELA_24H"]
        return {
            # ⚠️ SAUDE — o servico esta vivo?
            "HEALTH_SERVICE_STATE": m["AGORA"]["SERVICE_STATE"],
            "HEALTH_SUPERVISOR_ALIVE": m["AGORA"]["SUPERVISOR_ALIVE"],
            "HEALTH_WORKER_STATE": m["AGORA"]["WORKER_STATE"],
            # ⚠️ PRODUCAO — o servico esta a PRODUZIR? (separado da saude)
            "PRODUCTIVITY_STATE": m["PRODUCTIVITY_STATE"],
            "READY_CURRENT_24H": j24["READY_CURRENT"],          # indicador PRINCIPAL
            "QUALIFY_COMPLETED_24H": j24["QUALIFY_COMPLETED"],  # trabalho util (mesmo se bloqueou)
            "QUALIFY_TO_READY_YIELD_24H": m["RENDIMENTO"]["QUALIFY_TO_READY_YIELD_24H"],
            "READY_CURRENT_1H": m["JANELA_1H"]["READY_CURRENT"],
            "QUALIFY_COMPLETED_1H": m["JANELA_1H"]["QUALIFY_COMPLETED"],
            "NEW_CANDIDATES_24H": j24["NEW_CANDIDATES"],
            "RETRY_24H": j24["RETRY"], "REJECTED_24H": j24["REJECTED"],
            "CAPABILITY_BLOCK_24H": j24["CAPABILITY_BLOCK"],
            "UNKNOWN_24H": j24["UNKNOWN"],
            "QUALIFY_PENDING": m["AGORA"]["QUALIFY_PENDING"],
            "QUEUE_DRAIN_ESTIMATE": m["QUEUE_DRAIN_ESTIMATE"],
            "DISCOVERY_HEALTH": m["DISCOVERY_HEALTH"],
            # ⚠️ NAVEGABILIDADE — o numero chega a fonte real
            "READY_CURRENT_24H_SOURCES": _ready_sources_24h(),
            "LLM_USED_FOR_METRICS": "NO",
        }
    except Exception as ex:
        return {"RENDIMENTO_ERRO": str(ex)[:200], "LLM_USED_FOR_METRICS": "NO"}


def _ready_sources_24h() -> list:
    """As fontes reais promovidas nas ultimas 24h, com nome/tipo/resumo curto."""
    try:
        from datetime import timedelta
        import telemetria_do_curador as TT
        import cartao_de_fonte as CC
        agora = datetime.now(timezone.utc)
        janela = TT.ready_sources_janela(TT._ledger_transicoes(),
                                         agora - timedelta(hours=24), agora)
        return CC.cartoes_navegaveis([r["SOURCE_ID"] for r in janela])[:50]
    except Exception:
        return []


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
    _disc = _status_discovery()
    _rend = _rendimento()
    return {
        "GERADO_EM": LC.agora(),

        # Derivado do PID real — nao hardcoded.
        # SOURCE_CURATOR_RUNNING mantido por compatibilidade; o campo canonico
        # e SOURCE_CURATOR_SERVICE (RUNNING / STOPPED / BLOCKED). «Running»
        # aqui e o SERVICO (supervisor vivo), nao o worker — um servico com o
        # worker IDLE continua a correr.
        **_estado_servico_snapshot,
        "SOURCE_CURATOR_RUNNING": (
            _estado_servico_snapshot.get("SOURCE_CURATOR_SERVICE") == "RUNNING"),

        # ⚠️ QUATRO NUMEROS, E NENHUM SUBSTITUI OUTRO.
        #
        #   READY_TOTAL          o estado no livro. NAO e «prontas».
        #   READY_LEGACY         promovidas pela regua antiga. NAO sao prontas.
        #   READY_CURRENT        promovidas pelo gate de detalhe.
        #   COLLECTION_ELIGIBLE  o que a Collection pode mesmo tocar hoje
        #                        (READY_CURRENT menos as que pedem olho humano).
        #
        # Um painel que diz «87 prontas» com 77 delas por remedir e um painel
        # que mente devagar. Quem autoriza coleta le COLLECTION_ELIGIBLE.
        "READY_TOTAL": m["READY"],
        "READY_LEGACY": m["READY_LEGACY"],
        "READY_CURRENT": m["READY_CURRENT"],
        "HUMAN_REVIEW_REQUIRED": m["HUMAN_REVIEW_REQUIRED"],
        "COLLECTION_ELIGIBLE": m["COLLECTION_ELIGIBLE"],
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

        # O GATILHO DE FILA BAIXA (PASSO 8): quantas candidatas ainda podem
        # virar trabalho automatico, e se ja e preciso pedir descoberta.
        **_nivel_da_fila(),

        # A ULTIMA CORRIDA DA DESCOBERTA: lida da prova, nunca escrita a mao.

        "POR_ESTADO": {k: v for k, v in LC.metricas().items() if v},

        # Campos de discovery (FASE 12)
        **_disc,

        # SOURCE CURATOR — RENDIMENTO (observabilidade; SAUDE != PRODUCAO)
        "SOURCE_CURATOR_RENDIMENTO": _rend,
    }


def main() -> int:
    s = status()
    SAIDA.write_text(json.dumps(s, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(s, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
