#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera a fixture SINTETICA do pote v2.1 (D125) que o casco le em tests/test_pote_v21_no_casco.mjs.

    python3 provas/potes_um_cartao/gerar_fixture_v21.py

Corrida A (2 provas no cruzamento OLIVO x mosca) e publicada; corrida B traz 1 documento novo (SINT-DOC-D)
que toca 3 potes (portfolio, meeting, windows). O pote B aponta A como ANTERIOR (RUN_ID + SHA256).
Os mesmos construtores de tests/test_pote_v21.py — a fixture e o teste nao divergem.
⚠️ DADO SINTETICO DECLARADO: todo id comeca por SINT- (ou e XQ-/SG2- de uma chave SINT).
"""
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401
import pote_intelligence_casco as P  # noqa: E402
from tests.test_pote_v21 import corrida, prova, publicar  # noqa: E402

FX = os.path.join(RAIZ, "tests", "fixtures", "pote")


def gerar():
    a = P.adaptar_v21(corrida("SINT-IR-A", [prova(1), prova(2)]))
    ant, sha = publicar(a)
    b = P.adaptar_v21(corrida("SINT-IR-B", [prova(1), prova(2), prova("D")]), ant, sha,
                      {"SINT-NAO-EXISTE-MAIS": "SINT: exemplo de causa"})
    return a, b


def main():
    a, b = gerar()
    for nome, p in (("POTE-SINTETICO-V21-A.json", a), ("POTE-SINTETICO-V21.json", b)):
        with open(os.path.join(FX, nome), "w", encoding="utf-8") as f:
            json.dump(p, f, ensure_ascii=False, indent=1)
            f.write("\n")
    print("A", a["CONTAGEM_DE_CARTOES"], "B", b["DELTA_CONTAGEM"], "->", FX)
    return 0


if __name__ == "__main__":
    sys.exit(main())
