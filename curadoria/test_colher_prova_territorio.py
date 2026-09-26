# -*- coding: utf-8 -*-
"""MICRO-PROVA — o leitor de prova de território: teto D38, robots cumprido, portão IT, casca JS não conta duas vezes,
e o --aplicar só escreve no canal o que o próprio canal aceita. Sem rede."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import colher_prova_territorio as C   # noqa: E402
import decisao_semantica as DS        # noqa: E402

B = "https://www.agraria.exemplo.it"
FICHA = {"CANDIDATA_ID": "CAND-9001", "NOME": "Dip. Scienze Agrarie, Exemplo", "URL": B + "/"}
CASA = ('<html><title>Dipartimento di Scienze Agrarie</title><a href="/chi-siamo">chi siamo</a>'
        '<a href="/notizie/2026/seminario-sulla-difesa-della-vite">x</a>'
        '<a href="/notizie/2026/bando-borse-di-studio-agronomia">y</a>'
        '<a href="/privacy">p</a><a href="/notizie/2026/terzo-articolo-sulle-colture-ortive">z</a></html>').encode()
PAG = {B + "/robots.txt": (200, b"User-agent: *\nDisallow: /riservato/\n", ""),
       B + "/": (200, CASA, ""),
       B + "/chi-siamo": (200, b"<title>Chi siamo</title><p>Il Dipartimento...</p>", ""),
       B + "/notizie/2026/seminario-sulla-difesa-della-vite": (200, b"<title>Seminario</title><p>uno</p>", ""),
       B + "/notizie/2026/bando-borse-di-studio-agronomia": (200, b"<title>Bando</title><p>due</p>", ""),
       B + "/notizie/2026/terzo-articolo-sulle-colture-ortive": (200, b"<title>Terzo</title><p>tre</p>", "")}


class Colher(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(self.enterContext(tempfile.TemporaryDirectory(prefix="prova-terr-")))
        self.pedidos = []

    def buscar(self, paginas):
        def f(u):
            self.pedidos.append(u)
            return paginas.get(u, (404, b"", "HTTP 404"))
        return f

    def test_prova_completa_em_5_pedidos_no_maximo(self):
        r = C.colher(FICHA, self.buscar(PAG), lambda: {"EGRESS_GATE": "PASS"}, self.tmp, dormir=lambda s: None)
        self.assertTrue(r["PROVA_COMPLETA"], r.get("PORQUE_PAROU"))
        self.assertLessEqual(len(self.pedidos), C.TETO_D38)
        self.assertEqual(["INSTITUCIONAL", "CONTEUDO", "CONTEUDO"], [p["PAPEL"] for p in r["PROVAS"]])
        self.assertTrue(r["PROVAS"][0]["URL"].endswith("/chi-siamo"))
        self.assertEqual(C.A_DECIDIR, r["TERRITORIO"])
        for p in r["PROVAS"]:
            self.assertTrue(Path(p["BYTES_EM"]).exists())

    def test_sem_portao_zero_pedidos(self):
        r = C.colher(FICHA, self.buscar(PAG), lambda: {"EGRESS_GATE": "BLOCKED"}, self.tmp)
        self.assertEqual([], self.pedidos)
        self.assertIn("portao", r["PORQUE_PAROU"])

    def test_robots_ilegivel_para_tudo(self):
        pag = dict(PAG)
        pag[B + "/robots.txt"] = (0, b"", "URLError: [WinError 10054]")
        r = C.colher(FICHA, self.buscar(pag), lambda: {"EGRESS_GATE": "PASS"}, self.tmp, dormir=lambda s: None)
        self.assertEqual([B + "/robots.txt"], self.pedidos)
        self.assertEqual([], r["PROVAS"])

    def test_robots_que_proibe_a_entrada_e_cumprido(self):
        pag = dict(PAG)
        pag[B + "/robots.txt"] = (200, b"User-agent: *\nDisallow: /\n", "")
        r = C.colher(FICHA, self.buscar(pag), lambda: {"EGRESS_GATE": "PASS"}, self.tmp, dormir=lambda s: None)
        self.assertEqual(1, len(self.pedidos))
        self.assertIn("proibe", r["PORQUE_PAROU"])

    def test_casca_js_nao_conta_duas_vezes(self):
        pag = dict(PAG)
        casca = (200, b"<html><div id=app></div><script src=app.js></script></html>", "")
        for k in list(pag):
            if "/notizie/" in k:
                pag[k] = casca
        r = C.colher(FICHA, self.buscar(pag), lambda: {"EGRESS_GATE": "PASS"}, self.tmp, dormir=lambda s: None)
        self.assertFalse(r["PROVA_COMPLETA"])
        self.assertEqual(1, sum(1 for p in r["PROVAS"] if p["PAPEL"] == "CONTEUDO"))


class Aplicar(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(self.enterContext(tempfile.TemporaryDirectory(prefix="aplicar-")))
        self.dec = self.tmp / "DECISOES.json"
        velha = {"CANDIDATA_ID": "CAND-9001", "URL": FICHA["URL"], "TERRITORIO": "NAO SEI",
                 "CATEGORIA": "PROVA_INSUFICIENTE", "MOTIVO": "so 1 pagina"}
        self.dec.write_text(json.dumps({"DECISOES": [velha], "TOTAL": 1}), encoding="utf-8")
        r = C.colher(FICHA, lambda u: PAG.get(u, (404, b"", "HTTP 404")), lambda: {"EGRESS_GATE": "PASS"},
                     self.tmp / "b", dormir=lambda s: None)
        self.proposta = r

    def test_a_decidir_nao_entra(self):
        out = C.aplicar([self.proposta], self.dec, {"CAND-9001": FICHA})
        self.assertEqual([], out["ENTRAM"])

    def test_decidida_substitui_o_nao_sei_e_o_canal_a_aceita(self):
        d = dict(self.proposta, TERRITORIO="T5", PAIS="IT", DECIDIDO_POR="ENSAIO", PORQUE="departamento")
        out = C.aplicar([d], self.dec, {"CAND-9001": FICHA})
        self.assertEqual(["CAND-9001"], out["ENTRAM"])
        dec, porque = DS.decisao_para("CAND-9001", FICHA, self.dec)
        self.assertIsNotNone(dec, porque)
        self.assertEqual("T5", dec["TERRITORIO"])
        self.assertEqual("NAO SEI", dec["ANTERIOR"][0]["TERRITORIO"])

    def test_sem_decidido_por_nao_entra(self):
        d = dict(self.proposta, TERRITORIO="T5", PAIS="IT", DECIDIDO_POR="")
        out = C.aplicar([d], self.dec, {"CAND-9001": FICHA})
        self.assertEqual([], out["ENTRAM"])
        self.assertIn("DECIDIDO_POR", out["FICAM"][0]["PORQUE"])


if __name__ == "__main__":
    unittest.main()
