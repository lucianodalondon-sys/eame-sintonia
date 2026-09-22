#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Os 12 testes da telemetria (missao TELEMETRIA-V1). ZERO LLM, tudo sintetico.

Cada teste isola o ledger/fila/run-log/estado em ficheiros temporarios — nunca
lê a lane viva. As definições são as de `telemetria.py`.
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
import lifecycle as LC
import supervisor as S
import telemetria as T

PID_MORTO = 99999999
AGORA = datetime(2026, 9, 22, 12, 0, 0, tzinfo=timezone.utc)


def _tr(sid, novo, quando, *, reason="", ev=None, prev=None):
    return {"SOURCE_ID": sid, "PREVIOUS_STATE": prev, "NEW_STATE": novo,
            "REASON": reason, "EVIDENCE_REF": ev, "OBSERVED_AT": quando.isoformat(),
            "OWNER": "SOURCE_CURATOR", "VERSION": "v1"}


class TestTelemetria(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="telem-test-"))
        self._orig = {"LEDGER": T.LEDGER, "RUNLOG": T.RUNLOG, "CANDID": T.CANDID,
                      "CKPT": T.CHECKPOINT_HIST, "FILA": F.FILA,
                      "ESTADO": S.ESTADO, "DIARIO": S.DIARIO, "PARAR": S.PARAR}
        T.LEDGER = self.tmp / "ledger.json"
        T.RUNLOG = self.tmp / "run.ndjson"
        T.CANDID = self.tmp / "cand.json"
        T.CHECKPOINT_HIST = self.tmp / "ckpt.ndjson"
        F.FILA = self.tmp / "fila.json"
        S.ESTADO = self.tmp / "state.json"
        S.DIARIO = self.tmp / "sup-run.ndjson"
        S.PARAR = self.tmp / "PARAR.flag"
        self._ledger([])
        self._fila([])
        self._estado(vivo=True, hb_seg=5)

    def tearDown(self):
        for k, v in self._orig.items():
            if k in ("LEDGER", "RUNLOG", "CANDID", "CKPT"):
                setattr(T, {"CKPT": "CHECKPOINT_HIST"}.get(k, k), v)
            elif k == "FILA":
                F.FILA = v
            else:
                setattr(S, k, v)

    # --- fixtures ---
    def _ledger(self, transicoes):
        T.LEDGER.write_text(json.dumps({"TRANSICOES": transicoes}, ensure_ascii=False),
                            encoding="utf-8")

    def _fila(self, tarefas):
        F.FILA.write_text(json.dumps({"PROXIMO_ID": len(tarefas) + 1,
                                      "TAREFAS": tarefas}, ensure_ascii=False),
                          encoding="utf-8")

    def _estado(self, *, vivo, hb_seg):
        pid = os.getpid() if vivo else PID_MORTO
        S.ESTADO.write_text(json.dumps({
            "SUPERVISOR_STATE": "RUNNING", "SUPERVISOR_PID": pid,
            "WORKER_PID": None, "SUPERVISOR_STARTED_AT": (AGORA - timedelta(hours=6)).isoformat(),
        }, ensure_ascii=False), encoding="utf-8")
        at = (AGORA - timedelta(seconds=hb_seg)).isoformat()
        S.DIARIO.write_text(json.dumps({"EVENTO": "T", "AT": at}) + "\n", encoding="utf-8")

    def _qtask(self, tid, created, status=F.DONE):
        return {"TASK_ID": tid, "SOURCE_ID": "CAND-%s" % tid, "TASK_TYPE": F.QUALIFY,
                "PRIORITY": 30, "STATUS": status, "ATTEMPTS": 0, "NEXT_ATTEMPT_AT": None,
                "LAST_ERROR": None, "MOTIVO": "", "CREATED_AT": created.isoformat(),
                "UPDATED_AT": created.isoformat()}

    # 1
    def test_10_qualify_concluidas_sao_10(self):
        tr = [_tr("IT-T5-%03d" % i, LC.CONTRACT_PENDING, AGORA - timedelta(minutes=30),
                  reason="QUALIFY: CAND-%d -> IT-T5-%03d" % (i, i)) for i in range(10)]
        self._ledger(tr)
        m = T.metricas(AGORA)
        self.assertEqual(m["JANELA_24H"]["QUALIFY_COMPLETED"], 10)
        self.assertEqual(m["JANELA_1H"]["QUALIFY_COMPLETED"], 10)

    # 2
    def test_ready_e_subconjunto_das_concluidas(self):
        tr = []
        for i in range(5):
            sid = "IT-T5-%03d" % i
            tr.append(_tr(sid, LC.CONTRACT_PENDING, AGORA - timedelta(minutes=40),
                          reason="QUALIFY: -> %s" % sid))
        # so 2 chegaram a READY (via canario, mais tarde)
        for i in range(2):
            tr.append(_tr("IT-T5-%03d" % i, LC.READY_FOR_COLLECTION,
                          AGORA - timedelta(minutes=10), ev="EV-x-CANARY-1"))
        self._ledger(tr)
        d = AGORA - timedelta(hours=24)
        ready = {r["SOURCE_ID"] for r in T.ready_sources_janela(tr, d, AGORA)}
        qual = T.qualify_sources_janela(tr, d, AGORA)
        self.assertTrue(ready <= qual, "toda READY tem de ter sido qualificada")
        m = T.metricas(AGORA)
        self.assertLessEqual(m["JANELA_24H"]["READY_CURRENT"], m["JANELA_24H"]["QUALIFY_COMPLETED"])

    # 3
    def test_duplicata_nao_vira_candidata_nova(self):
        # duas REALIMENTACAO: a segunda com discovery a devolver 0 novas (duplicatas)
        rl = [{"EVENTO": "REALIMENTACAO", "AT": (AGORA - timedelta(minutes=20)).isoformat(),
               "DISCOVERY": {"CANDIDATAS_NOVAS": 3, "CRAWL": 5}},
              {"EVENTO": "REALIMENTACAO", "AT": (AGORA - timedelta(minutes=10)).isoformat(),
               "DISCOVERY": {"CANDIDATAS_NOVAS": 0, "CRAWL": 5}}]
        T.RUNLOG.write_text("\n".join(json.dumps(x) for x in rl) + "\n", encoding="utf-8")
        m = T.metricas(AGORA)
        # so as 3 realmente novas contam; a duplicata (0 novas) nao infla
        self.assertEqual(m["JANELA_1H"]["NEW_CANDIDATES"], 3)

    # 4
    def test_janela_1h_nao_inclui_evento_antigo(self):
        tr = [_tr("IT-T5-001", LC.READY_FOR_COLLECTION, AGORA - timedelta(hours=3),
                  ev="EV-x-CANARY-1")]
        self._ledger(tr)
        m = T.metricas(AGORA)
        self.assertEqual(m["JANELA_1H"]["READY_CURRENT"], 0)
        self.assertEqual(m["JANELA_24H"]["READY_CURRENT"], 1)

    # 5
    def test_janela_24h_inclui_evento_correto(self):
        tr = [_tr("IT-T5-001", LC.READY_FOR_COLLECTION, AGORA - timedelta(hours=10),
                  ev="EV-x-CANARY-1")]
        self._ledger(tr)
        m = T.metricas(AGORA)
        self.assertEqual(m["JANELA_24H"]["READY_CURRENT"], 1)

    # 6
    def test_reiniciar_painel_nao_zera_historico(self):
        T.talvez_checkpoint(T.metricas(AGORA), motivo="a", forcar=True)
        # "reiniciar o painel" = reler o ficheiro do zero
        hist = T.historico_checkpoints()
        self.assertEqual(len(hist), 1)
        self.assertEqual(len(T.historico_checkpoints()), 1)

    # 7
    def test_reiniciar_supervisor_nao_zera_producao_24h(self):
        tr = [_tr("IT-T5-%03d" % i, LC.READY_FOR_COLLECTION, AGORA - timedelta(hours=2),
                  ev="EV-x-CANARY-1") for i in range(4)]
        self._ledger(tr)
        # supervisor "reiniciou": sessao nova (comecou agora), mas 24h vem do ledger
        S.ESTADO.write_text(json.dumps({"SUPERVISOR_STATE": "RUNNING",
            "SUPERVISOR_PID": os.getpid(),
            "SUPERVISOR_STARTED_AT": (AGORA - timedelta(minutes=1)).isoformat()},
            ensure_ascii=False), encoding="utf-8")
        m = T.metricas(AGORA)
        self.assertEqual(m["JANELA_24H"]["READY_CURRENT"], 4, "24h vem do ledger, sobrevive ao restart")
        self.assertEqual(m["SESSAO"]["READY_CURRENT_SESSION"], 0, "sessao nova, mas nao apaga o 24h")

    # 8
    def test_json_stale_nao_diz_running_se_processo_morreu(self):
        self._estado(vivo=False, hb_seg=5)   # SUPERVISOR_PID morto
        m = T.metricas(AGORA)
        self.assertNotEqual(m["AGORA"]["SERVICE_STATE"], "RUNNING")
        self.assertFalse(m["AGORA"]["SUPERVISOR_ALIVE"])

    # 9
    def test_fila_zero_processo_vivo_e_idle_nao_stopped(self):
        self._fila([])
        m = T.metricas(AGORA)
        self.assertEqual(m["AGORA"]["SERVICE_STATE"], "RUNNING")
        self.assertEqual(m["PRODUCTIVITY_STATE"], "IDLE_NO_WORK")

    # 10
    def test_500_descobertas_0_ready_nao_e_500_uteis(self):
        rl = [{"EVENTO": "REALIMENTACAO", "AT": (AGORA - timedelta(minutes=5)).isoformat(),
               "DISCOVERY": {"CANDIDATAS_NOVAS": 500, "CRAWL": 500}}]
        T.RUNLOG.write_text("\n".join(json.dumps(x) for x in rl) + "\n", encoding="utf-8")
        self._ledger([])   # zero READY
        m = T.metricas(AGORA)
        self.assertEqual(m["JANELA_1H"]["NEW_CANDIDATES"], 500)
        self.assertEqual(m["JANELA_1H"]["READY_CURRENT"], 0)
        # os dois campos existem SEPARADOS; nenhum campo diz "500 uteis"
        self.assertNotEqual(m["JANELA_1H"]["NEW_CANDIDATES"], m["JANELA_1H"]["READY_CURRENT"])

    # 11
    def test_divisao_por_zero_nao_da_yield_falso(self):
        self._ledger([])   # 0 qualify, 0 ready
        m = T.metricas(AGORA)
        self.assertEqual(m["RENDIMENTO"]["QUALIFY_TO_READY_YIELD_1H"], "N/A")
        self.assertEqual(m["RENDIMENTO"]["QUALIFY_TO_READY_YIELD_24H"], "N/A")

    # 13 (alvo do red team M6): bloqueio nao pode contar como READY
    def test_bloqueio_nao_conta_como_ready(self):
        tr = [_tr("CAND-1", LC.CAPABILITY_BLOCK, AGORA - timedelta(minutes=5),
                  ev="EV-CAND-1-QUALIFY-1")]
        self._ledger(tr)
        m = T.metricas(AGORA)
        self.assertEqual(m["JANELA_24H"]["READY_CURRENT"], 0, "bloqueio nao e READY")
        self.assertEqual(m["JANELA_24H"]["CAPABILITY_BLOCK"], 1)

    # 14 (alvo do red team M7): fila com trabalho e sem progresso NAO e "normal"
    def test_fila_com_trabalho_sem_progresso_nao_e_produtivo(self):
        # worker vivo, fila com pendente, heartbeat velho (> timeout)
        self._fila([self._qtask("A", AGORA - timedelta(hours=2), status=F.PENDING)])
        self._estado(vivo=True, hb_seg=T.HEARTBEAT_TIMEOUT_S + 100)
        # WORKER_PID vivo para o estado do worker nao ser DOWN
        S.ESTADO.write_text(json.dumps({"SUPERVISOR_STATE": "RUNNING",
            "SUPERVISOR_PID": os.getpid(), "WORKER_PID": os.getpid(),
            "SUPERVISOR_STARTED_AT": (AGORA - timedelta(hours=6)).isoformat()},
            ensure_ascii=False), encoding="utf-8")
        m = T.metricas(AGORA)
        self.assertEqual(m["PRODUCTIVITY_STATE"], "ACTIVE_NO_OUTPUT",
                         "vivo + fila > 0 + sem progresso != ACTIVE_PRODUCTIVE")

    # 12
    def test_checkpoint_sem_mudanca_nao_faz_spam(self):
        m = T.metricas(AGORA)
        r1 = T.talvez_checkpoint(m, motivo="1")
        r2 = T.talvez_checkpoint(m, motivo="2")   # nada mudou
        self.assertTrue(r1["ESCRITO"])
        self.assertFalse(r2["ESCRITO"])
        self.assertEqual(len(T.historico_checkpoints()), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
