"""AJUSTES-MICRO — os saltos que gastam o teto: medir (medir_saltos) e propor a entrada final (entrada_final).

Sem rede: o salto le-se no que o transporte ja registou (robots de duas origens na mesma corrida);
a proposta so sai se o LINK_PATTERN aceitar uma materia ja colhida na origem final.
"""
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "ferramentas" / "rendimento"))
sys.path.insert(0, str(RAIZ / "curadoria"))
import medir_saltos as MS  # noqa: E402
import entrada_final as EF  # noqa: E402

PAD = r"^https?://(www\.)?etvilloresi\.it/news/[a-z0-9-]+/[a-z0-9]+(?:-[a-z0-9]+)+/?$"


def _resumo(pedidos, origens, det):
    return {"contadores": {"DETAIL_REQUESTS": det, "COURTESY_REFUSALS": {}},
            "CORTESIA": {"PEDIDOS_POR_DOMINIO": {"x": pedidos}, "ROBOTS": {o: {} for o in origens}}}


class OsSaltos(unittest.TestCase):

    def test_1_desperdicio_e_o_que_passa_de_robots_indice_e_materias(self):
        self.assertEqual(MS.medir_corrida(_resumo(5, ["https://www.v.it", "https://v.it"], 1))["DESPERDICIO"], 2)
        self.assertEqual(MS.medir_corrida(_resumo(5, ["https://m.it"], 3))["DESPERDICIO"], 0)
        self.assertEqual(MS.medir_corrida(_resumo(2, ["https://m.it"], 0))["DESPERDICIO"], 0)

    def test_2_salto_de_origem_so_com_duas_origens_e_a_final_e_a_que_nao_e_do_contrato(self):
        runs = {"R1": _resumo(5, ["https://www.etvilloresi.it", "https://etvilloresi.it"], 1),
                "R2": _resumo(5, ["https://www.cia.it"], 2)}
        est = [("ONDA", {"FONTES": [{"SOURCE_ID": "V", "RUN_ID": "R1"}, {"SOURCE_ID": "C", "RUN_ID": "R2"}]})]
        r = MS.medir(runs, est, {"V": "https://www.etvilloresi.it/", "C": "https://www.cia.it/news/"})
        f = {l["SOURCE_ID"]: l for l in r["FONTES"]}
        self.assertTrue(f["V"]["SALTO_DE_ORIGEM"])
        self.assertEqual(f["V"]["INDEX_URL_PROPOSTO"], "https://etvilloresi.it/")
        self.assertFalse(f["C"]["SALTO_DE_ORIGEM"])            # 1 so origem: o salto (se houver) nao e de origem
        self.assertEqual(r["COM_DESPERDICIO_SEM_SALTO_DE_ORIGEM"], ["C"])


class AEntradaFinal(unittest.TestCase):
    C = {"SOURCE_ID": "V", "ACQUISITION": {"STRATEGY": "HTML_LINK_DISCOVERY", "INDEX_URL": "https://www.etvilloresi.it/",
                                             "LINK_PATTERN": PAD, "MAX_TARGETS": 1}}
    M = {"SALTO_DE_ORIGEM": True, "ORIGEM_FINAL": "https://etvilloresi.it", "DESPERDICIO_POR_CORRIDA": [2, 2]}

    def test_3_propoe_so_a_index_url_com_prova_colhida(self):
        p = EF.propor(self.C, self.M, {"https://etvilloresi.it/news/imprese/la-carovana-del-po/"})
        self.assertEqual(p["DESFECHO"], "PADRAO_NOVO")
        self.assertEqual(p["INDEX_URL"], "https://etvilloresi.it/")
        self.assertEqual(p["LINK_PATTERN"], PAD)                # o padrao nao muda
        self.assertEqual(p["ITEM_LIDO"], "https://etvilloresi.it/news/imprese/la-carovana-del-po/")

    def test_4_sem_prova_na_origem_final_nao_propoe(self):
        p = EF.propor(self.C, self.M, {"https://www.etvilloresi.it/news/imprese/la-carovana-del-po/"})
        self.assertEqual(p["DESFECHO"], "SEM_PROPOSTA")
        p = EF.propor(dict(self.C, ACQUISITION=dict(self.C["ACQUISITION"], LINK_PATTERN=r"^https://www\.etvilloresi\.it/.*")),
                      self.M, {"https://etvilloresi.it/news/imprese/la-carovana-del-po/"})
        self.assertEqual(p["DESFECHO"], "SEM_PROPOSTA")       # o padrao nao aceitaria a origem final

    def test_5_sem_salto_ou_ja_na_final_nao_propoe(self):
        self.assertEqual(EF.propor(self.C, dict(self.M, SALTO_DE_ORIGEM=False), set())["DESFECHO"], "SEM_PROPOSTA")
        ja = dict(self.C, ACQUISITION=dict(self.C["ACQUISITION"], INDEX_URL="https://etvilloresi.it/"))
        self.assertEqual(EF.propor(ja, self.M, {"https://etvilloresi.it/news/imprese/x-y/"})["PORQUE"],
                         "a entrada ja esta na origem final")

    def test_6_pela_porta_do_reparo_so_mudam_os_campos_permitidos_e_fica_por_remedir(self):
        """Com o contrato REAL da Villoresi (fixture): o validador da casa aprova, so a INDEX_URL muda."""
        import json
        import reparar_contrato as RC
        base = json.loads((RAIZ / "tests" / "fixtures" / "entrada_final_villoresi.json").read_text(encoding="utf-8"))["CONTRATO"]
        p = EF.propor(base, self.M, {"https://etvilloresi.it/news/imprese/la-carovana-del-po-un-viaggio/"})
        self.assertEqual(p["DESFECHO"], "PADRAO_NOVO", p)
        novo = RC.aplicar(base, p, quando="2026-09-25T00:00:00Z")
        self.assertEqual(novo["ACQUISITION"]["INDEX_URL"], "https://etvilloresi.it/")
        self.assertEqual({k: v for k, v in novo["ACQUISITION"].items() if k != "INDEX_URL"},
                         {k: v for k, v in base["ACQUISITION"].items() if k != "INDEX_URL"})
        self.assertTrue(novo["REPARO_DE_CONTRATO"]["PRECISA_DE_REMEDIR"])
        self.assertEqual(novo["REPARO_DE_CONTRATO"]["ACQUISITION_ANTERIOR"]["INDEX_URL"], "https://www.etvilloresi.it/")

if __name__ == "__main__":
    unittest.main(verbosity=2)
