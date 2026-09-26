#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""HR-6: o re-medir so toca READY + HUMAN_REVIEW_REQUIRED, e so escreve com --aplicar.

Sem rede e sem o livro real: o portao, o livro e a fila sao substituidos.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import remedir_hr6 as H  # noqa: E402

VEREDITOS = {
    "IT-HR": {"STATE": "READY_FOR_COLLECTION", "MOTIVO": "HUMAN_REVIEW_REQUIRED"},
    "IT-OK": {"STATE": "READY_FOR_COLLECTION", "MOTIVO": "ELIGIBLE"},
    "IT-FALHOU": {"STATE": "CONTRACTED_CANARY_FAILED", "MOTIVO": "ESTADO_NAO_READY"},
}
CTX = {"livro": {}, "evidencias": {}, "contratos": {}}


class Remedir(unittest.TestCase):
    def setUp(self):
        self.p = [mock.patch.object(H.G, "avaliar", lambda s, **k: dict(VEREDITOS[s])),
                  mock.patch.object(H.G, "url_do_item_aberto", lambda s, **k: "https://ex.it/news/x/")]
        for p in self.p:
            p.start()

    def tearDown(self):
        for p in self.p:
            p.stop()

    def test_so_a_hr_e_re_medida(self):
        plano = H.planear(["IT-HR", "IT-OK", "IT-FALHOU"], ctx=CTX)
        self.assertEqual(["REMEDIR", "NADA", "NADA"], [x["ACCAO"] for x in plano])

    def test_aplicar_escreve_canary_pending_e_validate_route(self):
        plano = H.planear(["IT-HR", "IT-OK"], ctx=CTX)
        reg, fila = [], []
        with mock.patch.object(H.LC, "estado_de", lambda s: "READY_FOR_COLLECTION"), \
                mock.patch.object(H.LC, "registar", lambda *a, **k: reg.append((a, k))), \
                mock.patch.object(H.F, "enfileirar",
                                  lambda s, t, **k: fila.append((s, t)) or {"TASK_ID": "T1"}):
            feitas = H.aplicar(plano)
        self.assertEqual([("IT-HR", H.F.VALIDATE_ROUTE)], fila)
        self.assertEqual(1, len(reg))
        self.assertEqual(("IT-HR", H.LC.CANARY_PENDING), reg[0][0][:2])
        self.assertEqual(H.EVIDENCE_REF, reg[0][1]["evidence_ref"])
        self.assertTrue(feitas[0]["FEITO"])

    def test_estado_mudou_entre_plano_e_escrita_nao_escreve(self):
        plano = H.planear(["IT-HR"], ctx=CTX)
        reg = []
        with mock.patch.object(H.LC, "estado_de", lambda s: "CANARY_PENDING"), \
                mock.patch.object(H.LC, "registar", lambda *a, **k: reg.append(a)):
            feitas = H.aplicar(plano)
        self.assertEqual([], reg)
        self.assertFalse(feitas[0]["FEITO"])

    def test_sem_aplicar_nada_e_escrito(self):
        with mock.patch.object(H, "planear", lambda ids: [{"ACCAO": "REMEDIR", "SOURCE_ID": "IT-HR"}]), \
                mock.patch.object(H, "aplicar", side_effect=AssertionError("escreveu")):
            self.assertEqual(0, H.main(["--fontes=IT-HR"]))


if __name__ == "__main__":
    unittest.main()
