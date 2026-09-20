#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A PROVA POR ETAPA — o ficheiro para onde o EVIDENCE_REF do livro aponta.

    O LIVRO GUARDA A TRANSICAO. A PROVA FICA AQUI. O LIVRO NAO ENGORDA.

Um so escritor para o worker e para o resemeador: dois escritores do mesmo
ficheiro com formatos ligeiramente diferentes e a forma mais barata de perder
uma prova sem ninguem dar por isso.
"""
from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
EVIDENCIA = RAIZ / "curadoria" / "LIFECYCLE-EVIDENCE-V1.json"

CONTRATO = "SOURCE_CURATOR_EVIDENCE/v1"


def agora() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ler() -> dict:
    if EVIDENCIA.exists():
        return json.loads(EVIDENCIA.read_text(encoding="utf-8"))
    return {"DATASET": "LIFECYCLE-EVIDENCE-V1", "CONTRATO": CONTRATO,
            "LEI": "prova por etapa. EVIDENCE_REF do livro aponta para aqui.",
            "PROVAS": []}


def _gravar(d: dict) -> None:
    """Escrita atomica, como a do livro: um worker morto a meio nao deixa a
    prova truncada."""
    EVIDENCIA.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(EVIDENCIA.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(d, fh, ensure_ascii=False, indent=1)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, EVIDENCIA)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def guardar(source_id: str, etapa: str, dados: dict) -> str:
    """Guarda a prova e devolve a referencia que o livro deve citar."""
    d = _ler()
    ref = "EV-%s-%s-%04d" % (source_id, etapa, len(d["PROVAS"]) + 1)
    d["PROVAS"].append({"EVIDENCE_REF": ref, "SOURCE_ID": source_id,
                        "ETAPA": etapa, "OBSERVED_AT": agora(), "DADOS": dados})
    _gravar(d)
    return ref


def por_ref(ref: str) -> dict | None:
    for p in _ler()["PROVAS"]:
        if p["EVIDENCE_REF"] == ref:
            return p
    return None


def de(source_id: str) -> list[dict]:
    return [p for p in _ler()["PROVAS"] if p["SOURCE_ID"] == source_id]
