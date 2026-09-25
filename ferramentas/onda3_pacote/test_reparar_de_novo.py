#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""REPARAR DE NOVO: só enfileira REPAIR_CONTRACT para quem não é READY nem retirada; só com --aplicar."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import reparar_de_novo as R  # noqa: E402

ESTADOS = {"IT-FALHOU": "CONTRACTED_CANARY_FAILED", "IT-READY": "READY_FOR_COLLECTION",
           "IT-RETIRADA": "CONTRACTED_CANARY_FAILED"}
CONTRATOS = {"IT-FALHOU": {"SOURCE_ID": "IT-FALHOU"}, "IT-READY": {"SOURCE_ID": "IT-READY"},
             "IT-RETIRADA": {"SOURCE_ID": "IT-RETIRADA", "ESTADO_CATALOGO": "RETIRADA_POR_DECISAO",
                             "CATALOGO_D9": {"DECISAO": "D52"}}}


class RepararDeNovo(unittest.TestCase):
    def _plano(self, ids):
        return R.planear(ids, contratos=CONTRATOS, estado_de=ESTADOS.get)

    def test_so_a_falhada_nao_retirada_e_reparada(self):
        p = {x["SOURCE_ID"]: x for x in self._plano(["IT-FALHOU", "IT-READY", "IT-RETIRADA", "IT-FORA"])}
        self.assertEqual("REPARAR", p["IT-FALHOU"]["ACCAO"])
        self.assertEqual("NADA", p["IT-READY"]["ACCAO"])
        self.assertIn("D52", p["IT-RETIRADA"]["PORQUE"])
        self.assertIn("fora do livro", p["IT-FORA"]["PORQUE"])

    def test_aplicar_usa_a_porta_da_fila_com_repair_contract(self):
        fila = []
        with mock.patch.object(R.F, "enfileirar", lambda s, t, **k: fila.append((s, t)) or {"TASK_ID": "T9"}):
            feitas = R.aplicar(self._plano(["IT-FALHOU", "IT-READY"]))
        self.assertEqual([("IT-FALHOU", R.F.REPAIR_CONTRACT)], fila)
        self.assertEqual("T9", feitas[0]["TASK_ID"])

    def test_sem_aplicar_nada_e_escrito(self):
        with mock.patch.object(R, "planear", lambda ids: [{"ACCAO": "REPARAR", "SOURCE_ID": "IT-FALHOU",
                                                            "STATE": "X", "PORQUE": ""}]), \
                mock.patch.object(R, "aplicar", side_effect=AssertionError("escreveu")):
            self.assertEqual(0, R.main(["--fontes=IT-FALHOU"]))


if __name__ == "__main__":
    unittest.main()
