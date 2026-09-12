#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A AUTORIZAÇÃO DE GASTO — «alguém permitiu ESTA compra, e permitiu para ISTO?»

    py leis/autorizacao_de_gasto.py          # o contrato, dito em voz alta

É a única pergunta deste ficheiro. Ele NÃO pergunta se a fonte serve, se a rota
existe, quanto sobra no orçamento, nem quantas idas à rede restam. Essas quatro
têm donos, e estão nomeadas no fim deste cabeçalho.

POR QUE ISTO EXISTE
-------------------
Medido nesta árvore, antes desta lei:

    PAID_CREATION_PRIMITIVES = 1      coleta/coletor.py::executar, o POST
    CALLERS_DESSE_PRIMITIVE  = 4      e três deles saltam o roteador
    CAN_SPEND_WITHOUT_AUTH   = 4

`coletor.executar()` é de facto a porta única por onde uma corrida paga nasce —
mas quatro sítios chamam-na, e três não passam por `scrap_executor.COLLECT`.
Havia teto de dinheiro, teto de rede, política de rota e cap do lado do
provider. Não havia a pergunta anterior a todas elas:

    ALGUÉM AUTORIZOU ESTA COMPRA?

Os quatro gates existentes respondem «cabe?», «é permitido pela rota?», «quanto
no máximo?». Nenhum responde «quem disse que sim?». E um sistema que sabe
exactamente quanto pode gastar sem saber se devia gastar é um sistema que gasta
com precisão contabilística em coisas que ninguém pediu.

    CREDENTIAL_PRESENT != SPEND_AUTHORIZED
    ROUTE_ALLOWED      != SPEND_AUTHORIZED
    BUDGET_PRESENT     != SPEND_AUTHORIZED
    PAID_PROVIDER      != POLICY_OVERRIDE

ESTE FICHEIRO NÃO ABRE O LIVRO
-------------------------------
O dono de `SOURCE_RELEVANCE` é `leis/relevancia_da_fonte.py`, e ele vive na
linhagem SR-01, fora desta. Esta lei **recebe** o veredito dele e valida-o.
Nunca o calcula.

    SOURCE_RELEVANCE_OWNER != SPEND_ENFORCER.

Concretamente, e por escrito: este ficheiro não lê `LIVRO-DE-RELEVANCIA`, não
classifica fonte, não interpreta palavra-chave, não decide SIM/NÃO, não fabrica
`SOURCE_ID` e não pergunta nada ao Atlas. Se um dia o fizesse, a casa passava a
ter duas verdades sobre relevância e a segunda envelhecia calada.

    O GUARDA CONFERE O BILHETE. ELE NÃO É O DONO DO ESPECTÁCULO.

E O GUARDA NÃO REFAZ A TABELA DO PORTÃO
----------------------------------------
A tentação era ler `RESULTADO` e reaplicar `REGRA_DO_PORTAO`. Isso seria a
mesma lei escrita duas vezes, e a cópia daria respostas antigas no dia em que o
original mudasse. O que se faz é o oposto, e é fail-closed:

    EXIGE-SE A ÚNICA COMBINAÇÃO QUE NÃO TEM LEITURA DUPLA:
    VEREDITO = AUTORIZA  **E**  ESTADO_DA_RELEVANCIA = SIM.

Qualquer outra combinação recusa — inclusive uma que uma versão futura do
portão viesse a autorizar. Errar para o lado do «não compra» custa uma linha a
alguém; errar para o outro lado custa dinheiro que ninguém pediu.

AS QUATRO AUSÊNCIAS NÃO SÃO UM «NÃO»
-------------------------------------
Vêm de `leis/relevancia_da_fonte.py`, e esta lei não as achata:

    NAO_AVALIADA   ninguém olhou
    NAO_SEI        olhou-se e não se concluiu
    ERRO           tentou-se olhar e a avaliação rebentou
    NAO            olhou-se, concluiu-se, e a resposta é não

As quatro dão zero POST. Mas a RECUSA tem nomes diferentes, e tem de ter: dizer
`NOT_RELEVANT` a uma fonte que ninguém abriu é inventar um julgamento.

    FALTA DE AUTORIZAÇÃO É FALTA DE AUTORIZAÇÃO.

TRÊS MODOS, E DOIS DELES PODEM GASTAR ANTES DE HAVER «SIM»
------------------------------------------------------------
    NORMAL   colher a sério                 exige SOURCE_RELEVANCE = SIM
    PROBE    «esta candidata merece?»       exige autorização humana + limites
    TRIAL    «esta ROTA consegue?»          exige autorização humana + limites

O PROBE existe para não fechar o ciclo impossível:

    PARA PROVAR QUE A FONTE SERVE É PRECISO OBSERVÁ-LA,
    E PARA A OBSERVAR SERIA PRECISO ELA JÁ SERVIR.

Por isso ele arranca legitimamente de `NAO_AVALIADA`. O preço é que ele é
limitado em tudo — corridas, POSTs, dólares, itens, rede — e não promove nada:

    PROBE != DECISION.  Quem escreve no livro é o dono do livro.

E o TRIAL é outra pergunta ainda: não mede a fonte, mede a ROTA. Nenhum dos
dois é coleta, e uma `NORMAL_COLLECTION` não pode vestir-se de nenhum deles
para saltar a relevância.

O QUE ESTA LEI NÃO É — E QUEM É O DONO DE CADA UMA
---------------------------------------------------
    SPEND_AUTHORIZATION != SOURCE_RELEVANCE  -> leis/relevancia_da_fonte.py (SR-01)
    SPEND_AUTHORIZATION != ITEM_RELEVANCE    -> admissao/admissao.py
    SPEND_AUTHORIZATION != FINANCIAL_BUDGET  -> coleta/coletor.py::OrcamentoFinanceiro
    SPEND_AUTHORIZATION != NETWORK_BUDGET    -> coleta/scrap_http.py
    SPEND_AUTHORIZATION != ROUTE_POLICY      -> leis/social_matriz.py · coleta/social_rotas.py
    SPEND_AUTHORIZATION != PROVIDER_CAP      -> maxTotalChargeUsd, do lado do provider
    SPEND_AUTHORIZATION != CREDENTIAL        -> ferramentas/apify_pool.py

        TOKEN_OWNER != SPEND_OWNER.

A ordem importa e é esta: a autorização vem ANTES de todos. Ela não substitui
nenhum — passar aqui é ganhar o direito de ser perguntado a seguir.

    CAN DO != DID DO.  ONE CONCEPT -> ONE OWNER.
"""

from __future__ import annotations

import os
import sys

_AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(_AQUI)
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401 — põe as gavetas no caminho de importação

CONTRATO = 'AUTORIZACAO_DE_GASTO/v1'

# ══════════════════════════════════════════════════════════════════════════
# O EIXO DO MODO — TRÊS PALAVRAS, E O DONO DELAS É ESTE FICHEIRO
# ══════════════════════════════════════════════════════════════════════════
# Viviam em `coleta/scrap_executor.py`, que tinha duas. A terceira obrigou a
# escolher um dono, e o modo é uma pergunta de AUTORIZAÇÃO: ele existe para
# dizer que prova é preciso trazer antes de comprar. `scrap_executor` importa
# daqui, e não o contrário — ele importa `coletor`, e `coletor` importa esta
# lei; declarar os modos lá criaria um ciclo.
NORMAL = 'NORMAL'
TRIAL = 'TRIAL'
PROBE = 'PROBE'
MODOS = (NORMAL, TRIAL, PROBE)

#: Os modos que NÃO são coleta. Nenhum deles promete resultado, e nenhum deles
#: promove estado nenhum ao passar.
MODOS_DE_MEDIDA = (TRIAL, PROBE)

# ══════════════════════════════════════════════════════════════════════════
# O VOCABULÁRIO VEM DO DONO DA RELEVÂNCIA — NÃO SE INVENTA AQUI
# ══════════════════════════════════════════════════════════════════════════
# São as palavras de `leis/relevancia_da_fonte.py` (SR-01). Estão escritas aqui
# porque essa lei não vive nesta linhagem — e `tests/test_scrap_sr02_*` reprova
# se alguém lhes mexer sem dizer porquê. Duas listas com as mesmas palavras são
# duas verdades; uma lista copiada com o original nomeado é uma citação.
SIM = 'SIM'
NAO = 'NAO'
NAO_SEI = 'NAO_SEI'
NAO_SE_APLICA = 'NAO_SE_APLICA'
ERRO = 'ERRO'
NAO_AVALIADA = 'NAO_AVALIADA'

#: Os vereditos do portão de relevância. Três, e nenhum é sinónimo de outro.
AUTORIZA = 'AUTORIZA'
BARRA = 'BARRA'
EXIGE_AVALIACAO = 'EXIGE_AVALIACAO'
VEREDITOS = (AUTORIZA, BARRA, EXIGE_AVALIACAO)

#: Os campos que uma autorização de relevância tem de trazer. Os nomes são os
#: do SR-01: `relevancia_da_fonte.portao()` devolve exactamente estes.
CAMPOS_DA_AUTORIZACAO = ('VEREDITO', 'SOURCE_ID', 'PROPOSITO',
                         'ESTADO_DA_RELEVANCIA', 'VERSAO_DO_PORTAO', 'CONTRATO')

#: Os campos que uma autorização humana de PROBE ou TRIAL tem de trazer.
#: Um limite em falta é um limite infinito, e um limite infinito não é limite.
CAMPOS_DO_LIMITE = ('AUTORIZACAO_HUMANA', 'MAX_PROVIDER_RUNS',
                    'MAX_START_POSTS', 'MAX_USD')
#: E o PROBE traz ainda este: ele observa uma candidata, e uma observação sem
#: fim é uma coleta com outro nome.
CAMPO_SO_DO_PROBE = 'MAX_ITEMS'


# ══════════════════════════════════════════════════════════════════════════
# A RECUSA
# ══════════════════════════════════════════════════════════════════════════
class SemAutorizacaoDeGasto(RuntimeError):
    """Ninguém autorizou esta compra. Ela NÃO nasce.

    Levanta-se ANTES do POST, como `SemOrcamentoFinanceiro` e
    `SemOrcamentoDeRede` — as três são recusas da casa, não falhas do provider,
    e sobem como estado e não como exceção larga.
    """

    def __init__(self, motivo, *, estado, modo=None, source_id=None,
                 proposito=None):
        super().__init__(motivo)
        self.estado = estado
        self.modo = modo
        self.source_id = source_id
        self.proposito = proposito


#: Os estados da recusa. Cada ausência mantém o seu nome — achatá-las todas em
#: `NOT_RELEVANT` inventaria um julgamento que ninguém fez.
SEM_AUTORIZACAO = 'SPEND_NOT_AUTHORIZED'
RELEVANCIA_BARRADA = 'SOURCE_NOT_RELEVANT_FOR_PURPOSE'
RELEVANCIA_POR_AVALIAR = 'SOURCE_RELEVANCE_NOT_EVALUATED'
RELEVANCIA_INCERTA = 'SOURCE_RELEVANCE_UNKNOWN'
RELEVANCIA_COM_ERRO = 'SOURCE_RELEVANCE_EVALUATION_ERROR'
FONTE_ERRADA = 'AUTHORIZATION_FOR_ANOTHER_SOURCE'
PROPOSITO_ERRADO = 'AUTHORIZATION_FOR_ANOTHER_PURPOSE'
SOURCE_ID_AUSENTE = 'SOURCE_ID_MISSING'
SOURCE_ID_E_URL = 'URL_IS_NOT_A_SOURCE_ID'
LIMITE_AUSENTE = 'HUMAN_AUTHORIZATION_LIMIT_MISSING'
CONTRATO_ERRADO = 'AUTHORIZATION_CONTRACT_MISMATCH'

#: O que cada estado da relevância vira, quando barra. Um mapa de NOMES, não
#: uma regra: a decisão de barrar já foi tomada acima.
_NOME_DA_AUSENCIA = {
    NAO: RELEVANCIA_BARRADA,
    NAO_SE_APLICA: RELEVANCIA_BARRADA,
    NAO_AVALIADA: RELEVANCIA_POR_AVALIAR,
    NAO_SEI: RELEVANCIA_INCERTA,
    ERRO: RELEVANCIA_COM_ERRO,
}


# ══════════════════════════════════════════════════════════════════════════
# A IDENTIDADE DA FONTE — CONFERIR NÃO É FABRICAR
# ══════════════════════════════════════════════════════════════════════════
_PREFIXOS_DE_URL = ('http://', 'https://', 'ftp://', 'www.', '//')


def conferir_source_id(source_id):
    """→ o SOURCE_ID, ou levanta. NUNCA o inventa a partir de uma URL.

    COL-LAW-206, e é a mesma conferência de `relevancia_da_fonte`. Um endereço
    é onde se bate; não é quem publica. Aceitar uma URL faria a mesma fonte
    nascer duas vezes no dia em que mudasse de domínio, e a decisão antiga
    ficava órfã sem ninguém reparar.

        URL NÃO É SOURCE_ID.
    """
    if not isinstance(source_id, str) or not source_id.strip():
        raise SemAutorizacaoDeGasto(
            'SOURCE_ID ausente: não há par (fonte, propósito) para autorizar.',
            estado=SOURCE_ID_AUSENTE)
    s = source_id.strip()
    if any(s.lower().startswith(p) for p in _PREFIXOS_DE_URL) or '/' in s:
        raise SemAutorizacaoDeGasto(
            'URL NÃO É SOURCE_ID (COL-LAW-206): «%s». O endereço muda e a '
            'fonte fica.' % s[:80], estado=SOURCE_ID_E_URL, source_id=s)
    return s


# ══════════════════════════════════════════════════════════════════════════
# OS LIMITES DE UMA AUTORIZAÇÃO HUMANA
# ══════════════════════════════════════════════════════════════════════════
def _conferir_limites(autorizacao, modo):
    """Levanta se faltar limite. → o dicionário dos limites conferidos.

        UM LIMITE EM FALTA É UM LIMITE INFINITO,
        E UM LIMITE INFINITO NÃO É UM LIMITE.
    """
    campos = list(CAMPOS_DO_LIMITE)
    if modo == PROBE:
        campos.append(CAMPO_SO_DO_PROBE)
    fora = {}
    for campo in campos:
        valor = autorizacao.get(campo)
        if valor is None or valor is False or (isinstance(valor, str)
                                               and not valor.strip()):
            raise SemAutorizacaoDeGasto(
                'autorização de %s sem «%s». %s' % (modo, campo,
                                                    'Sem ele não há teto.'),
                estado=LIMITE_AUSENTE, modo=modo)
        if campo != 'AUTORIZACAO_HUMANA':
            try:
                numero = float(valor)
            except (TypeError, ValueError):
                raise SemAutorizacaoDeGasto(
                    'o limite «%s» de %s não é um número: %r'
                    % (campo, modo, valor), estado=LIMITE_AUSENTE, modo=modo)
            if numero <= 0:
                # Zero não é «sem limite»; é «não pode». E quem não pode não
                # devia estar a pedir autorização para comprar.
                raise SemAutorizacaoDeGasto(
                    'o limite «%s» de %s é %s — isso não autoriza nada.'
                    % (campo, modo, valor), estado=LIMITE_AUSENTE, modo=modo)
            fora[campo] = numero
        else:
            fora[campo] = valor
    return fora


# ══════════════════════════════════════════════════════════════════════════
# A GUARDA
# ══════════════════════════════════════════════════════════════════════════
def pode_comprar(*, modo, autorizacao, source_id=None, proposito=None,
                 ator=None):
    """A GUARDA COMUM. → o recibo da autorização, ou levanta.

    Chamada IMEDIATAMENTE antes do POST que cria a execução paga, em
    `coleta/coletor.py::executar` — o único sítio desta árvore onde uma corrida
    paga nasce. Todos os caminhos convergem lá, e por isso a guarda está lá:

        UMA GUARDA QUE VIVE NUM CAMINHO GUARDA UM CAMINHO.
        UMA GUARDA QUE VIVE NA PRIMITIVA GUARDA TODOS.

    `autorizacao = None` recusa. É o comportamento certo e é deliberado: um
    chamador novo que não saiba desta lei não compra, em vez de comprar por
    omissão.

        FAIL CLOSED. O SILÊNCIO NÃO AUTORIZA.
    """
    if modo not in MODOS:
        raise SemAutorizacaoDeGasto(
            'modo de execução desconhecido: %r. Os três são %s'
            % (modo, ', '.join(MODOS)), estado=SEM_AUTORIZACAO, modo=modo)
    if not isinstance(autorizacao, dict) or not autorizacao:
        raise SemAutorizacaoDeGasto(
            'nenhuma autorização de gasto chegou a esta compra (modo %s, ator '
            '%s). Ter chave, teto e rota permitida não é ter autorização.'
            % (modo, ator), estado=SEM_AUTORIZACAO, modo=modo)

    if modo in MODOS_DE_MEDIDA:
        # ── PROBE e TRIAL: quem autoriza é GENTE, e traz os limites ────────
        # Nenhum dos dois pergunta pela relevância — é essa a razão de
        # existirem. O que se exige em troca é que sejam finitos.
        limites = _conferir_limites(autorizacao, modo)
        return {
            'CAN_START_PAID_EXECUTION': True,
            'MODE': modo,
            'BASIS': 'HUMAN_AUTHORIZATION',
            'SOURCE_ID': autorizacao.get('SOURCE_ID'),
            'PROPOSITO': autorizacao.get('PROPOSITO'),
            'LIMITES': limites,
            'SOURCE_RELEVANCE_CONSULTED': False,
            'PROMOTES_RELEVANCE': False,      # PROBE != DECISION
            'CONTRATO': CONTRATO,
        }

    # ── NORMAL: exige o «sim» do dono da relevância, para ESTE par ─────────
    for campo in CAMPOS_DA_AUTORIZACAO:
        if campo not in autorizacao:
            raise SemAutorizacaoDeGasto(
                'a autorização não traz «%s» — não é um veredito do portão de '
                'relevância.' % campo, estado=CONTRATO_ERRADO, modo=modo)

    pedido_sid = conferir_source_id(source_id)
    autorizado_sid = conferir_source_id(autorizacao.get('SOURCE_ID'))
    if pedido_sid != autorizado_sid:
        raise SemAutorizacaoDeGasto(
            'a autorização é da fonte «%s» e a compra é da fonte «%s».'
            % (autorizado_sid, pedido_sid), estado=FONTE_ERRADA, modo=modo,
            source_id=pedido_sid)

    pedido_prop = str(proposito or '').strip()
    autorizado_prop = str(autorizacao.get('PROPOSITO') or '').strip()
    if not pedido_prop:
        raise SemAutorizacaoDeGasto(
            'a compra não diz para que propósito é. A relevância é do PAR '
            '(fonte, propósito); sem propósito não há par.',
            estado=PROPOSITO_ERRADO, modo=modo, source_id=pedido_sid)
    if pedido_prop != autorizado_prop:
        raise SemAutorizacaoDeGasto(
            'a autorização é para «%s» e a compra é para «%s». Um SIM para um '
            'propósito não é um SIM para outro.' % (autorizado_prop, pedido_prop),
            estado=PROPOSITO_ERRADO, modo=modo, source_id=pedido_sid,
            proposito=pedido_prop)

    # ── A ÚNICA COMBINAÇÃO SEM LEITURA DUPLA ──────────────────────────────
    veredito = autorizacao.get('VEREDITO')
    estado_rel = autorizacao.get('ESTADO_DA_RELEVANCIA')
    if veredito != AUTORIZA or estado_rel != SIM:
        nome = _NOME_DA_AUSENCIA.get(estado_rel, SEM_AUTORIZACAO)
        raise SemAutorizacaoDeGasto(
            'o portão de relevância diz VEREDITO=%s com ESTADO=%s para (%s, %s). '
            'Só AUTORIZA com SIM compra.' % (veredito, estado_rel, pedido_sid,
                                             pedido_prop),
            estado=nome, modo=modo, source_id=pedido_sid, proposito=pedido_prop)

    return {
        'CAN_START_PAID_EXECUTION': True,
        'MODE': modo,
        'BASIS': 'SOURCE_RELEVANCE',
        'SOURCE_ID': pedido_sid,
        'PROPOSITO': pedido_prop,
        'ESTADO_DA_RELEVANCIA': estado_rel,
        'VERSAO_DO_PORTAO': autorizacao.get('VERSAO_DO_PORTAO'),
        'DECISAO': autorizacao.get('DECISAO'),
        'EVIDENCE_REFERENCE': (autorizacao.get('DECISAO') or {}).get('EVIDENCIA')
                              if isinstance(autorizacao.get('DECISAO'), dict)
                              else None,
        'SOURCE_RELEVANCE_CONSULTED': True,
        'PROMOTES_RELEVANCE': False,
        'CONTRATO': CONTRATO,
    }


#: O que esta lei NUNCA cria. Escrito para a pressa do mês que vem.
NAO_CRIAR = ('LIVRO_DE_RELEVANCIA_LOCAL', 'CLASSIFICADOR_DE_FONTE',
             'SOURCE_ID_FABRICADO', 'AUTORIZACAO_POR_OMISSAO',
             'MODO_QUE_DISPENSA_AUTORIZACAO')

LEIS = (
    'CREDENTIAL_PRESENT != SPEND_AUTHORIZED',
    'ROUTE_ALLOWED != SPEND_AUTHORIZED',
    'BUDGET_PRESENT != SPEND_AUTHORIZED',
    'PAID_PROVIDER != POLICY_OVERRIDE',
    'TOKEN_OWNER != SPEND_OWNER',
    'SOURCE_RELEVANCE_OWNER != SPEND_ENFORCER',
    'NORMAL_COLLECTION != SOURCE_EVALUATION_PROBE != CAPABILITY_TRIAL',
    'PROBE != DECISION',
    'UM LIMITE EM FALTA E UM LIMITE INFINITO',
    'FAIL CLOSED — O SILENCIO NAO AUTORIZA',
)


def main():
    print(__doc__.strip().splitlines()[0])
    print()
    print('CONTRATO = %s' % CONTRATO)
    print('MODOS    = %s' % ', '.join(MODOS))
    print()
    for lei in LEIS:
        print('    %s' % lei)
    return 0


if __name__ == '__main__':
    sys.exit(main())
