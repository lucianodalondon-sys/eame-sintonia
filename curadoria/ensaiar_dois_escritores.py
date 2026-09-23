#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DOIS ESCRITORES? — supervisor e workers REAIS numa COPIA da worktree.

    uso: py <COPIA>/curadoria/ensaiar_dois_escritores.py --sou-uma-copia [--drenar]

Encurta o relogio para caber num ensaio: HEARTBEAT_TIMEOUT_S = 10 s no
supervisor, e o worker com --pausa 12 (dorme 12 s entre tarefas). Assim o
supervisor da como morto um worker que esta so a descansar entre tarefas —
o mesmo que acontece em producao com uma volta/tarefa de mais de 300 s.

A cada ~0,5 s regista: que PIDs de worker estao vivos no SO, e que tarefas
fecharam. Cada worker imprime uma linha por tarefa; com --drenar le-se o
stdout de cada um num fio (para saber QUEM fechou cada tarefa — desvia-se da
producao, onde ninguem le). Sem --drenar, e como em producao.

Sem rede: tarefas CANARY de fontes SEM contrato. Recusa-se num checkout git.
"""
from __future__ import annotations

import json
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))

N_TAREFAS = 8
JANELA_S = 75


def _vivo(pid: int) -> bool:
    r = subprocess.run(["tasklist", "/FI", "PID eq %d" % pid, "/NH", "/FO", "CSV"],
                       capture_output=True, text=True, encoding="cp850", errors="replace")
    return str(pid) in r.stdout


def main() -> int:
    if "--sou-uma-copia" not in sys.argv or (RAIZ / ".git").exists():
        print("recuso: corre so numa copia (tar), nunca num checkout")
        return 2
    drenar = "--drenar" in sys.argv

    import fila as F
    import supervisor as S

    S.HEARTBEAT_TIMEOUT_S = 10
    agora = datetime.now(timezone.utc).isoformat()
    F.FILA.write_text(json.dumps({"PROXIMO_ID": 70000 + N_TAREFAS, "TAREFAS": [
        {"TASK_ID": "T7%04d" % i, "SOURCE_ID": "IT-ENSAIO-SEM-CONTRATO-%02d" % i,
         "TASK_TYPE": F.CANARY, "PRIORITY": 60, "STATUS": F.PENDING, "ATTEMPTS": 0,
         "NEXT_ATTEMPT_AT": None, "LAST_ERROR": None, "MOTIVO": "ensaio",
         "CREATED_AT": agora, "UPDATED_AT": agora} for i in range(N_TAREFAS)]}),
        encoding="utf-8")
    S.DIARIO.write_text("", encoding="utf-8")
    S.PARAR.unlink(missing_ok=True)

    linhas: list = []            # (t, pid, linha) — so com --drenar

    def _drena(p):
        for l in iter(p.stdout.readline, ""):
            if l.strip().startswith("IT-ENSAIO"):
                linhas.append((round(time.time() - t0, 1), p.pid, l.split()[0]))

    estado = {"SUPERVISOR_STATE": "STARTING", "RESTARTS_TOTAL": 0,
              "CRASHES_SEM_PROGRESSO": []}
    proc = None
    pids: list[int] = []
    amostras = []
    t0 = time.time()
    while time.time() - t0 < JANELA_S:
        a, estado, novo = S.uma_volta_sup(estado, proc, pausa_worker=12)
        if novo is not proc and novo is not None:
            pids.append(novo.pid)
            if drenar and novo.stdout:
                threading.Thread(target=_drena, args=(novo,), daemon=True).start()
        proc = novo            # como em producao: a referencia antiga e largada
        vivos = [p for p in pids if _vivo(p)]
        fechadas = sum(1 for t in F._ler()["TAREFAS"] if t["STATUS"] != F.PENDING)
        amostras.append({"T": round(time.time() - t0, 1), "ACCAO": a,
                         "VIVOS": vivos, "FECHADAS": fechadas})
        if fechadas == N_TAREFAS and a == "IDLE":
            break
        time.sleep(0.5)

    for p in pids:
        if _vivo(p):
            subprocess.run(["taskkill", "/F", "/PID", str(p)], capture_output=True)
    evs = [json.loads(l).get("EVENTO") for l in
           S.DIARIO.read_text(encoding="utf-8").splitlines() if l.strip()]
    max_vivos = max(len(s["VIVOS"]) for s in amostras)
    sobrepos = [s for s in amostras if len(s["VIVOS"]) > 1]
    por_pid = {}
    for t, pid, l in linhas:
        por_pid.setdefault(pid, []).append(t)
    # dois escritores = dois PIDs que fecham tarefas em intervalos que se cruzam
    cruzam = False
    ps = list(por_pid.values())
    for i in range(len(ps)):
        for j in range(i + 1, len(ps)):
            if ps[i] and ps[j] and min(ps[i]) < max(ps[j]) and min(ps[j]) < max(ps[i]):
                cruzam = True
    res = {
        "DATASET": "DOIS-ESCRITORES-ENSAIO-V1",
        "CODIGO": "com terminate antes de relancar" if hasattr(S, "WORKER_LOG") else "sem terminate (anterior)",
        "DRENADO": drenar,
        "PIDS_LANCADOS": pids,
        "MAX_WORKERS_VIVOS_AO_MESMO_TEMPO": max_vivos,
        "SEGUNDOS_COM_2_OU_MAIS_VIVOS": len(sobrepos) * 0.5,
        "TAREFAS_FECHADAS_POR_PID": {str(k): len(v) for k, v in por_pid.items()},
        "PIDS_A_FECHAR_TAREFAS_EM_INTERVALOS_QUE_SE_CRUZAM": cruzam,
        "LINHAS_POR_PID": {str(k): v for k, v in por_pid.items()},
        "TAREFAS_FECHADAS_MAIS_DE_UMA_VEZ": sorted({s for _, _, s in linhas if sum(1 for _, _, x in linhas if x == s) > 1}),
        "EVENTOS": evs,
        "AMOSTRAS": amostras,
    }
    nome = "DOIS-ESCRITORES-ENSAIO-%s.json" % ("DRENADO" if drenar else "PRODUCAO")
    (RAIZ / "curadoria" / nome).write_text(json.dumps(res, ensure_ascii=False, indent=1)
                                           + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in res.items() if k not in ("AMOSTRAS",)},
                     ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
