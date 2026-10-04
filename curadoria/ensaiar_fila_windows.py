#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ENSAIO: UM LOTE COM LEITORES AGRESSIVOS — supervisor e worker REAIS, numa COPIA.

    uso: py <COPIA>/curadoria/ensaiar_fila_windows.py --sou-uma-copia [--tarefas N]

Dois leitores da fila em PROCESSOS SEPARADOS, a cada 100 ms, durante todo o
lote: um «de fora» (Path.read_text, como um verificador) e um «da casa»
(fila._ler, como o painel). O supervisor corre como em producao (poll 1 s
aqui, para o ensaio caber em minutos) e lanca o ciclo_continuo real.

Sem rede: tarefas CANARY de fontes SEM contrato — o worker barra-as na hora,
e cada uma e uma escrita na fila (proxima + bloquear). Recusa-se num checkout.

Mede: tarefas fechadas, mortes do worker por RC, PermissionError no stdout do
worker, WORKER_PENDURADO_TERMINADO, maximo de workers vivos (pelos Popen do
proprio supervisor).
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))

LEITOR_DE_FORA = r'''
import sys, time
from pathlib import Path
p = Path(sys.argv[1]); n = e = 0; fim = time.time() + float(sys.argv[2])
while time.time() < fim:
    try: p.read_text(encoding="utf-8"); n += 1
    except Exception: e += 1
    time.sleep(0.1)
print("DE_FORA", n, e)
'''
LEITOR_DA_CASA = r'''
import sys, time
sys.path.insert(0, sys.argv[3])
import fila as F
n = e = 0; fim = time.time() + float(sys.argv[2])
while time.time() < fim:
    try: F._ler(); F.elegiveis(); n += 1
    except Exception: e += 1
    time.sleep(0.1)
print("DA_CASA", n, e)
'''


def main() -> int:
    if "--sou-uma-copia" not in sys.argv or (RAIZ / ".git").exists():
        print("recuso: corre so numa copia (tar), nunca num checkout")
        return 2
    n_tarefas = 150
    if "--tarefas" in sys.argv:
        n_tarefas = int(sys.argv[sys.argv.index("--tarefas") + 1])

    import fila as F
    import supervisor as S

    agora = datetime.now(timezone.utc).isoformat()
    F.FILA.write_text(json.dumps({"PROXIMO_ID": 60000 + n_tarefas, "TAREFAS": [
        {"TASK_ID": "T6%04d" % i, "SOURCE_ID": "IT-ENSAIO-SEM-CONTRATO-%03d" % i,
         "TASK_TYPE": F.CANARY, "PRIORITY": 60, "STATUS": F.PENDING, "ATTEMPTS": 0,
         "NEXT_ATTEMPT_AT": None, "LAST_ERROR": None, "MOTIVO": "ensaio",
         "CREATED_AT": agora, "UPDATED_AT": agora} for i in range(n_tarefas)]}),
        encoding="utf-8")
    S.DIARIO.write_text("", encoding="utf-8")
    S.PARAR.unlink(missing_ok=True)
    log_worker = getattr(S, "WORKER_LOG", None)
    if log_worker and log_worker.exists():
        log_worker.unlink()

    janela = 240
    leitores = [
        subprocess.Popen([sys.executable, "-c", LEITOR_DE_FORA, str(F.FILA), str(janela)],
                         stdout=subprocess.PIPE, text=True),
        subprocess.Popen([sys.executable, "-c", LEITOR_DA_CASA, str(F.FILA), str(janela),
                          str(RAIZ / "curadoria")], stdout=subprocess.PIPE, text=True),
    ]
    saidas_do_worker = []         # so no codigo antigo (PIPE): lido no fim

    estado = {"SUPERVISOR_STATE": "STARTING", "RESTARTS_TOTAL": 0,
              "CRASHES_SEM_PROGRESSO": [], "LAST_DISCOVERY_AT": agora}
    procs = []
    proc = None
    max_vivos = 0
    t0 = time.time()
    while time.time() - t0 < janela:
        a, estado, novo = S.uma_volta_sup(estado, proc, pausa_worker=0.05)
        if novo is not None and novo is not proc:
            procs.append(novo)
        proc = novo
        max_vivos = max(max_vivos, sum(1 for p in procs if p.poll() is None))
        fechadas = sum(1 for t in F._ler()["TAREFAS"] if t["STATUS"] != F.PENDING
                       and t["STATUS"] != F.IN_PROGRESS)
        if fechadas == n_tarefas and a == "IDLE":
            break
        time.sleep(1)
    dur = round(time.time() - t0)

    for p in procs:
        if p.poll() is None:
            p.kill()
            p.wait()
        if p.stdout:
            try:
                saidas_do_worker.append(p.stdout.read())
            except Exception:
                pass
    for l in leitores:
        l.kill()
    fila_fim = F._ler()["TAREFAS"]
    evs = [json.loads(l) for l in S.DIARIO.read_text(encoding="utf-8").splitlines()
           if l.strip()]
    stdout_worker = "".join(saidas_do_worker)
    if log_worker and log_worker.exists():
        stdout_worker += log_worker.read_text(encoding="utf-8", errors="replace")
    mortes = [e for e in evs if e.get("EVENTO") == "WORKER_MORTO"]
    res = {
        "DATASET": "FILA-WINDOWS-ENSAIO-V1",
        "CODIGO": "novo (fila com paciencia, pid tri-estado)"
                  if hasattr(F, "REPLACE_RETRIES") else "producao 5b8f400c",
        "TAREFAS": n_tarefas,
        "SEGUNDOS": dur,
        "LEITORES": "2 processos a cada 100 ms (read_text de fora + fila._ler da casa)",
        "FECHADAS": sum(1 for t in fila_fim if t["STATUS"] in (F.BLOCKED, F.DONE)),
        "IN_PROGRESS_NO_FIM": sum(1 for t in fila_fim if t["STATUS"] == F.IN_PROGRESS),
        "PENDING_NO_FIM": sum(1 for t in fila_fim if t["STATUS"] == F.PENDING),
        "WORKERS_LANCADOS": len(procs),
        "MAX_WORKERS_VIVOS": max_vivos,
        "MORTES_POR_RC": {str(k): sum(1 for m in mortes if m.get("RC") == k)
                          for k in sorted({m.get("RC") for m in mortes}, key=str)},
        "PERMISSION_ERROR_NO_STDOUT_DO_WORKER": stdout_worker.count("PermissionError"),
        "WORKER_PENDURADO_TERMINADO": sum(1 for e in evs
                                          if e.get("EVENTO") == "WORKER_PENDURADO_TERMINADO"),
        "EVENTOS": [e.get("EVENTO") for e in evs],
    }
    out = RAIZ / "curadoria" / "FILA-WINDOWS-ENSAIO-V1.json"
    out.write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in res.items() if k != "EVENTOS"}, ensure_ascii=False,
                     indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
