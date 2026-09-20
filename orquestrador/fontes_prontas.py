#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A PORTA POR ONDE A COLLECTION PERGUNTA «QUE FONTES ESTAO READY AGORA?»

    SOURCE CURATOR PREPARA. COLLECTION COLETA.

Este e o lado da COLLECTION do contrato `curadoria/interface_collection.py`.
Ele nao sabe o que e uma fila, um canario ou um gate de rota — sabe TRES
verbos, e so estes tres:

    ids_ready() / lista_ready()   quais fontes posso colher agora
    exigir_ready(source_id)       posso colher ESTA? (recusa pelo nome se nao)
    reportar_avaria(source_id)    esta quebrou na minha mao — reparem

O que ele NAO faz, e um teste tenta faze-lo fazer:

    NAO PROMOVE. NAO REPARA. NAO CONSTROI CONTRATO. NAO CANARIA.

---------------------------------------------------------------------------
NAO SEI NAO E READY — E TAMBEM NAO E BLOQUEIO

`exigir_ready` so recusa fonte que o Curator CONHECE e nao tem em READY. Uma
fonte que o Curator nunca viu (um SOURCE_ID de fixture, um pais que ainda nao
tem ciclo de vida) passa com `CONHECIDA=False`: transformar «nao sei» em
bloqueio por omissao e a outra forma de o fail-closed mentir. O orquestrador
diz no recibo qual dos dois aconteceu.
"""
from __future__ import annotations

import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401 — poe as gavetas do processo no caminho

import interface_collection as IC  # noqa: E402 — o contrato, do lado do Curator

CONTRATO = "COLLECTION_READY_SOURCES_DOOR/v1"


class FonteNaoReady(RuntimeError):
    """O Curator conhece a fonte e ela NAO esta READY_FOR_COLLECTION."""


def lista_ready(territorio: str | None = None) -> list[dict]:
    """A lista viva, derivada do livro do Curator no instante da chamada."""
    fontes = IC.ready_sources()
    if territorio:
        fontes = [f for f in fontes if f.get("TERRITORY") == territorio]
    return fontes


def ids_ready(territorio: str | None = None) -> list[str]:
    return [f["SOURCE_ID"] for f in lista_ready(territorio)]


def exigir_ready(source_id: str) -> dict:
    """Fail-closed para o que o Curator conhece; NAO SEI para o que nao conhece.

    Devolve {"CONHECIDA": bool, "ESTADO": str|None}. Levanta `FonteNaoReady`,
    com o estado pelo nome, quando a fonte e conhecida e nao esta READY.
    """
    estado = IC.estado_actual(source_id)
    if estado is None:
        return {"CONHECIDA": False, "ESTADO": None,
                "PORQUE": ("o SOURCE CURATOR nao conhece %s: NAO SEI nao e READY nem "
                           "bloqueio; a corrida segue pela regra que ja valia" % source_id)}
    if estado != IC.LC.READY_FOR_COLLECTION:
        raise FonteNaoReady(
            "FONTE_NAO_READY [%s]: o SOURCE CURATOR tem-na em %s; a COLLECTION so "
            "consome READY_FOR_COLLECTION. Quem a devolve a READY e o Curator, com "
            "canario novo — nao esta corrida." % (source_id, estado))
    return {"CONHECIDA": True, "ESTADO": estado}


def reportar_avaria(source_id: str, failure_type: str, *, run_id: str = "",
                    route: str = "", evidence_ref: str = "") -> dict:
    """SOURCE_REPAIR_NEEDED. A Collection sinaliza e SEGUE. Nao repara."""
    return IC.source_repair_needed(source_id, failure_type, run_id=run_id,
                                   route=route, evidence_ref=evidence_ref)


def plano_de_coleta(territorio: str | None = None) -> list[dict]:
    """O que um driver de coleta itera: uma linha por fonte READY, com o
    comando canonico ja composto. Nenhuma fonte fora de READY entra aqui."""
    out = []
    for f in lista_ready(territorio):
        t = f.get("TERRITORY", "NAO SEI")
        out.append({
            "SOURCE_ID": f["SOURCE_ID"], "TERRITORY": t,
            "CAPABILITY": f.get("CAPABILITY"), "ROUTE": f.get("ROUTE"),
            "EVIDENCE_REF": f.get("EVIDENCE_REF"),
            "FILTROS": {"pais": "IT", "fonte": f["SOURCE_ID"], "universo": t},
        })
    return out
