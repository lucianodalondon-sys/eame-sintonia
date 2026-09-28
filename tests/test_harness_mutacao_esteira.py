#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O HARNESS DE MUTACAO DA ESTEIRA-SOZINHA NAO DEPENDE DO FIM DE LINHA (FECHO 28/09).

    python3 -m unittest tests.test_harness_mutacao_esteira -v

Vive FORA de `tests.test_esteira_sozinha` de proposito: este teste confere que cada alvo de mutante
existe no codigo, e por isso reprovaria com QUALQUER mutante plantado. Se corresse dentro da bateria
que o harness usa, mataria os mutantes por si so e esconderia um teste de comportamento em falta.
"""
import importlib.util
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]


# ── O HARNESS DE MUTACAO NAO DEPENDE DO FIM DE LINHA (FECHO 28/09) ──────────
class TestHarnessDeMutacaoCRLF(unittest.TestCase):
    def setUp(self):
        spec = importlib.util.spec_from_file_location("mutantes_esteira",
                                                      RAIZ / "provas" / "esteira_sozinha" / "mutantes.py")
        self.MU = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.MU)

    def test_todo_alvo_e_unico_em_lf_e_em_crlf_e_o_mutante_guarda_o_fim_de_linha(self):
        # autocrlf=true: o mesmo ficheiro chega com CRLF. Todo alvo (os de varias linhas tambem) tem de
        # bater UMA vez nos dois, e o mutante em CRLF nao pode ganhar um \n solto.
        for mid, f, _finge, velho, novo in self.MU.MUTANTES:
            lf = (RAIZ / f).read_bytes().replace(b"\r\n", b"\n")
            crlf = lf.replace(b"\n", b"\r\n")
            m_lf, n_lf = self.MU.aplicar(lf, velho, novo)
            m_crlf, n_crlf = self.MU.aplicar(crlf, velho, novo)
            self.assertEqual((n_lf, n_crlf), (1, 1), mid)
            self.assertNotEqual(m_lf, lf, mid)
            self.assertEqual(m_crlf, m_lf.replace(b"\n", b"\r\n"), mid)
            self.assertEqual(m_crlf.count(b"\n"), m_crlf.count(b"\r\n"), mid)


if __name__ == "__main__":
    unittest.main()
