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
        # ⚠️ O WORKER E OUTRO PROCESSO: le a fila REAL do disco, nao este F.FILA.
        # Medido em 23/09: com o lancador verdadeiro, o worker filho pegava a
        # IT-T7-050 da fila real (WAITING_RETRY -> IN_PROGRESS) durante a suite.
        # O lancador continua o verdadeiro; so o filho e inofensivo, salvo cmd explicito.
        _lancar_real = S._lancar_worker
        S._lancar_worker = lambda pausa=1.0, cmd=None: _lancar_real(
            pausa, cmd=cmd or [sys.executable, "-c", "import time; time.sleep(30)"])
        self.addCleanup(setattr, S, "_lancar_worker", _lancar_real)
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
        W._pulso = lambda r: r.get("RESULTADO") != "EM_CURSO" and vistos.append(r["TASK_ID"])
        try:
            W.correr(pausa=0, verboso=False)
        finally:
            W._pulso = orig
        self.assertEqual(len(vistos), 3)


class TestPulsoDuranteATarefa(_Isolado):
    def _correr_com_tarefa_de(self, dur_s, teto_s):
        import time as _t
        F.enfileirar("IT-LONGA", F.CANARY, priority=1, motivo="t")
        pulsos = []
        orig = (W._pulso, W.executar_uma, W.PULSO_INTERVALO_S, W.TAREFA_MAX_S)
        W._pulso = lambda r: pulsos.append((_t.time(), r.get("RESULTADO")))
        W.PULSO_INTERVALO_S, W.TAREFA_MAX_S = 0.1, teto_s

        def _lenta(t, contratos):
            _t.sleep(dur_s)
            F.concluir(t["TASK_ID"], "ok")
            return {"TASK_ID": t["TASK_ID"], "SOURCE_ID": t["SOURCE_ID"],
                    "TASK_TYPE": t["TASK_TYPE"], "RESULTADO": "OK", "PORQUE": ""}
        W.executar_uma = _lenta
        W._arrancar_fio_de_pulso()        # fio proprio, ja com o intervalo curto
        t0 = _t.time()
        try:
            W.correr(pausa=0, verboso=False)
        finally:
            _t.sleep(0.3)
            (W._pulso, W.executar_uma, W.PULSO_INTERVALO_S, W.TAREFA_MAX_S) = orig
        return t0, [(t - t0, r) for t, r in pulsos]

    def test_correr_arranca_o_fio_de_pulso_sozinho(self):
        F.enfileirar("IT-SEM-CONTRATO-FIO", F.CANARY, priority=1, motivo="t")
        chamadas = []
        orig = (W._arrancar_fio_de_pulso, list(W._FIO_ARRANCADO))
        W._FIO_ARRANCADO.clear()
        W._arrancar_fio_de_pulso = lambda: (chamadas.append(1),
                                            W._FIO_ARRANCADO.append(1))
        try:
            W.correr(pausa=0, verboso=False)
        finally:
            W._arrancar_fio_de_pulso = orig[0]
            W._FIO_ARRANCADO[:] = orig[1]
        self.assertEqual(chamadas, [1])

    def test_tarefa_longa_pulsa_durante(self):
        _, p = self._correr_com_tarefa_de(1.2, teto_s=60)
        em_curso = [t for t, r in p if r == "EM_CURSO"]
        self.assertGreaterEqual(len(em_curso), 5, p)

    def test_tarefa_encravada_deixa_de_pulsar_no_teto(self):
        _, p = self._correr_com_tarefa_de(1.5, teto_s=0.3)
        em_curso = [t for t, r in p if r == "EM_CURSO"]
        self.assertTrue(em_curso, p)                     # pulsou no inicio
        self.assertLess(max(em_curso), 0.3 + 0.25, p)    # e calou-se no teto


class TestOrfaComServicoParado(_Isolado):
    def test_orfa_velha_e_recuperada_e_acorda_o_worker(self):
        t = F.enfileirar("IT-T7-107", F.BUILD_CONTRACT, priority=45, motivo="t")
        velho = (datetime.now(timezone.utc) - timedelta(minutes=31)).isoformat()
        d = F._ler()
        d["TAREFAS"][0].update({"STATUS": F.IN_PROGRESS, "UPDATED_AT": velho})
        F._gravar(d)
        self.assertEqual(F.elegiveis(), [])          # a orfa nao acorda ninguem
        estado = {"CRASHES_SEM_PROGRESSO": [], "RESTARTS_TOTAL": 0}
        orig = S._lancar_worker
        S._lancar_worker = lambda pausa=1.0, cmd=None: subprocess.Popen(
            [sys.executable, "-c", "pass"])
        try:
            accao, estado, novo = S.uma_volta_sup(estado, None)
        finally:
            S._lancar_worker = orig
        if novo:
            novo.wait(timeout=30)
        self.assertEqual(accao, "RELANCADO")
        self.assertEqual(F._ler()["TAREFAS"][0]["STATUS"], F.PENDING)
        evs = [json.loads(l)["EVENTO"] for l in
               S.DIARIO.read_text(encoding="utf-8").splitlines() if l.strip()]
        self.assertIn("ORFAS_RECUPERADAS", evs)

    def test_tarefa_em_curso_recente_nao_e_tocada(self):
        F.enfileirar("IT-X-9", F.CANARY, priority=1, motivo="t")
        d = F._ler()
        d["TAREFAS"][0]["STATUS"] = F.IN_PROGRESS    # UPDATED_AT = agora
        F._gravar(d)
        accao, _, _ = S.uma_volta_sup({"CRASHES_SEM_PROGRESSO": []}, None)
        self.assertEqual(accao, "IDLE")
        self.assertEqual(F._ler()["TAREFAS"][0]["STATUS"], F.IN_PROGRESS)


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
        # no INSTANTE do lancamento: o antigo ainda vive? (um so escritor)
        S._lancar_worker = lambda pausa=1.0, cmd=None: lancados.append(
            pendurado.poll() is None) or subprocess.Popen([sys.executable, "-c", "pass"])
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
        self.assertEqual(lancados, [False],
                         "o worker antigo ainda estava vivo quando o novo foi lancado")
        evs = [json.loads(l)["EVENTO"] for l in
               S.DIARIO.read_text(encoding="utf-8").splitlines() if l.strip()]
        i_term = evs.index("WORKER_PENDURADO_TERMINADO")
        self.assertLess(i_term, evs.index("WORKER_RELANCADO"))
        self.assertNotEqual(S._saida_limpa(None), True)


if __name__ == "__main__":
    unittest.main()
