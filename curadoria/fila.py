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
import time
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


# ⚠️ NO WINDOWS, UM LEITOR TRAVA O ESCRITOR. os.replace sobre um ficheiro que
# outro processo tem aberto (Python abre sem FILE_SHARE_DELETE) falha com
# PermissionError [WinError 5]. Visto ao vivo (M2e, 04:37Z): o worker 129352
# morreu RC=1 dentro de F.concluir, com a tarefa executada e a fila a
# dize-la IN_PROGRESS. Medido: com um leitor em ciclo, 371 de 500 trocas
# falharam. Os leitores sao legitimos (supervisor, painel, telemetria,
# verificadores) e seguram o ficheiro milissegundos.
#
# Cura: esperar e tentar outra vez, com teto; esgotado o teto, o erro SOBE —
# a escrita nunca se perde em silencio. REPLACE_RETRIES conta quantas vezes
# isto aconteceu neste processo.
#
# Medido e descartado: abrir a leitura com FILE_SHARE_DELETE (CreateFileW) nao
# muda nada mensuravel — 5000 leituras contra um escritor em ciclo: 0 vs 1 erro,
# 5 vs 6 esperas do escritor. O os.replace do Windows recusa na mesma. O
# remedio e a espera, nao a partilha.
#
#     UM LEITOR A OLHAR NAO E UM ESCRITOR A MAIS: ESPERA-SE POR ELE.
ESPERAS_PERMISSAO_S = (0.02, 0.05, 0.1, 0.2, 0.4, 0.8, 1.6)
REPLACE_RETRIES = {"GRAVAR": 0, "LER": 0}


def _com_paciencia(accao, contador: str):
    for espera in ESPERAS_PERMISSAO_S:
        try:
            return accao()
        except PermissionError:
            REPLACE_RETRIES[contador] += 1
            time.sleep(espera)
    return accao()            # ultima tentativa: se falhar, o erro sobe


def _ler() -> dict:
    if not FILA.exists():
        return {"DATASET": "LIFECYCLE-QUEUE-V1", "CONTRATO": CONTRATO,
                "LEI": ("fila duravel. Um 429 adia UMA tarefa, nunca a fila. "
                        "O worker nunca dorme a espera de uma fonte."),
                "PROXIMO_ID": 1, "TAREFAS": []}
    return json.loads(_com_paciencia(lambda: FILA.read_text(encoding="utf-8"),
                                     "LER"))


def _gravar(d: dict) -> None:
    FILA.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(FILA.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(d, fh, ensure_ascii=False, indent=1)
            fh.flush()
            os.fsync(fh.fileno())
        _com_paciencia(lambda: os.replace(tmp, FILA), "GRAVAR")
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


# ---------------------------------------------------------------------------
# INTERMITENCIA != SENTENCA
# ---------------------------------------------------------------------------
# Medido em 22/09 (DIAGNOSTICO-FILA-DO-BOT-V1, a6c68263): 62 das 69 FAILED
# morreram por «teto de 5 tentativas: robots nao pode ser lido». Sondadas, 42
# liam o robots.txt nessa mesma tarde. www.meteotrentino.it deu 200 e, minutos
# depois, ligacao cancelada. O teto de 5 tentativas em ~4 h (BACKOFF) mede a
# rede de UMA tarde, nao a fonte — e depois a fonte fica FAILED para sempre.
#
#     UM TETO DE TENTATIVAS TRANSFORMA UMA INTERMITENCIA NUMA SENTENCA.
#
# O remedio NAO e apagar o teto: e dar-lhe uma segunda escala, lenta. Uma FAILED
# cujo erro e de TRANSPORTE (nunca de politica) volta a WAITING_RETRY depois de
# um intervalo longo, UMA tentativa de cada vez, e com teto proprio. Esgotado o
# teto de revivencias sem nunca ter lido, fica MORTA — declarada, com o motivo.
#
# ⚠️ So assinaturas de transporte. Um 403 no robots chega ao worker como
# Disallow total -> BLOCK (policy), nunca como «nao pode ser lido»: nao passa
# por aqui, e revive-lo seria contornar o muro.
ASSINATURAS_INTERMITENTES = (
    "robots nao pode ser lido",
    "robots.txt ilegivel",
    "URLError",
    "TimeoutError",
    "timed out",
    "ConnectionResetError",
    "RemoteDisconnected",
)
# Tentativas de revivencia: 6 h, 24 h, 72 h depois da ultima falha. Tres
# leituras em dias diferentes separam «rede de uma tarde» de «host que nao
# responde»; mais do que isso seria insistencia, menos seria a mesma tarde.
REVIVE_BACKOFF_S = (6 * 3600, 24 * 3600, 72 * 3600)
REVIVE_MAX = len(REVIVE_BACKOFF_S)
MORTA = "MORTA"   # marca em INTERMITENCIA_VEREDICTO; o STATUS continua FAILED


def e_intermitente(t: dict) -> bool:
    err = t.get("LAST_ERROR") or ""
    return (t.get("STATUS") == FAILED and err.startswith("teto de")
            and any(a in err for a in ASSINATURAS_INTERMITENTES))


def reviver_intermitentes(agora: datetime | None = None) -> list[dict]:
    """FAILED por transporte -> WAITING_RETRY com backoff longo e teto proprio.

    Deterministico, sem rede: a tentativa de revivencia E a sonda — quem le o
    robots de novo e o worker, pela etapa normal. Devolve as tarefas mexidas
    (revividas ou declaradas MORTAS); nada e apagado.

    A tarefa revivida recebe ATTEMPTS = MAX_ATTEMPTS - 1: UMA tentativa. Se
    falhar outra vez, `adiar` devolve-a a FAILED pelo teto normal e a proxima
    revivencia usa o degrau seguinte de REVIVE_BACKOFF_S.
    """
    n = agora or agora_utc()
    d = _ler()
    mexidas = []
    for t in d["TAREFAS"]:
        if not e_intermitente(t):
            continue
        if t.get("INTERMITENCIA_VEREDICTO") == MORTA:
            continue
        k = int(t.get("REVIVALS", 0))
        if k >= REVIVE_MAX:
            t["INTERMITENCIA_VEREDICTO"] = MORTA
            t["MOTIVO"] = ("morta: %d revivencias em dias diferentes sem ler "
                           "(ultimo erro: %s)" % (k, (t["LAST_ERROR"] or "")[:90]))
            t["UPDATED_AT"] = _iso(n)
            mexidas.append(dict(t))
            continue
        quando = _parse(t["UPDATED_AT"]) + timedelta(seconds=REVIVE_BACKOFF_S[k])
        if quando > n:
            continue          # ainda nao e a hora: nem mexe, nem anota
        t.setdefault("REVIVE_HISTORICO", []).append(
            {"AT": _iso(n), "ERA": (t["LAST_ERROR"] or "")[:120]})
        t["REVIVALS"] = k + 1
        t["STATUS"] = WAITING_RETRY
        t["ATTEMPTS"] = MAX_ATTEMPTS - 1
        t["NEXT_ATTEMPT_AT"] = _iso(n)
        t["LAST_ERROR"] = ("revivida %d/%d: falha de transporte nao e sentenca "
                           "(era: %s)" % (k + 1, REVIVE_MAX,
                                          (t["LAST_ERROR"] or "")[:90]))
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
