#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O CONTRATO ENTRE O SOURCE CURATOR E A COLLECTION — duas funcoes, e so.

    CURATOR ENTREGA:  READY_SOURCES
    COLLECTION DEVOLVE: SOURCE_REPAIR_NEEDED

Nada mais atravessa esta fronteira. A Collection nao precisa de saber que
existe fila, canario, gate de rota ou caracterizacao — precisa de saber
QUAIS FONTES ESTAO PRONTAS AGORA e de ter onde dizer QUANDO UMA QUEBROU.

    ACOPLAR IMPLEMENTACOES E O QUE FAZ UMA MISSAO DE FONTES VIRAR
    UMA SEGUNDA COLLECTION.

---------------------------------------------------------------------------
PORQUE `ready_sources()` LE O LIVRO E NAO UM CAMPO

Um snapshot guardado envelhece em silencio: uma fonte marcada DEGRADED
continuaria a aparecer como READY ate alguem regenerar o ficheiro. Aqui o
READY e DERIVADO do livro a cada chamada — se a ultima transicao foi
DEGRADED, a fonte desaparece da lista no mesmo instante.

    READY E UMA CONSEQUENCIA, NUNCA UM CARIMBO.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))

import fila as F          # noqa: E402
import lifecycle as LC    # noqa: E402

CONTRATO = "CURATOR_COLLECTION_INTERFACE/v1"
CONTRATOS = RAIZ / "curadoria" / "italy_contracts_curator.json"
CARACT = RAIZ / "curadoria" / "SOURCE-CHARACTERIZATION-V1.json"
SNAPSHOT = RAIZ / "curadoria" / "READY-SOURCES-V1.json"


def _contratos() -> dict:
    d = json.loads(CONTRATOS.read_text(encoding="utf-8"))
    return {c["SOURCE_ID"]: c for c in d["FONTES"]}


def _cadencias() -> dict:
    """A cadencia vem da CARACTERIZACAO — o que a fonte realmente publica —,
    nunca de um numero unico inventado para todas (FASE 8)."""
    if not CARACT.exists():
        return {}
    d = json.loads(CARACT.read_text(encoding="utf-8"))
    return {f.get("SOURCE_ID") or f.get("CANDIDATE_ID"): f for f in d["FONTES"]}


def ready_sources() -> list[dict]:
    """FASE 6 — «quais fontes estao READY agora?».

    Derivado do livro no instante da chamada. Uma fonte degradada ha um
    segundo ja nao vem aqui.
    """
    est = LC.snapshot()
    contratos = _contratos()
    car = _cadencias()
    out = []
    for sid, estado in sorted(est.items()):
        if estado != LC.READY_FOR_COLLECTION:
            continue
        c = contratos.get(sid, {})
        h = [t for t in LC.historia(sid) if t["NEW_STATE"] == LC.READY_FOR_COLLECTION]
        ult = h[-1] if h else {}
        ch = car.get(sid, {})
        out.append({
            "SOURCE_ID": sid,
            "CAPABILITY": c.get("ACQUISITION", {}).get("STRATEGY", "NAO SEI"),
            "CONTRACT_VERSION": c.get("CONTRACT_HASH", "NAO SEI"),
            "ROUTE_VERSION": c.get("ACQUISITION", {}).get("ROUTE_TYPE", "NAO SEI"),
            "STATUS": estado,
            "LAST_VALIDATED_AT": ult.get("OBSERVED_AT", "NAO SEI"),
            "LAST_SUCCESSFUL_CANARY_AT": ult.get("OBSERVED_AT", "NAO SEI"),
            "EVIDENCE_REF": ult.get("EVIDENCE_REF", "NAO SEI"),
            "CADENCE": ch.get("CADENCIA_INICIAL", "NAO SEI"),
            "HEALTH": "HEALTHY",
            "TERRITORY": c.get("TERRITORY", "NAO SEI"),
        })
    return out


def source_repair_needed(source_id: str, failure_type: str, *,
                         route: str = "", run_id: str = "",
                         evidence_ref: str = "", observed_at: str = "") -> dict:
    """FASE 7 — o caminho inverso. A UNICA porta da Collection para este livro.

        A COLLECTION SINALIZA. NAO REPARA.

    Marca a fonte DEGRADED e poe REPAIR na fila do Curator. A Collection sai
    daqui e segue para a proxima fonte: reparar no meio da coleta e o que
    esta missao existe para acabar.
    """
    estado = LC.estado_de(source_id)
    if estado != LC.READY_FOR_COLLECTION:
        return {"ACEITE": False, "SOURCE_ID": source_id, "ESTADO": estado,
                "PORQUE": ("so se reporta quebra de fonte que estava READY; "
                           "esta esta em %s" % estado)}

    linha = LC.registar(
        source_id, LC.DEGRADED,
        "Collection reportou %s%s" % (failure_type, " em %s" % run_id if run_id else ""),
        owner=LC.OWNER_COLLECTION,
        evidence_ref=evidence_ref or run_id or "NAO SEI")

    t = F.enfileirar(source_id, F.REPAIR, priority=80,
                     motivo="degradada na Collection: %s" % failure_type)
    return {"ACEITE": True, "SOURCE_ID": source_id, "NOVO_ESTADO": LC.DEGRADED,
            "TASK_ID": t["TASK_ID"], "OBSERVED_AT": linha["OBSERVED_AT"],
            "FAILURE_TYPE": failure_type, "ROUTE": route, "RUN_ID": run_id}


def metricas_operacionais() -> dict:
    """FASE 13 — o que um painel «IT — SOURCES STATUS LIVE» leria."""
    m = LC.metricas()
    q = F.metricas()
    return {
        "SOURCES_TOTAL": m["SOURCES_TOTAL"],
        "READY": m[LC.READY_FOR_COLLECTION],
        "QUALIFYING": m[LC.QUALIFYING],
        "CANARY_PENDING": m[LC.CANARY_PENDING],
        "RETRY_AFTER": m[LC.RETRY_AFTER],
        "DEGRADED": m[LC.DEGRADED],
        "REPAIRING": m[LC.REPAIRING],
        "POLICY_BLOCK": m[LC.POLICY_BLOCK],
        "AUTH_BLOCK": m[LC.AUTH_BLOCK],
        "CAPABILITY_BLOCK": m[LC.CAPABILITY_BLOCK],
        "ROUTE_BLOCKED": m[LC.CONTRACT_READY_ROUTE_BLOCKED],
        "CANARY_FAILED": m[LC.CONTRACTED_CANARY_FAILED],
        "SEMANTIC_REVIEW": m[LC.SEMANTIC_REVIEW],
        "UNKNOWN": m[LC.UNKNOWN],
        "QUEUE_PENDING": q["QUEUE_PENDING"],
        "QUEUE_ELIGIBLE_NOW": q["QUEUE_ELIGIBLE_NOW"],
        "QUEUE_WAITING_RETRY": q["QUEUE_WAITING_RETRY"],
        "QUEUE_BLOCKED": q["BLOCKED"],
        "QUEUE_DONE": q["DONE"],
    }


def main() -> int:
    r = ready_sources()
    d = {"DATASET": "READY-SOURCES-V1", "CONTRATO": CONTRATO,
         "LEI": ("o que o Curator entrega a Collection. Derivado do livro; "
                 "uma fonte degradada sai daqui no mesmo instante."),
         "GERADO_EM": LC.agora(),
         "READY_TOTAL": len(r),
         "METRICAS": metricas_operacionais(),
         "FONTES": r}
    SNAPSHOT.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    print("READY_SOURCES = %d" % len(r))
    print(json.dumps(metricas_operacionais(), ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
