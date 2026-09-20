#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ALIMENTAR A FILA — pôr na fila o trabalho que existe e ninguém pediu.

    O BOT NAO ESPERA QUE LUCIANO ESCOLHA FONTE POR FONTE.

Três origens de trabalho, por ordem de prioridade operacional:

    80  REPAIR      fonte degradada na Collection — a mais urgente
    60  CANARY      já tem contrato, falta provar a rota de hoje
    40  REVALIDATE  canário falhou antes; tentar outra vez
    30  BUILD_CONTRACT  tem SOURCE_ID e caracterização, falta contrato

⚠️ O QUE NAO SE ENFILEIRA:
as `RECONCILIATION_REQUIRED` não entram. O estado delas depende de um
adaptador que vive noutra árvore, e correr o canário daqui mediria uma
capacidade que esta branch não tem.

    PROVADO NOUTRA ARVORE != DISPONIVEL NESTA.

E as `PARADOS` (policy/auth/capability) também não: insistir no que a
política barra não é persistência, é contorno.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))

import fila as F          # noqa: E402
import lifecycle as LC    # noqa: E402

ALLOC = RAIZ / "curadoria" / "SOURCE-ID-ALLOCATION-V1.json"
CONTRATOS = RAIZ / "curadoria" / "italy_contracts_curator.json"
CARACT = RAIZ / "curadoria" / "SOURCE-CHARACTERIZATION-V1.json"


def main() -> int:
    est = LC.snapshot()
    contratos = {c["SOURCE_ID"] for c in
                 json.loads(CONTRATOS.read_text(encoding="utf-8"))["FONTES"]}
    posto = {"REPAIR": 0, "REVALIDATE": 0, "BUILD_CONTRACT": 0}

    # 1. Degradadas — o reparo vem primeiro.
    for sid, e in est.items():
        if e in (LC.DEGRADED, LC.REPAIRING):
            F.enfileirar(sid, F.REPAIR, priority=80,
                         motivo="degradada — reparar e canariar de novo")
            posto["REPAIR"] += 1

    # 2. Canário falhou antes: a fonte respondeu, o padrão é que não serviu.
    #    Não é recusa definitiva — merece nova tentativa contra o site de hoje.
    for sid, e in est.items():
        if e == LC.CONTRACTED_CANARY_FAILED and sid in contratos:
            F.enfileirar(sid, F.REVALIDATE, priority=40,
                         motivo="canario falhou antes — remedir contra o site de hoje")
            posto["REVALIDATE"] += 1

    # 3. Tem identidade e caracterização, falta o contrato.
    #
    # ⚠️ SÓ as que NÃO pedem capacidade nova. `SMALL_ADAPTATION_REQUIRED`
    # a começar por «SIM» é uma DECISÃO do dono, não um esquecimento: a
    # missão 04 deixou-as de fora porque o molde genérico nunca encontraria
    # os itens delas. Enfileirá-las aqui seria contornar essa decisão e
    # produzir contratos que falham sempre no canário.
    #
    #     SOURCE_GAP != CAPABILITY_GAP. Estas são CAPABILITY, e o dono é o
    #     SCRAP ENGINEER — entregam-se como fila, não se «resolvem» aqui.
    car = {}
    if CARACT.exists():
        car = {x.get("CANDIDATE_ID"): x for x in
               json.loads(CARACT.read_text(encoding="utf-8"))["FONTES"]}
    capability_gap = []

    if ALLOC.exists():
        for n in json.loads(ALLOC.read_text(encoding="utf-8"))["NOVAS"]:
            sid = n["SOURCE_ID"]
            if sid in contratos or sid in est:
                continue
            f = car.get(n.get("CANDIDATE_ID"), {})
            adapt = str(f.get("SMALL_ADAPTATION_REQUIRED", ""))
            if adapt and not adapt.startswith("NAO"):
                LC.registar(sid, LC.CAPABILITY_BLOCK,
                            "exige capacidade nova: %s — dono SCRAP ENGINEER"
                            % adapt[:80],
                            evidence_ref="CARACT:SOURCE-CHARACTERIZATION-V1.json")
                capability_gap.append({"SOURCE_ID": sid,
                                       "NOME": n.get("NOME", "")[:60],
                                       "TERRITORY": n.get("TERRITORY"),
                                       "MISSING_COMPONENT": adapt[:80],
                                       "OWNER": "SCRAP ENGINEER"})
                continue
            LC.registar(sid, LC.CONTRACT_PENDING,
                        "SOURCE_ID atribuido e fonte caracterizada; falta contrato",
                        evidence_ref="ALLOC:SOURCE-ID-ALLOCATION-V1.json")
            F.enfileirar(sid, F.BUILD_CONTRACT, priority=30,
                         motivo="tem identidade e caracterizacao, falta contrato")
            posto["BUILD_CONTRACT"] += 1

    if capability_gap:
        (RAIZ / "curadoria" / "SOURCE-CAPABILITY-GAPS-V1.json").write_text(
            json.dumps({"DATASET": "SOURCE-CAPABILITY-GAPS-V1",
                        "LEI": ("fonte boa, aquisicao impossivel com o que ha. "
                                "Nao e recusa da fonte nem trabalho do Curator."),
                        "GERADO_EM": LC.agora(),
                        "TOTAL": len(capability_gap),
                        "AGRUPADO_POR_COMPONENTE": {
                            k: sum(1 for g in capability_gap
                                   if g["MISSING_COMPONENT"] == k)
                            for k in {g["MISSING_COMPONENT"] for g in capability_gap}},
                        "FONTES": capability_gap},
                       ensure_ascii=False, indent=1), encoding="utf-8")

    print("ENFILEIRADO = %s" % json.dumps(posto, ensure_ascii=False))
    print("NAO_ENFILEIRADO:")
    print("  RECONCILIATION_REQUIRED = %d  (adaptador vive noutra arvore)"
          % sum(1 for e in est.values() if e == LC.RECONCILIATION_REQUIRED))
    print("  BLOQUEADAS por policy   = %d  (insistir seria contorno)"
          % sum(1 for e in est.values() if e in LC.PARADOS))
    print("\nFILA = %s" % json.dumps(F.metricas(), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
