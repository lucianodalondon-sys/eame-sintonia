#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SOC-TEMPO (D61/D63) — a DATA DE PUBLICACAO e o LUGAR DE QUEM PUBLICA chegam a porta, com BASE e PRECISAO.

Dados reais do repositorio: o bruto de um post LinkedIn colhido em 24/09
(`data/samples/SOCIAL-IT/raw-free/LINKEDIN/post-7490681050906439680__3fa4d7dc1dfd8eed.txt`),
o cadastro-mestre (`candidatas/ITALY-SOURCE-MASTER-V1.json`) e o Atlas.
"""
import json
import os
import sys
import tempfile
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in ("coleta", "leis", "regras", ""):
    sys.path.insert(0, os.path.join(RAIZ, _p) if _p else RAIZ)

import adaptador_linkedin as LI      # noqa: E402
import ingresso as ING               # noqa: E402
import lugar_da_organizacao as LO    # noqa: E402
import scrap_colheita as SC          # noqa: E402

POST_REAL = os.path.join(RAIZ, "data", "samples", "SOCIAL-IT", "raw-free", "LINKEDIN",
                         "post-7490681050906439680__3fa4d7dc1dfd8eed.txt")


def _post_real():
    with open(POST_REAL, encoding="utf-8") as f:
        return json.load(f)


def _objeto(**muda):
    raw = _post_real()
    ob = {"PLATFORM": "LINKEDIN", "URL": "https://www.linkedin.com/feed/update/urn:li:activity:7490681050906439680",
          "COUNTRY_SCOPE": "IT", "PUBLISHED_AT": raw["PUBLISHED_AT"],
          "PUBLISHED_AT_SOURCE": "PLATAFORMA — LinkedIn, pagina publica do post, %s" % raw["PUBLISHED_AT_SOURCE"],
          "PUBLISHED_AT_PRECISION": LI.precisao_da_publicacao(raw["PUBLISHED_AT"]),
          "COLLECTED_AT": "2026-09-24T14:07:22+00:00", "SOURCE_LOCATION": None}
    ob.update(muda)
    return ob


class APrecisaoDaPublicacao(unittest.TestCase):
    def test_o_post_real_declara_ate_ao_segundo(self):
        raw = _post_real()
        self.assertEqual(raw["PUBLISHED_AT_SOURCE"], "JSON_LD_VideoObject.datePublished")
        self.assertEqual(LI.precisao_da_publicacao(raw["PUBLISHED_AT"]), "SECOND")

    def test_nao_se_arredonda_para_cima(self):
        self.assertEqual(LI.precisao_da_publicacao("2026-08-05T08:12Z"), "MINUTE")
        self.assertEqual(LI.precisao_da_publicacao("2026-08-05"), "DAY")
        for v in ("", None, "ieri", "NAO SEI"):
            self.assertEqual(LI.precisao_da_publicacao(v), "NAO DECLARADA", v)


class APublicacaoAtravessaComBase(unittest.TestCase):
    def test_data_base_e_precisao_chegam_a_porta(self):
        u = SC.unidade(_objeto(), run_id="IT-T9-X", fonte=None)
        p = ING.para_a_porta(u)
        raw = _post_real()
        self.assertEqual(p["published_at"], raw["PUBLISHED_AT"])
        self.assertIn("JSON_LD_VideoObject.datePublished", p["published_at_basis"])
        self.assertEqual(p["published_at_precision"], "SECOND")

    def test_a_publicacao_nunca_e_a_hora_da_coleta(self):
        # D63: usar a data de coleta no lugar da publicacao REPROVA.
        u = SC.unidade(_objeto(), run_id="IT-T9-X", fonte=None)
        self.assertNotEqual(u["PUBLISHED_AT"], "2026-09-24T14:07:22+00:00")
        self.assertEqual(u["OBSERVED_AT"], "2026-09-24T14:07:22+00:00")

    def test_sem_data_nao_ha_base(self):
        u = SC.unidade(_objeto(PUBLISHED_AT=None, PUBLISHED_AT_PRECISION="NAO DECLARADA"),
                       run_id="IT-T9-X", fonte=None)
        self.assertNotIn("PUBLISHED_AT", u)
        self.assertNotIn("PUBLISHED_AT_BASIS", u, "base de um valor que nao existe nao e prova")
        self.assertEqual(u["PUBLISHED_AT_PRECISION"], "NAO DECLARADA")


class OLugarDeQuemPublica(unittest.TestCase):
    def test_sede_no_cadastro_mestre_da_a_provincia(self):
        r = LO.lugar_da_organizacao("https://www.arpae.it/")
        self.assertEqual((r["SOURCE_LOCATION"], r["SOURCE_LOCATION_PRECISION"]), ("Bologna", "PROVINCE"))
        self.assertIn("IT-OWN-002", r["SOURCE_LOCATION_BASIS"])

    def test_sem_sede_vale_o_pais_da_ficha_e_nunca_a_regiao_de_cobertura(self):
        r = LO.lugar_da_organizacao("https://www.arpalazio.it/")
        self.assertEqual((r["SOURCE_LOCATION"], r["SOURCE_LOCATION_PRECISION"]), ("ITALY", "COUNTRY"))
        self.assertNotIn("LAZIO", r["SOURCE_LOCATION"].upper(), "REGION do Atlas e cobertura, nao morada")

    def test_sem_prova_e_NAO_SEI_com_o_porque(self):
        for s in ("https://nao-existe.example.it/", None):
            r = LO.lugar_da_organizacao(s)
            self.assertEqual(r["SOURCE_LOCATION"], "NAO SEI")
            self.assertTrue(r["SOURCE_LOCATION_BASIS"].startswith("NAO SEI:"))

    def test_conta_de_plataforma_nao_herda_a_sede_do_vizinho(self):
        # DA-16: no Atlas real, youtube.com e instagram.com davam ITALY (pais de OUTRAS fontes).
        for s in ("https://www.youtube.com/channel/UCMfZsQVzUE4oF00c_0nzFVw",
                  "https://www.instagram.com/qualquer_conta/", "https://it.linkedin.com/company/x",
                  "https://open.spotify.com/show/x", "https://www.spreaker.com/show/5506797/episodes/feed",
                  "https://anchor.fm/s/724a46c0/podcast/rss", "https://youtu.be/e0RWUj904Hk"):
            r = LO.lugar_da_organizacao(s)
            self.assertEqual((r["SOURCE_LOCATION"], r["SOURCE_LOCATION_PRECISION"]),
                             ("NAO SEI", "NAO DECLARADA"), s)
            self.assertIn("plataforma", r["SOURCE_LOCATION_BASIS"], s)

    def test_nem_atlas_nem_cadastro_emprestam_morada_a_plataforma(self):
        atlas = "#### IT-T8-999\nCOUNTRY: ITALY\nURL: https://www.youtube.com/@vizinho\n"
        owners = [{"OWNER_ID": "IT-OWN-X", "WEBSITE": "https://www.youtube.com/@vizinho",
                   "PROVINCE": "Roma"}]
        r = LO.lugar_da_organizacao("https://www.youtube.com/@outro", owners=owners, atlas_texto=atlas)
        self.assertEqual(r["SOURCE_LOCATION"], "NAO SEI")

    def test_o_site_oficial_continua_a_dar_a_sede(self):
        r = LO.lugar_da_organizacao("https://www.crea.gov.it/")
        self.assertEqual((r["SOURCE_LOCATION"], r["SOURCE_LOCATION_PRECISION"]), ("Roma", "PROVINCE"))
        self.assertFalse(LO.e_plataforma("youtube-agro.it"), "sufixo parecido nao e plataforma")


class OScrapLeOLugarDoContrato(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="soc-tempo-")
        os.makedirs(os.path.join(self.tmp, "curadoria"))
        with open(os.path.join(self.tmp, LO.LIVRO_CURATOR), "w", encoding="utf-8") as f:
            json.dump({"FONTES": [{"SOURCE_ID": "IT-T2-777", "SOURCE_LOCATION": "Bologna",
                                   "SOURCE_LOCATION_PRECISION": "PROVINCE",
                                   "SOURCE_LOCATION_BASIS": "SEDE declarada no cadastro-mestre (IT-OWN-002)"}]}, f)
        self._raiz = SC.RAIZ
        SC.RAIZ = self.tmp

    def tearDown(self):
        SC.RAIZ = self._raiz

    def test_o_contrato_da_o_lugar_quando_a_observacao_nao_o_traz(self):
        u = SC.unidade(_objeto(), run_id="IT-T2-X", fonte="IT-T2-777")
        p = ING.para_a_porta(u)
        self.assertEqual(p["source_location"], "Bologna")
        self.assertEqual(p["source_location_precision"], "PROVINCE")
        self.assertIn("IT-OWN-002", p["source_location_basis"])

    def test_o_pais_do_pedido_nunca_vira_lugar_da_fonte(self):
        # Fonte sem lugar no contrato: COUNTRY_SCOPE=IT e onde NOS pedimos, nao onde a fonte esta.
        u = SC.unidade(_objeto(COUNTRY_SCOPE="IT"), run_id="IT-T2-X", fonte="IT-T2-000")
        self.assertNotIn("SOURCE_LOCATION", u)
        self.assertNotIn("SOURCE_LOCATION_BASIS", u)

    def test_o_que_a_observacao_declara_ganha_ao_contrato(self):
        u = SC.unidade(_objeto(SOURCE_LOCATION="Faenza"), run_id="IT-T2-X", fonte="IT-T2-777")
        self.assertEqual(u["SOURCE_LOCATION"], "Faenza")


if __name__ == "__main__":
    unittest.main(verbosity=2)
