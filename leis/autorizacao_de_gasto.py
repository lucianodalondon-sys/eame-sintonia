#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A AUTORIZACAO DE GASTO — «esta compra foi autorizada, para ISTO?»

    py leis/autorizacao_de_gasto.py     # o contrato, dito em voz alta

E a unica pergunta deste ficheiro. Ele NAO pergunta se a fonte serve, se a rota
e permitida, se ha saldo, nem se o item interessa. Essas quatro tem donos, e
estao nomeados no fim deste cabecalho.

    SPEND_GUARD_OWNER = leis/autorizacao_de_gasto.py

POR QUE ISTO EXISTE
-------------------
Medido nesta arvore, antes desta lei:

    PAID_CREATION_PRIMITIVES        = 1   coleta/coletor.py:616
    PRODUCTION_CALLERS_OF_THAT_DOOR = 4
    CALLERS_REQUIRING_AUTHORIZATION = 0

`coleta/coletor.py` e o dono unico do POST que acende um ator — e o unico
`metodo='POST'` da arvore inteira, medido. Mas ele nao perguntava a NINGUEM se
aquela compra estava autorizada. Havia orcamento de rede, orcamento financeiro,
teto do lado do provider, uma trava de retentativa e o registo do custo — cinco
travas sobre QUANTO se podia gastar, e nenhuma sobre SE se podia.

    TER TETO NAO E TER PERMISSAO. UM TETO DIZ «NAO MAIS QUE ISTO».
    UMA AUTORIZACAO DIZ «ISTO, E SO ISTO».

E o token nao responde a pergunta:

    TOKEN_PRESENT != SPEND_AUTHORIZED
    CREDENTIAL    != AUTHORIZATION
    ROUTE_ALLOWED != SPEND_AUTHORIZED
    BUDGET_PRESENT != SPEND_AUTHORIZED

O QUE ESTA LEI NAO FAZ, E QUEM O FAZ
-------------------------------------
    quem julga a FONTE ....... leis/relevancia_da_fonte.py   (SR-01, outro ramo)
    quem julga a ROTA ........ leis/social_matriz.py
    quem guarda o TOKEN ...... ferramentas/apify_pool.py
    quem cria a EXECUCAO ..... coleta/coletor.py
    quem limita o DINHEIRO ... coleta/coletor.py :: orcamento_financeiro
    quem limita a REDE ....... coleta/scrap_http.py :: orcamento_de_rede
    quem julga o ITEM ........ ninguem aqui, e de proposito

    SOURCE_RELEVANCE != COST != ROUTE_POLICY != ITEM_RELEVANCE.

    O SCRAP NAO JULGA RELEVANCIA. ELE OBEDECE A UMA AUTORIZACAO.

Esta lei nao calcula relevancia e nao sabe calcula-la. Ela VERIFICA que uma
decisao do dono certo veio junto, que ela e do PAR exacto que se vai colher, e
que os tetos declarados nela cobrem esta chamada. O vocabulario vem do dono:
`leis/relevancia_da_fonte.py`, que por sua vez o importa de `admissao`. Tres
ficheiros, uma lista de palavras — e a lista continua a ser UMA porque esta lei
nao guarda copia dela. Enquanto o dono nao estiver nesta arvore, os dois modos
que julgam fonte recusam com `DONO_DA_RELEVANCIA_AUSENTE`.

OS TRES MODOS, E ELES NAO SE SUBSTITUEM
----------------------------------------
    NORMAL_COLLECTION        colher uma fonte que JA foi avaliada e serve
    SOURCE_EVALUATION_PROBE  obter amostra pequena de fonte AINDA NAO avaliada,
                             para que o dono da relevancia POSSA avalia-la
    CAPABILITY_TRIAL         medir se um provider/rota/capacidade CONSEGUE

O `PROBE` existe por uma razao logica e nao por conveniencia: exigir
`RELEVANCE_RESULT = SIM` para tudo fecharia um ciclo — uma fonte nunca avaliada
nunca poderia ser amostrada, e sem amostra ninguem a avalia.

    UM PORTAO QUE EXIGE A RESPOSTA PARA DEIXAR FAZER A PERGUNTA
    NAO E UM PORTAO. E UM MURO.

Mas o PROBE **nao** promove nada, e isso e a outra metade:

    PROBE != DECISION. Depois de um probe, a fonte continua NAO_AVALIADA
    ate que o dono da relevancia escreva no livro dele.

E nenhum dos tres pode vestir-se de outro:

    NORMAL_COLLECTION NAO PODE DECLARAR-SE TRIAL NEM PROBE PARA FURAR O GATE.

O `TRIAL` desta lei tambem **nao e** o `scrap_executor.TRIAL`. Aquele e um eixo
EPISTEMOLOGICO — «vou medir se consigo, e nao espero resultado» — e o proprio
ficheiro dele escreve `TRIAL NAO AUTORIZA GASTO`. Continua a nao autorizar. Esta
lei e que autoriza, e exige autorizacao humana explicita para o fazer.

    MODO EPISTEMOLOGICO != AUTORIZACAO DE GASTO.
"""
from __future__ import annotations

import contextlib
import os
import sys
import threading
from dataclasses import dataclass, field, asdict

_HERE = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(_HERE)
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401

# ── O EIXO DA RELEVANCIA VEM DO DONO DELE, E O DONO NAO SE COPIA PARA CA ──
# Duas listas com as mesmas palavras sao duas verdades, e a segunda envelhece
# calada. `leis/relevancia_da_fonte.py` e o dono do eixo, e ele importa as
# palavras de `admissao`. Aqui importa-se DELE.
#
#     DEPENDER DO DONO != SER O DONO.
#
# O dono nasce na SR-01, NOUTRO RAMO. Trazer o ficheiro dele para dentro desta
# missao faria desta arvore um SEGUNDO dono do mesmo conceito — e dois donos do
# mesmo conceito e o defeito que o System Map existe para apanhar. Entao ele nao
# vem: importa-se se estiver, e se nao estiver esta lei RECUSA em vez de
# adivinhar as palavras dele.
#
#     SEM O DONO DA RELEVANCIA, NENHUMA COLHEITA COM FONTE E AUTORIZAVEL.
#
# Fechar por ausencia e MAIS trava, nao menos. O `CAPABILITY_TRIAL` nao julga
# fonte nenhuma e continua a funcionar — e por isso as sentinelas desta casa
# continuam a poder atravessar a porta paga contra um provider falso. O `NORMAL`
# e o `PROBE`, que julgam fonte, passam a recusar com nome proprio.
try:
    import relevancia_da_fonte as rf  # noqa: E402
    DONO_DA_RELEVANCIA = rf.CONTRATO
except ImportError:                                   # pragma: no cover
    rf = None
    DONO_DA_RELEVANCIA = None

CONTRATO = 'AUTORIZACAO_DE_GASTO/v1'

# ── OS TRES MODOS ─────────────────────────────────────────────────────────
NORMAL = 'NORMAL_COLLECTION'
PROBE = 'SOURCE_EVALUATION_PROBE'
TRIAL = 'CAPABILITY_TRIAL'
MODOS = (NORMAL, PROBE, TRIAL)

#: Os modos que exigem autorizacao HUMANA explicita. O `NORMAL` nao esta aqui
#: porque a decisao que o autoriza ja e humana por construcao: ela vem do livro
#: de relevancia, que gente escreve. Os outros dois gastam SEM essa decisao, e
#: por isso precisam de alguem a assinar por eles.
EXIGEM_HUMANO = (PROBE, TRIAL)

#: Os modos que precisam de saber QUE FONTE se vai colher. O `TRIAL` nao: ele
#: mede o provider, nao a fonte — e fingir uma fonte para um trial seria
#: fabricar um par que ninguem avaliou.
EXIGEM_FONTE = (NORMAL, PROBE)

# ── O VOCABULARIO FECHADO DA RECUSA ───────────────────────────────────────
# Cada recusa diz UMA coisa. `NOT_RELEVANT` para tudo seria transformar sete
# ausencias diferentes num julgamento que ninguem fez.
#
#     AUSENCIA DE AUTORIZACAO CONTINUA A SER AUSENCIA DE AUTORIZACAO.
AUTORIZA = 'AUTORIZA'
SEM_AUTORIZACAO = 'SEM_AUTORIZACAO'
MODO_DESCONHECIDO = 'MODO_DESCONHECIDO'
FONTE_AUSENTE = 'SOURCE_ID_AUSENTE'
FONTE_INVALIDA = 'SOURCE_ID_INVALIDO'
FONTE_DIFERENTE = 'AUTORIZACAO_DE_OUTRA_FONTE'
PROPOSITO_AUSENTE = 'PROPOSITO_AUSENTE'
PROPOSITO_DIFERENTE = 'AUTORIZACAO_DE_OUTRO_PROPOSITO'
RELEVANCIA_AUSENTE = 'RELEVANCE_RESULT_AUSENTE'
RELEVANCIA_NAO_AUTORIZA = 'RELEVANCE_RESULT_NAO_AUTORIZA'
VEREDITO_NAO_AUTORIZA = 'RELEVANCE_VERDICT_NAO_AUTORIZA'
SEM_HUMANO = 'AUTORIZACAO_HUMANA_AUSENTE'
SEM_TETO = 'TETO_AUSENTE'
TETO_ESTOURADO = 'TETO_ESTOURADO'
TETO_ACIMA_DO_AUTORIZADO = 'TETO_ACIMA_DO_AUTORIZADO'
SEM_ALVO = 'ALVO_AUSENTE'
#: O dono da relevancia nao esta na arvore. NAO e o mesmo que «a fonte nao
#: serve»: e «a lei que julga fontes nao esta instalada». Uma recusa que
#: dissesse RELEVANCE_RESULT_AUSENTE aqui esconderia um facto de ARQUITETURA
#: atras de um facto de DADOS, e quem lesse o rasto procuraria a decisao em vez
#: do ficheiro.
DONO_AUSENTE = 'DONO_DA_RELEVANCIA_AUSENTE'
RECUSAS = (SEM_AUTORIZACAO, MODO_DESCONHECIDO, FONTE_AUSENTE, FONTE_INVALIDA,
           FONTE_DIFERENTE, PROPOSITO_AUSENTE, PROPOSITO_DIFERENTE,
           RELEVANCIA_AUSENTE, RELEVANCIA_NAO_AUTORIZA, VEREDITO_NAO_AUTORIZA,
           SEM_HUMANO, SEM_TETO, TETO_ESTOURADO, TETO_ACIMA_DO_AUTORIZADO,
           SEM_ALVO, DONO_AUSENTE)

#: Os tetos que TODA autorizacao tem de declarar. Um teto ausente nao e um teto
#: infinito: e uma autorizacao incompleta, e ela nao autoriza.
TETOS = ('MAX_PROVIDER_RUNS', 'MAX_START_POSTS', 'MAX_USD', 'MAX_ITEMS')

#: O que esta lei NUNCA cria. Escrito para que a proxima missao nao o invente.
NAO_CRIAR = ('SOURCE_SCORE', 'RELEVANCE_COMPUTATION', 'ITEM_RELEVANCE',
             'AUTO_PROMOTION', 'AUTORIZACAO_IMPLICITA_POR_TOKEN',
             'AUTORIZACAO_IMPLICITA_POR_ORCAMENTO')


class AutorizacaoInvalida(ValueError):
    """A autorizacao nao respeita o contrato. Levanta na CONSTRUCAO, nao no uso.

    Uma autorizacao mal formada que so rebentasse no momento da compra seria uma
    autorizacao que passou por todo o codigo a parecer valida.
    """


class SemAutorizacaoDeGasto(RuntimeError):
    """A compra foi recusada. Carrega o veredito inteiro, nunca so uma frase."""

    def __init__(self, veredito):
        self.veredito = veredito
        super().__init__('%s · %s' % (veredito.get('RECUSA'), veredito.get('PORQUE')))


@dataclass
class Autorizacao:
    """Uma autorizacao de gasto. Imutavel no que decide; contavel no que gasta.

    Os campos de decisao sao conferidos na construcao. Os contadores sobem a
    cada compra, e e o que faz `MAX_START_POSTS = 1` significar UM.
    """
    MODO: str
    #: Quem assinou. Obrigatorio em PROBE e TRIAL — ver `EXIGEM_HUMANO`.
    HUMAN_AUTHORIZATION: str = None
    PROPOSITO: str = None
    SOURCE_ID: str = None
    #: A decisao do dono da relevancia, copiada e nao recalculada.
    RELEVANCE_RESULT: str = None
    RELEVANCE_VERDICT: str = None
    DECISION_VERSION: str = None
    EVIDENCE_REFERENCE: str = None
    #: O alvo do TRIAL: provider/rota/capacidade que se vai medir.
    ALVO: str = None
    MAX_PROVIDER_RUNS: int = None
    MAX_START_POSTS: int = None
    MAX_USD: float = None
    MAX_ITEMS: int = None
    #: Contadores. Nao entram na igualdade nem no `asdict` de decisao.
    _posts: int = field(default=0, repr=False)
    _runs: int = field(default=0, repr=False)

    def __post_init__(self):
        if self.MODO not in MODOS:
            raise AutorizacaoInvalida(
                'MODO %r fora do vocabulario. Aceitos: %s' % (self.MODO, ', '.join(MODOS)))
        for t in TETOS:
            v = getattr(self, t)
            if v is None:
                raise AutorizacaoInvalida(
                    '%s: %s ausente. UM TETO AUSENTE NAO E UM TETO INFINITO — e uma '
                    'autorizacao incompleta.' % (self.MODO, t))
            if v < 0:
                raise AutorizacaoInvalida('%s: %s negativo (%r)' % (self.MODO, t, v))
        if self.MODO in EXIGEM_HUMANO and not self.HUMAN_AUTHORIZATION:
            raise AutorizacaoInvalida(
                '%s exige HUMAN_AUTHORIZATION: ele gasta SEM uma decisao de relevancia, '
                'entao alguem assina por ele.' % self.MODO)
        if self.MODO in EXIGEM_FONTE:
            if rf is None:
                raise AutorizacaoInvalida(
                    '%s exige o dono da relevancia (leis/relevancia_da_fonte.py) e ele '
                    'nao esta nesta arvore. ESTA LEI NAO ADIVINHA O VOCABULARIO DELE.'
                    % self.MODO)
            if not self.SOURCE_ID:
                raise AutorizacaoInvalida('%s exige SOURCE_ID' % self.MODO)
            # URL NAO E SOURCE_ID, e quem o diz e o dono do SOURCE_ID.
            rf.conferir_source_id(self.SOURCE_ID)
            if not self.PROPOSITO:
                raise AutorizacaoInvalida(
                    '%s exige PROPOSITO: a decisao e do PAR (fonte, proposito), nunca da '
                    'fonte sozinha.' % self.MODO)
        if self.MODO == NORMAL:
            if not self.RELEVANCE_RESULT:
                raise AutorizacaoInvalida(
                    'NORMAL_COLLECTION exige RELEVANCE_RESULT do dono da relevancia. '
                    'Sem ele isto seria um PROBE sem assinatura.')
            if self.RELEVANCE_RESULT not in rf.RESULTADOS and self.RELEVANCE_RESULT != rf.NAO_AVALIADA:
                raise AutorizacaoInvalida(
                    'RELEVANCE_RESULT %r fora do vocabulario do dono. Aceitos: %s, %s'
                    % (self.RELEVANCE_RESULT, ', '.join(rf.RESULTADOS), rf.NAO_AVALIADA))
        if self.MODO == TRIAL and not self.ALVO:
            raise AutorizacaoInvalida(
                'CAPABILITY_TRIAL exige ALVO: um ensaio sem alvo fixo e uma compra sem '
                'pergunta.')

    # ── O QUE JA SE GASTOU DESTA AUTORIZACAO ──────────────────────────────
    def consumir(self):
        """Conta UM POST e UMA execucao. Chamado DEPOIS de autorizado."""
        self._posts += 1
        self._runs += 1

    @property
    def posts_usados(self):
        return self._posts

    @property
    def runs_usadas(self):
        return self._runs

    def decisao(self):
        """→ so os campos de DECISAO, sem contadores. E o que vai para o rasto."""
        d = asdict(self)
        d.pop('_posts', None)
        d.pop('_runs', None)
        return d


# ══════════════════════════════════════════════════════════════════════════
# O CONTEXTO — o mesmo desenho que os dois orcamentos ja usam
# ══════════════════════════════════════════════════════════════════════════
# Ambiente, e nao parametro, pelo motivo que `coletor.orcamento_financeiro` ja
# escreveu: a autorizacao atravessa camadas que nao tem porque a conhecer. O que
# NAO se herda e o valor por omissao: sem ninguem instalar, e `None`, e `None`
# recusa.
#
#     FAIL CLOSED: NENHUMA AUTORIZACAO INSTALADA == NENHUMA COMPRA.
_LOCAL = threading.local()


def autorizacao_actual():
    """A autorizacao desta execucao, ou None quando ninguem declarou uma."""
    return getattr(_LOCAL, 'autorizacao', None)


@contextlib.contextmanager
def autorizacao(auth):
    """Instala UMA autorizacao para o bloco inteiro."""
    if not isinstance(auth, Autorizacao):
        raise AutorizacaoInvalida(
            'so uma Autorizacao autoriza. Recebi %s — e um dicionario que se parece com '
            'uma autorizacao nao passou pela conferencia dela.' % type(auth).__name__)
    anterior = getattr(_LOCAL, 'autorizacao', None)
    _LOCAL.autorizacao = auth
    try:
        yield auth
    finally:
        _LOCAL.autorizacao = anterior


# ══════════════════════════════════════════════════════════════════════════
# A CONFERENCIA
# ══════════════════════════════════════════════════════════════════════════
def _nao(recusa, porque, **extra):
    v = {'CONTRATO': CONTRATO, 'AUTORIZA': False, 'RECUSA': recusa, 'PORQUE': porque}
    v.update(extra)
    return v


def conferir(auth, *, source_id=None, proposito=None, actor=None, teto_usd=None):
    """→ o veredito. Nao levanta, nao gasta, nao toca a rede. Custa zero.

    Publica de proposito: e isto que as sentinelas exercem, e e isto que um
    mutante que aceite `NAO_AVALIADA` faz mudar de resposta.
    """
    if auth is None:
        return _nao(SEM_AUTORIZACAO,
                    'nenhuma autorizacao instalada. Ter token, rota permitida e orcamento '
                    'nao e ter permissao.')
    if not isinstance(auth, Autorizacao):
        return _nao(SEM_AUTORIZACAO,
                    'o objeto instalado nao e uma Autorizacao conferida (%s)'
                    % type(auth).__name__)
    if auth.MODO not in MODOS:
        return _nao(MODO_DESCONHECIDO, 'MODO %r' % auth.MODO)

    # ── OS TETOS, ANTES DE TUDO O RESTO ───────────────────────────────────
    # Um teto ja estourado recusa qualquer modo. Conferir isto primeiro impede
    # que uma autorizacao valida compre duas vezes por a segunda compra ter
    # passado pelas mesmas conferencias de identidade.
    if auth.posts_usados >= auth.MAX_START_POSTS:
        return _nao(TETO_ESTOURADO,
                    'MAX_START_POSTS = %d, e %d POST(s) ja sairam desta autorizacao'
                    % (auth.MAX_START_POSTS, auth.posts_usados),
                    TETO='MAX_START_POSTS')
    if auth.runs_usadas >= auth.MAX_PROVIDER_RUNS:
        return _nao(TETO_ESTOURADO,
                    'MAX_PROVIDER_RUNS = %d, e %d execucao(oes) ja nasceram'
                    % (auth.MAX_PROVIDER_RUNS, auth.runs_usadas),
                    TETO='MAX_PROVIDER_RUNS')
    if teto_usd is not None and teto_usd > auth.MAX_USD:
        return _nao(TETO_ACIMA_DO_AUTORIZADO,
                    'a chamada pede teto %s e a autorizacao concede %s'
                    % (teto_usd, auth.MAX_USD), TETO='MAX_USD')

    if auth.MODO in EXIGEM_HUMANO and not auth.HUMAN_AUTHORIZATION:
        return _nao(SEM_HUMANO, '%s sem assinatura humana' % auth.MODO)

    # ── A IDENTIDADE DO QUE SE VAI COLHER ─────────────────────────────────
    if auth.MODO in EXIGEM_FONTE:
        # Sem o dono, nao ha vocabulario nem validador de SOURCE_ID — e uma
        # guarda que decidisse sem eles estaria a inventar a lei do vizinho.
        if rf is None:
            return _nao(DONO_AUSENTE,
                        '%s exige leis/relevancia_da_fonte.py e ele nao esta nesta '
                        'arvore. SEM O DONO DA RELEVANCIA, NENHUMA COLHEITA COM FONTE '
                        'E AUTORIZAVEL.' % auth.MODO)
        if not source_id:
            return _nao(FONTE_AUSENTE,
                        'a chamada nao declarou SOURCE_ID, e %s exige o par exacto'
                        % auth.MODO)
        try:
            rf.conferir_source_id(source_id)
        except rf.SourceIdInvalido as e:
            return _nao(FONTE_INVALIDA, str(e))
        if source_id != auth.SOURCE_ID:
            return _nao(FONTE_DIFERENTE,
                        'autorizado para %r e a chamada colhe %r'
                        % (auth.SOURCE_ID, source_id))
        if not proposito:
            return _nao(PROPOSITO_AUSENTE,
                        'a chamada nao declarou PROPOSITO, e a decisao e do PAR')
        if proposito != auth.PROPOSITO:
            return _nao(PROPOSITO_DIFERENTE,
                        'autorizado para %r e a chamada colhe %r'
                        % (auth.PROPOSITO, proposito))

    # ── E A RELEVANCIA, SO PARA O MODO QUE A EXIGE ────────────────────────
    if auth.MODO == NORMAL:
        if not auth.RELEVANCE_RESULT:
            return _nao(RELEVANCIA_AUSENTE, 'NORMAL_COLLECTION sem RELEVANCE_RESULT')
        # SO `SIM` autoriza. As outras cinco palavras — NAO, NAO_SEI,
        # NAO_SE_APLICA, ERRO, NAO_AVALIADA — recusam, e recusam com o nome
        # delas para que o rasto nao as ache a mesma coisa.
        if auth.RELEVANCE_RESULT != rf.SIM:
            return _nao(RELEVANCIA_NAO_AUTORIZA,
                        'RELEVANCE_RESULT = %s. Só %s autoriza gasto, e as outras nao sao '
                        'sinonimos umas das outras.' % (auth.RELEVANCE_RESULT, rf.SIM),
                        RELEVANCE_RESULT=auth.RELEVANCE_RESULT)
        # E o veredito do portao do dono, quando ele veio, tem de concordar.
        if auth.RELEVANCE_VERDICT and auth.RELEVANCE_VERDICT != rf.AUTORIZA:
            return _nao(VEREDITO_NAO_AUTORIZA,
                        'RELEVANCE_VERDICT = %s' % auth.RELEVANCE_VERDICT)
    if auth.MODO == TRIAL and not auth.ALVO:
        return _nao(SEM_ALVO, 'CAPABILITY_TRIAL sem alvo')

    return {'CONTRATO': CONTRATO, 'AUTORIZA': True, 'RECUSA': None,
            'MODO': auth.MODO, 'SOURCE_ID': auth.SOURCE_ID,
            'PROPOSITO': auth.PROPOSITO,
            'RELEVANCE_RESULT': auth.RELEVANCE_RESULT,
            'RELEVANCE_VERDICT': auth.RELEVANCE_VERDICT,
            'DECISION_VERSION': auth.DECISION_VERSION,
            'EVIDENCE_REFERENCE': auth.EVIDENCE_REFERENCE,
            'HUMAN_AUTHORIZATION': auth.HUMAN_AUTHORIZATION,
            'ALVO': auth.ALVO, 'ACTOR': actor,
            'POSTS_USED': auth.posts_usados, 'MAX_START_POSTS': auth.MAX_START_POSTS,
            'MAX_USD': auth.MAX_USD, 'MAX_ITEMS': auth.MAX_ITEMS,
            'PORQUE': None}


def exigir(*, actor=None, source_id=None, proposito=None, teto_usd=None):
    """A GUARDA. Levanta `SemAutorizacaoDeGasto` ou devolve o veredito e CONSOME.

    Chamada por `coleta/coletor.py` imediatamente antes de comprometer dinheiro.
    E o unico sitio da casa que decide se uma compra acontece.

        A GUARDA NAO DECIDE SE A FONTE E RELEVANTE. Ela verifica uma decisao que
        ja veio do dono certo, para o par exacto, dentro dos tetos declarados.
    """
    auth = autorizacao_actual()
    v = conferir(auth, source_id=source_id, proposito=proposito, actor=actor,
                 teto_usd=teto_usd)
    if not v['AUTORIZA']:
        raise SemAutorizacaoDeGasto(v)
    auth.consumir()
    v['POSTS_USED'] = auth.posts_usados
    return v


LEIS = (
    'TOKEN_PRESENT != SPEND_AUTHORIZED',
    'CREDENTIAL != AUTHORIZATION',
    'ROUTE_ALLOWED != SPEND_AUTHORIZED',
    'BUDGET_PRESENT != SPEND_AUTHORIZED',
    'PAID_PROVIDER != POLICY_OVERRIDE',
    'NORMAL_COLLECTION != SOURCE_EVALUATION_PROBE != CAPABILITY_TRIAL',
    'PROBE != DECISION',
    'UM TETO AUSENTE NAO E UM TETO INFINITO',
    'AUSENCIA DE AUTORIZACAO CONTINUA A SER AUSENCIA DE AUTORIZACAO',
)


def main():
    print('\n%s\n%s\n' % (CONTRATO, '=' * len(CONTRATO)))
    print('MODOS            %s' % ' · '.join(MODOS))
    print('EXIGEM_HUMANO    %s' % ' · '.join(EXIGEM_HUMANO))
    print('EXIGEM_FONTE     %s' % ' · '.join(EXIGEM_FONTE))
    print('TETOS            %s' % ' · '.join(TETOS))
    if rf is None:
        print('DONO DA RELEVANCIA  AUSENTE nesta arvore — %s e %s recusam com %s'
              % (NORMAL, PROBE, DONO_AUSENTE))
    else:
        print('SO AUTORIZA      RELEVANCE_RESULT = %s (dono: %s)' % (rf.SIM, rf.CONTRATO))
    print('\nRECUSAS (%d):' % len(RECUSAS))
    for r in RECUSAS:
        print('   %s' % r)
    print('\nNAO_CRIAR:')
    for n in NAO_CRIAR:
        print('   %s' % n)
    print()
    for lei in LEIS:
        print('   %s' % lei)
    print()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
