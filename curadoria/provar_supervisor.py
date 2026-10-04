#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PROVA DE CONTINUIDADE DO SUPERVISOR — entregavel da missao SUPERVISOR-V1.

Prova os 10 requisitos. Usa uma_volta_sup() directamente para asserar a
SEQUENCIA de accoes (ADDENDUM-01 DEFEITO 2), em vez de timeouts sobre
ficheiros.

Nomenclatura honesta:
  REAL     = subprocess real, fila real, verificacao de PID no SO
  SIMULADO = estado injectado ou fila controlada, sem rede
  NOT_RUN  = nao correu (declarado explicitamente)
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))

import fila as F       # noqa: E402
import supervisor as S # noqa: E402

PROVA_SAIDA = RAIZ / "curadoria" / "SUPERVISOR-PROOF-V1.json"
PARAR       = RAIZ / "curadoria" / "PARAR.flag"
LOCK        = RAIZ / "curadoria" / "SUPERVISOR.lock"

TEST_SID_A = "IT-PROOF-SUP-001"
TEST_SID_B = "IT-PROOF-SUP-002"
TEST_SID_C = "IT-PROOF-SUP-003"


# ---------------------------------------------------------------------------
# Utilitarios
# ---------------------------------------------------------------------------

def _agora() -> str:
    return datetime.now(timezone.utc).isoformat()


def _limpar_tarefas_prova() -> None:
    d = F._ler()
    d["TAREFAS"] = [t for t in d["TAREFAS"]
                    if not t["SOURCE_ID"].startswith("IT-PROOF-")]
    F._gravar(d)


def _injetar(sid: str, tipo: str = F.CANARY) -> dict:
    return F.enfileirar(sid, tipo, priority=10,
                        motivo="PROVA SUPERVISOR — remover apos teste")


def _estado_inicial() -> dict:
    for p in (S.ESTADO, S.LOCK, PARAR):
        p.unlink(missing_ok=True)
    return {
        "SUPERVISOR_STATE": "STARTING",
        "RESTARTS_TOTAL": 0,
        "CRASHES_SEM_PROGRESSO": [],
    }


def _aguardar_tarefa_fechada(sids: list[str], timeout: float = 20.0) -> bool:
    t0 = time.monotonic()
    while time.monotonic() - t0 < timeout:
        d = F._ler()
        fechadas = [t for t in d["TAREFAS"]
                    if t["SOURCE_ID"] in sids
                    and t["STATUS"] in (F.DONE, F.FAILED, F.BLOCKED)]
        if fechadas:
            return True
        time.sleep(0.3)
    return False


def _matar_proc(proc: subprocess.Popen) -> bool:
    """Kill no Windows. Devolve True se o processo morreu."""
    try:
        subprocess.run(["taskkill", "/F", "/PID", str(proc.pid)],
                       capture_output=True, timeout=5)
    except Exception:
        try:
            proc.kill()
        except Exception:
            return False
    t0 = time.monotonic()
    while time.monotonic() - t0 < 8:
        if not S._pid_no_so(proc.pid):
            return True
        time.sleep(0.2)
    return False


def _lancar_worker_directo(pausa: float = 0.5) -> subprocess.Popen:
    """Lanca ciclo_continuo.py directamente (sem supervisor subprocess)."""
    cmd = [sys.executable,
           str(RAIZ / "curadoria" / "ciclo_continuo.py"),
           "--pausa", str(pausa)]
    return subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, encoding="utf-8", errors="replace",
    )


# ---------------------------------------------------------------------------
# Provas individuais — usando uma_volta_sup() directamente
# ---------------------------------------------------------------------------

def prova_01_worker_arranca(resultados: dict) -> tuple[dict, subprocess.Popen | None]:
    """REAL. Worker arranca quando ha trabalho elegivel.

    Chamamos uma_volta_sup com proc=None e verificamos que a accao devolvida
    e RELANCADO (e que um subprocess real foi criado).
    """
    estado = _estado_inicial()
    _limpar_tarefas_prova()
    _injetar(TEST_SID_A)

    accao, estado, proc = S.uma_volta_sup(estado, None, pausa_worker=0.5)
    passou = (accao == "RELANCADO"
              and proc is not None
              and S._pid_no_so(proc.pid))
    resultados["01_WORKER_ARRANCA"] = {
        "PASSOU": passou,
        "TIPO": "REAL",
        "ACCAO": accao,
        "WORKER_PID": proc.pid if proc else None,
        "NOTA": ("accao=RELANCADO, PID=%s vivo" % (proc.pid if proc else None))
                if passou else "accao=%s ou PID morto" % accao,
    }
    return estado, proc


def prova_02_processa_item(resultados: dict,
                           estado: dict, proc: subprocess.Popen | None) -> dict:
    """REAL. Worker processa pelo menos 1 item."""
    passou = False
    if proc:
        passou = _aguardar_tarefa_fechada([TEST_SID_A], timeout=20)
        # Dar uma volta ao supervisor para actualizar o estado.
        accao2, estado, proc = S.uma_volta_sup(estado, proc, pausa_worker=0.5)

    resultados["02_PROCESSA_ITEM"] = {
        "PASSOU": passou,
        "TIPO": "REAL",
        "NOTA": "tarefa IT-PROOF-SUP-001 fechada (BLOCK esperado — sem contrato)"
                if passou else "worker nao processou em 20s",
    }
    return estado


def prova_03_estado_persiste(resultados: dict, estado: dict) -> None:
    """REAL. SUPERVISOR-STATE.json existe e tem PID."""
    s_disco = S._ler_estado()
    passou = (S.ESTADO.exists()
              and s_disco.get("WORKER_PID") is not None
              and s_disco.get("SUPERVISOR_STATE") is not None)
    resultados["03_ESTADO_PERSISTE"] = {
        "PASSOU": passou,
        "TIPO": "REAL",
        "SUPERVISOR_STATE": s_disco.get("SUPERVISOR_STATE"),
        "WORKER_PID": s_disco.get("WORKER_PID"),
    }


def prova_04_matar_worker(resultados: dict,
                          estado: dict, proc: subprocess.Popen | None
                          ) -> tuple[dict, subprocess.Popen | None, int | None]:
    """REAL. Mata o worker e verifica que o PID desapareceu do SO."""
    if not proc or not S._pid_no_so(proc.pid):
        resultados["04_MATAR_WORKER"] = {
            "PASSOU": False, "TIPO": "REAL",
            "NOTA": "sem worker vivo para matar",
        }
        return estado, proc, None

    _injetar(TEST_SID_B)
    _injetar(TEST_SID_C)
    pid_morto = proc.pid
    morreu = _matar_proc(proc)

    resultados["04_MATAR_WORKER"] = {
        "PASSOU": morreu,
        "TIPO": "REAL",
        "PID_MORTO": pid_morto,
        "NOTA": "taskkill confirmado" if morreu else "processo nao morreu em 8s",
    }
    return estado, proc, pid_morto if morreu else None


def prova_05_06_detecta_e_relanca(resultados: dict,
                                   estado: dict, proc: subprocess.Popen | None,
                                   pid_morto: int | None
                                   ) -> tuple[dict, subprocess.Popen | None]:
    """REAL. Supervisor detecta morte (05) e relanca (06) — numa volta observavel.

    Com uma_volta_sup:
    - proc.poll() nao e None (worker morto) -> _worker_vivo = False
    - crashes_sem_progresso < CRASH_MAX
    - elegiveis > 0 (B e C injectados)
    -> accao = RELANCADO (prova 05 e 06 de uma vez)
    """
    if pid_morto is None:
        for num, nome in [("05", "DETECTA_MORTE"), ("06", "RELANCA")]:
            resultados["%s_%s" % (num, nome)] = {
                "PASSOU": False, "TIPO": "REAL",
                "NOTA": "prova 04 falhou — sem PID morto",
            }
        return estado, proc

    accao, estado, proc_novo = S.uma_volta_sup(estado, proc, pausa_worker=0.5)
    detectou = (accao in ("RELANCADO", "IDLE"))
    relancou = (accao == "RELANCADO"
                and proc_novo is not None
                and S._pid_no_so(proc_novo.pid))

    resultados["05_DETECTA_MORTE"] = {
        "PASSOU": detectou,
        "TIPO": "REAL",
        "ACCAO": accao,
        "NOTA": ("morte detectada — accao=%s" % accao) if detectou
                else "accao inesperada: %s" % accao,
    }
    resultados["06_RELANCA"] = {
        "PASSOU": relancou,
        "TIPO": "REAL",
        "ACCAO": accao,
        "PID_NOVO": proc_novo.pid if proc_novo else None,
        "RESTARTS_TOTAL": estado.get("RESTARTS_TOTAL"),
        "NOTA": ("relancado com PID=%s" % (proc_novo.pid if proc_novo else None))
                if relancou else "nao relancou (accao=%s)" % accao,
    }
    return estado, proc_novo


def prova_07_retoma_sem_perder_estado(resultados: dict,
                                       estado: dict,
                                       proc: subprocess.Popen | None) -> None:
    """REAL + SIMULADO.

    REAL: fila intacta (tarefas de teste presentes), ORFAS_RECUPERADAS no log.
    SIMULADO: demonstracao directa de recuperar_orfas() com timestamp antigo
    (o timeout de 1800s impossibilita prova real no tempo do teste).
    """
    d = F._ler()
    tarefas_teste = [t for t in d["TAREFAS"]
                     if t["SOURCE_ID"].startswith("IT-PROOF-SUP-")]
    fila_intacta = len(tarefas_teste) >= 2

    # Prova directa de recuperar_orfas com timestamp forjado (SIMULADO).
    _injetar("IT-PROOF-ORFA-001")
    d2 = F._ler()
    for t in d2["TAREFAS"]:
        if t["SOURCE_ID"] == "IT-PROOF-ORFA-001":
            t["STATUS"] = F.IN_PROGRESS
            # Timestamp velho: 31 minutos antes.
            from datetime import timedelta
            t["UPDATED_AT"] = (datetime.now(timezone.utc)
                               - timedelta(minutes=31)).isoformat()
    F._gravar(d2)

    orfas = F.recuperar_orfas()
    orfas_ids = [o["SOURCE_ID"] for o in orfas]
    orfas_demo = "IT-PROOF-ORFA-001" in orfas_ids

    # Limpar.
    d3 = F._ler()
    d3["TAREFAS"] = [t for t in d3["TAREFAS"]
                     if t["SOURCE_ID"] != "IT-PROOF-ORFA-001"]
    F._gravar(d3)

    # Log do supervisor tem ORFAS_RECUPERADAS?
    orfas_no_log = False
    try:
        linhas = S.DIARIO.read_text(encoding="utf-8", errors="replace").splitlines()
        for linha in reversed(linhas[-200:]):
            try:
                ev = json.loads(linha)
                if ev.get("EVENTO") == "ORFAS_RECUPERADAS":
                    orfas_no_log = True
                    break
            except Exception:
                pass
    except Exception:
        pass

    passou = fila_intacta and orfas_demo
    resultados["07_RETOMA_SEM_PERDER_ESTADO"] = {
        "PASSOU": passou,
        "TIPO": "REAL+SIMULADO",
        "FILA_INTACTA_REAL": fila_intacta,
        "TAREFAS_TESTE": len(tarefas_teste),
        "ORFAS_DEMO_SIMULADO": orfas_demo,
        "ORFAS_NO_LOG": orfas_no_log,
        "NOTA": ("fila intacta [REAL]; recuperar_orfas prova mecanismo [SIMULADO]"
                 if passou else "falhou: fila_intacta=%s orfas_demo=%s"
                 % (fila_intacta, orfas_demo)),
    }


def prova_08_retry_nao_bloqueia(resultados: dict) -> None:
    """SIMULADO. Uma tarefa em RETRY nao bloqueia as outras."""
    _limpar_tarefas_prova()
    _injetar("IT-PROOF-RETRY-001")
    _injetar("IT-PROOF-RETRY-002")

    d = F._ler()
    ta = next(t for t in d["TAREFAS"]
              if t["SOURCE_ID"] == "IT-PROOF-RETRY-001")
    tb = next(t for t in d["TAREFAS"]
              if t["SOURCE_ID"] == "IT-PROOF-RETRY-002")

    F.adiar(ta["TASK_ID"], retry_after_s=3600, erro="429 simulado",
            agora=F.agora_utc())

    elegiveis = [t["TASK_ID"] for t in F.elegiveis()
                 if t["SOURCE_ID"].startswith("IT-PROOF-RETRY-")]
    passou = tb["TASK_ID"] in elegiveis

    resultados["08_RETRY_NAO_BLOQUEIA"] = {
        "PASSOU": passou,
        "TIPO": "SIMULADO",
        "ELEGIVEIS_TESTE": elegiveis,
        "NOTA": ("RETRY-001 adiada; RETRY-002 continua elegivel" if passou
                 else "RETRY-002 desapareceu dos elegiveis — bug na fila"),
    }
    _limpar_tarefas_prova()


def prova_09_parar_flag(resultados: dict) -> None:
    """SIMULADO. PARAR.flag impede relancamento.

    Sequencia observada: uma_volta_sup com PARAR.flag existente -> PARA_FLAG.
    """
    estado_t = {
        "SUPERVISOR_STATE": "STARTING",
        "RESTARTS_TOTAL": 0,
        "CRASHES_SEM_PROGRESSO": [],
    }
    _injetar(TEST_SID_A)
    PARAR.write_text("PROVA-09: parar solicitado pelo teste", encoding="utf-8")

    accao, estado_t, proc_t = S.uma_volta_sup(estado_t, None, pausa_worker=0.5)

    passou = accao == "PARA_FLAG" and proc_t is None
    resultados["09_PARAR_FLAG"] = {
        "PASSOU": passou,
        "TIPO": "SIMULADO",
        "ACCAO": accao,
        "WORKER_PID": proc_t.pid if proc_t else None,
        "NOTA": ("PARA_FLAG devolvido; worker nao lancado" if passou
                 else "accao inesperada: %s" % accao),
    }
    PARAR.unlink(missing_ok=True)


def prova_10_crashloop_blocked(resultados: dict) -> None:
    """SIMULADO. Crashloop SEM PROGRESSO -> BLOQUEADO.

    Injecto CRASH_MAX mortes sem progresso no estado e verifico que
    uma_volta_sup devolve BLOQUEADO.

    Tambem verifica que morte COM progresso NAO conta para o crashloop
    (defeito 3 do ADDENDUM-01).
    """
    # --- parte A: crashloop sem progresso -> BLOQUEADO ---
    from datetime import timedelta
    agora_ts = _agora()
    crashes = [{"AT": agora_ts, "LAST_HB": None}
               for _ in range(S.CRASH_MAX)]
    estado_t = {
        "SUPERVISOR_STATE": "RUNNING",
        "RESTARTS_TOTAL": S.CRASH_MAX,
        "CRASHES_SEM_PROGRESSO": crashes,
        "WORKER_PID": None,
    }
    _limpar_tarefas_prova()
    _injetar(TEST_SID_A)
    PARAR.unlink(missing_ok=True)

    accao_a, estado_a, proc_a = S.uma_volta_sup(estado_t, None, pausa_worker=0.5)
    passou_a = accao_a == "BLOQUEADO"

    # --- parte B: morte COM progresso nao alimenta o crashloop ---
    # Simular um worker que morre mas cujo heartbeat avancou.
    estado_b = {
        "SUPERVISOR_STATE": "RUNNING",
        "RESTARTS_TOTAL": 0,
        "CRASHES_SEM_PROGRESSO": [],
        "WORKER_PID": 99999,
        "LAST_PROGRESS_AT": "2026-01-01T00:00:00+00:00",
    }
    _injetar(TEST_SID_B)

    # Escrever um heartbeat mais recente no run log.
    import json as _json
    S.DIARIO.open("a", encoding="utf-8").write(
        _json.dumps({"EVENTO": "VOLTA", "AT": _agora(),
                     "ORIGEM": "WORKER_TESTE"}) + "\n"
    )
    # proc simulado que ja morreu (poll != None)
    proc_simulado = subprocess.Popen(
        [sys.executable, "-c", "pass"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    proc_simulado.wait()  # ja terminou, poll() retorna 0

    accao_b, estado_b2, _ = S.uma_volta_sup(estado_b, proc_simulado, pausa_worker=0.5)
    # Com progresso, crashes_sem_progresso deve ser zerado e nao BLOQUEADO.
    passou_b = (accao_b != "BLOQUEADO"
                and len(estado_b2.get("CRASHES_SEM_PROGRESSO", [])) == 0)

    passou = passou_a and passou_b
    resultados["10_CRASHLOOP_BLOCKED"] = {
        "PASSOU": passou,
        "TIPO": "SIMULADO",
        "ACCAO_CRASHLOOP": accao_a,
        "ACCAO_COM_PROGRESSO": accao_b,
        "CRASHES_APOS_PROGRESSO": len(estado_b2.get("CRASHES_SEM_PROGRESSO", [])),
        "NOTA": ("crashloop->BLOQUEADO [A]; morte com progresso nao conta [B]"
                 if passou
                 else "falhou: A=%s (esperado BLOQUEADO), B=%s (esperado reset)"
                 % (accao_a, accao_b)),
    }
    _limpar_tarefas_prova()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    print("PROVA DE CONTINUIDADE DO SUPERVISOR — %s" % _agora(), flush=True)

    resultados: dict = {
        "DATASET": "SUPERVISOR-PROOF-V1",
        "GERADO_EM": _agora(),
        "MISSAO": "SOURCE-CURATOR-SUPERVISOR-V1",
    }

    estado: dict = {}
    proc: subprocess.Popen | None = None

    try:
        PARAR.unlink(missing_ok=True)
        LOCK.unlink(missing_ok=True)
        _limpar_tarefas_prova()

        print("01 — worker arranca (REAL)...", flush=True)
        estado, proc = prova_01_worker_arranca(resultados)
        print("   %s" % resultados["01_WORKER_ARRANCA"]["NOTA"], flush=True)

        print("02 — processa item (REAL)...", flush=True)
        estado = prova_02_processa_item(resultados, estado, proc)
        print("   %s" % resultados["02_PROCESSA_ITEM"]["NOTA"], flush=True)

        print("03 — estado persiste (REAL)...", flush=True)
        prova_03_estado_persiste(resultados, estado)
        print("   state=%s pid=%s" % (
            resultados["03_ESTADO_PERSISTE"]["SUPERVISOR_STATE"],
            resultados["03_ESTADO_PERSISTE"]["WORKER_PID"]), flush=True)

        print("04 — matar worker (REAL)...", flush=True)
        estado, proc, pid_morto = prova_04_matar_worker(resultados, estado, proc)
        print("   %s" % resultados["04_MATAR_WORKER"]["NOTA"], flush=True)

        print("05+06 — detecta morte e relanca (REAL)...", flush=True)
        estado, proc = prova_05_06_detecta_e_relanca(
            resultados, estado, proc, pid_morto)
        print("   05: %s" % resultados["05_DETECTA_MORTE"]["NOTA"], flush=True)
        print("   06: %s" % resultados["06_RELANCA"]["NOTA"], flush=True)

        print("07 — retoma sem perder estado (REAL+SIMULADO)...", flush=True)
        prova_07_retoma_sem_perder_estado(resultados, estado, proc)
        print("   %s" % resultados["07_RETOMA_SEM_PERDER_ESTADO"]["NOTA"],
              flush=True)

    finally:
        # Parar o worker que ficou a correr.
        if proc and proc.poll() is None:
            try:
                proc.terminate()
                proc.wait(timeout=5)
            except Exception:
                proc.kill()
        PARAR.unlink(missing_ok=True)
        LOCK.unlink(missing_ok=True)

    # Provas isoladas (nao precisam do worker das provas 01-07).
    print("08 — retry nao bloqueia (SIMULADO)...", flush=True)
    prova_08_retry_nao_bloqueia(resultados)
    print("   %s" % resultados["08_RETRY_NAO_BLOQUEIA"]["NOTA"], flush=True)

    print("09 — PARAR.flag (SIMULADO)...", flush=True)
    prova_09_parar_flag(resultados)
    print("   %s" % resultados["09_PARAR_FLAG"]["NOTA"], flush=True)

    print("10 — crashloop BLOCKED (SIMULADO)...", flush=True)
    prova_10_crashloop_blocked(resultados)
    print("   %s" % resultados["10_CRASHLOOP_BLOCKED"]["NOTA"], flush=True)

    # Limpeza final.
    _limpar_tarefas_prova()
    PARAR.unlink(missing_ok=True)
    LOCK.unlink(missing_ok=True)

    # --- veredito ---
    provas = {k: v for k, v in resultados.items()
              if len(k) >= 2 and k[:2].isdigit()}
    falhas = [k for k, v in provas.items() if not v.get("PASSOU")]

    resultados["CONTINUOUS_OPERATION_PROVEN"] = "YES" if not falhas else "NO"
    resultados["FALHAS"] = falhas
    resultados["PROVAS_TOTAL"] = len(provas)
    resultados["PROVAS_PASSOU"] = len(provas) - len(falhas)

    PROVA_SAIDA.write_text(
        json.dumps(resultados, ensure_ascii=False, indent=1, default=str),
        encoding="utf-8"
    )

    print("\n--- VEREDITO ---", flush=True)
    for k, v in sorted(provas.items()):
        estado_str = "PASS" if v.get("PASSOU") else "FAIL"
        tipo = v.get("TIPO", "?")
        print("  %s  [%s] %s" % (estado_str, tipo, k), flush=True)
    print("\nCONTINUOUS_OPERATION_PROVEN = %s"
          % resultados["CONTINUOUS_OPERATION_PROVEN"], flush=True)
    if falhas:
        print("FALHOU: %s" % ", ".join(falhas), flush=True)
    print("Gravado em: %s" % PROVA_SAIDA, flush=True)
    return 0 if not falhas else 1


if __name__ == "__main__":
    raise SystemExit(main())
