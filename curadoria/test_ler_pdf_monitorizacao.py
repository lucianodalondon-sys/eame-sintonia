# -*- coding: utf-8 -*-
"""LER PDF DE MONITORIZACAO — todas as linhas com sinal, sem resumir; teto D38; robots; portao. Sem rede."""
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import ler_pdf_monitorizacao as L   # noqa: E402

TEXTO = """
                 ERSA - Servizio fitosanitario e chimico
        MONITORAGGIO Halyomorpha halys (cimice asiatica) - 18 agosto 2026

   Stazione / trappola          Comune             Catture sett. 33    Catture sett. 34
   Trappola 1                   Pradamano               12                 34
   Trappola 2                   Cormons                  3                  7

   Nella settimana si registrano 41 catture complessive; il volo degli adulti e in aumento.
   Olivo: infestazione attiva pari al 4 % delle drupe; la soglia di intervento e del 10%.
   Testo generico senza numeri.
   Via Sabbatini 5, 33050 Pozzuolo del Friuli
"""


class Linhas(unittest.TestCase):
    def setUp(self):
        self.l = L.linhas_com_sinal(TEXTO, cultura="pero")

    def test_tabela_da_armadilha_linha_a_linha(self):
        t = [x for x in self.l if "TABELA" in x["TIPOS"] and x["LINHA"].strip().startswith("Trappola 1")]
        self.assertEqual(1, len(t))
        self.assertEqual(["1", "12", "34"], t[0]["NUMEROS"])
        self.assertIn(t[0]["PRAGA"].lower(), {"cimice asiatica", "halyomorpha"})   # o mesmo insecto
        self.assertEqual("2026-08-18", t[0]["DATA"])
        self.assertEqual("documento", t[0]["DATA_DE_ONDE"])

    def test_nada_e_resumido(self):
        for x in self.l:
            self.assertIn(x["LINHA"], TEXTO)                  # a linha e a do texto, inteira

    def test_contagem_voo_percentagem_limiar(self):
        tipos = {t for x in self.l for t in x["TIPOS"]}
        self.assertTrue({"CONTAGEM", "VOO", "PERCENTAGEM", "LIMIAR", "TABELA"} <= tipos, tipos)

    def test_percentagem_sem_contexto_de_infestacao_nao_conta(self):
        ls = L.linhas_com_sinal("IVA agevolata al 10% sul prezzo del prodotto\nTasso di cambio 3,5% annuo\n")
        self.assertFalse([x for x in ls if "PERCENTAGEM" in x["TIPOS"]])

    def test_morada_nao_e_sinal(self):
        self.assertFalse([x for x in self.l if "Sabbatini" in x["LINHA"]])
        self.assertFalse([x for x in self.l if "senza numeri" in x["LINHA"]])


class Correr(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(self.enterContext(tempfile.TemporaryDirectory(prefix="pdfmon-")))
        self.pedidos = []

    def buscar(self, pag):
        def f(u):
            self.pedidos.append(u)
            return pag.get(u, (404, b"", "HTTP 404"))
        return f

    def correr(self, alvos, pag, portao="PASS"):
        return L.correr(alvos, self.buscar(pag), lambda: {"EGRESS_GATE": portao}, self.tmp, dormir=lambda s: None)

    def alvos(self, n, dom="https://ersa.exemplo.it"):
        return [{"ID": "P%02d" % i, "URL": "%s/b%d.pdf" % (dom, i), "CULTURA": "pero"} for i in range(n)]

    def test_teto_5_contando_o_robots(self):
        pag = {"https://ersa.exemplo.it/robots.txt": (404, b"", "")}
        r = self.correr(self.alvos(6), pag)
        self.assertEqual(5, len(self.pedidos))
        self.assertEqual(2, sum(1 for x in r if "teto" in x.get("PORQUE", "")))

    def test_robots_cumprido(self):
        pag = {"https://ersa.exemplo.it/robots.txt": (200, b"User-agent: *\nDisallow: /b1.pdf\n", "")}
        r = self.correr(self.alvos(2), pag)
        self.assertNotIn("https://ersa.exemplo.it/b1.pdf", self.pedidos)
        self.assertEqual("robots.txt proibe", r[1]["PORQUE"])

    def test_sem_portao_zero_pedidos(self):
        self.correr(self.alvos(2), {}, portao="BLOCKED")
        self.assertEqual([], self.pedidos)

    def test_html_no_lugar_do_pdf(self):
        pag = {"https://ersa.exemplo.it/robots.txt": (404, b"", ""),
               "https://ersa.exemplo.it/b0.pdf": (200, b"<html>login</html>", "")}
        r = self.correr(self.alvos(1), pag)
        self.assertEqual("NAO_E_PDF", r[0]["ESTADO"])

    def test_pdf_lido_guarda_texto_integral(self):
        pag = {"https://ersa.exemplo.it/robots.txt": (404, b"", ""),
               "https://ersa.exemplo.it/b0.pdf": (200, b"%PDF-1.4 falso", "")}
        r = L.ler(self.alvos(1)[0], self.buscar(pag), self.tmp, extrair=lambda p: TEXTO)
        self.assertEqual("LIDO", r["ESTADO"])
        self.assertEqual(TEXTO, Path(r["TEXTO_INTEGRAL_EM"]).read_text(encoding="utf-8"))
        self.assertGreaterEqual(r["POR_TIPO"]["TABELA"], 2)

    @unittest.skipUnless(shutil.which("pdftotext"), "pdftotext ausente")
    def test_pdftotext_real_falha_alto_com_lixo(self):
        p = self.tmp / "lixo.pdf"
        p.write_bytes(b"%PDF-1.4 nao e um pdf de verdade")
        with self.assertRaises(RuntimeError):
            L.texto_do_pdf(p)


if __name__ == "__main__":
    unittest.main()
