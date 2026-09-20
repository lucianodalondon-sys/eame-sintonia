#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FASE 15 — ATAQUES AO CONTRATO CURATOR <-> COLLECTION.

O contrato tem duas frases. Estes testes tentam fazer cada uma mentir.
"""
from __future__ import annotations

import importlib
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))

import fila as F                      # noqa: E402
import interface_collection as IC     # noqa: E402
import lifecycle as LC                # noqa: E402


class Isolada(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        d = Path(self.tmp.name)
        importlib.reload(LC)
        importlib.reload(F)
        importlib.reload(IC)
        LC.LIVRO = d / "LEDGER.json"
        F.FILA = d / "QUEUE.json"
        IC.LC, IC.F = LC, F
        IC.CONTRATOS = RAIZ / "curadoria" / "italy_contracts_curator.json"

    def tearDown(self):
        self.tmp.cleanup()

    def _pronta(self, sid="IT-T10-018"):
        LC.registar(sid, LC.CANARY_PENDING, "pronta")
        LC.registar(sid, LC.READY_FOR_COLLECTION, "canario", evidence_ref="EV-1")
        return sid


class READYeDerivadoNaoCarimbado(Isolada):
    def test_uma_fonte_degradada_sai_de_READY_no_mesmo_instante(self):
        sid = self._pronta()
        self.assertIn(sid, [r["SOURCE_ID"] for r in IC.ready_sources()])
        IC.source_repair_needed(sid, "HTTP_404", run_id="RUN-1")
        self.assertNotIn(sid, [r["SOURCE_ID"] for r in IC.ready_sources()],
                         "READY era um carimbo velho, nao uma consequencia")

    def test_READY_traz_a_evidencia_que_o_promoveu(self):
        sid = self._pronta()
        r = IC.ready_sources()[0]
        self.assertEqual(r["EVIDENCE_REF"], "EV-1")
        self.assertNotEqual(r["LAST_SUCCESSFUL_CANARY_AT"], "NAO SEI")


class ACollectionNaoAtravessaAFronteira(Isolada):
    def test_reportar_quebra_de_fonte_que_nunca_foi_READY_e_recusado(self):
        LC.registar("IT-T7-800", LC.CANARY_PENDING, "nem chegou a READY")
        r = IC.source_repair_needed("IT-T7-800", "HTTP_500")
        self.assertFalse(r["ACEITE"])
        self.assertEqual(LC.estado_de("IT-T7-800"), LC.CANARY_PENDING)

    def test_reportar_quebra_NAO_repara_nem_promove(self):
        sid = self._pronta()
        IC.source_repair_needed(sid, "WAF_BLOCK", run_id="RUN-9")
        self.assertEqual(LC.estado_de(sid), LC.DEGRADED,
                         "a Collection reparou sozinha — fronteira furada")

    def test_a_quebra_cria_trabalho_para_o_CURATOR(self):
        sid = self._pronta()
        r = IC.source_repair_needed(sid, "HTTP_404", run_id="RUN-3")
        t = [x for x in F.elegiveis() if x["TASK_ID"] == r["TASK_ID"]]
        self.assertEqual(len(t), 1)
        self.assertEqual(t[0]["TASK_TYPE"], F.REPAIR)


class OCicloFechaEDepende_DeNovoCanario(Isolada):
    def test_ciclo_completo_READY_DEGRADED_REPAIRING_READY(self):
        sid = self._pronta()
        IC.source_repair_needed(sid, "HTTP_404", run_id="RUN-1")
        self.assertEqual(IC.metricas_operacionais()["READY"], 0)
        self.assertEqual(IC.metricas_operacionais()["DEGRADED"], 1)

        LC.registar(sid, LC.REPAIRING, "curator assume")
        with self.assertRaises(ValueError):
            LC.registar(sid, LC.READY_FOR_COLLECTION, "sem canario novo")

        LC.registar(sid, LC.READY_FOR_COLLECTION, "canario novo passou",
                    evidence_ref="EV-2")
        self.assertEqual(IC.metricas_operacionais()["READY"], 1)
        self.assertEqual(IC.ready_sources()[0]["EVIDENCE_REF"], "EV-2",
                         "a evidencia ficou a do canario VELHO")


class MetricasNaoEscondemNada(Isolada):
    def test_todos_os_contadores_aparecem_mesmo_a_zero(self):
        self._pronta()
        m = IC.metricas_operacionais()
        for k in ("READY", "DEGRADED", "REPAIRING", "POLICY_BLOCK",
                  "AUTH_BLOCK", "CAPABILITY_BLOCK", "QUEUE_WAITING_RETRY"):
            self.assertIn(k, m)
        self.assertEqual(m["DEGRADED"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
