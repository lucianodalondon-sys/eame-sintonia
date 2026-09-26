# -*- coding: utf-8 -*-
"""SCRAP-EVOLUCAO-V1 (B, D, E) — sem rede.

  B  a rota HTTP da fonte: cara de navegador com UM dono (regras/ROTA-NAVEGADOR.json), sem Referer,
     opcional por contrato/ficha, e a rota usada na proveniencia (COL-LAW-704); o `medir` do coordenador
     passa pelo portao inteiro e deixa um recibo que a janela de 24 h das rodadas le.
  D  _links da prova de territorio: so <a>/<area>, endereco canonico, PDF passa.
  E  espera por dominio com castigo: dobra depois de 403/429/503/10054, cumpre Retry-After, nunca pede mais.
"""
import email.utils
import io
import json
import os
import sys
import tempfile
import unittest
import urllib.error
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

RAIZ = Path(__file__).resolve().parents[1]
for p in ("coleta", "curadoria", "provas"):
    sys.path.insert(0, str(RAIZ / p))
import espera_por_dominio as EPD        # noqa: E402
import rota_navegador as RN             # noqa: E402

FICHA = json.loads((RAIZ / "regras" / "ROTA-NAVEGADOR.json").read_text(encoding="utf-8"))


class _Resp(io.BytesIO):
    status = 200

    def __init__(self, corpo=b"<html>ok</html>", headers=None):
        super().__init__(corpo)
        self.headers = headers or {}

    def geturl(self):
        return "https://x.it/"

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


# ── B · a rota ─────────────────────────────────────────────────────────────────────────────────
class B1_Ficha(unittest.TestCase):
    def test_navegador_usa_a_ficha_e_nao_manda_referer(self):
        h = RN.cabecalhos(RN.ROTA_NAVEGADOR)
        self.assertEqual(h, {"User-Agent": FICHA["UA"], "Accept": FICHA["ACCEPT"],
                             "Accept-Language": FICHA["ACCEPT_LANGUAGE"]})
        self.assertNotIn("Referer", h)
        self.assertFalse([k for k in FICHA if "REFERER" in k.upper() and not k.startswith("_")])
        self.assertIn("Chrome/", FICHA["UA"])
        self.assertIn("Safari/", FICHA["UA"])
        self.assertTrue(FICHA["ACCEPT_LANGUAGE"].startswith("it-IT"))

    def test_declarada_devolve_os_cabecalhos_do_leitor_sem_mexer(self):
        leitor = {"User-Agent": "Casa/1", "Accept": "*/*"}
        self.assertEqual(RN.cabecalhos(RN.ROTA_DECLARADA, do_leitor=leitor), leitor)

    def test_rota_desconhecida_e_erro_nao_palpite(self):
        self.assertEqual(RN.rota_da_fonte({}), RN.ROTA_DECLARADA)
        self.assertEqual(RN.rota_da_fonte({"ACQUISITION": {"ROTA_HTTP": "NAVEGADOR"}}), RN.ROTA_NAVEGADOR)
        with self.assertRaises(ValueError):
            RN.rota_da_fonte({"ACQUISITION": {"ROTA_HTTP": "FURTIVO"}})
        with self.assertRaises(ValueError):
            RN.cabecalhos("FURTIVO")

    def test_proveniencia_cita_a_lei_e_nao_a_repete(self):
        p = RN.proveniencia(RN.ROTA_NAVEGADOR)
        self.assertEqual(p["ROTA_HTTP"], "NAVEGADOR")
        self.assertIn("COL-LAW-704", p["ROTA_HTTP_DESCRICAO"])
        self.assertEqual(RN.proveniencia(RN.ROTA_DECLARADA)["ROTA_HTTP"], "DECLARADA")

    def test_o_coletor_web_le_o_mesmo_dono(self):
        js = (RAIZ / "coleta" / "italy_pilot_collect.mjs").read_text(encoding="utf-8")
        self.assertIn('new URL("../regras/ROTA-NAVEGADOR.json", import.meta.url)', js)
        self.assertNotIn('const UA = "Mozilla', js)
        self.assertIn("ROTA_NAVEGADOR.ACCEPT_LANGUAGE", js)


class B2_Canario(unittest.TestCase):
    def setUp(self):
        import canario as CAN
        self.CAN = CAN
        self.pedidos = []

        def urlopen(req, **k):
            self.pedidos.append(dict(req.header_items()))
            return _Resp(b'<html><body><a href="/news/mosca-dell-olivo-in-aumento/">m</a>' + b"x" * 500
                         + b"</body></html>")
        self.enterContext(mock.patch.object(CAN.urllib.request, "urlopen", urlopen))

    def _contrato(self, rota=None):
        aq = {"STRATEGY": "HTML_LINK_DISCOVERY", "INDEX_URL": "https://www.fonte.it/news/",
              "LINK_PATTERN": r"/news/[a-z-]+/$"}
        if rota:
            aq["ROTA_HTTP"] = rota
        return {"SOURCE_ID": "IT-T0-999", "OUTPUT_TYPE": "HTML", "ACQUISITION": aq}

    def test_contrato_com_rota_navegador_pede_com_a_ficha_e_diz_por_onde_veio(self):
        r = self.CAN.canario_html(self._contrato("NAVEGADOR"))
        self.assertTrue(self.pedidos)
        self.assertTrue(all(p.get("User-agent") == FICHA["UA"] for p in self.pedidos), self.pedidos)
        self.assertTrue(all("Referer" not in p for p in self.pedidos))
        self.assertEqual(r["ROTA_HTTP"], "NAVEGADOR")
        self.assertIn("COL-LAW-704", r["ROTA_HTTP_DESCRICAO"])

    def test_sem_rota_o_canario_continua_com_o_leitor_da_casa(self):
        import capturador as CAP
        r = self.CAN.canario_html(self._contrato())
        self.assertTrue(all(p.get("User-agent") == CAP.UA for p in self.pedidos), self.pedidos)
        self.assertEqual(r["ROTA_HTTP"], "DECLARADA")

    def test_a_rota_nao_vaza_para_o_canario_seguinte(self):
        import capturador as CAP
        self.CAN.canario_html(self._contrato("NAVEGADOR"))
        self.pedidos.clear()
        self.CAN.buscar("https://www.fonte.it/")
        self.assertEqual(self.pedidos[0].get("User-agent"), CAP.UA)


class B3_Medir(unittest.TestCase):
    URL = "https://dashboard01.green-planet.it/"

    def setUp(self):
        self.tmp = Path(self.enterContext(tempfile.TemporaryDirectory(prefix="rota-nav-")))
        self.pedidos = []

    def pedido(self, url):
        self.pedidos.append(url)
        return 200, b"<html>bacheca</html>", "", url, None

    def _medir(self, **k):
        base = dict(livros=str(self.tmp / "livros"), recibos=None, saida=str(self.tmp / "saida"),
                    egresso=lambda: {"EGRESS_COUNTRY_CODE": "IT", "VOTOS": 3},
                    janela=lambda *a: None, robots=lambda u: (True, "permite"), pedido=self.pedido)
        base.update(k)
        (self.tmp / "livros").mkdir(exist_ok=True)
        return RN.medir(self.URL, **base)

    def test_egresso_fora_de_italia_nada_sai(self):
        r = self._medir(egresso=lambda: {"EGRESS_COUNTRY_CODE": "BR"})
        self.assertEqual(self.pedidos, [])
        self.assertTrue(r["PAROU"].startswith("EGRESSO_NAO_IT"))
        self.assertEqual(sum(r["PEDIDOS_POR_DOMINIO"].values()), 0)

    def test_janela_de_24h_fechada_nada_sai(self):
        r = self._medir(janela=lambda *a: "2026-09-27T10:00:00+00:00")
        self.assertEqual(self.pedidos, [])
        self.assertTrue(r["PAROU"].startswith("JANELA_24H"))

    def test_robots_que_barra_gasta_so_o_robots(self):
        r = self._medir(robots=lambda u: (False, "barra"))
        self.assertEqual(self.pedidos, [])
        self.assertEqual(r["PEDIDOS_POR_DOMINIO"], {"green-planet.it": 1})

    def test_um_pedido_bytes_guardados_e_recibo_que_as_rodadas_leem(self):
        r = self._medir()
        self.assertEqual(self.pedidos, [self.URL])
        self.assertIsNone(r["PAROU"])
        self.assertEqual(r["PEDIDOS_POR_DOMINIO"], {"green-planet.it": 2})
        self.assertEqual(r["ROTA_HTTP"], "NAVEGADOR")
        self.assertEqual((self.tmp / "saida" / "CORPO.bin").read_bytes(), b"<html>bacheca</html>")
        # a janela REAL das rodadas le o recibo: um segundo medir no mesmo dia fica fechado
        fecha = RN._janela_24h("dashboard01.green-planet.it", str(self.tmp / "livros"), str(self.tmp / "saida"))
        self.assertIsNotNone(fecha)
        self.pedidos.clear()
        r2 = self._medir(janela=None, recibos=str(self.tmp / "saida"), saida=str(self.tmp / "saida2"))
        self.assertEqual(self.pedidos, [])
        self.assertTrue(r2["PAROU"].startswith("JANELA_24H"))


# ── D · ligacoes ───────────────────────────────────────────────────────────────────────────────
class D_Links(unittest.TestCase):
    def setUp(self):
        import colher_prova_territorio as C
        self.C = C

    def test_so_a_e_area_contam(self):
        h = (b'<link rel="stylesheet" href="/tema.css"><link rel="alternate" href="/feed/">'
             b'<svg><use href="/icons.svg#seta"/><use xlink:href="/icons.svg#x"/></svg>'
             b'<a href="/notizie/uno">1</a><map><area href="/mappa-regione"></map>')
        self.assertEqual(self.C._links(h, "https://www.a.it/"),
                         ["https://www.a.it/notizie/uno", "https://www.a.it/mappa-regione"])

    def test_canonico_junta_o_que_e_a_mesma_pagina(self):
        h = (b'<a href="/x?b=2&amp;a=1#topo">1</a><a href="HTTPS://WWW.A.IT:443/x?a=1&b=2">2</a>'
             b"<a href='/y'>3</a><a href=/z>4</a><a href=\"#so-ancora\">5</a>")
        self.assertEqual(self.C._links(h, "https://www.a.it/"),
                         ["https://www.a.it/x?a=1&b=2", "https://www.a.it/y", "https://www.a.it/z"])

    def test_pdf_passa_sempre(self):
        h = b'<a href="/bollettini/2026/bollettino-38.pdf">pdf</a>'
        self.assertEqual(self.C._links(h, "https://www.a.it/"), ["https://www.a.it/bollettini/2026/bollettino-38.pdf"])

    def test_outro_site_continua_fora(self):
        self.assertEqual(self.C._links(b'<a href="https://outro.it/x">o</a>', "https://www.a.it/"), [])

    def test_canonico_nao_perde_porta_propria_nem_parametro_vazio(self):
        self.assertEqual(self.C.canonico("http://A.it:8080/p?z=&a=1#f"), "http://a.it:8080/p?a=1&z=")
        self.assertEqual(self.C.canonico("https://a.it"), "https://a.it/")


# ── B+E · a prova de territorio ────────────────────────────────────────────────────────────────
B = "https://www.agraria.exemplo.it"
CASA = ('<html><title>Dip</title><a href="/chi-siamo">c</a>'
        '<a href="/notizie/2026/seminario-sulla-difesa-della-vite">x</a>'
        '<a href="/notizie/2026/bando-borse-di-studio-agronomia">y</a></html>').encode()


class BE_Colher(unittest.TestCase):
    def setUp(self):
        import colher_prova_territorio as C
        self.C = C
        self.tmp = Path(self.enterContext(tempfile.TemporaryDirectory(prefix="prova-evo-")))
        self.chamadas, self.sonos = [], []

    def _buscar(self, paginas):
        def f(u, **k):
            self.chamadas.append((u, k))
            return paginas.get(u, (404, b"", "HTTP 404"))
        return f

    def _colher(self, ficha, paginas):
        return self.C.colher(ficha, self._buscar(paginas), lambda: {"EGRESS_GATE": "PASS"}, self.tmp,
                             dormir=self.sonos.append, pausa=3.0)

    def _paginas(self, **troca):
        p = {B + "/robots.txt": (404, b"", "HTTP 404"), B + "/": (200, CASA, ""),
             B + "/chi-siamo": (200, b"<title>Chi siamo</title>", ""),
             B + "/notizie/2026/seminario-sulla-difesa-della-vite": (200, b"<title>S</title>1", ""),
             B + "/notizie/2026/bando-borse-di-studio-agronomia": (200, b"<title>B</title>2", "")}
        p.update(troca)
        return p

    def test_ficha_com_rota_navegador_pede_por_ela_e_cada_prova_o_diz(self):
        r = self._colher({"CANDIDATA_ID": "CAND-9101", "URL": B + "/", "ROTA_HTTP": "NAVEGADOR"}, self._paginas())
        self.assertTrue(r["PROVA_COMPLETA"], r)
        self.assertTrue(all(k == {"rota": "NAVEGADOR"} for _, k in self.chamadas))
        self.assertEqual(r["ROTA_HTTP"], "NAVEGADOR")
        self.assertTrue(all(p["ROTA_HTTP"] == "NAVEGADOR" for p in r["PROVAS"]))

    def test_sem_rota_o_leitor_injectado_e_chamado_como_sempre(self):
        r = self._colher({"CANDIDATA_ID": "CAND-9102", "URL": B + "/"}, self._paginas())
        self.assertTrue(all(k == {} for _, k in self.chamadas))
        self.assertEqual(r["ROTA_HTTP"], "DECLARADA")

    def test_pausa_normal_e_a_de_sempre(self):
        self._colher({"CANDIDATA_ID": "CAND-9103", "URL": B + "/"}, self._paginas())
        self.assertEqual(self.sonos, [3.0] * (len(self.chamadas) - 1))

    def test_429_dobra_a_espera_e_nao_pede_mais(self):
        pag = self._paginas(**{B + "/chi-siamo": (429, b"", "HTTP 429")})
        r = self._colher({"CANDIDATA_ID": "CAND-9104", "URL": B + "/"}, pag)
        urls = [u for u, _ in self.chamadas]
        self.assertEqual(len(urls), len(set(urls)), "um castigo nunca vira retentativa")
        self.assertLessEqual(r["PEDIDOS"], self.C.TETO_D38)
        i = urls.index(B + "/chi-siamo")
        self.assertEqual(self.sonos[i], 6.0)             # o pedido seguinte ao 429 espera o dobro

    def test_ligacao_cortada_10054_tambem_castiga(self):
        pag = self._paginas(**{B + "/": (0, b"", "ConnectionResetError: [WinError 10054] forcibly closed")})
        self._colher({"CANDIDATA_ID": "CAND-9105", "URL": B + "/"}, pag)
        self.assertEqual(len(self.chamadas), 2)          # robots + entrada que falhou: para ai
        self.assertEqual(self.sonos, [3.0])


# ── E · a peca da espera ───────────────────────────────────────────────────────────────────────
class E_Espera(unittest.TestCase):
    def _e(self, **k):
        self.sonos, self.t = [], [0.0]
        return EPD.EsperaPorDominio(dominio_de=lambda u: u.split("/")[2], dormir=self.sonos.append,
                                    relogio=lambda: self.t[0], **{"base": 1.0, "maximo": 60.0, **k})

    def test_dobra_ate_ao_maximo_e_desce_para_metade(self):
        e = self._e()
        esperas = [e.depois("https://a.it/x", http=429)["ESPERA_SEGUINTE_S"] for _ in range(8)]
        self.assertEqual(esperas, [2, 4, 8, 16, 32, 60, 60, 60])
        self.assertEqual(e.depois("https://a.it/x", http=200)["ESPERA_SEGUINTE_S"], 30)
        for _ in range(10):
            e.depois("https://a.it/x", http=200)
        self.assertEqual(e.atraso_de("https://a.it/x"), 1.0)

    def test_cada_dominio_tem_a_sua_espera(self):
        e = self._e()
        e.depois("https://a.it/x", http=403)
        self.assertEqual(e.atraso_de("https://a.it/y"), 2.0)
        self.assertEqual(e.atraso_de("https://b.it/y"), 1.0)

    def test_retry_after_em_segundos_e_em_data(self):
        e = self._e()
        self.assertEqual(e.depois("https://a.it/", http=503, retry_after="45")["ESPERA_SEGUINTE_S"], 45)
        quando = email.utils.format_datetime(datetime.now(timezone.utc) + timedelta(seconds=20), usegmt=True)
        s = EPD.segundos_do_retry_after(quando)
        self.assertTrue(15 <= s <= 21, s)
        self.assertIsNone(EPD.segundos_do_retry_after("amanha"))

    def test_retry_after_maior_que_o_maximo_desiste(self):
        d = self._e().depois("https://a.it/", http=429, retry_after="3600")
        self.assertTrue(d["DESISTIR"])
        self.assertEqual(d["ESPERA_SEGUINTE_S"], 60)

    def test_antes_dorme_so_o_que_falta(self):
        e = self._e()
        self.assertEqual(e.antes("https://a.it/"), 0.0)       # primeiro pedido: nao dorme
        e.depois("https://a.it/", http=429)                   # espera 2
        self.t[0] = 0.5
        e.antes("https://a.it/")
        self.assertEqual(self.sonos, [1.5])

    def test_resposta_boa_nunca_castiga(self):
        for st in (200, 301, 404, None):
            self.assertFalse(EPD.e_bloqueio(st, ""), st)
        for st in (403, 429, 503):
            self.assertTrue(EPD.e_bloqueio(st, ""), st)
        self.assertTrue(EPD.e_bloqueio(0, "URLError: [WinError 10054] Connessione interrotta"))


class E_ScrapHttp(unittest.TestCase):
    def setUp(self):
        import scrap_http as H
        self.H = H
        H.ESPERA.atraso.clear()
        self.sonos = []
        self.enterContext(mock.patch.object(H, "permitido", lambda u: (True, "ok")))
        self.enterContext(mock.patch.object(H.time, "sleep", self.sonos.append))

    def test_resposta_boa_respira_a_pausa_de_sempre(self):
        with mock.patch.object(self.H.urllib.request, "urlopen", lambda req, **k: _Resp()):
            self.H.buscar("https://a.it/x")
        self.assertEqual(self.sonos, [self.H.PAUSA_ENTRE_CHAMADAS])

    def test_429_com_retry_after_e_cumprido_e_o_erro_mantem_o_nome(self):
        def urlopen(req, **k):
            raise urllib.error.HTTPError(req.full_url, 429, "Too Many", {"Retry-After": "7"}, None)
        with mock.patch.object(self.H.urllib.request, "urlopen", urlopen):
            with self.assertRaises(self.H.RotaBloqueada):
                self.H.buscar_bytes("https://a.it/x")
        self.assertEqual(self.sonos, [7.0])

    def test_ligacao_cortada_dobra(self):
        def urlopen(req, **k):
            raise ConnectionResetError(10054, "forcibly closed")
        with mock.patch.object(self.H.urllib.request, "urlopen", urlopen):
            with self.assertRaises(self.H.RotaBloqueada):
                self.H.buscar("https://a.it/x")
        self.assertEqual(self.sonos, [2 * self.H.PAUSA_ENTRE_CHAMADAS])


if __name__ == "__main__":
    unittest.main()
