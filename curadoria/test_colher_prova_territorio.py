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
HOJE = "2026-09-26"


def noticia(titulo, data="12 marzo 2026", corpo=None):
    """Uma pagina de conteudo PUBLICADO: HTML, data de publicacao, texto a serio (> 600 letras)."""
    corpo = corpo or ("La difesa della vite nella campagna in corso richiede attenzione alla peronospora. " * 10)
    return ("<html><head><title>%s</title></head><body><nav>menu menu</nav><article><h1>%s</h1>"
            "<p class='data'>%s</p><p>%s</p></article></body></html>" % (titulo, titulo, data, corpo)).encode()


CHI = ("<html><title>Chi siamo</title><body><p>" + "Il Dipartimento di Scienze Agrarie studia le colture. " * 8
       + "</p></body></html>").encode()
PAG = {B + "/robots.txt": (200, b"User-agent: *\nDisallow: /riservato/\n", ""),
       B + "/": (200, CASA, ""),
       B + "/chi-siamo": (200, CHI, ""),
       B + "/notizie/2026/seminario-sulla-difesa-della-vite": (200, noticia("Seminario"), ""),
       B + "/notizie/2026/bando-borse-di-studio-agronomia": (200, noticia("Bando", "03/04/2026"), ""),
       B + "/notizie/2026/terzo-articolo-sulle-colture-ortive": (200, noticia("Terzo", "2026-05-01"), "")}


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
        r = C.colher(FICHA, self.buscar(PAG), lambda: {"EGRESS_GATE": "PASS"}, self.tmp, dormir=lambda s: None, hoje=HOJE)
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
        self.assertEqual(0, sum(1 for p in r["PROVAS"] if p["PAPEL"] == "CONTEUDO"))
        self.assertEqual(1, len(r["REJEITADAS"]), "a casca repetida nao se guarda duas vezes")


class ConteudoPublicado(Colher):
    """LOTE 1 real (26/09): 7 das 9 «completas» tinham como CONTEUDO o favicon, a ajuda, «Qualita», «Sedi»,
    regras de revista... PROVA_COMPLETA passa a exigir conteudo PUBLICADO: HTML, texto a serio e data."""

    def colher(self, pag, casa=None):
        pag = dict(pag)
        if casa is not None:
            pag[B + "/"] = (200, casa, "")
        return C.colher(FICHA, self.buscar(pag), lambda: {"EGRESS_GATE": "PASS"}, self.tmp,
                        dormir=lambda s: None, hoje=HOJE)

    def test_favicon_na_pasta_com_ano_nao_e_conteudo(self):
        self.assertFalse(C._parece_conteudo(B + "/sites/all/themes/unipd_2017/favicon.ico", B + "/"))
        j = C.juizo_de_conteudo(bytes([0, 0, 1, 0]) + b"\x10" * 400, B + "/x/favicon.ico", HOJE)
        self.assertFalse(j["SERVE"])
        self.assertIn("binario", j["PORQUE"])

    def test_paginas_de_servico_nao_sao_candidatas(self):
        for cam in ("/it/impresa/2013-04-04-08-54-42/help.html", "/vp-1219-assicurazione-della-qualita.html",
                    "/vp-150-struttura-e-sedi.html", "/index.php/ijfs/it/Open-Access-Publishing-Fee",
                    "/it/dipartimento/piano-strategico-di-dipartimento-e-piano-di-sviluppo",
                    "/content/dipartimento/direttore-e-organi-collegiali", "/it/didattica/summer-e-winter-school"):
            with self.subTest(cam=cam):
                self.assertFalse(C._parece_conteudo(B + cam, B + "/"))
        self.assertTrue(C._parece_conteudo(B + "/campagne-passate/comunicato-10-03-2025/", B + "/"))

    def test_estatico_com_ano_no_caminho_nao_e_conteudo(self):
        for cam in ("/uploads/2024/03/logo.svg", "/media/2025/programma.docx", "/sites/all/themes/x/2026/pagina"):
            with self.subTest(cam=cam):
                self.assertFalse(C._parece_conteudo(B + cam, B + "/"))

    def test_ano_colado_a_um_nome_nao_e_data(self):
        self.assertFalse(C._parece_conteudo(B + "/archivio/tema_2017", B + "/"))
        self.assertTrue(C._parece_conteudo(B + "/archivio/2017", B + "/"))

    def test_pagina_sem_data_e_rejeitada_e_nao_conta(self):
        pag = dict(PAG)
        pag[B + "/notizie/2026/bando-borse-di-studio-agronomia"] = (200, noticia("Bando", data="Ufficio bandi"), "")
        pag[B + "/notizie/2026/terzo-articolo-sulle-colture-ortive"] = (200, noticia("Terzo", data="sempre aperto"), "")
        r = self.colher(pag)
        self.assertFalse(r["PROVA_COMPLETA"])
        self.assertEqual(1, sum(1 for p in r["PROVAS"] if p["PAPEL"] == "CONTEUDO"))
        self.assertEqual(1, len(r["REJEITADAS"]))
        self.assertIn("sem data", r["REJEITADAS"][0]["JUIZO"]["PORQUE"])
        self.assertIn("sem data", r["PORQUE_PAROU"])
        self.assertTrue(Path(r["REJEITADAS"][0]["BYTES_EM"]).exists(), "a rejeitada fica guardada para auditoria")

    def test_a_data_de_hoje_e_o_aviso_do_dia_nao_publicacao(self):
        j = C.juizo_de_conteudo(noticia("Previsione", data="Sabato 26 Settembre 2026"), B + "/meteo/le-tappe", HOJE)
        self.assertFalse(j["SERVE"])
        j = C.juizo_de_conteudo(noticia("Previsione", data="Venerdi 25 Settembre 2026"), B + "/meteo/le-tappe", HOJE)
        self.assertTrue(j["SERVE"])
        self.assertEqual("2026-09-25", j["DATA_PUBLICADA"])

    def test_texto_curto_nao_e_conteudo(self):
        j = C.juizo_de_conteudo(noticia("Segnalazioni", corpo="Invia una segnalazione."), B + "/node/1942", HOJE)
        self.assertFalse(j["SERVE"])
        self.assertIn("texto curto", j["PORQUE"])

    def test_menu_e_rodape_nao_contam_como_texto(self):
        pag = ("<html><title>Avviso del 12/03/2026</title><nav>" + "Notizie Eventi Didattica " * 60 + "</nav><p>ok</p>"
               "<footer>" + "Via Brecce Bianche 10 Ancona " * 40 + "</footer></html>").encode()
        self.assertFalse(C.juizo_de_conteudo(pag, B + "/n/2026/x", HOJE)["SERVE"])

    def test_institucional_vazia_nao_completa(self):
        pag = dict(PAG)
        pag[B + "/chi-siamo"] = (200, b"<html><title>Organizzazione</title><p>Organizzazione</p></html>", "")
        r = self.colher(pag)
        self.assertFalse(r["PROVA_COMPLETA"])
        self.assertIn("institucional quase vazia", r["PORQUE_PAROU"])

    def test_primeiro_o_que_tem_data_no_endereco(self):
        casa = ('<html><a href="/chi-siamo">c</a><a href="/progetti-sulla-vite-e-sulle-olive">p</a>'
                '<a href="/notizie/2026/seminario-sulla-difesa-della-vite">n1</a>'
                '<a href="/notizie/2026/bando-borse-di-studio-agronomia">n2</a></html>').encode()
        self.assertTrue(C._parece_conteudo(B + "/progetti-sulla-vite-e-sulle-olive", B + "/"))
        r = self.colher(PAG, casa)
        self.assertTrue(r["PROVA_COMPLETA"], r.get("PORQUE_PAROU"))
        self.assertNotIn(B + "/progetti-sulla-vite-e-sulle-olive", self.pedidos)


class LoteComFichasNovas(unittest.TestCase):
    """LOTE 2B: consorzi que ainda nao estao na porta. So se registam os que a prova aprovar."""
    VIVO = [{"CANDIDATA_ID": "CAND-0001", "NOME": "Condifesa TVB", "URL": "https://www.condifesatvb.it/"}]

    def test_nova_entra_com_id_provisorio(self):
        f = C.fichas_do_lote({"FICHAS_NOVAS": [{"ID": "L2B-01", "NOME": "Condifesa Foggia",
                                                 "URL": "http://www.condifesafoggia.it/"}]}, self.VIVO)
        self.assertEqual(["L2B-01"], list(f))
        self.assertTrue(f["L2B-01"]["NAO_REGISTADA"])

    def test_nova_que_ja_esta_na_porta_e_erro(self):
        with self.assertRaises(SystemExit):
            C.fichas_do_lote({"FICHAS_NOVAS": [{"ID": "L2B-01", "NOME": "x", "URL": "http://condifesatvb.it"}]},
                             self.VIVO)

    def test_id_provisorio_nao_pode_parecer_cand(self):
        with self.assertRaises(SystemExit):
            C.fichas_do_lote({"FICHAS_NOVAS": [{"ID": "CAND-9999", "NOME": "x", "URL": "https://a.it/"}]}, self.VIVO)

    def test_cand_desconhecida_e_erro(self):
        with self.assertRaises(SystemExit):
            C.fichas_do_lote({"CANDIDATAS": ["CAND-0404"]}, self.VIVO)


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
