#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
C10.8A-F — O TETO DE GASTO, PROVADO SEM GASTAR UM CÊNTIMO.

    py provas/orcamento_financeiro.py

A C10.8A-R fechou o primeiro teto: quantos ACESSOS uma execução pode fazer. Este
é o segundo, e mede outra coisa.

    REQUEST COUNT != MONEY.
    NETWORK BUDGET decide SE CABE MAIS UMA IDA.
    FINANCIAL BUDGET decide SE PODEMOS ASSUMIR MAIS EXPOSIÇÃO FINANCEIRA.

O QUE É FALSO AQUI, E SÓ ISSO
-------------------------------
`coletor._curl` — a função que fala com a Apify. O fake fica POR BAIXO do teto e
regista cada `POST` que chegou ao fundo, com o `maxTotalChargeUsd` que ia nele.
Se o runtime deixar passar uma chamada a mais, ou mandar um teto acima do saldo,
é o fake que acusa.

    UM TETO QUE SE MEDE A SI PRÓPRIO MEDE O ESPELHO.

Tudo o resto é o runtime real: `COLLECT` → `social_rotas` → a rota → o
`coletor.executar` verdadeiro, com a reserva, a liquidação e o manifesto.

    APIFY_RUNS = 0 · PAID_RUNS = 0 · REAL_COST_USD = 0 · NETWORK_REAL = 0
"""
import json
import os
import sys
import threading

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in ('coleta', 'leis', 'medidas', 'ferramentas', 'guarda', ''):
    sys.path.insert(0, os.path.join(RAIZ, p) if p else RAIZ)

import autorizacao_de_gasto as ag  # noqa: E402 — a guarda, so o tipo e a porta
import coletor as ct              # noqa: E402  — o dono do dinheiro
import scrap_executor as sx       # noqa: E402
import scrap_registo as reg       # noqa: E402
import social_matriz as mz        # noqa: E402
reg.carregar_adaptadores()

FALHAS = []
PLAT, CAPAC = 'YOUTUBE', 'youtube.native_caption'
ATOR = 'fake~ator-pago-da-prova'
MOTIVO = 'FREE_ROUTE_UNAVAILABLE'


def diz(ok, titulo, detalhe=''):
    print('  %-5s %-56s %s' % ('ok' if ok else 'FALHA', titulo[:56],
                               str(detalhe)[:60]))
    if not ok:
        FALHAS.append(titulo)


# ══════════════════════════════════════════════════════════════════════════
# O PROVIDER FALSO — POR BAIXO DO TETO, E ELE CONTA O QUE SAIU
# ══════════════════════════════════════════════════════════════════════════
class Resultado(object):
    def __init__(self, corpo, rc=0):
        self.returncode, self.stdout, self.stderr = rc, corpo, ''


class FalsoApify(object):
    """Substitui `subprocess.run` DENTRO do coletor — por BAIXO dos dois tetos.

    Trocar `_curl` inteiro poria o fake POR CIMA do gate de rede, e um teto que
    o fake contorna nunca seria medido. O fake tem de ser sempre a camada mais
    funda: o que chega a ele é o que realmente teria saído.

        UM FAKE ACIMA DO GATE MEDE O FAKE.

    `guiao` é a lista de custos (`usageTotalUsd`) que cada POST devolve, por
    ordem. Um elemento `None` significa «a execução nasceu e o custo não veio»;
    uma exceção significa que o POST caiu no transporte.
    """

    def __init__(self, guiao):
        self.guiao = list(guiao)
        self.posts = []            # (actor, maxTotalChargeUsd ou None)
        self.gets = []

    def _teto_da_url(self, url):
        for parte in url.split('?', 1)[-1].split('&'):
            if parte.startswith('maxTotalChargeUsd='):
                return float(parte.split('=', 1)[1])
        return None

    def __call__(self, cmd, **k):
        url = cmd[-1]
        metodo = cmd[cmd.index('-X') + 1] if '-X' in cmd else 'GET'
        if metodo.upper() == 'POST':
            teto = self._teto_da_url(url)
            self.posts.append((url.split('/acts/')[-1].split('/')[0], teto))
            passo = (self.guiao[len(self.posts) - 1]
                     if len(self.guiao) >= len(self.posts) else 0.0)
            if isinstance(passo, Exception):
                # O transporte caiu: `curl` volta sem saida, e o `_curl` real
                # levanta `PostTalvezCriado` sozinho. O fake nao levanta nada —
                # quem decide o que uma queda significa e o runtime.
                return Resultado('', rc=52)
            return Resultado(json.dumps({'data': {
                'id': 'run-%d' % len(self.posts), 'status': 'SUCCEEDED',
                'startedAt': '2026-09-12T00:00:00.000Z',
                'finishedAt': '2026-09-12T00:00:05.000Z',
                'buildNumber': '0.0.1',
                'defaultDatasetId': 'ds-%d' % len(self.posts),
                'usageTotalUsd': passo}}))
        self.gets.append(url)
        if '/datasets/' in url:
            return Resultado(json.dumps([{'id': 'item-1'}]))
        if '/keys' in url:
            return Resultado(json.dumps({'data': {'items': []}}))
        return Resultado(json.dumps({'data': {}}))


class Cenario(object):
    """Instala o provider falso e a rota paga, e desfaz tudo à saída."""

    def __init__(self, guiao, *, teto_da_rota=None, achar_orfa=False):
        self.falso = FalsoApify(guiao)
        self.teto_da_rota = teto_da_rota
        self.achar_orfa = achar_orfa

    def autorizacao(self):
        """A autorizacao humana desta PROVA. Acrescentada na SCRAP-CV-01.

        ⚠️ Desde a convergencia nenhuma compra atravessa `coletor.executar` sem
        alguem que responda por ela. Sem isto a prova morria no portao errado —
        `AUTORIZACAO_AUSENTE` antes de o teto de gasto ser exercido — e passaria
        a medir a guarda em vez do orcamento.

        Motivo `TRIAL_DE_CAPACIDADE` porque e o que isto e: um ensaio de ROTA
        contra um fornecedor falso, e nao coleta de fonte nenhuma. E o limite
        humano acompanha o orcamento declarado:

            FINANCIAL_BUDGET.AUTHORIZED <= AUTORIZACAO.max_usd
        """
        orc = ct.orcamento_financeiro_actual()
        return ag.autorizar(
            motivo=ag.TRIAL_DE_CAPACIDADE, proposito='C10-8A-F',
            max_execucoes=1, max_usd=(orc.autorizado if orc is not None else 1.00) or 0.01,
            quem_autorizou='a prova C10.8A-F',
            porque='medir o teto de gasto contra um fornecedor falso',
            condicao_de_paragem='um POST por chamada da rota')

    def rota(self, *, run_id, country_scope='IT', medida=None, **k):
        """A rota paga. Ela chama o `coletor.executar` REAL."""
        itens, man = ct.executar(
            ATOR, {'q': 1}, token='TOKEN-FALSO', run_id=run_id, platform=PLAT,
            country=country_scope, mission='C10-8A-F', query='prova',
            source_version='prova', evidence_path='data/samples/prova.json',
            wait=60, salvar_raw=False, teto_usd=self.teto_da_rota,
            autorizacao=self.autorizacao(), proposito='C10-8A-F',
            motivo_do_gasto=ag.TRIAL_DE_CAPACIDADE)
        if medida is not None:
            r = man.get('FINANCIAL_RESERVATION') or {}
            medida['COST_STATE'] = r.get('COST_STATE', 'UNKNOWN')
            medida['ACTUAL_COST_USD'] = r.get('ACTUAL_COST_USD')
            medida['PROVIDER_SIDE_CAP_USD'] = r.get('PROVIDER_SIDE_CAP')
            medida['FINANCIAL_RESERVATION'] = r
        if man['STATUS'] == 'FAILED':
            raise RuntimeError(str(man.get('ERROR'))[:120])
        return itens

    def __enter__(self):
        self._run = ct.subprocess.run
        ct.subprocess.run = self.falso
        # ⚠️ E A PORTA TEM DE SER A PORTA — SCRAP-CV-01.
        # `regras/sensor_coleta.py` troca `coletor._curl` no CORPO do modulo:
        # basta alguem importa-lo para o transporte da unica porta paga mudar no
        # processo inteiro. Com ele trocado, fingir o `subprocess` deixa de
        # fingir alguma coisa — o pedido sai por `urllib` e vai MESMO a rede, e
        # a promessa `NETWORK_REAL = 0` desta suite deixa de valer.
        #
        #     UM FAKE QUE JA NAO ESTA NO CAMINHO NAO E UM FAKE.
        self._curl = ct._curl
        ct._curl = ct._CURL_ORIGINAL
        if self.achar_orfa:
            ct._ultima_execucao = lambda actor, **k: {
                'id': 'orfa-1', 'status': 'SUCCEEDED', 'usageTotalUsd': 0.12,
                'defaultDatasetId': 'ds-orfa', 'startedAt': '2026-09-12T00:00:00.000Z',
                'finishedAt': '2026-09-12T00:00:09.000Z'}
        # A rota entra NO MAPA REAL, por emprestimo e so durante o bloco. O
        # registo recusa um segundo dono — e bem — entao a prova nao finge ser
        # outro adaptador: ela empresta a funcao e devolve-a intacta.
        self._antes = dict(reg._MAPA[(PLAT, CAPAC)])
        reg._MAPA[(PLAT, CAPAC)] = dict(self._antes, ROTA=self.rota)
        return self

    def __exit__(self, *a):
        ct.subprocess.run = self._run
        ct._curl = self._curl
        if self.achar_orfa:
            ct._ultima_execucao = _ULTIMA_REAL
        reg._MAPA[(PLAT, CAPAC)] = self._antes
        return False


_ULTIMA_REAL = ct._ultima_execucao


def colher(*, teto_de_gasto=None, teto_de_rede=None, guiao=(0.0,),
           teto_da_rota=None, achar_orfa=False, chamadas=1, modo=sx.NORMAL,
           permitir_pago=True):
    """Uma execução do runtime real, com o provider falso por baixo."""
    with Cenario(guiao, teto_da_rota=teto_da_rota, achar_orfa=achar_orfa) as c:
        pedido = dict(platform=PLAT, capability=CAPAC, scope='PONTUAL',
                      modo=modo, permitir_pago=permitir_pago, motivo_pago=MOTIVO)
        if teto_de_gasto is not None:
            pedido['teto_de_gasto'] = teto_de_gasto
        if teto_de_rede is not None:
            pedido['teto_de_rede'] = teto_de_rede
        saidas = []
        if chamadas == 1:
            saidas.append(sx.COLLECT(run_id='c108af-1', **pedido))
        else:
            # Várias chamadas DENTRO da mesma execução: um só `with`, um só saldo.
            import coletor as _ct
            with _ct.orcamento_financeiro(teto_de_gasto) as orc:
                for i in range(chamadas):
                    p = dict(pedido)
                    p.pop('teto_de_gasto', None)
                    saidas.append(sx.COLLECT(run_id='c108af-%d' % (i + 1), **p))
                saidas.append(([], orc.para_o_rasto()))
        return saidas, c.falso


print('=' * 88)
print('C10.8A-F · O ORCAMENTO FINANCEIRO DO SINTONIA SCRAP')
print('=' * 88)

# ══ O CENSO, ANTES DE QUALQUER PROVA ══════════════════════════════════════
print('\n── quem pode comprometer dinheiro nesta casa ──')
import ast                                                        # noqa: E402
fonte = open(os.path.join(RAIZ, 'coleta', 'coletor.py'), encoding='utf-8').read()
posts = [n for n in ast.walk(ast.parse(fonte))
         if isinstance(n, ast.Call) and any(
             kw.arg == 'metodo' and isinstance(kw.value, ast.Constant)
             and str(kw.value.value).upper() == 'POST' for kw in n.keywords)]
diz(len(posts) == 1, 'um unico POST cria execucao paga em toda a casa',
    '%d em coletor.py' % len(posts))
pagas = []
for nome, d in sorted(sx.cap.DECLARADAS.items()):
    rotas = (mz.MATRIZ.get(d[0]) or {}).get(sx.cap.da_matriz(nome))
    esc = mz._rota_padrao(rotas) if rotas else None
    if esc and esc['CLASSE'] in ('APIFY', 'OFFICIAL_API_PAID'):
        pagas.append((nome, bool(reg.rota_de(d[0], nome))))
diz(True, 'capacidades com rota paga por omissao', '%d de %d declaradas'
    % (len(pagas), len(sx.cap.DECLARADAS)))
diz(sum(1 for _n, tem in pagas if tem) == 0,
    'e nenhuma delas tem adaptador — a rota paga nao e alcancavel hoje',
    '%d com adaptador' % sum(1 for _n, tem in pagas if tem))

# ══ F0 · LIMITE ZERO ══════════════════════════════════════════════════════
print('\n── F0 · limite 0: o provider nao e chamado ──')
(saidas, falso) = colher(teto_de_gasto=0)
objetos, trace = saidas[0]
diz(len(falso.posts) == 0, 'nenhum POST chegou ao provider', len(falso.posts))
diz(trace.get('RESULT') == 'FINANCIAL_BUDGET_EXHAUSTED',
    'o estado e o do teto financeiro, e nao outro', trace.get('RESULT'))
diz(trace.get('FINANCIAL_CALLS_REFUSED') == 1, 'a recusa ficou registada', 1)
diz(trace.get('FINANCIAL_BUDGET_ACTUAL_USD') == 0.0, 'gasto real = 0', 0)

# ══ F1 · UMA CHAMADA ══════════════════════════════════════════════════════
print('\n── F1 · limite 1.00, custo real 0.25 ──')
(saidas, falso) = colher(teto_de_gasto=1.00, guiao=(0.25,))
objetos, trace = saidas[0]
diz(len(falso.posts) == 1, 'um POST, e um so', len(falso.posts))
diz(trace.get('FINANCIAL_BUDGET_ACTUAL_USD') == 0.25, 'ACTUAL = 0.25',
    trace.get('FINANCIAL_BUDGET_ACTUAL_USD'))
diz(trace.get('FINANCIAL_BUDGET_REMAINING_USD') == 0.75, 'REMAINING = 0.75',
    trace.get('FINANCIAL_BUDGET_REMAINING_USD'))
diz(trace.get('COST_STATE') == ct.CUSTO_LIDO, 'COST_STATE = READ_NOT_SETTLED',
    trace.get('COST_STATE'))
diz(len(objetos) == 1, 'e o objeto veio', len(objetos))

# ══ F2 · SEGUNDA CHAMADA RECEBE O QUE RESTA ═══════════════════════════════
print('\n── F2 · a segunda chamada nao recebe o teto original ──')
(saidas, falso) = colher(teto_de_gasto=1.00, guiao=(0.25, 0.10), chamadas=2)
tetos = [t for _a, t in falso.posts]
diz(tetos[0] == 1.00, 'a primeira leva o saldo inteiro', tetos[0])
diz(tetos[1] is not None and abs(tetos[1] - 0.75) < 1e-9,
    'a segunda leva 0.75 — o que RESTA, nao o teto original', tetos[1])
diz(all(t <= 1.00 for t in tetos), 'PROVIDER CAP <= EXECUTION REMAINING, sempre',
    tetos)

# ══ F3 · EXAUSTAO ═════════════════════════════════════════════════════════
print('\n── F3 · esgotado: a proxima morre ANTES do provider ──')
(saidas, falso) = colher(teto_de_gasto=0.30, guiao=(0.30, 0.10), chamadas=2)
_o1, t1 = saidas[0]
_o2, t2 = saidas[1]
diz(len(falso.posts) == 1, 'so o primeiro POST saiu', len(falso.posts))
diz(t2.get('RESULT') == 'FINANCIAL_BUDGET_EXHAUSTED',
    'a segunda e recusada pelo teto', t2.get('RESULT'))
diz(saidas[2][1]['FINANCIAL_CALLS_REFUSED'] == 1, 'e ficou no rasto como recusa', 1)

# ══ F4 · POST TALVEZ CRIADO ═══════════════════════════════════════════════
print('\n── F4 · o POST caiu no transporte: UNKNOWN, e o saldo NAO volta ──')
(saidas, falso) = colher(teto_de_gasto=1.00,
                         guiao=(ct.PostTalvezCriado('tunel caiu'),))
_o, trace = saidas[0]
diz(trace.get('FINANCIAL_BUDGET_UNKNOWN_USD') == 1.00,
    'o comprometido virou UNKNOWN, inteiro',
    trace.get('FINANCIAL_BUDGET_UNKNOWN_USD'))
diz(trace.get('FINANCIAL_BUDGET_REMAINING_USD') == 0.0,
    'e o saldo NAO voltou para 1.00',
    trace.get('FINANCIAL_BUDGET_REMAINING_USD'))
diz(trace.get('FINANCIAL_BUDGET_ACTUAL_USD') == 0.0,
    'e UNKNOWN nao foi contado como gasto medido',
    trace.get('FINANCIAL_BUDGET_ACTUAL_USD'))
tent = (trace.get('FINANCIAL_ATTEMPTS') or [{}])[0]
diz(tent.get('COST_STATE') == ct.CUSTO_DESCONHECIDO,
    'a tentativa diz UNKNOWN, e nao zero', tent.get('COST_STATE'))

print('\n── F4b · o POST caiu e a execucao orfa foi ADOTADA: custo conhecido ──')
(saidas, falso) = colher(teto_de_gasto=1.00, achar_orfa=True,
                         guiao=(ct.PostTalvezCriado('tunel caiu'),))
_o, trace = saidas[0]
diz(trace.get('FINANCIAL_BUDGET_ACTUAL_USD') == 0.12,
    'adotar a execucao torna o custo LEGIVEL',
    trace.get('FINANCIAL_BUDGET_ACTUAL_USD'))
diz(trace.get('FINANCIAL_BUDGET_UNKNOWN_USD') == 0.0,
    'e nada fica por conhecer', trace.get('FINANCIAL_BUDGET_UNKNOWN_USD'))

# ══ F5 · O PROVIDER COBRA ACIMA DO TETO ═══════════════════════════════════
print('\n── F5 · o provider cobrou acima do cap que lhe foi dado ──')
(saidas, falso) = colher(teto_de_gasto=1.00, teto_da_rota=0.20, guiao=(0.55,))
_o, trace = saidas[0]
tent = (trace.get('FINANCIAL_ATTEMPTS') or [{}])[0]
diz(tent.get('OUTCOME') == 'PROVIDER_EXCEEDED_CAP',
    'a casa detectou e NAO chamou isto de sucesso financeiro',
    tent.get('OUTCOME'))
diz(abs((tent.get('PROVIDER_CAP_BREACH_USD') or 0) - 0.35) < 1e-9,
    'e registou de quanto foi o excesso', tent.get('PROVIDER_CAP_BREACH_USD'))
diz(trace.get('FINANCIAL_BUDGET_ACTUAL_USD') == 0.55,
    'o gasto registado e o REAL, e nao o teto', 0.55)

# ══ F6 · ROTA GRATUITA ════════════════════════════════════════════════════
print('\n── F6 · teto financeiro 0 nao impede rota GRATUITA ──')
import shutil                                                     # noqa: E402
import tempfile                                                   # noqa: E402
import coletor as _ct                                             # noqa: E402
import scrap_http as _http                                        # noqa: E402
import social_envelope as _env                                    # noqa: E402

BRUTO = os.path.join(RAIZ, 'data/samples/SOCIAL-IT/raw-free/BLUESKY/'
                     'authorFeed-caasrl.bsky.social__07f7506618bbd2b6.txt')
CORPO = open(BRUTO, encoding='utf-8').read()


import urllib.request                                              # noqa: E402

ROBOTS = '# Hello Friends!\nUser-agent: *\nAllow: /\n'


class Resposta(object):
    def __init__(self, corpo):
        self._c, self.status, self._lido = corpo.encode('utf-8'), 200, False

    def read(self, *a):
        if self._lido:
            return b''
        self._lido = True
        return self._c

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def close(self):
        pass


def sem_rede(fn):
    """Corre `fn` com o TRANSPORTE falso — nunca com `buscar` falso.

    Trocar `http.buscar` poria o fake POR CIMA do portao do robots e de
    qualquer cobranca que `buscar` faca. O fake tem de ser sempre a camada
    mais funda.

        UM FAKE QUE SUBSTITUI A FUNCAO MEDIDA MEDE O FAKE.
    """
    real, gaveta = urllib.request.urlopen, _env.RAW_DIR

    def falso(req, *a, **k):
        url = req.full_url if hasattr(req, 'full_url') else str(req)
        return Resposta(ROBOTS if url.endswith('/robots.txt') else CORPO)

    urllib.request.urlopen = falso
    _http._ROBOTS.clear()
    _env.RAW_DIR = tempfile.mkdtemp(prefix='c108af-')
    try:
        return fn()
    finally:
        urllib.request.urlopen = real
        _http._ROBOTS.clear()
        shutil.rmtree(_env.RAW_DIR, ignore_errors=True)
        _env.RAW_DIR = gaveta


with _ct.orcamento_financeiro(0) as orc:
    objetos, trace = sem_rede(lambda: sx.COLLECT(
        platform='BLUESKY', capability='bluesky.author.incremental',
        run_id='c108af-free', handle='caasrl.bsky.social', limit=1))
diz(len(objetos) == 1, 'a rota gratuita colheu com o saldo a zero', len(objetos))
diz(orc.gasto == 0.0 and orc.comprometido == 0.0,
    'e nao tocou o orcamento financeiro', orc.gasto)
diz(trace.get('COST_STATE') == 'FREE_ROUTE_BY_POLICY',
    'o custo dela e zero por POLITICA, e o rasto di-lo', trace.get('COST_STATE'))

# ══ F7 · REPROCESSAMENTO LOCAL ════════════════════════════════════════════
print('\n── F7 · reprocessar bytes locais custa zero ──')
# Sem fake nenhum, e com os DOIS tetos a zero. Se algum socket abrisse, o teto
# de rede levantava; se alguma reserva nascesse, o financeiro levantava. O que
# se mede aqui e o que os bytes ja preservados produzem sozinhos.
#
#     UM FAKE INSTALADO DEPOIS DO TETO CONTORNA O TETO.
with _ct.orcamento_financeiro(0) as orc:
    with _http.orcamento_de_rede(0) as orede:
        feed = json.loads(CORPO).get('feed') or []
        objetos = [_env.envelope(
            platform='BLUESKY', native_id=(i.get('post') or {}).get('uri'),
            url=None, content_type='POST', route='reprocess',
            executor='provas/orcamento_financeiro.py', run_id='c108af-r',
            country_scope='IT',
            text=((i.get('post') or {}).get('record') or {}).get('text'))
            for i in feed]
diz(len(objetos) >= 1, 'os bytes preservados produziram objetos', len(objetos))
diz(orc.gasto == 0.0 and orc.comprometido == 0.0,
    'e nao tocaram o orcamento financeiro', orc.gasto)
diz(orede.usados == 0, 'nem o de rede — nenhum socket abriu', orede.usados)

# ══ MULTI-CALL: O SALDO NAO REINICIA ══════════════════════════════════════
print('\n── multi-call: duas chamadas na MESMA execucao ──')
(saidas, falso) = colher(teto_de_gasto=1.00, guiao=(0.40, 0.30), chamadas=2)
rasto = saidas[2][1]
diz(abs(rasto['FINANCIAL_BUDGET_ACTUAL_USD'] - 0.70) < 1e-9,
    'TOTAL actual = 0.70', rasto['FINANCIAL_BUDGET_ACTUAL_USD'])
diz(abs(rasto['FINANCIAL_BUDGET_REMAINING_USD'] - 0.30) < 1e-9,
    'REMAINING = 0.30 — o saldo nao reiniciou',
    rasto['FINANCIAL_BUDGET_REMAINING_USD'])

# ══ EXECUCOES INDEPENDENTES ═══════════════════════════════════════════════
print('\n── duas execucoes, dois saldos ──')
(sA, _f) = colher(teto_de_gasto=1.00, guiao=(0.40,))
(sB, _f) = colher(teto_de_gasto=2.00, guiao=(0.40,))
diz(sA[0][1]['FINANCIAL_BUDGET_AUTHORIZED_USD'] == 1.00
    and sB[0][1]['FINANCIAL_BUDGET_AUTHORIZED_USD'] == 2.00,
    'cada execucao tem o teto que declarou', '1.00 e 2.00')
diz(sB[0][1]['FINANCIAL_BUDGET_ACTUAL_USD'] == 0.40,
    'e a segunda nao herdou a divida da primeira',
    sB[0][1]['FINANCIAL_BUDGET_ACTUAL_USD'])
diz(ct.orcamento_financeiro_actual() is None,
    'fora do bloco nao ha orcamento nenhum', ct.orcamento_financeiro_actual())

# ══ CONCORRENCIA ══════════════════════════════════════════════════════════
print('\n── concorrencia: duas chamadas simultaneas, um so saldo ──')
# A primeira versao desta sonda procurava as PALAVRAS no ficheiro — e encontrou
# o comentario que eu proprio tinha escrito a dizer que elas nao estavam la.
#
#     UMA SONDA QUE PROCURA A PALAVRA ENCONTRA A FRASE QUE DIZ QUE ELA NAO EXISTE.
#
# Entao ela le a ARVORE: imports e chamadas, nunca prosa.
# E ela mede quem ARRANCA execucao concorrente, nao quem importa `threading`.
# Este proprio ficheiro usa `threading.Lock` e `threading.local` — um para
# proteger o saldo, o outro para o isolar por execucao. Nenhum dos dois cria
# uma segunda linha de execucao.
#
#     IMPORTAR `threading` NAO E CORRER EM PARALELO.
ARRANCAM = ('Thread', 'ThreadPoolExecutor', 'ProcessPoolExecutor', 'Pool',
            'Process', 'run_in_executor', 'gather', 'create_task')
serial = []
for mod in ('coleta/coletor.py', 'coleta/instagram_coleta.py',
            'regras/sensor_coleta.py', 'coleta/comunicacao_coleta.py'):
    arv = ast.parse(open(os.path.join(RAIZ, mod), encoding='utf-8').read())
    achados = sorted({
        getattr(n.func, 'attr', None) or getattr(n.func, 'id', None)
        for n in ast.walk(arv) if isinstance(n, ast.Call)
    } & set(ARRANCAM))
    serial.append((mod, achados))
diz(not any(c for _m, c in serial),
    'as portas pagas de hoje sao SERIAIS — medido na arvore, nao na prosa',
    '; '.join('%s:%s' % (os.path.basename(m), c or 'nenhum') for m, c in serial))

orc = ct.OrcamentoFinanceiro(1.00)
barreira, vistos, trava = threading.Barrier(2), [], threading.Lock()


def _atacar():
    barreira.wait()
    try:
        r = orc.reservar(pedido=0.80, ator='ataque')
    except ct.SemOrcamentoFinanceiro:
        r = None
    with trava:
        vistos.append(r)


fios = [threading.Thread(target=_atacar) for _ in range(2)]
for f in fios:
    f.start()
for f in fios:
    f.join()
ganhos = [v for v in vistos if v is not None]
# O ataque queria 0.80 + 0.80 = 1.60 num teto de 1.00. O que a casa faz NAO e
# recusar a segunda: e REBAIXA-LA ao que resta. O invariante que importa nao e
# «so uma passa» — e que a soma nunca ultrapasse o autorizado.
diz(abs(sum(g.cap for g in ganhos) - 1.00) < 1e-9,
    'as duas juntas comprometeram exactamente o autorizado, nunca mais',
    ' + '.join('%.2f' % g.cap for g in ganhos))
diz(orc.comprometido <= 1.00, 'COMMITTED <= AUTHORIZED, sob corrida real',
    orc.comprometido)
diz(all(g.cap <= 1.00 for g in ganhos),
    'e nenhuma reserva sozinha passou do teto', [g.cap for g in ganhos])

# ══ NETWORK × FINANCIAL ═══════════════════════════════════════════════════
print('\n── os dois gates, e nenhum substitui o outro ──')
casos = [(2, 0, False), (0, 1.00, False), (2, 1.00, True), (0, 0, False)]
for rede, dinheiro, esperado in casos:
    (saidas, falso) = colher(teto_de_gasto=dinheiro, teto_de_rede=rede,
                             guiao=(0.10,))
    chegou = len(falso.posts) > 0
    _o, trace = saidas[0]
    diz(chegou == esperado,
        'NETWORK=%s FINANCIAL=%s -> provider %s' % (
            rede, dinheiro, 'chamado' if esperado else 'nao chamado'),
        'RESULT=%s' % trace.get('RESULT'))

# ══ AUTORIZACAO != ORCAMENTO ══════════════════════════════════════════════
print('\n── autorizar gasto nao e declarar ate quanto ──')
(saidas, falso) = colher(teto_de_gasto=0.50, guiao=(0.10,), permitir_pago=False)
_o, trace = saidas[0]
diz(len(falso.posts) == 0, 'sem `permitir_pago`, o teto nao autoriza nada',
    len(falso.posts))
diz(trace.get('RESULT') == 'BUDGET_EXHAUSTED'
    and trace.get('ROUTER_RECORD', {}).get('ESTADO_ORIGINAL') == 'PAID_ROUTE_REFUSED',
    'e a recusa continua a ser a da AUTORIZACAO',
    trace.get('ROUTER_RECORD', {}).get('ESTADO_ORIGINAL'))

print('\n── e um ensaio pago sem teto de gasto nao comeca ──')
(saidas, falso) = colher(teto_de_gasto=None, guiao=(0.10,), modo=sx.TRIAL)
_o, trace = saidas[0]
diz(len(falso.posts) == 0, 'nenhum POST saiu', len(falso.posts))
diz(trace.get('RESULT') == 'PAID_TRIAL_WITHOUT_FINANCIAL_BUDGET',
    'NO FINANCIAL LIMIT -> NO PAID TRIAL', trace.get('RESULT'))

# ══ NOT_RUN != UNKNOWN != ZERO ════════════════════════════════════════════
print('\n── os tres estados do custo nao colapsam ──')
_o, t_nao_correu = sx.COLLECT(platform='LINKEDIN', capability='linkedin.comments',
                              run_id='c108af-notrun')
diz(t_nao_correu.get('COST_STATE') == 'NOT_RUN',
    'rota que nao correu: NOT_RUN', t_nao_correu.get('COST_STATE'))
diz(t_nao_correu.get('ACTUAL_COST_USD') is None,
    'e sem numero nenhum ao lado', t_nao_correu.get('ACTUAL_COST_USD'))
(saidas, _f) = colher(teto_de_gasto=1.00, guiao=(0.0,))
diz(saidas[0][1].get('COST_STATE') == ct.CUSTO_LIDO
    and saidas[0][1].get('ACTUAL_COST_USD') == 0.0,
    'provider chamado e custou zero: READ_NOT_SETTLED com 0.0',
    saidas[0][1].get('COST_STATE'))
(saidas, _f) = colher(teto_de_gasto=1.00, guiao=(None,))
diz(saidas[0][1].get('COST_STATE') == ct.CUSTO_DESCONHECIDO
    and saidas[0][1].get('ACTUAL_COST_USD') is None,
    'provider chamado e custo ilegivel: UNKNOWN, sem numero',
    saidas[0][1].get('COST_STATE'))

# ══ O RASTO ═══════════════════════════════════════════════════════════════
print('\n── o rasto distingue os sete conceitos ──')
(saidas, _f) = colher(teto_de_gasto=1.00, guiao=(0.25,))
_o, trace = saidas[0]
for campo in ('FINANCIAL_BUDGET_AUTHORIZED_USD', 'FINANCIAL_BUDGET_COMMITTED_USD',
              'FINANCIAL_BUDGET_ACTUAL_USD', 'FINANCIAL_BUDGET_UNKNOWN_USD',
              'FINANCIAL_BUDGET_REMAINING_USD', 'FINANCIAL_BUDGET_EXHAUSTED',
              'FINANCIAL_CALLS_REFUSED', 'FINANCIAL_ATTEMPTS'):
    diz(campo in trace, campo, trace.get(campo))
t = (trace['FINANCIAL_ATTEMPTS'] or [{}])[0]
for campo in ('PROVIDER', 'ACTOR', 'MOTIVO_PAGO', 'PROVIDER_SIDE_CAP',
              'OUTCOME', 'COST_STATE', 'ACTUAL_COST_USD'):
    diz(campo in t, 'tentativa · %s' % campo, t.get(campo))
diz('TOKEN' not in json.dumps(trace) and 'TOKEN-FALSO' not in json.dumps(trace),
    'e o rasto nao leva o token', 'sem segredo')

print('\n── sem teto declarado, o rasto nao inventa um ──')
(saidas, falso) = colher(teto_de_gasto=None, guiao=(0.25,))
_o, trace = saidas[0]
diz('FINANCIAL_BUDGET_AUTHORIZED_USD' not in trace,
    'nenhum campo de orcamento nasce sozinho',
    [c for c in trace if c.startswith('FINANCIAL_BUDGET')])
# ⚠️ MUDANCA DE COMPORTAMENTO DECLARADA — SCRAP-CV-01.
# Esta linha exigia UM POST: sem orcamento declarado, a rota paga corria na
# mesma e nenhum `maxTotalChargeUsd` ia ao fornecedor. Era coerente com a
# C10.8A-F isolada — aquela missao instalava um teto, nao fechava a porta a
# quem nao instalasse nenhum.
#
# A CV-01 mediu o que isso custava depois de a SR-02 trazer o limite humano:
# sem ninguem a somar, `max_usd` renascia inteiro a cada POST, e um dolar
# autorizado pagava dois. O ledger deixou de ser opcional.
#
#     SEM_LEDGER_NAO_GASTEI.
diz(falso.posts == [], 'sem ledger nenhum, nao se compra', falso.posts)
diz(trace.get('RESULT') == 'SPEND_NOT_AUTHORIZED',
    'e a recusa tem nome proprio — nem teto, nem transporte',
    trace.get('RESULT'))

print('\n' + '=' * 88)
print('NETWORK_REAL      = 0   (provider falso em todos os casos)')
print('APIFY_RUNS        = 0')
print('PAID_RUNS         = 0')
print('REAL_COST_USD     = 0')
print('ORCAMENTO_FINANCEIRO=%s' % ('FALHOU · %d' % len(FALHAS) if FALHAS else 'PASS'))
if FALHAS:
    for f in FALHAS:
        print('  · %s' % f)
sys.exit(1 if FALHAS else 0)
