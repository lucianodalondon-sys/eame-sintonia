#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O CONTRATO DE INTELIGÊNCIA COMERCIAL — a conclusão estruturada, não a evidência crua.

    python3 scripts/v21_briefing.py

    SE O CONSUMIDOR TEM DE LER EVIDÊNCIA BRUTA PARA INVENTAR A OPORTUNIDADE,
    A INTELIGÊNCIA NÃO ENTREGOU A OPORTUNIDADE: ENTREGOU A LIÇÃO DE CASA.

Hoje o pacote entrega 43 oportunidades corretas e 7.023 registros de apoio, e
quem consome tem de cruzar os dois para descobrir POR QUE aquilo pode virar
venda, QUE produtos cabem e QUEM deve fazer o quê. Esta camada responde essas
perguntas em campo estruturado.

O QUE ELA **NÃO** DECIDE
-------------------------
Nada. Nem um estado, nem um limiar, nem um produto.

    ESTA CAMADA NÃO TEM RÉGUA PRÓPRIA. ELA LÊ AS QUE JÁ EXISTEM.

Cada valor aqui aponta para o dono da decisão que o produziu:

| campo                | dono da decisão                                    |
|----------------------|----------------------------------------------------|
| `DIRECTION`          | `v21_necessidade.direcao()`                        |
| `WINDOW`             | `v21_oportunidades.janela()` + `janela_vale()`     |
| `COMMERCIAL_PRIORITY`| `v21_comercial.prioridade()`                       |
| `PUBLICATION_STATE`  | `v21_catraca` sobre `v21_comercial.externo()`      |
| `DEPARTMENTS`        | `v21_oportunidades` · o `ACTION_MAP` do arquétipo  |
| `MATCH_STATE`        | `LINK_STRENGTH` do par de rótulo, como o rótulo o escreveu |

O que é NOVO aqui é a COMPOSIÇÃO — dizer, com as peças que já existem, se a
cadeia PROBLEMA → NECESSIDADE → MOMENTO → PORTFÓLIO → AÇÃO fecha inteira. E
quando não fecha, dizer qual elo faltou, em vez de escrever uma frase comercial
plausível por cima do buraco.

    NUNCA ESCREVER UMA FRASE COMERCIAL PORQUE UM PRODUTO E UMA DOENÇA
    APARECERAM NO MESMO CONJUNTO. SE NÃO SE PROVA: UNKNOWN.

WHY_NOW É MAIS ESTRITO QUE `COMMERCIAL_WINDOW`, DE PROPÓSITO
--------------------------------------------------------------
`COMMERCIAL_WINDOW` da régua comercial aceita duas origens: a janela de
APLICAÇÃO declarada, e — quando não há janela — a data do documento, que responde
«o sinal é de hoje?». As duas são verdadeiras e nenhuma foi alterada aqui.

Mas a missão pede uma coisa a mais, e ela é justa:

    SE A JANELA É UNKNOWN, ACT_NOW NÃO PODE NASCER POR DEFAULT.

Então `WHY_NOW = ACT_NOW` exige janela de APLICAÇÃO declarada. Sem ela, um caso
comercialmente pronto sai `VALIDATE_NOW` — que não é rebaixamento: é a leitura
correta, e é ela que manda Market Development validar a janela antes de o
Comercial ativar. Medido: `WHY_NOW=ACT_NOW` nunca é maior que
`COMMERCIAL_WINDOW=ACT_NOW`, e o teste `test_why_now_nunca_infla` prova isso.

FRASE COM VARIÁVEL DENTRO NÃO EXISTE NESTA CAMADA
--------------------------------------------------
Nenhum registro carrega prosa. Todos os campos são CÓDIGO, ID ou NÚMERO; as
frases vivem no cabeçalho, uma vez por código, em PT/IT/EN. O briefing curto é
um `TEMPLATE_CODE` com `SLOTS` preenchidos por valores canônicos, e cada slot
carrega o ID da evidência que o sustenta.

    O CÓDIGO É DADO. A FRASE É TEXTO. E CADA PEDAÇO DA FRASE TEM DONO.
"""
import json
import os
import sys
from collections import Counter, OrderedDict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ING = os.path.join(ROOT, 'build', 'ITALY-REALITY-HANDOFF-V2.1', 'DESIGN-INGEST')
OUT = os.path.join(ING, 'OPPORTUNITY-BRIEFINGS.json')
# A data de referência do pacote, lida do próprio pacote — nunca `date.today()`,
# que faria a mesma entrada produzir saída diferente amanhã.
DATA_REF = None

sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import v21_comercial as CM        # noqa: E402  · dono da prioridade comercial
import v21_normalizar as N        # noqa: E402  · dono do lexico
import v21_necessidade as NEC     # noqa: E402  · dono da direção da necessidade
import v21_oportunidades as OPP   # noqa: E402  · dono da janela e dos portões

# ═══════════════════════════════════════════════════════════════════════════
# OS VOCABULÁRIOS
# ═══════════════════════════════════════════════════════════════════════════

# ── WHY_NOW ─────────────────────────────────────────────────────────────────
ACT_NOW = 'ACT_NOW'
VALIDATE_NOW = 'VALIDATE_NOW'
PREPARE = 'PREPARE'
WATCH = 'WATCH'
FUTURE = 'FUTURE'
CLOSED = 'CLOSED'
UNKNOWN = 'UNKNOWN'
WHY_NOW_STATES = (ACT_NOW, VALIDATE_NOW, PREPARE, WATCH, FUTURE, CLOSED, UNKNOWN)

# ── ESTADOS DE AÇÃO POR DEPARTAMENTO ────────────────────────────────────────
A_ACT, A_PREPARE, A_VALIDATE, A_WATCH, A_NONE, A_UNKNOWN = (
    'ACT_NOW', 'PREPARE', 'VALIDATE', 'WATCH', 'NO_ACTION', 'UNKNOWN')
ACTION_STATES = (A_ACT, A_PREPARE, A_VALIDATE, A_WATCH, A_NONE, A_UNKNOWN)

# ── PAPÉIS DA EVIDÊNCIA ─────────────────────────────────────────────────────
R_SIGNAL = 'SUPPORTS_SIGNAL'
R_DIRECTION = 'SUPPORTS_DIRECTION'
R_WINDOW = 'SUPPORTS_WINDOW'
R_PRODUCT = 'SUPPORTS_PRODUCT_MATCH'
R_REGION = 'SUPPORTS_REGIONAL_CONTEXT'
R_COMMERCIAL = 'SUPPORTS_COMMERCIAL_ACTION'
R_WEAKENS = 'WEAKENS'
R_CONTRADICTS = 'CONTRADICTS'
R_CLOSES = 'CLOSES'
R_BACKGROUND = 'BACKGROUND_ONLY'
EVIDENCE_ROLES = (R_SIGNAL, R_DIRECTION, R_WINDOW, R_PRODUCT, R_REGION,
                  R_COMMERCIAL, R_WEAKENS, R_CONTRADICTS, R_CLOSES,
                  R_BACKGROUND, UNKNOWN)

# ── ESTADOS DE MATCH DE PRODUTO ─────────────────────────────────────────────
M_VERIFIED = 'VERIFIED_LABEL_MATCH'        # cultura E alvo, na mesma linha ou bloco
M_CROP_ONLY = 'CROP_ONLY_MATCH'            # a cultura bate; o alvo não está no rótulo
M_SPECTRUM = 'PRODUCT_SPECTRUM_ONLY'       # o rótulo declara os dois SEPARADAMENTE
M_NO_TARGET_ASKED = 'CROP_MATCH_NO_TARGET_IN_CASE'   # o caso não nomeia alvo
MATCH_STATES = (M_VERIFIED, M_CROP_ONLY, M_SPECTRUM, M_NO_TARGET_ASKED)

# `LINK_STRENGTH` do par de rótulo → o que ele prova. É o rótulo que decide,
# não nós: as três forças já vêm escritas em PRODUCT-RELATIONSHIPS.
FORCA_PROVA_PAR = {'LINHA_DA_TABELA': True, 'BLOCO_DA_CULTURA': True,
                   'DECLARACAO_DE_PRODUTO': False}

# ── O QUE FALTA ─────────────────────────────────────────────────────────────
FALTA = OrderedDict([
    ('WINDOW', 'janela de aplicação declarada para esta cultura, este alvo e '
               'esta região.'),
    ('RECOMMENDATION', 'uma frase da fonte que recomende intervir.'),
    ('REGIONAL_CONFIRMATION', 'confirmação de que a observação fala pela região '
                              'que a oportunidade alega.'),
    ('PRODUCT', 'produto do catálogo comercial ADAMA com rótulo no par cultura '
                '× alvo.'),
    ('REGULATORY', 'autorização ministerial verificada para o par.'),
    ('COMMERCIAL_MATERIAL', 'a página pública do produto declara esta cultura — '
                            'material externo não pode prometer mais do que o '
                            'catálogo anuncia.'),
    ('DIRECTION', 'a direção da necessidade: a fonte não diz se manda agir.'),
    ('MAGNITUDE', 'quanto — área, incidência, severidade. O boletim observa; '
                  'não faz censo.'),
    ('TARGET', 'um alvo agronômico nomeado.'),
    ('SECOND_EVIDENCE_FAMILY', 'uma segunda família de evidência externa. '
                               'Corroboração é amplificador, não contador cego: '
                               'a falta não invalida, e fica escrita.'),
    ('SOURCE_SENTENCE', 'o trecho original da fonte que sustenta a leitura.'),
])

# ── POR QUE AGORA, POR CÓDIGO ───────────────────────────────────────────────
WHY_NOW_CODE = OrderedDict([
    ('WN_SOURCE_SAYS_STOP', 'a fonte que sustenta o caso manda parar, suspender '
                            'ou dá a defesa por concluída.'),
    ('WN_APPLICATION_WINDOW_OPEN', 'há janela de APLICAÇÃO declarada e ela está '
                                   'aberta agora.'),
    ('WN_NO_APPLICATION_WINDOW', 'a necessidade é positiva e corrente, mas não '
                                 'há janela de aplicação declarada: o momento '
                                 'precisa ser validado antes de virar ação.'),
    ('WN_WINDOW_NOT_NOW', 'há janela de aplicação declarada e ela não é agora.'),
    ('WN_COMMERCIAL_PREPARE', 'a relação comercial fecha e o momento é de '
                              'preparação.'),
    ('WN_OPENING_WITHOUT_NEED', 'há abertura de mercado ou de concorrente e não '
                                'há necessidade agronômica corrente.'),
    ('WN_REGULATORY_HORIZON', 'o horizonte é regulatório e longo.'),
    ('WN_STRATEGIC_NO_HORIZON', 'o caso importa e não tem horizonte temporal '
                                'declarado.'),
    ('WN_COMMERCIAL_TO_VALIDATE', 'falta um elemento indispensável — a régua '
                                  'comercial diz qual em WHY_COMMERCIAL_CODES.'),
])

# ── OS ELOS DA CADEIA COMERCIAL ─────────────────────────────────────────────
ELOS = ('PROBLEM', 'AGRONOMIC_NEED', 'MOMENT', 'ADAMA_PORTFOLIO', 'POSSIBLE_ACTION')
REASON_PROVEN = 'PROVEN'

# ── AS AÇÕES, POR CÓDIGO ────────────────────────────────────────────────────
ACAO = OrderedDict([
    ('MD_ACTIVATE_RECOMMENDATION', 'levar a recomendação regional ao campo.'),
    ('MD_VALIDATE_WINDOW', 'confirmar a janela regional de aplicação e a '
                           'recomendação antes de qualquer ativação.'),
    ('MD_VALIDATE_MISSING', 'validar o elemento que falta — a lista está em '
                            'WHAT_IS_MISSING.'),
    ('MD_WATCH_NEXT_BULLETIN', 'acompanhar o próximo boletim da mesma região.'),
    ('CM_ACTIVATE_SALES', 'ativar a força de vendas na região da afirmação.'),
    ('CM_HOLD_UNTIL_VALIDATION', 'não ativar a força de vendas até a validação '
                                 'de Desenvolvimento de Mercado.'),
    ('CM_PREPARE_TERRITORY', 'preparar território e distribuição sem afirmar '
                             'recomendação técnica.'),
    ('CM_NO_ACTION', 'não agir: a fonte não sustenta abordagem comercial agora.'),
    ('MK_PREPARE_MATERIAL', 'preparar material apoiado no que o catálogo público '
                            'já declara.'),
    ('MK_HOLD_MATERIAL', 'não produzir material externo antes da validação.'),
    ('MK_WATCH', 'observar sem produzir peça.'),
    ('ST_TECHNICAL_SUPPORT', 'dar suporte técnico ao par cultura × alvo com base '
                             'no rótulo.'),
    ('ST_VALIDATE_TECHNICAL', 'conferir a leitura agronômica contra a fonte '
                              'original antes de ela sair de casa.'),
    ('ST_WATCH_SCIENCE', 'acompanhar a literatura sobre o par.'),
    ('SP_CHECK_AVAILABILITY', 'conferir disponibilidade do produto na janela.'),
    ('SP_WATCH', 'observar sem mover estoque.'),
    ('PF_REVIEW_PORTFOLIO', 'rever a cobertura de portfólio para o par.'),
    ('PF_WATCH', 'observar a cobertura sem mover portfólio.'),
    ('RG_PREPARE_REGULATORY', 'preparar a resposta regulatória à data europeia.'),
    ('RG_WATCH', 'acompanhar o estado regulatório da substância.'),
    ('UNKNOWN', 'não há dado que sustente ação para este departamento.'),
])

# ── O QUE DESTRAVA O PRÓXIMO PASSO ──────────────────────────────────────────
GATILHO = OrderedDict([
    ('TR_APPLICATION_WINDOW_DECLARED', 'uma janela de aplicação declarada para '
                                       'cultura, alvo e região.'),
    ('TR_NEXT_BULLETIN', 'o próximo boletim do mesmo serviço regional.'),
    ('TR_CATALOG_DECLARES_CROP', 'a página pública do produto passar a declarar '
                                 'esta cultura.'),
    ('TR_SECOND_EVIDENCE_FAMILY', 'uma segunda família de evidência externa '
                                  'sobre o mesmo par.'),
    ('TR_REGULATORY_DATE', 'a data europeia da substância.'),
    ('TR_NONE', 'nada: a fonte fechou a porta e reabri-la exige fato novo.'),
    ('TR_UNKNOWN', 'não se sabe o que destravaria — e inventar um gatilho seria '
                   'inventar uma sequência organizacional.'),
])

# ── A MATRIZ DEPARTAMENTO × WHY_NOW ─────────────────────────────────────────
#
# ⚠️ Esta matriz NÃO inventa hierarquia. Ela diz duas coisas que o dado sustenta:
# (1) quem valida vem antes de quem ativa, e (2) material externo vem depois de
# validação. A dependência é sempre para o departamento que produz o fato que
# falta — nunca uma cadeia de comando imaginada.
#
#     NÃO INVENTAR SEQUÊNCIA ORGANIZACIONAL SE O DADO NÃO A SUSTENTA.
#     ONDE ELE NÃO SUSTENTA, O ESTADO É UNKNOWN.
#
# (estado, código da ação, dependência, gatilho)
_MATRIZ = {
 ACT_NOW: {
   'MARKET_DEVELOPMENT': (A_ACT, 'MD_ACTIVATE_RECOMMENDATION', None, 'TR_NEXT_BULLETIN'),
   'COMMERCIAL': (A_ACT, 'CM_ACTIVATE_SALES', 'MARKET_DEVELOPMENT', 'TR_NEXT_BULLETIN'),
   'MARKETING': (A_PREPARE, 'MK_PREPARE_MATERIAL', 'MARKET_DEVELOPMENT', 'TR_CATALOG_DECLARES_CROP'),
   'SCIENCE_TECHNICAL': (A_PREPARE, 'ST_TECHNICAL_SUPPORT', None, 'TR_NEXT_BULLETIN'),
   'SUPPLY': (A_PREPARE, 'SP_CHECK_AVAILABILITY', None, 'TR_APPLICATION_WINDOW_DECLARED'),
   'PORTFOLIO': (A_WATCH, 'PF_WATCH', None, 'TR_SECOND_EVIDENCE_FAMILY'),
   'REGULATORY': (A_WATCH, 'RG_WATCH', None, 'TR_REGULATORY_DATE'),
 },
 VALIDATE_NOW: {
   'MARKET_DEVELOPMENT': (A_VALIDATE, 'MD_VALIDATE_WINDOW', None, 'TR_APPLICATION_WINDOW_DECLARED'),
   'COMMERCIAL': (A_PREPARE, 'CM_HOLD_UNTIL_VALIDATION', 'MARKET_DEVELOPMENT', 'TR_APPLICATION_WINDOW_DECLARED'),
   'MARKETING': (A_PREPARE, 'MK_HOLD_MATERIAL', 'MARKET_DEVELOPMENT', 'TR_APPLICATION_WINDOW_DECLARED'),
   'SCIENCE_TECHNICAL': (A_VALIDATE, 'ST_VALIDATE_TECHNICAL', None, 'TR_NEXT_BULLETIN'),
   'SUPPLY': (A_WATCH, 'SP_WATCH', 'MARKET_DEVELOPMENT', 'TR_APPLICATION_WINDOW_DECLARED'),
   'PORTFOLIO': (A_WATCH, 'PF_WATCH', None, 'TR_SECOND_EVIDENCE_FAMILY'),
   'REGULATORY': (A_WATCH, 'RG_WATCH', None, 'TR_REGULATORY_DATE'),
 },
 PREPARE: {
   'MARKET_DEVELOPMENT': (A_PREPARE, 'MD_VALIDATE_WINDOW', None, 'TR_APPLICATION_WINDOW_DECLARED'),
   'COMMERCIAL': (A_PREPARE, 'CM_PREPARE_TERRITORY', 'MARKET_DEVELOPMENT', 'TR_APPLICATION_WINDOW_DECLARED'),
   'MARKETING': (A_PREPARE, 'MK_PREPARE_MATERIAL', 'MARKET_DEVELOPMENT', 'TR_CATALOG_DECLARES_CROP'),
   'SCIENCE_TECHNICAL': (A_PREPARE, 'ST_TECHNICAL_SUPPORT', None, 'TR_NEXT_BULLETIN'),
   'SUPPLY': (A_WATCH, 'SP_WATCH', None, 'TR_APPLICATION_WINDOW_DECLARED'),
   'PORTFOLIO': (A_WATCH, 'PF_WATCH', None, 'TR_SECOND_EVIDENCE_FAMILY'),
   'REGULATORY': (A_WATCH, 'RG_WATCH', None, 'TR_REGULATORY_DATE'),
 },
 WATCH: {
   'MARKET_DEVELOPMENT': (A_WATCH, 'MD_WATCH_NEXT_BULLETIN', None, 'TR_NEXT_BULLETIN'),
   'COMMERCIAL': (A_NONE, 'CM_NO_ACTION', 'MARKET_DEVELOPMENT', 'TR_SECOND_EVIDENCE_FAMILY'),
   'MARKETING': (A_WATCH, 'MK_WATCH', None, 'TR_SECOND_EVIDENCE_FAMILY'),
   'SCIENCE_TECHNICAL': (A_WATCH, 'ST_WATCH_SCIENCE', None, 'TR_SECOND_EVIDENCE_FAMILY'),
   'SUPPLY': (A_NONE, 'SP_WATCH', None, 'TR_UNKNOWN'),
   'PORTFOLIO': (A_WATCH, 'PF_REVIEW_PORTFOLIO', None, 'TR_SECOND_EVIDENCE_FAMILY'),
   'REGULATORY': (A_WATCH, 'RG_WATCH', None, 'TR_REGULATORY_DATE'),
 },
 FUTURE: {
   'MARKET_DEVELOPMENT': (A_WATCH, 'MD_WATCH_NEXT_BULLETIN', None, 'TR_REGULATORY_DATE'),
   'COMMERCIAL': (A_NONE, 'CM_NO_ACTION', 'REGULATORY', 'TR_REGULATORY_DATE'),
   'MARKETING': (A_NONE, 'MK_WATCH', 'REGULATORY', 'TR_REGULATORY_DATE'),
   'SCIENCE_TECHNICAL': (A_WATCH, 'ST_WATCH_SCIENCE', None, 'TR_REGULATORY_DATE'),
   'SUPPLY': (A_PREPARE, 'SP_CHECK_AVAILABILITY', 'REGULATORY', 'TR_REGULATORY_DATE'),
   'PORTFOLIO': (A_PREPARE, 'PF_REVIEW_PORTFOLIO', 'REGULATORY', 'TR_REGULATORY_DATE'),
   'REGULATORY': (A_PREPARE, 'RG_PREPARE_REGULATORY', None, 'TR_REGULATORY_DATE'),
 },
 CLOSED: {
   'MARKET_DEVELOPMENT': (A_WATCH, 'MD_WATCH_NEXT_BULLETIN', None, 'TR_NEXT_BULLETIN'),
   'COMMERCIAL': (A_NONE, 'CM_NO_ACTION', None, 'TR_NONE'),
   'MARKETING': (A_NONE, 'MK_HOLD_MATERIAL', None, 'TR_NONE'),
   'SCIENCE_TECHNICAL': (A_WATCH, 'ST_WATCH_SCIENCE', None, 'TR_NEXT_BULLETIN'),
   'SUPPLY': (A_NONE, 'SP_WATCH', None, 'TR_NONE'),
   'PORTFOLIO': (A_NONE, 'PF_WATCH', None, 'TR_NONE'),
   'REGULATORY': (A_NONE, 'RG_WATCH', None, 'TR_NONE'),
 },
}

DEPARTAMENTOS_DO_MODELO = ('MARKET_DEVELOPMENT', 'COMMERCIAL', 'MARKETING',
                           'SCIENCE_TECHNICAL', 'SUPPLY', 'PORTFOLIO',
                           'REGULATORY')

# ── O BRIEFING CURTO, POR TEMPLATE ──────────────────────────────────────────
# Cada template é uma frase FIXA com marcadores. Os marcadores são preenchidos
# por valores CANÔNICOS (IDs), e cada um carrega a evidência que o sustenta.
TEMPLATE = OrderedDict([
    ('BR_PRESSURE_WINDOW_PROVEN', {
        'PT': '{TARGET} em {CROP} · {REGION}: pressão observada e janela de '
              'aplicação declarada. O portfólio ADAMA tem {PRODUCTS} '
              'solução(ões) com uso compatível no par.',
        'IT': '{TARGET} su {CROP} · {REGION}: pressione osservata e finestra di '
              'applicazione dichiarata. Il portafoglio ADAMA ha {PRODUCTS} '
              'soluzione/i con impiego compatibile sulla coppia.',
        'EN': '{TARGET} on {CROP} · {REGION}: pressure observed and an '
              'application window declared. The ADAMA portfolio has {PRODUCTS} '
              'solution(s) with compatible use on the pair.',
        'SLOTS': ['TARGET', 'CROP', 'REGION', 'PRODUCTS']}),
    ('BR_PRESSURE_WINDOW_UNPROVEN', {
        'PT': '{TARGET} em {CROP} · {REGION}: pressão observada — a janela '
              'regional ainda precisa de validação. O portfólio ADAMA tem '
              '{PRODUCTS} solução(ões) com uso compatível no par.',
        'IT': '{TARGET} su {CROP} · {REGION}: pressione osservata — la finestra '
              'regionale richiede ancora validazione. Il portafoglio ADAMA ha '
              '{PRODUCTS} soluzione/i con impiego compatibile sulla coppia.',
        'EN': '{TARGET} on {CROP} · {REGION}: pressure observed — the regional '
              'window still needs validation. The ADAMA portfolio has '
              '{PRODUCTS} solution(s) with compatible use on the pair.',
        'SLOTS': ['TARGET', 'CROP', 'REGION', 'PRODUCTS']}),
    ('BR_SOURCE_CLOSES', {
        'PT': '{TARGET} em {CROP} · {REGION}: a fonte não manda agir. Não há '
              'razão de venda agora, e a evidência que fecha viaja junto.',
        'IT': '{TARGET} su {CROP} · {REGION}: la fonte non prescrive di '
              'intervenire. Non c\'è ragione di vendita ora, e l\'evidenza che '
              'chiude viaggia insieme.',
        'EN': '{TARGET} on {CROP} · {REGION}: the source does not call for '
              'action. There is no sales reason now, and the closing evidence '
              'travels with the case.',
        'SLOTS': ['TARGET', 'CROP', 'REGION']}),
    ('BR_OPENING_WITHOUT_NEED', {
        'PT': '{CROP} · {REGION}: há movimento externo de mercado ou de '
              'concorrente e nenhum problema agronômico nomeado. Não é venda: '
              'é observação.',
        'IT': '{CROP} · {REGION}: c\'è movimento esterno di mercato o di '
              'concorrente e nessun problema agronomico nominato. Non è '
              'vendita: è osservazione.',
        'EN': '{CROP} · {REGION}: there is external market or competitor '
              'movement and no named agronomic problem. This is not a sale: it '
              'is an observation.',
        'SLOTS': ['CROP', 'REGION']}),
    ('BR_REGULATORY_HORIZON', {
        'PT': '{CROP} · {REGION}: preparação regulatória. Data europeia '
              'publicada, sem necessidade de campo corrente.',
        'IT': '{CROP} · {REGION}: preparazione regolatoria. Data europea '
              'pubblicata, senza necessità di campo corrente.',
        'EN': '{CROP} · {REGION}: regulatory preparation. A European date is '
              'published, with no current field need.',
        'SLOTS': ['CROP', 'REGION']}),
    ('BR_UNKNOWN', {
        'PT': 'não há cadeia factual suficiente para um briefing comercial. '
              'O que falta está em WHAT_IS_MISSING.',
        'IT': 'non c\'è catena fattuale sufficiente per un briefing '
              'commerciale. Ciò che manca è in WHAT_IS_MISSING.',
        'EN': 'there is not enough factual chain for a commercial briefing. '
              'What is missing is listed in WHAT_IS_MISSING.',
        'SLOTS': []}),
])

# ── O RESUMO DE CADA EVIDÊNCIA ──────────────────────────────────────────────
RESUMO_EVIDENCIA = OrderedDict([
    ('IE_PRESSURE_OBSERVED', 'o documento registra a presença do alvo na '
                             'cultura. A evidência sustenta o sinal e não '
                             'determina sozinha uma janela de aplicação.'),
    ('IE_SOURCE_RECOMMENDS', 'o documento recomenda intervir sobre este par.'),
    ('IE_SOURCE_STOPS', 'o documento manda parar, suspender, dá a defesa por '
                        'concluída ou proíbe a intervenção.'),
    ('IE_SOURCE_MONITORS', 'o documento manda observar, e observar não é '
                           'tratar.'),
    ('IE_LABEL_PAIR', 'o rótulo ministerial nomeia esta cultura e este alvo.'),
    ('IE_LABEL_SPECTRUM', 'o rótulo declara o alvo e a cultura SEPARADAMENTE: '
                          'espectro de produto não é espectro na cultura.'),
    ('IE_WINDOW_DECLARED', 'o registro declara uma janela para esta cultura, '
                           'este alvo e esta região.'),
    ('IE_REGIONAL_CONTEXT', 'o registro descreve o mesmo território da '
                            'afirmação.'),
    ('IE_BACKGROUND', 'o registro é contexto: não observa o par no campo e não '
                      'autoriza produto nele.'),
    ('IE_UNKNOWN', 'não se sabe que papel este registro exerce no caso.'),
])

IMPLICACAO = OrderedDict([
    ('CI_SUPPORTS_SALE', 'sustenta abordagem comercial no par.'),
    ('CI_COOLS_OPPORTUNITY', 'esfria a oportunidade: a fonte não sustenta '
                             'abordagem comercial agora.'),
    ('CI_ENABLES_PRODUCT_CLAIM', 'permite nomear produto autorizado no par.'),
    ('CI_NO_IMPLICATION', 'não tem implicação comercial própria.'),
    ('UNKNOWN', 'a fonte não permite concluir implicação comercial.'),
])

# Papel da evidência → implicação comercial. A regra é uma tabela, não uma
# opinião por caso, e há uma coluna UNKNOWN de propósito:
#
#     NÃO RESUMIR «COMERCIALMENTE» O QUE A FONTE NÃO PERMITE CONCLUIR.
IMPLICACAO_DO_PAPEL = {
    R_DIRECTION: 'CI_SUPPORTS_SALE',
    R_SIGNAL: 'UNKNOWN',           # presença não é recomendação
    R_PRODUCT: 'CI_ENABLES_PRODUCT_CLAIM',
    R_COMMERCIAL: 'CI_ENABLES_PRODUCT_CLAIM',
    R_WINDOW: 'CI_SUPPORTS_SALE',
    R_REGION: 'CI_NO_IMPLICATION',
    R_BACKGROUND: 'CI_NO_IMPLICATION',
    R_WEAKENS: 'CI_COOLS_OPPORTUNITY',
    R_CONTRADICTS: 'CI_COOLS_OPPORTUNITY',
    R_CLOSES: 'CI_COOLS_OPPORTUNITY',
    UNKNOWN: 'UNKNOWN',
}


# ═══════════════════════════════════════════════════════════════════════════
# AS LEITURAS
# ═══════════════════════════════════════════════════════════════════════════
def _le(nome):
    p = os.path.join(ING, nome)
    if not os.path.exists(p):
        return []
    return json.load(open(p, encoding='utf-8')).get('RECORDS') or []


def por_que_agora(o):
    """→ (WHY_NOW, [códigos]). Sem régua nova: só composição das que existem.

    ⚠️ ACT_NOW EXIGE JANELA DE APLICAÇÃO. `COMMERCIAL_WINDOW` da régua comercial
    também aceita a data do documento — e está certo, porque essa data responde
    «o sinal é de hoje?». Mas «hoje há sinal» não é «hoje é a hora de aplicar»,
    e a missão foi explícita:

        SE A JANELA É UNKNOWN, ACT_NOW NÃO PODE NASCER POR DEFAULT.

    Nada foi afrouxado para isto: WHY_NOW é ESTRITAMENTE mais conservador que
    COMMERCIAL_WINDOW, nunca mais permissivo.
    """
    need = o.get('NEED_DIRECTION') or UNKNOWN
    if need in CM.NECESSIDADE_FECHADA:
        return CLOSED, ['WN_SOURCE_SAYS_STOP']

    pri = o.get('COMMERCIAL_PRIORITY')
    tem_janela = (o.get('WINDOW_STATE') not in (None, 'UNKNOWN')
                  and o.get('WINDOW_KIND') == 'APPLICATION')

    if pri == CM.SALES_READY:
        if not tem_janela:
            return VALIDATE_NOW, ['WN_NO_APPLICATION_WINDOW']
        if o.get('COMMERCIAL_WINDOW') == 'ACT_NOW':
            return ACT_NOW, ['WN_APPLICATION_WINDOW_OPEN']
        return PREPARE, ['WN_WINDOW_NOT_NOW']
    if pri == CM.SALES_PREPARE:
        return PREPARE, ['WN_COMMERCIAL_PREPARE']
    if pri == CM.COMMERCIAL_WATCH:
        return WATCH, ['WN_OPENING_WITHOUT_NEED']
    if pri == CM.STRATEGIC_OPPORTUNITY:
        if o.get('STATUS') == 'FUTURE_PREPARATION':
            return FUTURE, ['WN_REGULATORY_HORIZON']
        return WATCH, ['WN_STRATEGIC_NO_HORIZON']
    return UNKNOWN, ['WN_COMMERCIAL_TO_VALIDATE']


def portfolio(o, pares, reg_por_num, ix_com, ai_por_prod, ai_por_id, janelas):
    """→ [PORTFOLIO_MATCH]. TODOS os que cabem, não só o primeiro.

    A ponte é o par de rótulo: ele traz o número de registro e diz para que
    cultura e que alvo aquele registro está autorizado. O estado do match sai da
    força que o PRÓPRIO rótulo declara em `LINK_STRENGTH` — não de leitura nossa.
    """
    crop, alvo = o.get('CROP'), o.get('TARGET')
    if not crop:
        return [], []
    por_reg = {}
    for r in pares:
        if crop not in (r.get('CROP_IDS') or []):
            continue
        n = CM.num(r.get('REGISTRATION_NUMBER'))
        por_reg.setdefault(n, []).append(r)

    saida, so_cultura = [], []
    for n, rs in sorted(por_reg.items()):
        no_alvo = [r for r in rs if alvo and alvo in (r.get('ISSUE_IDS') or [])]
        provam = [r for r in no_alvo if FORCA_PROVA_PAR.get(r.get('LINK_STRENGTH'))]
        espectro = [r for r in no_alvo if not FORCA_PROVA_PAR.get(r.get('LINK_STRENGTH'))]

        if not alvo:
            # O caso não nomeia alvo. O rótulo cobre a CULTURA, e dizer mais do
            # que isso seria promover cobertura de cultura a cobertura de alvo.
            estado, evid = M_NO_TARGET_ASKED, rs
        elif provam:
            estado, evid = M_VERIFIED, provam
        elif espectro:
            estado, evid = M_SPECTRUM, espectro
        else:
            # ⚠️ O CASO NOMEIA UM ALVO E ESTE RÓTULO NÃO O NOMEIA.
            # Autorização na cultura NÃO é autorização contra o alvo. Pôr este
            # produto na lista de matches faria o payload afirmar que ele cabe
            # na oportunidade — e ninguém que lesse a lista iria conferir
            # produto a produto qual dos 25 tem o alvo e qual não tem.
            #
            #     COBERTURA DE CULTURA NÃO É COBERTURA DE ALVO.
            #
            # Ele não some: é contado em CROP_LEVEL_ONLY_COUNT, ao lado.
            so_cultura.append(n)
            continue

        reg = reg_por_num.get(n) or {}
        cat = (ix_com.get(n) or [None])[0]
        nome = (reg.get('NAME') or (cat or {}).get('NAME')
                or rs[0].get('PRODUCT_NAME'))

        # Substâncias ativas — o que o produto CONTÉM. O que ele pode fazer é
        # do rótulo, e vive noutro campo.
        subst = []
        for pai in ai_por_prod.get(n, []):
            a = ai_por_id.get(pai.get('ACTIVE_INGREDIENT_ID')) or {}
            subst.append({
                'ACTIVE_INGREDIENT_ID': pai.get('ACTIVE_INGREDIENT_ID'),
                'NAME': pai.get('ACTIVE_INGREDIENT'),
                'MOA_STATE': a.get('MOA_STATE') or UNKNOWN,
                'HRAC': a.get('HRAC'), 'IRAC': a.get('IRAC'), 'FRAC': a.get('FRAC'),
                'EU_STATE': a.get('EU_STATE') or UNKNOWN,
                'EU_EXPIRATION_OF_APPROVAL': a.get('EU_EXPIRATION_OF_APPROVAL'),
                'EVIDENCE_IDS': [pai.get('ID')],
            })

        declara, _q = (CM.catalogo_declara_cultura(crop, [cat]) if cat
                       else (False, None))

        # Janela: a chave mínima é do motor, e é dele que ela continua sendo.
        jan = [w['ID'] for w in janelas
               if OPP.janela_vale(w, crop, alvo, o.get('GEOGRAPHY'))]

        # ⚠️ A DATA VENCIDA É UM FATO, E SÓ UM FATO.
        # A doutrina do repositório já está escrita em `adama_es_gate.py` e em
        # `adama_it_intelligence.py`, e ela não é minha para reescrever:
        #
        #     EXPIRY != WITHDRAWAL. DATA VENCIDA ENTRA COMO DATA, NUNCA COMO
        #     RETIRADA. E `CURRENTLY_MARKETABLE` É UNKNOWN SEMPRE, porque
        #     depende do período de smaltimento, fixado por decreto e ausente
        #     deste dataset.
        #
        # Então o produto CONTINUA um match válido: o rótulo diz o que ele
        # cobre, e isso não mudou. O que a data faz é impedir que ele seja
        # NOMEADO PARA FORA sem alguém conferir — medido: 5 dos 5 produtos do
        # par milho × piralide têm data 2026-08-31, dois dias antes da data de
        # referência do pacote.
        vencida = bool(reg.get('EXPIRY')) and str(reg['EXPIRY']) < str(DATA_REF)
        restr = []
        if vencida:
            restr.append('AUTHORIZATION_DATE_PAST_REFERENCE')
        if estado == M_SPECTRUM:
            restr.append('SPECTRUM_NOT_CROP_SPECIFIC')
        if estado == M_CROP_ONLY and alvo:
            restr.append('TARGET_NOT_ON_LABEL')
        if cat and not declara:
            restr.append('CATALOG_DOES_NOT_DECLARE_CROP')
        if not cat:
            restr.append('NOT_IN_PUBLIC_CATALOG')
        # `AUTHORIZATION_HAS_EXPIRY_DATE` foi retirado daqui: TODOS os 463
        # matches o carregavam, porque toda autorização tem data. Restrição que
        # vale para todo mundo não restringe ninguém — só faz barulho.

        saida.append({
            'PRODUCT_ID': reg.get('ID') or (cat or {}).get('ID') or ('REG_' + n),
            'PRODUCT_NAME': nome,
            'REGISTRATION_NUMBER': rs[0].get('REGISTRATION_NUMBER'),
            'ACTIVE_SUBSTANCES': subst,
            'MATCH_STATE': estado,
            'MATCH_REASON_CODE': {M_VERIFIED: 'IE_LABEL_PAIR',
                                  M_SPECTRUM: 'IE_LABEL_SPECTRUM',
                                  M_CROP_ONLY: 'IE_LABEL_SPECTRUM',
                                  M_NO_TARGET_ASKED: 'IE_LABEL_SPECTRUM'}[estado],
            'CROP_FIT': {
                'STATE': 'DECLARED_ON_LABEL',
                'CROP_ID': crop,
                'CROP_ON_LABEL': rs[0].get('CROP_ON_LABEL'),
                'EVIDENCE_IDS': [r['ID'] for r in rs[:6]]},
            'TARGET_FIT': ({
                'STATE': estado,
                'ISSUE_ID': alvo,
                'TARGET_ON_LABEL': evid[0].get('TARGET_ON_LABEL'),
                'TARGET_AS_WRITTEN': evid[0].get('TARGET_AS_WRITTEN'),
                'LINK_STRENGTH': evid[0].get('LINK_STRENGTH'),
                'EVIDENCE_IDS': [r['ID'] for r in evid[:6]]}
                if alvo else {'STATE': UNKNOWN, 'ISSUE_ID': None,
                              'EVIDENCE_IDS': []}),
            'REGULATORY_FIT': {
                'STATE': 'AUTHORIZED_IN_ITALY' if reg else UNKNOWN,
                'AUTHORIZATION_HOLDER': reg.get('AUTHORIZATION_HOLDER'),
                'AUTHORIZATION_STATUS': reg.get('STATUS'),
                'EXPIRY': reg.get('EXPIRY'),
                'AUTHORIZATION_GEOGRAPHY': reg.get('REGION_IDS') or [],
                'EVIDENCE_IDS': [reg['ID']] if reg else []},
            'REGIONAL_FIT': {
                'STATE': ('NATIONAL_AUTHORIZATION_CONTAINS_REGION'
                          if 'GEO_ITALY' in (reg.get('REGION_IDS') or [])
                          else UNKNOWN),
                'CLAIM_REGION': o.get('GEOGRAPHY'),
                'LAW': 'rotulo nacional CONTEM a regiao; conter nao e contradizer.'},
            'WINDOW_FIT': {
                'STATE': 'WINDOW_DECLARED' if jan else UNKNOWN,
                'WINDOW_IDS': jan,
                'LAW': 'uma janela e de uma cultura, de um alvo e de uma regiao. '
                       'Coincidir na cultura nao e ser a mesma janela.'},
            'COMMERCIAL_CATALOG': {
                'STATE': 'IN_PUBLIC_CATALOG' if cat else 'NOT_IN_PUBLIC_CATALOG',
                'CATALOG_PRODUCT_ID': (cat or {}).get('ID'),
                'PUBLIC_CATALOG_URL': (cat or {}).get('PUBLIC_CATALOG_URL'),
                'CATALOG_DECLARES_CROP': bool(declara),
                'CROPS_DECLARED_ON_SITE': (cat or {}).get('CROPS_DECLARED_ON_SITE') or []},
            'VALIDATION_STATE': ('READY_TO_NAME_EXTERNALLY'
                                 if (estado == M_VERIFIED and cat and declara
                                     and not vencida)
                                 else 'INTERNAL_READING_ONLY'),
            'MARKETABLE_STATE': UNKNOWN,
            'MARKETABLE_LAW': 'CURRENTLY_MARKETABLE e UNKNOWN sempre: depende do '
                              'periodo de smaltimento, fixado por decreto e '
                              'ausente deste dataset. EXPIRY != WITHDRAWAL — '
                              'data vencida entra como data, nunca como retirada.',
            'RESTRICTION_CODES': restr,
            'EVIDENCE_IDS': [r['ID'] for r in evid[:6]],
        })
    # Ordem estável e SEM significado de escolha: nome, para o diff ser legível.
    saida.sort(key=lambda x: (x['PRODUCT_NAME'] or '').upper())
    return saida, so_cultura


def principal(matches):
    """→ (PRIMARY_MATCH, código da regra). UNKNOWN quando não há regra defensável.

        SE NÃO HÁ REGRA PARA ESCOLHER UM PRINCIPAL, NÃO SE ESCOLHE PELA ORDEM
        DA LISTA. A ORDEM É ALFABÉTICA E NÃO SIGNIFICA NADA.
    """
    fortes = [m for m in matches if m['VALIDATION_STATE'] == 'READY_TO_NAME_EXTERNALLY']
    if len(fortes) == 1:
        return fortes[0]['PRODUCT_ID'], 'PM_SINGLE_EXTERNALLY_NAMEABLE'
    if len(fortes) > 1:
        return None, 'PM_SEVERAL_EQUALLY_DEFENSIBLE'
    return None, 'PM_NONE_EXTERNALLY_NAMEABLE'


def o_que_falta(o, matches, why_now):
    f = []
    if not o.get('TARGET'):
        f.append('TARGET')
    if o.get('WINDOW_STATE') in (None, 'UNKNOWN') or o.get('WINDOW_KIND') != 'APPLICATION':
        f.append('WINDOW')
    if (o.get('NEED_DIRECTION') or UNKNOWN) == UNKNOWN:
        f.append('DIRECTION')
    elif o.get('NEED_DIRECTION') not in CM.NECESSIDADE_POSITIVA and why_now != CLOSED:
        f.append('RECOMMENDATION')
    if not o.get('NEED_EXCERPT'):
        f.append('SOURCE_SENTENCE')
    if o.get('CLAIM_GEOGRAPHY_HOLDS') is not True:
        f.append('REGIONAL_CONFIRMATION')
    if not (o.get('COMMERCIAL_PRODUCT_COUNT') or 0):
        f.append('PRODUCT')
    if o.get('PRODUCT_LINK_STATE') != 'VERIFIED_LABEL_MATCH':
        f.append('REGULATORY')
    elif matches and all('AUTHORIZATION_DATE_PAST_REFERENCE' in m['RESTRICTION_CODES']
                         for m in matches):
        f.append('REGULATORY')
    if matches and not any(m['COMMERCIAL_CATALOG']['CATALOG_DECLARES_CROP']
                           for m in matches):
        f.append('COMMERCIAL_MATERIAL')
    if len(o.get('EVIDENCE_FAMILIES') or []) < 2:
        f.append('SECOND_EVIDENCE_FAMILY')
    # A magnitude não é medida por nenhuma fonte do pacote: boletim observa,
    # não faz censo. Fica declarada como ausente sempre que há alvo.
    if o.get('TARGET'):
        f.append('MAGNITUDE')
    return f


def cadeia_comercial(o, matches, why_now, falta):
    """PROBLEMA → NECESSIDADE → MOMENTO → PORTFÓLIO → AÇÃO, elo a elo."""
    c = OrderedDict()
    c['PROBLEM'] = ({'STATE': 'DECLARED', 'VALUE': o['TARGET'],
                     'EVIDENCE_IDS': [o.get('NEED_EVIDENCE_ID')] if o.get('NEED_EVIDENCE_ID') else []}
                    if o.get('TARGET') else {'STATE': UNKNOWN, 'VALUE': None,
                                             'EVIDENCE_IDS': []})
    need = o.get('NEED_DIRECTION') or UNKNOWN
    c['AGRONOMIC_NEED'] = (
        {'STATE': 'POSITIVE', 'VALUE': need,
         'EVIDENCE_IDS': [o['NEED_EVIDENCE_ID']] if o.get('NEED_EVIDENCE_ID') else [],
         'SOURCE_EXCERPT': o.get('NEED_EXCERPT') or '',
         'METHOD': o.get('NEED_METHOD')}
        if need in CM.NECESSIDADE_POSITIVA
        else {'STATE': UNKNOWN if need == UNKNOWN else 'NOT_POSITIVE',
              'VALUE': need, 'EVIDENCE_IDS': [], 'SOURCE_EXCERPT': '',
              'METHOD': None})

    if o.get('WINDOW_KIND') == 'APPLICATION' and o.get('WINDOW_STATE') not in (None, UNKNOWN):
        c['MOMENT'] = {'STATE': 'APPLICATION_WINDOW', 'VALUE': o.get('WINDOW_FIELD'),
                       'EVIDENCE_IDS': []}
    elif o.get('SIGNAL_AGE_DAYS') is not None and o['SIGNAL_AGE_DAYS'] <= 120:
        # O portão C do motor já decide que 120 dias é o limite do «corrente».
        # Reusar o limiar dele é o contrário de inventar um.
        c['MOMENT'] = {'STATE': 'SIGNAL_RECENCY', 'VALUE': o.get('SIGNAL_DATE'),
                       'EVIDENCE_IDS': [o['NEED_EVIDENCE_ID']] if o.get('NEED_EVIDENCE_ID') else []}
    else:
        c['MOMENT'] = {'STATE': UNKNOWN, 'VALUE': None, 'EVIDENCE_IDS': []}

    fortes = [m for m in matches if m['MATCH_STATE'] == M_VERIFIED
              and m['COMMERCIAL_CATALOG']['STATE'] == 'IN_PUBLIC_CATALOG']
    c['ADAMA_PORTFOLIO'] = ({'STATE': 'VERIFIED_AND_IN_CATALOG',
                             'VALUE': [m['PRODUCT_ID'] for m in fortes],
                             'EVIDENCE_IDS': [i for m in fortes for i in m['EVIDENCE_IDS'][:2]]}
                            if fortes else {'STATE': UNKNOWN, 'VALUE': [],
                                            'EVIDENCE_IDS': []})
    c['POSSIBLE_ACTION'] = ({'STATE': 'DERIVED_FROM_WHY_NOW', 'VALUE': why_now,
                             'EVIDENCE_IDS': []}
                            if why_now not in (UNKNOWN, CLOSED)
                            else {'STATE': UNKNOWN, 'VALUE': why_now,
                                  'EVIDENCE_IDS': []})

    faltando = [k for k in ELOS if c[k]['STATE'] == UNKNOWN or c[k]['STATE'] == 'NOT_POSITIVE']
    return c, (REASON_PROVEN if not faltando else UNKNOWN), faltando


def mapa_de_acao(o, why_now, falta):
    """Um registro por departamento, e os departamentos vêm do motor."""
    linhas = []
    deps = [d for d in (o.get('ACTION_MAP') or []) if d in DEPARTAMENTOS_DO_MODELO]
    tabela = _MATRIZ.get(why_now)
    for d in deps:
        if tabela is None:
            # WHY_NOW = UNKNOWN. Só há um departamento cujo trabalho o dado
            # sustenta: quem valida o que falta — e só quando SABEMOS o que falta.
            if d == 'MARKET_DEVELOPMENT' and falta:
                linhas.append({'DEPARTMENT': d, 'ACTION_STATE': A_VALIDATE,
                               'ACTION_CODE': 'MD_VALIDATE_MISSING',
                               'WHY_CODES': ['WN_COMMERCIAL_TO_VALIDATE'],
                               'EVIDENCE_IDS': [], 'DEPENDENCY': None,
                               'NEXT_TRIGGER': 'TR_UNKNOWN',
                               'MISSING_CODES': falta})
            else:
                linhas.append({'DEPARTMENT': d, 'ACTION_STATE': A_UNKNOWN,
                               'ACTION_CODE': 'UNKNOWN',
                               'WHY_CODES': ['WN_COMMERCIAL_TO_VALIDATE'],
                               'EVIDENCE_IDS': [], 'DEPENDENCY': 'MARKET_DEVELOPMENT',
                               'NEXT_TRIGGER': 'TR_UNKNOWN', 'MISSING_CODES': falta})
            continue
        estado, acao, dep, gat = tabela[d]
        ev = []
        if o.get('NEED_EVIDENCE_ID') and estado in (A_ACT, A_VALIDATE, A_PREPARE):
            ev.append(o['NEED_EVIDENCE_ID'])
        linhas.append({'DEPARTMENT': d, 'ACTION_STATE': estado,
                       'ACTION_CODE': acao,
                       'WHY_CODES': [], 'EVIDENCE_IDS': ev,
                       'DEPENDENCY': dep, 'NEXT_TRIGGER': gat,
                       'MISSING_CODES': [c for c in falta
                                         if c in ('WINDOW', 'COMMERCIAL_MATERIAL')]})
    return linhas


def papel_da_evidencia(o, ev, dir_por_sinal):
    """Que papel esta evidência exerce NESTE caso. Casos negativos preservados."""
    t = ev.get('ENTITY_TYPE')
    need = o.get('NEED_DIRECTION') or UNKNOWN
    if ev['ID'] == o.get('NEED_EVIDENCE_ID'):
        return R_CLOSES if need in CM.NECESSIDADE_FECHADA else R_DIRECTION
    if t == 'LABEL_USE_RELATIONSHIP':
        return R_PRODUCT
    if t in ('COMMERCIAL_PRODUCT', 'CATALOG_PRODUCT'):
        return R_COMMERCIAL
    if t == 'CROP_WINDOW':
        return R_WINDOW
    if t == 'FIELD_SIGNAL':
        d = dir_por_sinal.get((ev['ID'], o.get('CROP'), o.get('TARGET')))
        if d and d in CM.NECESSIDADE_FECHADA and need in CM.NECESSIDADE_POSITIVA:
            # ⚠️ CASO NEGATIVO PRESERVADO. Um boletim da mesma região que manda
            # parar não some porque outro manda agir: ele CONTRADIZ, e viaja.
            return R_CONTRADICTS
        if d and d in CM.NECESSIDADE_MORNA and need in CM.NECESSIDADE_POSITIVA:
            return R_WEAKENS
        return R_SIGNAL
    if t in ('MARKET_OBSERVATION', 'COMPETITOR_ACTIVITY', 'EVENT', 'AGROMET_CONDITION'):
        if o.get('GEOGRAPHY') in (ev.get('REGION_IDS') or []):
            return R_REGION
        return R_BACKGROUND
    if t in ('SCIENTIFIC_RECORD', 'NEWS_ITEM', 'RESISTANCE_RECORD', 'PUBLIC_VOICE',
             'CROP_ECONOMIC_WEIGHT_CLAIM', 'REGULATORY_FUTURE_FACT',
             'ACTIVE_INGREDIENT', 'REGULATORY_PRODUCT', 'PRODUCT_ACTIVE_INGREDIENT'):
        return R_BACKGROUND
    return UNKNOWN


def resumo_da_evidencia(papel, ev, dir_por_sinal, o):
    if papel == R_DIRECTION:
        return 'IE_SOURCE_RECOMMENDS'
    if papel == R_CLOSES or papel == R_CONTRADICTS:
        return 'IE_SOURCE_STOPS'
    if papel == R_WEAKENS:
        return 'IE_SOURCE_MONITORS'
    if papel == R_SIGNAL:
        return 'IE_PRESSURE_OBSERVED'
    if papel == R_PRODUCT:
        return ('IE_LABEL_PAIR' if FORCA_PROVA_PAR.get(ev.get('LINK_STRENGTH'))
                else 'IE_LABEL_SPECTRUM')
    if papel == R_WINDOW:
        return 'IE_WINDOW_DECLARED'
    if papel == R_REGION:
        return 'IE_REGIONAL_CONTEXT'
    if papel == R_BACKGROUND or papel == R_COMMERCIAL:
        return 'IE_BACKGROUND'
    return 'IE_UNKNOWN'


def departamento_da_evidencia(papel):
    if papel in (R_DIRECTION, R_WINDOW):
        return 'MARKET_DEVELOPMENT'
    if papel in (R_PRODUCT, R_COMMERCIAL):
        return 'PORTFOLIO'
    if papel in (R_CLOSES, R_CONTRADICTS, R_WEAKENS):
        return 'SCIENCE_TECHNICAL'
    if papel == R_SIGNAL:
        return 'SCIENCE_TECHNICAL'
    return None


def rotulo(cid):
    """O nome legível de um ID canônico — o PRIMEIRO termo do léxico.

    ⚠️ NÃO é tradução nem invenção: é o termo que o próprio léxico usa para
    reconhecer aquele ID nos documentos italianos, e é por ele que o ID existe.
    Se o léxico não conhece o ID, o rótulo É o ID — nunca um nome bonito
    escolhido aqui.

        NOME QUE NÃO SAI DO LÉXICO É NOME INVENTADO.
    """
    if not cid:
        return None
    for tab in (N.CROP_ALIAS, N.ISSUE_ALIAS, N.REGION_ALIAS):
        v = tab.get(cid)
        if v:
            return v[0]
    return cid


def briefing_curto(o, why_now, matches):
    n = len([m for m in matches if m['MATCH_STATE'] == M_VERIFIED])
    slots = {'CROP': o.get('CROP'), 'TARGET': o.get('TARGET'),
             'REGION': o.get('GEOGRAPHY'), 'PRODUCTS': n}
    labels = {'CROP': rotulo(o.get('CROP')), 'TARGET': rotulo(o.get('TARGET')),
              'REGION': rotulo(o.get('GEOGRAPHY')), 'PRODUCTS': n}
    ev = {'CROP': [o['NEED_EVIDENCE_ID']] if o.get('NEED_EVIDENCE_ID') else [],
          'TARGET': [o['NEED_EVIDENCE_ID']] if o.get('NEED_EVIDENCE_ID') else [],
          'REGION': [o['NEED_EVIDENCE_ID']] if o.get('NEED_EVIDENCE_ID') else [],
          'PRODUCTS': [i for m in matches if m['MATCH_STATE'] == M_VERIFIED
                       for i in m['EVIDENCE_IDS'][:1]]}
    if why_now == CLOSED:
        cod = 'BR_SOURCE_CLOSES'
    elif why_now == ACT_NOW:
        cod = 'BR_PRESSURE_WINDOW_PROVEN'
    elif why_now == VALIDATE_NOW:
        cod = 'BR_PRESSURE_WINDOW_UNPROVEN'
    elif why_now == WATCH:
        cod = 'BR_OPENING_WITHOUT_NEED'
    elif why_now == FUTURE:
        cod = 'BR_REGULATORY_HORIZON'
    else:
        cod = 'BR_UNKNOWN'
    usados = TEMPLATE[cod]['SLOTS']
    return {'TEMPLATE_CODE': cod,
            'SLOTS': {k: slots[k] for k in usados},
            'SLOT_LABELS': {k: labels[k] for k in usados},
            'SLOT_LABELS_LAW': 'o rotulo e o PRIMEIRO termo do lexico para aquele '
                               'ID canonico — o termo pelo qual o ID e '
                               'reconhecido nos documentos. Nao e traducao nem '
                               'nome escolhido aqui.',
            'SLOT_EVIDENCE_IDS': {k: ev.get(k, []) for k in usados}}


def razao_de_venda(o, why_now, cadeia, matches):
    """A frase curta e factual — ou UNKNOWN, e nunca uma frase plausível.

        CADA SEGMENTO DA FRASE TEM DE TER EVIDÊNCIA RASTREÁVEL.
    """
    if why_now in (ACT_NOW, VALIDATE_NOW) and cadeia['AGRONOMIC_NEED']['STATE'] == 'POSITIVE':
        b = briefing_curto(o, why_now, matches)
        return {'STATE': REASON_PROVEN, **b}
    return {'STATE': UNKNOWN, 'TEMPLATE_CODE': 'BR_UNKNOWN', 'SLOTS': {},
            'SLOT_LABELS': {}, 'SLOT_EVIDENCE_IDS': {}}


def main():
    global DATA_REF
    opp_pkg = json.load(open(os.path.join(ING, 'OPPORTUNITIES.json'), encoding='utf-8'))
    DATA_REF = opp_pkg.get('BUILT_AT')
    pares = _le('PRODUCT-RELATIONSHIPS.json')
    janelas = _le('CROP-WINDOWS.json')
    sinais = _le('CURRENT-FIELD-SIGNALS.json')

    reg_por_num = {CM.num(p.get('REGISTRATION_NUMBER')): p
                   for p in _le('PRODUCTS-REGULATORY.json')}
    ix_com = CM.indice_comercial(_le('PRODUCTS-COMMERCIAL.json'))
    ai_por_id = {a['ID']: a for a in _le('ACTIVE-INGREDIENTS.json')}
    ai_por_prod = {}
    for pai in _le('PRODUCT-ACTIVE-INGREDIENTS.json'):
        ai_por_prod.setdefault(CM.num(pai.get('REGISTRATION_NUMBER')), []).append(pai)

    # Índice de todos os registros citáveis como evidência.
    idx = {}
    for arq in sorted(os.listdir(ING)):
        if not arq.endswith('.json') or arq.startswith('CANONICAL'):
            continue
        d = json.load(open(os.path.join(ING, arq), encoding='utf-8'))
        for r in (d.get('RECORDS') or []):
            if isinstance(r, dict) and r.get('ID') and r['ID'] not in idx:
                idx[r['ID']] = r

    # A direção que CADA sinal declara para CADA par — pelo dono da regra.
    dir_por_sinal = {}
    for s in sinais:
        for p in NEC.pares_observados(s):
            dir_por_sinal[(s['ID'], p['CROP_ID'], p['ISSUE_ID'])] = p['NEED_DIRECTION']

    fichas = []
    for o in opp_pkg['RECORDS']:
        matches, so_cultura = portfolio(o, pares, reg_por_num, ix_com,
                                        ai_por_prod, ai_por_id, janelas)
        why_now, why_codes = por_que_agora(o)
        falta = o_que_falta(o, matches, why_now)
        cadeia, estado_razao, elos_faltando = cadeia_comercial(o, matches, why_now, falta)
        pm, pm_regra = principal(matches)

        evidencias = []
        for eid in (o.get('EVIDENCE_IDS') or []):
            ev = idx.get(eid)
            if not ev:
                continue
            papel = papel_da_evidencia(o, ev, dir_por_sinal)
            resumo = resumo_da_evidencia(papel, ev, dir_por_sinal, o)
            evidencias.append({
                'EVIDENCE_ID': eid,
                'ENTITY_TYPE': ev.get('ENTITY_TYPE'),
                'EVIDENCE_ROLE': papel,
                # ⚠️ A PROVA VIAJA INTEIRA. Nada aqui substitui o registro
                # original: URL, data, fonte e procedência vêm dele, e o texto
                # completo continua morando na coleção que o publicou.
                'SOURCE_IDS': ev.get('SOURCE_IDS') or [],
                'SOURCE_URLS': ev.get('SOURCE_URLS') or [],
                'REFERENCE_DATE': ev.get('REFERENCE_DATE'),
                'PROVENANCE': ev.get('PROVENANCE'),
                'ORIGINAL_RECORD_REF': {'COLLECTION_ID': ev.get('ENTITY_TYPE'),
                                        'RECORD_ID': eid},
                'INTELLIGENCE_HEADLINE_SLOTS': {'TARGET': o.get('TARGET'),
                                                'REGION': o.get('GEOGRAPHY')},
                'INTELLIGENCE_SUMMARY_CODE': resumo,
                'COMMERCIAL_IMPLICATION_CODE': IMPLICACAO_DO_PAPEL.get(papel, UNKNOWN),
                'DEPARTMENT_ACTION': departamento_da_evidencia(papel),
            })

        acoes = mapa_de_acao(o, why_now, falta)
        fichas.append(OrderedDict([
            ('ID', 'BRF_' + o['ID'][4:]),
            ('OPPORTUNITY_ID', o['ID']),
            ('ENTITY_TYPE', 'OPPORTUNITY_BRIEFING'),
            ('PROVENANCE', 'REAL_DERIVED'),
            ('QA_STATUS', 'EVIDENCE_DERIVED'),
            ('CLIENT_SAFE', False),
            ('WHY_NOT_CLIENT_SAFE', 'o briefing e leitura nossa sobre leitura '
                                    'nossa. A regra do CLIENT_SAFE vale para o '
                                    'que nos mesmos produzimos, ou nao e regra.'),
            ('SOURCE_IDS', o.get('SOURCE_IDS') or []),
            ('SOURCE_URLS', o.get('SOURCE_URLS') or []),
            ('REFERENCE_DATE', o.get('REFERENCE_DATE')),
            ('CROP_IDS', o.get('CROP_IDS') or []),
            ('ISSUE_IDS', o.get('ISSUE_IDS') or []),
            ('REGION_IDS', o.get('REGION_IDS') or []),
            ('GEOGRAPHIC_SCOPE', o.get('GEOGRAPHIC_SCOPE')),
            ('PUBLICATION_STATE', o.get('PUBLICATION_STATE')),
            ('WHAT_IS_HAPPENING', OrderedDict([
                ('CROP_ID', o.get('CROP')),
                ('ISSUE_ID', o.get('TARGET')),
                ('REGION_ID', o.get('GEOGRAPHY')),
                ('GEOGRAPHIC_SCOPE', o.get('GEOGRAPHIC_SCOPE')),
                ('SIGNAL_DATE', o.get('SIGNAL_DATE')),
                ('SIGNAL_AGE_DAYS', o.get('SIGNAL_AGE_DAYS')),
                ('DIRECTION', o.get('NEED_DIRECTION') or UNKNOWN),
                ('DIRECTION_EVIDENCE_ID', o.get('NEED_EVIDENCE_ID')),
                ('DIRECTION_METHOD', o.get('NEED_METHOD')),
                ('SOURCE_EXCERPT', o.get('NEED_EXCERPT') or ''),
                ('EVIDENCE_COUNT', o.get('EVIDENCE_COUNT')),
                ('EVIDENCE_FAMILIES', o.get('EVIDENCE_FAMILIES') or []),
                ('PUBLISHER_COUNT', len(o.get('SOURCE_IDS') or [])),
                ('SUMMARY', briefing_curto(o, why_now, matches)),
            ])),
            ('WHY_THIS_IS_A_COMMERCIAL_OPPORTUNITY', OrderedDict([
                ('COMMERCIAL_REASON_STATE', estado_razao),
                ('CHAIN', cadeia),
                ('MISSING_LINKS', elos_faltando),
                ('REASON_CODES', o.get('WHY_COMMERCIAL_CODES') or []),
                ('COMMERCIAL_PRIORITY', o.get('COMMERCIAL_PRIORITY')),
                ('OWNER', 'v21_comercial.prioridade()'),
            ])),
            ('WHY_NOW', why_now),
            ('WHY_NOW_CODES', why_codes),
            ('WHY_NOW_LAW', 'ACT_NOW exige janela de APLICACAO declarada. Sem ela, '
                            'um caso comercialmente pronto sai VALIDATE_NOW: '
                            'ACT_NOW NAO NASCE POR DEFAULT quando a janela e '
                            'UNKNOWN. Esta camada e estritamente mais conservadora '
                            'que COMMERCIAL_WINDOW e nunca mais permissiva.'),
            ('WINDOW', OrderedDict([
                ('STATE', o.get('WINDOW_STATE') or UNKNOWN),
                ('KIND', o.get('WINDOW_KIND')),
                ('FIELD', o.get('WINDOW_FIELD')),
                ('START', o.get('WINDOW_START')),
                ('END', o.get('WINDOW_END')),
                ('DAYS_REMAINING', o.get('DAYS_REMAINING')),
                ('COMMERCIAL_WINDOW', o.get('COMMERCIAL_WINDOW')),
                ('COMMERCIAL_WINDOW_FROM', o.get('COMMERCIAL_WINDOW_FROM')),
                ('OWNER', 'v21_oportunidades.janela()'),
            ])),
            ('PORTFOLIO_MATCHES', matches),
            ('PORTFOLIO_MATCH_COUNT', len(matches)),
            ('CROP_LEVEL_ONLY_COUNT', len(so_cultura)),
            ('CROP_LEVEL_ONLY_LAW', 'produtos com rotulo NESTA CULTURA e sem este '
                                    'ALVO no rotulo. Nao entram em '
                                    'PORTFOLIO_MATCHES porque autorizacao na '
                                    'cultura nao e autorizacao contra o alvo — '
                                    'mas o numero fica, para que a ausencia seja '
                                    'contada e nao escondida.'),
            ('PRIMARY_MATCH', pm),
            ('PRIMARY_MATCH_RULE', pm_regra),
            ('PRIMARY_MATCH_LAW', 'PRIMARY_MATCH so nasce quando ha UM produto '
                                  'simultaneamente com par de rotulo verificado, '
                                  'presente no catalogo publico e com a cultura '
                                  'declarada na propria pagina. Havendo zero ou '
                                  'mais de um: UNKNOWN. A ordem da lista e '
                                  'alfabetica e NAO significa escolha.'),
            ('SALES_REASON', razao_de_venda(o, why_now, cadeia, matches)),
            ('WHAT_IS_MISSING', falta),
            ('ACTION_MAP', acoes),
            ('ACTION_MAP_LAW', 'os departamentos vem do ACTION_MAP do motor de '
                               'oportunidades; o estado de cada um sai da matriz '
                               'departamento x WHY_NOW. Onde o dado nao sustenta '
                               'acao, o estado e UNKNOWN — nao se inventa '
                               'sequencia organizacional.'),
            ('EVIDENCES', evidencias),
            ('EVIDENCE_ROLE_LAW', 'nem toda evidencia serve para esquentar '
                                  'oportunidade. WEAKENS, CONTRADICTS e CLOSES '
                                  'sao papeis de primeira classe, e o registro '
                                  'que os exerce viaja com o caso.'),
            ('BRIEFING_DOES_NOT_PROVE', o.get('COMMERCIAL_DOES_NOT_PROVE')),
        ]))

    pacote = OrderedDict([
        ('COLLECTION', 'OPPORTUNITY_BRIEFINGS'),
        ('FILE', 'OPPORTUNITY-BRIEFINGS.json'),
        ('SCHEMA_VERSION', 'V2.1'),
        ('PRIMARY_KEY', 'ID'),
        ('SOURCE_OF_TRUTH', 'composicao sobre OPPORTUNITIES.json e as colecoes '
                            'de apoio. Nenhuma regua nova.'),
        ('COUNT_TOTAL', len(fichas)),
        ('COUNT_CLIENT_SAFE', 0),
        ('BY_WHY_NOW', dict(Counter(f['WHY_NOW'] for f in fichas))),
        ('BY_COMMERCIAL_REASON_STATE',
         dict(Counter(f['WHY_THIS_IS_A_COMMERCIAL_OPPORTUNITY']['COMMERCIAL_REASON_STATE']
                      for f in fichas))),
        ('BY_PRIMARY_MATCH_RULE', dict(Counter(f['PRIMARY_MATCH_RULE'] for f in fichas))),
        ('BY_EVIDENCE_ROLE', dict(Counter(e['EVIDENCE_ROLE'] for f in fichas
                                          for e in f['EVIDENCES']))),
        ('BY_ACTION_STATE', dict(Counter(a['ACTION_STATE'] for f in fichas
                                         for a in f['ACTION_MAP']))),
        ('BY_MISSING', dict(Counter(m for f in fichas for m in f['WHAT_IS_MISSING']))),
        ('PORTFOLIO_MATCHES_TOTAL', sum(f['PORTFOLIO_MATCH_COUNT'] for f in fichas)),
        ('WHY_NOW_STATES', list(WHY_NOW_STATES)),
        ('ACTION_STATES', list(ACTION_STATES)),
        ('EVIDENCE_ROLES', list(EVIDENCE_ROLES)),
        ('MATCH_STATES', list(MATCH_STATES)),
        ('DEPARTMENTS', list(DEPARTAMENTOS_DO_MODELO)),
        ('PHRASES', OrderedDict([
            ('WHY_NOW_CODE', dict(WHY_NOW_CODE)),
            ('WHAT_IS_MISSING', dict(FALTA)),
            ('ACTION_CODE', dict(ACAO)),
            ('NEXT_TRIGGER', dict(GATILHO)),
            ('INTELLIGENCE_SUMMARY_CODE', dict(RESUMO_EVIDENCIA)),
            ('COMMERCIAL_IMPLICATION_CODE', dict(IMPLICACAO)),
            ('BRIEFING_TEMPLATE', {k: v for k, v in TEMPLATE.items()}),
        ])),
        ('PHRASES_LAW', 'nenhum REGISTRO desta colecao carrega prosa: so codigo, '
                        'ID e numero. As frases vivem aqui, uma vez por codigo, e '
                        'os templates trazem marcador — nunca valor dentro da '
                        'frase. FRASE COM VARIAVEL DENTRO NUNCA FICA TRADUZIDA.'),
        ('LAW', 'esta camada NAO DECIDE NADA. Cada valor aponta para o dono da '
                'decisao que o produziu, e OWNER esta escrito ao lado dos campos '
                'derivados. O que e novo aqui e a COMPOSICAO: dizer se a cadeia '
                'PROBLEMA > NECESSIDADE > MOMENTO > PORTFOLIO > ACAO fecha, e '
                'qual elo faltou quando nao fecha. Sem prova: UNKNOWN.'),
        ('LOCALIZED_FIELDS', []),
        ('RECORDS', fichas),
    ])
    json.dump(pacote, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    print('== CONTRATO DE INTELIGENCIA COMERCIAL ==')
    print('fichas           : %d' % len(fichas))
    print('WHY_NOW          : %s' % pacote['BY_WHY_NOW'])
    print('razao comercial  : %s' % pacote['BY_COMMERCIAL_REASON_STATE'])
    print('PRIMARY_MATCH    : %s' % pacote['BY_PRIMARY_MATCH_RULE'])
    print('papeis de evid.  : %s' % pacote['BY_EVIDENCE_ROLE'])
    print('estados de acao  : %s' % pacote['BY_ACTION_STATE'])
    print('matches totais   : %d' % pacote['PORTFOLIO_MATCHES_TOTAL'])
    print('gravado: %s' % OUT)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
