#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O WORKER PENDURADO — M2d, 23/09/2026. Tres defeitos, tres provas.

    1. UM CANO SEM LEITOR NAO E UM LOG, E UM TRAVAO.
    2. O PULSO E POR TAREFA, NAO POR VOLTA.
    3. UM SO ESCRITOR: QUEM SE DA COMO MORTO, MORRE.

Tudo em TemporaryDirectory: fila, estado, diario, pulso e log do worker.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import fila as F          # noqa: E402
import supervisor as S    # noqa: E402
import worker as W        # noqa: E402

# um filho que escreve 200 KB — 50 vezes o cano do Windows (~4 KB) — e sai
FALADOR = [sys.executable, "-c",
           "import sys\nfor i in range(2000): print('x' * 99, flush=True)\nsys.exit(0)"]


class _Isolado(unittest.TestCase):
    def setUp(self):
        self._td = tempfile.TemporaryDirectory(prefix="pendurado-")
        t = Path(self._td.name)
        self._orig = (F.FILA, S.ESTADO, S.DIARIO, S.PARAR, S.PULSO, S.WORKER_LOG, W.PULSO)
        F.FILA = t / "fila.json"
        S.ESTADO = t / "estado.json"
        S.DIARIO = t / "diario.ndjson"
        S.PARAR = t / "PARAR.flag"
        S.PULSO = W.PULSO = t / "pulso.json"
        S.WORKER_LOG = t / "worker.log"
        F.FILA.write_text(json.dumps({"PROXIMO_ID": 1, "TAREFAS": []}), encoding="utf-8")

    def tearDown(self):
        (F.FILA, S.ESTADO, S.DIARIO, S.PARAR, S.PULSO, S.WORKER_LOG, W.PULSO) = self._orig
        self._td.cleanup()


class TestCanoSemLeitor(_Isolado):
    def test_worker_falador_termina_e_o_que_disse_fica_no_log(self):
        p = S._lancar_worker(cmd=FALADOR)
        try:
            rc = p.wait(timeout=30)       # com PIPE nao lido pendura aos ~4 KB
        finally:
            if p.poll() is None:
                p.kill()
                p.wait()
        self.assertEqual(rc, 0)
        self.assertGreaterEqual(S.WORKER_LOG.stat().st_size, 200_000)

    def test_log_grande_roda_no_arranque(self):
        S.WORKER_LOG.write_bytes(b"x" * (S.WORKER_LOG_MAX_BYTES + 1))
        p = S._lancar_worker(cmd=[sys.executable, "-c", "print('novo')"])
        p.wait(timeout=30)
        velho = S.WORKER_LOG.with_name(S.WORKER_LOG.name + ".1")
        self.assertTrue(velho.exists())
        self.assertIn("novo", S.WORKER_LOG.read_text(encoding="utf-8"))


class TestPulsoPorTarefa(_Isolado):
    def test_pulso_novo_vence_diario_velho(self):
        velho = datetime.now(timezone.utc) - timedelta(seconds=600)
        S.DIARIO.write_text(json.dumps({"EVENTO": "VOLTA", "AT": velho.isoformat()}) + "\n",
                            encoding="utf-8")
        W._pulso({"TASK_ID": "T1", "RESULTADO": "OK"})
        hb = S._ultimo_heartbeat()
        self.assertLess((datetime.now(timezone.utc) - hb).total_seconds(), 60)

    def test_worker_vivo_a_meio_de_uma_volta_longa(self):
        # PID vivo, ultima VOLTA ha 10 min, mas uma tarefa fechou agora
        p = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
        try:
            velho = datetime.now(timezone.utc) - timedelta(seconds=600)
            S.DIARIO.write_text(json.dumps({"EVENTO": "VOLTA", "AT": velho.isoformat()})
                                + "\n", encoding="utf-8")
            W._pulso({"TASK_ID": "T1", "RESULTADO": "OK"})
            self.assertTrue(S._worker_vivo({"WORKER_PID": p.pid}))
        finally:
            p.kill()
            p.wait()

    def test_correr_pulsa_a_cada_tarefa(self):
        for i in range(3):
            F.enfileirar("IT-SEM-CONTRATO-%d" % i, F.CANARY, priority=1, motivo="t")
        vistos = []
        orig = W._pulso
        W._pulso = lambda r: vistos.append(r["TASK_ID"])
        try:
            W.correr(pausa=0, verboso=False)
        finally:
            W._pulso = orig
        self.assertEqual(len(vistos), 3)


class TestUmSoEscritor(_Isolado):
    def test_pendurado_e_terminado_antes_de_relancar(self):
        pendurado = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"])
        velho = datetime.now(timezone.utc) - timedelta(seconds=S.HEARTBEAT_TIMEOUT_S + 60)
        S.DIARIO.write_text(json.dumps({"EVENTO": "VOLTA", "AT": velho.isoformat()}) + "\n",
                            encoding="utf-8")
        F.enfileirar("IT-X-1", F.CANARY, priority=1, motivo="t")
        estado = {"WORKER_PID": pendurado.pid, "CRASHES_SEM_PROGRESSO": [],
                  "LAST_PROGRESS_AT": velho.isoformat(), "RESTARTS_TOTAL": 0}
        lancados = []
        orig = S._lancar_worker
        S._lancar_worker = lambda pausa=1.0, cmd=None: lancados.append(1) or \
            subprocess.Popen([sys.executable, "-c", "pass"])
        try:
            accao, estado, novo = S.uma_volta_sup(estado, pendurado)
        finally:
            S._lancar_worker = orig
            if pendurado.poll() is None:
                pendurado.kill()
            pendurado.wait()
            if novo:
                novo.wait(timeout=30)
        self.assertEqual(accao, "RELANCADO")
        evs = [json.loads(l)["EVENTO"] for l in
               S.DIARIO.read_text(encoding="utf-8").splitlines() if l.strip()]
        i_term = evs.index("WORKER_PENDURADO_TERMINADO")
        self.assertLess(i_term, evs.index("WORKER_RELANCADO"))
        self.assertNotEqual(S._saida_limpa(None), True)


if __name__ == "__main__":
    unittest.main()
