"""A comparacao previsao x resultado do MICRO (LOTE-MICRO-V3): denominador, NAO_RODOU e o limiar. Sem rede."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ferramentas" / "rendimento"))
import comparar_lote_micro as C  # noqa: E402

LOTE = {"ESCOLHA": [{"SOURCE_ID": s, "PREVISAO_DOCUMENTOS_NOVOS": 3, "PREVISAO_SIM": p}
                    for s, p in [("IT-T10-018", 3.0), ("A", "NAO_SEI"), ("B", "NAO_SEI"), ("C", "NAO_SEI"),
                                 ("D", "NAO_SEI"), ("E", 0.0)]]}


def _cenario(sim_por_fonte, nao_rodou=()):
    estado = {"FONTES": []}
    runs, dec = {}, []
    for i, (s, sim) in enumerate(sim_por_fonte.items()):
        if s in nao_rodou:
            estado["FONTES"].append({"SOURCE_ID": s, "CORREU": False, "PORQUE_NAO_CORREU": "TETO_DOMINIO"})
            continue
        rid = "RUN-%d" % i
        estado["FONTES"].append({"SOURCE_ID": s, "CORREU": True, "RUN_ID": rid, "STATUS": "SUCCESS"})
        runs[rid] = {"RUN_ID": rid, "contadores": {"DETAIL_NEW": 3}}
        dec += [{"corrida": rid, "resultado": "SIM"}] * sim + [{"corrida": rid, "resultado": "NAO_SEI"}]
    return estado, runs, dec


class AComparacao(unittest.TestCase):

    def test_1_dois_sim_em_seis_passa_um_nao(self):
        base = {s: 0 for s in ["IT-T10-018", "A", "B", "C", "D", "E"]}
        r = C.comparar(LOTE, *_cenario(dict(base, **{"IT-T10-018": 2})))
        self.assertTrue(r["PASSA_D35"])
        self.assertAlmostEqual(r["TAXA_D35"], 0.3333, places=3)
        r = C.comparar(LOTE, *_cenario(dict(base, **{"IT-T10-018": 1})))
        self.assertFalse(r["PASSA_D35"])                  # 1/6 = 16,7 % nao e > 16,7 %

    def test_2_nao_rodou_nao_e_zero_e_sai_do_denominador(self):
        base = {s: 0 for s in ["IT-T10-018", "A", "B", "C", "D", "E"]}
        r = C.comparar(LOTE, *_cenario(dict(base, **{"IT-T10-018": 1, "A": 1}), nao_rodou=("E",)))
        self.assertEqual(r["FONTES_QUE_CORRERAM"], 5)
        self.assertEqual(r["NAO_RODARAM"], ["E"])
        self.assertEqual([l["ESTADO"] for l in r["LINHAS"] if l["SOURCE_ID"] == "E"], ["NAO_RODOU"])
        self.assertTrue(r["PASSA_D35"])                   # 2/5 = 40 %

    def test_3_um_so_sim_nunca_passa_mesmo_com_poucas_fontes(self):
        r = C.comparar(LOTE, *_cenario({"IT-T10-018": 1, "A": 0, "B": 0, "C": 0, "D": 0, "E": 0},
                                       nao_rodou=("A", "B", "C", "D")))
        self.assertAlmostEqual(r["TAXA_D35"], 0.5)
        self.assertFalse(r["PASSA_D35"])                  # 50 %, mas < 2 SIM

    def test_4_previsao_contra_resultado_por_fonte(self):
        r = C.comparar(LOTE, *_cenario({"IT-T10-018": 1, "A": 2, "B": 0, "C": 0, "D": 0, "E": 1}))
        v = {l["SOURCE_ID"]: l["SIM_VS_PREVISTO"] for l in r["LINHAS"]}
        self.assertEqual((v["IT-T10-018"], v["A"], v["E"]), ("ABAIXO", "previsao NAO_SEI", "ACIMA"))
        self.assertEqual(r["SIM_SO_DA_MYFRUIT"], 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
