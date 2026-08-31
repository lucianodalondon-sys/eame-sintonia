# -*- coding: utf-8 -*-
"""CONTRATO MULTILINGUE — modelo executavel. NAO ligado ao casco, NAO traduz nada.

    ONE SHELL  +  ONE CANONICAL CORPUS  +  MULTIPLE LANGUAGE REPRESENTATIONS

Este modulo existe para PROVAR o contrato, nao para executa-lo. Ele nao chama tradutor,
nao escreve em banco, nao le rede e nao toca no casco V7. O que ele faz e impor, em
codigo, as regras que um documento sozinho nao consegue impor:

  1. SOURCE_LANGUAGE nunca muda por causa de traducao.
  2. Um objeto, varias linguas — nunca varios objetos.
  3. A ontologia tem ID proprio; o rotulo e representacao.
  4. TRADUCAO != EVIDENCIA. O original nunca se perde.
  5. Identificador nao se traduz.
  6. Qualidade nao se afirma sem revisao.
  7. Traduz uma vez, versiona, reusa.

MASS_TRANSLATION_EXECUTED = NO.
"""
import hashlib

# ---------------------------------------------------------------- vocabularios
# Fechado, minusculo, ISO-639-1. O acervo hoje usa 15 grafias diferentes para isto.
LINGUAS = ('pt', 'en', 'es', 'fr', 'it')

# `MULTI` e `UNKNOWN` NAO sao linguas: sao estados. Um documento multilingue nao tem
# lingua de origem — tem varias, e cada trecho tem a sua.
ESTADOS_DE_LINGUA = ('MULTI', 'UNKNOWN')

METODOS = ('MACHINE', 'HUMAN', 'SOURCE_PROVIDED')

QUALIDADES = (
    'SOURCE_ORIGINAL',              # nao e traducao: e o texto de origem
    'MACHINE_TRANSLATED',           # maquina, sem revisao humana
    'HUMAN_REVIEWED',               # revisada por pessoa
    'SOURCE_PROVIDED_TRANSLATION',  # a propria fonte publicou nesta lingua
)

# metodo -> qualidades que ele PODE declarar. Maquina nunca vira revisada sozinha.
QUALIDADE_PERMITIDA = {
    'MACHINE': ('MACHINE_TRANSLATED', 'HUMAN_REVIEWED'),
    'HUMAN': ('HUMAN_REVIEWED',),
    'SOURCE_PROVIDED': ('SOURCE_PROVIDED_TRANSLATION',),
}

# Campos que sao IDENTIDADE, nao texto. Traduzir qualquer um destes destroi a chave.
NAO_TRADUZIVEIS = (
    'PRODUCT_COMMERCIAL_NAME',   # MAXENTIS nao vira "Maxentis" em outra lingua
    'COMPANY_NAME',              # razao social e identidade juridica
    'TRADEMARK',                 # a marca e a chave nova que o Foresight traz
    'ACTIVE_INGREDIENT',         # protioconazol tem nome por lingua, mas o CAS manda
    'SCIENTIFIC_NAME',           # Venturia oleaginea e o ancoradouro entre linguas
    'REGISTRATION_ID',           # ES-00211 nao tem traducao
    'SOURCE_QUOTE',              # citacao traduzida deixa de ser citacao
)

TIPOS_DE_ONTOLOGIA = ('CROP', 'ISSUE', 'MOLECULE', 'EVENT_TYPE', 'DEPARTMENT')


class ContratoViolado(Exception):
    """A operacao quebraria uma regra do contrato multilingue."""


# ------------------------------------------------------------ normalizacao
def normalizar_lingua(valor):
    """Devolve (codigo, estado). Fail closed: o que nao e lingua sai como estado.

    Medido em 2026-08-30: 78 de 81 artefatos de `data/samples` declaram
    ORIGINAL_LANGUAGE, em **15 grafias diferentes** — 'ES', 'es', 'EN', 'en',
    'en (majoritario)', 'multi', 'FR/ES', 'FR/ES/IT', 'ES / EN'...  17 desses 78 (22 %)
    nao sao uma lingua unica. Esta funcao e o portao que fecha isso sem apagar o caso:
    documento multilingue vira MULTI, e MULTI nao e lingua.
    """
    if valor is None:
        return (None, 'UNKNOWN')
    v = str(valor).strip()
    if not v:
        return (None, 'UNKNOWN')
    baixo = v.lower()
    if baixo in LINGUAS:
        return (baixo, 'OK')
    # 'FR/ES', 'ES / EN', 'multi', 'en (majoritario)' — nenhum e lingua unica
    separadores = ('/', ',', ';', ' e ', '+')
    if baixo == 'multi' or any(s in baixo for s in separadores) or '(' in baixo:
        return (None, 'MULTI')
    return (None, 'UNKNOWN')


def _hash(texto):
    return hashlib.sha256(str(texto).encode('utf-8')).hexdigest()


# ------------------------------------------------------- CONTENT_ENTITY
def content_entity(content_id, original_language, original_text, source,
                   published_at=None, nao_traduziveis=None, fact_country=None):
    """O objeto canonico. Um por conteudo — NUNCA um por lingua."""
    lang, estado = normalizar_lingua(original_language)
    if estado == 'UNKNOWN':
        raise ContratoViolado(
            'ORIGINAL_LANGUAGE nao reconhecida (%r). Declare uma de %s, ou MULTI.'
            % (original_language, list(LINGUAS)))
    if not content_id:
        raise ContratoViolado('CONTENT_ID e obrigatorio: e a chave que sobrevive a traducao')
    ident = dict(nao_traduziveis or {})
    for k in ident:
        if k not in NAO_TRADUZIVEIS:
            raise ContratoViolado('campo %r nao esta na lista de identidade' % k)
    return {
        'CONTENT_ID': content_id,
        'SOURCE_LANGUAGE': lang,           # None quando MULTI — e isso e honesto
        'SOURCE_LANGUAGE_STATE': estado,
        'ORIGINAL_TEXT': original_text,
        'ORIGINAL_TEXT_HASH': _hash(original_text),
        'SOURCE': source,
        'PUBLISHED_AT': published_at,
        'FACT_COUNTRY': fact_country,
        'NON_TRANSLATABLE': ident,
        'TRANSLATIONS': {},
        'ORIGINAL_EVIDENCE_PRESERVED': True,
    }


def registrar_traducao(entidade, translation_language, translated_text,
                       translation_method, translated_at, quality_state=None,
                       translation_version=1):
    """Acrescenta uma representacao. NUNCA muda a origem.

    A entidade e mutada apenas em TRANSLATIONS. Qualquer tentativa de escrever em
    SOURCE_LANGUAGE ou ORIGINAL_TEXT por aqui e impossivel por construcao — e ha teste
    que confere os dois depois de traduzir para quatro linguas.
    """
    lang, estado = normalizar_lingua(translation_language)
    if estado != 'OK':
        raise ContratoViolado('DISPLAY_LANGUAGE precisa ser uma lingua unica, veio %r'
                              % (translation_language,))
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
        'TRANSLATION_LANGUAGE': lang,
        'TRANSLATED_TEXT': translated_text,
        'TRANSLATION_METHOD': translation_method,
        'TRANSLATION_VERSION': translation_version,
        'TRANSLATED_AT': translated_at,
        'QUALITY_STATE': quality_state,
        'SOURCE_TEXT_HASH': entidade['ORIGINAL_TEXT_HASH'],
        'IS_EVIDENCE': False,   # TRANSLATED_EVIDENCE != ORIGINAL_EVIDENCE
    }
    return entidade['TRANSLATIONS'][lang]


def precisa_retraduzir(entidade, lang):
    """TRANSLATE_ONCE / STORE / VERSION / REUSE.

    Uma traducao so envelhece quando o TEXTO CANONICO muda. Reexibir nao envelhece nada.
    """
    t = entidade['TRANSLATIONS'].get(lang)
    if t is None:
        return ('MISSING', 'nunca traduzido para esta lingua')
    if t['SOURCE_TEXT_HASH'] != entidade['ORIGINAL_TEXT_HASH']:
        return ('STALE', 'o texto canonico mudou depois desta traducao')
    return ('FRESH', 'reusar — nao traduzir de novo')


# --------------------------------------------------------------- exibicao
def montar_exibicao(entidade, display_language):
    """O que a tela recebe. Sempre com a porta de volta ao original.

    TRADUCAO E REPRESENTACAO PARA LEITURA. Claim regulatorio, cientifico ou tecnico
    nunca perde a ligacao com o texto original — por isso VIEW_ORIGINAL e SOURCE saem
    em TODA exibicao, inclusive quando nao houve traducao nenhuma.
    """
    lang, estado = normalizar_lingua(display_language)
    if estado != 'OK':
        raise ContratoViolado('DISPLAY_LANGUAGE invalida: %r' % (display_language,))
    if lang == entidade['SOURCE_LANGUAGE']:
        texto, quality, de = entidade['ORIGINAL_TEXT'], 'SOURCE_ORIGINAL', None
    else:
        t = entidade['TRANSLATIONS'].get(lang)
        if t is None:
            # sem traducao NAO se mostra vazio: mostra o original e declara
            texto, quality, de = entidade['ORIGINAL_TEXT'], 'SOURCE_ORIGINAL', None
        else:
            texto, quality, de = (t['TRANSLATED_TEXT'], t['QUALITY_STATE'],
                                  entidade['SOURCE_LANGUAGE'])
    saida = {
        'CONTENT_ID': entidade['CONTENT_ID'],
        'DISPLAY_LANGUAGE': lang,
        'DISPLAY_TEXT': texto,
        'ORIGINAL_LANGUAGE': entidade['SOURCE_LANGUAGE'],
        'SOURCE_LANGUAGE_STATE': entidade['SOURCE_LANGUAGE_STATE'],
        'QUALITY_STATE': quality,
        'TRANSLATED_FROM': de,
        'VIEW_ORIGINAL': entidade['ORIGINAL_TEXT'],
        'SOURCE': entidade['SOURCE'],
        'IS_EVIDENCE': de is None,
    }
    # identidade viaja intacta em toda lingua
    saida.update(entidade['NON_TRANSLATABLE'])
    return saida


# --------------------------------------------------------------- ontologia
def termo(term_id, kind, labels, scientific_name=None, aliases=None,
          adama_disease_icon_id=None):
    """ONTOLOGY_TERM. A identidade e o ID; o rotulo e representacao.

    O acervo ja tem o ancoradouro: `eppo-dictionary.json`, 492 culturas e 1.381 pragas
    com CODIGO EPPO como chave — OLVEU = Olea europaea, SEPTTR = Zymoseptoria tritici.
    O que ele NAO tem sao rotulos em fr, it e en: so `es` e `scientific`.
    """
    if kind not in TIPOS_DE_ONTOLOGIA:
        raise ContratoViolado('tipo de ontologia desconhecido: %r' % (kind,))
    if not term_id:
        raise ContratoViolado('TERM_ID e obrigatorio — o rotulo nunca e a identidade')
    for l in labels:
        if l not in LINGUAS:
            raise ContratoViolado('rotulo em lingua fora do vocabulario: %r' % (l,))
    return {
        'TERM_ID': term_id,
        'KIND': kind,
        'SCIENTIFIC_NAME': scientific_name,
        'LABELS': dict(labels),
        'ALIASES': dict(aliases or {}),
        'ADAMA_DISEASE_ICON_ID': adama_disease_icon_id,
        'ICON_BINDING_STATE': ('BOUND' if adama_disease_icon_id else
                               ('PENDING_OFFICIAL_ICON' if kind == 'ISSUE' else 'NOT_APPLICABLE')),
    }


def resolver_rotulo(t, lang):
    """Rotulo com cadeia de fallback DECLARADA. Nunca devolve vazio, nunca inventa.

    Ordem: lingua pedida -> nome cientifico -> ingles -> qualquer rotulo existente.
    O estado do fallback sai junto: a tela precisa poder dizer que esta mostrando o
    nome cientifico porque nao ha rotulo naquela lingua.
    """
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
    """ADAMA_DISEASE_ICON_ID — vinculo planejado, nunca inventado.

    O design system da ADAMA tem icones oficiais de doenca. O casco V7 NAO os traz:
    medido, ele so tem a forma 'A' da marca e as quatro CORES de linha de produto
    (`disease-control` e cor, nao icone). Enquanto o conjunto oficial nao chegar, o
    estado e PENDING_OFFICIAL_ICON — e a regra e nao desenhar generico no lugar.
    """
    if t['KIND'] != 'ISSUE':
        return {'ICON': None, 'STATE': 'NOT_APPLICABLE'}
    if t.get('ADAMA_DISEASE_ICON_ID'):
        return {'ICON': t['ADAMA_DISEASE_ICON_ID'], 'STATE': 'BOUND'}
    return {'ICON': None, 'STATE': 'PENDING_OFFICIAL_ICON',
            'RULE': 'nao criar icone generico quando existir o oficial — esperar o oficial'}


# ------------------------------------------------------------------ busca
def indexar(entidades, termos):
    """Um indice, nao um acervo por lingua.

    Cada entrada aponta para o MESMO objeto canonico. A busca em qualquer lingua chega
    ao mesmo CONTENT_ID / TERM_ID — e o caminho que a achou fica declarado, porque
    "achei pelo texto traduzido" e uma confianca diferente de "achei pelo ID".
    """
    idx = []
    for e in entidades:
        idx.append({'MATCH_TEXT': e['ORIGINAL_TEXT'], 'PATH': 'ORIGINAL_TEXT',
                    'LANG': e['SOURCE_LANGUAGE'], 'CANONICAL_ID': e['CONTENT_ID']})
        for lang, t in e['TRANSLATIONS'].items():
            idx.append({'MATCH_TEXT': t['TRANSLATED_TEXT'], 'PATH': 'TRANSLATED_TEXT',
                        'LANG': lang, 'CANONICAL_ID': e['CONTENT_ID']})
        for k, v in e['NON_TRANSLATABLE'].items():
            idx.append({'MATCH_TEXT': v, 'PATH': 'IDENTIFIER:%s' % k,
                        'LANG': None, 'CANONICAL_ID': e['CONTENT_ID']})
    for t in termos:
        if t.get('SCIENTIFIC_NAME'):
            idx.append({'MATCH_TEXT': t['SCIENTIFIC_NAME'], 'PATH': 'SCIENTIFIC_NAME',
                        'LANG': None, 'CANONICAL_ID': t['TERM_ID']})
        for lang, lab in t['LABELS'].items():
            idx.append({'MATCH_TEXT': lab, 'PATH': 'ONTOLOGY_LABEL',
                        'LANG': lang, 'CANONICAL_ID': t['TERM_ID']})
        for lang, als in (t['ALIASES'] or {}).items():
            for a in als:
                idx.append({'MATCH_TEXT': a, 'PATH': 'ALIAS',
                            'LANG': lang, 'CANONICAL_ID': t['TERM_ID']})
    return idx


def buscar(idx, termo_busca):
    """Devolve IDs canonicos + por onde cada um foi achado. Sem score, sem ordem."""
    q = str(termo_busca).strip().lower()
    achados = {}
    for e in idx:
        if q and q in str(e['MATCH_TEXT']).lower():
            achados.setdefault(e['CANONICAL_ID'], []).append(
                {'PATH': e['PATH'], 'LANG': e['LANG']})
    return achados
