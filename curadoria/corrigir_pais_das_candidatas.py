#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Corrige o PAIS das candidatas que o crawl registou como IT por omissao.

    py curadoria/corrigir_pais_das_candidatas.py              # so mede
    py curadoria/corrigir_pais_das_candidatas.py --aplicar    # mede e grava
    py curadoria/corrigir_pais_das_candidatas.py --fila COPIA.json   # outra fila

⚠️ O LUGAR NUNCA SE PRESUME. Ate 23/09, `descobrir.crawl_sementes` registava
toda candidata com PAIS=IT (FAO, INRAE, CropLife...). So essas sao revistas:
QUEM_VIU == "curadoria/crawl_sementes". O catalogo (`curadoria/descobrir.py`) e
outras portas declararam o pais a mao, e ficam como estao.

Cada candidata alterada guarda PAIS_ANTES e PAIS_PROVA, e a NOTA ganha o
mesmo registo: nada fica sem proveniencia. Aplicar com o bot parado — a fila
de candidatas e um livro do servico.
"""
from __future__ import annotations

import argparse
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))
sys.path.insert(0, str(RAIZ / "candidatas"))
import fonte_nova as FN          # noqa: E402
from descobrir import pais_pela_prova  # noqa: E402

PORTA_DO_CRAWL = "curadoria/crawl_sementes"


def corrigir(doc: dict) -> tuple[list[dict], Counter]:
    """Altera `doc` no sitio. Devolve (alteradas, contagem de transicoes)."""
    agora = datetime.now(timezone.utc).isoformat()
    alteradas, trans = [], Counter()
    for c in doc.get("CANDIDATAS", []):
        if c.get("QUEM_VIU") != PORTA_DO_CRAWL:
            continue
        novo, prova = pais_pela_prova(c.get("URL", ""))
        antes = c.get("PAIS")
        if novo == antes:
            trans["%s=%s" % (antes, novo)] += 1
            continue
        c["PAIS_ANTES"] = antes
        c["PAIS"] = novo
        c["PAIS_PROVA"] = prova
        c["NOTA"] = ("%s | PAIS %s->%s em %s: %s"
                     % (c.get("NOTA") or "", antes, novo, agora[:10], prova)).lstrip(" |")
        trans["%s->%s" % (antes, novo)] += 1
        alteradas.append(c)
    return alteradas, trans


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--aplicar", action="store_true")
    ap.add_argument("--fila", help="caminho de outra fila de candidatas (ex.: uma copia)")
    a = ap.parse_args(argv)
    if a.fila:
        FN.FILA = Path(a.fila)
    doc = FN.carregar()
    total = len(doc.get("CANDIDATAS", []))
    do_crawl = sum(1 for c in doc.get("CANDIDATAS", []) if c.get("QUEM_VIU") == PORTA_DO_CRAWL)
    alteradas, trans = corrigir(doc)
    print("CANDIDATAS %d · DO_CRAWL %d · ALTERADAS %d" % (total, do_crawl, len(alteradas)))
    for k, n in sorted(trans.items(), key=lambda x: -x[1]):
        print("  %-16s %d" % (k, n))
    sem_prova = [c["CANDIDATA_ID"] for c in alteradas if not c.get("PAIS_PROVA")]
    print("SEM_PROVENIENCIA %d" % len(sem_prova))
    if a.aplicar:
        FN.gravar(doc)
        print("GRAVADO: %s" % FN.FILA)
    else:
        print("so medido (use --aplicar para gravar)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
