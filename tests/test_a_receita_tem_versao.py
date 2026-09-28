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
from coleta import texto_fonte  # noqa: E402
from guarda.preservar_derivado import hash_dos_parametros  # noqa: E402

VAZIA = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

#: (producer, versão) -> hash da receita. SÓ SE ACRESCENTA.
RECEITAS_POR_VERSAO = {
    # "1" nomeou DUAS receitas (vazia até 20/09; a de TEXT_OWNER desde 21/09):
    # é o defeito que este teste passa a impedir. Fica registada a primeira.
    ("texto-de-html", "1"): VAZIA,
    ("texto-de-html", "2"): "477d63427363",       # prefixo: medido no derivado 1060
    # DERIVACAO-ESTRUTURA (28/09): `limpar()` passa a dar `\n` nas etiquetas de
    # bloco, e a REGUA (nome + impressao da sonda) entra na receita. Hash inteiro.
    ("texto-de-html", "3"): "b467ba0da5ee4754c8da839b48d1b162749819ebf369563f00d731001697ce06",
    # DERIVACAO-ESTRUTURA-V2 (28/09): `limpar/3` — uma passagem, etiqueta nenhuma
    # atravessa outro «<» (o «</» orfao do balsamico engolia titulo e subtitulo).
    ("texto-de-html", "4"): "bb811cae3e7cf42991338477ce97679c22a0736662e526cf65ad0414c21ab48a",
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

    def test_a_regua_de_extracao_esta_na_receita(self):
        # A receita diz QUEM extrai (TEXT_OWNER) e COMO (TEXT_RULE + impressao da sonda).
        r = html.receita()
        self.assertEqual(r["TEXT_RULE"], texto_fonte.REGUA)
        self.assertEqual(r["TEXT_RULE_PROBE_SHA256"], texto_fonte.impressao_da_regua())

    def test_mudar_limpar_sem_subir_a_versao_reprova(self):
        # Mutacao em memoria: a `limpar()` antiga (achatava tudo numa linha) no lugar da
        # atual. A versao nao sobe, e a receita registada para ela tem de deixar de bater.
        original = texto_fonte.limpar

        def achatada(dados, ctype=""):
            import html as _h
            import re as _re
            t = dados.decode("utf-8", errors="replace")
            t = _re.sub(r"<(script|style)\b.*?</\1>", " ", t, flags=_re.S | _re.I)
            t = _re.sub(r"<[^>]+>", " ", t)
            t = _h.unescape(t)
            t = _re.sub(r"[ \t\xa0]+", " ", t)
            t = _re.sub(r"\n\s*\n+", "\n", t)
            return "\n".join(l.strip() for l in t.split("\n") if l.strip())

        try:
            texto_fonte.limpar = achatada
            h = hash_dos_parametros(html.receita())
        finally:
            texto_fonte.limpar = original
        self.assertFalse(h.startswith(RECEITAS_POR_VERSAO[(html.EXECUTOR_ID, html.EXECUTOR_VERSION)]),
                         "a regua mudou e a receita nao: o derivado achatado e o estruturado "
                         "teriam a mesma identidade")
        self.assertNotEqual(h, hash_dos_parametros(html.receita()))

    def test_voltar_a_limpar_de_duas_passagens_sem_subir_a_versao_reprova(self):
        # Mutacao em memoria: a `limpar/2` (bloco numa passagem, o resto noutra — a do
        # «</» orfao que engolia o titulo) no lugar da atual, com a versao "4".
        original = texto_fonte.limpar

        def duas_passagens(dados, ctype=""):
            import html as _h
            import re as _re
            t = dados.decode("utf-8", errors="replace")
            t = _re.sub(r"<(script|style)\b.*?</\1>", " ", t, flags=_re.S | _re.I)
            t = _re.sub(r"</?(?:%s)\b[^>]*>" % "|".join(texto_fonte.BLOCOS), "\n", t, flags=_re.I)
            t = _re.sub(r"<[^>]+>", " ", t)
            t = _h.unescape(t)
            t = _re.sub(r"[ \t\xa0]+", " ", t)
            t = _re.sub(r"\n\s*\n+", "\n", t)
            return "\n".join(l.strip() for l in t.split("\n") if l.strip())

        try:
            texto_fonte.limpar = duas_passagens
            h = hash_dos_parametros(html.receita())
        finally:
            texto_fonte.limpar = original
        self.assertFalse(h.startswith(RECEITAS_POR_VERSAO[(html.EXECUTOR_ID, html.EXECUTOR_VERSION)]),
                         "a sonda nao distingue a regua 2 da 3: o caso do «</» orfao saiu dela")

    def test_o_registo_cobre_os_dois_extratores_de_texto(self):
        self.assertEqual(set(ext.registo()), {html.EXECUTOR_ID, pdf.EXECUTOR_ID})


if __name__ == "__main__":
    unittest.main(verbosity=2)
