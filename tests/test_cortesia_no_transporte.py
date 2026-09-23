"""A5 — a cortesia (robots.txt, pausa por host, teto por site) vive DENTRO do coletor.

Corre `provas/cortesia_http_local.mjs`: o transporte de verdade (`baixar()` com o
curl) contra um servidor HTTP em 127.0.0.1, sem rede externa. Quem conta os
pedidos e o servidor. A prova morre com codigo != 0 se uma verificacao falhar;
o red team (`provas/cortesia_red_team.mjs`) mostra que desligar cada guarda a mata.

~2 minutos: a pausa minima de 1 s por host e medida a serio, nao simulada.
"""
import os
import re
import subprocess
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestCortesiaNoTransporte(unittest.TestCase):

    def test_a_prova_local_passa_inteira(self):
        env = {k: v for k, v in os.environ.items()
               if k not in ("SINTONIA_PAUSA_POR_HOST_S", "SINTONIA_TETO_POR_HOST")}
        env["NODE_DISABLE_COMPILE_CACHE"] = "1"
        r = subprocess.run(["node", "provas/cortesia_http_local.mjs"], cwd=RAIZ, env=env,
                           capture_output=True, text=True, encoding="utf-8", errors="replace",
                           timeout=600)
        m = re.search(r"CORTESIA_HTTP_LOCAL · passou=(\d+) FALHAS=(\d+)", r.stdout)
        self.assertIsNotNone(m, r.stdout[-2000:] + r.stderr[-2000:])
        self.assertEqual(m.group(2), "0", r.stdout[-3000:])
        # Vazio nao passa: a prova tem de ter verificado alguma coisa.
        self.assertGreaterEqual(int(m.group(1)), 27, r.stdout[-3000:])
        self.assertEqual(r.returncode, 0, r.stdout[-3000:])


if __name__ == "__main__":
    unittest.main(verbosity=2)
