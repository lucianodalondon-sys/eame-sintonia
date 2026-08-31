# -*- coding: utf-8 -*-
"""CONTRATO MULTILINGUE — modelo executavel. NAO ligado ao casco, NAO traduz nada.

    ONE SHELL  +  ONE CANONICAL CORPUS  +  MULTIPLE LANGUAGE REPRESENTATIONS

RED TEAM 2026-08-30 — o que esta rodada corrigiu no MEU proprio contrato:

  1. `ORIGINAL_LANGUAGE` estava sobrecarregado. Virou CINCO papeis distintos.
  2. Eu media ARTEFATO e chamava de FONTE. Os dois numeros agora sao separados.
  3. `ACTIVE_INGREDIENT` nao e identificador imutavel: e ID canonico COM rotulos locais.
  4. `SOURCE_QUOTE` nao e identificador. Virou ORIGINAL_QUOTE / TRANSLATED_QUOTE /
     SOURCE_REFERENCE.
  5. EPPO nao resolve a ontologia inteira. `EPPO_BACKED_ENTITY_ID` passa a ser declarado.
  6. Os icones oficiais da ADAMA EXISTEM, fora do casco. O estado nao e "faltando".
  7. Contrato pronto != acervo conforme. Selos separados.

MASS_TRANSLATION_EXECUTED = NO · CORPUS_MIGRATION_EXECUTED = NO
"""
import hashlib

# ============================================================ 1 · VOCABULARIO
LINGUAS = ('pt', 'en', 'es', 'fr', 'it')

# `MULTILINGUAL` e `UNKNOWN` NAO sao linguas: sao ESTADOS. Um documento multilingue nao
# tem lingua de origem — tem varias, e cada trecho tem a sua.
ESTADOS_DE_LINGUA = ('MULTILINGUAL', 'UNKNOWN')
VOCABULARIO_FECHADO = LINGUAS + ESTADOS_DE_LINGUA

# ---------------------------------------------------- os CINCO papeis de lingua
PAPEIS_DE_LINGUA = {
    'SOURCE_LANGUAGE': 'a lingua da EVIDENCIA / fonte original. Nunca muda por traducao.',
    'ARTIFACT_LANGUAGE': 'a lingua em que um relatorio, handoff, analise ou sintese do '
                         'SINTONIA foi escrito. Nao diz nada sobre a fonte.',
    'UI_LANGUAGE': 'a lingua da interface: menus, botoes, filtros, estados.',
    'DISPLAY_LANGUAGE': 'a lingua escolhida para apresentar o conteudo.',
    'TRANSLATION_TARGET_LANGUAGE': 'a lingua de uma representacao traduzida.',
}

METODOS = ('MACHINE', 'HUMAN', 'SOURCE_PROVIDED')

QUALIDADES = ('SOURCE_ORIGINAL', 'MACHINE_TRANSLATED', 'HUMAN_REVIEWED',
              'SOURCE_PROVIDED_TRANSLATION')

QUALIDADE_PERMITIDA = {
    'MACHINE': ('MACHINE_TRANSLATED', 'HUMAN_REVIEWED'),
    'HUMAN': ('HUMAN_REVIEWED',),
    'SOURCE_PROVIDED': ('SOURCE_PROVIDED_TRANSLATION',),
}

# ============================================ 3 · IDENTIDADE vs ID + ROTULO
#
# GRUPO A — identidade que NUNCA se traduz. Traduzir destroi a chave.
IDENTIDADES_IMUTAVEIS = (
    'TRADEMARK_ID',
    'TRADEMARK_CANONICAL_NAME',
    'COMPANY_ID',
    'COMPANY_LEGAL_NAME',
    'REGISTRATION_ID',
    'SCIENTIFIC_NAME',
    'PRODUCT_COMMERCIAL_NAME',
)

# GRUPO B — ID canonico invariante, ROTULO local legitimo em cada lingua.
#
# CORRECAO DESTA RODADA: `ACTIVE_INGREDIENT` estava no grupo A. Errado.
# "prothioconazole" / "protioconazol" / "protioconazolo" sao a MESMA molecula, e exigir
# que o texto fosse byte-a-byte igual em cinco linguas obrigaria a mostrar a grafia
# francesa a um leitor italiano. A invariancia e do ID, nunca do rotulo.
ENTIDADES_COM_ID_E_ROTULO = (
    'ACTIVE_INGREDIENT_ID',
    'CROP_ID',
    'ISSUE_ID',
    'MOLECULE_ID',
    'EVENT_TYPE_ID',
    'DEPARTMENT_ID',
)

TIPOS_DE_ONTOLOGIA = ('CROP', 'ISSUE', 'MOLECULE', 'EVENT_TYPE', 'DEPARTMENT')

# EPPO so existe para organismo e planta. Molecula, tipo de evento e departamento
# precisam de OUTRO identificador canonico — declarado, nunca o rotulo.
TIPOS_COM_EPPO = ('CROP', 'ISSUE')

# ================================================== 8 · CAMINHOS DE RECUPERACAO
# Os sete nomeados pelo coordenador, mais dois que a busca exercita de verdade e que
# nao cabiam em nenhum dos sete sem mentir sobre o que sao.
MATCH_PATHS = (
    'CANONICAL_ID_MATCH',
    'REGISTRATION_ID_MATCH',
    'ORIGINAL_TEXT_MATCH',
    'OFFICIAL_ALIAS_MATCH',
    'HUMAN_REVIEWED_TRANSLATION_MATCH',
    'MACHINE_TRANSLATION_MATCH',
    'SEMANTIC_MATCH',
    # acrescentados e declarados como acrescimo:
    'ONTOLOGY_LABEL_MATCH',    # rotulo OFICIAL nao e apelido
    'SCIENTIFIC_NAME_MATCH',   # atravessa as cinco linguas sem traducao
)

# ============================================ 6 · ICONE OFICIAL DE DOENCA
#
# CORRECAO DESTA RODADA: eu escrevi PENDING_OFFICIAL_ICON, como se o ativo oficial fosse
# desconhecido. Ele NAO e. O casco V7 nao o carrega — isso e outra coisa.
ICONE_ASSET_STATE = 'EXISTS_EXTERNALLY_IN_DESIGN_SYSTEM'
ICONE_BINDING_STATE_PADRAO = 'NOT_IMPLEMENTED'
ICONE_CROSSWALK_STATE = 'NOT_MEASURED'


class ContratoViolado(Exception):
    """A operacao quebraria uma regra do contrato multilingue."""


# ------------------------------------------------------------ normalizacao
def normalizar_lingua(valor):
    """Devolve (codigo, estado). Fail closed: o que nao e lingua sai como estado.

    Estados possiveis: OK · MULTILINGUAL · UNKNOWN.
    `UNKNOWN` e preservado quando nao foi medido — nao vira chute.
    """
    if valor is None:
        return (None, 'UNKNOWN')
    v = str(valor).strip()
    if not v:
        return (None, 'UNKNOWN')
    baixo = v.lower()
    if baixo in LINGUAS:
        return (baixo, 'OK')
    if v.upper() in ESTADOS_DE_LINGUA:
        return (None, v.upper())
    # 'FR/ES', 'ES / EN', 'multi', 'en (majoritario)' — nenhum e language code
    if baixo == 'multi' or any(s in baixo for s in ('/', ',', ';', '+', ' e ')) or '(' in baixo:
        return (None, 'MULTILINGUAL')
    return (None, 'UNKNOWN')


def _hash(texto):
    return hashlib.sha256(str(texto).encode('utf-8')).hexdigest()


# ================================================== 2 · CONTENT_ENTITY
def content_entity(content_id, source_language, original_text, source,
                   artifact_language=None, published_at=None, identidades=None,
                   fact_country=None, segments=None, original_quote=None,
                   source_reference=None):
    """O objeto canonico. Um por conteudo — NUNCA um por lingua.

    `source_language` e a lingua da FONTE. `artifact_language` e a lingua em que o
    SINTONIA escreveu sobre ela. Os dois nunca se substituem: um boletim frances
    resumido num relatorio em portugues tem SOURCE_LANGUAGE=fr e ARTIFACT_LANGUAGE=pt.
    """
    if not content_id:
        raise ContratoViolado('CONTENT_ID e obrigatorio: e a chave que sobrevive a traducao')
    lang, estado = normalizar_lingua(source_language)
    if estado == 'UNKNOWN' and source_language is not None:
        raise ContratoViolado(
            'SOURCE_LANGUAGE fora do vocabulario fechado (%r). Use %s.'
            % (source_language, list(VOCABULARIO_FECHADO)))
    # MULTILINGUAL exige que alguem tenha decidido: ou ha segmentos, ou o estado foi
    # declarado de proposito. Deixar 'FR/ES/IT' virar MULTILINGUAL em silencio seria
    # trocar um dado ruim por um estado bonito.
    if estado == 'MULTILINGUAL':
        declarado = str(source_language).strip().upper() == 'MULTILINGUAL'
        if not segments and not declarado:
            raise ContratoViolado(
                'SOURCE_LANGUAGE multilingue (%r) exige SEGMENT_LANGUAGE por trecho, '
                'ou a declaracao explicita MULTILINGUAL. Uma string como "FR/ES/IT" '
                'nao e language code.' % (source_language,))
    art_lang, art_estado = normalizar_lingua(artifact_language)

    ident = dict(identidades or {})
    for k in ident:
        if k in ENTIDADES_COM_ID_E_ROTULO:
            raise ContratoViolado(
                '%r tem ID canonico e ROTULO local: vive na ontologia, nao na lista de '
                'identidades imutaveis' % k)
        if k not in IDENTIDADES_IMUTAVEIS:
            raise ContratoViolado('campo %r nao esta na lista de identidades imutaveis' % k)

    segs = []
    for s in (segments or []):
        sl, se = normalizar_lingua(s.get('SEGMENT_LANGUAGE'))
        if se != 'OK':
            raise ContratoViolado('SEGMENT_LANGUAGE precisa ser lingua unica, veio %r'
                                  % (s.get('SEGMENT_LANGUAGE'),))
        segs.append({'SEGMENT_ID': s.get('SEGMENT_ID'), 'SEGMENT_LANGUAGE': sl,
                     'TEXT': s.get('TEXT')})

    return {
        'CONTENT_ID': content_id,
        'SOURCE_LANGUAGE': lang,
        'SOURCE_LANGUAGE_STATE': estado,
        'ARTIFACT_LANGUAGE': art_lang,
        'ARTIFACT_LANGUAGE_STATE': art_estado,
        'SEGMENTS': segs,
        'ORIGINAL_TEXT': original_text,
        'ORIGINAL_TEXT_HASH': _hash(original_text),
        'ORIGINAL_QUOTE': original_quote,
        'SOURCE_REFERENCE': source_reference,
        'SOURCE': source,
        'PUBLISHED_AT': published_at,
        'FACT_COUNTRY': fact_country,
        'IDENTITIES': ident,
        'TRANSLATIONS': {},
    }


def registrar_traducao(entidade, translation_target_language, translated_text,
                       translation_method, translated_at, quality_state=None,
                       translation_version=1, translated_quote=None):
    """Acrescenta uma representacao. NUNCA muda a origem."""
    lang, estado = normalizar_lingua(translation_target_language)
    if estado != 'OK':
        raise ContratoViolado('TRANSLATION_TARGET_LANGUAGE precisa ser lingua unica, veio %r'
                              % (translation_target_language,))
    if lang == entidade['SOURCE_LANGUAGE']:
        raise ContratoViolado(
            'traduzir para a propria lingua de origem (%s) nao e traducao: o estado '
            'correto e SOURCE_ORIGINAL' % lang)
    if translation_method not in METODOS:
        raise ContratoViolado('TRANSLATION_METHOD desconhecido: %r' % (translation_method,))
    if quality_state is None:
        quality_state = QUALIDADE_PERMITIDA[translation_method][0]
    if quality_state not in QUALIDADE_PERMITIDA[translation_method]:
        raise ContratoViolado(
            'metodo %s nao pode declarar qualidade %s — afirmar revisao humana sem '
            'revisao e o unico erro desta camada que o usuario nao consegue detectar'
            % (translation_method, quality_state))
    entidade['TRANSLATIONS'][lang] = {
        'CONTENT_ID': entidade['CONTENT_ID'],
        'TRANSLATION_TARGET_LANGUAGE': lang,
        'TRANSLATED_TEXT': translated_text,
        'TRANSLATED_QUOTE': translated_quote,
        'TRANSLATION_METHOD': translation_method,
        'TRANSLATION_VERSION': translation_version,
        'TRANSLATED_AT': translated_at,
        'QUALITY_STATE': quality_state,
        'SOURCE_TEXT_HASH': entidade['ORIGINAL_TEXT_HASH'],
        'IS_EVIDENCE': False,
    }
    return entidade['TRANSLATIONS'][lang]


def precisa_retraduzir(entidade, lang):
    """TRANSLATE_ONCE / STORE / VERSION / REUSE. Reexibir nao envelhece nada."""
    t = entidade['TRANSLATIONS'].get(lang)
    if t is None:
        return ('MISSING', 'nunca traduzido para esta lingua')
    if t['SOURCE_TEXT_HASH'] != entidade['ORIGINAL_TEXT_HASH']:
        return ('STALE', 'o texto canonico mudou depois desta traducao')
    return ('FRESH', 'reusar — nao traduzir de novo')


# ============================================================ 4 · CITACAO
def montar_exibicao(entidade, display_language):
    """O que a tela recebe. Sempre com a porta de volta ao original.

    A citacao pode ser apresentada traduzida — DESDE QUE marcada como traducao e com o
    original ao lado. O que nao pode e a traducao SUBSTITUIR o original.
    """
    lang, estado = normalizar_lingua(display_language)
    if estado != 'OK':
        raise ContratoViolado('DISPLAY_LANGUAGE invalida: %r' % (display_language,))
    t = entidade['TRANSLATIONS'].get(lang)
    if lang == entidade['SOURCE_LANGUAGE'] or t is None:
        texto, quality, de = entidade['ORIGINAL_TEXT'], 'SOURCE_ORIGINAL', None
        quote_exibida, quote_e_traducao = entidade['ORIGINAL_QUOTE'], False
    else:
        texto, quality, de = t['TRANSLATED_TEXT'], t['QUALITY_STATE'], entidade['SOURCE_LANGUAGE']
        if t.get('TRANSLATED_QUOTE'):
            quote_exibida, quote_e_traducao = t['TRANSLATED_QUOTE'], True
        else:
            quote_exibida, quote_e_traducao = entidade['ORIGINAL_QUOTE'], False
    saida = {
        'CONTENT_ID': entidade['CONTENT_ID'],
        'DISPLAY_LANGUAGE': lang,
        'DISPLAY_TEXT': texto,
        'SOURCE_LANGUAGE': entidade['SOURCE_LANGUAGE'],
        'SOURCE_LANGUAGE_STATE': entidade['SOURCE_LANGUAGE_STATE'],
        'ARTIFACT_LANGUAGE': entidade['ARTIFACT_LANGUAGE'],
        'QUALITY_STATE': quality,
        'TRANSLATED_FROM': de,
        'VIEW_ORIGINAL': entidade['ORIGINAL_TEXT'],
        'SOURCE': entidade['SOURCE'],
        'SOURCE_REFERENCE': entidade['SOURCE_REFERENCE'],
        'IS_EVIDENCE': de is None,
        # citacao: o original NUNCA sai da tela
        'ORIGINAL_QUOTE': entidade['ORIGINAL_QUOTE'],
        'QUOTE_DISPLAYED': quote_exibida,
        'QUOTE_IS_TRANSLATION': quote_e_traducao,
        'QUOTE_IS_EVIDENCE': not quote_e_traducao,
    }
    saida.update(entidade['IDENTITIES'])
    return saida


# ========================================================== 5 · ONTOLOGIA
def termo(term_id, kind, labels, scientific_name=None, aliases=None,
          adama_disease_icon_id=None, eppo_backed=None):
    """ONTOLOGY_TERM. A identidade e o ID; o rotulo e representacao.

    `eppo_backed` e DECLARADO, nao adivinhado. EPPO cobre organismo e planta; molecula,
    tipo de evento e departamento precisam de outro identificador canonico.
    """
    if kind not in TIPOS_DE_ONTOLOGIA:
        raise ContratoViolado('tipo de ontologia desconhecido: %r' % (kind,))
    if not term_id:
        raise ContratoViolado('TERM_ID e obrigatorio — o rotulo nunca e a identidade')
    for l in labels:
        if l not in LINGUAS:
            raise ContratoViolado('rotulo em lingua fora do vocabulario: %r' % (l,))
    if eppo_backed is None:
        eppo_backed = 'NOT_MEASURED'
    if eppo_backed == 'YES' and kind not in TIPOS_COM_EPPO:
        raise ContratoViolado(
            '%s nao pode ser EPPO_BACKED: EPPO cobre %s' % (kind, list(TIPOS_COM_EPPO)))
    return {
        'TERM_ID': term_id,
        'KIND': kind,
        'SCIENTIFIC_NAME': scientific_name,
        'LABELS': dict(labels),
        'ALIASES': dict(aliases or {}),
        'EPPO_BACKED_ENTITY_ID': eppo_backed,
        'ADAMA_DISEASE_ICON_ID': adama_disease_icon_id,
    }


def resolver_rotulo(t, lang):
    """Rotulo com cadeia de fallback DECLARADA. Nunca vazio, nunca inventado."""
    lang, estado = normalizar_lingua(lang)
    if estado != 'OK':
        raise ContratoViolado('lingua invalida para rotulo: %r' % (lang,))
    if t['LABELS'].get(lang):
        return {'TEXT': t['LABELS'][lang], 'FALLBACK': None, 'TERM_ID': t['TERM_ID']}
    if t.get('SCIENTIFIC_NAME'):
        return {'TEXT': t['SCIENTIFIC_NAME'], 'FALLBACK': 'SCIENTIFIC_NAME',
                'TERM_ID': t['TERM_ID']}
    if t['LABELS'].get('en'):
        return {'TEXT': t['LABELS']['en'], 'FALLBACK': 'EN', 'TERM_ID': t['TERM_ID']}
    if t['LABELS']:
        k = sorted(t['LABELS'])[0]
        return {'TEXT': t['LABELS'][k], 'FALLBACK': k.upper(), 'TERM_ID': t['TERM_ID']}
    return {'TEXT': t['TERM_ID'], 'FALLBACK': 'TERM_ID', 'TERM_ID': t['TERM_ID']}


def icone_da_doenca(t):
    """ADAMA_DISEASE_ICON_ID.

    O ativo oficial EXISTE, no design system disponivel no Claude Design. O que nao
    existe e o VINCULO tecnico e o mapa DISEASE_ID <-> ICON_ID. Sao tres estados
    diferentes, e escrever "icone faltando" confundiria os tres.
    """
    if t['KIND'] != 'ISSUE':
        return {'ICON': None, 'ASSET': 'NOT_APPLICABLE', 'BINDING': 'NOT_APPLICABLE',
                'CROSSWALK': 'NOT_APPLICABLE'}
    if t.get('ADAMA_DISEASE_ICON_ID'):
        return {'ICON': t['ADAMA_DISEASE_ICON_ID'], 'ASSET': ICONE_ASSET_STATE,
                'BINDING': 'MAPPED', 'CROSSWALK': 'DECLARED_FOR_THIS_TERM'}
    return {
        'ICON': None,
        'ASSET': ICONE_ASSET_STATE,          # EXISTS_EXTERNALLY_IN_DESIGN_SYSTEM
        'BINDING': ICONE_BINDING_STATE_PADRAO,   # NOT_IMPLEMENTED
        'CROSSWALK': ICONE_CROSSWALK_STATE,      # NOT_MEASURED
        'RULE': 'nao desenhar substituto, nao extrair nem recriar manualmente. A '
                'implementacao futura consulta o asset oficial do Claude Design.',
    }


# ============================================================= 6 · BUSCA
def indexar(entidades, termos):
    """Um indice, nao um acervo por lingua. O CAMINHO do achado viaja com o resultado."""
    idx = []
    for e in entidades:
        idx.append({'MATCH_TEXT': e['ORIGINAL_TEXT'], 'PATH': 'ORIGINAL_TEXT_MATCH',
                    'LANG': e['SOURCE_LANGUAGE'], 'CANONICAL_ID': e['CONTENT_ID']})
        for s in e['SEGMENTS']:
            idx.append({'MATCH_TEXT': s['TEXT'], 'PATH': 'ORIGINAL_TEXT_MATCH',
                        'LANG': s['SEGMENT_LANGUAGE'], 'CANONICAL_ID': e['CONTENT_ID']})
        for lang, t in e['TRANSLATIONS'].items():
            path = ('HUMAN_REVIEWED_TRANSLATION_MATCH'
                    if t['QUALITY_STATE'] in ('HUMAN_REVIEWED', 'SOURCE_PROVIDED_TRANSLATION')
                    else 'MACHINE_TRANSLATION_MATCH')
            idx.append({'MATCH_TEXT': t['TRANSLATED_TEXT'], 'PATH': path,
                        'LANG': lang, 'CANONICAL_ID': e['CONTENT_ID']})
        for k, v in e['IDENTITIES'].items():
            path = ('REGISTRATION_ID_MATCH' if k == 'REGISTRATION_ID' else
                    ('SCIENTIFIC_NAME_MATCH' if k == 'SCIENTIFIC_NAME' else
                     'CANONICAL_ID_MATCH'))
            idx.append({'MATCH_TEXT': v, 'PATH': path, 'LANG': None,
                        'CANONICAL_ID': e['CONTENT_ID'], 'FIELD': k})
    for t in termos:
        idx.append({'MATCH_TEXT': t['TERM_ID'], 'PATH': 'CANONICAL_ID_MATCH',
                    'LANG': None, 'CANONICAL_ID': t['TERM_ID']})
        if t.get('SCIENTIFIC_NAME'):
            idx.append({'MATCH_TEXT': t['SCIENTIFIC_NAME'], 'PATH': 'SCIENTIFIC_NAME_MATCH',
                        'LANG': None, 'CANONICAL_ID': t['TERM_ID']})
        for lang, lab in t['LABELS'].items():
            idx.append({'MATCH_TEXT': lab, 'PATH': 'ONTOLOGY_LABEL_MATCH',
                        'LANG': lang, 'CANONICAL_ID': t['TERM_ID']})
        for lang, als in (t['ALIASES'] or {}).items():
            for a in als:
                idx.append({'MATCH_TEXT': a, 'PATH': 'OFFICIAL_ALIAS_MATCH',
                            'LANG': lang, 'CANONICAL_ID': t['TERM_ID']})
    for e in idx:
        if e['PATH'] not in MATCH_PATHS:
            raise ContratoViolado('caminho de recuperacao nao declarado: %r' % e['PATH'])
    return idx


def buscar(idx, termo_busca):
    """Devolve IDs canonicos + por onde cada um foi achado. Sem score, sem ordem."""
    q = str(termo_busca).strip().lower()
    achados = {}
    for e in idx:
        if q and q in str(e['MATCH_TEXT']).lower():
            achados.setdefault(e['CANONICAL_ID'], []).append(
                {'PATH': e['PATH'], 'LANG': e['LANG'], 'FIELD': e.get('FIELD')})
    return achados


# ======================================== 7 · SELOS: contrato != acervo
def selos():
    """CONTRACT_GUARD e CORPUS_AUDIT_RESULT sao coisas diferentes.

    O contrato pode estar pronto com o acervo legado inteiro fora de conformidade — e
    esta. Misturar os dois selos venderia migracao que nao aconteceu.
    """
    return {
        # --- o que as PROVAS garantem sobre o MODELO
        'CONTRACT_GUARD': {
            'SOURCE_LANGUAGE_PRESERVATION_RULE': 'PROVED_BY_TESTS',
            'ORIGINAL_EVIDENCE_PRESERVATION_RULE': 'PROVED_BY_TESTS',
            'SOURCE_LANGUAGE_NE_ARTIFACT_LANGUAGE': 'PROVED_BY_TESTS',
            'CANONICAL_ID_NE_DISPLAY_LABEL': 'PROVED_BY_TESTS',
            'ONE_CANONICAL_CORPUS': 'YES',
            'SEPARATE_DATABASE_PER_LANGUAGE': 'NO',
            'ONTOLOGY_LANGUAGE_INDEPENDENT': 'YES',
            'CROSS_LANGUAGE_SEARCH_MODEL': 'READY',
        },
        # --- o que foi MEDIDO no acervo que ja existe
        'CORPUS_AUDIT_RESULT': {
            'ARTIFACTS_WITH_LEGACY_LANGUAGE_DECLARATION': '78/81',
            'ARTIFACT_LANGUAGE_FORMATS_FOUND': 15,
            'ARTIFACT_VALUES_THAT_ARE_NOT_A_SINGLE_LANGUAGE': '17/78',
            'SOURCE_RECORDS_SCANNED': 5998,
            'SOURCE_RECORDS_WITH_LANGUAGE_FIELD': 283,
            'SOURCE_RECORDS_WITH_A_DECLARED_LANGUAGE_VALUE': 0,
            'SOURCE_RECORD_LANGUAGE_COVERAGE': 'MEASURED_ZERO_DECLARED',
            'SOURCE_RECORD_LANGUAGE_PROOF': 'NOT_MEASURED',
            'LEGACY_LANGUAGE_FIELD_INTEGRITY': 'NOT_PROVED',
            'LEGACY_SOURCE_LANGUAGE_INTEGRITY': 'NOT_PROVED',
            'LEGACY_CORPUS_EVIDENCE_INTEGRITY': 'NOT_MEASURED',
            'LEGACY_CORPUS_MULTILINGUAL_COMPLIANCE': 'NOT_MEASURED',
        },
        # --- o que NAO existe ainda, dito com o nome exato
        'IMPLEMENTATION_STATE': {
            'CROSS_LANGUAGE_SEARCH_INDEX': 'NOT_IMPLEMENTED',
            'CORPUS_MIGRATION_EXECUTED': 'NO',
            'MASS_TRANSLATION_EXECUTED': 'NO',
            'OFFICIAL_ADAMA_DISEASE_ICON_ASSET': ICONE_ASSET_STATE,
            'DISEASE_ICON_CROSSWALK': ICONE_CROSSWALK_STATE,
            'TECHNICAL_ICON_BINDING': ICONE_BINDING_STATE_PADRAO,
            'PRODUCT_IMPLEMENTATION_MODE': 'NOT_ENTERED',
            'CASCO_V7_MODIFIED': 'NO',
        },
    }
