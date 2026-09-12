#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RED TEAM DA AUTORIZACAO DE GASTO — 37 ataques ao dinheiro, e todos tem de morrer.

    py provas/red_team_da_autorizacao_de_gasto.py

    UM PORTAO QUE SO APROVA NAO E UM PORTAO.

Cada ataque aqui e uma maneira concreta de fazer esta casa COMPRAR sem que
ninguem tenha autorizado a compra — ou de fazer uma recusa de autorizacao
parecer um juizo sobre a fonte.

    ATAQUE_MORTO   o sistema recusou    -> bom
    ATAQUE_VIVO    o ataque comprou     -> a porta nao serve

O fornecedor e fingido SO na fronteira externa: um espiao que CONTA os POST e
nunca abre ligacao. Tudo o resto e o codigo real.

    APIFY_REAL_RUNS = 0 · PROVIDER_START_POSTS_REAL = 0 · REAL_COST_USD = 0
"""

from __future__ import annotations

import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(_HERE)
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401

import autorizacao_de_gasto as ag        # noqa: E402
import relevancia_da_fonte as rel        # noqa: E402
import coletor                           # noqa: E402
import censo_das_portas_de_gasto as censo  # noqa: E402

ATAQUES = []


def ataque(codigo, nome):
    def deco(f):
        ATAQUES.append((codigo, nome, f))
        return f
    return deco


def _decisao(sid, prop, resultado, **kw):
    kw.setdefault('motivo', 'red team')
    kw.setdefault('metodo', 'RED_TEAM')
    if resultado in rel.RESULTADOS_QUE_AFIRMAM:
        kw.setdefault('evidencia', {'file': 'x', 'line': 1})
    return rel.Decisao(source_id=sid, proposito=prop, resultado=resultado,
                       **kw).para_livro()


class Espiao:
    """O fornecedor, fingido SO na fronteira. Conta POST; nunca sai da maquina."""

    def __init__(self):
        self.posts = 0

    def __call__(self, url, *, token, metodo='GET', corpo=None, timeout=300,
                 tentativas=4):
        if str(metodo).upper() == 'POST':
            self.posts += 1
            return {'data': {'id': 'FAKE', 'status': 'SUCCEEDED',
                             'startedAt': '2026-09-12T00:00:00.000Z',
                             'finishedAt': '2026-09-12T00:00:01.000Z',
                             'defaultDatasetId': 'DS', 'buildNumber': '1',
                             'usageTotalUsd': 0.0}}
        return [] if '/datasets/' in url else {'data': {}}


def _comprar(autorizacao, **kw):
    """Tenta comprar pela porta real. → numero de POST que sairam."""
    e = Espiao()
    antes = coletor._curl
    coletor._curl = e
    try:
        base = dict(token='T', run_id='R', platform='P', country='IT',
                    mission='M', query='q', source_version='v',
                    evidence_path='e', salvar_raw=False,
                    autorizacao=autorizacao,
                    proposito=getattr(autorizacao, 'proposito', None),
                    source_id=getattr(autorizacao, 'source_id', None),
                    motivo_do_gasto=getattr(autorizacao, 'motivo', None),
                    teto_usd=getattr(autorizacao, 'max_usd', None))
        base.update(kw)
        try:
            coletor.executar('apify~ator', {}, **base)
        except (ag.GastoRecusado, ag.AutorizacaoInvalida):
            pass
    finally:
        coletor._curl = antes
    return e.posts


def _normal(livro, sid='IT-T9-002', prop='T9'):
    return ag.autorizar(motivo=ag.COLETA_NORMAL, proposito=prop, source_id=sid,
                        max_usd=0.05, livro=livro)


# ══════════════════════════════════════════════════════════════════════════
# 1-2 · OS CAMINHOS DIRECTOS
# ══════════════════════════════════════════════════════════════════════════
@ataque('RT-01', 'script directo compra sem decisao de relevancia')
def rt01():
    return _comprar(None) == 0, 'zero POST sem autorizacao'


@ataque('RT-02', 'workflow chama o script COM token e compra sem relevancia')
def rt02():
    """⚠️ A PRIMEIRA VERSAO DESTE ATAQUE CORREU SEM TOKEN, E NAO PROVAVA NADA.

    Sem chave no ambiente, `apify_pool.pool()` volta vazio e
    `executar_com_pool` nem chega a chamar o trabalho: nao se gasta porque nao
    ha com que gastar, e a guarda nunca e exercida.

        NAO TER CHAVE NAO E TER PORTAO.

    O ataque real poe uma chave no ambiente — falsa, e nunca usada, porque o
    transporte esta substituido por um espiao que conta POST e nao abre
    ligacao. Assim mede-se o que interessa: com credencial na mao, o caminho
    do workflow consegue comprar?
    """
    import subprocess
    codigo = (
        'import sys, os; sys.path.insert(0, "."); import _gavetas, coletor;\n'
        'saiu = {"posts": 0}\n'
        'def espiao(url, *, token, metodo="GET", corpo=None, timeout=300, tentativas=4):\n'
        '    if str(metodo).upper() == "POST": saiu["posts"] += 1\n'
        '    return [] if "/datasets/" in url else {"data": {}}\n'
        'coletor._curl = espiao\n'
        'import comunicacao_coleta as cc\n'
        # o artefato de saida nao entra na medicao: o ataque conta POST, e um
        # ficheiro deixado na arvore faria a corrida seguinte medir esta.
        'cc._gravar = lambda *a, **k: "(ataque: nao gravado)"\n'
        'try: cc.fase_posts("INSTAGRAM")\n'
        'except Exception as e: print("RECUSOU:", type(e).__name__, e)\n'
        'print("POSTS_QUE_SAIRAM=%d" % saiu["posts"])')
    chave = 'apify_api_' + 'x' * 36
    r = subprocess.run([sys.executable, '-c', codigo], cwd=RAIZ,
                       capture_output=True, text=True, timeout=300,
                       env=dict(os.environ, APIFY_TOKEN=chave))
    saida = r.stdout + r.stderr
    return 'POSTS_QUE_SAIRAM=0' in saida, saida.strip().splitlines()[-1][:150] if saida.strip() else 'sem saida'


# ══════════════════════════════════════════════════════════════════════════
# 3-7 · CREDENCIAL, E AS QUATRO AUSENCIAS
# ══════════════════════════════════════════════════════════════════════════
@ataque('RT-03', 'token presente vale como autorizacao')
def rt03():
    # a chamada leva token e NAO leva autorizacao
    return _comprar(None, token='apify_api_' + 'x' * 36) == 0, \
        'CREDENTIAL != AUTHORIZATION'


@ataque('RT-04', 'SIM para T3 usado para comprar em T9')
def rt04():
    livro = [_decisao('IT-T9-002', 'T3', rel.SIM)]
    try:
        a = _normal(livro, prop='T9')
    except ag.AutorizacaoInvalida:
        return True, 'a autorizacao nem chega a nascer'
    return _comprar(a) == 0, 'a autorizacao nasceu — isso ja e falha'


@ataque('RT-05', 'NAO_SEI tratado como SIM')
def rt05():
    livro = [_decisao('IT-T9-002', 'T9', rel.NAO_SEI)]
    try:
        _normal(livro)
        return False, 'NAO_SEI autorizou gasto'
    except ag.AutorizacaoInvalida as e:
        return rel.NAO_SEI in str(e), 'recusou, e o estado continua NAO_SEI'


@ataque('RT-06', 'ERRO tratado como SIM')
def rt06():
    livro = [_decisao('IT-T9-002', 'T9', rel.ERRO)]
    try:
        _normal(livro)
        return False, 'ERRO autorizou gasto'
    except ag.AutorizacaoInvalida as e:
        return rel.ERRO in str(e), 'recusou, e continua a ser ERRO'


@ataque('RT-07', 'NAO_AVALIADA tratada como SIM')
def rt07():
    try:
        _normal([])
        return False, 'fonte que ninguem abriu autorizou gasto'
    except ag.AutorizacaoInvalida as e:
        return rel.NAO_AVALIADA in str(e), 'recusou, e nao chamou a fonte de irrelevante'


# ══════════════════════════════════════════════════════════════════════════
# 8-9 · A IDENTIDADE DA FONTE
# ══════════════════════════════════════════════════════════════════════════
@ataque('RT-08', 'URL usada como SOURCE_ID na autorizacao')
def rt08():
    try:
        ag.autorizar(motivo=ag.COLETA_NORMAL, proposito='T9',
                     source_id='https://instagram.com/basf', livro=[])
        return False, 'aceitou URL como identidade'
    except (rel.SourceIdInvalido, ag.AutorizacaoInvalida):
        return True, 'URL NAO E SOURCE_ID (COL-LAW-206)'


@ataque('RT-09', 'source id fabricado a partir do URL no probe')
def rt09():
    mortos = 0
    for u in ('https://x.it', 'www.x.it', 'a/b'):
        try:
            ag.autorizar(motivo=ag.PROVA_DE_RELEVANCIA, proposito='T9',
                         source_id=u, max_execucoes=1, max_usd=0.01,
                         quem_autorizou='x', porque='y', condicao_de_paragem='z')
        except (rel.SourceIdInvalido, ag.AutorizacaoInvalida):
            mortos += 1
    return mortos == 3, '%d de 3 recusadas' % mortos


# ══════════════════════════════════════════════════════════════════════════
# 10-13 · SUBSTITUICOES INDEVIDAS
# ══════════════════════════════════════════════════════════════════════════
@ataque('RT-10', 'fornecedor pago como override de politica')
def rt10():
    fonte = open(os.path.join(RAIZ, 'leis', 'autorizacao_de_gasto.py'),
                 encoding='utf-8').read()
    return ('PAID_PROVIDER != POLICY_OVERRIDE' in fonte
            and _comprar(None) == 0), 'pagar nao compra excepcao'


@ataque('RT-11', 'orcamento presente substitui a relevancia')
def rt11():
    try:
        ag.autorizar(motivo=ag.COLETA_NORMAL, proposito='T9',
                     source_id='IT-T9-002', max_usd=999.0, max_execucoes=99,
                     quem_autorizou='tesouraria', porque='ha dinheiro',
                     condicao_de_paragem='acabar o dinheiro', livro=[])
        return False, 'ter orcamento comprou sem decisao de fonte'
    except ag.AutorizacaoInvalida as e:
        return 'RELEVANCIA_NAO_AUTORIZA' in str(e), 'dinheiro nao substitui decisao'


@ataque('RT-12', 'relevancia SIM substitui a politica de rota')
def rt12():
    """SIM autoriza o GASTO; nao autoriza a rota nem dispensa o teto."""
    livro = [_decisao('IT-T9-002', 'T9', rel.SIM)]
    a = _normal(livro)
    # sem teto no fornecedor, a compra nao sai mesmo com SIM
    return _comprar(a, teto_usd=None) == 0, 'SIM nao dispensa o teto do fornecedor'


@ataque('RT-13', 'rota gratuita passa a exigir autorizacao paga')
def rt13():
    """A guarda vive na porta PAGA. Rota de graca nao a atravessa.

    Se exigisse, a casa deixaria de conseguir observar de graca — e o portao
    da SR-01 passaria a dizer «nao» a tudo o que nao tem decisao.
    """
    import inspect
    import social_rotas as sr
    p = set(inspect.signature(sr._executar).parameters)
    fonte = open(os.path.join(RAIZ, 'coleta', 'social_rotas.py'),
                 encoding='utf-8').read()
    return ('autorizacao' not in p and 'autorizacao_de_gasto' not in fonte), \
        'a rota livre continua livre'


# ══════════════════════════════════════════════════════════════════════════
# 14-19 · O PROBE E O TRIAL
# ══════════════════════════════════════════════════════════════════════════
@ataque('RT-14', 'probe de avaliacao bloqueado por nao ter SIM')
def rt14():
    """O ataque ao contrario: se o probe exigisse SIM, o ciclo fechava."""
    a = ag.autorizar(motivo=ag.PROVA_DE_RELEVANCIA, proposito='T9',
                     source_id='IT-T9-002', max_execucoes=1, max_usd=0.01,
                     quem_autorizou='luciano', porque='descobrir se serve',
                     condicao_de_paragem='1 execucao')
    return _comprar(a) == 1, 'o probe atravessa com a fonte ainda NAO_AVALIADA'


@ataque('RT-15', 'probe vira coleta ilimitada')
def rt15():
    a = ag.autorizar(motivo=ag.PROVA_DE_RELEVANCIA, proposito='T9',
                     source_id='IT-T9-002', max_execucoes=1, max_usd=0.01,
                     quem_autorizou='l', porque='p', condicao_de_paragem='1')
    total = _comprar(a) + _comprar(a) + _comprar(a)
    return total == 1, '%d POST em 3 tentativas' % total


@ataque('RT-16', 'probe sem teto de execucoes')
def rt16():
    try:
        ag.autorizar(motivo=ag.PROVA_DE_RELEVANCIA, proposito='T9',
                     source_id='IT-T9-002', max_usd=0.01, quem_autorizou='l',
                     porque='p', condicao_de_paragem='1')
        return False, 'probe sem teto de execucoes foi concedido'
    except ag.AutorizacaoInvalida as e:
        return 'SEM_TETO_DE_EXECUCOES' in str(e), str(e)[:60]


@ataque('RT-17', 'probe sem teto de dolares')
def rt17():
    try:
        ag.autorizar(motivo=ag.PROVA_DE_RELEVANCIA, proposito='T9',
                     source_id='IT-T9-002', max_execucoes=1, quem_autorizou='l',
                     porque='p', condicao_de_paragem='1')
        return False, 'cheque em branco concedido'
    except ag.AutorizacaoInvalida as e:
        return 'SEM_TETO_DE_DOLARES' in str(e), str(e)[:60]


@ataque('RT-18', 'capability trial vira coleta normal')
def rt18():
    a = ag.autorizar(motivo=ag.TRIAL_DE_CAPACIDADE, proposito='T9',
                     max_execucoes=1, max_usd=0.10, quem_autorizou='l',
                     porque='provar a rota', condicao_de_paragem='um POST')
    return _comprar(a, motivo_do_gasto=ag.COLETA_NORMAL) == 0, \
        'TRIAL != COLLECTION'


@ataque('RT-19', 'coleta normal chama-se TRIAL para contornar')
def rt19():
    livro = [_decisao('IT-T9-002', 'T9', rel.SIM)]
    a = _normal(livro)
    return _comprar(a, motivo_do_gasto=ag.TRIAL_DE_CAPACIDADE) == 0, \
        'o motivo declarado tem de bater com o autorizado'


# ══════════════════════════════════════════════════════════════════════════
# 20-25 · QUEM ASSINA
# ══════════════════════════════════════════════════════════════════════════
@ataque('RT-20', 'workflow inventa a propria autorizacao')
def rt20():
    falsa = type('A', (), {'motivo': ag.COLETA_NORMAL, 'proposito': 'T9',
                           'source_id': 'IT-T9-002', 'max_usd': 99.0,
                           'restantes': 99})()
    return _comprar(falsa) == 0, 'objecto parecido nao passa o selo'


@ataque('RT-21', 'adapter inventa a propria autorizacao')
def rt21():
    try:
        ag.Autorizacao(motivo=ag.COLETA_NORMAL, proposito='T9',
                       source_id='IT-T9-002', max_execucoes=9, max_usd=9.0,
                       quem_autorizou='eu', porque='x', condicao_de_paragem='y')
        return False, 'construtor aceitou sem o selo'
    except ag.AutorizacaoInvalida:
        return True, 'so autorizar() consegue emitir'


@ataque('RT-22', 'apify_pool passa a decidir relevancia')
def rt22():
    fonte = open(os.path.join(RAIZ, 'ferramentas', 'apify_pool.py'),
                 encoding='utf-8').read()
    proibidos = [p for p in ('relevancia_da_fonte', 'LIVRO-DE-RELEVANCIA',
                             'SOURCE_RELEVANCE', 'autorizacao_de_gasto')
                 if p in fonte]
    return not proibidos, 'o dono da chave continua so dono da chave'


@ataque('RT-23', 'coletor passa a decidir relevancia')
def rt23():
    fonte = open(os.path.join(RAIZ, 'coleta', 'coletor.py'), encoding='utf-8').read()
    proibidos = [p for p in ('import relevancia_da_fonte', 'LIVRO-DE-RELEVANCIA',
                             'rel.portao') if p in fonte]
    return not proibidos, 'a porta que gasta nao tem opiniao sobre a fonte'


@ataque('RT-24', 'o dono da relevancia recebe token da Apify')
def rt24():
    import inspect
    fonte = open(os.path.join(RAIZ, 'leis', 'relevancia_da_fonte.py'),
                 encoding='utf-8').read()
    sem_token = not any(p in fonte for p in ('APIFY_TOKEN', 'apify_pool', 'import coletor'))
    p = set(inspect.signature(rel.portao).parameters)
    return sem_token and not (p & {'token', 'credencial'}), \
        'quem decide nao toca no dinheiro'


@ataque('RT-25', 'nasce um segundo dono do livro de relevancia')
def rt25():
    """⚠️ A PRIMEIRA VERSAO PROCURAVA `def registar` NO TEXTO DOS FICHEIROS —
    e apanhou-se a si propria, porque a procura escreve a palavra que procura.

        UM ATAQUE QUE ENCONTRA O SEU PROPRIO CODIGO NAO MEDIU NADA.

    Mede-se o comportamento: so um modulo sabe escrever no livro, e escrever
    exige passar pelo contrato dele.
    """
    import tempfile
    escritores = []
    for nome, mod in list(sys.modules.items()):
        if mod is None or not hasattr(mod, '__file__') or not mod.__file__:
            continue
        if not str(mod.__file__).startswith(RAIZ):
            continue
        fn = getattr(mod, 'registar', None)
        if callable(fn) and 'LIVRO' in str(getattr(mod, 'LIVRO', '')):
            escritores.append(nome)
    # e o unico escritor recusa uma linha que nao cumpre o contrato
    recusa_lixo = False
    with tempfile.TemporaryDirectory() as d:
        try:
            rel.registar([{'inventado': True}], raiz=d)
        except rel.DecisaoInvalida:
            recusa_lixo = True
    return escritores == ['relevancia_da_fonte'] and recusa_lixo, \
        'escritores do livro: %s · recusa linha fora do contrato: %s' % (
            escritores, recusa_lixo)


# ══════════════════════════════════════════════════════════════════════════
# 26-31 · A TOPOLOGIA DO DINHEIRO
# ══════════════════════════════════════════════════════════════════════════
@ataque('RT-26', 'uma segunda primitiva paga sobrevive sem guarda')
def rt26():
    c = censo.medir()
    return c['PAID_CREATION_PRIMITIVES'] == ['coleta/coletor.py'], \
        'primitivas: %s' % c['PAID_CREATION_PRIMITIVES']


@ataque('RT-27', 'POST directo por curl contorna a guarda')
def rt27():
    """⚠️ A PRIMEIRA VERSAO PROCURAVA O ENDERECO EM TEXTO, e apanhou tres
    ficheiros que apenas o NOMEIAM: `medidas/portao.py` guarda-o como rotulo
    (`PORTA_NOVA = 'POST /acts/{actor}/runs...'`) e os dois donos descrevem-no
    nos proprios cabecalhos.

        NOMEAR UM ENDERECO NAO E CHAMA-LO.

    Mede-se quem o CHAMA: o censo exige endereco de criacao **e** metodo POST
    no mesmo ficheiro, e ha um so. E prova-se que esse um recusa sem
    autorizacao, com um espiao que contaria o POST se ele saisse.
    """
    c = censo.medir()
    um_so = c['PAID_CREATION_PRIMITIVES'] == ['coleta/coletor.py']
    return um_so and _comprar(None) == 0, \
        'primitivas de criacao: %s · POST sem autorizacao: %d' % (
            c['PAID_CREATION_PRIMITIVES'], _comprar(None))


@ataque('RT-28', 'subprocesso contorna a guarda')
def rt28():
    """O transporte e trocavel; a porta nao.

    `regras/sensor_coleta.py` substitui `coletor._curl` por urllib — e continua
    a chamar `coletor.executar`. Por isso a guarda vive em `executar`, nao no
    transporte: um guarda no `_curl` teria sido trocado junto com ele.
    """
    fonte = open(os.path.join(RAIZ, 'regras', 'sensor_coleta.py'),
                 encoding='utf-8').read()
    troca_transporte = 'coletor._curl = _curl_robusto' in fonte
    usa_porta = 'coletor.executar(' in fonte
    passa_autorizacao = 'autorizacao=autorizacao' in fonte
    return troca_transporte and usa_porta and passa_autorizacao, \
        'troca o transporte, mantem a porta, e leva a autorizacao'


@ataque('RT-29', 'rotacao de chave compra de novo sem nova autorizacao')
def rt29():
    a = ag.autorizar(motivo=ag.TRIAL_DE_CAPACIDADE, proposito='T9',
                     max_execucoes=1, max_usd=0.10, quem_autorizou='l',
                     porque='p', condicao_de_paragem='um POST')
    # cinco chaves no cofre = cinco tentativas com a MESMA autorizacao
    total = sum(_comprar(a, token='chave-%d' % i) for i in range(5))
    return total == 1, '%d POST com 5 chaves e 1 autorizacao' % total


@ataque('RT-30', 'retry pago contorna o teto de execucoes')
def rt30():
    a = ag.autorizar(motivo=ag.PROVA_DE_RELEVANCIA, proposito='T9',
                     source_id='IT-T9-002', max_execucoes=2, max_usd=0.02,
                     quem_autorizou='l', porque='p', condicao_de_paragem='2')
    total = sum(_comprar(a) for _ in range(10))
    return total == 2, '%d POST com teto de 2' % total


@ataque('RT-31', 'teto do lado do fornecedor ausente')
def rt31():
    livro = [_decisao('IT-T9-002', 'T9', rel.SIM)]
    a = _normal(livro)
    return _comprar(a, teto_usd=None) == 0, 'sem maxTotalChargeUsd nao sai POST'


# ══════════════════════════════════════════════════════════════════════════
# 32-37 · O QUE A RECUSA SIGNIFICA
# ══════════════════════════════════════════════════════════════════════════
@ataque('RT-32', 'UNKNOWN exposure vira zero')
def rt32():
    """Custo nao medido nao pode ser escrito como zero."""
    livro = [_decisao('IT-T9-002', 'T9', rel.SIM)]
    a = _normal(livro)
    e = Espiao()
    antes = coletor._curl
    coletor._curl = e
    try:
        _, man = coletor.executar(
            'apify~ator', {}, token='T', run_id='R', platform='P', country='IT',
            mission='M', query='q', source_version='v', evidence_path='ev',
            salvar_raw=False, autorizacao=a, proposito='T9',
            source_id='IT-T9-002', motivo_do_gasto=ag.COLETA_NORMAL, teto_usd=0.05)
    finally:
        coletor._curl = antes
    return man.get('COST_STATE') == 'NOT_SETTLED', \
        'COST_STATE=%s — custo por liquidar nao e custo zero' % man.get('COST_STATE')


@ataque('RT-33', 'proposito ausente na autorizacao')
def rt33():
    mortos = 0
    for m in (ag.COLETA_NORMAL, ag.PROVA_DE_RELEVANCIA, ag.TRIAL_DE_CAPACIDADE):
        try:
            ag.autorizar(motivo=m, proposito='', source_id='IT-T9-002',
                         max_execucoes=1, max_usd=0.01, quem_autorizou='l',
                         porque='p', condicao_de_paragem='1', livro=[])
        except ag.AutorizacaoInvalida:
            mortos += 1
    return mortos == 3, '%d de 3 motivos recusam proposito vazio' % mortos


@ataque('RT-34', 'invocacao manual contorna')
def rt34():
    """A linha de comando nao assina cheques."""
    import subprocess
    r = subprocess.run([sys.executable, '-c',
                        'import sys; sys.path.insert(0, "."); import _gavetas, coletor; '
                        'coletor.executar("a", {}, token="t", run_id="r", platform="p", '
                        'country="c", mission="m", query="q", source_version="s", '
                        'evidence_path="e")'],
                       cwd=RAIZ, capture_output=True, text=True, timeout=120)
    return r.returncode != 0 and 'SEM_AUTORIZACAO_NAO_GASTEI' in (r.stdout + r.stderr), \
        'exit=%s' % r.returncode


@ataque('RT-35', 'test helper consegue gastar')
def rt35():
    """Um ajudante de teste que comprasse seria uma porta com outro nome."""
    c = censo.medir()
    de_teste = [f for f in c['PODEM_CRIAR_EXECUCAO_PAGA']
                if f.startswith(('tests/', 'provas/'))]
    sem_guarda = []
    for f in de_teste:
        t = open(os.path.join(RAIZ, f), encoding='utf-8').read()
        if 'coletor.executar(' in t and 'autorizacao' not in t:
            sem_guarda.append(f)
    return not sem_guarda, 'ajudantes que compram sem autorizacao: %s' % sem_guarda


@ataque('RT-36', 'a recusa apresenta-se como fonte irrelevante')
def rt36():
    """AUTHORIZATION_MISSING != NOT_RELEVANT."""
    try:
        _normal([])
        return False, 'nem sequer recusou'
    except ag.AutorizacaoInvalida as e:
        t = str(e).upper()
        return ('NOT_RELEVANT' not in t and 'IRRELEVANTE' not in t
                and rel.NAO_AVALIADA in str(e)), 'a recusa nao julga a fonte'


@ataque('RT-37', 'a recusa apresenta-se como falha da plataforma')
def rt37():
    """Uma recusa nossa nao pode sair como corrida FAILED da Apify."""
    e = Espiao()
    antes = coletor._curl
    coletor._curl = e
    try:
        coletor.executar('a', {}, token='t', run_id='r', platform='p',
                         country='c', mission='m', query='q', source_version='s',
                         evidence_path='ev', salvar_raw=False)
        return False, 'nao recusou'
    except ag.GastoRecusado:
        return e.posts == 0, 'levantou antes de qualquer ida a rede'
    except Exception as ex:                                     # noqa: BLE001
        return False, 'recusou com a excepcao errada: %s' % type(ex).__name__
    finally:
        coletor._curl = antes


def main() -> int:
    print('RED TEAM · AUTORIZACAO DE GASTO')
    print('=' * 76)
    vivos, mortos, linhas = [], [], []
    for codigo, nome, f in ATAQUES:
        try:
            morreu, nota = f()
        except Exception as e:                                  # noqa: BLE001
            # UM ATAQUE QUE REBENTA NAO E UM ATAQUE QUE MORREU.
            morreu, nota = False, 'o ataque rebentou: %s: %s' % (type(e).__name__, e)
        (mortos if morreu else vivos).append(codigo)
        linhas.append({'CODIGO': codigo, 'ATAQUE': nome,
                       'ESTADO': 'ATAQUE_MORTO' if morreu else 'ATAQUE_VIVO',
                       'NOTA': str(nota)[:220]})
        print('  %-7s %-9s %s' % (codigo, 'MORTO' if morreu else 'VIVO  <<<', nome[:58]))
        print('          %s' % str(nota)[:150])
    print('=' * 76)
    print('ATAQUES=%d · MORTOS=%d · VIVOS=%d' % (len(ATAQUES), len(mortos), len(vivos)))
    if vivos:
        print('SOBREVIVERAM: %s' % ', '.join(vivos))
        return 1
    print('TODOS OS ATAQUES MORRERAM.')
    print('APIFY_REAL_RUNS = 0 · PROVIDER_START_POSTS_REAL = 0 · REAL_COST_USD = 0')
    if '--escrever' in sys.argv:
        saida = os.path.join(RAIZ, 'data', 'derivados',
                             'RED-TEAM-AUTORIZACAO-DE-GASTO-V1.json')
        os.makedirs(os.path.dirname(saida), exist_ok=True)
        with open(saida, 'w', encoding='utf-8') as f:
            f.write(json.dumps(
                {'SCHEMA': 'sintonia.red-team-autorizacao-de-gasto/1',
                 'CONTRATO': ag.CONTRATO, 'TOTAL': len(ATAQUES),
                 'MORTOS': len(mortos), 'VIVOS': len(vivos),
                 'APIFY_REAL_RUNS': 0, 'REAL_COST_USD': 0,
                 'ATAQUES': linhas}, ensure_ascii=False, indent=2) + '\n')
        print('escrito: data/derivados/RED-TEAM-AUTORIZACAO-DE-GASTO-V1.json')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
