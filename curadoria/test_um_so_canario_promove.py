#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""UM SO CANARIO PROMOVE (UNIFICACAO-V1, 23/09/2026).

Antes havia dois juizes: o canario do worker promovia READY_FOR_COLLECTION
quando «resolvia», e a regua dos quatro passos (ready_split) decidia depois,
na ponte e no portao, se esse READY valia. No livro unificado: 111 READY, 88
delas LEGACY — READY que o portao nunca deixa colher.

Agora a regua e o juiz na hora da promocao. Tudo numa pasta descartavel, com
a etapa do canario injectada: nenhuma etapa real corre, nada sai a rede.
"""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import sys
AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import fila as F                     # noqa: E402
import lifecycle as LC               # noqa: E402
import ready_split as RS             # noqa: E402
import worker as W                   # noqa: E402
from test_worker_volta_sobrevive import _contrato  # noqa: E402

BOA, PARCIAL = "IT-X-101", "IT-X-102"
ITEM = {"URL": "https://ex.it/news/mosca-olivo-2026/", "HTTP": 200, "HTML_KIND": "CONTENT",
        "CAPA_OU_MATERIA": RS.MATERIA, "PARAGRAPH_CHARACTERS": 2000}


def etapa(sid, contrato):
    if sid == BOA:
        return "OK", {"PASS": True, "DETAIL_GATE_PASSED": True, "DETAIL_ENUMERATED": 5,
                      "ITEM_ABERTO": dict(ITEM)}
    # resolve e passa o gate «nao e capa», mas o corpo e curto: PASS_PARCIAL.
    return "OK", {"PASS": True, "DETAIL_GATE_PASSED": True, "DETAIL_ENUMERATED": 5,
                  "ITEM_ABERTO": dict(ITEM, PARAGRAPH_CHARACTERS=120)}


class UmSoCanarioPromove(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        d = Path(self.tmp.name)
        self._antes = (LC.LIVRO, F.FILA, W.EVIDENCIA, W.CONTRATOS)
        LC.LIVRO = d / "LEDGER.json"
        F.FILA = d / "QUEUE.json"
        W.EVIDENCIA = d / "EVIDENCE.json"
        # o pulso do worker e prova de vida para o supervisor: nunca o real
        self.addCleanup(setattr, W, "PULSO", W.PULSO)
        W.PULSO = d / "WORKER-HEARTBEAT.json"
        W.CONTRATOS = d / "contracts.json"
        W.CONTRATOS.write_text(json.dumps({"FONTES": [_contrato(BOA), _contrato(PARCIAL)]}),
                               encoding="utf-8")
        for sid in (BOA, PARCIAL):
            LC.registar(sid, LC.CANARY_PENDING, "prova")
            F.enfileirar(sid, F.CANARY, priority=60)
        self._etapas = mock.patch.dict(W.ETAPAS, {F.CANARY: etapa})
        self._etapas.start()

    def tearDown(self):
        self._etapas.stop()
        LC.LIVRO, F.FILA, W.EVIDENCIA, W.CONTRATOS = self._antes
        self.tmp.cleanup()

    def test_so_os_quatro_passos_promovem(self):
        feitos = {r["SOURCE_ID"]: r for r in W.correr(pausa=0, verboso=False)}
        self.assertEqual(LC.estado_de(BOA), LC.READY_FOR_COLLECTION)
        self.assertEqual(feitos[BOA]["RESULTADO"], "OK")
        # o canario resolveu, mas a regua nao: nao ha READY, ha falha com o porque.
        self.assertEqual(LC.estado_de(PARCIAL), LC.CONTRACTED_CANARY_FAILED)
        self.assertEqual(feitos[PARCIAL]["RESULTADO"], "PASS_PARCIAL")
        ult = LC.historia(PARCIAL)[-1]
        self.assertIn("regua dos quatro passos", ult["REASON"])
        self.assertTrue(ult["EVIDENCE_REF"])

    def test_toda_a_ready_do_worker_e_current_pela_regua(self):
        W.correr(pausa=0, verboso=False)
        livro = json.loads(LC.LIVRO.read_text(encoding="utf-8"))
        contratos = {c["SOURCE_ID"]: c for c in
                     json.loads(W.CONTRATOS.read_text(encoding="utf-8"))["FONTES"]}
        provas = {p["EVIDENCE_REF"]: p for p in
                  json.loads(W.EVIDENCIA.read_text(encoding="utf-8"))["PROVAS"]}
        prontas = [t["SOURCE_ID"] for t in livro["TRANSICOES"]
                   if t["NEW_STATE"] == LC.READY_FOR_COLLECTION]
        self.assertEqual(prontas, [BOA])
        for sid in prontas:
            self.assertEqual(RS.regua_de(sid, livro=livro, evidencias=provas,
                                         contratos=contratos), RS.REGUA_CURRENT)


class OWorkerPromovePelaListaUnica(unittest.TestCase):
    """BOLETINS-V2: o worker pergunta a LISTA UNICA (RS.REGUAS_QUE_ADMITEM). Uma «pagina = boletim» com a
    prova completa da sua regua (PAGINA_BOLETIM/v1) e promovida; a mesma forma sem o recorte do boletim
    fica PASS_PARCIAL. Antes da lista unica, o worker so via DETAIL/v1 e a pagina nunca era READY."""

    def setUp(self):
        from test_pagina_boletim import contrato_boletim
        self.tmp = tempfile.TemporaryDirectory()
        d = Path(self.tmp.name)
        self._antes = (LC.LIVRO, F.FILA, W.EVIDENCIA, W.CONTRATOS)
        LC.LIVRO = d / "LEDGER.json"
        F.FILA = d / "QUEUE.json"
        W.EVIDENCIA = d / "EVIDENCE.json"
        self.addCleanup(setattr, W, "PULSO", W.PULSO)
        W.PULSO = d / "WORKER-HEARTBEAT.json"
        W.CONTRATOS = d / "contracts.json"
        boa, curta = contrato_boletim(), contrato_boletim()
        boa["SOURCE_ID"], curta["SOURCE_ID"] = "IT-T2-901", "IT-T2-902"
        boa["IDENTITY"]["DOCUMENT_ID"] = boa["IDENTITY"]["DOCUMENT_ID"].replace("IT-T2-900", "IT-T2-901")
        curta["IDENTITY"]["DOCUMENT_ID"] = curta["IDENTITY"]["DOCUMENT_ID"].replace("IT-T2-900", "IT-T2-902")
        W.CONTRATOS.write_text(json.dumps({"FONTES": [boa, curta]}), encoding="utf-8")
        for sid in ("IT-T2-901", "IT-T2-902"):
            LC.registar(sid, LC.CANARY_PENDING, "prova")
            F.enfileirar(sid, F.CANARY, priority=60)

        def etapa_boletim(sid, contrato):
            item = {"URL": contrato["ACQUISITION"]["URL"], "HTTP": 200, "FORMA": "PAGINA_E_BOLETIM",
                    "DOCUMENT_ID": sid + ":BOLETIM:2026-09-24", "CONTENT_SHA256": "a" * 64,
                    "SOURCE_DATE_ISO": "2026-09-24", "DATA_COMPROVADA": True,
                    "BOLETIM_CARACTERES": 3848 if sid == "IT-T2-901" else 40}
            return "OK", {"PASS": True, "DETAIL_GATE_PASSED": True, "DETAIL_GATE": RS.REGUA_PAGINA_BOLETIM,
                          "ITEM_ABERTO": item}
        self._etapas = mock.patch.dict(W.ETAPAS, {F.CANARY: etapa_boletim})
        self._etapas.start()

    def tearDown(self):
        self._etapas.stop()
        LC.LIVRO, F.FILA, W.EVIDENCIA, W.CONTRATOS = self._antes
        self.tmp.cleanup()

    def test_pagina_boletim_completa_e_promovida_a_curta_nao(self):
        feitos = {r["SOURCE_ID"]: r for r in W.correr(pausa=0, verboso=False)}
        self.assertEqual(LC.estado_de("IT-T2-901"), LC.READY_FOR_COLLECTION, feitos.get("IT-T2-901"))
        self.assertEqual(feitos["IT-T2-901"]["RESULTADO"], "OK")
        self.assertEqual(LC.estado_de("IT-T2-902"), LC.CONTRACTED_CANARY_FAILED)
        self.assertEqual(feitos["IT-T2-902"]["RESULTADO"], "PASS_PARCIAL")


if __name__ == "__main__":
    unittest.main()
