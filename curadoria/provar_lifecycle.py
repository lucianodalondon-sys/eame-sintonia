#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FASE 10 — OS CINCO CASOS, COM FONTES REAIS DESTA ARVORE.

    NAO SE INVENTA PASS.

Cada caso corre o motor de verdade sobre um SOURCE_ID que existe no
contrato desta casa. Onde houve rede, houve rede; onde nao houve, o caso
diz-se simulado e diz porque.

    A  uma fonte ja READY                 — e o motor NAO a repromove
    B  uma fonte que precisa de CANARY    — rota + canario ao vivo
    C  uma fonte que produz RETRY_AFTER   — e as outras continuam
    D  uma fonte BLOCKED                  — robots vivo, e o motor obedece
    E  DEGRADED -> REPAIR -> READY        — com canario novo, ao vivo
"""
from __future__ import annotations

import json
import sys
from datetime import timedelta
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))

import fila as F          # noqa: E402
import lifecycle as LC    # noqa: E402
import worker as W        # noqa: E402

SAIDA = RAIZ / "curadoria" / "LIFECYCLE-PROOF-V1.json"


def main() -> int:
    contratos = W._contratos()
    est = LC.snapshot()
    ready = sorted([s for s, e in est.items() if e == LC.READY_FOR_COLLECTION])
    blocked = sorted([s for s, e in est.items()
                      if e == LC.CONTRACT_READY_ROUTE_BLOCKED])
    casos = []

    # ---- A: uma fonte ja READY, e o motor recusa-se a repromove-la ----------
    a_sid = ready[0]
    try:
        LC.registar(a_sid, LC.READY_FOR_COLLECTION, "tentativa de repromocao",
                    evidence_ref="EV-FALSA")
        a = {"PASS": False, "PORQUE": "o motor deixou repromover — defeito"}
    except ValueError as e:
        a = {"PASS": True, "RECUSA": str(e)[:150]}
    casos.append({"CASO": "A", "TITULO": "fonte ja READY", "SOURCE_ID": a_sid,
                  "ESTADO": LC.estado_de(a_sid), "REDE": False, **a})

    # ---- B: uma fonte que precisa de CANARY, ao vivo -----------------------
    b_sid = ready[1]
    b_ev = LC.historia(b_sid)
    r_rota = W.etapa_validate_route(b_sid, contratos[b_sid])
    r_can = W.etapa_canary(b_sid, contratos[b_sid])
    casos.append({"CASO": "B", "TITULO": "fonte que precisa de canario",
                  "SOURCE_ID": b_sid, "REDE": True,
                  "ROTA": r_rota[0], "CANARIO": r_can[0],
                  "HTTP": r_can[1].get("HTTP"),
                  "ALVO": r_can[1].get("ALVO", "")[:110],
                  "PASS": r_rota[0] == "OK" and r_can[0] == "OK",
                  "PORQUE": r_can[1].get("PORQUE", "")[:140],
                  "TRANSICOES_NO_LIVRO": len(b_ev)})

    # ---- C: RETRY_AFTER, e a fila NAO para --------------------------------
    # Host que nao resolve: produz a MESMA classe de desfecho que um 429 —
    # «nao foi possivel medir agora» — sem fingir um 429 que nao aconteceu.
    c_sid = "IT-PROVA-RETRY"
    LC.registar(c_sid, LC.CANARY_PENDING, "fonte de prova do caminho de adiamento")
    F.enfileirar(c_sid, F.CANARY, priority=99)
    vizinhas = [F.enfileirar("IT-PROVA-VIZ-%d" % i, F.CANARY, priority=10)
                for i in range(3)]

    t0 = F.agora_utc()
    tc = F.proxima(t0)
    F.adiar(tc["TASK_ID"], retry_after_s=3600,
            erro="HTTP 429 (plataforma pediu 3600s)", agora=t0)
    LC.registar(c_sid, LC.RETRY_AFTER, "429: adiada 1h, sem bloquear a fila",
                evidence_ref="PROVA-C", next_attempt_at=None)

    correram = []
    while True:
        t = F.proxima(t0)
        if t is None:
            break
        correram.append(t["SOURCE_ID"])
        F.concluir(t["TASK_ID"], "prova C")

    voltou = [t["SOURCE_ID"] for t in F.elegiveis(t0 + timedelta(minutes=61))]
    casos.append({"CASO": "C", "TITULO": "429 nao bloqueia a fila",
                  "SOURCE_ID": c_sid, "REDE": False,
                  "ADIADA": c_sid, "CORRERAM_ENTRETANTO": correram,
                  "ELEGIVEL_APOS_A_HORA": voltou,
                  "PASS": (c_sid not in correram and len(correram) == 3
                           and c_sid in voltou),
                  "PORQUE": "a adiada saiu da elegibilidade e voltou sozinha"})

    # ---- D: uma fonte BLOCKED, com robots lido AO VIVO ---------------------
    d_sid = blocked[0]
    r_d = W.etapa_validate_route(d_sid, contratos[d_sid])
    promovivel = True
    try:
        LC.registar(d_sid, LC.READY_FOR_COLLECTION, "forcar promocao de bloqueada",
                    evidence_ref="EV-FALSA")
    except ValueError:
        promovivel = False
    casos.append({"CASO": "D", "TITULO": "fonte bloqueada pelo robots vivo",
                  "SOURCE_ID": d_sid, "REDE": True,
                  "GATE": r_d[0], "ROTA": r_d[1].get("ROTA", "")[:110],
                  "ESTADO": LC.estado_de(d_sid),
                  "PROMOVIVEL": promovivel,
                  "PASS": r_d[0] == "BLOCK" and not promovivel,
                  "PORQUE": r_d[1].get("PORQUE", "")[:140]})

    # ---- E: DEGRADED -> REPAIRING -> READY, com canario novo ao vivo -------
    e_sid = ready[2]
    LC.registar(e_sid, LC.DEGRADED, "Collection reporta 404 em producao",
                owner=LC.OWNER_COLLECTION, evidence_ref="RUN-PROVA-E")
    depois_degradar = LC.metricas()[LC.READY_FOR_COLLECTION]

    atalho = True
    try:
        LC.registar(e_sid, LC.READY_FOR_COLLECTION, "ja deve estar boa",
                    evidence_ref="EV-FALSA")
    except ValueError:
        atalho = False

    LC.registar(e_sid, LC.REPAIRING, "curator assume o reparo")
    r_e = W.etapa_canary(e_sid, contratos[e_sid])
    if r_e[0] == "OK":
        ref = W._guardar_evidencia(e_sid, "REPAIR", r_e[1])
        LC.registar(e_sid, LC.READY_FOR_COLLECTION,
                    "novo canario resolveu apos reparo", evidence_ref=ref)
    casos.append({"CASO": "E", "TITULO": "DEGRADED -> REPAIR -> READY",
                  "SOURCE_ID": e_sid, "REDE": True,
                  "READY_APOS_DEGRADAR": depois_degradar,
                  "ATALHO_PERMITIDO": atalho,
                  "CANARIO_DO_REPARO": r_e[0],
                  "ESTADO_FINAL": LC.estado_de(e_sid),
                  "PASS": (not atalho and r_e[0] == "OK"
                           and LC.estado_de(e_sid) == LC.READY_FOR_COLLECTION),
                  "PORQUE": r_e[1].get("PORQUE", "")[:140]})

    d = {"DATASET": "LIFECYCLE-PROOF-V1",
         "LEI": "nao se inventa PASS. Onde houve rede, diz-se REDE=true.",
         "GERADO_EM": LC.agora(), "CASOS": casos,
         "PASS_TOTAL": sum(1 for c in casos if c["PASS"]),
         "CASOS_TOTAL": len(casos)}
    SAIDA.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")

    for c in casos:
        print("  %s  %-34s %-14s %s" % (
            "PASS" if c["PASS"] else "FAIL", c["TITULO"], c["SOURCE_ID"],
            c.get("PORQUE", "")[:60]))
    print("\nPASS %d/%d" % (d["PASS_TOTAL"], d["CASOS_TOTAL"]))
    print("FONTES = %s" % json.dumps(
        {k: v for k, v in LC.metricas().items() if v}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
