#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AS VINTE PROVAS DA C3 — o cutover, e o que nao pode voltar.

A C2 provou que a API oficial atende as quatro capacidades. Isso nao bastava:
os caminhos antigos continuavam CAPAZES de gastar nos dois atores. Estas provas
existem para que essa capacidade deixe de existir, e nao volte em silencio.

    NAO CHAMAR NO TESTE FELIZ NAO E PROVA DE NADA. O que prova e a sentinela
    que reprova quando alguem volta a poder chamar.
"""
import ast
import io
import json
import os
import shutil
import subprocess
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

CHAVE_FALSA = 'chave-de-teste-que-nunca-sai-daqui'

#: Os dois que esta missao aposenta do runtime.
APOSENTADOS = ('streamers~youtube-scraper', 'streamers~youtube-comments-scraper')

#: Os ficheiros onde um caller runtime poderia voltar a nascer.
CALLERS = ('coleta/comunicacao_coleta.py', 'regras/sensor_coleta.py')


def _fonte(rel):
    with io.open(os.path.join(RAIZ, rel), encoding='utf-8') as f:
        return f.read()


def _corpo(rel):
    """O ficheiro sem docstrings nem comentarios — e COM os valores de string.

    ⚠️ A primeira versao desta funcao apagava TODA constante de texto, para
    limpar as docstrings de uma vez. Ela limpava a mais, e o buraco era grave:

        ATORES = {'YOUTUBE': 'streamers~youtube-scraper'}
        viraria
        ATORES = {'': ''}

    — e a sentinela que procura o nome do ator PASSARIA com o ator de volta no
    codigo. Uma sentinela que nao ve o que procura nao e uma sentinela.

    Agora so a DOCSTRING e apagada: o primeiro `Expr` de texto de cada modulo,
    classe e funcao. Tudo o resto sobrevive, porque tudo o resto executa.
    """
    arvore = ast.parse(_fonte(rel))
    for no in ast.walk(arvore):
        if not isinstance(no, (ast.Module, ast.ClassDef, ast.FunctionDef,
                               ast.AsyncFunctionDef)):
            continue
        corpo = getattr(no, 'body', None) or []
        if (corpo and isinstance(corpo[0], ast.Expr)
                and isinstance(corpo[0].value, ast.Constant)
                and isinstance(corpo[0].value.value, str)):
            corpo[0].value.value = ''
    # `ast.unparse` ja deixa os comentarios de fora: eles nao viram nos.
    return ast.unparse(arvore)


class _ErroHttp(urllib.error.HTTPError):
    def __init__(self, code, reason):
        b = json.dumps({'error': {'errors': [{'reason': reason}]}}).encode()
        super().__init__('https://x', code, 'e', {}, io.BytesIO(b))


def _transporte(resposta=None, erro=None):
    def dentro(url):
        if erro is not None:
            raise erro
        return resposta or {'items': []}
    return dentro


class _Base(unittest.TestCase):
    """Chave falsa no ambiente, bruto em pasta descartavel. Lei da casa desde a C2."""

    def setUp(self):
        self._antes = os.environ.get(yt.ENV_CHAVE)
        os.environ[yt.ENV_CHAVE] = CHAVE_FALSA
        self._tmp = tempfile.mkdtemp(prefix='c3-raw-')
        self._raw_antes = env.RAW_DIR
        env.RAW_DIR = self._tmp

    def tearDown(self):
        env.RAW_DIR = self._raw_antes
        shutil.rmtree(self._tmp, ignore_errors=True)
        if self._antes is None:
            os.environ.pop(yt.ENV_CHAVE, None)
        else:
            os.environ[yt.ENV_CHAVE] = self._antes


# ══════════════════════════════════════════════════════════════════════════
class T1a4OsTresCallersPedemCapacidade(unittest.TestCase):
    """Os tres caminhos antigos pedem CAPACIDADE, nao ferramenta."""

    def test_comunicacao_declara_capacidade_para_youtube(self):
        import comunicacao_coleta as cc
        self.assertIn('YOUTUBE', cc.CAPACIDADES_SCRAP)
        self.assertNotIn('YOUTUBE', cc.ATORES,
                         'o YouTube voltou a tabela de atores')

    def test_sensor_declara_capacidade_para_busca_e_comentario(self):
        import sensor_coleta as sc
        self.assertEqual(sc.CAPACIDADES_SCRAP['YOUTUBE_SEARCH'], 'youtube.search')
        self.assertEqual(sc.CAPACIDADES_SCRAP['YOUTUBE_COMMENTS'], 'youtube.comments')
        self.assertNotIn('YOUTUBE_SEARCH', sc.ATORES)
        self.assertNotIn('YOUTUBE_COMMENTS', sc.ATORES)

    def test_as_capacidades_pedidas_existem_e_tem_caminho(self):
        reg.carregar_adaptadores()
        import comunicacao_coleta as cc
        import sensor_coleta as sc
        pedidas = (list(cc.CAPACIDADES_SCRAP['YOUTUBE'].values())
                   + list(sc.CAPACIDADES_SCRAP.values()))
        for c in pedidas:
            with self.subTest(c):
                self.assertTrue(cap.existe(c), '%s nao esta declarada' % c)
                self.assertTrue(reg.tem_caminho('YOUTUBE', c), '%s sem caminho' % c)

    def test_a_bifurcacao_e_por_tabela_e_nao_por_nome_de_plataforma(self):
        # Um `if plataforma == 'YOUTUBE'` faria do caller um segundo roteador, e
        # o proximo a migrar acrescentaria o segundo `elif`.
        corpo = _corpo('coleta/comunicacao_coleta.py')
        self.assertNotIn("plataforma == 'YOUTUBE'", corpo)
        self.assertIn('CAPACIDADES_SCRAP', corpo)


class T5e6NenhumChamaOsAposentados(unittest.TestCase):
    """A sentinela estrutural: nenhum caller pode sequer NOMEAR os dois."""

    def test_nenhum_caller_nomeia_os_atores_aposentados(self):
        for rel in CALLERS:
            corpo = _corpo(rel)
            for ator in APOSENTADOS:
                self.assertNotIn(ator, corpo,
                                 '%s voltou a nomear %s' % (rel, ator))

    def test_nenhum_caller_nomeia_as_chaves_antigas_da_tabela(self):
        corpo = _corpo('regras/sensor_coleta.py')
        for chave in ("ATORES['YOUTUBE_SEARCH']", "ATORES['YOUTUBE_COMMENTS']"):
            self.assertNotIn(chave, corpo, chave)

    def test_a_sentinela_ve_o_nome_se_ele_voltar(self):
        """Uma sentinela que nao ve o que procura nao e uma sentinela.

        A primeira versao de `_corpo` apagava toda constante de texto, e um
        ator de volta no codigo passaria despercebido. Isto reprova se ela
        voltar a cegar.
        """
        import tempfile as tf
        codigo = "ATORES = {'YOUTUBE': '%s'}\n" % APOSENTADOS[0]
        d = tf.mkdtemp(prefix='c3-sentinela-')
        try:
            rel = os.path.join(d, 'falso.py')
            with io.open(rel, 'w', encoding='utf-8') as f:
                f.write('"""docstring que deve sumir."""\n' + codigo)
            arvore = ast.parse(io.open(rel, encoding='utf-8').read())
            for no in ast.walk(arvore):
                corpo = getattr(no, 'body', None) or []
                if (isinstance(no, ast.Module) and corpo
                        and isinstance(corpo[0], ast.Expr)
                        and isinstance(corpo[0].value, ast.Constant)):
                    corpo[0].value.value = ''
            visto = ast.unparse(arvore)
        finally:
            shutil.rmtree(d, ignore_errors=True)
        self.assertIn(APOSENTADOS[0], visto, 'a sentinela ficou cega')
        self.assertNotIn('docstring que deve sumir', visto)

    def test_o_repositorio_nao_tem_caller_runtime_dos_dois(self):
        """Varre o codigo vivo inteiro, nao so os tres ficheiros migrados."""
        vivos = []
        for gaveta in _gavetas.GAVETAS:
            base = os.path.join(RAIZ, gaveta)
            if not os.path.isdir(base):
                continue
            for pasta, _d, ficheiros in os.walk(base):
                for f in ficheiros:
                    if not f.endswith('.py'):
                        continue
                    rel = os.path.relpath(os.path.join(pasta, f), RAIZ)
                    corpo = _corpo(rel)
                    if any(a in corpo for a in APOSENTADOS):
                        vivos.append(rel)
        self.assertEqual(vivos, [], 'caller runtime sobrevivente: %s' % vivos)

    def test_o_ator_de_legenda_continua_onde_ainda_e_preciso(self):
        # Aposentar o que tem substituto NAO autoriza aposentar o que nao tem.
        import sensor_coleta as sc
        self.assertEqual(sc.ATORES['YOUTUBE_TRANSCRIPT'],
                         'pintostudio~youtube-transcript-scraper')


class T7e8SemanticaDoSensorPreservada(unittest.TestCase):
    """A migracao nao pode promover candidato a identidade."""

    def test_search_hit_nao_vira_pessoa(self):
        import sensor_coleta as sc
        v = {'NATIVE_ID': 'abc12345678', 'TITLE': 't', 'URL': 'u',
             'RAW': {'CHANNEL_TITLE': 'Canal Silva'}}
        c = sc._cand_video(v, {'NAME': 'Ana Silva', 'PERSON_ID': 'P1'}, 'termo',
                           {'LOTE': 'A'}, rota='PERSON_NAME_SEARCH')
        self.assertEqual(c['CHANNEL_IDENTITY_STATE'], 'NOT_PROVED')
        self.assertIn('SEARCH_HIT != PERSON', c['CHANNEL_IDENTITY_EVIDENCE'])

    def test_lugar_do_fato_continua_desconhecido(self):
        import sensor_coleta as sc
        c = sc._cand_video({'NATIVE_ID': 'x'}, None, 't', {}, rota='R')
        self.assertEqual(c['COUNTRY_OF_FACT'], 'NOT_KNOWN')
        self.assertEqual(c['REGION_OF_FACT'], 'NOT_KNOWN')

    def test_o_region_code_nao_vira_lugar_do_objeto(self):
        # A C2 mediu: `regionCode` molda ranking, nao prova lugar do autor.
        self.assertIn('REQUEST_REGION_CODE', _fonte('coleta/youtube_oficial.py'))
        self.assertIn('AUTHOR_LOCATION', _fonte('coleta/youtube_oficial.py'))


class T9EstadosDistintos(_Base):
    """Desligado, vazio e erro continuam tres coisas."""

    def _collect(self, capacidade, *, resposta=None, erro=None, **kw):
        s = yt.Sessao(api_key=CHAVE_FALSA, transporte=_transporte(resposta, erro))
        return scrap.COLLECT(platform='YOUTUBE', capability=capacidade,
                             run_id='T-C3', country_scope='IT', sessao=s, **kw)

    def test_tres_estados_tres_nomes(self):
        _o, desligado = self._collect('youtube.comments', video_id='x' * 11,
                                      limite_threads=1,
                                      erro=_ErroHttp(403, 'commentsDisabled'))
        _o, vazio = self._collect('youtube.comments', video_id='y' * 11,
                                  limite_threads=1, resposta={'items': []})
        _o, erro = self._collect('youtube.comments', video_id='z' * 11,
                                 limite_threads=1,
                                 erro=_ErroHttp(500, 'backendError'))
        self.assertEqual(desligado['RESULT'], 'FEATURE_DISABLED')
        self.assertEqual(vazio['RESULT'], 'ZERO_RESULTS')
        self.assertEqual(erro['RESULT'], 'SOURCE_UNAVAILABLE')
        self.assertEqual(len({desligado['RESULT'], vazio['RESULT'], erro['RESULT']}), 3)

    def test_comentario_desligado_nao_contamina_o_lote(self):
        # O lote so muda de estado se o video falhar por outra coisa. Desligado,
        # vazio e OK sao os tres que ele tolera sem contaminar os vizinhos.
        corpo = _corpo('regras/sensor_coleta.py')
        self.assertIn('FEATURE_DISABLED', corpo,
                      'o lote de comentarios deixou de tolerar video desligado')
        self.assertIn('ZERO_RESULTS', corpo)


class T10a13RotaOficialSemQuedaParaPago(_Base):
    """Provider oficial, custo zero, quota separada, e nenhuma fuga para a Apify."""

    def _collect(self, capacidade, *, erro=None, **kw):
        s = yt.Sessao(api_key=CHAVE_FALSA, transporte=_transporte(None, erro))
        return scrap.COLLECT(platform='YOUTUBE', capability=capacidade,
                             run_id='T-C3', country_scope='IT', sessao=s, **kw)

    def test_provider_e_a_api_oficial(self):
        for c, kw in (('youtube.search', dict(termo='t', limit=1)),
                      ('youtube.comments', dict(video_id='x' * 11, limite_threads=1))):
            with self.subTest(c):
                _o, tr = self._collect(c, **kw)
                self.assertEqual(tr['PROVIDER_REQUESTED'], forn.API_OFICIAL)
                self.assertEqual(tr.get('ROUTE_CLASS'), 'OFFICIAL_API_FREE')

    def test_custo_em_dolar_e_zero_na_rota_oficial(self):
        self.assertEqual(yt.COST_USD, 0.0)
        self.assertEqual(yt.COST_BASIS, 'QUOTA_GRATUITA_OFICIAL')

    def test_quota_nao_se_converte_em_dolar(self):
        # Dois numeros, duas unidades. Somar daria um terceiro que nao existe.
        s = yt.Sessao(api_key=CHAVE_FALSA, transporte=_transporte({'items': []}))
        yt.buscar(termo='t', run_id='T-C3', limit=1, sessao=s)
        m = s.metricas()
        self.assertEqual(m['COST_USD'], 0.0)
        self.assertEqual(m['SEARCH_CALLS_USED'], 1)
        self.assertEqual(m['SEARCH_CALLS_REMAINING'], 'UNKNOWN')

    def test_erro_oficial_nao_cai_para_apify(self):
        for razao in ('quotaExceeded', 'keyInvalid', 'backendError'):
            with self.subTest(razao):
                _o, tr = self._collect('youtube.search', termo='t', limit=1,
                                       erro=_ErroHttp(403, razao))
                self.assertFalse(tr['PAID_PROVIDER_USED'])
                self.assertIsNone(tr['PROVIDER_USED'])
                self.assertIsNone(tr['WHY_FALLBACK'])


class T14e15UmRoteadorUmAdaptador(unittest.TestCase):
    """A C1 e a C2 nao regridem."""

    def test_o_roteador_continua_sem_conhecer_plataformas(self):
        corpo = _corpo('coleta/social_rotas.py')
        for plat in ('INSTAGRAM', 'LINKEDIN', 'FACEBOOK', 'MASTODON'):
            self.assertNotIn("'%s'" % plat, corpo)
        self.assertNotIn('youtube_oficial', corpo)
        self.assertEqual(sr.ADAPTADORES, {})

    def test_so_um_adaptador_de_youtube(self):
        reg.carregar_adaptadores()
        donos = {r['ADAPTADOR'] for k, r in reg.registados().items()
                 if k[0] == 'YOUTUBE'}
        self.assertEqual(donos, {'adaptador_youtube'})

    def test_os_callers_nao_saltam_o_scrap(self):
        # O caminho e caller -> executor -> router/registry -> adaptador -> API.
        for rel in CALLERS:
            corpo = _corpo(rel)
            self.assertNotIn('import youtube_oficial', corpo,
                             '%s fala com a API por fora do SCRAP' % rel)

    def test_nenhum_segundo_executor_nasceu(self):
        donos = []
        for gaveta in _gavetas.GAVETAS:
            base = os.path.join(RAIZ, gaveta)
            if not os.path.isdir(base):
                continue
            for pasta, _d, fs in os.walk(base):
                for f in fs:
                    if f.endswith('.py'):
                        rel = os.path.relpath(os.path.join(pasta, f), RAIZ)
                        t = _fonte(rel)
                        if 'def COLLECT(' in t and 'def CAPABILITIES(' in t:
                            donos.append(rel)
        self.assertEqual(donos, ['coleta/scrap_executor.py'])


class T16e17HistoriaIntacta(unittest.TestCase):
    """Aposentar nao e apagar."""

    def test_os_artefatos_historicos_continuam(self):
        for rel in ('data/samples/RUN-MANIFEST.json',
                    'data/samples/SENSOR-PILOT/RUNS-A.json',
                    'data/samples/SENSOR-PILOT/COMENTARIOS-A.json'):
            self.assertTrue(os.path.exists(os.path.join(RAIZ, rel)), rel)

    def test_o_gasto_dos_aposentados_continua_legivel(self):
        texto = _fonte('data/samples/SENSOR-PILOT/RUNS-A.json')
        self.assertTrue(any(a in texto for a in APOSENTADOS),
                        'a historia do gasto desapareceu')

    def test_o_censo_de_custo_continua_citavel(self):
        for rel in ('docs/sintonia-scrap/CENSO-DOS-ACTORS-E-CUSTO-V1.md',
                    'docs/sintonia-scrap/C2-YOUTUBE-OFFICIAL-FIRST.md'):
            self.assertTrue(os.path.exists(os.path.join(RAIZ, rel)), rel)


class T18RawDeTesteNuncaNoAcervo(unittest.TestCase):
    """LEI NOVA DA CASA, nascida de um defeito meu na C2.

    Seis ficheiros de bruto inventado entraram num commit, na pasta do bruto
    verdadeiro, com o nome certo. Isto existe para que nao volte.

        BRUTO DE TESTE AO LADO DE BRUTO DE COLETA E A PROVA DE UMA COLETA QUE
        NUNCA ACONTECEU.
    """

    ACERVO = ('data/samples', 'data/raw')

    def test_as_provas_desta_casa_redirecionam_o_bruto(self):
        for rel in ('tests/test_c2_youtube_oficial.py', 'tests/test_c3_youtube_cutover.py'):
            corpo = _fonte(rel)
            self.assertIn('env.RAW_DIR', corpo, '%s nao redireciona o bruto' % rel)
            self.assertIn('tempfile', corpo, '%s nao usa pasta descartavel' % rel)

    def test_a_suite_nao_deixou_bruto_novo_na_arvore(self):
        r = subprocess.run(['git', 'status', '--porcelain'] + list(self.ACERVO),
                           cwd=RAIZ, capture_output=True, text=True)
        sujos = [l for l in r.stdout.split('\n') if l.strip()
                 and 'raw' in l.lower()]
        self.assertEqual(sujos, [], 'bruto novo no acervo: %s' % sujos)

    def test_gravar_raw_respeita_o_redirecionamento(self):
        tmp = tempfile.mkdtemp(prefix='c3-sentinela-')
        antes = env.RAW_DIR
        env.RAW_DIR = tmp
        try:
            ref = env.guardar_raw('YOUTUBE', 'sentinela', '{"a":1}')
            self.assertTrue(str(ref).startswith(tmp) or tmp in str(ref),
                            'o bruto escapou do redirecionamento: %s' % ref)
        finally:
            env.RAW_DIR = antes
            shutil.rmtree(tmp, ignore_errors=True)


class T18bOBugQueOCutoverDescobriu(unittest.TestCase):
    """`normalizar` lia um campo que o lote congelado nunca teve.

    Nenhuma das 22 contas carrega `ACCOUNT_SCOPE`. O acesso direto levantava
    `KeyError` na PRIMEIRA conta, de qualquer plataforma — a prova de que esta
    normalizacao nunca correu ate ao fim desde que o lote foi congelado.
    """

    def test_conta_sem_o_campo_nao_rebenta(self):
        import comunicacao_coleta as cc
        conta = {'ACCOUNT_HANDLE': 'h', 'ACCOUNT_URL': 'u', 'COMPANY': 'C',
                 'COUNTRY': 'IT'}
        item = cc.normalizar({'NATIVE_ID': 'x'}, conta, 'YOUTUBE', 30, {})
        self.assertEqual(item['ACCOUNT_SCOPE'], 'NOT_KNOWN')

    def test_nenhuma_conta_do_lote_tem_o_campo(self):
        import comunicacao_coleta as cc
        contas = cc.contas_autorizadas()
        semear = [c for c in contas if 'ACCOUNT_SCOPE' in c]
        self.assertEqual(semear, [],
                         'o lote ganhou o campo — reveja o valor honesto')

    def test_toda_conta_do_lote_normaliza(self):
        import comunicacao_coleta as cc
        for conta in cc.contas_autorizadas():
            with self.subTest(conta.get('ACCOUNT_URL')):
                cc.normalizar({'NATIVE_ID': 'x'}, conta, conta['PLATFORM'], 30, {})


class T19SegredoNuncaNoLog(unittest.TestCase):
    """Nada do caminho novo imprime, mede ou resume a chave."""

    FICHEIROS = CALLERS + ('coleta/adaptador_youtube.py', 'coleta/scrap_executor.py')

    def test_ninguem_imprime_nem_mede_a_chave(self):
        for rel in self.FICHEIROS:
            corpo = _corpo(rel)
            # `len(chaves)` e o POOL da Apify, nao a chave do YouTube. O
            # padrao tem de nomear o que procura, senao reprova por parecenca.
            for proibido in ('print(yt.chave', 'print(api_key', 'len(api_key',
                             'len(yt.chave', 'api_key[:', 'yt.chave()[:',
                             'print(os.environ[', "os.environ['YOUTUBE_DATA_API_KEY'])"):
                self.assertNotIn(proibido, corpo, '%s: %s' % (rel, proibido))

    def test_o_redator_apaga_a_forma_da_chave(self):
        import social_sessao as ss
        falsa = 'AIza' + 'Sy' + 'B' * 33
        self.assertNotIn(falsa, ss.redigir('?key=%s' % falsa))


class T20UmContratoDeProvenienciaSo(unittest.TestCase):
    """Nenhum segundo vocabulario de proveniencia nasceu."""

    def test_o_vocabulario_de_fornecedor_tem_um_dono(self):
        donos = []
        for gaveta in _gavetas.GAVETAS:
            base = os.path.join(RAIZ, gaveta)
            if not os.path.isdir(base):
                continue
            for pasta, _d, fs in os.walk(base):
                for f in fs:
                    if f.endswith('.py'):
                        rel = os.path.relpath(os.path.join(pasta, f), RAIZ)
                        t = _fonte(rel)
                        if 'PROVIDER_REQUESTED' in t and 'def conferir(' in t:
                            donos.append(rel)
        self.assertEqual(donos, ['coleta/scrap_fornecedores.py'], donos)

    def test_os_callers_reusam_o_trace_do_scrap(self):
        for rel in CALLERS:
            self.assertIn('COLLECTION_PROVIDER', _fonte(rel),
                          '%s nao declara quem trouxe' % rel)

    def test_ator_ausente_nao_e_ator_desconhecido(self):
        import sensor_coleta as sc
        prov = sc._proveniencia({'RUN_ID': 'R', 'COLLECTION_PROVIDER': 'OFFICIAL_API',
                                 'PAID': False}, None, 'A', 'B')
        self.assertEqual(prov['APIFY_ACTOR'], 'NAO_SE_APLICA')
        self.assertNotEqual(prov['APIFY_ACTOR'], 'NOT_KNOWN')
        self.assertFalse(prov['PAID'])

    def test_o_contador_de_pago_nao_conta_o_gratuito(self):
        import comunicacao_coleta as cc
        r = {'ITEMS': [], 'UNITS_DONE': [], 'UNITS_PENDING': [], 'STATE': 'DONE',
             'DUPLICATES_REMOVED': 0}
        mans = [{'PAID': False, 'COST_USD': 0.0, 'OFFICIAL_API_QUOTA_USED': 2,
                 'COLLECTION_PROVIDER': 'OFFICIAL_API'},
                {'PAID': True, 'COST_USD': 1.5, 'COLLECTION_PROVIDER': 'APIFY'}]
        tmp = tempfile.mkdtemp(prefix='c3-posts-')
        antes = cc.SAIDA
        cc.SAIDA = tmp
        try:
            corpo = cc._gravar_posts('TESTE', [], {'DIAS': 30}, r, mans, 'NO')
        finally:
            cc.SAIDA = antes
            shutil.rmtree(tmp, ignore_errors=True)
        self.assertEqual(corpo['COLLECTION_RUNS'], 2)
        self.assertEqual(corpo['APIFY_RUNS'], 1, 'a rota gratuita foi contada como paga')
        self.assertEqual(corpo['OFFICIAL_API_QUOTA_USED'], 2)


# ══════════════════════════════════════════════════════════════════════════
class T21AQuotaNaoSeInventa(_Base):
    """O numero de quota publicado e MEDIDO, ou declara-se PISO. Nunca suposto.

    Estas provas nasceram de um defeito MEU, nesta mesma missao. O primeiro
    corte escrevia `+= 1` para o passo da colheita e `= 1` para o do sensor,
    com o raciocinio «uma pagina custa uma unidade». Medido com transporte
    injetado, o passo da colheita custa DUAS:

        channels.list      1 unidade   (achar a playlist de uploads)
        playlistItems.list 1 unidade   (le-la)

    O artefato saia com metade do gasto real, com cara de medida.
    """

    def _transporte(self):
        def dentro(url):
            from urllib.parse import urlparse, parse_qs
            q = urlparse(url)
            metodo = q.path.rsplit('/', 1)[-1]
            if metodo == 'channels':
                parte = (parse_qs(q.query).get('part') or [''])[0]
                if 'contentDetails' in parte:
                    return {'items': [{'id': 'UCteste', 'snippet': {'title': 'T'},
                                       'contentDetails': {'relatedPlaylists':
                                                          {'uploads': 'UUteste'}}}]}
                return {'items': [{'id': 'UCteste', 'snippet': {'title': 'T'}}]}
            if metodo == 'playlistItems':
                return {'items': []}
            return {'items': []}
        return dentro

    def test_a_colheita_custa_mais_do_que_uma_unidade(self):
        """A medida que prova que o literal `1` estava errado."""
        s = yt.Sessao(transporte=self._transporte())
        antes = dict(s.usado)
        scrap.COLLECT(platform='YOUTUBE', capability='youtube.channel.discovery',
                      run_id='T21', country_scope='IT', sessao=s,
                      channel_id='UCteste', limit=50)
        gasto = s.usado[yt.GENERAL] - antes[yt.GENERAL]
        self.assertGreater(gasto, 1,
                           'se a colheita passasse a custar 1 unidade, o literal '
                           'antigo estaria certo e esta prova pode sair')

    def test_nenhum_caller_atribui_quota_por_literal(self):
        """A sentinela. Um digito escrito a mao neste campo reprova."""
        import ast as _ast
        maus = []
        for rel in CALLERS:
            arvore = _ast.parse(_fonte(rel))
            for no in _ast.walk(arvore):
                alvos = []
                if isinstance(no, _ast.Assign):
                    alvos = no.targets
                elif isinstance(no, _ast.AugAssign):
                    alvos = [no.target]
                nomeia = False
                for a in alvos:
                    if (isinstance(a, _ast.Subscript)
                            and isinstance(a.slice, _ast.Constant)
                            and a.slice.value == 'OFFICIAL_API_QUOTA_USED'):
                        nomeia = True
                if not nomeia:
                    continue
                v = no.value
                if isinstance(v, _ast.Constant) and isinstance(v.value, int) and v.value:
                    maus.append('%s:%d' % (rel, no.lineno))
        self.assertEqual(maus, [], 'quota atribuida por literal: %s' % maus)

    def test_a_rota_que_nao_declara_unidades_sai_parcial(self):
        import sensor_coleta as sc
        _it, man, _p = sc._rodar_scrap('youtube.search', run_id='T21',
                                       platform='YOUTUBE', country='IT',
                                       query='x', lote='T21', termo='x', limit=1,
                                       sessao=yt.Sessao(transporte=self._transporte()))
        self.assertEqual(man['OFFICIAL_API_QUOTA_STATE'], 'PARTIAL')
        self.assertEqual(man['OFFICIAL_API_QUOTA_USED'], 0,
                         'o piso e o que foi declarado, e nada foi declarado')

    def test_parcial_contamina_o_lote(self):
        import sensor_coleta as sc
        man = {'OFFICIAL_API_QUOTA_USED': 3, 'OFFICIAL_API_QUOTA_STATE': 'MEASURED'}
        sc._juntar_quota(man, {'OFFICIAL_API_QUOTA_USED': 0,
                               'OFFICIAL_API_QUOTA_STATE': 'PARTIAL'})
        self.assertEqual(man['OFFICIAL_API_QUOTA_STATE'], 'PARTIAL',
                         'um lote meio medido nao e um lote medido')
        self.assertEqual(man['OFFICIAL_API_QUOTA_USED'], 3)

    def test_o_artefato_declara_se_a_soma_esta_completa(self):
        import comunicacao_coleta as cc
        r = {'ITEMS': [], 'UNITS_DONE': [], 'UNITS_PENDING': [], 'STATE': 'DONE',
             'DUPLICATES_REMOVED': 0}
        tmp = tempfile.mkdtemp(prefix='c3-posts-')
        antes = cc.SAIDA
        cc.SAIDA = tmp
        try:
            parcial = cc._gravar_posts(
                'TESTE', [], {'DIAS': 30}, r,
                [{'PAID': False, 'OFFICIAL_API_QUOTA_USED': 1,
                  'OFFICIAL_API_QUOTA_STATE': 'PARTIAL'}], 'NO')
            medido = cc._gravar_posts(
                'TESTE', [], {'DIAS': 30}, r,
                [{'PAID': False, 'OFFICIAL_API_QUOTA_USED': 3,
                  'OFFICIAL_API_QUOTA_STATE': 'MEASURED'}], 'NO')
            paga = cc._gravar_posts(
                'TESTE', [], {'DIAS': 30}, r, [{'PAID': True, 'COST_USD': 1.5}], 'NO')
        finally:
            cc.SAIDA = antes
            shutil.rmtree(tmp, ignore_errors=True)
        self.assertEqual(parcial['OFFICIAL_API_QUOTA_STATE'], 'PARTIAL')
        self.assertEqual(medido['OFFICIAL_API_QUOTA_STATE'], 'MEASURED')
        self.assertEqual(paga['OFFICIAL_API_QUOTA_STATE'], 'NOT_APPLICABLE',
                         'rota paga nao gasta quota oficial — isso nao e zero medido')

    def test_quota_e_estado_viajam_juntos_ate_a_medicao(self):
        """Publicar o piso sem a palavra que diz que e piso e publicar um total."""
        t = _fonte('coleta/comunicacao_medir.py')
        self.assertIn('Q_OFFICIAL_API_QUOTA_USED', t)
        self.assertIn('Q_OFFICIAL_API_QUOTA_STATE', t)


if __name__ == '__main__':
    unittest.main(verbosity=2)
