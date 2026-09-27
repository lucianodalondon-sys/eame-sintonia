#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""UMA FONTE QUE REBENTA NAO MATA A VOLTA (PROVAS-P1, DEFEITO 3).

Medido antes da correccao, em copia descartavel: 3 tarefas, a do meio levanta
RuntimeError -> a volta inteira morria; IT-X-001 DONE, IT-BOOM IN_PROGRESS,
IT-X-003 PENDING sem ninguem lhe tocar; em 4 voltas seguidas a venenosa
ficava IN_PROGRESS para sempre; o RUN-LOG (escrito so no fim da volta) nao
recebia batimento e o supervisor contava a morte como SEM PROGRESSO — tres
fontes venenosas em 120 s mandavam o servico a BLOCKED por culpa das fontes.

Aqui tudo corre numa pasta descartavel (molde de test_ready_split.py:44-48):
fila, livro, evidencia, contratos, lotes, status, sinal e diario. A etapa
venenosa e injectada em W.ETAPAS; nenhuma etapa real corre, nada sai a rede.

    FONTE FALHOU != SERVICO MORREU.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import ciclo_continuo as CC          # noqa: E402
import fila as F                     # noqa: E402
import interface_collection as IC    # noqa: E402
import lifecycle as LC               # noqa: E402
import lotes as LOTES                # noqa: E402
import nivel_da_fila as NIVEL        # noqa: E402
import status_live as SL             # noqa: E402
import supervisor as S               # noqa: E402
import worker as W                   # noqa: E402
from test_canario_detalhe import CONTRATO  # noqa: E402

BOA_1, VENENOSA, BOA_3 = "IT-X-001", "IT-BOOM", "IT-X-003"


def _contrato(sid: str) -> dict:
    c = json.loads(json.dumps(CONTRATO))
    c["SOURCE_ID"] = sid
    c["SOURCE_CONTRACT_HASH"] = "hash-" + sid.lower()
    c["IDENTITY"]["DOCUMENT_ID"] = sid + ":URL:{doc.1}"
    return c


def etapa_com_veneno(chamadas: list):
    """A etapa injectada: regista quem foi chamado; rebenta so na venenosa."""
    def _fn(sid: str, contrato: dict):
        chamadas.append(sid)
        if sid == VENENOSA:
            raise RuntimeError("a fonte rebentou a meio da etapa")
        # A prova tem os QUATRO passos: desde a UNIFICACAO-V1 e a regua dos
        # quatro passos que promove, e este teste mede a volta, nao a regua.
        return "OK", {"PASS": True, "ALVO": "x", "DETAIL_GATE_PASSED": True,
                      "DETAIL_GATE": "prova", "DETAIL_ENUMERATED": 5,
                      "ITEM_ABERTO": {"URL": "https://ex.it/news/mosca-olivo-2026/", "HTTP": 200,
                                      "HTML_KIND": "CONTENT", "CAPA_OU_MATERIA": "MATERIA_PROVAVEL",
                                      "PARAGRAPH_CHARACTERS": 2000}}
    return _fn


class AVoltaSobrevive(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        d = Path(self.tmp.name)
        self._antes = (LC.LIVRO, F.FILA, W.EVIDENCIA, W.CONTRATOS, IC.CONTRATOS,
                       IC.CARACT, LOTES.LOTES, LOTES.ALLOC, SL.SAIDA, SL.LOTES,
                       NIVEL.SAIDA, CC.DIARIO, S.DIARIO, S.ESTADO, S.LOCK, S.PARAR)
        LC.LIVRO = d / "LEDGER.json"
        F.FILA = d / "QUEUE.json"
        W.EVIDENCIA = d / "EVIDENCE.json"
        # o pulso do worker e prova de vida para o supervisor: nunca o real
        self.addCleanup(setattr, W, "PULSO", W.PULSO)
        W.PULSO = d / "WORKER-HEARTBEAT.json"
        W.CONTRATOS = IC.CONTRATOS = d / "contracts.json"
        IC.CARACT = d / "nao-existe.json"
        LOTES.LOTES = SL.LOTES = d / "BATCHES.json"
        LOTES.ALLOC = d / "nao-existe-alloc.json"
        SL.SAIDA = d / "STATUS-LIVE.json"
        NIVEL.SAIDA = d / "DISCOVERY-SIGNAL.json"
        CC.DIARIO = S.DIARIO = d / "RUN-LOG.ndjson"
        S.ESTADO = d / "SUPERVISOR-STATE.json"
        self.addCleanup(setattr, S, "PULSO", S.PULSO)  # o pulso lido e batimento: nunca o real
        S.PULSO = d / "WORKER-HEARTBEAT.json"
        S.LOCK = d / "SUPERVISOR.lock"
        S.PARAR = d / "PARAR.flag"
        W.CONTRATOS.write_text(json.dumps({"FONTES": [
            _contrato(BOA_1), _contrato(VENENOSA), _contrato(BOA_3)]}), encoding="utf-8")
        for sid in (BOA_1, VENENOSA, BOA_3):
            LC.registar(sid, LC.CANARY_PENDING, "prova")
        # Prioridades decrescentes: a ordem da volta e BOA_1, VENENOSA, BOA_3.
        F.enfileirar(BOA_1, F.CANARY, priority=70)
        F.enfileirar(VENENOSA, F.CANARY, priority=60)
        F.enfileirar(BOA_3, F.CANARY, priority=50)
        self.chamadas: list = []
        self._etapas = mock.patch.dict(W.ETAPAS, {F.CANARY: etapa_com_veneno(self.chamadas)})
        self._etapas.start()
        self._procs: list[subprocess.Popen] = []

    def tearDown(self):
        self._etapas.stop()
        for p in self._procs:
            if p.poll() is None:
                p.kill()
            if p.stdout:
                p.stdout.close()
        (LC.LIVRO, F.FILA, W.EVIDENCIA, W.CONTRATOS, IC.CONTRATOS, IC.CARACT,
         LOTES.LOTES, LOTES.ALLOC, SL.SAIDA, SL.LOTES, NIVEL.SAIDA, CC.DIARIO,
         S.DIARIO, S.ESTADO, S.LOCK, S.PARAR) = self._antes
        self.tmp.cleanup()

    def _tarefa(self, sid: str) -> dict:
        return next(t for t in F._ler()["TAREFAS"] if t["SOURCE_ID"] == sid)

    # 1 -----------------------------------------------------------------------
    def test_1_as_tarefas_seguintes_da_mesma_volta_continuam(self):
        feitos = W.correr(pausa=0, verboso=False)
        self.assertEqual(self.chamadas, [BOA_1, VENENOSA, BOA_3],
                         "a volta parou na venenosa em vez de seguir")
        self.assertEqual([f["SOURCE_ID"] for f in feitos], [BOA_1, VENENOSA, BOA_3])
        self.assertEqual(self._tarefa(BOA_1)["STATUS"], F.DONE)
        self.assertEqual(self._tarefa(BOA_3)["STATUS"], F.DONE)
        venenosa = self._tarefa(VENENOSA)
        self.assertEqual(venenosa["STATUS"], F.WAITING_RETRY,
                         "a venenosa devia estar a esperar o relogio, nao %s" % venenosa["STATUS"])
        self.assertIn("RuntimeError", venenosa["LAST_ERROR"])
        # O desfecho diz que foi a FONTE, com a excecao escrita na evidencia.
        boom = next(f for f in feitos if f["SOURCE_ID"] == VENENOSA)
        self.assertEqual(boom["RESULTADO"], "RETRY")
        self.assertTrue(boom["FONTE_FALHOU"])
        provas = json.loads(W.EVIDENCIA.read_text(encoding="utf-8"))["PROVAS"]
        prova = next(p for p in provas if p["SOURCE_ID"] == VENENOSA)
        self.assertEqual(prova["DADOS"]["EXCECAO"], "RuntimeError")
        # As boas foram promovidas — a volta fez o trabalho todo.
        self.assertEqual(LC.estado_de(BOA_1), LC.READY_FOR_COLLECTION)
        self.assertEqual(LC.estado_de(BOA_3), LC.READY_FOR_COLLECTION)

    # 2 -----------------------------------------------------------------------
    def test_2_a_venenosa_incrementa_attempts_e_acaba_failed(self):
        """N voltas com o relogio a andar um dia por volta: ATTEMPTS sobe uma
        unidade por volta, nunca fica IN_PROGRESS, e fecha em FAILED — nao
        reentra para sempre."""
        relogio = [datetime.now(timezone.utc)]
        historico = []
        with mock.patch.object(F, "agora_utc", lambda: relogio[0]):
            for volta in range(1, 8):
                W.correr(pausa=0, verboso=False)
                t = self._tarefa(VENENOSA)
                historico.append((volta, t["ATTEMPTS"], t["STATUS"]))
                self.assertNotEqual(t["STATUS"], F.IN_PROGRESS,
                                    "ficou IN_PROGRESS na volta %d" % volta)
                if t["STATUS"] == F.FAILED:
                    break
                relogio[0] += timedelta(days=1)
        self.assertEqual(historico[-1][2], F.FAILED, "nunca chegou a FAILED: %s" % historico)
        # Uma tentativa por volta, sem saltos nem repeticoes.
        self.assertEqual([h[1] for h in historico], list(range(1, len(historico) + 1)), historico)
        self.assertEqual(self._tarefa(VENENOSA)["ATTEMPTS"], len(historico))
        self.assertIn("teto de", self._tarefa(VENENOSA)["LAST_ERROR"])
        # Depois de FAILED, mais uma volta nao lhe toca.
        antes = len(self.chamadas)
        with mock.patch.object(F, "agora_utc", lambda: relogio[0] + timedelta(days=30)):
            W.correr(pausa=0, verboso=False)
        self.assertEqual(len(self.chamadas), antes, "a venenosa FAILED voltou a ser chamada")

    # 3 -----------------------------------------------------------------------
    def test_3_a_volta_com_veneno_e_progresso_para_o_supervisor(self):
        """A volta inteira (ciclo_continuo.uma_volta) sobrevive, escreve o
        batimento com FONTES_REBENTARAM=1, e o supervisor le a morte seguinte
        do worker como morte COM progresso: contador de crashes a zero."""
        v = CC.uma_volta(pausa=0)
        self.assertEqual(v["TAREFAS_EXECUTADAS"], 3)
        self.assertEqual(v["FONTES_REBENTARAM"], 1)
        self.assertEqual(v["RESULTADOS"]["RETRY"], 1)
        linhas = [json.loads(l) for l in CC.DIARIO.read_text(encoding="utf-8").splitlines() if l.strip()]
        self.assertEqual(linhas[-1]["EVENTO"], "VOLTA")
        self.assertEqual(linhas[-1]["FONTES_REBENTARAM"], 1)

        # O worker morre DEPOIS desta volta. O supervisor tem de ver progresso.
        proc_morto = subprocess.Popen([sys.executable, "-c", "pass"],
                                      stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        self._procs.append(proc_morto)
        proc_morto.wait(timeout=10)
        estado = {"SUPERVISOR_STATE": "RUNNING", "RESTARTS_TOTAL": 1,
                  "CRASHES_SEM_PROGRESSO": [], "WORKER_PID": proc_morto.pid,
                  "LAST_PROGRESS_AT": None}
        with mock.patch.object(S, "_lancar_worker", side_effect=AssertionError("nao devia relancar")):
            accao, estado2, _ = S.uma_volta_sup(estado, proc_morto)
        self.assertEqual(estado2["CRASHES_SEM_PROGRESSO"], [],
                         "a volta com uma fonte venenosa contou como morte SEM progresso")
        self.assertNotEqual(accao, "BLOQUEADO")
        self.assertEqual(accao, "IDLE")  # 2 DONE + 1 a espera do relogio: nada elegivel
        morte = next(l for l in reversed(linhas_de(CC.DIARIO)) if l["EVENTO"] == "WORKER_MORTO")
        self.assertTrue(morte["PROGREDIU"])

    # 4 -----------------------------------------------------------------------
    def test_4_block_continua_sem_tentativas_novas(self):
        """NAO_INSISTIR preservado: um BLOCK devolvido pela etapa (AUTH) nao
        passa pelo try/except, nao ganha ATTEMPTS e nao reentra."""
        def _bloqueia(sid, contrato):
            self.chamadas.append(sid)
            return "BLOCK", {"CLASSE": "AUTH", "PORQUE": "401 na porta"}
        with mock.patch.dict(W.ETAPAS, {F.CANARY: _bloqueia}):
            W.correr(pausa=0, verboso=False)
            for sid in (BOA_1, VENENOSA, BOA_3):
                t = self._tarefa(sid)
                self.assertEqual(t["STATUS"], F.BLOCKED, sid)
                self.assertEqual(t["ATTEMPTS"], 0, sid)
                self.assertEqual(LC.estado_de(sid), LC.AUTH_BLOCK, sid)
            antes = len(self.chamadas)
            with mock.patch.object(F, "agora_utc", lambda: datetime.now(timezone.utc) + timedelta(days=30)):
                W.correr(pausa=0, verboso=False)
            self.assertEqual(len(self.chamadas), antes, "um BLOCK voltou a ser tentado")


def linhas_de(p: Path) -> list[dict]:
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


if __name__ == "__main__":
    unittest.main(verbosity=2)
