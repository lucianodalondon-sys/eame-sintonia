#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
C10.8A — O PRIMEIRO TRIAL REAL DO SINTONIA SCRAP, CONTRA REDE DE VERDADE.

    py provas/bluesky_trial_ao_vivo.py            # corre a chamada real
    py provas/bluesky_trial_ao_vivo.py --reprocessar   # so o RAW, sem rede

Esta prova NAO e uma coleta. E uma sentinela: um objeto, de uma conta, para
responder a uma pergunta que nenhuma fixture responde —

    O MECANISMO `TRIAL` DA C10.7 FUNCIONA CONTRA UMA PLATAFORMA REAL,
    PELA CADEIA CANONICA INTEIRA, SEM BYPASS E SEM GASTO?

O TETO E DURO, E ELE MORDE
----------------------------
`MAX_PEDIDOS` nao e um comentario: o transporte e embrulhado e a requisicao
numero tres LEVANTA. Uma prova que so PROMETE nao paginar mede a promessa.

    UM TETO QUE NAO RECUSA NAO E UM TETO.

E o portao do `robots.txt` conta. Ele e uma ida a rede como qualquer outra, e
escondê-lo do orcamento seria a mesma contabilidade que esta casa recusa noutros
sitios.

    UM PEDIDO QUE NAO CONTA PARA O TETO CONTA PARA O HOST.
"""
import hashlib
import io
import json
import os
import sys
import time
import urllib.request

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in ('coleta', 'leis', 'medidas', 'ferramentas', 'guarda', ''):
    sys.path.insert(0, os.path.join(RAIZ, p) if p else RAIZ)

import scrap_capacidades as cap     # noqa: E402
import scrap_executor as sx         # noqa: E402
import scrap_registo as reg         # noqa: E402
import social_envelope as env       # noqa: E402
import social_matriz as mz          # noqa: E402
reg.carregar_adaptadores()

PLATAFORMA = 'BLUESKY'
CAPACIDADE = 'bluesky.author.incremental'
#: O alvo NAO foi escolhido na internet. Ele veio do RAW preservado de uma
#: corrida canonica de `bluesky.account.discovery`, commitada em `cf3aec60`
#: (2026-09-08), com o termo `agricoltura` que esta casa declara em `ALVOS`.
#: Entre os sete devolvidos, escolheu-se o unico com nome de ORGANIZACAO:
#: uma sentinela nao deve ser a conta pessoal de ninguem.
ALVO = 'caasrl.bsky.social'
ALVO_ORIGEM = ('cf3aec60:data/samples/SOCIAL-IT/raw-free/BLUESKY/'
               'searchActors-agricoltura__7ab1f4d86783235e.txt')
ESCOPO = 'IT'
TETO = 1
MAX_PEDIDOS = 2

FALHAS = []
PEDIDOS = []


def diz(ok, titulo, detalhe=''):
    print('  %-4s %-54s %s' % ('ok' if ok else 'FALHA', titulo[:54], str(detalhe)[:66]))
    if not ok:
        FALHAS.append(titulo)


class TetoEstourado(RuntimeError):
    """A terceira requisicao. Ela NAO sai desta maquina."""


def _contar_e_limitar():
    """Embrulha o transporte. Conta, mede, e RECUSA a partir do teto."""
    original = urllib.request.urlopen

    def contado(req, *a, **k):
        url = req.full_url if hasattr(req, 'full_url') else str(req)
        if len(PEDIDOS) >= MAX_PEDIDOS:
            raise TetoEstourado('pedido %d excede MAX_PEDIDOS=%d: %s'
                                % (len(PEDIDOS) + 1, MAX_PEDIDOS, url))
        marca = time.time()
        registo = {'URL': url, 'STATUS': None, 'BYTES': 0, 'MS': None,
                   'ERRO': None}
        PEDIDOS.append(registo)
        try:
            resposta = original(req, *a, **k)
        except Exception as e:                                    # noqa: BLE001
            registo['ERRO'] = '%s: %s' % (type(e).__name__, e)
            registo['MS'] = int((time.time() - marca) * 1000)
            raise
        corpo = resposta.read()
        registo.update({'STATUS': resposta.status, 'BYTES': len(corpo),
                        'MS': int((time.time() - marca) * 1000)})
        # devolve um objeto que se comporta como a resposta, com o corpo ja lido
        return _Relida(resposta, corpo)
    urllib.request.urlopen = contado
    return original


class _Relida(object):
    """A resposta, com o corpo ja lido uma vez — para o contador poder medir
    os bytes sem tirar a leitura a quem chamou."""

    def __init__(self, resposta, corpo):
        self._r, self._c, self._lido = resposta, corpo, False

    def read(self, *a):
        if self._lido:
            return b''
        self._lido = True
        return self._c

    def __enter__(self):
        return self

    def __exit__(self, *a):
        try:
            self._r.close()
        except Exception:                                         # noqa: BLE001
            pass

    def __getattr__(self, n):
        return getattr(self._r, n)


def _sha(caminho):
    with io.open(caminho, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


def _sha_da_declaracao():
    return _sha(os.path.join(RAIZ, 'coleta', 'scrap_capacidades.py'))


# ══ REPROCESSAMENTO — FASE 18, sem rede nenhuma ═══════════════════════════
def reprocessar(referencia):
    """Corre o adaptador sobre os BYTES PRESERVADOS. Zero rede.

    Isto e o que garante que uma regra pode mudar sem recoletar. E prova-se
    trancando a rede: uma prova que PODE tocar a rede nao prova que nao tocou.
    """
    import socket
    tentativas = {'n': 0}
    original = socket.socket

    class Trancado(original):
        def __init__(self, *a, **k):
            tentativas['n'] += 1
            raise RuntimeError('SAIDA DE REDE no reprocessamento')
    socket.socket = Trancado
    try:
        caminho = os.path.join(RAIZ, referencia)
        with io.open(caminho, encoding='utf-8') as f:
            corpo = f.read()
        import social_rotas as sr                                 # noqa: F401
        import scrap_http as http
        buscar_real = http.buscar
        http.buscar = lambda *a, **k: corpo
        try:
            objetos = reg.rota_de(PLATAFORMA, CAPACIDADE)(
                handle=ALVO, limit=TETO, run_id='C108A-REPROC',
                country_scope=ESCOPO, medida={})
        finally:
            http.buscar = buscar_real
    finally:
        socket.socket = original
    return objetos, tentativas['n']


if '--reprocessar' in sys.argv:
    ref = sys.argv[sys.argv.index('--reprocessar') + 1]
    objetos, tentativas = reprocessar(ref)
    print('REPROCESS_NETWORK = %d' % tentativas)
    print('OBJETOS           = %d' % len(objetos))
    print(json.dumps(objetos[0] if objetos else {}, ensure_ascii=False, indent=1))
    raise SystemExit(0)

# ── O ENSAIO A SECO DESTA PROVA, CONTRA OS BYTES QUE JA TEMOS ─────────────
# ⚠️ A PRIMEIRA VOLTA DESTA PROVA REBENTOU NUMA SONDA DEPOIS DA CHAMADA REAL.
# A rede foi gasta e o registo perdeu-se por um `TypeError` meu. Uma prova que
# so se descobre partida DEPOIS de sair a rede cobra a rede pelo meu erro.
#
#     UMA PROVA QUE SO SE TESTA AO VIVO TESTA-SE A CUSTA DO HOST.
#
# `--a-seco <raw>` corre o corpo INTEIRO contra bytes preservados, com a rede
# trancada. Serve para validar as assercoes antes de haver um unico pedido.
A_SECO = None
if '--a-seco' in sys.argv:
    A_SECO = sys.argv[sys.argv.index('--a-seco') + 1]
    import socket as _socket
    _corpo_preservado = io.open(os.path.join(RAIZ, A_SECO), encoding='utf-8').read()
    import scrap_http as _http
    _http.buscar = lambda *a, **k: _corpo_preservado
    _original_socket = _socket.socket

    class _Trancado(_original_socket):
        def __init__(s, *a, **k):
            raise RuntimeError('SAIDA DE REDE no ensaio a seco')
    _socket.socket = _Trancado
    MAX_PEDIDOS = 99   # o teto nao e o que este modo mede

print('=' * 88)
print('C10.8A · O PRIMEIRO TRIAL AO VIVO DO SINTONIA SCRAP%s'
      % ('  [ENSAIO A SECO]' if A_SECO else ''))
print('=' * 88)

# ══ ANTES ═════════════════════════════════════════════════════════════════
print('\n── o estado ANTES, medido sem rede ──')
estado_antes = cap.estado(CAPACIDADE)
sha_antes = _sha_da_declaracao()
decisao = mz.decisao(PLATAFORMA, cap.da_matriz(CAPACIDADE))
normal = sx.CHECK(PLATAFORMA, CAPACIDADE)
ensaio = sx.CHECK(PLATAFORMA, CAPACIDADE, modo=sx.TRIAL)
diz(estado_antes == 'NOT_EXECUTED', 'CAPABILITY_STATE', estado_antes)
diz(decisao['DECISAO'] == mz.PERMITIDA_SIM, 'POLICY', decisao['DECISAO'])
diz(decisao['CLASSE'] == 'PUBLIC_NATIVE', 'a rota nao e paga', decisao['CLASSE'])
diz(reg.sonda_de(PLATAFORMA, CAPACIDADE) is None, 'CREDENTIAL_REQUIRED = NO',
    'sem sonda de credencial')
diz(not normal['CAN'], 'CHECK NORMAL recusa', normal['STATE'])
diz(ensaio['CAN'] and ensaio['STATE'] == sx.ELEGIVEL_PARA_ENSAIO,
    'CHECK TRIAL aceita', ensaio['STATE'])
print('  · alvo      %s' % ALVO)
print('  · origem    %s' % ALVO_ORIGEM)
print('  · SHA antes %s' % sha_antes[:16])

# ══ A CHAMADA REAL ════════════════════════════════════════════════════════
print('\n── a chamada REAL, pelo caminho canonico ──')
print('  · teto de pedidos   %d (o portao do robots.txt conta)' % MAX_PEDIDOS)
quando = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
urlopen_real = _contar_e_limitar()
try:
    objetos, trace = sx.COLLECT(platform=PLATAFORMA, capability=CAPACIDADE,
                                run_id='C108A-TRIAL', modo=sx.TRIAL,
                                handle=ALVO, limit=TETO, country_scope=ESCOPO)
finally:
    urllib.request.urlopen = urlopen_real

# ⚠️ O ARTEFATO E ESCRITO ANTES DE QUALQUER ASSERCAO PODER REBENTAR.
# A primeira volta desta prova rebentou numa sonda DEPOIS de a chamada real ter
# corrido — e o registo do que aconteceu na rede perdeu-se com ela.
#
#     UMA CHAMADA REAL QUE NAO DEIXOU REGISTO CUSTOU A REDE E NAO COMPROU NADA.
def _guardar():
    # ⚠️ O ENSAIO A SECO NAO ESCREVE POR CIMA DO REGISTO DA CORRIDA REAL.
    # Escreveu uma vez, e apagou a unica coisa que a rede tinha comprado.
    #
    #     UM ENSAIO A SECO QUE ESCREVE POR CIMA DA CORRIDA REAL APAGA A PROVA.
    nome = '_c108a_ensaio_a_seco.json' if A_SECO else '_c108a_ultima_corrida.json'
    io.open(os.path.join(RAIZ, 'provas', nome), 'w',
            encoding='utf-8').write(json.dumps(
                {'QUANDO': quando, 'ALVO': ALVO, 'ALVO_ORIGEM': ALVO_ORIGEM,
                 'MODO_DA_PROVA': 'A_SECO' if A_SECO else 'AO_VIVO',
                 'TETO_DE_PEDIDOS': MAX_PEDIDOS, 'PEDIDOS': PEDIDOS,
                 'OBJETOS': len(objetos),
                 'TRACE': {k: v for k, v in trace.items() if k != 'CHECK'},
                 'ENVELOPE': objetos[0] if objetos else None},
                ensure_ascii=False, indent=1))


_guardar()
print('  · quando            %s' % quando)
for i, p in enumerate(PEDIDOS, 1):
    print('  · pedido %d          %s' % (i, p['URL'][:70]))
    print('      status=%s bytes=%s ms=%s%s'
          % (p['STATUS'], p['BYTES'], p['MS'],
             ' ERRO=%s' % p['ERRO'] if p['ERRO'] else ''))
diz(len(PEDIDOS) <= MAX_PEDIDOS, 'HTTP_REQUESTS dentro do teto',
    '%d de %d' % (len(PEDIDOS), MAX_PEDIDOS))
diz(A_SECO is not None or any(p['STATUS'] == 200 for p in PEDIDOS),
    'a fonte respondeu 200', str([p['STATUS'] for p in PEDIDOS]) or 'a seco')
diz(bool(objetos), 'OBJECT_COUNT >= 1', str(len(objetos)))
diz(trace.get('RESULT') not in (None, 'ZERO_RESULTS'),
    'o resultado nao e ZERO_RESULTS', str(trace.get('RESULT')))

# ══ O TRACE ═══════════════════════════════════════════════════════════════
print('\n── o trace ──')
for chave in ('EXECUTION_MODE', 'CAPABILITY_STATE_BEFORE',
              'CAPABILITY_STATE_AFTER', 'RESULT', 'ROUTE', 'ROUTE_CLASS',
              'AUTH_MODE', 'PROVIDER_REQUESTED', 'PROVIDER_USED',
              'WHY_FALLBACK', 'PAID_PROVIDER_USED', 'COST_USD',
              'EXECUTOR_ID'):
    print('  · %-26s %s' % (chave, trace.get(chave)))
diz(trace.get('EXECUTION_MODE') == sx.TRIAL, 'EXECUTION_MODE = TRIAL',
    str(trace.get('EXECUTION_MODE')))
diz(trace.get('CAPABILITY_STATE_BEFORE') == 'NOT_EXECUTED',
    'CAPABILITY_STATE_BEFORE', str(trace.get('CAPABILITY_STATE_BEFORE')))
diz(trace.get('CAPABILITY_STATE_AFTER') == estado_antes,
    'CAPABILITY_STATE_AFTER inalterado durante o trial',
    str(trace.get('CAPABILITY_STATE_AFTER')))
diz(float(trace.get('COST_USD') or 0) == 0.0, 'COST_USD = 0 (a matriz declara zero)',
    str(trace.get('COST_USD')))
diz(trace.get('PAID_PROVIDER_USED') is False, 'PAID_PROVIDER_USED = False',
    str(trace.get('PAID_PROVIDER_USED')))
diz('getAuthorFeed' in str(trace.get('ROUTE')), 'ROUTE e a rota real',
    str(trace.get('ROUTE')))
diz(trace.get('ROUTE_CLASS') == 'PUBLIC_NATIVE', 'ROUTE_CLASS',
    str(trace.get('ROUTE_CLASS')))
diz(trace.get('PROVIDER_USED') == trace.get('PROVIDER_REQUESTED')
    or trace.get('WHY_FALLBACK'), 'nao houve fallback silencioso',
    '%s → %s' % (trace.get('PROVIDER_REQUESTED'), trace.get('PROVIDER_USED')))

# ══ NAO PROMOVEU ══════════════════════════════════════════════════════════
print('\n── o trial nao promoveu nada ──')
diz(cap.estado(CAPACIDADE) == estado_antes, 'CAPABILITY_STATE continua',
    cap.estado(CAPACIDADE))
diz(_sha_da_declaracao() == sha_antes, 'o ficheiro da declaracao nao mudou',
    _sha_da_declaracao()[:16])

# ══ RAW PRIMEIRO ══════════════════════════════════════════════════════════
print('\n── o RAW, lido de volta do disco ──')
# ⚠️ `RAW_REFERENCE` NAO E UM CAMINHO. E um dicionario com PATH, SHA256,
# BYTES e o estado de PRESERVACAO — e a primeira versao desta sonda tratou-o
# como string e rebentou DEPOIS de a chamada real ja ter corrido.
#
#     UMA SONDA QUE ASSUME A FORMA DO CAMPO MEDE A ASSUNCAO.
ref = (objetos[0].get('RAW_REFERENCE') if objetos else None) or {}
caminho = os.path.join(RAIZ, ref['PATH']) if ref.get('PATH') else None
print('  · PATH              %s' % ref.get('PATH'))
print('  · SHA256            %s' % ref.get('SHA256'))
print('  · BYTES             %s' % ref.get('BYTES'))
print('  · PRESERVATION      %s' % ref.get('PRESERVATION'))
diz(bool(caminho) and os.path.exists(caminho), 'o RAW existe no disco',
    ('%d bytes' % os.path.getsize(caminho)) if caminho
    and os.path.exists(caminho) else 'ausente')
if caminho and os.path.exists(caminho):
    bruto = io.open(caminho, encoding='utf-8').read()
    diz(_sha(caminho) == ref.get('SHA256'),
        'o SHA do disco bate com o declarado no envelope', _sha(caminho)[:24])
    feed = json.loads(bruto).get('feed') or []
    diz(len(feed) >= 1, 'o RAW contem o feed da fonte', '%d itens' % len(feed))
    diz(len(feed) == len(objetos), 'um objeto por item do RAW',
        '%d raw / %d objetos' % (len(feed), len(objetos)))

# ══ O ENVELOPE ════════════════════════════════════════════════════════════
if objetos:
    print('\n── o envelope de UM objeto ──')
    o = objetos[0]
    for chave in ('PLATFORM', 'NATIVE_ID', 'URL', 'CONTENT_TYPE', 'ROUTE',
                  'RUN_ID', 'COUNTRY_SCOPE', 'SOURCE_ACCOUNT', 'PUBLISHED_AT',
                  'LANGUAGE', 'SOURCE_LOCATION', 'RAW_REFERENCE'):
        print('  · %-18s %s' % (chave, str(o.get(chave))[:64]))
    diz(o.get('PLATFORM') == 'BLUESKY', 'PLATFORM', o.get('PLATFORM'))
    diz(str(o.get('NATIVE_ID') or '').startswith('at://'),
        'NATIVE_ID e a URI real do post', str(o.get('NATIVE_ID'))[:40])
    diz(o.get('CONTENT_TYPE') == 'POST', 'CONTENT_TYPE', o.get('CONTENT_TYPE'))
    diz('getAuthorFeed' in str(o.get('ROUTE')), 'ROUTE e a rota real',
        o.get('ROUTE'))
    diz(o.get('RUN_ID') == 'C108A-TRIAL', 'RUN_ID e o da execucao',
        o.get('RUN_ID'))
    diz(o.get('COUNTRY_SCOPE') == ESCOPO, 'COUNTRY_SCOPE e o pedido',
        o.get('COUNTRY_SCOPE'))
    diz(o.get('SOURCE_ACCOUNT') == ALVO, 'SOURCE_ACCOUNT veio da fonte',
        o.get('SOURCE_ACCOUNT'))
    diz(bool(o.get('PUBLISHED_AT')), 'PUBLISHED_AT veio da fonte',
        o.get('PUBLISHED_AT'))
    # ⚠️ SOURCE_LOCATION NAO E COUNTRY_SCOPE. Um e onde eu PROCUREI; o outro e
    # de onde a coisa E. Confundi-los faz o escopo da busca virar facto.
    diz(o.get('SOURCE_LOCATION') != ESCOPO or o.get('SOURCE_LOCATION') is None,
        'SOURCE_LOCATION nao foi fabricado a partir do escopo',
        str(o.get('SOURCE_LOCATION')))
    diz(o.get('NATIVE_ID') != o.get('URL'), 'NATIVE_ID != URL',
        'sao dois campos')

print('\n' + '=' * 88)
print('TARGET_HANDLE     = %s' % ALVO)
print('HTTP_REQUESTS     = %d  (teto %s, portao do robots incluido)'
      % (len(PEDIDOS), 'n/a a seco' if A_SECO else MAX_PEDIDOS))
# Nao dizer «YES» por habito: no ensaio a seco a rede esteve TRANCADA, e um
# relatorio que diz o contrario e uma prova que mente sobre si propria.
print('NETWORK_REAL      = %s' % ('NO (ensaio a seco)' if A_SECO else 'YES'))
print('CREDENTIALS       = 0')
print('PAID_RUNS         = 0')
print('COST_USD          = %s' % trace.get('COST_USD'))
print('OBJECT_COUNT      = %d' % len(objetos))
print('STATE_PROMOTED_DURING_TRIAL = NO')
print('BLUESKY_TRIAL=%s' % ('PASS' if not FALHAS else 'FAIL'))
for f in FALHAS:
    print('  falhou: %s' % f)
raise SystemExit(0 if not FALHAS else 1)
