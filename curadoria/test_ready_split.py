#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OS DOIS READY NAO SE MISTURAM — e a regua le-se na evidencia, nao num campo.

Livro, fila, evidencia e contratos numa pasta descartavel. Nada toca o livro
real; o «outro livro» e injectado (sem git).
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import canario as CAN                # noqa: E402
import fila as F                     # noqa: E402
import interface_collection as IC    # noqa: E402
import lifecycle as LC               # noqa: E402
import lotes as LOTES                # noqa: E402
import ready_split as RS             # noqa: E402
import worker as W                   # noqa: E402
from test_canario_detalhe import CONTRATO, INDEX, indice_com_itens, rede  # noqa: E402
from test_retrato_html import artigo_sintetico                            # noqa: E402

VELHA, NOVA, NUNCA = "IT-PROVA-VELHA", "IT-PROVA-NOVA", "IT-PROVA-NUNCA"


def _contrato(sid: str, **extra) -> dict:
    c = json.loads(json.dumps(CONTRATO))
    c["SOURCE_ID"] = sid
    c["SOURCE_CONTRACT_HASH"] = "hash-" + sid[-5:].lower()
    c["IDENTITY"]["DOCUMENT_ID"] = sid + ":URL:{doc.1}"
    c.update(extra)
    return c


class OsDoisReady(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        d = Path(self.tmp.name)
        self._antes = (LC.LIVRO, F.FILA, W.EVIDENCIA, W.CONTRATOS, RS.EVIDENCIA,
                       RS.CONTRATOS, RS.SAIDA, IC.CONTRATOS, IC.CARACT, LOTES.LOTES, LOTES.ALLOC)
        LC.LIVRO = d / "LEDGER.json"
        F.FILA = d / "QUEUE.json"
        W.EVIDENCIA = RS.EVIDENCIA = d / "EVIDENCE.json"
        W.CONTRATOS = RS.CONTRATOS = IC.CONTRATOS = d / "contracts.json"
        RS.SAIDA = d / "SPLIT.json"
        IC.CARACT = d / "nao-existe.json"
        LOTES.LOTES = d / "BATCHES.json"
        LOTES.ALLOC = d / "nao-existe-alloc.json"
        W.CONTRATOS.write_text(json.dumps({"FONTES": [
            _contrato(VELHA), _contrato(NOVA), _contrato(NUNCA)]}), encoding="utf-8")
        # VELHA: promovida pela regua antiga (evidencia sem DETAIL_GATE_PASSED)
        LC.registar(VELHA, LC.CANARY_PENDING, "prova")
        ref = W._guardar_evidencia(VELHA, "CANARY", {"PASS": True, "ALVO": "x"})
        LC.registar(VELHA, LC.READY_FOR_COLLECTION, "canario resolveu", evidence_ref=ref)
        # NOVA: promovida pelo worker com o gate
        LC.registar(NOVA, LC.CANARY_PENDING, "prova")
        F.enfileirar(NOVA, F.CANARY)
        with mock.patch.object(CAN, "buscar", rede({INDEX: indice_com_itens(), "https://ex.it/news/mosca-olivo-calo-termico/": artigo_sintetico()})):
            W.executar_uma(F.proxima(), W._contratos())
        # NUNCA: nunca promovida
        LC.registar(NUNCA, LC.CANARY_PENDING, "prova")

    def tearDown(self):
        (LC.LIVRO, F.FILA, W.EVIDENCIA, W.CONTRATOS, RS.EVIDENCIA, RS.CONTRATOS, RS.SAIDA,
         IC.CONTRATOS, IC.CARACT, LOTES.LOTES, LOTES.ALLOC) = self._antes
        self.tmp.cleanup()

    def test_1_a_regua_le_se_na_evidencia(self):
        self.assertEqual(RS.REGUA_LEGACY, RS.regua_de(VELHA))
        self.assertEqual(RS.REGUA_CURRENT, RS.regua_de(NOVA))
        self.assertEqual("NAO SEI", RS.regua_de(NUNCA))
        self.assertEqual(LC.READY_FOR_COLLECTION, LC.estado_de(NOVA))

    def test_2_separar_nao_mistura_e_conta_o_terceiro_livro(self):
        r = RS.separar(ready_do_outro={VELHA, "IT-T5-999", "IT-T2-998"})
        self.assertEqual(2, r["READY_TOTAL"])
        self.assertEqual(1, r["READY_LEGACY"])
        self.assertEqual(1, r["READY_CURRENT"])
        self.assertEqual([VELHA], [x["SOURCE_ID"] for x in r["DETALHE_LEGACY"]])
        self.assertEqual([NOVA], [x["SOURCE_ID"] for x in r["DETALHE_CURRENT"]])
        t = r["SO_NUM_DOS_LIVROS"]
        self.assertTrue(t["MEDIDO"])
        self.assertEqual(1, t["NOS_DOIS"])
        self.assertEqual([NOVA], t["SO_AQUI"])
        self.assertEqual(2, t["SO_NO_OUTRO"])
        self.assertEqual({"T2": 1, "T5": 1}, t["SO_NO_OUTRO_POR_TERRITORIO"])

    def test_3_outro_livro_ilegivel_e_NAO_SEI_nao_zero(self):
        with mock.patch.object(RS, "_ready_do_outro_livro", return_value=None):
            r = RS.separar()
        self.assertFalse(r["SO_NUM_DOS_LIVROS"]["MEDIDO"])
        self.assertNotIn("SO_NO_OUTRO", r["SO_NUM_DOS_LIVROS"])

    def test_4_contrato_alterado_depois_do_ready_e_marcado_e_remedido(self):
        # a rota da VELHA muda DEPOIS da promocao
        d = json.loads(W.CONTRATOS.read_text(encoding="utf-8"))
        for c in d["FONTES"]:
            if c["SOURCE_ID"] == VELHA:
                c["ROUTE_PROVENANCE"] = {"INTEGRADO_EM": "2999-01-01T00:00:00+00:00"}
        W.CONTRATOS.write_text(json.dumps(d), encoding="utf-8")
        r = RS.separar(ready_do_outro=set())
        self.assertEqual([VELHA], r["DETALHE_LEGACY_COM_CONTRATO_ALTERADO"])
        self.assertFalse(r["DETALHE_CURRENT"][0]["CONTRATO_ALTERADO_DEPOIS_DO_READY"])

        feitas = RS.remedir([VELHA, NUNCA], motivo="contrato alterado")
        self.assertTrue(feitas[0]["FEITO"])
        self.assertFalse(feitas[1]["FEITO"], "so se remede o que esta READY")
        self.assertEqual(LC.CANARY_PENDING, LC.estado_de(VELHA))
        self.assertEqual(1, len([t for t in F.elegiveis() if t["SOURCE_ID"] == VELHA
                                 and t["TASK_TYPE"] == F.VALIDATE_ROUTE]))
        # o READY antigo continua no livro — nao se apaga
        self.assertIsNotNone(RS.ultima_promocao(VELHA))
        r2 = RS.separar(ready_do_outro=set())
        self.assertEqual(0, r2["READY_LEGACY"])
        self.assertEqual([VELHA], r2["DETALHE_LEGACY_SUBSTITUIDAS"])

    def test_5_a_interface_entrega_SO_a_regua_de_hoje(self):
        """⚠️ ESTE TESTE MUDOU DE LADO EM 2026-09-21, E ISSO E O PONTO.

        Antes exigia que `ready_sources()` trouxesse VELHA **e** NOVA, com a
        etiqueta `READY_RULE` a distingui-las. Uma etiqueta que ninguem le nao
        e um portao: a Collection recebia as duas no mesmo saco. Agora a
        entrega e so a regua de hoje, e a VELHA le-se no inventario — onde
        aparece com o motivo da recusa escrito.
        """
        linhas = {r["SOURCE_ID"]: r for r in IC.ready_sources()}
        self.assertEqual([NOVA], sorted(linhas), "READY_LEGACY entrou na entrega")
        self.assertEqual(RS.REGUA_CURRENT, linhas[NOVA]["READY_RULE"])
        self.assertTrue(linhas[NOVA]["COLLECTION_ELIGIBLE"])

        inv = {r["SOURCE_ID"]: r for r in IC.inventario_ready()}
        self.assertEqual([NOVA, VELHA], sorted(inv), "o inventario esconde READY")
        self.assertFalse(inv[VELHA]["COLLECTION_ELIGIBLE"])
        self.assertIn("READY_LEGACY", inv[VELHA]["ELIGIBILITY_REASON"])
        self.assertEqual("hash-velha", inv[VELHA]["CONTRACT_VERSION"],
                         "a chave do contrato e SOURCE_CONTRACT_HASH — nunca mais «NAO SEI»")

        m = IC.metricas_operacionais()
        self.assertEqual((2, 1, 1, 1),
                         (m["READY"], m["READY_LEGACY"], m["READY_CURRENT"],
                          m["COLLECTION_ELIGIBLE"]))
        lote = LOTES.fechar_lote()
        self.assertTrue(lote["CRIADO"])
        fontes = json.loads(LOTES.LOTES.read_text(encoding="utf-8"))["LOTES"][0]["FONTES"]
        self.assertEqual({RS.REGUA_CURRENT}, {f["READY_RULE"] for f in fontes},
                         "o lote levou uma fonte da regua antiga para a Collection")

    def test_6_revalidate_que_passa_vindo_de_CANARY_FAILED_nao_rebenta(self):
        """Antes: ValueError (READY exige CANARY_PENDING/REPAIRING) e o worker
        morria no primeiro REVALIDATE bem sucedido."""
        LC.registar(NUNCA, LC.CONTRACTED_CANARY_FAILED, "falhou antes",
                    evidence_ref="EV-x")
        F.enfileirar(NUNCA, F.REVALIDATE, priority=40)
        with mock.patch.object(CAN, "buscar", rede({INDEX: indice_com_itens(),
                                                    # D32 (1): corpo proprio — o mesmo corpo de outra
                                                    # fonte READY seria DUPLICADA_DE_IRMA, e nao e isso
                                                    # que este teste mede
                                                    "https://ex.it/news/mosca-olivo-calo-termico/": artigo_sintetico(
                                                        corpo="La mosca dell'olivo rallenta con il caldo. " * 40)})):
            r = W.executar_uma(F.proxima(), W._contratos())
        self.assertEqual("OK", r["RESULTADO"])
        self.assertEqual(LC.READY_FOR_COLLECTION, LC.estado_de(NUNCA))
        estados = [t["NEW_STATE"] for t in LC.historia(NUNCA)]
        self.assertEqual([LC.CANARY_PENDING, LC.CONTRACTED_CANARY_FAILED,
                          LC.CANARY_PENDING, LC.READY_FOR_COLLECTION], estados)
        self.assertEqual(RS.REGUA_CURRENT, RS.regua_de(NUNCA))


if __name__ == "__main__":
    unittest.main()
