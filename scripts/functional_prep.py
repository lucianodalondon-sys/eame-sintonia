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
             'REGION_OF_STUDY: nao existe no registro'],
            GUARDRAILS_EXPERT))
    return saida


# ---------------------------------------------------- COMPETITOR FORESIGHT
def adaptar_foresight(_doc=None):
    """Nao existe artefato de COMPETITOR FORESIGHT em nenhuma branch (medido 2026-08-30).

    Este adaptador existe para FALHAR, e a falha e a entrega: preparar um schema a
    partir do nome da missao seria inventar. O que se sabe hoje veio de OUTRA missao,
    que declarou a fronteira: IP, BRAND, REGULATORY e PRODUCT continuam do Foresight.
    """
    raise SchemaIncompativel(
        'COMPETITOR_FORESIGHT: NO_ARTIFACT_IN_REPO em 2026-08-30. '
        'Varredura de nomes em 13 refs de origin e git grep por "foresight" nao acharam '
        'artefato. Adaptador so pode ser escrito depois do handoff.')


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
