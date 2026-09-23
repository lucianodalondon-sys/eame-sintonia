#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ENSAIO DO CICLO COMPLETO — supervisor e worker REAIS, numa COPIA da worktree.

    uso: py <COPIA>/curadoria/ensaiar_gatilho_ocioso.py --sou-uma-copia

⚠️ Corre so numa copia: substitui a fila por uma fila sintetica e o supervisor
lanca o ciclo_continuo verdadeiro, que escreve no diario, no status e no
ledger DA ARVORE ONDE ESTE FICHEIRO ESTA. Sem --sou-uma-copia recusa-se, e
recusa-se tambem se a arvore for um checkout git (a copia e feita com tar).

Sem rede: a unica tarefa e uma CANARY de uma fonte SEM contrato, que o worker
barra na hora («sem contrato nesta arvore»). A discovery fica em intervalo
(LAST_DISCOVERY_AT = agora); a fila sintetica nao tem FAILED para reviver.

Sequencia esperada (assertada):
    IDLE (gatilho corre: FEEDER)  ...  IDLE silencioso
    -> relogio vence -> RELANCADO -> VIVO... -> worker processa (BLOCK)
    -> WORKER_OCIOSO_SAIU (rc 0) -> WORKER_SAIU_LIMPO -> IDLE (gatilho corre)
    -> IDLE silencioso durante a janela de contagem
"""
from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))

RELOGIO_S = 20          # a tarefa adiada vence daqui a 20 s
POLL_S = 3              # voltas curtas na fase de trabalho
JANELA_IDLE_S = 180     # fase final: poll de producao (15 s), a contar eventos


def _iso(dt):
    return dt.isoformat()


def main() -> int:
    if "--sou-uma-copia" not in sys.argv or (RAIZ / ".git").exists():
        print("recuso: corre so numa copia (tar), nunca num checkout")
        return 2

    import fila as F
    import gatilho_discovery as GD
    import supervisor as S

    agora = datetime.now(timezone.utc)
    vence = agora + timedelta(seconds=RELOGIO_S)
    tarefas = [
        {"TASK_ID": "T90001", "SOURCE_ID": "IT-ENSAIO-DONE", "TASK_TYPE": F.CANARY,
         "PRIORITY": 60, "STATUS": F.DONE, "ATTEMPTS": 1, "NEXT_ATTEMPT_AT": None,
         "LAST_ERROR": None, "MOTIVO": "ensaio", "CREATED_AT": _iso(agora),
         "UPDATED_AT": _iso(agora)},
        {"TASK_ID": "T90002", "SOURCE_ID": "IT-ENSAIO-SEM-CONTRATO",
         "TASK_TYPE": F.CANARY, "PRIORITY": 60, "STATUS": F.WAITING_RETRY,
         "ATTEMPTS": 1, "NEXT_ATTEMPT_AT": _iso(vence), "LAST_ERROR": "ensaio",
         "MOTIVO": "ensaio", "CREATED_AT": _iso(agora), "UPDATED_AT": _iso(agora)},
    ]
    F.FILA.write_text(json.dumps({"PROXIMO_ID": 90003, "TAREFAS": tarefas}),
                      encoding="utf-8")
    S.DIARIO.write_text("", encoding="utf-8")
    S.PARAR.unlink(missing_ok=True)

    estado = {"SUPERVISOR_STATE": "STARTING", "RESTARTS_TOTAL": 0,
              "CRASHES_SEM_PROGRESSO": [],
              "LAST_DISCOVERY_AT": _iso(agora)}            # discovery em intervalo
    realim = []

    def _hook():
        m = GD.talvez_alimentar(estado)
        if m.get("ACCOES"):
            S._anotar({"EVENTO": "REALIMENTACAO", **m})
            realim.append(m["ACCOES"])

    accoes = []
    proc = None
    t_fim_trabalho = None
    deadline = time.time() + 240
    while time.time() < deadline:
        a, estado, proc = S.uma_volta_sup(estado, proc, pausa_worker=0.2,
                                          hook_fila_vazia=_hook)
        if not accoes or accoes[-1] != a:
            accoes.append(a)
        if a == "BLOQUEADO":
            break
        # trabalho feito e de volta a IDLE -> passa a fase de contagem
        if "RELANCADO" in accoes and a == "IDLE" and t_fim_trabalho is None:
            t_fim_trabalho = time.time()
            break
        time.sleep(POLL_S)

    # fase de contagem: o supervisor como em producao (poll 15 s), fila vazia
    linhas_antes = len(S.DIARIO.read_text(encoding="utf-8").splitlines())
    voltas_idle = 0
    t0 = time.time()
    while time.time() - t0 < JANELA_IDLE_S:
        a, estado, proc = S.uma_volta_sup(estado, proc, hook_fila_vazia=_hook)
        voltas_idle += 1
        if accoes[-1] != a:
            accoes.append(a)
        time.sleep(S.SUPERVISOR_POLL_S)
    dur = time.time() - t0
    evs = [json.loads(l) for l in S.DIARIO.read_text(encoding="utf-8").splitlines()
           if l.strip()]
    na_janela = evs[linhas_antes:]

    seq_eventos = [e["EVENTO"] for e in evs]
    fila_fim = {t["TASK_ID"]: (t["STATUS"], t.get("LAST_ERROR"))
                for t in F._ler()["TAREFAS"]}
    res = {
        "DATASET": "GATILHO-OCIOSO-ENSAIO-V1",
        "EXECUTADO_EM": _iso(agora),
        "ONDE": "copia (tar) da worktree gatilho-ocioso-v1 em TEMP; processos reais",
        "SEQUENCIA_ACCOES_SUPERVISOR": accoes,
        "SEQUENCIA_EVENTOS_DIARIO": seq_eventos,
        "REALIMENTACOES_ACCOES": realim,
        "FILA_NO_FIM": fila_fim,
        "CRASHES_SEM_PROGRESSO": estado.get("CRASHES_SEM_PROGRESSO"),
        "JANELA_IDLE": {"SEGUNDOS": round(dur), "VOLTAS_DO_SUPERVISOR": voltas_idle,
                        "EVENTOS_ESCRITOS": len(na_janela),
                        "EVENTOS_POR_HORA_EXTRAPOLADO": round(len(na_janela) * 3600 / dur, 1),
                        "FEEDER_NOOP_TOTAL": estado.get("FEEDER_NOOP_TOTAL")},
    }
    ok = {
        "IDLE_ANTES_DO_RELOGIO": accoes[:1] == ["IDLE"],
        "RELANCADO_QUANDO_VENCE": "RELANCADO" in accoes,
        "WORKER_PROCESSOU": fila_fim["T90002"][0] == F.BLOCKED,
        "WORKER_OCIOSO_SAIU": "WORKER_OCIOSO_SAIU" in seq_eventos,
        "SUPERVISOR_VIU_SAIDA_LIMPA": "WORKER_SAIU_LIMPO" in seq_eventos,
        "IDLE_DEPOIS": accoes[-1] == "IDLE",
        "GATILHO_CORREU_DEPOIS_DA_SAIDA": (
            seq_eventos.index("WORKER_SAIU_LIMPO") < len(seq_eventos) - 1
            and "REALIMENTACAO" in seq_eventos[seq_eventos.index("WORKER_SAIU_LIMPO"):]),
        "NAO_BLOQUEOU": "BLOQUEADO" not in accoes and not estado.get("CRASHES_SEM_PROGRESSO"),
        "SEM_ECO_NA_JANELA": len(na_janela) == 0,
    }
    res["ASSERCOES"] = ok
    res["PASS"] = all(ok.values())
    out = RAIZ / "curadoria" / "GATILHO-OCIOSO-ENSAIO-V1.json"
    out.write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(res, ensure_ascii=False, indent=1))
    return 0 if res["PASS"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
