"""SCRAP-EVOLUCAO-V1 (A) — FEED_DISCOVERY: o motor le o feed da fonte, e o coletor de verdade colhe pelo feed.

Corre `regras/feed_discovery_test.mjs` (o motor, leitor injectado) e `provas/feed_local.mjs` (o coletor
real, `baixar()` com o curl, contra um servidor em 127.0.0.1; quem conta os pedidos e o servidor).
Sem rede externa.
"""
import os
import re
import subprocess
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _node(caminho):
    env = {k: v for k, v in os.environ.items()
           if k not in ("SINTONIA_PAUSA_POR_HOST_S", "SINTONIA_TETO_POR_HOST", "SINTONIA_TETO_ONDA")}
    env["NODE_DISABLE_COMPILE_CACHE"] = "1"
    return subprocess.run(["node", caminho], cwd=RAIZ, env=env, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=600)


class TestFeedDiscovery(unittest.TestCase):
    def test_o_motor_le_o_feed(self):
        r = _node("regras/feed_discovery_test.mjs")
        m = re.search(r"PASSOU (\d+) · FALHOU (\d+)", r.stdout)
        self.assertIsNotNone(m, r.stdout[-2000:] + r.stderr[-2000:])
        self.assertEqual(m.group(2), "0", r.stdout[-3000:])
        self.assertGreaterEqual(int(m.group(1)), 9)
        self.assertEqual(r.returncode, 0)

    def test_o_coletor_colhe_pelo_feed_no_teto(self):
        r = _node("provas/feed_local.mjs")
        m = re.search(r"FEED_LOCAL · passou=(\d+) FALHAS=(\d+)", r.stdout)
        self.assertIsNotNone(m, r.stdout[-2000:] + r.stderr[-2000:])
        self.assertEqual(m.group(2), "0", r.stdout[-3000:])
        self.assertGreaterEqual(int(m.group(1)), 4)
        self.assertEqual(r.returncode, 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
