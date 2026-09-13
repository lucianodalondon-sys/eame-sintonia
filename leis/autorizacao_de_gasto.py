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

⚠️ ESTE FICHEIRO EXISTIU DUAS VEZES, E ISSO E O DEFEITO QUE A SCRAP-OWNER-01
CONSERTOU
-------------------------------------------------------------------------
Duas linhagens desta casa escreveram, cada uma por si, um
`leis/autorizacao_de_gasto.py` para responder a MESMA pergunta. Os dois
declaravam `AUTORIZACAO_DE_GASTO/v1`. Media-se, e davam respostas OPOSTAS ao
mesmo input:

    um dicionario escrito a mao pelo chamador
        linha SCRAP-FLOW      ACEITE
        linha SR-02           RECUSADO

    uma autorizacao de UMA execucao, usada duas vezes
        linha SCRAP-FLOW      as duas passam (nao havia consumo)
        linha SR-02           a segunda e recusada

    DUAS IMPLEMENTACOES DO MESMO CONTRATO
    NAO SAO DUAS VERSOES DA VERDADE: SAO DUAS VERDADES.

E dois ficheiros com o mesmo nome de contrato sao piores do que dois nomes
diferentes — quem le o campo `CONTRATO` num manifesto nao consegue saber qual
dos dois comportamentos o produziu.

O QUE VENCEU, E PORQUE
----------------------
Venceu o modelo desta linhagem (SR-02), e nao por antiguidade: ele preserva
propriedades que o outro nao tinha, e o outro nao preservava nenhuma que este
nao tenha.

    autorizacao SELADA        o chamador nao a consegue escrever
    autorizacao CONSUMIVEL    uma execucao autorizada nao paga duas
    teto do FORNECEDOR        `maxTotalChargeUsd` conferido contra o autorizado
    pergunta ao DONO          `relevancia_da_fonte.portao` e chamado, nao imitado

O outro modelo validava um dicionario que o chamador construia — e validar um
campo que quem pede escreve e verificar a assinatura de quem assinou o cheque.

    CAMPO PREENCHIDO PELO CHAMADOR != AUTORIZACAO.

O CONTRATO SUBIU PARA v2, E A RAZAO E MEDIDA
---------------------------------------------
Nao se aumenta versao por cerimonia. Aumentou-se porque `v1` ja nomeava dois
comportamentos incompativeis, e deixar o nome como estava criaria um TERCEIRO
`v1`. `v2` e o primeiro nome desta casa que designa UM comportamento so.

DOIS EIXOS, E ELES NAO SAO O MESMO — A DECISAO ESTA AQUI
---------------------------------------------------------
Este ficheiro e dono de dois vocabularios, e isso e deliberado:

    MODO    (NORMAL · TRIAL · PROBE)
            o eixo da EXECUCAO. Ele muda o portao epistemologico do `CHECK`
            em `coleta/scrap_executor.py` — «promete resultado?» contra «da
            para medir?» — e aplica-se tambem a rotas GRATUITAS, onde nao ha
            gasto nenhum para autorizar.

    MOTIVO  (COLETA_NORMAL_DA_FONTE · PROVA_DE_RELEVANCIA_DA_FONTE ·
             TRIAL_DE_CAPACIDADE)
            o eixo do GASTO. So existe quando ha dinheiro, e e o que a
            autorizacao liga.

Os tres nomes de cada lado correspondem um a um, e por isso a tentacao era
fundi-los. Nao se fundiram porque uma coleta NORMAL de uma rota GRATUITA tem
modo e NAO tem motivo de gasto — fundir daria motivo de gasto a quem nao gasta.

    UMA ROTA QUE NAO GASTA NAO PRECISA DE AUTORIZACAO PARA GASTAR.

O que NAO existe e duas traducoes: `MOTIVO_DO_MODO`, aqui em baixo, e o unico
sitio onde um vira o outro. Os nomes curtos NAO sao um segundo vocabulario
publico da autorizacao — sao o vocabulario do outro eixo, e o mapa entre os
dois vive num sitio so.
"""

from __future__ import annotations

import os
import sys
import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone

_HERE = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(_HERE)
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401

import relevancia_da_fonte as rel  # noqa: E402 — PERGUNTA-SE; nao se decide aqui

CONTRATO = 'AUTORIZACAO_DE_GASTO/v2'
VERSAO_DA_GUARDA = '2'

#: O nome que esta casa ja usou para DOIS comportamentos diferentes.
#: Fica escrito para que um manifesto antigo se consiga ler.
CONTRATO_AMBIGUO_ANTERIOR = 'AUTORIZACAO_DE_GASTO/v1'

# ── OS TRES MOTIVOS ─────────────────────────────────────────────────────────
COLETA_NORMAL = 'COLETA_NORMAL_DA_FONTE'
PROVA_DE_RELEVANCIA = 'PROVA_DE_RELEVANCIA_DA_FONTE'
TRIAL_DE_CAPACIDADE = 'TRIAL_DE_CAPACIDADE'
MOTIVOS = (COLETA_NORMAL, PROVA_DE_RELEVANCIA, TRIAL_DE_CAPACIDADE)

# Os dois que NAO sao coleta da fonte, e por isso nao passam pelo portao de
# relevancia. Em troca, os dois exigem autorizacao humana e tetos.
MOTIVOS_DE_EXCECAO = (PROVA_DE_RELEVANCIA, TRIAL_DE_CAPACIDADE)

# ══════════════════════════════════════════════════════════════════════════
# O EIXO DA EXECUCAO — outro eixo, e o dono e este ficheiro
# ══════════════════════════════════════════════════════════════════════════
# `coleta/scrap_executor.py` importa daqui e nao ao contrario: ele importa
# `coletor`, e `coletor` importa esta lei. Declarar os modos la faria um ciclo.
#
# O modo aplica-se a TUDO o que corre — pago ou gratuito. O motivo so existe
# quando ha gasto. Ver o cabecalho: sao dois eixos, e nao se fundem.
NORMAL = 'NORMAL'
TRIAL = 'TRIAL'
PROBE = 'PROBE'
MODOS = (NORMAL, TRIAL, PROBE)

#: Os modos que NAO prometem resultado. Nenhum deles promove estado ao passar.
MODOS_DE_MEDIDA = (TRIAL, PROBE)

#: O UNICO sitio onde um eixo vira o outro. Duas traducoes seriam duas
#: semanticas, e a segunda aprenderia a responder o que a primeira recusa.
MOTIVO_DO_MODO = {
    NORMAL: COLETA_NORMAL,
    PROBE: PROVA_DE_RELEVANCIA,
    TRIAL: TRIAL_DE_CAPACIDADE,
}
MODO_DO_MOTIVO = {v: k for k, v in MOTIVO_DO_MODO.items()}


def motivo_do_modo(modo):
    """→ o motivo de gasto que este modo de execucao implica, ou levanta.

    Traduzir NAO e autorizar: quem chama isto ainda nao tem autorizacao
    nenhuma — so sabe que nome dar ao que vai pedir.
    """
    if modo in MOTIVOS:
        return modo               # ja veio no vocabulario do gasto
    if modo not in MOTIVO_DO_MODO:
        raise AutorizacaoInvalida(
            'MOTIVO_DESCONHECIDO: modo %r nao existe. Os tres sao %s'
            % (modo, ', '.join(MODOS)))
    return MOTIVO_DO_MODO[modo]

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

# ── E A TRAVA QUE FAZ DE CONFERIR-E-CONSUMIR UM SO ACTO ────────────────────
# ⚠️ MEDIDO NA NIGHT-SHIFT-01 §15, e reproduzido antes de corrigido:
#
#     autorizacao para 1 execucao   -> 2 corridas pagaram
#     autorizacao para 3 execucoes  -> 5 corridas pagaram
#
# E nao so na primitiva: pela PORTA PAGA de verdade, com 16 fios e teto 3,
# NASCERAM 4 POSTs. Uma compra alem do que a pessoa autorizou.
#
# A causa e a distancia entre duas linhas que pareciam uma:
#
#     if autorizacao.restantes <= 0: recusa
#     reg['GASTAS'] += 1
#
# Entre a pergunta e a resposta cabe outro fio. `+= 1` tambem nao e atomico —
# le, soma e escreve sao tres passos, e o interpretador troca de fio entre
# bytecodes. Nenhuma das duas coisas e rara o suficiente para nao acontecer
# numa maquina com carga.
#
#     UMA GUARDA QUE CONFERE E DEPOIS CONSOME
#     DEIXA PASSAR QUEM CHEGAR NO MEIO.
#     CONFERIR E CONSUMIR TEM DE SER UM SO ACTO.
#
# A trava e UMA, do modulo, e nao uma por autorizacao: a seccao critica nao
# faz E/S nenhuma — sao comparacoes e duas escritas num dicionario — e uma
# trava so torna a prova de correccao trivial. Serializar isto nao custa nada
# comparado com o POST que vem a seguir.
#
# E ELA NAO PRECISA DE ATRAVESSAR PROCESSOS. `_SELO` e um `object()` deste
# processo: uma autorizacao reconstruida noutro lado nao tem o selo e e
# recusada como `AUTORIZACAO_FABRICADA` — medido, nao presumido, em
# `provas/queda_e_repeticao_da_v1.py`. Um processo, um registo, uma trava.
#
#     COPIAR UMA AUTORIZACAO NAO E RECEBER UMA AUTORIZACAO.
_TRAVA = threading.Lock()

# ── O QUE JA FOI GASTO NAO VIVE DENTRO DA AUTORIZACAO ──────────────────────
# ⚠️ MEDIDO NESTA ARVORE, e reproduzido antes de corrigido (SCRAP-CV-02, cujas
# propriedades esta linha porta uma a uma):
#
#     a = autorizar(max_execucoes=1)      # UMA compra autorizada
#     b = copy.copy(a)
#     a -> POST 1 · b -> POST 1           # DUAS compras, uma autorizacao
#
# O contador vivia num campo do objecto, e uma copia leva o campo com ela. A
# `deepcopy` ja morria no selo, porque reconstroi; a `copy` rasa nao reconstroi
# nada — copia o `__dict__` inteiro, selo incluido.
#
#     COPIAR UMA AUTORIZACAO NAO E RECEBER UMA AUTORIZACAO.
#
# Entao o consumo passa a viver AQUI, indexado pela identidade cunhada no
# momento da concessao. Uma copia leva o mesmo nome, e o mesmo nome encontra o
# mesmo contador: ela nao ganha execucao nenhuma por ser copia.
#
#     UMA AUTORIZACAO VALE POR IDENTIDADE, E NAO PELA FORMA.
_CONSUMO = {}


def _registo(ident):
    return _CONSUMO.setdefault(ident, {'GASTAS': 0, 'LEDGER': None})


class AutorizacaoSelada(AttributeError):
    """Escrever numa autorizacao ja concedida. Nao se faz, e diz-se porque."""


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
    #: A identidade desta concessao. Cunhada uma vez, e e por ela que o
    #: registo de consumo a encontra — inclusive quando alguem a copia.
    _id: str = ''
    _fechada: bool = False

    def __post_init__(self):
        if self._selo is not _SELO:
            raise AutorizacaoInvalida(
                'AUTORIZACAO_FABRICADA: %s Use leis/autorizacao_de_gasto.autorizar().'
                % CAUSAS['AUTORIZACAO_FABRICADA'])
        self.concedida_em = self.concedida_em or agora()
        self._id = self._id or uuid.uuid4().hex
        _registo(self._id)
        # ── E A PARTIR DAQUI ELA NAO MUDA MAIS ──────────────────────────────
        # ⚠️ MEDIDO: `a.max_usd = 99.0` era aceite depois de concedida, e a
        # trava do fornecedor compara `teto_usd` contra `max_usd`. Subir o
        # campo subia o tecto — uma autorizacao de dez centimos passava a
        # autorizar noventa e nove dolares sem ninguem autorizar nada.
        #
        #     UMA AUTORIZACAO QUE MUDA DEPOIS DE CONCEDIDA NAO FOI CONFERIDA.
        self._fechada = True

    def __setattr__(self, nome, valor):
        if getattr(self, '_fechada', False):
            raise AutorizacaoSelada(
                'esta autorizacao ja foi concedida e nao se reescreve '
                '(tentou-se mudar «%s»). Para outros limites, pede-se outra.'
                % nome)
        object.__setattr__(self, nome, valor)

    @property
    def gastas(self) -> int:
        """Quantas execucoes ja se gastaram — lido do registo, nunca do objecto."""
        return _registo(self._id)['GASTAS']

    @property
    def ledger(self):
        """O orcamento contra o qual este limite humano foi conferido."""
        return _registo(self._id)['LEDGER']

    @property
    def restantes(self) -> int:
        return max(0, self.max_execucoes - self.gastas)

    def para_o_manifesto(self) -> dict:
        """O que fica escrito na corrida. Sem segredo, sem objecto."""
        return {
            'MOTIVO_DO_GASTO': self.motivo,
            'PROPOSITO': self.proposito,
            'SOURCE_ID': self.source_id,
            'MAX_EXECUCOES': self.max_execucoes,
            'EXECUCOES_GASTAS': self.gastas,
            'AUTORIZACAO_ID': self._id,
            'LEDGER': self.ledger,
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
                        teto_usd=None, orcamento_autorizado=None,
                        ledger=None) -> dict:
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
    # ── O LIMITE HUMANO CONTRA O LEDGER DA EXECUCAO ─────────────────────────
    # ⚠️ MEDIDO NESTA ARVORE, e reproduzido antes de corrigido:
    #
    #     autorizacao MAX_USD = 0.10 · orcamento declarado = 99.00 -> COMPROU
    #
    # A trava do fornecedor comparava `teto_usd` com `max_usd` e mais nada. O
    # ORCAMENTO da execucao — o que ela pode comprometer no total — nunca era
    # confrontado com o limite que a pessoa concedeu.
    #
    #     LIMITE HUMANO != LEDGER OPERACIONAL.
    #     FINANCIAL_BUDGET.AUTHORIZED <= AUTORIZACAO.MAX_USD.
    if orcamento_autorizado is not None and autorizacao.max_usd is not None:
        try:
            declarado = float(orcamento_autorizado)
            humano = float(autorizacao.max_usd)
        except (TypeError, ValueError):
            raise GastoRecusado(
                'ORCAMENTO_NAO_NUMERICO',
                'orcamento %r ou limite %r nao e numero'
                % (orcamento_autorizado, autorizacao.max_usd))
        if declarado > humano + 1e-9:
            raise GastoRecusado(
                'ORCAMENTO_ACIMA_DA_AUTORIZACAO',
                'a execucao declarou poder comprometer %.4f e a pessoa '
                'autorizou %.4f' % (declarado, humano))

    # ── E TEM DE SER SEMPRE O MESMO LEDGER ──────────────────────────────────
    # ⚠️ MEDIDO: a MESMA autorizacao gastou sob DOIS orcamentos separados. Cada
    # um cabia no limite humano; a soma nao. Conferir um limite contra um
    # ledger que muda a meio e o mesmo que nao o conferir.
    #
    #     UM LIMITE CONFERIDO CONTRA UM LEDGER QUE MUDA NAO FOI CONFERIDO.
    #
    # A saida NAO e dar um saldo a esta lei — seriam duas pecas a somar o mesmo
    # dolar. Ela guarda um NOME: a identidade do orcamento contra o qual o
    # limite foi conferido da primeira vez.
    #
    #     UM NOME NAO E UMA SOMA.
    # ⚠️ A PARTIR DAQUI, UM SO ACTO. Ver `_TRAVA`: ler o que resta, prender o
    # ledger e consumir sao tres passos sobre o MESMO registo, e separa-los
    # deixa passar quem chegar no meio. A trava entra aqui e nao antes: tudo o
    # que esta acima le apenas a autorizacao, que e imutavel depois de selada.
    reg = _registo(autorizacao._id)
    with _TRAVA:
        if ledger is not None:
            if reg['LEDGER'] is None:
                reg['LEDGER'] = ledger
            elif reg['LEDGER'] != ledger:
                raise GastoRecusado(
                    'AUTORIZACAO_DE_OUTRO_LEDGER',
                    'esta autorizacao ja foi conferida contra outro orcamento. Ela '
                    'vale dentro de UMA execucao; para outra, pede-se outra vez.')

        if autorizacao.restantes <= 0:
            raise GastoRecusado('AUTORIZACAO_ESGOTADA', CAUSAS['AUTORIZACAO_ESGOTADA'])

        reg['GASTAS'] += 1
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
