# -*- coding: utf-8 -*-
"""G2 / D25 — a coorte da Big Collection e a leitura de SAFE sobre ela. Sem rede."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import medir_gates_g2 as G  # noqa: E402


def _l(sid, coletor=True, ok=True):
    return {"SOURCE_ID": sid, "NO_COLETOR": coletor, "OK": ok and coletor}


class D25(unittest.TestCase):
    def test_a_coorte_e_so_quem_o_coletor_colhe_e_as_outras_vao_para_a_onda_seguinte(self):
        r = G._d25([_l("A"), _l("B"), _l("C", coletor=False)])
        self.assertEqual((["A", "B"], ["C"], "SAFE"),
                         (r["COORTE"], r["ONDAS_SEGUINTES_ELIGIBLE_WITHOUT_CONTRACT"],
                          r["APPROVED_SOURCE_ROUTE_COVERAGE"]))

    def test_uma_fonte_da_coorte_sem_rota_segura_reprova_e_diz_qual(self):
        r = G._d25([_l("A"), _l("B", ok=False)])
        self.assertEqual(("NOT_SAFE", ["B"]), (r["APPROVED_SOURCE_ROUTE_COVERAGE"], r["COORTE_FALHAM"]))

    def test_coorte_vazia_nao_e_safe(self):
        self.assertTrue(G._d25([_l("A", coletor=False)])["APPROVED_SOURCE_ROUTE_COVERAGE"].startswith("NAO_SEI"))


if __name__ == "__main__":
    unittest.main()
