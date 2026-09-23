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


PULSO = RAIZ / "curadoria" / "WORKER-HEARTBEAT.json"


def _ultimo_heartbeat() -> Optional[datetime]:
    """O mais recente de: ultima linha do run log, pulso por tarefa do worker.

    Sem o pulso, o heartbeat so avancava no fim de uma VOLTA inteira — e uma
    volta longa de trabalho real lia-se como worker pendurado (M2d).
    """
    marcas = [m for m in (_heartbeat_do_diario(), _heartbeat_do_pulso()) if m]
    return max(marcas) if marcas else None


def _heartbeat_do_pulso() -> Optional[datetime]:
    try:
        return datetime.fromisoformat(
            json.loads(PULSO.read_text(encoding="utf-8"))["AT"])
    except Exception:
        return None


def _heartbeat_do_diario() -> Optional[datetime]:
    """Le o timestamp AT da ultima linha do run log."""
    if not DIARIO.exists():
        return None
    try:
        last = None
        with DIARIO.open("r", encoding="utf-8", errors="replace") as fh:
            for linha in fh:
                linha = linha.strip()
                if linha:
                    last = linha
        if last:
            d = json.loads(last)
            return datetime.fromisoformat(d["AT"])
    except Exception:
        pass
    return None


def _saida_limpa(rc: Optional[int]) -> bool:
    """rc 0 = o worker saiu por decisao propria (ocioso, PARAR, --voltas).

    Um crash em Python sai com rc 1; um processo morto pelo SO nao sai com 0.
    None = ainda nao ha rc (processo sem poll) — nao e saida limpa.
    """
    return rc == 0


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

# ⚠️ O CANO QUE NINGUEM LE PENDURA O WORKER. Ate 23/09 o stdout do worker ia
# para subprocess.PIPE e o supervisor nunca o lia. O cano anonimo do Windows
# guarda ~4 KB: medido (M2d, WORKER-PENDURADO-ENSAIO-V1), o ciclo_continuo real
# escreveu 3.994 bytes, fechou 64 de 80 tarefas e ficou vivo e parado no print
# seguinte, para sempre. O que ele escreve vai agora para um ficheiro, que se
# roda no arranque — e o que antes se perdia no cano passa a ler-se.
#
#     UM CANO SEM LEITOR NAO E UM LOG, E UM TRAVAO.
WORKER_LOG = RAIZ / "curadoria" / "WORKER-STDOUT.log"
WORKER_LOG_MAX_BYTES = 5 * 1024 * 1024


def _abrir_log_do_worker():
    try:
        if WORKER_LOG.exists() and WORKER_LOG.stat().st_size > WORKER_LOG_MAX_BYTES:
            WORKER_LOG.replace(WORKER_LOG.with_name(WORKER_LOG.name + ".1"))
    except OSError:
        pass                       # rodar e cortesia; escrever e obrigatorio
    return WORKER_LOG.open("a", encoding="utf-8", errors="replace")


def _lancar_worker(pausa: float = 1.0, cmd: Optional[list] = None) -> subprocess.Popen:
    cmd = cmd or [sys.executable,
                  str(RAIZ / "curadoria" / "ciclo_continuo.py"),
                  "--pausa", str(pausa), "--sair-quando-ocioso"]
    log = _abrir_log_do_worker()
    try:
        return subprocess.Popen(
            cmd,
            stdout=log, stderr=subprocess.STDOUT,
            text=True, encoding="utf-8", errors="replace",
        )
    finally:
        log.close()                # o filho tem a sua copia do descritor


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

    hook_fila_vazia: callable() opcional chamado quando a fila de candidatos
    de discovery esta abaixo do limiar. Padrao None (sem hook — compativel
    com todos os testes existentes). Nao bloqueia; excecao e capturada e
    anotada sem parar o supervisor.
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

        # ⚠️ DECLARADO MORTO E AINDA VIVO: TERMINA-SE ANTES DE RELANCAR.
        # rc None = o processo existe mas o heartbeat envelheceu. Ate 23/09 o
        # supervisor relancava um segundo worker e deixava este vivo: dois
        # escritores na mesma fila, que grava sem trinco (fila._gravar). O
        # antigo so caia quando o cano fechado lhe rebentava o print seguinte.
        #
        #     UM SO ESCRITOR: QUEM SE DA COMO MORTO, MORRE.
        if rc is None:
            proc.terminate()
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=10)
            _anotar({"EVENTO": "WORKER_PENDURADO_TERMINADO",
                     "PID": estado["WORKER_PID"], "RC_APOS": proc.returncode,
                     "HB_AGORA": hb_str})

        _anotar({
            "EVENTO": "WORKER_MORTO",
            "PID": estado["WORKER_PID"],
            "RC": rc,
            "PROGREDIU": progrediu,
            "HB_ANTES": ultimo_hb_antes,
            "HB_AGORA": hb_str,
        })

        if _saida_limpa(rc):
            # ⚠️ SAIR NAO E MORRER. O worker ocioso sai com rc 0 de proposito
            # (ciclo_continuo --sair-quando-ocioso) e o heartbeat dele NAO
            # avanca desde a ultima volta VIVO — o supervisor ja o registou em
            # LAST_PROGRESS_AT. Contada como «morte sem progresso», 3 saidas
            # ociosas em 120 s mandariam o servico a BLOCKED. O contador fica
            # como esta: uma saida limpa nao e crash nem e progresso.
            _anotar({"EVENTO": "WORKER_SAIU_LIMPO", "PID": estado["WORKER_PID"],
                     "RC": rc})
        elif progrediu:
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

        # Hook de discovery: se a fila de candidatos estiver baixa, accionar.
        if hook_fila_vazia is not None:
            try:
                hook_fila_vazia()
            except Exception as ex:
                _anotar({"EVENTO": "DISCOVERY_HOOK_ERRO",
                         "ERRO": str(ex)[:200]})

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

    # ⚠️ O GATILHO DO MODO CONTINUO. Sem isto, o supervisor ficava IDLE para
    # sempre quando a fila esvaziasse — «a fila acabou» viraria paragem de
    # facto. O hook so age abaixo do limiar (ver gatilho_discovery), por isso
    # nao ha busy-loop nem despejo de candidatas.
    import gatilho_discovery as GD  # noqa: E402

    def _hook_fila_vazia():
        m = GD.talvez_alimentar(estado)
        if m.get("ACCOES"):
            _anotar({"EVENTO": "REALIMENTACAO", **m})

    try:
        while True:
            accao, estado, proc = uma_volta_sup(estado, proc, pausa_worker,
                                                hook_fila_vazia=_hook_fila_vazia)

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
    """Estado do servico DERIVADO DO SO no instante da leitura. Nunca levanta.

        UM JSON QUE DIZ RUNNING NAO E UM PROCESSO QUE EXISTE.

    O ficheiro SUPERVISOR-STATE.json guarda o ultimo rotulo que o supervisor
    escreveu — e esse rotulo envelhece: o processo morre e o ficheiro continua
    a dizer RUNNING, WORKER_ALIVE=true. Aqui NADA se herda do ficheiro para a
    vida:

      - o supervisor esta vivo? PID gravado existe no SO, agora?
      - o worker esta vivo? PID gravado existe no SO, agora?
      - o heartbeat e recente? senao, STALE, com o delta em segundos a vista.

    O ficheiro so contribui os PIDs e os contadores historicos (restarts, etc.);
    a vida vem sempre do SO.
    """
    try:
        s = _ler_estado()
    except Exception:
        s = {}

    agora = datetime.now(timezone.utc)

    # --- LIVENESS: PID no SO, no instante da leitura ---
    worker_pid = s.get("WORKER_PID")
    worker_pid_no_so = bool(worker_pid and _pid_no_so(worker_pid))
    sup_pid = s.get("SUPERVISOR_PID")
    sup_vivo = bool(sup_pid and _pid_no_so(sup_pid))

    # --- HEARTBEAT: idade real, sempre calculada ---
    hb = _ultimo_heartbeat()
    hb_iso = hb.isoformat() if hb else None
    hb_idade = (agora - hb).total_seconds() if hb else None
    hb_stale = bool(hb_idade is not None and hb_idade >= HEARTBEAT_TIMEOUT_S)

    # Worker vivo = PID no SO E heartbeat recente. Um PID vivo com heartbeat
    # velho e um worker PENDURADO, nao um worker a trabalhar.
    worker_alive = worker_pid_no_so and not hb_stale

    parar = PARAR.exists()
    try:
        n_eleg = len(F.elegiveis())
    except Exception:
        n_eleg = None

    estado_gravado = s.get("SUPERVISOR_STATE", "UNKNOWN")

    # --- ESTADO DO SUPERVISOR (do SO, nao do ficheiro) ---
    if estado_gravado == "BLOCKED":
        # crashloop: o supervisor pos-se BLOCKED e saiu. O rotulo persiste com
        # a razao; o processo ja nao esta vivo — e isso e coerente.
        supervisor_state = "BLOCKED"
    elif sup_vivo:
        supervisor_state = "STOPPING" if parar else "RUNNING"
    else:
        supervisor_state = "STOPPED"

    # --- ESTADO DO WORKER ---
    if worker_pid_no_so and hb_stale:
        worker_state = "STALE"           # PID existe, mas nao progride
    elif worker_alive:
        worker_state = "WORKING"
    elif supervisor_state == "RUNNING" and n_eleg == 0:
        worker_state = "IDLE"            # sem trabalho NAO se chama STOPPED
    elif supervisor_state == "RUNNING" and n_eleg:
        worker_state = "PENDING_RELAUNCH"
    else:
        worker_state = "DOWN"

    # --- rollup de compatibilidade ---
    service = {"RUNNING": "RUNNING", "STOPPING": "RUNNING",
               "BLOCKED": "BLOCKED"}.get(supervisor_state, "STOPPED")

    return {
        "SOURCE_CURATOR_SERVICE":    service,
        "SUPERVISOR_STATE":          supervisor_state,
        "SUPERVISOR_PID":            sup_pid,
        "SUPERVISOR_ALIVE":          sup_vivo,
        "WORKER_STATE":              worker_state,
        "WORKER_PID":                worker_pid,
        "WORKER_ALIVE":              worker_alive,
        "HEARTBEAT_AT":              hb_iso,
        "HEARTBEAT_AGE_S":           round(hb_idade, 1) if hb_idade is not None else None,
        "HEARTBEAT_STALE":           hb_stale,
        "HEARTBEAT_TIMEOUT_S":       HEARTBEAT_TIMEOUT_S,
        "QUEUE_ELIGIBLE_NOW":        n_eleg,
        "STOP_REQUESTED":            parar,
        "LAST_PROGRESS_AT":          hb_iso or s.get("LAST_PROGRESS_AT"),
        "RESTARTS_TOTAL":            s.get("RESTARTS_TOTAL", 0),
        "LAST_RESTART_AT":           s.get("LAST_RESTART_AT"),
        "LAST_RESTART_REASON":       s.get("LAST_RESTART_REASON"),
        "SUPERVISOR_BLOCKED_REASON": s.get("SUPERVISOR_BLOCKED_REASON"),
        # O FEEDER so corre quando a condicao muda; as voltas saltadas contam
        # aqui, para que o silencio no diario nao seja silencio no painel.
        "FEEDER_CHAMADAS_TOTAL":     s.get("FEEDER_CHAMADAS_TOTAL", 0),
        "FEEDER_NOOP_TOTAL":         s.get("FEEDER_NOOP_TOTAL", 0),
        "FEEDER_NOOP_ULTIMO_AT":     s.get("FEEDER_NOOP_ULTIMO_AT"),
        "FEEDER_ULTIMA_CHAMADA_AT":  s.get("FEEDER_ULTIMA_CHAMADA_AT"),
        "LIVENESS_SOURCE":           "DERIVED_FROM_OS_AT_READ_TIME",
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
