#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O CONTRATO ENTRE O SOURCE CURATOR E A COLLECTION — duas frases, e so.

    CURATOR ENTREGA:    READY_SOURCES
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

---------------------------------------------------------------------------
DE ONDE VEM A FICHA DE CADA FONTE (integracao 2026-09-20)

O que se sabe do CONTRATO (estrategia, rota, tipo de rota, territorio) vem de
`ESTADO-ACTUAL-DAS-FONTES-V1.json`, materializado do registo que a Collection
executa hoje (`regras/italy_contracts.mjs`). Nao vem do `italy_contracts_curator
.json`: esse e a fotografia do curator, e a fotografia ja disse uma vez que 50
fontes estavam bloqueadas por uma rota que a casa entretanto trocou.

O que se sabe do ESTADO vem do livro. So do livro.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))

import fila as F          # noqa: E402
import lifecycle as LC    # noqa: E402

CONTRATO = "CURATOR_COLLECTION_INTERFACE/v2"
ESTADO_ACTUAL = RAIZ / "curadoria" / "ESTADO-ACTUAL-DAS-FONTES-V1.json"
CARACT = RAIZ / "curadoria" / "SOURCE-CHARACTERIZATION-V1.json"
SNAPSHOT = RAIZ / "curadoria" / "READY-SOURCES-V1.json"


def _contratos() -> tuple[dict, str]:
    """{SOURCE_ID: ficha do registo actual}, e o HEAD de que o registo veio."""
    if not ESTADO_ACTUAL.exists():
        return {}, "NAO SEI"
    d = json.loads(ESTADO_ACTUAL.read_text(encoding="utf-8"))
    return {f["SOURCE_ID"]: f for f in d["FONTES"]}, d.get("HEAD", "NAO SEI")


def _cadencias() -> dict:
    """A cadencia vem da CARACTERIZACAO — o que a fonte realmente publica —,
    nunca de um numero unico inventado para todas."""
    if not CARACT.exists():
        return {}
    d = json.loads(CARACT.read_text(encoding="utf-8"))
    return {f.get("SOURCE_ID") or f.get("CANDIDATE_ID"): f for f in d["FONTES"]}


# ---------------------------------------------------------------------------
# O QUE A COLLECTION PODE PERGUNTAR (so leitura)
# ---------------------------------------------------------------------------
def estado_actual(source_id: str) -> str | None:
    """O estado de UMA fonte, relido do livro. None = o Curator nao a conhece.

        NAO CONHECER NAO E READY. E TAMBEM NAO E BLOQUEADA. E NAO SEI.
    """
    return LC.estado_de(source_id)


def esta_ready(source_id: str) -> bool:
    return LC.estado_de(source_id) == LC.READY_FOR_COLLECTION


def ready_ids() -> list[str]:
    return sorted(s for s, e in LC.snapshot().items() if e == LC.READY_FOR_COLLECTION)


def ready_sources() -> list[dict]:
    """«Quais fontes estao READY agora?» — derivado do livro no instante da
    chamada. Uma fonte degradada ha um segundo ja nao vem aqui."""
    est = LC.snapshot()
    contratos, head = _contratos()
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
            "CAPABILITY": c.get("ADAPTER_ID") or c.get("STRATEGY") or "NAO SEI",
            "CONTRACT_VERSION": "regras/italy_contracts.mjs@%s" % head if c else "NAO SEI",
            "ROUTE_VERSION": c.get("ROUTE_TYPE", "NAO SEI"),
            "ROUTE": c.get("ROUTE", "NAO SEI"),
            "STATUS": estado,
            "LAST_VALIDATED_AT": ult.get("OBSERVED_AT", "NAO SEI"),
            "LAST_SUCCESSFUL_CANARY_AT": ult.get("OBSERVED_AT", "NAO SEI"),
            "EVIDENCE_REF": ult.get("EVIDENCE_REF", "NAO SEI"),
            "CADENCE": ch.get("CADENCIA_INICIAL", "NAO SEI"),
            "HEALTH": "HEALTHY",
            "TERRITORY": c.get("TERRITORY", "NAO SEI"),
        })
    return out


# ---------------------------------------------------------------------------
# O QUE A COLLECTION PODE DIZER (uma frase)
# ---------------------------------------------------------------------------
def source_repair_needed(source_id: str, failure_type: str, *,
                         route: str = "", run_id: str = "",
                         evidence_ref: str = "", observed_at: str = "") -> dict:
    """O caminho inverso. A UNICA porta da Collection para este livro.

        A COLLECTION SINALIZA. NAO REPARA.

    Marca a fonte DEGRADED e poe REPAIR na fila do Curator. A Collection sai
    daqui e segue para a proxima fonte: reparar no meio da coleta e o que
    esta divisao existe para acabar.
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
    """O que um painel «IT — SOURCES STATUS LIVE» leria. Zeros visiveis."""
    m = LC.metricas()
    q = F.metricas()
    return {
        "SOURCES_TOTAL": m["SOURCES_TOTAL"],
        "READY": m[LC.READY_FOR_COLLECTION],
        "DISCOVERED": m[LC.DISCOVERED],
        "QUALIFYING": m[LC.QUALIFYING],
        "CONTRACT_PENDING": m[LC.CONTRACT_PENDING],
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
                 "uma fonte degradada sai daqui no mesmo instante. Este ficheiro "
                 "e um RECIBO do instante em que foi gerado — quem quer a lista "
                 "viva chama ready_sources()."),
         "GERADO_EM": LC.agora(),
         "READY_TOTAL": len(r),
         "READY_POR_TERRITORIO": _por(r, "TERRITORY"),
         "READY_POR_CAPACIDADE": _por(r, "CAPABILITY"),
         "METRICAS": metricas_operacionais(),
         "FONTES": r}
    SNAPSHOT.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("READY_SOURCES = %d" % len(r))
    print(json.dumps(metricas_operacionais(), ensure_ascii=False, indent=1))
    return 0


def _por(rows: list[dict], campo: str) -> dict:
    out: dict[str, int] = {}
    for r in rows:
        out[r[campo]] = out.get(r[campo], 0) + 1
    return dict(sorted(out.items()))


if __name__ == "__main__":
    raise SystemExit(main())
