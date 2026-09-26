# -*- coding: utf-8 -*-
"""C2 (FREIO-SOCIAL) · a onda social pede `teto=1` por conta LinkedIn e monta rodadas que cabem no D38.

O contrato diz `teto: 2`; duas contas assim dariam 6 pedidos a linkedin.com numa onda.
"""
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (RAIZ, os.path.join(RAIZ, "curadoria"), os.path.join(RAIZ, "orquestrador")):
    sys.path.insert(0, p)
import _gavetas  # noqa: E402,F401
import plano_onda_social as P  # noqa: E402


def contrato(sid, fase, filtros):
    return {"SOURCE_ID": sid, "TERRITORY": "T5",
            "ACQUISITION": {"STRATEGY": "SCRAP_FASE", "FASE": fase, "FILTROS": filtros}}


LI = contrato("IT-T5-190", "video-linkedin", {"pagina": "https://www.linkedin.com/company/ispra_2/", "teto": 2})
YT = contrato("IT-T5-192", "canal-youtube", {"canal_id": "UCXUG407gp3CnWnfS3ycijhA"})


class C2TetoDoPedido(unittest.TestCase):
    def test_o_pedido_leva_teto_1_e_o_contrato_nao_muda(self):
        p = P.pedido_de(LI)
        self.assertEqual(p.filtros["teto"], "1")
        self.assertEqual(LI["ACQUISITION"]["FILTROS"]["teto"], 2)

    def test_sem_override_fica_o_do_contrato(self):
        self.assertEqual(P.pedido_de(LI, teto_linkedin=None).filtros["teto"], "2")

    def test_youtube_nao_ganha_teto(self):
        self.assertNotIn("teto", P.pedido_de(YT).filtros)


class C2Rodadas(unittest.TestCase):
    def linhas(self, n_li, n_yt):
        return ([{"SOURCE_ID": "LI-%d" % i, "FASE": "video-linkedin", "NA_ONDA": True} for i in range(n_li)]
                + [{"SOURCE_ID": "YT-%d" % i, "FASE": "canal-youtube", "NA_ONDA": True} for i in range(n_yt)]
                + [{"SOURCE_ID": "FORA", "FASE": "video-linkedin", "NA_ONDA": False}])

    def test_duas_contas_e_um_canal_por_onda_e_cabe(self):
        r = P.rodadas(self.linhas(5, 2))
        self.assertEqual([len(x["LINKEDIN"]) for x in r], [2, 2, 1])
        self.assertEqual([len(x["YOUTUBE"]) for x in r], [1, 1, 0])
        self.assertEqual(r[0]["PREVISTO_POR_DOMINIO"], {"linkedin.com": 4, "licdn.com": 4, "youtube.com": 4})
        self.assertTrue(all(x["CABE_NO_TETO"] for x in r))
        self.assertNotIn("FORA", [s for x in r for s in x["LINKEDIN"]])

    def test_com_o_teto_do_contrato_duas_contas_nao_cabem(self):
        r = P.rodadas(self.linhas(2, 0), teto_linkedin=2)
        self.assertEqual(r[0]["PREVISTO_POR_DOMINIO"]["linkedin.com"], 6)
        self.assertFalse(r[0]["CABE_NO_TETO"])

    def test_o_youtube_manda_no_numero_de_ondas(self):
        self.assertEqual(len(P.rodadas(self.linhas(2, 7))), 7)


if __name__ == "__main__":
    unittest.main()
