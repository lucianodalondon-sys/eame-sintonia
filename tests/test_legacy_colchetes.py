# -*- coding: utf-8 -*-
"""LEGACY-99 D · um link malformado («[») na pagina de entrada nao derruba o reparo.

Medido a 25/09 na IT-T12-019 (ersaf.lombardia.it): REPAIR_CONTRACT rebentava com
«ValueError: Invalid IPv6 URL» em reparar_contrato.familias (urlparse de um href).
Sem rede: a pagina e um literal.
"""
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))
import canario as CAN            # noqa: E402
import reparar_contrato as R     # noqa: E402

PAGINA = (b'<a href="https://www.x.it/news/uno-due-tre">a</a>'
          b'<a href="http://[bad/x">b</a>'
          b'<a href="https://www.x.it/news/quattro-cinque-sei">c</a>'
          b'<a href="https://www.x.it:porto/y">d</a>'
          b'<a href="/news/sette-otto-nove">e</a>')


class Colchetes(unittest.TestCase):
    def test_o_dono_dos_links_deixa_de_fora_o_que_nao_e_endereco(self):
        h = CAN.hrefs_da_entrada(PAGINA, "https://www.x.it/")
        self.assertNotIn("http://[bad/x", h)
        self.assertNotIn("https://www.x.it:porto/y", h)
        self.assertIn("https://www.x.it/news/uno-due-tre", h)
        self.assertIn("https://www.x.it/news/sette-otto-nove", h)

    def test_o_reparo_ja_nao_rebenta_e_acha_a_familia(self):
        h = CAN.hrefs_da_entrada(PAGINA, "https://www.x.it/")
        fams = R.familias(h, "https://www.x.it/")      # antes: ValueError: Invalid IPv6 URL
        self.assertIsInstance(fams, list)


if __name__ == "__main__":
    unittest.main()
