#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A AUTORIZACAO DE GASTO — nenhuma compra sem quem responda por ela.

    py leis/autorizacao_de_gasto.py          # o contrato, dito em voz alta

    UMA CHAVE NO COFRE NAO E UMA CHAVE NO PROCESSO.
    UMA CHAVE NO PROCESSO NAO E AUTORIZACAO PARA GASTAR.

POR QUE ISTO EXISTE
-------------------
Medido nesta arvore, e nao herdado:

    PAID_CREATION_PRIMITIVES  = 1    coleta/coletor.py :: executar
    PODEM_CRIAR_EXECUCAO_PAGA = 5
    DESTES, QUE PERGUNTAVAM SE A FONTE SERVIA = 0

Havia exactamente UMA porta que acende execucao paga — o
`POST /v2/acts/{ator}/runs` dentro de `coletor.executar` — e para a atravessar
bastava ter um token na mao. Ter a credencial era, na pratica, ter a
autorizacao; e nenhuma das duas dizia PARA QUE FONTE nem PARA QUE PROPOSITO o
dinheiro estava a ser gasto.

    CREDENTIAL != AUTHORIZATION.
    TOKEN_PRESENT != SPEND_ALLOWED.
    ALLOWED_ROUTE != AUTHORIZED_SPEND.

⚠️ ESTE FICHEIRO NAO JULGA FONTE
---------------------------------
A relevancia de fonte tem dono, e nao e este: `leis/relevancia_da_fonte.py`.
Aqui **pergunta-se** a ele e obedece-se a resposta. Nem o dono da credencial
(`ferramentas/apify_pool.py`) nem o dono da execucao paga
(`coleta/coletor.py`) abrem o livro de relevancia — se abrissem, nasceria um
segundo dono da mesma verdade, e duas verdades divergem na terceira vez que
alguem mexe numa.

    ONE CONCEPT -> ONE OWNER.
    SOURCE RELEVANCE OWNER != SPEND ENFORCER.

TRES MOTIVOS DE GASTO, E NAO SAO A MESMA COISA
-----------------------------------------------
Tratar toda execucao paga como «coleta» fecharia a porta pela qual uma fonte
nova poderia alguma vez ser avaliada, e abriria a porta a chamar coleta de
«teste».

    COLETA_NORMAL_DA_FONTE
        colher de uma fonte para um proposito. EXIGE que a relevancia do par
        (FONTE, PROPOSITO) esteja provada. E o caso comum.

    PROVA_DE_RELEVANCIA_DA_FONTE
        o probe pequeno que existe PARA DESCOBRIR se a fonte serve. NAO pode
        exigir relevancia provada — exigi-la fecharia o ciclo:

            para gastar e preciso ser relevante
            -> para provar que e relevante e preciso observar
            -> para observar e preciso gastar

        Exige outra coisa: autorizacao humana, teto de execucoes, teto de
        dolares, amostra limitada e condicao de paragem.

    TRIAL_DE_CAPACIDADE
        a prova tecnica de que uma ROTA funciona — a C10.7 e a C10.8B desta
        casa. Nao pergunta se a fonte serve, porque nao esta a colher a fonte:
        esta a medir o caminho. Exige alvo fixo, autorizacao humana e tetos.

    TRIAL != COLLECTION.  PROBE != RELEVANCE DECISION.

E NENHUM DOS TRES SE DISFARCA DO OUTRO: o motivo entra na autorizacao, a
autorizacao e verificada contra o que a corrida DECLARA fazer, e uma
autorizacao de TRIAL nao serve para uma coleta normal.

A AUTORIZACAO NAO SE FABRICA
-----------------------------
Um chamador nao consegue construir uma `Autorizacao` valida sem passar por
`autorizar()`, que e onde as perguntas sao feitas. Nao e cerimonia: a maneira
mais provavel de este portao morrer e alguem, com pressa, montar o dicionario
a mao e passa-lo adiante.

    UMA AUTORIZACAO QUE O CHAMADOR CONSEGUE ESCREVER
    E UM CAMPO DE FORMULARIO, NAO UMA AUTORIZACAO.

E ELA GASTA-SE
--------------
Cada execucao paga CONSOME uma unidade da autorizacao. Uma autorizacao de uma
execucao nao paga duas — e isto nao e teoria: `ferramentas/apify_pool.py`
rotaciona a chave e RETOMA a mesma unidade quando a chave esgota, e
`regras/sensor_coleta.py` percorre o pool inteiro. Sem consumo, uma unica
autorizacao pagaria tantas execucoes quantas chaves houvesse no cofre.

    ROTACAO DE CHAVE NAO E NOVA AUTORIZACAO.
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone

_HERE = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(_HERE)
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401

import relevancia_da_fonte as rel  # noqa: E402 — PERGUNTA-SE; nao se decide aqui

CONTRATO = 'AUTORIZACAO_DE_GASTO/v1'
VERSAO_DA_GUARDA = '1'

# ── OS TRES MOTIVOS ─────────────────────────────────────────────────────────
COLETA_NORMAL = 'COLETA_NORMAL_DA_FONTE'
PROVA_DE_RELEVANCIA = 'PROVA_DE_RELEVANCIA_DA_FONTE'
TRIAL_DE_CAPACIDADE = 'TRIAL_DE_CAPACIDADE'
MOTIVOS = (COLETA_NORMAL, PROVA_DE_RELEVANCIA, TRIAL_DE_CAPACIDADE)

# Os dois que NAO sao coleta da fonte, e por isso nao passam pelo portao de
# relevancia. Em troca, os dois exigem autorizacao humana e tetos.
MOTIVOS_DE_EXCECAO = (PROVA_DE_RELEVANCIA, TRIAL_DE_CAPACIDADE)

# ── O VEREDITO ──────────────────────────────────────────────────────────────
# A casa ja tem idioma para isto: `SEM_CHECKPOINT_NAO_GASTEI` (COL-LAW-017).
# Segue-se o mesmo — recusar gasto diz-se na primeira pessoa e no passado.
AUTORIZADO = 'AUTORIZADO'
SEM_AUTORIZACAO_NAO_GASTEI = 'SEM_AUTORIZACAO_NAO_GASTEI'
VEREDITOS = (AUTORIZADO, SEM_AUTORIZACAO_NAO_GASTEI)

# ── AS CAUSAS DA RECUSA, e nenhuma delas diz «a fonte nao serve» ────────────
# ⚠️ ESTA DISTINCAO E O CORACAO DO FICHEIRO. Recusar gasto por falta de
# autorizacao NAO e um juizo sobre a fonte. Um sistema que respondesse
# `NOT_RELEVANT` a uma fonte que ninguem chegou a avaliar estaria a inventar
# uma medicao que nao existe.
#
#     AUTHORIZATION_MISSING != NOT_RELEVANT.
#     UNKNOWN != NO.
CAUSAS = {
    'AUTORIZACAO_AUSENTE': 'a corrida nao trouxe autorizacao nenhuma.',
    'AUTORIZACAO_FABRICADA': 'o objecto nao saiu de autorizar(): nao vale.',
    'MOTIVO_DESCONHECIDO': 'o motivo do gasto nao esta no vocabulario fechado.',
    'FONTE_AUSENTE': 'coleta normal sem SOURCE_ID: nao ha par a autorizar.',
    'PROPOSITO_AUSENTE': 'sem proposito, a autorizacao serviria a qualquer universo.',
    'RELEVANCIA_NAO_AUTORIZA': ('o dono da relevancia nao autorizou este par '
                                '(fonte, proposito). NAO e o mesmo que dizer '
                                'que a fonte nao serve.'),
    'SEM_AUTORIZACAO_HUMANA': ('probe e trial gastam por excecao, e excecao '
                               'precisa de alguem que responda por ela.'),
    'SEM_TETO_DE_EXECUCOES': 'gasto por excecao sem teto de execucoes e coleta.',
    'SEM_TETO_DE_DOLARES': 'gasto por excecao sem teto de dolares e um cheque em branco.',
    'SEM_CONDICAO_DE_PARAGEM': 'o que nao sabe parar nao sabe quanto vai custar.',
    'SEM_TETO_NO_FORNECEDOR': ('sem `teto_usd` a trava fica so do nosso lado, e '
                               'a nossa trava nao sobrevive a um bug nosso.'),
    'AUTORIZACAO_NAO_COBRE_ESTA_FONTE': 'autorizada para outra fonte.',
    'AUTORIZACAO_NAO_COBRE_ESTE_PROPOSITO': 'autorizada para outro proposito.',
    'AUTORIZACAO_NAO_COBRE_ESTE_MOTIVO': 'autorizada para outro motivo de gasto.',
    'AUTORIZACAO_ESGOTADA': ('as execucoes autorizadas ja foram usadas. Rotacao '
                             'de chave nao e nova autorizacao.'),
}


class AutorizacaoInvalida(ValueError):
    """Um pedido de autorizacao que nao se pode conceder. Para-se, e diz-se porque."""


class GastoRecusado(PermissionError):
    """A porta paga recusou. NAO e falha de rede, e NAO e juizo sobre a fonte."""

    def __init__(self, causa, detalhe=''):
        self.causa = causa
        self.detalhe = detalhe
        super().__init__('%s · %s%s' % (SEM_AUTORIZACAO_NAO_GASTEI, causa,
                                        (' — ' + detalhe) if detalhe else ''))


# ⚠️ O SELO. Privado ao modulo, e e a unica coisa que separa uma autorizacao
# de um dicionario que alguem escreveu. Sem ele, `Autorizacao(...)` levanta.
_SELO = object()


def agora() -> str:
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


@dataclass
class Autorizacao:
    """O direito de acender N execucoes pagas, para um fim declarado.

    Nao se constroi a mao: `autorizar()` e a unica porta.
    """

    motivo: str
    proposito: str
    source_id: str | None
    max_execucoes: int
    max_usd: float
    quem_autorizou: str
    porque: str
    condicao_de_paragem: str
    evidencia: dict = field(default_factory=dict)
    versao: str = VERSAO_DA_GUARDA
    concedida_em: str = ''
    _selo: object = None
    _gastas: int = 0

    def __post_init__(self):
        if self._selo is not _SELO:
            raise AutorizacaoInvalida(
                'AUTORIZACAO_FABRICADA: %s Use leis/autorizacao_de_gasto.autorizar().'
                % CAUSAS['AUTORIZACAO_FABRICADA'])
        self.concedida_em = self.concedida_em or agora()

    @property
    def restantes(self) -> int:
        return max(0, self.max_execucoes - self._gastas)

    def para_o_manifesto(self) -> dict:
        """O que fica escrito na corrida. Sem segredo, sem objecto."""
        return {
            'MOTIVO_DO_GASTO': self.motivo,
            'PROPOSITO': self.proposito,
            'SOURCE_ID': self.source_id,
            'MAX_EXECUCOES': self.max_execucoes,
            'EXECUCOES_GASTAS': self._gastas,
            'MAX_USD': self.max_usd,
            'QUEM_AUTORIZOU': self.quem_autorizou,
            'PORQUE': self.porque,
            'CONDICAO_DE_PARAGEM': self.condicao_de_paragem,
            'EVIDENCIA': self.evidencia,
            'VERSAO_DA_GUARDA': self.versao,
            'CONCEDIDA_EM': self.concedida_em,
            'CONTRATO': CONTRATO,
        }


def autorizar(*, motivo, proposito, source_id=None, max_execucoes=None,
              max_usd=None, quem_autorizou=None, porque=None,
              condicao_de_paragem=None, livro=None, raiz=RAIZ) -> Autorizacao:
    """A unica porta que concede o direito de gastar. → Autorizacao, ou levanta.

    ⚠️ NAO DECIDE RELEVANCIA. Para `COLETA_NORMAL_DA_FONTE` pergunta ao dono
    (`leis/relevancia_da_fonte.portao`) e obedece. Se ele nao autorizar, a
    recusa carrega o ESTADO que ele devolveu — `NAO`, `NAO_SEI`, `ERRO` ou
    `NAO_AVALIADA` — porque colapsar os quatro num «nao» seria transformar uma
    confissao num juizo.
    """
    if motivo not in MOTIVOS:
        raise AutorizacaoInvalida(
            'MOTIVO_DESCONHECIDO: %r. Ha: %s' % (motivo, ', '.join(MOTIVOS)))
    alvo = str(proposito or '').strip()
    if not alvo:
        raise AutorizacaoInvalida('PROPOSITO_AUSENTE: %s' % CAUSAS['PROPOSITO_AUSENTE'])

    # ── COLETA NORMAL: a relevancia do par tem de estar provada ─────────────
    if motivo == COLETA_NORMAL:
        if not str(source_id or '').strip():
            raise AutorizacaoInvalida('FONTE_AUSENTE: %s' % CAUSAS['FONTE_AUSENTE'])
        sid = rel.conferir_source_id(source_id)       # URL nunca e SOURCE_ID
        if livro is None:
            livro = rel.ler_livro(raiz)
        # ⚠️ `custo` fixo como rota paga, de proposito: quem chega aqui vem da
        # porta que gasta. Perguntar ao portao com `custo=gratuito` faria uma
        # rota paga ser avaliada como se fosse de graca.
        v = rel.portao(sid, alvo, livro, custo='rota paga (autorizacao_de_gasto)')
        if v['VEREDITO'] != rel.AUTORIZA:
            raise AutorizacaoInvalida(
                'RELEVANCIA_NAO_AUTORIZA: %s Estado do par (%s, %s): %s. %s'
                % (CAUSAS['RELEVANCIA_NAO_AUTORIZA'], sid, alvo,
                   v['ESTADO_DA_RELEVANCIA'], v['PORQUE']))
        evidencia = {'PORTAO_DE_RELEVANCIA': v['VEREDITO'],
                     'ESTADO_DA_RELEVANCIA': v['ESTADO_DA_RELEVANCIA'],
                     'DECISAO': v['DECISAO'],
                     'VERSAO_DO_PORTAO': v['VERSAO_DO_PORTAO']}
        n = int(max_execucoes) if max_execucoes else 1
        usd = float(max_usd) if max_usd is not None else None
        quem = quem_autorizou or 'PORTAO_DE_RELEVANCIA_DA_FONTE'
        motivo_escrito = porque or (
            'a fonte %s provou que serve para %s, e a decisao esta no livro '
            'com evidencia apontavel' % (sid, alvo))
        parar = condicao_de_paragem or 'as %d execucao(oes) autorizadas' % n
        return Autorizacao(motivo=motivo, proposito=alvo, source_id=sid,
                           max_execucoes=n, max_usd=usd, quem_autorizou=quem,
                           porque=motivo_escrito, condicao_de_paragem=parar,
                           evidencia=evidencia, _selo=_SELO)

    # ── PROBE E TRIAL: nao passam pela relevancia, e pagam por isso ─────────
    #     QUEM NAO PRECISA DE PROVAR QUE A FONTE SERVE
    #     PRECISA DE PROVAR QUEM RESPONDE PELA CONTA.
    if not str(quem_autorizou or '').strip():
        raise AutorizacaoInvalida(
            'SEM_AUTORIZACAO_HUMANA: %s' % CAUSAS['SEM_AUTORIZACAO_HUMANA'])
    if not str(porque or '').strip():
        raise AutorizacaoInvalida(
            'SEM_AUTORIZACAO_HUMANA: um gasto por excecao sem motivo escrito e '
            'indistinguivel de um gasto por engano.')
    if not max_execucoes or int(max_execucoes) < 1:
        raise AutorizacaoInvalida(
            'SEM_TETO_DE_EXECUCOES: %s' % CAUSAS['SEM_TETO_DE_EXECUCOES'])
    if max_usd is None or float(max_usd) <= 0:
        raise AutorizacaoInvalida(
            'SEM_TETO_DE_DOLARES: %s' % CAUSAS['SEM_TETO_DE_DOLARES'])
    if not str(condicao_de_paragem or '').strip():
        raise AutorizacaoInvalida(
            'SEM_CONDICAO_DE_PARAGEM: %s' % CAUSAS['SEM_CONDICAO_DE_PARAGEM'])

    sid = rel.conferir_source_id(source_id) if source_id else None
    if motivo == PROVA_DE_RELEVANCIA and sid is None:
        raise AutorizacaoInvalida(
            'FONTE_AUSENTE: um probe de relevancia sem fonte nomeada nao esta a '
            'avaliar nada — e coleta com outro nome.')

    return Autorizacao(motivo=motivo, proposito=alvo, source_id=sid,
                       max_execucoes=int(max_execucoes), max_usd=float(max_usd),
                       quem_autorizou=quem_autorizou, porque=porque,
                       condicao_de_paragem=condicao_de_paragem,
                       evidencia={'EXCECAO': motivo,
                                  'RELEVANCIA_NAO_FOI_CONSULTADA':
                                      'de proposito: ver o cabecalho do ficheiro'},
                       _selo=_SELO)


def conferir_e_consumir(autorizacao, *, motivo, proposito, source_id=None,
                        teto_usd=None) -> dict:
    """A PORTA. Chamada pelo dono da execucao paga, ANTES do POST.

    → o recibo da autorizacao, ou levanta `GastoRecusado`. Consome uma
    execucao: a mesma autorizacao nao paga duas vezes.

    ⚠️ ELA NAO LE O LIVRO DE RELEVANCIA. A pergunta ja foi feita em
    `autorizar()`; aqui so se confere que a autorizacao trazida cobre ESTA
    compra. Reler aqui daria ao dono da execucao paga uma opiniao sobre a
    fonte, que e exactamente o que nao pode ter.
    """
    if autorizacao is None:
        raise GastoRecusado('AUTORIZACAO_AUSENTE', CAUSAS['AUTORIZACAO_AUSENTE'])
    if not isinstance(autorizacao, Autorizacao) or autorizacao._selo is not _SELO:
        raise GastoRecusado('AUTORIZACAO_FABRICADA', CAUSAS['AUTORIZACAO_FABRICADA'])
    if autorizacao.motivo != motivo:
        raise GastoRecusado(
            'AUTORIZACAO_NAO_COBRE_ESTE_MOTIVO',
            'autorizada para %s, a corrida declara %s' % (autorizacao.motivo, motivo))
    if str(autorizacao.proposito) != str(proposito or '').strip():
        raise GastoRecusado(
            'AUTORIZACAO_NAO_COBRE_ESTE_PROPOSITO',
            'autorizada para %s, pedida para %s' % (autorizacao.proposito, proposito))
    if autorizacao.source_id is not None:
        if str(source_id or '').strip() != autorizacao.source_id:
            raise GastoRecusado(
                'AUTORIZACAO_NAO_COBRE_ESTA_FONTE',
                'autorizada para %s, pedida para %s'
                % (autorizacao.source_id, source_id))
    # ── A TRAVA DO LADO DO FORNECEDOR ───────────────────────────────────────
    # `teto_usd` vira `maxTotalChargeUsd` na plataforma, e e a unica protecao
    # que sobrevive a um defeito deste codigo (COL-LAW-019).
    if autorizacao.max_usd is not None:
        if teto_usd is None:
            raise GastoRecusado('SEM_TETO_NO_FORNECEDOR', CAUSAS['SEM_TETO_NO_FORNECEDOR'])
        if float(teto_usd) > float(autorizacao.max_usd) + 1e-9:
            raise GastoRecusado(
                'SEM_TETO_NO_FORNECEDOR',
                'teto pedido %.4f acima do autorizado %.4f'
                % (float(teto_usd), float(autorizacao.max_usd)))
    if autorizacao.restantes <= 0:
        raise GastoRecusado('AUTORIZACAO_ESGOTADA', CAUSAS['AUTORIZACAO_ESGOTADA'])

    autorizacao._gastas += 1
    recibo = autorizacao.para_o_manifesto()
    recibo['VEREDITO'] = AUTORIZADO
    recibo['TETO_USD_PEDIDO'] = teto_usd
    return recibo


LEIS = (
    'CREDENTIAL != AUTHORIZATION',
    'TOKEN_PRESENT != SPEND_ALLOWED',
    'ALLOWED_ROUTE != AUTHORIZED_SPEND',
    'PAID_PROVIDER != POLICY_OVERRIDE',
    'SOURCE RELEVANCE OWNER != SPEND ENFORCER',
    'COLETA NORMAL != PROVA DE RELEVANCIA != TRIAL DE CAPACIDADE',
    'AUTHORIZATION_MISSING != NOT_RELEVANT',
    'ROTACAO DE CHAVE NAO E NOVA AUTORIZACAO',
    'UMA AUTORIZACAO QUE O CHAMADOR ESCREVE NAO E UMA AUTORIZACAO',
    'GASTO POR EXCECAO SEM TETO E COLETA COM OUTRO NOME',
)


def main() -> int:
    print('CONTRATO %s · guarda v%s' % (CONTRATO, VERSAO_DA_GUARDA))
    print()
    print('OS TRES MOTIVOS DE GASTO:')
    for m in MOTIVOS:
        excecao = ' (excecao: nao passa pela relevancia)' if m in MOTIVOS_DE_EXCECAO else ''
        print('    %-32s%s' % (m, excecao))
    print()
    print('VEREDITOS: %s' % ' · '.join(VEREDITOS))
    print()
    print('AS CAUSAS DA RECUSA, e nenhuma diz «a fonte nao serve»:')
    for c in CAUSAS:
        print('    %s' % c)
    print()
    for l in LEIS:
        print('  · %s' % l)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
