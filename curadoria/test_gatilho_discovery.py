#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Testes do gatilho do modo continuo (low watermark -> feeder/discovery).

Prova as quatro decisoes, com feeder e discovery INJECTADOS (nunca toca a rede)
e fila/candidatas em ficheiros temporarios (nunca toca a lane).
"""
import json
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))

import fila as F
import gatilho_discovery as GD


class TestGatilho(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="gatilho-test-"))
        self._orig = {"F.FILA": F.FILA, "GD.CANDIDATAS": GD.CANDIDATAS}
        F.FILA = self.tmp / "fila.json"
        GD.CANDIDATAS = self.tmp / "cand.json"
        self.feeder_calls = 0
        self.disc_calls = 0

    def tearDown(self):
        F.FILA = self._orig["F.FILA"]
        GD.CANDIDATAS = self._orig["GD.CANDIDATAS"]

    def _fila(self, n_pending):
        tarefas = [{"TASK_ID": "T%05d" % i, "SOURCE_ID": "CAND-%04d" % i,
                    "TASK_TYPE": F.QUALIFY, "PRIORITY": 30, "STATUS": F.PENDING,
                    "ATTEMPTS": 0, "NEXT_ATTEMPT_AT": None, "LAST_ERROR": None,
                    "MOTIVO": "", "CREATED_AT": "2026-09-21T00:00:00+00:00",
                    "UPDATED_AT": "2026-09-21T00:00:00+00:00"}
                   for i in range(n_pending)]
        F.FILA.write_text(json.dumps({"PROXIMO_ID": n_pending + 1,
                                      "TAREFAS": tarefas}), encoding="utf-8")

    def _candidatas(self, n_candidata):
        cs = [{"CANDIDATA_ID": "CAND-%04d" % i, "ESTADO": "CANDIDATA"}
              for i in range(n_candidata)]
        GD.CANDIDATAS.write_text(json.dumps({"CANDIDATAS": cs}), encoding="utf-8")

    def _feeder(self):
        self.feeder_calls += 1
        return {"TAREFAS_CRIADAS": 0}

    def _descobrir(self):
        self.disc_calls += 1
        return {"CANDIDATAS_NOVAS": 3}

    def test_queue_ok_nao_faz_nada(self):
        self._fila(50)
        self._candidatas(0)
        m = GD.talvez_alimentar({}, feeder_fn=self._feeder, descobrir_fn=self._descobrir)
        self.assertEqual(m["DECISAO"], "QUEUE_OK")
        self.assertEqual(self.feeder_calls, 0)
        self.assertEqual(self.disc_calls, 0)

    def test_fila_baixa_acervo_cheio_so_feeder(self):
        self._fila(2)
        self._candidatas(100)     # acervo cheio -> nao aciona discovery
        m = GD.talvez_alimentar({}, feeder_fn=self._feeder, descobrir_fn=self._descobrir)
        self.assertIn("FEEDER", m["ACCOES"])
        self.assertEqual(self.disc_calls, 0)
        self.assertTrue(m["DECISAO"].startswith("FEEDER_SO"))

    def test_fila_e_acervo_baixos_aciona_discovery(self):
        self._fila(2)
        self._candidatas(5)       # acervo baixo -> discovery
        estado = {}
        m = GD.talvez_alimentar(estado, feeder_fn=self._feeder, descobrir_fn=self._descobrir)
        self.assertEqual(m["DECISAO"], "DISCOVERY_ACCIONADA")
        self.assertEqual(self.disc_calls, 1)
        self.assertIn("LAST_DISCOVERY_AT", estado)

    def test_discovery_respeita_intervalo(self):
        self._fila(2)
        self._candidatas(5)
        agora = datetime.now(timezone.utc)
        estado = {"LAST_DISCOVERY_AT": (agora - timedelta(seconds=60)).isoformat()}
        m = GD.talvez_alimentar(estado, feeder_fn=self._feeder,
                                descobrir_fn=self._descobrir, agora=agora)
        self.assertEqual(m["DECISAO"], "DISCOVERY_EM_INTERVALO")
        self.assertEqual(self.disc_calls, 0, "nao pode crawlar dentro do intervalo")


if __name__ == "__main__":
    unittest.main(verbosity=2)
