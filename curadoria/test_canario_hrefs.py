#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IA-CUR (24/09): o leitor do canario ve as ligacoes RELATIVAS sem barra.

Medido na Assomao: a listagem tem 44 noticias «news_open.php?EW_ID=N» (relativas, sem barra)
e o canario via 0 — a R1 dizia SEM_FAMILIA_DE_ITENS porque le pelo mesmo leitor."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "curadoria"))
import canario as C   # noqa: E402

PAGINA = ('<a href="news_open.php?EW_ID=15142">1</a><a href="news_open.php?EW_ID=15134&amp;l=it">2</a>'
          '<a href="/abs/">3</a><a href="//cdn.ex/y">4</a><a href="https://o.it/z#frag">5</a>'
          '<a href="mailto:a@b.it">6</a><a href="javascript:void(0)">7</a><a href="tel:+39">8</a>').encode()
INDEX = "https://www.assomao.it/it/news-aziende.php"


class OLeitorDoCanario(unittest.TestCase):

    def test_relativa_sem_barra_e_resolvida_contra_a_pagina(self):
        h = C.hrefs_da_entrada(PAGINA, INDEX)
        self.assertIn("https://www.assomao.it/it/news_open.php?EW_ID=15142", h)
        self.assertIn("https://www.assomao.it/it/news_open.php?EW_ID=15134&l=it", h)   # &amp; desfeito

    def test_o_que_ja_se_via_continua(self):
        h = C.hrefs_da_entrada(PAGINA, INDEX)
        self.assertIn("https://www.assomao.it/abs/", h)
        self.assertIn("https://cdn.ex/y", h)
        self.assertIn("https://o.it/z", h)                       # sem o fragmento

    def test_esquemas_que_nao_sao_pagina_ficam_fora(self):
        h = C.hrefs_da_entrada(PAGINA, INDEX)
        self.assertFalse([x for x in h if x.startswith(("mailto:", "javascript:", "tel:"))])
        self.assertEqual(len(h), 5)


if __name__ == "__main__":
    unittest.main()
