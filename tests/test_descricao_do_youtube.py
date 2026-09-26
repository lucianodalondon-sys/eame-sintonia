#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ACERVO-PARA-SALA-2 — a descricao que o autor do video escreveu, lida da pagina guardada.

Medido no acervo (26/09): as 612 paginas `watch?v=` fora da Sala davam so titulo e rodape
(~250 caracteres), porque a descricao vive em `ytInitialPlayerResponse.videoDetails`, dentro
de um `<script>`, e `coleta/texto_fonte.limpar()` apaga os scripts. 495 das 612 traziam
descricao com 40+ caracteres.

O que estes testes exigem:
  1. a pagina de video da o texto de antes MAIS a descricao;
  2. uma pagina sem `videoDetails` da EXACTAMENTE o texto de antes;
  3. um `videoDetails` partido nao inventa descricao;
  4. a receita do derivado so muda quando a descricao entrou (senao seria
     DERIVATION_DRIFT nas paginas de video, e um derivado novo inutil em todas as outras).

A amostra e um EXCERTO REAL (o `<title>` e o objecto `videoDetails` da pagina guardada no
armazem). Quando a pagina inteira esta nesta maquina, le-se tambem e confere-se o sha256.
"""
from __future__ import annotations

import hashlib
import os
import re
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)

import _gavetas  # noqa: E402,F401
from coleta import executor_texto_de_html as ex  # noqa: E402
from coleta import texto_fonte as tf  # noqa: E402

AMOSTRA = os.path.join(RAIZ, "tests", "dados", "descricao-yt", "it-t7-015-raw201-videodetails.html")
ORIGINAL = os.path.join(os.path.expanduser("~"), "sintonia-sala-italia", "armazem", "XX", "it-t7-015",
                        "OBSERVATION", "cf60e168c2643cd7-u4178bccb10c88b8f-f-Up25Lyn9I")
ORIGINAL_SHA256 = "cf60e168c2643cd75ae6e17eaf2e001b6f37450ea4f6cb16d7412de4169f64c4"
COMECO = "Ado Abruzzo, “Areali delle quattro D.O. Abruzzo"


def _amostra():
    with open(AMOSTRA, "rb") as fh:
        return fh.read()


def _limpar_de_antes(dados):
    """A `limpar()` de antes desta missao, copiada AQUI so como testemunha do «nada muda»."""
    import html  # noqa: PLC0415
    t = dados.decode("utf-8", errors="replace")
    t = re.sub(r"<(script|style)\b.*?</\1>", " ", t, flags=re.S | re.I)
    t = re.sub(r"<[^>]+>", " ", t)
    t = html.unescape(t)
    t = re.sub(r"[ \t\xa0]+", " ", t)
    t = re.sub(r"\n\s*\n+", "\n", t)
    return "\n".join(l.strip() for l in t.split("\n") if l.strip())


class ADescricaoEntra(unittest.TestCase):
    def test_a_descricao_do_excerto_real(self):
        d = tf.descricao_do_youtube(_amostra())
        self.assertTrue(d.startswith(COMECO), d[:80])
        self.assertEqual(1009, len(d))

    def test_o_texto_leva_o_de_antes_e_a_descricao(self):
        b = _amostra()
        antes, agora = _limpar_de_antes(b), tf.limpar(b, "text/html")
        self.assertTrue(agora.startswith(antes), "o texto de antes tem de continuar a frente")
        self.assertIn(COMECO, agora)
        self.assertNotIn(COMECO, antes)

    def test_a_pagina_inteira_do_armazem(self):
        if not os.path.exists(ORIGINAL):
            self.skipTest("a pagina inteira nao esta nesta maquina (armazem fora do Git)")
        with open(ORIGINAL, "rb") as fh:
            b = fh.read()
        self.assertEqual(ORIGINAL_SHA256, hashlib.sha256(b).hexdigest())
        self.assertEqual(tf.descricao_do_youtube(b), tf.descricao_do_youtube(_amostra()))
        self.assertGreater(len(tf.limpar(b, "text/html")), len(_limpar_de_antes(b)) + 900)


class NadaMaisMuda(unittest.TestCase):
    PAGINA = ("<html><head><title>Notizia</title><script>var x = {\"a\": 1};</script></head>"
              "<body><p>Il consorzio &amp; la vendemmia 2026</p></body></html>").encode()

    def test_pagina_sem_video_da_o_texto_de_antes(self):
        self.assertEqual(_limpar_de_antes(self.PAGINA), tf.limpar(self.PAGINA, "text/html"))
        self.assertEqual("", tf.descricao_do_youtube(self.PAGINA))

    def test_videodetails_partido_nao_inventa(self):
        b = b'<html><script>{"videoDetails":{"shortDescription":"meia fra</script></html>'
        self.assertEqual("", tf.descricao_do_youtube(b))
        self.assertEqual(_limpar_de_antes(b), tf.limpar(b, "text/html"))

    def test_descricao_vazia_nao_conta(self):
        b = b'<html><script>{"videoDetails":{"videoId":"x","shortDescription":"   "}}</script></html>'
        self.assertEqual("", tf.descricao_do_youtube(b))


class AReceitaSoMudaOndeOTextoMudou(unittest.TestCase):
    def test_pagina_sem_video_mantem_a_receita_de_antes(self):
        self.assertEqual({"TEXT_KIND", "TEXT_RELATION", "TEXT_BASIS", "DERIVATION_METHOD", "TEXT_OWNER"},
                         set(ex.receita(NadaMaisMuda.PAGINA)))

    def test_pagina_de_video_declara_o_dono_da_descricao(self):
        r = ex.receita(_amostra())
        self.assertEqual("coleta/texto_fonte.py::descricao_do_youtube", r.get("VIDEO_DESCRIPTION_OWNER"))


if __name__ == "__main__":
    unittest.main()
