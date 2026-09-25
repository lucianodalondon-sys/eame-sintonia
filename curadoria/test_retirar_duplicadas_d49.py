# -*- coding: utf-8 -*-
"""D49 — as 4 duplicadas saem pela marca de catalogo que o portao ja le. Sem rede, sem disco."""
import sys
import unittest
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import collection_gate as G           # noqa: E402
import retirar_duplicadas_d49 as D    # noqa: E402


def _c(sid, **extra):
    return dict({"SOURCE_ID": sid, "TERRITORY": sid.split("-")[1],
                 "ACQUISITION": {"INDEX_URL": "https://x.it/%s" % sid, "LINK_PATTERN": "^x$"}}, **extra)


def _livro(*extra):
    ids = ["IT-T2-051", "IT-T2-056", "IT-T2-106", "IT-T7-043", "IT-T7-100", "IT-T8-021", "IT-T8-068",
           "IT-T7-112", "IT-T7-115"]
    return {"FONTES": [_c(s) for s in ids] + list(extra)}


class D49(unittest.TestCase):
    def test_as_quatro_saem_com_o_motivo_e_quem_fica(self):
        depois, acoes = D.planear(_livro(), quando="2026-09-25T12:00:00+00:00")
        por = {c["SOURCE_ID"]: c for c in depois["FONTES"]}
        self.assertEqual({"IT-T2-056", "IT-T2-106", "IT-T7-100", "IT-T8-068"},
                         {a["SOURCE_ID"] for a in acoes if a["ACAO"] == "APLICA"})
        for sid, fica in (("IT-T2-056", "IT-T2-051"), ("IT-T2-106", "IT-T2-051"),
                          ("IT-T7-100", "IT-T7-043"), ("IT-T8-068", "IT-T8-021")):
            self.assertEqual(D.RETIRADA, por[sid]["ESTADO_CATALOGO"])
            d = por[sid]["CATALOGO_D9"]
            self.assertEqual(("D49", D.MOTIVO, fica, True), (d["DECISAO"], d["MOTIVO"], d["FICA"], d["REVERSIVEL"]))

    def test_quem_fica_e_a_cia_nao_mudam(self):
        depois, _ = D.planear(_livro())
        por = {c["SOURCE_ID"]: c for c in depois["FONTES"]}
        for sid in ("IT-T2-051", "IT-T7-043", "IT-T8-021", "IT-T7-112", "IT-T7-115"):
            self.assertNotIn("ESTADO_CATALOGO", por[sid], sid)

    def test_segunda_passagem_e_ja_aplicada_e_igual(self):
        d1, _ = D.planear(_livro(), quando="t")
        d2, acoes = D.planear(d1, quando="outro")
        self.assertEqual(d1, d2)
        self.assertEqual({"JA_APLICADA"}, {a["ACAO"] for a in acoes})

    def test_sem_a_ficha_que_fica_nao_retira(self):
        livro = _livro()
        livro["FONTES"] = [c for c in livro["FONTES"] if c["SOURCE_ID"] != "IT-T7-043"]
        _, acoes = D.planear(livro)
        a = [x for x in acoes if x["SOURCE_ID"] == "IT-T7-100"][0]
        self.assertEqual("SALTA", a["ACAO"])

    def test_retirada_por_outra_decisao_nao_se_reescreve(self):
        livro = _livro()
        livro["FONTES"][1] = _c("IT-T2-056", ESTADO_CATALOGO=D.RETIRADA, CATALOGO_D9={"DECISAO": "D9"})
        depois, acoes = D.planear(livro)
        self.assertEqual("SALTA", [a for a in acoes if a["SOURCE_ID"] == "IT-T2-056"][0]["ACAO"])
        self.assertEqual({"DECISAO": "D9"}, depois["FONTES"][1]["CATALOGO_D9"])

    def test_invariante_rebenta_se_mexer_noutro_campo(self):
        antes = _livro()
        depois, _ = D.planear(antes)
        depois["FONTES"][0]["TERRITORY"] = "T9"
        with self.assertRaises(D.InvarianteQuebrado):
            D.invariantes(antes, depois)

    def test_o_portao_recusa_com_o_motivo_da_d49(self):
        depois, _ = D.planear(_livro())
        c = {x["SOURCE_ID"]: x for x in depois["FONTES"]}["IT-T7-100"]
        self.assertEqual(G.RETIRADA_POR_DECISAO, c["ESTADO_CATALOGO"])
        self.assertIn("D49 · DUPLICADA_POR_SOBREPOSICAO_DE_ROTA: fica IT-T7-043", c["CATALOGO_D9"]["PORQUE"])


if __name__ == "__main__":
    unittest.main()
