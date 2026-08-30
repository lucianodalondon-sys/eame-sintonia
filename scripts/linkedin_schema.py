#!/usr/bin/env python3
"""
O CONTRATO REAL do Actor de perfil — observado, não adivinhado.

Desenhado a partir do esqueleto dos 8 itens recuperados (execuções já pagas,
`IT-LINKEDIN-RECOVERY.json`). Antes disto o parser procurava `profileUrl`, `url`
e `publicIdentifier` **no topo do objeto**. O Actor nunca devolveu nada disso: a
URL vive em `basic_info.profile_url`, aninhada um nível abaixo.

Foi só isso. Um nível de aninhamento transformou oito execuções pagas em oito
`NOT_FOUND`, e um relatório que parecia dizer algo sobre o LinkedIn não dizia
nada sobre o LinkedIn.

    PARSER_MISS ≠ PROFILE_NOT_FOUND

SEM DEZ ALIASES "POR TENTATIVA"
--------------------------------
A tentação óbvia é aceitar `profileUrl or profile_url or url or basic_info.url…`
até algo casar. Isso esconde a próxima mudança de contrato em vez de denunciá-la:
um schema novo passaria despercebido, e o silêncio voltaria disfarçado de dado.

Aqui há UMA função para UM schema comprovado. Formato que não bate devolve
`UNKNOWN_SCHEMA`, que é um estado alto e barulhento — e **nunca** `NOT_FOUND`.

    ACTOR_ITEM ≠ PROFILE
    HTTP_SUCCESS ≠ SEMANTIC_SUCCESS

E A ARMADILHA QUE OS DADOS RECUPERADOS REVELARAM
--------------------------------------------------
O Actor recebe uma CONSULTA DE BUSCA e devolve UM perfil. Ele sempre devolve
algum. Nada garante que seja a pessoa procurada — e o primeiro item recuperado
tem `first_name` de 4 letras e `last_name` de 7, que não corresponde a nenhum
nome longo da lista. Aceitar o retorno como identidade seria inventar pessoa.

    SEARCH_HIT ≠ PERSON

Por isso `conferir_identidade()` é separada e obrigatória: o perfil só é ligado
a um alvo quando sobrenome e nome batem. Sem isso, o estado é
`IDENTITY_UNVERIFIED` — que não é perfil encontrado nem perfil ausente.
"""
import unicodedata

SCHEMA_V1 = 'PROFILE_DETAIL_V1_BASIC_INFO'
UNKNOWN_SCHEMA = 'UNKNOWN_SCHEMA'
ERROR_ITEM = 'ERROR_ITEM'
IDENTITY_UNVERIFIED = 'IDENTITY_UNVERIFIED'


def _normal(s):
    s = unicodedata.normalize('NFKD', (s or '').lower())
    return ''.join(c for c in s if not unicodedata.combining(c)).strip()


def detectar_schema(item):
    """Que contrato é este item? Reconhece UM, e diz não saber sobre o resto."""
    if not isinstance(item, dict):
        return UNKNOWN_SCHEMA
    if 'error' in item or 'errorMessage' in item:
        return ERROR_ITEM
    bi = item.get('basic_info')
    if isinstance(bi, dict) and ('profile_url' in bi or 'public_identifier' in bi):
        return SCHEMA_V1
    return UNKNOWN_SCHEMA


def extrair_perfil(item):
    """→ dict do perfil, ou {'SCHEMA': ...} explicando por que não deu.

    Nunca devolve NOT_FOUND: ausência de perfil e falha de leitura são coisas
    diferentes, e confundi-las é o defeito que este arquivo existe para fechar.
    """
    schema = detectar_schema(item)
    if schema != SCHEMA_V1:
        return {'SCHEMA': schema, 'PROFILE_URL': None,
                'WHY': ('o item não bate com nenhum contrato comprovado; isto NÃO '
                        'significa que o perfil não exista')}
    bi = item['basic_info']
    loc = bi.get('location') or {}
    return {
        'SCHEMA': SCHEMA_V1,
        'PROFILE_URL': bi.get('profile_url'),
        'PUBLIC_IDENTIFIER': bi.get('public_identifier'),
        'URN': bi.get('urn'),
        'FULLNAME': bi.get('fullname'),
        'FIRST_NAME': bi.get('first_name'),
        'LAST_NAME': bi.get('last_name'),
        'HEADLINE': bi.get('headline'),
        'CURRENT_COMPANY': bi.get('current_company'),
        'LOCATION': loc.get('full'), 'COUNTRY_CODE': loc.get('country_code'),
        'ABOUT': bi.get('about'),
        'IS_CREATOR': bi.get('is_creator'), 'IS_TOP_VOICE': bi.get('is_top_voice'),
        'FOLLOWER_COUNT': bi.get('follower_count'),
        'EXPERIENCE_COUNT': len(item.get('experience') or []),
        'HAS_EDUCATION': bool(item.get('education')),
    }


def conferir_identidade(perfil, nome_alvo):
    """`SEARCH_HIT ≠ PERSON`. O Actor sempre devolve alguém; pode ser outro alguém."""
    if perfil.get('SCHEMA') != SCHEMA_V1:
        return perfil['SCHEMA'], 'schema não reconhecido, identidade não avaliável'
    alvo = _normal(nome_alvo).split()
    if not alvo:
        return IDENTITY_UNVERIFIED, 'nome alvo vazio'
    cheio = _normal(perfil.get('FULLNAME') or
                    '%s %s' % (perfil.get('FIRST_NAME') or '',
                               perfil.get('LAST_NAME') or ''))
    faltam = [p for p in alvo if p not in cheio]
    if faltam:
        return IDENTITY_UNVERIFIED, ('o perfil devolvido não contém %s do alvo'
                                     % ', '.join(faltam))
    return 'IDENTITY_CONFIRMED', ''


def identidade_do_item(item):
    """Dedupe por identidade do CONTEÚDO — nunca pelo token que a buscou."""
    p = extrair_perfil(item)
    return (p.get('PUBLIC_IDENTIFIER') or p.get('URN') or p.get('PROFILE_URL')
            or ('UNPARSED', str(sorted(item))[:160] if isinstance(item, dict) else str(item)[:160]))
