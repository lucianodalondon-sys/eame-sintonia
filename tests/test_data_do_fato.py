# -*- coding: utf-8 -*-
"""INTELLIGENCE R3 · DATA_DO_FACTO_ERRADA — o ano em que uma atividade COMECOU nao e a data do facto.

    py -m unittest tests.test_data_do_fato

Medido na Sala: «Xylella multiplex Matera» (Terra e Vita, publicado 2026-09-13) saiu fact_time = 2013 com a base
«CAMPO · AMARRADO_AO_ACONTECIMENTO · APPROXIMATE», porque o trecho dizia «monitoraggio … avviata nel 2013».
O dono da regra e `leis/fato_do_texto.py::_RE_INICIO_DE_ATIVIDADE`. Os casos vivem em
`tests/dados/data-do-fato/CASOS-DATA-DO-FATO-V1.json`. Sem rede, sem Sala.
"""
import json
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "leis"))
import fato_do_texto as FT   # noqa: E402

CASOS = json.loads((RAIZ / "tests" / "dados" / "data-do-fato" / "CASOS-DATA-DO-FATO-V1.json").read_text(encoding="utf-8"))
PUB = tuple(CASOS["PUBLICACAO"])


def _caso(i):
    return next(c for c in CASOS["CASOS"] if c["ID"] == i)


class TestDataDoFatoFixture(unittest.TestCase):
    def test_cada_caso_da_o_fact_time_esperado(self):
        for c in CASOS["CASOS"]:
            with self.subTest(c["ID"]):
                r = FT.campos_do_fato(c["TEXTO"], *PUB)
                self.assertEqual(c["ESPERADO_FACT_TIME"], r["fact_time"], r["fact_time_basis"])

    def test_o_inicio_tapado_fica_escrito_na_base(self):
        for c in CASOS["CASOS"]:
            if "ESPERADO_TAPADO" not in c:
                continue
            with self.subTest(c["ID"]):
                r = FT.campos_do_fato(c["TEXTO"], *PUB)
                self.assertIn("INICIO_DE_ATIVIDADE_OU_SERIE «%s»" % c["ESPERADO_TAPADO"], r["fact_time_basis"])

    def test_caso_real_nunca_cai_na_publicacao(self):
        c = _caso("REAL-XYLELLA-MATERA")
        r = FT.campos_do_fato(c["TEXTO"], *PUB)
        self.assertEqual(FT.NAO_SEI, r["fact_time"])
        self.assertEqual("NOT_KNOWN", r["fact_time_precision"])
        self.assertNotIn("2026-09-13", r["fact_time"])
        self.assertNotIn("AMARRADO_AO_ACONTECIMENTO", r["fact_time_basis"])
        self.assertIn("a data de publicação sozinha nunca preenche este campo", r["fact_time_basis"])

    def test_caso_real_o_menu_nao_da_lugar(self):
        c = _caso("REAL-XYLELLA-MATERA")
        r = FT.campos_do_fato(c["TEXTO"], *PUB)
        self.assertNotIn(c["NUNCA_NO_LUGAR"], r["fact_location"].split(FT.SEP))

    def test_evento_com_data_propria_continua_a_passar(self):
        for i in ("SINT-EVENTO-COM-DIA-PROPRIO", "SINT-EVENTO-COM-ANO-PROPRIO"):
            with self.subTest(i):
                c = _caso(i)
                r = FT.campos_do_fato(c["TEXTO"], *PUB)
                self.assertEqual(c["ESPERADO_FACT_TIME"], r["fact_time"])
                self.assertIn("AMARRADO_AO_ACONTECIMENTO", r["fact_time_basis"])


class TestInicioDeAtividadeRegra(unittest.TestCase):
    def test_lancamento_de_projeto_medido_no_acervo(self):
        # IT-T2-028 (EXTRATORES-V2-JUNTOS/MEDIDA-80ce1a3f.json): saia fact_time = 2021
        t = ("Lanciato nel 2021, il progetto ha raccolto un nutrito set di dati relativi a 15 indicatori di "
             "sostenibilità che vanno dalla qualità dell’aria al consumo di suolo, dalla mobilità al verde pubblico.\n")
        self.assertEqual(FT.NAO_SEI, FT.campos_do_fato(t)["fact_time"])

    def test_mes_e_ano_do_inicio_tambem_se_tapa(self):
        # sem o conserto o leitor dava fact_time = «settembre» (MONTH): o mes em que o monitoramento comecou
        t = "Il monitoraggio, avviato a settembre 2013, ha rilevato sintomi di Xylella nelle aree di confine.\n"
        r = FT.campos_do_fato(t, *PUB)
        self.assertEqual(FT.NAO_SEI, r["fact_time"], r["fact_time_basis"])
        self.assertIn("«avviato a settembre 2013»", r["fact_time_basis"])

    def test_dal_com_dia_nao_e_inicio_de_serie(self):
        # so o ANO se tapa: «dal 12 settembre» e o dia em que o facto comecou a ser observado
        m = FT._RE_INICIO_DE_ATIVIDADE.search("sintomi osservati dal 12 settembre 2026 in Puglia")
        self.assertIsNone(m)

    def test_nel_sozinho_nao_e_inicio(self):
        self.assertIsNone(FT._RE_INICIO_DE_ATIVIDADE.search("Nel 2025 sono stati constatati 40 focolai"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
