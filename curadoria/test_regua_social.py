#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SOC-ONDA2 — a régua do canário social lê o recibo do Scrap, e não promove o que não viu guardado."""
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))

import regua_social as RG  # noqa: E402

SID, FASE = "IT-T9-024", "video-linkedin"


def _env(itens=None, result="OK", sid=SID, fase=FASE, porque=""):
    return {"SOURCE_ID_DO_PEDIDO": sid, "FASE": fase, "COLHEITA": itens if itens is not None else [],
            "PORQUE_ZERO_COLHEITA": porque,
            "SUPORTE": [{"ESPECIE": "RUN_RECEIPT", "RESUMO": {"RESULT": result}}]}


def _item(autor="Gruppo Caviro", url="https://it.linkedin.com/company/gruppocaviro", **muda):
    ob = {"RAW": {"CREATOR_NAME": autor, "CREATOR_URL": url},"NATIVE_ID": "7490681050906439680", "PUBLISHED_AT": "2026-08-05T08:12:12Z",
          "OWNER_AUTHORIZED": "SIM", "PLATFORM_POLICY_STATUS": "DISALLOWED"}
    ob.update(muda)
    return {"ESPECIE": "COLHEITA", "OBSERVACAO": ob}


class ARegua(unittest.TestCase):
    def test_colheita_com_identidade_e_raw_e_ready(self):
        v, p = RG.julgar(_env([_item(), _item()]), SID, FASE, 2)
        self.assertEqual(v, RG.READY, p)

    def test_visto_sem_raw_no_banco_nao_e_ready(self):
        self.assertEqual(RG.julgar(_env([_item()]), SID, FASE, 0)[0], RG.FALHA)
        self.assertEqual(RG.julgar(_env([_item()]), SID, FASE, None)[0], RG.FALHA)

    def test_item_sem_identidade_ou_sem_autorizacao_falha(self):
        for campo in RG.CAMPOS_DO_ITEM:
            self.assertEqual(RG.julgar(_env([_item(**{campo: "NAO SEI"})]), SID, FASE, 1)[0], RG.FALHA, campo)
        self.assertEqual(RG.julgar(_env([_item(OWNER_AUTHORIZED="NAO")]), SID, FASE, 1)[0], RG.FALHA)

    def test_zero_legitimo_nao_e_falha_nem_ready(self):
        self.assertEqual(RG.julgar(_env([], "ZERO_RESULTS"), SID, FASE, 0)[0], RG.ZERO)

    def test_atlas_que_nao_conhece_e_falha_do_registo_nao_zero(self):
        v, p = RG.julgar(_env([], "ZERO_RESULTS", porque="o pedido nomeou uma fonte que o atlas não conhece: x"),
                         SID, FASE, 0)
        self.assertEqual(v, RG.FALHA)
        self.assertIn("Atlas", p)

    def test_envelope_de_outra_fonte_ou_fase_nao_serve(self):
        self.assertEqual(RG.julgar(_env([_item()], sid="IT-T9-025"), SID, FASE, 1)[0], RG.FALHA)
        self.assertEqual(RG.julgar(_env([_item()], fase="canal-youtube"), SID, FASE, 1)[0], RG.FALHA)

    def test_resultado_nao_ok_com_itens_falha(self):
        self.assertEqual(RG.julgar(_env([_item()], "PARTIAL_ERROR"), SID, FASE, 1)[0], RG.FALHA)


class OAutor(unittest.TestCase):
    """Medido em 24/09: republicacoes de outra organizacao, e um endereco cortado que
    levava a uma empresa do Canada."""

    def _j(self, itens):
        return RG.julgar(_env(itens), SID, FASE, len(itens), slug="gruppocaviro",
                         nome_da_fonte="Caviro — Linkedin ufficiale")

    def test_pagina_propria_com_nome_coerente_e_ready(self):
        self.assertEqual(self._j([_item()])[0], RG.READY)

    def test_so_republicacoes_nao_provam_a_fonte(self):
        v, p = self._j([_item("ABC Interreg", "https://www.linkedin.com/company/abc-interreg")])
        self.assertEqual(v, RG.FALHA)
        self.assertIn("NENHUM publicado", p)

    def test_uma_propria_basta_mesmo_com_republicacoes(self):
        v, _ = self._j([_item("ABC Interreg", "https://www.linkedin.com/company/abc-interreg"), _item()])
        self.assertEqual(v, RG.READY)

    def test_outro_pais_para_e_chama_humano(self):
        v, p = RG.julgar(_env([_item("Societ", "https://ca.linkedin.com/company/societ")]), SID, FASE, 1,
                         slug="societ", nome_da_fonte="SIA — Societa Italiana di Agronomia — Linkedin ufficiale")
        self.assertEqual(v, RG.FALHA)
        self.assertIn("HUMANO", p)

    def test_nome_sem_palavra_em_comum_para(self):
        v, p = RG.julgar(_env([_item("Ri.Nova", "https://it.linkedin.com/company/rinovaricerca")]), SID, FASE, 1,
                         slug="rinovaricerca", nome_da_fonte="CRPV — Centro Ricerche Produzioni Vegetali")
        self.assertEqual(v, RG.FALHA)
        self.assertIn("nenhuma palavra", p)


class OPortaoConheceARegua(unittest.TestCase):
    """ready_split/collection_gate: a promocao social so vale pelo veredito da regua social."""

    def setUp(self):
        import ready_split as RS
        self.RS = RS
        self.promo = {"OBSERVED_AT": "2026-09-24T14:30:00+00:00", "EVIDENCE_REF": "EV-X"}
        self.social = {"ACQUISITION": {"STRATEGY": "SCRAP_FASE", "FASE": FASE}}

    def test_veredito_ready_da_fase_do_contrato_e_social(self):
        r = self.RS.passos_da_promocao(self.promo, {"DADOS": {"VEREDITO": "READY", "FASE": FASE}}, self.social)
        self.assertEqual(r["REGUA"], self.RS.REGUA_SOCIAL)
        self.assertIn(r["REGUA"], self.RS.REGUAS_QUE_ADMITEM)

    def test_sem_veredito_ou_de_outra_fase_e_legacy(self):
        for dados in ({}, {"VEREDITO": "ZERO", "FASE": FASE}, {"VEREDITO": "READY", "FASE": "canal-youtube"}):
            r = self.RS.passos_da_promocao(self.promo, {"DADOS": dados}, self.social)
            self.assertEqual(r["REGUA"], self.RS.REGUA_LEGACY, dados)

    def test_contrato_html_nao_se_promove_pela_regua_social(self):
        html = {"ACQUISITION": {"STRATEGY": "HTML_LINK_DISCOVERY", "INDEX_URL": "https://x.it/news"}}
        r = self.RS.passos_da_promocao(self.promo, {"DADOS": {"VEREDITO": "READY", "FASE": FASE}}, html)
        self.assertEqual(r["REGUA"], self.RS.REGUA_LEGACY)


if __name__ == "__main__":
    unittest.main(verbosity=2)
