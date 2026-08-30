#!/usr/bin/env python3
"""
ADAMA ITALIA — CATÁLOGO LOCAL V1. O contrato, e o que dele já está medido.

A Espanha construiu catálogo → documentos → registro. A Itália chega pelo lado
oposto, e isso não é acidente: **o registro italiano já está medido e preservado**
— 163 produtos ADAMA no banco do Ministero della Salute, com número, substância,
formulação, vencimento e etiqueta — enquanto o catálogo comercial da adama.com
devolve 403 a tudo que sai deste contêiner, inclusive ao `robots.txt`.

Então este arquivo é duas coisas ao mesmo tempo:

  1. o CONTRATO do catálogo local italiano, escrito por inteiro e testado contra
     os 163 registros reais — para que o dia em que o catálogo chegar não seja o
     dia em que o schema é inventado às pressas;
  2. o HANDOFF: a lista exata do que o navegador local precisa trazer.

A LEI-MÃE, e ela é a razão de o arquivo existir
------------------------------------------------
    PORTFÓLIO GLOBAL ≠ PORTFÓLIO LOCAL ITÁLIA

Nenhum produto espanhol fecha resposta italiana. Todo registro emitido carrega
`COUNTRY = IT`, e há prova que varre a saída inteira procurando contaminação.

AS DUAS METADES, E POR QUE NÃO SE ENCOSTAM
--------------------------------------------
    REGISTRO   fitosanitari.salute.gov.it — a autoridade. MEDIDO: 163 produtos.
    CATÁLOGO   adama.com/italia — o que a empresa APRESENTA. BLOQUEADO por WAF.

A ADAMA não é autoridade regulatória sobre si mesma, e o Ministero não diz o que
a ADAMA apresenta. São perguntas diferentes com fontes diferentes, e o cruzamento
entre elas é o que este arquivo modela — nunca a fusão.

    PUBLIC_CATALOG_PRESENCE ≠ REGULATORY_REGISTRATION
    REGISTRATION ≠ COMMERCIAL_AVAILABILITY
    LOCAL_PRESENT_BUT_REGISTRATION_NOT_PROVED ≠ NOT_REGISTERED
    CAPTURE ≠ REGISTRATION
    NOME IGUAL ≠ MESMO REGISTRO

O QUE ESTE ARQUIVO SE RECUSA A FAZER
--------------------------------------
Produto cartesiano. O registro italiano dá CULTURA e dá ALVO, e **não dá o par**:
a tabela de doses cultura↔alvo não foi reconstruída do PDF, e o próprio dado diz
isso. Cruzar as duas listas produziria milhares de pares que ninguém autorizou.

    DECLARED_CROP ≠ CITED_CROP ≠ AUTHORIZED_CROP
    DOSE ≠ CROP_ISSUE_PAIR
    MENU_TERM ≠ AUTHORIZED_ISSUE
    PATH ≠ IDENTITY
    RAW PRESENCE ≠ RAW CONTENT VERIFIED
"""
import datetime
import hashlib
import json
import os
import re
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SAMPLES = os.path.join(ROOT, 'data', 'samples')
COUNTRY = 'IT'

# A autoridade regulatória italiana. NÃO é a adama.com.
FONTE_REGULATORIA = {
    'SOURCE_ID': 'IT-T4-001',
    'NAME': 'Banca Dati Prodotti Fitosanitari — Ministero della Salute',
    'URL': 'https://www.fitosanitari.salute.gov.it/',
    'ROLE': 'AUTHORITY',
    'WHAT_IT_PROVES': 'registro, titular, substância, formulação, vencimento, etiqueta',
    'WHAT_IT_DOES_NOT_PROVE': ['o que a ADAMA apresenta no catálogo comercial',
                               'disponibilidade comercial', 'preço', 'estoque'],
}
FONTE_CATALOGO = {
    'SOURCE_ID': 'IT-ADAMA-CATALOG',
    'NAME': 'ADAMA Italia — catálogo público',
    'URL': 'https://www.adama.com/italia/it',
    'ROLE': 'MANUFACTURER_CLAIM',
    'WHAT_IT_PROVES': 'o que a empresa APRESENTA localmente',
    'WHAT_IT_DOES_NOT_PROVE': ['registro', 'autorização', 'disponibilidade'],
}

# Medido nos 163 registros em 2026-08-30: o titular do registro italiano NÃO é
# sempre a entidade italiana.
#
#     ADAMA ITALIA S.R.L.      85
#     ADAMA AGAN LTD           35   (Israel)
#     ADAMA MAKHTESHIM LTD     26   (Israel)
#     ADAMA DEUTSCHLAND GMBH   17   (Alemanha)
#
# Os 163 são registros ITALIANOS — estão no banco do Ministero, valem na Itália.
# A nacionalidade do titular não decide o país do portfólio, e filtrar "portfólio
# italiano" por "titular é a ADAMA Italia" descartaria 78 produtos: 48% do total.
# O ataque 9 do red team encontrou isto tentando provar o contrário.
#
#     HOLDER_COUNTRY ≠ REGISTRATION_COUNTRY ≠ PORTFOLIO_COUNTRY
HOLDER_ENTITIES_MEASURED = {
    'ADAMA ITALIA S.R.L.': 85, 'ADAMA AGAN LTD': 35,
    'ADAMA MAKHTESHIM LTD': 26, 'ADAMA DEUTSCHLAND GMBH': 17,
}

REGISTRO = os.path.join(SAMPLES, 'IT-T4-001', 'IT-T4-001-portfolio-rotulo.json')
INTEL = os.path.join(SAMPLES, 'IT-T4-001', 'ITALY-ADAMA-REGULATORY-INTELLIGENCE.json')

# ─────────────────────────────────────────────────────── estados do crosswalk
LOCAL_REGISTERED = 'LOCAL_REGISTERED'
LOCAL_PRESENT_NOT_PROVED = 'LOCAL_PRESENT_BUT_REGISTRATION_NOT_PROVED'
REGISTRATION_CONFLICT = 'REGISTRATION_CONFLICT'
REGISTERED_NOT_IN_CATALOG = 'REGISTERED_BUT_NOT_IN_PUBLIC_CATALOG'
CROSSWALK_NOT_KNOWN = 'NOT_KNOWN'
# `NOT_REGISTERED` existe e NÃO entra por eliminação: exige consulta ao banco do
# Ministero que devolva ausência, não a minha falta de casamento.
NOT_REGISTERED = 'NOT_REGISTERED'

# ──────────────────────────────────────────────────── origem da relação cultura
CROP_DECLARED = 'DECLARED'          # a fonte diz "autorizzato su X"
CROP_CITED = 'CITED'                # X aparece no texto, sem dizer autorização
CROP_REGULATORY = 'AUTHORIZED_REGULATORY'   # a tabela de usos do registro
CROP_ROTATION_ONLY = 'ROTATION_ONLY'        # X só aparece como cultura sucessiva
ORIGENS_CULTURA = (CROP_DECLARED, CROP_CITED, CROP_REGULATORY, CROP_ROTATION_ONLY)

# ──────────────────────────────────────────────────────── espécies documentais
ETICHETTA = 'ETICHETTA'                  # o rótulo autorizado — documento legal
SCHEDA_TECNICA = 'SCHEDA_TECNICA'
SCHEDA_SICUREZZA = 'SCHEDA_DI_SICUREZZA'
BROCHURE = 'BROCHURE'
LEAFLET = 'LEAFLET'
CATALOGO_PDF = 'CATALOGO_PDF'
MATERIALE_TECNICO = 'MATERIALE_TECNICO'
DOC_OUTRO = 'ALTRO_DOCUMENTO'
TIPOS_DOC = (ETICHETTA, SCHEDA_TECNICA, SCHEDA_SICUREZZA, BROCHURE, LEAFLET,
             CATALOGO_PDF, MATERIALE_TECNICO, DOC_OUTRO)

# Nome do arquivo/rota → espécie. A ordem importa: `etichetta` antes de qualquer
# coisa, e o genérico por último. Um PDF promocional NÃO vira rótulo.
PADRAO_DOC = (
    (r'etichett|EtichettaServlet', ETICHETTA),
    (r'scheda[-_\s]*(?:di[-_\s]*)?sicurezz|\bsds\b|msds', SCHEDA_SICUREZZA),
    (r'scheda[-_\s]*tecnic|technical[-_\s]*sheet', SCHEDA_TECNICA),
    (r'brochure|depliant', BROCHURE),
    (r'leaflet|volantino', LEAFLET),
    (r'catalog', CATALOGO_PDF),
    (r'bollettin|nota[-_\s]*tecnic|guida', MATERIALE_TECNICO),
)


def tipo_de_documento(url_ou_nome):
    """Espécie documental a partir da rota/nome. Sem casar: ALTRO_DOCUMENTO.

    Chamar todo PDF de rótulo foi um defeito nomeado pela missão. O rótulo é o
    documento LEGAL; a brochura é material de venda. Confundi-los faria uma frase
    promocional herdar a autoridade de um ato administrativo.
    """
    s = (url_ou_nome or '').lower()
    for padrao, tipo in PADRAO_DOC:
        if re.search(padrao, s, re.I):
            return tipo
    return DOC_OUTRO


# ────────────────────────────────────────────────────────── chave de storage
_ILEGAIS = re.compile(r'[^A-Za-z0-9._-]+')


def storage_key(country, registration_id, doc_type, nome_original):
    """Chave determinística e segura. O nome original vive no metadata, não na chave.

    Portado da cicatriz espanhola:
      · NFC antes de qualquer coisa — "à" composto e decomposto são o MESMO nome,
        e sem normalizar viram duas chaves para um arquivo;
      · sem URL-decode silencioso — `%20` no nome não vira espaço aqui, porque
        decodificar muda a identidade do que foi baixado;
      · extensão preservada, porque o tipo importa a quem for ler depois;
      · sufixo de hash curto do nome original, para que dois arquivos diferentes
        com o mesmo nome saneado não colidam.
    """
    nome = unicodedata.normalize('NFC', str(nome_original or ''))
    raiz, ext = os.path.splitext(nome)
    ext = _ILEGAIS.sub('', ext)[:12]
    raiz_segura = _ILEGAIS.sub('-', raiz).strip('-')[:60] or 'documento'
    digest = hashlib.sha256(nome.encode('utf-8')).hexdigest()[:10]
    return '%s/%s/%s/%s-%s%s' % (country, registration_id or 'SEM-REGISTRO',
                                 doc_type, raiz_segura, digest, ext)


# ───────────────────────────────────────────────────────────────────── BBCH
_BBCH_INTERVALO = re.compile(r'bbch\s*:?\s*(\d{1,2})\s*[-–]\s*(\d{1,2})', re.I)
_BBCH_UNICO = re.compile(r'bbch\s*:?\s*(\d{1,2})(?!\s*[-–]\s*\d)', re.I)
_BBCH_LISTA = re.compile(r'bbch\s*:?\s*((?:\d{1,2}\s*,\s*)+\d{1,2})', re.I)


def bbch(texto):
    """→ dict com o que a fonte publicou. Nunca inventa o outro extremo.

    A cicatriz espanhola: `00-00` virava `00-07`, porque o parser preenchia o fim
    do intervalo quando ele faltava. Um estádio único é um estádio único — e se
    a fonte escreve 00-00, o intervalo é 00-00.
    """
    t = str(texto or '')
    m = _BBCH_LISTA.search(t)
    if m:
        vals = [int(x) for x in re.findall(r'\d{1,2}', m.group(1))]
        return {'BBCH_KIND': 'LIST', 'BBCH_VALUES': vals, 'BBCH_RAW': m.group(0)}
    m = _BBCH_INTERVALO.search(t)
    if m:
        return {'BBCH_KIND': 'RANGE', 'BBCH_FROM': int(m.group(1)),
                'BBCH_TO': int(m.group(2)), 'BBCH_RAW': m.group(0)}
    m = _BBCH_UNICO.search(t)
    if m:
        return {'BBCH_KIND': 'SINGLE', 'BBCH_VALUE': int(m.group(1)),
                'BBCH_RAW': m.group(0)}
    if re.search(r'\bbbch\b', t, re.I):
        return {'BBCH_KIND': 'TEXT_APPROXIMATE', 'BBCH_RAW': t[:120],
                'WHY': 'a fonte menciona BBCH sem número reconhecível'}
    return {'BBCH_KIND': 'UNKNOWN'}


# ────────────────────────────────────────────────────────────── crosswalk
def _chave_nome(s):
    s = unicodedata.normalize('NFKD', str(s or '').upper())
    s = ''.join(c for c in s if not unicodedata.combining(c))
    return re.sub(r'[^A-Z0-9]+', '', s)


def cruzar(catalogo, registro):
    """Catálogo público ↔ registro oficial. Um produto por vez, sem fundir.

    `catalogo` é o que a ADAMA apresenta; `registro` são os produtos do Ministero.
    O casamento é por REGISTRATION_ID quando o catálogo o publica. Quando não
    publica, casar só por NOME é um palpite — e quando o nome bate com MAIS DE UM
    registro, é um palpite que já se sabe errado.

        NOME IGUAL ≠ MESMO REGISTRO
    """
    por_id = {str(r.get('REGISTRATION_ID') or '').strip(): r for r in registro}
    por_nome = {}
    for r in registro:
        por_nome.setdefault(_chave_nome(r.get('PRODUCT')), []).append(r)

    rid = str(catalogo.get('REGISTRATION_ID') or '').strip()
    if rid:
        alvo = por_id.get(rid)
        if alvo:
            return {'STATE': LOCAL_REGISTERED, 'REGISTRATION_ID': rid,
                    'MATCHED_BY': 'REGISTRATION_ID',
                    'REGISTRATION_EVIDENCE': FONTE_REGULATORIA['SOURCE_ID']}
        return {'STATE': REGISTRATION_CONFLICT, 'REGISTRATION_ID': rid,
                'MATCHED_BY': 'REGISTRATION_ID',
                'WHY': ('o catálogo publica um número que não existe entre os '
                        'registros ADAMA medidos no Ministero')}

    candidatos = por_nome.get(_chave_nome(catalogo.get('PRODUCT_NAME')), [])
    if len(candidatos) == 1:
        return {'STATE': LOCAL_PRESENT_NOT_PROVED,
                'REGISTRATION_ID': None,
                'CANDIDATE_REGISTRATION_ID': candidatos[0].get('REGISTRATION_ID'),
                'MATCHED_BY': 'NAME_ONLY',
                'WHY': ('nome bate com um registro só, e nome não é registro. '
                        'Candidato anotado, identidade não fechada')}
    if len(candidatos) > 1:
        return {'STATE': REGISTRATION_CONFLICT, 'REGISTRATION_ID': None,
                'CANDIDATE_REGISTRATION_IDS': [c.get('REGISTRATION_ID')
                                               for c in candidatos],
                'MATCHED_BY': 'NAME_ONLY',
                'WHY': 'o mesmo nome comercial cobre mais de um registro'}
    return {'STATE': LOCAL_PRESENT_NOT_PROVED, 'REGISTRATION_ID': None,
            'MATCHED_BY': None,
            'WHY': ('presente no catálogo e sem correspondência entre os registros '
                    'ADAMA medidos. NÃO é NOT_REGISTERED: pode ser registro de '
                    'outro titular, nome comercial diferente do registrado, ou '
                    'produto fora do recorte medido')}


def escopo_de_pais(produto):
    """De onde vem o COUNTRY de um produto. Do registro, nunca do titular.

    Sem isto, um filtro ingênuo por "ADAMA ITALIA" no titular deixaria de fora
    quase metade do portfólio italiano — e o número resultante pareceria completo.
    """
    return {
        'PORTFOLIO_COUNTRY': COUNTRY,
        'REGISTRATION_COUNTRY': COUNTRY,
        'REGISTRATION_AUTHORITY': FONTE_REGULATORIA['SOURCE_ID'],
        'HOLDER': produto.get('HOLDER'),
        'HOLDER_IS_ITALIAN_ENTITY': 'ITALIA' in str(produto.get('HOLDER') or '').upper(),
        'WHY': ('o país do portfólio vem do REGISTRO, não do titular. '
                'HOLDER_COUNTRY ≠ REGISTRATION_COUNTRY ≠ PORTFOLIO_COUNTRY'),
    }


def captura(registration_id, source, source_version):
    """Identidade de CAPTURA. Nunca cria registro novo.

    A cicatriz espanhola em uma linha: identidade regulatória é (COUNTRY,
    REGISTRATION_ID); a captura é essa mais (SOURCE, SOURCE_VERSION). Ler a
    mesma etiqueta amanhã produz outra captura do MESMO registro.
    """
    return {'CAPTURE_KEY': (COUNTRY, str(registration_id), source, source_version),
            'REGISTRATION_KEY': (COUNTRY, str(registration_id)),
            'WHY': 'CAPTURE ≠ REGISTRATION'}


# ─────────────────────────────────────────────────── o que já está medido
def registro_medido():
    """Os 163 produtos ADAMA do banco do Ministero. Lado autoridade do crosswalk."""
    with open(REGISTRO, encoding='utf-8') as fh:
        d = json.load(fh)
    return d['PRODUCTS']


def relacoes_de_cultura(produto):
    """As relações cultura do REGISTRO, cada uma com a origem que a sustenta.

    O dado italiano já separa termo presente de cultura de rotação — e nenhum dos
    dois é uso autorizado, porque a tabela cultura↔alvo do PDF não foi
    reconstruída. Quem quiser AUTHORIZED_REGULATORY tem de ir buscá-la.
    """
    fora = []
    for c in produto.get('CROP_TERMS_PRESENT') or []:
        fora.append({'CROP': c, 'RELATION_ORIGIN': CROP_CITED,
                     'EVIDENCE': 'termo presente em contexto de uso na etiqueta',
                     'IS_AUTHORIZED_USE': False})
    for c in produto.get('CROP_TERMS_ROTATION_ONLY') or []:
        fora.append({'CROP': c, 'RELATION_ORIGIN': CROP_ROTATION_ONLY,
                     'EVIDENCE': 'aparece só como cultura sucessiva',
                     'IS_AUTHORIZED_USE': False})
    return fora


def pares_cultura_alvo(produto):
    """→ [] sempre, e o motivo junto. Isto NÃO é uma lacuna a preencher depois.

    O registro dá a lista de culturas e a lista de alvos. Multiplicá-las produziria
    pares que ninguém autorizou — para o GOLTIX, uma cultura e vinte e tantas ervas
    daninhas viram vinte e tantos pares falsos, e cada um deles pareceria um fato.

        DOSE ≠ CROP_ISSUE_PAIR
    """
    return {'PAIRS': [], 'STATE': 'NOT_RECONSTRUCTED_FROM_SOURCE',
            'CROPS_AVAILABLE': len(produto.get('CROP_TERMS_PRESENT') or []),
            'ISSUES_AVAILABLE': len(produto.get('ISSUES_FROM_SOURCE') or []),
            'WHY': ('a coluna cultura↔alvo da tabela de doses não foi reconstruída '
                    'do PDF. Cruzar as duas listas seria produto cartesiano')}


def main():
    prods = registro_medido()
    print('FONTE REGULATÓRIA :', FONTE_REGULATORIA['NAME'])
    print('FONTE CATÁLOGO    :', FONTE_CATALOGO['NAME'], '— 403 (WAF)')
    print('registros medidos :', len(prods))
    print('tipos documentais :', len(TIPOS_DOC))
    exemplo = prods[0]
    print()
    print('exemplo:', exemplo['PRODUCT'], exemplo['REGISTRATION_ID'])
    for r in relacoes_de_cultura(exemplo):
        print('   cultura %-12s %-14s autorizada=%s' % (r['CROP'], r['RELATION_ORIGIN'],
                                                        r['IS_AUTHORIZED_USE']))
    print('   pares cultura×alvo:', pares_cultura_alvo(exemplo)['STATE'])
    print('   storage key:', storage_key(COUNTRY, exemplo['REGISTRATION_ID'],
                                         ETICHETTA, 'Etichetta GOLTIX 2024.pdf'))


if __name__ == '__main__':
    main()
