#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TELEMETRIA DE RENDIMENTO DO SOURCE CURATOR — observabilidade, ZERO LLM.

    RUNNING = YES NAO SIGNIFICA PRODUZINDO = YES.

Este modulo NAO cria uma segunda fonte de verdade e NAO escreve na lane. Ele
DERIVA tudo, no instante da leitura, das fontes que ja existem:

    LIFECYCLE-LEDGER-V1.json    a fonte PRINCIPAL (transicoes append-only, OBSERVED_AT)
    LIFECYCLE-QUEUE-V1.json     a fila (estado + CREATED_AT/UPDATED_AT por tarefa)
    SOURCE-CURATOR-RUN-LOG.ndjson  o log de execucao (voltas, discovery, saude)
    supervisor.ler_estado_servico()  o estado runtime, DERIVADO DO SO

    NENHUM CONTADOR PARALELO. NENHUMA ARITMETICA POR LLM.

Regra do estado atual (a lei do ledger): o estado ATUAL de uma fonte e a ULTIMA
transicao dela. Nao se somam transicoes para obter totais atuais — uma fonte que
passou por READY e depois por RETRY nao e READY.

Como se atribui uma transicao a uma etapa (deterministico, medido no ledger):
    QUALIFY  -> EVIDENCE_REF contem "-QUALIFY-"  OU  REASON comeca por "QUALIFY:"
               (a via OK grava CONTRACT_PENDING com REASON "QUALIFY: ..."; as vias
                de bloqueio gravam com EVIDENCE_REF "EV-<id>-QUALIFY-<n>")
    CANARY/REVALIDATE -> EVIDENCE_REF contem "-CANARY-" ou "-REVALIDATE-"
Um bloqueio da PONTE traz EVIDENCE_REF "BRIDGE:..." e por isso NAO conta como
QUALIFY — o que separa o trabalho do worker do trabalho da ponte.
"""
from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))

import fila as F                # noqa: E402
import lifecycle as LC          # noqa: E402
import supervisor as S          # noqa: E402

LEDGER   = RAIZ / "curadoria" / "LIFECYCLE-LEDGER-V1.json"
RUNLOG   = RAIZ / "curadoria" / "SOURCE-CURATOR-RUN-LOG.ndjson"
CANDID   = RAIZ / "candidatas" / "FONTES-CANDIDATAS.json"

# O painel calcula na LEITURA; o checkpoint persistente e event-driven.
CHECKPOINT_HIST = RAIZ / "curadoria" / "TELEMETRY-CHECKPOINT-HISTORY-V1.ndjson"

# «Progresso recente» e «sem progresso anormal» derivam do timeout ja existente
# do heartbeat (300s). Nao se inventa timeout novo.
HEARTBEAT_TIMEOUT_S = S.HEARTBEAT_TIMEOUT_S

READY = LC.READY_FOR_COLLECTION


# ─────────────────────────────────────────────────────────────────────────
# Leitura tolerante — o SERVICO escreve estes ficheiros ao mesmo tempo. As
# escrituras sao atomicas (os.replace), logo uma leitura ve sempre uma versao
# INTEIRA (velha ou nova), nunca meia. O retry cobre so o transiente do SO.
# ─────────────────────────────────────────────────────────────────────────
def _ler_json(p: Path, default):
    for _ in range(3):
        try:
            if not p.exists():
                return default
            return json.loads(p.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            time.sleep(0.05)
    return default


def _ledger_transicoes() -> list[dict]:
    return _ler_json(LEDGER, {"TRANSICOES": []}).get("TRANSICOES", [])


def _runlog() -> list[dict]:
    linhas = []
    if not RUNLOG.exists():
        return linhas
    try:
        with RUNLOG.open("r", encoding="utf-8", errors="replace") as fh:
            for ln in fh:
                ln = ln.strip()
                if not ln:
                    continue
                try:
                    linhas.append(json.loads(ln))
                except json.JSONDecodeError:
                    continue
    except OSError:
        pass
    return linhas


def _parse(iso: str) -> datetime | None:
    try:
        d = datetime.fromisoformat(iso)
        return d if d.tzinfo else d.replace(tzinfo=timezone.utc)
    except (ValueError, TypeError):
        return None


# ─────────────────────────────────────────────────────────────────────────
# Classificacao de transicoes por etapa — deterministica
# ─────────────────────────────────────────────────────────────────────────
def _e_qualify(t: dict) -> bool:
    ev = t.get("EVIDENCE_REF") or ""
    return "-QUALIFY-" in ev or (t.get("REASON") or "").startswith("QUALIFY:")


def estado_atual_por_fonte(transicoes: list[dict]) -> dict:
    """{SOURCE_ID: estado atual} — a ULTIMA transicao de cada fonte manda."""
    est: dict[str, str] = {}
    for t in transicoes:
        est[t["SOURCE_ID"]] = t["NEW_STATE"]
    return est


def ready_sources_janela(transicoes: list[dict], desde: datetime,
                         ate: datetime) -> list[dict]:
    """As fontes promovidas a READY na janela — o numero navegavel ate a fonte.

    Devolve [{SOURCE_ID, READY_AT, EVIDENCE_REF}], a mais recente primeiro.
    """
    out = []
    for t in transicoes:
        if t["NEW_STATE"] != READY:
            continue
        at = _parse(t.get("OBSERVED_AT"))
        if at is not None and desde <= at < ate:
            out.append({"SOURCE_ID": t["SOURCE_ID"], "READY_AT": t["OBSERVED_AT"],
                        "EVIDENCE_REF": t.get("EVIDENCE_REF")})
    out.sort(key=lambda x: x["READY_AT"], reverse=True)
    return out


def qualify_sources_janela(transicoes: list[dict], desde: datetime,
                           ate: datetime) -> set:
    """Os SOURCE_ID cujo QUALIFY concluiu na janela."""
    return {t["SOURCE_ID"] for t in transicoes
            if _e_qualify(t) and (lambda a: a is not None and desde <= a < ate)(
                _parse(t.get("OBSERVED_AT")))}


def _janela(transicoes: list[dict], desde: datetime, ate: datetime) -> dict:
    """Conta EVENTOS (transicoes) numa janela [desde, ate). Nunca soma estado."""
    m = {"DISCOVERED": 0, "NEW_CANDIDATES": 0, "DUPLICATES": 0,
         "QUALIFY_STARTED": 0, "QUALIFY_COMPLETED": 0, "READY_CURRENT": 0,
         "RETRY": 0, "POLICY_BLOCK": 0, "CAPABILITY_BLOCK": 0,
         "UNKNOWN": 0, "REJECTED": 0}
    for t in transicoes:
        at = _parse(t.get("OBSERVED_AT"))
        if at is None or not (desde <= at < ate):
            continue
        ns = t["NEW_STATE"]
        if _e_qualify(t):
            m["QUALIFY_COMPLETED"] += 1
        if ns == READY:
            m["READY_CURRENT"] += 1
        elif ns == LC.RETRY_AFTER:
            m["RETRY"] += 1
        elif ns == LC.POLICY_BLOCK:
            m["POLICY_BLOCK"] += 1
        elif ns == LC.CAPABILITY_BLOCK:
            m["CAPABILITY_BLOCK"] += 1
        elif ns in (LC.SEMANTIC_REVIEW, LC.UNKNOWN):
            m["UNKNOWN"] += 1
        elif ns == LC.CONTRACTED_CANARY_FAILED:
            m["REJECTED"] += 1
    return m


def _discovery_da_janela(runlog: list[dict], desde: datetime, ate: datetime) -> dict:
    """DISCOVERED/NEW_CANDIDATES/DUPLICATES da janela, lidos do RUN-LOG.

    A discovery nao regista transicoes no lifecycle (as candidatas vivem noutro
    ficheiro), por isso a janela de descoberta le-se dos eventos REALIMENTACAO
    do run-log, que sao timestampados (AT). Sem evento na janela, e 0 medido —
    nao «NAO SEI»: o run-log e completo.
    """
    d = {"DISCOVERED": 0, "NEW_CANDIDATES": 0, "DUPLICATES": 0,
         "DISCOVERY_HOOK_ERRORS": 0}
    for e in runlog:
        at = _parse(e.get("AT"))
        if at is None or not (desde <= at < ate):
            continue
        ev = e.get("EVENTO", "")
        if ev == "DISCOVERY_HOOK_ERRO":
            d["DISCOVERY_HOOK_ERRORS"] += 1
        elif ev == "REALIMENTACAO":
            disc = e.get("DISCOVERY") or {}
            if isinstance(disc, dict):
                d["NEW_CANDIDATES"] += int(disc.get("CANDIDATAS_NOVAS") or 0)
                d["DISCOVERED"] += int(disc.get("CRAWL") or 0)
    return d


def _qualify_started(desde: datetime, ate: datetime) -> int:
    """QUALIFY que ENTRARAM no pipeline na janela (CREATED_AT na fila).

    «Started» = a tarefa QUALIFY entrou na fila (a ponte enfileirou-a). O
    CREATED_AT sobrevive na tarefa mesmo depois de DONE, por isso e contavel por
    janela sem contador paralelo.
    """
    q = _ler_json(F.FILA, {"TAREFAS": []}).get("TAREFAS", [])
    n = 0
    for t in q:
        if t.get("TASK_TYPE") != F.QUALIFY:
            continue
        at = _parse(t.get("CREATED_AT"))
        if at is not None and desde <= at < ate:
            n += 1
    return n


def _fila_metricas() -> dict:
    q = _ler_json(F.FILA, {"TAREFAS": []}).get("TAREFAS", [])
    m = {"QUEUE_TOTAL": len(q), "QUEUE_PENDING": 0, "QUEUE_IN_PROGRESS": 0,
         "QUEUE_DONE": 0, "QUEUE_BLOCKED": 0, "QUALIFY_PENDING": 0,
         "QUEUE_WAITING_RETRY": 0}
    for t in q:
        st, tp = t.get("STATUS"), t.get("TASK_TYPE")
        if st == F.PENDING:
            m["QUEUE_PENDING"] += 1
        elif st == F.IN_PROGRESS:
            m["QUEUE_IN_PROGRESS"] += 1
        elif st == F.DONE:
            m["QUEUE_DONE"] += 1
        elif st == F.BLOCKED:
            m["QUEUE_BLOCKED"] += 1
        elif st == F.WAITING_RETRY:
            m["QUEUE_WAITING_RETRY"] += 1
        if tp == F.QUALIFY and st in (F.PENDING, F.WAITING_RETRY):
            m["QUALIFY_PENDING"] += 1
    return m


def _yield(ready: int, qualify: int):
    """READY / QUALIFY_COMPLETED. Denominador 0 -> N/A. Nunca inventar %."""
    if qualify <= 0:
        return "N/A"
    return round(100.0 * ready / qualify, 1)


def _productivity_state(estado_srv: dict, filam: dict,
                        secs_since_progress) -> str:
    """DETERMINISTICO, separado da SAUDE. Deriva do timeout do heartbeat."""
    sup = estado_srv.get("SUPERVISOR_STATE")
    if sup == "BLOCKED":
        return "BLOCKED"
    if sup not in ("RUNNING", "STOPPING"):
        return "STOPPED"
    eleg = filam["QUEUE_PENDING"] + filam["QUEUE_WAITING_RETRY"]
    if estado_srv.get("WORKER_ALIVE"):
        recente = (secs_since_progress is not None
                   and secs_since_progress < HEARTBEAT_TIMEOUT_S)
        if recente:
            return "ACTIVE_PRODUCTIVE"
        if eleg > 0:
            return "ACTIVE_NO_OUTPUT"     # vivo, com fila, sem progresso anormal
        return "ACTIVE_PRODUCTIVE"
    # sem worker vivo
    if eleg == 0:
        return "IDLE_NO_WORK"
    return "ACTIVE_NO_OUTPUT"


def metricas(agora: datetime | None = None) -> dict:
    """A telemetria inteira, calculada AGORA a partir das fontes de verdade."""
    n = agora or datetime.now(timezone.utc)
    tr = _ledger_transicoes()
    runlog = _runlog()
    filam = _fila_metricas()
    srv = S.ler_estado_servico()

    # sessao = desde o arranque do supervisor ATUAL (do ficheiro de estado)
    est_ficheiro = S._ler_estado()
    sess_ini = _parse(est_ficheiro.get("SUPERVISOR_STARTED_AT")) or (n - timedelta(days=1))

    lp = _parse(srv.get("LAST_PROGRESS_AT"))
    secs_since = round((n - lp).total_seconds(), 1) if lp else None

    j1 = _janela(tr, n - timedelta(hours=1), n)
    j24 = _janela(tr, n - timedelta(hours=24), n)
    jsess = _janela(tr, sess_ini, n)
    d1 = _discovery_da_janela(runlog, n - timedelta(hours=1), n)
    d24 = _discovery_da_janela(runlog, n - timedelta(hours=24), n)
    dsess = _discovery_da_janela(runlog, sess_ini, n)
    j1.update({k: d1[k] for k in ("DISCOVERED", "NEW_CANDIDATES", "DUPLICATES")})
    j24.update({k: d24[k] for k in ("DISCOVERED", "NEW_CANDIDATES", "DUPLICATES")})
    j1["QUALIFY_STARTED"] = _qualify_started(n - timedelta(hours=1), n)
    j24["QUALIFY_STARTED"] = _qualify_started(n - timedelta(hours=24), n)

    # rendimento
    qph1 = j1["QUALIFY_COMPLETED"]           # por hora = contagem da janela 1h
    qph24 = round(j24["QUALIFY_COMPLETED"] / 24.0, 2)
    rph1 = j1["READY_CURRENT"]
    rph24 = round(j24["READY_CURRENT"] / 24.0, 2)

    # tempo por fonte: nao ha par (inicio,fim) fiavel por tarefa -> NAO SEI
    tempo = {"QUALIFY_MEDIAN_DURATION": "NAO SEI / PRECISA MEDIR",
             "QUALIFY_P90_DURATION": "NAO SEI / PRECISA MEDIR",
             "PORQUE": ("a fila guarda so o UPDATED_AT (sobrescrito); nao ha par "
                        "inicio->fim por tarefa. Medir exigiria instrumentar o worker.")}

    # custo: nao ha instrumentacao de custo atribuivel (coleta_id/custo)
    custo = {"VALOR": "NAO SEI",
             "PORQUE": ("sem instrumentacao de custo atribuivel (nao ha coleta_id "
                        "nem custo medido). O motor usa so rotas gratuitas por "
                        "contrato, mas «nao vi custo» != «custo = 0».")}

    # estimativa de drenagem da fila
    if filam["QUALIFY_PENDING"] == 0:
        drain = {"ESTIMATE": "FILA_VAZIA", "SAMPLE_WINDOW": "1h"}
    elif qph1 > 0:
        drain = {"ESTIMATE_HOURS": round(filam["QUALIFY_PENDING"] / qph1, 2),
                 "IS_ESTIMATE": True, "SAMPLE_WINDOW": "1h",
                 "BASIS": "QUALIFY_PENDING / QUALIFY_COMPLETED_1H"}
    else:
        drain = {"ESTIMATE": "NAO SEI / PRECISA MEDIR",
                 "PORQUE": "throughput 1h = 0 com fila > 0", "SAMPLE_WINDOW": "1h"}

    prod = _productivity_state(srv, filam, secs_since)

    # saude da discovery — o achado que a telemetria NAO pode mascarar
    disc_health = {
        "DISCOVERY_HOOK_ERRORS_1H": d1["DISCOVERY_HOOK_ERRORS"],
        "DISCOVERY_HOOK_ERRORS_24H": d24["DISCOVERY_HOOK_ERRORS"],
        "DISCOVERY_HOOK_ERRORS_SESSION": dsess["DISCOVERY_HOOK_ERRORS"],
        "DISCOVERY_HEALTHY": d24["DISCOVERY_HOOK_ERRORS"] == 0,
    }

    return {
        "GERADO_EM": n.isoformat(),
        "LLM_USED_FOR_METRICS": "NO",
        "TELEMETRY_SOURCE_OF_TRUTH": "LIFECYCLE-LEDGER-V1.json (+ QUEUE, RUN-LOG, SO)",

        "AGORA": {
            "SERVICE_STATE": srv.get("SOURCE_CURATOR_SERVICE"),
            "SUPERVISOR_ALIVE": srv.get("SUPERVISOR_ALIVE"),
            "SUPERVISOR_PID": srv.get("SUPERVISOR_PID"),
            "WORKER_STATE": srv.get("WORKER_STATE"),
            "WORKER_PID": srv.get("WORKER_PID"),
            "CURRENT_TASK_ID": _tarefa_em_curso().get("TASK_ID"),
            "CURRENT_STAGE": _tarefa_em_curso().get("TASK_TYPE"),
            "CURRENT_SOURCE_ID": _tarefa_em_curso().get("SOURCE_ID"),
            "LAST_PROGRESS_AT": srv.get("LAST_PROGRESS_AT"),
            "SECONDS_SINCE_LAST_PROGRESS": secs_since,
            **filam,
        },
        "JANELA_1H": j1,
        "JANELA_24H": j24,
        "SESSAO": {
            "STARTED_AT": sess_ini.isoformat(),
            "UPTIME_S": round((n - sess_ini).total_seconds(), 0),
            "DISCOVERED_SESSION": dsess["DISCOVERED"],
            "NEW_CANDIDATES_SESSION": dsess["NEW_CANDIDATES"],
            "QUALIFY_COMPLETED_SESSION": jsess["QUALIFY_COMPLETED"],
            "READY_CURRENT_SESSION": jsess["READY_CURRENT"],
        },
        "RENDIMENTO": {
            "QUALIFY_PER_HOUR_1H": qph1,
            "QUALIFY_PER_HOUR_24H": qph24,
            "READY_PER_HOUR_1H": rph1,
            "READY_PER_HOUR_24H": rph24,
            "QUALIFY_TO_READY_YIELD_1H": _yield(j1["READY_CURRENT"], j1["QUALIFY_COMPLETED"]),
            "QUALIFY_TO_READY_YIELD_24H": _yield(j24["READY_CURRENT"], j24["QUALIFY_COMPLETED"]),
        },
        "TEMPO_POR_FONTE": tempo,
        "CUSTO": custo,
        "PRODUCTIVITY_STATE": prod,
        "QUEUE_DRAIN_ESTIMATE": drain,
        "DISCOVERY_HEALTH": disc_health,
    }


def _tarefa_em_curso() -> dict:
    for t in _ler_json(F.FILA, {"TAREFAS": []}).get("TAREFAS", []):
        if t.get("STATUS") == F.IN_PROGRESS:
            return t
    return {}


# ─────────────────────────────────────────────────────────────────────────
# CHECKPOINT event-driven — o historico sobrevive a restart
# ─────────────────────────────────────────────────────────────────────────
def _ultimo_checkpoint() -> dict | None:
    if not CHECKPOINT_HIST.exists():
        return None
    ultimo = None
    try:
        with CHECKPOINT_HIST.open("r", encoding="utf-8", errors="replace") as fh:
            for ln in fh:
                ln = ln.strip()
                if ln:
                    ultimo = ln
    except OSError:
        return None
    if ultimo:
        try:
            return json.loads(ultimo)
        except json.JSONDecodeError:
            return None
    return None


def _assinatura(m: dict) -> tuple:
    """O que decide se «algo mudou» desde o ultimo checkpoint (produto util)."""
    return (m["SESSAO"]["QUALIFY_COMPLETED_SESSION"],
            m["SESSAO"]["READY_CURRENT_SESSION"],
            m["SESSAO"]["NEW_CANDIDATES_SESSION"],
            m["AGORA"]["QUEUE_TOTAL"], m["AGORA"]["QUEUE_DONE"])


def _novas_fontes_uteis(m: dict, limite: int = 8) -> dict:
    """As fontes READY mais recentes (24h), navegaveis: nome, tipo, 1 frase.

    Import tardio de cartao_de_fonte para evitar ciclo (cartao importa telemetria).
    Nunca levanta: uma seccao editorial nao pode partir o checkpoint.
    """
    try:
        import cartao_de_fonte as CC
        n = _parse(m["GERADO_EM"]) or datetime.now(timezone.utc)
        janela = ready_sources_janela(_ledger_transicoes(), n - timedelta(hours=24), n)
        nav = CC.cartoes_navegaveis([r["SOURCE_ID"] for r in janela])
        total = len(nav)
        return {"TOTAL_24H": total,
                "MAIS_RECENTES": nav[:limite],
                "MAIS": max(0, total - limite)}
    except Exception as ex:
        return {"ERRO": str(ex)[:120]}


def talvez_checkpoint(m: dict | None = None, *, motivo: str = "",
                      forcar: bool = False) -> dict:
    """Grava um checkpoint SO se houve mudanca (ou forcar). Event-driven.

    Nao cria checkpoint so para dizer zero: se a assinatura nao mudou desde o
    ultimo, nao escreve. Devolve {ESCRITO: bool, ...}.
    """
    m = m or metricas()
    ultimo = _ultimo_checkpoint()
    assin = list(_assinatura(m))
    if not forcar and ultimo is not None and ultimo.get("ASSINATURA") == assin:
        return {"ESCRITO": False, "MOTIVO": "sem mudanca desde o ultimo checkpoint"}

    linha = {
        "AT": m["GERADO_EM"],
        "MOTIVO": motivo or "mudanca detectada",
        "ASSINATURA": assin,
        "NOVAS_FONTES_UTEIS": _novas_fontes_uteis(m),
        "READY_CURRENT_24H": m["JANELA_24H"]["READY_CURRENT"],
        "QUALIFY_COMPLETED_24H": m["JANELA_24H"]["QUALIFY_COMPLETED"],
        "QUALIFY_TO_READY_YIELD_24H": m["RENDIMENTO"]["QUALIFY_TO_READY_YIELD_24H"],
        "QUEUE_PENDING": m["AGORA"]["QUEUE_PENDING"],
        "QUALIFY_PENDING": m["AGORA"]["QUALIFY_PENDING"],
        "PRODUCTIVITY_STATE": m["PRODUCTIVITY_STATE"],
        "SESSION_QUALIFY_COMPLETED": m["SESSAO"]["QUALIFY_COMPLETED_SESSION"],
        "SESSION_READY_CURRENT": m["SESSAO"]["READY_CURRENT_SESSION"],
        "DISCOVERY_HOOK_ERRORS_24H": m["DISCOVERY_HEALTH"]["DISCOVERY_HOOK_ERRORS_24H"],
    }
    with CHECKPOINT_HIST.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(linha, ensure_ascii=False) + "\n")
    return {"ESCRITO": True, "LINHA": linha}


def historico_checkpoints() -> list[dict]:
    out = []
    if not CHECKPOINT_HIST.exists():
        return out
    with CHECKPOINT_HIST.open("r", encoding="utf-8", errors="replace") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln:
                try:
                    out.append(json.loads(ln))
                except json.JSONDecodeError:
                    continue
    return out


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(description="Telemetria do Source Curator (ZERO LLM).")
    ap.add_argument("--checkpoint", action="store_true",
                    help="gravar um checkpoint se houve mudanca")
    ap.add_argument("--forcar", action="store_true")
    a = ap.parse_args()
    m = metricas()
    if a.checkpoint:
        r = talvez_checkpoint(m, motivo="CLI", forcar=a.forcar)
        m["CHECKPOINT"] = r
    print(json.dumps(m, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
