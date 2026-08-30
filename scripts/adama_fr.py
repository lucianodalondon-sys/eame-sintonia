#!/usr/bin/env python3
"""
ADAMA FRANÇA — CATÁLOGO LOCAL V1. O contrato, e o lado que já está medido.

A França chega com uma vantagem que nem a Espanha nem a Itália tiveram: a
autoridade publica o PAR cultura×alvo já amarrado, em dados abertos, com dose,
estádio BBCH e prazo de carência na mesma linha. Não é preciso reconstruir tabela
de PDF nem multiplicar listas.

    Espanha   o par vem de consulta ao servidor, e a dose sai de PDF
    Itália    163 PDFs parseados, e a coluna cultura↔alvo NÃO foi reconstruída
    França    `Vigne*Trt Part.Aer.*Mildiou(s)` — a própria ANSES amarra o par

A LEI-MÃE
----------
    PORTFÓLIO GLOBAL ≠ PORTFÓLIO LOCAL FRANÇA

Nenhum produto espanhol ou italiano fecha resposta francesa. FR ≠ ES ≠ IT.

AS DUAS METADES, E POR QUE NÃO SE ENCOSTAM
--------------------------------------------
    REGISTRO   ANSES / E-Phy — a autoridade.        MEDIDO nesta rodada.
    CATÁLOGO   adama.com/france — o que a empresa APRESENTA.

A ADAMA não é autoridade regulatória sobre si mesma, e a ANSES não diz o que a
ADAMA apresenta.

    PUBLIC_CATALOG_PRESENCE ≠ REGULATORY_REGISTRATION
    MANUFACTURER_CLAIM      ≠ REGULATORY_FACT
    REGISTRATION            ≠ COMMERCIAL_AVAILABILITY
    CAPTURE                 ≠ REGISTRATION
    NOME IGUAL              ≠ MESMO REGISTRO

O QUE FOI MEDIDO EM 2026-08-30 (dataset E-Phy de 2026-08-25)
--------------------------------------------------------------
    registro francês inteiro ....... 15.140 produtos
    com ADAMA no titular ........... 267
      · AUTORISE ................... 72      <- o portfólio francês de hoje
      · RETIRE .................... 195
    usos autorizados ADAMA ......... 582 linhas, em 70 AMMs
      · com alvo específico ........ 367 linhas -> 161 pares DISTINTOS
      · sem alvo, só tratamento .... 215 linhas ->  41 cultura×tratamento

O 267 É UMA ARMADILHA, E ELA JÁ ESTAVA ARMADA
-----------------------------------------------
Havia no acervo o número "267 produtos ADAMA na França". Ele está certo como
contagem de LINHAS COM ADAMA NO TITULAR, e errado como "portfólio". 195 desses
267 estão RETIRADOS — alguns desde 2015. Chamar 267 de portfólio francês infla
o que existe hoje em 3,7 vezes.

    REGISTERED_EVER ≠ CURRENTLY_AUTHORIZED

O TITULAR NÃO DECIDE O PAÍS
-----------------------------
A cicatriz italiana chega aqui e machuca menos, mas machuca. Dos 267, um é da
`ADAMA Agriculture B.V.` — entidade holandesa com registro FRANCÊS. Na Itália o
filtro ingênuo por titular nacional descartava 48% do portfólio; aqui descartaria
0,4%. A diferença é de tamanho, não de natureza:

    HOLDER_COUNTRY ≠ REGISTRATION_COUNTRY ≠ PORTFOLIO_COUNTRY

O QUE O CRUZAMENTO DOS 111 ACHOU (2026-08-30)
-----------------------------------------------
1. UMA FICHA NÃO É UM REGISTRO. As 111 fichas do catálogo francês escondem 62
   AMMs distintos: 33 registros aparecem com mais de um nome comercial, e o AMM
   2180260 sozinho tem CINCO fichas — Balesta, Gusto 3, Opposum, Surikate, Taste.
   Contar ficha como produto registrado infla 111 sobre 62: 79% a mais.

       CATALOG_ENTRY ≠ REGISTRATION

2. A VITRINE NÃO ACOMPANHA A AUTORIDADE. Cinco fichas continuam publicadas com
   registro RETIRADO: Merpan SC, Momentum F e Momentum Trio (retirados em
   31/10/2025), Elysium (24/05/2025) e Sunset (31/01/2025). O catálogo não mente
   — ele simplesmente não é o registro.

       PUBLIC_CATALOG_PRESENCE ≠ CURRENTLY_AUTHORIZED

3. HÁ PRODUTO ADAMA SOB REGISTRO DE OUTRA EMPRESA. A ficha `Milena` publica o
   AMM 2250282. Esse AMM existe no E-Phy, está AUTORIZADO — e se chama HARNIKO,
   titular GLOBACHEM NV. Não é do grupo ADAMA.

   Isto é o limite honesto do número 72: ele conta o que a ADAMA TITULA na
   França, e a ADAMA também apresenta produto registrado por terceiro. O
   crosswalk marca REGISTRATION_CONFLICT em vez de engolir a afirmação, e o
   número não é corrigido no escuro.

       HOLDER ≠ PORTFOLIO, e desta vez o titular nem é do grupo

O QUE ESTE ARQUIVO SE RECUSA A FAZER
--------------------------------------
Inventar alvo. 215 das 582 linhas de uso dizem só `Blé*Désherbage`: a cultura e o
tipo de tratamento, sem organismo nomeado. A fonte NÃO diz contra o quê. Preencher
o alvo por proximidade — "desherbagem, então é a erva daninha mais citada" —
fabricaria autorização.

    DOSE ≠ CROP_ISSUE_PAIR
    CO_PRESENCE ≠ AUTHORIZED_PAIR
    PATH ≠ IDENTITY
"""
import csv
import hashlib
import json
import os
import re
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
EPHY = os.path.join(ROOT, 'data', 'raw', 'FR', 'anses-ephy')
COUNTRY = 'FR'

FONTE_REGULATORIA = {
    'SOURCE_ID': 'FR-T4-001',
    'NAME': 'ANSES — catálogo E-Phy, dados abertos via data.gouv.fr',
    'URL': 'https://www.data.gouv.fr/fr/datasets/575e9fac88ee38072a640390/',
    'ROLE': 'REGULATORY_AUTHORITY',
    'LICENSE': 'Licence Ouverte (fr-lo)',
    'WHAT_IT_PROVES': ('AMM, titular, substâncias, formulação, função, estado, '
                       'usos autorizados com cultura×alvo, dose, BBCH, DAR, ZNT'),
    'WHAT_IT_DOES_NOT_PROVE': ['o que a ADAMA apresenta no catálogo comercial',
                               'disponibilidade comercial', 'preço', 'estoque'],
}
FONTE_CATALOGO = {
    'SOURCE_ID': 'FR-ADAMA-CATALOG',
    'NAME': 'ADAMA France — catálogo público',
    'URL': 'https://www.adama.com/france/fr',
    'ROLE': 'MANUFACTURER_CLAIM',
    'WHAT_IT_PROVES': 'o que a empresa APRESENTA localmente',
    'WHAT_IT_DOES_NOT_PROVE': ['registro', 'autorização', 'disponibilidade'],
    'ROUTE': 'HEADED_BROWSER_ONLY — curl e headless levam 403',
}

# ─────────────────────────────────────────────────────── estados do crosswalk
LOCAL_REGISTERED = 'LOCAL_REGISTERED'
LOCAL_PRESENT_NOT_PROVED = 'LOCAL_PRESENT_BUT_REGISTRATION_NOT_PROVED'
REGISTERED_NOT_IN_CATALOG = 'REGISTERED_BUT_NOT_IN_PUBLIC_CATALOG'
REGISTRATION_CONFLICT = 'REGISTRATION_CONFLICT'
CROSSWALK_NOT_KNOWN = 'NOT_KNOWN'
# Existe, e NÃO entra por eliminação: exige a autoridade devolvendo ausência,
# não a minha falta de casamento.
NOT_REGISTERED = 'NOT_REGISTERED'

# ──────────────────────────────────────────────────── origem da relação cultura
CROP_DECLARED = 'DECLARED'                 # o catálogo diz "autorisé sur X"
CROP_CITED = 'CITED'                       # X aparece no texto, sem autorização
CROP_REGULATORY = 'AUTHORIZED_REGULATORY'  # a tabela de usos da ANSES
ORIGENS_CULTURA = (CROP_DECLARED, CROP_CITED, CROP_REGULATORY)

# ──────────────────────────────────────────────────────── espécies documentais
ETIQUETTE = 'ETIQUETTE'                    # o rótulo autorizado — documento legal
FICHE_TECHNIQUE = 'FICHE_TECHNIQUE'
FICHE_SECURITE = 'FICHE_DE_DONNEES_DE_SECURITE'
BROCHURE = 'BROCHURE'
CATALOGUE = 'CATALOGUE'
GUIDE = 'GUIDE'
DOC_OUTRO = 'AUTRE_DOCUMENT'
TIPOS_DOC = (ETIQUETTE, FICHE_TECHNIQUE, FICHE_SECURITE, BROCHURE, CATALOGUE,
             GUIDE, DOC_OUTRO)

# Nome/rota → espécie. A ordem importa, e o genérico fica por último: chamar todo
# PDF de rótulo faria frase de venda herdar a autoridade de um ato administrativo.
PADRAO_DOC = (
    (r'etiquett|\bamm\b.*etiq', ETIQUETTE),
    (r'fds|fiche[-_\s]*(?:de[-_\s]*)?(?:donnees[-_\s]*de[-_\s]*)?securite|sds|msds',
     FICHE_SECURITE),
    (r'fiche[-_\s]*technique|\bft\b', FICHE_TECHNIQUE),
    (r'brochure|plaquette|depliant', BROCHURE),
    (r'catalogue', CATALOGUE),
    (r'guide|livre[-_\s]*blanc', GUIDE),
)


def tipo_de_documento(url_ou_nome):
    """Espécie documental a partir da rota/nome. Sem casar: AUTRE_DOCUMENT."""
    s = (url_ou_nome or '').lower()
    for padrao, tipo in PADRAO_DOC:
        if re.search(padrao, s, re.I):
            return tipo
    return DOC_OUTRO


# ────────────────────────────────────────────────────────── chave de storage
_ILEGAIS = re.compile(r'[^A-Za-z0-9._-]+')


def storage_key(country, registration_id, doc_type, nome_original, sha_conteudo):
    """Chave determinística, segura e ENDEREÇADA POR CONTEÚDO.

    Portado da cicatriz espanhola, onde o servidor recusou 10 de 196 com
    `InvalidKey`:
      · NFC antes de tudo — "é" composto e decomposto são o MESMO nome, e sem
        normalizar viram duas chaves para um arquivo. Em francês isso não é raro;
      · sem URL-decode silencioso — `%20` não vira espaço aqui, porque decodificar
        muda a identidade do que foi baixado;
      · extensão preservada;
      · o nome original vive no metadata, não na chave.

    E uma cicatriz francesa, encontrada pelo teste de colisão ANTES de qualquer
    upload: 153 documentos do catálogo, e 29 pares deles cairiam na MESMA chave
    com bytes diferentes. A causa é a rota `/media/NNNN/download?attachment` —
    o nome do arquivo é literalmente "download" para dezenas de PDFs, e quatro
    fichas do mesmo AMM 2240001 (Bilbatra, Forapro, Hermione, Robava) apontam
    para documentos distintos. Chave por NOME os empilharia num só objeto, e o
    último upload apagaria os outros sem erro nenhum.

    Por isso o `sha16` do CONTEÚDO abre o nome do objeto, como já era na Espanha:

        · duas capturas do mesmo arquivo caem no mesmo lugar (idempotente);
        · dois arquivos diferentes NUNCA caem no mesmo lugar;
        · sobrescrita silenciosa deixa de ser possível pelo formato da chave.

    `sha_conteudo` é obrigatório de propósito. Um valor padrão faria a proteção
    sumir exatamente onde ela é mais necessária: em quem esqueceu de passá-lo.

        PATH ≠ IDENTITY — a identidade continua sendo país + AMM + sha256 +
        metadata. O nome físico é infraestrutura, e pode ser seguro sem mudar o
        que o asset É.
    """
    if not sha_conteudo or len(str(sha_conteudo)) < 16:
        raise ValueError('storage_key exige o sha256 do conteúdo: sem ele a chave '
                         'não é endereçada por conteúdo e sobrescreve em silêncio')
    nome = unicodedata.normalize('NFC', str(nome_original or ''))
    raiz, ext = os.path.splitext(nome)
    ext = _ILEGAIS.sub('', ext)[:12]
    raiz_segura = _ILEGAIS.sub('-', raiz).strip('-')[:60] or 'document'
    return '%s/%s/%s/%s-%s%s' % (country, registration_id or 'SEM-AMM',
                                 doc_type, str(sha_conteudo)[:16], raiz_segura, ext)


def captura(amm, source, source_version):
    """Identidade de CAPTURA. Nunca cria registro novo.

    Identidade regulatória é (COUNTRY, AMM); a captura é essa mais (SOURCE,
    SOURCE_VERSION). Ler o mesmo E-Phy semana que vem produz outra captura do
    MESMO registro.
    """
    return {'CAPTURE_KEY': (COUNTRY, str(amm), source, source_version),
            'REGISTRATION_KEY': (COUNTRY, str(amm)),
            'WHY': 'CAPTURE ≠ REGISTRATION'}


# ══════════════════════════════════════════════════════════════════════════════
# O IDENTIFICADOR DE USO FRANCÊS — onde o par nasce amarrado, e onde ele não nasce
# ══════════════════════════════════════════════════════════════════════════════

TIPO_SEM_ALVO = 'TREATMENT_ONLY'
TIPO_COM_ALVO = 'ANCHORED_CROP_ISSUE'
TIPO_ILEGIVEL = 'UNPARSEABLE'


def usage_id(identificador):
    """`Vigne*Trt Part.Aer.*Mildiou(s)` → cultura, tratamento e alvo.

    Duas formas aparecem no dado, e a diferença entre elas é a diferença entre
    um fato e uma invenção:

        3 pedaços  Vigne*Trt Part.Aer.*Mildiou(s)   -> par ANCORADO pela ANSES
        2 pedaços  Blé*Désherbage                   -> cultura e tipo, SEM alvo

    Nas 215 linhas de 2 pedaços a fonte não nomeia organismo nenhum. Devolver um
    alvo ali seria fabricar autorização, e é por isso que `ISSUE` sai `None` e
    `IS_ANCHORED_PAIR` sai `False` — não como lacuna a preencher depois, mas como
    o que a fonte de fato disse.
    """
    bruto = str(identificador or '').strip()
    if not bruto:
        return {'KIND': TIPO_ILEGIVEL, 'CROP': None, 'TREATMENT': None,
                'ISSUE': None, 'IS_ANCHORED_PAIR': False, 'RAW': bruto,
                'WHY': 'identificador vazio'}
    partes = [p.strip() for p in bruto.split('*')]
    if len(partes) == 1:
        return {'KIND': TIPO_ILEGIVEL, 'CROP': partes[0], 'TREATMENT': None,
                'ISSUE': None, 'IS_ANCHORED_PAIR': False, 'RAW': bruto,
                'WHY': 'um pedaço só: há cultura e não há como saber o resto'}
    if len(partes) == 2:
        return {'KIND': TIPO_SEM_ALVO, 'CROP': partes[0], 'TREATMENT': partes[1],
                'ISSUE': None, 'IS_ANCHORED_PAIR': False, 'RAW': bruto,
                'WHY': ('a fonte dá cultura e tipo de tratamento e NÃO nomeia '
                        'organismo. DOSE ≠ CROP_ISSUE_PAIR')}
    return {'KIND': TIPO_COM_ALVO, 'CROP': partes[0],
            'TREATMENT': '*'.join(partes[1:-1]), 'ISSUE': partes[-1],
            'IS_ANCHORED_PAIR': True, 'RAW': bruto,
            'WHY': 'a própria ANSES amarra cultura e alvo no mesmo identificador'}


# ══════════════════════════════════════════════════════════════════════════════
# O LADO AUTORIDADE — lido do E-Phy, com o titular medido e não presumido
# ══════════════════════════════════════════════════════════════════════════════

# Nomes do grupo procurados no titular. `ADAMA` acha as duas entidades medidas;
# os outros estão aqui porque registro antigo pode ter ficado com o nome de antes
# da fusão, e não custa procurar o que não existe.
NOMES_DO_GRUPO = ('ADAMA', 'MAKHTESHIM', 'AGAN')

AUTORIZADO = 'AUTORISE'
RETIRADO = 'RETIRE'


def dobra(s):
    """Maiúscula sem acento, para comparar titular sem tropeçar em 'é'."""
    s = unicodedata.normalize('NFKD', str(s or '').upper())
    return ''.join(c for c in s if not unicodedata.combining(c))


def e_do_grupo(titular):
    """→ True se o titular é do grupo ADAMA, em qualquer entidade e qualquer país.

    Procurar `ADAMA FRANCE SAS` exato descartaria a `ADAMA Agriculture B.V.`, que
    tem registro francês válido. Na Itália o mesmo atalho custava 48%.
    """
    t = dobra(titular)
    return any(n in t for n in NOMES_DO_GRUPO)


def _ler(nome):
    caminho = os.path.join(EPHY, nome)
    with open(caminho, encoding='utf-8', newline='') as fh:
        return list(csv.DictReader(fh, delimiter=';'))


def registro_medido(so_autorizados=False):
    """Os produtos ADAMA do E-Phy. `so_autorizados` é o portfólio de hoje."""
    fora = []
    for r in _ler('produits_utf8.csv'):
        if not e_do_grupo(r.get('titulaire')):
            continue
        estado = (r.get('Etat d’autorisation') or '').strip()
        if so_autorizados and estado != AUTORIZADO:
            continue
        fora.append({
            'REGISTRATION_ID': (r.get('numero AMM') or '').strip(),
            'PRODUCT': (r.get('nom produit') or '').strip(),
            'SECOND_NAMES': (r.get('seconds noms commerciaux') or '').strip(),
            'HOLDER': (r.get('titulaire') or '').strip(),
            'SUBSTANCES': (r.get('Substances actives') or '').strip(),
            'FUNCTION': (r.get('fonctions') or '').strip(),
            'FORMULATION': (r.get('formulations') or '').strip(),
            'STATE': estado,
            'PRODUCT_TYPE': (r.get('type produit') or '').strip(),
            'FIRST_AUTHORIZED': (r.get('Date de première autorisation') or '').strip(),
            'WITHDRAWN': (r.get('Date de retrait du produit') or '').strip(),
            'COUNTRY': COUNTRY,
        })
    return fora


def usos_medidos(amms=None):
    """As linhas de uso autorizado, já com o identificador aberto."""
    fora = []
    for u in _ler('usages_des_produits_autorises_utf8.csv'):
        amm = (u.get('numero AMM') or '').strip()
        if amms is not None and amm not in amms:
            continue
        alvo = usage_id(u.get('identifiant usage'))
        fora.append({
            'REGISTRATION_ID': amm,
            'PRODUCT': (u.get('nom produit') or '').strip(),
            'USAGE_RAW': alvo['RAW'], 'CROP': alvo['CROP'],
            'TREATMENT': alvo['TREATMENT'], 'ISSUE': alvo['ISSUE'],
            'IS_ANCHORED_PAIR': alvo['IS_ANCHORED_PAIR'], 'KIND': alvo['KIND'],
            'RELATION_ORIGIN': CROP_REGULATORY,
            'DOSE': (u.get('dose retenue') or '').strip(),
            'DOSE_UNIT': (u.get('dose retenue unite') or '').strip(),
            'BBCH_MIN': (u.get('stade cultural min (BBCH)') or '').strip(),
            'BBCH_MAX': (u.get('stade cultural max (BBCH)') or '').strip(),
            'PHI_DAYS': (u.get('delai avant recolte jour') or '').strip(),
            'MAX_APPLICATIONS': (u.get("nombre max d'application") or '').strip(),
            'ZNT_AQUATIC_M': (u.get('ZNT aquatique (en m)') or '').strip(),
            'USE_STATE': (u.get('etat usage') or '').strip(),
            'COUNTRY': COUNTRY,
        })
    return fora


def escopo_de_pais(produto):
    """De onde vem o COUNTRY de um produto. Do registro, nunca do titular."""
    return {
        'PORTFOLIO_COUNTRY': COUNTRY,
        'REGISTRATION_COUNTRY': COUNTRY,
        'REGISTRATION_AUTHORITY': FONTE_REGULATORIA['SOURCE_ID'],
        'HOLDER': produto.get('HOLDER'),
        'HOLDER_IS_FRENCH_ENTITY': 'FRANCE' in dobra(produto.get('HOLDER')),
        'WHY': 'HOLDER_COUNTRY ≠ REGISTRATION_COUNTRY ≠ PORTFOLIO_COUNTRY',
    }


def _chave_nome(s):
    return re.sub(r'[^A-Z0-9]+', '', dobra(s))


# O título das fichas vem às vezes com a razão social colada: "Balesta - ADAMA
# France sas". Comparar com o registro sem tirar isso faz TODO nome sujo falhar.
_SUFIXO_EMPRESA = re.compile(
    r'\s*[-–|]\s*ADAMA(\s+FRANCE)?(\s+S\.?A\.?S\.?)?\s*$', re.I)


def nome_comercial(titulo):
    """→ o nome do produto, sem a razão social que o título às vezes carrega.

    O valor bruto NUNCA é jogado fora por quem chama: este é um nome DERIVADO,
    e o título original continua no manifesto. Derivar sem guardar o original
    seria perder a chance de descobrir que a derivação errou.
    """
    return _SUFIXO_EMPRESA.sub('', str(titulo or '').strip()).strip()


def nomes_do_registro(r):
    """Todos os nomes sob os quais um AMM é vendido. O registrado e os segundos.

    Medido em 2026-08-30, e é o achado que mais dói: o AMM 2180260 está no E-Phy
    como CARAKOL 3 e é vendido no catálogo francês como BALESTA e como GUSTO 3.
    O campo `seconds noms commerciaux` lista seis nomes para esse único registro.

    Na amostra de dez, CINCO nomes de catálogo não são o nome registrado:

        Balesta    -> CARAKOL 3      Alasi   -> STEMPER
        Gusto 3    -> CARAKOL 3      Agave   -> TYPHON
        Klartan Up -> MAVRIK FLO

    Casar só pelo nome registrado erraria metade da amostra — e o erro sairia
    como LOCAL_PRESENT_BUT_REGISTRATION_NOT_PROVED, que parece prudência.
    """
    nomes = [r.get('PRODUCT')]
    segundos = str(r.get('SECOND_NAMES') or '')
    nomes += [x.strip() for x in re.split(r'[|;/]', segundos) if x.strip()]
    return [n for n in nomes if n]


def cruzar(item_catalogo, registro):
    """Catálogo público ↔ registro oficial. Um produto por vez, sem fundir.

    Casa por AMM quando o catálogo publica o número. Quando não publica, tenta o
    nome — o registrado E os segundos nomes comerciais — e o resultado nunca sobe
    a LOCAL_REGISTERED: nome não é registro, e o máximo que ele dá é um candidato.
    """
    por_id = {str(r.get('REGISTRATION_ID') or '').strip(): r for r in registro}
    por_nome = {}
    for r in registro:
        for n in nomes_do_registro(r):
            por_nome.setdefault(_chave_nome(n), []).append(r)

    amm = str(item_catalogo.get('REGISTRATION_ID') or '').strip()
    if amm:
        if amm in por_id:
            return {'STATE': LOCAL_REGISTERED, 'REGISTRATION_ID': amm,
                    'MATCHED_BY': 'REGISTRATION_ID',
                    'REGISTRATION_EVIDENCE': FONTE_REGULATORIA['SOURCE_ID']}
        return {'STATE': REGISTRATION_CONFLICT, 'REGISTRATION_ID': amm,
                'MATCHED_BY': 'REGISTRATION_ID',
                'WHY': ('o catálogo publica um AMM que não existe entre os '
                        'registros ADAMA medidos na ANSES')}

    limpo = nome_comercial(item_catalogo.get('PRODUCT_NAME'))
    candidatos = por_nome.get(_chave_nome(limpo), [])
    # `dict.fromkeys` em vez de `set`: o mesmo registro pode ser alcançado pelo
    # nome registrado E por um segundo nome, e isso é UM candidato, não dois.
    candidatos = list({c['REGISTRATION_ID']: c for c in candidatos}.values())
    if len(candidatos) == 1:
        alvo = candidatos[0]
        por_segundo = _chave_nome(limpo) != _chave_nome(alvo.get('PRODUCT'))
        return {'STATE': LOCAL_PRESENT_NOT_PROVED, 'REGISTRATION_ID': None,
                'CANDIDATE_REGISTRATION_ID': alvo.get('REGISTRATION_ID'),
                'CANDIDATE_REGISTERED_NAME': alvo.get('PRODUCT'),
                'MATCHED_BY': 'SECOND_NAME' if por_segundo else 'NAME_ONLY',
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


MANIFESTO_CATALOGO = os.path.join(ROOT, 'data', 'raw', COUNTRY, 'adama-website',
                                  'MANIFESTO-CATALOGO.json')


def crosswalk(fichas=None, registro=None):
    """Catálogo ↔ ANSES, com as duas contagens que não podem ser a mesma.

    FICHAS são apresentações comerciais. REGISTROS são AMMs. Uma ficha e um
    registro parecem a mesma coisa até o dia em que duas fichas publicam o mesmo
    AMM — e então somar fichas conta o mesmo registro duas vezes.

        CATALOG_ENTRY ≠ REGISTRATION
    """
    if fichas is None:
        if not os.path.isfile(MANIFESTO_CATALOGO):
            return {'STATE': 'CATALOG_NOT_COLLECTED'}
        with open(MANIFESTO_CATALOGO, encoding='utf-8') as fh:
            fichas = json.load(fh)['PRODUCTS']

    registro = registro_medido() if registro is None else registro
    por_id = {r['REGISTRATION_ID']: r for r in registro}
    vivos = {r['REGISTRATION_ID'] for r in registro if r['STATE'] == AUTORIZADO}
    estados = {}
    amms_no_catalogo = set()
    conflitos = []
    vitrine_com_retirado = []
    for f in fichas:
        r = cruzar({'PRODUCT_NAME': f.get('PRODUCT_NAME'),
                    'REGISTRATION_ID': f.get('REGISTRATION_ID_CLAIMED')}, registro)
        estados[r['STATE']] = estados.get(r['STATE'], 0) + 1
        if r['STATE'] == LOCAL_REGISTERED:
            amms_no_catalogo.add(r['REGISTRATION_ID'])
            alvo = por_id.get(r['REGISTRATION_ID'])
            if alvo and alvo['STATE'] != AUTORIZADO:
                vitrine_com_retirado.append({
                    'PRODUCT': f.get('PRODUCT_NAME'),
                    'REGISTRATION_ID': r['REGISTRATION_ID'],
                    'REGISTERED_NAME': alvo['PRODUCT'],
                    'REGULATORY_STATE': alvo['STATE'],
                    'WITHDRAWN': alvo['WITHDRAWN']})
        elif r['STATE'] == REGISTRATION_CONFLICT:
            conflitos.append({'PRODUCT': f.get('PRODUCT_NAME'),
                              'CLAIMED': f.get('REGISTRATION_ID_CLAIMED'),
                              'WHY': r.get('WHY')})

    # O outro lado do cruzamento: registrado e ausente da vitrine.
    fora_do_catalogo = sorted(vivos - amms_no_catalogo)
    return {
        'CATALOG_ENTRIES': len(fichas),
        'CATALOG_ENTRIES_WITH_AMM_CLAIM': sum(
            1 for f in fichas if f.get('REGISTRATION_ID_CLAIMED')),
        'DISTINCT_REGISTRATIONS_BEHIND_CATALOG': len(amms_no_catalogo),
        'CATALOG_ENTRIES_MINUS_REGISTRATIONS':
            len(amms_no_catalogo) and len(fichas) - len(amms_no_catalogo),
        'REGULATORY_AUTHORIZED': len(vivos),
        'STATES': estados,
        'REGISTERED_BUT_NOT_IN_PUBLIC_CATALOG': len(fora_do_catalogo),
        'REGISTERED_NOT_IN_CATALOG_AMMS': fora_do_catalogo,
        # A vitrine não acompanha a autoridade em tempo real, e isso é um fato
        # sobre a vitrine — não um erro de leitura.
        'IN_CATALOG_BUT_REGISTRATION_WITHDRAWN': len(vitrine_com_retirado),
        'CATALOG_SHOWING_WITHDRAWN': vitrine_com_retirado,
        'REGISTRATION_CONFLICTS': conflitos,
        'NOT_REGISTERED': 0,
        'WHY_NOT_REGISTERED_ZERO': (
            'NOT_REGISTERED exige a autoridade devolvendo ausência para aquele '
            'produto. Falta de casamento aqui vira LOCAL_PRESENT_BUT_'
            'REGISTRATION_NOT_PROVED, nunca NOT_REGISTERED'),
    }


def censo():
    """Os números do lado autoridade. É o que o handoff francês pode afirmar hoje."""
    todos = registro_medido()
    vivos = [p for p in todos if p['STATE'] == AUTORIZADO]
    amms_vivos = {p['REGISTRATION_ID'] for p in vivos}
    usos = usos_medidos({p['REGISTRATION_ID'] for p in todos})
    ancorados = [u for u in usos if u['IS_ANCHORED_PAIR']]
    sem_alvo = [u for u in usos if u['KIND'] == TIPO_SEM_ALVO]
    return {
        'SOURCE': FONTE_REGULATORIA['SOURCE_ID'],
        'COUNTRY': COUNTRY,
        'REGULATORY_PRODUCTS_EVER': len(todos),
        'REGULATORY_PRODUCTS_AUTHORIZED': len(vivos),
        'REGULATORY_PRODUCTS_WITHDRAWN': len(todos) - len(vivos),
        'HOLDERS': sorted({p['HOLDER'] for p in todos}),
        'USE_ROWS': len(usos),
        'AMMS_WITH_USE': len({u['REGISTRATION_ID'] for u in usos}),
        'AMMS_AUTHORIZED_WITHOUT_USE': sorted(
            amms_vivos - {u['REGISTRATION_ID'] for u in usos}),
        'CROP_ISSUE_ANCHORED_ROWS': len(ancorados),
        'CROP_ISSUE_ANCHORED_DISTINCT': len({(u['CROP'], u['ISSUE']) for u in ancorados}),
        'CROP_TREATMENT_NO_ISSUE_ROWS': len(sem_alvo),
        'CROP_TREATMENT_NO_ISSUE_DISTINCT': len({(u['CROP'], u['TREATMENT'])
                                                 for u in sem_alvo}),
        'CROPS_DISTINCT': len({u['CROP'] for u in usos if u['CROP']}),
        'ROWS_WITH_DOSE': sum(1 for u in usos if u['DOSE']),
        'ROWS_WITH_BBCH_MIN': sum(1 for u in usos if u['BBCH_MIN']),
        'ROWS_WITH_BBCH_MAX': sum(1 for u in usos if u['BBCH_MAX']),
        'ROWS_WITH_PHI': sum(1 for u in usos if u['PHI_DAYS']),
        'CATALOG_PRODUCTS': None,
        'WHY_CATALOG_NULL': ('o catálogo público é outra fonte e ainda não foi '
                             'medido nesta rodada. CATALOG_PRESENCE ≠ REGISTRATION'),
    }


def main():
    c = censo()
    largura = max(len(k) for k in c)
    for k, v in c.items():
        if isinstance(v, list) and len(v) > 6:
            v = '%d itens' % len(v)
        print('%-*s : %s' % (largura, k, v))
    return 0


if __name__ == '__main__':
    sys.exit(main())
