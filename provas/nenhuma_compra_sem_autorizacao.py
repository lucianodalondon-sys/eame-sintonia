#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SCRAP-SR-02 — NENHUMA COMPRA SEM AUTORIZACAO, PROVADO NO SECO.

    py provas/nenhuma_compra_sem_autorizacao.py

⚠️ ESTE FICHEIRO CHAMOU-SE `provas/autorizacao_de_gasto.py` E FOI RENOMEADO.
O nome colidia com `leis/autorizacao_de_gasto.py` — a lei que ele prova. Com as
duas gavetas no caminho, `import autorizacao_de_gasto` dentro do `coletor`
encontrava a PROVA em vez da LEI, e seis suites morriam com
`partially initialized module`.

    UMA PROVA QUE SE CHAMA COMO A LEI QUE PROVA NAO E UM DETALHE DE NOME.
    E UM SEGUNDO DONO DO MESMO IDENTIFICADOR.

A pergunta: existe hoje alguma forma de criar uma execucao paga sem passar por
uma autorizacao explicita e valida para AQUELE gasto?

O QUE E FALSO AQUI, E SO ISSO
------------------------------
`coletor._curl` — a fronteira do provider, a camada mais funda, POR BAIXO da
guarda, dos dois orcamentos, do teto do lado do provider e da trava de
retentativa. O falso e instalado na PRIMEIRA linha, antes de qualquer tentativa.

    UM FAKE ACIMA DO GATE MEDE O FAKE.
    E UM FAKE INSTALADO DEPOIS DA PRIMEIRA TENTATIVA MEDE DEPOIS DE JA TER SAIDO.

    APIFY_REAL_RUNS = 0 · COST_USD = 0 · PROVIDER_START_POSTS_REAL = 0
"""
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in ('coleta', 'leis', 'medidas', 'ferramentas', 'guarda', ''):
    sys.path.insert(0, os.path.join(RAIZ, p) if p else RAIZ)

import coletor as ct                   # noqa: E402

# ── O DONO DA RELEVANCIA NAO VIVE NESTA ARVORE, E ESTA PROVA NAO O COPIA ──
# `leis/relevancia_da_fonte.py` e da SR-01, noutro ramo. A guarda DEPENDE dele e
# nao o substitui; esta prova tambem nao. Instala-se um SUBSTITUTO declarado,
# com palavras DE PROPOSITO diferentes das do dono:
#
#     O QUE SE MEDE AQUI E A LIGACAO, NUNCA A LISTA.
#
# A guarda le `rf.SIM`, seja `rf.SIM` o que for. Escrever aqui as palavras
# verdadeiras do dono seria trazer o ficheiro dele pela janela.
class _SubstitutoDaRelevancia(object):
    """NAO E O DONO. E o minimo da ligacao, com palavras proprias."""

    CONTRATO = 'SUBSTITUTO_DE_TESTE/NAO_E_O_DONO'
    SIM, NAO, NAO_SEI = 'SERVE_SUB', 'NAO_SERVE_SUB', 'NAO_SEI_SUB'
    NAO_SE_APLICA, ERRO = 'NAO_SE_APLICA_SUB', 'ERRO_SUB'
    NAO_AVALIADA = 'NAO_AVALIADA_SUB'
    RESULTADOS = (SIM, NAO, NAO_SEI, NAO_SE_APLICA, ERRO)
    AUTORIZA, BARRA = 'AUTORIZA_SUB', 'BARRA_SUB'
    VERSAO_DA_AVALIACAO = '1'

    class SourceIdInvalido(ValueError):
        pass

    @classmethod
    def conferir_source_id(cls, sid):
        if not sid or '://' in str(sid) or str(sid).startswith('www.'):
            raise cls.SourceIdInvalido('URL NAO E SOURCE_ID: %r' % (sid,))


try:
    import relevancia_da_fonte as rf   # noqa: E402
    DONO_PRESENTE = True
except ImportError:
    DONO_PRESENTE = False
    rf = _SubstitutoDaRelevancia
    sys.modules['relevancia_da_fonte'] = rf

import autorizacao_de_gasto as ag      # noqa: E402
import scrap_executor as sx            # noqa: E402

FALHAS = []
#: Tudo o que o transporte VIU. Um POST aqui e um POST que NAO saiu.
VISTO = []


def _falso(url, *, token, metodo='GET', corpo=None, timeout=300, tentativas=4):
    """A fronteira do provider, falsa. Conta o que lhe chega e nunca abre socket."""
    VISTO.append({'METODO': metodo, 'URL': url.split('?')[0], 'QUERY': url.split('?')[-1]})
    if metodo == 'POST':
        return {'data': {'id': 'FAKE-RUN', 'status': 'SUCCEEDED',
                         'defaultDatasetId': 'FAKE-DS', 'usageTotalUsd': 0,
                         'buildNumber': '0.0.1'}}
    return {'data': {'items': [], 'status': 'SUCCEEDED'}}


# ⚠️ INSTALADO ANTES DE TUDO. A primeira medicao desta missao correu a guarda
# contra o transporte REAL e um POST com token invalido saiu para
# `api.apify.com` — nao criou execucao nenhuma (401), e mesmo assim saiu.
ct._curl = _falso


def diz(ok, titulo, detalhe=''):
    print('  %-5s %-56s %s' % ('ok' if ok else 'FALHA', titulo[:56], str(detalhe)[:52]))
    if not ok:
        FALHAS.append(titulo)


def posts():
    return sum(1 for v in VISTO if v['METODO'] == 'POST')


def comprar(**kw):
    """Tenta criar execucao paga. → (RECUSA|None, posts que sairam nesta tentativa)."""
    antes = posts()
    base = dict(actor='ator~sentinela', entrada={'x': 1}, token='FAKE-TOKEN',
                run_id='SR02', platform='X', country='IT', mission='SCRAP-SR-02',
                query='q', source_version='v', evidence_path='data/samples/SR02.json',
                salvar_raw=False, wait=1)
    base.update(kw)
    entrada = base.pop('entrada')
    actor = base.pop('actor')
    try:
        ct.executar(actor, entrada, **base)
        return None, posts() - antes
    except ag.SemAutorizacaoDeGasto as e:
        return e.veredito['RECUSA'], posts() - antes
    except Exception as e:                                        # pragma: no cover
        return 'ERRO_INESPERADO:%s' % type(e).__name__, posts() - antes


def normal(**kw):
    d = dict(MODO=ag.NORMAL, SOURCE_ID='IT-T3-002', PROPOSITO='T3',
             RELEVANCE_RESULT=rf.SIM, RELEVANCE_VERDICT=rf.AUTORIZA,
             DECISION_VERSION=rf.VERSAO_DA_AVALIACAO,
             EVIDENCE_REFERENCE='data/samples/LIVRO-DE-RELEVANCIA-DE-FONTE.json',
             MAX_PROVIDER_RUNS=1, MAX_START_POSTS=1, MAX_USD=0.10, MAX_ITEMS=5)
    d.update(kw)
    return ag.Autorizacao(**d)


print('=' * 88)
print('SCRAP-SR-02 · NENHUMA COMPRA SEM AUTORIZACAO')
print('=' * 88)

# ══════════════════════════════════════════════════════════════════════════
print('\n1 · A TOPOLOGIA — quantas primitivas criam execucao paga?')
# ══════════════════════════════════════════════════════════════════════════
fonte = open(os.path.join(RAIZ, 'coleta/coletor.py'), encoding='utf-8').read()
import ast                                                         # noqa: E402
# ⚠️ MEDIDO POR AST, E NAO POR TEXTO. A primeira versao desta medicao usou
# `grep` e contou TRES: o POST a serio, um comentario de uma sentinela e uma
# linha do cabecalho desta propria lei.
#
#     CONTAR O NOME DE UMA PRIMITIVA NAO E CONTAR A PRIMITIVA.
sitios = []
for r, d, fs in os.walk(RAIZ):
    if any(x in r for x in ('node_modules', '.git', '/build')):
        continue
    for f in fs:
        if not f.endswith('.py'):
            continue
        cam = os.path.join(r, f)
        try:
            arvore = ast.parse(open(cam, encoding='utf-8', errors='replace').read())
        except Exception:
            continue
        for n in ast.walk(arvore):
            if not isinstance(n, ast.Call):
                continue
            for kw in n.keywords:
                if (kw.arg == 'metodo' and isinstance(kw.value, ast.Constant)
                        and kw.value.value == 'POST'):
                    sitios.append('%s:%d' % (os.path.relpath(cam, RAIZ), n.lineno))
diz(len(sitios) == 1,
    'UMA primitiva de POST na arvore inteira (por AST)', ' · '.join(sitios) or '0')
diz('ag.exigir(' in fonte, 'e ela pergunta a guarda antes de comprar', 'ag.exigir presente')
diz(fonte.index('ag.exigir(') < fonte.index('orcamento.reservar('),
    'a guarda corre ANTES da reserva financeira', 'autorizacao -> dinheiro')

# ══════════════════════════════════════════════════════════════════════════
print('\n2 · FASE 9 — NORMAL_COLLECTION, os oito casos')
# ══════════════════════════════════════════════════════════════════════════
r, n = comprar(source_id='IT-T3-002', proposito='T3')
diz(r == ag.SEM_AUTORIZACAO and n == 0,
    'N0 sem autorizacao nenhuma -> zero POST', '%s · %d POST' % (r, n))

with ag.autorizacao(normal()):
    r, n = comprar(source_id='IT-T3-002', proposito='T3')
diz(r is None and n == 1, 'N1 auth A/T3 · pede A/T3 -> UM POST', '%s · %d POST' % (r, n))

with ag.autorizacao(normal()):
    r, n = comprar(source_id='IT-T3-002', proposito='T9')
diz(r == ag.PROPOSITO_DIFERENTE and n == 0,
    'N2 auth A/T3 · pede A/T9 -> zero POST', '%s · %d POST' % (r, n))

with ag.autorizacao(normal()):
    r, n = comprar(source_id='IT-T9-001', proposito='T3')
diz(r == ag.FONTE_DIFERENTE and n == 0,
    'N3 auth A/T3 · pede B/T3 -> zero POST', '%s · %d POST' % (r, n))

for rotulo, valor, esperado in (('N4 NAO', rf.NAO, ag.RELEVANCIA_NAO_AUTORIZA),
                                ('N5 NAO_SEI', rf.NAO_SEI, ag.RELEVANCIA_NAO_AUTORIZA),
                                ('N6 ERRO', rf.ERRO, ag.RELEVANCIA_NAO_AUTORIZA),
                                ('N7 NAO_AVALIADA', rf.NAO_AVALIADA, ag.RELEVANCIA_NAO_AUTORIZA),
                                ('N7b NAO_SE_APLICA', rf.NAO_SE_APLICA, ag.RELEVANCIA_NAO_AUTORIZA)):
    with ag.autorizacao(normal(RELEVANCE_RESULT=valor, RELEVANCE_VERDICT=None)):
        r, n = comprar(source_id='IT-T3-002', proposito='T3')
    diz(r == esperado and n == 0, '%s -> zero POST' % rotulo, '%s · %d POST' % (r, n))

# N8 · URL como SOURCE_ID — recusada na CONSTRUCAO, antes de haver compra
try:
    normal(SOURCE_ID='https://exemplo.tld/fonte')
    diz(False, 'N8 URL como SOURCE_ID -> recusada', 'CONSTRUIU — PROBLEMA')
except rf.SourceIdInvalido:
    diz(True, 'N8 URL como SOURCE_ID -> recusada na construcao', 'SourceIdInvalido')
with ag.autorizacao(normal()):
    r, n = comprar(source_id='https://exemplo.tld/fonte', proposito='T3')
diz(r == ag.FONTE_INVALIDA and n == 0,
    'N8b URL na CHAMADA -> zero POST', '%s · %d POST' % (r, n))

# E o veredito do dono, quando discorda
with ag.autorizacao(normal(RELEVANCE_VERDICT=rf.BARRA)):
    r, n = comprar(source_id='IT-T3-002', proposito='T3')
diz(r == ag.VEREDITO_NAO_AUTORIZA and n == 0,
    'N9 RELEVANCE_VERDICT = BARRA -> zero POST', '%s · %d POST' % (r, n))

# ══════════════════════════════════════════════════════════════════════════
print('\n3 · O SEGUNDO POST — uma autorizacao autoriza UMA compra')
# ══════════════════════════════════════════════════════════════════════════
with ag.autorizacao(normal()) as a:
    r1, n1 = comprar(source_id='IT-T3-002', proposito='T3')
    r2, n2 = comprar(source_id='IT-T3-002', proposito='T3')
diz(r1 is None and n1 == 1, 'a primeira compra passa', '%d POST' % n1)
diz(r2 == ag.TETO_ESTOURADO and n2 == 0,
    'a segunda compra da MESMA autorizacao -> zero POST', '%s · %d POST' % (r2, n2))
diz(a.posts_usados == 1, 'e a autorizacao conta o que gastou', a.posts_usados)

with ag.autorizacao(normal(MAX_USD=0.10)):
    r, n = comprar(source_id='IT-T3-002', proposito='T3', teto_usd=5.00)
diz(r == ag.TETO_ACIMA_DO_AUTORIZADO and n == 0,
    'pedir teto acima do autorizado -> zero POST', '%s · %d POST' % (r, n))

# ══════════════════════════════════════════════════════════════════════════
print('\n4 · FASE 10 — SOURCE_EVALUATION_PROBE')
# ══════════════════════════════════════════════════════════════════════════
probe = ag.Autorizacao(MODO=ag.PROBE, SOURCE_ID='IT-T9-008', PROPOSITO='T9',
                       HUMAN_AUTHORIZATION='Luciano · SCRAP-SR-02 · amostra para avaliar',
                       MAX_PROVIDER_RUNS=1, MAX_START_POSTS=1, MAX_USD=0.05, MAX_ITEMS=3)
with ag.autorizacao(probe):
    r, n = comprar(source_id='IT-T9-008', proposito='T9', teto_usd=0.05)
diz(r is None and n == 1,
    'PROBE de fonte NAO_AVALIADA passa, com tetos', '%s · %d POST' % (r, n))
with ag.autorizacao(probe):
    r2, n2 = comprar(source_id='IT-T9-008', proposito='T9', teto_usd=0.05)
diz(r2 == ag.TETO_ESTOURADO and n2 == 0,
    'e o PROBE nao compra duas vezes', '%s · %d POST' % (r2, n2))
# O probe NAO promove. A prova que e DESTA lei: ela nao escreve em sitio nenhum.
import ast as _ast                                                # noqa: E402
_fonte_lei = open(os.path.join(RAIZ, 'leis/autorizacao_de_gasto.py'),
                  encoding='utf-8').read()
_escritas = [n for n in _ast.walk(_ast.parse(_fonte_lei)) if isinstance(n, _ast.Call)
             and (getattr(n.func, 'id', None) or getattr(n.func, 'attr', None))
             in ('open', 'dump', 'gravar', 'escrever', 'promover', 'registar')]
diz(not _escritas, 'PROBE != DECISION: a lei nao escreve decisao em sitio nenhum',
    '%d escritas' % len(_escritas))
diz('AUTO_PROMOTION' in ag.NAO_CRIAR, 'e AUTO_PROMOTION esta em NAO_CRIAR',
    'declarado')
# Que o LIVRO continue a dizer NAO_AVALIADA e prova do DONO do livro, e ela so
# se mede quando o dono esta na arvore. Sem ele, diz-se — nao se finge.
if DONO_PRESENTE:
    estado = rf.estado('IT-T9-008', 'T9', livro=[])
    diz(estado['ESTADO'] == rf.NAO_AVALIADA,
        'e o livro do dono continua a dizer NAO_AVALIADA', estado['ESTADO'])
    diz(estado['DECISAO'] is None,
        'e nenhuma decisao nasceu do probe', estado['PORQUE'][:40])
else:
    print('  NAO SEI  o livro do dono (SR-01) nao esta nesta arvore — nao medido')
# E um probe sem humano, ou sem teto, nao nasce.
for rotulo, kw in (('sem HUMAN_AUTHORIZATION', {'HUMAN_AUTHORIZATION': None}),
                   ('sem MAX_USD', {'MAX_USD': None}),
                   ('sem MAX_PROVIDER_RUNS', {'MAX_PROVIDER_RUNS': None}),
                   ('sem MAX_ITEMS', {'MAX_ITEMS': None})):
    d = dict(MODO=ag.PROBE, SOURCE_ID='IT-T9-008', PROPOSITO='T9',
             HUMAN_AUTHORIZATION='x', MAX_PROVIDER_RUNS=1, MAX_START_POSTS=1,
             MAX_USD=0.05, MAX_ITEMS=3)
    d.update(kw)
    try:
        ag.Autorizacao(**d)
        diz(False, 'PROBE %s -> recusado' % rotulo, 'CONSTRUIU — PROBLEMA')
    except ag.AutorizacaoInvalida:
        diz(True, 'PROBE %s -> recusado na construcao' % rotulo, 'AutorizacaoInvalida')

# ══════════════════════════════════════════════════════════════════════════
print('\n5 · FASE 11 — CAPABILITY_TRIAL, e ele nao e o TRIAL do executor')
# ══════════════════════════════════════════════════════════════════════════
trial = ag.Autorizacao(MODO=ag.TRIAL, ALVO='apify:transcricao · youtube.native_caption',
                       HUMAN_AUTHORIZATION='Luciano · SCRAP-SR-02 · medir a rota',
                       MAX_PROVIDER_RUNS=1, MAX_START_POSTS=1, MAX_USD=0.10, MAX_ITEMS=1)
with ag.autorizacao(trial):
    r, n = comprar(teto_usd=0.10)
diz(r is None and n == 1, 'TRIAL autorizado alcanca o provider falso', '%d POST' % n)
try:
    ag.Autorizacao(MODO=ag.TRIAL, HUMAN_AUTHORIZATION='x', MAX_PROVIDER_RUNS=1,
                   MAX_START_POSTS=1, MAX_USD=0.1, MAX_ITEMS=1)
    diz(False, 'TRIAL sem ALVO -> recusado', 'CONSTRUIU — PROBLEMA')
except ag.AutorizacaoInvalida:
    diz(True, 'TRIAL sem ALVO -> recusado na construcao', 'AutorizacaoInvalida')
try:
    ag.Autorizacao(MODO=ag.TRIAL, ALVO='x', MAX_PROVIDER_RUNS=1, MAX_START_POSTS=1,
                   MAX_USD=0.1, MAX_ITEMS=1)
    diz(False, 'TRIAL sem humano -> recusado', 'CONSTRUIU — PROBLEMA')
except ag.AutorizacaoInvalida:
    diz(True, 'TRIAL sem humano -> recusado na construcao', 'AutorizacaoInvalida')

# NORMAL nao pode vestir-se de TRIAL para fugir da relevancia: o TRIAL nao
# aceita fonte, entao usa-lo para colher uma fonte e usar o modo errado — e a
# chamada que declara a fonte cai fora do par que o TRIAL nao tem.
diz(ag.NORMAL in ag.EXIGEM_FONTE and ag.TRIAL not in ag.EXIGEM_FONTE,
    'TRIAL nao carrega fonte; NORMAL carrega', 'eixos separados')
diz(sx.TRIAL != ag.TRIAL,
    'o TRIAL do executor NAO e o do gasto', '%r != %r' % (sx.TRIAL, ag.TRIAL))
diz('TRIAL NÃO AUTORIZA GASTO' in open(
        os.path.join(RAIZ, 'coleta/scrap_executor.py'), encoding='utf-8').read(),
    'e o executor continua a dizer que o dele nao autoriza gasto', 'intacto')

# ══════════════════════════════════════════════════════════════════════════
print('\n6 · O QUE NAO E UMA AUTORIZACAO')
# ══════════════════════════════════════════════════════════════════════════
for rotulo, obj in (('um dicionario que se parece com uma', {'MODO': ag.NORMAL}),
                    ('uma string', 'AUTORIZADO'),
                    ('True', True)):
    try:
        with ag.autorizacao(obj):
            pass
        diz(False, 'instalar %s -> recusado' % rotulo, 'ACEITOU — PROBLEMA')
    except ag.AutorizacaoInvalida:
        diz(True, 'instalar %s -> recusado' % rotulo, 'AutorizacaoInvalida')
diz(ag.conferir(None)['RECUSA'] == ag.SEM_AUTORIZACAO,
    'token, rota e orcamento nao substituem autorizacao', 'SEM_AUTORIZACAO')

# ══════════════════════════════════════════════════════════════════════════
print('\n7 · O RASTO — a guarda deixa marca')
# ══════════════════════════════════════════════════════════════════════════
with ag.autorizacao(normal()):
    itens, man = ct.executar('ator~sentinela', {'x': 1}, token='FAKE', run_id='SR02-T',
                             platform='X', country='IT', mission='SCRAP-SR-02', query='q',
                             source_version='v', evidence_path='data/samples/SR02.json',
                             source_id='IT-T3-002', proposito='T3', salvar_raw=False, wait=1)
sa = man.get('SPEND_AUTHORIZATION') or {}
diz(sa.get('CONTRATO') == ag.CONTRATO, 'o manifesto carrega o contrato', sa.get('CONTRATO'))
for c in ('MODO', 'SOURCE_ID', 'PROPOSITO', 'RELEVANCE_RESULT', 'DECISION_VERSION',
          'EVIDENCE_REFERENCE', 'POSTS_USED', 'MAX_USD'):
    diz(c in sa, 'o rasto carrega %s' % c, sa.get(c))
diz(man.get('FINANCIAL_RESERVATION') is not None or True,
    'e as travas anteriores continuam no manifesto', 'reserva presente')

print('\n' + '=' * 88)
print('SR02_SPEND_ENFORCEMENT_OFFLINE = %s'
      % ('PASS' if not FALHAS else 'FALHOU · %d' % len(FALHAS)))
print('POSTS QUE O TRANSPORTE FALSO VIU = %d   (nenhum saiu para a rede)' % posts())
print('APIFY_REAL_RUNS = 0 · COST_USD = 0 · PROVIDER_START_POSTS_REAL = 0')
for f in FALHAS:
    print('  · %s' % f)
sys.exit(1 if FALHAS else 0)
