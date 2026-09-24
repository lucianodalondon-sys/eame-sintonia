# -*- coding: utf-8 -*-
"""EGR · O PORTÃO DE EGRESSO POR CONSENSO DE TRÊS VERIFICADORES.

A regra (decisão do bot Luciano, 24/09 15:05) está escrita em `superficie/rede.py`.
Estes testes votam SEM rede — cada verificador recebe uma resposta injetada.
"""
import json
import os
import sys
import tempfile
import time
import unittest
from unittest import mock

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "superficie"))
import rede  # noqa: E402

IPWHO = lambda p: (200, json.dumps({"success": True, "country_code": p, "ip": "1.2.3.4", "city": "X"}))  # noqa: E731
IPAPI = lambda p: (200, json.dumps({"status": "success", "countryCode": p}))  # noqa: E731
IFCO = lambda p: (200, json.dumps({"country_iso": p, "ip": "1.2.3.4"}))  # noqa: E731
R429 = (429, '{"status":429,"error":{"title":"Rate limit hit"}}')
TIMEOUT = (None, None)


def portao(a, b, c, tel=R429):
    return rede.portao_de_egresso("IT", respostas={"ipwho.is": a, "ip-api.com": b,
                                                   "ifconfig.co": c, "ipinfo.io": tel})


class AVotacao(unittest.TestCase):

    def test_2_IT_e_1_US_passa(self):
        v = portao(IPWHO("IT"), IPAPI("IT"), IFCO("US"))
        self.assertEqual(v["EGRESS_GATE"], "PASS")
        self.assertEqual(v["EGRESS_COUNTRY_CODE"], "IT")

    def test_o_discordante_fica_registado(self):
        v = portao(IPWHO("IT"), IPAPI("IT"), IFCO("US"))
        self.assertEqual(v["DISCORDANCIA"], [{"VERIFICADOR": "ifconfig.co", "DISSE": "US"}])
        self.assertEqual({x["VERIFICADOR"]: x["PAIS"] for x in v["VOTOS"]},
                         {"ipwho.is": "IT", "ip-api.com": "IT", "ifconfig.co": "US"})

    def test_2_US_e_1_IT_bloqueia(self):
        v = portao(IPWHO("US"), IPAPI("IT"), IFCO("US"))
        self.assertEqual(v["EGRESS_GATE"], "BLOCKED")
        self.assertEqual(v["EGRESS_VERDICT"], "BLOCKED")
        self.assertEqual(v["EGRESS_COUNTRY_CODE"], "US")

    def test_2_paises_diferentes_de_IT_bloqueiam(self):
        v = portao(IPWHO("US"), IPAPI("BR"), IFCO("IT"))
        self.assertEqual(v["EGRESS_GATE"], "BLOCKED")
        self.assertEqual(v["EGRESS_VERDICT"], "BLOCKED")

    def test_1_IT_e_2_429_e_unknown_e_bloqueia(self):
        v = portao(IPWHO("IT"), R429, R429)
        self.assertEqual(v["EGRESS_COUNTRY_CODE"], "UNKNOWN")
        self.assertEqual(v["EGRESS_VERDICT"], "UNKNOWN")
        self.assertEqual(v["EGRESS_GATE"], "BLOCKED", "UNKNOWN continua a bloquear")
        self.assertEqual(v["VOTOS_VALIDOS"], 1)

    def test_empate_e_unknown(self):
        v = portao(IPWHO("IT"), IPAPI("US"), TIMEOUT)
        self.assertEqual(v["EGRESS_COUNTRY_CODE"], "UNKNOWN")
        self.assertEqual(v["EGRESS_GATE"], "BLOCKED")
        self.assertEqual(v["EGRESS_VERDICT"], "UNKNOWN")

    def test_tres_paises_diferentes_e_unknown_no_pais(self):
        v = portao(IPWHO("FR"), IPAPI("US"), IFCO("IT"))
        self.assertEqual(v["EGRESS_COUNTRY_CODE"], "UNKNOWN")
        self.assertEqual(v["EGRESS_GATE"], "BLOCKED")

    def test_3_IT_passa_sem_discordancia(self):
        v = portao(IPWHO("IT"), IPAPI("IT"), IFCO("IT"))
        self.assertEqual(v["EGRESS_GATE"], "PASS")
        self.assertEqual(v["DISCORDANCIA"], [])


class OQueNaoEVoto(unittest.TestCase):

    def test_429_nao_e_voto(self):
        v = rede.voto("x", R429)
        self.assertIsNone(v["PAIS"])
        self.assertIn("429", v["PORQUE"])

    def test_429_com_pais_no_corpo_continua_sem_voto(self):
        """Um 429 que por acaso traga `country` no corpo nao vota."""
        self.assertIsNone(rede.voto("x", (429, '{"country":"IT"}'))["PAIS"])

    def test_timeout_json_partido_e_pais_ausente_nao_votam(self):
        for r in (TIMEOUT, (200, "<html>"), (200, "{}"), (200, '{"country": 7}'),
                  (200, '{"country": "Italia"}'), (200, "[1]")):
            with self.subTest(r=r):
                self.assertIsNone(rede.voto("x", r)["PAIS"])

    def test_o_servico_que_diz_que_falhou_nao_vota(self):
        r = (200, json.dumps({"success": False, "country_code": "IT"}))
        self.assertIsNone(rede.voto("ipwho.is", r, "country_code", ("success", True))["PAIS"])

    def test_o_ipinfo_nao_vota(self):
        """ipinfo.io saiu do caminho critico: mesmo a dizer IT, nao conta."""
        v = portao(IPWHO("IT"), R429, R429, tel=(200, '{"country":"IT"}'))
        self.assertEqual(v["EGRESS_GATE"], "BLOCKED")
        self.assertEqual(v["TELEMETRIA_SEM_VOTO"][0]["PAIS"], "IT")
        self.assertNotIn("ipinfo.io", [x["VERIFICADOR"] for x in v["VOTOS"]])

    def test_o_ip_e_a_cidade_nao_saem(self):
        texto = json.dumps(portao(IPWHO("IT"), IPAPI("IT"), IFCO("IT")))
        self.assertNotIn("1.2.3.4", texto)
        self.assertNotIn('"X"', texto)


class ACompatibilidade(unittest.TestCase):

    def test_o_json_mantem_os_campos_que_ja_se_liam(self):
        v = portao(IPWHO("IT"), IPAPI("IT"), IFCO("US"))
        for k in ("EGRESS_GATE", "EGRESS_COUNTRY_CODE", "EGRESS_REQUIRED", "VOTOS", "DISCORDANCIA"):
            self.assertIn(k, v)


class ACache(unittest.TestCase):

    def setUp(self):
        self.d = tempfile.mkdtemp(prefix="egr-cache-")
        self.f = os.path.join(self.d, "egresso-cache.json")
        self.env = mock.patch.dict(os.environ, {"SINTONIA_EGRESSO_CACHE": self.f})
        self.env.start()

    def tearDown(self):
        self.env.stop()

    def _medicao(self, pais, idade=0):
        m = rede.medir({"ipwho.is": IPWHO(pais), "ip-api.com": IPAPI(pais), "ifconfig.co": IFCO(pais)})
        m["MEDIDO_EM_EPOCH"] = time.time() - idade
        m["CHAVE_DO_AMBIENTE"] = rede.chave_do_ambiente()
        return m

    def test_cache_fresca_e_lida_sem_ir_a_rede(self):
        rede.gravar_cache(self._medicao("IT", idade=60))
        with mock.patch.object(rede, "_pedir", side_effect=AssertionError("foi a rede")):
            v = rede.portao_de_egresso("IT")
        self.assertEqual(v["EGRESS_GATE"], "PASS")
        self.assertTrue(v["DA_CACHE"])

    def test_cache_expirada_mede_outra_vez(self):
        rede.gravar_cache(self._medicao("IT", idade=rede.CACHE_SEGUNDOS + 1))
        chamadas = []

        def falso(url, timeout=10):
            chamadas.append(url)
            return IPAPI("US") if "ip-api" in url else (IPWHO("US") if "ipwho" in url else R429)
        with mock.patch.object(rede, "_pedir", side_effect=falso):
            v = rede.portao_de_egresso("IT")
        self.assertEqual(len(chamadas), 4, "3 que votam + ipinfo de telemetria")
        self.assertFalse(v["DA_CACHE"])
        self.assertEqual(v["EGRESS_GATE"], "BLOCKED")
        self.assertEqual(rede.ler_cache()["VOTOS"][0]["PAIS"], "US", "a medicao nova foi gravada")

    def test_cache_expira_aos_3_minutos(self):
        self.assertEqual(rede.CACHE_SEGUNDOS, 180)
        m = self._medicao("IT")
        rede.gravar_cache(m)
        self.assertIsNotNone(rede.ler_cache(agora=m["MEDIDO_EM_EPOCH"] + 179))
        self.assertIsNone(rede.ler_cache(agora=m["MEDIDO_EM_EPOCH"] + 180))

    def test_outro_ambiente_de_rede_nao_le_a_cache(self):
        """A prova offline (proxy morto) nao pode herdar o IT medido pela VPN."""
        rede.gravar_cache(self._medicao("IT"))
        # ⚠️ o valor tem de ser DIFERENTE do que ja estiver no ambiente: uma prova
        # que corre com HTTPS_PROXY=127.0.0.1:9 punha aqui o mesmo valor e a chave
        # nao mudava (medido 24/09, defeito deste teste).
        outro = (os.environ.get("HTTPS_PROXY") or "") + "-outro-ambiente"
        with mock.patch.dict(os.environ, {"HTTPS_PROXY": outro}):
            self.assertIsNone(rede.ler_cache())

    def test_injecao_nao_escreve_na_cache(self):
        portao(IPWHO("US"), IPAPI("US"), IFCO("US"))
        self.assertFalse(os.path.exists(self.f))

    def test_escrita_atomica_nao_deixa_meio_ficheiro(self):
        rede.gravar_cache(self._medicao("IT"))
        antes = open(self.f, encoding="utf-8").read()
        with mock.patch.object(rede.json, "dump", side_effect=OSError("disco cheio")):
            with self.assertRaises(OSError):
                rede.gravar_cache(self._medicao("US"))
        self.assertEqual(open(self.f, encoding="utf-8").read(), antes, "o ficheiro velho ficou inteiro")
        self.assertEqual([x for x in os.listdir(self.d) if x.endswith(".tmp")], [], "sem temporario orfao")

    def test_a_escrita_usa_os_replace(self):
        with mock.patch.object(rede.os, "replace", wraps=os.replace) as r:
            rede.gravar_cache(self._medicao("IT"))
        self.assertEqual(r.call_count, 1)

    def test_cache_corrompida_e_ignorada(self):
        with open(self.f, "w") as f:
            f.write("{meio")
        self.assertIsNone(rede.ler_cache())


# Quem pode citar o URL do ipinfo: SO os ficheiros que PROVAM a regra, nunca um
# consumidor. Cada um com o porque — um nome sem razao ao lado nao guarda nada.
PERMITIDOS = {
    # o dono: o ipinfo vive la como TELEMETRIA, sem voto
    "superficie/rede.py": "o dono; ipinfo so como telemetria",
    # prova offline: demonstra que o pedido ao ipinfo NAO sai numa corrida sem rede
    "provas/recollection_http_local.mjs": "prova que o ipinfo nao sai offline",
    # o ataque de mutacao: escreve o ipinfo como VERIFICADOR para provar que os testes o matam
    "scripts/egresso/mutar_egresso.py": "mutante `ipinfo_vota` (tem de morrer)",
    # este teste: o URL aparece no grep que ele proprio corre e nas respostas injetadas
    "tests/test_egresso_consenso.py": "a propria guarda (o padrao do grep)",
}
URL_DO_IPINFO = "https://ipinfo.io/json"


def quem_cita_o_ipinfo(extra_untracked=False):
    import subprocess
    cmd = ["git", "-C", RAIZ, "grep", "-l"] + (["--untracked"] if extra_untracked else [])
    cmd += ["-F", URL_DO_IPINFO, "--", "*.py", "*.mjs", "*.ps1", "*.sh", "*.yml"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return sorted(set(r.stdout.split()) - set(PERMITIDOS))


class NinguemPerguntaAoServicoDirectamente(unittest.TestCase):
    """Os consumidores leem a medida pelo rede.py (EGR)."""

    def test_nenhum_consumidor_chama_o_ipinfo(self):
        self.assertEqual(quem_cita_o_ipinfo(), [])

    def test_cada_permitido_existe_e_diz_porque(self):
        """Um permitido que ja nao existe e uma porta aberta sem dono."""
        for f, porque in PERMITIDOS.items():
            with self.subTest(f=f):
                self.assertTrue(os.path.isfile(os.path.join(RAIZ, f)), f)
                self.assertGreater(len(porque), 10)

    def test_a_guarda_morde_um_consumidor_novo(self):
        """O contraponto: um coletor novo com o URL do ipinfo poe a guarda vermelha."""
        falso = os.path.join(RAIZ, "coleta", "_consumidor_falso_egr.py")
        with open(falso, "w", encoding="utf-8") as f:
            f.write("URL = '%s'" % URL_DO_IPINFO + chr(10))
        try:
            self.assertEqual(quem_cita_o_ipinfo(extra_untracked=True),
                             ["coleta/_consumidor_falso_egr.py"])
        finally:
            os.remove(falso)


if __name__ == "__main__":
    unittest.main()
