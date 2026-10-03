# -*- coding: utf-8 -*-
"""O seletor do gabarito escolhe o ARTIGO, nunca a folha de estilo (2026-09-23)."""
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "medidas"))
import gabarito_t2_t12 as G  # noqa: E402

BASE = "https://www.arpa.exemplo.it/"


class Seletor(unittest.TestCase):
    def test_link_de_css_com_numero_nao_e_item(self):
        html = (b'<link rel="stylesheet" href="/css/banner.css?ver=1789127872">'
                b'<a href="/notizie/allerta-meteo-pioggia-forte-2026">x</a>')
        self.assertEqual(BASE + "notizie/allerta-meteo-pioggia-forte-2026",
                         G.primeiro_item(html, BASE))

    def test_icone_dentro_de_a_nao_e_item(self):
        html = b'<a href="/img/apple-icon-180x180.png">i</a><a href="/news/1234">n</a>'
        self.assertEqual(BASE + "news/1234", G.primeiro_item(html, BASE))

    def test_navegacao_e_outro_anfitriao_ficam_fora(self):
        html = (b'<a href="/privacy-policy-del-sito">p</a>'
                b'<a href="https://outro.it/uma-noticia-longa-aqui">o</a>')
        self.assertIsNone(G.primeiro_item(html, BASE))


if __name__ == "__main__":
    unittest.main()
