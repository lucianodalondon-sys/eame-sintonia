# -*- coding: utf-8 -*-
"""SOCIAL-MICRO-PREP · O VIDEO SOCIAL CHEGA A SALA COM A PRECISAO DA DATA E DO LUGAR.

Medido na Sala DESCARTAVEL (25/09, ce28040c, rede fechada): o video LinkedIn do
ISPRA entrou com `published_at` e `source_location` e as bases — e com
`tempo_lugar_evidencia` na de omissao («pousado antes da migration 033»), as
precisoes SECOND e COUNTRY perdidas. A rota do bruto (sem STRUCTURED) ia a
porta sem passar por `_fato_do_texto`, que so a rota documental chamava.

O item destes testes e o item REAL da porta dessa corrida
(`tests/dados/item-social-ispra-porta.json`), sem a observacao bruta.
"""
import ast
import copy
import json
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in ("", "orquestrador"):
    sys.path.insert(0, os.path.join(RAIZ, p) if p else RAIZ)
import _gavetas  # noqa: E402,F401
import orquestrador as O  # noqa: E402

with open(os.path.join(RAIZ, "tests", "dados", "item-social-ispra-porta.json"), encoding="utf-8") as _f:
    ITEM = json.load(_f)["ITEM"]


class TestOBrutoLevaAEvidencia(unittest.TestCase):
    def setUp(self):
        self.antes = copy.deepcopy(ITEM)
        self.fora = O.item_do_bruto_para_a_porta(ITEM)
        self.ev = self.fora.get("tempo_lugar_evidencia") or {}

    def test_as_precisoes_chegam_a_evidencia(self):
        self.assertEqual(self.ev.get("PUBLISHED_AT_PRECISION"), "SECOND")
        self.assertEqual(self.ev.get("SOURCE_LOCATION_PRECISION"), "COUNTRY")
        self.assertEqual(self.ev.get("LEITOR"), "leis/fato_do_texto.campos_do_fato")

    def test_data_e_lugar_da_fonte_nao_mudam(self):
        for k in ("published_at", "published_at_basis", "source_location", "source_location_basis"):
            self.assertEqual(self.fora.get(k), ITEM.get(k), k)

    def test_publicacao_nunca_vira_data_do_facto(self):
        # o post diz «Oggi» sem marca de que e o proprio dia (D64): NAO SEI com o porque
        self.assertNotEqual(self.fora.get("fact_time"), ITEM["published_at"])
        self.assertIn("NAO SEI", self.fora.get("fact_time_basis") or "")

    def test_lugar_da_fonte_nunca_vira_lugar_do_facto(self):
        self.assertNotEqual(self.fora.get("fact_location"), ITEM["source_location"])

    def test_o_item_da_entrada_nao_e_mexido(self):
        self.assertEqual(ITEM, self.antes)

    def test_sem_precisao_diz_nao_sei_e_nao_inventa(self):
        sem = {k: v for k, v in ITEM.items() if not k.endswith("_precision")}
        ev = O.item_do_bruto_para_a_porta(sem)["tempo_lugar_evidencia"]
        self.assertEqual(ev["PUBLISHED_AT_PRECISION"], "NAO SEI")
        self.assertEqual(ev["SOURCE_LOCATION_PRECISION"], "NAO SEI")

    def test_quem_ja_traz_evidencia_passa_intacto(self):
        ja = dict(ITEM, tempo_lugar_evidencia={"X": 1})
        self.assertIs(O.item_do_bruto_para_a_porta(ja), ja)

    def test_a_rota_do_bruto_passa_pela_leitura(self):
        # ligacao: o ramo SEM estruturados do `correr` chama a funcao.
        # A montagem inteira prova-se na Sala descartavel (SOCIAL-MICRO-PLANO.md).
        with open(os.path.join(RAIZ, "orquestrador", "orquestrador.py"), encoding="utf-8") as f:
            arvore = ast.parse(f.read())
        achou = False
        for no in ast.walk(arvore):
            if isinstance(no, ast.If) and isinstance(no.test, ast.Name) and no.test.id == "estruturados":
                fonte = ast.unparse(ast.Module(body=no.orelse, type_ignores=[]))
                achou = "item_do_bruto_para_a_porta" in fonte and "PARA_A_PORTA" in fonte
        self.assertTrue(achou, "o ramo do bruto foi a porta sem ler tempo e lugar")


if __name__ == "__main__":
    unittest.main()
