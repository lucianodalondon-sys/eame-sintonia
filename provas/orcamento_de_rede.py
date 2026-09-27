#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
C10.8A-R — O TETO DE ACESSOS EXTERNOS, PROVADO SEM TOCAR A REDE.

    py provas/orcamento_de_rede.py

A C10.8A declarou `MAX_REAL_HTTP_REQUESTS = 2` e fez sete. O teto existia — num
script, do lado de fora do runtime — e por isso reiniciou-se a cada volta e não
recusou nada.

    UM TETO QUE VIVE NA PROVA MEDE A PROVA.
    DECLARED BUDGET != ENFORCED BUDGET.

Esta prova mede o contrário: um teto que o runtime cobra, no ponto onde a
ligação abre, antes de existir socket.

O QUE É FALSO AQUI, E SÓ ISSO
-------------------------------
Um transporte falso substitui `urllib.request.urlopen` NO NÍVEL MAIS BAIXO —
por baixo do teto, nunca por cima. Ele conta cada tentativa que chega ao fundo.
Se o runtime deixar passar mais do que o teto, é o falso que acusa.

    UM TETO QUE SE MEDE A SI PRÓPRIO MEDE O ESPELHO.
"""
import io
import json
import os
import socket
import sys
import urllib.error
import urllib.request

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in ('coleta', 'leis', 'medidas', 'ferramentas', 'guarda', ''):
    sys.path.insert(0, os.path.join(RAIZ, p) if p else RAIZ)

import scrap_executor as sx        # noqa: E402
import scrap_http as http          # noqa: E402
import scrap_registo as reg        # noqa: E402
import social_envelope as env      # noqa: E402
reg.carregar_adaptadores()

FALHAS = []
RAW = ('data/samples/SOCIAL-IT/raw-free/BLUESKY/'
       'authorFeed-caasrl.bsky.social__07f7506618bbd2b6.txt')
ROBOTS = '# Hello Friends!\nUser-agent: *\nAllow: /\n'


def diz(ok, titulo, detalhe=''):
    print('  %-4s %-54s %s' % ('ok' if ok else 'FALHA', titulo[:54],
                               str(detalhe)[:64]))
    if not ok:
        FALHAS.append(titulo)


class _Resposta(object):
    def __init__(self, corpo, status=200):
        self._c, self.status = corpo.encode('utf-8'), status
        self._lido = False

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


class Falso(object):
    """O transporte falso, POR BAIXO do teto. Ele conta o que realmente saiu.

    `guiao` é uma lista de respostas ou exceções, consumida por ordem. O que
    sobrar depois dela repete a última.
    """

    def __init__(self, guiao):
        self.guiao, self.chegaram = list(guiao), []

    def __call__(self, req, *a, **k):
        url = req.full_url if hasattr(req, 'full_url') else str(req)
        self.chegaram.append(url)
        efeito = (self.guiao.pop(0) if self.guiao
                  else _Resposta(json.dumps({'feed': []})))
        if isinstance(efeito, Exception):
            raise efeito
        return efeito


def _robots():
    return _Resposta(ROBOTS)


def _feed():
    return _Resposta(io.open(os.path.join(RAIZ, RAW), encoding='utf-8').read())


def correr(limite, guiao, *, capacidade='bluesky.author.incremental',
           plataforma='BLUESKY', **kw):
    """Corre o caminho canônico com teto e transporte falso. → (obj, trace, falso)."""
    falso = Falso(guiao)
    http._ROBOTS.clear()
    real_urlopen, real_conectar = urllib.request.urlopen, socket.create_connection
    gaveta = env.RAW_DIR
    import tempfile
    import shutil
    env.RAW_DIR = tempfile.mkdtemp(prefix='c108ar-')

    # ⚠️ O FALSO ENTRA POR BAIXO. Instalá-lo depois do teto faria o teto medir
    # o falso; instalá-lo antes faz o falso medir o teto.
    urllib.request.urlopen = falso
    socket.create_connection = lambda *a, **k: (_ for _ in ()).throw(
        RuntimeError('SAIDA DE REDE REAL nesta prova'))
    try:
        pedido = dict(platform=plataforma, capability=capacidade,
                      run_id='ORC', modo=sx.TRIAL, handle='x.bsky.social',
                      limit=1, country_scope='IT')
        pedido.update(kw)
        if limite is not None:
            pedido['teto_de_rede'] = limite
        return sx.COLLECT(**pedido) + (falso,)
    finally:
        urllib.request.urlopen = real_urlopen
        socket.create_connection = real_conectar
        shutil.rmtree(env.RAW_DIR, ignore_errors=True)
        env.RAW_DIR = gaveta
        http._ROBOTS.clear()


print('=' * 88)
print('C10.8A-R · O ORCAMENTO DE REDE DO SINTONIA SCRAP')
print('=' * 88)

# ══ A MATRIZ DO TETO ══════════════════════════════════════════════════════
print('\n── a matriz: quantos pedidos SAEM de verdade, por teto ──')
CASOS = (
    ('A · limite 0', 0, [_robots(), _feed()], 0, 0),
    ('B · limite 1', 1, [_robots(), _feed()], 1, 0),
    ('C · limite 2', 2, [_robots(), _feed()], 2, 1),
    ('D · limite 2 com timeout', 2, [_robots(), TimeoutError('nada'),
                                     _feed()], 2, 0),
    ('E · limite 3 com timeout', 3, [_robots(), TimeoutError('nada'),
                                     _feed()], 2, 0),
    ('F · limite 2 com 500', 2, [_robots(),
                                 urllib.error.HTTPError('u', 500, 'x', {}, None),
                                 _feed()], 2, 0),
)
for nome, limite, guiao, esperados, objetos_esperados in CASOS:
    objetos, trace, falso = correr(limite, guiao)
    saiu = len(falso.chegaram)
    diz(saiu == esperados, '%s → %d pedido(s) na rede' % (nome, saiu),
        'esperado %d · objetos %d' % (esperados, len(objetos)))
    diz(len(objetos) == objetos_esperados,
        '%s → %d objeto(s)' % (nome, len(objetos)),
        'esperado %d' % objetos_esperados)
    usado = trace.get('NETWORK_REQUESTS_USED')
    diz(usado == saiu, '%s → o rasto bate com o que saiu' % nome,
        'rasto=%s falso=%d' % (usado, saiu))

# ══ O TETO RECUSA ANTES DO SOCKET ═════════════════════════════════════════
print('\n── a tentativa N+1 morre ANTES da rede ──')
objetos, trace, falso = correr(1, [_robots(), _feed()])
diz(len(falso.chegaram) == 1, 'NETWORK_CALL_N_PLUS_1 = 0',
    '%d chegaram ao transporte' % len(falso.chegaram))
diz(falso.chegaram[0].endswith('/robots.txt'),
    'o que saiu foi o portao, e nao a rota', falso.chegaram[0][:48])
diz(trace.get('NETWORK_BUDGET_EXHAUSTED') is True, 'o rasto diz que esgotou',
    str(trace.get('NETWORK_BUDGET_EXHAUSTED')))
recusados = [t for t in (trace.get('NETWORK_ATTEMPTS') or [])
             if t['OUTCOME'] == 'REFUSED_BY_BUDGET']
diz(len(recusados) == 1, 'a recusa ficou registada como tentativa',
    str(recusados[0] if recusados else '—'))
diz(recusados and recusados[0]['COUNTED'] is False,
    'a tentativa recusada NAO foi contada como usada',
    str(recusados[0]['COUNTED']) if recusados else '—')

# ══ O PORTAO CONTA ════════════════════════════════════════════════════════
print('\n── o robots.txt conta como pedido ──')
objetos, trace, falso = correr(2, [_robots(), _feed()])
tipos = [t['TYPE'] for t in trace.get('NETWORK_ATTEMPTS') or []]
diz(tipos == [http.PEDIDO_ROBOTS, http.PEDIDO_ROTA],
    'o rasto nomeia portao e rota, por ordem', ' → '.join(tipos))
diz(trace['NETWORK_REQUESTS_USED'] == 2, 'os dois foram contados',
    str(trace['NETWORK_REQUESTS_USED']))

# ══ MULTI-HOST: O TETO E TOTAL ════════════════════════════════════════════
print('\n── o teto e da EXECUCAO, nao de cada host ──')
objetos, trace, falso = correr(2, [_robots(), _feed(), _robots()])
hosts = {t['TARGET'] for t in trace.get('NETWORK_ATTEMPTS') or [] if t['COUNTED']}
diz(len(falso.chegaram) == 2, 'so dois pedidos sairam no total',
    '%d · hosts tocados: %s' % (len(falso.chegaram), ', '.join(sorted(hosts))))

# ══ DUAS EXECUCOES NAO PARTILHAM CONTADOR ═════════════════════════════════
print('\n── duas execucoes, dois orcamentos ──')
_o1, t1, f1 = correr(2, [_robots(), _feed()])
_o2, t2, f2 = correr(2, [_robots(), _feed()])
diz(t1['NETWORK_REQUESTS_USED'] == t2['NETWORK_REQUESTS_USED'] == 2,
    'a segunda execucao nao herdou a divida da primeira',
    '%s e %s' % (t1['NETWORK_REQUESTS_USED'], t2['NETWORK_REQUESTS_USED']))
diz(len(f2.chegaram) == 2, 'e ela saiu a rede na mesma', str(len(f2.chegaram)))
diz(http.orcamento_actual() is None, 'fora do bloco nao ha orcamento nenhum',
    str(http.orcamento_actual()))

# ══ SEM TETO, PRODUCAO NAO MUDA ═══════════════════════════════════════════
print('\n── sem teto declarado, nada muda ──')
objetos, trace, falso = correr(None, [_robots(), _feed()])
diz(len(objetos) == 1, 'o caminho normal continua a colher', str(len(objetos)))
diz('NETWORK_BUDGET_LIMIT' not in trace,
    'e o rasto nao inventa um teto que ninguem pediu',
    str(trace.get('NETWORK_BUDGET_LIMIT')))

# ══ REPROCESSAR NAO GASTA ═════════════════════════════════════════════════
print('\n── reprocessar bytes locais custa zero ──')
corpo = io.open(os.path.join(RAIZ, RAW), encoding='utf-8').read()
buscar = http.buscar
http.buscar = lambda *a, **k: corpo
import tempfile
import shutil
gaveta, env.RAW_DIR = env.RAW_DIR, tempfile.mkdtemp(prefix='c108ar-r-')
try:
    with http.orcamento_de_rede(2) as orc:
        objetos = reg.rota_de('BLUESKY', 'bluesky.author.incremental')(
            handle='x', limit=1, run_id='ORC-R', country_scope='IT', medida={})
finally:
    http.buscar = buscar
    shutil.rmtree(env.RAW_DIR, ignore_errors=True)
    env.RAW_DIR = gaveta
diz(orc.usados == 0, 'REPROCESS gastou zero do orcamento', str(orc.usados))
diz(len(objetos) == 1, 'e produziu o objeto na mesma', str(len(objetos)))

# ══ AUTORIZAR GASTO NAO COMPRA PEDIDOS ════════════════════════════════════
print('\n── autorizar dinheiro nao compra acessos ──')
objetos, trace, falso = correr(1, [_robots(), _feed()],
                               permitir_pago=True,
                               motivo_pago='FREE_ROUTE_UNAVAILABLE')
diz(len(falso.chegaram) == 1, '`permitir_pago` nao aumentou o teto',
    '%d pedidos sairam' % len(falso.chegaram))
diz(trace.get('NETWORK_BUDGET_EXHAUSTED') is True,
    'o teto de rede continua a ser o teto de rede',
    str(trace.get('NETWORK_BUDGET_EXHAUSTED')))

# ══ RETENTATIVA E DIAGNOSTICO ═════════════════════════════════════════════
print('\n── retentativa: o que existe hoje, e o que o teto faria ──')
# ⚠️ MEDIDO ANTES DE AFIRMAR: NAO HA CICLO DE RETENTATIVA NENHUM NO SCRAP.
# `leis/falhas.py` diz se retentar ADIANTA (`RECOVERY_ACTION = WAIT`), e
# ninguem no caminho de aquisicao age sobre isso. Dizer «a retentativa respeita
# o teto» sem isto seria verdadeiro por vazio.
#
#     UMA POLITICA QUE NINGUEM EXECUTA NAO E UM COMPORTAMENTO.
#
# O que se prova aqui e o CONTRATO: se uma retentativa acontecer dentro da
# execucao, ela gasta pedido como qualquer outra — e quando o teto acaba, ela
# morre antes do socket.
import ast
sem_ciclo = []
for rel in ('coleta/social_rotas.py', 'coleta/scrap_executor.py',
            'coleta/scrap_http.py'):
    arv = ast.parse(io.open(os.path.join(RAIZ, rel), encoding='utf-8').read())
    ciclos = [n for n in ast.walk(arv) if isinstance(n, (ast.For, ast.While))
              and any(isinstance(c, ast.Call)
                      and (getattr(c.func, 'attr', None) in ('buscar', 'urlopen')
                           or getattr(c.func, 'id', None) in ('buscar',))
                      for c in ast.walk(n))]
    if not ciclos:
        sem_ciclo.append(rel)
diz(len(sem_ciclo) == 3,
    'nenhum dos tres tem ciclo de retentativa a volta da rede',
    '%d de 3' % len(sem_ciclo))

falso = Falso([_robots(), TimeoutError('nada'), _feed()])
real = urllib.request.urlopen
urllib.request.urlopen = falso
http._ROBOTS.clear()
try:
    with http.orcamento_de_rede(2) as orc:
        pedido = urllib.request.Request('https://exemplo.tld/robots.txt')
        pedido.tipo_de_pedido = http.PEDIDO_ROBOTS
        urllib.request.urlopen(pedido)
        primeira = urllib.request.Request('https://exemplo.tld/x')
        primeira.tipo_de_pedido = http.PEDIDO_ROTA
        try:
            urllib.request.urlopen(primeira)
        except TimeoutError:
            pass
        # a RETENTATIVA, que seria a terceira ida a rede
        segunda = urllib.request.Request('https://exemplo.tld/x')
        segunda.tipo_de_pedido = http.PEDIDO_RETENTATIVA
        try:
            urllib.request.urlopen(segunda)
            recusou = False
        except http.SemOrcamentoDeRede:
            recusou = True
finally:
    urllib.request.urlopen = real
    http._ROBOTS.clear()
diz(recusou, 'a retentativa foi recusada pelo teto', 'limite 2, ela seria a 3a')
diz(len(falso.chegaram) == 2, 'e NAO chegou ao transporte',
    '%d chegaram' % len(falso.chegaram))
diz(any(t['TYPE'] == http.PEDIDO_RETENTATIVA and not t['COUNTED']
        for t in orc.tentativas),
    'e ficou no rasto como RETRY recusado',
    str([t['TYPE'] for t in orc.tentativas]))

print('\n── diagnostico: quem toca a rede gasta, mesmo a diagnosticar ──')
falso = Falso([_robots(), urllib.error.HTTPError('u', 500, 'x', {}, None)])
urllib.request.urlopen = falso
http._ROBOTS.clear()
try:
    with http.orcamento_de_rede(2) as orc2:
        p1 = urllib.request.Request('https://exemplo.tld/robots.txt')
        p1.tipo_de_pedido = http.PEDIDO_ROBOTS
        urllib.request.urlopen(p1)
        p2 = urllib.request.Request('https://exemplo.tld/x')
        p2.tipo_de_pedido = http.PEDIDO_ROTA
        try:
            urllib.request.urlopen(p2)
        except urllib.error.HTTPError:
            pass
        # o DIAGNOSTICO — foi exactamente isto que a C10.8A fez por fora
        d = urllib.request.Request('https://exemplo.tld/robots.txt')
        d.tipo_de_pedido = http.PEDIDO_DIAGNOSTICO
        try:
            urllib.request.urlopen(d)
            recusou_d = False
        except http.SemOrcamentoDeRede:
            recusou_d = True
finally:
    urllib.request.urlopen = real
    http._ROBOTS.clear()
diz(recusou_d, 'o diagnostico tambem e recusado quando o teto acabou',
    'foi este o passo que a C10.8A deu por fora do teto')
diz(len(falso.chegaram) == 2, 'e tambem NAO chegou ao transporte',
    '%d chegaram' % len(falso.chegaram))

print('\n' + '=' * 88)
print('NETWORK_REAL      = 0   (transporte falso em todos os casos)')
print('PAID_RUNS         = 0')
print('ORCAMENTO_DE_REDE=%s' % ('PASS' if not FALHAS else 'FAIL'))
for f in FALHAS:
    print('  falhou: %s' % f)
raise SystemExit(0 if not FALHAS else 1)
