"""D42 (2) — «a página é o boletim» provada no COLETOR de verdade, contra um servidor local.

Corre `provas/janela_formas/pagina_boletim_local.mjs` (zero rede externa: proxy numa porta fechada, só
127.0.0.1). Seis rodadas: documento novo com RAW preservado; o menu muda e o boletim não -> SEEN_AGAIN
pela impressão do recorte; correção na mesma data -> versão nova do mesmo documento; data nova ->
documento novo; sem data -> tempos UNKNOWN; sem o boletim -> IDENTITY_FAILED."""
import os
import re
import shutil
import subprocess
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@unittest.skipUnless(shutil.which("node"), "sem node nesta maquina")
class TestPaginaBoletimNoColetor(unittest.TestCase):

    def test_as_seis_rodadas_passam(self):
        env = {k: v for k, v in os.environ.items()
               if k not in ("SINTONIA_PAUSA_POR_HOST_S", "SINTONIA_TETO_POR_HOST")}
        env["NODE_DISABLE_COMPILE_CACHE"] = "1"
        r = subprocess.run(["node", "provas/janela_formas/pagina_boletim_local.mjs"], cwd=RAIZ, env=env,
                           capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=600)
        m = re.search(r"PAGINA_BOLETIM_LOCAL · passou=(\d+) FALHAS=(\d+)", r.stdout)
        self.assertIsNotNone(m, r.stdout[-2000:] + r.stderr[-2000:])
        self.assertEqual("0", m.group(2), r.stdout[-3000:])
        self.assertEqual("6", m.group(1), "a prova tem de ter verificado as seis rodadas")


if __name__ == "__main__":
    unittest.main()
