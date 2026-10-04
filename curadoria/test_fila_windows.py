#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DOIS DEFEITOS DE WINDOWS — M2e, 23/09/2026.

    UM LEITOR A OLHAR NAO E UM ESCRITOR A MAIS: ESPERA-SE POR ELE.
    NAO CONSEGUI PERGUNTAR != NAO EXISTE.

1. os.replace da fila falhava com PermissionError [WinError 5] enquanto
   outro processo lia o ficheiro — o worker morria a meio de F.concluir.
2. _pid_no_so devolvia False em qualquer excepcao do tasklist (timeout sob
   carga) — o supervisor terminava um worker saudavel como «pendurado».

Tudo em TemporaryDirectory.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import fila as F          # noqa: E402
import supervisor as S    # noqa: E402

WINDOWS = os.name == "nt"


class _Isolado(unittest.TestCase):
    def setUp(self):
        self._td = tempfile.TemporaryDirectory(prefix="fila-windows-")
        # ⚠️ O WORKER E OUTRO PROCESSO: le a fila REAL do disco, nao este F.FILA.
        # Medido em 23/09: com o lancador verdadeiro, o worker filho pegava a
        # IT-T7-050 da fila real (WAITING_RETRY -> IN_PROGRESS) durante a suite.
        # O lancador continua o verdadeiro; so o filho e inofensivo, salvo cmd explicito.
        _lancar_real = S._lancar_worker
        S._lancar_worker = lambda pausa=1.0, cmd=None: _lancar_real(
            pausa, cmd=cmd or [sys.executable, "-c", "import time; time.sleep(30)"])
        self.addCleanup(setattr, S, "_lancar_worker", _lancar_real)
        t = Path(self._td.name)
        self.pasta = t
        self._orig = (F.FILA, S.ESTADO, S.DIARIO, S.PARAR, S.PULSO)
        F.FILA = t / "fila.json"
        S.ESTADO = t / "estado.json"
        S.DIARIO = t / "diario.ndjson"
        S.PARAR = t / "PARAR.flag"
        S.PULSO = t / "pulso.json"
        F._gravar({"PROXIMO_ID": 1, "TAREFAS": []})
        F.REPLACE_RETRIES.update({"GRAVAR": 0, "LER": 0})

    def tearDown(self):
        (F.FILA, S.ESTADO, S.DIARIO, S.PARAR, S.PULSO) = self._orig
        self._td.cleanup()


@unittest.skipUnless(WINDOWS, "o defeito e do Windows")
class TestLeitorNaoMataOEscritor(_Isolado):
    def test_leitor_a_segurar_o_ficheiro_espera_se_por_ele(self):
        fh = open(F.FILA, "r", encoding="utf-8")     # leitor de fora, open() normal
        threading.Timer(0.3, fh.close).start()        # larga-o daqui a 0,3 s
        F._gravar({"PROXIMO_ID": 7, "TAREFAS": []})   # antes: PermissionError
        self.assertEqual(F._ler()["PROXIMO_ID"], 7)
        self.assertGreater(F.REPLACE_RETRIES["GRAVAR"], 0)

    def test_leitor_que_nunca_larga_falha_alto_e_nada_se_perde(self):
        antes = F.FILA.read_text(encoding="utf-8")
        fh = open(F.FILA, "r", encoding="utf-8")
        try:
            with self.assertRaises(PermissionError):
                F._gravar({"PROXIMO_ID": 99, "TAREFAS": []})
        finally:
            fh.close()
        self.assertEqual(F.FILA.read_text(encoding="utf-8"), antes)
        self.assertEqual(list(self.pasta.glob("*.tmp")), [])   # sem lixo

    def test_leitor_da_casa_em_ciclo_nao_perde_escritas(self):
        # leitor da casa em ciclo (como o supervisor e o painel): 0 escritas perdidas
        parar = [False]

        def leitor():
            while not parar[0]:
                F._ler()
                time.sleep(0.01)
        th = threading.Thread(target=leitor, daemon=True)
        th.start()
        try:
            for i in range(200):
                F._gravar({"PROXIMO_ID": i, "TAREFAS": []})
        finally:
            parar[0] = True
            th.join()
        self.assertEqual(F._ler()["PROXIMO_ID"], 199)


class TestLeituraComPaciencia(_Isolado):
    def test_leitura_recusada_duas_vezes_e_tentada_de_novo(self):
        n = {"v": 0}
        caminho = F.FILA

        class _Teimoso(type(caminho)):
            def read_text(self, *a, **k):
                n["v"] += 1
                if n["v"] <= 2:
                    raise PermissionError(5, "ocupado")
                return super().read_text(*a, **k)
        F.FILA = _Teimoso(caminho)
        try:
            self.assertEqual(F._ler()["PROXIMO_ID"], 1)
        finally:
            F.FILA = caminho
        self.assertEqual(F.REPLACE_RETRIES["LER"], 2)


class TestTasklistNaoSeiNaoEMorto(_Isolado):
    def _tasklist_em_timeout(self):
        orig = S.subprocess.run

        def _lento(*a, **k):
            raise subprocess.TimeoutExpired(a[0], k.get("timeout"))
        S.subprocess.run = _lento
        self.addCleanup(setattr, S.subprocess, "run", orig)

    def _vivo(self):
        p = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
        self.addCleanup(lambda: (p.kill(), p.wait()))
        return p

    def _pulso_fresco(self):
        S.PULSO.write_text(json.dumps({"AT": datetime.now(timezone.utc).isoformat()}),
                           encoding="utf-8")

    def test_timeout_do_tasklist_e_nao_sei(self):
        p = self._vivo()
        self._tasklist_em_timeout()
        self.assertIsNone(S._pid_no_so(p.pid))

    def test_pid_inexistente_continua_a_ser_morto(self):
        self.assertIs(S._pid_no_so(4_000_000), False)

    def test_filho_proprio_vivo_nao_precisa_do_tasklist(self):
        p = self._vivo()
        self._pulso_fresco()
        self._tasklist_em_timeout()
        self.assertTrue(S._worker_vivo({"WORKER_PID": p.pid}, p))

    def test_filho_proprio_nao_depende_de_um_tasklist_que_erra(self):
        # tasklist responde, mas sem o PID (saida estranha): para um filho
        # proprio, a verdade e proc.poll(), nao o tasklist
        p = self._vivo()
        self._pulso_fresco()
        orig = S.subprocess.run
        S.subprocess.run = lambda *a, **k: subprocess.CompletedProcess(a[0], 0, "", "")
        self.addCleanup(setattr, S.subprocess, "run", orig)
        self.assertIs(S._pid_no_so(p.pid), False)          # o tasklist erra
        self.assertTrue(S._worker_vivo({"WORKER_PID": p.pid}, p))

    def test_filho_proprio_morto_e_morto(self):
        p = subprocess.Popen([sys.executable, "-c", "pass"])
        p.wait(timeout=30)
        self._pulso_fresco()
        self.assertFalse(S._worker_vivo({"WORKER_PID": p.pid}, p))

    def test_sem_popen_nao_sei_com_heartbeat_fresco_e_vivo(self):
        p = self._vivo()
        self._pulso_fresco()
        self._tasklist_em_timeout()
        self.assertTrue(S._worker_vivo({"WORKER_PID": p.pid}))

    def test_sem_popen_nao_sei_com_heartbeat_velho_e_pendurado(self):
        p = self._vivo()
        velho = datetime.now(timezone.utc) - timedelta(seconds=S.HEARTBEAT_TIMEOUT_S + 30)
        S.PULSO.write_text(json.dumps({"AT": velho.isoformat()}), encoding="utf-8")
        self._tasklist_em_timeout()
        self.assertFalse(S._worker_vivo({"WORKER_PID": p.pid}))

    def test_supervisor_nao_mata_worker_saudavel_com_tasklist_lento(self):
        p = self._vivo()
        self._pulso_fresco()
        self._tasklist_em_timeout()
        F.enfileirar("IT-X-1", F.CANARY, priority=1, motivo="t")
        estado = {"WORKER_PID": p.pid, "CRASHES_SEM_PROGRESSO": [], "RESTARTS_TOTAL": 1}
        accao, estado, proc = S.uma_volta_sup(estado, p)
        self.assertEqual(accao, "VIVO")
        self.assertIsNone(p.poll(), "o worker saudavel foi terminado")
        evs = S.DIARIO.read_text(encoding="utf-8") if S.DIARIO.exists() else ""
        self.assertNotIn("WORKER_PENDURADO_TERMINADO", evs)

    def test_lock_de_supervisor_vivo_nao_e_orfao_com_tasklist_lento(self):
        self._tasklist_em_timeout()
        dados = {"PID": os.getpid(), "STARTED_AT": datetime.now(timezone.utc).isoformat(),
                 "TOKEN": "t"}
        self.assertFalse(S._lock_e_orfao(dados))


if __name__ == "__main__":
    unittest.main()
