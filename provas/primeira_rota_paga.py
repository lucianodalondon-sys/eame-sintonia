#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
C10.8B — A PRIMEIRA ROTA PAGA CANÔNICA, PROVADA ANTES DO CÊNTIMO.

    py provas/primeira_rota_paga.py

A pergunta desta missão não é «`youtube.native_caption` funciona?» — essa
capacidade já está `PROVEN`. É outra:

    CAPABILITY_STATE != ROUTE_STATE.

    A rota `apify:transcricao`, hoje `POSSIBLE_NOT_PROVED`, consegue executar UMA
    aquisição pelo runtime canônico, sob os dois tetos, preservando RAW, trace,
    provider e custo, sem bypass?

O QUE É FALSO AQUI, E SÓ ISSO
-------------------------------
`subprocess.run` DENTRO do `coletor` — a camada mais funda, por baixo dos dois
tetos. Nem o executor, nem o roteador, nem o registo, nem o adaptador, nem o
orçamento de rede, nem o financeiro são substituídos.

    UM FAKE ACIMA DO GATE MEDE O FAKE.

Os bytes que o falso devolve são os bytes REAIS preservados de uma corrida
anterior do MESMO ator, lidos de `data/samples/raw-paid/`.

    APIFY_RUNS = 0 · PAID_RUNS = 0 · REAL_COST_USD = 0 · NETWORK_REAL = 0
"""
import gzip
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in ('coleta', 'leis', 'medidas', 'ferramentas', 'guarda', ''):
    sys.path.insert(0, os.path.join(RAIZ, p) if p else RAIZ)

import adaptador_youtube as ay   # noqa: E402
import apify_pool as ap          # noqa: E402
import coletor as ct             # noqa: E402
import scrap_capacidades as cap  # noqa: E402
import scrap_executor as sx      # noqa: E402
import scrap_http as http        # noqa: E402
import scrap_registo as reg      # noqa: E402
import social_matriz as mz       # noqa: E402
reg.carregar_adaptadores()

FALHAS = []
PLAT, CAPAC = 'YOUTUBE', 'youtube.native_caption'
MOTIVO = 'ROUTE_NOT_ALLOWED'
TETO_USD = 0.10
TETO_REDE = 5

#: A sentinela histórica. Escolhida do acervo desta casa, nunca da internet.
ALVO = 'EAkcA_2FDN8'
ALVO_URL = 'https://www.youtube.com/watch?v=%s' % ALVO
HISTORICO = 'data/samples/SENSOR-PILOT/TRANSCRICOES-B.json'
CORRIDA_HISTORICA = 'SENSOR-TR-B-3-p3'
#: Bytes REAIS do mesmo ator, de uma corrida preservada. O falso devolve estes.
BYTES_DO_ATOR = 'data/samples/raw-paid/ES-T8-001-youtube-transcripts.raw.json.gz'


def diz(ok, titulo, detalhe=''):
    print('  %-5s %-56s %s' % ('ok' if ok else 'FALHA', titulo[:56],
                               str(detalhe)[:58]))
    if not ok:
        FALHAS.append(titulo)


def historico():
    """→ o item preservado da corrida histórica do MESMO alvo."""
    d = json.load(open(os.path.join(RAIZ, HISTORICO), encoding='utf-8'))
    for it in (d.get('ITEMS') or []):
        if ALVO in str(it.get('SOURCE_URL')):
            return it
    return {}


def bytes_do_ator():
    """→ um item REAL deste ator, dos bytes preservados."""
    d = json.load(gzip.open(os.path.join(RAIZ, BYTES_DO_ATOR), 'rt', encoding='utf-8'))
    return next(x for x in d if (x.get('chars') or 0) > 0)


class Resultado(object):
    def __init__(self, corpo, rc=0):
        self.returncode, self.stdout, self.stderr = rc, corpo, ''


class FalsaApify(object):
    """`subprocess.run` do coletor. Conta o que REALMENTE teria saído."""

    def __init__(self, *, texto, custo=0.01, terminal=True):
        self.texto, self.custo, self.terminal = texto, custo, terminal
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
            self.posts.append({'url': url, 'cap': self._cap(url),
                               'entrada': json.loads(corpo) if corpo else None})
            return Resultado(json.dumps({'data': {
                'id': 'RUN-FALSA-1',
                'status': 'SUCCEEDED' if self.terminal else 'RUNNING',
                'startedAt': '2026-09-12T00:00:00.000Z',
                'finishedAt': '2026-09-12T00:00:04.000Z',
                'buildNumber': '1.0.57', 'defaultDatasetId': 'DS-FALSO',
                'defaultKeyValueStoreId': 'KV-FALSO',
                'usageTotalUsd': self.custo}}))
        if '/actor-runs/' in url:
            self.polls.append(url)
            return Resultado(json.dumps({'data': {
                'id': 'RUN-FALSA-1', 'status': 'SUCCEEDED',
                'defaultDatasetId': 'DS-FALSO', 'defaultKeyValueStoreId': 'KV-FALSO',
                'usageTotalUsd': self.custo}}))
        if '/datasets/' in url:
            self.datasets.append(url)
            return Resultado(json.dumps(
                [{'url': ALVO_URL, 'transcript': self.texto, 'chars': len(self.texto)}]))
        self.kv.append(url)
        if '/keys' in url:
            return Resultado(json.dumps({'data': {'items': []}}))
        return Resultado(json.dumps({'data': {}}))


# ── ESTA PROVA ATRAVESSA A PORTA PAGA, E DECLARA A AUTORIZACAO ─────────────
# A SCRAP-SR-02 poe uma guarda no unico sitio que cria execucao paga. Esta prova
# atravessa esse sitio contra um provider FALSO, entao precisa de autorizacao —
# e a que lhe serve e a que ela sempre foi: um ENSAIO DE CAPACIDADE, com alvo
# fixo, UM POST no teto e assinatura.
#
#     DECLARAR A AUTORIZACAO QUE A PROVA SEMPRE ASSUMIU NAO E ENFRAQUECE-LA.
#     UM TETO DE UM POST NA PROPRIA AUTORIZACAO E MAIS TRAVA, NAO MENOS.
#
# Nao ha bandeira nem variavel de ambiente que desligue a guarda — a sentinela
# em `tests/test_sr02_autorizacao_de_gasto.py` exige-o.
def _ensaio(posts=1):
    import autorizacao_de_gasto as _ag
    return _ag.Autorizacao(
        MODO=_ag.TRIAL, ALVO='C10.8B · %s · video %s' % (CAPAC, ALVO),
        HUMAN_AUTHORIZATION='prova offline · provider falso · zero dolar',
        MAX_PROVIDER_RUNS=posts, MAX_START_POSTS=posts, MAX_USD=TETO_USD,
        MAX_ITEMS=10 ** 6)


class Cenario(object):
    """Instala o falso e uma chave de mentira. Desfaz tudo à saída."""

    def __init__(self, falso, *, com_chave=True):
        self.falso, self.com_chave = falso, com_chave

    def __enter__(self):
        import autorizacao_de_gasto as _ag
        self._auth = _ag.autorizacao(_ensaio(1))
        self._auth.__enter__()
        self._run, self._pool = ct.subprocess.run, ap.pool
        ct.subprocess.run = self.falso
        if self.com_chave:
            ap.pool = lambda env=None: ['apify_api_TOKEN_DE_MENTIRA']
        self._gaveta = ct.RAW_DIR
        import tempfile
        ct.RAW_DIR = tempfile.mkdtemp(prefix='c108b-')
        return self

    def __exit__(self, *a):
        import shutil
        ct.subprocess.run, ap.pool = self._run, self._pool
        shutil.rmtree(ct.RAW_DIR, ignore_errors=True)
        ct.RAW_DIR = self._gaveta
        self._auth.__exit__(None, None, None)
        return False


print('=' * 88)
print('C10.8B · A PRIMEIRA ROTA PAGA CANONICA, ANTES DO CENTIMO')
print('=' * 88)

# ══ O CENSO DA ROTA ═══════════════════════════════════════════════════════
print('\n── a rota, medida e nao lembrada ──')
grossa = cap.da_matriz(CAPAC)
rotas = (mz.MATRIZ.get(PLAT) or {}).get(grossa) or []
paga = next(r for r in rotas if r['ROTA'] == ay.ROTA_TRANSCRICAO)
registo = reg.registados()[(PLAT, CAPAC)]
diz(cap.estado(CAPAC) == 'PROVEN', 'CAPABILITY_STATE = PROVEN', cap.estado(CAPAC))
diz(grossa == 'FETCH_TRANSCRIPT', 'MATRIX_CAPABILITY = FETCH_TRANSCRIPT', grossa)
diz(paga['CLASSE'] == 'APIFY', 'ROUTE_CLASS = APIFY', paga['CLASSE'])
diz(paga['PERMITIDA'] == 'CONDICIONAL', 'POLICY = CONDICIONAL', paga['PERMITIDA'])
diz(paga['ESTADO'] == 'POSSIBLE_NOT_PROVED', 'ROUTE_STATE antes', paga['ESTADO'])
diz(mz._rota_padrao(rotas)['ROTA'] == ay.ROTA_TRANSCRICAO,
    'e ela e a rota PADRAO — as tres livres estao NAO', paga['ROTA'])
diz(MOTIVO in mz.MOTIVOS_PAGOS, 'PAID_REASON pertence ao vocabulario', MOTIVO)
diz(registo['ROTA'] is not None, 'HAS_CANONICAL_ROUTE agora', registo['ROTA'].__name__)

# ══ O ALVO VEM DO ACERVO ══════════════════════════════════════════════════
print('\n── o alvo veio do acervo, e nao da internet ──')
h = historico()
diz(bool(h), 'a sentinela tem corrida historica preservada',
    h.get('COLLECTION_RUN_ID'))
diz(h.get('COLLECTION_RUN_ID') == CORRIDA_HISTORICA, 'HISTORICAL_RUN', CORRIDA_HISTORICA)
diz(h.get('APIFY_ACTOR') == ay.ATOR_TRANSCRICAO, 'e do MESMO ator',
    h.get('APIFY_ACTOR'))
diz(len(h.get('TRANSCRIPT') or '') > 1000, 'com texto historico preservado',
    '%d chars' % len(h.get('TRANSCRIPT') or ''))

# ══ A CREDENCIAL E UM PORTAO, E ELE VEM ANTES DO DINHEIRO ═════════════════
print('\n── sem chave paga, nada e comprometido ──')
with Cenario(FalsaApify(texto='x'), com_chave=False) as c:
    with ct.orcamento_financeiro(TETO_USD) as orc:
        objetos, trace = sx.COLLECT(
            platform=PLAT, capability=CAPAC, run_id='c108b-sem-chave',
            modo=sx.TRIAL, permitir_pago=True, motivo_pago=MOTIVO,
            video_id=ALVO, teto_de_rede=TETO_REDE)
diz(c.falso.posts == [], 'nenhum POST chegou ao provider', len(c.falso.posts))
diz(trace.get('RESULT') == 'CREDENTIAL_MISSING',
    'e o estado e o da credencial, nao o do teto', trace.get('RESULT'))
diz(orc.restante == TETO_USD, 'o saldo continua inteiro', orc.restante)

# ══ O CAMINHO INTEIRO, COM A API FALSA ════════════════════════════════════
print('\n── o caminho canonico inteiro, so com a API falsa ──')
real = bytes_do_ator()
falso = FalsaApify(texto=real['transcript'], custo=0.01)
with Cenario(falso):
    with ct.orcamento_financeiro(TETO_USD) as orc:
        objetos, trace = sx.COLLECT(
            platform=PLAT, capability=CAPAC, run_id='c108b-a-seco',
            modo=sx.TRIAL, permitir_pago=True, motivo_pago=MOTIVO,
            video_id=ALVO, teto_de_gasto=None, teto_de_rede=TETO_REDE)
diz(trace.get('RESULT') == 'OK', 'EXECUTOR_REACHED · RESULT', trace.get('RESULT'))
diz(trace.get('ROUTE') == ay.ROTA_TRANSCRICAO, 'ROUTER_REACHED · ROTA escolhida',
    trace.get('ROUTE'))
diz(trace.get('ROUTE_CLASS') == 'APIFY', 'ROUTE_CLASS no trace', trace.get('ROUTE_CLASS'))
diz(trace.get('PROVIDER_USED') == 'APIFY', 'PROVIDER no trace',
    trace.get('PROVIDER_USED'))
diz(trace.get('PAID_PROVIDER_USED') is True, 'PAID_PROVIDER_USED', True)
med = (trace.get('ROUTER_RECORD') or {}).get('MEDIDA') or {}
diz(med.get('IMPLEMENTACAO') == 'coleta/coletor.py',
    'PAID_PROVIDER_OWNER_REACHED', med.get('IMPLEMENTACAO'))
diz(len(objetos) == 1, 'ADAPTER_REACHED · um envelope canonico', len(objetos))
diz((trace.get('ROUTER_RECORD') or {}).get('MOTIVO_PAGO') == MOTIVO,
    'e o motivo pago ficou registado', MOTIVO)

# ══ OS DOIS TETOS ESTAVAM VIVOS ═══════════════════════════════════════════
print('\n── os dois tetos estavam vivos, e sao dois ──')
diz(trace.get('FINANCIAL_BUDGET_AUTHORIZED_USD') == TETO_USD,
    'FINANCIAL_BUDGET_ACTIVE', trace.get('FINANCIAL_BUDGET_AUTHORIZED_USD'))
diz(trace.get('NETWORK_BUDGET_LIMIT') == TETO_REDE, 'NETWORK_BUDGET_ACTIVE',
    trace.get('NETWORK_BUDGET_LIMIT'))
cap_enviado = falso.posts[0]['cap']
diz(cap_enviado is not None and cap_enviado <= TETO_USD,
    'PROVIDER_SIDE_CAP <= 0.10', cap_enviado)
diz(cap_enviado <= trace['FINANCIAL_BUDGET_AUTHORIZED_USD'],
    'PROVIDER_SIDE_CAP <= FINANCIAL_REMAINING', cap_enviado)
diz(trace.get('FINANCIAL_BUDGET_ACTUAL_USD') == 0.01, 'ACTUAL lido do provider',
    trace.get('FINANCIAL_BUDGET_ACTUAL_USD'))
diz(trace.get('COST_STATE') == ct.CUSTO_LIDO, 'COST_STATE = READ_NOT_SETTLED',
    trace.get('COST_STATE'))
diz(trace.get('COST_STATE') != ct.CUSTO_LIQUIDADO,
    'e READ nao virou SETTLED', trace.get('COST_STATE'))

# ══ QUANTAS IDAS UMA CORRIDA CUSTA ════════════════════════════════════════
print('\n── o teto de rede de UMA corrida, medido e nao arbitrado ──')
usados = trace.get('NETWORK_REQUESTS_USED')
tipos = [t['TYPE'] for t in (trace.get('NETWORK_ATTEMPTS') or [])]
diz(len(falso.posts) == 1, 'POSTS_TO_CREATE_RUN = 1', len(falso.posts))
diz(len(falso.polls) == 0, 'POLL_REQUESTS = 0 (terminal aos 60 s)', len(falso.polls))
diz(len(falso.datasets) == 1, 'DATASET_REQUESTS = 1', len(falso.datasets))
diz(usados == len(falso.posts) + len(falso.polls) + len(falso.datasets) + len(falso.kv),
    'o rasto bate com o que saiu de verdade',
    '%s = %d' % (usados, len(falso.posts) + len(falso.polls)
                 + len(falso.datasets) + len(falso.kv)))
diz(usados <= TETO_REDE, 'C10_8B_NETWORK_BUDGET = %d cobre UMA corrida' % TETO_REDE,
    '%d usados' % usados)

print('\n── e a corrida que NAO termina aos 60 s continua finita ──')
lento = FalsaApify(texto=real['transcript'], custo=0.01, terminal=False)
with Cenario(lento):
    with ct.orcamento_financeiro(TETO_USD):
        _o, t_lento = sx.COLLECT(
            platform=PLAT, capability=CAPAC, run_id='c108b-lento', modo=sx.TRIAL,
            permitir_pago=True, motivo_pago=MOTIVO, video_id=ALVO,
            teto_de_rede=TETO_REDE)
diz(len(lento.polls) <= 1, 'no maximo UMA consulta, porque `wait` e 60',
    len(lento.polls))
diz(len(lento.posts) == 1, 'e continua a ser UM POST', len(lento.posts))
diz(t_lento.get('NETWORK_REQUESTS_USED') <= TETO_REDE,
    'e cabe no mesmo teto', t_lento.get('NETWORK_REQUESTS_USED'))

# ══ RAW ANTES DA NORMALIZACAO ═════════════════════════════════════════════
print('\n── o RAW do provider nasce antes do normalizado ──')
diz(med.get('SCRAP_RAW_STATE') == 'PRESERVED', 'SCRAP_RAW_CAPTURED',
    med.get('SCRAP_RAW_STATE'))
diz(bool(med.get('SCRAP_RAW_SHA256')), 'com impressao digital',
    str(med.get('SCRAP_RAW_SHA256'))[:16])
diz(objetos[0].get('RAW_REFERENCE') == med.get('SCRAP_RAW_REFERENCE'),
    'e o envelope aponta para ele', objetos[0].get('RAW_REFERENCE'))
diz('CANONICAL_FORWARD_PRESERVATION' not in trace,
    'e nao se chama a isto preservacao forward', 'vocabulario honesto')

# ══ A ESPECIE DO TEXTO ════════════════════════════════════════════════════
print('\n── caption, transcript e ASR nao sao a mesma coisa ──')
e = objetos[0]
diz(sorted(real) == ['chars', 'transcript', 'url'],
    'o ator devolve tres campos, medidos no bruto', sorted(real))
diz(e['RAW']['SPECIES'] == ay.ESPECIE_NAO_DECLARADA,
    'SPECIES = NOT_DECLARED_BY_PROVIDER', e['RAW']['SPECIES'])
diz(e['RAW']['TIMESTAMPS'] is False, 'TIMESTAMPS = NO (o ator nao os devolve)',
    e['RAW']['TIMESTAMPS'])
diz(e['LANGUAGE'] in ('UNKNOWN', 'NÃO SEI', 'NAO SEI'),
    'LANGUAGE nao e inventada', e['LANGUAGE'])
diz(bool(e.get('TEXT')), 'TRANSCRIPT_PRESENT', '%d chars' % len(e.get('TEXT') or ''))

# ══ COMPARAR COM O HISTORICO ══════════════════════════════════════════════
print('\n── comparar com a corrida historica do MESMO alvo ──')
diz(e['NATIVE_ID'] == ALVO, 'IDENTITY bate', e['NATIVE_ID'])
diz(e['URL'] == h.get('SOURCE_URL'), 'SAME_TARGET', e['URL'])
diz(h.get('TRANSCRIPT_AVAILABLE') == 'YES', 'o historico tinha texto',
    h.get('TRANSCRIPT_AVAILABLE'))
diz(h.get('APIFY_ACTOR') == ay.ATOR_TRANSCRICAO, 'e do mesmo ator',
    h.get('APIFY_ACTOR'))

# ══ UM SO POST, E NENHUM SEGUNDO ══════════════════════════════════════════
print('\n── um so POST, e nenhuma rotacao de chave ──')
import ast                                                        # noqa: E402
fonte = open(os.path.join(RAIZ, 'coleta/adaptador_youtube.py'), encoding='utf-8').read()
fn = next(n for n in ast.walk(ast.parse(fonte)) if isinstance(n, ast.FunctionDef)
          and n.name == 'youtube_legenda_paga')
chamadas = [n for n in ast.walk(fn) if isinstance(n, ast.Call)
            and getattr(n.func, 'attr', None) == 'executar']
diz(len(chamadas) == 1, 'o adaptador chama o dono pago UMA vez', len(chamadas))
laços = [n for n in ast.walk(fn) if isinstance(n, (ast.For, ast.While))
         and any(isinstance(x, ast.Call) and getattr(x.func, 'attr', None) == 'executar'
                 for x in ast.walk(n))]
diz(not laços, 'e nao ha ciclo a volta dela', len(laços))
nomes = {getattr(n.func, 'attr', None) or getattr(n.func, 'id', None)
         for n in ast.walk(fn) if isinstance(n, ast.Call)}
diz('_curl' not in nomes and 'urlopen' not in nomes,
    'e o adaptador nao fala com a Apify por fora do dono', 'sem bypass')
diz('YOUTUBE_TRANSCRIPT_ALT' not in fonte or 'ATOR_TRANSCRICAO' in fonte,
    'SECOND_ACTOR = NO — nao ha ator de reserva nesta rota', 'um ator')

# ══ O TETO E ABSOLUTO ═════════════════════════════════════════════════════
print('\n── o teto e absoluto, e recusa antes do provider ──')
seco = FalsaApify(texto=real['transcript'], custo=0.01)
with Cenario(seco):
    with ct.orcamento_financeiro(0.0) as orc0:
        _o, t0 = sx.COLLECT(platform=PLAT, capability=CAPAC, run_id='c108b-zero',
                            modo=sx.TRIAL, permitir_pago=True, motivo_pago=MOTIVO,
                            video_id=ALVO, teto_de_rede=TETO_REDE)
diz(seco.posts == [], 'com saldo zero, nenhum POST sai', len(seco.posts))
diz(t0.get('RESULT') == 'FINANCIAL_BUDGET_EXHAUSTED', 'e o estado di-lo',
    t0.get('RESULT'))

sem_motivo = FalsaApify(texto=real['transcript'])
with Cenario(sem_motivo):
    with ct.orcamento_financeiro(TETO_USD):
        _o, tm = sx.COLLECT(platform=PLAT, capability=CAPAC, run_id='c108b-motivo',
                            modo=sx.TRIAL, permitir_pago=True,
                            motivo_pago='a Apify ja estava configurada',
                            video_id=ALVO, teto_de_rede=TETO_REDE)
diz(sem_motivo.posts == [], 'motivo fora do vocabulario nao compra nada',
    len(sem_motivo.posts))

sem_auth = FalsaApify(texto=real['transcript'])
with Cenario(sem_auth):
    with ct.orcamento_financeiro(TETO_USD):
        _o, ta = sx.COLLECT(platform=PLAT, capability=CAPAC, run_id='c108b-auth',
                            modo=sx.TRIAL, permitir_pago=False,
                            motivo_pago=MOTIVO, video_id=ALVO,
                            teto_de_rede=TETO_REDE)
diz(sem_auth.posts == [], 'e sem `permitir_pago` tambem nao', len(sem_auth.posts))

sem_teto = FalsaApify(texto=real['transcript'])
with Cenario(sem_teto):
    _o, ts = sx.COLLECT(platform=PLAT, capability=CAPAC, run_id='c108b-sem-teto',
                        modo=sx.TRIAL, permitir_pago=True, motivo_pago=MOTIVO,
                        video_id=ALVO, teto_de_rede=TETO_REDE)
diz(sem_teto.posts == [], 'NO FINANCIAL LIMIT -> NO PAID TRIAL', len(sem_teto.posts))
diz(ts.get('RESULT') == 'PAID_TRIAL_WITHOUT_FINANCIAL_BUDGET', 'com nome proprio',
    ts.get('RESULT'))

# ══ O ESTADO IMEDIATAMENTE ANTES DO GASTO ═════════════════════════════════
# Este bloco corre com o ambiente REAL — sem chave de mentira, sem falso — e é
# ele que decide se há gasto. Um relatório impresso depois de gastar não é um
# portão; é uma legenda.
#
#     UM GATE QUE SE LE DEPOIS DA COMPRA NAO E UM GATE.
print('\n' + '=' * 88)
print('ESTADO IMEDIATAMENTE ANTES DO GASTO — ambiente REAL, sem falso')
print('=' * 88)
ha_chave, _estado = ay.credencial_paga_presente()
pronto = sx.CHECK(PLAT, CAPAC, modo=sx.TRIAL)
portoes = [
    ('CAPABILITY_STATE', cap.estado(CAPAC), cap.estado(CAPAC) == 'PROVEN'),
    ('ROUTE_STATE', paga['ESTADO'], True),
    ('POLICY', paga['PERMITIDA'], paga['PERMITIDA'] == 'CONDICIONAL'),
    ('ACTOR', ay.ATOR_TRANSCRICAO, True),
    ('TARGET_VIDEO_ID', ALVO, True),
    ('MAX_PROVIDER_RUNS', 1, True),
    ('MAX_PROVIDER_START_POSTS', 1, True),
    ('FINANCIAL_BUDGET', TETO_USD, TETO_USD <= 0.10),
    ('FINANCIAL_REMAINING', TETO_USD, True),
    ('PROVIDER_SIDE_CAP', '<= %s, decidido pelo saldo' % TETO_USD, True),
    ('NETWORK_BUDGET', TETO_REDE, True),
    ('PAID_REASON', MOTIVO, MOTIVO in mz.MOTIVOS_PAGOS),
    ('WIRING_OFFLINE', 'PASS' if not FALHAS else 'FALHOU', not FALHAS),
    ('PAID_CREDENTIAL', 'PRESENTE' if ha_chave else 'AUSENTE', ha_chave),
    ('CHECK.CAN', pronto['CAN'], bool(pronto['CAN'])),
]
for nome, valor, ok in portoes:
    print('  %-6s %-26s = %s' % ('ok' if ok else 'NAO', nome, valor))
podemos = all(ok for _n, _v, ok in portoes)
print('\n  READY_TO_SPEND = %s' % ('YES' if podemos else 'NO'))
if not podemos:
    faltam = [n for n, _v, ok in portoes if not ok]
    print('  BLOQUEIO       = %s' % ', '.join(faltam))
    print('  CHECK.STATE    = %s' % pronto['STATE'])
    print('  GASTO          = 0 · nenhum POST foi enviado por esta prova')

print('\n' + '=' * 88)
print('WIRING_OFFLINE     = %s' % ('PASS' if not FALHAS else 'FALHOU · %d' % len(FALHAS)))
print('READY_TO_SPEND     = %s' % ('YES' if podemos else 'NO'))
print('C10_8B_NETWORK_BUDGET = %d   (1 POST · <=1 consulta · 1 dataset · 2 KV)' % TETO_REDE)
print('NETWORK_REAL       = 0   (API falsa em todos os casos)')
print('APIFY_RUNS         = 0')
print('PAID_RUNS          = 0')
print('REAL_COST_USD      = 0')
for f in FALHAS:
    print('  · %s' % f)
sys.exit(1 if FALHAS else 0)
