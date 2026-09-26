# -*- coding: utf-8 -*-
"""MEDIR CONTAGENS — o sinal precoce medido nos bytes: teto D38, robots, portao, login fora. Sem rede."""
import sys
import tempfile
import unittest
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import medir_contagens as MC   # noqa: E402

B = "https://fito.exemplo.it"
ALVO = {"ID": "LM-01", "SOURCE_ID": "IT-T3-999", "NOME": "SFR Exemplo", "URL": B + "/", "REGIAO": "Exemplo"}
CASA = ('<html><body><a href="/chi-siamo">Chi siamo</a><a href="/bollettini">Bollettini di difesa</a>'
        '<a href="/monitoraggio-catture-cimice-asiatica">Monitoraggio catture cimice asiatica</a>'
        '<a href="/dati/catture-2026.csv">Catture 2026 (CSV)</a><a href="/privacy">privacy</a></body></html>').encode()
TABELA = ("<html><body><article><h1>Monitoraggio cimice asiatica - settimana 12/09/2026</h1>"
          "<p>Pubblicato il 12/09/2026. Rete regionale di trappole a feromone su pero e melo.</p>"
          "<table><tr><th>Trappola</th><th>Catture</th></tr><tr><td>Ferrara 1</td><td>34</td></tr>"
          "<tr><td>Ferrara 2</td><td>12</td></tr><tr><td>Modena 1</td><td>7</td></tr></table>"
          "<p>Settimana precedente 05/09/2026: 21 catture; 29/08/2026: 9 catture.</p></article></body></html>").encode()
BOLL = ("<html><body><article><h1>Bollettino 03/09/2026</h1><p>Si consiglia di intervenire sulla vite "
        "contro la peronospora. " + "Testo del bollettino. " * 40 + "</p></article></body></html>").encode()
PAG = {B + "/robots.txt": (200, b"User-agent: *\nDisallow: /riservato/\n", ""),
       B + "/": (200, CASA, ""),
       B + "/monitoraggio-catture-cimice-asiatica": (200, TABELA, ""),
       B + "/bollettini": (200, BOLL, "")}


class Medir(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(self.enterContext(tempfile.TemporaryDirectory(prefix="contagens-")))
        self.pedidos = []

    def medir(self, pag):
        def buscar(u):
            self.pedidos.append(u)
            return pag.get(u, (404, b"", "HTTP 404"))
        return MC.medir(ALVO, buscar, lambda: {"EGRESS_GATE": "PASS"}, self.tmp, dormir=lambda s: None)

    def test_acha_a_tabela_de_capturas(self):
        r = self.medir(PAG)
        self.assertEqual("CONTAGEM_PUBLICA", r["VEREDITO"], r.get("PORQUE"))
        self.assertTrue(r["TABELA_EM"].endswith("/monitoraggio-catture-cimice-asiatica"))
        self.assertEqual("HTML (tabela)", r["FORMATO_DA_TABELA"])
        self.assertIn("cimice asiatica", r["PRAGAS"])
        self.assertIn("pero", r["CULTURAS"])
        self.assertEqual("csv", r["LINKS_DE_DADOS"][0]["EXT"])
        self.assertLessEqual(len(self.pedidos), MC.TETO)
        self.assertNotIn(B + "/dati/catture-2026.csv", self.pedidos, "ficheiro de dados: diz-se onde, nao se abre")

    def test_o_mais_forte_primeiro(self):
        self.medir(PAG)
        self.assertEqual(B + "/monitoraggio-catture-cimice-asiatica", self.pedidos[2])

    def test_so_boletim_nao_e_contagem(self):
        pag = dict(PAG)
        pag[B + "/"] = (200, b'<html><a href="/bollettini">Bollettini di difesa</a></html>', "")
        r = self.medir(pag)
        self.assertEqual("SO_BOLETIM", r["VEREDITO"])

    def test_so_ficheiro_diz_onde_esta(self):
        pag = dict(PAG)
        pag[B + "/"] = (200, b'<html><a href="/dati/catture-2026.csv">Catture 2026</a></html>', "")
        r = self.medir(pag)
        self.assertEqual("TABELA_EM_FICHEIRO", r["VEREDITO"])
        self.assertEqual("CSV", r["FORMATO_DA_TABELA"])

    def test_login_fica_fora(self):
        pag = dict(PAG)
        pag[B + "/monitoraggio-catture-cimice-asiatica"] = (
            200, b'<html><form><input type="password" name="pw"></form><p>Area riservata ai tecnici</p></html>', "")
        pag[B + "/"] = (200, b'<html><a href="/monitoraggio-catture-cimice-asiatica">Monitoraggio catture</a></html>', "")
        r = self.medir(pag)
        self.assertEqual("LOGIN", r["VEREDITO"])

    def test_contagem_sem_data_nao_conta(self):
        pag = dict(PAG)
        pag[B + "/monitoraggio-catture-cimice-asiatica"] = (
            200, b"<html><p>Trappola 1: 34 catture. Trappola 2: 12 catture.</p></html>", "")
        r = self.medir(pag)
        self.assertNotEqual("CONTAGEM_PUBLICA", r["VEREDITO"])

    def test_robots_cumprido(self):
        pag = dict(PAG)
        pag[B + "/robots.txt"] = (200, b"User-agent: *\nDisallow: /\n", "")
        r = self.medir(pag)
        self.assertEqual("NAO_SEI", r["VEREDITO"])
        self.assertEqual(1, len(self.pedidos))

    def test_sem_portao_zero_pedidos(self):
        r = MC.medir(ALVO, lambda u: self.fail("pediu"), lambda: {"EGRESS_GATE": "BLOCKED"}, self.tmp)
        self.assertEqual(0, r["PEDIDOS"])

    def test_frequencia_pela_mediana(self):
        self.assertIn("~7 dias", MC.frequencia(["2026-08-29", "2026-09-05", "2026-09-12", "2026-09-19"]))
        self.assertIn("NAO SEI", MC.frequencia(["2026-09-12"]))

    def test_percentagem_depois_da_palavra_e_login_do_menu(self):
        """Terre dell'Etruria (acervo IT-T3-005): «infestazione attiva prossima al 5 %» e um login no menu."""
        pag = ("<html><body><form><input type='password'></form><article><h1>Newsletter 06/09/2026</h1><p>I punti "
               "monitorati evidenziano un'infestazione attiva prossima al 5 %, valore per cui e opportuno un intervento "
               "larvicida contro la mosca dell'olivo. " + "Testo tecnico. " * 50 + "</p></article></body></html>").encode()
        r = MC.ler_pagina(pag, B + "/news")
        self.assertTrue(r["PCT_INFESTACAO"])
        self.assertFalse(r["LOGIN"])

    def test_pdf_diz_o_formato(self):
        self.assertEqual("PDF", MC.ler_pagina(b"%PDF-1.4 ...", B + "/x.pdf")["FORMATO"])


if __name__ == "__main__":
    unittest.main()
