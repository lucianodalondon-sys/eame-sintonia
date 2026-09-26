#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RECEITA NOVA = VERSÃO NOVA (DEDUP-PARA-INSTALAR, 26/09).

Medido na Sala real: dois derivados `texto-de-html` versão "1" com receitas
diferentes (sem parâmetros em 20/09; com `TEXT_OWNER` desde f0c6ea6f, 21/09). A
versão deixou de dizer qual derivação era — e a D79 compara «o mesmo extrator»
pela receita inteira.

Este teste guarda, para cada extrator de texto, o hash da receita POR VERSÃO. Se
alguém mudar a `receita()` sem subir `EXECUTOR_VERSION`, o hash desta versão deixa
de bater e o teste reprova. Subiu a versão? Acrescenta-se uma linha nova aqui —
as antigas ficam, porque a Sala guarda derivados de todas.
"""
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
for g in (str(RAIZ), str(RAIZ / "admissao")):
    if g not in sys.path:
        sys.path.insert(0, g)

import _gavetas  # noqa: E402,F401
from coleta import executor_texto_de_html as html  # noqa: E402
from coleta import executor_texto_de_pdf as pdf  # noqa: E402
from coleta import extratores_de_texto as ext  # noqa: E402
from guarda.preservar_derivado import hash_dos_parametros  # noqa: E402

VAZIA = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

#: (producer, versão) -> hash da receita. SÓ SE ACRESCENTA.
RECEITAS_POR_VERSAO = {
    # "1" nomeou DUAS receitas (vazia até 20/09; a de TEXT_OWNER desde 21/09):
    # é o defeito que este teste passa a impedir. Fica registada a primeira.
    ("texto-de-html", "1"): VAZIA,
    ("texto-de-html", "2"): "477d63427363",       # prefixo: medido no derivado 1060
    ("texto-de-pdf", "1"): VAZIA,
}


class AReceitaTemVersao(unittest.TestCase):

    def conferir(self, modulo):
        chave = (modulo.EXECUTOR_ID, modulo.EXECUTOR_VERSION)
        self.assertIn(chave, RECEITAS_POR_VERSAO,
                      "versao nova sem receita registada: acrescente %r" % (chave,))
        h = hash_dos_parametros(modulo.receita())
        self.assertTrue(h.startswith(RECEITAS_POR_VERSAO[chave]),
                        "%s mudou a receita (hash %s) sem subir EXECUTOR_VERSION=%r"
                        % (modulo.EXECUTOR_ID, h[:12], modulo.EXECUTOR_VERSION))

    def test_html(self):
        self.conferir(html)

    def test_pdf(self):
        self.conferir(pdf)

    def test_o_registo_devolve_a_versao_e_a_receita_do_executor(self):
        texto, versao, receita = ext.registo()["texto-de-html"](
            b"<html><body><p>Bollettino fitosanitario n. 1 della Regione Puglia.</p></body></html>",
            "text/html")
        self.assertEqual((versao, receita),
                         (html.EXECUTOR_VERSION, hash_dos_parametros(html.receita())))
        self.assertIn("Bollettino", texto or "")

    def test_o_registo_cobre_os_dois_extratores_de_texto(self):
        self.assertEqual(set(ext.registo()), {html.EXECUTOR_ID, pdf.EXECUTOR_ID})


if __name__ == "__main__":
    unittest.main(verbosity=2)
