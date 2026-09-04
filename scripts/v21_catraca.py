#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A CATRACA — a porta única entre o acervo e o publicável.

    python3 scripts/v21_catraca.py

    DADO BRUTO NÃO É PUBLICÁVEL.

O material pode ficar no acervo sem passar pela inteligência: guardar é barato e
jogar fora é irreversível. O que ele NÃO pode é atravessar para o lado
publicável sem ter passado. Esta é a diferença entre um arquivo e uma
afirmação.

O QUE ESTA CAMADA **NÃO** É
----------------------------
Não é um segundo motor de oportunidades, e não substitui a régua comercial.
Ela não pontua, não classifica, não descobre nada e — a propriedade que vale
provar — **nunca promove**:

    A CATRACA SÓ SEGURA. NUNCA EMPURRA.

`PUBLICATION_STATE` nasce de `EXTERNAL_MATERIAL_READY`, que é decisão de
`v21_comercial.externo()` e continua sendo dele. A catraca só pode REBAIXAR o
que aquele dono já decidiu, e só por um motivo: material citado que não
completou uma etapa obrigatória da trilha. O teste `test_catraca_nunca_promove`
existe para que essa propriedade seja verificada, não prometida.

⚠️ E ELA TAMBÉM NÃO É DONA DO CARTÃO. `STATUS`, `WHY_NOW_CHAIN`,
`ACTION_CHAIN_LINKS`, `WINDOW_DEFINED`, `WINDOW_OPEN_NOW`, `WINDOW_TYPE`,
`PORTFOLIO_MATCHES`, `PRIMARY_MATCH`, `ACTION_BY_DEPARTMENT`, `EVIDENCE_ROLES`,
`INTELLIGENCE_BRIEF` e `WHAT_IS_MISSING` são de `v21_oportunidades.py` — e a
reconciliação de linhagem provou por que isso importa: uma camada paralela que
recalculava «por que agora» sem conhecer a janela agronômica devolvia
`VALIDATE_NOW` onde o motor, com os quatro elos fechados, devolve `ACT_NOW`.

    DUAS RESPOSTAS PARA A MESMA PERGUNTA NÃO SÃO REDUNDÂNCIA: SÃO UM BUG
    ESPERANDO A HORA DE APARECER NA TELA.

AS CINCO ETAPAS OBRIGATÓRIAS
-----------------------------
A trilha universal, escrita como a missão a escreveu, tem etapas que produzem
DADO (normalização, classificação, extração de relações) e etapas que produzem
LEITURA (cruzamento, janela, portfólio, prioridade comercial, mapa de ação).
As primeiras são do material; as segundas são da oportunidade e já têm dono.

A catraca mede as do MATERIAL, uma a uma, e por registro:

    IDENTITY_PROVENANCE   tem identidade e origem declarada
    NORMALIZATION         os eixos canônicos existem (cultura, alvo, região)
    CLASSIFICATION        tem QA_STATUS e CLIENT_SAFE booleano
    MISSION_RULER         a régua de QA não o rejeitou
    RELATION_EXTRACTION   o extrator de pares teve texto para ler

TRÊS ESTADOS POR ETAPA, E O DO MEIO É O QUE IMPORTA
----------------------------------------------------
`PASSED` · `UNKNOWN` · `FAILED`, e mais `NOT_APPLICABLE` para a etapa que não
faz sentido naquele tipo de registro.

`UNKNOWN` é o estado que esta camada existe para tornar visível.

    UM REGISTRO IGNORADO EM SILÊNCIO É PIOR QUE UM RECUSADO EM VOZ ALTA.

Quatro boletins REAIS do acervo — `IT-CAN-71D68FCB7D`, `IT-CAN-6EFC8DC91A`,
`IT-CAN-EB63AEC4AA`, `IT-CAN-49BA29FF51` — chegam hoje ao motor de
oportunidades sem nenhum texto de leitura: a prosa deles vive só em
`RESEARCH.o_que`, e `promover_research` é tudo-ou-nada. O extrator de pares não
tem o que ler, o registro não funda caso nenhum, e nada no pacote dizia isso.
A partir daqui diz: `RELATION_EXTRACTION = UNKNOWN`, com o código do motivo.

A catraca **não conserta** esse caso — consertá-lo move texto para a tela em 35
registros e é decisão de quem manda, não efeito colateral de uma medição. Ela o
torna CONTÁVEL, que é o passo que faltava.

O QUE FAZ A CADEIA PARAR
-------------------------
Três coisas, e nenhuma delas é um número que se possa afrouxar:

    V1  uma oportunidade PUBLISHABLE citando material QUARANTINED
    V2  um registro sem QA_STATUS — a classificação nunca rodou nele
    V3  uma oportunidade citando evidência que não existe no pacote
    V4  a catraca promovendo alguém (defeito nosso, não do dado)

Hoje as quatro medem zero. É de propósito: uma trava que nasce vermelha ensina
a ignorar trava. Ela nasce verde e passa a ser obrigatória a partir de agora.
"""
import json
import os
import sys
from collections import Counter, OrderedDict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ING = os.path.join(ROOT, 'build', 'ITALY-REALITY-HANDOFF-V2.1', 'DESIGN-INGEST')
OUT = os.path.join(ING, 'PUBLICATION-GATE.json')
PORTA = os.path.join(ROOT, 'build', 'ITALY-REALITY-HANDOFF-V2',
                     'CANONICAL-INTELLIGENCE.json')

sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import v21_necessidade as NEC  # noqa: E402
from v21_campos_de_lingua import campos_do_registro, e_portugues, parte_minha  # noqa: E402

# ── OS ESTADOS DE ETAPA ──────────────────────────────────────────────────────
PASSED = 'PASSED'
UNKNOWN = 'UNKNOWN'
FAILED = 'FAILED'
NOT_APPLICABLE = 'NOT_APPLICABLE'

ETAPAS = ('IDENTITY_PROVENANCE', 'NORMALIZATION', 'CLASSIFICATION',
          'MISSION_RULER', 'RELATION_EXTRACTION', 'LOCALIZATION')

# ── OS ESTADOS DE SAÍDA DO MATERIAL ──────────────────────────────────────────
MATERIAL_PASSED = 'PASSED'              # completou todas as etapas aplicáveis
MATERIAL_INCOMPLETE = 'INCOMPLETE'      # alguma etapa ficou UNKNOWN
MATERIAL_QUARANTINED = 'QUARANTINED'    # alguma etapa FALHOU

# ── OS ESTADOS DE SAÍDA DA OPORTUNIDADE ──────────────────────────────────────
PUBLISHABLE = 'PUBLISHABLE'
VALIDATION_REQUIRED = 'VALIDATION_REQUIRED'
GATE_UNKNOWN = 'UNKNOWN'
QUARANTINED = 'QUARANTINED'

ESTADOS_DE_PUBLICACAO = (PUBLISHABLE, VALIDATION_REQUIRED, GATE_UNKNOWN, QUARANTINED)

# Ordem de permissividade: PUBLISHABLE é o mais permissivo. A catraca só pode
# mover para a DIREITA nesta lista, nunca para a esquerda. É assim que
# «só segura, nunca empurra» vira uma comparação de inteiros.
PERMISSIVIDADE = {PUBLISHABLE: 0, VALIDATION_REQUIRED: 1,
                  GATE_UNKNOWN: 2, QUARANTINED: 3}

# O que `EXTERNAL_MATERIAL_READY` — decisão de v21_comercial.externo() — vale
# nesta escala. A catraca começa daqui e só pode piorar.
DE_EXTERNO = {'YES': PUBLISHABLE,
              'VALIDATION_REQUIRED': VALIDATION_REQUIRED,
              'NO': VALIDATION_REQUIRED}

# ── OS MOTIVOS, POR CÓDIGO ───────────────────────────────────────────────────
# Código é dado; frase é texto. Nenhum código carrega valor variável dentro.
MOTIVO = OrderedDict([
    ('NO_ID', 'o registro não tem identidade própria.'),
    ('NO_ENTITY_TYPE', 'o registro não declara que tipo de coisa é.'),
    ('NO_PROVENANCE', 'o registro não declara procedência.'),
    ('PROVENANCE_UNRECOVERABLE', 'a procedência está declarada como não '
                                 'recuperável — é UM NÃO SEI honesto, não uma '
                                 'falha silenciosa.'),
    ('NO_SOURCE', 'o registro não cita fonte nem URL e não declara por quê.'),
    ('SENTINEL_DECLARED_ABSENCE', 'o registro é uma sentinela: existe para dar '
                                  'endereço a uma ausência já citada, e por '
                                  'isso não tem fonte própria.'),
    ('AXES_MISSING', 'os eixos canônicos (cultura, alvo, região) não existem '
                     'como campo no registro. Todas as 26 coleções de material '
                     'os trazem em 100% dos registros, então a ausência é UM '
                     'NÃO SEI sobre a normalização — não uma falha provada.'),
    ('SCOPE_MISSING', 'o registro não declara escopo geográfico.'),
    ('NO_QA_STATUS', 'o registro não tem QA_STATUS: a classificação nunca '
                     'rodou nele.'),
    ('CLIENT_SAFE_NOT_BOOLEAN', 'CLIENT_SAFE não é booleano.'),
    ('QA_REJECTED', 'a régua de QA rejeitou este registro.'),
    ('NO_TEXT_FOR_PAIR_EXTRACTION', 'o extrator de pares não tem texto para '
                                    'ler: a leitura existe só dentro de '
                                    'RESEARCH, e a promoção é tudo-ou-nada.'),
    ('READING_ONLY_IN_PORTUGUESE', 'a leitura deste registro existe só em '
                                   'português: ela não chega ao leitor italiano '
                                   'nem ao inglês. NÃO é falha de inteligência — '
                                   'é falta de tradução, e por isso UNKNOWN.'),
    ('DROPPED_AT_DOOR', 'o registro está na porta de coleta e não existe no '
                        'pacote: nenhuma coleção o recebeu, e ninguém declarou '
                        'que não o receberia.'),
])

# Tipos de registro em que a extração de relações é a etapa que decide se o
# material pode fundar oportunidade. Nos outros ela não se aplica — e
# NOT_APPLICABLE não é aprovação disfarçada: é a declaração de que a pergunta
# não cabe.
TIPOS_QUE_FUNDAM_PAR = ('FIELD_SIGNAL',)

# Arquivos que não são coleção de MATERIAL, e por que cada um está fora.
#
#   CANONICAL-INTELLIGENCE-MASTER  é o ÍNDICE sobre as coleções: os mesmos
#       registros numa projeção reduzida, sem ISSUE_IDS. Contá-lo duplicaria
#       cada material e o reprovaria pela forma do índice, não pela sua.
#   RELATIONSHIPS · CLIENT-SAFE-CROSSINGS  são CRUZAMENTOS: leitura nossa sobre
#       material que já passou aqui. Cruzamento não é material; a etapa dele é
#       de oportunidade e já tem dono em v21_crossings.py.
#   OPPORTUNITY-*  são a leitura, não a matéria-prima dela.
#
#     O ÍNDICE NÃO É UM SEGUNDO ACERVO, E O CRUZAMENTO NÃO É UM SEGUNDO FATO.
NAO_E_COLECAO = ('APP-MANIFEST.json', '_COLECOES.json', '_PARCIAL.json',
                 'CANONICAL-INTELLIGENCE-MASTER.json',
                 'RELATIONSHIPS.json', 'CLIENT-SAFE-CROSSINGS.json',
                 'OPPORTUNITIES.json', 'OPPORTUNITY-RULES.json',
                 'OPPORTUNITY-EVIDENCE.json', 'OPPORTUNITY-REJECTIONS.json',
                 'PUBLICATION-GATE.json')


# ── O CENSO DA PORTA ────────────────────────────────────────────────────────
#
# ⚠️ ESTA SEÇÃO EXISTE PORQUE A TESTEMUNHA DA TRILHA UNIVERSAL ACHOU UM BURACO.
# Injetamos uma fixture em cada uma das DEZ famílias da porta real de coleta.
# Oito atravessaram. DUAS sumiram — sem erro, sem quarentena, sem estado. E não
# eram só as fixtures: são 26 REGISTROS REAIS que estão na porta hoje e não
# existem em coleção nenhuma do pacote.
#
#     UM REGISTRO QUE ENTRA PELA PORTA E NÃO SAI EM LUGAR NENHUM NÃO FOI
#     RECUSADO: ELE DESAPARECEU. E DESAPARECER É PIOR QUE SER RECUSADO.
#
# As duas não são o mesmo caso, e por isso cada uma traz o motivo escrito:
#
#   COMMERCIAL_CATALOG (10)  são meta-registros SOBRE a própria coleta —
#       censo do catálogo, defeito de método, divergência catálogo × registro.
#       São papel de trabalho, e papel de trabalho não vira material. Os
#       produtos do catálogo entram por outra porta (IT-LASTMILE e o pacote de
#       product-intelligence), e entram: são os 51 de PRODUCTS-COMMERCIAL.
#
#   HERBICIDE_CURRENT_CONTEXT (16)  NÃO é papel de trabalho: são JANELAS
#       CORRENTES declaradas pelo serviço fitossanitário regional, por
#       província, com os ativos permitidos e as derrogações de calendário.
#       É exatamente o tipo de registro cuja ausência faz WHY_NOW=ACT_NOW ser
#       impossível em todo o pacote — porque `WINDOW_KIND=APPLICATION` não
#       existe em lugar nenhum. Ingeri-la é uma missão com coleção própria,
#       normalização própria e dono próprio; fazê-lo de passagem aqui seria
#       criar um segundo dono para a janela.
#
# O que esta camada faz é o mínimo honesto: DECLARAR as duas, contá-las, e
# tornar FATAL qualquer buraco NOVO — uma família que ninguém declarou, ou uma
# família ingerida que passe a perder registro.
FAMILIA_NAO_INGERIDA = {
    'COMMERCIAL_CATALOG':
        'meta-registro sobre a propria coleta (censo, defeito de metodo, '
        'divergencia catalogo x registro). Papel de trabalho nao e material; '
        'os produtos do catalogo entram por IT-LASTMILE e sao os 51 de '
        'PRODUCTS-COMMERCIAL.json.',
    'HERBICIDE_CURRENT_CONTEXT':
        'ABERTO. Sao janelas correntes de herbicida declaradas pelo servico '
        'fitossanitario regional, por provincia. NAO e papel de trabalho: e '
        'material de campo, e a ausencia dele e a causa medida de nao existir '
        'WINDOW_KIND=APPLICATION no pacote inteiro. Ingerir a familia exige '
        'colecao, normalizacao e dono proprios — e uma missao, nao um efeito '
        'colateral desta.',
}


def censo_da_porta(ids_no_pacote):
    """→ (por família, [violações]). Quem entrou pela porta e sumiu no caminho?"""
    if not os.path.exists(PORTA):
        return {}, ['a porta de coleta nao existe em %s' % PORTA]
    d = json.load(open(PORTA, encoding='utf-8'))
    por_fam = {}
    for r in (d.get('RECORDS') or []):
        f = r.get('FAMILIA') or 'SEM_FAMILIA'
        por_fam.setdefault(f, []).append(r.get('CANONICAL_RECORD_ID'))

    fora, saida = [], {}
    for fam, ids in sorted(por_fam.items()):
        entraram = [i for i in ids if i in ids_no_pacote]
        sumiram = [i for i in ids if i not in ids_no_pacote]
        declarada = fam in FAMILIA_NAO_INGERIDA
        saida[fam] = {'NA_PORTA': len(ids), 'NO_PACOTE': len(entraram),
                      'SUMIRAM': len(sumiram),
                      'DECLARADA_COMO_NAO_INGERIDA': declarada,
                      'WHY': FAMILIA_NAO_INGERIDA.get(fam),
                      'DROPPED_IDS': sorted(sumiram)[:8]}
        if not sumiram:
            continue
        if declarada and not entraram:
            continue          # buraco conhecido, declarado, e inteiro
        # Buraco NOVO: ou a familia nao esta declarada, ou uma familia que
        # entrava passou a perder registro. As duas param a cadeia.
        fora.append(fam)
    return saida, fora


def _lista(v):
    return isinstance(v, list)


def etapas_do_registro(r):
    """→ ({etapa: estado}, [códigos de motivo]). Uma leitura, sem efeito."""
    e, m = {}, []

    # 1 · IDENTIDADE E PROCEDÊNCIA
    if not r.get('ID'):
        e['IDENTITY_PROVENANCE'] = FAILED
        m.append('NO_ID')
    elif not r.get('ENTITY_TYPE'):
        e['IDENTITY_PROVENANCE'] = FAILED
        m.append('NO_ENTITY_TYPE')
    elif not r.get('PROVENANCE'):
        e['IDENTITY_PROVENANCE'] = FAILED
        m.append('NO_PROVENANCE')
    elif r.get('SOURCE_URLS') or r.get('SOURCE_IDS'):
        e['IDENTITY_PROVENANCE'] = PASSED
    elif r.get('PROVENANCE') == 'SENTINELA':
        # A sentinela é o endereço de uma ausência declarada. Exigir fonte dela
        # seria exigir fonte do «não sei» — que é justamente o que ela publica.
        e['IDENTITY_PROVENANCE'] = PASSED
        m.append('SENTINEL_DECLARED_ABSENCE')
    elif r.get('PROVENANCE_STATE') == 'UNRECOVERABLE':
        # Declarar que não se sabe recuperar é diferente de não ter olhado.
        e['IDENTITY_PROVENANCE'] = UNKNOWN
        m.append('PROVENANCE_UNRECOVERABLE')
    else:
        e['IDENTITY_PROVENANCE'] = UNKNOWN
        m.append('NO_SOURCE')

    # 2 · NORMALIZAÇÃO — os eixos existem como campo, ainda que vazios.
    # Vazio é resposta: «este registro não fala de cultura nenhuma». Ausente é
    # outra coisa: o normalizador não passou por aqui.
    if not all(_lista(r.get(k)) for k in ('CROP_IDS', 'ISSUE_IDS', 'REGION_IDS')):
        # ⚠️ UNKNOWN, NÃO FAILED. Medido: as 26 coleções de material trazem os
        # três eixos em 100% dos registros, e os únicos casos sem eles eram o
        # índice e os cruzamentos — que não são material e saíram do censo.
        # Um eixo ausente prova que a normalização não deixou marca; não prova
        # que ela reprovou. Chamar isso de falha promoveria um NÃO SEI a acusação.
        e['NORMALIZATION'] = UNKNOWN
        m.append('AXES_MISSING')
    elif not r.get('GEOGRAPHIC_SCOPE'):
        e['NORMALIZATION'] = UNKNOWN
        m.append('SCOPE_MISSING')
    else:
        e['NORMALIZATION'] = PASSED

    # 3 · CLASSIFICAÇÃO
    if not r.get('QA_STATUS'):
        e['CLASSIFICATION'] = FAILED
        m.append('NO_QA_STATUS')
    elif not isinstance(r.get('CLIENT_SAFE'), bool):
        e['CLASSIFICATION'] = FAILED
        m.append('CLIENT_SAFE_NOT_BOOLEAN')
    else:
        e['CLASSIFICATION'] = PASSED

    # 4 · A RÉGUA DA MISSÃO
    # CLIENT_SAFE=false NÃO é reprovação: 1.183 pares de rótulo são derivação
    # nossa e nascem false por construção. O que reprova é o QA dizer REJECTED.
    if r.get('QA_STATUS') == 'QA_REJECTED':
        e['MISSION_RULER'] = FAILED
        m.append('QA_REJECTED')
    else:
        e['MISSION_RULER'] = PASSED

    # 5 · EXTRAÇÃO DE RELAÇÕES
    if r.get('ENTITY_TYPE') not in TIPOS_QUE_FUNDAM_PAR:
        e['RELATION_EXTRACTION'] = NOT_APPLICABLE
    elif any(r.get(c) for c in NEC.CAMPOS_DE_TEXTO):
        e['RELATION_EXTRACTION'] = PASSED
    else:
        e['RELATION_EXTRACTION'] = UNKNOWN
        m.append('NO_TEXT_FOR_PAIR_EXTRACTION')

    # 6 · LOCALIZAÇÃO — a leitura chega na língua de quem vai ler?
    #
    # ⚠️ ESTA ETAPA VEIO DE UMA MEDIÇÃO, e a medição corrigiu uma decisão minha.
    # A primeira versão pôs `AINDA_SO_EM_PORTUGUES` na lista fatal da aceitação,
    # e a testemunha da trilha universal mostrou o resultado: um boletim novo
    # qualquer parava a cadeia inteira, porque a leitura dele nasce em português.
    # Lacuna de tradução não é falha de inteligência, e a consequência dela é
    # deste registro — não do pacote.
    #
    #     A CONSEQUÊNCIA DE UM REGISTRO É DO REGISTRO.
    pendente = [c for c, v, _res in campos_do_registro(r)
                if isinstance(v, str) and e_portugues(parte_minha(c, v)[0])
                and not r.get(c + '_IT')]
    if not pendente:
        e['LOCALIZATION'] = PASSED
    else:
        e['LOCALIZATION'] = UNKNOWN
        m.append('READING_ONLY_IN_PORTUGUESE')

    return e, m


def estado_do_material(etapas):
    if FAILED in etapas.values():
        return MATERIAL_QUARANTINED
    if UNKNOWN in etapas.values():
        return MATERIAL_INCOMPLETE
    return MATERIAL_PASSED


def censo_do_material():
    """→ {ID: {ESTADO, ETAPAS, MOTIVOS, COLECAO, ENTITY_TYPE}}."""
    censo = {}
    for arq in sorted(os.listdir(ING)):
        if not arq.endswith('.json') or arq in NAO_E_COLECAO:
            continue
        d = json.load(open(os.path.join(ING, arq), encoding='utf-8'))
        if not (isinstance(d, dict) and isinstance(d.get('RECORDS'), list)):
            continue
        for r in d['RECORDS']:
            et, mot = etapas_do_registro(r)
            rid = r.get('ID') or ('%s#%d' % (arq, len(censo)))
            censo[rid] = {'COLLECTION': arq, 'ENTITY_TYPE': r.get('ENTITY_TYPE'),
                          'STAGES': et, 'REASON_CODES': mot,
                          'MATERIAL_STATE': estado_do_material(et)}
    return censo


def estado_de_publicacao(o, censo):
    """→ (PUBLICATION_STATE, TRAIL_STATE, quarentenados, incompletos, ausentes).

    Começa no que a régua comercial decidiu e só pode piorar.
    """
    de_fora = DE_EXTERNO.get(o.get('EXTERNAL_MATERIAL_READY'), GATE_UNKNOWN)
    if de_fora == VALIDATION_REQUIRED and not o.get('EXTERNAL_BLOCKER_CODES'):
        # Sem bloqueio nomeado não se pode dizer o que falta validar.
        de_fora = GATE_UNKNOWN

    quarent, incompl, ausentes = [], [], []
    for eid in (o.get('EVIDENCE_IDS') or []):
        c = censo.get(eid)
        if c is None:
            ausentes.append(eid)
        elif c['MATERIAL_STATE'] == MATERIAL_QUARANTINED:
            quarent.append(eid)
        elif c['MATERIAL_STATE'] == MATERIAL_INCOMPLETE:
            incompl.append(eid)

    if quarent or ausentes:
        estado, trilha = QUARANTINED, 'BROKEN'
    elif incompl:
        # INCOMPLETO NÃO É QUEBRADO. Um apoio cuja procedência está declarada
        # como não recuperável continua sendo apoio: o portão F do motor já
        # decide o que fazer com ele, e repetir a decisão aqui seria criar um
        # segundo dono. A catraca só torna a incompletude CONTÁVEL.
        estado, trilha = de_fora, 'INCOMPLETE'
    else:
        estado, trilha = de_fora, 'COMPLETE'

    return estado, trilha, quarent, incompl, ausentes


def main():
    censo = censo_do_material()
    porta, familias_furadas = censo_da_porta(set(censo))
    caminho_opp = os.path.join(ING, 'OPPORTUNITIES.json')
    pacote = json.load(open(caminho_opp, encoding='utf-8'))

    violacoes = {'V1_PUBLICAVEL_COM_MATERIAL_EM_QUARENTENA': [],
                 'V2_REGISTRO_SEM_CLASSIFICACAO': [],
                 'V3_EVIDENCIA_CITADA_QUE_NAO_EXISTE': [],
                 'V4_CATRACA_PROMOVEU': [],
                 'V5_FAMILIA_SUMIU_NA_PORTA_SEM_DECLARACAO': familias_furadas}

    for rid, c in censo.items():
        if 'NO_QA_STATUS' in c['REASON_CODES']:
            violacoes['V2_REGISTRO_SEM_CLASSIFICACAO'].append(rid)

    por_estado = Counter()
    por_trilha = Counter()
    for o in pacote['RECORDS']:
        est, trilha, quar, inc, aus = estado_de_publicacao(o, censo)
        antes = DE_EXTERNO.get(o.get('EXTERNAL_MATERIAL_READY'), GATE_UNKNOWN)
        if PERMISSIVIDADE[est] < PERMISSIVIDADE[antes]:
            violacoes['V4_CATRACA_PROMOVEU'].append(o['ID'])
        if est == PUBLISHABLE and quar:
            violacoes['V1_PUBLICAVEL_COM_MATERIAL_EM_QUARENTENA'].append(o['ID'])
        if aus:
            violacoes['V3_EVIDENCIA_CITADA_QUE_NAO_EXISTE'].append(o['ID'])

        o['PUBLICATION_STATE'] = est
        o['TRAIL_STATE'] = trilha
        o['TRAIL_QUARANTINED_EVIDENCE_IDS'] = quar
        o['TRAIL_INCOMPLETE_EVIDENCE_IDS'] = inc
        o['TRAIL_MISSING_EVIDENCE_IDS'] = aus
        o['PUBLICATION_STATE_FROM'] = 'EXTERNAL_MATERIAL_READY'
        o['PUBLICATION_GATE_LAW'] = (
            'DADO BRUTO NAO E PUBLICAVEL. PUBLICATION_STATE nasce de '
            'EXTERNAL_MATERIAL_READY, que e decisao de v21_comercial.externo(), '
            'e a catraca so pode REBAIXA-LO — nunca promove-lo. O material pode '
            'ficar no acervo sem passar pela inteligencia; o que ele nao pode e '
            'sustentar afirmacao publicavel sem ter passado.')
        por_estado[est] += 1
        por_trilha[trilha] += 1

    pacote['BY_PUBLICATION_STATE'] = dict(por_estado)
    pacote['BY_TRAIL_STATE'] = dict(por_trilha)
    pacote['PUBLICATION_GATE_STATES'] = list(ESTADOS_DE_PUBLICACAO)
    json.dump(pacote, open(caminho_opp, 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)

    por_material = Counter(c['MATERIAL_STATE'] for c in censo.values())
    por_motivo = Counter(m for c in censo.values() for m in c['REASON_CODES'])
    incompletos = sorted(rid for rid, c in censo.items()
                         if c['MATERIAL_STATE'] != MATERIAL_PASSED)

    relatorio = {
        'COLLECTION': 'PUBLICATION_GATE',
        'FILE': 'PUBLICATION-GATE.json',
        'SCHEMA_VERSION': 'V2.1',
        'PRIMARY_KEY': 'RECORD_ID',
        'SOURCE_OF_TRUTH': 'a catraca, sobre o proprio DESIGN-INGEST',
        'STAGES': list(ETAPAS),
        'STAGE_STATES': [PASSED, UNKNOWN, FAILED, NOT_APPLICABLE],
        'MATERIAL_STATES': [MATERIAL_PASSED, MATERIAL_INCOMPLETE, MATERIAL_QUARANTINED],
        'PUBLICATION_STATES': list(ESTADOS_DE_PUBLICACAO),
        'REASON_CODES': dict(MOTIVO),
        'DOOR': PORTA.replace(ROOT + os.sep, '').replace(os.sep, '/'),
        'DOOR_CENSUS': porta,
        'DOOR_NOT_INGESTED_FAMILIES': dict(FAMILIA_NAO_INGERIDA),
        'DOOR_LAW': 'toda familia da porta ou entra no pacote, ou esta declarada '
                    'em DOOR_NOT_INGESTED_FAMILIES com o motivo escrito. Buraco '
                    'novo — familia nao declarada, ou familia que entrava e '
                    'passou a perder registro — PARA a cadeia.',
        'COUNT_MATERIAL': len(censo),
        'BY_MATERIAL_STATE': dict(por_material),
        'BY_REASON_CODE': dict(por_motivo),
        'BY_PUBLICATION_STATE': dict(por_estado),
        'BY_TRAIL_STATE': dict(por_trilha),
        'VIOLATIONS': {k: v for k, v in violacoes.items()},
        'VIOLATION_COUNT': sum(len(v) for v in violacoes.values()),
        'RECORDS': [dict(censo[rid], RECORD_ID=rid) for rid in incompletos],
        'RECORDS_LAW': 'so o material que NAO passou inteiro aparece aqui. O que '
                       'passou e contado em BY_MATERIAL_STATE e nao se repete '
                       'registro a registro: um relatorio que lista tudo nao e '
                       'lido por ninguem.',
        'LAW': 'A CATRACA SO SEGURA, NUNCA EMPURRA. Ela nao pontua, nao classifica '
               'e nao descobre: mede se o material completou as etapas '
               'obrigatorias e impede que o que falhou sustente afirmacao '
               'publicavel. UNKNOWN continua UNKNOWN, e passa a ser contavel.',
        'LOCALIZED_FIELDS': [],
        'LOCALIZATION_LAW': 'esta colecao nao tem prosa: so codigo, ID e numero. '
                            'O codigo e dado e nao tem lingua; a frase de cada '
                            'codigo vive em REASON_CODES, no cabecalho, e se '
                            'traduz uma vez.',
    }
    json.dump(relatorio, open(OUT, 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)

    print('== A CATRACA ==')
    print('porta            : %d familias · %s'
          % (len(porta),
             ' · '.join('%s %d/%d' % (f[:14], v['NO_PACOTE'], v['NA_PORTA'])
                        for f, v in sorted(porta.items()) if v['SUMIRAM'])
             or 'nenhuma perde registro'))
    print('material         : %d registros · %s'
          % (len(censo), dict(por_material)))
    for cod, n in sorted(por_motivo.items()):
        print('  %-32s %d' % (cod, n))
    print('oportunidades    : %s' % dict(por_estado))
    print('trilha           : %s' % dict(por_trilha))
    print('gravado: %s' % OUT)

    n = sum(len(v) for v in violacoes.values())
    if n:
        print('\n  PARADO — a catraca recusa %d passagem(ns):' % n)
        for k, v in violacoes.items():
            if v:
                print('  %s: %s%s' % (k, ', '.join(v[:5]),
                                      ' …' if len(v) > 5 else ''))
        return 1
    print('\n  VIOLACOES: 0')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
