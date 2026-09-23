#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O PAINEL PERGUNTA AO SO — nunca herda verde de um ficheiro velho.

    FICHEIRO DIZ RUNNING != PROCESSO EXISTE.

O SO e simulado (`_pid_no_so` / `_proc_e_python`), o ficheiro de estado e o
run log vivem numa pasta descartavel. Cada caso e o que o painel tem de dizer.
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import supervisor as SUP  # noqa: E402


class OPainel(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        d = Path(self.tmp.name)
        self._antes = (SUP.ESTADO, SUP.DIARIO)
        SUP.ESTADO, SUP.DIARIO = d / "S.json", d / "L.ndjson"

    def tearDown(self):
        SUP.ESTADO, SUP.DIARIO = self._antes
        self.tmp.cleanup()

    def _estado(self, **campos):
        SUP.ESTADO.write_text(json.dumps(campos), encoding="utf-8")

    def _batimento(self, ha_segundos: int):
        at = (datetime.now(timezone.utc) - timedelta(seconds=ha_segundos)).isoformat()
        SUP.DIARIO.write_text(json.dumps({"EVENTO": "VOLTA", "AT": at}) + "\n", encoding="utf-8")

    def _ler(self, vivos: set):
        with mock.patch.object(SUP, "_pid_no_so", lambda pid: pid in vivos), \
             mock.patch.object(SUP, "_proc_e_python", lambda pid: pid in vivos):
            return SUP.ler_estado_servico()

    def test_1_ficheiro_RUNNING_com_pid_inexistente_e_STOPPED_BROKEN(self):
        """O achado que originou a missao: RUNNING + WORKER_PID 97820, PID morto."""
        self._estado(SUPERVISOR_STATE="RUNNING", WORKER_PID=97820, SUPERVISOR_PID=1)
        self._batimento(10)
        r = self._ler(vivos=set())
        self.assertEqual("STOPPED_BROKEN", r["SERVICE_DIAGNOSIS"])
        self.assertFalse(r["WORKER_ALIVE"])
        self.assertFalse(r["SUPERVISOR_ALIVE"])
        self.assertEqual("RUNNING", r["SERVICE_STATE_IN_FILE"], "o que o ficheiro dizia fica visivel")

    def test_2_RUNNING_com_os_dois_vivos_e_batimento_fresco_e_RUNNING(self):
        self._estado(SUPERVISOR_STATE="RUNNING", WORKER_PID=200, SUPERVISOR_PID=100)
        self._batimento(10)
        r = self._ler(vivos={100, 200})
        self.assertEqual("RUNNING", r["SERVICE_DIAGNOSIS"])
        self.assertTrue(r["HEARTBEAT_FRESH"])

    def test_3_RUNNING_com_worker_vivo_mas_batimento_velho_e_STOPPED_BROKEN(self):
        self._estado(SUPERVISOR_STATE="RUNNING", WORKER_PID=200, SUPERVISOR_PID=100)
        self._batimento(SUP.HEARTBEAT_TIMEOUT_S + 60)
        r = self._ler(vivos={100, 200})
        self.assertEqual("STOPPED_BROKEN", r["SERVICE_DIAGNOSIS"], "um processo pendurado nao e RUNNING")
        self.assertFalse(r["HEARTBEAT_FRESH"])

    def test_4_IDLE_com_supervisor_vivo_e_IDLE_e_com_supervisor_morto_e_STOPPED_BROKEN(self):
        self._estado(SUPERVISOR_STATE="IDLE", WORKER_PID=None, SUPERVISOR_PID=100)
        self.assertEqual("IDLE", self._ler(vivos={100})["SERVICE_DIAGNOSIS"])
        self.assertEqual("STOPPED_BROKEN", self._ler(vivos=set())["SERVICE_DIAGNOSIS"])

    def test_5_STOPPED_pela_bandeira_e_STOPPED_FINISHED(self):
        self._estado(SUPERVISOR_STATE="STOPPED", WORKER_PID=None, SUPERVISOR_PID=100)
        self.assertEqual("STOPPED_FINISHED", self._ler(vivos=set())["SERVICE_DIAGNOSIS"])

    def test_6_pid_reciclado_por_processo_que_nao_e_python_nao_conta_como_vivo(self):
        self._estado(SUPERVISOR_STATE="RUNNING", WORKER_PID=200, SUPERVISOR_PID=100)
        self._batimento(10)
        with mock.patch.object(SUP, "_pid_no_so", lambda pid: True), \
             mock.patch.object(SUP, "_proc_e_python", lambda pid: pid == 100):
            r = SUP.ler_estado_servico()
        self.assertFalse(r["WORKER_ALIVE"])
        self.assertEqual("STOPPED_BROKEN", r["SERVICE_DIAGNOSIS"])

    def test_7_sem_ficheiro_e_UNKNOWN_nao_verde(self):
        r = self._ler(vivos={1, 2, 3})
        self.assertEqual("UNKNOWN", r["SERVICE_DIAGNOSIS"])
        self.assertFalse(r["WORKER_ALIVE"])


if __name__ == "__main__":
    unittest.main()
