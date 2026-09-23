#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O WORKER OCIOSO QUE DESLIGAVA O GATILHO — M2c, 23/09/2026.

    SEM TRABALHO A VISTA, O WORKER DEVOLVE A CADEIRA.
    SAIR NAO E MORRER.

Tudo isolado em TemporaryDirectory: fila, estado, diario e PARAR.flag do
supervisor e do ciclo sao redireccionados. Nenhum processo real de worker e
lancado aqui (o ensaio com processos reais e `ensaiar_gatilho_ocioso.py`, que
corre numa COPIA da worktree).
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

import ciclo_continuo as C   # noqa: E402
import fila as F             # noqa: E402
import supervisor as S       # noqa: E402


def _proc(rc: int) -> subprocess.Popen:
    p = subprocess.Popen([sys.executable, "-c", "import sys; sys.exit(%d)" % rc],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    p.wait(timeout=30)
    return p


class _Isolado(unittest.TestCase):
    def setUp(self):
        self._td = tempfile.TemporaryDirectory(prefix="ocioso-")
        t = Path(self._td.name)
        self._orig = (F.FILA, S.ESTADO, S.DIARIO, S.PARAR, C.DIARIO, C.PARAR)
        F.FILA = t / "fila.json"
        S.ESTADO = t / "estado.json"
        self.addCleanup(setattr, S, "PULSO", S.PULSO)  # o pulso lido e batimento: nunca o real
        S.PULSO = t / "WORKER-HEARTBEAT.json"
        S.DIARIO = C.DIARIO = t / "diario.ndjson"
        S.PARAR = C.PARAR = t / "PARAR.flag"
        F.FILA.write_text(json.dumps({"PROXIMO_ID": 1, "TAREFAS": []}),
                          encoding="utf-8")

    def tearDown(self):
        (F.FILA, S.ESTADO, S.DIARIO, S.PARAR, C.DIARIO, C.PARAR) = self._orig
        self._td.cleanup()

    def _eventos(self):
        if not S.DIARIO.exists():
            return []
        return [json.loads(l) for l in S.DIARIO.read_text(encoding="utf-8").splitlines()
                if l.strip()]

    def _hb(self):
        # o worker escreveu uma VOLTA; o supervisor ja a viu (LAST_PROGRESS_AT)
        at = datetime.now(timezone.utc).isoformat()
        with S.DIARIO.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({"EVENTO": "VOLTA", "AT": at}) + "\n")
        return at


class TestSaidaOciosaNaoECrash(_Isolado):
    def _tres_saidas(self, rc):
        estado = {"SUPERVISOR_STATE": "RUNNING", "RESTARTS_TOTAL": 3,
                  "CRASHES_SEM_PROGRESSO": []}
        accoes, hooks = [], []
        for _ in range(S.CRASH_MAX):
            hb = self._hb()
            estado["LAST_PROGRESS_AT"] = hb       # o que a volta VIVO grava
            p = _proc(rc)
            estado["WORKER_PID"] = p.pid
            a, estado, novo = S.uma_volta_sup(
                estado, p, hook_fila_vazia=lambda: hooks.append(1))
            accoes.append(a)
            self.assertIsNone(novo)
        # e a volta seguinte, com trabalho, decide relancar ou bloquear
        F.enfileirar("IT-X-001", F.CANARY, priority=1, motivo="teste")
        estado["WORKER_PID"] = None
        orig = S._lancar_worker
        S._lancar_worker = lambda pausa=1.0: _proc(0)
        try:
            a, estado, _ = S.uma_volta_sup(estado, None)
        finally:
            S._lancar_worker = orig
        accoes.append(a)
        return accoes, estado, hooks

    def test_tres_saidas_ociosas_em_120s_nao_bloqueiam(self):
        accoes, estado, hooks = self._tres_saidas(0)
        self.assertEqual(accoes, ["IDLE", "IDLE", "IDLE", "RELANCADO"])
        self.assertEqual(estado["CRASHES_SEM_PROGRESSO"], [])
        self.assertEqual(len(hooks), 3)                  # o gatilho correu 3 vezes
        evs = [e["EVENTO"] for e in self._eventos()]
        self.assertEqual(evs.count("WORKER_SAIU_LIMPO"), 3)

    def test_controlo_tres_crashes_sem_progresso_bloqueiam(self):
        accoes, estado, _ = self._tres_saidas(1)
        self.assertEqual(accoes[-1], "BLOQUEADO")
        self.assertEqual(len(estado["CRASHES_SEM_PROGRESSO"]), S.CRASH_MAX)

    def test_saida_limpa_so_com_rc_zero(self):
        self.assertTrue(S._saida_limpa(0))
        for rc in (1, 2, -9, 3221225786, None):
            self.assertFalse(S._saida_limpa(rc), rc)

    def test_supervisor_lanca_o_worker_com_saida_ociosa(self):
        capturado = {}
        orig = subprocess.Popen

        def _falso(cmd, **kw):
            capturado["cmd"] = cmd
            return orig([sys.executable, "-c", "pass"],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        S.subprocess.Popen = _falso
        try:
            S._lancar_worker(0.1).wait(timeout=30)
        finally:
            S.subprocess.Popen = orig
        self.assertIn("--sair-quando-ocioso", capturado["cmd"])


class TestCicloSaiQuandoOcioso(_Isolado):
    def _correr(self, argv, volta, prox):
        orig = (C.uma_volta, C._proximo_relogio, C.time.sleep, sys.argv)
        dormiu = []

        def _dormir(s):
            dormiu.append(s)
            raise KeyboardInterrupt        # a primeira espera acaba o teste
        C.uma_volta = lambda pausa: dict(volta)
        C._proximo_relogio = lambda: prox
        C.time.sleep = _dormir
        sys.argv = ["ciclo_continuo.py"] + argv
        try:
            rc = C.main()
        except KeyboardInterrupt:
            rc = "DORMIU"
        finally:
            C.uma_volta, C._proximo_relogio, C.time.sleep, sys.argv = orig
        return rc, dormiu

    VAZIA = {"QUEUE_ELIGIBLE_NOW": 0, "TAREFAS_EXECUTADAS": 0, "RESULTADOS": {},
             "READY_TOTAL": 0, "QUEUE_WAITING_RETRY": 0}

    def test_fila_vazia_sem_relogio_sai_com_rc_0(self):
        rc, dormiu = self._correr(["--sair-quando-ocioso"], self.VAZIA, None)
        self.assertEqual((rc, dormiu), (0, []))
        ev = [e for e in self._eventos() if e["EVENTO"] == "WORKER_OCIOSO_SAIU"]
        self.assertEqual(len(ev), 1)

    def test_relogio_longe_sai(self):
        rc, _ = self._correr(["--sair-quando-ocioso"], self.VAZIA, 6 * 3600.0)
        self.assertEqual(rc, 0)

    def test_relogio_dentro_da_espera_fica_e_dorme(self):
        rc, dormiu = self._correr(["--sair-quando-ocioso"], self.VAZIA, 40.0)
        self.assertEqual(rc, "DORMIU")
        self.assertEqual(dormiu, [41.0])

    def test_sem_a_opcao_mantem_o_comportamento_antigo(self):
        rc, dormiu = self._correr([], self.VAZIA, None)
        self.assertEqual((rc, dormiu), ("DORMIU", [C.ESPERA_MAX]))

    def test_com_trabalho_elegivel_nunca_sai(self):
        cheia = dict(self.VAZIA, QUEUE_ELIGIBLE_NOW=3)
        orig = C.uma_volta
        n = {"v": 0}

        def _duas(pausa):
            n["v"] += 1
            if n["v"] > 2:
                raise KeyboardInterrupt
            return dict(cheia)
        C.uma_volta = _duas
        sys_argv = sys.argv
        sys.argv = ["ciclo_continuo.py", "--sair-quando-ocioso"]
        try:
            with self.assertRaises(KeyboardInterrupt):
                C.main()
        finally:
            C.uma_volta, sys.argv = orig, sys_argv
        self.assertFalse([e for e in self._eventos()
                          if e["EVENTO"] == "WORKER_OCIOSO_SAIU"])


class TestProximoRelogioReal(_Isolado):
    def test_le_o_waiting_retry_da_fila(self):
        t = F.enfileirar("IT-X-002", F.CANARY, priority=1, motivo="teste")
        F.adiar(t["TASK_ID"], retry_after_s=3600)
        prox = C._proximo_relogio()
        self.assertTrue(3500 < prox <= 3600, prox)


if __name__ == "__main__":
    unittest.main()
