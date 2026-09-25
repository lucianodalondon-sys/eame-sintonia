#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""D37 — cada objeto de video do LinkedIn leva TRES campos separados de politica:
OWNER_AUTHORIZED, PLATFORM_POLICY_STATUS e ROBOTS_STATUS (+ endereco e data da medicao)."""
import inspect
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in ("coleta", "leis", ""):
    sys.path.insert(0, os.path.join(RAIZ, _p) if _p else RAIZ)

import adaptador_linkedin as LI  # noqa: E402


class OsTresCamposSeparados(unittest.TestCase):
    def test_a_organizacao_leva_os_tres_campos_e_a_medicao(self):
        p = LI.politica_do_objeto(LI.DECISAO_DO_DONO)
        self.assertEqual(p["OWNER_AUTHORIZED"], "SIM")
        self.assertEqual(p["PLATFORM_POLICY_STATUS"], "DISALLOWED")
        self.assertEqual(p["ROBOTS_STATUS"], "DISALLOW_ALL")
        self.assertEqual(p["ROBOTS_URL"], "https://www.linkedin.com/robots.txt")
        self.assertRegex(p["ROBOTS_MEDIDO_EM"], r"^\d{4}-\d{2}-\d{2}$")
        self.assertEqual(p["DECISAO_DO_DONO"], "D23")
        self.assertEqual(p["DECISAO_DO_ROBOTS"], "D37")

    def test_nenhum_campo_resume_outro(self):
        p = LI.politica_do_objeto("D23")
        valores = [p["OWNER_AUTHORIZED"], p["PLATFORM_POLICY_STATUS"], p["ROBOTS_STATUS"]]
        self.assertEqual(len(set(valores)), 3)
        for v in valores:
            self.assertNotIn("·", v)

    def test_a_medicao_citada_existe_na_matriz(self):
        texto = open(os.path.join(RAIZ, "leis", "social_matriz.py"), encoding="utf-8").read()
        self.assertIn("linkedin.com/robots.txt", texto)
        self.assertIn("Medido em %s" % LI.ROBOTS_MEDIDO_EM, texto)

    def test_o_bruto_e_o_envelope_levam_os_campos(self):
        fonte = inspect.getsource(LI._adquirir_um)
        self.assertIn("**politica_do_objeto(nome_decisao)", fonte, "o bruto (RAW) tem de levar os campos")
        self.assertIn("envelope.update(politica_do_objeto(nome_decisao))", fonte,
                      "o envelope (a observacao) tem de levar os campos")


if __name__ == "__main__":
    unittest.main(verbosity=2)
