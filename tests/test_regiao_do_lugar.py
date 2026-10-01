#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""T5 · REGION_ID DO OBJETO DE AFIRMACAO = geografia(FACT_LOCATION) — o dono da regra e motor/v21_normalizar.geografia.

    python -m pytest tests/test_regiao_do_lugar.py -q

O que se prova (coordenador 01/10, T5; medicao do Casco ENTREGA-CASCO-T5-REGIAO.md):
  * a regiao do objeto vem SO do FACT_LOCATION da afirmacao (nunca do SOURCE_LOCATION, nunca do nome cunhado);
  * provincia -> REGION_ID da regiao-continente MAS com REGION_REPRESENTS=False e PROVINCE_IDS (PROVINCIAL != REGIONAL);
  * lugar que a tabela do dono nao conhece -> NAO SEI (sem adivinhar);
  * PAIS / UE NAO SAO REGIAO: geografia() devolve GEO_ITALY/GEO_EU marcados REGIONAL, mas o vocabulario do proprio
    dono os declara constantes de ESCOPO (ITALIA/UE ao lado de REGIOES; escopo() tem NACIONAL/EUROPEU) e o leitor do
    Casco tambem (italy-app-model.js: «GEO_ITALY and GEO_EU are SCOPES, not regions … let a national fact be counted
    as a regional one»). Por isso REGION_ID = NAO SEI e o escopo viaja como NACIONAL/EUROPEU.
Sintetico, construido por regra a partir do caso de tests/test_g0_da_afirmacao (sem IDs nem trechos da R9).
"""
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "tests"))
import _gavetas  # noqa: E402,F401

import motor_das_capacidades as M                # noqa: E402
import gatilho_da_inteligencia as GI             # noqa: E402
from test_g0_da_afirmacao import _Caso, _afirmacao  # noqa: E402

LINHAS = ("Il 3 settembre 2026 piogge intense in Puglia sui vigneti.",
          "Il 4 settembre 2026 piogge intense a Lecce sui vigneti.",
          "Il 5 settembre 2026 caldo anomalo in Italia sui vigneti.",
          "Il 6 settembre 2026 grandine a Nociglia sui vigneti.",
          "Il 7 settembre 2026 piogge intense in Toscana e Umbria sui vigneti.",
          "Il 8 settembre 2026 caldo anomalo in Europa sui vigneti.")
TEXTO = "NOTIZIARIO SINTETICO T5\n" + "\n".join(LINHAS) + "\n"
LUGAR = {LINHAS[0]: "Puglia", LINHAS[1]: "Lecce", LINHAS[2]: "Italia", LINHAS[3]: "Nociglia",
         LINHAS[4]: "Toscana e Umbria", LINHAS[5]: "Europa"}


class _T5(_Caso):
    def setUp(self):
        super().setUp()
        self.linha.update(texto=TEXTO, source_location="Puglia")
        self.afs = {}
        for i, fr in enumerate(LINHAS):
            d = "%d settembre 2026" % (3 + i)
            self.afs[LUGAR[fr]] = _afirmacao(self.linha, fr, d, "2026-09-%02d" % (3 + i), LUGAR[fr], texto=TEXTO)

    def objs(self):
        s = self.correr(*self.afs.values())
        return {o["CHAVES"]["FACT_LOCATION"]: o for o in self.archive(s)}, s

    def geo(self, o):
        return o["CHAVES"]["GEOGRAFIA_DO_LUGAR"]


class TestRegiaoDoLugar(_T5):
    def test_regiao_escrita_vira_region_id_e_representa(self):
        o = self.objs()[0]["Puglia"]
        self.assertEqual(o["CHAVES"]["REGION_ID"], "REGION_PUGLIA")
        g = self.geo(o)
        self.assertEqual((g["GEOGRAPHIC_SCOPE"], g["REGION_REPRESENTS"], g["PROVINCE_IDS"]), ("REGIONAL", True, []))
        es = o["CHAVES"]["ENTITY_SOURCE"]["REGION_ID"]
        self.assertEqual(es["VALOR"], "REGION_PUGLIA")
        self.assertIn("v21_normalizar.geografia", es["ENTITY_SOURCE"])
        self.assertEqual(es["DE"], "AFIRMACAO.FACT_LOCATION")

    def test_provincia_leva_a_regiao_continente_mas_nao_fala_por_ela(self):
        g = self.geo(self.objs()[0]["Lecce"])
        self.assertEqual(self.objs()[0]["Lecce"]["CHAVES"]["REGION_ID"], "REGION_PUGLIA")
        self.assertEqual((g["PROVINCE_IDS"], g["GEOGRAPHIC_SCOPE"], g["REGION_REPRESENTS"]),
                         (["PROV_LECCE"], "PROVINCIAL", False))

    def test_pais_nao_e_regiao(self):
        o = self.objs()[0]["Italia"]
        self.assertEqual(o["CHAVES"]["REGION_ID"], "NAO SEI")
        g = self.geo(o)
        self.assertEqual((g["GEOGRAPHIC_SCOPE"], g["REGION_REPRESENTS"], g["REGION_IDS"]), ("NACIONAL", False, []))
        self.assertIn("GEO_ITALY", g["ESCOPO_IDS"])

    def test_europa_nao_e_regiao(self):
        o = self.objs()[0]["Europa"]
        self.assertEqual(o["CHAVES"]["REGION_ID"], "NAO SEI")
        self.assertEqual(self.geo(o)["GEOGRAPHIC_SCOPE"], "EUROPEU")

    def test_lugar_desconhecido_da_tabela_fica_nao_sei(self):
        o = self.objs()[0]["Nociglia"]
        self.assertEqual(o["CHAVES"]["REGION_ID"], "NAO SEI")
        self.assertEqual(self.geo(o)["GEOGRAPHY_STATE"], "GEOGRAPHY_UNKNOWN")

    def test_duas_regioes_nao_viram_uma(self):
        o = self.objs()[0]["Toscana e Umbria"]
        self.assertEqual(o["CHAVES"]["REGION_ID"], "NAO SEI")
        self.assertEqual(self.geo(o)["REGION_IDS"], ["REGION_TOSCANA", "REGION_UMBRIA"])

    def test_source_location_nunca_vira_regiao(self):
        # a fonte e da Puglia (source_location) e o facto e em lugar desconhecido: nada se herda da fonte
        o = self.objs()[0]["Nociglia"]
        self.assertNotEqual(o["CHAVES"]["REGION_ID"], "REGION_PUGLIA")
        self.assertEqual(self.geo(o)["DE"], "AFIRMACAO.FACT_LOCATION")

    def test_o_motor_e_o_pote_passam_nos_fiscais(self):
        _, s = self.objs()
        self.assertEqual(M.conferir_saida(s), [])
        pote, _ = GI.montar_o_pote(s)
        self.assertEqual(GI.VP.validar(pote), [])
        for o in pote["COMPARTIMENTOS"]["archive"]["OBJETOS"]:
            self.assertIn("GEOGRAFIA_DO_LUGAR", o["FORA_DO_CONTRATO"])
            self.assertEqual(o["CHAVES"]["REGION_ID"], self.geo_do_pote(o))

    def geo_do_pote(self, o):
        g = o["FORA_DO_CONTRATO"]["GEOGRAFIA_DO_LUGAR"]
        return g["REGION_IDS"][0] if g["REGION_ID_DECIDIDO"] else "NAO SEI"


if __name__ == "__main__":
    unittest.main()
