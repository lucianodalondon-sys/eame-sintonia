#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OS CAMPOS DA DESCOBERTA NO PAINEL SAO LIDOS, NUNCA ESCRITOS A MAO.

Enxerto de candidate-bridge-v1 (63b71421) em status_live.py. La, o ramo
`except` devolvia `CANDIDATES_TOTAL: 0` e `READY_LEGACY: 18` — um zero que
parece medicao e um 18 que nao acompanha o livro. Aqui cada campo vem do
ficheiro de prova da descoberta; sem ficheiro e NUNCA; ficheiro ilegivel e
«NAO SEI: <Excecao>». A prova vive numa pasta descartavel.

    UM PAINEL QUE MENTE E PIOR DO QUE NAO TER PAINEL.
"""
from __future__ import annotations

import json
import re
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

import fila as F          # noqa: E402
import lifecycle as LC    # noqa: E402
import status_live as SL  # noqa: E402

OS_CAMPOS = ("DISCOVERY_SERVICE", "LAST_DISCOVERY_RUN", "LAST_DISCOVERY_RUN_AGE_H",
             "CANDIDATES_NEW", "DEDUP_REJECTED")


class OPainelDaDescoberta(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        d = Path(self.tmp.name)
        self._antes = (SL.DISCOVERY_PROOF, LC.LIVRO, F.FILA, SL.LOTES, SL.SAIDA)
        SL.DISCOVERY_PROOF = d / "PROOF.json"
        LC.LIVRO = d / "LEDGER.json"
        F.FILA = d / "QUEUE.json"
        SL.LOTES = d / "BATCHES.json"
        SL.SAIDA = d / "STATUS-LIVE.json"

    def tearDown(self):
        (SL.DISCOVERY_PROOF, LC.LIVRO, F.FILA, SL.LOTES, SL.SAIDA) = self._antes
        self.tmp.cleanup()

    def _prova(self, **campos):
        SL.DISCOVERY_PROOF.write_text(json.dumps(campos), encoding="utf-8")

    def test_1_sem_prova_diz_NOT_RUN_e_NUNCA_e_nenhum_zero(self):
        r = SL._status_discovery()
        self.assertEqual(r["DISCOVERY_SERVICE"], "NOT_RUN")
        self.assertEqual(r["LAST_DISCOVERY_RUN"], "NUNCA")
        self.assertEqual(r["CANDIDATES_NEW"], "NUNCA")
        self.assertEqual(r["DEDUP_REJECTED"], "NUNCA")
        self.assertNotIn(0, r.values(), "um zero sem corrida seria medicao falsa")

    def test_2_com_prova_os_numeros_sao_os_da_prova(self):
        corrida = datetime.now(timezone.utc) - timedelta(hours=2)
        self._prova(CORRIDA_EM=corrida.isoformat(), NOVEL_CANDIDATES=7,
                    DUPLICATES_REJECTED=3)
        r = SL._status_discovery()
        self.assertEqual(r["DISCOVERY_SERVICE"], "RAN")
        self.assertEqual(r["LAST_DISCOVERY_RUN"], corrida.isoformat())
        self.assertEqual(r["CANDIDATES_NEW"], 7)
        self.assertEqual(r["DEDUP_REJECTED"], 3)
        self.assertAlmostEqual(r["LAST_DISCOVERY_RUN_AGE_H"], 2.0, delta=0.1)

    def test_3_prova_ilegivel_diz_NAO_SEI_com_a_excecao_e_nunca_zero(self):
        SL.DISCOVERY_PROOF.write_text("{{{ isto nao e json", encoding="utf-8")
        r = SL._status_discovery()
        for k in OS_CAMPOS:
            self.assertTrue(str(r[k]).startswith("NAO SEI: JSONDecodeError"), (k, r[k]))
        self.assertNotIn(0, r.values())

    def test_4_prova_sem_o_campo_diz_NAO_SEI_e_nao_inventa(self):
        self._prova(CORRIDA_EM=datetime.now(timezone.utc).isoformat())
        r = SL._status_discovery()
        self.assertTrue(str(r["CANDIDATES_NEW"]).startswith("NAO SEI: KeyError"), r)
        self.assertNotIn(0, r.values())

    def test_5_estatico_o_painel_nao_tem_numero_escrito_a_mao(self):
        """O defeito do bridge: 'READY_LEGACY': 18 e 'CANDIDATES_TOTAL': 0 literais."""
        fonte = (AQUI / "status_live.py").read_text(encoding="utf-8")
        literais = re.findall(
            r"[\"'](READY_LEGACY|READY_CURRENT|READY_TOTAL|CANDIDATES_NEW|"
            r"CANDIDATES_TOTAL|DEDUP_REJECTED|QUEUE_DEPTH)[\"']\s*:\s*\d+",
            fonte)
        self.assertEqual(literais, [],
                         "campo do painel com numero literal: %s" % literais)

    def test_6_os_campos_entram_no_status_completo(self):
        """status() carrega os cinco campos; o resto do painel e simulado para
        o teste nao ler nem escrever a arvore real."""
        self._prova(CORRIDA_EM=datetime.now(timezone.utc).isoformat(),
                    NOVEL_CANDIDATES=30, DUPLICATES_REJECTED=8)
        m = {"READY": 0, "READY_LEGACY": 0, "READY_CURRENT": 0, "QUEUE_PENDING": 0,
             "QUEUE_ELIGIBLE_NOW": 0, "QUEUE_WAITING_RETRY": 0}
        with mock.patch.object(SL.IC, "metricas_operacionais", return_value=m), \
             mock.patch.object(SL, "_estado_servico",
                               return_value={"SOURCE_CURATOR_SERVICE": "UNKNOWN",
                                             "WORKER_ALIVE": False}), \
             mock.patch.object(SL, "_nivel_da_fila",
                               return_value={"CANDIDATE_BACKLOG": "NAO SEI",
                                             "CANDIDATE_LOW_WATERMARK": "NAO SEI",
                                             "DISCOVERY_SIGNAL": "NAO SEI"}):
            s = SL.status()
        for k in OS_CAMPOS:
            self.assertIn(k, s, k)
        self.assertEqual(s["CANDIDATES_NEW"], 30)
        self.assertEqual(s["DEDUP_REJECTED"], 8)
        self.assertEqual(s["DISCOVERY_SERVICE"], "RAN")


if __name__ == "__main__":
    unittest.main(verbosity=2)
