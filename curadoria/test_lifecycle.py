#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OS DEZ ATAQUES AO CICLO DE VIDA DA FONTE.

Cada teste tenta DERRUBAR uma lei. Um teste que so confirma o caminho feliz
nao prova lei nenhuma — prova que o codigo corre.

    UM TESTE QUE NUNCA DIZ «NAO» NAO MEDE NADA.

O tempo e injetado em todos os testes de backoff. Uma prova que exigisse
esperar 60s reais nao se corria, e uma prova que nao se corre nao prova nada.
"""
from __future__ import annotations

import importlib
import json
import sys
import tempfile
import unittest
from datetime import timedelta
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))

import fila as F          # noqa: E402
import lifecycle as LC    # noqa: E402


class Isolada(unittest.TestCase):
    """Cada teste corre sobre ficheiros proprios: uma prova que escreve nunca
    escreve no deposito da casa."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        d = Path(self.tmp.name)
        importlib.reload(LC)
        importlib.reload(F)
        LC.LIVRO = d / "LEDGER.json"
        F.FILA = d / "QUEUE.json"

    def tearDown(self):
        self.tmp.cleanup()


class P1_CollectionNaoPromove(Isolada):
    def test_a_collection_nao_pode_declarar_READY(self):
        LC.registar("IT-T7-900", LC.CANARY_PENDING, "pronta para canario")
        with self.assertRaises(ValueError) as e:
            LC.registar("IT-T7-900", LC.READY_FOR_COLLECTION, "colhi e correu bem",
                        owner=LC.OWNER_COLLECTION, evidence_ref="EV-1")
        self.assertIn("Collection", str(e.exception))
        self.assertEqual(LC.estado_de("IT-T7-900"), LC.CANARY_PENDING)

    def test_a_collection_PODE_marcar_degradada(self):
        """Contraprova positiva: o guarda nao pode recusar tudo."""
        LC.registar("IT-T7-901", LC.CANARY_PENDING, "pronta")
        LC.registar("IT-T7-901", LC.READY_FOR_COLLECTION, "canario passou",
                    evidence_ref="EV-2")
        LC.registar("IT-T7-901", LC.DEGRADED, "404 em producao",
                    owner=LC.OWNER_COLLECTION, evidence_ref="RUN-77")
        self.assertEqual(LC.estado_de("IT-T7-901"), LC.DEGRADED)


class P2_ReadyExigeGatesReais(Isolada):
    def test_nao_se_salta_de_DISCOVERED_para_READY(self):
        LC.registar("IT-T7-902", LC.DISCOVERED, "descoberta")
        with self.assertRaises(ValueError) as e:
            LC.registar("IT-T7-902", LC.READY_FOR_COLLECTION, "parece boa",
                        evidence_ref="EV-3")
        self.assertIn("canario", str(e.exception))

    def test_READY_sem_evidencia_e_recusado(self):
        LC.registar("IT-T7-903", LC.CANARY_PENDING, "pronta")
        with self.assertRaises(ValueError) as e:
            LC.registar("IT-T7-903", LC.READY_FOR_COLLECTION, "passou, confia")
        self.assertIn("EVIDENCE_REF", str(e.exception))


class P3_BackoffNaoBloqueiaAFila(Isolada):
    def test_um_429_em_A_nao_impede_B_C_D(self):
        """O coracao da FASE 4, medido: A adiada, as outras correm na mesma volta."""
        for s in ("A", "B", "C", "D"):
            F.enfileirar("IT-T7-91%s" % s, F.CANARY)
        t0 = F.agora_utc()

        a = F.proxima(t0)
        self.assertEqual(a["SOURCE_ID"], "IT-T7-91A")
        F.adiar(a["TASK_ID"], retry_after_s=3600, erro="HTTP 429", agora=t0)

        correram = []
        while True:
            t = F.proxima(t0)
            if t is None:
                break
            correram.append(t["SOURCE_ID"])
            F.concluir(t["TASK_ID"])

        self.assertEqual(correram, ["IT-T7-91B", "IT-T7-91C", "IT-T7-91D"])
        self.assertNotIn("IT-T7-91A", correram)

    def test_A_volta_sozinha_quando_o_relogio_chega(self):
        F.enfileirar("IT-T7-920", F.CANARY)
        t0 = F.agora_utc()
        a = F.proxima(t0)
        F.adiar(a["TASK_ID"], retry_after_s=3600, erro="HTTP 429", agora=t0)

        self.assertEqual(len(F.elegiveis(t0 + timedelta(minutes=59))), 0)
        depois = F.elegiveis(t0 + timedelta(minutes=61))
        self.assertEqual([t["SOURCE_ID"] for t in depois], ["IT-T7-920"])

    def test_o_retry_after_da_plataforma_manda_no_relogio_da_casa(self):
        F.enfileirar("IT-T7-921", F.CANARY)
        t0 = F.agora_utc()
        a = F.proxima(t0)
        r = F.adiar(a["TASK_ID"], retry_after_s=7200, erro="429", agora=t0)
        esperado = t0 + timedelta(seconds=7200)
        self.assertEqual(F._parse(r["NEXT_ATTEMPT_AT"]), esperado)

    def test_o_retry_tem_teto_e_o_teto_e_observavel(self):
        F.enfileirar("IT-T7-922", F.CANARY)
        t0 = F.agora_utc()
        for _ in range(F.MAX_ATTEMPTS):
            t = F.proxima(t0 + timedelta(days=99))
            if t is None:
                break
            r = F.adiar(t["TASK_ID"], retry_after_s=1, erro="429", agora=t0)
        self.assertEqual(r["STATUS"], F.FAILED)
        self.assertIn("teto", r["LAST_ERROR"])


class P4_RetryPersiste(Isolada):
    def test_o_adiamento_sobrevive_a_releitura_do_disco(self):
        F.enfileirar("IT-T7-930", F.CANARY)
        t0 = F.agora_utc()
        a = F.proxima(t0)
        F.adiar(a["TASK_ID"], retry_after_s=1800, erro="429", agora=t0)

        d = json.loads(F.FILA.read_text(encoding="utf-8"))
        t = d["TAREFAS"][0]
        self.assertEqual(t["STATUS"], F.WAITING_RETRY)
        self.assertEqual(t["ATTEMPTS"], 1)
        self.assertTrue(t["NEXT_ATTEMPT_AT"])


class P5_RestartNaoPerdeTarefa(Isolada):
    def test_processo_morto_a_meio_deixa_a_tarefa_recuperavel(self):
        F.enfileirar("IT-T7-940", F.CANARY)
        F.enfileirar("IT-T7-941", F.CANARY)
        t0 = F.agora_utc()
        pego = F.proxima(t0)                      # marcada IN_PROGRESS no disco
        # ---- aqui o processo «morre»: nada mais e escrito ----

        d = json.loads(F.FILA.read_text(encoding="utf-8"))
        vivas = [t for t in d["TAREFAS"] if t["STATUS"] != F.DONE]
        self.assertEqual(len(vivas), 2, "nenhuma tarefa se perdeu no crash")

        # processo novo, meia hora depois
        recuperadas = F.recuperar_orfas(agora=t0 + timedelta(hours=1))
        self.assertEqual([r["SOURCE_ID"] for r in recuperadas], [pego["SOURCE_ID"]])
        self.assertEqual(len(F.elegiveis(t0 + timedelta(hours=1))), 2)


class P6_DuasExecucoesNaoPromovemDuplicado(Isolada):
    def test_enfileirar_o_mesmo_trabalho_duas_vezes_da_UMA_tarefa(self):
        a = F.enfileirar("IT-T7-950", F.CANARY)
        b = F.enfileirar("IT-T7-950", F.CANARY)
        self.assertEqual(a["TASK_ID"], b["TASK_ID"])
        self.assertEqual(F.metricas()["QUEUE_TOTAL"], 1)

    def test_promover_duas_vezes_nao_cria_segundo_READY(self):
        LC.registar("IT-T7-951", LC.CANARY_PENDING, "pronta")
        LC.registar("IT-T7-951", LC.READY_FOR_COLLECTION, "canario", evidence_ref="EV")
        with self.assertRaises(ValueError):
            LC.registar("IT-T7-951", LC.READY_FOR_COLLECTION, "outra vez",
                        evidence_ref="EV")
        self.assertEqual(LC.metricas()[LC.READY_FOR_COLLECTION], 1)


class P7_FonteBloqueadaNaoEntraEmReady(Isolada):
    def test_robots_block_nao_pode_ser_promovida(self):
        LC.registar("IT-T7-960", LC.CANARY_PENDING, "pronta")
        LC.registar("IT-T7-960", LC.CONTRACT_READY_ROUTE_BLOCKED,
                    "feed em Disallow", evidence_ref="EV")
        with self.assertRaises(ValueError):
            LC.registar("IT-T7-960", LC.READY_FOR_COLLECTION, "mas o canario passou",
                        evidence_ref="EV")
        self.assertEqual(LC.estado_de("IT-T7-960"), LC.CONTRACT_READY_ROUTE_BLOCKED)


class P8_DegradedNaoContinuaReady(Isolada):
    def test_apos_DEGRADED_a_fonte_ja_nao_consta_como_READY(self):
        LC.registar("IT-T7-970", LC.CANARY_PENDING, "pronta")
        LC.registar("IT-T7-970", LC.READY_FOR_COLLECTION, "canario", evidence_ref="EV")
        self.assertEqual(LC.metricas()[LC.READY_FOR_COLLECTION], 1)
        LC.registar("IT-T7-970", LC.DEGRADED, "falhou em producao",
                    owner=LC.OWNER_COLLECTION, evidence_ref="RUN-9")
        self.assertEqual(LC.metricas()[LC.READY_FOR_COLLECTION], 0)
        self.assertEqual(LC.metricas()[LC.DEGRADED], 1)


class P9_ReparoExigeNovoCanario(Isolada):
    def test_de_DEGRADED_nao_se_volta_a_READY_por_decreto(self):
        LC.registar("IT-T7-980", LC.CANARY_PENDING, "pronta")
        LC.registar("IT-T7-980", LC.READY_FOR_COLLECTION, "canario", evidence_ref="EV")
        LC.registar("IT-T7-980", LC.DEGRADED, "quebrou",
                    owner=LC.OWNER_COLLECTION, evidence_ref="RUN-1")
        with self.assertRaises(ValueError) as e:
            LC.registar("IT-T7-980", LC.READY_FOR_COLLECTION, "ja deve estar boa",
                        evidence_ref="EV")
        self.assertIn("REPAIRING", str(e.exception))

    def test_o_caminho_legitimo_DEGRADED_REPAIRING_READY_funciona(self):
        """Contraprova: o reparo real tem de conseguir passar."""
        LC.registar("IT-T7-981", LC.CANARY_PENDING, "pronta")
        LC.registar("IT-T7-981", LC.READY_FOR_COLLECTION, "canario", evidence_ref="EV")
        LC.registar("IT-T7-981", LC.DEGRADED, "quebrou",
                    owner=LC.OWNER_COLLECTION, evidence_ref="RUN-1")
        LC.registar("IT-T7-981", LC.REPAIRING, "curator assume o reparo")
        LC.registar("IT-T7-981", LC.READY_FOR_COLLECTION,
                    "novo canario resolveu", evidence_ref="EV-NOVO")
        self.assertEqual(LC.estado_de("IT-T7-981"), LC.READY_FOR_COLLECTION)


class P10_IdentidadeEProcedenciaEstaveis(Isolada):
    def test_o_SOURCE_ID_nao_muda_no_retry_e_a_historia_preserva_se(self):
        LC.registar("IT-T7-990", LC.CANARY_PENDING, "pronta")
        LC.registar("IT-T7-990", LC.RETRY_AFTER, "429", evidence_ref="EV-1")
        LC.registar("IT-T7-990", LC.CANARY_PENDING, "voltou a ser elegivel")
        LC.registar("IT-T7-990", LC.READY_FOR_COLLECTION, "canario", evidence_ref="EV-2")

        h = LC.historia("IT-T7-990")
        self.assertEqual(len(h), 4, "append-only: nenhuma linha foi sobrescrita")
        self.assertTrue(all(x["SOURCE_ID"] == "IT-T7-990" for x in h))
        self.assertEqual([x["NEW_STATE"] for x in h],
                         [LC.CANARY_PENDING, LC.RETRY_AFTER, LC.CANARY_PENDING,
                          LC.READY_FOR_COLLECTION])
        self.assertTrue(all(x["OWNER"] and x["VERSION"] for x in h))

    def test_nenhum_DOCUMENT_ID_e_fabricado_pelo_lifecycle(self):
        """O cadastro de fonte nao cunha identidade de documento. Nunca."""
        fonte = Path(LC.__file__).read_text(encoding="utf-8")
        self.assertNotIn("DOCUMENT_ID", fonte)


class P11_MetricasNaoEscondemZeros(Isolada):
    def test_estado_com_zero_aparece_como_zero(self):
        LC.registar("IT-T7-995", LC.DISCOVERED, "x")
        m = LC.metricas()
        for e in LC.ESTADOS:
            self.assertIn(e, m, "estado %s desapareceu da tabela" % e)
        self.assertEqual(m[LC.DEGRADED], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
