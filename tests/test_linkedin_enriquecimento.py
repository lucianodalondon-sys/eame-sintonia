# -*- coding: utf-8 -*-
"""As leis do LINKEDIN ENRICHMENT V1, executadas — nao escritas num comentario.

Cada teste aqui existe por um defeito medido nesta rodada, nao por simetria:

  · a rota publica de perfil devolveu 999 para os 5 alvos, e um 999 lido como
    "perfil nao existe" inventaria uma ausencia;
  · a URL de midia do RAW e assinada e vence em ~7 dias — RAW preservado nao e
    midia preservada;
  · dois de tres videos nao tinham fala, e um deles fez o modelo alucinar
    "Suscribete" sobre musica. Aquilo, promovido a fala, poria uma autoridade
    fitossanitaria pedindo inscricao num canal;
  · o corpus espanhol do LinkedIn e o universo canonico sao dois espacos de
    identidade distintos, e casar por nome parecido criaria pessoa.
"""
import datetime
import json
import os
import re
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import linkedin_enriquecimento as le   # noqa: E402

ARTEFATOS = os.path.join(ROOT, 'data', 'samples', 'LINKEDIN-ENRICHMENT')
UTC = datetime.timezone.utc


class TestNaoGastaNada(unittest.TestCase):
    """A frente inteira roda sobre material ja pago. Custo zero e verificavel."""

    def test_nao_importa_o_coletor_pago(self):
        with open(le.__file__, encoding='utf-8') as fh:
            fonte = fh.read()
        for proibido in ('import coletor', 'import apify_pool', 'apify.com'):
            self.assertNotIn(proibido, fonte,
                             'o enriquecimento nao pode abrir rota paga: %s' % proibido)

    def test_saida_declara_zero_execucoes_e_zero_custo(self):
        out = le.enriquecer()
        self.assertEqual(0, out['NEW_ACTOR_RUNS'])
        self.assertEqual(0, out['COST_USD'])


class TestIdentidadeNuncaCriaPessoa(unittest.TestCase):
    """NAME_MATCH != PERSON. O LinkedIn enriquece quem ja existe, ou nao enriquece."""

    def setUp(self):
        self.mapa, _ = le.mapa_de_identidade()

    def test_perfil_sem_prova_sai_nao_sei_e_nao_vira_pessoa(self):
        ident, ligado = le.resolver_identidade(
            'https://www.linkedin.com/in/alguem-que-ninguem-provou-123', self.mapa)
        self.assertFalse(ligado)
        self.assertEqual(le.NAO_SEI, ident['IDENTITY'])
        self.assertEqual(le.NAO_SEI, ident['PERSON_ID'])
        self.assertIn('NÃO autoriza criar pessoa nova', ident['WHY'])

    def test_nao_sei_nao_e_confundido_com_ausencia_de_pessoa(self):
        ident, _ = le.resolver_identidade('https://www.linkedin.com/in/xyz', self.mapa)
        self.assertIn('NÃO significa que a pessoa não exista', ident['WHY'])

    def test_identidade_vem_do_dono_declarado_e_nao_e_decidida_aqui(self):
        ident, _ = le.resolver_identidade('https://www.linkedin.com/in/xyz', self.mapa)
        self.assertEqual('SENSOR-PILOT/CANAL-IDENTIDADE', ident['IDENTITY_OWNER'])

    def test_pessoa_com_varios_perfis_provados_e_carimbada_nao_escolhida(self):
        multiplos = [v for v in self.mapa.values()
                     if v['MULTIPLE_PROVED_PROFILES'] == 'YES']
        # Antonio Logrieco saiu com tres perfis PROVADOS pela regra de identidade.
        # O estado precisa existir para que a pergunta continue aberta.
        for v in multiplos:
            self.assertGreater(v['PERSON_PROFILE_COUNT'], 1)

    def test_dedupe_e_por_identidade_do_conteudo_nunca_pela_consulta(self):
        a = le.identificador_publico(
            'https://www.linkedin.com/in/nicolamori?miniProfileUrn=urn%3Ali%3Afsd%3A1')
        b = le.identificador_publico('https://www.linkedin.com/in/nicolamori/')
        self.assertEqual(a, b, 'o mesmo perfil por duas consultas e UMA pessoa')


class TestMidiaAssinadaVence(unittest.TestCase):
    """RAW PRESERVADO != MIDIA PRESERVADA."""

    def test_url_vencida_e_estado_e_nao_ausencia_de_video(self):
        passado = int(datetime.datetime(2020, 1, 1, tzinfo=UTC).timestamp())
        estado, _exp = le.estado_da_url_de_midia(
            'https://dms.licdn.com/x/y.mp4?e=%d&v=beta' % passado)
        self.assertEqual(le.MEDIA_URL_EXPIRED, estado)
        self.assertNotEqual(le.NO_VIDEO, estado)

    def test_url_viva_e_reconhecida(self):
        futuro = int((datetime.datetime.now(UTC)
                      + datetime.timedelta(days=3)).timestamp())
        estado, exp = le.estado_da_url_de_midia('https://x/y.mp4?e=%d' % futuro)
        self.assertEqual(le.MEDIA_URL_PRESENT, estado)
        self.assertTrue(exp.endswith('Z'))

    def test_ausencia_de_url_nao_e_url_vencida(self):
        estado, _ = le.estado_da_url_de_midia(None)
        self.assertEqual(le.MEDIA_URL_ABSENT, estado)

    def test_video_com_url_vencida_nao_diz_que_o_video_nao_tem_fala(self):
        passado = int(datetime.datetime(2020, 1, 1, tzinfo=UTC).timestamp())
        post = {'HAS_VIDEO': True, 'MEDIA_URL_STATE': le.MEDIA_URL_EXPIRED,
                'MEDIA_URL_EXPIRES_AT': '2020-01-01T00:00:00Z'}
        esc = le.escada_do_video(post)
        self.assertEqual(le.MEDIA_URL_EXPIRED, esc['VIDEO_LADDER'])
        self.assertIn('NÃO significa que o vídeo não tenha fala', esc['WHY'])
        _ = passado


class TestEscadaDoVideo(unittest.TestCase):
    """VIDEO != FALA, e TRANSCRICAO VAZIA != SEM AUDIO."""

    def _post(self):
        return {'HAS_VIDEO': True, 'MEDIA_URL_STATE': le.MEDIA_URL_PRESENT,
                'MEDIA_URL_EXPIRES_AT': '2099-01-01T00:00:00Z'}

    def test_falha_de_rota_nunca_vira_video_sem_legenda(self):
        esc = le.escada_do_video(self._post())
        self.assertEqual(le.NATIVE_CAPTION_NOT_IN_ROUTE, esc['NATIVE_CAPTION'])
        self.assertIn('NÃO SEI', esc['NATIVE_CAPTION_WHY'])

    def test_audio_lido_e_sem_fala_e_no_speech_nao_sem_audio(self):
        esc = le.escada_do_video(self._post(),
                                 {'TEXT': '', 'AUDIO_SECONDS': 21.8, 'MODEL': 'small'})
        self.assertEqual(le.NO_SPEECH_DETECTED, esc['VIDEO_LADDER'])
        self.assertEqual('YES', esc['AUDIO_WAS_READ'])
        self.assertIn('VÍDEO ≠ FALA', esc['WHY'])

    def test_alucinacao_curta_nao_e_promovida_a_voz_da_pessoa(self):
        # o caso real: 19 s de musica devolveram "Suscribete!"
        esc = le.escada_do_video(self._post(),
                                 {'TEXT': '¡Suscríbete!', 'AUDIO_SECONDS': 18.8,
                                  'MODEL': 'small'})
        self.assertEqual(le.SUSPECTED_HALLUCINATION, esc['VIDEO_LADDER'])
        self.assertNotEqual('WHISPER_TRANSCRIPT', esc['CONTENT_SOURCE'])

    def test_fala_densa_de_verdade_passa(self):
        esc = le.escada_do_video(self._post(),
                                 {'TEXT': 'x' * 823, 'AUDIO_SECONDS': 64.0,
                                  'MODEL': 'small'})
        self.assertEqual(le.TRANSCRIPT_OK, esc['VIDEO_LADDER'])
        self.assertEqual('WHISPER_TRANSCRIPT', esc['CONTENT_SOURCE'])

    def test_sem_video_nao_entra_na_escada(self):
        esc = le.escada_do_video({'HAS_VIDEO': False})
        self.assertEqual(le.NO_VIDEO, esc['VIDEO_LADDER'])

    def test_midia_viva_sem_whisper_e_not_attempted_nao_sem_fala(self):
        esc = le.escada_do_video(self._post())
        self.assertEqual(le.NOT_ATTEMPTED, esc['VIDEO_LADDER'])
        self.assertNotEqual(le.NO_SPEECH_DETECTED, esc['VIDEO_LADDER'])


class TestFatoInterpretacaoAcaoSeparados(unittest.TestCase):
    """As tres coisas nao cabem no mesmo dicionario, por construcao."""

    def test_cada_um_carrega_so_a_sua_chave(self):
        f = le.fato('o autor escreveu que houve aumento de pressao', {'X': 1})
        i = le.interpretacao('pode reforcar o sinal regional', 'FACT-1')
        a = le.acao('investigar conteudo local', 'DESENVOLVIMENTO_DE_MERCADO')
        self.assertNotIn('INTERPRETATION', f)
        self.assertNotIn('ACTION', f)
        self.assertNotIn('FACT', i)
        self.assertNotIn('ACTION', i)
        self.assertNotIn('FACT', a)
        self.assertNotIn('INTERPRETATION', a)

    def test_interpretacao_e_acao_nascem_marcadas_como_nao_provadas(self):
        self.assertEqual('HYPOTHESIS_NOT_PROVED',
                         le.interpretacao('x', 'y')['STATUS'])
        self.assertEqual('SUGGESTED_NOT_DECIDED', le.acao('x', 'y')['STATUS'])


class TestProveniencia(unittest.TestCase):
    """Todo fato resolve para a execucao que o produziu."""

    def _prov(self):
        return le.proveniencia(
            {'POST_URL': 'https://linkedin.com/posts/x', 'POST_ID': '1',
             'PUBLICATION_DATE': '2026-05-19T09:44:34.197Z'},
            {'PERSON_ID': 'https://openalex.org/A1'},
            content_source='POST_TEXT', transcript_method='NOT_AVAILABLE',
            run_id='ES-T8-002-2026-08-29-a',
            raw_path='data/samples/raw-paid/ES-T8-002-linkedin-posts-a.raw.json.gz',
            idioma='es')

    def test_campos_obrigatorios_da_missao(self):
        p = self._prov()
        for c in ('SOURCE_PLATFORM', 'SOURCE_URL', 'PERSON_ID', 'POST_ID',
                  'CAPTURED_AT', 'PUBLICATION_DATE', 'ORIGINAL_LANGUAGE',
                  'CONTENT_SOURCE', 'TRANSCRIPT_METHOD'):
            self.assertIn(c, p)
        self.assertEqual('LINKEDIN', p['SOURCE_PLATFORM'])

    def test_o_raw_que_sustenta_o_fato_e_nomeado(self):
        p = self._prov()
        self.assertTrue(p['RAW_EVIDENCE_PATH'].endswith('.raw.json.gz'))
        self.assertTrue(os.path.exists(os.path.join(ROOT, p['RAW_EVIDENCE_PATH'])))

    def test_enum_invalido_e_recusado_e_nao_gravado_torto(self):
        with self.assertRaises(AssertionError):
            le.proveniencia({}, {}, content_source='INVENTADO',
                            transcript_method='NOT_AVAILABLE', run_id='x',
                            raw_path='y', idioma='es')

    def test_localizacao_do_perfil_nao_vira_localizacao_do_fato(self):
        self.assertIn('NÃO DERIVADO', self._prov()['FACT_LOCATION'])


class TestPerfilNaoInfereCargo(unittest.TestCase):
    """headline prova a APRESENTACAO, nunca o papel tecnico."""

    def test_campos_declarados_sao_carimbados_como_declaracao(self):
        c = le.campos_de_perfil({'headline': 'Agronomo | Investigador',
                                 'firstName': 'A', 'lastName': 'B'})
        self.assertEqual('Agronomo | Investigador', c['SELF_DECLARED_HEADLINE'])
        self.assertNotIn('ROLE', c)
        self.assertIn('NÃO é derivado da headline', c['ROLE_NOT_INFERRED'])

    def test_metrica_social_fica_longe_do_fato_e_avisada(self):
        c = le.campos_de_perfil({'headline': 'x', 'followerCount': 99999})
        self.assertIn('FOLLOWERS ≠ AUTHORITY', c['ENGAGEMENT']['AVISO'])

    def test_campo_vazio_nao_conta_como_ganho(self):
        c = le.campos_de_perfil({'headline': 'x', 'about': None, 'skills': []})
        self.assertNotIn('SELF_DECLARED_ABOUT', le.ganho_de_perfil(c))
        self.assertNotIn('SELF_DECLARED_SKILLS', le.ganho_de_perfil(c))


class TestPostPreservaOQueANormalizacaoPerdia(unittest.TestCase):

    def _post_bruto(self):
        return {
            'id': '1', 'linkedinUrl': 'https://linkedin.com/posts/1',
            'content': 'texto com #repilo e https://exemplo.test/a',
            'author': {'name': 'X', 'linkedinUrl': 'https://www.linkedin.com/in/x?y=1'},
            'postedAt': {'date': '2026-05-19T09:44:34.197Z', 'postedAgoShort': '3mo'},
            'postVideo': {'videoUrl': 'https://dms.licdn.com/v.mp4?e=4102444800',
                          'thumbnailUrl': 't'},
            'postImages': [{'url': 'i'}],
            'document': {'title': 'D', 'transcribedDocumentUrl': 'https://x/d.pdf'},
            'article': {'title': 'A', 'link': 'https://x/a', 'subtitle': 'site'},
            'contentAttributes': [
                {'type': 'PROFILE_MENTION', 'profile': {'linkedinUrl': 'u'}},
                {'type': 'COMPANY_NAME', 'company': {'name': 'ACME'}}],
        }

    def test_midia_hashtag_mencao_e_link_sobrevivem(self):
        c = le.campos_de_post(self._post_bruto())
        self.assertTrue(c['HAS_VIDEO'])
        self.assertEqual(['repilo'], c['HASHTAGS'])
        self.assertEqual(['u'], c['PROFILE_MENTIONS'])
        self.assertEqual(['ACME'], c['COMPANY_MENTIONS'])
        self.assertEqual(1, len(c['EXTERNAL_LINKS']))
        self.assertTrue(c['DOCUMENT_PDF_URL'].endswith('.pdf'))
        self.assertEqual('https://x/a', c['ARTICLE_LINK'])

    def test_data_relativa_nao_vira_data_absoluta(self):
        c = le.campos_de_post(dict(self._post_bruto(),
                                   postedAt={'postedAgoShort': '3mo'}))
        self.assertEqual(le.NAO_SEI, c['PUBLICATION_DATE'])
        self.assertEqual('3mo', c['PUBLICATION_DATE_RELATIVE'])


class TestArtefatos(unittest.TestCase):
    """O que foi gravado precisa continuar verdadeiro e sem segredo."""

    def _carrega(self, nome):
        p = os.path.join(ARTEFATOS, nome)
        if not os.path.exists(p):
            self.skipTest('%s ainda nao foi gerado' % nome)
        with open(p, encoding='utf-8') as f:
            return f.read()

    def test_nenhum_artefato_carrega_token(self):
        for nome in ('ENRIQUECIMENTO-V1.json', 'MICROTESTE-V1.json'):
            texto = self._carrega(nome)
            self.assertIsNone(re.search(r'apify_api_[A-Za-z0-9]{10,}', texto),
                              '%s carrega token' % nome)

    def test_microteste_declara_custo_zero(self):
        d = json.loads(self._carrega('MICROTESTE-V1.json'))
        self.assertEqual(0, d['API_COST_USD'])
        self.assertEqual(0, d['NEW_ACTOR_RUNS'])

    def test_o_999_e_estado_de_acesso_e_nao_perfil_inexistente(self):
        d = json.loads(self._carrega('MICROTESTE-V1.json'))
        rota = d['A_ROTA_PUBLICA_DE_PERFIL']
        self.assertEqual('NOT_ACHIEVABLE_ON_PUBLIC_ROUTE', rota['VERDICT'])
        for i in rota['ITEMS']:
            self.assertIn('estado de ACESSO', i['WHY'])


class TestDataVemDeGracaDentroDoId(unittest.TestCase):
    """O padrao veio de fora; ele so entrou depois de ser medido AQUI DENTRO."""

    def test_o_urn_bate_com_a_plataforma_nos_472_posts_ja_pagos(self):
        """A conferencia que autorizou o padrao. Se ela cair, o padrao sai."""
        import gzip
        conferidos = ok = 0
        for nome in ('ES-T8-002-linkedin-posts-a.raw.json.gz',
                     'ES-T8-002-linkedin-posts-b.raw.json.gz'):
            caminho = os.path.join(ROOT, 'data', 'samples', 'raw-paid', nome)
            if not os.path.exists(caminho):
                self.skipTest('RAW ausente: %s' % nome)
            with gzip.open(caminho, 'rt', encoding='utf-8') as f:
                for post in json.load(f):
                    plataforma = (post.get('postedAt') or {}).get('timestamp')
                    derivada = le.data_do_urn(post.get('id'))
                    if plataforma is None or derivada is None:
                        continue
                    conferidos += 1
                    if abs(derivada.timestamp() - plataforma / 1000.0) <= 1.0:
                        ok += 1
        self.assertGreater(conferidos, 400, 'a conferencia precisa ter massa')
        self.assertEqual(conferidos, ok,
                         'o id parou de datar o post — o padrao nao vale mais')

    def test_data_relativa_sozinha_deixa_de_ser_nao_sei(self):
        c = le.campos_de_post({'id': '7462438040280436736', 'content': 'x',
                               'postedAt': {'postedAgoShort': '3mo'}})
        self.assertNotEqual(le.NAO_SEI, c['PUBLICATION_DATE'])
        self.assertEqual('RESOLVED_BY_URN', c['PUBLICATION_DATE_AGREEMENT'])

    def test_discordancia_e_estado_e_nao_desempate_silencioso(self):
        _iso, acordo = le.conferir_data('7462438040280436736',
                                        '2020-01-01T00:00:00Z')
        self.assertEqual('DISAGREE', acordo)

    def test_id_que_nao_e_id_de_post_nao_vira_data_de_1973(self):
        self.assertIsNone(le.data_do_urn('123'))
        self.assertIsNone(le.data_do_urn(None))
        self.assertIsNone(le.data_do_urn('nao-numero'))

    def test_nenhum_codigo_gpl_foi_copiado_a_licenca_e_declarada(self):
        with open(le.__file__, encoding='utf-8') as fh:
            fonte = fh.read()
        self.assertIn('GPL-3.0', fonte, 'a origem do padrao precisa estar declarada')
        self.assertIn('não foi copiado', fonte)


if __name__ == '__main__':
    unittest.main(verbosity=2)
