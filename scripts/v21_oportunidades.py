#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O MOTOR DE OPORTUNIDADES · descobre convergências defensáveis no V2.1.

    python3 scripts/v21_oportunidades.py

O QUE HAVIA ANTES
-----------------
Nada. `OPPORTUNITIES.json` trazia três fichas escritas à mão, importadas inteiras
do handoff anterior (`LEGACY_CASE_ID: IT-HERO-00x`), e a evidência delas era
prosa — «ver 01-DESIGN-READY/MARKET-PULSE/». Nenhum ID canônico, nenhuma regra,
nenhum portão. As três nasceram antes de existirem 2.030 pares de rótulo, 53
substâncias ativas e 47 fatos regulatórios europeus.

    FICHA ESCRITA À MÃO NÃO É MOTOR: É LEMBRANÇA DE UMA LEITURA.

A LEI QUE GOVERNA ESTE ARQUIVO
------------------------------
Uma oportunidade é LEITURA NOSSA sobre fatos de terceiros. Vale aqui a mesma
regra que já governa os cruzamentos, e ela vale porque vale para o que nós mesmos
produzimos:

    CLIENT_SAFE = false, SEMPRE. RENDERABLE_WITH_METHOD diz o que vai à tela.

Isso não é rebaixamento: é o portão. O que separa CONFIRMADA de DA VALIDAR é
`OPPORTUNITY_STATE` — e uma confirmada exige que TODA a evidência que a sustenta
seja ela própria client-safe, e que os oito portões passem.

    CRUZAMENTO NÃO É OPORTUNIDADE, E OPORTUNIDADE NÃO É PEDIDO.
"""
import hashlib
import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V21 = os.path.join(ROOT, 'build', 'ITALY-REALITY-HANDOFF-V2.1')
ING = os.path.join(V21, 'DESIGN-INGEST')
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import v21_datas as DT  # noqa: E402
import v21_necessidade as NE  # noqa: E402
import v21_comercial as CM  # noqa: E402
import v21_janelas as JN  # noqa: E402

HOJE = date(2026, 9, 2)          # a data de referência do pacote, pinada
JANELA_FUTURA = 365              # dias à frente que ainda contam como "preparar"


def _le(arq):
    p = os.path.join(ING, arq)
    if not os.path.exists(p):
        return []
    return json.load(open(p, encoding='utf-8')).get('RECORDS') or []


def _ix(regs, campo):
    d = defaultdict(list)
    for r in regs:
        for v in (r.get(campo) or []):
            d[v].append(r)
    return d


# ── ARQUÉTIPOS ───────────────────────────────────────────────────────────────
# ⚠️ FRASE COM VARIAVEL DENTRO NUNCA FICA TRADUZIDA: e frase nova a cada build,
# e a memoria de traducao chaveia pelo texto. Ja aconteceu duas vezes nesta
# missao. Entao o texto de tela e FIXO por arquetipo, e os numeros vivem em
# campos estruturados ao lado.
#
#     O NUMERO E DADO. A FRASE E TEXTO. MISTURA-LOS PERDE OS DOIS.
TEXTO = {
 'O1_FIELD_PRESSURE': {
   'WHY_NOW': 'um boletim fitossanitario oficial registra este alvo nesta cultura, e '
              'existe rotulo ADAMA que nomeia a combinacao cultura x alvo.',
   'ADAMA': 'ha produtos ADAMA cuja combinacao cultura x alvo esta escrita no rotulo '
            'ministerial, e nao inferida.',
   'PROVA': 'que o alvo foi observado pelo servico fitossanitario e que existe '
            'autorizacao para trata-lo nesta cultura.',
   'NAO_PROVA': 'NAO prova incidencia, area afetada, nem que o produtor va tratar. '
                'Boletim e observacao do servico, nao censo do campo.'},
 'O2_MARKET_MOMENT': {
   'WHY_NOW': 'ha preco corrente ou peso economico medido para esta cultura, e a ADAMA '
              'tem rotulo nela.',
   'ADAMA': 'ha produtos ADAMA com rotulo ministerial nesta cultura.',
   'PROVA': 'que a cultura tem preco publicado ou area medida, e que ha portfolio nela.',
   'NAO_PROVA': 'NAO prova lucro do produtor, demanda nem intencao de compra. '
                'PRECO DE PIAZZA NAO E PRECO NACIONAL.'},
 'O3_RESISTANCE_MOA': {
   'WHY_NOW': 'ha resistencia documentada para este alvo e a ADAMA tem rotulo com modo '
              'de acao declarado na mesma combinacao.',
   'ADAMA': 'os produtos ADAMA desta combinacao tem modo de acao classificado por '
            'HRAC, IRAC ou FRAC.',
   'PROVA': 'que a resistencia foi registrada na literatura e que existem produtos com '
            'modo de acao declarado.',
   'NAO_PROVA': 'NAO prova que a resistencia esteja ocorrendo agora nesta regiao, nem '
                'que o produto ADAMA a resolva. RESISTENCIA DOCUMENTADA NAO E '
                'INCIDENCIA CORRENTE.'},
 'O4_COMPETITIVE_OPENING': {
   'WHY_NOW': 'ha pecas correntes de comunicacao de concorrente sobre esta cultura, e a '
              'ADAMA tem rotulo nela.',
   'ADAMA': 'a ADAMA tem produto autorizado na cultura de que o concorrente fala.',
   'PROVA': 'que houve comunicacao publica de concorrente sobre esta cultura.',
   'NAO_PROVA': 'ANUNCIO ALCANCOU NAO E ANUNCIO MIRAVA, e COMUNICACAO NAO E '
                'PARTICIPACAO DE MERCADO. NAO prova investimento, share nem resultado.'},
 'O5_REGULATORY_PREPARATION': {
   'WHY_NOW': 'a aprovacao europeia desta substancia tem data-limite publicada, e '
              'autorizacoes italianas da ADAMA a contem.',
   'ADAMA': 'produtos ADAMA registrados na Italia contem esta substancia ativa.',
   'PROVA': 'que existe uma data europeia publicada e quais produtos a contem.',
   'NAO_PROVA': 'EXPIRACAO DE APROVACAO NAO E NAO-RENOVACAO, NAO e risco e NAO e '
                'oportunidade. ESTADO EUROPEU NAO E COMERCIALIZABILIDADE ITALIANA.'},
 'O6_SCIENCE_TO_FIELD': {
   'WHY_NOW': 'ha ciencia registrada sobre esta cultura e sinal de campo corrente nela.',
   'ADAMA': 'a ADAMA tem rotulo ministerial nesta cultura.',
   'PROVA': 'que existe literatura sobre o tema e que houve observacao de campo.',
   'NAO_PROVA': 'ARTIGO CIENTIFICO NAO E PRESENCA NO CAMPO. NAO prova incidencia nem '
                'eficacia de produto.'},
}

ARQ = {
    'O1_FIELD_PRESSURE': 'pressao de campo corrente sobre cultura com janela e rotulo ADAMA',
    'O2_MARKET_MOMENT': 'sinal de mercado ou peso economico sobre cultura com portfolio ADAMA',
    'O3_RESISTANCE_MOA': 'resistencia documentada com relevancia de campo ou ciencia e MoA ADAMA',
    'O4_COMPETITIVE_OPENING': 'comunicacao corrente de concorrente sobre cultura onde a ADAMA tem rotulo',
    'O5_REGULATORY_PREPARATION': 'data regulatoria europeia sobre substancia que produtos ADAMA contem',
    'O6_SCIENCE_TO_FIELD': 'ciencia relevante com evidencia corrente de campo e relevancia ADAMA',
}

# Estados de relação com o produto, do mais forte ao mais fraco.
VERIFIED_LABEL_MATCH = 'VERIFIED_LABEL_MATCH'
RELATED_PORTFOLIO = 'RELATED_PORTFOLIO'
LABEL_CHECK_NEEDED = 'LABEL_CHECK_NEEDED'

CONFIRMADA = 'OPPORTUNITY_CONFIRMED'
CANDIDATA = 'OPPORTUNITY_CANDIDATE'
ROTULO = {CONFIRMADA: ('OPPORTUNITÀ CONFERMATA', 'CONFIRMED OPPORTUNITY'),
          CANDIDATA: ('OPPORTUNITÀ DA VALIDARE', 'OPPORTUNITY TO VALIDATE')}


def identidade(arquetipo, crop, alvo, geo, jan):
    """A identidade é determinística: mesma situação, mesma ficha.

        CINCO CARTOES DA MESMA SITUACAO NAO SAO CINCO OPORTUNIDADES.
    """
    chave = '|'.join([arquetipo, crop or 'NO_CROP', alvo or 'NO_TARGET',
                      geo or 'NO_GEO', jan or 'NO_WINDOW'])
    return 'OPP_' + hashlib.sha256(chave.encode()).hexdigest()[:12].upper(), chave


def data_do_sinal(regs):
    """A data do proprio documento e evidencia temporal.

    A janela de APLICACAO e prosa em quase todo o pacote, e nao se inventa uma.
    Mas um boletim fitossanitario publicado tem data, e essa data responde
    «isto e corrente?» — que e a pergunta do portao C. As duas coisas convivem:
    WINDOW_* diz quando se aplica; SIGNAL_DATE diz quando se observou.

        NAO SABER A JANELA DE APLICACAO NAO E NAO SABER SE O SINAL E DE HOJE.
    """
    melhor = None
    for r in regs:
        if r.get('ENTITY_TYPE') not in ('FIELD_SIGNAL', 'MARKET_OBSERVATION',
                                        'COMPETITOR_ACTIVITY', 'EVENT'):
            continue
        d = DT.analisar(('REFERENCE_DATE', r.get('REFERENCE_DATE')),
                        ('PUBLICATION_DATE', r.get('PUBLICATION_DATE')),
                        ('START_DATE', r.get('START_DATE')))
        if d['DATE_PARSE_STATE'] == DT.UNKNOWN:
            continue
        v = d['END_DATE'] or d['START_DATE']
        if v and (melhor is None or v > melhor):
            melhor = v
    if not melhor:
        return None, None
    return melhor, (HOJE - date.fromisoformat(melhor)).days


# Que PERGUNTA cada campo de janela responde. Não é o mesmo relógio.
#
# ⚠️ O DEFEITO QUE ISTO CONSERTA. A única janela que o parser conseguia ler em
# todo o pacote era `PREPARATION_WINDOW = «ate 2027-05-31, quando historicamente
# sai o ato»` — a data em que a região costuma PUBLICAR O DECRETO. Ela ia para
# `WINDOW_*`, cujo campo declara «é a janela de APLICAÇÃO», e daí saía o
# `FUTURE_PREPARATION` de casos de videira cuja pressão de campo é outra coisa.
#
#     DATA DE ATO NÃO É JANELA DE APLICAÇÃO.
#     QUANDO SAI O DECRETO E QUANDO SE PULVERIZA SÃO DOIS RELÓGIOS.
TIPO_DE_JANELA = {
    'APPLICATION_WINDOW_2026': 'APPLICATION',
    'REGULATORY_WINDOW': 'APPLICATION',      # «2 tratamentos, 1ª janela 08–19/06»
    'MONITORING_WINDOW': 'MONITORING',
    'NEXT_IMPORTANT_WINDOW': 'PREPARATION',
    'PREPARATION_WINDOW': 'PREPARATION',     # «quando historicamente sai o ato»
}


# ── A CHAVE MÍNIMA DO VÍNCULO DE JANELA ─────────────────────────────────────
#
# O índice era `{cultura: [janelas]}`. Cultura coincidia, e a janela era
# herdada: dezesseis casos de videira — Umbria, Toscana, Emilia-Romagna,
# Friuli — carregavam as janelas obrigatórias de *flavescenza dourada* do
# Veneto, da Lombardia e do Piemonte. Doze deles nem têm Scaphoideus como alvo.
#
#     UMA JANELA É DE UMA CULTURA, DE UM ALVO E DE UMA REGIÃO.
#     COINCIDIR NA CULTURA NÃO É SER A MESMA JANELA.
#
# A chave mínima não é escolha de estilo: é o conjunto de eixos que a evidência
# declarou. Onde o registro declarou alvo, o alvo entra na chave; onde declarou
# região, a região entra. E o que ele NÃO declarou não vira exigência inventada
# — uma janela sem região é nacional, e o nacional contém a região.
#
#     CONTER NÃO É CONTRADIZER. MAS COINCIDIR TAMBÉM NÃO É CONTER.
_SEM_VALOR = ('', 'NAO SEI', 'NÃO SEI', 'NENHUM', 'NENHUMA', 'N/A', 'NA')


def _declarado(v):
    """Prosa que nomeia alguma coisa — «NAO SEI» não nomeia."""
    return str(v or '').strip().upper() not in _SEM_VALOR


def janela_vale(w, crop, alvo, geo):
    """A janela vale para esta combinação? Só se ELA MESMA a declarar.

    ⚠️ `ISSUE_IDS` vazio com `ISSUE` escrito em prosa NÃO é curinga: é alvo que
    existe e não se sabe nomear. `IT-WIN-006` declara «Cocciniglie farinose» e
    não tem ID para elas — emprestar essa janela à botrite seria inventar.

        EIXO SEM IDENTIDADE NÃO É EIXO AUSENTE. É «NÃO SEI».
    """
    if crop not in (w.get('CROP_IDS') or []):
        return False
    alvos = w.get('ISSUE_IDS') or []
    if alvos:
        if alvo not in alvos:
            return False
    elif _declarado(w.get('ISSUE')):
        return False
    regioes = w.get('REGION_IDS') or []
    if regioes and geo not in regioes:
        return False
    return True


def janela(regs):
    """→ (inicio, fim, dias, estado, campo, tipo). Prosa nunca vira janela."""
    for r in regs:
        for campo in TIPO_DE_JANELA:
            d = DT.analisar((campo, r.get(campo)))
            if d['DATE_PARSE_STATE'] != DT.UNKNOWN:
                fim = date.fromisoformat(d['END_DATE'])
                return (d['START_DATE'], d['END_DATE'], (fim - HOJE).days,
                        d['DATE_PARSE_STATE'], campo, TIPO_DE_JANELA[campo])
    return (None, None, None, 'UNKNOWN', None, None)


def score(dim):
    """0–2 por dimensão, máximo 12. Ordena; não prova."""
    return sum(min(2, max(0, v)) for v in dim.values())


# ── O ESTADO DE AÇÃO, E A CADEIA QUE «AGORA» EXIGE ──────────────────────────
#
# O defeito medido: a tela mostrava, no MESMO cartão, `ACT NOW` e «no canonical
# window linked». Os dois vinham do mesmo motor. `ACT_NOW` estava sendo emitido
# a partir da IDADE DO SINAL — «o boletim é de ontem» — e não da existência de
# uma janela de aplicação.
#
#     A DATA DO BOLETIM DIZ QUE O SINAL É CORRENTE.
#     ELA NÃO DIZ QUANDO SE PULVERIZA. SÃO DOIS RELÓGIOS.
#
# `ACT_NOW` passa a exigir os QUATRO ELOS, e o cartão publica quais fecharam:
#
#     SINAL ATUAL + JANELA COMPATÍVEL + VÍNCULO COM PORTFÓLIO + TEMPO PARA AÇÃO
#
# Sem janela, o estado honesto NÃO é `WATCH` — o serviço mandou intervir, e
# ignorar isso seria outra mentira, de sinal contrário. É `VALIDATE_NOW`: há
# necessidade declarada e produto ligado, e o que falta é a janela desta região.
#
#     O QUE FALTA TEM NOME. «NÃO SEI» COM ENDEREÇO É TRABALHO; SEM ENDEREÇO,
#     É DESCULPA.
ACT_NOW = 'ACT_NOW'
PREPARE_NOW = 'PREPARE_NOW'
FUTURE_PREPARATION = 'FUTURE_PREPARATION'
VALIDATE_NOW = 'VALIDATE_NOW'
WATCH = 'WATCH'
TO_VALIDATE = 'TO_VALIDATE'

ESTADOS_DE_ACAO = (ACT_NOW, PREPARE_NOW, FUTURE_PREPARATION, VALIDATE_NOW,
                   WATCH, TO_VALIDATE)

# Quantos dias de sinal ainda contam como «corrente». É o mesmo corte que o
# portão C já usava para recusar caso sem tempo: não é limiar novo.
SINAL_CORRENTE_DIAS = 30
SINAL_RECENTE_DIAS = 120

ELOS = ('SINAL_ATUAL', 'JANELA_DEFINIDA', 'JANELA_ABERTA_AGORA',
        'VINCULO_COM_PORTFOLIO', 'TEMPO_PARA_ACAO')

ELO_EXIGE = {
    'SINAL_ATUAL': 'um sinal de campo datado nos ultimos %d dias, cuja direcao '
                   'declarada manda agir' % SINAL_CORRENTE_DIAS,
    'JANELA_DEFINIDA': 'a fonte declara QUAL condicao define o momento — '
                       'fenologia, pre-colheita, limiar, fase da praga, clima '
                       'ou datas — para esta cultura, este alvo e esta regiao',
    'JANELA_ABERTA_AGORA': 'ha evidencia de que essa condicao esta satisfeita '
                           'AGORA. Saber o gatilho nao e saber que ele disparou',
    'VINCULO_COM_PORTFOLIO': 'rotulo ministerial no par cultura x alvo E '
                             'produto no catalogo comercial',
    'TEMPO_PARA_ACAO': 'a janela de calendario ainda nao fechou e fecha dentro '
                       'de %d dias, OU a condicao esta aberta agora e o '
                       'documento que o diz e corrente' % SINAL_CORRENTE_DIAS,
}


def elos_de_agora(o):
    """→ {elo: bool}. A cadeia factual que `ACT_NOW` exige, elo a elo."""
    idade = o.get('SIGNAL_AGE_DAYS')
    dias = o.get('DAYS_REMAINING')
    corrente = idade is not None and idade <= SINAL_CORRENTE_DIAS
    aberta = o.get('WINDOW_OPEN_NOW') == 'YES'
    calendario = dias is not None and 0 <= dias <= SINAL_CORRENTE_DIAS
    return {
        'SINAL_ATUAL': (corrente
                        and o.get('NEED_DIRECTION') in CM.NECESSIDADE_POSITIVA),
        'JANELA_DEFINIDA': o.get('WINDOW_DEFINED') == 'YES',
        'JANELA_ABERTA_AGORA': aberta,
        'VINCULO_COM_PORTFOLIO': (bool(o.get('TARGET'))
                                  and o.get('PRODUCT_LINK_STATE') == VERIFIED_LABEL_MATCH
                                  and (o.get('COMMERCIAL_PRODUCT_COUNT') or 0) > 0),
        # ⚠️ Ha tempo para agir de duas maneiras, e as duas sao declaradas: uma
        # janela de calendario que ainda nao fechou, ou uma condicao satisfeita
        # AGORA num documento corrente. Nunca a idade do sinal sozinha.
        'TEMPO_PARA_ACAO': calendario or (aberta and corrente),
    }


def estado_de_acao(o):
    """→ (estado, elos). Nenhum estado sai de soma de pontos nem de idade so.

    ⚠️ A ORDEM É LEI, não estilo: quem manda PARAR é lido antes de qualquer
    coisa que mande agir, e a janela é lida antes da urgência.
    """
    elos = elos_de_agora(o)
    if o.get('ARCHETYPE') == 'O5_REGULATORY_PREPARATION':
        return FUTURE_PREPARATION, elos
    if all(elos.values()):
        return ACT_NOW, elos
    dias = o.get('DAYS_REMAINING')
    if elos['JANELA_DEFINIDA'] and dias is not None:
        if 0 <= dias <= SINAL_CORRENTE_DIAS:
            # a janela esta aberta mas falta outro elo: nao e «agora» ainda
            return VALIDATE_NOW if elos['VINCULO_COM_PORTFOLIO'] else WATCH, elos
        if SINAL_CORRENTE_DIAS < dias <= SINAL_RECENTE_DIAS:
            return PREPARE_NOW, elos
        if dias > SINAL_RECENTE_DIAS:
            return FUTURE_PREPARATION, elos
        return WATCH, elos                     # janela fechada
    # sem janela: o que falta tem nome
    if elos['SINAL_ATUAL'] and elos['VINCULO_COM_PORTFOLIO']:
        return VALIDATE_NOW, elos
    return WATCH, elos


# ── E · QUEM DENTRO DA ADAMA FAZ O QUÊ ──────────────────────────────────────
#
# Um mapa de departamentos que sempre chama todo mundo não é um mapa: é uma lista
# de e-mails. Cada departamento aqui só é convocado por um FATO, e o fato vai
# junto. `SUPPLY` é o caso mais estrito, e de propósito — convocar Supply sem
# base factual é a forma mais curta de transformar leitura externa em previsão
# de demanda, que é o que este motor nunca pode fazer.
#
#     PRESSÃO AGRONÔMICA NÃO É PEDIDO. CONVOCAR SUPPLY SEM FATO É INVENTAR UM.
DEPARTAMENTOS = ('MARKET_DEVELOPMENT', 'COMMERCIAL', 'MARKETING',
                 'TECHNICAL_SCIENTIFIC', 'SUPPLY')


def acao_por_departamento(o, elos):
    """→ {departamento: {ACTION, WHY_CODE}}. Código, nunca frase com variável."""
    tem_alvo = bool(o.get('TARGET'))
    externo = o.get('EXTERNAL_MATERIAL_READY')
    prioridade = o.get('COMMERCIAL_PRIORITY')
    faltam = [e for e in ELOS if not elos[e]]

    # ⚠️ A REGRA PODE JÁ TER RESPONDIDO «DECIDE O POMAR». Mandar Market
    # Development definir a condição regional, nesse caso, é mandá-lo procurar
    # o que a Regione publicou que não existe.
    delegada = o.get('WINDOW_RULE_STATE') == 'RULE_DELEGATED_TO_FARM'
    if delegada and elos['SINAL_ATUAL']:
        # a regra ja e conhecida — «medir no pomar». Mandar validar a condicao
        # NA REGIAO seria mandar procurar um gatilho regional que a propria
        # Regione declarou nao existir.
        md = ('VALIDATE_AT_FARM_LEVEL', 'REGRA_DELEGADA_AO_POMAR')
    elif not elos['JANELA_DEFINIDA'] and elos['SINAL_ATUAL']:
        md = ('DEFINE_WINDOW_CONDITION', 'SEM_CONDICAO_DECLARADA')
    elif not elos['JANELA_ABERTA_AGORA'] and elos['SINAL_ATUAL']:
        md = ('VALIDATE_WINDOW_IN_REGION', 'CONDICAO_DECLARADA_ESTADO_DESCONHECIDO')
    elif elos['SINAL_ATUAL'] and tem_alvo:
        md = ('CONFIRM_RECOMMENDATION_IN_FIELD', 'SINAL_ATUAL_COM_ALVO')
    else:
        md = ('NO_MOVEMENT', 'SEM_SINAL_ATUAL')

    if o.get('STATUS') == ACT_NOW:
        com = ('CONTACT_NOW', 'CADEIA_COMPLETA')
    elif o.get('STATUS') == PREPARE_NOW:
        com = ('PREPARE', 'JANELA_FUTURA')
    elif prioridade in ('SALES_READY', 'SALES_PREPARE'):
        com = ('PREPARE', 'PRIORIDADE_COMERCIAL_SEM_TEMPO_PROVADO')
    else:
        com = ('NO_MOVEMENT', 'SEM_PRIORIDADE_COMERCIAL')

    if externo == 'YES':
        mkt = ('MESSAGE_AVAILABLE', 'EXTERNAL_MATERIAL_READY')
    elif externo == 'VALIDATION_REQUIRED':
        mkt = ('PREPARE_INTERNAL_ONLY', 'EXTERNAL_BLOCKED')
    else:
        mkt = ('NO_MOVEMENT', 'NAO_AUTORIZADO_A_SAIR')

    if delegada:
        tec = ('CONFIRM_AT_FARM_LEVEL', 'REGRA_DELEGADA_AO_POMAR')
    elif not elos['JANELA_DEFINIDA']:
        tec = ('ESTABLISH_WINDOW_CONDITION', 'SEM_CONDICAO_DECLARADA')
    elif not elos['JANELA_ABERTA_AGORA']:
        tec = ('CONFIRM_WINDOW_CONDITION_MET',
               'CONDICAO_DECLARADA_ESTADO_DESCONHECIDO')
    elif o.get('NEED_AMBIGUITY_CODES'):
        tec = ('RESOLVE_AMBIGUOUS_DIRECTION', 'DIRECAO_AMBIGUA')
    elif o.get('MODE_OF_ACTION_STATE') != 'CLASSIFIED':
        tec = ('CLASSIFY_MODE_OF_ACTION', 'MOA_NAO_CLASSIFICADO')
    else:
        tec = ('NO_MOVEMENT', 'NADA_A_VALIDAR')

    # ⚠️ SUPPLY só entra com fato publicado. Não existe «demanda esperada» aqui.
    if o.get('PRODUCT_RESTRICTIONS'):
        sup = ('WATCH_REGULATORY_DATE', 'DATA_REGULATORIA_EM_ATIVO_LIGADO')
    else:
        sup = ('NOT_CONVENED', 'SEM_BASE_FACTUAL')

    par = dict(zip(DEPARTAMENTOS, (md, com, mkt, tec, sup)))
    # ── o estado da acao, a dependencia e o que a destravaria ────────────────
    # Um mapa que so diz «o que fazer» nao diz quando parar de esperar. Cada
    # linha carrega de que elo ela depende e qual evento a muda.
    ESTADO = {'CONTACT_NOW': 'ACT', 'MESSAGE_AVAILABLE': 'ACT',
              'VALIDATE_WINDOW_IN_REGION': 'VALIDATE',
              'DEFINE_WINDOW_CONDITION': 'VALIDATE',
              'CONFIRM_RECOMMENDATION_IN_FIELD': 'VALIDATE',
              'ESTABLISH_WINDOW_CONDITION': 'VALIDATE',
              'VALIDATE_AT_FARM_LEVEL': 'VALIDATE',
              'CONFIRM_AT_FARM_LEVEL': 'VALIDATE',
              'CONFIRM_WINDOW_CONDITION_MET': 'VALIDATE',
              'RESOLVE_AMBIGUOUS_DIRECTION': 'VALIDATE',
              'CLASSIFY_MODE_OF_ACTION': 'VALIDATE',
              'PREPARE': 'PREPARE', 'PREPARE_INTERNAL_ONLY': 'PREPARE',
              'WATCH_REGULATORY_DATE': 'WATCH',
              'NO_MOVEMENT': 'NO_ACTION', 'NOT_CONVENED': 'NO_ACTION'}
    GATILHO = {
        'JANELA_DEFINIDA': (
            'a observacao do proprio pomar — a regra regional declara que a '
            'decisao e da empresa, e por isso nao ha gatilho regional para '
            'esperar' if delegada else
            'uma fonte que declare a condicao do momento para este par nesta '
            'regiao'),
        'JANELA_ABERTA_AGORA': 'evidencia de que a condicao declarada esta '
                               'satisfeita agora — estadio, limiar medido, '
                               'captura ou evento climatico',
        'SINAL_ATUAL': 'um boletim novo que declare necessidade positiva',
        'VINCULO_COM_PORTFOLIO': 'rotulo ministerial no par e produto no '
                                 'catalogo comercial',
        'TEMPO_PARA_ACAO': 'a janela abrir, ou a condicao ser confirmada',
    }
    prova = {
        'MARKET_DEVELOPMENT': [o.get('NEED_EVIDENCE_ID'), o.get('WINDOW_EVIDENCE_ID')],
        'COMMERCIAL': (o.get('MATCHED_COMMERCIAL_PRODUCT_IDS') or [])[:3],
        'MARKETING': [o.get('NEED_EVIDENCE_ID')],
        'TECHNICAL_SCIENTIFIC': [o.get('WINDOW_EVIDENCE_ID'), o.get('NEED_EVIDENCE_ID')],
        'SUPPLY': [f.get('EVIDENCE_ID') for f in (o.get('PRODUCT_RESTRICTIONS') or [])],
    }
    fora = {}
    for d, (a, w) in par.items():
        dep_elo = faltam[0] if faltam else None
        fora[d] = {'DEPARTMENT': d, 'ACTION_STATE': ESTADO.get(a, 'UNKNOWN'),
                   'ACTION': a, 'WHY_CODE': w,
                   'EVIDENCE': [x for x in prova.get(d, []) if x],
                   'DEPENDENCY': dep_elo,
                   'NEXT_TRIGGER': GATILHO.get(dep_elo) if dep_elo else None,
                   'MISSING_LINKS': faltam}
    return fora


# ── J · O PAPEL DE CADA EVIDÊNCIA, INCLUSIVE A QUE ESFRIA ───────────────────
#
# Um sistema que só classifica evidência a favor aprende a vender. O papel
# negativo é dado, e fica.
#
#     UMA EVIDÊNCIA PODE ESFRIAR UMA OPORTUNIDADE, E ISSO TAMBÉM É INTELIGÊNCIA.
PAPEIS = ('SUPPORTS_SIGNAL', 'SUPPORTS_DIRECTION', 'SUPPORTS_WINDOW',
          'SUPPORTS_PRODUCT_MATCH', 'SUPPORTS_REGIONAL_CONTEXT',
          'SUPPORTS_COMMERCIAL_ACTION', 'WEAKENS', 'CONTRADICTS', 'CLOSES',
          'BACKGROUND_ONLY', 'UNKNOWN')


def papel_das_evidencias(o, apoios):
    """→ [{EVIDENCE_ID, ENTITY_TYPE, ROLE, WHY_CODE}]. Uma linha por apoio."""
    fora = []
    for a in apoios:
        tipo = a.get('ENTITY_TYPE')
        if a['ID'] == o.get('NEED_EVIDENCE_ID'):
            papel, por = 'SUPPORTS_DIRECTION', 'FRASE_QUE_DECIDIU_A_DIRECAO'
        elif a['ID'] == o.get('WINDOW_EVIDENCE_ID'):
            papel, por = 'SUPPORTS_WINDOW', 'DECLARA_A_CONDICAO_DA_JANELA'
        elif tipo == 'LABEL_USE_RELATIONSHIP':
            papel, por = 'SUPPORTS_PRODUCT_MATCH', 'ROTULO_MINISTERIAL_NO_PAR'
        elif tipo == 'CROP_WINDOW':
            papel, por = 'BACKGROUND_ONLY', 'REGISTRO_DE_JANELA_SEM_DATA_APLICAVEL'
        elif tipo == 'FIELD_SIGNAL':
            papel, por = 'SUPPORTS_SIGNAL', 'OBSERVACAO_DE_CAMPO_NA_MESMA_REGIAO'
        elif tipo in ('MARKET_OBSERVATION', 'CROP_ECONOMIC_WEIGHT_CLAIM'):
            papel, por = 'SUPPORTS_REGIONAL_CONTEXT', 'CONTEXTO_DE_MERCADO'
        elif tipo == 'COMPETITOR_ACTIVITY':
            papel, por = 'SUPPORTS_COMMERCIAL_ACTION', 'MOVIMENTO_DE_CONCORRENTE'
        else:
            papel, por = 'BACKGROUND_ONLY', 'NAO_DECIDE_NENHUM_ELO'
        fora.append({'EVIDENCE_ID': a['ID'], 'ENTITY_TYPE': tipo,
                     'ROLE': papel, 'WHY_CODE': por})
    return fora


# ── E · O PORTFÓLIO, PRODUTO A PRODUTO ──────────────────────────────────────
#
# «Existem produtos ADAMA» não é um vínculo: é uma lista. Cada produto responde
# por si, e o que não se sabe dele aparece nele.
#
#     PRIMARY_MATCH NÃO É O PRIMEIRO DA LISTA. SEM REGRA DEFENSÁVEL, É UNKNOWN.
def portfolio(o, rotulos, casados, ai_por_prod, ai_por_id, ativos_da_fonte):
    """→ (matches, PRIMARY_MATCH, razão do primário)."""
    por_reg = defaultdict(list)
    for r in rotulos:
        por_reg[CM.num(r.get('REGISTRATION_NUMBER'))].append(r)
    fora = []
    for p in casados:
        reg = CM.num(p.get('MATCHED_REGULATORY_ID'))
        rots = por_reg.get(reg, [])
        ativos = [ai_por_id.get(x.get('ACTIVE_INGREDIENT_ID'))
                  for x in ai_por_prod.get(reg, [])]
        ativos = [a for a in ativos if a]
        declara = CM.catalogo_declara_cultura(o.get('CROP'), [p])[0]
        restr = [{'CODE': 'EU_APPROVAL_EXPIRES', 'ACTIVE_INGREDIENT': a.get('NAME'),
                  'DATE': a.get('EU_EXPIRATION_OF_APPROVAL'), 'EVIDENCE_ID': a['ID']}
                 for a in ativos if a.get('EU_EXPIRATION_OF_APPROVAL')]
        nomeado = [a['NAME'] for a in ativos
                   if a.get('NAME') and a['NAME'].upper() in ativos_da_fonte]
        fora.append({
            'PRODUCT_ID': p['ID'], 'PRODUCT_NAME': p.get('NAME'),
            'REGISTRATION_NUMBER': reg,
            'ACTIVE_INGREDIENTS': [a.get('NAME') for a in ativos],
            'MODE_OF_ACTION': sorted({'FRAC ' + str(a['FRAC']) for a in ativos
                                      if a.get('FRAC')} |
                                     {'IRAC ' + str(a['IRAC']) for a in ativos
                                      if a.get('IRAC')} |
                                     {'HRAC ' + str(a['HRAC']) for a in ativos
                                      if a.get('HRAC')}),
            'CROP_FIT': 'DECLARED_ON_CATALOG_PAGE' if declara else 'UNKNOWN',
            'TARGET_FIT': 'ON_MINISTERIAL_LABEL' if rots else 'UNKNOWN',
            'REGIONAL_FIT': 'NATIONAL_AUTHORIZATION_CONTAINS_REGION',
            'REGULATORY_FIT': 'AUTHORIZATION_LIVE' if reg else 'UNKNOWN',
            'WINDOW_FIT': o.get('WINDOW_OPEN_NOW') or 'UNKNOWN',
            'VALIDATION_STATE': ('LABEL_AND_CATALOG' if rots and declara
                                 else 'LABEL_ONLY' if rots else 'CATALOG_ONLY'),
            'EVIDENCE': [r['ID'] for r in rots[:4]] + [p['ID']],
            'RESTRICTIONS': restr,
            'SOURCE_NAMES_THIS_ACTIVE': nomeado,
            'MATCH_REASON': 'REGISTRATION_NUMBER_JOIN',
        })
    fora.sort(key=lambda m: str(m['PRODUCT_NAME']))
    # ⚠️ A REGRA DO PRIMÁRIO, E SÓ ELA: a fonte nomeou a substância, ou há um só.
    nomeados = [m for m in fora if m['SOURCE_NAMES_THIS_ACTIVE']]
    if len(nomeados) == 1:
        return fora, nomeados[0]['PRODUCT_ID'], 'FONTE_NOMEIA_A_SUBSTANCIA'
    if len(fora) == 1:
        return fora, fora[0]['PRODUCT_ID'], 'UNICO_PRODUTO_DO_CATALOGO_NO_PAR'
    return fora, None, 'SEM_REGRA_DEFENSAVEL_PARA_ESCOLHER'


# ── D e I · O BRIEFING, EM PEDAÇOS FIXOS COM VALOR AO LADO ──────────────────
#
# O briefing é frase, e frase com variável dentro nunca fica traduzida. Então o
# texto é FIXO e os valores vivem fora dele, em `VALUES`. A tela compõe.
#
#     A FRASE É A MESMA EM TODO BUILD. O QUE MUDA É O QUE ENTRA NELA.
BRIEFING = {
 'PRESSAO_RECENTE': 'Pressão recente de {ALVO} em {CULTURA} na {REGIAO}, '
                    'sustentada por {SINAIS} sinais de campo e {FONTES} fontes '
                    'independentes.',
 'FONTE_MANDA_PARAR': 'A fonte que sustenta o par não manda agir: ver '
                      'NEED_DIRECTION e a frase original.',
 'JANELA_ABERTA': 'A condição que define o momento está declarada e o mesmo '
                  'documento declara o estádio da cultura: a janela está aberta '
                  'agora.',
 'JANELA_DEFINIDA_ESTADO_DESCONHECIDO': 'A condição que define o momento está '
                                        'declarada, mas não há evidência de que '
                                        'esteja satisfeita agora.',
 'SEM_JANELA': 'Nenhuma fonte declara a condição que define o momento de '
               'intervir neste par e nesta região.',
 'JANELA_DELEGADA_AO_POMAR': 'A regra regional publicada declara que a decisão '
                             'de intervir é da própria empresa, pelas '
                             'observações e pelo histórico do pomar: não há '
                             'gatilho regional a coletar.',
 'PORTFOLIO': 'Há {PRODUTOS} produto(s) do catálogo comercial ADAMA com rótulo '
              'ministerial no par.',
 'SEM_PORTFOLIO': 'Nenhum produto do catálogo comercial ADAMA cobre este par '
                  'com rótulo ministerial.',
 'FONTE_NOMEIA_OUTRA_SUBSTANCIA': 'A fonte nomeia {ATIVOS_DA_FONTE} como '
                                  'solução; a substância do produto ADAMA '
                                  'ligado ao par é outra.',
 'ACAO_PRINCIPAL': 'Ação: {DEPARTAMENTO} deve {ACAO} antes de qualquer ativação '
                   'comercial.',
}


def briefing(o, matches, ativos_da_fonte):
    """→ [{CODE, VALUES}]. Nunca a frase pronta: o código e os valores."""
    b = []
    dim = o.get('COMMERCIAL_MAGNITUDE_DIMENSIONS') or {}
    if o.get('NEED_DIRECTION') in CM.NECESSIDADE_FECHADA:
        b.append({'CODE': 'FONTE_MANDA_PARAR', 'VALUES': {}})
    elif o.get('TARGET'):
        b.append({'CODE': 'PRESSAO_RECENTE', 'VALUES': {
            'ALVO': o['TARGET'], 'CULTURA': o['CROP'], 'REGIAO': o['GEOGRAPHY'],
            'SINAIS': dim.get('SINAIS_DE_CAMPO'),
            'FONTES': dim.get('FONTES_INDEPENDENTES')}})
    if o.get('WINDOW_RULE_STATE') == 'RULE_DELEGATED_TO_FARM':
        b.append({'CODE': 'JANELA_DELEGADA_AO_POMAR', 'VALUES': {}})
    elif o.get('WINDOW_DEFINED') != 'YES':
        b.append({'CODE': 'SEM_JANELA', 'VALUES': {}})
    elif o.get('WINDOW_OPEN_NOW') == 'YES':
        b.append({'CODE': 'JANELA_ABERTA', 'VALUES': {}})
    else:
        b.append({'CODE': 'JANELA_DEFINIDA_ESTADO_DESCONHECIDO', 'VALUES': {}})
    if matches:
        b.append({'CODE': 'PORTFOLIO', 'VALUES': {'PRODUTOS': len(matches)}})
        if ativos_da_fonte and not any(m['SOURCE_NAMES_THIS_ACTIVE']
                                       for m in matches):
            b.append({'CODE': 'FONTE_NOMEIA_OUTRA_SUBSTANCIA',
                      'VALUES': {'ATIVOS_DA_FONTE': sorted(ativos_da_fonte)}})
    else:
        b.append({'CODE': 'SEM_PORTFOLIO', 'VALUES': {}})
    dep = o.get('ACTION_BY_DEPARTMENT') or {}
    principal = next(((d, v) for d, v in dep.items()
                      if v.get('ACTION_STATE') in ('VALIDATE', 'ACT')), None)
    if principal:
        b.append({'CODE': 'ACAO_PRINCIPAL', 'VALUES': {
            'DEPARTAMENTO': principal[0], 'ACAO': principal[1]['ACTION']}})
    return b


def cadeia_de_agora(o, elos, apoios):
    """→ (codigos, cadeia). Obrigatorio para ACT_NOW; util para os outros.

    A cadeia nomeia o QUE sustenta cada elo, com identificador — nao com
    adjetivo. Um `ACT_NOW` sem cadeia completa nao existe.
    """
    janela = [a['ID'] for a in apoios if a.get('ENTITY_TYPE') == 'CROP_WINDOW']
    sinais = [a['ID'] for a in apoios if a.get('ENTITY_TYPE') == 'FIELD_SIGNAL']
    cadeia = {
        'SINAL_ATUAL': {'OK': elos['SINAL_ATUAL'],
                        'EVIDENCE': ([o['NEED_EVIDENCE_ID']]
                                     if o.get('NEED_EVIDENCE_ID') else sinais[:3]),
                        'FACT': o.get('SIGNAL_DATE')},
        'JANELA_DEFINIDA': {'OK': elos['JANELA_DEFINIDA'],
                            'EVIDENCE': ([o['WINDOW_EVIDENCE_ID']]
                                         if o.get('WINDOW_EVIDENCE_ID')
                                         else janela[:3]),
                            'FACT': o.get('WINDOW_TYPE') or o.get('WINDOW_FIELD')},
        'JANELA_ABERTA_AGORA': {'OK': elos['JANELA_ABERTA_AGORA'],
                                'EVIDENCE': ([o['WINDOW_EVIDENCE_ID']]
                                             if o.get('WINDOW_EVIDENCE_ID')
                                             else janela[:3]),
                                'FACT': o.get('WINDOW_OPEN_NOW_METHOD')},
        'VINCULO_COM_PORTFOLIO': {'OK': elos['VINCULO_COM_PORTFOLIO'],
                                  'EVIDENCE': o.get('MATCHED_COMMERCIAL_PRODUCT_IDS') or [],
                                  'FACT': o.get('PRODUCT_LINK_STATE')},
        'TEMPO_PARA_ACAO': {'OK': elos['TEMPO_PARA_ACAO'],
                            'EVIDENCE': janela[:3],
                            'FACT': o.get('DAYS_REMAINING')},
    }
    faltam = ['SEM_' + e for e in ELOS if not elos[e]]
    return (['CADEIA_COMPLETA'] if not faltam else faltam), cadeia


# Quem OBSERVA um fato no mundo, e por isso responde pela geografia da
# afirmação. O rótulo, o registro e a substância ativa não observam nada: eles
# dizem o que é permitido, e a permissão é nacional por construção.
TIPOS_QUE_OBSERVAM = ('FIELD_SIGNAL', 'MARKET_OBSERVATION', 'COMPETITOR_ACTIVITY',
                      'EVENT', 'PUBLIC_VOICE', 'SCIENTIFIC_RECORD',
                      'RESISTANCE_RECORD', 'CROP_ECONOMIC_WEIGHT_CLAIM',
                      'AGROMET_CONDITION', 'NEWS_ITEM', 'CROP_WINDOW')

# E quem só declara AUTORIZAÇÃO. A geografia destes vive à parte, em
# PRODUCT_AUTHORIZATION_GEOGRAPHY, e nunca entra no portão A.
TIPOS_DE_AUTORIZACAO = ('LABEL_USE_RELATIONSHIP', 'REGULATORY_PRODUCT',
                        'ACTIVE_INGREDIENT', 'REGULATORY_FUTURE_FACT',
                        'COMMERCIAL_PRODUCT')


# ── OS OITO PORTÕES DA CONFIRMAÇÃO ───────────────────────────────────────────
def portoes(o, ev):
    """A–H. Devolve a lista dos que FALHARAM. Score alto não abre portão.

        UM 12 COM PORTAO FECHADO CONTINUA SENDO UM 12 COM PORTAO FECHADO.
    """
    f = []
    # ⚠️ D2 · A GEOGRAFIA DA AFIRMACAO NAO SE MISTURA COM A DA AUTORIZACAO.
    # A versao anterior somava os REGION_IDS de TODOS os apoios. O sinal de campo
    # e regional (REGION_VENETO); o rotulo ministerial e GEO_ITALY, porque a
    # autorizacao vale no pais inteiro. Duas geografias, caso regional, portao
    # fechado por «geografias que nao se contem» — e sete casos O1 regionais e
    # provinciais caiam por causa da propria autorizacao que os tornava vendaveis.
    #
    #     ROTULO NACIONAL CONTEM A REGIAO. CONTER NAO E CONTRADIZER.
    #
    # Quem responde pela geografia da AFIRMACAO e quem OBSERVOU o fato. O rotulo
    # responde outra pergunta — «onde e permitido usar» — e essa resposta vive em
    # PRODUCT_AUTHORIZATION_GEOGRAPHY, ao lado, sem votar aqui.
    geos = {g for e in ev if e.get('ENTITY_TYPE') in TIPOS_QUE_OBSERVAM
            for g in (e.get('REGION_IDS') or [])}
    # A · geografia compatível: nenhum apoio pode falar por região que não é dele
    if any(e.get('REGION_REPRESENTS') is False and o['GEOGRAPHY_SCOPE'] == 'REGIONAL'
           for e in ev):
        f.append('A_GEOGRAFIA · apoio provincial sustentando alegacao regional')
    if len(geos) > 1 and o['GEOGRAPHY'] not in ('GEO_ITALY', 'GEO_EU') and \
            not geos <= {o['GEOGRAPHY']}:
        f.append('A_GEOGRAFIA · apoios em geografias que nao se contem')
    # B · identidade de cultura
    crops = {c for e in ev for c in (e.get('CROP_IDS') or [])}
    if o['CROP'] and crops and o['CROP'] not in crops:
        f.append('B_CULTURA · a cultura do caso nao aparece nos apoios')
    # C · tempo: janela de aplicacao OU sinal datado e recente
    if o['ARCHETYPE'] != 'O5_REGULATORY_PREPARATION' and \
            o['WINDOW_STATE'] == 'UNKNOWN' and \
            (o['SIGNAL_AGE_DAYS'] is None or o['SIGNAL_AGE_DAYS'] > 120):
        f.append('C_TEMPO · sem janela defensavel e sem sinal datado nos ultimos 120 dias')
    # D · problema agronômico evidenciado
    if o['ARCHETYPE'] in ('O1_FIELD_PRESSURE', 'O3_RESISTANCE_MOA', 'O6_SCIENCE_TO_FIELD') \
            and not o['TARGET']:
        f.append('D_PROBLEMA · sem alvo agronomico declarado')
    # E · relação ADAMA evidenciada
    if o['PRODUCT_LINK_STATE'] == LABEL_CHECK_NEEDED:
        f.append('E_ADAMA · rotulo por verificar (LABEL_CHECK_NEEDED)')
    if o['PRODUCT_LINK_STATE'] == RELATED_PORTFOLIO and o['ARCHETYPE'] != 'O5_REGULATORY_PREPARATION':
        f.append('E_ADAMA · so RELATED_PORTFOLIO nao confirma oportunidade comercial')
    # F · procedência resolvível
    sem = [e['ID'] for e in ev if not e.get('SOURCE_URLS')
           and e.get('PROVENANCE_STATE') == 'UNRECOVERABLE']
    if sem:
        f.append('F_PROCEDENCIA · apoio sem origem recuperavel: %s' % ', '.join(sem[:3]))
    # G · contradição
    if o['CROP'] and any(e.get('CROP_IDS') and o['CROP'] not in e['CROP_IDS']
                         and e.get('ENTITY_TYPE') == 'FIELD_SIGNAL' for e in ev):
        f.append('G_CONTRADICAO · sinal de campo de outra cultura no mesmo caso')
    # H · a leitura não pode exceder a evidência
    if any(not e.get('CLIENT_SAFE') for e in ev):
        f.append('H_EXCESSO · apoio que nao passou no portao de QA')
    return f


# ── O QUE O RED TEAM PODE LER ────────────────────────────────────────────────
# Os campos em que o caso AFIRMA alguma coisa. O red team procura extrapolacao
# aqui, e so aqui.
CAMPOS_AFIRMADOS = ('WHY_NOW', 'ADAMA_RELEVANCE', 'WHAT_IT_PROVES',
                    'CROP', 'TARGET', 'GEOGRAPHY', 'STATUS',
                    'PRODUCT_LINK_STATE', 'PRODUCT_RELATIONSHIPS')

# E os que o red team NAO pode ler, porque nao sao afirmacao do caso:
#   WHAT_IT_DOES_NOT_PROVE  a advertencia contra o erro
#   *_LAW, *_MEANS          texto metodologico e as proprias regras
#   BLOCKING_GATES          o resultado dos portoes
#   SCORE_*, NUMBERS        aritmetica


def _texto_afirmado(o):
    """So o que o caso AFIRMA — nunca a advertencia contra o proprio erro.

    ⚠️ O DEFEITO QUE ISTO CONSERTA (D1). A regra de extrapolacao de participacao
    de mercado rodava sobre `json.dumps(o)`, e `o` ja carregava
    `WHAT_IT_DOES_NOT_PROVE`, que e a frase FIXA do arquetipo O4 e diz
    «COMUNICACAO NAO E PARTICIPACAO DE MERCADO. NAO prova investimento, share nem
    resultado.» A regex casava com o proprio aviso, e os nove casos O4 ficavam
    inconfirmaveis por construcao — nenhum deles por merito.

        O AVISO CONTRA UM ERRO NAO E O ERRO.
        QUEM MEDE O PROPRIO TEXTO MEDE A SI MESMO.
    """
    partes = []
    for k in CAMPOS_AFIRMADOS:
        v = o.get(k)
        if isinstance(v, (list, tuple)):
            partes.extend(str(x) for x in v)
        elif v is not None:
            partes.append(str(v))
    return ' | '.join(partes)


# ── O RED TEAM ───────────────────────────────────────────────────────────────
def red_team(o, ev):
    """Nove perguntas, cada uma um defeito que este projeto ja cometeu."""
    m = []
    t = {e['ID']: e for e in ev}
    if len(ev) == 1:
        m.append('artefato de fonte unica: um documento nao e convergencia')
    if len({e.get('SOURCE_DOCUMENT_ID') or (e.get('SOURCE_URLS') or [None])[0]
            for e in ev} - {None}) < 2 and len(ev) > 1:
        m.append('todos os apoios saem do MESMO documento')
    if any(e.get('REGION_REPRESENTS') is False for e in ev) and \
            o['GEOGRAPHY_SCOPE'] in ('REGIONAL', 'NACIONAL'):
        m.append('geografia promovida: apoio provincial em alegacao mais ampla')
    if any(e.get('COMMODITY_STAGE') == 'PROCESSED_PRODUCT' for e in ev):
        m.append('preco de produto processado sustentando mercado da cultura')
    if o['ARCHETYPE'] == 'O5_REGULATORY_PREPARATION' and o['STATUS'] == 'ACT_NOW':
        m.append('data regulatoria virou urgencia')
    if any(e.get('ENTITY_TYPE') == 'COMPETITOR_ACTIVITY' for e in ev) and \
            re.search(r'share|participac|quota', _texto_afirmado(o), re.I):
        m.append('comunicacao de concorrente virou participacao de mercado')
    if o['ARCHETYPE'] == 'O3_RESISTANCE_MOA' and not any(
            e.get('ENTITY_TYPE') == 'FIELD_SIGNAL' for e in ev):
        m.append('resistencia documentada sem sinal de campo corrente: nao e incidencia')
    if o['PRODUCT_LINK_STATE'] != VERIFIED_LABEL_MATCH and \
            o['OPPORTUNITY_STATE'] == CONFIRMADA:
        m.append('relacao de portfolio tratada como verificacao de rotulo')
    if o['ARCHETYPE'] == 'O6_SCIENCE_TO_FIELD' and not any(
            e.get('ENTITY_TYPE') == 'FIELD_SIGNAL' for e in ev):
        m.append('artigo cientifico virou presenca no campo')
    if any(e.get('ENTITY_TYPE') == 'PUBLIC_VOICE' for e in ev) and len(ev) < 3:
        m.append('voz isolada tratada como incidencia')
    return m


def main():
    C = {n: _le(n + '.json') for n in (
        'CURRENT-FIELD-SIGNALS', 'CROP-WINDOWS', 'RESISTANCE', 'SCIENCE',
        'COMPETITOR-ACTIVITIES', 'MARKET-OBSERVATIONS', 'CROP-ECONOMIC-WEIGHT',
        'PRODUCT-RELATIONSHIPS', 'PRODUCTS-COMMERCIAL', 'PRODUCTS-REGULATORY',
        'ACTIVE-INGREDIENTS', 'PRODUCT-ACTIVE-INGREDIENTS',
        'REGULATORY-FUTURE-FACTS', 'PUBLIC-VOICES')}
    cs = {k: [x for x in v if x.get('CLIENT_SAFE')] for k, v in C.items()}

    lbl_crop = _ix(cs['PRODUCT-RELATIONSHIPS'], 'CROP_IDS')
    lbl_issue = _ix(cs['PRODUCT-RELATIONSHIPS'], 'ISSUE_IDS')
    field_crop = _ix(cs['CURRENT-FIELD-SIGNALS'], 'CROP_IDS')
    # ⚠️ NÃO existe mais índice de janela por cultura: era ele o defeito.
    # A janela é escolhida pelos eixos que ela mesma declara.
    todas_as_janelas = cs['CROP-WINDOWS']

    def janelas(crop, alvo, geo):
        return [w for w in todas_as_janelas if janela_vale(w, crop, alvo, geo)]
    res_crop = _ix(cs['RESISTANCE'], 'CROP_IDS')
    sci_crop = _ix(cs['SCIENCE'], 'CROP_IDS')
    comp_crop = _ix(cs['COMPETITOR-ACTIVITIES'], 'CROP_IDS')
    mkt_crop = _ix(cs['MARKET-OBSERVATIONS'], 'CROP_IDS')
    econ_crop = _ix(cs['CROP-ECONOMIC-WEIGHT'], 'CROP_IDS')

    reg_por_num = {re.sub(r'\D', '', str(p.get('REGISTRATION_NUMBER') or '')).lstrip('0').zfill(6): p
                   for p in cs['PRODUCTS-REGULATORY']}
    ai_por_prod = defaultdict(list)
    for r in cs['PRODUCT-ACTIVE-INGREDIENTS']:
        k = re.sub(r'\D', '', str(r.get('REGISTRATION_NUMBER') or '')).lstrip('0').zfill(6)
        ai_por_prod[k].append(r)
    ai_por_id = {a['ID']: a for a in cs['ACTIVE-INGREDIENTS']}

    # O catálogo comercial deixa de ser carregado e ignorado.
    ix_com = CM.indice_comercial(cs['PRODUCTS-COMMERCIAL'])
    # E o par cultura × alvo passa a ser o que a fonte OBSERVOU, não o produto
    # cartesiano entre duas listas planas do mesmo documento.
    pares_ix = NE.indice_de_pares(cs['CURRENT-FIELD-SIGNALS'])
    # ⚠️ A JANELA DEIXA DE SER SÓ CALENDÁRIO. Medido: das orações atribuídas a um
    # par, nenhuma declara datas — e treze declaram a condição por fenologia,
    # limiar, fase da praga, clima ou ato. `v21_janelas` é o dono do tipo.
    janelas_ix = defaultdict(list)
    for s_ in cs['CURRENT-FIELD-SIGNALS']:
        for j in JN.janelas_do_sinal(s_):
            janelas_ix[(j['CROP'], j['TARGET'])].append(j)

    # ── TRÊS PERGUNTAS QUE O BOLETIM RESPONDE, COM TRÊS DONOS ───────────────
    # O red team semântico mediu o motor a empilhar numa resposta só o que o
    # boletim diz em três: a FASE DA PRAGA, a RECOMENDAÇÃO e a JANELA. Sobre o
    # melo × carpocapsa do Veneto isso produzia
    # `CONDICAO_EXIGE_MEDICAO_QUE_NAO_TEMOS` num boletim que declarava a fase em
    # letras — «terzo volo terminato» — e que na frase seguinte mandava
    # continuar a defesa.
    #
    #     FIM DO VOO NÃO É FIM DA NECESSIDADE DE INTERVENÇÃO.
    #     E RECOMENDAR CONTINUAR NÃO É DECLARAR JANELA ABERTA.
    #
    # Cada uma passa a ter campo próprio, evidência própria e trecho próprio.
    datas_dos_sinais = {s_['ID']: str(s_.get('REFERENCE_DATE') or '')
                        for s_ in cs['CURRENT-FIELD-SIGNALS']}
    declarado_ix = defaultdict(list)
    for s_ in cs['CURRENT-FIELD-SIGNALS']:
        for campo, _metodo, crops, issues, oracao in NE.atribuicoes(s_):
            fase, _pf = NE.fase_da_praga(oracao)
            rec, _pr = NE.recomendacao(oracao)
            linha = {'SOURCE_ID': s_['ID'],
                     'REGION_IDS': s_.get('REGION_IDS') or [],
                     'DATE': datas_dos_sinais.get(s_['ID'], ''),
                     'FIELD': campo, 'CLAUSE': oracao[:320],
                     'PEST_STAGE': fase, 'RECOMMENDATION': rec,
                     'QUALITATIVE': NE.qualitativo(oracao),
                     'THRESHOLD_MEASURE': NE.limiar_declarado(oracao),
                     'DELEGATED': NE.decisao_delegada(oracao),
                     # ⚠️ um disciplinare descreve a biologia da praga — «il
                     # primo volo inizia verso la metà di aprile». Isso e a
                     # REGRA, nao o estado do campo hoje. So quem declara
                     # direcao declara estado.
                     'DECLARA_ESTADO': NE.declara_direcao(s_)}
            for c_ in crops:
                for i_ in issues:
                    declarado_ix[(c_, i_)].append(linha)

    def declarados(crop, alvo, geo):
        """→ as orações deste par NESTA região, da mais recente para a mais velha.

        A ordem é DECLARADA e não estatística: o documento mais recente que
        afirma alguma coisa é o que responde por ela. Empate desfaz-se pelo ID,
        para o pacote não mudar de conteúdo entre duas execuções iguais.
        """
        linhas = [d for d in declarado_ix.get((crop, alvo), [])
                  if geo in (d['REGION_IDS'] or [])]
        return sorted(linhas, key=lambda d: (d['DATE'], d['SOURCE_ID']),
                      reverse=True)

    def janela_tipada(crop, alvo, geo):
        """→ a candidata que vale para ESTA combinação, ou None.

        A região é lida do registro que fez a observação: uma condição
        declarada num boletim da Emilia-Romagna não descreve a Toscana.
        E a escolha entre candidatas é DECLARADA: primeiro a que está aberta
        agora, depois a de tipo mais forte, e um ato administrativo nunca é
        escolhido como janela agronômica.
        """
        cand = [j for j in janelas_ix.get((crop, alvo), [])
                if geo in (j['REGION_IDS'] or [])
                and j['WINDOW_TYPE'] in JN.AGRONOMICOS]
        if not cand:
            return None
        forca = {t: i for i, t in enumerate(JN.TIPOS)}
        cand.sort(key=lambda j: (0 if j['WINDOW_OPEN_NOW'] == 'YES' else
                                 1 if j['WINDOW_OPEN_NOW'] == 'UNKNOWN' else 2,
                                 forca[j['WINDOW_TYPE']],
                                 0 if j['CLAUSE_DIRECTION'] == NE.POSITIVE_PRESSURE
                                 else 1))
        return cand[0]

    def janela_administrativa(crop, alvo, geo):
        """→ o ato administrativo que fixa o momento para ESTE par, ou None.

        Ele NÃO é janela agronômica e continua a não ser — a lei não mudou. Mas
        dizer `WINDOW_RULE_MISSING` sobre um par cujo momento é fixado por um
        Piano di azione regionale é acusar a fonte de silêncio onde há norma.

            «NINGUÉM DECLAROU A REGRA» E «A REGRA É UMA OBRIGAÇÃO DE NORMA»
            SÃO RESPOSTAS DIFERENTES, E SÓ UMA DELAS PEDE COLETA.
        """
        return next((j for j in janelas_ix.get((crop, alvo), [])
                     if geo in (j['REGION_IDS'] or [])
                     and j['WINDOW_TYPE'] == JN.ADMINISTRATIVE_WINDOW), None)

    def _casados(rotulos):
        """Os registros do CATALOGO que o par de rotulo alcanca — nao so o nome."""
        vistos, fora = set(), []
        for r in rotulos:
            for p in ix_com.get(CM.num(r.get('REGISTRATION_NUMBER')), []):
                if p['ID'] not in vistos:
                    vistos.add(p['ID'])
                    fora.append(p)
        return fora

    def camada_comercial(o, apoios, rotulos, pinos):
        """As três perguntas comerciais que o V1 não fazia.

        1 · existe produto no CATÁLOGO comercial, e não só no registro?
        2 · a fonte manda AGIR, ou manda parar?
        3 · a geografia da AFIRMAÇÃO se sustenta — sem contar a do rótulo?
        """
        c = dict(CM.casar(list(rotulos), ix_com))

        # ── geografia: três coisas diferentes, três campos ────────────────────
        obs = [e for e in apoios if e.get('ENTITY_TYPE') in TIPOS_QUE_OBSERVAM]
        campo_geo = sorted({g for e in obs for g in (e.get('REGION_IDS') or [])})
        aut_geo = sorted({g for e in apoios
                          if e.get('ENTITY_TYPE') in TIPOS_DE_AUTORIZACAO
                          for g in (e.get('REGION_IDS') or [])})
        c['CLAIM_GEOGRAPHY'] = o['GEOGRAPHY']
        c['FIELD_GEOGRAPHY'] = campo_geo
        c['PRODUCT_AUTHORIZATION_GEOGRAPHY'] = aut_geo
        c['GEOGRAPHY_LAW'] = ('CLAIM_GEOGRAPHY e a geografia da AFIRMACAO; '
                              'FIELD_GEOGRAPHY e a de quem observou; '
                              'PRODUCT_AUTHORIZATION_GEOGRAPHY e onde o produto '
                              'e autorizado. Rotulo nacional CONTEM a regiao: '
                              'conter nao e contradizer, e por isso a terceira '
                              'nunca vota na primeira.')
        if o['GEOGRAPHY_SCOPE'] == 'PROVINCIAL':
            c['CLAIM_GEOGRAPHY_HOLDS'] = True
            c['CLAIM_GEOGRAPHY_WHY'] = 'a alegacao e tao estreita quanto o apoio'
        elif not campo_geo:
            c['CLAIM_GEOGRAPHY_HOLDS'] = o['GEOGRAPHY'] in ('GEO_ITALY', 'GEO_EU')
            c['CLAIM_GEOGRAPHY_WHY'] = ('nenhum apoio de observacao declara '
                                        'geografia propria')
        elif o['GEOGRAPHY'] in ('GEO_ITALY', 'GEO_EU'):
            promovida = any(e.get('REGION_REPRESENTS') is False for e in obs)
            c['CLAIM_GEOGRAPHY_HOLDS'] = not promovida
            c['CLAIM_GEOGRAPHY_WHY'] = ('apoio provincial sustentando alegacao '
                                        'mais ampla' if promovida else
                                        'ha apoio que fala pelo proprio ambito')
        else:
            cabe = set(campo_geo) <= {o['GEOGRAPHY']}
            representa = any(e.get('REGION_REPRESENTS') is not False for e in obs)
            c['CLAIM_GEOGRAPHY_HOLDS'] = bool(cabe and representa)
            c['CLAIM_GEOGRAPHY_WHY'] = (
                'a observacao cabe na geografia alegada e fala por ela' if
                (cabe and representa) else
                'a observacao nao cabe na geografia alegada' if not cabe else
                'nenhum apoio fala PELA regiao alegada')

        # ── necessidade: o que o texto da fonte manda fazer ───────────────────
        pinos = list(pinos)
        if pinos:
            direcao, pino = NE.direcao_do_par(pinos)
            c['NEED_DIRECTION'] = direcao
            c['NEED_EVIDENCE_ID'] = pino['NEED_EVIDENCE_ID']
            c['NEED_EXCERPT'] = pino['NEED_EXCERPT']
            c['NEED_METHOD'] = pino['NEED_METHOD']
            c['NEED_FIELD'] = pino['NEED_FIELD']
            # Por que NAO se sabe, quando nao se sabe. Um `UNKNOWN` mudo parece
            # «nao havia texto»; e o que houve foi texto que nomeia varios
            # alvos e uma direcao so.
            c['NEED_AMBIGUITY_CODES'] = list(pino.get('NEED_AMBIGUITY_CODES') or [])
        else:
            c['NEED_DIRECTION'] = NE.UNKNOWN
            c['NEED_EVIDENCE_ID'] = None
            c['NEED_EXCERPT'] = ''
            c['NEED_METHOD'] = None
            c['NEED_FIELD'] = None
            c['NEED_AMBIGUITY_CODES'] = []
        c['NEED_AMBIGUITY'] = ' '.join(NE.AMBIGUIDADE[k]
                                       for k in c['NEED_AMBIGUITY_CODES'])
        c['NEED_LAW'] = ('NEED_DIRECTION e INTERPRETACAO SINTONIA sobre o texto '
                         'de terceiro. A frase original viaja junto em '
                         'NEED_EXCERPT: quem discordar da leitura le a frase. '
                         'Entre oracoes do mesmo par, a que manda PARAR vence. '
                         'E uma oracao que nomeia varios alvos com uma direcao '
                         'so nao atribui direcao a nenhum deles: fica UNKNOWN, '
                         'com o motivo em NEED_AMBIGUITY.')

        # ── OS DOIS RELÓGIOS, SEPARADOS ──────────────────────────────────────
        #
        # A lei impressa neste mesmo campo já dizia: «sem janela de aplicação, a
        # data do documento diz apenas se o sinal é corrente». O CÓDIGO dizia
        # outra coisa — caía na idade do sinal e chamava aquilo de `ACT_NOW`.
        # Era assim que nascia o cartão com `ACT NOW` e «no canonical window
        # linked» lado a lado.
        #
        #     LEI IMPRESSA QUE O CÓDIGO NÃO CUMPRE É PIOR QUE LEI NENHUMA:
        #     ELA FAZ QUEM LÊ CONFIAR NO NÚMERO ERRADO.
        #
        # Agora `COMMERCIAL_WINDOW` só existe se houver janela de APLICAÇÃO, e a
        # recência do sinal vive à parte, com nome próprio.
        if o.get('WINDOW_KIND') == 'APPLICATION' and o.get('DAYS_REMAINING') is not None:
            d = o['DAYS_REMAINING']
            c['COMMERCIAL_WINDOW'] = ('ACT_NOW' if 0 <= d <= SINAL_CORRENTE_DIAS else
                                      'PREPARE_NOW' if SINAL_CORRENTE_DIAS < d <= SINAL_RECENTE_DIAS else
                                      'FUTURE' if d > SINAL_RECENTE_DIAS else 'CLOSED')
            c['COMMERCIAL_WINDOW_FROM'] = o.get('WINDOW_FIELD')
        else:
            c['COMMERCIAL_WINDOW'] = 'UNKNOWN'
            c['COMMERCIAL_WINDOW_FROM'] = None
        idade = o.get('SIGNAL_AGE_DAYS')
        c['SIGNAL_CURRENCY'] = ('UNKNOWN' if idade is None else
                                'CURRENT' if idade <= SINAL_CORRENTE_DIAS else
                                'RECENT' if idade <= SINAL_RECENTE_DIAS else 'OLD')
        # QUAL relogio declarou o momento. Nunca os dois com o mesmo nome.
        c['COMMERCIAL_TIMING_BASIS'] = (
            'APPLICATION_WINDOW' if c['COMMERCIAL_WINDOW'] in ('ACT_NOW', 'PREPARE_NOW')
            else 'CURRENT_SOURCE_RECOMMENDATION'
            if (c['SIGNAL_CURRENCY'] == 'CURRENT'
                and c.get('NEED_DIRECTION') in CM.NECESSIDADE_POSITIVA)
            else 'NONE')
        c['COMMERCIAL_WINDOW_LAW'] = (
            'so janela de APLICACAO conta como tempo comercial. '
            'PREPARATION_WINDOW e data de ato — quando sai o decreto — e nao '
            'quando se pulveriza. Sem janela de aplicacao isto fica UNKNOWN: a '
            'data do documento responde SIGNAL_CURRENCY, que e outra pergunta.')

        # ── A JANELA, EM DUAS PERGUNTAS QUE NUNCA SAO A MESMA ────────────────
        # WINDOW_DEFINED  : sabemos QUAL condicao define o momento certo?
        # WINDOW_OPEN_NOW : ha evidencia de que a condicao esta satisfeita AGORA?
        #
        #     DEFINIDA NAO E ABERTA. SABER O GATILHO NAO E SABER QUE ELE DISPAROU.
        jt = janela_tipada(o.get('CROP'), o.get('TARGET'), o.get('GEOGRAPHY'))
        if o.get('WINDOW_KIND') == 'APPLICATION' and o.get('DAYS_REMAINING') is not None:
            d = o['DAYS_REMAINING']
            c['WINDOW_TYPE'] = JN.CALENDAR_WINDOW
            c['WINDOW_CONDITION'] = o.get('WINDOW_FIELD')
            c['WINDOW_DEFINED'] = 'YES'
            c['WINDOW_OPEN_NOW'] = 'YES' if 0 <= d else 'NO'
            c['WINDOW_OPEN_NOW_METHOD'] = 'DATAS_DECLARADAS_NO_REGISTRO'
            c['WINDOW_EVIDENCE_ID'] = None
        elif jt:
            c['WINDOW_TYPE'] = jt['WINDOW_TYPE']
            c['WINDOW_CONDITION'] = jt['WINDOW_CONDITION']
            c['WINDOW_DEFINED'] = 'YES'
            c['WINDOW_OPEN_NOW'] = jt['WINDOW_OPEN_NOW']
            c['WINDOW_OPEN_NOW_METHOD'] = jt['OPEN_NOW_METHOD']
            c['WINDOW_EVIDENCE_ID'] = jt['SOURCE_ID']
            c['PHENOLOGY_DECLARED'] = jt.get('PHENOLOGY_DECLARED')
        else:
            c['WINDOW_TYPE'] = None
            c['WINDOW_CONDITION'] = None
            c['WINDOW_DEFINED'] = 'NO'
            c['WINDOW_OPEN_NOW'] = 'UNKNOWN'
            c['WINDOW_OPEN_NOW_METHOD'] = 'NENHUMA_CONDICAO_DECLARADA_PARA_O_PAR'
            c['WINDOW_EVIDENCE_ID'] = None
        c.setdefault('PHENOLOGY_DECLARED', None)
        c['WINDOW_TYPE_LAW'] = (
            'a fonte italiana declara o momento por FENOLOGIA, LIMIAR, FASE DA '
            'PRAGA ou CONDICAO CLIMATICA — quase nunca por datas. WINDOW_TYPE '
            'diz qual delas. ATO ADMINISTRATIVO nunca vira janela agronomica: '
            'prazo de norma e obrigacao, e vale so para o alvo que a norma '
            'nomeia.')

        # ── A FASE DA PRAGA · o que o inseto está a fazer, e nada mais ───────
        dec = declarados(o.get('CROP'), o.get('TARGET'), o.get('GEOGRAPHY'))
        fase = next((d for d in dec if d['DECLARA_ESTADO']
                     and d['PEST_STAGE'] != NE.STAGE_NOT_DECLARED), None)
        c['PEST_STAGE_STATE'] = fase['PEST_STAGE'] if fase else NE.STAGE_NOT_DECLARED
        c['PEST_STAGE_EVIDENCE_ID'] = fase['SOURCE_ID'] if fase else None
        c['PEST_STAGE_EXCERPT'] = fase['CLAUSE'] if fase else ''
        c['PEST_STAGE_LAW'] = (
            'a fase da praga e FATO DECLARADO pela fonte, com trecho ao lado. '
            'Ela NAO responde se ha janela, se ela esta aberta nem se a defesa '
            'acabou: fim do voo nao e fim da necessidade de intervencao. Quem '
            'declara mais recentemente responde; empate desfaz-se pelo ID.')

        # ── A RECOMENDAÇÃO · o que o serviço manda fazer ─────────────────────
        # Quem manda PARAR continua a vencer: se a direcao do par e restritiva,
        # a recomendacao espelha-a. So dentro da porta aberta e que a distincao
        # «comecar» x «continuar» tem lugar — e ela vem de uma oracao que a
        # declara, com dono proprio.
        if c.get('NEED_DIRECTION') in NE.RESTRITIVOS:
            c['ACTION_RECOMMENDATION_STATE'] = NE._DIRECAO_PARA_RECOMENDACAO[
                c['NEED_DIRECTION']]
            c['ACTION_RECOMMENDATION_EVIDENCE_ID'] = c.get('NEED_EVIDENCE_ID')
            c['ACTION_RECOMMENDATION_EXCERPT'] = c.get('NEED_EXCERPT') or ''
        else:
            cont = next((d for d in dec if d['DECLARA_ESTADO']
                         and d['RECOMMENDATION'] == NE.CONTINUE_RECOMMENDED), None)
            if cont:
                c['ACTION_RECOMMENDATION_STATE'] = NE.CONTINUE_RECOMMENDED
                c['ACTION_RECOMMENDATION_EVIDENCE_ID'] = cont['SOURCE_ID']
                c['ACTION_RECOMMENDATION_EXCERPT'] = cont['CLAUSE']
            else:
                c['ACTION_RECOMMENDATION_STATE'] = (
                    NE._DIRECAO_PARA_RECOMENDACAO.get(
                        c.get('NEED_DIRECTION'), NE.RECOMMENDATION_NOT_DECLARED))
                c['ACTION_RECOMMENDATION_EVIDENCE_ID'] = c.get('NEED_EVIDENCE_ID')
                c['ACTION_RECOMMENDATION_EXCERPT'] = c.get('NEED_EXCERPT') or ''
        c['ACTION_RECOMMENDATION_LAW'] = (
            'a recomendacao e o que a fonte MANDA FAZER, e nao a prova de que o '
            'momento chegou. CONTINUE_RECOMMENDED diz que a defesa ja decorria '
            'e nao deve parar — util exatamente quando a fase da praga terminou. '
            'Entre oracoes do mesmo par, a que manda parar continua a vencer.')

        # ── O LIMIAR · houve medição declarada, ou só prosa? ─────────────────
        if c.get('WINDOW_TYPE') == JN.THRESHOLD_WINDOW:
            med = next((d for d in dec if d['DECLARA_ESTADO']
                        and d['THRESHOLD_MEASURE']), None)
            qual = next((d for d in dec if d['DECLARA_ESTADO']
                         and d['QUALITATIVE']), None)
            if med:
                c['THRESHOLD_STATE'] = 'MEASUREMENT_DECLARED'
                c['THRESHOLD_STATE_EVIDENCE_ID'] = med['SOURCE_ID']
            elif qual:
                c['THRESHOLD_STATE'] = 'QUALITATIVE_PICTURE_ONLY'
                c['THRESHOLD_STATE_EVIDENCE_ID'] = qual['SOURCE_ID']
                # e entao o metodo da janela para de mentir: nao e que a fonte
                # nao falou — e que o que ela falou nao responde a pergunta.
                if c.get('WINDOW_OPEN_NOW') == 'UNKNOWN':
                    c['WINDOW_OPEN_NOW_METHOD'] = (
                        'FONTE_DECLARA_QUADRO_QUALITATIVO_NAO_A_MEDICAO')
            else:
                c['THRESHOLD_STATE'] = 'NOT_DECLARED'
                c['THRESHOLD_STATE_EVIDENCE_ID'] = None
        else:
            c['THRESHOLD_STATE'] = 'NOT_APPLICABLE'
            c['THRESHOLD_STATE_EVIDENCE_ID'] = None
        # ── A REGRA · declarada, delegada ao pomar, ou inexistente ──────────
        # `WINDOW_RULE_MISSING` diz «ninguem declarou a condicao». Mas o Manuale
        # difesa integrata del melo do Veneto declara — e o que ele declara e que
        # a decisao e da empresa. Chamar isso de regra ausente e acusar a fonte
        # de nao ter dito o que ela disse com todas as letras.
        deleg = next((d for d in dec if d['DELEGATED']), None)
        adm = janela_administrativa(o.get('CROP'), o.get('TARGET'),
                                    o.get('GEOGRAPHY'))
        if c.get('WINDOW_TYPE') == JN.RULE_DELEGATED_TO_FARM:
            c['WINDOW_RULE_STATE'] = 'RULE_DELEGATED_TO_FARM'
            c['WINDOW_RULE_EVIDENCE_ID'] = c.get('WINDOW_EVIDENCE_ID')
        elif c.get('WINDOW_DEFINED') == 'YES':
            c['WINDOW_RULE_STATE'] = 'RULE_DECLARED'
            c['WINDOW_RULE_EVIDENCE_ID'] = c.get('WINDOW_EVIDENCE_ID')
        elif deleg:
            c['WINDOW_RULE_STATE'] = 'RULE_DELEGATED_TO_FARM'
            c['WINDOW_RULE_EVIDENCE_ID'] = deleg['SOURCE_ID']
        elif adm:
            c['WINDOW_RULE_STATE'] = 'RULE_ADMINISTRATIVE_ONLY'
            c['WINDOW_RULE_EVIDENCE_ID'] = adm['SOURCE_ID']
            c['WINDOW_RULE_CONDITION'] = adm['WINDOW_CONDITION']
        else:
            c['WINDOW_RULE_STATE'] = 'RULE_NOT_DECLARED'
            c['WINDOW_RULE_EVIDENCE_ID'] = None
        c.setdefault('WINDOW_RULE_CONDITION', c.get('WINDOW_CONDITION'))
        c['WINDOW_RULE_STATE_LAW'] = (
            'RULE_DELEGATED_TO_FARM nao e janela e nunca abre uma: e a fonte '
            'regional declarando que o gatilho e do pomar, pelas observacoes e '
            'pelo historico dele. RULE_ADMINISTRATIVE_ONLY e a norma fixando o '
            'momento — obrigacao, nao agronomia, e por isso WINDOW_DEFINED '
            'continua NO. Coletar mais nao muda nenhuma das duas: a resposta ja '
            'foi dada. RULE_NOT_DECLARED e o unico dos quatro que pede coleta.')

        c['THRESHOLD_STATE_LAW'] = (
            'diz se a fonte declarou MEDICAO, quadro QUALITATIVO ou nada. NUNCA '
            'responde WINDOW_OPEN_NOW: «pochissime aree sopra soglia» traz as '
            'duas coisas na mesma frase, e frase qualitativa so responde a uma '
            'condicao quantitativa quando a propria fonte declara a equivalencia.')

        # ── O QUE O PRODUTO É · modo de acao, dose e restricao ────────────────
        # Tudo isto ja estava no acervo, ligado por NUMERO DE REGISTRO — a mesma
        # juncao que o catalogo comercial ja usa. A tela dizia «mode of action =
        # not known» porque o CARTAO nao carregava o campo, nao porque o acervo
        # nao soubesse.
        #
        #     «NÃO SEI» DITO POR QUEM NÃO FOI OLHAR NÃO É «NÃO SEI»: É DESCUIDO.
        ativos, frac, restricoes = {}, set(), {}
        for r in rotulos:
            for pai in ai_por_prod.get(CM.num(r.get('REGISTRATION_NUMBER')), []):
                a = ai_por_id.get(pai.get('ACTIVE_INGREDIENT_ID'))
                if not a:
                    continue
                ativos[a['ID']] = a.get('NAME')
                if a.get('FRAC'):
                    frac.add('FRAC ' + str(a['FRAC']))
                if a.get('IRAC'):
                    frac.add('IRAC ' + str(a['IRAC']))
                if a.get('HRAC'):
                    frac.add('HRAC ' + str(a['HRAC']))
                if a.get('EU_EXPIRATION_OF_APPROVAL'):
                    # a mesma substancia chega por varios rotulos: o FATO e um so
                    restricoes[a['ID']] = {
                        'CODE': 'EU_APPROVAL_EXPIRES',
                        'ACTIVE_INGREDIENT': a.get('NAME'),
                        'DATE': a['EU_EXPIRATION_OF_APPROVAL'],
                        'EVIDENCE_ID': a['ID']}
        c['ACTIVE_INGREDIENT_IDS'] = sorted(ativos)
        c['ACTIVE_INGREDIENT_NAMES'] = sorted(v for v in ativos.values() if v)
        c['MODE_OF_ACTION_CODES'] = sorted(frac)
        c['MODE_OF_ACTION_STATE'] = 'CLASSIFIED' if frac else 'UNKNOWN'
        c['PRODUCT_RESTRICTIONS'] = [restricoes[k] for k in sorted(restricoes)]
        c['PRODUCT_RESTRICTIONS_LAW'] = (
            'restricao aqui e FATO PUBLICADO com data e fonte — expiracao de '
            'aprovacao europeia, por exemplo. Expiracao NAO e retirada, nao e '
            'risco e nao e oportunidade: e uma data no Jornal Oficial.')
        # A dose e o modo de emprego estao na FRASE DO ROTULO, e e assim que
        # viajam: citacao, nao campo estruturado. Estruturar «100-150 ml/hl»
        # seria interpretar bula, e bula nao se interpreta por regex.
        c['LABEL_QUOTES'] = [q for q in (r.get('QUOTE_FROM_LABEL')
                                         for r in rotulos[:3]) if q]
        c['APPLICATION_STATE'] = ('QUOTED_ON_LABEL' if c['LABEL_QUOTES']
                                  else 'UNKNOWN')

        # ── TAMANHO · so dimensao defensavel, nunca dinheiro ─────────────────
        sinais = [a for a in apoios if a.get('ENTITY_TYPE') == 'FIELD_SIGNAL']
        fontes = {(a.get('SOURCE_IDS') or [None])[0] for a in sinais} - {None}
        area = [e for e in econ_crop.get(o.get('CROP'), [])
                if e.get('INDICATOR') == 'AREA'
                and o.get('GEOGRAPHY') in (e.get('REGION_IDS') or [])]
        dim = {'SINAIS_DE_CAMPO': len(sinais),
               'FONTES_INDEPENDENTES': len(fontes),
               'REGIOES_DO_PAR': None,
               'AREA_OFICIAL_HA': (area[0].get('VALUE') if area else None),
               'AREA_EVIDENCE_ID': (area[0].get('ID') if area else None)}
        c['COMMERCIAL_MAGNITUDE_DIMENSIONS'] = dim
        c['COMMERCIAL_MAGNITUDE'] = ('UNKNOWN' if not (dim['SINAIS_DE_CAMPO'] or
                                                       dim['AREA_OFICIAL_HA'])
                                     else 'MEASURED_BY_DIMENSION')
        c['COMMERCIAL_MAGNITUDE_LAW'] = (
            'NAO ha TAM, SAM nem dinheiro: nao ha fonte para eles. O tamanho '
            'aqui e o que se pode contar — sinais, fontes independentes e area '
            'oficial quando existe linha client-safe. Sem nenhuma dessas, '
            'UNKNOWN.')

        # ── AS QUATRO CONFIANÇAS, SEPARADAS ──────────────────────────────────
        # Uma confianca so obriga a media entre coisas que nao se somam: o sinal
        # pode ser forte e a janela inexistente, e a media esconderia as duas.
        c['SIGNAL_CONFIDENCE'] = (
            'ALTA' if len(fontes) >= 2 and c['SIGNAL_CURRENCY'] == 'CURRENT' else
            'MEDIA' if sinais and c['SIGNAL_CURRENCY'] in ('CURRENT', 'RECENT')
            else 'BAIXA')
        c['WINDOW_CONFIDENCE'] = (
            'ALTA' if o.get('WINDOW_KIND') == 'APPLICATION' else
            'MEDIA' if o.get('WINDOW_KIND') else 'NENHUMA')
        c['PRODUCT_MATCH_CONFIDENCE'] = (
            'ALTA' if (o.get('PRODUCT_LINK_STATE') == VERIFIED_LABEL_MATCH
                       and c['COMMERCIAL_PRODUCT_COUNT']) else
            'MEDIA' if o.get('PRODUCT_LINK_STATE') == VERIFIED_LABEL_MATCH
            else 'BAIXA')
        c['CONFIDENCE_LAW'] = (
            'quatro perguntas diferentes, quatro respostas. SIGNAL fala do que '
            'foi observado; WINDOW, de quando agir; PRODUCT_MATCH, do vinculo '
            'com o portfolio; COMMERCIAL_READINESS e COMMERCIAL_PRIORITY, que '
            'vive ao lado. Media entre elas escondia justamente a que faltava.')
        return c

    brutos, rejeitados = [], []

    def emitir(arquetipo, crop, alvo, geo, escopo, apoios, link, produtos,
               numeros, dim, acao, rotulos=(), pinos=()):
        T = TEXTO[arquetipo]
        porque_agora, relevancia = T['WHY_NOW'], T['ADAMA']
        prova, nao_prova = T['PROVA'], T['NAO_PROVA']
        apoios = [a for a in apoios if a]
        if not apoios:
            return
        ini, fim, dias, jest, jcampo, jtipo = janela(janelas(crop, alvo, geo) + apoios)
        sdata, sidade = data_do_sinal(apoios)
        oid, chave = identidade(arquetipo, crop, alvo, geo,
                                ini or ('EU' if arquetipo == 'O5_REGULATORY_PREPARATION' else None))
        o = {'ID': oid, 'IDENTITY_KEY': chave, 'ARCHETYPE': arquetipo,
             'CROP': crop, 'TARGET': alvo, 'GEOGRAPHY': geo, 'GEOGRAPHY_SCOPE': escopo,
             'WINDOW_START': ini, 'WINDOW_END': fim, 'DAYS_REMAINING': dias,
             'WINDOW_STATE': jest, 'WINDOW_FIELD': jcampo, 'WINDOW_KIND': jtipo,
             'SIGNAL_DATE': sdata, 'SIGNAL_AGE_DAYS': sidade,
             'PRODUCT_LINK_STATE': link,
             'PRODUCT_RELATIONSHIPS': produtos[:12],
             'EVIDENCE_IDS': [a['ID'] for a in apoios],
             'EVIDENCE_FAMILIES': sorted({a.get('ENTITY_TYPE') for a in apoios}),
             'WHY_NOW': porque_agora, 'ADAMA_RELEVANCE': relevancia,
             'NUMBERS': numeros,
             'WHAT_IT_PROVES': prova, 'WHAT_IT_DOES_NOT_PROVE': nao_prova,
             'SCORE_DIMENSIONS': dim, 'OPPORTUNITY_SCORE': score(dim),
             'ACTION_MAP': acao}
        o.update(camada_comercial(o, apoios, rotulos, pinos))
        # ⚠️ O estado de acao sai da CADEIA, nunca da idade do sinal sozinha.
        o['STATUS'], elos = estado_de_acao(o)
        o['ACTION_CHAIN_LINKS'] = {k: bool(v) for k, v in elos.items()}
        codigos, cadeia = cadeia_de_agora(o, elos, apoios)
        o['WHY_NOW_CODES'] = codigos
        o['WHY_NOW_CHAIN'] = cadeia
        o['WHY_NOW_LAW'] = (
            'ACT_NOW so existe com os quatro elos fechados: sinal atual, janela '
            'compativel, vinculo com portfolio e tempo para agir. Sem janela nao '
            'ha ACT_NOW — ha VALIDATE_NOW, que diz o que falta. A idade do '
            'boletim vive em SIGNAL_CURRENCY e nunca substitui a janela.')
        falhas = portoes(o, apoios)
        o['OPPORTUNITY_STATE'] = CONFIRMADA if not falhas else CANDIDATA
        o['BLOCKING_GATES'] = falhas
        rt = red_team(o, apoios)
        o['RED_TEAM_FINDINGS'] = rt
        if rt:
            # o red team NAO confirma nada: so derruba
            o['OPPORTUNITY_STATE'] = CANDIDATA
            o['BLOCKING_GATES'] = falhas + ['RED_TEAM · ' + x for x in rt]
        if o['OPPORTUNITY_STATE'] == CANDIDATA:
            o['STATUS'] = 'TO_VALIDATE' if falhas else o['STATUS']
        o['CONFIDENCE'] = ('ALTA' if o['OPPORTUNITY_STATE'] == CONFIRMADA
                           else ('MEDIA' if o['OPPORTUNITY_SCORE'] >= 8 else 'BAIXA'))
        # ── a segunda pergunta, ao lado da primeira ───────────────────────────
        # OPPORTUNITY_STATE responde «esta leitura se sustenta?».
        # COMMERCIAL_PRIORITY responde «isto e oportunidade comercial defensavel
        # para o portfolio ADAMA?». Sao perguntas diferentes, e nenhuma substitui
        # a outra: um caso pode ser CONFIRMADO e nao vender, e pode VENDER com um
        # portao aberto que o impede de ser confirmado.
        pri, codigos = CM.prioridade(o)
        o['COMMERCIAL_PRIORITY'] = pri
        o['COMMERCIAL_PRIORITY_MEANS'] = CM.SIGNIFICADO[pri]
        # O código é o dado; a frase é o texto. O valor que a frase não carrega
        # dentro vive em NEED_DIRECTION, COMMERCIAL_WINDOW e
        # COMMERCIAL_PRODUCT_COUNT — frase com variável dentro nunca fica
        # traduzida, e este projeto já perdeu duas traduções assim.
        o['WHY_COMMERCIAL_CODES'] = codigos
        o['WHY_COMMERCIAL'] = CM.frase(codigos)
        o['COMMERCIAL_DOES_NOT_PROVE'] = CM.NAO_PROVA
        # ── e a terceira pergunta: isto pode SAIR de casa? ────────────────────
        # SALES_READY e decisao interna. Enviar a um revendedor ou a um RTV e
        # afirmacao publica, e precisa sobreviver a quem a ler sem nos conhecer.
        ext, bloqueios = CM.externo(o, _casados(rotulos))
        o['EXTERNAL_MATERIAL_READY'] = ext
        o['EXTERNAL_BLOCKER_CODES'] = bloqueios
        o['EXTERNAL_BLOCKERS'] = ' '.join(CM.BLOQUEIO_EXTERNO[c] for c in bloqueios)
        o['EXTERNAL_MATERIAL_LAW'] = CM.EXTERNAL_LAW
        o['COMMERCIAL_PRIORITY_LAW'] = (
            'portoes semanticos, nunca soma de pontos. O score ORDENA dentro da '
            'mesma categoria e nao promove ninguem de categoria. E nao ha numero '
            'minimo de familias externas: corroboracao e amplificador, nao '
            'contador cego.')
        # ⚠️ O mapa de departamentos e o ULTIMO: ele le as tres colunas e o
        # estado de acao ja fechados. Calcula-lo antes seria convocar gente com
        # base num estado que ainda ia mudar.
        # ── E · o portfolio, produto a produto, com o primario declarado ─────
        ativos_fonte = {a.get('NAME', '').upper()
                        for a in cs['ACTIVE-INGREDIENTS']
                        if a.get('NAME') and re.search(
                            r'\b%s\b' % re.escape(a['NAME']),
                            str(o.get('NEED_EXCERPT') or ''), re.I)}
        matches, primario, razao_primario = portfolio(
            o, rotulos, _casados(rotulos), ai_por_prod, ai_por_id, ativos_fonte)
        o['PORTFOLIO_MATCHES'] = matches
        o['PRIMARY_MATCH'] = primario
        o['PRIMARY_MATCH_REASON'] = razao_primario
        o['SOURCE_NAMED_ACTIVES'] = sorted(ativos_fonte)
        o['PORTFOLIO_LAW'] = (
            'cada produto responde por si: CROP_FIT, TARGET_FIT, REGIONAL_FIT, '
            'REGULATORY_FIT e WINDOW_FIT sao lidos um a um. PRIMARY_MATCH nao e '
            'o primeiro da lista: so existe quando a fonte nomeia a substancia '
            'ou quando ha um produto so. Sem regra, UNKNOWN.')
        # ── O QUE FALTA, com nome — a lista que dirige a proxima coleta ──────
        falta = []
        if o.get('TARGET'):
            # a fonte pode ter respondido a pergunta com «decide o pomar».
            # Isso FECHA a pergunta da regra: sabemos qual e — medir no pomar.
            # O que continua em aberto e a medicao, e ela nao e regional.
            if o.get('WINDOW_RULE_STATE') == 'RULE_DELEGATED_TO_FARM':
                falta.append('WINDOW_RULE_DELEGATED_TO_FARM')
            elif o.get('WINDOW_RULE_STATE') == 'RULE_ADMINISTRATIVE_ONLY':
                falta.append('WINDOW_RULE_ADMINISTRATIVE_ONLY')
            elif o.get('WINDOW_DEFINED') != 'YES':
                falta.append('WINDOW_RULE_MISSING')
            elif o.get('WINDOW_OPEN_NOW') != 'YES':
                falta.append('WINDOW_STATE_UNKNOWN')
            if not (o.get('COMMERCIAL_PRODUCT_COUNT') or 0):
                falta.append('COMMERCIAL_PRODUCT_MISSING')
            if o.get('PRODUCT_LINK_STATE') != VERIFIED_LABEL_MATCH:
                falta.append('LABEL_LINK_MISSING')
            if o.get('NEED_DIRECTION') == NE.UNKNOWN:
                falta.append('DIRECTION_UNKNOWN')
            if o.get('NEED_AMBIGUITY_CODES'):
                falta.append('DIRECTION_AMBIGUOUS')
            if o.get('SIGNAL_CURRENCY') not in ('CURRENT', 'RECENT'):
                falta.append('SIGNAL_NOT_RECENT')
            # estes dois faltam SEMPRE, e dizer isso e o contrario de esconder:
            # boletim declara ocorrencia, nao incidencia; e o acervo e um
            # retrato, nao uma serie.
            falta.append('INTENSITY_UNKNOWN')
            falta.append('RECURRENCE_UNKNOWN')
        else:
            falta.append('NO_AGRONOMIC_TARGET')
        if not str(o.get('GEOGRAPHY') or '').startswith('REGION_'):
            falta.append('REGION_NOT_DECLARED')
        if not (o.get('COMMERCIAL_MAGNITUDE_DIMENSIONS') or {}).get('AREA_OFICIAL_HA'):
            falta.append('OFFICIAL_AREA_NOT_CLIENT_SAFE')
        o['WHAT_IS_MISSING'] = falta
        o['WHAT_IS_MISSING_LAW'] = (
            'a lista do que falta e a pauta da proxima coleta. INTENSITY e '
            'RECURRENCE aparecem em todo caso agronomico porque o boletim '
            'declara ocorrencia e nao incidencia, e porque o acervo e um '
            'retrato e nao uma serie.')
        o['EVIDENCE_ROLES'] = papel_das_evidencias(o, apoios)
        # ⚠️ A FONTE QUE RESPONDEU «QUANDO AGIR» TEM DE ESTAR NA LISTA QUE SE
        # AUDITA. Um disciplinare regional nao observa par nenhum — e por isso
        # nunca entrava em `apoios`. O cartao citava-o em WINDOW_EVIDENCE_ID e
        # nao o listava em EVIDENCE_IDS: quem fosse conferir a lista nao
        # encontrava o documento que decidiu a janela.
        #
        #     CITAR NUM CAMPO E NAO LISTAR NA EVIDENCIA E ESCONDER A FONTE
        #     ONDE SO QUEM JA SABE VAI OLHAR.
        for eid, por in ((o.get('WINDOW_EVIDENCE_ID'),
                          'DECLARA_A_CONDICAO_DA_JANELA'),
                         (o.get('WINDOW_RULE_EVIDENCE_ID'),
                          'DECLARA_A_REGRA_DO_MOMENTO')):
            if eid and eid not in o['EVIDENCE_IDS']:
                o['EVIDENCE_IDS'].append(eid)
                o['EVIDENCE_ROLES'].append({
                    'EVIDENCE_ID': eid, 'ENTITY_TYPE': 'FIELD_SIGNAL',
                    'ROLE': 'SUPPORTS_WINDOW', 'WHY_CODE': por})
        o['EVIDENCE_IDS'] = sorted(set(o['EVIDENCE_IDS']))
        o['EVIDENCE_FAMILIES'] = sorted(set(o['EVIDENCE_FAMILIES'])
                                        | {'FIELD_SIGNAL'}
                                        if o.get('WINDOW_EVIDENCE_ID')
                                        else o['EVIDENCE_FAMILIES'])
        o['EVIDENCE_ROLES'].sort(key=lambda e: e['EVIDENCE_ID'])
        o['EVIDENCE_ROLES_LAW'] = (
            'toda evidencia recebe papel, inclusive a que esfria o caso. Um '
            'sistema que so classifica evidencia a favor aprende a vender.')
        o['ACTION_BY_DEPARTMENT'] = acao_por_departamento(o, elos)
        o['INTELLIGENCE_BRIEF'] = briefing(o, matches, ativos_fonte)
        o['INTELLIGENCE_BRIEF_LAW'] = (
            'o briefing sai em CODIGO mais VALORES, nunca em frase pronta: '
            'frase com variavel dentro e frase nova a cada build e nasce sem '
            'traducao. Os textos fixos vivem no cabecalho da colecao.')
        o['ACTION_BY_DEPARTMENT_LAW'] = (
            'cada departamento e convocado por um FATO, e o fato vai junto em '
            'WHY_CODE. SUPPLY so entra com data regulatoria publicada sobre '
            'ativo ligado ao caso: pressao agronomica NAO e pedido, e convocar '
            'Supply sem fato seria inventar demanda.')
        brutos.append((o, apoios))

    # ══ O1 · PRESSÃO DE CAMPO ════════════════════════════════════════════════
    # ⚠️ O PAR AGORA É O QUE A FONTE OBSERVOU, e não o cruzamento de duas listas.
    # A versão anterior tomava todas as culturas do boletim × todos os alvos do
    # boletim: um documento com dez culturas e um alvo normalizado produzia dez
    # pares, e daí saíam «beterraba × ticchiolatura» e «soja × ticchiolatura».
    # O que impedia esses pares de virarem cartão não era um portão — era a
    # tabela de rótulo, que por acaso não tinha autorização para eles. A sanidade
    # agronômica estava sendo feita por acidente.
    #
    #     LISTA DE CULTURAS × LISTA DE ALVOS NÃO É OBSERVAÇÃO.
    #     O PAR EXISTE ONDE A FONTE O ESCREVEU JUNTO.
    # ⚠️ E O CASO É POR REGIÃO, porque o serviço fitossanitário é regional.
    # Medido: 7 dos 12 pares observados têm DIREÇÃO DIFERENTE em regiões
    # diferentes — a Emilia-Romagna manda intervir contra botrite na mesma
    # semana em que a Toscana manda suspender; a ERSA declara limiar de
    # tratamento para a piralide enquanto a Lombardia PROÍBE inseticida durante
    # a floração. Juntar as duas num caso «nacional» e depois deixar a mais
    # restritiva vencer promove geografia E apaga a oportunidade real da outra.
    #
    #     DUAS REGIÕES QUE DISCORDAM NÃO SÃO UM CASO NACIONAL:
    #     SÃO DOIS CASOS, E CADA UM ESTÁ CERTO ONDE ESTÁ.
    #
    # Um sinal sem região declarada não funda caso nenhum: ele não tem geografia
    # para alegar. Continua contando como apoio onde a região já existe.
    for (crop, alvo), pinos in sorted(pares_ix.items()):
        por_regiao = defaultdict(list)
        for p in pinos:
            s = next((x for x in field_crop.get(crop, [])
                      if x['ID'] == p['NEED_EVIDENCE_ID']), None)
            for g in (s.get('REGION_IDS') or []) if s else []:
                por_regiao[g].append((p, s))
        rot = [r for r in lbl_crop.get(crop, []) if alvo in (r.get('ISSUE_IDS') or [])]
        if not rot:
            continue
        prods = sorted({r.get('PRODUCT_NAME') for r in rot if r.get('PRODUCT_NAME')})
        for geo, itens in sorted(por_regiao.items()):
            sin = list({s['ID']: s for _p, s in itens}.values())
            pin_geo = [p for p, _s in itens]
            esc = sin[0].get('GEOGRAPHIC_SCOPE') or 'REGIONAL'
            jan = janelas(crop, alvo, geo)
            emitir('O1_FIELD_PRESSURE', crop, alvo, geo, esc,
                   sin[:8] + jan[:3] + rot[:6],
                   VERIFIED_LABEL_MATCH if rot else LABEL_CHECK_NEEDED, prods,
                   {'PRODUTOS_COM_ROTULO': len(prods), 'SINAIS_DE_CAMPO': len(sin)},
                   {'CURRENTNESS': 2 if sin else 0, 'GEOGRAPHY': 2,
                    'AGRONOMIC': 2 if alvo else 1, 'ADAMA': 2 if rot else 0,
                    'MULTI_SOURCE': min(2, len({s.get('SOURCE_IDS', [None])[0]
                                                for s in sin})),
                    'ACTIONABILITY': 2 if jan else 1},
                   ['MARKET_DEVELOPMENT', 'COMMERCIAL', 'SCIENCE_TECHNICAL'],
                   rotulos=rot, pinos=pin_geo)

    # ══ O2 · MOMENTO DE MERCADO ══════════════════════════════════════════════
    for crop in sorted(set(mkt_crop) | set(econ_crop)):
        mk = [m for m in mkt_crop.get(crop, [])
              if m.get('COMMODITY_STAGE') != 'PROCESSED_PRODUCT']
        ec = econ_crop.get(crop, [])
        rot = lbl_crop.get(crop, [])
        if not (mk or ec) or not rot:
            continue
        prods = sorted({r.get('PRODUCT_NAME') for r in rot if r.get('PRODUCT_NAME')})
        emitir('O2_MARKET_MOMENT', crop, None, 'GEO_ITALY', 'NACIONAL',
               mk[:6] + ec[:3] + rot[:6],
               VERIFIED_LABEL_MATCH if rot else RELATED_PORTFOLIO, prods,
               {'PRODUTOS_COM_ROTULO': len(prods), 'OBSERVACOES_DE_MERCADO': len(mk),
                'LINHAS_DE_PESO_ECONOMICO': len(ec)},
               {'CURRENTNESS': 2 if mk else 1, 'GEOGRAPHY': 1, 'AGRONOMIC': 1,
                'ADAMA': 2 if rot else 0,
                'MULTI_SOURCE': min(2, (1 if mk else 0) + (1 if ec else 0)),
                'ACTIONABILITY': 1},
               ['MARKET_DEVELOPMENT', 'PORTFOLIO', 'COMMERCIAL'], rotulos=rot)

    # ══ O3 · RESISTÊNCIA / MoA ═══════════════════════════════════════════════
    for crop, rs in sorted(res_crop.items()):
        alvos = {i for r in rs for i in (r.get('ISSUE_IDS') or [])}
        for alvo in sorted(alvos) or [None]:
            r0 = [r for r in rs if not alvo or alvo in (r.get('ISSUE_IDS') or [])]
            # o sinal de campo do par vem do par OBSERVADO, nunca do inventario
            ids_par = {p['NEED_EVIDENCE_ID'] for p in pares_ix.get((crop, alvo), [])}
            camp = [s for s in field_crop.get(crop, []) if s['ID'] in ids_par]
            rot = [r for r in lbl_crop.get(crop, [])
                   if not alvo or alvo in (r.get('ISSUE_IDS') or [])]
            regs = {re.sub(r'\D', '', str(r.get('REGISTRATION_NUMBER') or '')).lstrip('0').zfill(6)
                    for r in rot}
            ais = [ai_por_id.get(x['ACTIVE_INGREDIENT_ID']) for g in regs
                   for x in ai_por_prod.get(g, []) if x.get('ACTIVE_INGREDIENT_ID') in ai_por_id]
            ais = [a for a in ais if a]
            if not r0 or not rot:
                continue
            moas = sorted({m for a in ais for m in
                           (a.get('HRAC'), a.get('IRAC'), a.get('FRAC')) if m})
            emitir('O3_RESISTANCE_MOA', crop, alvo, 'GEO_ITALY', 'NACIONAL',
                   r0[:6] + camp[:4] + rot[:6] + ais[:6],
                   VERIFIED_LABEL_MATCH if rot else LABEL_CHECK_NEEDED,
                   sorted({r.get('PRODUCT_NAME') for r in rot if r.get('PRODUCT_NAME')}),
                   {'MODOS_DE_ACAO': moas, 'REGISTOS_DE_RESISTENCIA': len(r0),
                    'SINAIS_DE_CAMPO': len(camp)},
                   {'CURRENTNESS': 2 if camp else 0, 'GEOGRAPHY': 1,
                    'AGRONOMIC': 2 if alvo else 1, 'ADAMA': 2 if moas else 1,
                    'MULTI_SOURCE': min(2, (1 if camp else 0) + (1 if ais else 0)),
                    'ACTIONABILITY': 1},
                   ['SCIENCE_TECHNICAL', 'MARKET_DEVELOPMENT', 'PORTFOLIO'],
                   rotulos=rot, pinos=pares_ix.get((crop, alvo), []))

    # ══ O4 · ABERTURA COMPETITIVA ════════════════════════════════════════════
    for crop, ats in sorted(comp_crop.items()):
        rot = lbl_crop.get(crop, [])
        if not rot or len(ats) < 3:
            continue
        emitir('O4_COMPETITIVE_OPENING', crop, None, 'GEO_ITALY', 'NACIONAL',
               ats[:8] + rot[:6],
               VERIFIED_LABEL_MATCH if rot else RELATED_PORTFOLIO,
               sorted({r.get('PRODUCT_NAME') for r in rot if r.get('PRODUCT_NAME')}),
               {'PECAS_DE_CONCORRENTE': len(ats), 'PRODUTOS_COM_ROTULO': len(rot)},
               {'CURRENTNESS': 2, 'GEOGRAPHY': 1, 'AGRONOMIC': 1,
                'ADAMA': 2 if rot else 0, 'MULTI_SOURCE': 2 if len(ats) > 5 else 1,
                'ACTIONABILITY': 1},
               ['MARKETING', 'MARKET_DEVELOPMENT', 'COMMERCIAL'], rotulos=rot)

    # ══ O5 · PREPARAÇÃO REGULATÓRIA ══════════════════════════════════════════
    for f in sorted(cs['REGULATORY-FUTURE-FACTS'], key=lambda x: x['ID']):
        regs = [r for r in (f.get('ITALIAN_REGISTRATIONS') or [])]
        prods = [reg_por_num.get(re.sub(r'\D', '', str(r)).lstrip('0').zfill(6))
                 for r in regs]
        prods = [p for p in prods if p]
        if not prods:
            continue
        ai = ai_por_id.get(f.get('ACTIVE_INGREDIENT_ID'))
        rot = [r for r in cs['PRODUCT-RELATIONSHIPS']
               if re.sub(r'\D', '', str(r.get('REGISTRATION_NUMBER') or '')).lstrip('0').zfill(6)
               in {re.sub(r'\D', '', str(x)).lstrip('0').zfill(6) for x in regs}]
        crops = sorted({c for r in rot for c in (r.get('CROP_IDS') or [])})
        d = DT.analisar(('EU_EXPIRATION_OF_APPROVAL', f.get('EU_EXPIRATION_OF_APPROVAL')))
        dias = (date.fromisoformat(d['END_DATE']) - HOJE).days if d['END_DATE'] else None
        o_ap = [f] + prods[:6] + ([ai] if ai else []) + rot[:4]
        emitir('O5_REGULATORY_PREPARATION', crops[0] if len(crops) == 1 else None,
               None, 'GEO_EU', 'EUROPEU', o_ap,
               VERIFIED_LABEL_MATCH if rot else RELATED_PORTFOLIO,
               sorted({p.get('NAME') for p in prods if p.get('NAME')}),
               {'SUBSTANCIA': f.get('ACTIVE_INGREDIENT'),
                'DATA_LIMITE_UE': f.get('EU_EXPIRATION_OF_APPROVAL'),
                'PRODUTOS_ADAMA': len(prods), 'CULTURAS_DE_ROTULO': len(crops),
                'DIAS_ATE_A_DATA': dias},
               {'CURRENTNESS': 1, 'GEOGRAPHY': 1, 'AGRONOMIC': 1 if crops else 0,
                'ADAMA': 2 if rot else 1, 'MULTI_SOURCE': 2 if ai else 1,
                'ACTIONABILITY': 2 if dias and dias < 540 else 1},
               ['REGULATORY', 'PORTFOLIO', 'SUPPLY', 'MARKET_DEVELOPMENT'],
               rotulos=rot)

    # ══ O6 · CIÊNCIA → CAMPO ═════════════════════════════════════════════════
    for crop, sc in sorted(sci_crop.items()):
        camp = field_crop.get(crop, [])
        rot = lbl_crop.get(crop, [])
        if not camp or not rot or len(sc) < 2:
            continue
        emitir('O6_SCIENCE_TO_FIELD', crop, None, 'GEO_ITALY', 'NACIONAL',
               sc[:6] + camp[:4] + rot[:4],
               VERIFIED_LABEL_MATCH if rot else RELATED_PORTFOLIO,
               sorted({r.get('PRODUCT_NAME') for r in rot if r.get('PRODUCT_NAME')}),
               {'TRABALHOS_CIENTIFICOS': len(sc), 'SINAIS_DE_CAMPO': len(camp),
                'PRODUTOS_COM_ROTULO': len(rot)},
               {'CURRENTNESS': 2 if camp else 0, 'GEOGRAPHY': 1, 'AGRONOMIC': 1,
                'ADAMA': 2 if rot else 0, 'MULTI_SOURCE': 2, 'ACTIONABILITY': 1},
               ['SCIENCE_TECHNICAL', 'MARKET_DEVELOPMENT'], rotulos=rot)

    # ── D · a extensao regional do par, que so se sabe olhando todos ─────────
    # Quantas regioes distintas trazem ESTE par cultura x alvo. E dimensao de
    # tamanho — recorrencia geografica — e nao se pode calcular caso a caso:
    # depende do conjunto. Por isso e a ultima coisa que o motor preenche.
    regioes = defaultdict(set)
    for o, _ev in brutos:
        if o.get('TARGET'):
            regioes[(o['CROP'], o['TARGET'])].add(o['GEOGRAPHY'])
    for o, _ev in brutos:
        d = o.get('COMMERCIAL_MAGNITUDE_DIMENSIONS')
        if d is not None:
            d['REGIOES_DO_PAR'] = (len(regioes[(o['CROP'], o['TARGET'])])
                                   if o.get('TARGET') else None)
    return brutos, rejeitados, C, cs


def gravar(brutos, C, cs):
    """Dedup determinístico, tradução dos campos de tela e os cinco artefatos."""
    porid = {}
    colapsados = 0
    for o, ev in brutos:
        if o['ID'] in porid:
            # A MESMA SITUACAO NAO VIRA DOIS CARTOES: o apoio reforca o caso.
            a, aev = porid[o['ID']]
            a['EVIDENCE_IDS'] = sorted(set(a['EVIDENCE_IDS']) | set(o['EVIDENCE_IDS']))
            a['EVIDENCE_FAMILIES'] = sorted(set(a['EVIDENCE_FAMILIES']) |
                                            set(o['EVIDENCE_FAMILIES']))
            a['MERGED_FROM'] = a.get('MERGED_FROM', 0) + 1
            colapsados += 1
            continue
        porid[o['ID']] = (o, ev)

    regs, rejeitados = [], []
    for oid in sorted(porid):
        o, ev = porid[oid]
        it, en = ROTULO[o['OPPORTUNITY_STATE']]
        r = {
            'ID': o['ID'], 'ENTITY_TYPE': 'OPPORTUNITY',
            'PROVENANCE': 'REAL_DERIVED', 'QA_STATUS': 'EVIDENCE_DERIVED',
            # ⚠️ SEMPRE false, e isto NAO e rebaixamento: e o portao.
            # A juncao e leitura nossa, como no cruzamento. O que vai a tela e
            # decidido por RENDERABLE_WITH_METHOD, e o metodo vai junto.
            'CLIENT_SAFE': False,
            'RENDERABLE_WITH_METHOD': o['OPPORTUNITY_STATE'] == CONFIRMADA,
            'WHY_NOT_CLIENT_SAFE':
                'oportunidade e LEITURA NOSSA sobre fatos de terceiros. A regra vale '
                'para o que nos mesmos produzimos, ou nao e regra. Cada apoio citado '
                'em EVIDENCE_IDS passou pelo portao; a juncao nao passa, e por isso '
                'vai a tela com o metodo declarado ao lado.',
            'SOURCE_IDS': sorted({s for e in ev for s in (e.get('SOURCE_IDS') or [])}) or ['SRC_NAO_DECLARADA'],
            'SOURCE_URLS': sorted({u for e in ev for u in (e.get('SOURCE_URLS') or [])})[:12],
            'REFERENCE_DATE': HOJE.isoformat(),
            'CROP_IDS': [o['CROP']] if o['CROP'] else [],
            'ISSUE_IDS': [o['TARGET']] if o['TARGET'] else [],
            'REGION_IDS': [o['GEOGRAPHY']], 'GEOGRAPHIC_SCOPE': o['GEOGRAPHY_SCOPE'],
            'OPPORTUNITY_STATE': o['OPPORTUNITY_STATE'],
            'OPPORTUNITY_LABEL_IT': it, 'OPPORTUNITY_LABEL_EN': en,
            'ARCHETYPE': o['ARCHETYPE'], 'ARCHETYPE_MEANS': ARQ[o['ARCHETYPE']],
            'STATUS': o['STATUS'],
            'STATUS_LAW': 'o estado e INTERPRETACAO SINTONIA derivada da CADEIA de '
                          'quatro elos, nunca da idade do sinal sozinha. Nunca infere '
                          'demanda de revenda, sell-in, estoque, pedido nem pipeline '
                          'interno.',
            'ACTION_CHAIN_LINKS': o['ACTION_CHAIN_LINKS'],
            'ACTION_CHAIN_REQUIRES': ELO_EXIGE,
            'WHY_NOW_CODES': o['WHY_NOW_CODES'],
            'WHY_NOW_CHAIN': o['WHY_NOW_CHAIN'],
            'WHY_NOW_LAW': o['WHY_NOW_LAW'],
            'SIGNAL_CURRENCY': o['SIGNAL_CURRENCY'],
            'COMMERCIAL_TIMING_BASIS': o['COMMERCIAL_TIMING_BASIS'],
            'WINDOW_TYPE': o['WINDOW_TYPE'],
            'WINDOW_CONDITION': o['WINDOW_CONDITION'],
            'WINDOW_DEFINED': o['WINDOW_DEFINED'],
            'WINDOW_OPEN_NOW': o['WINDOW_OPEN_NOW'],
            'WINDOW_OPEN_NOW_METHOD': o['WINDOW_OPEN_NOW_METHOD'],
            'WINDOW_EVIDENCE_ID': o['WINDOW_EVIDENCE_ID'],
            'PHENOLOGY_DECLARED': o['PHENOLOGY_DECLARED'],
            'WINDOW_TYPE_LAW': o['WINDOW_TYPE_LAW'],
            # três perguntas, três respostas, três donos — nunca empilhadas
            'PEST_STAGE_STATE': o['PEST_STAGE_STATE'],
            'PEST_STAGE_EVIDENCE_ID': o['PEST_STAGE_EVIDENCE_ID'],
            'PEST_STAGE_EXCERPT': o['PEST_STAGE_EXCERPT'],
            'PEST_STAGE_LAW': o['PEST_STAGE_LAW'],
            'ACTION_RECOMMENDATION_STATE': o['ACTION_RECOMMENDATION_STATE'],
            'ACTION_RECOMMENDATION_EVIDENCE_ID': o['ACTION_RECOMMENDATION_EVIDENCE_ID'],
            'ACTION_RECOMMENDATION_EXCERPT': o['ACTION_RECOMMENDATION_EXCERPT'],
            'ACTION_RECOMMENDATION_LAW': o['ACTION_RECOMMENDATION_LAW'],
            'THRESHOLD_STATE': o['THRESHOLD_STATE'],
            'THRESHOLD_STATE_EVIDENCE_ID': o['THRESHOLD_STATE_EVIDENCE_ID'],
            'THRESHOLD_STATE_LAW': o['THRESHOLD_STATE_LAW'],
            'WINDOW_RULE_STATE': o['WINDOW_RULE_STATE'],
            'WINDOW_RULE_EVIDENCE_ID': o['WINDOW_RULE_EVIDENCE_ID'],
            'WINDOW_RULE_CONDITION': o['WINDOW_RULE_CONDITION'],
            'WINDOW_RULE_STATE_LAW': o['WINDOW_RULE_STATE_LAW'],
            'ACTIVE_INGREDIENT_IDS': o['ACTIVE_INGREDIENT_IDS'],
            'ACTIVE_INGREDIENT_NAMES': o['ACTIVE_INGREDIENT_NAMES'],
            'MODE_OF_ACTION_CODES': o['MODE_OF_ACTION_CODES'],
            'MODE_OF_ACTION_STATE': o['MODE_OF_ACTION_STATE'],
            'APPLICATION_STATE': o['APPLICATION_STATE'],
            'LABEL_QUOTES': o['LABEL_QUOTES'],
            'PRODUCT_RESTRICTIONS': o['PRODUCT_RESTRICTIONS'],
            'PRODUCT_RESTRICTIONS_LAW': o['PRODUCT_RESTRICTIONS_LAW'],
            'COMMERCIAL_MAGNITUDE': o['COMMERCIAL_MAGNITUDE'],
            'COMMERCIAL_MAGNITUDE_DIMENSIONS': o['COMMERCIAL_MAGNITUDE_DIMENSIONS'],
            'COMMERCIAL_MAGNITUDE_LAW': o['COMMERCIAL_MAGNITUDE_LAW'],
            'SIGNAL_CONFIDENCE': o['SIGNAL_CONFIDENCE'],
            'WINDOW_CONFIDENCE': o['WINDOW_CONFIDENCE'],
            'PRODUCT_MATCH_CONFIDENCE': o['PRODUCT_MATCH_CONFIDENCE'],
            'CONFIDENCE_LAW': o['CONFIDENCE_LAW'],
            'ACTION_BY_DEPARTMENT': o['ACTION_BY_DEPARTMENT'],
            'ACTION_BY_DEPARTMENT_LAW': o['ACTION_BY_DEPARTMENT_LAW'],
            'PORTFOLIO_MATCHES': o['PORTFOLIO_MATCHES'],
            'PRIMARY_MATCH': o['PRIMARY_MATCH'],
            'PRIMARY_MATCH_REASON': o['PRIMARY_MATCH_REASON'],
            'SOURCE_NAMED_ACTIVES': o['SOURCE_NAMED_ACTIVES'],
            'PORTFOLIO_LAW': o['PORTFOLIO_LAW'],
            'EVIDENCE_ROLES': o['EVIDENCE_ROLES'],
            'EVIDENCE_ROLES_LAW': o['EVIDENCE_ROLES_LAW'],
            'INTELLIGENCE_BRIEF': o['INTELLIGENCE_BRIEF'],
            'WHAT_IS_MISSING': o['WHAT_IS_MISSING'],
            'WHAT_IS_MISSING_LAW': o['WHAT_IS_MISSING_LAW'],
            'INTELLIGENCE_BRIEF_LAW': o['INTELLIGENCE_BRIEF_LAW'],
            'CROP': o['CROP'], 'TARGET': o['TARGET'], 'GEOGRAPHY': o['GEOGRAPHY'],
            'WINDOW_START': o['WINDOW_START'], 'WINDOW_END': o['WINDOW_END'],
            'DAYS_REMAINING': o['DAYS_REMAINING'], 'WINDOW_STATE': o['WINDOW_STATE'],
            'SIGNAL_DATE': o['SIGNAL_DATE'], 'SIGNAL_AGE_DAYS': o['SIGNAL_AGE_DAYS'],
            'WINDOW_LAW': 'WINDOW_* e a janela de APLICACAO, lida de campo declarado; '
                          'quando nao ha, fica UNKNOWN e nao se inventa. SIGNAL_DATE e '
                          'a data do documento que sustenta o caso — diz se o sinal e '
                          'corrente, nao quando aplicar.',
            'WHY_NOW': o['WHY_NOW'], 'ADAMA_RELEVANCE': o['ADAMA_RELEVANCE'],
            'NUMBERS': o['NUMBERS'],
            'NUMBERS_LAW': 'os numeros vivem aqui, fora da frase: frase com variavel '
                           'dentro e frase nova a cada build e nunca fica traduzida.',
            'PRODUCT_LINK_STATE': o['PRODUCT_LINK_STATE'],
            'PRODUCT_RELATIONSHIPS': o['PRODUCT_RELATIONSHIPS'],
            'EVIDENCE_IDS': o['EVIDENCE_IDS'],
            'EVIDENCE_FAMILIES': o['EVIDENCE_FAMILIES'],
            'EVIDENCE_COUNT': len(o['EVIDENCE_IDS']),
            'WHAT_IT_PROVES': o['WHAT_IT_PROVES'],
            'WHAT_IT_DOES_NOT_PROVE': o['WHAT_IT_DOES_NOT_PROVE'],
            'CONFIDENCE': o['CONFIDENCE'],
            'OPPORTUNITY_SCORE': o['OPPORTUNITY_SCORE'],
            'SCORE_DIMENSIONS': o['SCORE_DIMENSIONS'],
            'SCORE_LAW': 'o score ORDENA, nao prova. Um 12 com portao fechado continua '
                         'sendo um 12 com portao fechado.',
            'BLOCKING_GATES': o['BLOCKING_GATES'],
            'RED_TEAM_FINDINGS': o['RED_TEAM_FINDINGS'],
            'ACTION_MAP': o['ACTION_MAP'],
            'ACTION_MAP_LAW': 'quem deve olhar isto agora e leitura de inteligencia '
                              'externa, nao prova de que o departamento deva agir.',
            # O motor roda no passo 5e, DEPOIS do carimbo de origem do passo 4:
            # o registro tem de trazer a propria camada, ou nasce sem procedencia.
            # E a camada e DERIVED_V2_1 porque a oportunidade e leitura NOSSA — nao
            # veio de fonte nenhuma, nasceu aqui.
            'ORIGIN_LAYER': 'DERIVED_V2_1',
            'MERGED_FROM': o.get('MERGED_FROM', 0),
            'IDENTITY_KEY': o['IDENTITY_KEY'],

            # ── A CAMADA COMERCIAL · V1.1 ────────────────────────────────────
            # Independente de OPPORTUNITY_STATE, e ao lado dele. Um caso pode
            # ser CONFIRMADO e nao vender; pode vender com um portao aberto.
            'COMMERCIAL_PRIORITY': o['COMMERCIAL_PRIORITY'],
            'COMMERCIAL_PRIORITY_MEANS': o['COMMERCIAL_PRIORITY_MEANS'],
            'COMMERCIAL_PRIORITY_LAW': o['COMMERCIAL_PRIORITY_LAW'],
            'EXTERNAL_MATERIAL_READY': o['EXTERNAL_MATERIAL_READY'],
            'EXTERNAL_BLOCKER_CODES': o['EXTERNAL_BLOCKER_CODES'],
            'EXTERNAL_BLOCKERS': o['EXTERNAL_BLOCKERS'],
            'EXTERNAL_MATERIAL_LAW': o['EXTERNAL_MATERIAL_LAW'],
            'WHY_COMMERCIAL': o['WHY_COMMERCIAL'],
            'WHY_COMMERCIAL_CODES': o['WHY_COMMERCIAL_CODES'],
            'COMMERCIAL_DOES_NOT_PROVE': o['COMMERCIAL_DOES_NOT_PROVE'],

            'NEED_DIRECTION': o['NEED_DIRECTION'],
            'NEED_EVIDENCE_ID': o['NEED_EVIDENCE_ID'],
            'NEED_EXCERPT': o['NEED_EXCERPT'],
            'NEED_METHOD': o['NEED_METHOD'],
            'NEED_FIELD': o['NEED_FIELD'],
            'NEED_AMBIGUITY_CODES': o['NEED_AMBIGUITY_CODES'],
            'NEED_AMBIGUITY': o['NEED_AMBIGUITY'],
            'NEED_LAW': o['NEED_LAW'],

            'MATCHED_COMMERCIAL_PRODUCT_IDS': o['MATCHED_COMMERCIAL_PRODUCT_IDS'],
            'MATCHED_COMMERCIAL_PRODUCT_NAMES': o['MATCHED_COMMERCIAL_PRODUCT_NAMES'],
            'COMMERCIAL_PRODUCT_COUNT': o['COMMERCIAL_PRODUCT_COUNT'],
            'COMMERCIAL_MATCH_LAW': o['COMMERCIAL_MATCH_LAW'],

            'CLAIM_GEOGRAPHY': o['CLAIM_GEOGRAPHY'],
            'FIELD_GEOGRAPHY': o['FIELD_GEOGRAPHY'],
            'PRODUCT_AUTHORIZATION_GEOGRAPHY': o['PRODUCT_AUTHORIZATION_GEOGRAPHY'],
            'CLAIM_GEOGRAPHY_HOLDS': o['CLAIM_GEOGRAPHY_HOLDS'],
            'CLAIM_GEOGRAPHY_WHY': o['CLAIM_GEOGRAPHY_WHY'],
            'GEOGRAPHY_LAW': o['GEOGRAPHY_LAW'],

            'WINDOW_FIELD': o['WINDOW_FIELD'], 'WINDOW_KIND': o['WINDOW_KIND'],
            'COMMERCIAL_WINDOW': o['COMMERCIAL_WINDOW'],
            'COMMERCIAL_WINDOW_FROM': o['COMMERCIAL_WINDOW_FROM'],
            'COMMERCIAL_WINDOW_LAW': o['COMMERCIAL_WINDOW_LAW'],
        }
        if o.get('MERGED_FROM'):
            r['DEDUP_NOTE'] = ('%d registros adicionais descreviam a MESMA situacao e '
                               'reforcam este caso em vez de criar cartoes novos.'
                               % o['MERGED_FROM'])
        regs.append(r)

    ev_out = {'LEI': 'toda evidencia citada por ID canonico. Nenhuma juncao por texto.',
              'POR_OPORTUNIDADE': {r['ID']: r['EVIDENCE_IDS'] for r in regs}}
    return regs, ev_out, colapsados


if __name__ == '__main__':
    brutos, _rej, C, cs = main()
    regs, ev_out, colapsados = gravar(brutos, C, cs)
    conf = [r for r in regs if r['OPPORTUNITY_STATE'] == CONFIRMADA]
    cand = [r for r in regs if r['OPPORTUNITY_STATE'] == CANDIDATA]
    rejeitados = [{'ID': r['ID'], 'ARCHETYPE': r['ARCHETYPE'],
                   'POR_QUE': r['RED_TEAM_FINDINGS'] + r['BLOCKING_GATES']}
                  for r in cand if r['RED_TEAM_FINDINGS']]

    hdr = {'COLLECTION': 'OPPORTUNITIES', 'FILE': 'OPPORTUNITIES.json',
           'SCHEMA_VERSION': 'V2.1', 'BUILT_AT': HOJE.isoformat(), 'PRIMARY_KEY': 'ID',
           'SOURCE_OF_TRUTH': 'motor de oportunidades sobre o proprio V2.1',
           'COUNT_TOTAL': len(regs), 'COUNT_CLIENT_SAFE': 0,
           'COUNT_CONFIRMED': len(conf), 'COUNT_CANDIDATE': len(cand),
           'COUNT_RENDERABLE_WITH_METHOD': len(conf),
           'BY_ARCHETYPE': dict(Counter(r['ARCHETYPE'] for r in regs)),
           'BY_STATUS': dict(Counter(r['STATUS'] for r in regs)),
           # ── a segunda pergunta, contada ao lado da primeira ──────────────
           'BY_COMMERCIAL_PRIORITY':
               dict(Counter(r['COMMERCIAL_PRIORITY'] for r in regs)),
           'BY_NEED_DIRECTION':
               dict(Counter(r['NEED_DIRECTION'] for r in regs)),
           'BY_EXTERNAL_MATERIAL_READY':
               dict(Counter(r['EXTERNAL_MATERIAL_READY'] for r in regs)),
           'COUNT_WITH_COMMERCIAL_PRODUCT':
               sum(1 for r in regs if r['COMMERCIAL_PRODUCT_COUNT']),
           'COMMERCIAL_LAW':
               'COMMERCIAL_PRIORITY nao substitui OPPORTUNITY_STATE: um diz se a '
               'leitura se sustenta, o outro se ela vende. Sao perguntas '
               'diferentes, e um caso pode ser CONFIRMADO e nao vender.',
           'DUPLICATES_COLLAPSED': colapsados,
           'BY_ORIGIN': {'DERIVED_V2_1': len(regs)},
           'BY_QA': {'EVIDENCE_DERIVED': len(regs)},
           'LAW': 'CLIENT_SAFE=false em TODAS, e isso nao e rebaixamento: e o portao. '
                  'A juncao e leitura nossa. RENDERABLE_WITH_METHOD separa a confirmada '
                  'da que ainda tem portao fechado. CRUZAMENTO NAO E OPORTUNIDADE, E '
                  'OPORTUNIDADE NAO E PEDIDO.',
           'LOCALIZED_FIELDS': ['WHY_NOW', 'ADAMA_RELEVANCE', 'WHAT_IT_PROVES',
                                'WHAT_IT_DOES_NOT_PROVE'],
           'RECORDS': regs}
    json.dump(hdr, open(os.path.join(ING, 'OPPORTUNITIES.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    json.dump(ev_out, open(os.path.join(ING, 'OPPORTUNITY-EVIDENCE.json'), 'w',
                           encoding='utf-8'), ensure_ascii=False, indent=1)
    json.dump({'ARQUETIPOS': ARQ, 'PORTOES': list('ABCDEFGH'),
               'ESTADOS_DE_PRODUTO': [VERIFIED_LABEL_MATCH, RELATED_PORTFOLIO,
                                      LABEL_CHECK_NEEDED],
               'ESTADOS_DE_ACAO': list(ESTADOS_DE_ACAO),
               'ESTADOS_DE_ACAO_LEI': (
                   'ACT_NOW exige os quatro elos de ACTION_CHAIN_REQUIRES. '
                   'VALIDATE_NOW e o estado de quem tem necessidade declarada e '
                   'produto ligado e NAO tem janela: o que falta tem nome. '
                   'A idade do sinal vive em SIGNAL_CURRENCY e nunca vira '
                   'janela.'),
               'ACTION_CHAIN_REQUIRES': ELO_EXIGE,
               'WINDOW_TYPES': list(JN.TIPOS),
               'WINDOW_TYPES_AGRONOMIC': list(JN.AGRONOMICOS),
               'INTELLIGENCE_BRIEF_TEMPLATES': BRIEFING,
               'EVIDENCE_ROLES_VOCABULARY': list(PAPEIS),
               'PRIORIDADES_COMERCIAIS': {p: CM.SIGNIFICADO[p]
                                          for p in CM.PRIORIDADES},
               'DIRECOES_DE_NECESSIDADE': NE.ESTADOS,
               'METODOS_DE_PAR': list(NE.FORCA_DO_METODO),
               'LEI_DO_PAR': 'o par cultura x alvo e o que a fonte OBSERVOU. '
                             'Lista de culturas x lista de alvos e produto '
                             'cartesiano, nao observacao.',
               'LEI_DA_PRIORIDADE_COMERCIAL':
                   'portoes semanticos, nunca soma de pontos. Sem numero minimo '
                   'de familias externas: corroboracao e amplificador, nao '
                   'contador cego.',
               'SCORE': {'DIMENSOES': ['CURRENTNESS', 'GEOGRAPHY', 'AGRONOMIC',
                                       'ADAMA', 'MULTI_SOURCE', 'ACTIONABILITY'],
                         'MAXIMO': 12,
                         'LEI': 'ordena, nao prova'},
               'LEI_DO_CLIENT_SAFE':
                   'oportunidade e derivacao: CLIENT_SAFE=false sempre.'},
              open(os.path.join(ING, 'OPPORTUNITY-RULES.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    json.dump({'LEI': 'o red team so derruba; nunca confirma.',
               'TOTAL': len(rejeitados), 'REJEICOES': rejeitados},
              open(os.path.join(ING, 'OPPORTUNITY-REJECTIONS.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print('== MOTOR DE OPORTUNIDADES ==')
    print('  confirmadas %d · candidatas %d · total %d · colapsadas %d'
          % (len(conf), len(cand), len(regs), colapsados))
    print('  por arquetipo: %s' % dict(Counter(r['ARCHETYPE'] for r in regs)))
    print('  por estado   : %s' % dict(Counter(r['STATUS'] for r in regs)))
    print('  derrubadas pelo red team: %d' % len(rejeitados))
    print('  PRIORIDADE COMERCIAL: %s'
          % dict(Counter(r['COMMERCIAL_PRIORITY'] for r in regs)))
    print('  direcao da necessidade: %s'
          % dict(Counter(r['NEED_DIRECTION'] for r in regs)))
    print('  MATERIAL EXTERNO: %s'
          % dict(Counter(r['EXTERNAL_MATERIAL_READY'] for r in regs)))
    print('  com produto do catalogo comercial: %d de %d'
          % (sum(1 for r in regs if r['COMMERCIAL_PRODUCT_COUNT']), len(regs)))
