# -*- coding: utf-8 -*-
"""SCRAP-EVOLUCAO-V1 (F) — captura_xhr: o navegador acha o JSON; o teto manda no navegador tambem.

Unidades sem navegador (Porteiro, candidatos, proposta, portao do `correr`) e UMA prova com o Chrome de
verdade (sem janela, perfil novo) contra um servidor em 127.0.0.1 — a saida externa do Chrome vai para um
proxy numa porta fechada (127.0.0.1:9). Quem conta os pedidos e o SERVIDOR.
"""
import http.server
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "ferramentas"))
import captura_xhr as X  # noqa: E402
import cdp               # noqa: E402
import navegador         # noqa: E402


class Porteiro(unittest.TestCase):
    def test_imagem_fonte_estilo_media_nunca_saem(self):
        p = X.Porteiro(teto=5)
        for t in ("Image", "Font", "Stylesheet", "Media"):
            self.assertFalse(p.decidir("https://a.it/x", t)[0], t)
        self.assertEqual(p.gastos, {})

    def test_o_teto_conta_o_robots_e_recusa_o_resto(self):
        p = X.Porteiro(teto=3, gastos={"a.it": 1})
        self.assertEqual([p.decidir("https://www.a.it/%d" % i, "XHR")[0] for i in range(4)], [True, True, False, False])
        self.assertEqual(p.gastos, {"a.it": 3})
        self.assertTrue(p.decidir("https://b.it/", "Script")[0])          # outro dominio, outro orcamento

    def test_d91_cada_pedido_pede_licenca_ao_robots(self):
        vistos = []

        def robots(u):
            vistos.append(u)
            return ("/privado/" not in u), "robots de teste"
        p = X.Porteiro(teto=5, gastos={"a.it": 1}, robots=robots, robots_lidos={"https://www.a.it"})
        self.assertTrue(p.decidir("https://www.a.it/api/news.json", "XHR")[0])
        self.assertFalse(p.decidir("https://www.a.it/privado/dati.json", "XHR")[0])
        self.assertEqual(vistos, ["https://www.a.it/api/news.json", "https://www.a.it/privado/dati.json"])
        self.assertEqual(p.gastos, {"a.it": 2})                   # o proibido nao gastou teto

    def test_d91_origem_nova_le_o_robots_dela_e_isso_conta_no_teto_dela(self):
        p = X.Porteiro(teto=2, gastos={"a.it": 1}, robots=lambda u: (True, "ok"), robots_lidos={"https://www.a.it"})
        self.assertTrue(p.decidir("https://cdn.b.it/app.js", "Script")[0])
        self.assertEqual(p.gastos["b.it"], 2)                     # robots de cdn.b.it + o script
        self.assertFalse(p.decidir("https://api.b.it/x.json", "XHR")[0])   # origem nova, sem teto para o robots
        self.assertIn("antes de ler o robots", p.recusados[-1][2])

    def test_data_e_blob_nao_sao_rede(self):
        p = X.Porteiro(teto=0)
        self.assertTrue(p.decidir("data:image/png;base64,xx", "Image")[0])


class Candidatos(unittest.TestCase):
    EV = [
        {"method": "Network.requestWillBeSent", "params": {"requestId": "1", "request": {"method": "GET"}}},
        {"method": "Network.requestWillBeSent", "params": {"requestId": "2", "request": {"method": "POST"}}},
        {"method": "Network.responseReceived", "params": {"requestId": "0", "type": "Document",
                                                          "response": {"url": "https://a.it/", "status": 200, "mimeType": "text/html"}}},
        {"method": "Network.responseReceived", "params": {"requestId": "1", "type": "Fetch",
                                                          "response": {"url": "https://a.it/api/news", "status": 200, "mimeType": "application/json"}}},
        {"method": "Network.responseReceived", "params": {"requestId": "2", "type": "XHR",
                                                          "response": {"url": "https://a.it/api/busca", "status": 200, "mimeType": "application/json"}}},
        {"method": "Network.loadingFinished", "params": {"requestId": "1", "encodedDataLength": 321}},
    ]

    def test_so_json_e_com_metodo_e_fim(self):
        c = X.candidatos(self.EV)
        self.assertEqual([x["URL"] for x in c], ["https://a.it/api/news", "https://a.it/api/busca"])
        self.assertEqual((c[0]["METODO"], c[0]["TERMINOU"], c[0]["BYTES_NA_REDE"]), ("GET", True, 321))

    def test_so_get_200_vira_proposta_static_endpoint(self):
        c = X.candidatos(self.EV)
        p = X.proposta("IT-T7-164", "https://a.it/", c[0], b'{"x":1}')
        self.assertEqual(p["ESTADO"], "PROPOSTA")
        self.assertEqual(p["ACQUISITION"], {"STRATEGY": "STATIC_ENDPOINT", "URL": "https://a.it/api/news"})
        self.assertIn("COL-LAW-704", p["DESCOBERTO_POR"])
        self.assertEqual(X.proposta("IT-T7-164", "https://a.it/", c[1], b"{}")["ESTADO"], "NAO_SERVE")


class Portao(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="cxhr-")
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.abriu = []

    def _correr(self, **k):
        base = dict(livros=self.tmp, recibos=None, saida=os.path.join(self.tmp, "s"),
                    egresso=lambda: {"EGRESS_COUNTRY_CODE": "IT"}, janela=lambda *a: None,
                    robots=lambda u: (True, "ok"), abrir_aba=lambda porta: self.abriu.append(porta))
        base.update(k)
        return X.correr("https://www.pecorinoromano.com/", "IT-T7-164", **base)

    def test_sem_italia_o_navegador_nem_abre(self):
        r = self._correr(egresso=lambda: {"EGRESS_COUNTRY_CODE": "BR"})
        self.assertEqual(self.abriu, [])
        self.assertTrue(r["PAROU"].startswith("EGRESSO_NAO_IT"))

    def test_janela_fechada_ou_robots_que_barra_o_navegador_nem_abre(self):
        self.assertTrue(self._correr(janela=lambda *a: "amanha")["PAROU"].startswith("JANELA_24H"))
        r = self._correr(robots=lambda u: (False, "barra"))
        self.assertEqual(self.abriu, [])
        self.assertEqual(r["PEDIDOS_POR_DOMINIO"], {"pecorinoromano.com": 1})


def _porta_livre():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    p = s.getsockname()[1]
    s.close()
    return p


PAGINA = b"""<!doctype html><html><head><link rel="stylesheet" href="/tema.css"></head><body>
<img src="/logo.png"><ul id="l"></ul>
<script>
fetch('/api/notizie.json').then(r => r.json()).then(d => {
  document.getElementById('l').innerHTML = d.itens.map(i => '<li>' + i.titolo + '</li>').join('');
  return fetch('/api/secondo.json');
}).then(() => fetch('/api/terzo.json')).catch(() => {});
fetch('https://esterno.example.it/traccia.js').catch(() => {});
</script></body></html>"""
DADOS = json.dumps({"itens": [{"titolo": "Pecorino, bollettino n. 38", "url": "/news/38"}]}).encode()


@unittest.skipUnless(navegador.descobrir()["FOUND"], "sem Chrome nesta maquina")
class ChromeDeVerdade(unittest.TestCase):
    def setUp(self):
        self.pedidos = []
        pedidos = self.pedidos

        class H(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                pedidos.append(self.path)
                if self.path == "/":
                    corpo, tipo = PAGINA, "text/html; charset=utf-8"
                elif self.path.endswith(".json"):
                    corpo, tipo = DADOS, "application/json"
                else:
                    corpo, tipo = b"x", "application/octet-stream"
                self.send_response(200)
                self.send_header("Content-Type", tipo)
                self.send_header("Content-Length", str(len(corpo)))
                self.end_headers()
                self.wfile.write(corpo)

            def log_message(self, *a):
                pass
        self.srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), H)
        threading.Thread(target=self.srv.serve_forever, daemon=True).start()
        self.addCleanup(self.srv.server_close)
        self.addCleanup(self.srv.shutdown)
        self.perfil = tempfile.mkdtemp(prefix="cxhr-perfil-")
        self.porta = _porta_livre()
        exe = navegador.descobrir()["EXECUTABLE"]
        args = navegador.argumentos("about:blank", perfil=self.perfil, headless=True, porta_devtools=self.porta)
        args[-1:-1] = ["--proxy-server=http://127.0.0.1:9", "--disable-background-networking",
                       "--disable-component-update", "--disable-sync", "--no-pings"]
        self.chrome = subprocess.Popen([exe] + args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.addCleanup(shutil.rmtree, self.perfil, True)
        self.addCleanup(self._matar)
        fim = time.time() + 30
        while True:
            try:
                self.aba = cdp.Aba(cdp._aba_de_pagina(self.porta)["webSocketDebuggerUrl"])
                break
            except cdp.Erro:
                if time.time() > fim:
                    raise
                time.sleep(0.5)

    def _matar(self):
        try:
            self.aba.fechar()
        except Exception:  # noqa: BLE001
            pass
        self.chrome.kill()
        self.chrome.wait(15)

    def test_acha_o_json_e_o_teto_para_o_navegador(self):
        url = "http://127.0.0.1:%d/" % self.srv.server_address[1]
        # teto 3 com o robots ja contado: sobra 2 = a pagina + o 1.o JSON. O 2.o e o 3.o JSON nao saem.
        porteiro = X.Porteiro(teto=3, gastos={"127.0.0.1": 1})
        r = X.capturar(self.aba, url, porteiro, segundos=8)
        self.assertEqual(self.pedidos, ["/", "/api/notizie.json"], "o servidor so viu o que o teto deixou")
        self.assertNotIn("/tema.css", self.pedidos)
        self.assertNotIn("/logo.png", self.pedidos)
        [c] = [c for c in r["CANDIDATOS"] if c["HTTP"] == 200]
        self.assertEqual(c["URL"], url + "api/notizie.json")
        self.assertEqual(c["METODO"], "GET")
        self.assertEqual(r["CORPOS"][c["REQUEST_ID"]], DADOS)
        p = X.proposta("IT-T0-999", url, c, r["CORPOS"][c["REQUEST_ID"]])
        self.assertEqual(p["ACQUISITION"]["STRATEGY"], "STATIC_ENDPOINT")
        self.assertEqual(porteiro.gastos["127.0.0.1"], 3)
        recusas = {d["URL"].rsplit("/", 1)[-1] for d in r["DECISOES"] if not d["SAIU"]}
        self.assertTrue({"tema.css", "logo.png", "secondo.json"} <= recusas, recusas)
        self.assertTrue(any("esterno.example.it" in d["URL"] for d in r["DECISOES"]))

    def test_d91_o_json_proibido_pelo_robots_nao_chega_ao_servidor(self):
        import urllib.robotparser
        rp = urllib.robotparser.RobotFileParser()
        rp.parse(["User-agent: *", "Disallow: /api/"])
        url = "http://127.0.0.1:%d/" % self.srv.server_address[1]
        porteiro = X.Porteiro(teto=5, gastos={"127.0.0.1": 1}, robots=lambda u: (rp.can_fetch("*", u), "teste"),
                              robots_lidos={url.rstrip("/")})
        r = X.capturar(self.aba, url, porteiro, segundos=8)
        self.assertEqual(self.pedidos, ["/"])
        self.assertEqual([c for c in r["CANDIDATOS"] if c["HTTP"] == 200], [])
        self.assertTrue(any(d["URL"].endswith("/api/notizie.json") and "ROBOTS" in d["PORQUE"] for d in r["DECISOES"]))


if __name__ == "__main__":
    unittest.main()
