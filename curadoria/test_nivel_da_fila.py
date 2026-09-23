#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O gatilho de fila baixa emite DISCOVERY_NEEDED ao cruzar o nivel — e so entao.

Apos a correcao B4 (D2): a contagem de HTML_NUNCA_CARACTERIZADAS_NOVAS exclui
fontes que ja tiveram uma tarefa QUALIFY (mesmo BLOQUEADA). O helper baldes()
inclui HTML_NOVAS_IDS e os testes isolam F.FILA para evitar leitura do disco
real durante os testes.
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fila as F        # noqa: E402
import nivel_da_fila as N  # noqa: E402


def baldes(html_novas: int, mais_amostra: int, social: int = 75) -> dict:
    """Baldes minimos com HTML_NOVAS_IDS para que os testes nao dependam do disco real."""
    html_ids = ["CAND-%04d" % i for i in range(html_novas)]
    return {
        "UNIVERSO_DESTA_ARVORE": 241,
        "TOTAIS": {"JA_COM_CONTRATO": 77, "COM_SOURCE_ID_SEM_CONTRATO": 7,
                   "SEM_TERRITORIO": 13, "CARACTERIZADAS_NAO_READY": 27,
                   "NUNCA_CARACTERIZADAS": 117},
        "CARACTERIZADAS_NAO_READY_PORQUE": {"NEEDS_MORE_SAMPLING": mais_amostra,
                                            "CAPABILITY_BLOCK": 14},
        "NUNCA_CARACTERIZADAS": {"HTML_NOVAS": html_novas, "HTML_NOVAS_IDS": html_ids,
                                 "SOCIAL": social, "HTML": html_novas + 2},
    }


class OGatilho(unittest.TestCase):

    def setUp(self):
        # Isolar a fila para que _qualify_ja_tentadas() nao leia o disco real.
        self.tmp = Path(tempfile.mkdtemp(prefix="nivel-test-"))
        self._orig_fila = F.FILA
        F.FILA = self.tmp / "fila.json"
        F.FILA.write_text(json.dumps({"PROXIMO_ID": 1, "TAREFAS": []}),
                          encoding="utf-8")

    def tearDown(self):
        F.FILA = self._orig_fila

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

    def test_5_sobre_o_disco_real_o_numero_reflecte_as_nao_tentadas(self):
        """No disco real: backlog = HTML_NOVAS nao tentadas + NEEDS_MORE_SAMPLING."""
        # Restaurar F.FILA para o disco real neste teste especifico.
        F.FILA = self._orig_fila
        import baldes_das_candidatas as B
        b = B.calcular()
        tentadas = N._qualify_ja_tentadas()
        html_ids = set(b["NUNCA_CARACTERIZADAS"].get("HTML_NOVAS_IDS", []))
        html_actionable = len(html_ids - tentadas)
        mais_amostra = b["CARACTERIZADAS_NAO_READY_PORQUE"].get("NEEDS_MORE_SAMPLING", 0)
        r = N.medir(b)
        self.assertEqual(html_actionable + mais_amostra, r["CANDIDATE_BACKLOG"])


if __name__ == "__main__":
    unittest.main()
