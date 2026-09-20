# -*- coding: utf-8 -*-
"""DOIS TEXTOS DIFERENTES DO MESMO INSTANTE NÃO SÃO UMA DIVERGÊNCIA.

Medido em 20/09/2026: 4 das 46 passagens de reprocessamento da Big Collection 2
saíram `RAW_PERSISTENCE_FAILED` com a linha escrita, os bytes iguais e a chave
a devolver a linha. A conferência pós-escrita (`_difere`) comparava
`captured_at` como texto: o Postgres devolve `…03.44Z` (corta zeros à direita)
e o item dizia `…03.440Z`. As quatro eram exactamente as observações com
milissegundos terminados em zero. Estas provas fixam a regra e o caso real.
"""
import datetime
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401
from guarda import preservar_coleta as pc  # noqa: E402


class OMesmoInstanteEmDoisTextos(unittest.TestCase):

    def test_o_caso_real_das_quatro_passagens(self):
        for banco, corrida in (("2026-09-20T11:09:03.44Z", "2026-09-20T11:09:03.440Z"),
                               ("2026-09-20T11:09:38.01Z", "2026-09-20T11:09:38.010Z"),
                               ("2026-09-20T11:13:46.43Z", "2026-09-20T11:13:46.430Z"),
                               ("2026-09-20T11:19:33.19Z", "2026-09-20T11:19:33.190Z")):
            with self.subTest(banco=banco):
                self.assertEqual(pc._difere({"captured_at": banco}, {"captured_at": corrida},
                                            ("captured_at",)), [])

    def test_fuso_e_precisao_nao_fabricam_divergencia(self):
        self.assertEqual(pc._difere({"captured_at": "2026-09-20 11:09:03.44+00"},
                                    {"captured_at": "2026-09-20T11:09:03.440Z"}, ("captured_at",)), [])
        self.assertEqual(pc._difere({"captured_at": datetime.datetime(2026, 9, 20, 11, 9, 3, 440000,
                                                                       tzinfo=datetime.timezone.utc)},
                                    {"captured_at": "2026-09-20T11:09:03.440Z"}, ("captured_at",)), [])

    def test_instantes_diferentes_continuam_a_divergir(self):
        fora = pc._difere({"captured_at": "2026-09-20T11:09:03.441Z"},
                          {"captured_at": "2026-09-20T11:09:03.440Z"}, ("captured_at",))
        self.assertEqual([f["CAMPO"] for f in fora], ["captured_at"])

    def test_o_que_nao_e_instante_compara_se_como_antes(self):
        self.assertEqual(pc._difere({"sha256": "abc"}, {"sha256": "abc"}, ("sha256",)), [])
        self.assertEqual([f["CAMPO"] for f in pc._difere({"sha256": "abc"}, {"sha256": "abd"}, ("sha256",))],
                         ["sha256"])
        # um sha256 nao se le como data, mesmo comecando por digitos
        self.assertIsNone(pc._instante("2026092011090344abcdef"))
        self.assertIsNone(pc._instante(3828444))
        self.assertIsNone(pc._instante("NAO SEI"))

    def test_none_dos_dois_lados_nao_e_divergencia_e_de_um_lado_e(self):
        self.assertEqual(pc._difere({"captured_at": None}, {"captured_at": None}, ("captured_at",)), [])
        self.assertEqual(len(pc._difere({"captured_at": None}, {"captured_at": "2026-09-20T11:09:03.440Z"},
                                        ("captured_at",))), 1)


if __name__ == "__main__":
    unittest.main()
