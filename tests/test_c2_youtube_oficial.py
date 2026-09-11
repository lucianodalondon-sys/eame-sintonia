#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AS DEZASSEIS PROVAS DA C2 — o YouTube pela rota oficial, e o que nao pode voltar.

Nenhuma delas precisa de rede nem da chave real: `youtube_oficial.Sessao` aceita
transporte injetado, e e por isso que um comentario desativado e uma quota
estourada podem ser exercidos num portatil sem internet.

    UM TESTE QUE SO CORRE QUANDO A INTERNET ESTA BOA NAO CORRE QUANDO MAIS
    SE PRECISA DELE.
"""
import io
import json
import os
import shutil
import socket
import sys
import tempfile
import unittest
import urllib.error

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401
import scrap_capacidades as cap    # noqa: E402
import scrap_executor as scrap     # noqa: E402
import scrap_fornecedores as forn  # noqa: E402
import scrap_registo as reg        # noqa: E402
import social_envelope as env      # noqa: E402
import social_rotas as sr          # noqa: E402
import youtube_oficial as yt       # noqa: E402

QUATRO = ('youtube.search', 'youtube.channel.discovery',
          'youtube.video.metadata', 'youtube.comments')

CHAVE_FALSA = 'chave-de-teste-que-nunca-sai-daqui'


def _fonte(rel):
    with io.open(os.path.join(RAIZ, rel), encoding='utf-8') as f:
        return f.read()


class _ErroHttp(urllib.error.HTTPError):
    """Um HTTPError DE VERDADE, com o corpo que a API do YouTube devolve.

    Nao e uma imitacao de proposito: o caminho que este teste exerce depende de
    `except urllib.error.HTTPError`, e um duble que nao herda dele provaria
    outro caminho — o generico, que e exatamente o que nao queremos.
    """

    def __init__(self, code, reason):
        corpo = json.dumps({'error': {'errors': [{'reason': reason}]}}).encode()
        super().__init__('https://www.googleapis.com/youtube/v3/x', code,
                         'erro de teste', {}, io.BytesIO(corpo))


def _transporte(resposta=None, erro=None):
    def dentro(url):
        assert 'key=' in url, 'a chamada tem de levar a credencial'
        if erro is not None:
            raise erro
        return resposta or {'items': []}
    return dentro


def _com_chave(fn):
    """Corre com uma chave falsa no ambiente e devolve-o como estava."""
    def dentro(*a, **k):
        antes = os.environ.get(yt.ENV_CHAVE)
        os.environ[yt.ENV_CHAVE] = CHAVE_FALSA
        try:
            return fn(*a, **k)
        finally:
            if antes is None:
                os.environ.pop(yt.ENV_CHAVE, None)
            else:
                os.environ[yt.ENV_CHAVE] = antes
    dentro.__name__ = fn.__name__
    return dentro


# ══════════════════════════════════════════════════════════════════════════
class T1SegredoNuncaNoLog(unittest.TestCase):
    """O valor da chave nao sai — nem inteiro, nem em pedacos, nem em hash."""

    FICHEIROS = ('coleta/adaptador_youtube.py', 'coleta/scrap_executor.py',
                 'coleta/social_scrap.py', 'coleta/youtube_oficial.py',
                 'coleta/social_rotas.py')

    def test_ninguem_imprime_a_chave(self):
        for rel in self.FICHEIROS:
            corpo = _fonte(rel).split('"""', 2)[-1]
            for proibido in ('print(chave', 'print(api_key', 'print(self.api_key',
                             'print(os.environ[', "print(os.environ.get('YOUTUBE"):
                self.assertNotIn(proibido, corpo, '%s: %s' % (rel, proibido))

    def test_ninguem_mede_nem_resume_a_chave(self):
        # Um comprimento com prefixo e meio segredo, e meio segredo num log e um
        # segredo num log. Hash tambem nao: hash de chave curta quebra-se.
        for rel in self.FICHEIROS:
            corpo = _fonte(rel).split('"""', 2)[-1]
            for proibido in ('len(chave', 'len(api_key', 'len(self.api_key',
                             'sha256(chave', 'md5(chave', 'chave()[:', 'api_key[:'):
                self.assertNotIn(proibido, corpo, '%s: %s' % (rel, proibido))

    def test_a_sonda_devolve_booleano_e_nunca_o_valor(self):
        import adaptador_youtube as ay
        antes = os.environ.get(yt.ENV_CHAVE)
        os.environ[yt.ENV_CHAVE] = CHAVE_FALSA
        try:
            ok, estado = ay.pronto_para_api()
        finally:
            if antes is None:
                os.environ.pop(yt.ENV_CHAVE, None)
            else:
                os.environ[yt.ENV_CHAVE] = antes
        self.assertIs(ok, True)
        self.assertEqual(estado, 'CREDENTIAL_MISSING')
        self.assertNotIn(CHAVE_FALSA, repr((ok, estado)))

    def test_o_redator_apaga_a_forma_da_chave_do_google(self):
        import social_sessao as ss
        # A forma `AIza…` e a do Google. Montada, nunca escrita: o varredor de
        # segredos desta casa apanhou um teste meu na C1 por escrever uma por
        # extenso, e tinha razao.
        falsa = 'AIza' + 'Sy' + 'A' * 33
        self.assertNotIn(falsa, ss.redigir('https://x/y?key=%s' % falsa))


class T2SegredoChegaAoModulo(unittest.TestCase):
    """A chave do ambiente chega a quem a usa, e o nome e um so."""

    def test_o_nome_canonico_e_unico(self):
        self.assertEqual(yt.ENV_CHAVE, 'YOUTUBE_DATA_API_KEY')

    def test_o_workflow_injeta_o_mesmo_nome_que_o_codigo_le(self):
        wf = _fonte('.github/workflows/scrap-social.yml')
        self.assertIn('%s: ${{ secrets.%s }}' % (yt.ENV_CHAVE, yt.ENV_CHAVE), wf,
                      'o nome no workflow divergiu do nome que o codigo le')

    def test_a_fase_desta_missao_esta_no_workflow(self):
        self.assertIn('youtube-oficial', _fonte('.github/workflows/scrap-social.yml'))

    @_com_chave
    def test_a_sessao_ve_a_chave_do_ambiente(self):
        s = yt.Sessao(transporte=_transporte())
        self.assertTrue(s.disponivel())


class _Base(unittest.TestCase):
    """Base com transporte injetado, para as provas que atravessam a cadeia.

    A chave falsa entra no ambiente porque o `CHECK` a exige ANTES de deixar o
    `COLLECT` correr — e isso e o comportamento certo, nao um estorvo. O valor
    nunca chega a rede: o transporte injetado nunca abre socket.

    E O BRUTO VAI PARA UMA PASTA DESCARTAVEL, POR UM MOTIVO MEDIDO
    ---------------------------------------------------------------
    `social_envelope.guardar_raw` grava o corpo da resposta ANTES de normalizar,
    e faz muito bem: se o normalizador quebrar, a coleta nao precisa ser
    refeita. Mas num TESTE o corpo e inventado — `abc12345678`, `aaaaaaaaaaa` —
    e ele caia em `data/samples/SOCIAL-IT/raw-free/YOUTUBE/`, ao lado do bruto
    de coletas verdadeiras.

    Seis desses ficheiros chegaram a entrar num commit desta missao antes de
    alguem reparar.

        BRUTO DE TESTE AO LADO DE BRUTO DE COLETA E PIOR QUE LIXO: e uma prova
        de uma coleta que nunca aconteceu, com o nome certo e a pasta certa.

    Cada teste desta base escreve numa pasta temporaria que morre com ele.
    """

    def setUp(self):
        self._antes = os.environ.get(yt.ENV_CHAVE)
        os.environ[yt.ENV_CHAVE] = CHAVE_FALSA
        self._tmp = tempfile.mkdtemp(prefix='c2-raw-')
        self._raw_antes = env.RAW_DIR
        env.RAW_DIR = self._tmp

    def tearDown(self):
        env.RAW_DIR = self._raw_antes
        shutil.rmtree(self._tmp, ignore_errors=True)
        if self._antes is None:
            os.environ.pop(yt.ENV_CHAVE, None)
        else:
            os.environ[yt.ENV_CHAVE] = self._antes

    def _collect(self, capacidade, *, resposta=None, erro=None, **kw):
        sessao = yt.Sessao(api_key=CHAVE_FALSA,
                           transporte=_transporte(resposta, erro))
        return scrap.COLLECT(platform='YOUTUBE', capability=capacidade,
                             run_id='T-C2', country_scope='IT',
                             sessao=sessao, **kw)


class T3a6PelaApiOficial(_Base):
    """As quatro pedem e usam a API oficial, e o trace di-lo."""

    PEDIDOS = {
        'youtube.search': dict(termo='t', limit=1),
        'youtube.channel.discovery': dict(channel_id='UC' + 'x' * 22, limit=1),
        'youtube.video.metadata': dict(video_ids=['abc12345678']),
        'youtube.comments': dict(video_id='abc12345678', limite_threads=1),
    }

    def test_as_quatro_declaram_a_api_oficial_como_fornecedor(self):
        for c in QUATRO:
            with self.subTest(c):
                _o, trace = self._collect(c, **self.PEDIDOS[c])
                t = scrap.TRACE(trace)
                self.assertEqual(t['PROVIDER_REQUESTED'], forn.API_OFICIAL, c)
                self.assertEqual(trace.get('ROUTE_CLASS'), 'OFFICIAL_API_FREE', c)
                self.assertTrue(str(trace.get('ROUTE')).startswith('youtube-data-api-v3:'), c)

    def test_a_rota_escolhida_e_o_metodo_certo_de_cada_uma(self):
        esperado = {'youtube.search': 'search.list',
                    'youtube.channel.discovery': 'playlistItems.list',
                    'youtube.video.metadata': 'videos.list',
                    'youtube.comments': 'commentThreads.list'}
        for c, metodo in esperado.items():
            with self.subTest(c):
                _o, trace = self._collect(c, **self.PEDIDOS[c])
                self.assertTrue(str(trace['ROUTE']).endswith(metodo),
                                '%s saiu por %s' % (c, trace['ROUTE']))


class T7SemApify(_Base):
    """Nenhuma das quatro cai para rota paga. A recusa e o resultado."""

    def test_nenhuma_usa_fornecedor_pago(self):
        for c, kw in T3a6PelaApiOficial.PEDIDOS.items():
            with self.subTest(c):
                _o, trace = self._collect(c, **kw)
                self.assertFalse(trace['PAID_PROVIDER_USED'], c)
                self.assertNotEqual(trace.get('PROVIDER_USED'), forn.APIFY, c)

    def test_a_matriz_nao_poe_apify_como_padrao_em_nenhuma_das_quatro(self):
        import social_matriz as mz
        for grossa in ('SEARCH_KEYWORD', 'INCREMENTAL', 'FETCH_VIDEO_METADATA',
                       'FETCH_COMMENTS'):
            d = mz._rota_padrao(mz.MATRIZ['YOUTUBE'][grossa])
            self.assertEqual(d['CLASSE'], 'OFFICIAL_API_FREE', grossa)

    def test_a_rota_paga_continua_a_precisar_de_motivo_declarado(self):
        # A trava do gasto nao foi afrouxada por esta missao.
        objs, r = sr.executar(platform='YOUTUBE', capability='FETCH_TRANSCRIPT',
                              run_id='T-C2', country_scope='IT')
        self.assertEqual(objs, [])
        self.assertIn(r['ESTADO'], ('PAID_ROUTE_REFUSED', 'BUDGET_EXHAUSTED'))


class T8ErroNaoEZero(_Base):
    """Erro de API nao vira coleta vazia. Sao factos diferentes."""

    def test_erro_de_servidor_nao_vira_zero_results(self):
        _o, trace = self._collect('youtube.search', termo='t', limit=1,
                                  erro=_ErroHttp(500, 'backendError'))
        self.assertNotEqual(trace['RESULT'], 'ZERO_RESULTS')
        self.assertEqual(trace['RESULT'], 'SOURCE_UNAVAILABLE')

    def test_chave_invalida_tem_estado_proprio(self):
        _o, trace = self._collect('youtube.search', termo='t', limit=1,
                                  erro=_ErroHttp(400, 'keyInvalid'))
        self.assertEqual(trace['RESULT'], 'AUTH_EXPIRED')
        self.assertNotEqual(trace['RESULT'], 'CREDENTIAL_MISSING')

    def test_credencial_ausente_nao_e_erro_desconhecido(self):
        # Medido na C1 e corrigido aqui: o estado dizia UNKNOWN_ERROR enquanto a
        # mensagem dizia, por extenso, «Isto e CREDENTIAL_MISSING».
        antes = os.environ.pop(yt.ENV_CHAVE, None)
        try:
            objs, r = sr.executar(platform='YOUTUBE', capability='SEARCH_KEYWORD',
                                  run_id='T-C2', country_scope='IT', termo='t', limit=1)
        finally:
            if antes is not None:
                os.environ[yt.ENV_CHAVE] = antes
        self.assertEqual(objs, [])
        self.assertEqual(r['ESTADO'], 'CREDENTIAL_MISSING')

    def test_video_apagado_nao_e_zero(self):
        _o, trace = self._collect('youtube.comments', video_id='x' * 11,
                                  limite_threads=1, erro=_ErroHttp(404, 'videoNotFound'))
        self.assertEqual(trace['RESULT'], 'SOURCE_GONE')


class T9QuotaNaoCaiParaPago(_Base):
    """Quota acabada e teto nosso sao coisas diferentes, e nenhuma compra nada."""

    def test_quota_deles_tem_estado_proprio(self):
        _o, trace = self._collect('youtube.search', termo='t', limit=1,
                                  erro=_ErroHttp(403, 'quotaExceeded'))
        self.assertEqual(trace['RESULT'], 'QUOTA_EXHAUSTED')
        self.assertFalse(trace['PAID_PROVIDER_USED'])
        self.assertIsNone(trace['PROVIDER_USED'], 'ninguem entregou, e o trace diz')

    def test_o_teto_nosso_nao_se_confunde_com_a_quota_deles(self):
        sessao = yt.Sessao(api_key=CHAVE_FALSA, teto_search=0,
                           transporte=_transporte())
        _o, trace = scrap.COLLECT(platform='YOUTUBE', capability='youtube.search',
                                  run_id='T-C2', country_scope='IT',
                                  sessao=sessao, termo='t', limit=1)
        self.assertEqual(trace['RESULT'], 'BUDGET_EXHAUSTED')
        self.assertNotEqual(trace['RESULT'], 'QUOTA_EXHAUSTED')

    def test_quota_estourada_nao_chama_apify(self):
        _o, trace = self._collect('youtube.comments', video_id='x' * 11,
                                  limite_threads=1,
                                  erro=_ErroHttp(403, 'quotaExceeded'))
        self.assertIsNone(trace['WHY_FALLBACK'])
        self.assertFalse(trace['PAID_PROVIDER_USED'])


class T10ComentarioDesativado(_Base):
    """Comentario desligado e um fato sobre o video, nao ausencia de coleta."""

    def test_desativado_tem_estado_proprio(self):
        _o, trace = self._collect('youtube.comments', video_id='x' * 11,
                                  limite_threads=1,
                                  erro=_ErroHttp(403, 'commentsDisabled'))
        self.assertEqual(trace['RESULT'], 'FEATURE_DISABLED')

    def test_desativado_nao_e_zero_results(self):
        _o, desligado = self._collect('youtube.comments', video_id='x' * 11,
                                      limite_threads=1,
                                      erro=_ErroHttp(403, 'commentsDisabled'))
        _o2, vazio = self._collect('youtube.comments', video_id='y' * 11,
                                   limite_threads=1,
                                   resposta={'items': []})
        self.assertNotEqual(desligado['RESULT'], vazio['RESULT'])
        self.assertEqual(vazio['RESULT'], 'ZERO_RESULTS')

    def test_a_traducao_da_razao_nativa_e_declarada(self):
        self.assertEqual(yt.RAZOES['commentsDisabled'], 'FEATURE_DISABLED')


class T11BatchingDeMetadata(_Base):
    """N identificadores numa chamada. Uma unidade, nao N."""

    def test_uma_chamada_para_varios_ids(self):
        s = yt.Sessao(api_key=CHAVE_FALSA, transporte=_transporte({'items': []}))
        yt.metadata(video_ids=['a' * 11, 'b' * 11, 'c' * 11], run_id='T-C2', sessao=s)
        self.assertEqual(s.requests, 1, 'tres ids deviam custar UMA chamada')
        self.assertEqual(s.usado[yt.GENERAL], 1)

    def test_o_custo_nao_cresce_com_o_numero_de_ids(self):
        um = yt.Sessao(api_key=CHAVE_FALSA, transporte=_transporte({'items': []}))
        yt.metadata(video_ids=['a' * 11], run_id='T-C2', sessao=um)
        dez = yt.Sessao(api_key=CHAVE_FALSA, transporte=_transporte({'items': []}))
        yt.metadata(video_ids=['%011d' % i for i in range(10)], run_id='T-C2', sessao=dez)
        self.assertEqual(um.usado[yt.GENERAL], dez.usado[yt.GENERAL])


class T12BuscaNaoEIncremental(_Base):
    """Descobrir e vigiar sao capacidades diferentes, e ate a quota o sabe."""

    def test_sao_capacidades_declaradas_separadas(self):
        self.assertNotEqual(cap.da_matriz('youtube.search'),
                            cap.da_matriz('youtube.channel.discovery'))

    def test_caem_em_baldes_de_quota_diferentes(self):
        self.assertEqual(yt.QUOTA['search.list'][0], yt.SEARCH)
        self.assertEqual(yt.QUOTA['playlistItems.list'][0], yt.GENERAL)

    def test_os_baldes_nao_se_somam(self):
        s = yt.Sessao(api_key=CHAVE_FALSA, transporte=_transporte({'items': []}))
        yt.buscar(termo='t', run_id='T-C2', limit=1, sessao=s)
        self.assertEqual(s.usado[yt.SEARCH], 1)
        self.assertEqual(s.usado[yt.GENERAL], 0, 'a busca comeu o balde errado')


class T13RoteadorContinuaCego(unittest.TestCase):
    """A C1 tirou o nome das plataformas do roteador. A C2 nao o devolve."""

    def test_o_roteador_nao_nomeia_plataformas(self):
        corpo = _fonte('coleta/social_rotas.py').split('"""', 2)[-1]
        corpo = '\n'.join(l for l in corpo.split('\n')
                          if not l.strip().startswith('#'))
        for plat in ('INSTAGRAM', 'LINKEDIN', 'FACEBOOK', 'MASTODON', 'BLUESKY'):
            self.assertNotIn("'%s'" % plat, corpo, plat)

    def test_o_roteador_nao_importa_o_dono_da_api(self):
        corpo = _fonte('coleta/social_rotas.py').split('"""', 2)[-1]
        self.assertNotIn('youtube_oficial', corpo,
                         'o roteador passou a conhecer o motor de uma plataforma')

    def test_a_tabela_do_roteador_continua_vazia_em_producao(self):
        self.assertEqual(sr.ADAPTADORES, {})


class T14SemSegundoExecutor(unittest.TestCase):
    """Nenhum segundo roteador, executor ou orquestrador nasceu nesta missao."""

    def test_nao_ha_ficheiro_paralelo_de_youtube(self):
        for proibido in ('coleta/youtube_scrap_v2.py', 'coleta/youtube_zero_apify.py',
                         'coleta/scrap_orquestrador.py', 'coleta/scrap_router2.py'):
            self.assertFalse(os.path.exists(os.path.join(RAIZ, proibido)), proibido)

    def test_so_um_executor_declara_os_seis_verbos(self):
        donos = []
        for gaveta in _gavetas.GAVETAS:
            base = os.path.join(RAIZ, gaveta)
            if not os.path.isdir(base):
                continue
            for pasta, _d, ficheiros in os.walk(base):
                for f in ficheiros:
                    if not f.endswith('.py'):
                        continue
                    rel = os.path.relpath(os.path.join(pasta, f), RAIZ)
                    fonte = _fonte(rel)
                    if 'def COLLECT(' in fonte and 'def CAPABILITIES(' in fonte:
                        donos.append(rel)
        self.assertEqual(donos, ['coleta/scrap_executor.py'], donos)

    def test_o_executor_continua_a_nao_importar_o_orquestrador(self):
        corpo = _fonte('coleta/scrap_executor.py').split('"""', 2)[-1]
        self.assertNotIn('import orquestrador', corpo)

    def test_a_fase_nova_nao_fala_com_a_api_direto(self):
        fonte = _fonte('coleta/social_scrap.py')
        corpo = fonte[fonte.index('def youtube_oficial_prova'):]
        corpo = corpo[:corpo.index('\ndef main(')]
        for atalho in ('yt.buscar(', 'yt.uploads_recentes(', 'yt.metadata(',
                       'yt.comentarios('):
            self.assertNotIn(atalho, corpo,
                             'a fase saltou o executor e foi direto a API')


class T15HistoriaPreservada(unittest.TestCase):
    """Actor aposentado sai da execucao. Nao some da historia."""

    HISTORICOS = ('data/samples/RUN-MANIFEST.json',
                  'data/samples/SENSOR-PILOT/RUNS-A.json',
                  'data/samples/SENSOR-PILOT/RUNS-E.json')

    def test_os_artefatos_historicos_continuam_no_disco(self):
        for rel in self.HISTORICOS:
            self.assertTrue(os.path.exists(os.path.join(RAIZ, rel)), rel)

    def test_o_gasto_medido_continua_legivel(self):
        achou = False
        for rel in self.HISTORICOS:
            texto = _fonte(rel)
            if 'streamers~youtube-comments-scraper' in texto:
                achou = True
        self.assertTrue(achou, 'a historia do actor mais caro desapareceu')

    def test_o_censo_do_benchmark_continua_citavel(self):
        self.assertTrue(os.path.exists(os.path.join(
            RAIZ, 'docs/sintonia-scrap/CENSO-DOS-ACTORS-E-CUSTO-V1.md')))


class T16TranscriptNaoFoiResolvido(unittest.TestCase):
    """A chave existir nao prova que legenda de terceiro funciona."""

    def test_a_legenda_continua_declarada_sem_rota(self):
        self.assertFalse(reg.tem_caminho('YOUTUBE', 'youtube.native_caption'))

    def test_a_rota_padrao_de_transcript_continua_sendo_paga(self):
        import social_matriz as mz
        d = mz._rota_padrao(mz.MATRIZ['YOUTUBE']['FETCH_TRANSCRIPT'])
        self.assertEqual(d['CLASSE'], 'APIFY',
                         'transcript mudou de rota sem prova nesta missao')

    def test_a_midia_continua_bloqueada(self):
        self.assertEqual(cap.estado('youtube.media'), cap.BLOCKED)
        self.assertFalse(cap.promete_resultado('youtube.media'))

    def test_o_check_recusa_as_duas(self):
        for c in ('youtube.native_caption', 'youtube.media'):
            self.assertFalse(scrap.CHECK('YOUTUBE', c)['CAN'], c)


class TCheckNaoGasta(unittest.TestCase):
    """O CHECK responde sem tocar a rede. Se tocasse, nao seria um check."""

    def test_quatro_checks_sem_um_socket(self):
        reg.carregar_adaptadores()
        antes = os.environ.get(yt.ENV_CHAVE)
        os.environ[yt.ENV_CHAVE] = CHAVE_FALSA
        real_s, real_c = socket.socket, socket.create_connection
        tentativas = []

        def _proibido(*a, **k):
            tentativas.append(a)
            raise AssertionError('o CHECK tocou a rede')
        socket.socket, socket.create_connection = _proibido, _proibido
        try:
            for c in QUATRO:
                v = scrap.CHECK('YOUTUBE', c)
                self.assertTrue(v['CAN'], c)
                self.assertEqual(v['COST_TO_CHECK_USD'], 0.0)
        finally:
            socket.socket, socket.create_connection = real_s, real_c
            if antes is None:
                os.environ.pop(yt.ENV_CHAVE, None)
            else:
                os.environ[yt.ENV_CHAVE] = antes
        self.assertEqual(tentativas, [])


if __name__ == '__main__':
    unittest.main(verbosity=2)
