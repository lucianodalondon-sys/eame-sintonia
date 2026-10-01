#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O HARNESS DE MUTACAO DO L2-DISPARADOR: todo alvo existe UMA vez, em LF e em CRLF.

    python3 -m unittest tests.test_harness_mutacao_l2 -v

Vive FORA de `tests.test_disparador_intelligence` de proposito (como na ESTEIRA-SOZINHA): este teste
reprovaria com QUALQUER mutante plantado, e dentro da bateria que o harness corre mataria os mutantes
por si so, escondendo um teste de comportamento em falta.
"""
import importlib.util
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]


class TestHarnessDeMutacaoL2(unittest.TestCase):
    def setUp(self):
        spec = importlib.util.spec_from_file_location("mutantes_l2", RAIZ / "provas" / "l2" / "mutantes.py")
        self.MU = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.MU)

    def test_todo_alvo_e_unico_em_lf_e_em_crlf_e_o_mutante_guarda_o_fim_de_linha(self):
        for mid, f, _finge, velho, novo in self.MU.MUTANTES:
            lf = (RAIZ / f).read_bytes().replace(b"\r\n", b"\n")
            crlf = lf.replace(b"\n", b"\r\n")
            m_lf, n_lf = self.MU.aplicar(lf, velho, novo)
            m_crlf, n_crlf = self.MU.aplicar(crlf, velho, novo)
            self.assertEqual((n_lf, n_crlf), (1, 1), mid)
            self.assertNotEqual(m_lf, lf, mid)
            self.assertEqual(m_crlf, m_lf.replace(b"\n", b"\r\n"), mid)

    def test_os_alvos_do_g0_da_afirmacao_tambem(self):
        spec = importlib.util.spec_from_file_location("mutantes_g0_l2", RAIZ / "provas" / "l2" / "mutantes_g0.py")
        mg = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mg)
        for mid, f, _finge, velho, novo in mg.MUTANTES:
            lf = (RAIZ / f).read_bytes().replace(b"\r\n", b"\n")
            self.assertEqual(self.MU.aplicar(lf, velho, novo)[1], 1, mid)
            self.assertEqual(self.MU.aplicar(lf.replace(b"\n", b"\r\n"), velho, novo)[1], 1, mid)

    def test_os_ids_nao_se_repetem(self):
        ids = [m[0] for m in self.MU.MUTANTES]
        self.assertEqual(len(ids), len(set(ids)))


if __name__ == "__main__":
    unittest.main()
