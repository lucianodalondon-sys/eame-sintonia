#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O frescor da referencia (D117.4): a regra 14/30 dias, contada desde a ULTIMA CHECAGEM."""
import json
import os
import subprocess
import sys
import tempfile
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401

import frescor_da_referencia as F  # noqa: E402


class ARegra14e30(unittest.TestCase):
    def _e(self, checagem, hoje="2026-10-01", edicao="2026-09-14"):
        return F.estado_frescor(edicao, checagem, hoje)

    def test_13_dias_em_dia(self):
        r = self._e("2026-09-18")
        self.assertEqual((r["DIAS_DESDE_A_CHECAGEM"], r["ESTADO_FRESCOR"], r["AUTORIZACOES"]),
                         (13, F.EM_DIA, F.AUTORIZACOES_VALEM_NA_EDICAO))

    def test_14_dias_pode_estar_desatualizado(self):
        r = self._e("2026-09-17")
        self.assertEqual((r["DIAS_DESDE_A_CHECAGEM"], r["ESTADO_FRESCOR"], r["AUTORIZACOES"]),
                         (14, F.PODE_ESTAR_DESATUALIZADO, F.AUTORIZACOES_VALEM_NA_EDICAO))

    def test_29_dias_ainda_nao_pede_confirmacao(self):
        r = self._e("2026-09-02")
        self.assertEqual((r["DIAS_DESDE_A_CHECAGEM"], r["AUTORIZACOES"]), (29, F.AUTORIZACOES_VALEM_NA_EDICAO))

    def test_30_dias_autorizacoes_a_confirmar(self):
        r = self._e("2026-09-01")
        self.assertEqual((r["DIAS_DESDE_A_CHECAGEM"], r["ESTADO_FRESCOR"], r["AUTORIZACOES"]),
                         (30, F.PODE_ESTAR_DESATUALIZADO, F.AUTORIZACOES_A_CONFIRMAR))

    def test_conta_desde_a_checagem_e_nao_desde_a_edicao(self):
        r = self._e("2026-09-30", edicao="2026-06-01")
        self.assertEqual(r["ESTADO_FRESCOR"], F.EM_DIA, "edicao velha checada ontem esta em dia")
        r = self._e("2026-09-01", edicao="2026-09-30")
        self.assertEqual(r["AUTORIZACOES"], F.AUTORIZACOES_A_CONFIRMAR,
                         "edicao nova nao salva uma checagem velha")

    def test_sem_checagem_e_nao_sei_nunca_em_dia(self):
        r = self._e(None)
        self.assertEqual((r["ESTADO_FRESCOR"], r["AUTORIZACOES"], r["ULTIMA_CHECAGEM_OK"]),
                         (F.ESTADO_NAO_SEI, F.AUTORIZACOES_A_CONFIRMAR, "NAO SEI"))

    def test_checagem_no_futuro_nao_prova_frescura(self):
        self.assertEqual(self._e("2026-10-05")["ESTADO_FRESCOR"], F.ESTADO_NAO_SEI)

    def test_aceita_instante_com_hora(self):
        self.assertEqual(self._e("2026-09-18T17:20:53.177Z")["DIAS_DESDE_A_CHECAGEM"], 13)

    def test_expoe_os_tres_campos_da_d117(self):
        r = self._e("2026-09-18")
        for c in ("EDICAO_DATA", "ULTIMA_CHECAGEM_OK", "ESTADO_FRESCOR"):
            self.assertIn(c, r)


class AChecagemVemDoLivro(unittest.TestCase):
    OBS = [
        {"SOURCE_ID": "IT-T4-001", "HEALTH_STATE": "HEALTHY", "OBSERVATION_RESULT": "NEW_DOCUMENT",
         "CAPTURED_AT": "2026-09-18T17:20:53Z", "SOURCE_DATE_ISO": "2026-09-14"},
        {"SOURCE_ID": "IT-T4-001", "HEALTH_STATE": "HEALTHY", "OBSERVATION_RESULT": "SEEN_AGAIN",
         "CAPTURED_AT": "2026-09-22T19:00:00Z", "SOURCE_DATE_ISO": "2026-09-14"},
        {"SOURCE_ID": "IT-T4-001", "HEALTH_STATE": "FAILED", "CAPTURED_AT": "2026-09-29T19:00:00Z"},
        {"SOURCE_ID": "IT-T9-999", "HEALTH_STATE": "FAILED", "CAPTURED_AT": "2026-09-29T19:00:00Z"},
    ]

    def test_seen_again_conta_e_failed_nao(self):
        c = F.checagens_do_livro(self.OBS)
        self.assertEqual(c["IT-T4-001"], {"ULTIMA_CHECAGEM_OK": "2026-09-22T19:00:00Z",
                                          "EDICAO_DATA": "2026-09-14"})
        self.assertEqual(c["IT-T9-999"], {"ULTIMA_CHECAGEM_OK": None, "EDICAO_DATA": None})

    def test_a_cli_responde_em_json(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "observations.ndjson")
            with open(p, "w", encoding="utf-8") as f:
                f.write("\n".join(json.dumps(o) for o in self.OBS) + "\n")
            r = subprocess.run([sys.executable, os.path.join(RAIZ, "leis", "frescor_da_referencia.py"),
                                "--json", "--hoje=2026-10-20", "--livro=%s" % p],
                               capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(r.returncode, 0, r.stderr)
            j = json.loads(r.stdout)
            self.assertEqual(j["FONTES"]["IT-T4-001"]["DIAS_DESDE_A_CHECAGEM"], 28)
            self.assertEqual(j["FONTES"]["IT-T4-001"]["ULTIMA_CHECAGEM_OK_INSTANTE"], "2026-09-22T19:00:00Z")
            self.assertEqual(j["FONTES"]["IT-T9-999"]["ESTADO_FRESCOR"], F.ESTADO_NAO_SEI)


if __name__ == "__main__":
    unittest.main(verbosity=2)
