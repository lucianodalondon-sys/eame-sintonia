"""O guarda das receitas: padrao generico = defeito. Sem rede.

A proposta de LINK_PATTERN so vale se separar materia de capa. Um padrao que
case tudo («.*») separa nada — e o molde WordPress medido na 6-PREP-c e a forma
branda do mesmo defeito.
"""
import importlib.util
import json
import re
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
_s = importlib.util.spec_from_file_location("censo_e_proposta",
                                            RAIZ / "scripts" / "receitas" / "censo_e_proposta.py")
CP = importlib.util.module_from_spec(_s)
_s.loader.exec_module(CP)

IDX = "https://www.exemplo.it/news/"
LINKS = [IDX + f"artigo-numero-{i}-da-semana" for i in range(6)] + [
    "https://www.exemplo.it/contatti", "https://www.exemplo.it/chi-siamo",
    "https://www.exemplo.it/news/category/mercati"]


class TestGuardaRecusaGenerico(unittest.TestCase):

    def test_ponto_asterisco_e_recusado(self):
        self.assertIsNotNone(CP.e_generico(".*", IDX, LINKS, []))
        self.assertIsNotNone(CP.e_generico(r"^https?://(www\.)?exemplo\.it/.*$", IDX, LINKS, []))

    def test_padrao_que_casa_o_indice_e_recusado(self):
        self.assertIsNotNone(CP.e_generico(r"^https?://(www\.)?exemplo\.it/news/?.*$", IDX, LINKS, []))

    def test_padrao_que_casa_navegacao_e_recusado(self):
        self.assertIsNotNone(CP.e_generico(r"^https?://(www\.)?exemplo\.it/news/[a-z-]+(/[a-z-]+)?/?$",
                                           IDX, LINKS, []))

    def test_padrao_que_casa_capa_conhecida_e_recusado(self):
        self.assertIsNotNone(CP.e_generico(r"^https?://(www\.)?exemplo\.it/[a-z]+/?$", IDX, [],
                                           ["https://www.exemplo.it/eventi"]))

    def test_padrao_estreito_passa(self):
        self.assertIsNone(CP.e_generico(r"^https?://(www\.)?exemplo\.it/news/artigo(?:-[a-z0-9]+)+/?$",
                                        IDX, LINKS, []))

    def test_padrao_que_nao_compila_e_recusado(self):
        self.assertIsNotNone(CP.e_generico("([", IDX, LINKS, []))


class TestPadraoDerivado(unittest.TestCase):

    def test_seccao_constante_fica_literal_e_numero_nao(self):
        m = "https://site.it/news-e-eventi/2024/titolo-della-notizia-uno/"
        fam = ["https://site.it/news-e-eventi/2024/altra-notizia-del-giorno/"]
        rx = CP.padrao_de(CP.esqueleto(m), m, fam)
        self.assertIn(r"news\-e\-eventi", rx)          # seccao: literal
        self.assertNotIn("2024", rx)                    # numero: nunca literal
        self.assertTrue(re.match(rx, "https://site.it/news-e-eventi/2025/outra-coisa-nova/"))


class TestAPropostaPublicada(unittest.TestCase):
    """Cada padrao publicado em curadoria/PROPOSTA-RECEITAS-V1.json passa o
    guarda, casa as suas materias confirmadas e nenhuma capa."""

    def setUp(self):
        f = RAIZ / "curadoria" / "PROPOSTA-RECEITAS-V1.json"
        if not f.exists():
            self.skipTest("proposta ainda nao gerada")
        self.d = json.loads(f.read_text(encoding="utf-8"))

    def test_nenhuma_proposta_generica_e_todas_com_prova(self):
        n = 0
        for l in self.d["FONTES"]:
            for p in l["PROPOSTAS"]:
                if p["CAMPO"] != "ACQUISITION.LINK_PATTERN":
                    continue
                n += 1
                rx = re.compile(p["DEPOIS"])
                self.assertIsNone(CP.e_generico(p["DEPOIS"], l["INDEX_URL"], [], []), l["SOURCE_ID"])
                self.assertFalse(rx.match(".*"))
                for m in p["PROVA"]["MATERIAS_CONFIRMADAS"]:
                    self.assertTrue(rx.match(m), (l["SOURCE_ID"], m))
                self.assertTrue(p["PROVA"]["CAPAS_CASADAS_DEPOIS"].startswith("0/"), l["SOURCE_ID"])
        self.assertGreater(n, 0)

    def test_estado_e_proposta_nao_aplicada(self):
        self.assertIn("NAO APLICADA", self.d["ESTADO"])


if __name__ == "__main__":
    unittest.main()
