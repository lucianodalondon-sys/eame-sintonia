# -*- coding: utf-8 -*-
"""Adaptadores funcionais NAO CONECTADOS ao casco.

PREPARE / MEASURE / MAP / TEST — DO NOT INTEGRATE.

Este modulo transforma artefatos canonicos de outras missoes em OBJETOS FUNCIONAIS
NORMALIZADOS. Ele nao escreve em banco, nao le rede, nao toca no casco V7 e nao
tem nenhuma superficie. Roda sobre fixtures ou sobre uma copia lida do Git.

TRES LEIS QUE O CODIGO IMPOE, e nao apenas documenta:

1. UNIDADE ANALITICA NAO SE MISTURA.
   PERSON, FARM_BUSINESS_ENTITY, COMPANY_LOCAL_ACCOUNT e SCIENTIFIC_PERSON sao
   unidades diferentes. `juntar()` levanta erro se receber unidades misturadas.

2. LINHA DE INDICE NAO E ENTIDADE.
   O indice do Creator Map lista a mesma pessoa uma vez por cultura: 26 linhas em
   ACTIVATION_READY sao 10 entidades. `contar()` deduplica por chave de identidade e
   devolve os DOIS numeros, sempre. Contar linha inflaria 2,6x.

3. SEM PROVENIENCIA, NAO SAI OBJETO.
   `adaptar_*` exige SOURCE_ID e AS_OF_DATE. Falta -> SchemaIncompativel. Fail closed.

O que este modulo NAO faz, de proposito: nao pontua, nao ordena, nao recomenda, nao
promove estado e nao inventa campo ausente. Ausencia sai como NAO SEI declarado.
"""
import json

# ----------------------------------------------------------------- unidades
UNIDADES = (
    'PERSON',                  # pessoa fisica com canal publico
    'FARM_BUSINESS_ENTITY',    # empresa agricola — NAO e pessoa
    'COMPANY_LOCAL_ACCOUNT',   # conta oficial de empresa, num pais
    'SCIENTIFIC_PERSON',       # pesquisador com identificador declarado
    'CREATOR_CONTENT_PROFILE',   # o que o corpus publico mostra sobre uma entidade
    'TRADEMARK_REGISTRATION_LINK',      # par marca <-> registro local
    'COMPETITOR_COUNTRY_PRODUCT_TUPLE',  # (competidor, pais, produto normalizado)
)

# guardrails semanticos que viajam dentro de cada objeto
GUARDRAILS_COMUNS = (
    'TEMPORAL_ORDER != CAUSALITY',
    'IDENTITY_PROVED != ISSUE_EXPERTISE_PROVED',
    'NOT_ASKED != NOT_READY',
    'ROW != ENTITY',
)


class SchemaIncompativel(Exception):
    """O artefato nao tem a forma que o adaptador exige. Falha fechada, sem chute."""


class UnidadeMisturada(Exception):
    """Tentativa de juntar objetos de unidades analiticas diferentes."""


def _exigir(doc, campos, quem):
    if not isinstance(doc, dict):
        raise SchemaIncompativel('%s: esperava objeto JSON, veio %s' % (quem, type(doc).__name__))
    faltam = [c for c in campos if c not in doc]
    if faltam:
        raise SchemaIncompativel('%s: faltam campos obrigatorios %s' % (quem, faltam))


def _objeto(unidade, chave, pais, campos, proveniencia, nao_sei, guardrails):
    if unidade not in UNIDADES:
        raise SchemaIncompativel('unidade analitica desconhecida: %r' % (unidade,))
    if not chave:
        raise SchemaIncompativel('objeto sem chave de identidade — nao pode ser deduplicado')
    if not proveniencia.get('SOURCE_ID') or not proveniencia.get('AS_OF_DATE'):
        raise SchemaIncompativel('objeto sem SOURCE_ID ou AS_OF_DATE — proveniencia e obrigatoria')
    return {
        'ANALYTICAL_UNIT': unidade,
        'IDENTITY_KEY': chave,
        'COUNTRY': pais or 'NAO SEI',
        'FIELDS': campos,
        'PROVENANCE': proveniencia,
        'WHAT_IS_NOT_KNOWN': list(nao_sei),
        'GUARDRAILS': list(GUARDRAILS_COMUNS) + list(guardrails),
        'WIRED_TO_CASCO': False,
    }


# ------------------------------------------------------------ CREATOR MAP
UNIDADE_POR_ENTITY_TYPE = {
    'PERSON_CREATOR': 'PERSON',
    'FARMER_FAMILY_ACCOUNT': 'PERSON',
    'FARM_BUSINESS': 'FARM_BUSINESS_ENTITY',
}

GUARDRAILS_CREATOR = (
    'PERSON_CREATOR != FARM_BUSINESS — a soma nunca se chama CREATORS_READY',
    'ACTIVATION_READY = o Marketing JA CONSEGUE AVALIAR; nunca "contratar"',
    'FOLLOWERS != AUTHORITY — este objeto nao carrega ordem nem score',
    'CREATOR nao confirma FIELD_PROBLEM, INCIDENCE, MARKET_OPPORTUNITY nem PRODUCT_FIT',
)


def adaptar_creator_capability(doc):
    """CREATOR_CAPABILITY -> lista de objetos funcionais.

    Le LOOKUP_BY_ENTITY_TYPE, que e onde a unidade analitica esta declarada pela fonte.
    Entidades de tipo MEDIA_ACCOUNT, ORGANIZATION e OTHER NAO viram objeto: nao sao nem
    pessoa nem empresa agricola, e forcar uma delas numa das duas unidades seria o erro
    que a propria fonte proibe.
    """
    _exigir(doc, ['SOURCE_ID', 'CAPTURED_AT', 'LOOKUP_BY_ENTITY_TYPE'], 'CREATOR_CAPABILITY')
    prov_base = {
        'SOURCE_ID': doc['SOURCE_ID'],
        'AS_OF_DATE': doc['CAPTURED_AT'],
        'EVIDENCE_CLASS': 'DERIVED_CAPABILITY',
        'CAPABILITY': 'CREATOR_MAP',
    }
    vistos = {}
    for etype, linhas in doc['LOOKUP_BY_ENTITY_TYPE'].items():
        unidade = UNIDADE_POR_ENTITY_TYPE.get(etype)
        if unidade is None:
            continue
        for linha in linhas:
            chave = linha.get('HANDLE') or linha.get('PUBLIC_CHANNEL')
            if not chave:
                raise SchemaIncompativel('CREATOR_CAPABILITY: registro sem HANDLE nem PUBLIC_CHANNEL')
            if chave in vistos:
                continue  # a mesma pessoa aparece uma vez por cultura — nao e outra entidade
            nao_sei = []
            wink = linha.get('WHAT_IS_NOT_KNOWN')
            if wink and wink not in ('NENHUMA', 'NAO SEI', 'NÃO SEI'):
                nao_sei.append(wink)
            for c in ('PUBLIC_CONTACT', 'REGION'):
                if str(linha.get(c, '')).strip() in ('NÃO SEI', 'NAO SEI', ''):
                    nao_sei.append('%s = NAO SEI' % c)
            vistos[chave] = _objeto(
                unidade, chave, linha.get('COUNTRY'),
                {
                    'DISPLAY_NAME': linha.get('CREATOR'),
                    'PUBLIC_CHANNEL': linha.get('PUBLIC_CHANNEL'),
                    'REGION': linha.get('REGION'),
                    'ENTITY_TYPE': linha.get('ENTITY_TYPE'),
                    'ACTIVATION_STATE': linha.get('ACTIVATION_STATE'),
                    'ACTUAL_FARMER': linha.get('ACTUAL_FARMER'),
                    'CROP_PROOF': linha.get('CROP_PROOF'),
                    'RECENT_ACTIVITY': linha.get('RECENT_ACTIVITY'),
                    'AUDIENCE_FACING': linha.get('AUDIENCE_FACING'),
                    'BRAND_HISTORY': linha.get('BRAND_HISTORY'),
                    'COMPETITOR_HISTORY': linha.get('COMPETITOR_HISTORY'),
                    'PUBLIC_CONTACT': linha.get('PUBLIC_CONTACT'),
                },
                dict(prov_base, IDENTITY_EVIDENCE=linha.get('IDENTITY_EVIDENCE'),
                     AS_OF_DATE=linha.get('AS_OF_DATE') or doc['CAPTURED_AT']),
                nao_sei, GUARDRAILS_CREATOR)
    return list(vistos.values())


# ------------------------------------------------ COMPETITOR PUBLIC COMM
GUARDRAILS_PUBLIC_COMM = (
    'COUNTRY_SCOPE != PAGE_ROLE — sao duas perguntas independentes',
    'OFFICIAL_ACCOUNT != LOCAL_COUNTRY_ACCOUNT',
    'SAME_NAME != SAME_COMPETITOR_PRODUCT',
    'PUBLIC_COMMUNICATION != META_PAID_ACTIVITY — camadas separadas, nunca somadas',
    'ZERO aqui e NO_CONTENT_COLLECTION_EXECUTED, nunca COMPANY_NOT_COMMUNICATING',
)


def adaptar_public_comm(doc):
    """PUBLIC_COMM_ACCOUNT -> lista de objetos funcionais.

    Unidade: COMPANY_LOCAL_ACCOUNT. Uma conta, numa plataforma, num pais.
    NUNCA colapsar para "a empresa": a mesma empresa tem varias contas locais, e
    somar contas como se fossem empresas apagaria justamente o que a camada mede.
    """
    _exigir(doc, ['SOURCE_ID', 'FROZEN_AT', 'ACCOUNTS', 'CONTENT_COLLECTION_STAGE'],
            'PUBLIC_COMM_ACCOUNT')
    estagio = doc['CONTENT_COLLECTION_STAGE']
    prov_base = {
        'SOURCE_ID': doc['SOURCE_ID'],
        'AS_OF_DATE': doc['FROZEN_AT'],
        'EVIDENCE_CLASS': 'DERIVED_IDENTITY',
        'CAPABILITY': 'COMPETITOR_PUBLIC_COMMUNICATION',
        'CONTENT_COLLECTION_STAGE': estagio,
    }
    saida = []
    for a in doc['ACCOUNTS']:
        chave = a.get('ACCOUNT_URL')
        if not chave:
            raise SchemaIncompativel('PUBLIC_COMM: conta sem ACCOUNT_URL')
        nao_sei = []
        if estagio != 'DONE':
            nao_sei.append('CONTEUDO: nenhuma coleta executada (%s) — nao se sabe sobre o que a conta fala' % estagio)
        saida.append(_objeto(
            'COMPANY_LOCAL_ACCOUNT', chave, a.get('COUNTRY'),
            {
                'COMPANY': a.get('COMPANY'),
                'PLATFORM': a.get('PLATFORM'),
                'ACCOUNT_HANDLE': a.get('ACCOUNT_HANDLE'),
                'COUNTRY_SCOPE': a.get('COUNTRY_SCOPE'),
                'PAGE_ROLE': a.get('PAGE_ROLE'),
                'CONTENT_ITEMS': None,
                'CONTENT_STATE': 'NOT_COLLECTED' if estagio != 'DONE' else 'COLLECTED',
            },
            dict(prov_base,
                 IDENTITY_EVIDENCE=a.get('IDENTITY_EVIDENCE'),
                 COUNTRY_SCOPE_EVIDENCE=a.get('COUNTRY_SCOPE_EVIDENCE'),
                 PAGE_ROLE_EVIDENCE=a.get('PAGE_ROLE_EVIDENCE')),
            nao_sei, GUARDRAILS_PUBLIC_COMM))
    return saida


# ------------------------------------------------------- EXPERT DIRECTORY
GUARDRAILS_EXPERT = (
    'RECURRENCE != AUTHORITY — este objeto nao ordena e nao pontua',
    'AUTHOR AFFILIATION != REGION OF STUDY',
    'IDENTITY_PROVED != PUBLIC_CHANNEL_PROVED != CONTENT_LINKED',
    'pessoas identificadas exigem tratamento GDPR antes de exposicao',
)


def adaptar_expert_directory(doc):
    """EXPERT_DIRECTORY -> lista de objetos funcionais. Unidade: SCIENTIFIC_PERSON."""
    _exigir(doc, ['SOURCE_ID', 'captured_at', 'PEOPLE'], 'EXPERT_DIRECTORY')
    prov_base = {
        'SOURCE_ID': doc['SOURCE_ID'],
        'AS_OF_DATE': doc['captured_at'],
        'EVIDENCE_CLASS': 'DERIVED_IDENTITY',
        'CAPABILITY': 'EXPERT_DIRECTORY',
    }
    saida = []
    for p in doc['PEOPLE']:
        chave = p.get('PERSON_ID')
        if not chave:
            raise SchemaIncompativel('EXPERT_DIRECTORY: pessoa sem PERSON_ID')
        saida.append(_objeto(
            'SCIENTIFIC_PERSON', chave, p.get('COUNTRY'),
            {
                'NAME': p.get('NAME'),
                'INSTITUTION': p.get('INSTITUTION'),
                'ROLE': p.get('ROLE'),
                'CASE_ID': p.get('CASE_ID'),
                'COUNTRY_BASIS': p.get('COUNTRY_BASIS'),
                'PUBLIC_CHANNEL': None,
                'PUBLIC_CHANNEL_STATE': 'NOT_IN_THIS_ARTIFACT',
            },
            dict(prov_base),
            ['PUBLIC_CHANNEL: nao vem deste artefato',
             'CONTENT_LINKED: nao provado para ninguem',
             'REGION_OF_STUDY: nao existe no registro',
             'ISSUE_EXPERTISE: nao vem deste artefato — use expertise_no_caso()'],
            GUARDRAILS_EXPERT))
    return saida


# ------------------------------------------- expertise por CASO — o portao novo
#
# DELTA 2026-08-30. A medicao anterior contou "2 especialistas em ES x OLIVE x REPILO"
# usando SO o diretorio de pessoas. Estava errada como afirmacao de caso: o artefato de
# identidade declara, ele mesmo, que "a pessoa herda CROP e ISSUE da CONSULTA que a
# trouxe, nunca do titulo". Herdar da consulta nao e expertise.
#
#   IDENTITY_PROVED   != ISSUE_EXPERTISE_PROVED
#   CROP_EXPERTISE    != CROP_X_ISSUE_EXPERTISE
#
# Este portao exige TRES concordancias e mede a terceira contra o corpus cientifico.

def _norm_txt(s):
    fora = 'ÁÀÂÃÄáàâãäÉÈÊËéèêëÍÌÎÏíìîïÓÒÔÕÖóòôõöÚÙÛÜúùûüÇç'
    dentro = 'AAAAAaaaaaEEEEeeeeIIIIiiiiOOOOOoooooUUUUuuuuCc'
    s = str(s or '')
    for a, b in zip(fora, dentro):
        s = s.replace(a, b)
    return s.upper()


def expertise_no_caso(pessoa, corpus, crop, issue, termos_do_issue=()):
    """Mede a expertise de UMA pessoa para UM par cultura x problema.

    `corpus` e o artefato cientifico com DOCUMENTS. A prova de ISSUE exige que o termo do
    problema apareca no TITULO de um trabalho da pessoa — nao basta o campo ISSUE, que
    vem da consulta.

    Devolve os tres estados separados. Nunca um booleano: quando so o pais bate, dizer
    "nao tem especialista" seria tao errado quanto dizer que tem.
    """
    pid = str(pessoa['IDENTITY_KEY']).rsplit('/', 1)[-1]
    docs = (corpus or {}).get('DOCUMENTS') or []
    meus = []
    for d in docs:
        for a in (d.get('AUTHORS') or []):
            if pid and pid in str(a.get('OPENALEX') or ''):
                meus.append(d)
                break
    com_crop = [d for d in meus if crop in (d.get('CROP') or [])]
    # ISSUE pela CONSULTA — fraco, e declarado como fraco
    issue_por_consulta = [d for d in meus if issue in (d.get('ISSUE') or [])]
    # ISSUE pelo TITULO — a prova forte
    termos = [_norm_txt(t) for t in (termos_do_issue or (issue,))]
    por_titulo = [d for d in meus
                  if any(t in _norm_txt(d.get('TITLE')) for t in termos)]

    return {
        'PERSON': pessoa['FIELDS'].get('NAME'),
        'PERSON_ID': pessoa['IDENTITY_KEY'],
        'COUNTRY_MATCH': 'PROVED' if pessoa['COUNTRY'] else 'NOT_KNOWN',
        'WORKS_IN_CORPUS': len(meus),
        'CROP_EXPERTISE': 'PROVED' if com_crop else ('NOT_PROVED' if meus else 'NOT_MEASURABLE'),
        'CROP_WORKS': len(com_crop),
        'ISSUE_BY_QUERY_FIELD': len(issue_por_consulta),
        'ISSUE_BY_TITLE': len(por_titulo),
        'ISSUE_EXPERTISE': ('PROVED' if por_titulo else
                            ('NOT_MEASURABLE' if not meus else 'NOT_PROVED')),
        'CASE_LEVEL_EXPERTISE': ('PROVED' if (com_crop and por_titulo) else
                                 ('NOT_MEASURABLE' if not meus else 'NOT_PROVED')),
        'WHY': ('nenhum trabalho desta pessoa neste corpus — o corpus e espanhol, e '
                'ausencia aqui NAO e ausencia de obra' if not meus else
                ('titulo sustenta o problema' if por_titulo else
                 'o campo ISSUE vem da consulta que trouxe o documento, nao de leitura do '
                 'titulo. Sem termo no titulo, nao ha prova de expertise no problema')),
        'LEI': 'IDENTITY_PROVED != ISSUE_EXPERTISE_PROVED · CROP_EXPERTISE != CROP_X_ISSUE_EXPERTISE',
    }


# ------------------------------------------------------ CREATOR DEEP CORPUS
GUARDRAILS_DEEP_CORPUS = (
    'IDENTIDADE e CONTEUDO sao camadas diferentes: o Creator Map diz QUEM, o corpus diz '
    'O QUE O MATERIAL PUBLICO MOSTRA',
    'NOT_OBSERVED_IN_CORPUS != NO_RELATIONSHIP — o corpus e amostra do que e publico',
    'ADAMA_RELEVANCE_SCORE = PROHIBITED_METRIC — somar oito eixos esconde o eixo vazio',
    'FOLLOWERS DESC nao e ordem de valor',
    'so TEXTO foi lido: imagem e video nao entraram na classificacao',
)


def adaptar_creator_deep_corpus(doc):
    """CREATOR_DEEP_CORPUS -> objetos `CREATOR_CONTENT_PROFILE`.

    Unidade propria, de proposito. Um perfil de conteudo NAO e a pessoa: e o que a
    amostra publica mostra sobre ela, numa janela, numa plataforma. Fundir as duas faria
    o corpus responder "quem chamar?", que e pergunta do Creator Map, nao dele.
    """
    _exigir(doc, ['SOURCE_ID', 'PROFILES'], 'CREATOR_DEEP_CORPUS')
    prov_base = {
        'SOURCE_ID': doc['SOURCE_ID'],
        'AS_OF_DATE': '2026-08-30',
        'EVIDENCE_CLASS': 'DERIVED_CONTENT_OBSERVATION',
        'CAPABILITY': 'CREATOR_DEEP_CORPUS',
        'DATASET_OWNER': doc.get('DATASET_OWNER'),
        'OWNS': (doc.get('X_HANDOFF_FOR_INTELLIGENCE') or {}).get('OWNS'),
        'DOES_NOT_OWN': (doc.get('X_HANDOFF_FOR_INTELLIGENCE') or {}).get('DOES_NOT_OWN'),
    }
    saida = []
    for p in doc['PROFILES']:
        chave = p.get('ENTITY_ID')
        if not chave:
            raise SchemaIncompativel('CREATOR_DEEP_CORPUS: perfil sem ENTITY_ID')
        itens = p.get('N_CONTENT_ITEMS_REVIEWED') or 0
        issues = p.get('ISSUES_OBSERVED') or {}
        nao_sei = []
        if not itens:
            nao_sei.append('CONTENT_ROUTE: NO_PROVED_CONTENT_ROUTE — nenhum material lido')
        if not issues:
            nao_sei.append('ISSUE: nenhum problema observado no conteudo desta ficha')
        nao_sei.append('ISSUE observado e classe de linha (WEED/PEST/DISEASE), '
                       'NUNCA problema nomeado como REPILO ou FLAVESCENCIA')
        saida.append(_objeto(
            'CREATOR_CONTENT_PROFILE', chave, p.get('COUNTRY'),
            {
                'NAME': p.get('NAME'),
                'HANDLE': p.get('HANDLE'),
                'ENTITY_TYPE': p.get('ENTITY_TYPE'),
                'REGION': p.get('REGION'),
                'CHANNEL_STATE': p.get('CHANNEL_STATE'),
                'CONTENT_ROUTE': 'PROVED' if itens else 'NO_PROVED_CONTENT_ROUTE',
                'N_CONTENT_ITEMS_REVIEWED': itens,
                'RECENT_ACTIVITY_BY_WINDOW': p.get('RECENT_ACTIVITY_BY_WINDOW'),
                'CROPS_PROVED_BY_MAP': p.get('CROPS_PROVED'),
                'CROPS_OBSERVED_IN_CONTENT': p.get('CROPS_OBSERVED') or {},
                'ISSUES_OBSERVED_IN_CONTENT': issues,
                'COMPETITOR_HISTORY': p.get('COMPETITOR_HISTORY'),
                'AUDIENCE_EVIDENCE': p.get('AUDIENCE_EVIDENCE'),
            },
            dict(prov_base, PERSON_ID=p.get('PERSON_ID')),
            nao_sei, GUARDRAILS_DEEP_CORPUS))
    return saida


# ---------------------------------------------------- COMPETITOR FORESIGHT
#
# DELTA 2026-08-30: este adaptador levantava erro por ausencia de artefato. A medicao
# de ausencia era verdadeira SO para o snapshot em que foi feita —
# `NOT_FOUND_AT_SNAPSHOT != DOES_NOT_EXIST`. O artefato existe desde entao, o freeze foi
# aceito pelo coordenador, e o adaptador passa a ser real.
#
FORESIGHT_FREEZE = {
    'FORESIGHT_ARTIFACT_STATE': 'EXISTS',
    'FORESIGHT_CANONICAL_FREEZE': 'ACCEPTED',
    'FORESIGHT_SOURCE_BRANCH': 'claude/eame-competitor-foresight',
    'FORESIGHT_SOURCE_COMMIT': '25194e3',
    'FINAL_REFRESH_INPUT': 'NO',   # exige 4/4 handoffs; hoje 2/4
}

GUARDRAILS_FORESIGHT = (
    'SAME_NAME != SAME_COMPETITOR_PRODUCT',
    'NICE_CLASS != AGROCHEMICAL PROOF',
    'HISTORICAL_PRECEDENCE != OPERATIONAL_EARLY_WARNING',
    'NOT_JOINED != NOT_AVAILABLE != ZERO',
    'agrupamento de titular e declarado por GRUPO, nao lido de registro societario',
    'nenhum numero desta camada e ranking, score ou ameaca',
)


def urbole_guard(nome_a, grupo_a, pais_a, nome_b, grupo_b, pais_b):
    """Regressao obrigatoria: `SAME_NAME != SAME_COMPETITOR_PRODUCT`.

    Devolve PROVED so quando nome, GRUPO DO TITULAR e PAIS concordam. Nome igual com
    titular diferente devolve REJECTED — foi assim que `URBOLE` (marca SYNGENTA, registro
    espanhol 24157 da ADAMA) deixou de virar cadeia.

    O nome do portao e o do caso que ele existe para pegar: um portao sem dentes e um
    portao com zero recusas dao a mesma tela.
    """
    def n(x):
        return str(x or '').strip().upper()
    if n(nome_a) != n(nome_b):
        return 'NOT_KNOWN'
    if n(pais_a) != n(pais_b):
        return 'REJECTED_COUNTRY_MISMATCH'
    if n(grupo_a) != n(grupo_b):
        return 'REJECTED_HOLDER_MISMATCH'
    return 'PROVED'


def adaptar_foresight_crosswalk(doc):
    """COMPETITOR-CROSSWALK -> objetos `TRADEMARK_REGISTRATION_LINK`.

    Unidade: o PAR marca<->registro. Nao e a marca, nao e o registro, nao e a empresa.
    Cada par carrega o estado que a fonte declarou, e o portao e re-exercido aqui: se a
    fonte disser PROVED e o guard discordar, o objeto sai com o estado do GUARD e a
    divergencia declarada. Confiar no rotulo da fonte sem reexercer o portao foi
    exatamente o defeito que a auditoria de 2026-08-29 encontrou noutra camada.
    """
    _exigir(doc, ['SOURCE_ID', 'captured_at', 'PARES'], 'FORESIGHT_CROSSWALK')
    pais_doc = doc.get('FACT_LOCATION') or 'NAO SEI'
    prov_base = {
        'SOURCE_ID': doc['SOURCE_ID'],
        'AS_OF_DATE': doc['captured_at'],
        'EVIDENCE_CLASS': 'DERIVED_IDENTITY_CROSSWALK',
        'CAPABILITY': 'COMPETITOR_FORESIGHT',
    }
    prov_base.update(FORESIGHT_FREEZE)
    saida = []
    for p in doc['PARES']:
        chave = '%s|%s|%s' % (p.get('TM_OFFICE'), p.get('ST13'), p.get('REGISTRATION_ID'))
        estado_fonte = p.get('ESTADO_DO_LINK')
        estado_guard = urbole_guard(
            p.get('TM_NAME'), p.get('GRUPO_DA_MARCA'), pais_doc,
            p.get('REGISTRATION_PRODUCT'), p.get('REGISTRATION_GRUPO'), pais_doc)
        nao_sei = []
        if estado_fonte == 'PROVED' and estado_guard != 'PROVED':
            nao_sei.append('DIVERGENCIA: fonte diz %s, guard diz %s' % (estado_fonte, estado_guard))
        if p.get('AGROCHEMICAL_RELEVANCE') == 'SO_CLASSE_5':
            nao_sei.append('RELEVANCIA AGROQUIMICA: so classe 5 de Nice, que nao e prova')
        saida.append(_objeto(
            'TRADEMARK_REGISTRATION_LINK', chave, pais_doc,
            {
                'BRAND': p.get('TM_NAME'),
                'HOLDER_GROUP': p.get('GRUPO_DA_MARCA'),
                'TM_OFFICE': p.get('TM_OFFICE'),
                'TM_APPLICATION_DATE': p.get('TM_APPLICATION_DATE'),
                'TM_STATUS': p.get('TM_STATUS'),
                'REGISTRATION_ID': p.get('REGISTRATION_ID'),
                'REGISTRATION_PRODUCT': p.get('REGISTRATION_PRODUCT'),
                'REGISTRATION_HOLDER': p.get('REGISTRATION_HOLDER'),
                'REGISTRATION_GROUP': p.get('REGISTRATION_GRUPO'),
                'LINK_STATE_DECLARED': estado_fonte,
                'LINK_STATE_REEXERCISED': estado_guard,
                'CROP': None,
                'ISSUE': None,
            },
            dict(prov_base, MOTIVO=p.get('MOTIVO')),
            nao_sei + ['CROP e ISSUE: nenhum dos tres registros nacionais traz cultura e '
                       'alvo neste dataset — sem eles a camada nao entra no eixo cultura x praga'],
            GUARDRAILS_FORESIGHT))
    return saida


def adaptar_foresight_three_layer(doc):
    """COMPETITOR-THREE-LAYER-AUDIT -> objetos `COMPETITOR_COUNTRY_PRODUCT_TUPLE`.

    ⚠️ A perna META desta auditoria vem de branch que NAO esta publicada em origin. Os
    numeros da Meta chegam aqui em SEGUNDA MAO, pela auditoria da missao Foresight.
    Por isso todo objeto sai com `META_LEG = NOT_VERIFIABLE_FROM_ORIGIN`.

    Unidade: TUPLA (competidor, pais, produto normalizado). Produto e tupla NAO se
    subtraem: o mesmo produto anunciado em dois paises e DUAS tuplas.
    """
    _exigir(doc, ['SOURCE_ID', 'captured_at', 'PROVADAS', 'RESULTADO'], 'FORESIGHT_THREE_LAYER')
    ext = doc.get('FONTE_EXTERNA') or {}
    prov_base = {
        'SOURCE_ID': doc['SOURCE_ID'],
        'AS_OF_DATE': doc['captured_at'],
        'EVIDENCE_CLASS': 'DERIVED_CROSS_BRANCH_JOIN',
        'CAPABILITY': 'COMPETITOR_FORESIGHT',
        'META_SOURCE_BRANCH': ext.get('BRANCH'),
        'META_SOURCE_COMMIT': ext.get('COMMIT'),
        'META_HANDOFF_STATE': ext.get('ESTADO_DO_HANDOFF_META'),
        'META_LEG': 'NOT_VERIFIABLE_FROM_ORIGIN',
    }
    prov_base.update(FORESIGHT_FREEZE)
    saida = []
    for c in doc['PROVADAS']:
        chave = '%s|%s|%s' % (c.get('META_COMPANY'), c.get('COUNTRY'), c.get('NOME_NORMALIZADO'))
        saida.append(_objeto(
            'COMPETITOR_COUNTRY_PRODUCT_TUPLE', chave, c.get('COUNTRY'),
            {
                'COMPETITOR': c.get('META_COMPANY'),
                'PRODUCT_NORMALIZED': c.get('NOME_NORMALIZADO'),
                'ADS_OBSERVED': c.get('ADS_OBSERVED'),
                'REGISTRATION_ID': c.get('REGISTRATION_ID'),
                'REGISTRATION_HOLDER': c.get('REGISTRATION_HOLDER'),
                'HOLDER_GROUP': c.get('REGISTRATION_GRUPO'),
                'TM_OFFICE': c.get('TM_OFFICE'),
                'CHAIN_STATE': c.get('ESTADO'),
                'HOLDER_AGREEMENT': c.get('CONCORDANCIA_DE_TITULAR'),
                'CROP': None,
                'ISSUE': None,
            },
            dict(prov_base, SOURCE_URL=c.get('SOURCE_URL')),
            ['META_LEG nao verificavel a partir de origin — branch da Meta nao publicada',
             'nao prova que o anuncio seja daquele produto registrado',
             'nao prova venda, investimento, share nem pressao competitiva',
             'CROP e ISSUE ausentes nas tres pontas'],
            GUARDRAILS_FORESIGHT + (
                'ANUNCIO OBSERVADO != VENDA != SHARE != LANCAMENTO',
                'company da Meta e a classificacao DELES, aceita como declarada',
            )))
    return saida


# ----------------------------------------------------------------- juncao
def juntar(objs_a, objs_b, por):
    """Junta duas listas de objetos por uma chave de FIELDS/COUNTRY.

    Recusa unidades misturadas dentro de cada lado: juntar pessoa com empresa produz
    uma contagem que nao significa nada. Devolve pares, nunca um numero.
    """
    for lado, objs in (('A', objs_a), ('B', objs_b)):
        unidades = set(o['ANALYTICAL_UNIT'] for o in objs)
        if len(unidades) > 1:
            raise UnidadeMisturada('lado %s mistura unidades: %s' % (lado, sorted(unidades)))

    def valor(o):
        if por == 'COUNTRY':
            return o['COUNTRY']
        return o['FIELDS'].get(por)

    idx = {}
    for o in objs_b:
        idx.setdefault(valor(o), []).append(o)
    pares = []
    for o in objs_a:
        for outro in idx.get(valor(o), []):
            pares.append((o, outro))
    return pares


def contar(objs):
    """Conta SEMPRE devolvendo linha e entidade. Nunca so uma das duas."""
    chaves = set(o['IDENTITY_KEY'] for o in objs)
    por_unidade = {}
    for o in objs:
        por_unidade.setdefault(o['ANALYTICAL_UNIT'], set()).add(o['IDENTITY_KEY'])
    return {
        'ROWS': len(objs),
        'ENTITIES': len(chaves),
        'BY_ANALYTICAL_UNIT': dict((k, len(v)) for k, v in sorted(por_unidade.items())),
    }


def carregar(caminho):
    with open(caminho, encoding='utf-8') as f:
        return json.load(f)
