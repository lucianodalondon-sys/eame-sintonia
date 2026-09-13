#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
C10.7 — O ENSAIO CANÔNICO, MEDIDO SEM REDE E SEM BANCO.

    py provas/ensaio_canonico_de_capacidade.py

Esta prova não coleta nada, não gasta nada, não abre banco e não toca a rede.
Ela mede a ferramenta SCRAP a responder a uma pergunta que até aqui não tinha
resposta canônica:

    COMO UMA CAPACIDADE `NOT_EXECUTED` É MEDIDA PELA PRIMEIRA VEZ
    SEM SAIR DO EXECUTOR?

O QUE É FALSO AQUI, E SÓ ISSO
-------------------------------
O único objeto substituído é `scrap_http.buscar` — a chamada externa do
fornecedor. O executor, o roteador, o registo e o adaptador correm a sério, com
as mesmas linhas que correm em produção.

    MOCKAR O RUNTIME PROVA O MOCK. MOCKAR A PORTA EXTERNA PROVA O RUNTIME.

E o RAW é desviado para uma gaveta temporária, porque uma prova que escreve no
acervo mede o acervo a seguir.
"""
import hashlib
import io
import json
import os
import shutil
import sys
import tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in ('coleta', 'leis', 'medidas', 'ferramentas', 'guarda', ''):
    sys.path.insert(0, os.path.join(RAIZ, p) if p else RAIZ)

import scrap_capacidades as cap     # noqa: E402
import scrap_executor as sx         # noqa: E402
import scrap_http as http           # noqa: E402
import scrap_registo as reg         # noqa: E402
import social_envelope as env       # noqa: E402
import social_matriz as mz          # noqa: E402
import social_rotas as sr           # noqa: E402
reg.carregar_adaptadores()

FALHAS = []
REDE = {'sockets': 0}
TOCOU = {'http': 0, 'roteador': 0, 'adaptador': 0}


def diz(ok, titulo, detalhe=''):
    print('  %-4s %-56s %s' % ('ok' if ok else 'FALHA', titulo[:56], detalhe[:62]))
    if not ok:
        FALHAS.append(titulo)


class SaidaDeRede(Exception):
    pass


def _trancar_rede():
    import socket
    original = socket.socket

    class Trancado(original):
        def __init__(self, *a, **k):
            REDE['sockets'] += 1
            raise SaidaDeRede('SAIDA DE REDE REAL nesta prova')
    socket.socket = Trancado


_trancar_rede()

#: A resposta do fornecedor falso. Um post de Mastodon, na forma que a API
#: documenta — porque um fixture com a forma errada prova o fixture.
RESPOSTA_MASTODON = json.dumps([{
    'id': '111', 'uri': 'https://exemplo.social/users/agro/statuses/111',
    'url': 'https://exemplo.social/@agro/111',
    'created_at': '2026-09-01T10:00:00.000Z', 'language': 'it',
    'content': '<p>Prova de ensaio canonico.</p>',
    'account': {'acct': 'agro@exemplo.social'},
}])


def _falso(url, **kw):
    TOCOU['http'] += 1
    return RESPOSTA_MASTODON


print('=' * 86)
print('C10.7 · O ENSAIO CANONICO DE CAPACIDADE')
print('=' * 86)

# ══ F1 · O PARADOXO, MEDIDO ANTES DE QUALQUER CONSERTO ════════════════════
print('\n── F1 · o ciclo fechado que existia ──')
PRESAS = [(p, n) for n, v in sx.CAPABILITIES().items()
          for p in (v['PLATFORM'],)
          if v['CAPABILITY_STATE'] == 'NOT_EXECUTED' and v['HAS_ROUTE']]
diz(bool(PRESAS), 'ha capacidade NOT_EXECUTED COM rota ligada',
    ', '.join('%s/%s' % x for x in PRESAS) or 'nenhuma')
for plat, nome in PRESAS:
    v = sx.CHECK(plat, nome)
    diz(v['CAN'] is False and v['STATE'] == sx.SEM_PROMESSA,
        '%s: NORMAL continua a recusar' % nome, v['STATE'])
    d = mz.decisao(plat, cap.da_matriz(nome))
    diz(d['DECISAO'] == mz.PERMITIDA_SIM, '%s: e a politica PERMITE' % nome,
        d['DECISAO'])

# ══ F2 · NORMAL CONTRA TRIAL, MESMO PEDIDO ════════════════════════════════
print('\n── F2 · o mesmo pedido nos dois modos ──')
PLAT, CAPAC = 'MASTODON', 'mastodon.account.incremental'
estado_antes = cap.estado(CAPAC)
antes_do_ficheiro = hashlib.sha256(
    io.open(os.path.join(RAIZ, 'coleta', 'scrap_capacidades.py'),
            'rb').read()).hexdigest()

gaveta = tempfile.mkdtemp(prefix='c107-')
raw_real, http_real = env.RAW_DIR, http.buscar
_rota_real = sr._rota_executavel


def _espia_rota(plat, capac):
    TOCOU['roteador'] += 1
    fn = _rota_real(plat, capac)
    if fn is None:
        return None

    def embrulho(**kw):
        TOCOU['adaptador'] += 1
        return fn(**kw)
    return embrulho


env.RAW_DIR = gaveta
http.buscar = _falso
sr._rota_executavel = _espia_rota
try:
    o_normal, t_normal = sx.COLLECT(platform=PLAT, capability=CAPAC,
                                    run_id='C107-NORMAL',
                                    instancia='exemplo.social', acct_id='1',
                                    limit=5)
    o_trial, t_trial = sx.COLLECT(platform=PLAT, capability=CAPAC,
                                  run_id='C107-TRIAL', modo=sx.TRIAL,
                                  instancia='exemplo.social', acct_id='1',
                                  limit=5)
finally:
    env.RAW_DIR, http.buscar = raw_real, http_real
    sr._rota_executavel = _rota_real
    shutil.rmtree(gaveta, ignore_errors=True)

diz(o_normal == [], 'NORMAL: nenhum objeto', str(len(o_normal)))
diz(t_normal['CHECK']['STATE'] == sx.SEM_PROMESSA,
    'NORMAL: recusado pelo estado da capacidade', t_normal['CHECK']['STATE'])
diz(t_normal['EXECUTION_MODE'] == sx.NORMAL, 'NORMAL: o trace nomeia o modo',
    t_normal['EXECUTION_MODE'])
diz(bool(o_trial), 'TRIAL: o caminho chegou ao fim e trouxe objeto',
    str(len(o_trial)))
diz(t_trial['EXECUTION_MODE'] == sx.TRIAL, 'TRIAL: o trace nomeia o modo',
    t_trial['EXECUTION_MODE'])
diz(t_trial['CHECK']['STATE'] == sx.ELEGIVEL_PARA_ENSAIO,
    'TRIAL: o CHECK distingue ensaio de producao', t_trial['CHECK']['STATE'])
diz(t_trial['CHECK']['PRODUCTION_READY'] is False,
    'TRIAL: PRODUCTION_READY continua falso',
    str(t_trial['CHECK']['PRODUCTION_READY']))

# ══ F3 · A CADEIA INTEIRA FOI ATRAVESSADA ═════════════════════════════════
print('\n── F3 · quem foi tocado, e por onde ──')
diz(TOCOU['roteador'] >= 1, 'ROUTER_REACHED', str(TOCOU['roteador']))
diz(TOCOU['adaptador'] >= 1, 'ADAPTER_REACHED', str(TOCOU['adaptador']))
diz(TOCOU['http'] >= 1, 'FAKE_PROVIDER_REACHED', str(TOCOU['http']))
diz(REDE['sockets'] == 0, 'NETWORK_REAL = 0', str(REDE['sockets']))
diz(t_trial.get('EXECUTOR_ID') == sx.EXECUTOR_ID, 'EXECUTOR_REACHED',
    str(t_trial.get('EXECUTOR_ID')))

# ══ F4 · O ENSAIO NAO PROMOVE ESTADO ══════════════════════════════════════
print('\n── F4 · o ensaio nao promove nada ──')
depois_do_ficheiro = hashlib.sha256(
    io.open(os.path.join(RAIZ, 'coleta', 'scrap_capacidades.py'),
            'rb').read()).hexdigest()
diz(cap.estado(CAPAC) == estado_antes, 'CAPABILITY_STATE inalterado',
    '%s → %s' % (estado_antes, cap.estado(CAPAC)))
diz(antes_do_ficheiro == depois_do_ficheiro,
    'o ficheiro da declaracao nao foi escrito', depois_do_ficheiro[:12])
diz(t_trial['CAPABILITY_STATE_BEFORE'] == t_trial['CAPABILITY_STATE_AFTER'],
    'o trace carrega BEFORE == AFTER',
    '%s == %s' % (t_trial['CAPABILITY_STATE_BEFORE'],
                  t_trial['CAPABILITY_STATE_AFTER']))
diz(t_trial['CAPABILITY_STATE_AFTER'] != 'PROVEN',
    'um ensaio com objetos NAO virou PROVEN',
    t_trial['CAPABILITY_STATE_AFTER'])

# ══ F5 · A POLITICA GANHA SEMPRE ══════════════════════════════════════════
print('\n── F5 · o ensaio nao sobrescreve a politica ──')
chamadas = {'n': 0}


def _conta(url, **kw):
    chamadas['n'] += 1
    return RESPOSTA_MASTODON


http.buscar = _conta
try:
    d = mz.decisao('LINKEDIN', 'FETCH_POST')
    diz(d['DECISAO'] == mz.NAO_PERMITIDA, 'LINKEDIN/FETCH_POST continua proibida',
        d['DECISAO'])
    _o, r = sr.executar(platform='LINKEDIN', capability='FETCH_POST',
                        run_id='C107-POL')
    diz(r['ESTADO'] == 'ROUTE_NOT_ALLOWED', 'o roteador recusa a rota proibida',
        r['ESTADO'])
    diz(chamadas['n'] == 0, 'ROUTE_NOT_ALLOWED_PROVIDER_CALLS = 0',
        str(chamadas['n']))
    # e a capacidade PROVEN sobre rota proibida continua sem correr por ensaio
    v = sx.CHECK('LINKEDIN', 'linkedin.direct_post', modo=sx.TRIAL)
    diz(v['CAN'] is False, 'sem rota ligada, o ensaio tambem nao passa',
        v['STATE'])
finally:
    http.buscar = http_real

# ══ F6 · BLOCKED NAO VIRA EXECUTAVEL ══════════════════════════════════════
print('\n── F6 · BLOCKED nao entra em ensaio ──')
bloqueadas = [(v['PLATFORM'], n) for n, v in sx.CAPABILITIES().items()
              if v['CAPABILITY_STATE'] == 'BLOCKED']
diz(bool(bloqueadas), 'ha capacidade BLOCKED para medir', str(len(bloqueadas)))
chamadas['n'] = 0
http.buscar = _conta
try:
    for plat, nome in bloqueadas:
        v = sx.CHECK(plat, nome, modo=sx.TRIAL)
        if v['CAN'] or v['STATE'] != sx.ENSAIO_RECUSADO:
            diz(False, '%s entrou em ensaio' % nome, v['STATE'])
    diz(all(sx.CHECK(p, n, modo=sx.TRIAL)['STATE'] == sx.ENSAIO_RECUSADO
            for p, n in bloqueadas),
        'as %d BLOCKED recusam em ensaio' % len(bloqueadas), sx.ENSAIO_RECUSADO)
    diz(chamadas['n'] == 0, 'BLOCKED_CAPABILITY_TRIAL_PROVIDER_CALLS = 0',
        str(chamadas['n']))
finally:
    http.buscar = http_real

# ══ F7 · O ENSAIO NAO AUTORIZA GASTO ══════════════════════════════════════
print('\n── F7 · o ensaio nao e autorizacao de gasto ──')
padrao = mz._rota_padrao(mz.MATRIZ['INSTAGRAM']['FETCH_COMMENTS'])
diz(padrao['CLASSE'] == 'APIFY', 'INSTAGRAM/FETCH_COMMENTS tem rota padrao PAGA',
    padrao['ROTA'])
_o, r_pago = sr.executar(platform='INSTAGRAM', capability='FETCH_COMMENTS',
                         run_id='C107-PAGO')
diz(r_pago.get('ESTADO_ORIGINAL') == 'PAID_ROUTE_REFUSED',
    'a rota paga continua a exigir autorizacao explicita',
    str(r_pago.get('ESTADO_ORIGINAL')))
import ast                                                        # noqa: E402
arv = ast.parse(io.open(os.path.join(RAIZ, 'coleta', 'scrap_executor.py'),
                        encoding='utf-8').read())
fn = next(n for n in ast.walk(arv) if isinstance(n, ast.FunctionDef)
          and n.name == 'COLLECT')
nomes = {c.value for c in ast.walk(fn) if isinstance(c, ast.Constant)
         and isinstance(c.value, str)}
diz('permitir_pago' not in nomes and 'motivo_pago' not in nomes,
    'o executor nao toca no eixo do gasto', 'nenhuma mencao')

# ══ F8 · A INTROSPECCAO RESPONDE SEM EXECUTAR ═════════════════════════════
print('\n── F8 · CAPABILITIES nao corre nada ──')
chamadas['n'] = 0
http.buscar = _conta
try:
    caps = sx.CAPABILITIES()
finally:
    http.buscar = http_real
diz(chamadas['n'] == 0, 'CAPABILITIES nao chamou o fornecedor', str(chamadas['n']))
diz(all({'PRODUCTION_READY', 'TRIAL_ELIGIBLE', 'POLICY_DECISION'} <= set(v)
        for v in caps.values()),
    'os tres eixos aparecem em todas as capacidades', '%d capacidades' % len(caps))
divergentes = [n for n, v in caps.items()
               if v['HAS_ROUTE'] != reg.tem_caminho(v['PLATFORM'], n)]
diz(not divergentes, 'HAS_ROUTE concorda com o dono do registo',
    '%d divergencias' % len(divergentes))
elegiveis = [n for n, v in caps.items()
             if v['TRIAL_ELIGIBLE'] and not v['PRODUCTION_READY']]
diz(bool(elegiveis), 'ha capacidade elegivel a ensaio e nao pronta',
    ', '.join(elegiveis))

print('\n' + '=' * 86)
print('NETWORK_REAL          = %d' % REDE['sockets'])
print('PAID_RUNS             = 0')
print('STATE_PROMOTED        = NO')
print('PRODUCTION_BEHAVIOR   = UNCHANGED')
print('ENSAIO_CANONICO=%s' % ('PASS' if not FALHAS else 'FAIL'))
for f in FALHAS:
    print('  falhou: %s' % f)
raise SystemExit(0 if not FALHAS else 1)
