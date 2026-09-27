# -*- coding: utf-8 -*-
"""MAESTRO-SOCIAL · o baixador (yt-dlp) nao desperdica vagas do teto D41.

Contra o YouTube de mentira (`provas/social-qualificar/medir_yt_dlp_offline.py`: um intermediario
local que nunca repassa nada), com os argumentos REAIS de `youtube_transcrever.argumentos_do_yt_dlp`:

    B1  os argumentos levam fatia de 50M, 1 tentativa, filtro de duracao e o marcador
    B2  audio de 25 MiB e 5 min: 4 pedidos (3 + 1 fatia) — sem o ajuste eram 6 (medido)
    B3  video de 15 min: 3 pedidos, NADA ao googlevideo, e o transcritor diz VIDEO_LONGO_DEMAIS
    B4  a duracao maxima le-se do ambiente
"""
import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest import mock

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (RAIZ, os.path.join(RAIZ, "coleta"), os.path.join(RAIZ, "ferramentas")):
    sys.path.insert(0, p)
import _gavetas  # noqa: E402,F401
import youtube_transcrever as ytv  # noqa: E402
from tests.test_prova_teto_social import _pasta_do_yt_dlp  # noqa: E402


def _mitm():
    caminho = os.path.join(RAIZ, "provas", "social-qualificar", "medir_yt_dlp_offline.py")
    spec = importlib.util.spec_from_file_location("medir_yt_dlp_offline_b", caminho)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class B1Argumentos(unittest.TestCase):
    def test_os_ajustes_estao_la(self):
        a = ytv.argumentos_do_yt_dlp("X")
        for par in (["--http-chunk-size", "50M"], ["--retries", "1"], ["--fragment-retries", "1"],
                    ["--extractor-retries", "1"], ["--match-filter", "duration <= 540"]):
            i = a.index(par[0])
            self.assertEqual(a[i:i + 2], par)
        self.assertIn("--print-traffic", a)                            # a contagem continua
        self.assertIn("--no-simulate", a)                              # o --print nao pode virar simulacao


class B4DuracaoDoAmbiente(unittest.TestCase):
    def test_o_ambiente_manda(self):
        with mock.patch.dict(os.environ, {"SINTONIA_YT_DURACAO_MAX_S": "1200"}):
            a = ytv.argumentos_do_yt_dlp("X")
        self.assertEqual(a[a.index("--match-filter") + 1], "duration <= 1200")
        with mock.patch.dict(os.environ, {"SINTONIA_YT_DURACAO_MAX_S": "0"}), self.assertRaises(ValueError):
            ytv.argumentos_do_yt_dlp("X")


class _Mitm(unittest.TestCase):
    def setUp(self):
        libs = _pasta_do_yt_dlp()
        if not libs:
            self.skipTest("yt_dlp nao esta nesta maquina")
        self.tmp = tempfile.mkdtemp(prefix="baixador-")
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.m = _mitm()
        cert, chave = self.m.certificado(self.tmp)
        self.p = self.m.Proxy(("127.0.0.1", 0), self.m.Resp)
        self.p.cert, self.p.chave = cert, chave
        threading.Thread(target=self.p.serve_forever, daemon=True).start()
        self.addCleanup(self.p.shutdown)
        self.px = "http://127.0.0.1:%d" % self.p.server_address[1]
        self.so = os.path.join(self.tmp, "libs")
        shutil.copytree(os.path.join(libs, "yt_dlp"), os.path.join(self.so, "yt_dlp"))

    def correr(self, tamanho, duracao):
        self.m.PEDIDOS.clear()
        self.m.TAMANHO["n"], self.m.DURACAO["s"] = tamanho, duracao
        env = dict(os.environ, PYTHONPATH=self.so, HTTP_PROXY=self.px, HTTPS_PROXY=self.px,
                   http_proxy=self.px, https_proxy=self.px, NO_PROXY="", no_proxy="")
        env.pop("SINTONIA_TETO_ONDA", None)
        env.pop("SINTONIA_YT_DURACAO_MAX_S", None)
        return subprocess.run([sys.executable, ytv.FREIO_DO_YT_DLP] + ytv.argumentos_do_yt_dlp(self.tmp)
                              + ["--proxy", self.px, "--no-check-certificates", "--no-cache-dir",
                                 "https://www.youtube.com/watch?v=" + self.m.VID],
                              capture_output=True, text=True, encoding="utf-8", errors="replace",
                              env=env, timeout=300)


class B2FatiaGrande(_Mitm):
    def test_25_mib_em_4_pedidos(self):
        r = self.correr(25 << 20, 300)
        self.assertEqual(self.m._por_host(self.m.PEDIDOS),
                         {"www.youtube.com": 3, "rr1---sn-abc.googlevideo.com": 1}, self.m.PEDIDOS)
        self.assertIn("MAESTRO_PASSOU_O_FILTRO", r.stdout)


class B3VideoLongo(_Mitm):
    def test_15_min_nao_descarrega(self):
        r = self.correr(25 << 20, 900)
        self.assertEqual(self.m._por_host(self.m.PEDIDOS), {"www.youtube.com": 3}, self.m.PEDIDOS)
        self.assertNotIn("MAESTRO_PASSOU_O_FILTRO", r.stdout)
        self.assertEqual(r.returncode, 0)
        # e o transcritor da o nome certo a isto
        with mock.patch.object(ytv, "MEDIA", self.tmp), \
                mock.patch.object(ytv.subprocess, "run", return_value=r):
            wav, motivo = ytv._audio(self.m.VID)
        self.assertIsNone(wav)
        self.assertTrue(motivo.startswith("VIDEO_LONGO_DEMAIS"), motivo)


if __name__ == "__main__":
    unittest.main()
