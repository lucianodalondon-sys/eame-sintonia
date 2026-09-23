"""LD3 — a politica do NAO SEI esta pronta e NAO esta ligada."""
from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))
import politica_nao_sei as P  # noqa: E402
import retrato_html as RH      # noqa: E402

NS = {"CAPA_OU_MATERIA": P.NAO_SEI}


class TestPoliticaNaoSei(unittest.TestCase):
    def test_depois_da_d11_e_quarentena(self):
        # Q1 (2026-09-23): a D11 decidiu a opcao C. Era PASSA ate a decisao.
        self.assertEqual(P.ACTIVA, P.QUARENTENA)
        self.assertEqual(P.decidir(NS)["ACCAO"], "QUARENTENA")

    def test_as_tres_respostas(self):
        self.assertEqual(P.decidir(NS, P.PASSA)["ACCAO"], "ENTRA")
        self.assertEqual(P.decidir(NS, P.PESSOA)["ACCAO"], "PESSOA_LE")
        self.assertEqual(P.decidir(NS, P.QUARENTENA)["ACCAO"], "QUARENTENA")

    def test_capa_e_materia_nao_dependem_da_politica(self):
        for pol in P.POLITICAS:
            self.assertEqual(P.decidir({"CAPA_OU_MATERIA": P.CAPA}, pol)["ACCAO"], "REPROVA")
            self.assertEqual(P.decidir({"CAPA_OU_MATERIA": P.MATERIA}, pol)["ACCAO"], "ENTRA")

    def test_retrato_sem_veredito_e_nao_sei(self):
        self.assertEqual(P.decidir(None, P.PESSOA)["ACCAO"], "PESSOA_LE")

    def test_politica_inventada_falha_alto(self):
        with self.assertRaises(ValueError):
            P.decidir(NS, "TALVEZ")

    def test_ligada_so_na_porta_depois_da_d11(self):
        # Q1 (2026-09-23): a D11 decidiu, e a politica foi ligada num sitio so — a
        # pergunta `materia` da porta de admissao. O gate de FONTE (retrato_html,
        # dono LD3) continua intocado: so reprova CAPA_PROVAVEL.
        contrato = {"OUTPUT_TYPE": "HTML", "ACQUISITION": {"STRATEGY": "HTML_LINK_DISCOVERY"}}
        self.assertIsNone(RH.gate_capa_nao_e_materia(contrato, dict(NS, LINKS=0,
                          NON_WHITESPACE_CHARACTERS=0, PARAGRAPH_CHARACTERS=0)))
        r = subprocess.run(["git", "grep", "-l", "politica_nao_sei", "--", "*.py", "*.mjs"],
                           cwd=RAIZ, capture_output=True, text=True)
        chamadores = [f for f in r.stdout.split() if not f.endswith((
            "politica_nao_sei.py", "test_politica_nao_sei.py", "test_quarentena_naosei.py",
            "ensaio_quarentena_naosei.py"))]
        self.assertEqual(chamadores, ["admissao/admissao.py"],
                         "a politica tem de estar ligada na porta, e SO na porta")


if __name__ == "__main__":
    unittest.main()
