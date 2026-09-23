#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Testes da etapa QUALIFY do worker — o defeito 1 da missao SERVICE-V1.

    ENFILEIRADA != PROCESSAVEL.

Antes desta etapa existir, uma tarefa QUALIFY caia em BLOCK «etapa sem
executor» (ou no guard «sem contrato», que uma candidata nova nunca tem). Estes
testes provam que:

  1. o guard de «sem contrato» deixa QUALIFY passar (nao a bloqueia);
  2. QUALIFY de uma fonte HTML com territorio determinavel aloca SOURCE_ID
     canonico, poe a fonte em CONTRACT_PENDING e enfileira BUILD_CONTRACT;
  3. QUALIFY NUNCA promove READY (nem quando OK);
  4. territorio NAO SEI -> SEMANTIC_REVIEW, sem fabricar SOURCE_ID;
  5. YouTube -> CAPABILITY_BLOCK (sem molde de video);
  6. correr duas vezes a mesma candidata nao cunha um segundo SOURCE_ID.

Tudo em ficheiros temporarios: nao toca a lane real.
"""
import importlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))
sys.path.insert(0, str(RAIZ / "candidatas"))

import fila as F
import fonte_nova as FN
import lifecycle as LC
import worker as W


class TestQualify(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(self.enterContext(tempfile.TemporaryDirectory(prefix="qualify-test-")))
        # Redireciona TODO o estado que a etapa toca para a pasta temporaria.
        self._orig = {
            "F.FILA": F.FILA, "LC.LIVRO": LC.LIVRO,
            "W.ALLOCATION": W.ALLOCATION, "W.EVIDENCIA": W.EVIDENCIA,
            "FN.FILA": FN.FILA,
        }
        F.FILA = self.tmp / "fila.json"
        LC.LIVRO = self.tmp / "livro.json"
        W.ALLOCATION = self.tmp / "alloc.json"
        W.EVIDENCIA = self.tmp / "evid.json"
        # o pulso do worker e prova de vida para o supervisor: nunca o real
        self.addCleanup(setattr, W, "PULSO", W.PULSO)
        W.PULSO = self.tmp / "WORKER-HEARTBEAT.json"
        FN.FILA = self.tmp / "candidatas.json"
        # Registo de alocacao com um teto por territorio (para prever a sequencia).
        W.ALLOCATION.write_text(json.dumps({
            "DATASET": "SOURCE-ID-ALLOCATION-V1",
            "MAIOR_POR_TERRITORIO_ANTES": {"T7": 14, "T5": 36},
            "ATRIBUIDOS": 0, "NOVAS": [],
        }, ensure_ascii=False), encoding="utf-8")

    def tearDown(self):
        for k, v in self._orig.items():
            mod, attr = k.split(".")
            setattr({"F": F, "LC": LC, "W": W, "FN": FN}[mod], attr, v)

    def _candidata(self, cand_id, tipo, nome, url, pais="IT"):
        doc = FN.carregar()
        doc["CANDIDATAS"].append({
            "CANDIDATA_ID": cand_id, "TIPO": tipo, "NOME": nome, "URL": url,
            "PAIS": pais, "ESTADO": "EM_ANALISE", "SOURCE_ID": None,
        })
        FN.gravar(doc)

    def _correr_uma(self, cand_id, tipo, nome, url):
        self._candidata(cand_id, tipo, nome, url)
        F.enfileirar(cand_id, F.QUALIFY, priority=30, motivo="teste")
        feitos = W.correr(max_tarefas=1, pausa=0, verboso=False)
        return feitos[0]

    def test_guard_nao_bloqueia_qualify(self):
        """O guard de «sem contrato» NAO pode barrar QUALIFY."""
        r = self._correr_uma("CAND-9001", "ORGANIZACAO",
                              "Consorzio Tutela Vini", "https://consorziovini.it")
        self.assertNotEqual(r["PORQUE"], "sem contrato")
        self.assertNotIn("etapa", r["PORQUE"])

    def test_html_aloca_e_enfileira_build_contract(self):
        r = self._correr_uma("CAND-9002", "ORGANIZACAO",
                              "Consorzio Tutela Vini", "https://consorziovini.it")
        self.assertEqual(r["RESULTADO"], "OK")
        # SOURCE_ID canonico alocado, sequencia = teto+1 (T7 -> 015).
        alloc = json.loads(W.ALLOCATION.read_text(encoding="utf-8"))
        sids = [n["SOURCE_ID"] for n in alloc["NOVAS"]]
        self.assertEqual(len(sids), 1)
        sid = sids[0]
        self.assertTrue(sid.startswith("IT-T7-"), "territorio consorzio = T7: %s" % sid)
        # BUILD_CONTRACT enfileirado SOB o SOURCE_ID real, nao sob o CAND.
        tarefas = F._ler()["TAREFAS"]
        bc = [t for t in tarefas if t["TASK_TYPE"] == F.BUILD_CONTRACT]
        self.assertEqual(len(bc), 1)
        self.assertEqual(bc[0]["SOURCE_ID"], sid)
        # A tarefa QUALIFY (chave = CAND) ficou DONE.
        q = [t for t in tarefas if t["TASK_ID"] == r["TASK_ID"]][0]
        self.assertEqual(q["STATUS"], F.DONE)
        # lifecycle: CONTRACT_PENDING sob o SOURCE_ID real.
        self.assertEqual(LC.estado_de(sid), LC.CONTRACT_PENDING)

    def test_qualify_nunca_promove_ready(self):
        """A prova central: QUALIFY OK nao pode deixar NENHUMA fonte em READY."""
        self._correr_uma("CAND-9003", "BASE_OFICIAL",
                          "Universita di Bologna", "https://unibo.it")
        snap = LC.snapshot()
        self.assertNotIn(LC.READY_FOR_COLLECTION, snap.values(),
                         "QUALIFY promoveu READY — proibido: %s" % snap)

    def test_territorio_naosei_vira_semantic_sem_fabricar(self):
        r = self._correr_uma("CAND-9004", "ORGANIZACAO",
                              "Granarolo", "https://granarolo.example")
        self.assertEqual(r["RESULTADO"], "BLOCK")
        # NAO fabricou SOURCE_ID.
        alloc = json.loads(W.ALLOCATION.read_text(encoding="utf-8"))
        self.assertEqual(alloc["NOVAS"], [], "nao pode alocar quando o territorio e NAO SEI")
        self.assertEqual(LC.estado_de("CAND-9004"), LC.SEMANTIC_REVIEW)

    def test_youtube_vira_capability_block(self):
        r = self._correr_uma("CAND-9005", "YOUTUBE",
                              "Canale Agricoltura", "https://youtube.com/@agri")
        self.assertEqual(r["RESULTADO"], "BLOCK")
        self.assertEqual(LC.estado_de("CAND-9005"), LC.CAPABILITY_BLOCK)

    def test_idempotente_nao_cunha_segundo_id(self):
        self._correr_uma("CAND-9006", "ORGANIZACAO",
                         "Consorzio Tutela Vini", "https://consorziovini.it")
        alloc1 = json.loads(W.ALLOCATION.read_text(encoding="utf-8"))
        sid1 = alloc1["NOVAS"][0]["SOURCE_ID"]
        # Segunda passagem da mesma candidata: reusa o numero, nao cria outro.
        sid2, novo = W._alocar_source_id("CAND-9006", "T7", "HTML_SITE",
                                         {"NOME": "x", "URL": "y"}, "reteste")
        self.assertEqual(sid1, sid2)
        self.assertFalse(novo)
        alloc2 = json.loads(W.ALLOCATION.read_text(encoding="utf-8"))
        self.assertEqual(len(alloc2["NOVAS"]), 1)


class TestDesbloqueio(unittest.TestCase):
    """recuperar_bloqueadas_por_defeito so mexe no que foi barrado por DEFEITO."""

    def setUp(self):
        self.tmp = Path(self.enterContext(tempfile.TemporaryDirectory(prefix="desbloq-test-")))
        self._orig = F.FILA
        F.FILA = self.tmp / "fila.json"

    def tearDown(self):
        F.FILA = self._orig

    def _tarefa(self, tid, sid, tipo, status, erro):
        return {"TASK_ID": tid, "SOURCE_ID": sid, "TASK_TYPE": tipo,
                "PRIORITY": 30, "STATUS": status, "ATTEMPTS": 1,
                "NEXT_ATTEMPT_AT": None, "LAST_ERROR": erro, "MOTIVO": "",
                "CREATED_AT": "2026-09-21T00:00:00+00:00",
                "UPDATED_AT": "2026-09-21T00:00:00+00:00"}

    def test_desbloqueia_qualify_mas_nao_canary_nem_policy(self):
        tarefas = [
            self._tarefa("T1", "CAND-1", F.QUALIFY, F.BLOCKED, "sem contrato nesta arvore"),
            self._tarefa("T2", "CAND-2", F.QUALIFY, F.BLOCKED, "sem contrato nesta arvore"),
            self._tarefa("T3", "IT-T3-1", F.CANARY, F.BLOCKED, "sem contrato nesta arvore"),
            self._tarefa("T4", "CAND-4", F.QUALIFY, F.BLOCKED,
                         "LINKEDIN_POLICY: coleta automatizada proibida pelos TOS"),
        ]
        F.FILA.write_text(json.dumps({"PROXIMO_ID": 5, "TAREFAS": tarefas}),
                          encoding="utf-8")
        mex = F.recuperar_bloqueadas_por_defeito(
            ["sem contrato", "etapa nao implementada"], task_types={F.QUALIFY})
        self.assertEqual({m["TASK_ID"] for m in mex}, {"T1", "T2"})
        d = F._ler()["TAREFAS"]
        por_id = {t["TASK_ID"]: t for t in d}
        self.assertEqual(por_id["T1"]["STATUS"], F.PENDING)
        self.assertEqual(por_id["T2"]["STATUS"], F.PENDING)
        self.assertEqual(por_id["T3"]["STATUS"], F.BLOCKED, "CANARY sem contrato e bloqueio legitimo")
        self.assertEqual(por_id["T4"]["STATUS"], F.BLOCKED, "policy nao se desbloqueia")


if __name__ == "__main__":
    unittest.main(verbosity=2)
