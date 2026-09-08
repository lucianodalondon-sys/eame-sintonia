#!/usr/bin/env python3
"""
ANTI-DRIFT — as travas que impedem os defeitos JÁ COMETIDOS de voltarem.

Cada teste aqui existe porque a coisa que ele proíbe aconteceu de verdade nesta
casa. Não são hipóteses: são cicatrizes.
"""
import io
import os
import re
import sys
import unittest
import urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

import falhas                     # noqa: E402
import social_matriz as mz        # noqa: E402
import youtube_oficial as yt      # noqa: E402

FALSA = '-'.join(['CHAVE', 'DE', 'TESTE'])


def _t(*r):
    fila = list(r)

    def f(url):
        x = fila.pop(0) if fila else {'items': []}
        if isinstance(x, BaseException):
            raise x
        return x
    return f


class TestUmDonoDaQuota(unittest.TestCase):
    """A matriz sabia o modelo certo e o executor mantinha outro numero."""

    def test_o_executor_nao_declara_quota_propria(self):
        """`QUOTA` do adaptador tem de ser a matriz LIDA, nao uma segunda tabela."""
        self.assertEqual(yt.QUOTA, mz.QUOTA_METODO['YOUTUBE'])
        self.assertEqual(yt.LIMITE_PADRAO, mz.LIMITE_PADRAO_PROJETO['YOUTUBE'])
        self.assertEqual(yt.QUOTA_MODEL_VERSION, mz.QUOTA_MODEL_VERSION)

    def test_a_chamada_pergunta_ao_dono_na_hora(self):
        """Nao basta o espelho bater no import: a decisao que gasta consulta a matriz."""
        original = dict(mz.QUOTA_METODO['YOUTUBE'])
        try:
            mz.QUOTA_METODO['YOUTUBE']['videos.list'] = ('SEARCH', 7)
            s = yt.Sessao(**{'api_key': FALSA}, teto_search=99, teto_geral=99,
                          transporte=_t({'items': []}))
            s.chamar('videos.list', {'id': 'x'})
            self.assertEqual(s.usado[yt.SEARCH], 7,
                             'o executor ignorou a matriz e usou tabela propria')
        finally:
            mz.QUOTA_METODO['YOUTUBE'] = original

    def test_search_nunca_volta_a_custar_100_unidades_gerais(self):
        bucket, custo = mz.quota_de('YOUTUBE', 'search.list')
        self.assertEqual(bucket, 'SEARCH')
        self.assertEqual(custo, 1)

    def test_metodo_sem_regra_nao_pode_ser_chamado(self):
        with self.assertRaises(KeyError):
            mz.quota_de('YOUTUBE', 'videos.insert')

    def test_nenhuma_fonte_declara_100_unidades_como_custo_atual(self):
        """Varre codigo e docs. Narrativa historica e permitida; declaracao nao."""
        alvos = []
        for base in ('scripts', 'docs'):
            for raiz, _d, arqs in os.walk(os.path.join(ROOT, base)):
                if '__pycache__' in raiz:
                    continue
                for a in arqs:
                    if a.endswith(('.py', '.md')):
                        alvos.append(os.path.join(raiz, a))
        # A frase proibida e a que AFIRMA no presente. "a versao anterior dizia X"
        # continua valendo — apagar a memoria do erro nao e consertar o erro.
        proibido = re.compile(
            r'(?i)search\.list[^.\n]{0,40}(custa|cost[a]?|=)\s*100\s*(unidade|unit)')
        ruins = []
        for f in alvos:
            txt = io.open(f, encoding='utf-8', errors='replace').read()
            for m in proibido.finditer(txt):
                trecho = txt[max(0, m.start() - 120):m.start()]
                # A marca do texto HISTORICO e o passado: "declarava", "mantinha",
                # "a versao anterior". Um texto que volte a DECLARAR o modelo velho
                # estaria no presente, e nao casa com nenhum destes.
                if any(p in trecho.lower() for p in
                       ('versão anterior', 'versao anterior', 'estava desatualizado',
                        'a primeira versão', 'a primeira versao', 'declarava',
                        'mantinha', 'já dizia', 'ja dizia', 'proibid', 'e dizia')):
                    continue
                ruins.append((os.path.relpath(f, ROOT), m.group(0)[:60]))
        self.assertEqual(ruins, [], 'modelo antigo de quota declarado como atual: %s'
                         % ruins)


class TestUCUUNuncaViraOficial(unittest.TestCase):
    """FALHA DA ROTA OFICIAL NAO TRANSFORMA HEURISTICA EM FATO."""

    def _sessao_que_falha(self, exc):
        return yt.Sessao(**{'api_key': FALSA}, transporte=_t(exc))

    def test_1_sucesso_e_OFICIAL(self):
        s = yt.Sessao(**{'api_key': FALSA}, transporte=_t(
            {'items': [{'contentDetails': {'relatedPlaylists': {'uploads': 'UUof'}}}]}))
        pl, proc = yt.uploads_playlist(channel_id='UCabc', sessao=s)
        self.assertEqual(pl, 'UUof')
        self.assertEqual(proc['PROVENANCE'], yt.OFICIAL)

    def test_2_canal_inexistente_nao_vira_palpite(self):
        s = yt.Sessao(**{'api_key': FALSA}, transporte=_t({'items': []}))
        with self.assertRaises(yt.CanalNaoEncontrado):
            yt.uploads_playlist(channel_id='UCsumiu', sessao=s)

    def test_3_timeout_nao_vira_palpite(self):
        with self.assertRaises(urllib.error.URLError):
            yt.uploads_playlist(channel_id='UCabc',
                                sessao=self._sessao_que_falha(
                                    urllib.error.URLError('timeout')))

    def test_4_parser_drift_nao_vira_palpite(self):
        s = yt.Sessao(**{'api_key': FALSA},
                      transporte=_t({'items': [{'contentDetails': 'ISTO E STRING'}]}))
        with self.assertRaises((AttributeError, TypeError)):
            yt.uploads_playlist(channel_id='UCabc', sessao=s)

    def test_5_quota_estourada_nao_vira_palpite(self):
        s = yt.Sessao(**{'api_key': FALSA}, teto_geral=0, transporte=_t({'items': []}))
        with self.assertRaises(yt.TetoDaExecucao):
            yt.uploads_playlist(channel_id='UCabc', sessao=s)

    def test_6_credencial_ausente_nao_vira_palpite(self):
        s = yt.Sessao(**{'api_key': None}, transporte=_t({'items': []}))
        with self.assertRaises(yt.SemCredencial):
            yt.uploads_playlist(channel_id='UCabc', sessao=s)

    def test_7_hint_explicito_continua_marcado_como_hint(self):
        pl, proc = yt.uploads_hint(
            channel_id='UCabc',
            porque='levantamento exploratorio descartavel que nao entra no acervo')
        self.assertEqual(pl, 'UUabc')
        self.assertEqual(proc['PROVENANCE'], yt.DERIVED_HINT)
        self.assertIn('WHY_DERIVED_HINT_USED', proc)
        self.assertNotEqual(proc['PROVENANCE'], yt.OFICIAL)

    def test_7b_api_falhou_nao_e_justificativa(self):
        for desculpa in ('a API falhou', 'timeout', 'channels.list falhou',
                         'deu erro na api oficial e eu precisava do id'):
            with self.assertRaises(ValueError, msg=desculpa):
                yt.uploads_hint(channel_id='UCabc', porque=desculpa)

    def test_8_oficial_vence_o_derivado_quando_divergem(self):
        s = yt.Sessao(**{'api_key': FALSA}, transporte=_t(
            {'items': [{'contentDetails':
                        {'relatedPlaylists': {'uploads': 'UU_DIFERENTE'}}}]}))
        pl, _ = yt.uploads_playlist(channel_id='UCabc', sessao=s)
        self.assertNotEqual(pl, yt.uploads_derivado('UCabc'))
        self.assertEqual(pl, 'UU_DIFERENTE')

    def test_nao_existe_caminho_automatico_para_o_palpite(self):
        import inspect
        self.assertNotIn('permitir_derivado',
                         inspect.signature(yt.uploads_playlist).parameters)
        self.assertNotIn('permitir_derivado',
                         inspect.signature(yt.uploads_recentes).parameters)

    def test_palpite_guardado_em_disco_nao_vira_fato(self):
        e = yt.checkpoint_atualizar({}, channel_id='UCx', playlist_id='UUx',
                                    provenance=yt.DERIVED_HINT)
        self.assertEqual(yt.cache_de_playlists(e), {},
                         'palpite entrou no cache so por ter dormido no disco')


class TestCheckpointPersistente(unittest.TestCase):
    """CACHE EM RAM NAO E CHECKPOINT PERSISTENTE."""

    def test_identidade_obedece_a_lei_canonica(self):
        import coleta_checkpoint as cc
        ok, ruins = cc.identidade_valida(yt.CAMPOS_DA_IDENTIDADE)
        self.assertTrue(ok, 'identidade com campo proibido: %s' % ruins)
        for proibido in ('TOKEN', 'RUN_ID', 'DATASET_ID', 'CAPTURED_AT'):
            self.assertNotIn(proibido, yt.CAMPOS_DA_IDENTIDADE)

    def test_identidade_e_estavel_entre_execucoes(self):
        self.assertEqual(yt._identidade('UCabc'), yt._identidade('UCabc'))
        self.assertNotEqual(yt._identidade('UCabc'), yt._identidade('UCdef'))

    def test_17_primeira_run_coleta(self):
        itens = [{'contentDetails': {'videoId': 'v%d' % i},
                  'snippet': {'title': 't%d' % i}} for i in range(3)]
        s = yt.Sessao(**{'api_key': FALSA}, transporte=_t(
            {'items': [{'contentDetails': {'relatedPlaylists': {'uploads': 'UUx'}}}]},
            {'items': itens}))
        objs, s, r = yt.uploads_recentes(channel_id='UCx', run_id='R1', sessao=s)
        self.assertEqual(r['NEW'], 3)
        self.assertFalse(r['STOPPED_AT_KNOWN'])
        self.assertEqual(s.por_metodo['channels.list']['REQUESTS'], 1)

    def test_18_segunda_run_sem_novidade_para_cedo(self):
        estado = yt.checkpoint_atualizar({}, channel_id='UCx', playlist_id='UUx',
                                         provenance=yt.OFICIAL,
                                         novos_ids=['v0', 'v1', 'v2'])
        cache = yt.cache_de_playlists(estado)
        itens = [{'contentDetails': {'videoId': 'v%d' % i},
                  'snippet': {'title': 't'}} for i in range(3)]
        s = yt.Sessao(**{'api_key': FALSA}, transporte=_t({'items': itens}))
        conhecidos = yt.checkpoint_do_canal(estado, 'UCx')['VIDEOS_CONHECIDOS']
        objs, s, r = yt.uploads_recentes(channel_id='UCx', run_id='R2',
                                         conhecidos=conhecidos, sessao=s, cache=cache)
        self.assertEqual(r['NEW'], 0)
        self.assertTrue(r['STOPPED_AT_KNOWN'])
        self.assertEqual(r['UPLOADS_EXAMINED'], 1, 'examinou alem do primeiro conhecido')
        self.assertNotIn('channels.list', s.por_metodo,
                         'repetiu channels.list com a playlist ja no checkpoint')

    def test_19_uma_novidade_traz_so_a_novidade(self):
        estado = yt.checkpoint_atualizar({}, channel_id='UCx', playlist_id='UUx',
                                         provenance=yt.OFICIAL,
                                         novos_ids=['v1', 'v0'])
        cache = yt.cache_de_playlists(estado)
        itens = [{'contentDetails': {'videoId': v}, 'snippet': {'title': 't'}}
                 for v in ('v2', 'v1', 'v0')]
        s = yt.Sessao(**{'api_key': FALSA}, transporte=_t({'items': itens}))
        objs, s, r = yt.uploads_recentes(
            channel_id='UCx', run_id='R3',
            conhecidos=yt.checkpoint_do_canal(estado, 'UCx')['VIDEOS_CONHECIDOS'],
            sessao=s, cache=cache)
        self.assertEqual(r['NEW'], 1)
        self.assertEqual(objs[0]['NATIVE_ID'], 'v2')

    def test_20_retomada_apos_pagina_interrompida_nao_recoleta_tudo(self):
        """Run 1 morre depois da 1a pagina; run 2 comeca do que ficou conhecido."""
        p1 = [{'contentDetails': {'videoId': 'v%d' % i}, 'snippet': {'title': 't'}}
              for i in (5, 4)]
        s1 = yt.Sessao(**{'api_key': FALSA}, teto_geral=2, transporte=_t(
            {'items': [{'contentDetails': {'relatedPlaylists': {'uploads': 'UUx'}}}]},
            {'items': p1, 'nextPageToken': 'P2'},
            {'items': [{'contentDetails': {'videoId': 'v3'}, 'snippet': {'title': 't'}}]}))
        estado = {}
        try:
            objs, s1, r = yt.uploads_recentes(channel_id='UCx', run_id='R1',
                                              limit=50, sessao=s1)
        except yt.TetoDaExecucao:
            objs, r = [], None
        # O que chegou ANTES da morte foi persistido pelo chamador.
        estado = yt.checkpoint_atualizar(estado, channel_id='UCx', playlist_id='UUx',
                                         provenance=yt.OFICIAL,
                                         novos_ids=['v5', 'v4'])
        cache = yt.cache_de_playlists(estado)
        s2 = yt.Sessao(**{'api_key': FALSA}, transporte=_t(
            {'items': [{'contentDetails': {'videoId': v}, 'snippet': {'title': 't'}}
                       for v in ('v5', 'v4', 'v3')]}))
        objs2, s2, r2 = yt.uploads_recentes(
            channel_id='UCx', run_id='R2',
            conhecidos=yt.checkpoint_do_canal(estado, 'UCx')['VIDEOS_CONHECIDOS'],
            sessao=s2, cache=cache)
        self.assertEqual(r2['NEW'], 0, 'recoletou o que ja tinha vindo')
        self.assertTrue(r2['STOPPED_AT_KNOWN'])
        self.assertNotIn('channels.list', s2.por_metodo)


class TestCacheNaoSeDescreveComoPersistente(unittest.TestCase):
    def test_o_modulo_diz_a_diferenca(self):
        txt = io.open(os.path.join(ROOT, 'scripts', 'youtube_oficial.py'),
                      encoding='utf-8').read()
        self.assertIn('CACHE EM RAM NÃO É CHECKPOINT PERSISTENTE', txt)


class TestCommentsDisabledNuncaVoltaAZero(unittest.TestCase):
    def test_o_mapa_de_razoes_nao_regride(self):
        self.assertEqual(yt.RAZOES['commentsDisabled'], 'FEATURE_DISABLED')

    def test_os_tres_estados_continuam_distintos(self):
        tres = {falhas.traduzir('FEATURE_DISABLED'),
                falhas.traduzir('ZERO_RESULTS'),
                falhas.traduzir('NOT_APPLICABLE')}
        self.assertEqual(len(tres), 3)


if __name__ == '__main__':
    unittest.main(verbosity=1)
