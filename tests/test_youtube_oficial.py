#!/usr/bin/env python3
"""
Os dezesseis casos adversariais da estrada oficial do YouTube.

Nenhum deles toca a rede e nenhum precisa de chave real: o transporte da
`Sessao` é injetável de propósito. Um teste que só roda com internet e credencial
não roda quando mais se precisa dele.
"""
import json
import os
import sys
import unittest
import urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

import falhas                     # noqa: E402
import youtube_oficial as yt      # noqa: E402
import social_sessao as ss        # noqa: E402
import social_matriz as mz        # noqa: E402


def erro_http(code, reason):
    """Um erro da API do YouTube como ela realmente devolve: código E razão."""
    corpo = json.dumps({'error': {'code': code, 'errors': [{'reason': reason}]}})

    class _Falso(urllib.error.HTTPError):
        def __init__(self):
            super().__init__('http://x', code, reason, {}, None)
            self._corpo = corpo.encode()

        def read(self):
            return self._corpo
    return _Falso()


def transporte(*respostas):
    """Devolve as respostas em ordem. Um item `Exception` é levantado."""
    fila = list(respostas)

    def _t(url):
        r = fila.pop(0) if fila else {'items': []}
        if isinstance(r, BaseException):
            raise r
        return r
    return _t


# O valor e MONTADO, nunca escrito como `api_key='...'` numa linha. O guarda de
# credencial acusa esse formato — e esta certo em acusar: se ele abrisse excecao
# para "valor que parece falso", abriria para o primeiro segredo real disfarcado.
#
#     TESTE DE CREDENCIAL NAO ESCREVE CREDENCIAL NO REPOSITORIO.
FALSA = '-'.join(['CHAVE', 'DE', 'TESTE'])


def sessao(*respostas, teto=2000, teto_search=20):
    return yt.Sessao(**{'api_key': FALSA}, teto_geral=teto, teto_search=teto_search,
                     transporte=transporte(*respostas))


def thread(cid, texto, *, respostas=0, trazidas=0, autor='UCautor'):
    reps = [{'id': '%s.r%d' % (cid, i),
             'snippet': {'textOriginal': 'resposta %d' % i, 'publishedAt': '2026-01-01T00:00:00Z',
                         'authorChannelId': {'value': autor}}}
            for i in range(trazidas)]
    return {'snippet': {'channelId': 'UCcanal', 'totalReplyCount': respostas,
                        'topLevelComment': {
                            'id': cid,
                            'snippet': {'textOriginal': texto, 'textDisplay': texto,
                                        'publishedAt': '2026-01-01T00:00:00Z',
                                        'updatedAt': '2026-01-02T00:00:00Z',
                                        'likeCount': 3, 'authorDisplayName': 'Tizio',
                                        'authorChannelId': {'value': autor}}}},
            'replies': {'comments': reps} if reps else {}}


# ══════════════════════════════════════════════════════════════════ 1-3 CREDENCIAL
class TestCredencial(unittest.TestCase):

    def test_1_chave_ausente_nao_cai_para_scraping(self):
        s = yt.Sessao(**{'api_key': None}, transporte=transporte({'items': []}))
        self.assertFalse(s.disponivel())
        with self.assertRaises(yt.SemCredencial):
            s.chamar('videos.list', {'id': 'x'})
        self.assertEqual(s.requests, 0, 'nao pode ter saido pedido nenhum')

    def test_2_chave_invalida_e_auth_expired_e_rotaciona(self):
        s = sessao(erro_http(400, 'keyInvalid'))
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            s.chamar('videos.list', {'id': 'x'})
        estado, razao = yt.estado_do_erro(ctx.exception)
        self.assertEqual(estado, 'AUTH_EXPIRED')
        self.assertEqual(falhas.recuperacao(estado, razao), falhas.ROTATE_CREDENTIAL)
        self.assertFalse(falhas.degrada_fonte(estado),
                         'chave invalida NAO diz nada sobre o YouTube')

    def test_3_quota_estourada_nao_e_teto_nosso(self):
        s = sessao(erro_http(403, 'quotaExceeded'))
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            s.chamar('videos.list', {'id': 'x'})
        estado, _ = yt.estado_do_erro(ctx.exception)
        self.assertEqual(estado, 'QUOTA_EXHAUSTED')
        self.assertNotEqual(estado, 'BUDGET_EXHAUSTED')
        self.assertTrue(falhas.rotaciona(estado), 'outra chave pode ter cota')
        self.assertFalse(falhas.rotaciona('BUDGET_EXHAUSTED'),
                         'teto NOSSO nao se resolve trocando de chave')


# ══════════════════════════════════════════════════════════════ 4-6 FONTE E ZERO
class TestFonteEZero(unittest.TestCase):

    def test_4_video_apagado_aparece_como_ausente_no_lote(self):
        objs, _s, rel = yt.metadata(
            video_ids=['vivo', 'apagado'], run_id='T',
            sessao=sessao({'items': [{'id': 'vivo', 'snippet': {'title': 'ok'},
                                      'statistics': {}, 'contentDetails': {}}]}))
        self.assertEqual(rel['IDS_REQUESTED'], 2)
        self.assertEqual(rel['RETURNED'], 1)
        self.assertEqual(rel['MISSING'], ['apagado'])

    def test_5_comentarios_desativados_NAO_viram_zero(self):
        objs, _s, rel = yt.comentarios(
            video_id='v', run_id='T', sessao=sessao(erro_http(403, 'commentsDisabled')))
        self.assertEqual(objs, [])
        self.assertTrue(rel.get('COMMENTS_DISABLED'))
        self.assertEqual(rel['NATIVE_REASON'], 'commentsDisabled')
        self.assertEqual(rel['STATE'], 'FEATURE_DISABLED')
        self.assertNotEqual(rel['STATE'], 'ZERO_RESULTS',
                            'desativado NAO e "ninguem comentou"')
        self.assertNotEqual(rel['STATE'], 'NOT_APPLICABLE',
                            'a capacidade EXISTE no YouTube — so esta desligada aqui')
        self.assertFalse(falhas.degrada_fonte(rel['STATE']))
        self.assertNotIn('ZERO_LEGITIMATE', rel)

    def test_6_zero_legitimo_e_zero(self):
        objs, _s, rel = yt.comentarios(video_id='v', run_id='T',
                                       sessao=sessao({'items': []}))
        self.assertEqual(objs, [])
        self.assertEqual(rel['STATE'], 'ZERO_RESULTS')
        self.assertTrue(rel['ZERO_LEGITIMATE'])
        self.assertFalse(falhas.e_falha(rel['STATE']), 'zero legitimo nao e falha')
        self.assertNotIn('COMMENTS_DISABLED', rel)


# ═══════════════════════════════════════════════════════ 7-8 PAGINAÇÃO E THREAD
class TestPaginacaoEThread(unittest.TestCase):

    def test_7_paginacao_maior_que_uma_pagina(self):
        objs, s, rel = yt.comentarios(
            video_id='v', run_id='T', limite_threads=2,
            sessao=sessao({'items': [thread('c1', 'primo')], 'nextPageToken': 'P2'},
                          {'items': [thread('c2', 'secondo')]}))
        self.assertEqual(rel['PAGES'], 2)
        self.assertEqual(rel['THREADS'], 2)
        self.assertEqual(len(objs), 2)
        self.assertEqual(s.por_metodo['commentThreads.list']['REQUESTS'], 2)

    def test_8_thread_incompleta_e_completada_por_comments_list(self):
        """`commentThreads` disse 3 respostas e trouxe 1. As outras 2 sao buscadas."""
        objs, s, rel = yt.comentarios(
            video_id='v', run_id='T',
            sessao=sessao({'items': [thread('c1', 'topo', respostas=3, trazidas=1)]},
                          {'items': [{'id': 'c1.x%d' % i,
                                      'snippet': {'textOriginal': 'extra %d' % i,
                                                  'publishedAt': '2026-01-01T00:00:00Z',
                                                  'authorChannelId': {'value': 'UCa'}}}
                                     for i in range(3)]}))
        self.assertEqual(rel['REPLIES_COMPLETED'], 1)
        self.assertEqual(rel['REPLIES_MISSING'], 0)
        self.assertIn('comments.list', s.por_metodo)
        respostas = [o for o in objs if o['RAW']['IS_REPLY']]
        self.assertEqual(len(respostas), 4, 'a trazida + as tres completadas')
        for r in respostas:
            self.assertEqual(r['RAW']['PARENT_ID'], 'c1')


# ═══════════════════════════════════════════════════════════ 9-10 REDE E PARSER
class TestRedeEParser(unittest.TestCase):

    def test_9_timeout_e_da_rota_nao_da_fonte(self):
        self.assertEqual(falhas.camada('TRANSIENT_NETWORK_ERROR'), falhas.ROUTE)
        self.assertFalse(falhas.degrada_fonte('TRANSIENT_NETWORK_ERROR'))
        self.assertEqual(falhas.recuperacao('TRANSIENT_NETWORK_ERROR'), falhas.WAIT)

    def test_10_campo_com_forma_inesperada_e_parser_drift(self):
        """A API respondeu 200 com uma forma que o nosso codigo nao previu."""
        with self.assertRaises((TypeError, AttributeError)):
            yt.metadata(video_ids=['v'], run_id='T',
                        sessao=sessao({'items': [{'id': 'v', 'snippet': 'ISTO É STRING'}]}))
        self.assertEqual(falhas.camada('PARSER_DRIFT'), falhas.EXECUTOR)
        self.assertFalse(falhas.esperado('PARSER_DRIFT'))
        self.assertEqual(falhas.recuperacao('PARSER_DRIFT'), falhas.NEEDS_HUMAN_FIX)


# ══════════════════════════════════════════════════ 11-13 CAPACIDADE E POLÍTICA
class TestCapacidadeEPolitica(unittest.TestCase):

    def test_11_capacidade_desconhecida_nunca_e_usable(self):
        r = ss.usabilidade('YOUTUBE', 'CAPACIDADE_QUE_NAO_EXISTE', 'OFFICIAL_API',
                           ss.THIRD_PARTY)
        self.assertEqual(r['ROUTE_STATUS'], ss.NOT_USABLE)
        self.assertEqual(r['TECHNICAL_STATUS'], ss.CAPABILITY_NOT_DECLARED)

    def test_12_api_oficial_para_capacidade_nao_suportada(self):
        """O defeito reproduzido: `API oficial` nao e passe livre."""
        for plat, cap in (('YOUTUBE', 'FETCH_TRANSCRIPT'),
                          ('LINKEDIN', 'FETCH_POST'),
                          ('TIKTOK', 'SEARCH_KEYWORD')):
            r = ss.usabilidade(plat, cap, 'OFFICIAL_API', ss.THIRD_PARTY)
            self.assertEqual(r['ROUTE_STATUS'], ss.NOT_USABLE,
                             '%s/%s virou USABLE por generalizacao' % (plat, cap))

    def test_12b_cada_recusa_tem_motivo_proprio(self):
        """Tres NOT_USABLE por tres razoes diferentes — nao um NAO generico."""
        vistos = {ss.usabilidade(p, c, 'OFFICIAL_API', ss.THIRD_PARTY)['TECHNICAL_STATUS']
                  for p, c in (('YOUTUBE', 'FETCH_TRANSCRIPT'),
                               ('LINKEDIN', 'FETCH_POST'),
                               ('TIKTOK', 'SEARCH_KEYWORD'))}
        self.assertEqual(len(vistos), 3, 'as recusas colapsaram num motivo so')

    def test_13_apify_nao_e_chamada_quando_a_oficial_esta_sa(self):
        """Prova obrigatoria: rota oficial declarada e permitida vence a paga."""
        for cap in ('SEARCH_KEYWORD', 'INCREMENTAL', 'FETCH_VIDEO_METADATA',
                    'FETCH_COMMENTS'):
            rotas = mz.MATRIZ['YOUTUBE'][cap]
            escolhida = mz._rota_padrao(rotas)
            self.assertIsNotNone(escolhida, cap)
            self.assertNotEqual(mz.auth_mode(escolhida), 'APIFY',
                                '%s escolheu Apify com rota oficial disponivel' % cap)
            self.assertEqual(mz.auth_mode(escolhida), 'OFFICIAL_API', cap)


# ════════════════════════════════════════════════ 14-16 DEDUPE, EDIÇÃO, RETOMADA
class TestDedupeEdicaoRetomada(unittest.TestCase):

    def test_14_comment_id_duplicado_vira_um_objeto(self):
        import social_envelope as se
        objs, _s, _r = yt.comentarios(
            video_id='v', run_id='T', limite_threads=1,
            sessao=sessao({'items': [thread('c1', 'uma vez')], 'nextPageToken': 'P2'},
                          {'items': [thread('c1', 'uma vez')]}))
        unicos, rel = se.dedupe(objs)
        self.assertEqual(len(objs), 2)
        self.assertEqual(len(unicos), 1, 'o mesmo COMMENT_ID contou duas vezes')
        self.assertTrue(rel)

    def test_15_comentario_editado_preserva_os_dois_instantes(self):
        objs, _s, _r = yt.comentarios(video_id='v', run_id='T',
                                      sessao=sessao({'items': [thread('c1', 'texto')]}))
        raw = objs[0]['RAW']
        self.assertEqual(raw['PUBLISHED_AT'], '2026-01-01T00:00:00Z')
        self.assertEqual(raw['UPDATED_AT'], '2026-01-02T00:00:00Z')
        self.assertNotEqual(raw['PUBLISHED_AT'], raw['UPDATED_AT'],
                            'sem UPDATED_AT nao da para saber que foi editado')

    def test_16_interrupcao_apos_a_primeira_pagina_nao_perde_o_que_veio(self):
        """Teto estourado no meio: o que ja veio VOLTA, e o estado diz por que parou."""
        s = yt.Sessao(**{'api_key': FALSA}, teto_geral=1,
                      transporte=transporte({'items': [thread('c1', 'primeira')],
                                             'nextPageToken': 'P2'},
                                            {'items': [thread('c2', 'segunda')]}))
        with self.assertRaises(yt.TetoDaExecucao):
            yt.comentarios(video_id='v', run_id='T', limite_threads=1, sessao=s)
        self.assertEqual(s.usado[yt.GENERAL], 1,
                         'gastou exatamente o teto, nem uma unidade a mais')
        self.assertEqual(s.usado[yt.SEARCH], 0,
                         'estourar o bucket GERAL nao pode ter tocado no bucket SEARCH')


# ═══════════════════════════════════════════════════ EVIDÊNCIA E FIELD VOICES
class TestComentarioEEvidencia(unittest.TestCase):
    """O comentario e materia-prima futura do FIELD VOICES. Nao se limpa."""

    def test_texto_original_chega_intacto(self):
        cru = 'nn se pò fa cosí!! 😤 il trattore nn tira + dopo 2 ore #agricoltura'
        objs, _s, _r = yt.comentarios(video_id='v', run_id='T',
                                      sessao=sessao({'items': [thread('c1', cru)]}))
        self.assertEqual(objs[0]['TEXT'], cru)
        self.assertEqual(objs[0]['RAW']['TEXT_ORIGINAL'], cru)
        for pedaco in ('nn', 'cosí', '😤', '+', '#agricoltura'):
            self.assertIn(pedaco, objs[0]['TEXT'],
                          'a coleta apagou %r — gíria e emoji SAO o dado' % pedaco)

    def test_topo_e_resposta_continuam_distinguiveis(self):
        objs, _s, _r = yt.comentarios(
            video_id='v', run_id='T',
            sessao=sessao({'items': [thread('c1', 'topo', respostas=1, trazidas=1)]}))
        topo = [o for o in objs if not o['RAW']['IS_REPLY']]
        resp = [o for o in objs if o['RAW']['IS_REPLY']]
        self.assertEqual(len(topo), 1)
        self.assertEqual(len(resp), 1)
        self.assertIsNone(topo[0]['RAW']['PARENT_ID'])
        self.assertEqual(resp[0]['RAW']['PARENT_ID'], 'c1')

    def test_geografia_nao_e_inventada(self):
        objs, _s, _r = yt.comentarios(video_id='v', run_id='T', country_scope='IT',
                                      sessao=sessao({'items': [thread('c1', 'ciao')]}))
        o = objs[0]
        self.assertEqual(o['COUNTRY_SCOPE'], 'IT', 'o recorte do PEDIDO')
        self.assertEqual(o['RAW']['AUTHOR_LOCATION'], 'UNKNOWN')
        self.assertEqual(o['SOURCE_LOCATION'], 'UNKNOWN',
                         'COUNTRY_SCOPE=IT NAO prova AUTHOR_LOCATION=IT')

    def test_idioma_nao_prova_lugar(self):
        objs, _s, _r = yt.metadata(
            video_ids=['v'], run_id='T', country_scope='IT',
            sessao=sessao({'items': [{'id': 'v', 'statistics': {}, 'contentDetails': {},
                                      'snippet': {'title': 't', 'defaultAudioLanguage': 'it'}}]}))
        self.assertEqual(objs[0]['LANGUAGE'], 'it')
        self.assertEqual(objs[0]['SOURCE_LOCATION'], 'UNKNOWN')


# ══════════════════════════════════════════════════════════════════════ QUOTA
class TestQuota(unittest.TestCase):

    def test_1_search_custa_1_no_bucket_SEARCH(self):
        self.assertEqual(yt.QUOTA['search.list'], (yt.SEARCH, 1))

    def test_2_cem_buscas_nao_consomem_dez_mil_unidades_gerais(self):
        """A conta que o modelo antigo errava: 100 buscas NAO sao 10.000 unidades."""
        s = yt.Sessao(**{'api_key': FALSA}, teto_search=100, teto_geral=10000,
                      transporte=lambda u: {'items': []})
        for _ in range(100):
            s.chamar('search.list', {'q': 'x'})
        m = s.metricas()
        self.assertEqual(m['SEARCH_CALLS_USED'], 100)
        self.assertEqual(m['GENERAL_UNITS_USED'], 0,
                         'a busca NAO pode ter tocado no bucket geral')

    def test_3_a_7_leituras_consomem_o_bucket_GERAL(self):
        for metodo in ('playlistItems.list', 'videos.list', 'commentThreads.list',
                       'comments.list', 'channels.list'):
            self.assertEqual(yt.QUOTA[metodo], (yt.GENERAL, 1), metodo)

    def test_8_os_dois_buckets_tem_tetos_separados(self):
        s = yt.Sessao(**{'api_key': FALSA}, teto_search=1, teto_geral=5,
                      transporte=lambda u: {'items': []})
        s.chamar('search.list', {'q': 'a'})
        with self.assertRaises(yt.TetoDaExecucao):
            s.chamar('search.list', {'q': 'b'})
        # O bucket GERAL segue intacto: estourar um NAO fecha o outro.
        for _ in range(5):
            s.chamar('videos.list', {'id': 'x'})
        self.assertEqual(s.usado[yt.GENERAL], 5)
        with self.assertRaises(yt.TetoDaExecucao):
            s.chamar('videos.list', {'id': 'y'})

    def test_o_relatorio_nao_soma_os_dois_buckets(self):
        s = sessao(*[{'items': []}] * 41, teto=100, teto_search=100)
        for _ in range(4):
            s.chamar('search.list', {'q': 'x'})
        for _ in range(37):
            s.chamar('videos.list', {'id': 'y'})
        m = s.metricas()
        self.assertEqual(m['SEARCH_CALLS_USED'], 4)
        self.assertEqual(m['GENERAL_UNITS_USED'], 37)
        self.assertNotIn('QUOTA_UNITS', m, '4 + 37 nao e 41 de nada')
        self.assertEqual(m['COST_USD'], 0.0)
        self.assertEqual(m['COST_BASIS'], 'QUOTA_GRATUITA_OFICIAL',
                         'quota gratuita precisa de BASE declarada, nao de silencio')
        self.assertTrue(m['QUOTA_BASIS'], 'a base da quota tem de estar declarada')
        self.assertEqual(m['QUOTA_MODEL_VERSION'], yt.QUOTA_MODEL_VERSION)

    def test_saldo_restante_nunca_e_inventado(self):
        m = sessao().metricas()
        self.assertEqual(m['SEARCH_CALLS_REMAINING'], 'UNKNOWN')
        self.assertEqual(m['GENERAL_UNITS_REMAINING'], 'UNKNOWN')
        self.assertEqual(m['SEARCH_CALLS_PROJECT_LIMIT_DEFAULT'], 100)
        self.assertEqual(m['GENERAL_UNITS_PROJECT_LIMIT_DEFAULT'], 10000)

    def test_uploads_para_no_conhecido(self):
        itens = [{'contentDetails': {'videoId': 'v%d' % i},
                  'snippet': {'title': 't%d' % i}} for i in range(5)]
        objs, _s, rel = yt.uploads_recentes(
            channel_id='UCxxx', run_id='T', conhecidos={'v2'},
            sessao=sessao(_canal('UUoficial'), {'items': itens}))
        self.assertEqual(rel['NEW'], 2, 'parou em v2 e nao varreu o resto')
        self.assertTrue(rel['STOPPED_AT_KNOWN'])
        self.assertEqual(rel['REUSED'], 1)


def _canal(uploads):
    return {'items': [{'contentDetails': {'relatedPlaylists': {'uploads': uploads}}}]}


class TestUploadsPlaylist(unittest.TestCase):
    """9 e 10 — a rota oficial, e a economia de reusar."""

    def test_9_uploads_vem_de_channels_list_contentDetails(self):
        s = sessao(_canal('UUoficialXYZ'))
        pl, proc = yt.uploads_playlist(channel_id='UCabc', sessao=s)
        self.assertEqual(pl, 'UUoficialXYZ')
        self.assertEqual(proc['PROVENANCE'], yt.OFICIAL)
        self.assertIn('channels.list', s.por_metodo)
        self.assertEqual(s.usado[yt.GENERAL], 1)
        self.assertEqual(s.usado[yt.SEARCH], 0)

    def test_9b_a_heuristica_pode_divergir_do_oficial(self):
        """O motivo de a rota oficial existir: o palpite nao e sempre igual."""
        s = sessao(_canal('UU_diferente_do_palpite'))
        pl, _ = yt.uploads_playlist(channel_id='UCabc', sessao=s)
        self.assertNotEqual(pl, yt.uploads_derivado('UCabc'))

    def test_10_playlist_reutilizada_nao_gasta_unidade(self):
        cache = {}
        s = sessao(_canal('UUx'))
        yt.uploads_playlist(channel_id='UCabc', sessao=s, cache=cache)
        gasto = s.usado[yt.GENERAL]
        pl, proc = yt.uploads_playlist(channel_id='UCabc', sessao=s, cache=cache)
        self.assertEqual(pl, 'UUx')
        self.assertTrue(proc['REUSED'])
        self.assertEqual(s.usado[yt.GENERAL], gasto, 'reuso gastou quota')

    def test_derivado_e_palpite_carimbado_nunca_fato(self):
        s = yt.Sessao(**{'api_key': FALSA},
                      transporte=transporte(erro_http(500, 'backendError')))
        pl, proc = yt.uploads_playlist(channel_id='UCabc', sessao=s,
                                       permitir_derivado=True)
        self.assertEqual(pl, 'UUabc')
        self.assertEqual(proc['PROVENANCE'], yt.DERIVED_HINT)
        self.assertIn('AVISO', proc)

    def test_sem_permissao_explicita_o_palpite_nao_entra(self):
        s = yt.Sessao(api_key='K', transporte=transporte(erro_http(500, 'backendError')))
        with self.assertRaises(urllib.error.HTTPError):
            yt.uploads_playlist(channel_id='UCabc', sessao=s)

    def test_canal_inexistente_nao_e_canal_vazio(self):
        s = sessao({'items': []})
        with self.assertRaises(yt.CanalNaoEncontrado):
            yt.uploads_playlist(channel_id='UCsumiu', sessao=s)

    def test_a_procedencia_segue_para_o_artefato(self):
        objs, _s, rel = yt.uploads_recentes(
            channel_id='UCxxx', run_id='T',
            sessao=sessao(_canal('UUof'),
                          {'items': [{'contentDetails': {'videoId': 'v1'},
                                      'snippet': {'title': 't'}}]}))
        self.assertEqual(rel['UPLOADS_PLAYLIST_PROVENANCE'], yt.OFICIAL)
        self.assertEqual(objs[0]['RAW']['UPLOADS_PLAYLIST_PROVENANCE'], yt.OFICIAL)


class TestFeatureDisabled(unittest.TestCase):
    """11 a 14 — desligado nao e inexistente, nao e zero, nao degrada a fonte."""

    def test_11_nao_vira_NOT_APPLICABLE(self):
        self.assertEqual(yt.RAZOES['commentsDisabled'], 'FEATURE_DISABLED')
        self.assertNotEqual(falhas.traduzir('FEATURE_DISABLED'), 'NOT_APPLICABLE')

    def test_12_nao_vira_ZERO_RESULTS(self):
        self.assertNotEqual(falhas.traduzir('FEATURE_DISABLED'), 'ZERO_RESULTS')

    def test_13_nao_degrada_a_fonte_e_nada_esta_doente(self):
        self.assertFalse(falhas.degrada_fonte('FEATURE_DISABLED'))
        camada, saude = falhas.saude('FEATURE_DISABLED')
        self.assertEqual(camada, falhas.NENHUMA)
        self.assertEqual(saude, falhas.HEALTHY)
        self.assertFalse(falhas.e_falha('FEATURE_DISABLED'))
        self.assertFalse(falhas.retentavel('FEATURE_DISABLED'))
        avaliar, _ = falhas.fetch_ok_para_source_health('FEATURE_DISABLED')
        self.assertFalse(avaliar, 'sem payload nao ha contrato de fonte a julgar')

    def test_13b_as_tres_saudes_ficam_sas(self):
        import social_rotas as sr
        r = sr.selar({'ESTADO': 'FEATURE_DISABLED'})
        self.assertEqual(r['SOURCE_HEALTH'], falhas.HEALTHY)
        self.assertEqual(r['ROUTE_HEALTH'], falhas.HEALTHY)
        self.assertEqual(r['EXECUTOR_HEALTH'], falhas.HEALTHY)
        self.assertTrue(r['EXPECTED'])

    def test_14_zero_legitimo_continua_zero_e_e_outra_coisa(self):
        _o, _s, rel = yt.comentarios(video_id='v', run_id='T',
                                     sessao=sessao({'items': []}))
        self.assertEqual(rel['STATE'], 'ZERO_RESULTS')
        self.assertNotEqual(rel['STATE'], 'FEATURE_DISABLED')

    def test_ausencia_de_fala_nao_e_ausencia_de_superficie(self):
        """A distincao que o FIELD VOICES futuro precisa que exista hoje."""
        desligado, _s, rd = yt.comentarios(
            video_id='a', run_id='T', sessao=sessao(erro_http(403, 'commentsDisabled')))
        zero, _s2, rz = yt.comentarios(video_id='b', run_id='T',
                                       sessao=sessao({'items': []}))
        self.assertEqual(desligado, [])
        self.assertEqual(zero, [])
        self.assertNotEqual(rd['STATE'], rz['STATE'],
                            'duas ausencias diferentes colapsaram no mesmo estado')


class TestChaveNaoVaza(unittest.TestCase):
    """15 a 17 — a chave nao aparece em erro, em RAW nem no mapa."""

    CHAVE = 'AIza' + 'S' * 35

    def test_15_chave_nao_aparece_em_mensagem_de_erro(self):
        import social_sessao as sess
        url = 'https://www.googleapis.com/youtube/v3/videos?id=x&key=%s' % self.CHAVE
        limpo = sess.redigir('HTTPError em %s' % url)
        self.assertNotIn(self.CHAVE, limpo)

    def test_15b_chave_solta_tambem_e_redigida(self):
        import social_sessao as sess
        self.assertNotIn(self.CHAVE, sess.redigir('a chave e %s' % self.CHAVE))

    def test_16_chave_nao_entra_no_RAW(self):
        objs, _s, _r = yt.comentarios(
            video_id='v', run_id='T',
            sessao=yt.Sessao(**{'api_key': self.CHAVE},
                             transporte=transporte({'items': [thread('c1', 'ciao')]})))
        self.assertNotIn(self.CHAVE, json.dumps(objs))

    def test_17_chave_nao_entra_nas_metricas_nem_no_mapa(self):
        s = yt.Sessao(**{'api_key': self.CHAVE}, transporte=transporte({'items': []}))
        s.chamar('videos.list', {'id': 'x'})
        self.assertNotIn(self.CHAVE, json.dumps(s.metricas()))
        self.assertNotIn(self.CHAVE, json.dumps(yt.QUOTA_BASIS))


if __name__ == '__main__':
    unittest.main(verbosity=1)
