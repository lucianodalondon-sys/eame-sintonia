"""FECHAR-ONDA2-B (D60 c) — o nome fisico da pasta nao derruba a fonte, e a identidade nao muda.

Corre `provas/nome_da_pasta_windows.mjs`: sem rede, com os 42 contratos em risco do robo vivo
(37 pelo LINK_PATTERN com `\?`), o DOCUMENT_ID calculado pelo motor de verdade e o mkdir feito a
serio numa pasta temporaria.
"""
import os
import re
import subprocess
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class ONomeDaPastaNaoDerrubaAFonte(unittest.TestCase):

    def test_a_prova_passa_inteira(self):
        env = dict(os.environ, NODE_DISABLE_COMPILE_CACHE="1")
        r = subprocess.run(["node", "provas/nome_da_pasta_windows.mjs"], cwd=RAIZ, env=env,
                           capture_output=True, text=True, encoding="utf-8", errors="replace",
                           timeout=300)
        m = re.search(r"NOME_DA_PASTA_WINDOWS · passou=(\d+) FALHAS=(\d+)", r.stdout)
        self.assertIsNotNone(m, r.stdout[-2000:] + r.stderr[-2000:])
        self.assertEqual(m.group(2), "0", r.stdout[-3000:])
        self.assertGreaterEqual(int(m.group(1)), 18, r.stdout[-3000:])   # vazio nao passa (N1 so no Windows)
        self.assertEqual(r.returncode, 0, r.stdout[-3000:])


if __name__ == "__main__":
    unittest.main(verbosity=2)
