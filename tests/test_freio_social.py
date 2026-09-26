# -*- coding: utf-8 -*-
"""FREIO-SOCIAL · o pedido que passaria do teto D38 (D41 no YouTube) NAO SAI.

Sem rede: um servidor em 127.0.0.1 conta o que recebe (portao do Scrap), e um
intermediario local faz de youtube.com + googlevideo.com para o yt-dlp REAL
(`provas/social-qualificar/medir_yt_dlp_offline.py`), sem nunca repassar nada.

    F1  scrap_http: com livro da onda, o 6.o pedido ao dominio nao chega ao servidor
    F2  scrap_colheita (fase social): a recusa fica na linha do livro de corridas
    F3  scrap_colheita (fase social) sem livro da onda: livro PROPRIO da corrida, apagado no fim
    F4  sem livro nenhum, o scrap_http nao trava (as outras fases nao mudam)
    F5  yt-dlp com freio: youtube.com ja com 2 → 3 pedidos saem, o do googlevideo NAO (D41)
    F6  yt-dlp com freio, livro vazio: 4 pedidos, todos em youtube.com no livro
    F7  youtube_transcrever._audio corre o yt-dlp PELO freio e recolhe as recusas do filho
    F8  dois processos da onda nao passam os dois pelo 5.o lugar (reservar e atomico)
    F9  a lista de sufixos e a D41 sao as MESMAS do transporte web
"""
import importlib.util
import json
import os
import re
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
import teto_da_onda as teto  # noqa: E402
from coleta import scrap_colheita as sc  # noqa: E402
import scrap_executor as sx  # noqa: E402
import youtube_transcrever as ytv  # noqa: E402
from tests.test_prova_teto_social import _Servidor, _pasta_do_yt_dlp  # noqa: E402

RUN = "IT-T8-2026-09-26-040000-0123456789abcdef"


def _mitm():
    caminho = os.path.join(RAIZ, "provas", "social-qualificar", "medir_yt_dlp_offline.py")
    spec = importlib.util.spec_from_file_location("medir_yt_dlp_offline", caminho)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class _ComLivro(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="freio-")
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.livro = os.path.join(self.tmp, "TETO-ONDA.json")
        p = mock.patch.dict(os.environ, {teto.ENV_LIVRO: self.livro})
        p.start()
        self.addCleanup(p.stop)
        os.environ.pop(teto.ENV_TETO, None)
        teto.zerar()
        http.zerar_contagem()
        http._ROBOTS.clear()
        p = mock.patch.object(http, "PAUSA_ENTRE_CHAMADAS", 0)
        p.start()
        self.addCleanup(p.stop)

    def gasto(self):
        with open(self.livro, encoding="utf-8") as f:
            return json.load(f)["PEDIDOS_POR_DOMINIO"]


class F1OSextoPedidoNaoSai(_ComLivro):
    def test_o_6o_pedido_nao_chega_ao_servidor(self):
        srv = _Servidor()
        self.addCleanup(srv.fechar)
        recusado = None
        for i in range(8):
            try:
                http.buscar(srv.url("/p%d" % i), aceitar_json=False)
            except http.TetoDoDominio as e:
                recusado = e
                break
        self.assertIsNotNone(recusado, srv.pedidos)
        self.assertIsInstance(recusado, http.RotaNaoPermitida)     # politica nossa, nao bloqueio
        self.assertEqual(len(srv.pedidos), 5, srv.pedidos)          # robots + 4 rotas
        self.assertEqual(self.gasto(), {"127.0.0.1": 5})
        self.assertEqual(http.pedidos_por_host()[0], {"127.0.0.1": 5})   # conta so o que saiu
        [r] = teto.recusas()
        self.assertEqual((r["MOTIVO"], r["ORCAMENTO"], r["GASTO"]), ("TETO_DOMINIO", "127.0.0.1", 5))

    def test_teto_por_ambiente(self):
        os.environ[teto.ENV_TETO] = "2"
        self.addCleanup(os.environ.pop, teto.ENV_TETO, None)
        srv = _Servidor()
        self.addCleanup(srv.fechar)
        http.buscar(srv.url("/a"), aceitar_json=False)              # robots + /a = 2
        with self.assertRaises(http.TetoDoDominio):
            http.buscar(srv.url("/b"), aceitar_json=False)
        self.assertEqual(srv.pedidos, ["/robots.txt", "/a"])


class _Corrida(_ComLivro):
    def setUp(self):
        super().setUp()
        p = mock.patch.dict(os.environ, {"ITALY_OPS_ROOT": self.tmp})
        p.start()
        self.addCleanup(p.stop)
        p = mock.patch.object(sc, "escrever", lambda env, raiz=None: os.path.join(self.tmp, "ENVELOPE.json"))
        p.start()
        self.addCleanup(p.stop)
        self.srv = _Servidor()
        self.addCleanup(self.srv.fechar)

    def linhas(self):
        with open(os.path.join(self.tmp, sc.LIVRO_DE_CORRIDAS), encoding="utf-8") as f:
            return [json.loads(l) for l in f if l.strip()]

    def collect_que_pede(self, n):
        def collect(**kw):
            for i in range(n):
                http.buscar(self.srv.url("/c%d" % i), aceitar_json=False)
            return [], {"RESULT": "OK", "COST_STATE": "RUN"}
        return collect

    def correr(self, collect):
        with mock.patch.object(sx, "COLLECT", collect), mock.patch("sys.stdout"):
            return sc.main(["--run-id=%s" % RUN, "--fonte=IT-T8-001", "canal-youtube", "--canal-id=UCx"])


class F2ARecusaFicaNaLinha(_Corrida):
    def test_linha_leva_recusas_e_o_teto(self):
        with self.assertRaises(http.TetoDoDominio):
            self.correr(self.collect_que_pede(9))
        [l] = self.linhas()
        self.assertEqual(len(self.srv.pedidos), 5)
        self.assertIn("ABORTED", l)
        self.assertEqual(l["CORTESIA"]["PEDIDOS_POR_HOST"], {"127.0.0.1": 5})
        self.assertEqual(l["CORTESIA"]["TETO_POR_DOMINIO"], 5)
        self.assertEqual([r["MOTIVO"] for r in l["CORTESIA"]["RECUSAS"]], ["TETO_DOMINIO"])

    def test_sem_recusa_a_linha_nao_inventa_recusas(self):
        self.correr(self.collect_que_pede(2))
        [l] = self.linhas()
        self.assertNotIn("RECUSAS", l["CORTESIA"])


class F3LivroProprioDaCorrida(_Corrida):
    def setUp(self):
        super().setUp()
        os.environ.pop(teto.ENV_LIVRO)                               # a onda nao deu livro

    def test_corrida_social_sozinha_tem_teto_e_o_livro_morre_com_ela(self):
        visto = {}

        def collect(**kw):
            visto["livro"] = os.environ.get(teto.ENV_LIVRO)
            return self.collect_que_pede(9)(**kw)
        with self.assertRaises(http.TetoDoDominio):
            self.correr(collect)
        self.assertTrue(visto["livro"] and "TETO-CORRIDA-" in visto["livro"], visto)
        self.assertEqual(len(self.srv.pedidos), 5)
        self.assertIsNone(os.environ.get(teto.ENV_LIVRO))
        self.assertFalse(os.path.exists(os.path.dirname(visto["livro"])))


class F4SemLivroNaoTrava(unittest.TestCase):
    def test_fora_da_onda_o_portao_nao_muda(self):
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop(teto.ENV_LIVRO, None)
            http.zerar_contagem()
            http._ROBOTS.clear()
            srv = _Servidor()
            self.addCleanup(srv.fechar)
            with mock.patch.object(http, "PAUSA_ENTRE_CHAMADAS", 0):
                for i in range(7):
                    http.buscar(srv.url("/q%d" % i), aceitar_json=False)
            self.assertEqual(len(srv.pedidos), 8)


class _YtDlp(_ComLivro):
    def setUp(self):
        super().setUp()
        self.libs = _pasta_do_yt_dlp()
        if not self.libs:
            self.skipTest("yt_dlp nao esta nesta maquina")
        self.m = _mitm()
        self.m.PEDIDOS.clear()
        self.m.TAMANHO["n"] = 3 << 20
        cert, chave = self.m.certificado(self.tmp)
        self.p = self.m.Proxy(("127.0.0.1", 0), self.m.Resp)
        self.p.cert, self.p.chave = cert, chave
        threading.Thread(target=self.p.serve_forever, daemon=True).start()
        self.addCleanup(self.p.shutdown)
        self.proxy = "http://127.0.0.1:%d" % self.p.server_address[1]
        self.so_yt = os.path.join(self.tmp, "libs")
        shutil.copytree(os.path.join(self.libs, "yt_dlp"), os.path.join(self.so_yt, "yt_dlp"))
        self.recusas = os.path.join(self.tmp, "recusas.ndjson")

    def correr(self):
        env = dict(os.environ, PYTHONPATH=self.so_yt, HTTP_PROXY=self.proxy, HTTPS_PROXY=self.proxy,
                   http_proxy=self.proxy, https_proxy=self.proxy, NO_PROXY="", no_proxy="",
                   SINTONIA_TETO_RECUSAS=self.recusas)
        return subprocess.run(
            [sys.executable, ytv.FREIO_DO_YT_DLP, "-q", "--no-warnings", "--print-traffic",
             "-f", "bestaudio/best", "--proxy", self.proxy, "--no-check-certificates", "--no-cache-dir",
             "-o", os.path.join(self.tmp, "%(id)s.%(ext)s"), "https://www.youtube.com/watch?v=" + self.m.VID],
            capture_output=True, text=True, encoding="utf-8", errors="replace", env=env, timeout=300)

    def hosts(self):
        return [x["HOST"] for x in self.m.PEDIDOS]


class F5YtDlpD41(_YtDlp):
    def test_googlevideo_paga_no_youtube_e_o_pedido_nao_sai(self):
        with open(self.livro, "w", encoding="utf-8") as f:
            json.dump({"PEDIDOS_POR_DOMINIO": {"youtube.com": 2}}, f)
        r = self.correr()
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual(self.hosts(), ["www.youtube.com"] * 3, self.m.PEDIDOS)   # nada ao googlevideo
        self.assertEqual(self.gasto(), {"youtube.com": 5})
        rec = teto.ler_recusas_do_filho(self.recusas)
        self.assertTrue(rec and rec[0]["ORCAMENTO"] == "youtube.com" and "googlevideo.com" in rec[0]["HOST"], rec)
        self.assertEqual(ytv.trafego_do_yt_dlp(r.stdout), {"www.youtube.com": 3})


class F6YtDlpLivroVazio(_YtDlp):
    def test_quatro_pedidos_um_orcamento(self):
        r = self.correr()
        self.assertEqual(len(self.m.PEDIDOS), 4, self.m.PEDIDOS)
        self.assertEqual(self.gasto(), {"youtube.com": 4})
        self.assertEqual(teto.ler_recusas_do_filho(self.recusas), [])
        self.assertEqual(sum(ytv.trafego_do_yt_dlp(r.stdout).values()), 4)


class F7OTranscritorUsaOFreio(unittest.TestCase):
    def test_corre_pelo_freio_e_recolhe_recusas(self):
        teto.zerar()
        visto = {}

        def run(cmd, **kw):
            visto["cmd"], visto["env"] = cmd, kw.get("env") or {}
            with open(visto["env"]["SINTONIA_TETO_RECUSAS"], "a", encoding="utf-8") as f:
                f.write(json.dumps({"MOTIVO": "TETO_DOMINIO", "ORCAMENTO": "youtube.com",
                                    "HOST": "rr1---sn-a.googlevideo.com"}) + "\n")
            return subprocess.CompletedProcess(cmd, 1, stdout="", stderr="ERROR: TETO_DOMINIO")
        tmp = tempfile.mkdtemp(prefix="freio-ytv-")
        self.addCleanup(shutil.rmtree, tmp, True)
        with mock.patch.object(ytv, "MEDIA", tmp), mock.patch.object(ytv.subprocess, "run", run):
            wav, motivo = ytv._audio("AbCdEfGhIjK")
        self.assertIsNone(wav)
        self.assertEqual(visto["cmd"][1], ytv.FREIO_DO_YT_DLP)
        self.assertNotIn("-m", visto["cmd"][:3])
        self.assertTrue(motivo.startswith("TETO_DOMINIO"), motivo)
        self.assertEqual([r["ORCAMENTO"] for r in teto.recusas()], ["youtube.com"])
        self.assertFalse(os.path.exists(visto["env"]["SINTONIA_TETO_RECUSAS"]))


class F8ReservarEAtomico(_ComLivro):
    def test_quatro_processos_nunca_passam_de_5(self):
        prog = ("import sys; sys.path.insert(0, %r); import teto_da_onda as t\n"
                "ok = 0\n"
                "for _ in range(3):\n"
                "    try: t.reservar('www.linkedin.com'); ok += 1\n"
                "    except t.TetoDaOnda: pass\n"
                "print(ok)" % os.path.join(RAIZ, "coleta"))
        ps = [subprocess.Popen([sys.executable, "-c", prog], stdout=subprocess.PIPE, text=True,
                               env=dict(os.environ)) for _ in range(4)]
        oks = [int(p.communicate(timeout=120)[0].strip().splitlines()[-1]) for p in ps]
        self.assertEqual(sum(oks), 5, oks)
        self.assertEqual(self.gasto(), {"linkedin.com": 5})


class F9ParidadeComOTransporteWeb(unittest.TestCase):
    def test_mesmos_sufixos_e_mesma_d41(self):
        with open(os.path.join(RAIZ, "coleta", "italy_pilot_collect.mjs"), encoding="utf-8") as f:
            mjs = f.read()
        bloco = mjs[mjs.index("export const SUFIXOS_DE_DOIS_NIVEIS"):]
        bloco = bloco[:bloco.index("]));")]
        self.assertEqual(set(re.findall(r'"([a-z.-]+\.[a-z]+)"', bloco)), set(teto.SUFIXOS_DE_DOIS_NIVEIS))
        d41 = re.search(r"MESMO_ORCAMENTO = Object\.freeze\((\{[^}]*\})\)", mjs).group(1)
        self.assertEqual(json.loads(d41), teto.MESMO_ORCAMENTO)
        self.assertEqual(teto.orcamento_de("rr3---sn-x.googlevideo.com"), "youtube.com")
        self.assertEqual(teto.orcamento_de("media.licdn.com"), "licdn.com")
        self.assertEqual(teto.orcamento_de("www.salute.gov.it"), "salute.gov.it")


if __name__ == "__main__":
    unittest.main()
