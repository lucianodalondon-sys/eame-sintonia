#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Testes do defeito 2 — o painel nao pode ler JSON morto como processo vivo.

    UM JSON QUE DIZ RUNNING NAO E UM PROCESSO QUE EXISTE.

O caso medido pelo dono: SUPERVISOR-STATE.json diz SUPERVISOR_STATE=RUNNING,
WORKER_PID=104344, WORKER_ALIVE=true — e o SO diz que 104344 nao existe. O
painel mostrava RUNNING. Estes testes provam que a liveness vem SEMPRE do SO.
"""
import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))

import fila as F
import supervisor as S

PID_MORTO = 99999999  # PID que nao existe no SO


class TestLiveness(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(self.enterContext(tempfile.TemporaryDirectory(prefix="live-test-")))
        self._orig = {"ESTADO": S.ESTADO, "DIARIO": S.DIARIO,
                      "PARAR": S.PARAR, "F.FILA": F.FILA}
        S.ESTADO = self.tmp / "state.json"
        S.DIARIO = self.tmp / "run.ndjson"
        S.PARAR = self.tmp / "PARAR.flag"

    def tearDown(self):
        S.ESTADO = self._orig["ESTADO"]
        S.DIARIO = self._orig["DIARIO"]
        S.PARAR = self._orig["PARAR"]
        F.FILA = self._orig["F.FILA"]

    def _estado(self, **kw):
        S.ESTADO.write_text(json.dumps(kw, ensure_ascii=False), encoding="utf-8")

    def _hb(self, segundos_atras):
        at = (datetime.now(timezone.utc)
              - timedelta(seconds=segundos_atras)).isoformat()
        S.DIARIO.write_text(json.dumps({"EVENTO": "TESTE", "AT": at}) + "\n",
                            encoding="utf-8")

    def _fila_vazia(self):
        F.FILA = self.tmp / "fila-vazia.json"
        F.FILA.write_text(json.dumps({"PROXIMO_ID": 1, "TAREFAS": []}),
                          encoding="utf-8")

    def test_pid_morto_com_json_running_nao_e_running(self):
        """O defeito exacto do dono: JSON diz RUNNING/alive com PID morto."""
        self._estado(SUPERVISOR_STATE="RUNNING", WORKER_PID=PID_MORTO,
                     WORKER_ALIVE=True, SUPERVISOR_PID=PID_MORTO)
        self._hb(10)
        r = S.ler_estado_servico()
        self.assertFalse(r["WORKER_ALIVE"], "PID morto nao pode ser WORKER_ALIVE")
        self.assertFalse(r["SUPERVISOR_ALIVE"], "PID morto nao e supervisor vivo")
        self.assertEqual(r["SOURCE_CURATOR_SERVICE"], "STOPPED")
        self.assertEqual(r["SUPERVISOR_STATE"], "STOPPED")
        self.assertEqual(r["LIVENESS_SOURCE"], "DERIVED_FROM_OS_AT_READ_TIME")

    def test_heartbeat_velho_e_stale_com_delta_a_vista(self):
        """PID vivo mas heartbeat velho = worker PENDURADO, com o delta a vista."""
        self._estado(SUPERVISOR_STATE="RUNNING", WORKER_PID=os.getpid(),
                     SUPERVISOR_PID=os.getpid())
        self._hb(S.HEARTBEAT_TIMEOUT_S + 120)
        r = S.ler_estado_servico()
        self.assertEqual(r["WORKER_STATE"], "STALE")
        self.assertFalse(r["WORKER_ALIVE"], "heartbeat velho nao e worker vivo")
        self.assertTrue(r["HEARTBEAT_STALE"])
        self.assertIsNotNone(r["HEARTBEAT_AGE_S"])
        self.assertGreaterEqual(r["HEARTBEAT_AGE_S"], S.HEARTBEAT_TIMEOUT_S)

    def test_idle_nao_se_chama_stopped(self):
        """Supervisor vivo + worker sem trabalho = RUNNING/IDLE, nunca STOPPED."""
        self._fila_vazia()
        self._estado(SUPERVISOR_STATE="RUNNING", SUPERVISOR_PID=os.getpid(),
                     WORKER_PID=None)
        self._hb(5)
        r = S.ler_estado_servico()
        self.assertEqual(r["SUPERVISOR_STATE"], "RUNNING")
        self.assertEqual(r["SOURCE_CURATOR_SERVICE"], "RUNNING")
        self.assertEqual(r["WORKER_STATE"], "IDLE")
        self.assertEqual(r["QUEUE_ELIGIBLE_NOW"], 0)

    def test_worker_vivo_com_heartbeat_recente(self):
        self._estado(SUPERVISOR_STATE="RUNNING", WORKER_PID=os.getpid(),
                     SUPERVISOR_PID=os.getpid())
        self._hb(3)
        r = S.ler_estado_servico()
        self.assertTrue(r["WORKER_ALIVE"])
        self.assertEqual(r["WORKER_STATE"], "WORKING")


if __name__ == "__main__":
    unittest.main(verbosity=2)
