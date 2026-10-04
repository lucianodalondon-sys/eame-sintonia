"""S4 -- o PAIS da candidata vem da prova do endereco; nunca IT por omissao.

Ate 23/09, crawl_sementes registava toda candidata com PAIS=IT porque a tinha
visto num site italiano (FAO, INRAE, CropLife, Benaki...). O teste atravessa o
crawl verdadeiro com a rede simulada na fronteira: semente italiana, links para
fora de Italia, e confere o pais que chega a porta de registo.
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(AQUI.parent / "candidatas"))
import corrigir_pais_das_candidatas as CP   # noqa: E402
import descobrir as D                        # noqa: E402
import fonte_nova as FN                      # noqa: E402

SEMENTE = "https://www.coldiretti.it/"
LINKS = {
    "https://www.fao.org/home/en/": "NAO SEI",
    "https://www.inrae.fr/": "FR",
    "https://biostimulants.eu/": "EU",
    "https://en.bpi.gr/": "OUTRO",
    "https://www.regione.veneto.it/web/agricoltura-e-foreste": "IT",
}


class TestPaisNoCrawl(unittest.TestCase):

    def _crawl(self):
        registos = []

        def _registar(**kw):
            registos.append(kw)
            return {"CANDIDATA_ID": "CAND-%04d" % (9100 + len(registos))}

        html = "".join('<a href="%s">x</a>' % u for u in LINKS)
        with mock.patch.object(D, "_extrair_sementes_legitimas", return_value=[SEMENTE]), \
             mock.patch.object(D, "_sementes_de_segunda_geracao", return_value=[]), \
             mock.patch.object(D, "_permitido", return_value=True), \
             mock.patch.object(D, "_buscar_pagina_html", return_value=(html, 200, "text/html")), \
             mock.patch.object(D, "_verificar_url", return_value=(True, 200, "text/html")), \
             mock.patch.object(D, "_filtrar_link", return_value=(True, "teste")), \
             mock.patch.object(D, "_e_duplicado", return_value=(False, "")), \
             mock.patch.object(D, "_gravar_visitados", lambda *_a, **_k: None), \
             mock.patch.object(D, "registar", _registar):
            D.crawl_sementes(D.Orcamento(total=50), set(),
                             {"VISITADOS": {}, "REJEITADOS": {}}, [], max_sementes=1)
        return {r["url"]: r for r in registos}

    def test_link_visto_em_site_italiano_nao_herda_it(self):
        regs = self._crawl()
        self.assertEqual(set(regs), set(LINKS), "o crawl nao registou os links do teste")
        for url, esperado in LINKS.items():
            with self.subTest(url=url):
                self.assertEqual(regs[url]["pais"], esperado)

    def test_a_prova_do_pais_fica_na_nota(self):
        for url, r in self._crawl().items():
            with self.subTest(url=url):
                self.assertIn("PAIS_PROVA=", r["nota"])


class TestPaisPelaProva(unittest.TestCase):

    def test_dominio_generico_nao_prova_lugar(self):
        for u in ("https://croplife.org/", "https://www.fertilizerseurope.com/",
                  "https://www.youtube.com/@canale"):
            with self.subTest(u=u):
                self.assertEqual(D.pais_pela_prova(u)[0], "NAO SEI")

    def test_nao_sei_e_um_pais_aceite_pela_porta(self):
        self.assertIn("NAO SEI", FN.PAISES)


class TestCorrigirCandidatasAntigas(unittest.TestCase):

    def _doc(self):
        return {"CANDIDATAS": [
            {"CANDIDATA_ID": "CAND-1", "URL": "https://www.fao.org/", "PAIS": "IT",
             "QUEM_VIU": "curadoria/crawl_sementes", "NOTA": "n"},
            {"CANDIDATA_ID": "CAND-2", "URL": "https://www.arpae.it/", "PAIS": "IT",
             "QUEM_VIU": "curadoria/crawl_sementes", "NOTA": "n"},
            {"CANDIDATA_ID": "CAND-3", "URL": "https://www.fao.org/", "PAIS": "IT",
             "QUEM_VIU": "curadoria/descobrir.py", "NOTA": "catalogo declarado"},
        ]}

    def test_so_o_crawl_e_corrigido_e_com_proveniencia(self):
        doc = self._doc()
        alteradas, _ = CP.corrigir(doc)
        por = {c["CANDIDATA_ID"]: c for c in doc["CANDIDATAS"]}
        self.assertEqual([c["CANDIDATA_ID"] for c in alteradas], ["CAND-1"])
        self.assertEqual(por["CAND-1"]["PAIS"], "NAO SEI")
        self.assertEqual(por["CAND-1"]["PAIS_ANTES"], "IT")
        self.assertTrue(por["CAND-1"]["PAIS_PROVA"])
        self.assertIn("PAIS IT->NAO SEI", por["CAND-1"]["NOTA"])
        self.assertEqual(por["CAND-2"]["PAIS"], "IT")          # .it prova IT
        self.assertEqual(por["CAND-3"]["PAIS"], "IT")          # catalogo: declarado a mao

    def test_segunda_corrida_nao_muda_nada(self):
        doc = self._doc()
        CP.corrigir(doc)
        alteradas, _ = CP.corrigir(doc)
        self.assertEqual(alteradas, [])

    def test_medir_nao_grava(self):
        tmp = Path(tempfile.mkdtemp(prefix="pais-")) / "fila.json"
        tmp.write_text(json.dumps(self._doc()), encoding="utf-8")
        antes = tmp.read_bytes()
        orig = FN.FILA
        try:
            CP.main(["--fila", str(tmp)])
        finally:
            FN.FILA = orig
        self.assertEqual(tmp.read_bytes(), antes)


if __name__ == "__main__":
    unittest.main(verbosity=2)
