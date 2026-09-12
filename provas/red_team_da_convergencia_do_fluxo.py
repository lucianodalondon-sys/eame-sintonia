#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RED TEAM DA CONVERGENCIA — SCRAP-CV-02.

    py provas/red_team_da_convergencia_do_fluxo.py

A PERGUNTA
----------
O fluxo canonico do SCRAP e o controle de gasto passaram a viver na mesma linha.
Esta prova tenta COMPRAR de quinze maneiras nomeadas, atravessando essa linha.

Cada ataque declara o que teria de acontecer para ele MORRER. Um ataque que
rebenta de outra maneira NAO conta como defesa: conta como ATAQUE_VIVO, porque
uma excecao que ninguem previu nao e um portao — e uma surpresa.

    UM ATAQUE QUE LEVANTA POR OUTRO MOTIVO NAO FOI BARRADO. FOI IGNORADO.
    UMA RECUSA PELO MOTIVO ERRADO NAO E UMA DEFESA. E UM ACIDENTE.

E NADA AQUI SAI DA MAQUINA
---------------------------
O espiao substitui `subprocess.run` — o processo `curl` — e mais nada. Ficam
reais e por cima dele `_curl`, o teto de rede, o orcamento financeiro,
`executar`, a guarda e o roteador.

    NETWORK_REAL = 0 · APIFY_REAL_RUNS = 0 · PAID_REAL_RUNS = 0 · REAL_COST_USD = 0
"""
from __future__ import annotations

import contextlib
import copy
import json
import os
import shutil
import sys
import tempfile
import types

_AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(_AQUI)
for p in ('coleta', 'leis', 'medidas', 'ferramentas', 'guarda', ''):
    sys.path.insert(0, os.path.join(RAIZ, p) if p else RAIZ)

import autorizacao_de_gasto as az   # noqa: E402
import coletor as ct                # noqa: E402
import falhas                       # noqa: E402
import scrap_http as http           # noqa: E402

SAIDA = os.path.join(RAIZ, 'data', 'derivados', 'RED-TEAM-CONVERGENCIA-FLUXO-V1.json')
ATOR = 'fake~ator-do-red-team'
MORREU, VIVO = 'MORREU', 'ATAQUE_VIVO'


class CurlFalso(object):
    def __init__(self, custos=None):
        self.posts = 0
        self.tetos = []
        self.custos = list(custos or [])

    class _R(object):
        def __init__(self, out, rc=0, err=''):
            self.returncode, self.stdout, self.stderr = rc, out, err

    def __call__(self, cmd, **k):
        url = cmd[-1]
        if '-X' in cmd and cmd[cmd.index('-X') + 1].upper() == 'POST':
            self.posts += 1
            for parte in url.split('?')[-1].split('&'):
                if parte.startswith('maxTotalChargeUsd='):
                    self.tetos.append(float(parte.split('=', 1)[1]))
            custo = self.custos.pop(0) if self.custos else 0.0
            if custo is not None and self.tetos and custo > self.tetos[-1]:
                custo = self.tetos[-1]
            return self._R(json.dumps({'data': {
                'id': 'R%d' % self.posts, 'status': 'SUCCEEDED',
                'startedAt': '2026-09-12T00:00:00.000Z',
                'finishedAt': '2026-09-12T00:00:01.000Z',
                'defaultDatasetId': 'DS', 'buildNumber': '1',
                'usageTotalUsd': custo}}))
        if '/datasets/' in url:
            return self._R('[]')
        return self._R(json.dumps({'data': {}}))


class Mundo(object):
    """Um campo de tiro que nao deixa marca na arvore, e que repoe a PORTA."""

    def __enter__(self):
        self.curl = CurlFalso()
        self._run, self._curl = ct.subprocess.run, ct._curl
        ct.subprocess.run = self.curl
        ct._curl = ct._CURL_DA_CASA
        self._raw = ct.RAW_DIR
        self._tmp = tempfile.mkdtemp(prefix='cv02-rt-')
        ct.RAW_DIR = self._tmp
        return self

    def __exit__(self, *a):
        ct.subprocess.run, ct._curl = self._run, self._curl
        ct.RAW_DIR = self._raw
        shutil.rmtree(self._tmp, ignore_errors=True)
        return False


CAMPOS_TRIAL = {'AUTORIZACAO_HUMANA': 'red team CV-02', 'MAX_PROVIDER_RUNS': 1,
                'MAX_START_POSTS': 1, 'MAX_USD': 0.10}
CAMPOS_NORMAL = {'VEREDITO': az.AUTORIZA, 'SOURCE_ID': 'IT-T3-001',
                 'PROPOSITO': 'T3', 'ESTADO_DA_RELEVANCIA': az.SIM,
                 'VERSAO_DO_PORTAO': '1', 'CONTRATO': 'RELEVANCIA_DA_FONTE/v1',
                 'DECISAO': {'EVIDENCIA': {'F': 'LIVRO'}},
                 'MAX_PROVIDER_RUNS': 1, 'MAX_START_POSTS': 1, 'MAX_USD': 0.10}


def trial(**mud):
    return az.conceder(dict(CAMPOS_TRIAL, **mud))


def comprar(mundo, autorizacao, *, orcamento=0.10, rede=None, teto=0.10,
            modo=az.TRIAL, **kw):
    base = dict(token='T', run_id='R', platform='YOUTUBE', country='IT',
                mission='CV-02', query='q', source_version='v',
                evidence_path='/dev/null', wait=60, salvar_raw=False,
                modo=modo, autorizacao=autorizacao, teto_usd=teto)
    base.update(kw)
    with contextlib.ExitStack() as pilha:
        if orcamento is not None:
            pilha.enter_context(ct.orcamento_financeiro(orcamento))
        if rede is not None:
            pilha.enter_context(http.orcamento_de_rede(rede))
        return ct.executar(ATOR, {'q': 1}, **base)


# ── COMO SE MEDE UM ATAQUE ──────────────────────────────────────────────────
def recusa(estado):
    def julgar(fn):
        try:
            fn()
        except az.SemAutorizacaoDeGasto as e:
            if e.estado == estado:
                return True, 'SemAutorizacaoDeGasto · %s' % e.estado
            return False, 'morreu pelo estado ERRADO: %s (esperado %s)' % (e.estado, estado)
        except BaseException as e:                                # noqa: BLE001
            return False, 'levantou %s — nao foi a guarda' % type(e).__name__
        return False, 'PASSOU: comprou'
    return julgar


def levanta(tipo):
    def julgar(fn):
        try:
            fn()
        except tipo:
            return True, tipo.__name__
        except BaseException as e:                                # noqa: BLE001
            return False, 'levantou %s, esperado %s' % (type(e).__name__, tipo.__name__)
        return False, 'PASSOU'
    return julgar


def medida(pergunta):
    def julgar(fn):
        try:
            ok, obs = fn()
        except BaseException as e:                                # noqa: BLE001
            return False, 'levantou %s — a medicao nao aconteceu' % type(e).__name__
        return bool(ok), obs
    return julgar


ATAQUES = []


def ataque(ident, nome, lei, julgar):
    def registar(fn):
        ATAQUES.append((ident, nome, lei, julgar, fn))
        return fn
    return registar


# ══════════════════════════════════════════════════════════════════════════
# 1–4 · A AUTORIZACAO NAO SE FABRICA, NAO SE COPIA E NAO SE EMENDA
# ══════════════════════════════════════════════════════════════════════════
@ataque('RT01', 'reconstruir a autorizacao pela classe, com os mesmos campos',
        'UMA AUTORIZACAO QUE O CHAMADOR ESCREVE E UM CAMPO DE FORMULARIO',
        recusa(az.SEM_AUTORIZACAO))
def rt01():
    valida = trial()
    forjada = az.Autorizacao(dict(valida, MAX_USD=99.0, MAX_PROVIDER_RUNS=99))
    with Mundo() as m:
        comprar(m, forjada)


@ataque('RT02', 'copy.copy de uma autorizacao valida',
        'COPIAR UMA AUTORIZACAO NAO E RECEBER UMA AUTORIZACAO',
        medida('a copia nao se faz, ou nao compra'))
def rt02():
    a = trial()
    with Mundo() as m:
        try:
            copia = copy.copy(a)
        except az.SemAutorizacaoDeGasto:
            return True, 'a copia nem se consegue construir (selada)'
        try:
            comprar(m, copia)
        except az.SemAutorizacaoDeGasto as e:
            return e.estado == az.SEM_AUTORIZACAO, 'recusada: %s' % e.estado
        return False, 'a copia COMPROU'


@ataque('RT03', 'copy.deepcopy de uma autorizacao ja gasta, para a repor',
        'COPIAR UMA AUTORIZACAO NAO E RECEBER UMA AUTORIZACAO',
        medida('a copia nao se faz, ou nao compra'))
def rt03():
    a = trial()
    with Mundo() as m:
        comprar(m, a)                       # gasta a unica execucao
        try:
            copia = copy.deepcopy(a)
        except az.SemAutorizacaoDeGasto:
            return m.curl.posts == 1, 'a copia nem se consegue construir (selada)'
        try:
            comprar(m, copia)
        except az.SemAutorizacaoDeGasto:
            return m.curl.posts == 1, 'POSTS = %d' % m.curl.posts
        return False, 'a copia comprou outra vez: POSTS = %d' % m.curl.posts


@ataque('RT04', 'mudar MAX_USD depois de a autorizacao ser concedida',
        'UMA AUTORIZACAO QUE MUDA DEPOIS DE CONFERIDA NAO FOI CONFERIDA',
        medida('nenhuma das quatro escritas passa'))
def rt04():
    a = trial(MAX_USD=0.10)
    passaram = []
    for nome, mexer in (('__setitem__', lambda: a.__setitem__('MAX_USD', 99.0)),
                        ('update', lambda: a.update(MAX_USD=99.0)),
                        ('pop', lambda: a.pop('MAX_USD')),
                        ('setdefault', lambda: a.setdefault('MAX_ITEMS', 99))):
        try:
            mexer()
            passaram.append(nome)
        except az.SemAutorizacaoDeGasto:
            pass
    return not passaram and a['MAX_USD'] == 0.10, 'escritas que passaram: %s' % (passaram or 'nenhuma')


# ══════════════════════════════════════════════════════════════════════════
# 5 · O LIMITE HUMANO NAO RENASCE
# ══════════════════════════════════════════════════════════════════════════
@ataque('RT05', 'duas chamadas cujo teto somado passa o limite humano',
        'FINANCIAL_BUDGET.AUTHORIZED <= AUTORIZACAO.MAX_USD',
        medida('a exposicao representada fica dentro do limite humano'))
def rt05():
    a = trial(MAX_PROVIDER_RUNS=2, MAX_USD=1.00)
    exposto, compradas = 0.0, 0
    with Mundo() as m:
        m.curl.custos = [0.60, 0.60]
        for _ in range(2):
            try:
                with ct.orcamento_financeiro(1.00) as orc:   # cada uma declara 1.00
                    comprar(m, a, orcamento=None, teto=1.00)
                    exposto += orc.exposto_micros / float(ct.MICRO)
                    compradas += 1
            except az.SemAutorizacaoDeGasto:
                pass
        return (exposto <= 1.0 + 1e-9 and compradas >= 1,
                'EXPOSICAO = %.4f sob MAX_USD = 1.00 · compras = %d'
                % (exposto, compradas))


# ══════════════════════════════════════════════════════════════════════════
# 6–7 · A RECUSA NAO SE VESTE DE REDE, E NAO PEDE PARA SER REPETIDA
# ══════════════════════════════════════════════════════════════════════════
@ataque('RT06', 'apanhar a recusa de gasto com `except OSError`',
        'SPEND_NOT_AUTHORIZED != NETWORK_ERROR',
        medida('nenhum `except OSError` a apanha'))
def rt06():
    e = az.SemAutorizacaoDeGasto('x', estado=az.SEM_AUTORIZACAO)
    apanhada = isinstance(e, (OSError, PermissionError, ConnectionError))
    return (not apanhada and isinstance(e, RuntimeError),
            'OSError=%s · RuntimeError=%s' % (apanhada, isinstance(e, RuntimeError)))


@ataque('RT07', 'transformar a recusa de gasto em WAIT',
        'SPEND_NOT_AUTHORIZED = NO_RETRY',
        medida('a recuperacao canonica e NO_RETRY, e nao WAIT'))
def rt07():
    nomes = (az.SEM_AUTORIZACAO, az.RELEVANCIA_BARRADA, az.RELEVANCIA_POR_AVALIAR,
             az.RELEVANCIA_INCERTA, az.RELEVANCIA_COM_ERRO, az.LIMITE_AUSENTE,
             az.FONTE_ERRADA, az.PROPOSITO_ERRADO, az.CONTRATO_ERRADO)
    maus = [n for n in nomes
            if falhas.recuperacao(falhas.traduzir(n)) != 'NO_RETRY']
    return not maus, 'estados que pediriam retry: %s' % (maus or 'nenhum')


# ══════════════════════════════════════════════════════════════════════════
# 8–10 · O TRANSPORTE TROCADO
# ══════════════════════════════════════════════════════════════════════════
@ataque('RT08', 'importar sensor_coleta antes da prova, para a rede ficar real',
        'UM FAKE QUE JA NAO ESTA NO CAMINHO NAO E UM FAKE',
        medida('a porta e reposta e o POST cai no fake'))
def rt08():
    import urllib.request
    import sensor_coleta                                        # noqa: F401
    saiu = []

    def urlopen_falso(req, *a, **k):
        saiu.append(1)
        raise AssertionError('a prova offline foi a rede')

    real = urllib.request.urlopen
    urllib.request.urlopen = urlopen_falso
    try:
        with Mundo() as m:
            comprar(m, trial())
            return (m.curl.posts == 1 and not saiu,
                    'POSTS no fake = %d · idas reais = %d' % (m.curl.posts, len(saiu)))
    finally:
        urllib.request.urlopen = real


@ataque('RT09', 'substituir `_curl` por um transporte sem teto de rede',
        'TROCAR O TRANSPORTE NAO PODE TROCAR QUEM CONTA AS IDAS',
        medida('o transporte substituto pede ao dono da rede'))
def rt09():
    import urllib.request
    import sensor_coleta
    saiu = []

    def urlopen_falso(req, *a, **k):
        saiu.append(1)
        raise AssertionError('o pedido SAIU com o teto de acessos a zero')

    real, guardado = urllib.request.urlopen, ct._curl
    urllib.request.urlopen = urlopen_falso
    try:
        with http.orcamento_de_rede(0):
            try:
                sensor_coleta._curl_robusto(
                    'https://api.apify.com/v2/acts/x/runs',
                    token='T', metodo='POST', corpo={})
            except http.SemOrcamentoDeRede:
                return not saiu, 'idas que escaparam ao teto: %d' % len(saiu)
            except BaseException as e:                          # noqa: BLE001
                return False, 'levantou %s' % type(e).__name__
        return False, 'passou sem pedir'
    finally:
        urllib.request.urlopen = real
        ct._curl = guardado


@ataque('RT10', 'fazer o transporte substituto repetir o POST',
        'REPETIR UM GET E BARATO. REPETIR UM POST E COMPRAR DE NOVO',
        medida('um POST, uma tentativa'))
def rt10():
    import urllib.request
    import sensor_coleta
    tentativas = []

    def urlopen_falso(req, *a, **k):
        tentativas.append(req.get_method())
        raise OSError('ws_closed_mid_exchange')

    real, guardado = urllib.request.urlopen, ct._curl
    urllib.request.urlopen = urlopen_falso
    try:
        try:
            sensor_coleta._curl_robusto('https://api.apify.com/v2/acts/x/runs',
                                        token='T', metodo='POST', corpo={})
        except ct.PostTalvezCriado:
            pass
        except BaseException as e:                              # noqa: BLE001
            return False, 'levantou %s' % type(e).__name__
        return len(tentativas) == 1, 'POSTs enviados = %d' % len(tentativas)
    finally:
        urllib.request.urlopen = real
        ct._curl = guardado


# ══════════════════════════════════════════════════════════════════════════
# 11–12 · A PORTA PAGA, E O LEDGER
# ══════════════════════════════════════════════════════════════════════════
@ataque('RT11', 'chamar a primitiva paga fora do roteador, sem autorizacao',
        'UMA GUARDA QUE VIVE NA PRIMITIVA GUARDA TODOS OS CAMINHOS',
        recusa(az.SEM_AUTORIZACAO))
def rt11():
    with Mundo() as m:
        comprar(m, None)


@ataque('RT12', 'colher em NORMAL sem ledger declarado',
        'SEM LEDGER NAO SE COMPRA', recusa(az.SEM_AUTORIZACAO))
def rt12():
    a = az.conceder(CAMPOS_NORMAL)
    with Mundo() as m:
        comprar(m, a, orcamento=None, modo=az.NORMAL,
                source_id='IT-T3-001', proposito='T3')


# ══════════════════════════════════════════════════════════════════════════
# 13–15 · A UNIDADE AUTORIZADA
# ══════════════════════════════════════════════════════════════════════════
@ataque('RT13', 'emendar a autorizacao entre a conferencia e o POST',
        'UMA AUTORIZACAO QUE MUDA DEPOIS DE CONFERIDA NAO FOI CONFERIDA',
        medida('o teto que chega ao fornecedor e o que foi conferido'))
def rt13():
    a = trial(MAX_USD=0.10)
    with Mundo() as m:
        with ct.orcamento_financeiro(0.10):
            az.pode_comprar(modo=az.TRIAL, autorizacao=a,
                            orcamento_autorizado=0.10)
            try:
                a['MAX_USD'] = 99.0                 # depois de conferida
            except az.SemAutorizacaoDeGasto:
                pass
            comprar(m, a, orcamento=None, teto=99.0)
        return (m.curl.tetos and m.curl.tetos[-1] <= 0.10 + 1e-9,
                'teto enviado = %s · MAX_USD = %s' % (m.curl.tetos, a['MAX_USD']))


@ataque('RT14', 'queimar a unidade antes de o orcamento recusar',
        'UM GATE BARATO CORRE PRIMEIRO, E NAO QUEIMA NADA AO RECUSAR',
        medida('a autorizacao volta intacta quando o dinheiro recusa'))
def rt14():
    a = trial(MAX_USD=0.10)
    with Mundo() as m:
        with ct.orcamento_financeiro(0.10) as orc:
            orc.reservar(pedido=0.10, ator='x', rota='y', missao='z')   # esgota
            try:
                comprar(m, a, orcamento=None, teto=0.10)
            except ct.SemOrcamentoFinanceiro:
                pass
            except BaseException as e:                          # noqa: BLE001
                return False, 'levantou %s' % type(e).__name__
        return (a._gastas == 0 and m.curl.posts == 0,
                'AUTH_GASTAS = %d · POSTS = %d' % (a._gastas, m.curl.posts))


@ataque('RT15', 'devolver a unidade depois de um POST que talvez tenha saido',
        'AUSENCIA DE NOTICIA NAO E PROVA DE AUSENCIA DE COMPRA',
        medida('a unidade NAO volta quando o POST pode ter chegado'))
def rt15():
    a = trial(MAX_PROVIDER_RUNS=2, MAX_USD=0.20)
    with Mundo() as m:
        def cai_no_post(cmd, **k):
            if '-X' in cmd and cmd[cmd.index('-X') + 1].upper() == 'POST':
                m.curl.posts += 1
                return CurlFalso._R('', rc=56, err='ws_closed_mid_exchange')
            return CurlFalso._R(json.dumps({'data': {}}))
        ct.subprocess.run = cai_no_post
        with ct.orcamento_financeiro(0.20) as orc:
            comprar(m, a, orcamento=None, teto=0.20)
            return (a._gastas == 1 and orc.desconhecido > 0,
                    'AUTH_GASTAS = %d · DESCONHECIDO = %.4f'
                    % (a._gastas, orc.desconhecido))


def main():
    linhas, vivos = [], 0
    for ident, nome, lei, julgar, fn in ATAQUES:
        morreu, observado = julgar(fn)
        vivos += 0 if morreu else 1
        linhas.append({'ID': ident, 'ATAQUE': nome, 'LEI': lei,
                       'VEREDITO': MORREU if morreu else VIVO,
                       'OBSERVADO': observado})
        print('  %s  %-6s %-60s %s' % ('·' if morreu else '!', ident, nome[:60],
                                       MORREU if morreu else VIVO))
        if not morreu:
            print('          %s' % observado)

    print()
    print('  ATAQUES = %d · MORRERAM = %d · ATAQUE_VIVO = %d'
          % (len(linhas), len(linhas) - vivos, vivos))
    print('  NETWORK_REAL = 0 · APIFY_REAL_RUNS = 0 · REAL_COST_USD = 0')

    os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
    with open(SAIDA, 'w', encoding='utf-8') as f:
        json.dump({'CONTRATO': 'RED_TEAM_CONVERGENCIA_FLUXO/v1',
                   'ATAQUES': len(linhas), 'MORRERAM': len(linhas) - vivos,
                   'ATAQUE_VIVO': vivos, 'PAID_REAL_RUNS': 0,
                   'REAL_COST_USD': 0, 'LINHAS': linhas},
                  f, ensure_ascii=False, indent=1)
    print('  escrito: %s' % os.path.relpath(SAIDA, RAIZ))
    return 1 if vivos else 0


if __name__ == '__main__':
    raise SystemExit(main())
