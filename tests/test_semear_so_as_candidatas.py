# -*- coding: utf-8 -*-
"""SOCIAL-QUALIFICAR · `semear_qualify_social.py --candidatas` semeia SO o lote pedido.

Sem o filtro entravam todas as elegiveis (40 LinkedIn e 64 YouTube no livro de 25/09), e
entre os canais ha contas que ja sao fonte no vivo por outro endereco. Uma candidata pedida
que nao e elegivel nao entra a forca: diz-se qual.
"""
import io
import os
import sys
import unittest
from contextlib import redirect_stdout
from unittest import mock

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in ("curadoria", "candidatas"):
    sys.path.insert(0, os.path.join(RAIZ, p))
import semear_qualify_social as S  # noqa: E402

ELEG = [{"CANDIDATA_ID": "CAND-0118", "URL": "https://www.linkedin.com/company/ispra_2"},
        {"CANDIDATA_ID": "CAND-0133", "URL": "https://www.linkedin.com/company/arpa-valle-d-aosta"},
        {"CANDIDATA_ID": "CAND-0092", "URL": "https://www.linkedin.com/company/syngenta"}]


class _Fila:
    QUALIFY = "QUALIFY"

    def __init__(self):
        self.t = []

    def _ler(self):
        return {"TAREFAS": [{"TASK_ID": i} for i in range(len(self.t))]}

    def enfileirar(self, sid, tipo, **kw):
        self.t.append(sid)


class TestSoAsCandidatas(unittest.TestCase):
    def correr(self, *args):
        fila = _Fila()
        out = io.StringIO()
        with mock.patch.object(S, "elegiveis", lambda tipo="LINKEDIN": list(ELEG)), \
                mock.patch.dict(sys.modules, {"fila": fila}), \
                mock.patch.object(sys, "argv", ["x", *args]), redirect_stdout(out):
            rc = S.main()
        return rc, fila.t, out.getvalue()

    def test_so_o_lote_entra(self):
        rc, semeadas, _ = self.correr("--aplicar", "--copia", "--candidatas", "CAND-0118,CAND-0133")
        self.assertEqual(rc, 0)
        self.assertEqual(sorted(semeadas), ["CAND-0118", "CAND-0133"])

    def test_pedida_nao_elegivel_nao_entra_e_diz_se(self):
        rc, semeadas, out = self.correr("--aplicar", "--copia", "--candidatas", "CAND-0118,CAND-9999")
        self.assertEqual(semeadas, ["CAND-0118"])
        self.assertIn("CAND-9999", out)
        self.assertIn("NAO ELEGIVEIS", out)

    def test_sem_filtro_entram_todas(self):
        _, semeadas, _ = self.correr("--aplicar", "--copia")
        self.assertEqual(len(semeadas), 3)

    def test_mostrar_nao_semeia(self):
        _, semeadas, out = self.correr("--candidatas", "CAND-0133")
        self.assertEqual(semeadas, [])
        self.assertIn("CAND-0133", out)
        self.assertNotIn("CAND-0092", out)


if __name__ == "__main__":
    unittest.main()
