#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Testes da caracterizacao — as regras novas da missao 03.

Os 35 testes das missoes anteriores continuam e nao sao tocados. Aqui testam-se
apenas as regras acrescentadas, e sobretudo as que impedem um juizo errado:

    LOW_YIELD  != LOW_VALUE
    DORMANT    != IRRELEVANT
    «nao li»   != «nao serve»
    listagem   != item
    plataforma != identidade de fonte
"""
from __future__ import annotations

import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))
import caracterizador as CH  # noqa: E402


def item(tipo="HTML", temas=("PHYTOSANITARY",), data="2026-09-01", titulo="x"):
    return {"ITEM_TYPE": tipo, "TOPICS": list(temas),
            "PUBLISHED_AT": data, "TITLE": titulo, "BYTES": 1000,
            "GEOGRAPHIES": [], "CROPS": []}


def ha(dias):
    return (datetime.now(timezone.utc) - timedelta(days=dias)).strftime("%Y-%m-%d")


class TesteAmostragemAdaptativa(unittest.TestCase):
    def test_fonte_homogenea_estabiliza_cedo(self):
        # tres itens do mesmo tipo e tema: nao vale a pena pedir mais
        itens = [item() for _ in range(3)]
        estavel, porque = CH.padrao_estavel(itens)
        self.assertEqual(estavel, "SIM", porque)

    def test_fonte_heterogenea_pede_mais_amostra(self):
        itens = [item(tipo="HTML", temas=("MARKET",)),
                 item(tipo="PDF", temas=("REGULATORY",)),
                 item(tipo="XML", temas=("SCIENCE",))]
        estavel, porque = CH.padrao_estavel(itens)
        self.assertEqual(estavel, "NAO", porque)

    def test_um_item_nao_tem_padrao_e_diz_NAO_SEI(self):
        # ⚠️ um item nao e um padrao fraco: e a AUSENCIA de padrao observavel.
        estavel, _ = CH.padrao_estavel([item()])
        self.assertEqual(estavel, "NAO SEI")

    def test_tecto_nao_e_meta(self):
        self.assertGreater(CH.AMOSTRA_TECTO, CH.AMOSTRA_INICIAL)
        self.assertEqual(CH.AMOSTRA_INICIAL, 3)


class TesteActividade(unittest.TestCase):
    def test_dormant_e_recencia_nao_ritmo(self):
        datas = [ha(400), ha(430), ha(460), ha(490)]
        act, porque = CH.actividade(datas, 4)
        self.assertEqual(act, "DORMANT", porque)

    def test_dormant_nao_e_irrelevante(self):
        # ⚠️ A REGRA QUE PROTEGE O ARQUIVO. Uma fonte parada continua dona do
        # que publicou. O que muda e a cadencia, nao a relevancia.
        _, porque = CH.actividade([ha(400), ha(500), ha(600)], 3)
        self.assertIn("nao e a relevancia", porque.replace("—", "").lower()
                      .replace("o que muda nao e a relevancia", "nao e a relevancia"))
        rel, _ = CH.relevancia(["PHYTOSANITARY"], ["veneto"], [], "DORMANT")
        self.assertEqual(rel, "YES", "DORMANT rebaixou a relevancia")

    def test_sem_datas_e_UNKNOWN_e_nunca_DORMANT(self):
        # nao ter medido != estar parado
        act, porque = CH.actividade([], 3)
        self.assertEqual(act, "UNKNOWN")
        self.assertIn("NAO e DORMANT", porque)

    def test_activo_recente_com_ritmo_semanal(self):
        act, _ = CH.actividade([ha(3), ha(10), ha(17), ha(24)], 4)
        self.assertEqual(act, "ACTIVE_HIGH_FREQUENCY")


class TesteCadencia(unittest.TestCase):
    def test_dormant_recebe_vigia_rara_nao_coleta_regular(self):
        cad, porque = CH.cadencia_inicial("DORMANT", "HTML_SITE")
        self.assertEqual(cad, "QUARTERLY_WATCH")
        self.assertIn("nao coleta regular", porque)

    def test_unknown_recebe_sonda_para_medir_nao_para_colher(self):
        cad, porque = CH.cadencia_inicial("UNKNOWN", "HTML_SITE")
        self.assertEqual(cad, "MONTHLY_PROBE")
        self.assertIn("medir", porque)

    def test_facebook_rebaixa_por_custo_de_rota(self):
        # a rota de navegador custa: nao se visita diariamente de graca
        self.assertEqual(CH.cadencia_inicial("ACTIVE_HIGH_FREQUENCY", "FACEBOOK")[0],
                         "WEEKLY")
        self.assertEqual(CH.cadencia_inicial("ACTIVE_HIGH_FREQUENCY", "HTML_SITE")[0],
                         "DAILY")

    def test_cadencia_nao_usa_valor(self):
        # a Intelligence ainda nao existe: nenhum ramo pode depender de valor
        for act in CH.ACTIVIDADE:
            _, porque = CH.cadencia_inicial(act, "HTML_SITE")
            self.assertNotIn("valor", porque.lower())


class TesteRelevancia(unittest.TestCase):
    def test_low_yield_nao_vira_reject(self):
        # ⚠️ uma fonte que publica 1x por ano pode ser decisiva
        rel, _ = CH.relevancia(["REGULATORY"], ["sicilia"], [], "ACTIVE_LOW_FREQUENCY")
        self.assertEqual(rel, "YES")
        self.assertNotIn("NO", [rel])

    def test_sem_sinal_e_UNKNOWN_nao_NO(self):
        # falta de medida nao e juizo negativo
        rel, porque = CH.relevancia(["UNKNOWN"], [], [], "UNKNOWN")
        self.assertEqual(rel, "UNKNOWN")
        self.assertIn("falta", porque)

    def test_cultura_sozinha_sustenta_relevancia(self):
        rel, _ = CH.relevancia(["UNKNOWN"], [], ["vite", "olivo"], "ACTIVE_LOW_FREQUENCY")
        self.assertEqual(rel, "YES")


class TesteIdentidade(unittest.TestCase):
    """O caso Valagro: a captura funciona e a ficha esta errada sobre quem e."""

    def test_handle_de_outra_empresa_acusa_rebranding(self):
        v, porque = CH.identidade_bate(
            "Valagro — Youtube ufficiale", "https://www.youtube.com/@syngenta",
            ["Breakthroughs for farmers", "Cropwise Operations"])
        self.assertEqual(v, "NAO")
        self.assertIn("syngenta", porque)

    def test_nome_no_endereco_confere(self):
        v, _ = CH.identidade_bate("AgroNotizie — canale YouTube",
                                  "https://www.youtube.com/@agronotizietv", ["x"])
        self.assertEqual(v, "SIM")

    def test_nome_no_conteudo_confere(self):
        v, _ = CH.identidade_bate("ARSAC Calabria — canale", "https://youtube.com/@c1234",
                                  ["ARSAC apresenta o novo servico", "ARSAC em campo"])
        self.assertEqual(v, "SIM")

    def test_ausencia_de_sinal_e_NAO_SEI_nao_NAO(self):
        # ⚠️ nao encontrar o nome != provar que e outra entidade
        v, _ = CH.identidade_bate("Qualquer Consorzio — pagina",
                                  "https://www.facebook.com/abc123", ["Buongiorno"])
        self.assertEqual(v, "NAO SEI")


class TesteSinais(unittest.TestCase):
    def test_tema_exige_dois_sinais(self):
        # uma ocorrencia pode ser um item de menu
        self.assertEqual(CH.temas_de("bollettino fitosanitario"), ["UNKNOWN"])
        self.assertIn("PHYTOSANITARY",
                      CH.temas_de("bollettino fitosanitario e difesa integrata "
                                  "contro la peronospora e l oidio"))

    def test_sem_sinal_e_UNKNOWN_nunca_OTHER(self):
        # OTHER afirmaria que se olhou e nao encaixou; UNKNOWN confessa
        self.assertEqual(CH.temas_de("lorem ipsum dolor sit amet"), ["UNKNOWN"])

    def test_geografia_exige_dois_sinais(self):
        self.assertEqual(CH.geografias_de("veneto"), [])
        self.assertEqual(CH.geografias_de("veneto e ancora veneto"), ["veneto"])

    def test_le_metatags_quando_o_corpo_e_montado_por_javascript(self):
        """MEDIDO: 981 KB de Facebook davam 58 caracteres de texto visivel.
        O conteudo esta nas metatags publicas, e ler so o visivel perdia 14
        fontes reais por defeito do leitor."""
        html = (b'<html><head>'
                b'<meta property="og:description" content="ARPA Veneto - Pagina '
                b'Ufficiale, Veneto. Bollettino agrometeo e monitoraggio">'
                b'</head><body><script>var x=1</script></body></html>')
        t = CH.texto_de(html)
        self.assertIn("arpa veneto", t)
        self.assertIn("veneto", CH.geografias_de(t))


class TesteDecisaoFinal(unittest.TestCase):
    """As duas regras que uma corrida real corrigiu."""

    def setUp(self):
        sys.path.insert(0, str(RAIZ / "curadoria"))
        import consolidar_caracterizacao as CC
        self.CC = CC

    def _f(self, **kw):
        base = {"POLICY_STATUS": "OK", "LOGIN_REQUIRED": "NAO",
                "BROWSER_REQUIRED": "NAO", "SMALL_ADAPTATION_REQUIRED": "NAO",
                "DECLARED_IDENTITY_MATCHES_CONTENT": "SIM",
                "REPRESENTATIVE_SAMPLE_COUNT": 3, "SOURCE_PATTERN_STABLE": "SIM",
                "ACTIVITY": "ACTIVE_LOW_FREQUENCY",
                "INITIAL_COLLECTION_CADENCE": "MONTHLY",
                "SAMPLE_IS_FULL_AVAILABLE_UNIVERSE": False,
                "STABILITY_REASON": "", "SAMPLE_ERROR": None}
        base.update(kw)
        return base

    def test_um_item_nao_e_ONBOARDING_READY_mesmo_sendo_o_universo(self):
        # ⚠️ A REGRA CENTRAL DESTA MISSAO. Medido: 19 fontes com n=1 passavam
        # a READY por «universo inteiro» — refazendo, uma camada acima, o erro
        # que a missao existe para corrigir.
        e, porque = self.CC.decidir(self._f(
            REPRESENTATIVE_SAMPLE_COUNT=1, SOURCE_PATTERN_STABLE="NAO SEI",
            SAMPLE_IS_FULL_AVAILABLE_UNIVERSE=True))
        self.assertEqual(e, "NEEDS_MORE_SAMPLING")
        self.assertIn("nao o que ela normalmente publica", porque)

    def test_universo_inteiro_com_dois_itens_passa(self):
        e, _ = self.CC.decidir(self._f(
            REPRESENTATIVE_SAMPLE_COUNT=2, SOURCE_PATTERN_STABLE="NAO SEI",
            SAMPLE_IS_FULL_AVAILABLE_UNIVERSE=True))
        self.assertEqual(e, "ONBOARDING_READY")

    def test_exige_navegador_e_CAPABILITY_BLOCK_e_nao_falta_de_amostra(self):
        # ⚠️ CAPTURAR UMA AMOSTRA != TER ROTA DE COLETA. Medido: 14 fontes com
        # BROWSER_REQUIRED='NAO SEI' mas rota que exige navegador escapavam.
        e, porque = self.CC.decidir(self._f(
            BROWSER_REQUIRED="NAO SEI",
            SMALL_ADAPTATION_REQUIRED="SIM — exige navegador",
            REPRESENTATIVE_SAMPLE_COUNT=1, SOURCE_PATTERN_STABLE="NAO SEI"))
        self.assertEqual(e, "CAPABILITY_BLOCK")
        self.assertIn("SCRAP", porque)

    def test_dormant_com_padrao_estavel_e_READY(self):
        # DORMANT nao bloqueia: a cadencia ja reflecte o silencio
        e, _ = self.CC.decidir(self._f(ACTIVITY="DORMANT",
                                       INITIAL_COLLECTION_CADENCE="QUARTERLY_WATCH"))
        self.assertEqual(e, "ONBOARDING_READY")

    def test_identidade_errada_sobe_a_humano(self):
        e, _ = self.CC.decidir(self._f(DECLARED_IDENTITY_MATCHES_CONTENT="NAO",
                                       IDENTITY_REASON="handle de outra empresa"))
        self.assertEqual(e, "SEMANTIC_REVIEW_REQUIRED")

    def test_falta_de_amostra_nunca_vira_recusa(self):
        for n, est in ((1, "NAO SEI"), (2, "NAO"), (5, "NAO")):
            e, _ = self.CC.decidir(self._f(REPRESENTATIVE_SAMPLE_COUNT=n,
                                           SOURCE_PATTERN_STABLE=est))
            self.assertNotIn(e, ("REJECT", "REJECTED", "NO"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
