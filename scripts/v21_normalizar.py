#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OS IDS NORMALIZADOS — a base de tudo no V2.1 (§8 e §10).

    import v21_normalizar as N
    N.crop_id('mais')        → 'CROP_MAIZE'
    N.crop_id('Grapevine')   → 'CROP_GRAPEVINE'
    N.region_id('Veneto')    → 'REGION_VENETO'

⚠️ POR QUE ISTO EXISTE, E O QUE ELE CONSERTA
---------------------------------------------
O V2 gerou cruzamentos por INCLUSÃO DE TEXTO: procurava a palavra da cultura
dentro do campo livre `o_que`. Resultado medido: **36 IDs com a cultura errada**
e 7 de 19 cruzamentos contaminados. Um boletim de OLIVEIRA cuja descrição
mencionava milho entrou no cruzamento do MILHO.

    «string contains crop token» NÃO É UM JOIN. É uma coincidência de letras.

O §10 é explícito: normalizar ANTES, e depois juntar por ID EXATO.

⚠️ E A REGRA QUE IMPEDE O CONSERTO DE VIRAR OUTRO BUG
------------------------------------------------------
A normalização lê APENAS campos declarados de cultura (`crop`, `CROP`,
`crop_literal`), NUNCA a prosa. Se o campo declarado estiver vazio, o resultado
é `None` — e um registro sem cultura declarada simplesmente não participa de um
cruzamento por cultura.

    NÃO SABER A CULTURA É MELHOR DO QUE ADIVINHÁ-LA PELO TEXTO.
"""
import re
import unicodedata

# ── CULTURA ──────────────────────────────────────────────────────────────────
# Os apelidos são as formas que as QUATRO línguas do acervo usam: italiano das
# fontes, inglês do pacote anterior, português dos coletores, latim das fichas.
CROP_ALIAS = {
    'CROP_MAIZE': ['mais', 'mais dolce', 'granoturco', 'granturco', 'maize',
                   'corn', 'milho', 'sweet corn', 'zea mays'],
    'CROP_GRAPEVINE': ['vite', 'viti', 'vigneto', 'uva', 'uva da vino',
                       'uva da tavola', 'grapevine', 'grape', 'vine', 'videira',
                       'vid', 'vitis vinifera'],
    'CROP_DURUM_WHEAT': ['frumento duro', 'grano duro', 'durum', 'durum wheat',
                         'trigo duro'],
    'CROP_SOFT_WHEAT': ['frumento tenero', 'grano tenero', 'soft wheat',
                        'common wheat', 'trigo tenero', 'trigo mole'],
    'CROP_WHEAT_GENERIC': ['frumento', 'grano', 'wheat', 'trigo', 'cereali',
                           'cereals', 'cereali autunno vernini'],
    'CROP_BARLEY': ['orzo', 'barley', 'cevada'],
    'CROP_RICE': ['riso', 'risaia', 'rice', 'arroz', 'risone', 'oryza sativa'],
    'CROP_SOYBEAN': ['soia', 'soybean', 'soja', 'glycine max'],
    'CROP_SUGAR_BEET': ['barbabietola', 'barbabietola da zucchero', 'bietola',
                        'sugar beet', 'beterraba'],
    'CROP_OLIVE': ['olivo', 'olivi', 'oliveto', 'olive', 'oliva', 'olio d oliva',
                   'oliveira', 'azeitona', 'olea europaea'],
    'CROP_APPLE': ['melo', 'meli', 'mela', 'mele', 'apple', 'pomacee', 'maca',
                   'macieira', 'malus'],
    'CROP_PEAR': ['pero', 'peri', 'pera', 'pear'],
    'CROP_TOMATO': ['pomodoro', 'pomodoro da industria', 'tomato', 'tomate',
                    'solanum lycopersicum'],
    'CROP_PEACH': ['pesco', 'pesca', 'peach', 'nettarine', 'pessego'],
    'CROP_POTATO': ['patata', 'patate', 'potato', 'batata'],
    'CROP_SUNFLOWER': ['girasole', 'sunflower', 'girassol'],
    'CROP_KIWI': ['actinidia', 'kiwi'],
    'CROP_CITRUS': ['agrumi', 'citrus', 'arancio', 'limone'],
    'CROP_STONE_FRUIT': ['drupacee', 'stone fruit', 'susino', 'albicocco',
                         'ciliegio'],
    'CROP_VEGETABLES': ['orticole', 'ortaggi', 'vegetables', 'orticolo'],
}

# ── PROBLEMA ─────────────────────────────────────────────────────────────────
ISSUE_ALIAS = {
    'ISSUE_FLAVESCENCE': ['flavescenza', 'flavescenza dorata', 'flavescencia',
                          'giallumi', 'golden flavescence'],
    'ISSUE_SCAPHOIDEUS': ['scaphoideus', 'scaphoideus titanus', 'scafoideo'],
    'ISSUE_DOWNY_MILDEW': ['peronospora', 'plasmopara', 'downy mildew', 'mildiu'],
    'ISSUE_POWDERY_MILDEW': ['oidio', 'erysiphe', 'powdery mildew', 'mal bianco'],
    'ISSUE_BOTRYTIS': ['botrite', 'botrytis', 'muffa grigia', 'grey mould'],
    'ISSUE_SCAB': ['ticchiolatura', 'venturia', 'scab'],
    'ISSUE_SEPTORIA': ['septoria', 'septoriosi', 'zymoseptoria'],
    'ISSUE_FUSARIUM': ['fusarium', 'fusariosi', 'fusariose', 'don', 'micotossine',
                       'mycotoxin', 'micotossina'],
    'ISSUE_RUST': ['ruggine', 'puccinia', 'rust'],
    'ISSUE_CERCOSPORA': ['cercospora', 'cercosporiosi'],
    'ISSUE_BLAST': ['brusone', 'pyricularia', 'magnaporthe', 'blast'],
    'ISSUE_OLIVE_FLY': ['bactrocera oleae', 'mosca dell oliva', 'mosca dell olivo',
                        'olive fruit fly', 'mosca da oliveira'],
    'ISSUE_CODLING_MOTH': ['carpocapsa', 'cydia pomonella', 'codling moth'],
    'ISSUE_CORN_BORER': ['piralide', 'ostrinia', 'european corn borer'],
    'ISSUE_DIABROTICA': ['diabrotica'],
    'ISSUE_APHIDS': ['afidi', 'afide', 'aphis', 'myzus', 'aphid', 'pulgao'],
    'ISSUE_TUTA': ['tuta absoluta', 'tomato leafminer', 'tignola del pomodoro'],
    'ISSUE_GRAPE_MOTH': ['tignoletta', 'lobesia', 'grapevine moth', 'tignole'],
    'ISSUE_ECHINOCHLOA': ['echinochloa', 'giavone', 'giavona'],
    'ISSUE_LOLIUM': ['lolium', 'loietto', 'loglio'],
    'ISSUE_AMARANTHUS': ['amaranthus', 'amaranto'],
    'ISSUE_WEEDS_GENERIC': ['infestanti', 'malerbe', 'daninhas', 'weeds',
                            'diserbo', 'erbe infestanti'],
    'ISSUE_STINK_BUG': ['cimice asiatica', 'halyomorpha'],
    'ISSUE_DROUGHT': ['siccita', 'seca', 'drought'],
}

# ── REGIÃO ───────────────────────────────────────────────────────────────────
REGIOES = ['Abruzzo', 'Basilicata', 'Calabria', 'Campania', 'Emilia-Romagna',
           'Friuli-Venezia Giulia', 'Lazio', 'Liguria', 'Lombardia', 'Marche',
           'Molise', 'Piemonte', 'Puglia', 'Sardegna', 'Sicilia', 'Toscana',
           'Trentino-Alto Adige', 'Umbria', "Valle d'Aosta", 'Veneto']
REGION_ALIAS = {}
for r in REGIOES:
    rid = 'REGION_' + re.sub(r'[^A-Z]+', '_', r.upper()).strip('_')
    REGION_ALIAS[rid] = [r.lower(), r.lower().replace('-', ' ')]
REGION_ALIAS['REGION_FRIULI_VENEZIA_GIULIA'] += ['fvg', 'friuli']
REGION_ALIAS['REGION_TRENTINO_ALTO_ADIGE'] += ['trentino', 'trento', 'bolzano',
                                               'sudtirol', 'alto adige']
REGION_ALIAS['REGION_EMILIA_ROMAGNA'] += ['emilia', 'romagna']
REGION_ALIAS['REGION_VALLE_D_AOSTA'] += ["valle d aosta", 'aosta']
ITALIA = 'GEO_ITALY'
UE = 'GEO_EU'


def _n(t):
    t = ''.join(c for c in unicodedata.normalize('NFD', str(t or ''))
                if unicodedata.category(c) != 'Mn')
    return re.sub(r'[^a-z0-9]+', ' ', t.lower()).strip()


def _casa(texto, tabela):
    """Casa por PALAVRA INTEIRA, do apelido mais longo para o mais curto.

    A ordem importa: «frumento duro» tem de ganhar de «frumento», senão trigo
    duro vira trigo genérico e o cruzamento junta duas culturas diferentes.
    """
    t = ' %s ' % _n(texto)
    if not t.strip():
        return None
    melhor = (0, None)
    for eid, apelidos in tabela.items():
        for a in apelidos:
            if ' %s ' % _n(a) in t and len(a) > melhor[0]:
                melhor = (len(a), eid)
    return melhor[1]


# Acima disto, o campo não declara nada: é prosa. Um rótulo de cultura real
# cabe em poucas palavras («barbabietola da zucchero» tem 24 caracteres).
MAX_ROTULO = 60


def _e_prosa(v):
    """Texto longo ou com pontuação de frase é PROSA, não rótulo declarado."""
    t = str(v or '').strip()
    return len(t) > MAX_ROTULO or bool(re.search(r'[.;:!?]\s', t))


def crop_id(*campos):
    """→ CROP_* ou None. ⚠️ SÓ CAMPO DECLARADO, NUNCA PROSA.

    A trava não é um comentário pedindo boa-fé: campos que parecem frase são
    RECUSADOS. Foi exatamente por ler o campo livre `o_que` que o V2 produziu
    36 IDs com a cultura errada — um boletim de oliveira cuja descrição citava
    milho entrou no cruzamento do milho.

        SE A CULTURA NÃO ESTÁ NUM CAMPO DE CULTURA, ELA NÃO ESTÁ DECLARADA.
    """
    for c in campos:
        if _e_prosa(c):
            continue
        r = _casa(c, CROP_ALIAS)
        if r:
            return r
    return None


def issue_id(*campos, permitir_prosa=False):
    """→ ISSUE_* ou None.

    O problema PODE vir de prosa quando o chamador declara que aceita — um
    boletim escreve «Cercospora» no meio da orientação e não num campo próprio.
    Mas o padrão é recusar, e quem aceitar tem de dizer isso por escrito.
    """
    for c in campos:
        if not permitir_prosa and _e_prosa(c):
            continue
        r = _casa(c, ISSUE_ALIAS)
        if r:
            return r
    return None


def region_ids(*campos):
    """→ lista. Um boletim pode nomear duas regiões («TOSCANA-FVG»)."""
    achadas = []
    for c in campos:
        t = ' %s ' % _n(c)
        if not t.strip():
            continue
        for rid, apelidos in REGION_ALIAS.items():
            if rid in achadas:
                continue
            if any(' %s ' % _n(a) in t for a in apelidos):
                achadas.append(rid)
        if not achadas and re.search(r'\b(italia|italy|nazionale|nacional)\b', t):
            achadas.append(ITALIA)
        if not achadas and re.search(r'\b(ue|eu|europa|europeia|european)\b', t):
            achadas.append(UE)
    return achadas


def escopo(texto, nivel_declarado=None):
    """§7 · o escopo NUNCA sobe. Provincial não vira regional."""
    if nivel_declarado:
        n = str(nivel_declarado).upper()
        if n in ('EUROPEU', 'NACIONAL', 'MACROAREA', 'REGIONAL', 'PROVINCIAL',
                 'AREALE', 'AREAL', 'ESTACAO', 'PIAZZA', 'GRADE_DE_MODELO'):
            return 'AREALE' if n == 'AREAL' else n
    t = _n(texto)
    if re.search(r'\bprovinc', t):
        return 'PROVINCIAL'
    if re.search(r'\b(areal|areale|zona|lago|litorale|comprensor|metapontino)', t):
        return 'AREALE'
    if re.search(r'\b(stazione|estacao|station)\b', t):
        return 'ESTACAO'
    if re.search(r'\b(piazza|borsa|praca)\b', t):
        return 'PIAZZA'
    if re.search(r'\b(nord est|nord ovest|sud|isole|centro|macroarea)\b', t):
        return 'MACROAREA'
    if re.search(r'\b(europ|ue|eu)\b', t):
        return 'EUROPEU'
    if re.search(r'\b(itali|nazional|nacional)\b', t):
        return 'NACIONAL'
    if region_ids(texto):
        return 'REGIONAL'
    return 'NAO_SEI'


def client_safe(qa_status):
    """§8 · booleano explícito, e a regra é uma linha."""
    return qa_status in ('QA_PASS', 'QA_CORRECTED')
