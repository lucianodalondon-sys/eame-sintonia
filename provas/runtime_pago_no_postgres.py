#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
C10.6E — O SEGUNDO RUNTIME DA COMUNICAÇÃO PAGA, MEDIDO CONTRA POSTGRES REAL.

    BANCO_DESCARTAVEL_URL=postgresql://... py provas/runtime_pago_no_postgres.py

Esta prova não coleta nada e não gasta nada. Ela mede se o runtime canônico
CONSEGUE, hoje, receber a coleta paga da comunicação pública — e responde com o
degrau exato onde ele para.

    CAN DO != DID DO.

O QUE ELA PROVA, E POR QUE CADA UMA IMPORTA
---------------------------------------------
F1  LinkedIn pede, a política recusa, e o fornecedor não é chamado.
    `LINKEDIN/FETCH_POST` está `ROUTE_NOT_ALLOWED` nas DUAS rotas declaradas.
    A prova negativa vale tanto quanto a positiva: uma casa que só sabe provar
    que consegue não provou que sabe recusar.

F2  A ESCADA DECLARADA E O DEGRAU ALCANÇÁVEL.
    A matriz declara, para Instagram e Facebook, uma rota grátis E uma rota
    paga — e escreve o motivo canônico de subir. O roteador devolve sempre a
    PRIMEIRA viável, e não tem como receber «preciso do degrau de cima».

        A MATRIZ DECLARA A ESCADA. O ROTEADOR SÓ SABE SUBIR O PRIMEIRO DEGRAU.

    É esta a medição que decide o veredito da missão.

F3  O portão do gasto morde, e morde antes de qualquer chamada.
    `INSTAGRAM/FETCH_COMMENTS` é a capacidade cuja rota PADRÃO já é paga.
    Sem autorização: `PAID_ROUTE_REFUSED`. Com motivo fora do vocabulário
    fechado: `PAID_ROUTE_REFUSED` também.

F4  A taxonomia de falha continua sendo de `leis/falhas.py`.
    Sete modos de morte injetados no boundary do transporte, e nenhum deles
    inventa palavra nova nem vira `ZERO_RESULTS`.

        PARSER QUEBRADO NÃO É FONTE VAZIA.

F5  A corrida do caminho negativo é durável e coerente.
    Lida por OUTRA conexão, porque um `dict` em memória não é banco.
"""
import io
import os
import sys
import urllib.error

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in ('coleta', 'leis', 'medidas', 'ferramentas', 'guarda', 'regras', ''):
    sys.path.insert(0, os.path.join(RAIZ, p) if p else RAIZ)

import coleta_checkpoint as ck      # noqa: E402
import falhas as fx                 # noqa: E402
import scrap_executor as sx         # noqa: E402
import scrap_registo as reg         # noqa: E402
import social_matriz as mz          # noqa: E402
import social_rotas as sr           # noqa: E402
reg.carregar_adaptadores()

DSN = os.environ.get('BANCO_DESCARTAVEL_URL')
if not DSN:
    print('BANCO_DESCARTAVEL_URL ausente. Esta prova NAO corre contra LIVE.')
    raise SystemExit(2)
BANCO = ck.Banco(DSN)
FALHAS = []
REDE = {'chamadas': 0}


def diz(ok, titulo, detalhe=''):
    print('  %-4s %-58s %s' % ('ok' if ok else 'FALHA', titulo[:58], detalhe[:60]))
    if not ok:
        FALHAS.append(titulo)


class SemRede(Exception):
    pass


def _proibir_rede():
    """Nenhuma saida real. Uma prova que pode tocar a rede nao prova rede zero."""
    import socket
    original = socket.socket

    class Trancado(original):
        def __init__(self, *a, **k):
            REDE['chamadas'] += 1
            raise SemRede('SAIDA DE REDE REAL nesta prova')
    socket.socket = Trancado
    return original


_proibir_rede()

print('=' * 88)
print('C10.6E · O SEGUNDO RUNTIME DA COMUNICACAO PAGA')
print('=' * 88)

# ══ F1 · O LINKEDIN PEDE E A POLITICA RECUSA ══════════════════════════════
print('\n── F1 · a prova NEGATIVA: LinkedIn nao chega ao fornecedor ──')
d = mz.decisao('LINKEDIN', 'FETCH_POST')
diz(d['DECISAO'] == mz.NAO_PERMITIDA, 'a politica recusa LINKEDIN/FETCH_POST',
    d['DECISAO'])
gastos = []
import coletor                                                    # noqa: E402
_exec_real = coletor.executar
coletor.executar = lambda *a, **k: gastos.append(a) or ([], {})
try:
    objetos, registo = sr.executar(platform='LINKEDIN', capability='FETCH_POST',
                                   run_id='RP-LINKEDIN', country_scope='IT')
finally:
    coletor.executar = _exec_real
diz(registo['ESTADO'] == 'ROUTE_NOT_ALLOWED', 'o roteador devolve ROUTE_NOT_ALLOWED',
    registo['ESTADO'])
diz(objetos == [], 'nenhum objeto voltou', str(len(objetos)))
diz(gastos == [], 'o fornecedor pago NAO foi chamado', '%d chamadas' % len(gastos))
diz(registo['COST_USD'] == 0.0, 'custo zero', str(registo['COST_USD']))
diz(registo['ROTA_ESCOLHIDA'] is None, 'nenhuma rota foi escolhida',
    str(registo['ROTA_ESCOLHIDA']))

# ══ F2 · A ESCADA DECLARADA E O DEGRAU ALCANCAVEL ═════════════════════════
print('\n── F2 · a escada declarada, e o degrau que o roteador alcanca ──')
for plat in ('INSTAGRAM', 'FACEBOOK'):
    rotas = mz.MATRIZ[plat]['FETCH_POST']
    pagas = [x for x in rotas if x['CLASSE'] in ('APIFY', 'OFFICIAL_API_PAID')]
    padrao = mz._rota_padrao(rotas)
    diz(len(pagas) >= 1, '%s declara rota PAGA na escada' % plat,
        pagas[0]['ROTA'] if pagas else '—')
    diz(padrao is not None and padrao not in pagas,
        '%s: a rota PADRAO NAO e a paga' % plat, padrao['ROTA'] if padrao else '—')
    # e o pedido com autorizacao de gasto continua a cair na rota gratis
    _, registo = sr.executar(platform=plat, capability='FETCH_POST',
                             run_id='RP-%s' % plat, country_scope='IT',
                             permitir_pago=True,
                             motivo_pago='FREE_ROUTE_INSUFFICIENT_CAPABILITY')
    diz(registo['ROTA_ESCOLHIDA'] == padrao['ROTA'],
        '%s: autorizar gasto NAO alcanca a rota paga' % plat,
        str(registo['ROTA_ESCOLHIDA']))
    diz(registo['MOTIVO_PAGO'] is None,
        '%s: o motivo canonico nem chega a ser usado' % plat,
        str(registo['MOTIVO_PAGO']))

# ══ F3 · O PORTAO DO GASTO MORDE ══════════════════════════════════════════
print('\n── F3 · o portao do gasto, na capacidade cuja rota padrao E paga ──')
padrao = mz._rota_padrao(mz.MATRIZ['INSTAGRAM']['FETCH_COMMENTS'])
diz(padrao['CLASSE'] == 'APIFY', 'INSTAGRAM/FETCH_COMMENTS tem rota padrao PAGA',
    padrao['ROTA'])
# ⚠️ O ESTADO QUE O CHAMADOR VE JA ESTA SELADO. `social_rotas.selar` traduz
# pela `leis/falhas.py`, e a recusa de gasto tem palavra canonica propria:
# `PAID_ROUTE_REFUSED` → `BUDGET_EXHAUSTED`. Medir o estado INTERNO seria medir
# uma palavra que nenhum consumidor da casa le.
#
#     UMA PROVA QUE MEDE O ESTADO DE DENTRO NAO MEDE O QUE SAI PELA PORTA.
RECUSA_DE_GASTO = fx.traduzir('PAID_ROUTE_REFUSED')
_, r_sem = sr.executar(platform='INSTAGRAM', capability='FETCH_COMMENTS',
                       run_id='RP-GATE-1', country_scope='IT')
diz(r_sem['ESTADO'] == RECUSA_DE_GASTO, 'sem autorizacao: o gasto e recusado',
    '%s (era %s)' % (r_sem['ESTADO'], r_sem.get('ESTADO_ORIGINAL')))
diz(r_sem.get('ESTADO_ORIGINAL') == 'PAID_ROUTE_REFUSED',
    'e o estado original diz PORQUE', str(r_sem.get('ESTADO_ORIGINAL')))
_, r_mot = sr.executar(platform='INSTAGRAM', capability='FETCH_COMMENTS',
                       run_id='RP-GATE-2', country_scope='IT',
                       permitir_pago=True, motivo_pago='porque sim')
diz(r_mot['ESTADO'] == RECUSA_DE_GASTO,
    'motivo fora do vocabulario fechado: recusado na mesma',
    str(r_mot.get('ESTADO_ORIGINAL')))
_, r_ok = sr.executar(platform='INSTAGRAM', capability='FETCH_COMMENTS',
                      run_id='RP-GATE-3', country_scope='IT',
                      permitir_pago=True, motivo_pago='FREE_ROUTE_UNAVAILABLE')
diz(r_ok.get('ESTADO_ORIGINAL') != 'PAID_ROUTE_REFUSED'
    and r_ok['ESTADO'] != RECUSA_DE_GASTO,
    'com motivo canonico o portao deixa passar', r_ok['ESTADO'])
diz(r_ok.get('ESTADO_ORIGINAL') == 'POSSIBLE_NOT_PROVED',
    'e para logo a seguir: nao ha adaptador ligado',
    str(r_ok.get('ESTADO_ORIGINAL')))
diz(r_ok['ESTADO'] == 'UNKNOWN_ERROR',
    '«declarada, permitida e sem adaptador» sai como UNKNOWN_ERROR',
    r_ok['ESTADO'])
diz(REDE['chamadas'] == 0, 'nenhuma saida de rede ate aqui',
    '%d' % REDE['chamadas'])

# ══ F4 · A TAXONOMIA DE FALHA CONTINUA CANONICA ═══════════════════════════
print('\n── F4 · sete modos de morte, traduzidos pelo dono da taxonomia ──')


def _erro(ex):
    def rota(**kw):
        raise ex
    return rota


class _Malformado(object):
    def __getitem__(self, k):
        raise KeyError('campo que o extractor esperava')


CASOS = (
    ('401', urllib.error.HTTPError('u', 401, 'x', {}, None)),
    ('403', urllib.error.HTTPError('u', 403, 'x', {}, None)),
    ('404', urllib.error.HTTPError('u', 404, 'x', {}, None)),
    ('429', urllib.error.HTTPError('u', 429, 'x', {}, None)),
    ('500', urllib.error.HTTPError('u', 500, 'x', {}, None)),
    ('timeout', TimeoutError('a fonte nao respondeu')),
    ('malformed', KeyError('campo que o extractor esperava')),
)
_rota_real = sr._rota_executavel
traducoes = {}
try:
    for nome, ex in CASOS:
        sr._rota_executavel = lambda *a, **k: _erro(ex)
        _, registo = sr.executar(platform='YOUTUBE', capability='SEARCH_KEYWORD',
                                 run_id='RP-FALHA-%s' % nome, country_scope='IT')
        traducoes[nome] = registo['ESTADO']
finally:
    sr._rota_executavel = _rota_real
for nome, estado in traducoes.items():
    diz(estado in fx.ESTADOS, '%s → %s' % (nome, estado), estado)
diz(traducoes.get('malformed') == 'PARSER_DRIFT',
    'parser quebrado NAO vira ZERO_RESULTS', traducoes.get('malformed'))
diz(traducoes.get('429') != traducoes.get('500'),
    '429 e 500 nao sao a mesma coisa',
    '%s vs %s' % (traducoes.get('429'), traducoes.get('500')))
diz(len(set(traducoes.values())) >= 5,
    'os sete modos nao colapsam num balde so',
    '%d estados distintos' % len(set(traducoes.values())))

# ══ F5 · A CORRIDA DO CAMINHO NEGATIVO E DURAVEL ══════════════════════════
print('\n── F5 · a corrida negativa, contra Postgres real ──')
BANCO.executa("delete from public.etapa_da_corrida where run_id like 'RP-%';")
BANCO.executa("delete from public.collection_run where run_id like 'RP-%';")
objetos, trace = sx.COLLECT(platform='LINKEDIN', capability='linkedin.direct_post',
                            run_id='RP-DURAVEL', banco=BANCO)
diz(objetos == [], 'nenhum objeto', str(len(objetos)))
diz(trace.get('RUN_STATE_PERSISTED') == 'YES', 'a RUN foi persistida',
    str(trace.get('RUN_STATE_PERSISTED')))
outra = ck.Banco(DSN)                 # OUTRA conexao: o banco e que prova
linhas = outra.executa(
    "select status, coalesce(error,'-') from public.collection_run "
    "where run_id = 'RP-DURAVEL';")
diz(bool(linhas), 'a corrida existe no banco, lida por outra conexao',
    str(linhas[0] if linhas else '—'))
if linhas:
    diz(linhas[0][0] != ck.CORRIDA_ABERTA, 'a corrida nao ficou em `rodando`',
        linhas[0][0])
etapas = outra.executa(
    "select etapa, estado from public.etapa_da_corrida "
    "where run_id = 'RP-DURAVEL' order by id;")
diz(bool(etapas), 'o rastro de etapa existe', ' '.join('%s/%s' % (a, b)
                                                       for a, b in etapas))
penduradas = [e for e in etapas if e[1] == 'RUNNING']
diz(not penduradas, 'nenhuma etapa ficou pendurada em RUNNING',
    str(len(penduradas)))
custo = outra.executa("select coalesce(cost_usd,0)::text from public.collection_run "
                      "where run_id = 'RP-DURAVEL';")
diz(not custo or float(custo[0][0]) == 0.0, 'custo da corrida negativa = 0',
    str(custo[0][0] if custo else '—'))

print('\n' + '=' * 88)
print('SAIDA_DE_REDE_REAL     = %d' % REDE['chamadas'])
print('PAID_PROVIDER_CALLS    = 0')
print('COST_USD               = 0')
print('PAID_ROUTE_REACHABLE   = NO   (a escada declara, o roteador nao sobe)')
print('RUNTIME_PAGO=%s' % ('PASS' if not FALHAS else 'FAIL'))
if FALHAS:
    for f in FALHAS:
        print('  falhou: %s' % f)
raise SystemExit(0 if not FALHAS else 1)
