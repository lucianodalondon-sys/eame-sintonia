# -*- coding: utf-8 -*-
"""Guardas da ponte rota-provada -> tabela do coletor (ROTAS-ELEGIVEIS-V1).

Sem rede, sem escrever na tabela real: o portao e trocado por uma lista, e a
escrita vai para um ficheiro temporario.
"""
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))
import onboardar_rotas_provadas as O  # noqa: E402

AQ = {"STRATEGY": "HTML_LINK_DISCOVERY", "MATCH": "URL",
      "INDEX_URL": "https://a.it/", "LINK_PATTERN": "^https?://a\\.it/news/.+$", "MAX_TARGETS": 1}


def _cur(sid, aq=AQ):
    return {"SOURCE_ID": sid, "OWNER": "X", "NAME": "X", "TERRITORY": "T2",
            "BATCH_ID": "LOTE-HTML-ARTIGO", "OUTPUT_TYPE": "HTML", "ACQUISITION": dict(aq)}


def _prova(sid, v="ROUTE_PROVEN", doc="https://a.it/news/um-dois-tres", aq=AQ):
    return {"SOURCE_ID": sid, "VEREDITO": v, "CAUSA": "c", "INDEX_URL": aq["INDEX_URL"],
            "LINK_PATTERN": aq["LINK_PATTERN"], "INDEX_HTTP": 200, "LINKS_DE_DETALHE": 3,
            "CANARIO": {"URL": doc, "BYTES": 5000, "HTML_KIND": "CONTENT",
                        "PARAGRAPH_CHARACTERS": 900}}


class Ponte(unittest.TestCase):
    def planear(self, elegiveis, provas, curator, com_contrato=()):
        with mock.patch.object(O.G, "elegiveis", return_value=list(elegiveis)):
            return O.planear(ctx={}, canario={"GERADO_EM": "2026-09-22T00:00", "LINHAS": provas},
                             curator={c["SOURCE_ID"]: c for c in curator},
                             com_contrato=set(com_contrato))

    def test_elegivel_provada_sem_contrato_entra_com_a_aquisicao_do_curator(self):
        p = self.planear(["IT-T2-001"], [_prova("IT-T2-001")], [_cur("IT-T2-001")])
        self.assertEqual(["IT-T2-001"], [l["SOURCE_ID"] for l in p["ENTRA"]])
        self.assertEqual(AQ, p["ENTRA"][0]["ACQUISITION"])

    def test_nao_elegivel_nunca_entra_mesmo_provada(self):
        p = self.planear([], [_prova("IT-T2-001")], [_cur("IT-T2-001")])
        self.assertEqual([], p["ENTRA"])

    def test_quem_ja_tem_contrato_nao_e_reescrito(self):
        p = self.planear(["IT-T2-001"], [_prova("IT-T2-001")], [_cur("IT-T2-001")],
                         com_contrato=["IT-T2-001"])
        self.assertEqual(([], []), (p["ENTRA"], p["FICA"]))

    def test_canario_nao_provado_fica_com_o_veredito_escrito(self):
        for v in ("UNKNOWN", "CAPABILITY_BLOCK", "POLICY_BLOCK"):
            p = self.planear(["IT-T2-001"], [_prova("IT-T2-001", v)], [_cur("IT-T2-001")])
            self.assertEqual([], p["ENTRA"])
            self.assertIn(v, p["FICA"][0]["PORQUE"])

    def test_sem_canario_fica(self):
        p = self.planear(["IT-T2-001"], [], [_cur("IT-T2-001")])
        self.assertIn("SEM_CANARIO", p["FICA"][0]["PORQUE"])

    def test_canario_de_outra_aquisicao_nao_vale(self):
        outra = dict(AQ, INDEX_URL="https://a.it/news/")
        p = self.planear(["IT-T2-001"], [_prova("IT-T2-001", aq=outra)], [_cur("IT-T2-001")])
        self.assertEqual([], p["ENTRA"])
        self.assertIn("OUTRA aquisicao", p["FICA"][0]["PORQUE"])

    def test_duas_fichas_pelo_mesmo_documento_so_a_primeira_entra(self):
        p = self.planear(["IT-T2-001", "IT-T2-002"],
                         [_prova("IT-T2-001"), _prova("IT-T2-002")],
                         [_cur("IT-T2-001"), _cur("IT-T2-002")])
        self.assertEqual(["IT-T2-001"], [l["SOURCE_ID"] for l in p["ENTRA"]])
        self.assertIn("DUPLICADA", p["FICA"][0]["PORQUE"])

    def test_mesmo_site_e_padrao_de_fonte_ja_contratada_fica_como_duplicada(self):
        outra_porta = dict(AQ, INDEX_URL="https://www.a.it/@@seletor-de-lingua/it")
        p = self.planear(["IT-T2-002"], [_prova("IT-T2-002", aq=outra_porta)],
                         [_cur("IT-T2-001"), _cur("IT-T2-002", aq=outra_porta)],
                         com_contrato=["IT-T2-001"])
        self.assertEqual([], p["ENTRA"])
        self.assertIn("DUPLICADA de fonte ja contratada: IT-T2-001", p["FICA"][0]["PORQUE"])

    def test_outro_site_com_o_mesmo_padrao_nao_e_duplicada(self):
        outro = dict(AQ, INDEX_URL="https://b.it/")
        p = self.planear(["IT-T2-002"], [_prova("IT-T2-002", aq=outro)],
                         [_cur("IT-T2-001"), _cur("IT-T2-002", aq=outro)],
                         com_contrato=["IT-T2-001"])
        self.assertEqual(["IT-T2-002"], [l["SOURCE_ID"] for l in p["ENTRA"]])

    def test_aplicar_acrescenta_sem_repetir(self):
        with tempfile.TemporaryDirectory() as d:
            t = Path(d, "t.json")
            t.write_text(json.dumps({"FONTES": [{"SOURCE_ID": "IT-T2-001"}]}), encoding="utf-8")
            with mock.patch.object(O, "TABELA", t):
                l = O.linha_da_tabela(_cur("IT-T2-002"), _prova("IT-T2-002"), "2026-09-22")
                self.assertEqual(1, O.aplicar([l, {"SOURCE_ID": "IT-T2-001"}]))
                self.assertEqual(1, O.aplicar([l]) + 1)
            self.assertEqual(2, len(json.loads(t.read_text(encoding="utf-8"))["FONTES"]))

    def test_o_ficheiro_nao_tem_source_id_literal(self):
        texto = (RAIZ / "curadoria" / "onboardar_rotas_provadas.py").read_text(encoding="utf-8")
        import re
        self.assertIsNone(re.search(r"IT-T\d+-\d{3}", texto))


if __name__ == "__main__":
    unittest.main()
