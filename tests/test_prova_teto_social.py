#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PROVA-TETO-SOCIAL — as corridas do Scrap (LinkedIn/YouTube) escrevem PEDIDOS_POR_HOST no
livro de corridas, e a prova-teto conta youtube.com + googlevideo.com juntos (D41).

Sem rede externa: um servidor HTTP em 127.0.0.1 conta os pedidos que recebe, e a conta do
portao tem de bater com a dele. O `yt-dlp` real (quando esta nesta maquina) corre contra o
mesmo servidor, com `--print-traffic`.

    S1  o portao conta cada pedido que sai: robots + rota + salto de redireccionamento
    S2  o `--print-traffic` do yt-dlp le-se por Host (POST com corpo e CONNECT nao duplicam;
        pedido sem Host = None)
    S3  o yt-dlp REAL contra o servidor local: a leitura bate com o servidor
    S4  scrap_colheita.main escreve a linha: PEDIDOS_POR_HOST = o servidor; ABORTED quando
        rebenta (e a excepcao sobe); fase fora da contagem e yt-dlp nao contado -> sem
        PEDIDOS_POR_HOST
    S5  a prova-teto le essas linhas: PASS / FAIL pela D41 / NAO_SEI / RUN_ID XX-
"""
from __future__ import annotations

import http.server as servidor_http
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest import mock

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (RAIZ, os.path.join(RAIZ, "coleta"), os.path.join(RAIZ, "ferramentas"),
          os.path.join(RAIZ, "provas")):
    sys.path.insert(0, p)
import _gavetas  # noqa: E402,F401

for k in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "all_proxy"):
    os.environ[k] = "http://127.0.0.1:9"
os.environ["NO_PROXY"] = os.environ["no_proxy"] = "127.0.0.1,localhost"

import scrap_http as http  # noqa: E402
from coleta import scrap_colheita as sc  # noqa: E402
import scrap_executor as sx  # noqa: E402
import youtube_transcrever as ytv  # noqa: E402
import prova_teto_dominio as ptd  # noqa: E402

RUN = "IT-T8-2026-09-25-120000-0123456789abcdef"
RUN_XX = "XX-T8-2026-09-25-120001-fedcba9876543210"


class _Servidor(object):
    """Conta o que recebe. `/r` redirecciona para `/x`."""

    def __init__(self):
        self.pedidos = []
        dono = self

        class H(servidor_http.BaseHTTPRequestHandler):
            def do_GET(self):
                dono.pedidos.append(self.path)
                if self.path == "/robots.txt":
                    corpo = b"User-agent: *\nAllow: /\n"
                    self.send_response(200)
                elif self.path == "/r":
                    self.send_response(302)
                    self.send_header("Location", "/x")
                    self.end_headers()
                    return
                else:
                    corpo = b"RIFF" + b"\0" * 2000
                    self.send_response(200)
                self.send_header("Content-Length", str(len(corpo)))
                self.end_headers()
                self.wfile.write(corpo)

            def log_message(self, *a):
                pass

        self.s = servidor_http.ThreadingHTTPServer(("127.0.0.1", 0), H)
        self.porta = self.s.server_address[1]
        threading.Thread(target=self.s.serve_forever, daemon=True).start()

    def url(self, caminho):
        return "http://127.0.0.1:%d%s" % (self.porta, caminho)

    def fechar(self):
        self.s.shutdown()
        self.s.server_close()


class _Base(unittest.TestCase):
    def setUp(self):
        self.srv = _Servidor()
        self.addCleanup(self.srv.fechar)
        http.zerar_contagem()
        http._ROBOTS.clear()
        p = mock.patch.object(http, "PAUSA_ENTRE_CHAMADAS", 0)
        p.start()
        self.addCleanup(p.stop)


class S1OPortaoContaCadaPedido(_Base):

    def test_robots_rota_e_salto_batem_com_o_servidor(self):
        http.buscar(self.srv.url("/a"), aceitar_json=False)
        http.buscar(self.srv.url("/r"), aceitar_json=False)     # 302 -> /x
        por_host, fora = http.pedidos_por_host()
        self.assertEqual(self.srv.pedidos, ["/robots.txt", "/a", "/r", "/x"])
        self.assertEqual(por_host, {"127.0.0.1": 4})
        self.assertEqual(fora, [])

    def test_pedido_recusado_pelo_teto_nao_conta(self):
        with http.orcamento_de_rede(1):
            with self.assertRaises(http.SemOrcamentoDeRede):
                http.buscar(self.srv.url("/a"), aceitar_json=False)   # o robots gasta o 1
        self.assertEqual(self.srv.pedidos, ["/robots.txt"])
        self.assertEqual(http.pedidos_por_host()[0], {"127.0.0.1": 1})

    def test_https_tambem_conta_no_abridor_instalado(self):
        # O YouTube e o LinkedIn sao https. Sem rede: so os pre-processadores do abridor
        # que `urlopen` usa, na ordem em que ele os chamaria.
        import urllib.request
        req = urllib.request.Request("https://www.youtube.com/@canal")
        for p in urllib.request._opener.process_request.get("https", []):
            req = getattr(p, "https_request")(req)
        self.assertEqual(http.pedidos_por_host()[0], {"youtube.com": 1})

    def test_www_junta_ao_site_e_de_fora_soma(self):
        http.contar_pedido("WWW.YouTube.com")
        http.contar_de_fora({"www.youtube.com": 2, "rr1---sn-a.googlevideo.com": 3}, quem="yt-dlp")
        self.assertEqual(http.pedidos_por_host()[0],
                         {"youtube.com": 3, "rr1---sn-a.googlevideo.com": 3})
        http.contar_de_fora(None, quem="yt-dlp")
        self.assertEqual(http.pedidos_por_host()[1], ["yt-dlp"])


# Linhas reais do `--print-traffic` (yt-dlp 2026.8.19, medido nesta maquina contra 127.0.0.1),
# mais as formas que um video do YouTube produz: POST com corpo numa segunda linha `send:`,
# e o CONNECT de um proxy.
SAIDA = r"""director: Sending request via "urllib"
send: b'GET /watch?v=abcdefghijk HTTP/1.1\r\nHost: www.youtube.com\r\nUser-Agent: Mozilla/5.0\r\nConnection: close\r\n\r\n'
reply: 'HTTP/1.1 200 OK\r\n'
header: Content-Type: text/html
send: b'POST /youtubei/v1/player?prettyPrint=false HTTP/1.1\r\nHost: www.youtube.com\r\nContent-Length: 12\r\n\r\n'
send: b'{"context":1}'
send: b'CONNECT rr3---sn-x.googlevideo.com:443 HTTP/1.1\r\nHost: rr3---sn-x.googlevideo.com:443\r\n\r\n'
send: b'GET /videoplayback?range=0-1 HTTP/1.1\r\nHost: rr3---sn-x.googlevideo.com\r\n\r\n'
send: b'GET /videoplayback?range=2-3 HTTP/1.1\r\nHost: rr3---sn-x.googlevideo.com\r\n\r\n'
"""


class S2OTrafegoDoYtDlpLeSePorHost(unittest.TestCase):

    def test_conta_por_host_sem_duplicar_corpo_nem_connect(self):
        self.assertEqual(ytv.trafego_do_yt_dlp(SAIDA),
                         {"www.youtube.com": 2, "rr3---sn-x.googlevideo.com": 2})

    def test_pedido_sem_host_e_nao_contado(self):
        mau = SAIDA + "send: b'GET /x HTTP/1.1\\r\\nUser-Agent: y\\r\\n\\r\\n'\n"
        self.assertIsNone(ytv.trafego_do_yt_dlp(mau))

    def test_saida_sem_pedidos_e_zero(self):
        self.assertEqual(ytv.trafego_do_yt_dlp("ERROR: nada\n"), {})


class S2bOAdaptadorPassaOYtDlpAConta(unittest.TestCase):
    """`adaptador_youtube.youtube_audio_publico` entrega os pedidos do yt-dlp ao portao."""

    def setUp(self):
        http.zerar_contagem()

    def _audio(self, trafego, resposta):
        def falso(vid):
            ytv.ULTIMO_TRAFEGO = trafego
            return resposta
        return mock.patch.object(ytv, "_audio", falso)

    def _correr(self):
        import adaptador_youtube as ay
        try:
            ay.youtube_audio_publico(run_id=RUN, country_scope="IT", video_id="abcdefghijk")
        except Exception:                                          # noqa: BLE001
            pass                                                   # a falha e o caso medido

    def test_falha_do_yt_dlp_conta_os_pedidos_que_fez(self):
        with self._audio({"www.youtube.com": 2, "rr1---sn-a.googlevideo.com": 1},
                         (None, "YT_DLP_NAO_ENTREGOU: 403")):
            self._correr()
        self.assertEqual(http.pedidos_por_host(),
                         ({"youtube.com": 2, "rr1---sn-a.googlevideo.com": 1}, []))

    def test_sem_leitura_do_trafego_fica_declarado(self):
        with self._audio(None, (None, "YT_DLP_ESTOUROU_O_TEMPO")):
            self._correr()
        self.assertEqual(http.pedidos_por_host(), ({}, ["yt-dlp"]))

    def test_cache_nao_e_pedido(self):
        with self._audio({"www.youtube.com": 9}, (None, "CACHE")):
            self._correr()
        self.assertEqual(http.pedidos_por_host(), ({}, []))


def _pasta_do_yt_dlp():
    libs = os.environ.get("SINTONIA_LIBS") or os.path.join(os.path.expanduser("~"), ".sintonia-libs")
    return libs if os.path.isdir(os.path.join(libs, "yt_dlp")) else None


class S3OYtDlpRealContraOServidorLocal(_Base):

    def test_a_leitura_bate_com_o_servidor(self):
        libs = _pasta_do_yt_dlp()
        if not libs:
            self.skipTest("yt_dlp nao esta nesta maquina")
        tmp = tempfile.mkdtemp(prefix="pts-yt-")
        self.addCleanup(shutil.rmtree, tmp, True)
        # So o yt_dlp no caminho: o resto de ~/.sintonia-libs e cp311 (memoria desta casa).
        so_yt = os.path.join(tmp, "libs")
        shutil.copytree(os.path.join(libs, "yt_dlp"), os.path.join(so_yt, "yt_dlp"))
        r = subprocess.run([sys.executable, "-m", "yt_dlp", "-q", "--no-warnings", "--print-traffic",
                            "-o", os.path.join(tmp, "%(id)s.%(ext)s"), self.srv.url("/a.wav")],
                           capture_output=True, text=True, encoding="utf-8", errors="replace",
                           env=dict(os.environ, PYTHONPATH=so_yt), timeout=300)
        lidos = ytv.trafego_do_yt_dlp(r.stdout)
        self.assertTrue(self.srv.pedidos, r.stderr[-500:])
        self.assertEqual(lidos, {"127.0.0.1": len(self.srv.pedidos)}, r.stdout[-1500:])


class _ComLivro(_Base):
    def setUp(self):
        super().setUp()
        self.tmp = tempfile.mkdtemp(prefix="pts-livro-")
        self.addCleanup(shutil.rmtree, self.tmp, True)
        p = mock.patch.dict(os.environ, {"ITALY_OPS_ROOT": self.tmp})
        p.start()
        self.addCleanup(p.stop)
        p = mock.patch.object(sc, "escrever", lambda env, raiz=None: os.path.join(self.tmp, "ENVELOPE.json"))
        p.start()
        self.addCleanup(p.stop)
        self.livro = os.path.join(self.tmp, sc.LIVRO_DE_CORRIDAS)

    def linhas(self):
        with open(self.livro, encoding="utf-8") as f:
            return [json.loads(l) for l in f if l.strip()]

    def correr(self, fase, filtro, collect, run=RUN):
        with mock.patch.object(sx, "COLLECT", collect), mock.patch("sys.stdout"):
            return sc.main(["--run-id=%s" % run, "--fonte=IT-T8-001", fase, filtro])


class S4ALinhaDaCorrida(_ComLivro):

    def _collect_que_pede(self, *caminhos):
        def collect(**kw):
            for c in caminhos:
                http.buscar(self.srv.url(c), aceitar_json=False)
            return [], {"RESULT": "OK", "COST_STATE": "RUN"}
        return collect

    def test_corrida_social_escreve_pedidos_por_host_iguais_ao_servidor(self):
        self.correr("canal-youtube", "--canal-id=UCx", self._collect_que_pede("/a", "/r"))
        [l] = self.linhas()
        self.assertEqual(l["RUN_ID"], RUN)
        self.assertEqual(l["FASE"], "canal-youtube")
        self.assertNotIn("ABORTED", l)
        self.assertEqual(l["CORTESIA"]["PEDIDOS_POR_HOST"], {"127.0.0.1": len(self.srv.pedidos)})
        self.assertEqual(len(self.srv.pedidos), 4)

    def test_a_contagem_e_so_desta_corrida(self):
        self.correr("canal-youtube", "--canal-id=UCx", self._collect_que_pede("/a"))
        self.correr("video-linkedin", "--pagina=https://x", self._collect_que_pede("/b"), run=RUN_XX)
        l1, l2 = self.linhas()
        self.assertEqual(l1["CORTESIA"]["PEDIDOS_POR_HOST"], {"127.0.0.1": 2})   # robots + /a
        self.assertEqual(l2["CORTESIA"]["PEDIDOS_POR_HOST"], {"127.0.0.1": 1})   # robots em cache

    def test_corrida_que_rebenta_escreve_ABORTED_com_os_pedidos_e_a_excepcao_sobe(self):
        def collect(**kw):
            http.buscar(self.srv.url("/a"), aceitar_json=False)
            raise OSError("ENOENT: rebentou a meio")
        with self.assertRaises(OSError):
            self.correr("video-linkedin", "--pagina=https://x", collect)
        [l] = self.linhas()
        self.assertIn("ENOENT", l["ABORTED"]["ERRO"])
        self.assertEqual(l["CORTESIA"]["PEDIDOS_POR_HOST"], {"127.0.0.1": 2})

    def test_fase_fora_da_contagem_nao_leva_pedidos_por_host(self):
        self.correr("janela", "--teto=1", self._collect_que_pede("/a"))
        [l] = self.linhas()
        self.assertNotIn("PEDIDOS_POR_HOST", l["CORTESIA"])
        self.assertTrue(l["CORTESIA"]["PEDIDOS_NAO_CONTADOS"])

    def test_yt_dlp_sem_contagem_tira_os_pedidos_por_host(self):
        def collect(**kw):
            http.buscar(self.srv.url("/a"), aceitar_json=False)
            http.contar_de_fora(None, quem="yt-dlp")
            return [], {"RESULT": "OK", "COST_STATE": "RUN"}
        self.correr("audio-youtube", "--video=abcdefghijk", collect)
        [l] = self.linhas()
        self.assertNotIn("PEDIDOS_POR_HOST", l["CORTESIA"])
        self.assertEqual(l["CORTESIA"]["PEDIDOS_NAO_CONTADOS"], ["yt-dlp"])


class S5AProvaTetoLeAsLinhas(_ComLivro):

    def prova(self, ids):
        onda = os.path.join(self.tmp, "onda.txt")
        with open(onda, "w", encoding="utf-8") as f:
            f.write("\n".join(ids) + "\n")
        with mock.patch("sys.stdout"):
            return ptd.main(["--livro", self.livro, "--onda", onda])

    def _collect_de_fora(self, por_host):
        def collect(**kw):
            http.contar_de_fora(por_host, quem="yt-dlp")
            return [], {"RESULT": "OK", "COST_STATE": "RUN"}
        return collect

    def test_linha_da_corrida_social_fecha_a_prova(self):
        self.correr("canal-youtube", "--canal-id=UCx", S4ALinhaDaCorrida._collect_que_pede(self, "/a"))
        self.assertEqual(self.prova([RUN]), 0)

    def test_D41_youtube_e_googlevideo_somam_no_mesmo_orcamento(self):
        # 3 + 3: cada um sozinho passaria; juntos sao 6 > 5.
        self.correr("audio-youtube", "--video=abcdefghijk",
                    self._collect_de_fora({"www.youtube.com": 3, "rr3---sn-x.googlevideo.com": 3}))
        self.assertEqual(self.prova([RUN]), 1)
        r = ptd.verificar([RUN], ptd.ler_livro(open(self.livro, encoding="utf-8")))
        self.assertEqual(r["DOMINIOS_ACIMA_DO_TETO"], {"youtube.com": 6})

    def test_D41_dentro_do_teto_passa(self):
        self.correr("audio-youtube", "--video=abcdefghijk",
                    self._collect_de_fora({"www.youtube.com": 2, "rr3---sn-x.googlevideo.com": 3}))
        self.assertEqual(self.prova([RUN]), 0)

    def test_yt_dlp_nao_contado_da_NAO_SEI(self):
        self.correr("audio-youtube", "--video=abcdefghijk", self._collect_de_fora(None))
        self.assertEqual(self.prova([RUN]), 2)

    def test_run_id_XX_e_reconhecido(self):
        self.correr("canal-youtube", "--canal-id=UCx", S4ALinhaDaCorrida._collect_que_pede(self, "/a"),
                    run=RUN_XX)
        self.assertEqual(ptd.run_ids_da_onda("onda: %s" % RUN_XX), [RUN_XX])
        self.assertEqual(self.prova([RUN_XX]), 0)

    def test_linkedin_e_licdn_continuam_separados(self):
        # A D41 so junta o que nomeou: juntar de mais tambem e inventar.
        self.assertEqual(ptd.orcamento_de("dms.licdn.com"), "licdn.com")
        self.assertEqual(ptd.orcamento_de("www.linkedin.com"), "linkedin.com")
        self.assertEqual(ptd.orcamento_de("r1---sn-a.googlevideo.com"), "youtube.com")


if __name__ == "__main__":
    unittest.main(verbosity=2)
