"""D38 — o teto de 5 pedidos conta-se por DOMINIO REGISTAVEL e vale para a ONDA inteira.

Corre `provas/teto_dominio_local.mjs`: o transporte de verdade (`baixar()` com o curl)
contra um servidor HTTP em 127.0.0.1, sem rede externa. Quem conta os pedidos e o
servidor. O ataque (`provas/teto_dominio_mutacao.py`) mostra que desligar cada peca
do conserto a mata.
"""
import os
import re
import subprocess
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestTetoPorDominioNaOnda(unittest.TestCase):

    def test_a_prova_local_passa_inteira(self):
        env = {k: v for k, v in os.environ.items()
               if k not in ("SINTONIA_PAUSA_POR_HOST_S", "SINTONIA_TETO_POR_HOST", "SINTONIA_TETO_ONDA")}
        env["NODE_DISABLE_COMPILE_CACHE"] = "1"
        r = subprocess.run(["node", "provas/teto_dominio_local.mjs"], cwd=RAIZ, env=env,
                           capture_output=True, text=True, encoding="utf-8", errors="replace",
                           timeout=600)
        m = re.search(r"TETO_DOMINIO_LOCAL · passou=(\d+) FALHAS=(\d+)", r.stdout)
        self.assertIsNotNone(m, r.stdout[-2000:] + r.stderr[-2000:])
        self.assertEqual(m.group(2), "0", r.stdout[-3000:])
        self.assertGreaterEqual(int(m.group(1)), 7, r.stdout[-3000:])   # vazio nao passa
        self.assertEqual(r.returncode, 0, r.stdout[-3000:])


if __name__ == "__main__":
    unittest.main(verbosity=2)
