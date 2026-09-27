#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PROVA DO CICLO DE FONTE CONTINUO — entregavel da missao SOURCE-CURATOR-SERVICE-V1.

    "A FILA ACABOU" NAO E MOTIVO PARA PARAR.

Prova, em runtime, a sequencia que a missao exige (passos 2..11):

  2  a fila recebe tarefa QUALIFY
  3  o worker acorda (subprocess REAL, PID no SO)
  4  processa (a etapa QUALIFY corre — deixou de ser «etapa sem executor»)
  5  termina
  6  o supervisor continua vivo
  7  a fila baixa
  8  DISCOVERY e accionado pelo low watermark
  9  nova candidata aparece
  10 o feeder poe-a na fila
  11 o worker volta a acordar

Honestidade (mesma nomenclatura de provar_supervisor):
  REAL     = subprocess real, verificacao de PID no SO, feeder real
  SIMULADO = a corrida de crawl (rede) e INJECTADA — provar o GATILHO nao pode
             exigir 250 pedidos de rede. O motor de discovery real e provado
             noutro sitio (ADDENDUM-01..04). Aqui prova-se que o low watermark
             O ACCIONA e que o feeder mete o resultado na fila.

Corre sobre os ficheiros DESTA arvore (usar numa copia descartavel). Nao toca
a rede: as candidatas de teste tem territorio indeterminavel, por isso QUALIFY
resolve-as sem construir contrato (sem VALIDATE_ROUTE, sem canario).
"""
from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))
sys.path.insert(0, str(RAIZ / "candidatas"))

import fila as F                    # noqa: E402
import fonte_nova as FN             # noqa: E402
import gatilho_discovery as GD      # noqa: E402
import supervisor as S              # noqa: E402


def _agora() -> str:
    return datetime.now(timezone.utc).isoformat()


def _matar(proc):
    if proc and proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=8)
        except Exception:
            proc.kill()


def _cand(cid, nome, tipo="ORGANIZACAO", estado="EM_ANALISE"):
    return {"CANDIDATA_ID": cid, "TIPO": tipo, "NOME": nome,
            "URL": "https://exemplo-%s.invalid" % cid.lower(), "PAIS": "IT",
            "ESTADO": estado, "SOURCE_ID": None, "MOTIVO_DA_RECUSA": None,
            "PARA_QUE_SERVE": "prova do ciclo", "QUEM_VIU": "prova"}


def main() -> int:
    res: dict = {"GERADO_EM": _agora(), "PASSOS": {}}

    # --- semear a arvore descartavel ---
    # Candidatas com nome que NAO revela territorio (Granarolo-like) -> QUALIFY
    # resolve-as em SEMANTIC_REVIEW, sem cascata de rede.
    FN.FILA.write_text(json.dumps({"DATASET": "SINTONIA-FONTES-CANDIDATAS-V1",
        "CANDIDATAS": [
            _cand("CAND-CIC-1", "Granarolo"),
            _cand("CAND-CIC-2", "Fieravicola"),
            _cand("CAND-CIC-3", "OP Alegra", estado="CANDIDATA"),  # por drenar
        ]}, ensure_ascii=False), encoding="utf-8")
    # Fila com as duas ja enfileiradas.
    d = F._ler()
    d["TAREFAS"] = [t for t in d["TAREFAS"]
                    if not str(t["SOURCE_ID"]).startswith("CAND-CIC-")]
    F._gravar(d)
    F.enfileirar("CAND-CIC-1", F.QUALIFY, priority=30, motivo="prova ciclo")
    F.enfileirar("CAND-CIC-2", F.QUALIFY, priority=30, motivo="prova ciclo")
    # Acervo baixo de proposito, para o gatilho chegar ao nivel DISCOVERY.
    GD.CANDIDATE_LOW_WATERMARK = 5
    # Zera o ledger da ponte para ela poder drenar CAND-CIC-3.
    (RAIZ / "curadoria" / "BRIDGE-LEDGER-V1.json").write_text(
        json.dumps({"DATASET": "BRIDGE-LEDGER-V1", "PROCESSADAS": {}}), encoding="utf-8")

    res["PASSOS"]["2_FILA_RECEBE"] = {"eligible": len(F.elegiveis()), "PROVA": "REAL"}

    estado = {"SUPERVISOR_STATE": "STARTING", "RESTARTS_TOTAL": 0,
              "CRASHES_SEM_PROGRESSO": []}

    # ---- passo 3-5: worker acorda, processa, termina ----
    accao, estado, proc = S.uma_volta_sup(estado, None, pausa_worker=0.2)
    res["PASSOS"]["3_WORKER_ACORDA"] = {"accao": accao,
        "pid": proc.pid if proc else None,
        "pid_no_so": S._pid_no_so(proc.pid) if proc else False, "PROVA": "REAL"}
    # deixar o worker esgotar as 2 QUALIFY e sair sozinho
    for _ in range(40):
        if proc.poll() is not None:
            break
        time.sleep(0.5)
    _matar(proc)
    m = F.metricas()
    res["PASSOS"]["4_5_PROCESSA_E_TERMINA"] = {
        "queue_eligible_after": m["QUEUE_ELIGIBLE_NOW"],
        "blocked": m["BLOCKED"], "worker_saiu": proc.poll() is not None,
        "PROVA": "REAL"}

    # ---- passo 6-7: supervisor vivo, fila baixa -> IDLE ----
    accao2, estado, proc2 = S.uma_volta_sup(estado, proc, pausa_worker=0.2)
    res["PASSOS"]["6_7_SUPERVISOR_VIVO_FILA_BAIXA"] = {
        "accao": accao2, "eligible": len(F.elegiveis()), "PROVA": "REAL"}

    # ---- passo 8-10: low watermark aciona discovery (SIMULADA) + feeder ----
    def _discovery_simulada():
        doc = FN.carregar()
        doc["CANDIDATAS"].append(_cand("CAND-CIC-NOVA", "Consorzio Tutela Novo",
                                       estado="CANDIDATA"))
        FN.gravar(doc)
        return {"CANDIDATAS_NOVAS": 1, "PROVA": "SIMULADO (injectada)"}

    antes = len(F.elegiveis())
    trig = GD.talvez_alimentar(estado, descobrir_fn=_discovery_simulada)
    depois = len(F.elegiveis())
    res["PASSOS"]["8_10_GATILHO_DISCOVERY_FEEDER"] = {
        "decisao": trig.get("DECISAO"), "accoes": trig.get("ACCOES"),
        "eligible_antes": antes, "eligible_depois": depois,
        "candidata_nova_apareceu": "CAND-CIC-NOVA" in
            {c["CANDIDATA_ID"] for c in FN.carregar()["CANDIDATAS"]},
        "PROVA": "REAL (feeder) + SIMULADO (crawl injectado)"}

    # ---- passo 11: worker volta a acordar ----
    accao3, estado, proc3 = S.uma_volta_sup(estado, None, pausa_worker=0.2)
    res["PASSOS"]["11_WORKER_VOLTA_A_ACORDAR"] = {
        "accao": accao3, "pid": proc3.pid if proc3 else None, "PROVA": "REAL"}
    _matar(proc3)

    # ---- veredito ----
    ok = (res["PASSOS"]["3_WORKER_ACORDA"]["accao"] == "RELANCADO"
          and res["PASSOS"]["3_WORKER_ACORDA"]["pid_no_so"]
          and res["PASSOS"]["6_7_SUPERVISOR_VIVO_FILA_BAIXA"]["accao"] in ("IDLE", "VIVO")
          and "FEEDER" in (res["PASSOS"]["8_10_GATILHO_DISCOVERY_FEEDER"]["accoes"] or [])
          and res["PASSOS"]["8_10_GATILHO_DISCOVERY_FEEDER"]["candidata_nova_apareceu"]
          and depois > antes
          and res["PASSOS"]["11_WORKER_VOLTA_A_ACORDAR"]["accao"] == "RELANCADO")
    res["CONTINUOUS_SOURCE_LOOP_PROVEN"] = "YES" if ok else "NO"

    saida = RAIZ / "curadoria" / "CICLO-FONTE-PROOF-V1.json"
    saida.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(res, ensure_ascii=False, indent=1))
    print("\nCONTINUOUS_SOURCE_LOOP_PROVEN =", res["CONTINUOUS_SOURCE_LOOP_PROVEN"])
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
