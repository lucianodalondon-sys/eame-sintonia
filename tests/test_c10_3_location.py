#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
C10.3 — PLATAFORMA NAO E LOCALIZACAO.

    PLATFORM         o sistema onde a publicacao existe        INSTAGRAM
    COUNTRY_SCOPE    a frente de trabalho desta casa           IT
    SOURCE_LOCATION  onde a FONTE esta, quando provado
    FACT_LOCATION    onde o FACTO aconteceu, quando provado

Quatro eixos, e nenhum enche o outro. Ate a C10.3 a ficha RAW da cadeia de
Reel fazia `SOURCE_LOCATION = ident.get('PLATFORM')` e produzia
`SOURCE_LOCATION = INSTAGRAM` — semanticamente impossivel, porque o Instagram
e um sistema e nao um sitio no mundo.

O comentario que estava por cima daquela linha ja dizia a lei certa.

    CONTRACT_TEXT != IMPLEMENTATION. O comentario nao corrige o codigo.

E o que estes testes medem e o OBJETO PRODUZIDO, nunca o texto do ficheiro —
uma sentinela ancorada no texto mede o texto, nao a lei.
"""
import io
import os
import shutil
import sys
import tempfile
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in ('ferramentas', 'leis', ''):
    sys.path.insert(0, os.path.join(RAIZ, p) if p else RAIZ)

import artefato as art            # noqa: E402
import reel_transcricao as rt     # noqa: E402


class _ComFicheiro(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix='c103-')
        self.bytes = os.path.join(self.tmp, 'som.m4a')
        with io.open(self.bytes, 'wb') as f:
            f.write(b'x' * 20000)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def ficha(self, ident):
        return rt._ficha_raw(self.bytes, ident, run_id='R1',
                             capture_provider=rt.CAPTURA_YTDLP,
                             media_kind=rt.MIDIA_AUDIO)


class APlataformaNaoEUmSitioNoMundo(_ComFicheiro):
    """O defeito central: INSTAGRAM aparecia como localizacao da fonte."""

    def test_a_plataforma_nao_entra_em_source_location(self):
        raw = self.ficha({'PLATFORM': 'INSTAGRAM'})
        self.assertEqual(raw.SOURCE_LOCATION, art.NAO_SEI)
        self.assertNotEqual(raw.SOURCE_LOCATION, 'INSTAGRAM')

    def test_nenhuma_plataforma_conhecida_vira_localizacao(self):
        for plataforma in ('INSTAGRAM', 'YOUTUBE', 'LINKEDIN', 'FACEBOOK', 'X',
                           'TIKTOK', 'MASTODON'):
            raw = self.ficha({'PLATFORM': plataforma})
            self.assertEqual(raw.SOURCE_LOCATION, art.NAO_SEI, plataforma)
            self.assertEqual(raw.FACT_LOCATION, art.NAO_SEI, plataforma)

    def test_a_plataforma_continua_respondida_no_campo_dela(self):
        # SAIU DE SOURCE_LOCATION, NAO FOI APAGADA. A ficha tem de continuar a
        # responder «de qual plataforma veio?».
        raw = self.ficha({'PLATFORM': 'INSTAGRAM', 'POST_ID': 'ABC'})
        self.assertEqual((raw.NOTES or {}).get('PLATFORM'), 'INSTAGRAM')
        self.assertEqual((raw.NOTES or {}).get('POST_ID'), 'ABC')


class OEscopoNaoEGeografia(_ComFicheiro):
    """COUNTRY_SCOPE e o que eu PEDI. Nao e o que eu PROVEI."""

    def test_country_scope_nao_enche_source_location(self):
        raw = self.ficha({'PLATFORM': 'INSTAGRAM', 'COUNTRY_SCOPE': 'IT'})
        self.assertEqual(raw.COUNTRY_SCOPE, 'IT')
        self.assertEqual(raw.SOURCE_LOCATION, art.NAO_SEI)

    def test_country_scope_nao_enche_fact_location(self):
        raw = self.ficha({'PLATFORM': 'INSTAGRAM', 'COUNTRY_SCOPE': 'IT'})
        self.assertEqual(raw.FACT_LOCATION, art.NAO_SEI)

    def test_o_escopo_continua_a_ser_transportado(self):
        # Corrigir geografia nao e perder o eixo operacional.
        self.assertEqual(self.ficha({'COUNTRY_SCOPE': 'IT'}).COUNTRY_SCOPE, 'IT')


class OQueParecePaisENaoE(_ComFicheiro):
    """Nome de conta, handle, idioma e URL nao provam sitio nenhum."""

    def test_nome_de_conta_com_italia_nao_prova_italia(self):
        raw = self.ficha({'PLATFORM': 'INSTAGRAM',
                          'ACCOUNT_NAME': 'Syngenta Italia',
                          'ACCOUNT_ID': 'syngentaitalia'})
        self.assertEqual(raw.SOURCE_LOCATION, art.NAO_SEI)

    def test_handle_com_italia_nao_prova_italia(self):
        raw = self.ficha({'PLATFORM': 'INSTAGRAM',
                          'ACCOUNT_HANDLE_FROM_URL': 'bayer_italia'})
        self.assertEqual(raw.SOURCE_LOCATION, art.NAO_SEI)

    def test_idioma_italiano_nao_prova_italia(self):
        # Um agronomo suico do Ticino publica em italiano e nao e Italia.
        raw = self.ficha({'PLATFORM': 'INSTAGRAM', 'ITEM_LANGUAGE': 'it'})
        self.assertEqual(raw.SOURCE_LOCATION, art.NAO_SEI)
        self.assertEqual(raw.FACT_LOCATION, art.NAO_SEI)

    def test_url_com_it_no_caminho_nao_prova_italia(self):
        raw = self.ficha({'PLATFORM': 'INSTAGRAM',
                          'SOURCE_URL': 'https://www.instagram.com/it/reel/X/'})
        self.assertEqual(raw.SOURCE_LOCATION, art.NAO_SEI)


class QuandoHaProvaElaEPreservada(_ComFicheiro):
    """Recusar fabricacao nao e recusar evidencia."""

    def test_source_location_provado_e_transportado(self):
        raw = self.ficha({'PLATFORM': 'INSTAGRAM', 'SOURCE_LOCATION': 'IT'})
        self.assertEqual(raw.SOURCE_LOCATION, 'IT')

    def test_fact_location_provado_e_transportado(self):
        raw = self.ficha({'PLATFORM': 'INSTAGRAM', 'FACT_LOCATION': 'ES'})
        self.assertEqual(raw.FACT_LOCATION, 'ES')

    def test_os_dois_continuam_diferentes_quando_sao_diferentes(self):
        # O caso que a Biblia usa: revista italiana noticia praga espanhola.
        raw = self.ficha({'SOURCE_LOCATION': 'IT', 'FACT_LOCATION': 'ES'})
        self.assertEqual(raw.SOURCE_LOCATION, 'IT')
        self.assertEqual(raw.FACT_LOCATION, 'ES')
        self.assertNotEqual(raw.SOURCE_LOCATION, raw.FACT_LOCATION)

    def test_fonte_provada_nao_autoriza_facto(self):
        # MESMO com SOURCE_LOCATION provado, o facto continua por provar.
        raw = self.ficha({'PLATFORM': 'INSTAGRAM', 'SOURCE_LOCATION': 'IT'})
        self.assertEqual(raw.SOURCE_LOCATION, 'IT')
        self.assertEqual(raw.FACT_LOCATION, art.NAO_SEI)


class AAusenciaNaoViraValor(_ComFicheiro):
    def test_campo_ausente_vazio_ou_confissao_fica_no_sentinela(self):
        for valor in (None, '', 'NOT_KNOWN', 'NAO SEI'):
            raw = self.ficha({'PLATFORM': 'INSTAGRAM', 'SOURCE_LOCATION': valor})
            self.assertEqual(raw.SOURCE_LOCATION, art.NAO_SEI, repr(valor))

    def test_a_ficha_declara_os_dois_campos_de_geografia(self):
        # Quem declara SOURCE_LOCATION tem de declarar FACT_LOCATION — e a
        # regra que `tests/test_evidence` ja cobra das amostras publicadas.
        raw = self.ficha({'PLATFORM': 'INSTAGRAM'})
        self.assertTrue(hasattr(raw, 'SOURCE_LOCATION'))
        self.assertTrue(hasattr(raw, 'FACT_LOCATION'))


class OReelRealNaoGanhaGeografia(_ComFicheiro):
    """A sentinela da casa, sem descoberta nova e sem rede."""

    def test_o_reel_sai_sem_geografia_nenhuma_e_isso_e_pass(self):
        ident = rt.identidade_do_url(
            'https://www.instagram.com/reel/C-63RfHoJTU/')
        # O que a identidade de um Reel realmente traz: nenhum campo de
        # geografia. Se a cadeia inventasse um, seria do nada.
        self.assertEqual([k for k in ident if 'LOCATION' in k or 'COUNTRY' in k], [])
        raw = self.ficha(ident)
        self.assertEqual(raw.SOURCE_LOCATION, art.NAO_SEI)
        self.assertEqual(raw.FACT_LOCATION, art.NAO_SEI)
        self.assertEqual((raw.NOTES or {}).get('PLATFORM'), 'INSTAGRAM')
        self.assertEqual((raw.NOTES or {}).get('POST_ID'), 'C-63RfHoJTU')

    def test_o_resto_da_ficha_nao_regrediu(self):
        # C10.1 e C10 continuam de pe na mesma ficha.
        ident = rt.identidade_do_url(
            'https://www.instagram.com/reel/C-63RfHoJTU/')
        raw = self.ficha(ident)
        self.assertEqual(raw.SOURCE_ID, art.NAO_SEI)
        self.assertNotIn('instagram.com', str(raw.SOURCE_ID))
        self.assertIn('instagram.com', raw.SOURCE_URL)
        self.assertEqual((raw.NOTES or {}).get('MEDIA_KIND'), rt.MIDIA_AUDIO)
        self.assertTrue(raw.SHA256)


if __name__ == '__main__':
    unittest.main(verbosity=2)
