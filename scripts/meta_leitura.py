#!/usr/bin/env python3
"""
O QUE O ANUNCIO DIZ — e, com o mesmo cuidado, o que ele NAO diz.

Este arquivo le o texto do criativo e tenta resolver produto, categoria,
ingrediente ativo, cultura, problema e tipo de ativacao. Cada resposta sai com
um estado, e o estado e tao importante quanto a resposta:

    PROVED     o termo aparece LITERALMENTE no texto da fonte
    PARTIAL    aparece so o grupo ("cereales", "malas hierbas"), nao a especie
    NOT_KNOWN  nao aparece

A REGRA QUE MAIS SEGURA A MAO
------------------------------
Imagem de trigo NAO vira CROP=trigo. Este arquivo nem olha imagem, de proposito.
E nome comercial NAO vira ingrediente ativo: saber que "Ampligo" contem
lambda-cialotrina e conhecimento de fora, que precisa de validacao regulatoria
propria. Aqui, ingrediente so sai se o proprio anuncio escrever o nome dele.

    NOME_COMERCIAL != INGREDIENTE_ATIVO
    IMAGEM != PROVA

DE ONDE VEM O VOCABULARIO
--------------------------
Duas origens, e elas nao se misturam no registro:

1. `X-007-canonical-agro-dictionary.json`, que ja existe neste acervo: 105 pares
   cultura x alvo com nome frances de campo, codigo EPPO e nome cientifico,
   construidos com proposta espanhola e verificacao na EPPO Global Database.
   Termo daqui sai com `lexicon_source = X-007`.

2. Uma semente declarada a mao para espanhol e italiano, que o X-007 nao cobre
   porque nasceu do registro frances. Termo daqui sai com
   `lexicon_source = SEED_DECLARED` — e assumidamente nosso, nao da fonte.

Um termo do nosso lexico casando com o texto do anuncio prova que A PALAVRA
esta ali. Nao prova que o problema existe no campo, nem que o produto e
autorizado naquele pais. Sao camadas diferentes, e a missao pede que continuem
diferentes.

    PALAVRA_NO_ANUNCIO != PROBLEMA_NO_CAMPO
    ANUNCIO_OBSERVADO != REGISTRO_LOCAL
"""
import json
import os
import re
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
X007 = os.path.join(ROOT, 'data', 'samples', 'X-007-canonical-agro-dictionary.json')

PROVED = 'PROVED'
PARTIAL = 'PARTIAL'
NOT_KNOWN = 'NOT_KNOWN'


def norm(s):
    s = unicodedata.normalize('NFD', (s or '').lower())
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    return re.sub(r'\s+', ' ', s)


# ── categoria de produto ─────────────────────────────────────────────────────
# So palavras que o texto escreve. "OTHER" nao existe por palpite: se nenhuma
# aparece, e NOT_KNOWN.
CATEGORIA = {
    'HERBICIDE': ['herbicida', 'herbicide', 'erbicida', 'diserbante',
                  'desherbage', 'desherbant', 'malas hierbas', 'mauvaises herbes'],
    'FUNGICIDE': ['fungicida', 'fungicide', 'antioidico', 'antiperonosporico'],
    'INSECTICIDE': ['insecticida', 'insecticide', 'insetticida', 'acaricida',
                    'acaricide', 'nematicida'],
    'BIOCONTROL': ['biocontrol', 'biologico', 'biologique', 'bioprotection',
                   'lucha biologica', 'lotta biologica'],
    'BIOSTIMULANT': ['bioestimulante', 'biostimulant', 'biostimolante'],
    'SEED': ['semilla', 'semillas', 'sementi', 'semence', 'semences', 'hibrido',
             'ibrido', 'variedad', 'varieta', 'variete'],
    'FERTILIZER': ['fertilizante', 'fertilizzante', 'engrais', 'abono',
                   'concime', 'nutricion vegetal', 'nutrizione'],
    'AGTECH': ['agtech', 'plataforma digital', 'app agricola', 'agricultura digital',
               'agricoltura digitale', 'agriculture numerique'],
}

# ── tipo de ativacao ─────────────────────────────────────────────────────────
ATIVACAO = {
    'WEBINAR': ['webinar', 'webinaire', 'seminario online', 'diretta online'],
    'FIELD_EVENT': ['jornada de campo', 'dia de campo', 'giornata in campo',
                    'campo demostrativo', 'campo prova', 'visite d essai',
                    'porte aperte', 'demo en campo', 'ensayo de campo'],
    'LEAD_GENERATION': ['registrate', 'inscribete', 'iscriviti', 'inscrivez',
                        'descarga la guia', 'scarica la guida', 'telecharger',
                        'solicita informacion', 'richiedi informazioni',
                        'contactanos', 'contattaci'],
    'TECHNICAL_EDUCATION': ['como aplicar', 'dosis', 'dose', 'modo de empleo',
                            'recomendaciones tecnicas', 'consigli tecnici',
                            'conseils techniques', 'momento de aplicacion',
                            'epoca de aplicacion'],
    'SEASONAL_CAMPAIGN': ['campana de', 'campagna', 'campagne', 'esta temporada',
                          'questa stagione', 'cette saison'],
    'CORPORATE_COMMUNICATION': ['sostenibilidad', 'sostenibilita', 'durabilite',
                                'nuestro compromiso', 'il nostro impegno',
                                'notre engagement', 'trabaja con nosotros',
                                'lavora con noi', 'rejoignez'],
}

# Grupos: aparecem no texto, mas nao identificam especie. Viram PARTIAL.
GRUPOS_CULTURA = ['cereales', 'cereali', 'cereales de invierno', 'hortalizas',
                  'ortaggi', 'legumes', 'frutales', 'frutta', 'arboriculture',
                  'cultivos', 'colture', 'cultures']
GRUPOS_PROBLEMA = ['malas hierbas', 'mauvaises herbes', 'infestanti', 'hongos',
                   'funghi', 'champignons', 'plagas', 'parassiti', 'ravageurs',
                   'enfermedades', 'malattie', 'maladies', 'insectos', 'insetti']

# Semente declarada por nos: ES e IT, que o X-007 (nascido do registro frances)
# nao traz. Cada linha e uma escolha nossa, e o registro diz isso.
SEED_CULTURA = {
    'Vitis vinifera': ['vid', 'viña', 'vina', 'viñedo', 'vite', 'vigneto', 'uva'],
    'Triticum aestivum': ['trigo', 'frumento', 'grano tenero', 'ble'],
    'Hordeum vulgare': ['cebada', 'orzo', 'orge'],
    'Zea mays': ['maiz', 'mais', 'maïs'],
    'Olea europaea': ['olivo', 'olivar', 'oliveto', 'olivier'],
    'Solanum lycopersicum': ['tomate', 'pomodoro'],
    'Malus domestica': ['manzano', 'melo', 'pommier'],
    'Prunus persica': ['melocotonero', 'pesco', 'pecher'],
    'Citrus': ['citricos', 'agrumi', 'agrumes', 'naranjo', 'arancio'],
    'Helianthus annuus': ['girasol', 'girasole', 'tournesol'],
    'Brassica napus': ['colza'],
    'Beta vulgaris': ['remolacha', 'barbabietola', 'betterave'],
    'Oryza sativa': ['arroz', 'riso', 'riz'],
}
SEED_PROBLEMA = {
    'Plasmopara viticola': ['mildiu', 'peronospora', 'mildiou'],
    'Erysiphe necator': ['oidio', 'oidium'],
    'Botrytis cinerea': ['botritis', 'botrite', 'botrytis'],
    'Venturia oleaginea': ['repilo'],
    'Zymoseptoria tritici': ['septoria', 'septoriosis'],
    'Puccinia': ['roya', 'ruggine', 'rouille'],
    'Amaranthus': ['amaranto', 'bledo'],
    'Alternaria': ['alternaria'],
    'Fusarium': ['fusarium', 'fusariosis', 'fusariosi'],
    'Tuta absoluta': ['tuta absoluta', 'tuta'],
    'Halyomorpha halys': ['cimice asiatica', 'chinche apestoso'],
}


def _x007():
    if not os.path.exists(X007):
        return {}, {}
    with open(X007, encoding='utf-8') as f:
        d = json.load(f)
    culturas, problemas = {}, {}

    def _acolher(destino, canonico, original):
        # o X-007 as vezes traz o canonico como LISTA (um termo frances que casou
        # com mais de uma especie). Achatar aqui, e nao escolher uma por conta
        # propria, preserva a ambiguidade que a fonte declarou.
        for c in (canonico if isinstance(canonico, list) else [canonico]):
            if not isinstance(c, str) or not c:
                continue
            destino.setdefault(c, set()).update({norm(original), norm(c)})

    for r in d.get('records', []):
        _acolher(culturas, r.get('CANONICAL_CROP'), r.get('ORIGINAL_CROP'))
        _acolher(problemas, r.get('CANONICAL_TARGET'), r.get('ORIGINAL_TARGET'))
    return ({k: sorted(v) for k, v in culturas.items()},
            {k: sorted(v) for k, v in problemas.items()})


def lexico():
    cx, px = _x007()
    cultura = {k: [(t, 'X-007') for t in v if len(t) > 3] for k, v in cx.items()}
    problema = {k: [(t, 'X-007') for t in v if len(t) > 3] for k, v in px.items()}
    for k, termos in SEED_CULTURA.items():
        cultura.setdefault(k, []).extend((norm(t), 'SEED_DECLARED') for t in termos)
    for k, termos in SEED_PROBLEMA.items():
        problema.setdefault(k, []).extend((norm(t), 'SEED_DECLARED') for t in termos)
    return cultura, problema


_LEX_CULTURA, _LEX_PROBLEMA = lexico()


def _casar(texto_norm, lex):
    achados = []
    for canonico, termos in lex.items():
        for termo, fonte in termos:
            if not termo or len(termo) < 4:
                continue
            if re.search(r'\b' + re.escape(termo) + r'\b', texto_norm):
                achados.append({'canonical': canonico, 'term_matched': termo,
                                'lexicon_source': fonte, 'state': PROVED})
                break
    return achados


def _grupos(texto_norm, grupos, rotulo):
    return [{'canonical': None, 'term_matched': g, 'lexicon_source': 'SEED_DECLARED',
             'state': PARTIAL, 'nota': '%s de grupo, nao de especie' % rotulo}
            for g in grupos if re.search(r'\b' + re.escape(g) + r'\b', texto_norm)]


# ── produto ──────────────────────────────────────────────────────────────────
# O simbolo (R) ou (TM) e a declaracao de marca feita PELO ANUNCIANTE. Isso e
# prova. Uma palavra em maiusculas e so uma palavra em maiusculas.
_MARCA_REG = re.compile(r'([A-Z][A-Za-z0-9\-]{2,20})\s*[®™]')
_MAIUSCULA = re.compile(r'\b([A-Z]{4,15})\b')
_PARADAS = {'ADAMA', 'BASF', 'BAYER', 'CORTEVA', 'SYNGENTA', 'NUFARM', 'UPL',
            'FMC', 'HTTP', 'HTTPS', 'WWW', 'ONLINE', 'GRATIS', 'NUEVO', 'NUOVO',
            'CLICK', 'LINK', 'BIO', 'AGRO', 'CROP', 'SCIENCE'}


def produtos(texto):
    reg = [{'product_name': m.group(1), 'state': PROVED,
            'proof': 'MARCA_REGISTRADA_NO_TEXTO'}
           for m in _MARCA_REG.finditer(texto or '')]
    vistos = {p['product_name'].lower() for p in reg}
    caps = []
    for m in _MAIUSCULA.finditer(texto or ''):
        t = m.group(1)
        if t in _PARADAS or t.lower() in vistos:
            continue
        vistos.add(t.lower())
        caps.append({'product_name': t, 'state': PARTIAL,
                     'proof': 'PALAVRA_EM_MAIUSCULAS_SEM_SIMBOLO_DE_MARCA'})
    return reg + caps[:5]


# Ingrediente ativo so sai se o texto escrever o nome. A lista e curta de
# proposito: e melhor NOT_KNOWN do que um ingrediente atribuido por reputacao
# do nome comercial.
INGREDIENTES = ['glifosato', 'glyphosate', 'azoxistrobina', 'azoxystrobine',
                'protioconazol', 'prothioconazole', 'tebuconazol', 'tebuconazole',
                'mancozeb', 'cobre', 'rame', 'cuivre', 'azufre', 'zolfo', 'soufre',
                'lambda cihalotrina', 'lambda cyhalothrine', 'abamectina',
                'clorantraniliprol', 'spinosad', 'deltametrina', 'deltamethrine',
                'metalaxil', 'metalaxyl', 'fluopyram', 'boscalid', 'difenoconazol']


def ingredientes(texto_norm):
    return [{'active_ingredient': i, 'state': PROVED,
             'proof': 'INGREDIENTE_ESCRITO_NO_ANUNCIO'}
            for i in INGREDIENTES
            if re.search(r'\b' + re.escape(norm(i)) + r'\b', texto_norm)]


def _dicionario(texto_norm, mapa):
    return [k for k, termos in mapa.items()
            if any(re.search(r'\b' + re.escape(norm(t)) + r'\b', texto_norm)
                   for t in termos)]


# ── criador ──────────────────────────────────────────────────────────────────
_HANDLE = re.compile(r'@([A-Za-z0-9_.]{3,30})')
PAID_NOT_PROVED = 'NOT_PROVED'


def criadores(texto):
    handles = sorted(set(_HANDLE.findall(texto or '')))
    if not handles:
        return []
    return [{'creator_handle': '@' + h, 'creator_id': None, 'creator_role': NOT_KNOWN,
             'collaboration_observed': 'MENTION_IN_CREATIVE_TEXT',
             'paid_creator_relation': PAID_NOT_PROVED,
             'nota': 'aparecer no criativo NAO prova contrato pago com a pessoa'}
            for h in handles]


def ler(anuncio):
    texto = anuncio.get('creative_text') or ''
    tn = norm(texto)
    culturas = _casar(tn, _LEX_CULTURA) + _grupos(tn, GRUPOS_CULTURA, 'cultura')
    problemas = _casar(tn, _LEX_PROBLEMA) + _grupos(tn, GRUPOS_PROBLEMA, 'problema')
    cats = _dicionario(tn, CATEGORIA)
    ativ = _dicionario(tn, ATIVACAO)
    prods = produtos(texto)
    ings = ingredientes(tn)

    def estado(lista):
        if any(x.get('state') == PROVED for x in lista):
            return PROVED
        return PARTIAL if lista else NOT_KNOWN

    if not ativ:
        ativ = ['PRODUCT_AD'] if (prods and cats) else []
    return {
        'crop': culturas, 'crop_state': estado(culturas),
        'issue': problemas, 'issue_state': estado(problemas),
        'product_category': cats or [NOT_KNOWN],
        'product_candidates': prods, 'product_state': estado(prods),
        'active_ingredient': ings,
        'active_ingredient_state': PROVED if ings else NOT_KNOWN,
        'activation_type': ativ or [NOT_KNOWN],
        'creators': criadores(texto),
        'nota': ('cultura e problema sao PALAVRAS achadas no texto do anuncio. '
                 'Nao sao prova de problema no campo nem de registro local.'),
    }
