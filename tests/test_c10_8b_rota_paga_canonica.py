# -*- coding: utf-8 -*-
"""C10.8B — as sentinelas da primeira rota paga canônica.

Todas medem COMPORTAMENTO, e o falso é sempre `subprocess.run` DENTRO do
coletor — a camada mais funda, por baixo dos dois tetos.

    UM FAKE ACIMA DO GATE MEDE O FAKE.
"""
import ast
import gzip
import io
import json
import os
import shutil
import sys
import tempfile
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in ('coleta', 'leis', 'medidas', 'ferramentas', 'guarda', ''):
    sys.path.insert(0, os.path.join(RAIZ, p) if p else RAIZ)

import adaptador_youtube as ay                                    # noqa: E402
import apify_pool as ap                                           # noqa: E402
import coletor as ct                                              # noqa: E402
import scrap_capacidades as cap                                   # noqa: E402
import scrap_executor as sx                                       # noqa: E402
import scrap_registo as reg                                       # noqa: E402
import social_matriz as mz                                        # noqa: E402
reg.carregar_adaptadores()

PLAT, CAPAC = 'YOUTUBE', 'youtube.native_caption'
MOTIVO = 'ROUTE_NOT_ALLOWED'
TETO_USD, TETO_REDE = 0.10, 5
ALVO = 'EAkcA_2FDN8'
ALVO_URL = 'https://www.youtube.com/watch?v=%s' % ALVO
HISTORICO = 'data/samples/SENSOR-PILOT/TRANSCRICOES-B.json'
BYTES = 'data/samples/raw-paid/ES-T8-001-youtube-transcripts.raw.json.gz'


def _fonte(rel):
    return io.open(os.path.join(RAIZ, rel), encoding='utf-8').read()


def _texto_real():
    d = json.load(gzip.open(os.path.join(RAIZ, BYTES), 'rt', encoding='utf-8'))
    return next(x for x in d if (x.get('chars') or 0) > 0)['transcript']


def _historico():
    d = json.load(io.open(os.path.join(RAIZ, HISTORICO), encoding='utf-8'))
    return next((i for i in (d.get('ITEMS') or [])
                 if ALVO in str(i.get('SOURCE_URL'))), {})


class _Resultado(object):
    def __init__(self, corpo, rc=0):
        self.returncode, self.stdout, self.stderr = rc, corpo, ''


class _Falsa(object):
    """`subprocess.run` do coletor — por BAIXO dos dois tetos."""

    def __init__(self, *, texto='texto', custo=0.01, terminal=True, itens=None):
        self.texto, self.custo, self.terminal = texto, custo, terminal
        self.itens = itens
        self.posts, self.polls, self.datasets, self.kv = [], [], [], []

    def _cap(self, url):
        for parte in url.split('?', 1)[-1].split('&'):
            if parte.startswith('maxTotalChargeUsd='):
                return float(parte.split('=', 1)[1])
        return None

    def __call__(self, cmd, **k):
        url = cmd[-1]
        metodo = cmd[cmd.index('-X') + 1] if '-X' in cmd else 'GET'
        corpo = cmd[cmd.index('-d') + 1] if '-d' in cmd else None
        if metodo.upper() == 'POST':
            self.posts.append({'cap': self._cap(url),
                               'entrada': json.loads(corpo) if corpo else None,
                               'url': url})
            return _Resultado(json.dumps({'data': {
                'id': 'RUN-FALSA-1',
                'status': 'SUCCEEDED' if self.terminal else 'RUNNING',
                'startedAt': '2026-09-12T00:00:00.000Z',
                'finishedAt': '2026-09-12T00:00:04.000Z',
                'buildNumber': '1.0.57', 'defaultDatasetId': 'DS-FALSO',
                'defaultKeyValueStoreId': 'KV-FALSO',
                'usageTotalUsd': self.custo}}))
        if '/actor-runs/' in url:
            self.polls.append(url)
            return _Resultado(json.dumps({'data': {
                'id': 'RUN-FALSA-1', 'status': 'SUCCEEDED',
                'defaultDatasetId': 'DS-FALSO',
                'defaultKeyValueStoreId': 'KV-FALSO',
                'usageTotalUsd': self.custo}}))
        if '/datasets/' in url:
            self.datasets.append(url)
            itens = self.itens if self.itens is not None else [
                {'url': ALVO_URL, 'transcript': self.texto, 'chars': len(self.texto)}]
            return _Resultado(json.dumps(itens))
        self.kv.append(url)
        return _Resultado(json.dumps({'data': {'items': []}}))


class _Cenario(object):
    def __init__(self, falso, *, com_chave=True):
        self.falso, self.com_chave = falso, com_chave

    def __enter__(self):
        self._run, self._pool, self._gaveta = ct.subprocess.run, ap.pool, ct.RAW_DIR
        ct.subprocess.run = self.falso
        if self.com_chave:
            ap.pool = lambda env=None: ['apify_api_TOKEN_DE_MENTIRA']
        ct.RAW_DIR = tempfile.mkdtemp(prefix='t-c108b-')
        return self

    def __exit__(self, *a):
        ct.subprocess.run, ap.pool = self._run, self._pool
        shutil.rmtree(ct.RAW_DIR, ignore_errors=True)
        ct.RAW_DIR = self._gaveta
        return False


#: A AUTORIZACAO DE GASTO DESTA BATERIA, DESDE A SCRAP-SR-02.
#:
#: Ela mede a ROTA PAGA, e desde a SR-02 uma rota paga so nasce com alguem a
#: autoriza-la. Escreve-la aqui e a mesma escolha que a producao faz em
#: `social_scrap.FASES_PAGAS`: os limites vivem em Python versionado.
#:
#:     UM AJUDANTE DE TESTE QUE COMPRA SEM AUTORIZACAO
#:     PROVA UM SISTEMA QUE NAO E ESTE.
AUTORIZACAO = {'AUTORIZACAO_HUMANA': 'bateria C10.8B, provider falso',
               'MAX_PROVIDER_RUNS': 1, 'MAX_START_POSTS': 1,
               'MAX_USD': TETO_USD}


def _colher(falso, *, gasto=TETO_USD, rede=TETO_REDE, com_chave=True,
            permitir_pago=True, motivo=MOTIVO, modo=sx.TRIAL, video=ALVO,
            autorizacao=AUTORIZACAO):
    with _Cenario(falso, com_chave=com_chave):
        pedido = dict(platform=PLAT, capability=CAPAC, run_id='t-c108b',
                      modo=modo, permitir_pago=permitir_pago, motivo_pago=motivo,
                      video_id=video, autorizacao=autorizacao)
        if rede is not None:
            pedido['teto_de_rede'] = rede
        if gasto is None:
            return sx.COLLECT(**pedido)
        with ct.orcamento_financeiro(gasto) as orc:
            objetos, trace = sx.COLLECT(**pedido)
            trace['_ORCAMENTO'] = orc
            return objetos, trace


# ══════════════════════════════════════════════════════════════════════════
class ACapacidadeNaoEARota(unittest.TestCase):
    """CAPABILITY PROVEN != PAID ROUTE PROVEN."""

    def test_1_a_capacidade_continua_PROVEN(self):
        self.assertEqual(cap.estado(CAPAC), 'PROVEN')

    def test_2_a_rota_paga_e_a_padrao_porque_as_livres_estao_NAO(self):
        rotas = (mz.MATRIZ.get(PLAT) or {}).get(cap.da_matriz(CAPAC)) or []
        livres = [r for r in rotas if r['CLASSE'] != 'APIFY']
        self.assertTrue(livres, 'a matriz deixou de declarar as rotas livres')
        for r in livres:
            self.assertEqual(r['PERMITIDA'], 'NAO', r['ROTA'])
        self.assertEqual(mz._rota_padrao(rotas)['ROTA'], ay.ROTA_TRANSCRICAO)

    def test_2b_o_estado_da_rota_e_coerente_com_a_evidencia(self):
        """Uma rota promovida tem de citar o artefato da corrida que a provou.

        Não se exige `POSSIBLE_NOT_PROVED` para sempre — isso faria a sentinela
        reprovar no dia em que a rota fosse legitimamente provada, que é o
        defeito que a C10.8A já pagou. O que se exige é COERÊNCIA:

            ROUTE ALLOWED != ROUTE EXECUTED.
            UMA ROTA PROMOVIDA SEM ARTEFATO DIZ QUE CORREU QUANDO NÃO CORREU.
        """
        rotas = (mz.MATRIZ.get(PLAT) or {}).get(cap.da_matriz(CAPAC)) or []
        paga = next(r for r in rotas if r['ROTA'] == ay.ROTA_TRANSCRICAO)
        if paga['ESTADO'] in ('PROVED', 'PARTIAL'):
            self.assertTrue(
                paga.get('EVIDENCIA'),
                'a rota paga foi promovida para %s e nao cita artefato nenhum'
                % paga['ESTADO'])
        else:
            self.assertEqual(paga['ESTADO'], 'POSSIBLE_NOT_PROVED',
                             'estado de rota fora do vocabulario: %s' % paga['ESTADO'])

    def test_2d_PROVED_exige_entrega_medida_no_registo_da_corrida(self):
        """`PROVED` diz «esta rota entrega». O registo da corrida é quem sabe.

            PROVIDER REACHED != CAPABILITY DELIVERED.
        """
        rotas = (mz.MATRIZ.get(PLAT) or {}).get(cap.da_matriz(CAPAC)) or []
        paga = next(r for r in rotas if r['ROTA'] == ay.ROTA_TRANSCRICAO)
        if paga['ESTADO'] != 'PROVED':
            return
        registo = os.path.join(RAIZ, 'data/samples/SCRAP-YOUTUBE/yt-legenda-paga.json')
        self.assertTrue(os.path.exists(registo),
                        'a rota diz PROVED e nao ha registo de corrida nenhuma')
        with io.open(registo, encoding='utf-8') as f:
            d = json.load(f)
        self.assertTrue(
            any(i.get('TRANSCRIPT_PRESENT') for i in (d.get('ITEMS') or [])),
            'a rota foi promovida a PROVED e a corrida registada nao entregou '
            'transcricao nenhuma')

    def test_2c_promovida_a_PARTIAL_a_nota_diz_qual_e_o_limite(self):
        """`PARTIAL` sem o limite escrito é `PROVED` com outro nome."""
        rotas = (mz.MATRIZ.get(PLAT) or {}).get(cap.da_matriz(CAPAC)) or []
        paga = next(r for r in rotas if r['ROTA'] == ay.ROTA_TRANSCRICAO)
        if paga['ESTADO'] == 'PARTIAL':
            self.assertIn('PROVIDER REACHED != CAPABILITY DELIVERED',
                          paga['NOTA'],
                          'a rota e PARTIAL e a nota nao diz onde ela para')

    def test_3_a_politica_da_rota_paga_nao_mudou(self):
        rotas = (mz.MATRIZ.get(PLAT) or {}).get(cap.da_matriz(CAPAC)) or []
        paga = next(r for r in rotas if r['ROTA'] == ay.ROTA_TRANSCRICAO)
        self.assertEqual(paga['PERMITIDA'], 'CONDICIONAL')
        self.assertEqual(paga['CLASSE'], 'APIFY')


class OCaminhoEOCanonicoInteiro(unittest.TestCase):

    def test_4_executor_router_adapter_e_dono_pago(self):
        f = _Falsa(texto=_texto_real())
        objetos, trace = _colher(f)
        self.assertEqual(trace.get('RESULT'), 'OK')
        self.assertEqual(trace.get('ROUTE'), ay.ROTA_TRANSCRICAO)
        self.assertEqual(trace.get('ROUTE_CLASS'), 'APIFY')
        self.assertEqual(trace.get('PROVIDER_USED'), 'APIFY')
        self.assertTrue(trace.get('PAID_PROVIDER_USED'))
        med = (trace.get('ROUTER_RECORD') or {}).get('MEDIDA') or {}
        self.assertEqual(med.get('IMPLEMENTACAO'), 'coleta/coletor.py')
        self.assertEqual(len(objetos), 1)

    def test_5_o_adaptador_nao_fala_com_a_apify_por_fora_do_dono(self):
        fonte = _fonte('coleta/adaptador_youtube.py')
        fn = next(n for n in ast.walk(ast.parse(fonte))
                  if isinstance(n, ast.FunctionDef) and n.name == 'youtube_legenda_paga')
        nomes = {getattr(n.func, 'attr', None) or getattr(n.func, 'id', None)
                 for n in ast.walk(fn) if isinstance(n, ast.Call)}
        for proibido in ('_curl', 'urlopen', 'run', 'Popen', 'buscar'):
            self.assertNotIn(proibido, nomes,
                             'o adaptador passou a falar com a rede por fora')
        texto = ast.get_source_segment(fonte, fn) or ''
        self.assertNotIn('api.apify.com', texto)
        self.assertNotIn('maxTotalChargeUsd', texto)

    def test_6_o_executor_nao_conhece_o_id_do_ator(self):
        fonte = _fonte('coleta/scrap_executor.py')
        self.assertNotIn(ay.ATOR_TRANSCRICAO, fonte)
        self.assertNotIn('pintostudio', fonte)

    def test_7_o_router_nao_conhece_o_id_do_ator(self):
        self.assertNotIn('pintostudio', _fonte('coleta/social_rotas.py'))


class UmSoPOSTeNenhumSegundo(unittest.TestCase):
    """MAX_PROVIDER_START_POSTS = 1 — e ele vence a taxonomia de falha."""

    def test_8_uma_chamada_ao_dono_pago_sem_ciclo(self):
        fonte = _fonte('coleta/adaptador_youtube.py')
        fn = next(n for n in ast.walk(ast.parse(fonte))
                  if isinstance(n, ast.FunctionDef) and n.name == 'youtube_legenda_paga')
        chamadas = [n for n in ast.walk(fn) if isinstance(n, ast.Call)
                    and getattr(n.func, 'attr', None) == 'executar']
        self.assertEqual(len(chamadas), 1)
        ciclos = [n for n in ast.walk(fn) if isinstance(n, (ast.For, ast.While))
                  and any(isinstance(x, ast.Call)
                          and getattr(x.func, 'attr', None) == 'executar'
                          for x in ast.walk(n))]
        self.assertEqual(ciclos, [], 'nasceu um ciclo a volta da compra')

    def test_9_a_rota_nao_roda_chaves(self):
        fonte = _fonte('coleta/adaptador_youtube.py')
        fn = next(n for n in ast.walk(ast.parse(fonte))
                  if isinstance(n, ast.FunctionDef) and n.name == 'youtube_legenda_paga')
        texto = ast.get_source_segment(fonte, fn) or ''
        self.assertIn('chaves[0]', texto,
                      'a rota paga passou a escolher chave de outra maneira')
        self.assertNotIn('for pos', texto)
        self.assertNotIn('enumerate(chaves', texto)

    def test_10_um_POST_e_so_um_chega_ao_provider(self):
        f = _Falsa(texto=_texto_real())
        _o, _t = _colher(f)
        self.assertEqual(len(f.posts), 1)

    def test_11_nao_ha_ator_de_reserva_nesta_rota(self):
        fonte = _fonte('coleta/adaptador_youtube.py')
        fn = next(n for n in ast.walk(ast.parse(fonte))
                  if isinstance(n, ast.FunctionDef) and n.name == 'youtube_legenda_paga')
        texto = ast.get_source_segment(fonte, fn) or ''
        self.assertNotIn('_ALT', texto, 'entrou um segundo ator na rota paga')

    def test_12_um_so_alvo_e_a_entrada_e_singular(self):
        f = _Falsa(texto=_texto_real())
        _o, _t = _colher(f)
        entrada = f.posts[0]['entrada']
        self.assertEqual(sorted(entrada), ['videoUrl'],
                         'a entrada do ator deixou de ser a do contrato de hoje')
        self.assertNotIn('videoUrls', entrada)
        self.assertEqual(entrada['videoUrl'], ALVO_URL)


class OsDoisTetosNaRotaPaga(unittest.TestCase):

    def test_13_o_cap_do_provider_cabe_no_teto_e_no_saldo(self):
        f = _Falsa(texto=_texto_real())
        _o, t = _colher(f)
        self.assertIsNotNone(f.posts[0]['cap'])
        self.assertLessEqual(f.posts[0]['cap'], TETO_USD)
        self.assertLessEqual(f.posts[0]['cap'],
                             t['FINANCIAL_BUDGET_AUTHORIZED_USD'])

    def test_14_saldo_zero_nao_compra(self):
        f = _Falsa(texto=_texto_real())
        _o, t = _colher(f, gasto=0.0)
        self.assertEqual(f.posts, [])
        self.assertEqual(t.get('RESULT'), 'FINANCIAL_BUDGET_EXHAUSTED')

    def test_15_sem_teto_declarado_o_ensaio_pago_nao_comeca(self):
        f = _Falsa(texto=_texto_real())
        _o, t = _colher(f, gasto=None)
        self.assertEqual(f.posts, [])
        self.assertEqual(t.get('RESULT'), 'PAID_TRIAL_WITHOUT_FINANCIAL_BUDGET')

    def test_16_o_teto_de_rede_cobre_uma_corrida_e_recusa_a_mais(self):
        f = _Falsa(texto=_texto_real())
        _o, t = _colher(f)
        usados = t['NETWORK_REQUESTS_USED']
        self.assertLessEqual(usados, TETO_REDE)
        self.assertEqual(usados, len(f.posts) + len(f.polls)
                         + len(f.datasets) + len(f.kv))

    def test_17_teto_de_rede_zero_nao_deixa_o_POST_sair(self):
        f = _Falsa(texto=_texto_real())
        _o, t = _colher(f, rede=0)
        self.assertEqual(f.posts, [])
        self.assertEqual(t.get('RESULT'), 'NETWORK_BUDGET_EXHAUSTED')

    def test_18_a_corrida_lenta_continua_finita(self):
        f = _Falsa(texto=_texto_real(), terminal=False)
        _o, t = _colher(f)
        self.assertLessEqual(len(f.polls), 1,
                             '`wait` deixou de limitar as consultas')
        self.assertEqual(len(f.posts), 1)
        self.assertLessEqual(t['NETWORK_REQUESTS_USED'], TETO_REDE)


class AAutorizacaoNaoEOOrcamento(unittest.TestCase):

    def test_19_sem_permitir_pago_nao_compra(self):
        f = _Falsa(texto=_texto_real())
        _o, t = _colher(f, permitir_pago=False)
        self.assertEqual(f.posts, [])
        self.assertEqual(t['ROUTER_RECORD']['ESTADO_ORIGINAL'], 'PAID_ROUTE_REFUSED')

    def test_20_motivo_fora_do_vocabulario_nao_compra(self):
        f = _Falsa(texto=_texto_real())
        _o, t = _colher(f, motivo='a Apify ja estava configurada')
        self.assertEqual(f.posts, [])
        self.assertEqual(t['ROUTER_RECORD']['ESTADO_ORIGINAL'], 'PAID_ROUTE_REFUSED')

    def test_21_o_motivo_desta_rota_e_canonico(self):
        self.assertIn(MOTIVO, mz.MOTIVOS_PAGOS)
        f = _Falsa(texto=_texto_real())
        _o, t = _colher(f)
        self.assertEqual(t['ROUTER_RECORD']['MOTIVO_PAGO'], MOTIVO)


class ACredencialEUmPortaoLivre(unittest.TestCase):
    """Sem chave não há compra para autorizar — e a sonda não gasta nada."""

    def test_22_a_sonda_le_a_chave_paga_e_nao_a_do_youtube(self):
        fonte = _fonte('coleta/adaptador_youtube.py')
        fn = next(n for n in ast.walk(ast.parse(fonte))
                  if isinstance(n, ast.FunctionDef)
                  and n.name == 'credencial_paga_presente')
        texto = ast.get_source_segment(fonte, fn) or ''
        self.assertIn('apify_pool', texto)
        self.assertNotIn('youtube_oficial', texto)

    def test_23_sem_chave_nada_e_comprometido(self):
        f = _Falsa(texto=_texto_real())
        _o, t = _colher(f, com_chave=False)
        self.assertEqual(f.posts, [])
        self.assertEqual(t.get('RESULT'), 'CREDENTIAL_MISSING')

    def test_23b_a_rota_recusa_sozinha_mesmo_sem_a_sonda(self):
        """Dois portões, e cada um tem de segurar sozinho.

        `test_23` mede o `CHECK`: a sonda gratuita recusa antes de tudo. Mas se
        alguém desligar a sonda, a rota ainda não pode comprar sem chave — senão
        o portão seria um só, disfarçado de dois.

            UM PORTAO QUE SO FUNCIONA PORQUE OUTRO O PRECEDE NAO E UM PORTAO.
        """
        f = _Falsa(texto=_texto_real())
        antes = dict(reg._MAPA[(PLAT, CAPAC)])
        pool_antes = ap.pool
        reg._MAPA[(PLAT, CAPAC)] = dict(antes, PRONTO=None)
        ap.pool = lambda env=None: []
        try:
            with _Cenario(f, com_chave=False):
                with ct.orcamento_financeiro(TETO_USD) as orc:
                    _o, t = sx.COLLECT(
                        platform=PLAT, capability=CAPAC, run_id='t-sem-sonda',
                        modo=sx.TRIAL, permitir_pago=True, motivo_pago=MOTIVO,
                        video_id=ALVO, teto_de_rede=TETO_REDE)
        finally:
            reg._MAPA[(PLAT, CAPAC)] = antes
            ap.pool = pool_antes
        self.assertEqual(f.posts, [], 'a rota comprou sem credencial nenhuma')
        self.assertEqual(t.get('RESULT'), 'CREDENTIAL_MISSING')
        self.assertEqual(orc.restante, TETO_USD)

    def test_24_e_o_saldo_continua_inteiro(self):
        f = _Falsa(texto=_texto_real())
        _o, t = _colher(f, com_chave=False)
        self.assertEqual(t['FINANCIAL_BUDGET_REMAINING_USD'], TETO_USD)
        self.assertEqual(t['FINANCIAL_BUDGET_UNKNOWN_USD'], 0.0)

    def test_25_a_sonda_nunca_devolve_a_chave(self):
        ap_antes = ap.pool
        ap.pool = lambda env=None: ['apify_api_SEGREDO_QUE_NAO_PODE_SAIR']
        try:
            ha, estado = ay.credencial_paga_presente()
        finally:
            ap.pool = ap_antes
        self.assertIs(ha, True)
        self.assertNotIn('SEGREDO', str(estado))


class ORawNasceAntesDoNormalizado(unittest.TestCase):

    def test_26_o_raw_do_provider_e_preservado_com_impressao_digital(self):
        f = _Falsa(texto=_texto_real())
        objetos, t = _colher(f)
        med = (t.get('ROUTER_RECORD') or {}).get('MEDIDA') or {}
        self.assertEqual(med.get('SCRAP_RAW_STATE'), 'PRESERVED')
        self.assertTrue(med.get('SCRAP_RAW_SHA256'))
        self.assertEqual(objetos[0]['RAW_REFERENCE'],
                         med.get('SCRAP_RAW_REFERENCE'))

    def test_27_o_raw_e_escrito_antes_de_o_manifesto_fechar(self):
        fonte = _fonte('coleta/coletor.py')
        fn = next(n for n in ast.walk(ast.parse(fonte))
                  if isinstance(n, ast.FunctionDef) and n.name == 'executar')
        grava = fecha = None
        for i, no in enumerate(fn.body):
            t = ast.dump(no)
            if grava is None and 'raw_sha' in t and 'sha256' in t:
                grava = i
            if fecha is None and "attr='novo_run'" in t:
                fecha = i
        self.assertIsNotNone(grava, 'o RAW deixou de ser gravado')
        self.assertIsNotNone(fecha, 'o manifesto deixou de nascer')
        self.assertLess(grava, fecha, 'o normalizado passou a nascer antes do RAW')

    def test_28_e_nao_se_chama_a_isto_preservacao_forward(self):
        f = _Falsa(texto=_texto_real())
        _o, t = _colher(f)
        self.assertNotIn('CANONICAL_FORWARD_PRESERVATION', t)


class AEspecieDoTextoNaoSeInventa(unittest.TestCase):
    """CAPTION != TRANSCRIPT != ASR."""

    def test_29_a_especie_nao_e_declarada_pelo_provider(self):
        f = _Falsa(texto=_texto_real())
        objetos, _t = _colher(f)
        self.assertEqual(objetos[0]['RAW']['SPECIES'], 'NOT_DECLARED_BY_PROVIDER')
        self.assertIs(objetos[0]['RAW']['TIMESTAMPS'], False)

    def test_30_a_lingua_nao_e_inventada(self):
        f = _Falsa(texto=_texto_real())
        objetos, _t = _colher(f)
        self.assertIn(objetos[0]['LANGUAGE'], ('UNKNOWN', 'NÃO SEI', 'NAO SEI'))

    def test_31_o_ator_devolve_tres_campos_medidos_no_bruto(self):
        d = json.load(gzip.open(os.path.join(RAIZ, BYTES), 'rt', encoding='utf-8'))
        self.assertTrue(d)
        for it in d[:5]:
            self.assertEqual(sorted(it), ['chars', 'transcript', 'url'])

    def test_32_pedida_e_vazia_e_um_estado_nao_uma_ausencia(self):
        f = _Falsa(itens=[{'url': ALVO_URL, 'transcript': '', 'chars': 0}])
        objetos, t = _colher(f)
        self.assertEqual(len(objetos), 1, 'um item vazio virou ausencia de item')
        self.assertIsNone(objetos[0]['TEXT'])
        self.assertIs(objetos[0]['RAW']['TRANSCRIPT_PRESENT'], False)
        self.assertNotEqual(t.get('RESULT'), 'ZERO_RESULTS')


class OCustoNaoMente(unittest.TestCase):

    def test_33_o_custo_lido_nao_se_diz_liquidado(self):
        f = _Falsa(texto=_texto_real(), custo=0.01)
        _o, t = _colher(f)
        self.assertEqual(t.get('COST_STATE'), 'READ_NOT_SETTLED')
        self.assertEqual(t['FINANCIAL_BUDGET_ACTUAL_USD'], 0.01)

    def test_34_custo_ausente_nao_vira_zero(self):
        f = _Falsa(texto=_texto_real(), custo=None)
        _o, t = _colher(f)
        self.assertEqual(t.get('COST_STATE'), 'UNKNOWN')
        self.assertIsNone(t.get('ACTUAL_COST_USD'))
        self.assertEqual(t['FINANCIAL_BUDGET_ACTUAL_USD'], 0.0)
        self.assertGreater(t['FINANCIAL_BUDGET_UNKNOWN_USD'], 0.0)

    def test_34b_post_ambiguo_nao_se_le_como_NOT_RUN(self):
        """O caso mais perigoso: o POST caiu e a compra pode ter acontecido.

            NOT_RUN != UNKNOWN.
            POTENTIAL COMMITMENT != NOTHING HAPPENED.
        """
        class Cai(_Falsa):
            def __call__(s, cmd, **k):
                if '-X' in cmd and cmd[cmd.index('-X') + 1] == 'POST':
                    s.posts.append({'cap': s._cap(cmd[-1]), 'entrada': None,
                                    'url': cmd[-1]})
                    return _Resultado('', rc=52)
                return _Falsa.__call__(s, cmd, **k)

        f = Cai(texto=_texto_real())
        _o, t = _colher(f)
        self.assertEqual(len(f.posts), 1, 'o POST foi repetido')
        self.assertEqual(t.get('COST_STATE'), 'UNKNOWN')
        self.assertNotEqual(t.get('COST_STATE'), 'NOT_RUN')
        self.assertIsNone(t.get('ACTUAL_COST_USD'))
        self.assertEqual(t['FINANCIAL_BUDGET_UNKNOWN_USD'], TETO_USD)
        self.assertEqual(t['FINANCIAL_BUDGET_REMAINING_USD'], 0.0)

    def test_35_o_token_nao_aparece_no_rasto(self):
        f = _Falsa(texto=_texto_real())
        objetos, t = _colher(f)
        for corpo in (json.dumps(t, default=str), json.dumps(objetos, default=str)):
            self.assertNotIn('TOKEN_DE_MENTIRA', corpo)
            self.assertNotIn('apify_api_', corpo)


class OAlvoVeioDoAcervo(unittest.TestCase):

    def test_36_a_sentinela_tem_corrida_e_texto_historicos(self):
        h = _historico()
        self.assertTrue(h, 'a sentinela historica desapareceu do acervo')
        self.assertEqual(h.get('APIFY_ACTOR'), ay.ATOR_TRANSCRICAO)
        self.assertEqual(h.get('TRANSCRIPT_AVAILABLE'), 'YES')
        self.assertGreater(len(h.get('TRANSCRIPT') or ''), 1000)

    def test_37_e_o_envelope_aponta_para_o_mesmo_alvo(self):
        f = _Falsa(texto=_texto_real())
        objetos, _t = _colher(f)
        self.assertEqual(objetos[0]['NATIVE_ID'], ALVO)
        self.assertEqual(objetos[0]['URL'], _historico().get('SOURCE_URL'))


class OGateVemAntesDoGasto(unittest.TestCase):

    def test_38_a_prova_imprime_o_estado_antes_de_gastar(self):
        fonte = _fonte('provas/primeira_rota_paga.py')
        self.assertIn('READY_TO_SPEND', fonte)
        self.assertIn('credencial_paga_presente', fonte)
        self.assertIn('ct.subprocess.run', fonte,
                      'a prova passou a substituir algo acima do gate')

    def test_39_a_prova_nao_chama_o_dono_pago_diretamente(self):
        fonte = _fonte('provas/primeira_rota_paga.py')
        arv = ast.parse(fonte)
        diretas = [n for n in ast.walk(arv) if isinstance(n, ast.Call)
                   and getattr(n.func, 'attr', None) == 'executar'
                   and getattr(getattr(n.func, 'value', None), 'id', None) == 'ct']
        self.assertEqual(diretas, [],
                         'a prova passou a chamar coletor.executar por fora do SCRAP')

    def test_40_a_rota_paga_tem_sonda_de_prontidao(self):
        r = reg.registados()[(PLAT, CAPAC)]
        self.assertIsNotNone(r['PRONTO'], 'a rota paga ficou sem sonda gratuita')
        self.assertIsNotNone(r['ROTA'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
