#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RED TEAM DA CONVERGENCIA DO GASTO — SCRAP-CV-01.

    py provas/red_team_da_convergencia.py

A PERGUNTA
----------
Duas leis que passaram em separado nao provam nada juntas. Esta prova tenta
COMPRAR — de 27 maneiras — atravessando a linha que a CV-01 uniu:

    SPEND_AUTHORIZATION != FINANCIAL_BUDGET != NETWORK_BUDGET

Cada ataque nomeia o que teria de acontecer para ele MORRER. Um ataque que
rebenta de outra maneira NAO conta como defesa: conta como `ATAQUE_VIVO`, porque
uma excecao que ninguem previu nao e um portao — e uma surpresa.

    UM ATAQUE QUE LEVANTA POR OUTRO MOTIVO NAO FOI BARRADO. FOI IGNORADO.

E NADA AQUI SAI DA MAQUINA
---------------------------
O espiao substitui `subprocess.run` — o processo `curl` — e mais nada. Ficam
reais e por cima dele: `_curl`, o teto de rede, o orcamento financeiro,
`executar`, a guarda de autorizacao e o portao de relevancia. Substituir
qualquer um deles invalidaria a prova: seria medir o fake.

    NETWORK_REAL = 0 · APIFY_REAL_RUNS = 0 · PAID_REAL_RUNS = 0 · REAL_COST_USD = 0
"""
from __future__ import annotations

import contextlib
import copy
import dataclasses
import json
import os
import shutil
import sys
import tempfile
import types

_AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(_AQUI)
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401

import autorizacao_de_gasto as ag   # noqa: E402
import relevancia_da_fonte as rel   # noqa: E402
import coletor                      # noqa: E402
import scrap_http                   # noqa: E402

SAIDA = os.path.join(RAIZ, 'data', 'derivados', 'RED-TEAM-CONVERGENCIA-V1.json')
MORREU = 'MORREU'
VIVO = 'ATAQUE_VIVO'


# ── O MUNDO EXTERNO, E SO ELE ───────────────────────────────────────────────
class CurlFalso(object):
    def __init__(self, custos=None, respeita_o_teto=True):
        self.posts = 0
        self.custos = list(custos or [])
        self.tetos = []
        # ⚠️ UM FORNECEDOR QUE IGNORA O TETO E UM CASO DIFERENTE, E TEM ATAQUE
        # PROPRIO (RT31). Misturar os dois faria uma trava NOSSA que funcionou
        # parecer uma trava que falhou.
        self.respeita_o_teto = respeita_o_teto

    class _R(object):
        def __init__(self, out, rc=0, err=''):
            self.returncode, self.stdout, self.stderr = rc, out, err

    def __call__(self, cmd, **k):
        url = cmd[-1]
        if '-X' in cmd and cmd[cmd.index('-X') + 1] == 'POST':
            self.posts += 1
            for p in url.split('?')[-1].split('&'):
                if p.startswith('maxTotalChargeUsd='):
                    self.tetos.append(float(p.split('=', 1)[1]))
            custo = self.custos.pop(0) if self.custos else 0.0
            if (self.respeita_o_teto and custo is not None and self.tetos
                    and custo > self.tetos[-1]):
                custo = self.tetos[-1]
            return self._R(json.dumps({'data': {
                'id': 'FAKE-%d' % self.posts, 'status': 'SUCCEEDED',
                'startedAt': '2026-09-12T00:00:00.000Z',
                'finishedAt': '2026-09-12T00:00:01.000Z',
                'defaultDatasetId': 'DS', 'buildNumber': '1',
                'usageTotalUsd': custo}}))
        if '/datasets/' in url:
            return self._R('[]')
        return self._R(json.dumps({'data': {}}))


class Mundo(object):
    """Um campo de tiro que nao deixa marca na arvore."""

    def __enter__(self):
        self.curl = CurlFalso()
        self._run = coletor.subprocess.run
        coletor.subprocess.run = self.curl
        self._raw = coletor.RAW_DIR
        self._tmp = tempfile.mkdtemp(prefix='cv01-rt-')
        coletor.RAW_DIR = self._tmp
        return self

    def __exit__(self, *a):
        coletor.subprocess.run = self._run
        coletor.RAW_DIR = self._raw
        shutil.rmtree(self._tmp, ignore_errors=True)
        return False


def decisao(source_id, proposito, resultado, **kw):
    kw.setdefault('motivo', 'medido nesta prova')
    kw.setdefault('metodo', 'PROVA_BARATA_ACERVO')
    if resultado in rel.RESULTADOS_QUE_AFIRMAM:
        kw.setdefault('evidencia', {'file': 'data/samples/x.json', 'line': 1})
    return rel.Decisao(source_id=source_id, proposito=proposito,
                       resultado=resultado, **kw).para_livro()


def trial(**kw):
    base = dict(motivo=ag.TRIAL_DE_CAPACIDADE, proposito='T9', max_execucoes=1,
                max_usd=0.10, quem_autorizou='luciano',
                porque='provar a rota paga', condicao_de_paragem='um POST')
    base.update(kw)
    return ag.autorizar(**base)


def comprar(mundo, autorizacao, *, orcamento=0.10, rede=None, teto=None, **kw):
    """A porta paga REAL — os tres portoes de verdade, o fornecedor falso."""
    base = dict(token='T', run_id='R', platform='P', country='IT', mission='M',
                query='q', source_version='v', evidence_path='e',
                salvar_raw=False, autorizacao=autorizacao,
                proposito=getattr(autorizacao, 'proposito', None),
                source_id=getattr(autorizacao, 'source_id', None),
                motivo_do_gasto=getattr(autorizacao, 'motivo', None),
                teto_usd=teto if teto is not None
                else getattr(autorizacao, 'max_usd', None))
    base.update(kw)
    with contextlib.ExitStack() as pilha:
        if orcamento is not None:
            pilha.enter_context(coletor.orcamento_financeiro(orcamento))
        if rede is not None:
            pilha.enter_context(scrap_http.orcamento_de_rede(rede))
        return coletor.executar('apify~ator', {}, **base)


# ── COMO SE MEDE UM ATAQUE ──────────────────────────────────────────────────
def recusa(causa):
    """O ataque tem de morrer com ESTA causa, vinda da guarda de gasto."""
    def julgar(fn):
        try:
            fn()
        except ag.GastoRecusado as e:
            if e.causa == causa:
                return True, 'GastoRecusado · %s' % e.causa
            return False, 'morreu pela causa ERRADA: %s (esperada %s)' % (e.causa, causa)
        except BaseException as e:                              # noqa: BLE001
            return False, 'levantou %s — nao foi o portao' % type(e).__name__
        return False, 'PASSOU: comprou'
    return julgar


def invalida(marca):
    """O ataque tem de morrer ao PEDIR a autorizacao, e a mensagem di-lo."""
    def julgar(fn):
        try:
            fn()
        except ag.AutorizacaoInvalida as e:
            if marca in str(e):
                return True, 'AutorizacaoInvalida · %s' % marca
            return False, 'AutorizacaoInvalida por outro motivo: %s' % str(e)[:90]
        except BaseException as e:                              # noqa: BLE001
            return False, 'levantou %s — nao foi a guarda' % type(e).__name__
        return False, 'PASSOU: autorizou'
    return julgar


def levanta(tipo, marca=''):
    def julgar(fn):
        try:
            fn()
        except tipo as e:
            if marca and marca not in str(e):
                return False, '%s com outra mensagem: %s' % (tipo.__name__, str(e)[:90])
            return True, tipo.__name__
        except BaseException as e:                              # noqa: BLE001
            return False, 'levantou %s, esperado %s' % (type(e).__name__, tipo.__name__)
        return False, 'PASSOU'
    return julgar


def medida(pergunta):
    """O ataque nao levanta: e uma MEDICAO que tem de bater certo."""
    def julgar(fn):
        try:
            ok, obs = fn()
        except BaseException as e:                              # noqa: BLE001
            return False, 'levantou %s — a medicao nao chegou a acontecer' % type(e).__name__
        return bool(ok), obs
    return julgar


ATAQUES = []


def ataque(ident, nome, lei, julgar):
    def registar(fn):
        ATAQUES.append((ident, nome, lei, julgar, fn))
        return fn
    return registar


# ══════════════════════════════════════════════════════════════════════════
# EIXO 1 · A AUTORIZACAO (QUEM · POR QUE · PARA QUE)
# ══════════════════════════════════════════════════════════════════════════
@ataque('RT01', 'comprar sem autorizacao nenhuma',
        'CREDENTIAL != AUTHORIZATION', recusa('AUTORIZACAO_AUSENTE'))
def rt01():
    with Mundo() as m:
        comprar(m, None, proposito='T9', motivo_do_gasto=ag.TRIAL_DE_CAPACIDADE,
                teto_usd=0.10)


@ataque('RT02', 'construir a Autorizacao a mao, sem passar por autorizar()',
        'UMA AUTORIZACAO QUE O CHAMADOR ESCREVE NAO E UMA AUTORIZACAO',
        levanta(ag.AutorizacaoInvalida, 'AUTORIZACAO_FABRICADA'))
def rt02():
    ag.Autorizacao(motivo=ag.TRIAL_DE_CAPACIDADE, proposito='T9', source_id=None,
                   max_execucoes=99, max_usd=99.0, quem_autorizou='eu',
                   porque='porque sim', condicao_de_paragem='nenhuma')


@ataque('RT03', 'dataclasses.replace numa autorizacao valida para inflar o teto',
        'DUAS AUTORIZACOES IGUAIS NAO SAO A MESMA AUTORIZACAO',
        recusa('AUTORIZACAO_FABRICADA'))
def rt03():
    a = trial()
    falsa = dataclasses.replace(a, max_execucoes=99, max_usd=99.0)
    with Mundo() as m:
        comprar(m, falsa, orcamento=0.10, teto=0.10)


@ataque('RT04', 'copy.deepcopy da autorizacao ja gasta, para a repor a zero',
        'ROTACAO DE CHAVE NAO E NOVA AUTORIZACAO', recusa('AUTORIZACAO_FABRICADA'))
def rt04():
    a = trial()
    with Mundo() as m:
        comprar(m, a, orcamento=0.10)
        comprar(m, copy.deepcopy(a), orcamento=0.10)


@ataque('RT05', 'um dicionario com as chaves certas, passado como autorizacao',
        'UMA AUTORIZACAO QUE O CHAMADOR ESCREVE NAO E UMA AUTORIZACAO',
        recusa('AUTORIZACAO_FABRICADA'))
def rt05():
    falsa = {'motivo': ag.TRIAL_DE_CAPACIDADE, 'proposito': 'T9',
             'max_execucoes': 99, 'max_usd': 99.0}
    with Mundo() as m:
        comprar(m, falsa, orcamento=0.10, proposito='T9',
                motivo_do_gasto=ag.TRIAL_DE_CAPACIDADE, teto=0.10)


@ataque('RT06', 'um objecto que IMITA a interface da autorizacao (duck typing)',
        'UMA AUTORIZACAO QUE O CHAMADOR ESCREVE NAO E UMA AUTORIZACAO',
        recusa('AUTORIZACAO_FABRICADA'))
def rt06():
    falsa = types.SimpleNamespace(
        motivo=ag.TRIAL_DE_CAPACIDADE, proposito='T9', source_id=None,
        max_execucoes=99, max_usd=99.0, restantes=99, _selo=object(),
        para_o_manifesto=lambda: {})
    with Mundo() as m:
        comprar(m, falsa, orcamento=0.10)


@ataque('RT07', 'autorizacao de TRIAL usada para uma COLETA_NORMAL',
        'TRIAL != COLLECTION', recusa('AUTORIZACAO_NAO_COBRE_ESTE_MOTIVO'))
def rt07():
    a = trial()
    with Mundo() as m:
        comprar(m, a, orcamento=0.10, motivo_do_gasto=ag.COLETA_NORMAL)


@ataque('RT08', 'autorizacao de T3 a comprar em T9',
        'A DECISAO E DO PAR (FONTE, PROPOSITO)',
        recusa('AUTORIZACAO_NAO_COBRE_ESTE_PROPOSITO'))
def rt08():
    a = trial(proposito='T3')
    with Mundo() as m:
        comprar(m, a, orcamento=0.10, proposito='T9')


@ataque('RT09', 'autorizacao da fonte A usada para comprar da fonte B',
        'A DECISAO DE UMA FONTE NAO FALA PELAS OUTRAS',
        recusa('AUTORIZACAO_NAO_COBRE_ESTA_FONTE'))
def rt09():
    a = ag.autorizar(motivo=ag.PROVA_DE_RELEVANCIA, proposito='T9',
                     source_id='IT-T9-001', max_execucoes=1, max_usd=0.01,
                     quem_autorizou='luciano', porque='descobrir se serve',
                     condicao_de_paragem='1 execucao')
    with Mundo() as m:
        comprar(m, a, orcamento=0.01, source_id='IT-T9-999')


@ataque('RT10', 'gastar duas vezes uma autorizacao de uma execucao',
        'UMA AUTORIZACAO DE UMA EXECUCAO NAO PAGA DUAS',
        recusa('AUTORIZACAO_ESGOTADA'))
def rt10():
    a = trial(max_execucoes=1, max_usd=1.00)
    with Mundo() as m:
        with coletor.orcamento_financeiro(1.00):
            comprar(m, a, orcamento=None, teto=1.00)
            comprar(m, a, orcamento=None, teto=1.00)


@ataque('RT11', 'quatro chaves do cofre a renovar a mesma autorizacao',
        'ROTACAO DE CHAVE NAO E NOVA AUTORIZACAO',
        medida('um POST por unidade autorizada, e nao um por chave'))
def rt11():
    a = trial(max_execucoes=1, max_usd=1.00)
    with Mundo() as m:
        with coletor.orcamento_financeiro(1.00):
            for chave in ('K1', 'K2', 'K3', 'K4'):
                try:
                    comprar(m, a, orcamento=None, token=chave, teto=1.00)
                except ag.GastoRecusado:
                    pass
        return m.curl.posts == 1, 'POSTS = %d com 4 chaves' % m.curl.posts


@ataque('RT12', 'coleta normal sem teto de dolares — o cheque em branco',
        'GASTO SEM TETO E CHEQUE EM BRANCO', invalida('SEM_TETO_DE_DOLARES'))
def rt12():
    livro = [decisao('IT-T9-002', 'T9', rel.SIM)]
    ag.autorizar(motivo=ag.COLETA_NORMAL, proposito='T9',
                 source_id='IT-T9-002', livro=livro)


@ataque('RT13', 'trial sem quem responda pela conta',
        'QUEM NAO PROVA QUE A FONTE SERVE PROVA QUEM PAGA',
        invalida('SEM_AUTORIZACAO_HUMANA'))
def rt13():
    ag.autorizar(motivo=ag.TRIAL_DE_CAPACIDADE, proposito='T9',
                 max_execucoes=1, max_usd=0.10, quem_autorizou='',
                 porque='provar a rota', condicao_de_paragem='um POST')


@ataque('RT14', 'trial sem condicao de paragem',
        'O QUE NAO SABE PARAR NAO SABE QUANTO VAI CUSTAR',
        invalida('SEM_CONDICAO_DE_PARAGEM'))
def rt14():
    ag.autorizar(motivo=ag.TRIAL_DE_CAPACIDADE, proposito='T9',
                 max_execucoes=1, max_usd=0.10, quem_autorizou='luciano',
                 porque='provar a rota', condicao_de_paragem='')


@ataque('RT15', 'inventar um quarto motivo de gasto',
        'O VOCABULARIO DOS MOTIVOS E FECHADO',
        invalida('MOTIVO_DESCONHECIDO'))
def rt15():
    ag.autorizar(motivo='COLETA_URGENTE', proposito='T9', max_execucoes=1,
                 max_usd=0.10, quem_autorizou='luciano', porque='urgente',
                 condicao_de_paragem='1')


# ══════════════════════════════════════════════════════════════════════════
# EIXO 2 · A RELEVANCIA DA FONTE (e ela NAO e um portao de gasto)
# ══════════════════════════════════════════════════════════════════════════
@ataque('RT16', 'coletar de uma fonte que ninguem avaliou',
        'AUSENCIA DE AVALIACAO NAO E AUTORIZACAO',
        invalida('RELEVANCIA_NAO_AUTORIZA'))
def rt16():
    ag.autorizar(motivo=ag.COLETA_NORMAL, proposito='T9',
                 source_id='IT-T9-NUNCA-VISTA', max_usd=0.05, livro=[])


@ataque('RT17', 'passar uma URL como identidade da fonte',
        'URL NAO E IDENTIDADE DE FONTE',
        levanta(rel.SourceIdInvalido))
def rt17():
    ag.autorizar(motivo=ag.COLETA_NORMAL, proposito='T9',
                 source_id='https://www.agronotizie.it', max_usd=0.05,
                 livro=[decisao('IT-T9-002', 'T9', rel.SIM)])


@ataque('RT18', 'um SIM em T3 a pagar uma coleta em T9',
        'A DECISAO E DO PAR (FONTE, PROPOSITO)',
        invalida('RELEVANCIA_NAO_AUTORIZA'))
def rt18():
    livro = [decisao('IT-T9-002', 'T3', rel.SIM)]
    ag.autorizar(motivo=ag.COLETA_NORMAL, proposito='T9',
                 source_id='IT-T9-002', max_usd=0.05, livro=livro)


@ataque('RT19', 'ler a recusa por falta de autorizacao como «a fonte nao serve»',
        'AUTHORIZATION_MISSING != NOT_RELEVANT',
        medida('a recusa nomeia o ESTADO, e nao um juizo sobre a fonte'))
def rt19():
    try:
        ag.autorizar(motivo=ag.COLETA_NORMAL, proposito='T9',
                     source_id='IT-T9-NUNCA-VISTA', max_usd=0.05, livro=[])
    except ag.AutorizacaoInvalida as e:
        texto = str(e)
        return (rel.NAO_AVALIADA in texto and 'NAO e o mesmo' in texto,
                'estado na recusa: %s' % (rel.NAO_AVALIADA in texto))
    return False, 'nao recusou'


@ataque('RT20', 'um probe pago a promover a fonte a relevante',
        'PROBE != RELEVANCE DECISION',
        medida('o livro nao ganha linha nenhuma por se ter gasto'))
def rt20():
    livro = []
    a = ag.autorizar(motivo=ag.PROVA_DE_RELEVANCIA, proposito='T9',
                     source_id='IT-T9-003', max_execucoes=1, max_usd=0.01,
                     quem_autorizou='luciano', porque='descobrir se serve',
                     condicao_de_paragem='1 execucao')
    with Mundo() as m:
        comprar(m, a, orcamento=0.01)
        antes = rel.estado('IT-T9-003', 'T9', livro)['ESTADO']
        return (antes == rel.NAO_AVALIADA and livro == [],
                'estado depois do probe pago: %s · linhas no livro: %d'
                % (antes, len(livro)))


# ══════════════════════════════════════════════════════════════════════════
# EIXO 3 · O ORCAMENTO FINANCEIRO (ATE QUANTO)
# ══════════════════════════════════════════════════════════════════════════
@ataque('RT21', 'comprar sem declarar orcamento financeiro nenhum',
        'SEM_LEDGER_NAO_GASTEI', recusa('SEM_LEDGER_NAO_GASTEI'))
def rt21():
    a = trial()
    with Mundo() as m:
        comprar(m, a, orcamento=None)


@ataque('RT22', 'declarar um orcamento maior do que o limite humano',
        'FINANCIAL_BUDGET.AUTHORIZED <= AUTORIZACAO.max_usd',
        recusa('ORCAMENTO_ACIMA_DO_AUTORIZADO'))
def rt22():
    a = trial(max_usd=0.10)
    with Mundo() as m:
        comprar(m, a, orcamento=5.00, teto=0.10)


@ataque('RT23', 'duas execucoes a renovar o limite humano inteiro — O DEFEITO',
        'CADA POST NAO GANHA O LIMITE INTEIRO OUTRA VEZ',
        medida('a exposicao total fica dentro do limite humano'))
def rt23():
    # ⚠️ O fornecedor RESPEITA o teto aqui, e isso e deliberado: este ataque
    # mede a NOSSA trava. Um fornecedor que cobra acima do que lhe mandamos
    # rebentaria o limite mesmo com a nossa trava perfeita — e isso e outro
    # ataque, o RT31, com outro veredito.
    a = trial(max_execucoes=2, max_usd=1.00, condicao_de_paragem='2 execucoes')
    with Mundo() as m:
        m.curl.custos = [0.60, 0.60]
        with coletor.orcamento_financeiro(1.00) as orc:
            for _ in range(2):
                try:
                    comprar(m, a, orcamento=None, teto=1.00)
                except coletor.SemOrcamentoFinanceiro:
                    pass
            exposto = orc.exposto_micros / float(coletor.MICRO)
            return (exposto <= 1.0 + 1e-9,
                    'EXPOSICAO = %.4f com max_usd = 1.00' % exposto)


@ataque('RT24', 'pedir ao fornecedor um teto maior do que o saldo que resta',
        'PROVIDER CAP <= EXECUTION REMAINING',
        medida('o teto enviado e rebaixado ao saldo'))
def rt24():
    a = trial(max_execucoes=2, max_usd=1.00, condicao_de_paragem='2')
    with Mundo() as m:
        m.curl.custos = [0.80]
        with coletor.orcamento_financeiro(1.00):
            comprar(m, a, orcamento=None, teto=1.00)
            comprar(m, a, orcamento=None, teto=1.00)
        return (m.curl.tetos[-1] <= 0.20 + 1e-9,
                'tetos enviados = %s' % m.curl.tetos)


@ataque('RT25', 'custo que a plataforma nao reportou, lido como custo zero',
        'UNKNOWN COST != ZERO COST',
        medida('o dinheiro fica FORA do saldo, como desconhecido'))
def rt25():
    a = trial(max_execucoes=2, max_usd=1.00, condicao_de_paragem='2')
    with Mundo() as m:
        m.curl.custos = [None]
        with coletor.orcamento_financeiro(1.00) as orc:
            comprar(m, a, orcamento=None, teto=0.50)
            return (orc.desconhecido > 0 and orc.restante < 1.00,
                    'DESCONHECIDO = %.4f · RESTANTE = %.4f'
                    % (orc.desconhecido, orc.restante))


@ataque('RT26', 'abrir um segundo orcamento aninhado para ganhar saldo novo',
        'SPEND_AUTHORIZATION != FINANCIAL_BUDGET',
        medida('o limite humano continua a limitar mesmo com saldo novo'))
def rt26():
    a = trial(max_execucoes=1, max_usd=0.10)
    with Mundo() as m:
        with coletor.orcamento_financeiro(0.10):
            comprar(m, a, orcamento=None, teto=0.10)
            with coletor.orcamento_financeiro(0.10):     # saldo novo em folha
                try:
                    comprar(m, a, orcamento=None, teto=0.10)
                except ag.GastoRecusado as e:
                    return (e.causa == 'AUTORIZACAO_ESGOTADA' and m.curl.posts == 1,
                            'causa = %s · POSTS = %d' % (e.causa, m.curl.posts))
        return False, 'o saldo novo comprou: POSTS = %d' % m.curl.posts


# ══════════════════════════════════════════════════════════════════════════
# EIXO 4 · O TETO DE REDE, E A RECUSA QUE NAO SE VESTE DE FONTE
# ══════════════════════════════════════════════════════════════════════════
@ataque('RT27', 'gastar com o teto de ACESSOS esgotado',
        'FINANCIAL_BUDGET != NETWORK_BUDGET',
        medida('zero POST, e o dinheiro reservado volta INTEIRO'))
def rt27():
    a = trial()
    with Mundo() as m:
        with coletor.orcamento_financeiro(0.10) as orc:
            with scrap_http.orcamento_de_rede(0):
                try:
                    comprar(m, a, orcamento=None, rede=None, teto=0.10)
                except scrap_http.SemOrcamentoDeRede:
                    pass
                except BaseException as e:                      # noqa: BLE001
                    return False, 'levantou %s' % type(e).__name__
            return (m.curl.posts == 0 and orc.restante == 0.10 and a._gastas == 0,
                    'POSTS = %d · RESTANTE = %.4f · AUTH_GASTAS = %d'
                    % (m.curl.posts, orc.restante, a._gastas))


@ataque('RT28', 'a recusa desta casa vestida de falha da fonte no manifesto',
        'UM except LARGO NAO DISTINGUE QUEM DISSE NAO',
        medida('a recusa PROPAGA — nao vira STATUS: FAILED da Apify'))
def rt28():
    a = trial()
    with Mundo() as m:
        with coletor.orcamento_financeiro(0.10):
            with scrap_http.orcamento_de_rede(0):
                try:
                    comprar(m, a, orcamento=None, teto=0.10)
                except scrap_http.SemOrcamentoDeRede:
                    return True, 'SemOrcamentoDeRede propagou'
                except BaseException as e:                      # noqa: BLE001
                    return False, 'virou %s' % type(e).__name__
        return False, 'a recusa foi engolida e virou manifesto'


# ══════════════════════════════════════════════════════════════════════════
# EIXO 5 · OS DONOS
# ══════════════════════════════════════════════════════════════════════════
@ataque('RT29', 'o dono da execucao paga a ganhar opiniao sobre a fonte',
        'SOURCE RELEVANCE OWNER != SPEND ENFORCER',
        medida('coletor nao importou o dono da relevancia'))
def rt29():
    mods = [getattr(v, '__name__', '') for v in vars(coletor).values()
            if isinstance(v, types.ModuleType)]
    return ('relevancia_da_fonte' not in mods,
            'modulos que o coletor importou: %s'
            % sorted(x for x in mods if 'relev' in x or 'autoriz' in x) or 'nenhum')


@ataque('RT30', 'a guarda de gasto a ganhar um ledger proprio',
        'LIMITE HUMANO != LEDGER OPERACIONAL',
        medida('a guarda nao expoe nada que some dinheiro'))
def rt30():
    expostos = [n for n in ('OrcamentoFinanceiro', 'Reserva', 'reservar',
                            'liquidar', 'desconhecer', 'anular')
                if hasattr(ag, n)]
    return not expostos, 'a guarda expoe: %s' % (expostos or 'nada de ledger')


@ataque('RT31', 'o fornecedor cobra ACIMA do teto e isso passa por sucesso',
        'UMA TRAVA QUE NAO TRAVOU TEM DE APARECER COMO TAL',
        medida('a reserva fica marcada PROVIDER_EXCEEDED_CAP'))
def rt31():
    a = trial(max_execucoes=1, max_usd=1.00)
    with Mundo() as m:
        m.curl.respeita_o_teto = False
        m.curl.custos = [5.00]                  # pedimos 0.20, ele cobra 5.00
        with coletor.orcamento_financeiro(1.00) as orc:
            comprar(m, a, orcamento=None, teto=0.20)
            fura = [t for t in orc.tentativas
                    if t.get('OUTCOME') == 'PROVIDER_EXCEEDED_CAP']
            return (len(fura) == 1 and fura[0].get('PROVIDER_CAP_BREACH_USD'),
                    'OUTCOMES = %s' % [t.get('OUTCOME') for t in orc.tentativas])


@ataque('RT32', 'importar o sensor troca o transporte e a ida deixa de ser contada',
        'TROCAR O TRANSPORTE NAO PODE TROCAR QUEM CONTA AS IDAS',
        medida('o transporte substituto tambem pede ao dono da rede'))
def rt32():
    import urllib.request
    import sensor_coleta
    saiu = []

    def urlopen_falso(req, *a, **k):
        saiu.append(1)
        raise AssertionError('o pedido SAIU com o teto de acessos a zero')

    real, guardado = urllib.request.urlopen, coletor._curl
    urllib.request.urlopen = urlopen_falso
    try:
        with scrap_http.orcamento_de_rede(0):
            try:
                sensor_coleta._curl_robusto('https://api.apify.com/v2/acts/x/runs',
                                            token='T', metodo='POST', corpo={})
            except scrap_http.SemOrcamentoDeRede:
                return not saiu, 'idas que escaparam ao teto: %d' % len(saiu)
            except BaseException as e:                          # noqa: BLE001
                return False, 'levantou %s' % type(e).__name__
        return False, 'passou sem pedir'
    finally:
        urllib.request.urlopen = real
        coletor._curl = guardado


@ataque('RT33', 'o transporte substituto repete o POST e compra quatro vezes',
        'REPETIR UM GET E BARATO. REPETIR UM POST E COMPRAR DE NOVO',
        medida('um POST, uma tentativa'))
def rt33():
    import urllib.request
    import sensor_coleta
    tentativas = []

    def urlopen_falso(req, *a, **k):
        tentativas.append(req.get_method())
        raise OSError('ws_closed_mid_exchange')

    real, guardado = urllib.request.urlopen, coletor._curl
    urllib.request.urlopen = urlopen_falso
    try:
        try:
            sensor_coleta._curl_robusto('https://api.apify.com/v2/acts/x/runs',
                                        token='T', metodo='POST', corpo={})
        except coletor.PostTalvezCriado:
            pass
        except BaseException as e:                              # noqa: BLE001
            return False, 'levantou %s' % type(e).__name__
        return len(tentativas) == 1, 'POSTs enviados = %d' % len(tentativas)
    finally:
        urllib.request.urlopen = real
        coletor._curl = guardado


@ataque('RT34', 'a rede recusa e mesmo assim queima uma execucao autorizada',
        'UM POST QUE NAO SAIU NAO GASTA UMA AUTORIZACAO',
        medida('a autorizacao volta intacta'))
def rt34():
    a = trial(max_execucoes=1, max_usd=0.10)
    with Mundo() as m:
        with coletor.orcamento_financeiro(0.10):
            with scrap_http.orcamento_de_rede(0):
                try:
                    comprar(m, a, orcamento=None, teto=0.10)
                except scrap_http.SemOrcamentoDeRede:
                    pass
                except BaseException as e:                      # noqa: BLE001
                    return False, 'levantou %s' % type(e).__name__
        return (a._gastas == 0 and m.curl.posts == 0,
                'AUTH_GASTAS = %d · POSTS = %d' % (a._gastas, m.curl.posts))


@ataque('RT35', 'devolver a execucao quando o POST TALVEZ tenha saido',
        'AUSENCIA DE NOTICIA NAO E PROVA DE AUSENCIA DE COMPRA',
        medida('a unidade NAO volta quando o POST caiu no transporte'))
def rt35():
    a = trial(max_execucoes=2, max_usd=0.20, condicao_de_paragem='2')
    with Mundo() as m:
        def cai_no_post(cmd, **k):
            if '-X' in cmd and cmd[cmd.index('-X') + 1] == 'POST':
                m.curl.posts += 1
                r = CurlFalso._R('', rc=56, err='ws_closed_mid_exchange')
                return r
            return CurlFalso._R(json.dumps({'data': {}}))
        coletor.subprocess.run = cai_no_post
        with coletor.orcamento_financeiro(0.20) as orc:
            comprar(m, a, orcamento=None, teto=0.20)
            return (a._gastas == 1 and orc.desconhecido > 0,
                    'AUTH_GASTAS = %d · DESCONHECIDO = %.4f'
                    % (a._gastas, orc.desconhecido))


def main():
    linhas, vivos = [], 0
    for ident, nome, lei, julgar, fn in ATAQUES:
        morreu, observado = julgar(fn)
        veredito = MORREU if morreu else VIVO
        vivos += 0 if morreu else 1
        linhas.append({'ID': ident, 'ATAQUE': nome, 'LEI': lei,
                       'VEREDITO': veredito, 'OBSERVADO': observado})
        print('  %s  %-6s %-62s %s' % ('·' if morreu else '!', ident, nome[:62],
                                       veredito))
        if not morreu:
            print('          %s' % observado)

    print()
    print('  ATAQUES = %d · MORRERAM = %d · ATAQUE_VIVO = %d'
          % (len(linhas), len(linhas) - vivos, vivos))
    print('  NETWORK_REAL = 0 · APIFY_REAL_RUNS = 0 · REAL_COST_USD = 0')

    os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
    with open(SAIDA, 'w', encoding='utf-8') as f:
        json.dump({'CONTRATO': 'RED_TEAM_CONVERGENCIA/v1',
                   'ATAQUES': len(linhas),
                   'MORRERAM': len(linhas) - vivos,
                   'ATAQUE_VIVO': vivos,
                   'PAID_REAL_RUNS': 0, 'REAL_COST_USD': 0,
                   'LINHAS': linhas}, f, ensure_ascii=False, indent=1)
    print('  escrito: %s' % os.path.relpath(SAIDA, RAIZ))
    return 1 if vivos else 0


if __name__ == '__main__':
    raise SystemExit(main())
