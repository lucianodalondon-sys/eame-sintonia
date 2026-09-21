#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SUPERVISOR DO SOURCE CURATOR — relanca o worker quando ele morre.

O ciclo_continuo.py e um while True dentro de um processo. Se o processo morre
(crash, reboot, Ctrl-C, Orca fechado), o estado sobrevive no disco mas ninguem
relanca. Este ficheiro e esse dono.

    RESTART_WORKER  +  RECOVER_FROM_PERSISTED_STATE  =>  este ficheiro.

Decisoes de design (com defeitos da auditoria ADDENDUM-01 corrigidos):

1. LOCK COM TOKEN + BOOT TIME
   O lock guarda PID + STARTED_AT + TOKEN (uuid4) em JSON. Ao verificar
   um lock existente: o processo existe? e Python? o STARTED_AT e posterior
   ao boot do sistema? Se qualquer check falhar, o lock e orfao.
   Metodo: wmic os get LastBootUpTime (medido e funcional neste ambiente).
   Declarado: METODO_VERIFICACAO_LOCK = "BOOT_TIME_WMIC + PROCESS_NAME".

2. FUNCAO OBSERVAVEL: uma_volta_sup()
   O loop principal e decomposto em iteracoes observaveis. Os testes
   chamam uma_volta_sup() directamente e asseram a SEQUENCIA de accoes
   (VIVO / RELANCADO / IDLE / BLOQUEADO / PARA_FLAG). O modo --seco deixou
   de existir como argumento; o loop com N iteracoes substituiu.
   Garantia: ao sair, o supervisor SEMPRE termina o worker ou declara
   explicitamente no estado que o deixou a correr.

3. CRASH COUNTER SO CONTA MORTES SEM PROGRESSO
   CRASHES_SEM_PROGRESSO conta apenas mortes onde o heartbeat NAO avancou
   desde a morte anterior. Uma morte com progresso (heartbeat avancou)
   repoe o contador a zero. MORRER != MORRER SEM PROGREDIR.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))

import fila as F  # noqa: E402

ESTADO = RAIZ / "curadoria" / "SUPERVISOR-STATE.json"
LOCK   = RAIZ / "curadoria" / "SUPERVISOR.lock"
PARAR  = RAIZ / "curadoria" / "PARAR.flag"
DIARIO = RAIZ / "curadoria" / "SOURCE-CURATOR-RUN-LOG.ndjson"

# Anti-crashloop: N mortes SEM PROGRESSO dentro de CRASH_JANELA_S -> BLOCKED.
CRASH_MAX      = 3
CRASH_JANELA_S = 120

# Depois de quanto tempo sem heartbeat o worker e considerado pendurado.
# ciclo_continuo.py dorme no maximo ESPERA_MAX=120s entre voltas.
HEARTBEAT_TIMEOUT_S = 300

# Intervalo padrao entre iteracoes do loop principal.
SUPERVISOR_POLL_S = 15

# Metodo de verificacao de lock declarado — para rastreabilidade.
# BOOT_TIME: offset wmic parseado, comparacao aware datetime UTC vs UTC.
METODO_VERIFICACAO_LOCK = "BOOT_TIME_WMIC_UTC_AWARE + PROCESS_NAME"


# ---------------------------------------------------------------------------
# Utilitarios
# ---------------------------------------------------------------------------

def _agora() -> str:
    return datetime.now(timezone.utc).isoformat()


def _anotar(evento: dict) -> None:
    evento["AT"] = _agora()
    evento["ORIGEM"] = "SUPERVISOR"
    with DIARIO.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(evento, ensure_ascii=False) + "\n")


def _ler_estado() -> dict:
    if ESTADO.exists():
        try:
            return json.loads(ESTADO.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def _gravar_estado(d: dict) -> None:
    d["ATUALIZADO_EM"] = _agora()
    ESTADO.write_text(json.dumps(d, ensure_ascii=False, indent=1),
                      encoding="utf-8")


# ---------------------------------------------------------------------------
# Boot time do sistema (Windows) — para verificar se um lock e anterior ao
# reboot e portanto orfao independentemente do PID.
# Medido: wmic os get LastBootUpTime devolve "LastBootUpTime=YYYYMMDDHHmmss..."
#
# FORMATO wmic: YYYYMMDDHHmmss.ffffff±OFFSET_MINUTOS
#   ex.: 20260910212951.500000-180
#        hora local = 2026-09-10 21:29:51
#        offset     = -180 min = UTC-3
#        UTC        = 2026-09-11 00:29:51Z
#
# _agora() usa datetime.now(timezone.utc) — STARTED_AT e SEMPRE UTC.
# A comparacao em _lock_e_orfao deve ser entre datetimes aware, nunca
# entre strings de fusos diferentes.
# ---------------------------------------------------------------------------

def _parse_wmic_boot_time(raw: str) -> Optional[datetime]:
    """Parseia a string bruta do wmic e devolve datetime aware em UTC.

    raw: "YYYYMMDDHHmmss.ffffff±OFFSET_MINUTOS"
    Devolve None se o formato nao for reconhecido — degradar para NAO SEI
    e melhor do que comparar valores de fusos diferentes.
    """
    try:
        dt_naive = datetime.strptime(raw[:14], "%Y%m%d%H%M%S")
        rest = raw[14:]  # ".ffffff±offset"
        sign_pos = None
        for i, c in enumerate(rest):
            if c in ("+", "-"):
                sign_pos = i
                sign = c
                break
        if sign_pos is None:
            return None
        off_min = int(rest[sign_pos + 1:])
        if sign == "-":
            off_min = -off_min
        tz_local = timezone(timedelta(minutes=off_min))
        return dt_naive.replace(tzinfo=tz_local).astimezone(timezone.utc)
    except Exception:
        return None


def _boot_time_utc() -> Optional[datetime]:
    """Devolve o boot time do sistema como datetime UTC aware, ou None."""
    try:
        r = subprocess.run(
            ["wmic", "os", "get", "LastBootUpTime", "/FORMAT:LIST"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=5,
        )
        for line in r.stdout.splitlines():
            line = line.strip().replace(" ", "")
            if "LastBootUpTime=" in line:
                raw = line.split("=", 1)[1].strip()
                return _parse_wmic_boot_time(raw)
    except Exception:
        pass
    return None


def _proc_e_python(pid: int) -> bool:
    """Verifica se o processo com este PID tem 'python' no nome da imagem."""
    try:
        r = subprocess.run(
            ["tasklist", "/FI", "PID eq %d" % pid, "/NH", "/FO", "CSV"],
            capture_output=True, text=True, timeout=5
        )
        return "python" in r.stdout.lower()
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Verificacao de liveness — PID + heartbeat
# ---------------------------------------------------------------------------

def _pid_no_so(pid: int) -> bool:
    """Verifica se o PID existe no SO (Windows)."""
    try:
        r = subprocess.run(
            ["tasklist", "/FI", "PID eq %d" % pid, "/NH", "/FO", "CSV"],
            capture_output=True, text=True, timeout=5
        )
        return str(pid) in r.stdout
    except Exception:
        return False


def _ultimo_heartbeat() -> Optional[datetime]:
    """Le o timestamp AT da ultima linha do run log escrita pelo WORKER.

    ⚠️ O supervisor escreve no MESMO diario que le (`_anotar`: WORKER_MORTO,
    WORKER_RELANCADO, SUPERVISOR_BLOCKED...). Medido (PROVAS-P1, DEFEITO 1):
    contando essas linhas, cada morte via o WORKER_RELANCADO anterior como
    "batimento novo", `progrediu` dava True, o contador zerava, e o
    anti-crashloop nunca disparou — 8 mortes seguidas sem progresso, 8
    relancamentos. As linhas com ORIGEM=SUPERVISOR sao o supervisor a falar
    de si; batimento e so o que o worker escreveu.

        O SUPERVISOR NAO PODE OUVIR O PROPRIO ECO COMO PROVA DE VIDA.
    """
    if not DIARIO.exists():
        return None
    try:
        last = None
        with DIARIO.open("r", encoding="utf-8", errors="replace") as fh:
            for linha in fh:
                linha = linha.strip()
                if linha and '"ORIGEM": "SUPERVISOR"' not in linha:
                    last = linha
        if last:
            d = json.loads(last)
            if d.get("ORIGEM") == "SUPERVISOR":
                return None
            return datetime.fromisoformat(d["AT"])
    except Exception:
        pass
    return None


def _worker_vivo(estado: dict) -> bool:
    """PID existe no SO E heartbeat recente."""
    pid = estado.get("WORKER_PID")
    if not pid:
        return False
    if not _pid_no_so(pid):
        return False
    hb = _ultimo_heartbeat()
    if hb is None:
        arrancou = estado.get("WORKER_STARTED_AT")
        if arrancou:
            delta = (datetime.now(timezone.utc)
                     - datetime.fromisoformat(arrancou)).total_seconds()
            return delta < HEARTBEAT_TIMEOUT_S
        return False
    delta = (datetime.now(timezone.utc) - hb).total_seconds()
    return delta < HEARTBEAT_TIMEOUT_S


# ---------------------------------------------------------------------------
# Lancamento do worker
# ---------------------------------------------------------------------------

def _lancar_worker(pausa: float = 1.0) -> subprocess.Popen:
    cmd = [sys.executable,
           str(RAIZ / "curadoria" / "ciclo_continuo.py"),
           "--pausa", str(pausa)]
    return subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, encoding="utf-8", errors="replace",
    )


# ---------------------------------------------------------------------------
# Lock de instancia unica — corrigido (ADDENDUM-01 DEFEITO 1)
#
# METODO: PID + STARTED_AT + TOKEN no JSON do lock.
# Verificacao de orfao:
#   a) PID nao existe no SO -> orfao
#   b) PID existe mas nao e python -> orfao (PID reciclado por outro processo)
#   c) STARTED_AT anterior ao boot do sistema -> orfao (sobreviveu no disco
#      mas o processo nao sobreviveu ao reboot)
#   d) Todas as verificacoes passam -> lock valido, nao tocar
# ---------------------------------------------------------------------------

def _lock_e_orfao(lock_data: dict) -> bool:
    """True se o lock deve ser considerado orfao e pode ser removido."""
    pid = lock_data.get("PID")
    if not pid:
        return True

    # a) PID existe?
    if not _pid_no_so(pid):
        return True

    # b) PID e um processo Python?
    if not _proc_e_python(pid):
        return True  # PID reciclado por processo nao-Python

    # c) STARTED_AT anterior ao boot? (boot_time pode ser None se wmic falhar)
    # STARTED_AT e gerado por _agora() = datetime.now(timezone.utc).isoformat()
    # — sempre UTC. boot_time_utc() tambem devolve UTC aware. Comparacao segura.
    # Se boot_time for None (wmic indisponivel): check inactivo, nao comparar.
    started_at = lock_data.get("STARTED_AT", "")
    boot_time = _boot_time_utc()
    if boot_time is not None and started_at:
        try:
            started_dt = datetime.fromisoformat(started_at)
            if started_dt.tzinfo is None:
                started_dt = started_dt.replace(tzinfo=timezone.utc)
            if started_dt < boot_time:
                return True
        except ValueError:
            pass

    return False


def _adquirir_lock() -> Optional[int]:
    """Devolve o fd do lock ou None se ja houver outro supervisor valido."""
    while True:
        try:
            fd = os.open(str(LOCK), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            conteudo = json.dumps({
                "PID": os.getpid(),
                "STARTED_AT": _agora(),
                "TOKEN": str(uuid.uuid4()),
                "METODO_VERIFICACAO": METODO_VERIFICACAO_LOCK,
            })
            os.write(fd, conteudo.encode("utf-8"))
            return fd
        except FileExistsError:
            try:
                lock_data = json.loads(LOCK.read_text(encoding="utf-8",
                                                      errors="replace"))
            except Exception:
                # Ficheiro corrompido — remover e tentar de novo.
                LOCK.unlink(missing_ok=True)
                continue

            if _lock_e_orfao(lock_data):
                LOCK.unlink(missing_ok=True)
                continue  # tentar de novo

            return None  # outro supervisor valido em execucao


def _libertar_lock(fd: int) -> None:
    try:
        os.close(fd)
    except Exception:
        pass
    LOCK.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Funcao observavel — corrigido (ADDENDUM-01 DEFEITO 2)
#
# uma_volta_sup() e a unidade testavel do loop.
# Devolve (accao, estado, proc) onde accao e:
#   VIVO       — worker esta a correr normalmente
#   RELANCADO  — worker foi relancado
#   IDLE       — sem trabalho elegivel
#   BLOQUEADO  — crashloop detectado; servico em BLOCKED
#   PARA_FLAG  — PARAR.flag existe; nao relancar
# ---------------------------------------------------------------------------

def uma_volta_sup(
    estado: dict,
    proc: Optional[subprocess.Popen],
    pausa_worker: float = 1.0,
    hook_fila_vazia=None,
) -> tuple[str, dict, Optional[subprocess.Popen]]:
    """Uma iteracao do supervisor.

    Testavel: nao dorme, nao tem side-effects de timing. O caller decide
    quantas vezes chamar e o que fazer com o resultado.

    hook_fila_vazia: callable() opcional, chamado UMA vez por volta em que
    nao ha trabalho elegivel (IDLE). E o unico ponto onde fila vazia pode
    accionar descoberta — sem ele o ciclo nunca se realimenta. Padrao None
    (sem hook: comportamento identico ao de antes). Nao bloqueia a volta:
    excecao no hook e anotada no diario como DISCOVERY_HOOK_ERRO e a volta
    devolve IDLE na mesma. (Enxerto de candidate-bridge-v1, 63b71421.)
    """
    # --- PARAR.flag ---
    if PARAR.exists():
        return "PARA_FLAG", estado, proc

    # --- estado actual do worker ---
    worker_vivo = (proc is not None
                   and proc.poll() is None
                   and _worker_vivo(estado))

    if worker_vivo:
        hb = _ultimo_heartbeat()
        if hb:
            estado["LAST_PROGRESS_AT"] = hb.isoformat()
        estado["SUPERVISOR_STATE"] = "RUNNING"
        estado["WORKER_ALIVE"] = True
        _gravar_estado(estado)
        return "VIVO", estado, proc

    # --- worker nao esta vivo ---

    # Registar morte e actualizar contador de crashes SEM progresso.
    # (ADDENDUM-01 DEFEITO 3: so conta mortes sem progresso.)
    if proc is not None and estado.get("WORKER_PID"):
        hb_atual = _ultimo_heartbeat()
        hb_str   = hb_atual.isoformat() if hb_atual else None
        ultimo_hb_antes = estado.get("LAST_PROGRESS_AT")

        # Progresso = heartbeat avancou desde o ultimo registo.
        progrediu = bool(hb_str and hb_str != ultimo_hb_antes)

        if hb_str:
            estado["LAST_PROGRESS_AT"] = hb_str

        rc = proc.returncode if proc.poll() is not None else None
        _anotar({
            "EVENTO": "WORKER_MORTO",
            "PID": estado["WORKER_PID"],
            "RC": rc,
            "PROGREDIU": progrediu,
            "HB_ANTES": ultimo_hb_antes,
            "HB_AGORA": hb_str,
        })

        if progrediu:
            # Morte com progresso: repoe o contador.
            estado["CRASHES_SEM_PROGRESSO"] = []
        else:
            agora_ts  = _agora()
            agora_dt  = datetime.fromisoformat(agora_ts)
            estado.setdefault("CRASHES_SEM_PROGRESSO", []).append({
                "AT": agora_ts,
                "LAST_HB": hb_str,
            })
            # Remover entradas fora da janela temporal.
            estado["CRASHES_SEM_PROGRESSO"] = [
                c for c in estado["CRASHES_SEM_PROGRESSO"]
                if (agora_dt - datetime.fromisoformat(c["AT"])).total_seconds()
                < CRASH_JANELA_S
            ]

    # --- anti-crashloop ---
    n_sem_progresso = len(estado.get("CRASHES_SEM_PROGRESSO", []))
    if n_sem_progresso >= CRASH_MAX:
        motivo = ("worker morreu %d vezes em %ds sem progresso "
                  "— crashloop detectado" % (CRASH_MAX, CRASH_JANELA_S))
        estado["SUPERVISOR_STATE"] = "BLOCKED"
        estado["SUPERVISOR_BLOCKED_REASON"] = motivo
        estado["WORKER_PID"] = None
        _gravar_estado(estado)
        _anotar({"EVENTO": "SUPERVISOR_BLOCKED", "MOTIVO": motivo})
        return "BLOQUEADO", estado, None

    # --- sem trabalho elegivel -> IDLE ---
    n_elegiveis = len(F.elegiveis())
    if n_elegiveis == 0:
        estado["SUPERVISOR_STATE"] = "IDLE"
        estado["WORKER_PID"] = None

        # Hook de discovery: fila vazia e o momento de pedir candidatas.
        # Quem passa o hook decide o que ele faz; o supervisor so garante
        # que uma excecao la dentro nao o mata.
        if hook_fila_vazia is not None:
            try:
                hook_fila_vazia()
            except Exception as ex:  # noqa: BLE001 — o hook nao manda no loop
                _anotar({"EVENTO": "DISCOVERY_HOOK_ERRO",
                         "ERRO": "%s: %s" % (type(ex).__name__, str(ex)[:200])})

        _gravar_estado(estado)
        return "IDLE", estado, None

    # --- relancar ---
    motivo = "sem worker vivo e %d tarefas elegiveis" % n_elegiveis
    proc_novo = _lancar_worker(pausa_worker)
    estado["WORKER_PID"]          = proc_novo.pid
    estado["WORKER_STARTED_AT"]   = _agora()
    estado["SUPERVISOR_STATE"]    = "RUNNING"
    estado["RESTARTS_TOTAL"]      = estado.get("RESTARTS_TOTAL", 0) + 1
    estado["LAST_RESTART_AT"]     = _agora()
    estado["LAST_RESTART_REASON"] = motivo
    _gravar_estado(estado)
    _anotar({
        "EVENTO": "WORKER_RELANCADO",
        "PID": proc_novo.pid,
        "RESTARTS_TOTAL": estado["RESTARTS_TOTAL"],
        "MOTIVO": motivo,
    })
    return "RELANCADO", estado, proc_novo


# ---------------------------------------------------------------------------
# Loop principal
# ---------------------------------------------------------------------------

def supervisionar(pausa_worker: float = 1.0,
                  poll: float = SUPERVISOR_POLL_S) -> int:
    lock_fd = _adquirir_lock()
    if lock_fd is None:
        print("SUPERVISOR ja em execucao (lock valido). A sair.")
        return 1

    try:
        return _loop(pausa_worker, poll)
    finally:
        _libertar_lock(lock_fd)


def _loop(pausa_worker: float, poll: float) -> int:
    estado = _ler_estado()
    estado.setdefault("SUPERVISOR_STATE", "STARTING")
    estado.setdefault("RESTARTS_TOTAL", 0)
    estado.setdefault("CRASHES_SEM_PROGRESSO", [])
    estado["SUPERVISOR_PID"]        = os.getpid()
    estado["SUPERVISOR_STARTED_AT"] = _agora()

    orfas = F.recuperar_orfas()
    if orfas:
        _anotar({"EVENTO": "ORFAS_RECUPERADAS", "TOTAL": len(orfas)})
    _anotar({
        "EVENTO": "SUPERVISOR_ARRANQUE",
        "SUPERVISOR_PID": os.getpid(),
        "ORFAS_RECUPERADAS": len(orfas),
    })

    proc: Optional[subprocess.Popen] = None

    try:
        while True:
            accao, estado, proc = uma_volta_sup(estado, proc, pausa_worker)

            if accao == "PARA_FLAG":
                motivo = PARAR.read_text(encoding="utf-8").strip()[:120]
                print("SUPERVISOR: PARAR.flag — %s" % motivo, flush=True)
                estado["SUPERVISOR_STATE"] = "STOPPED"
                estado["WORKER_PID"] = None
                _gravar_estado(estado)
                _anotar({"EVENTO": "SUPERVISOR_PARADO_POR_FLAG",
                         "MOTIVO": motivo})
                return 0

            if accao == "BLOQUEADO":
                return 2

            print("SUPERVISOR: %s (restarts=%d)" % (
                accao, estado.get("RESTARTS_TOTAL", 0)), flush=True)

            time.sleep(poll)

    finally:
        # Garantia: ao sair, o supervisor termina o worker ou declara
        # explicitamente no estado que o deixou a correr.
        if proc and proc.poll() is None:
            _anotar({"EVENTO": "SUPERVISOR_TERMINA_WORKER_NA_SAIDA",
                     "PID": proc.pid,
                     "MOTIVO": "supervisor a terminar — terminar worker para evitar orfao"})
            proc.terminate()
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()
            estado["WORKER_PID"] = None
            estado["SUPERVISOR_STATE"] = "STOPPED"
            _gravar_estado(estado)


# ---------------------------------------------------------------------------
# Leitura de estado (para o status_live)
# ---------------------------------------------------------------------------

def ler_estado_servico() -> dict:
    """Devolve o estado actual do servico. Nunca levanta excecao.

        FICHEIRO DIZ RUNNING != PROCESSO EXISTE.

    Medido (CANDIDATE-FEEDER-V1, PASSO 9): um STATUS-LIVE dizia RUNNING com
    WORKER_ALIVE true e WORKER_PID 97820 — PID inexistente. O painel herdava
    verde de um ficheiro velho. Aqui cada PID e perguntado ao SO (tasklist),
    e o nome do estado distingue TRES paragens que o ficheiro confundia:

        RUNNING           ficheiro RUNNING, worker vivo no SO, batimento fresco
        IDLE              supervisor vivo, sem worker de proposito (0 elegiveis)
        STOPPED_FINISHED  o supervisor saiu limpo (PARAR.flag ou fim pedido)
        STOPPED_BROKEN    o ficheiro diz RUNNING/IDLE e o SO diz que nao ha
                          ninguem — morreu sem escrever
        BLOCKED           crashloop declarado pelo proprio supervisor
        UNKNOWN           sem ficheiro, ou ficheiro ilegivel

    O supervisor tambem e medido: um IDLE com o SUPERVISOR_PID morto e um
    STOPPED_BROKEN, nao um IDLE.
    """
    try:
        s = _ler_estado()
    except Exception:
        s = {}

    pid   = s.get("WORKER_PID")
    alive = bool(pid and _pid_no_so(pid) and _proc_e_python(pid))
    sup_pid = s.get("SUPERVISOR_PID")
    sup_alive = bool(sup_pid and _pid_no_so(sup_pid) and _proc_e_python(sup_pid))

    hb = _ultimo_heartbeat()
    hb_fresco = None
    if hb:
        s["LAST_PROGRESS_AT"] = hb.isoformat()
        delta = (datetime.now(timezone.utc) - hb).total_seconds()
        hb_fresco = delta < HEARTBEAT_TIMEOUT_S
        if alive and not hb_fresco:
            alive = False

    ficheiro = s.get("SUPERVISOR_STATE", "UNKNOWN") if s else "UNKNOWN"
    if ficheiro == "RUNNING":
        state = "RUNNING" if (alive and sup_alive) else "STOPPED_BROKEN"
    elif ficheiro == "IDLE":
        state = "IDLE" if sup_alive else "STOPPED_BROKEN"
    elif ficheiro == "STOPPED":
        state = "STOPPED_FINISHED"
    elif ficheiro == "BLOCKED":
        state = "BLOCKED"
    elif ficheiro == "STARTING":
        state = "RUNNING" if sup_alive else "STOPPED_BROKEN"
    else:
        state = "UNKNOWN"

    return {
        "SOURCE_CURATOR_SERVICE":   state,
        "SERVICE_STATE_IN_FILE":    ficheiro,
        "SERVICE_STATE_MEASURED_VIA": "tasklist PID + nome de imagem python + batimento no run log",
        "SUPERVISOR_PID":           sup_pid,
        "SUPERVISOR_ALIVE":         sup_alive,
        "WORKER_PID":               pid,
        "WORKER_ALIVE":             alive,
        "HEARTBEAT_FRESH":          hb_fresco,
        "LAST_PROGRESS_AT":         s.get("LAST_PROGRESS_AT"),
        "RESTARTS_TOTAL":           s.get("RESTARTS_TOTAL", 0),
        "LAST_RESTART_AT":          s.get("LAST_RESTART_AT"),
        "LAST_RESTART_REASON":      s.get("LAST_RESTART_REASON"),
        "SUPERVISOR_BLOCKED_REASON": s.get("SUPERVISOR_BLOCKED_REASON"),
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(
        description="Supervisor do Source Curator — relanca o worker quando morre.")
    ap.add_argument("--pausa", type=float, default=1.0)
    ap.add_argument("--poll",  type=float, default=SUPERVISOR_POLL_S)
    ap.add_argument("--estado", action="store_true",
                    help="Mostrar estado actual e sair")
    a = ap.parse_args()

    if a.estado:
        print(json.dumps(ler_estado_servico(), ensure_ascii=False, indent=1))
        return 0

    print("SUPERVISOR DO SOURCE CURATOR — PID=%d  arrancou=%s"
          % (os.getpid(), _agora()), flush=True)
    return supervisionar(a.pausa, a.poll)


if __name__ == "__main__":
    raise SystemExit(main())
