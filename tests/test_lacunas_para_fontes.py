# -*- coding: utf-8 -*-
"""LACUNAS-PARA-FONTES (D87) · propor e registar sem rede, sem inventar, sem duplicar, so numa copia da fila."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "ferramentas" / "lacunas"))
import lacunas_para_fontes as LP   # noqa: E402

FN = LP.FN


def fila_minima(pasta: Path, linhas: list) -> Path:
    f = pasta / "FONTES-CANDIDATAS.json"
    d = {"DATASET": "SINTONIA-FONTES-CANDIDATAS-V1", "LEI": "teste", "ESTADOS": {}, "CANDIDATAS": linhas}
    f.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    return f


def linha(i, url, tipo="YOUTUBE", estado="CANDIDATA"):
    return {"CANDIDATA_ID": "CAND-%04d" % i, "TIPO": tipo, "PAIS": "IT", "NOME": "x", "URL": url, "ESTADO": estado,
            "SOURCE_ID": None}


class Provas(unittest.TestCase):
    def test_prova_contem(self):
        self.assertTrue(LP.prova_contem("https://a.it/p?x=1&y=2", 'href="https://a.it/p?x=1&amp;y=2"'))
        self.assertTrue(LP.prova_contem("https://a.it/b/", "ver https://a.it/b ali"))
        self.assertFalse(LP.prova_contem("https://a.it/c", "https://a.it/b"))

    def test_a_mesma_conta_escrita_de_outra_forma(self):
        self.assertEqual(LP.handle("https://www.youtube.com/user/myfruitvideo"), LP.handle("https://www.youtube.com/@myfruitvideo"))
        self.assertNotEqual(LP.handle("https://www.youtube.com/channel/UCaaa"), LP.handle("https://www.youtube.com/channel/UCbbb"))
        self.assertEqual(LP.handle("https://it.linkedin.com/company/ismeaofficial"),
                         LP.handle("https://www.linkedin.com/company/ismeaofficial"))

    def test_filtros(self):
        self.assertTrue(LP.RUIDO.search("https://twitter.com/intent"))
        self.assertTrue(LP.RUIDO.search("https://www.facebook.com/profile.php"))
        self.assertFalse(LP.RUIDO.search("https://www.facebook.com/agronotizie"))
        self.assertTrue(LP.SEM_ROTA.search("https://x.com/Agrofarma_news"))
        self.assertTrue(LP.GERAL.search("https://www.instagram.com/regionetoscana"))
        self.assertTrue(LP.FORA_DO_FOCO.search("https://www.youtube.com/user/ParmigianoReggianoIT"))
        self.assertFalse(LP.FORA_DO_FOCO.search("CONAF — Consiglio Ordine Nazionale Dottori Agronomi e Forestali"))


class AsLacunas(unittest.TestCase):
    @unittest.skipUnless(LP.R2.exists(), "livros da Intelligence fora desta maquina")
    def test_cada_numero_confere_nos_livros(self):
        m = LP.medir_lacunas()
        for lid in LP.LACUNAS:
            for p in m[lid]["PROVA"]:
                self.assertTrue(p["CONFERE"], (lid, p))


class Propor(unittest.TestCase):
    """Sobre uma fila minima: o que ja existe e ponteiro, a outra grafia da mesma conta nao duplica,
    o fora do foco nao entra, e sem abrir os bytes um perfil do armazem nao se regista."""

    def setUp(self):
        self.d = tempfile.TemporaryDirectory()
        self.fila = fila_minima(Path(self.d.name), [
            linha(1, "https://www.youtube.com/user/myfruitvideo"),
            linha(2, "http://www.condifesafoggia.it/", "ORGANIZACAO")])
        self.doc = LP.propor(self.fila, bytes_=False)
        self.por = {p["URL"]: p for p in self.doc["PROPOSTAS"]}

    def tearDown(self):
        self.d.cleanup()

    def test_ja_na_fila_e_outra_forma(self):
        self.assertEqual("JA_NA_FILA", self.por["http://www.condifesafoggia.it/"]["ACAO"])
        self.assertEqual("JA_NA_FILA_OUTRA_FORMA", self.por["https://www.youtube.com/@myfruitvideo"]["ACAO"])

    def test_fora_do_foco(self):
        self.assertEqual("FORA_DO_FOCO", self.por["https://www.youtube.com/user/ParmigianoReggianoIT"]["ACAO"])

    def test_sem_abrir_os_bytes_o_perfil_do_armazem_nao_entra(self):
        soc = [p for p in self.doc["PROPOSTAS"] if p["ORIGEM"] == "SOCIAIS-NO-ARMAZEM"]
        self.assertTrue(soc)
        self.assertFalse([p for p in soc if p["ACAO"] == "REGISTAR"])

    def test_dos_ramos_a_prova_e_conferida_e_so_novas_entram(self):
        reg = [p for p in self.doc["PROPOSTAS"] if p["ACAO"] == "REGISTAR"]
        self.assertGreaterEqual(len(reg), 40)
        for p in reg:
            self.assertIs(p["PROVA_CONFERIDA"], True)
            self.assertIn(p["TIPO"], FN.TIPOS)
            self.assertTrue(p["PARA_QUE"].strip())
        self.assertIn("L2-REGIAO", self.por["https://www.condifesamodena.it/"]["LACUNAS"])

    def test_o_mesmo_endereco_so_uma_vez(self):
        urls = [FN.normalizar(p["URL"]) for p in self.doc["PROPOSTAS"]]
        self.assertEqual(len(urls), len(set(urls)))


class Registar(unittest.TestCase):
    def test_so_numa_copia_e_redes_de_organizacao_em_policy_block(self):
        self.assertEqual(2, LP.main(["x", "--registar", "--propostas=nada.json",
                                     "--fila=%s" % (RAIZ / "candidatas" / "FONTES-CANDIDATAS.json")]))
        with tempfile.TemporaryDirectory() as d:
            fila = fila_minima(Path(d), [linha(1, "https://a.it/")])
            props = {"PROPOSTAS": [
                {"ACAO": "REGISTAR", "TIPO": "LINKEDIN", "PAIS": "IT", "NOME": "Org — pagina LinkedIn",
                 "URL": "https://www.linkedin.com/company/org-x", "PARA_QUE": "Voci dal Campo", "LACUNAS": ["L5-PESSOA-CAMPO"],
                 "NOTA": "PROVA_IDENTIDADE=https://org-x.it/ (pagina oficial)", "PROVA_IDENTIDADE": "https://org-x.it/",
                 "ORIGEM": "t"},
                {"ACAO": "REGISTAR", "TIPO": "ORGANIZACAO", "PAIS": "IT", "NOME": "Condifesa X", "URL": "https://cx.it/",
                 "PARA_QUE": "Finestre", "LACUNAS": ["L2-REGIAO"], "NOTA": "PAIS_PROVA=asnacodi", "PROVA_IDENTIDADE": "r",
                 "ORIGEM": "t"},
                {"ACAO": "JA_NA_FILA", "TIPO": "ORGANIZACAO", "PAIS": "IT", "NOME": "a", "URL": "https://a.it/",
                 "PARA_QUE": "x", "LACUNAS": [], "NOTA": "", "PROVA_IDENTIDADE": "r", "ORIGEM": "t"}]}
            r = LP.registar(props, fila)
            self.assertEqual(["CAND-0002", "CAND-0003"], [x["CANDIDATA_ID"] for x in r])
            q = {c["CANDIDATA_ID"]: c for c in json.loads(fila.read_text(encoding="utf-8"))["CANDIDATAS"]}
            self.assertEqual("POLICY_BLOCK", q["CAND-0002"]["ESTADO"])
            self.assertTrue(q["CAND-0002"]["EVIDENCIA"].startswith("TERMOS https://"))
            self.assertEqual("CANDIDATA", q["CAND-0003"]["ESTADO"])
            self.assertIn("LACUNAS=L2-REGIAO", q["CAND-0003"]["NOTA"])
            self.assertEqual(3, len(q))


if __name__ == "__main__":
    unittest.main()
