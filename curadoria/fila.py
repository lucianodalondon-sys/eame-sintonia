#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A FILA DURAVEL DO SOURCE CURATOR — trabalho que sobrevive ao processo.

    SE O AGENTE PARAR, NAO SE PERDE TRABALHO.
    SE REINICIAR, CONTINUA DE ONDE PAROU.

O disco e a fila. A RAM nao e fila — uma lista em memoria desaparece com o
processo e leva consigo o que faltava fazer.

---------------------------------------------------------------------------
A REGRA QUE ESTA MISSAO EXISTE PARA PROVAR (FASE 4)

    UM 429 NUMA FONTE NAO PODE PARAR AS OUTRAS.

O erro classico e `time.sleep(retry_after)`: o processo adormece e toda a
fila adormece com ele. Aqui um 429 nao dorme — MARCA `NEXT_ATTEMPT_AT` no
futuro e a tarefa deixa de ser ELEGIVEL. O worker pega a seguinte e continua.
Quando o relogio passa `NEXT_ATTEMPT_AT`, a tarefa volta sozinha a ser
elegivel, sem ninguem a acordar.

    ESPERAR != BLOQUEAR.
    Uma tarefa adiada esta a esperar. Um worker adormecido esta a bloquear.

O tempo e injetavel (`agora=`) de proposito: uma prova de backoff que exige
esperar 60s reais nao se corre, e uma prova que nao se corre nao prova nada.
"""
from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
FILA = RAIZ / "curadoria" / "LIFECYCLE-QUEUE-V1.json"

CONTRATO = "SOURCE_CURATOR_QUEUE/v1"

# TASK_TYPE — cada um mapeia para UMA etapa que ja existe nesta casa.
DISCOVER = "DISCOVER"
QUALIFY = "QUALIFY"
BUILD_CONTRACT = "BUILD_CONTRACT"
VALIDATE_ROUTE = "VALIDATE_ROUTE"
CANARY = "CANARY"
CHARACTERIZE = "CHARACTERIZE"
REPAIR = "REPAIR"
REVALIDATE = "REVALIDATE"

TASK_TYPES = frozenset({DISCOVER, QUALIFY, BUILD_CONTRACT, VALIDATE_ROUTE,
                        CANARY, CHARACTERIZE, REPAIR, REVALIDATE})

PENDING = "PENDING"
IN_PROGRESS = "IN_PROGRESS"
DONE = "DONE"
FAILED = "FAILED"
WAITING_RETRY = "WAITING_RETRY"
BLOCKED = "BLOCKED"

# Teto de tentativas. Sem teto, uma fonte morta e reencontrada para sempre e
# a fila nunca esvazia.
MAX_ATTEMPTS = 5

# Backoff exponencial em segundos, por numero de tentativas ja feitas.
# Usado SO quando a plataforma nao disse Retry-After. Quando ela diz, manda
# ela: o relogio da casa nao sabe mais do que o servidor sobre o servidor.
BACKOFF = (60, 300, 900, 3600, 10800)


def agora_utc() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.isoformat()


def _parse(s: str) -> datetime:
    return datetime.fromisoformat(s)


def _ler() -> dict:
    if not FILA.exists():
        return {"DATASET": "LIFECYCLE-QUEUE-V1", "CONTRATO": CONTRATO,
                "LEI": ("fila duravel. Um 429 adia UMA tarefa, nunca a fila. "
                        "O worker nunca dorme a espera de uma fonte."),
                "PROXIMO_ID": 1, "TAREFAS": []}
    return json.loads(FILA.read_text(encoding="utf-8"))


def _gravar(d: dict) -> None:
    FILA.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(FILA.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(d, fh, ensure_ascii=False, indent=1)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, FILA)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def enfileirar(source_id: str, task_type: str, *, priority: int = 50,
               motivo: str = "") -> dict:
    """Poe trabalho na fila. Idempotente por (SOURCE_ID, TASK_TYPE) aberto:
    reenfileirar o mesmo trabalho pendente devolve a tarefa existente em vez
    de criar uma segunda — duas execucoes nao podem promover em duplicado.
    """
    if task_type not in TASK_TYPES:
        raise ValueError("TASK_TYPE desconhecido: %s" % task_type)
    d = _ler()
    for t in d["TAREFAS"]:
        if (t["SOURCE_ID"] == source_id and t["TASK_TYPE"] == task_type
                and t["STATUS"] in (PENDING, IN_PROGRESS, WAITING_RETRY)):
            return t

    t = {
        "TASK_ID": "T%05d" % d["PROXIMO_ID"],
        "SOURCE_ID": source_id,
        "TASK_TYPE": task_type,
        "PRIORITY": priority,
        "STATUS": PENDING,
        "ATTEMPTS": 0,
        "NEXT_ATTEMPT_AT": None,
        "LAST_ERROR": None,
        "MOTIVO": motivo,
        "CREATED_AT": _iso(agora_utc()),
        "UPDATED_AT": _iso(agora_utc()),
    }
    d["TAREFAS"].append(t)
    d["PROXIMO_ID"] += 1
    _gravar(d)
    return t


def elegiveis(agora: datetime | None = None) -> list[dict]:
    """O que pode correr AGORA. Uma tarefa em WAITING_RETRY cujo relogio ainda
    nao chegou NAO aparece aqui — e e por isso que ela nao bloqueia ninguem.
    """
    n = agora or agora_utc()
    d = _ler()
    out = []
    for t in d["TAREFAS"]:
        if t["STATUS"] == PENDING:
            out.append(t)
        elif t["STATUS"] == WAITING_RETRY and t["NEXT_ATTEMPT_AT"]:
            if _parse(t["NEXT_ATTEMPT_AT"]) <= n:
                out.append(t)
    out.sort(key=lambda x: (-x["PRIORITY"], x["CREATED_AT"]))
    return out


def proxima(agora: datetime | None = None) -> dict | None:
    """Pega a tarefa seguinte e marca-a IN_PROGRESS no disco.

    Marcar ANTES de executar: se o processo morrer a meio, quem reabrir o
    ficheiro ve uma tarefa IN_PROGRESS, que e verdade — alguem comecou e nao
    fechou. Inventar que ela nunca comecou seria mentir sobre o passado.
    """
    n = agora or agora_utc()
    cands = elegiveis(n)
    if not cands:
        return None
    alvo = cands[0]
    d = _ler()
    for t in d["TAREFAS"]:
        if t["TASK_ID"] == alvo["TASK_ID"]:
            t["STATUS"] = IN_PROGRESS
            t["UPDATED_AT"] = _iso(n)
            _gravar(d)
            return dict(t)
    return None


def _actualizar(task_id: str, campos: dict) -> dict:
    d = _ler()
    for t in d["TAREFAS"]:
        if t["TASK_ID"] == task_id:
            t.update(campos)
            t["UPDATED_AT"] = _iso(agora_utc())
            _gravar(d)
            return dict(t)
    raise KeyError("tarefa desconhecida: %s" % task_id)


def concluir(task_id: str, motivo: str = "") -> dict:
    return _actualizar(task_id, {"STATUS": DONE, "LAST_ERROR": None,
                                 "MOTIVO": motivo or "concluida"})


def bloquear(task_id: str, motivo: str) -> dict:
    """Policy/auth/capability: nao se tenta outra vez. Tentar de novo o que
    esta barrado por politica nao e persistencia, e contorno."""
    return _actualizar(task_id, {"STATUS": BLOCKED, "LAST_ERROR": motivo})


def adiar(task_id: str, *, retry_after_s: int | None = None,
          erro: str = "", agora: datetime | None = None) -> dict:
    """O 429 desta casa. NAO DORME — marca o relogio e devolve o controlo.

    Se a plataforma mandou Retry-After, manda ela. Senao, o backoff da casa,
    que tem teto.
    """
    n = agora or agora_utc()
    d = _ler()
    for t in d["TAREFAS"]:
        if t["TASK_ID"] != task_id:
            continue
        tentativas = t["ATTEMPTS"] + 1
        if tentativas >= MAX_ATTEMPTS:
            t["STATUS"] = FAILED
            t["ATTEMPTS"] = tentativas
            t["LAST_ERROR"] = "teto de %d tentativas: %s" % (MAX_ATTEMPTS, erro)
            t["UPDATED_AT"] = _iso(n)
            _gravar(d)
            return dict(t)

        espera = retry_after_s if retry_after_s is not None else \
            BACKOFF[min(tentativas - 1, len(BACKOFF) - 1)]
        t["STATUS"] = WAITING_RETRY
        t["ATTEMPTS"] = tentativas
        t["NEXT_ATTEMPT_AT"] = _iso(n + timedelta(seconds=espera))
        t["LAST_ERROR"] = erro
        t["UPDATED_AT"] = _iso(n)
        _gravar(d)
        return dict(t)
    raise KeyError("tarefa desconhecida: %s" % task_id)


def recuperar_orfas(agora: datetime | None = None, limite_s: int = 1800) -> list[dict]:
    """Depois de um crash: tarefas IN_PROGRESS que ninguem fechou.

    Nao se apagam nem se fingem novas — voltam a PENDING com a marca de que
    foram recuperadas. O ATTEMPTS nao se perde.
    """
    n = agora or agora_utc()
    d = _ler()
    mexidas = []
    for t in d["TAREFAS"]:
        if t["STATUS"] != IN_PROGRESS:
            continue
        if (n - _parse(t["UPDATED_AT"])).total_seconds() >= limite_s:
            t["STATUS"] = PENDING
            t["LAST_ERROR"] = "recuperada: processo anterior nao fechou esta tarefa"
            t["UPDATED_AT"] = _iso(n)
            mexidas.append(dict(t))
    if mexidas:
        _gravar(d)
    return mexidas


def recuperar_bloqueadas_por_defeito(assinaturas: list[str],
                                     task_types: set[str] | None = None,
                                     agora: datetime | None = None) -> list[dict]:
    """Reenfileira tarefas BLOCKED por um DEFEITO do worker — nunca por politica.

        BLOQUEIO POR DEFEITO SOME QUANDO O DEFEITO E CORRIGIDO.
        BLOQUEIO POR POLICY/AUTH/CAPABILITY, NAO — e nao se toca nele aqui.

    So mexe em BLOCKED cujo LAST_ERROR casa uma das `assinaturas` (ex.: «sem
    contrato», «etapa nao implementada») E, se `task_types` for dado, cujo tipo
    esteja nesse conjunto. Uma QUALIFY barrada pelo guard «sem contrato» foi
    vitima do defeito (uma candidata nunca tem contrato); mas um CANARY barrado
    por «sem contrato» e um canario legitimo sem contrato — outra coisa. Por
    isso o tipo importa, e por isso as assinaturas sao explicitas, nao
    «desbloquear tudo».
    """
    n = agora or agora_utc()
    d = _ler()
    mexidas = []
    for t in d["TAREFAS"]:
        if t["STATUS"] != BLOCKED:
            continue
        if task_types is not None and t["TASK_TYPE"] not in task_types:
            continue
        err = t.get("LAST_ERROR") or ""
        if any(a in err for a in assinaturas):
            t["STATUS"] = PENDING
            t["LAST_ERROR"] = ("reenfileirada: bloqueio por defeito corrigido "
                               "(era: %s)" % err[:90])
            t["UPDATED_AT"] = _iso(n)
            mexidas.append(dict(t))
    if mexidas:
        _gravar(d)
    return mexidas


def metricas(agora: datetime | None = None) -> dict:
    n = agora or agora_utc()
    d = _ler()
    m = {s: 0 for s in (PENDING, IN_PROGRESS, DONE, FAILED, WAITING_RETRY, BLOCKED)}
    for t in d["TAREFAS"]:
        m[t["STATUS"]] = m.get(t["STATUS"], 0) + 1
    m["QUEUE_TOTAL"] = len(d["TAREFAS"])
    m["QUEUE_PENDING"] = m[PENDING] + m[WAITING_RETRY]
    m["QUEUE_ELIGIBLE_NOW"] = len(elegiveis(n))
    m["QUEUE_WAITING_RETRY"] = m[WAITING_RETRY]
    return m
