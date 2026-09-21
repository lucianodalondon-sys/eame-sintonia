#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A CADEIA REAL, PONTA A PONTA — BRIDGE-FEEDER G1 e G2.

    CANDIDATA existe -> ponte reconhece -> tarefa criada -> entra na fila
    -> supervisor deteta -> worker processa -> lifecycle recebe (ou nao)

Tudo em pasta descartavel: porta, ledger da ponte, fila, livro, evidencia,
contratos, estado e diario do supervisor. O lancador de worker do supervisor
e um processo inerte (o molde de test_supervisor.py); o worker que processa
e o REAL (`worker.correr`), no processo do teste, sem rede — a etapa QUALIFY
nao tem executor e nao precisa de contrato para ser decidida.

O QUE ESTA CADEIA PROVA E O QUE NAO PROVA
-----------------------------------------
A ponte cria tarefas QUALIFY. O worker desta arvore (identico ao do bridge:
worker.py nao foi tocado em 63b71421) NAO TEM executor para QUALIFY e, sem
contrato, BLOQUEIA a tarefa com «sem contrato nesta arvore». O lifecycle nao
recebe nada nesse ramo. Para as sociais, o lifecycle recebe POLICY_BLOCK /
CAPABILITY_BLOCK directamente da ponte.

    Isto e medido aqui e escrito no relatorio. Nao se inventa um executor
    de QUALIFY para a cadeia parecer completa.

G2 — idempotencia: a mesma candidata duas vezes da UMA tarefa; um retry
legitimo preserva o historico (ATTEMPTS, LAST_ERROR); uma tarefa bloqueada
nao trava as outras.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))
sys.path.insert(0, str(RAIZ / "candidatas"))

import fila as F              # noqa: E402
import fonte_nova as FN       # noqa: E402
import lifecycle as LC        # noqa: E402
import ponte_candidatas as P  # noqa: E402
import supervisor as S        # noqa: E402
import worker as W            # noqa: E402

CAMINHOS_REAIS = {
    "F.FILA":   RAIZ / "curadoria" / "LIFECYCLE-QUEUE-V1.json",
    "LC.LIVRO": RAIZ / "curadoria" / "LIFECYCLE-LEDGER-V1.json",
    "FN.FILA":  RAIZ / "candidatas" / "FONTES-CANDIDATAS.json",
    "P.LEDGER": RAIZ / "curadoria" / "BRIDGE-LEDGER-V1.json",
    "W.EVIDENCIA": RAIZ / "curadoria" / "LIFECYCLE-EVIDENCE-V1.json",
    "S.ESTADO": RAIZ / "curadoria" / "SUPERVISOR-STATE.json",
    "S.DIARIO": RAIZ / "curadoria" / "SOURCE-CURATOR-RUN-LOG.ndjson",
}


def _impressao(p: Path) -> str:
    if not p.exists():
        return "AUSENTE"
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _impressoes() -> dict:
    return {k: _impressao(p) for k, p in CAMINHOS_REAIS.items()}


class ACadeia(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        d = Path(self.tmp.name)
        self._antes = (LC.LIVRO, F.FILA, FN.FILA, P.CARACT, P.LEDGER, W.EVIDENCIA,
                       W.CONTRATOS, S.ESTADO, S.DIARIO, S.LOCK, S.PARAR)
        self._reais_antes = _impressoes()
        LC.LIVRO = d / "LEDGER.json"
        F.FILA = d / "QUEUE.json"
        FN.FILA = d / "FONTES-CANDIDATAS.json"
        P.CARACT = d / "CARACT-nao-existe.json"
        P.LEDGER = d / "BRIDGE-LEDGER.json"
        W.EVIDENCIA = d / "EVIDENCE.json"
        W.CONTRATOS = d / "contracts.json"
        W.CONTRATOS.write_text(json.dumps({"FONTES": []}), encoding="utf-8")
        S.ESTADO = d / "SUPERVISOR-STATE.json"
        S.DIARIO = d / "RUN-LOG.ndjson"
        S.LOCK = d / "SUPERVISOR.lock"
        S.PARAR = d / "PARAR.flag"
        self._procs: list[subprocess.Popen] = []
        self._lancador = mock.patch.object(S, "_lancar_worker", self._worker_inerte)
        self._lancador.start()

    def tearDown(self):
        self._lancador.stop()
        for p in self._procs:
            if p.poll() is None:
                p.kill()
                p.wait(timeout=5)
            if p.stdout:
                p.stdout.close()
        (LC.LIVRO, F.FILA, FN.FILA, P.CARACT, P.LEDGER, W.EVIDENCIA,
         W.CONTRATOS, S.ESTADO, S.DIARIO, S.LOCK, S.PARAR) = self._antes
        self.tmp.cleanup()
        depois = _impressoes()
        self.assertEqual(self._reais_antes, depois,
                         "um ficheiro REAL mudou durante o teste: %s"
                         % [k for k in depois if depois[k] != self._reais_antes[k]])

    def _worker_inerte(self, pausa: float = 1.0) -> subprocess.Popen:
        p = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"],
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             text=True, encoding="utf-8", errors="replace")
        self._procs.append(p)
        return p

    def _candidata(self, tipo: str, nome: str, url: str) -> dict:
        return FN.registar(tipo=tipo, pais="IT", nome=nome, url=url,
                           para_que="prova da cadeia", quem_viu="TEST_cadeia",
                           onde_viu=url)

    def _tarefas(self) -> list:
        return F._ler()["TAREFAS"]

    def _estado_sup(self) -> dict:
        return {"SUPERVISOR_STATE": "STARTING", "RESTARTS_TOTAL": 0,
                "CRASHES_SEM_PROGRESSO": [], "WORKER_PID": None}

    # G1 ---------------------------------------------------------------------
    def test_g1_a_cadeia_ponta_a_ponta_com_os_numeros_de_cada_salto(self):
        # 1. CANDIDATA existe
        a = self._candidata("BASE_OFICIAL", "Base oficial de prova",
                            "https://g1.test-sintonia.it/oficial")
        b = self._candidata("LINKEDIN", "Pagina LinkedIn de prova",
                            "https://www.linkedin.com/company/g1-test-sintonia")
        c = self._candidata("ORGANIZACAO", "Organizacao de prova",
                            "https://g1.test-sintonia.it/org")
        self.assertEqual(len(FN.carregar()["CANDIDATAS"]), 3)
        self.assertEqual(F.metricas()["QUEUE_TOTAL"], 0)

        # 2. ponte reconhece -> 3. tarefa criada -> 4. entra na fila
        m = P.processar()
        self.assertEqual(m["CANDIDATAS_LIDAS"], 3)
        self.assertEqual(m["TAREFAS_CRIADAS"], 2)
        self.assertEqual(m["ENFILEIRADAS"], 2)
        self.assertEqual(m["CLASSIFICADAS_BARRADAS"], 1)
        self.assertEqual(m["SOCIAIS_ENFILEIRADAS"], 0)
        self.assertEqual(m["QUEUE_DEPTH_ANTES"], 0)
        self.assertEqual(m["QUEUE_DEPTH_DEPOIS"], 2)
        tarefas = self._tarefas()
        self.assertEqual({t["TASK_TYPE"] for t in tarefas}, {F.QUALIFY})
        self.assertEqual({t["STATUS"] for t in tarefas}, {F.PENDING})
        self.assertEqual({t["SOURCE_ID"] for t in tarefas},
                         {a["CANDIDATA_ID"], c["CANDIDATA_ID"]})
        elegiveis = F.elegiveis()
        self.assertEqual(len(elegiveis), 2)
        # A social foi ao livro directamente, sem passar pela fila.
        self.assertEqual(LC.estado_de(b["CANDIDATA_ID"]), LC.POLICY_BLOCK)
        self.assertIsNone(LC.estado_de(a["CANDIDATA_ID"]))

        # 5. supervisor deteta (2 elegiveis -> lanca worker)
        estado = self._estado_sup()
        accao, estado, proc = S.uma_volta_sup(estado, None, pausa_worker=0.1)
        self.assertEqual(accao, "RELANCADO")
        self.assertIn("2 tarefas elegiveis", estado["LAST_RESTART_REASON"])
        pid_worker = proc.pid
        self.assertEqual(estado["WORKER_PID"], pid_worker)

        # 6. worker processa (o real, em processo, sem rede)
        feitos = W.correr(pausa=0, verboso=False)
        self.assertEqual(len(feitos), 2, feitos)
        self.assertEqual({f["RESULTADO"] for f in feitos}, {"BLOCK"}, feitos)
        self.assertEqual({f["PORQUE"] for f in feitos}, {"sem contrato"}, feitos)
        tarefas = self._tarefas()
        self.assertEqual({t["STATUS"] for t in tarefas}, {F.BLOCKED})
        self.assertEqual({t["LAST_ERROR"] for t in tarefas},
                         {"sem contrato nesta arvore"})
        self.assertEqual(F.elegiveis(), [])

        # 7. lifecycle recebe: NADA para QUALIFY (medido, nao escondido).
        self.assertIsNone(LC.estado_de(a["CANDIDATA_ID"]),
                          "QUALIFY bloqueada no worker nao chega ao livro")
        self.assertIsNone(LC.estado_de(c["CANDIDATA_ID"]))
        self.assertEqual(LC.estado_de(b["CANDIDATA_ID"]), LC.POLICY_BLOCK)

        # 8. e a volta seguinte do supervisor, com o worker morto e a fila
        #    sem elegiveis, e IDLE — o ponto onde o hook de descoberta corre.
        proc.kill()
        proc.wait(timeout=10)
        chamadas = []
        accao2, estado, proc2 = S.uma_volta_sup(estado, proc, pausa_worker=0.1,
                                                hook_fila_vazia=lambda: chamadas.append(1))
        self.assertEqual(accao2, "IDLE")
        self.assertEqual(chamadas, [1])

        print("\nG1 CADEIA: candidatas=3 -> ponte: tarefas_criadas=%d barradas=%d "
              "-> fila: elegiveis=%d -> supervisor: RELANCADO pid=%d -> worker: "
              "feitos=%d resultado=%s -> livro: POLICY_BLOCK=1 QUALIFY=0 -> IDLE hook=1"
              % (m["TAREFAS_CRIADAS"], m["CLASSIFICADAS_BARRADAS"], len(elegiveis),
                 pid_worker, len(feitos), sorted({f["RESULTADO"] for f in feitos})))

    # G2 ---------------------------------------------------------------------
    def test_g2_a_mesma_candidata_duas_vezes_da_uma_tarefa(self):
        url = "https://g2.test-sintonia.it/uma"
        x = self._candidata("BASE_OFICIAL", "Uma", url)
        y = self._candidata("BASE_OFICIAL", "Uma outra vez", url + "/")
        self.assertEqual(x["CANDIDATA_ID"], y["CANDIDATA_ID"], "a porta dedupa pela URL")
        self.assertEqual(len(FN.carregar()["CANDIDATAS"]), 1)
        m1 = P.processar()
        m2 = P.processar()
        self.assertEqual(m1["TAREFAS_CRIADAS"], 1)
        self.assertEqual(m2["TAREFAS_CRIADAS"], 0)
        self.assertEqual(len(self._tarefas()), 1)
        # E mesmo sem o ledger da ponte, a fila nao aceita a segunda aberta.
        t = F.enfileirar(x["CANDIDATA_ID"], F.QUALIFY, priority=30)
        self.assertEqual(t["TASK_ID"], self._tarefas()[0]["TASK_ID"])
        self.assertEqual(len(self._tarefas()), 1)

    def test_g2_um_retry_legitimo_preserva_o_historico(self):
        x = self._candidata("ORGANIZACAO", "Retry", "https://g2.test-sintonia.it/retry")
        P.processar()
        tid = self._tarefas()[0]["TASK_ID"]
        # 429 da casa: adiar com relogio a zero — elegivel ja, com historico.
        F.adiar(tid, retry_after_s=0, erro="429 simulado")
        P.processar()  # a ponte nao cria segunda tarefa nem apaga a primeira
        tarefas = self._tarefas()
        self.assertEqual(len(tarefas), 1)
        t = tarefas[0]
        self.assertEqual(t["TASK_ID"], tid)
        self.assertEqual(t["ATTEMPTS"], 1)
        self.assertEqual(t["LAST_ERROR"], "429 simulado")
        self.assertEqual([e["TASK_ID"] for e in F.elegiveis()], [tid])

    def test_g2_uma_tarefa_bloqueada_nao_trava_o_resto_da_fila(self):
        a = self._candidata("BASE_OFICIAL", "A", "https://g2.test-sintonia.it/a")
        self._candidata("INSTAGRAM", "Social no meio",
                        "https://www.instagram.com/g2_test_sintonia")
        c = self._candidata("CIENCIA", "C", "https://g2.test-sintonia.it/c")
        m = P.processar()
        self.assertEqual(m["TAREFAS_CRIADAS"], 2)
        self.assertEqual(m["CLASSIFICADAS_BARRADAS"], 1)
        ta = next(t for t in self._tarefas() if t["SOURCE_ID"] == a["CANDIDATA_ID"])
        F.bloquear(ta["TASK_ID"], "bloqueada de proposito")
        self.assertEqual([e["SOURCE_ID"] for e in F.elegiveis()], [c["CANDIDATA_ID"]])
        feitos = W.correr(pausa=0, verboso=False)
        self.assertEqual([f["SOURCE_ID"] for f in feitos], [c["CANDIDATA_ID"]])
        self.assertEqual(F.elegiveis(), [])
        ta_depois = next(t for t in self._tarefas() if t["TASK_ID"] == ta["TASK_ID"])
        self.assertEqual(ta_depois["LAST_ERROR"], "bloqueada de proposito",
                         "a bloqueada ficou como estava; ninguem lhe tocou")


if __name__ == "__main__":
    unittest.main(verbosity=2)
