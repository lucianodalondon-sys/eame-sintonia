#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""G0/v4 — TODO READY ATRAVESSA O INTAKE (D100 · D100-b/L6 · D62-D64 · INT-LAW-091/100).

    python -m pytest tests/test_todo_ready_atravessa_o_intake.py -v

O DEFEITO (revisao do representante do dono, L1/L5.1): na R4, 180 dos 204 READY
foram tirados ANTES da corrida por um pre-filtro de FACT_TIME, e o mesmo IR da R3
foi reusado sobre um corte com +100 itens. A lei ja dizia o contrario: D62 manda
preservar o facto sem data; INT-LAW-091 manda a chave ausente bloquear SO o
crossing que depende dela.

    NEGATIVO    o ataque que a v3 deixava passar morre com o motivo NOMEADO;
    POSITIVO    a contraprova: o que a v3 fazia bem continua (G0 nao afrouxou —
                PUBLICATION_TIME continua a nao virar FACT_TIME, sem data
                continua a nao virar SINAL).
"""
import json
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
for g in ("", "motor", "provas"):
    if str(RAIZ / g) not in sys.path:
        sys.path.insert(0, str(RAIZ / g))

import corrida_da_inteligencia as CI          # noqa: E402

BASE = "CAMPO · ESCRITO_NO_TEXTO · DATE_EXACT · ancora «il 23 settembre»"


def item(i=1, **kw):
    base = {"ITEM_ID": "IT-X-%d" % i, "SOURCE_ID": "IT-T3-010", "RAW_OBSERVATION_ID": 1000 + i,
            "CORRIDA": "RUN-TESTE", "FACT_TIME": "2026-09-23", "FACT_TIME_BASIS": BASE,
            "CAPTURED_AT": "2026-09-25T22:58:29+00:00", "PUBLISHED_AT": "2026-09-24",
            "FACT_LOCATION": "Puglia", "FACT_LOCATION_BASIS": "CAMPO · CITADO · REGION"}
    base.update(kw)
    return base


SO_PUBLICACAO = dict(FACT_TIME="NAO SEI", FACT_TIME_BASIS="NAO SEI")


def correr(itens, universo="auto"):
    u = {"CORTE": "TESTE", "ITENS_NO_CORTE": len(itens)} if universo == "auto" else universo
    return CI.correr("pergunta de teste", itens, universo=u)


class Negativo_ItemSemDataNaoSaiDoLivro(unittest.TestCase):
    def test_negativo_so_publicacao_fica_no_livro_com_NAO_SEI_e_motivo(self):
        livro = correr([item(**SO_PUBLICACAO)])
        self.assertEqual(len(livro["LINEAGE"]), 1)
        l = livro["LINEAGE"][0]
        self.assertEqual(l["INTAKE"], "ADMITIDO_NA_CORRIDA")
        self.assertEqual(l["FACT_TIME"], CI.NAO_SEI)
        self.assertEqual(l["TEMPORAL_STATE"], "UNKNOWN_WINDOW")
        self.assertIn("FACT_TIME", l["PORQUE_TEMPO"])

    def test_negativo_falta_de_tempo_bloqueia_so_os_usos_que_exigem_tempo(self):
        l = correr([item(**SO_PUBLICACAO)])["LINEAGE"][0]
        self.assertEqual(set(l["USOS_BLOQUEADOS"]), set(CI.USOS_QUE_EXIGEM_TEMPO))
        self.assertIn("CROSSING_SEM_CHAVE_TIME", l["USOS_DISPONIVEIS"])
        self.assertIn("EVIDENCIA_NAVEGAVEL", l["USOS_DISPONIVEIS"])
        self.assertNotIn("ACT_NOW", l["USOS_DISPONIVEIS"])

    def test_negativo_o_pre_filtro_e_recusado(self):
        itens = [item(1), item(2, **SO_PUBLICACAO)]
        livro = CI.correr("pergunta de teste", itens[:1],
                          universo={"CORTE": "TESTE", "ITENS_NO_CORTE": 2})
        self.assertEqual(livro["RESULT_STATE"], "ERROR")
        self.assertIn("PRE_FILTRO", livro["ERRORS"][0]["PORQUE"])

    def test_negativo_corte_novo_nao_reusa_o_IR_do_corte_velho(self):
        a = correr([item(1)], universo={"CORTE": "sha-R3", "ITENS_NO_CORTE": 1})
        b = correr([item(1)], universo={"CORTE": "sha-R4", "ITENS_NO_CORTE": 1})
        self.assertNotEqual(a["INTELLIGENCE_RUN_ID"], b["INTELLIGENCE_RUN_ID"])
        r = CI.correr("pergunta de teste", [item(1)], universo={"CORTE": "sha-R4", "ITENS_NO_CORTE": 1},
                      ja_corridas={a["INTELLIGENCE_RUN_ID"]: a})
        self.assertNotEqual(r["RESULT_STATE"], "REUSED")

    def test_negativo_publicacao_vai_ao_lado_nunca_no_lugar(self):
        l = correr([item(**SO_PUBLICACAO)])["LINEAGE"][0]
        self.assertEqual(l["PUBLICATION_TIME"], "2026-09-24")
        self.assertEqual(l["FACT_TIME"], CI.NAO_SEI)
        self.assertTrue(l["PUBLICATION_TIME_NAO_E_FACT_TIME"])

    def test_negativo_sem_proveniencia_nenhum_uso(self):
        l = correr([item(**dict(SO_PUBLICACAO, RAW_OBSERVATION_ID="NAO SEI"))])["LINEAGE"][0]
        self.assertEqual(l["USOS_DISPONIVEIS"], [])
        self.assertTrue(l["PROVENIENCIA"].startswith("PARCIAL"))

    def test_negativo_futuro_fica_no_livro_e_bloqueia_tempo(self):
        l = correr([item(FACT_TIME="2027-04-20")])["LINEAGE"][0]
        self.assertEqual(l["TEMPORAL_STATE"], "FUTURO_EM_RELACAO_A_CAPTURA")
        self.assertIn("ACT_NOW", l["USOS_BLOQUEADOS"])

    def test_negativo_o_livro_conta_o_intake(self):
        livro = correr([item(1), item(2, **SO_PUBLICACAO), item(3, FACT_TIME="2027-04-20")])
        self.assertEqual(livro["INTAKE"]["RECEBIDOS"], 3)
        self.assertEqual(livro["INTAKE"]["NO_LIVRO"], 3)
        self.assertEqual(livro["INTAKE"]["DESCARTADOS_ANTES_DO_LIVRO"], 0)
        self.assertEqual(livro["INTAKE"]["POR_TEMPORAL_STATE"],
                         {"ANCORADO": 1, "FUTURO_EM_RELACAO_A_CAPTURA": 1, "UNKNOWN_WINDOW": 1})

    def test_negativo_pedido_diz_que_o_item_continua(self):
        livro = correr([item(**SO_PUBLICACAO)])
        self.assertIn("CONTINUA na corrida", livro["REQUIREMENTS"][0]["QUESTION_BLOCKED"])


class Positivo_G0NaoAfrouxou(unittest.TestCase):
    def test_positivo_ancorado_continua_sinal_com_todos_os_usos(self):
        livro = correr([item()])
        self.assertEqual(len(livro["SIGNALS"]), 1)
        l = livro["LINEAGE"][0]
        self.assertEqual(l["TEMPORAL_STATE"], "ANCORADO")
        self.assertEqual(l["USOS_BLOQUEADOS"], {})
        self.assertIn("ACT_NOW", l["USOS_DISPONIVEIS"])

    def test_positivo_sem_data_continua_sem_sinal(self):
        livro = correr([item(**SO_PUBLICACAO)])
        self.assertEqual(livro["SIGNALS"], [])
        self.assertEqual(livro["LINEAGE"][0]["G0"], CI.BLOQUEADO_EM_G0)

    def test_positivo_mesmo_corte_mesmo_IR(self):
        u = {"CORTE": "sha-R5", "ITENS_NO_CORTE": 1}
        self.assertEqual(correr([item()], u)["INTELLIGENCE_RUN_ID"], correr([item()], u)["INTELLIGENCE_RUN_ID"])

    def test_positivo_nada_de_null_no_tempo(self):
        s = json.dumps(correr([item(**SO_PUBLICACAO)]), ensure_ascii=False)
        self.assertNotIn('"FACT_TIME": null', s)

    def test_positivo_a_regra_subiu_para_v4(self):
        self.assertEqual(CI.RULESET_VERSION, "G0/v4")


if __name__ == "__main__":
    unittest.main()
