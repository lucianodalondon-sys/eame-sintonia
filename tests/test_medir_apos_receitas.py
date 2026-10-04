"""LD1 — a medicao antes/depois das receitas conta o que diz que conta.

Paginas sinteticas; o formato do retrato_html e fingido (o detector nao e o que se
testa aqui — e a contagem, as fatias e a separacao da circularidade).
"""
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "scripts" / "detector_capa"))
_s = importlib.util.spec_from_file_location(
    "medir_apos_receitas", RAIZ / "scripts" / "detector_capa" / "medir_apos_receitas.py")
MR = importlib.util.module_from_spec(_s)
_s.loader.exec_module(MR)
MG = MR.MG


def _livro(fontes: dict) -> dict:
    return {"FONTES": [{"SOURCE_ID": s, "ACQUISITION": aq} for s, aq in fontes.items()]}


ANTES = {"IT-A": {"INDEX_URL": "https://a.it/", "LINK_PATTERN": r"^https://a\.it/news/.+"},
         "IT-B": {"INDEX_URL": "https://b.it/", "LINK_PATTERN": r"^https://b\.it/generico/.+"}}
DEPOIS = {"IT-A": ANTES["IT-A"],
          "IT-B": {"INDEX_URL": "https://b.it/", "LINK_PATTERN": r"^https://b\.it/articolo/.+"}}

PAGINAS = [  # (ID, fonte, url, veredito, formato fingido)
    (1, "IT-A", "https://a.it/", "CAPA", MG.MAT),              # indice com cara de materia
    (2, "IT-A", "https://a.it/contatti", "CAPA", MG.NS),       # NAO_SEI: atravessa, nao calada
    (3, "IT-A", "https://a.it/news/x", "MATERIA", MG.MAT),
    (4, "IT-B", "https://b.it/", "CAPA", MG.CAPA),
    (5, "IT-B", "https://b.it/articolo/y", "MATERIA", MG.MAT),  # so casa a receita NOVA
]


class TestMedirAposReceitas(unittest.TestCase):
    def setUp(self):
        self._td = tempfile.TemporaryDirectory(prefix="ld1-")
        t = Path(self._td.name)
        (t / "antes.json").write_text(json.dumps(_livro(ANTES)), encoding="utf-8")
        (t / "depois.json").write_text(json.dumps(_livro(DEPOIS)), encoding="utf-8")
        for i, *_ in PAGINAS:
            (t / ("p%d.html" % i)).write_bytes(b"x")
        (t / "gab.json").write_text(json.dumps({"PAGINAS": [
            {"ID": i, "SOURCE_ID": s, "URL": u, "VEREDITO": v, "FICHEIRO": "p%d.html" % i}
            for i, s, u, v, _ in PAGINAS]}), encoding="utf-8")
        self._orig = MG.RH.retrato_do_html
        ordem = iter(PAGINAS)

        def _fingido(b):
            return {"CAPA_OU_MATERIA": next(ordem)[4]}
        MG.RH.retrato_do_html = _fingido
        self.t = t
        self.r = MR.medir(t / "antes.json", t / "depois.json", t, gabarito=t / "gab.json")

    def tearDown(self):
        MG.RH.retrato_do_html = self._orig
        self._td.cleanup()

    def _j(self, fatia, juiz, quando):
        return self.r["FATIAS"][fatia]["JUIZES"][juiz][quando]

    def test_a_fonte_com_receita_mudada_vai_para_a_fatia_circular(self):
        self.assertEqual(self.r["FONTES_COM_RECEITA_MUDADA"], ["IT-B"])
        self.assertEqual(self.r["FATIAS"]["AFETADAS_CIRCULAR"]["CAPAS"], 1)
        self.assertEqual(self.r["FATIAS"]["AFETADAS_CIRCULAR"]["MATERIAS"], 1)
        self.assertEqual(self.r["FATIAS"]["NAO_AFETADAS"]["CAPAS"], 2)

    def test_nao_sei_atravessa_o_portao_mas_nao_e_calada(self):
        x = self._j("TODAS", "ACTUAL", "ANTES_RECEITAS")
        self.assertEqual(x["FALSE_LISTING_AS_ARTICLE"], "2/3")   # #1 MAT e #2 NAO_SEI
        self.assertEqual(x["CAPA_CALADA_COMO_MATERIA"], "1/3")   # so o #1
        self.assertEqual(x["IDS"]["ATRAVESSA"], [1, 2])

    def test_receita_corrigida_deixa_de_barrar_a_materia(self):
        antes = self._j("TODAS", "SO_MORADA", "ANTES_RECEITAS")
        depois = self._j("TODAS", "SO_MORADA", "DEPOIS_RECEITAS")
        self.assertEqual(antes["FALSE_ARTICLE_AS_LISTING"], "1/2")   # #5 nao casa o generico
        self.assertEqual(depois["FALSE_ARTICLE_AS_LISTING"], "0/2")

    def test_o_actual_nao_depende_da_receita(self):
        self.assertEqual(self._j("TODAS", "ACTUAL", "ANTES_RECEITAS"),
                         self._j("TODAS", "ACTUAL", "DEPOIS_RECEITAS"))

    def test_usa_os_juizes_da_6prepc_sem_os_reescrever(self):
        self.assertTrue(set(MR.JUIZES) <= set(MG.JUIZES))
        self.assertFalse(any(hasattr(MR, j.lower()) for j in MR.JUIZES))


if __name__ == "__main__":
    unittest.main()
