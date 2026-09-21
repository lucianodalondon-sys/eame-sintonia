#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O gatilho de fila baixa emite DISCOVERY_NEEDED ao cruzar o nivel — e so entao."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nivel_da_fila as N  # noqa: E402


def baldes(html_novas: int, mais_amostra: int, social: int = 75) -> dict:
    return {
        "UNIVERSO_DESTA_ARVORE": 241,
        "TOTAIS": {"JA_COM_CONTRATO": 77, "COM_SOURCE_ID_SEM_CONTRATO": 7,
                   "SEM_TERRITORIO": 13, "CARACTERIZADAS_NAO_READY": 27,
                   "NUNCA_CARACTERIZADAS": 117},
        "CARACTERIZADAS_NAO_READY_PORQUE": {"NEEDS_MORE_SAMPLING": mais_amostra,
                                            "CAPABILITY_BLOCK": 14},
        "NUNCA_CARACTERIZADAS": {"HTML_NOVAS": html_novas, "SOCIAL": social, "HTML": html_novas + 2},
    }


class OGatilho(unittest.TestCase):

    def test_1_acima_do_nivel_nao_pede(self):
        r = N.medir(baldes(40, 11), watermark=20)
        self.assertEqual(51, r["CANDIDATE_BACKLOG"])
        self.assertFalse(r["DISCOVERY_NEEDED"])
        self.assertEqual("DISCOVERY_NOT_NEEDED", r["DISCOVERY_SIGNAL"])

    def test_2_abaixo_do_nivel_pede_pelo_nome(self):
        r = N.medir(baldes(5, 3), watermark=20)
        self.assertEqual(8, r["CANDIDATE_BACKLOG"])
        self.assertTrue(r["DISCOVERY_NEEDED"])
        self.assertEqual("DISCOVERY_NEEDED", r["DISCOVERY_SIGNAL"])
        self.assertEqual("source-discovery-v1", r["DISCOVERY_PRODUCER"]["LANE"])

    def test_3_no_nivel_exacto_ainda_nao_pede_e_um_abaixo_pede(self):
        self.assertFalse(N.medir(baldes(20, 0), watermark=20)["DISCOVERY_NEEDED"])
        self.assertTrue(N.medir(baldes(19, 0), watermark=20)["DISCOVERY_NEEDED"])

    def test_4_as_sociais_e_as_bloqueadas_nao_enchem_a_fila(self):
        """1000 sociais nao sao trabalho automatico: o backlog continua 0."""
        r = N.medir(baldes(0, 0, social=1000), watermark=20)
        self.assertEqual(0, r["CANDIDATE_BACKLOG"])
        self.assertTrue(r["DISCOVERY_NEEDED"])
        self.assertEqual(1000, r["FORA_DO_BACKLOG"]["SOCIAL_FORA_DE_ESCOPO"])

    def test_5_sobre_o_disco_real_o_numero_e_o_dos_baldes(self):
        import baldes_das_candidatas as B
        b = B.calcular()
        r = N.medir(b)
        self.assertEqual(b["NUNCA_CARACTERIZADAS"]["HTML_NOVAS"]
                         + b["CARACTERIZADAS_NAO_READY_PORQUE"].get("NEEDS_MORE_SAMPLING", 0),
                         r["CANDIDATE_BACKLOG"])


if __name__ == "__main__":
    unittest.main()
