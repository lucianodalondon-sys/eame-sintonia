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


class NinguemEPromovidoASource(_ComFicheiro):
    """Em social, QUEM E A SOURCE nao se adivinha — e esta cadeia nao adivinha.

    A investigacao paralela confirmou que nao se colapsa:

        SOURCE · ACCOUNT/CHANNEL · ORIGINAL_AUTHOR · ORIGINAL_POST
        REPOSTER · REPOST

    Medido nesta arvore: `ORIGINAL_AUTHOR`, `ORIGINAL_POST` e `REPOSTER` nao
    existem em ficheiro nenhum do repositorio. A casa nao tem modelo de repost,
    e esta missao NAO e a que o vai criar.

        NAO TER MODELO != PODER ESCOLHER UM DOS DOIS.

    O resultado correto, quando nao se sabe quem e a fonte, e nao saber.
    """

    def test_a_conta_nao_vira_identidade_de_fonte(self):
        raw = self.ficha({'PLATFORM': 'INSTAGRAM', 'ACCOUNT_ID': 'syngentaitalia',
                          'ACCOUNT_NAME': 'Syngenta Italia',
                          'ACCOUNT_URL': 'https://www.instagram.com/syngentaitalia/'})
        self.assertEqual(raw.SOURCE_ID, art.NAO_SEI)
        self.assertNotEqual(raw.SOURCE_ID, 'syngentaitalia')

    def test_a_conta_pode_ser_publisher_sem_ser_source(self):
        # PUBLISHER e SOURCE_ID sao campos DIFERENTES no contrato. Levar a conta
        # para PUBLISHER nao e promove-la a fonte — e o unico sitio onde ela
        # cabe sem mentir.
        raw = self.ficha({'PLATFORM': 'INSTAGRAM', 'ACCOUNT_ID': 'syngentaitalia'})
        self.assertEqual(raw.PUBLISHER, 'syngentaitalia')
        self.assertEqual(raw.SOURCE_ID, art.NAO_SEI)
        self.assertNotEqual(raw.PUBLISHER, raw.SOURCE_ID)

    def test_caso_F_repost_nao_escolhe_entre_o_repostador_e_o_autor(self):
        # A conta que publicou e A; o autor original e B. Sem contrato que diga
        # qual dos dois e a SOURCE, a resposta e nenhum dos dois.
        raw = self.ficha({'PLATFORM': 'INSTAGRAM',
                          'ACCOUNT_ID': 'conta_A',
                          'ACCOUNT_NAME': 'Perfil A que repostou',
                          'ORIGINAL_AUTHOR': 'conta_B',
                          'ORIGINAL_POST': 'https://www.instagram.com/reel/ORIGINAL/'})
        self.assertEqual(raw.SOURCE_ID, art.NAO_SEI)
        self.assertEqual(raw.SOURCE_LOCATION, art.NAO_SEI)
        self.assertEqual(raw.FACT_LOCATION, art.NAO_SEI)
        # e nenhum dos dois foi escolhido em silencio
        self.assertNotIn('conta_B', str(raw.SOURCE_ID))
        self.assertNotIn('conta_A', str(raw.SOURCE_ID))

    def test_o_autor_original_tambem_nao_vira_localizacao(self):
        raw = self.ficha({'PLATFORM': 'INSTAGRAM',
                          'ORIGINAL_AUTHOR': 'Bayer Italia',
                          'ACCOUNT_NAME': 'Consorzio Italiano'})
        self.assertEqual(raw.SOURCE_LOCATION, art.NAO_SEI)

    def test_a_casa_nao_tem_modelo_de_repost_e_esta_missao_nao_o_inventa(self):
        # Sentinela de escopo: se um destes campos nascer num contrato global,
        # foi noutra missao — e este teste obriga a olhar para ele.
        import os as _os
        achados = []
        for raiz, pastas, fs in _os.walk(RAIZ):
            pastas[:] = [d for d in pastas
                         if d not in ('.git', '__pycache__', 'node_modules', 'tests')]
            for f in fs:
                if not f.endswith('.py'):
                    continue
                caminho = _os.path.join(raiz, f)
                try:
                    with io.open(caminho, encoding='utf-8', errors='replace') as fh:
                        txt = fh.read()
                except Exception:                              # noqa: BLE001
                    continue
                for campo in ('ORIGINAL_AUTHOR', 'ORIGINAL_POST', 'REPOSTER'):
                    if campo in txt:
                        achados.append((_os.path.relpath(caminho, RAIZ), campo))
        self.assertEqual(achados, [],
                         'nasceu um modelo de autoria social: %s. Se foi de '
                         'proposito, esta cadeia precisa de ser remedida contra '
                         'ele.' % achados)


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
