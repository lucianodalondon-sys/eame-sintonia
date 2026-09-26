#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ROBO-DIAGNOSTICO (25/09) — o robo ocioso nao pode parecer avariado.

Medido no vivo ce28040c (22:25 local): supervisor vivo, fila com 0 elegiveis, e o painel
a mostrar HEARTBEAT_AGE_S=3683 / STALE e, no ficheiro, WORKER_ALIVE=true com WORKER_PID=null.
Nada estava partido: o worker tinha saido limpo (rc 0) por falta de trabalho — e sem worker
ninguem bate. Estes testes provam as duas leituras novas:

    SEM WORKER VIVO, BATIMENTO PARADO E O ESPERADO.   (HEARTBEAT_APLICA = False)
    QUEM NAO ESTA VIVO, O FICHEIRO NAO DIZ QUE ESTA.  (WORKER_ALIVE = False no ficheiro)

HEARTBEAT_STALE continua igual (test_status_liveness e o red team leem-no).
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


class RoboOcioso(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(self.enterContext(tempfile.TemporaryDirectory(prefix="robo-diag-")))
        for nome in ("ESTADO", "DIARIO", "PARAR", "PULSO"):
            self.addCleanup(setattr, S, nome, getattr(S, nome))
        self.addCleanup(setattr, F, "FILA", F.FILA)
        S.ESTADO = self.tmp / "state.json"
        S.PULSO = self.tmp / "WORKER-HEARTBEAT.json"
        S.DIARIO = self.tmp / "run.ndjson"
        S.PARAR = self.tmp / "PARAR.flag"
        F.FILA = self.tmp / "fila-vazia.json"
        F.FILA.write_text(json.dumps({"PROXIMO_ID": 1, "TAREFAS": []}), encoding="utf-8")

    def _estado(self, **kw):
        S.ESTADO.write_text(json.dumps(kw, ensure_ascii=False), encoding="utf-8")

    def _hb(self, segundos_atras):
        at = (datetime.now(timezone.utc) - timedelta(seconds=segundos_atras)).isoformat()
        S.DIARIO.write_text(json.dumps({"EVENTO": "TESTE", "AT": at}) + "\n", encoding="utf-8")

    def test_ocioso_com_batimento_velho_diz_que_o_batimento_nao_se_aplica(self):
        """O caso medido: supervisor vivo, sem worker, fila vazia, batimento de ~1 h."""
        self._estado(SUPERVISOR_STATE="IDLE", SUPERVISOR_PID=os.getpid(), WORKER_PID=None,
                     WORKER_ALIVE=True, RESTARTS_TOTAL=138)
        self._hb(3683)
        r = S.ler_estado_servico()
        self.assertEqual(r["WORKER_STATE"], "IDLE")
        self.assertTrue(r["HEARTBEAT_STALE"], "HEARTBEAT_STALE nao muda de sentido")
        self.assertFalse(r["HEARTBEAT_APLICA"])
        self.assertIn("NAO e defeito", r["HEARTBEAT_LEITURA"])
        self.assertIn("arranque do worker", r["RESTARTS_TOTAL_CONTA"])

    def test_worker_vivo_o_batimento_aplica_se(self):
        """Com worker vivo o batimento conta: STALE continua a querer dizer pendurado."""
        self._estado(SUPERVISOR_STATE="RUNNING", SUPERVISOR_PID=os.getpid(), WORKER_PID=os.getpid())
        self._hb(S.HEARTBEAT_TIMEOUT_S + 120)
        r = S.ler_estado_servico()
        self.assertEqual(r["WORKER_STATE"], "STALE")
        self.assertTrue(r["HEARTBEAT_APLICA"])
        self.assertIn("pendurado", r["HEARTBEAT_LEITURA"])

    def test_sem_worker_vivo_o_ficheiro_deixa_de_dizer_worker_alive(self):
        """uma_volta_sup sem worker e sem trabalho: IDLE, e o ficheiro diz WORKER_ALIVE=false."""
        estado = {"SUPERVISOR_STATE": "RUNNING", "WORKER_ALIVE": True, "WORKER_PID": None,
                  "RESTARTS_TOTAL": 5, "CRASHES_SEM_PROGRESSO": []}
        accao, estado, proc = S.uma_volta_sup(estado, None)
        self.assertEqual(accao, "IDLE")
        self.assertIsNone(proc, "fila vazia nao lanca worker")
        self.assertFalse(estado["WORKER_ALIVE"])
        gravado = json.loads(S.ESTADO.read_text(encoding="utf-8"))
        self.assertFalse(gravado["WORKER_ALIVE"])
        self.assertEqual(gravado["RESTARTS_TOTAL"], 5, "IDLE nao conta reinicio")


if __name__ == "__main__":
    unittest.main(verbosity=2)
