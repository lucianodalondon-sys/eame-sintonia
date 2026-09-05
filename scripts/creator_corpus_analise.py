#!/usr/bin/env python3
"""
ANÁLISE DO ACERVO — o que o material diz, e por que essa pessoa é relevante.

    py scripts/creator_corpus_analise.py classificar   # tipos, cultura, assunto, marca
    py scripts/creator_corpus_analise.py fichas        # perfil de relevância por entidade
    py scripts/creator_corpus_analise.py entrega       # o relatório A–X

TUDO AQUI É GRÁTIS
--------------------
Nenhuma chamada paga. Esta etapa só lê o que a coleta preservou. Isso importa
porque análise errada se refaz de graça — e refazer coleta, não.

A PERGUNTA CENTRAL, E O NÚMERO QUE ELA NÃO PODE VIRAR
-------------------------------------------------------
"Por que essa pessoa é relevante para a ADAMA naquele COUNTRY × REGION × CROP?"
A resposta é um PERFIL de oito eixos medidos lado a lado (§7), nunca um
`ADAMA_RELEVANCE_SCORE`. Um número único esconde qual eixo está vazio — e o
eixo vazio é justamente o que o Marketing precisa enxergar antes de decidir.

AS TRÊS CONFUSÕES QUE ESTE ARQUIVO RECUSA
-------------------------------------------
  `QUERY_CROP != PROVED_CROP`. A cultura que aparece no texto entra em
  `CROPS_OBSERVED_IN_CORPUS` — campo PRÓPRIO. `CROPS_PROVED` continua sendo do
  Creator Map, e nada aqui o escreve.

  `LANGUAGE != COUNTRY`. Um vídeo em espanhol não põe o fato na Espanha.
  `COUNTRY_OF_FACT` só sai de `NOT_KNOWN` quando o texto nomeia o lugar — por
  PALAVRA INTEIRA, porque a busca por pedaço de string já mandou 21 artigos de
  efetor fúngico para a Grécia por causa da palavra *secreted*.

  `RECURRENCE != AUTHORITY`. Contar quantas vezes alguém fala de repilo
  caracteriza o padrão público da conta. Não mede qualidade, autoridade nem
  importância de mercado, e o artefato diz isso onde a contagem aparece.
"""
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import creator_corpus as cc                                  # noqa: E402

# ═════════════════════════════════════════════ léxicos
# Explícitos e pequenos de propósito: um léxico que ninguém consegue ler é um
# léxico que ninguém consegue auditar. Todo termo é casado por PALAVRA INTEIRA.

CULTURAS = {
    'OLIVE': ('olivo', 'olivos', 'olivar', 'aceituna', 'aceitunas', 'oliva',
              'olivier', 'oliveto', 'olive'),
    'TOMATO': ('tomate', 'tomates', 'tomatera', 'pomodoro', 'pomodori'),
    'PEPPER': ('pimiento', 'pimientos', 'peperone', 'poivron'),
    # `mais` sem acento SAIU do léxico: em francês é a conjunção "mas". Medido
    # neste corpus — 10 dos 11 materiais marcados como milho eram o canal
    # francês dizendo "mas", e um deles falava de azoto em cereal. A palavra
    # inteira estava certa; a palavra é que era outra.
    'MAIZE': ('maíz', 'maiz', 'maïs', 'granoturco'),
    'WHEAT': ('trigo', 'blé', 'ble', 'frumento', 'grano'),
    'BARLEY': ('cebada', 'orge', 'orzo'),
    'GRAPEVINE': ('viña', 'vina', 'viñedo', 'vid', 'vigne', 'vigneto', 'uva'),
    'PISTACHIO': ('pistacho', 'pistachos', 'pistacchio'),
    'ALMOND': ('almendro', 'almendra', 'amandier', 'mandorlo'),
    'CAROB': ('algarrobo', 'algarroba', 'carrube'),
    'CITRUS': ('cítricos', 'citricos', 'naranjo', 'limonero', 'agrumi'),
    'POTATO': ('patata', 'patatas', 'pomme de terre', 'papa'),
    'SUNFLOWER': ('girasol', 'tournesol', 'girasole'),
    'RAPESEED': ('colza',),
    'PROTECTED_HORTICULTURE': ('invernadero', 'invernaderos', 'serra', 'serre'),
}

ASSUNTOS = {
    'DISEASE': ('repilo', 'mildiu', 'oídio', 'oidio', 'septoria', 'septoriose',
                'roya', 'rouille', 'ruggine', 'botritis', 'botrytis',
                'peronospora', 'fusarium', 'verticillium', 'antracnosis',
                'hongo', 'hongos', 'enfermedad', 'maladie', 'malattia'),
    'PEST': ('mosca', 'trips', 'pulgón', 'pulgon', 'araña roja', 'arana roja',
             'mosca blanca', 'prays', 'cochinilla', 'nematodo', 'nematodos',
             'plaga', 'plagas', 'ravageur', 'ravageurs', 'parassita',
             'insecto', 'insectos', 'oruga', 'gusano'),
    'WEED': ('malas hierbas', 'hierba', 'amaranthus', 'bledo', 'adventices',
             'désherbage', 'desherbage', 'diserbo', 'infestanti', 'maleza'),
}

TRATAMENTO = ('fungicida', 'herbicida', 'insecticida', 'fongicide', 'herbicide',
              'insecticide', 'fitosanitario', 'fitosanitarios', 'tratamiento',
              'traitement', 'trattamento', 'aplicación', 'aplicacion',
              'pulvérisation', 'pulverisation', 'caldo', 'dosis', 'dose',
              'materia activa', 'principio activo', 'sustancia activa')
# `bio` sozinho SAIU: das 20 ocorrências, 14 eram o nome da própria empresa
# (Bio Campojoyma). Nome de marca não é sinal de manejo biológico.
BIOLOGICO = ('biológico', 'biologico', 'biocontrol', 'fauna auxiliar',
             'suelta', 'depredador', 'ecológico', 'ecologico')

# Sinais de FORMA do material — o que a peça é, não do que ela fala.
FORMA = {
    'MACHINERY': ('tractor', 'tracteur', 'trattore', 'cosechadora',
                  'moissonneuse', 'atomizador', 'pulverizador', 'vibrador',
                  'remolque', 'apero', 'maquinaria'),
    'HARVEST': ('cosecha', 'recolección', 'recoleccion', 'vendimia', 'moisson',
                'récolte', 'recolte', 'raccolta', 'campaña de recogida'),
    'PLANTING': ('siembra', 'sembrar', 'plantación', 'plantacion', 'semis',
                 'semina', 'trasplante'),
    'IRRIGATION': ('riego', 'regar', 'goteo', 'irrigation', 'irrigazione'),
    'NUTRITION': ('abonado', 'abono', 'fertilizante', 'fertilización',
                  'fertilizacion', 'engrais', 'concime', 'nutrición'),
    'FIELD_TRIAL': ('ensayo', 'ensayos', 'prueba de campo', 'essai', 'prova di campo',
                    'parcela de ensayo'),
    'EVENT': ('feria', 'jornada', 'jornadas', 'congreso', 'salon', 'salón',
              'fiera', 'evento', 'demostración', 'demostracion'),
    'FARM_LIFESTYLE': ('familia', 'pueblo', 'perro', 'amanecer', 'atardecer',
                       'gracias por', 'vida en el campo'),
    'CONSUMER_FACING': ('receta', 'recetas', 'degustación', 'degustacion',
                        'tienda', 'comprar', 'venta directa', 'ricetta'),
    'FARM_BUSINESS': ('precio', 'precios', 'mercado', 'cooperativa', 'exportación',
                      'exportacion', 'factura', 'rentabilidad', 'cliente'),
}

# §8 · marcas vigiadas + variantes escritas
MARCAS = {
    'BAYER': ('bayer', 'crop science'), 'SYNGENTA': ('syngenta',),
    'BASF': ('basf',), 'CORTEVA': ('corteva', 'pioneer'), 'FMC': ('fmc',),
    'UPL': ('upl',), 'NUFARM': ('nufarm',),
    'CERTIS BELCHIM': ('certis', 'belchim'), 'SEIPASA': ('seipasa',),
    'ADAMA': ('adama',),
}
# Rótulos que a PLATAFORMA aplica quando há pagamento declarado. Só eles sobem a
# escada até PAID/SPONSORED — texto elogioso não é rótulo de pagamento.
ROTULOS_PAGOS = ('paid partnership', 'colaboración pagada', 'colaboracion pagada',
                 'publicidad', 'publi', 'partenariat rémunéré', '#ad',
                 '#publicidad', '#sponsored', 'sponsorizzato', 'in collaborazione con')


def _achar(texto, mapa):
    """Devolve as chaves cujo léxico aparece no texto, por PALAVRA INTEIRA."""
    return sorted({k for k, termos in mapa.items()
                   if any(cc.contem_palavra(texto, t) for t in termos)})


def _texto(m):
    return ' '.join(str(m.get(c) or '') for c in ('TITLE', 'TEXT', 'CAPTION'))


# ═════════════════════════════════════════════ §5, §6, §8 · classificar
def classificar():
    materiais = cc.carregar('CORPUS-MATERIALS.json')
    if not materiais:
        print('SEM_MATERIAL — rode antes as fases de coleta'); raise SystemExit(1)
    universo = {e['ENTITY_ID']: e for e in cc.carregar('CORPUS-UNIVERSE.json')}

    eventos_de_marca = []
    for m in materiais:
        t = _texto(m)
        tipos = set()
        culturas = _achar(t, CULTURAS)
        assuntos = _achar(t, ASSUNTOS)
        formas = _achar(t, FORMA)

        if 'DISEASE' in assuntos:
            tipos.add('DISEASE_CONTENT')
        if 'PEST' in assuntos:
            tipos.add('PEST_CONTENT')
        if 'WEED' in assuntos:
            tipos.add('WEED_CONTENT')
        if any(cc.contem_palavra(t, p) for p in TRATAMENTO):
            tipos.update(('APPLICATION_CONTENT', 'CROP_PROTECTION'))
        if any(cc.contem_palavra(t, p) for p in BIOLOGICO):
            tipos.add('BIOLOGICALS')
        tipos.update(formas)
        # CROP_MANAGEMENT precisa ser GANHO. A primeira versão o dava a todo
        # material que nomeasse uma cultura, e o resultado foi 50 de 50 para uma
        # conta cuja legenda inteira era `Pequeña avería #viña #viticultura` —
        # hashtag de cultura não é manejo de cultura. Com D_TECHNICAL_DEPTH
        # contando CROP_MANAGEMENT, isso publicava "50 materiais técnicos" para
        # quem tinha zero. Agora exige a cultura MAIS um sinal de manejo.
        manejo = bool(tipos & {'HARVEST', 'PLANTING', 'IRRIGATION', 'NUTRITION',
                               'APPLICATION_CONTENT', 'CROP_PROTECTION',
                               'FIELD_TRIAL', 'BIOLOGICALS'}) or bool(assuntos)
        if culturas and manejo and not (tipos & {'CONSUMER_FACING', 'FARM_LIFESTYLE'}):
            tipos.add('CROP_MANAGEMENT')
        if tipos & {'HARVEST', 'PLANTING', 'IRRIGATION', 'APPLICATION_CONTENT'}:
            tipos.add('FIELD_ROUTINE')
        # TECHNICAL_EXPLANATION exige explicação, não só o nome do problema:
        # dizer "tengo repilo" não é explicar repilo. Sem esse degrau, todo
        # material com uma praga no texto viraria profundidade técnica.
        if (assuntos or tipos & {'CROP_PROTECTION'}) and any(
                cc.contem_palavra(t, p) for p in
                ('cómo', 'como', 'por qué', 'porque', 'explicamos', 'consejo',
                 'consejos', 'clave', 'claves', 'comment', 'pourquoi',
                 'perché', 'perche', 'spieghiamo', 'te cuento', 'os explico')):
            tipos.add('TECHNICAL_EXPLANATION')

        marcas = _achar(t, MARCAS)
        # PALAVRA INTEIRA também aqui. O atalho `r in t.lower()` reintroduzia a
        # busca por pedaço de string pela porta dos fundos: `publi` casaria com
        # *publicación* e transformaria qualquer post que dissesse "publicação"
        # em conteúdo patrocinado.
        pago = any(cc.contem_palavra(t, r) for r in ROTULOS_PAGOS)
        if marcas:
            tipos.add('BRAND_MENTION')
        if pago:
            tipos.add('SPONSORED_CONTENT')
        if not tipos:
            tipos.add('OTHER' if t.strip() else 'NOT_KNOWN')

        m['CONTENT_TYPES'] = sorted(tipos & set(cc.TIPOS_DE_CONTEUDO))
        # Quanto texto REAL a legenda tem, tirando hashtag, arroba e emoji. Uma
        # legenda que é só `#viña #vino` não foi lida menos: ela não tem o que
        # ler. Sem este campo, "43 materiais OTHER" parece falha do léxico
        # quando é a legenda que está vazia — e as duas coisas pedem decisões
        # opostas.
        m['TEXT_SUBSTANCE'] = _substancia(t)
        # §6 · cultura VISTA no corpus. NUNCA escreve CROPS_PROVED.
        m['CROP'] = culturas or []
        m['ISSUE'] = assuntos or []
        m['DISEASE'] = ['OBSERVED'] if 'DISEASE' in assuntos else []
        m['PEST'] = ['OBSERVED'] if 'PEST' in assuntos else []
        m['WEED'] = ['OBSERVED'] if 'WEED' in assuntos else []
        m['BRANDS_OBSERVED'] = marcas
        # §8 · a escada. Rótulo da plataforma sobe; elogio no texto não.
        degrau = cc.NOT_KNOWN
        if marcas:
            degrau, _ = cc.promover_marca(None, 'BRAND_MENTION', m['URL'])
            if pago:
                degrau, _ = cc.promover_marca(degrau, 'SPONSORED_CONTENT_PROVED',
                                              'rótulo de patrocínio no próprio material')
        m['BRAND_EVIDENCE_LEVEL'] = degrau
        # §6 · país do fato. LANGUAGE != COUNTRY: só sai de NOT_KNOWN se o texto
        # nomear o lugar. A região herdada do Creator Map fica onde está.
        e = universo.get(m['ENTITY_ID'], {})
        m['COUNTRY_OF_FACT'] = _pais_no_texto(t) or cc.NOT_KNOWN
        m['REGION_OF_FACT'] = cc.NOT_KNOWN
        m['COUNTRY_OF_ENTITY'] = e.get('COUNTRY', cc.NOT_KNOWN)

        if marcas:
            for marca in marcas:
                eventos_de_marca.append({
                    'ENTITY_ID': m['ENTITY_ID'], 'CONTENT_ID': m['CONTENT_ID'],
                    'BRAND': marca, 'URL': m['URL'],
                    'OBSERVED_AT': m.get('PUBLISHED_AT'),
                    'EVIDENCE_LEVEL': degrau,
                    'IS_COMPETITOR': marca in cc.CONCORRENTES,
                    'LAW': 'menção != parceria paga; o degrau só sobe com '
                           'evidência do próprio degrau',
                })

    cc.gravar('CORPUS-OBSERVATIONS.json', {
        'WHAT_THIS_IS': 'observações derivadas do TEXTO do material.',
        'LAWS': ['QUERY_CROP != PROVED_CROP — CROP aqui é o que o corpus mostrou',
                 'LANGUAGE != COUNTRY — COUNTRY_OF_FACT exige o lugar nomeado',
                 'RECURRENCE != AUTHORITY',
                 'imagem sozinha NÃO prova cultura: só o texto foi lido'],
        'MATERIALS_CLASSIFIED': len(materiais),
        'BY_CONTENT_TYPE': dict(Counter(t for m in materiais for t in m['CONTENT_TYPES'])),
        'BY_CROP_OBSERVED': dict(Counter(c for m in materiais for c in m['CROP'])),
        'BY_ISSUE_OBSERVED': dict(Counter(i for m in materiais for i in m['ISSUE'])),
        'BRAND_EVENTS_TOTAL': len(eventos_de_marca),
        'BRAND_EVENTS': eventos_de_marca,
        'MATERIALS': materiais})
    print('CLASSIFICADOS=%d' % len(materiais))
    print('TIPOS:', dict(Counter(t for m in materiais for t in m['CONTENT_TYPES'])))
    print('CULTURAS:', dict(Counter(c for m in materiais for c in m['CROP'])))
    print('ASSUNTOS:', dict(Counter(i for m in materiais for i in m['ISSUE'])))
    print('EVENTOS_DE_MARCA=%d' % len(eventos_de_marca))


def _substancia(t):
    import re
    limpo = re.sub(r'[#@]\w+', ' ', t or '')
    limpo = re.sub(r'[^\w\s]', ' ', limpo, flags=re.UNICODE)
    palavras = [p for p in limpo.split() if len(p) > 2]
    if len(palavras) >= 15:
        return 'TEXT_RICH'
    if len(palavras) >= 4:
        return 'TEXT_SHORT'
    return 'HASHTAGS_OR_EMPTY'


PAISES = {
    'ES': ('españa', 'espana', 'spain', 'andalucía', 'andalucia', 'almería',
           'almeria', 'jaén', 'jaen', 'níjar', 'nijar', 'murcia', 'granada'),
    'FR': ('france', 'français', 'francais', 'loiret', 'touraine', 'beauce',
           'indre-et-loire'),
    'IT': ('italia', 'italy', 'veneto', 'padova', 'limena', 'lombardia'),
}


def _pais_no_texto(t):
    achados = _achar(t, PAISES)
    # Dois países nomeados no mesmo material não é "os dois": é ambíguo, e
    # escolher um seria inventar.
    return achados[0] if len(achados) == 1 else None


# ═════════════════════════════════════════════ §7, §13, §14 · fichas
def fichas():
    materiais = cc.carregar('CORPUS-OBSERVATIONS.json')
    if not materiais:
        print('SEM_OBSERVAÇÃO — rode antes: classificar'); raise SystemExit(1)
    universo = cc.carregar('CORPUS-UNIVERSE.json')
    comentarios = cc.carregar('CORPUS-COMMENTS.json')

    por_entidade = {}
    for m in materiais:
        por_entidade.setdefault(m['ENTITY_ID'], []).append(m)
    coment_por_entidade = {}
    for c in comentarios:
        coment_por_entidade.setdefault(c['ENTITY_ID'], []).append(c)

    fora = []
    for e in universo:
        itens = por_entidade.get(e['ENTITY_ID'], [])
        cms = coment_por_entidade.get(e['ENTITY_ID'], [])
        fora.append(_ficha(e, itens, cms))
    cc.gravar('CREATOR-CORPUS-FICHES.json', {
        'WHAT_THIS_IS': 'perfil de relevância por evidência. NÃO é recomendação '
                        'de contratação e NÃO é ranking.',
        'PROHIBITED_METRIC': cc.SCORE_PROIBIDO,
        'AXES': cc.EIXOS_DE_RELEVANCIA,
        'NO_RANKING': 'seguidores, views e likes ficam preservados como métrica '
                      'pública. FOLLOWERS DESC não é ordem de valor.',
        'FICHES_TOTAL': len(fora),
        'PROFILES': fora})
    for f in fora:
        print('%-6s %-24s N=%-4s campo=%-3s técnico=%-3s CP=%-3s marcas=%s' % (
            f['ENTITY_ID'], (f['HANDLE'] or '')[:24], f['N_CONTENT_ITEMS_REVIEWED'],
            f['RELEVANCE_PROFILE']['C_FARM_PROXIMITY']['FIELD_MATERIALS'],
            f['RELEVANCE_PROFILE']['D_TECHNICAL_DEPTH']['TECHNICAL_MATERIALS'],
            f['RELEVANCE_PROFILE']['E_CROP_PROTECTION_RELEVANCE']['MATERIALS'],
            ','.join(f['BRANDS_OBSERVED']) or '—'))


def _ficha(e, itens, cms):
    n = len(itens)
    tipos = Counter(t for m in itens for t in m['CONTENT_TYPES'])
    culturas = Counter(c for m in itens for c in m['CROP'])
    assuntos = Counter(i for m in itens for i in m['ISSUE'])
    marcas = sorted({b for m in itens for b in m['BRANDS_OBSERVED']})
    janelas = Counter(m['RECENCY_WINDOW'] for m in itens)

    de_campo = [m for m in itens if set(m['CONTENT_TYPES']) & set(cc.TIPOS_DE_CAMPO)]
    tecnicos = [m for m in itens if set(m['CONTENT_TYPES']) & set(cc.TIPOS_TECNICOS)]
    protecao = [m for m in itens if set(m['CONTENT_TYPES']) & set(cc.TIPOS_CROP_PROTECTION)]

    eventos_concorrente = [
        {'BRAND': b, 'CONTENT_ID': m['CONTENT_ID'], 'URL': m['URL'],
         'OBSERVED_AT': m.get('PUBLISHED_AT'), 'EVIDENCE_LEVEL': m['BRAND_EVIDENCE_LEVEL']}
        for m in itens for b in m['BRANDS_OBSERVED'] if b in cc.CONCORRENTES]
    patrocinio = [{'CONTENT_ID': m['CONTENT_ID'], 'URL': m['URL'],
                   'EVIDENCE_LEVEL': m['BRAND_EVIDENCE_LEVEL']}
                  for m in itens if 'SPONSORED_CONTENT' in m['CONTENT_TYPES']]

    classes = Counter(c['CLASS'] for c in cms)
    perguntas_tecnicas = [c for c in cms if c['CLASS'] == 'TECHNICAL_QUESTION']

    # §7-F · audiência. Só é dito o que o CONTEÚDO sugere; profissão de seguidor
    # não se infere. Sem material técnico e sem pergunta técnica, fica NOT_KNOWN.
    if perguntas_tecnicas and protecao:
        audiencia = 'MIXED'
    elif protecao or tecnicos:
        audiencia = 'GENERAL_AG'
    elif tipos.get('CONSUMER_FACING'):
        audiencia = 'CONSUMERS'
    else:
        audiencia = 'NOT_KNOWN'

    estilos = sorted({
        'FIELD_CONTENT' if de_campo else None,
        'TECHNICAL_EXPLANATION' if tipos.get('TECHNICAL_EXPLANATION') else None,
        'EVENT' if tipos.get('EVENT') else None,
        'PRODUCT_DEMO' if tipos.get('PRODUCT_MENTION') else None,
        'STORYTELLING' if tipos.get('FARM_LIFESTYLE') else None,
        'AWARENESS' if tipos.get('GENERAL_AG_AWARENESS') else None,
    } - {None}) or ['NOT_KNOWN']

    empresa = e['ENTITY_TYPE'] == 'FARM_BUSINESS'
    usos = _usos(empresa, de_campo, tecnicos, protecao, tipos)

    perfil = {
        'A_CROP_ALIGNMENT': {
            'CROPS_PROVED_BY_CREATOR_MAP': e['CROPS_PROVED'],
            'CROPS_OBSERVED_IN_CORPUS': dict(culturas),
            'OVERLAP': sorted(set(e['CROPS_PROVED']) & set(culturas)),
            'STATE': ('OVERLAP_OBSERVED' if set(e['CROPS_PROVED']) & set(culturas)
                      else 'NO_OVERLAP_IN_CORPUS' if n else 'NOT_MEASURED'),
            'LAW': 'QUERY_CROP != PROVED_CROP. O que o corpus mostra não reescreve '
                   'o que o Creator Map provou.'},
        'B_REGION_ALIGNMENT': {
            'REGION_FROM_CREATOR_MAP': e['REGION'],
            'COUNTRY_NAMED_IN_MATERIALS': dict(Counter(
                m['COUNTRY_OF_FACT'] for m in itens if m['COUNTRY_OF_FACT'] != cc.NOT_KNOWN)),
            'STATE': 'INHERITED_ONLY',
            'LAW': 'LANGUAGE != COUNTRY. Região do fato não foi extraída do texto '
                   'nesta rodada; a região da ficha é a do Creator Map.'},
        'C_FARM_PROXIMITY': {
            'FIELD_MATERIALS': len(de_campo),
            'N_OBSERVED': n,
            'STATE': ('FIELD_CONTENT_OBSERVED' if de_campo
                      else 'NO_FIELD_CONTENT_IN_CORPUS' if n else 'NOT_MEASURED'),
            'ACTUAL_FARMER': 'INHERITED_FROM_CREATOR_MAP'},
        'D_TECHNICAL_DEPTH': {
            'TECHNICAL_MATERIALS': len(tecnicos),
            'EXPLANATION_MATERIALS': tipos.get('TECHNICAL_EXPLANATION', 0),
            'RATE': cc.taxa('TECHNICAL_CONTENT_RATE', len(tecnicos), n),
            'STATE': ('TECHNICAL_CONTENT_OBSERVED' if tecnicos
                      else 'NO_TECHNICAL_CONTENT_IN_CORPUS' if n else 'NOT_MEASURED')},
        'E_CROP_PROTECTION_RELEVANCE': {
            'MATERIALS': len(protecao),
            'BY_ISSUE': dict(assuntos),
            'STATE': ('CROP_PROTECTION_CONTENT_OBSERVED' if protecao
                      else 'NOT_OBSERVED_IN_CORPUS' if n else 'NOT_MEASURED')},
        'F_AUDIENCE_FACING': {
            'VALUE': audiencia,
            'COMMENTS_SAMPLED': len(cms),
            'BY_COMMENT_CLASS': dict(classes),
            'LAW': 'profissão de seguidor não se infere. COMMENTER != FARMER.'},
        'G_ACTIVATION_STYLE': {'OBSERVED': estilos},
        'H_LOCAL_ADAMA_CONTEXT': {
            'VALUE': 'NOT_KNOWN',
            'WHY': 'o cruzamento só é lícito com portfólio ADAMA local PROVADO, e '
                   'esse artefato não está visível nesta branch. NOT_ASKED != '
                   'NOT_KNOWN por ausência de portfólio.',
            'DOES_NOT_MEAN': list(cc.CONTEXTO_ADAMA_NAO_SIGNIFICA)},
    }

    return {
        'ENTITY_ID': e['ENTITY_ID'], 'PERSON_ID': e['PERSON_ID'],
        'NAME': e['NAME'], 'HANDLE': e['HANDLE'],
        'ENTITY_TYPE': e['ENTITY_TYPE'],
        'COUNTRY': e['COUNTRY'], 'REGION': e['REGION'],
        'CROPS_PROVED': e['CROPS_PROVED'],
        'PUBLIC_CHANNEL': e['PUBLIC_CHANNEL'], 'PUBLIC_CONTACT': e['PUBLIC_CONTACT'],
        'CHANNEL_STATE': e['CHANNEL_STATE'],
        'N_CONTENT_ITEMS_REVIEWED': n,
        'RECENT_ACTIVITY_BY_WINDOW': dict(janelas),
        'CONTENT_TYPES_OBSERVED': dict(tipos),
        'TEXT_SUBSTANCE': dict(Counter(m.get('TEXT_SUBSTANCE') for m in itens)),
        'CROPS_OBSERVED': dict(culturas),
        'ISSUES_OBSERVED': dict(assuntos),
        'FIELD_CONTENT_EXAMPLES': [m['URL'] for m in de_campo[:5]],
        'TECHNICAL_CONTENT_EXAMPLES': [m['URL'] for m in tecnicos[:5]],
        'CROP_PROTECTION_EXAMPLES': [m['URL'] for m in protecao[:5]],
        'AUDIENCE_EVIDENCE': {
            'COMMENTS_SAMPLED': len(cms),
            'TECHNICAL_QUESTIONS': [c['TEXT'][:180] for c in perguntas_tecnicas[:5]],
            'BY_CLASS': dict(classes)},
        'BRANDS_OBSERVED': marcas,
        'COMPETITOR_RELATIONSHIP_EVIDENCE': eventos_concorrente,
        'COMPETITOR_HISTORY': (cc.historico_de_concorrente(eventos_concorrente)
                               if n else 'NOT_KNOWN'),
        'COMPETITOR_HISTORY_LAW': 'NOT_OBSERVED_IN_CORPUS != NO_RELATIONSHIP. '
                                  'O corpus é amostra do que é público.',
        'SPONSORED_CONTENT_EVIDENCE': patrocinio,
        'LOCAL_ADAMA_CONTEXT': 'NOT_KNOWN',
        'RELEVANCE_PROFILE': perfil,
        ('POSSIBLE_PARTNERSHIP_USE_CASES' if empresa
         else 'POSSIBLE_MARKETING_USE_CASES'): usos,
        'USE_CASES_ARE': 'hipóteses de AVALIAÇÃO. Não são recomendação de contratação.',
        'RECURRENCE_LAW': 'RECURRENCE != AUTHORITY != QUALITY != MARKET IMPORTANCE.',
        'WHAT_IS_NOT_KNOWN': _nao_sei(e, n, cms, protecao, itens),
        'TOP_EVIDENCE': [m['URL'] for m in (protecao or tecnicos or de_campo or itens)[:5]],
        'AS_OF_DATE': e['AS_OF_DATE'],
    }


def _usos(empresa, de_campo, tecnicos, protecao, tipos):
    """§13/§14 · hipóteses de avaliação, e só as que o corpus sustenta.

    A pergunta muda quando a entidade é empresa: não é "que conteúdo ela faz",
    é "o que essa fazenda/negócio PERMITE". Empresa não é creator, e chamar a
    empresa de creator é onde a distinção se perde primeiro.
    """
    if empresa:
        usos = []
        if de_campo:
            usos += ['FIELD_VISIT', 'CONTENT_PRODUCTION']
        if protecao or tecnicos:
            usos += ['TECHNICAL_DEMO', 'FIELD_TRIAL_CONTEXT']
        if tipos.get('FARM_BUSINESS'):
            usos += ['CASE_STUDY', 'FARMER_ACCESS']
        if tipos.get('EVENT'):
            usos.append('EVENT')
        return sorted(set(usos) & set(cc.USOS_FARM_BUSINESS)) or ['OTHER']
    usos = []
    if de_campo:
        usos.append('FIELD_CONTENT')
    if tipos.get('TECHNICAL_EXPLANATION') or tecnicos:
        usos.append('TECHNICAL_EDUCATION')
    if tipos.get('EVENT'):
        usos.append('EVENT')
    if tipos.get('FARM_LIFESTYLE'):
        usos.append('STORYTELLING')
    if tipos.get('PRODUCT_MENTION'):
        usos.append('PRODUCT_DEMO')
    if not usos:
        usos.append('GENERAL_AWARENESS' if tipos else 'OTHER')
    return sorted(set(usos) & set(cc.USOS_PESSOA)) or ['OTHER']


def _nao_sei(e, n, cms, protecao, itens):
    faltas = []
    if e['COLLECTABLE'] == 'NO':
        faltas.append('nenhum material: %s' % e['WHY_NOT_COLLECTABLE'])
    if n and n < 30:
        faltas.append('corpus abaixo do alvo de profundidade (N=%d de 30) — '
                      'é o que o canal publicou, não um defeito de coleta' % n)
    if not cms:
        faltas.append('nenhum comentário amostrado: audiência permanece NOT_KNOWN')
    if not protecao:
        faltas.append('nenhum material de proteção de cultivos no corpus lido — '
                      'NOT_OBSERVED_IN_CORPUS, nunca "não fala disso"')
    vazios = sum(1 for m in itens if m.get('TEXT_SUBSTANCE') == 'HASHTAGS_OR_EMPTY')
    if n and vazios >= n / 2:
        faltas.append('%d de %d legendas são só hashtag/emoji: a classificação por '
                      'TEXTO tem pouco o que ler neste canal, e o silêncio é da '
                      'legenda, não da pessoa' % (vazios, n))
    faltas.append('região do fato não extraída do texto: só a região herdada do '
                  'Creator Map está na ficha')
    faltas.append('imagem e vídeo não foram lidos: só TEXTO. Material sem legenda '
                  'não foi classificado por conteúdo visual')
    faltas.append('LOCAL_ADAMA_CONTEXT não cruzado: portfólio ADAMA local não '
                  'visível nesta branch')
    return faltas


# ═════════════════════════════════════════════ §20 · entrega
def entrega():
    fichas_ = cc.carregar('CREATOR-CORPUS-FICHES.json')
    materiais = cc.carregar('CORPUS-OBSERVATIONS.json')
    comentarios = cc.carregar('CORPUS-COMMENTS.json')
    universo = cc.carregar('CORPUS-UNIVERSE.json')
    if not fichas_:
        print('SEM_FICHA — rode antes: fichas'); raise SystemExit(1)

    runs = cc.carregar('RUN-MANIFEST-CORPUS.json')
    runs = list(runs.values()) if isinstance(runs, dict) else runs
    runs = [r for r in runs if isinstance(r, dict) and r.get('RUN_ID')]
    custo = sum(r['COST_USD'] for r in runs if isinstance(r.get('COST_USD'), (int, float)))

    pessoas = [f for f in fichas_ if f['ENTITY_TYPE'] == 'PERSON_CREATOR']
    empresas = [f for f in fichas_ if f['ENTITY_TYPE'] == 'FARM_BUSINESS']

    cc.gravar('CORPUS-DELIVERY.json', {
        'A_PERSON_CREATORS_ATTEMPTED': len(pessoas),
        'B_FARM_BUSINESSES_ATTEMPTED': len(empresas),
        'C_MATERIALS_COLLECTED': len(materiais),
        'D_MATERIALS_BY_PLATFORM': dict(Counter(m['PLATFORM'] for m in materiais)),
        'E_COVERAGE_BY_WINDOW': dict(Counter(m['RECENCY_WINDOW'] for m in materiais)),
        'F_CROP_COVERAGE': dict(Counter(c for m in materiais for c in m['CROP'])),
        'G_ISSUE_COVERAGE': dict(Counter(i for m in materiais for i in m['ISSUE'])),
        'H_FIELD_CONTENT_EXAMPLES': sum(len(f['FIELD_CONTENT_EXAMPLES']) for f in fichas_),
        'I_TECHNICAL_CONTENT_EXAMPLES': sum(len(f['TECHNICAL_CONTENT_EXAMPLES']) for f in fichas_),
        'J_CROP_PROTECTION_RELEVANCE': {
            f['ENTITY_ID']: f['RELEVANCE_PROFILE']['E_CROP_PROTECTION_RELEVANCE']['STATE']
            for f in fichas_},
        'K_AUDIENCE_EVIDENCE': {f['ENTITY_ID']: f['RELEVANCE_PROFILE']['F_AUDIENCE_FACING']['VALUE']
                                for f in fichas_},
        'L_COMMENTS_SAMPLED': len(comentarios),
        'M_TECHNICAL_QUESTIONS_OBSERVED': sum(
            1 for c in comentarios if c['CLASS'] == 'TECHNICAL_QUESTION'),
        'N_BRANDS_OBSERVED': dict(Counter(b for m in materiais for b in m['BRANDS_OBSERVED'])),
        'O_COMPETITOR_RELATIONSHIPS_OBSERVED': sum(
            len(f['COMPETITOR_RELATIONSHIP_EVIDENCE']) for f in fichas_),
        'P_SPONSORED_EVIDENCE': sum(len(f['SPONSORED_CONTENT_EVIDENCE']) for f in fichas_),
        'Q_LOCAL_ADAMA_CONTEXT_OVERLAP': {
            'STATE': 'NOT_KNOWN',
            'WHY': 'portfólio ADAMA local provado não está visível nesta branch'},
        'R_POSSIBLE_USE_CASES': {
            f['ENTITY_ID']: f.get('POSSIBLE_MARKETING_USE_CASES')
            or f.get('POSSIBLE_PARTNERSHIP_USE_CASES') for f in fichas_},
        'S_ENRICHED_PROFILES': len(fichas_),
        'T_CASE_CONVERGENCE_READINESS': _convergencia(fichas_),
        'U_META_CROSSOVER_READINESS': {
            'JOIN_KEYS': ['PERSON_ID', 'ENTITY_ID', 'HANDLE', 'BRAND', 'COUNTRY',
                          'CROP', 'OBSERVED_AT'],
            'IF_META_FINDS_THEM': 'CREATOR_APPEARANCE_OBSERVED',
            'PAID_CREATOR_RELATION': 'só sobe a PROVED com prova adicional — '
                                     'não é antecipado aqui'},
        'V_RUNS_ITEMS_COST': {
            'APIFY_RUNS': len(runs),
            'ITEMS_RAW': sum(r.get('ITEM_COUNT_RAW') or 0 for r in runs),
            'COST_USD': round(custo, 6),
            'RAW_PRESERVED': sum(1 for r in runs if r.get('RAW_EVIDENCE_STATE') == 'PRESERVED'),
            'BY_STATUS': dict(Counter(r.get('STATUS') for r in runs))},
        'W_STILL_NOT_KNOWN': sorted({x for f in fichas_ for x in f['WHAT_IS_NOT_KNOWN']}),
        'X_HANDOFF_FOR_INTELLIGENCE': {
            'DATASET_OWNER': cc.DATASET_OWNER,
            'OWNS': ['CONTENT MATERIALS', 'CONTENT OBSERVATIONS', 'AUDIENCE SAMPLE',
                     'BRAND RELATIONSHIP EVIDENCE'],
            'DOES_NOT_OWN': ['IDENTITY', 'ROLE', 'ACTIVATION_STATE'],
            'CREATOR_MAP_STATE': 'FROZEN — não tocado por esta missão',
            'SUPABASE': 'nenhuma migração aplicada; modelo apenas PROPOSTO',
            'OPTIONAL_REFRESH_INPUT': ('READY' if materiais else 'NOT_READY'),
            'BLOCKS_NOTHING': 'EARLY SIGNAL, META COMPETITOR e COMPETITOR FORESIGHT '
                              'seguem sem depender desta missão'},
        'CHANNELS_NOT_COLLECTED': [
            {'ENTITY_ID': e['ENTITY_ID'], 'HANDLE': e['HANDLE'],
             'WHY': e['WHY_NOT_COLLECTABLE']}
            for e in universo if e['COLLECTABLE'] == 'NO'],
        'PROHIBITED_METRIC': cc.SCORE_PROIBIDO,
    })
    print('A pessoas=%d · B empresas=%d · C materiais=%d · L comentários=%d'
          % (len(pessoas), len(empresas), len(materiais), len(comentarios)))
    print('V runs=%d itens=%d custo=%.4f USD' % (
        len(runs), sum(r.get('ITEM_COUNT_RAW') or 0 for r in runs), custo))


def _convergencia(fichas_):
    """§16 · o índice que deixa um caso perguntar 'há voz pública neste contexto?'"""
    idx = {}
    for f in fichas_:
        for crop in set(f['CROPS_PROVED']) | set(f['CROPS_OBSERVED']):
            chave = '%s|%s' % (f['COUNTRY'], crop)
            idx.setdefault(chave, []).append({
                'ENTITY_ID': f['ENTITY_ID'], 'WHO': f['NAME'], 'HANDLE': f['HANDLE'],
                'WHY_RELEVANT': f['RELEVANCE_PROFILE']['A_CROP_ALIGNMENT']['STATE'],
                'WHAT_THEY_TALK_ABOUT': sorted(f['ISSUES_OBSERVED']) or ['NOT_OBSERVED_IN_CORPUS'],
                'RECENT_MATERIAL': f['TOP_EVIDENCE'][:2],
                'COMPETITOR_HISTORY': f['COMPETITOR_HISTORY'],
                'CONTACT': f['PUBLIC_CONTACT'],
            })
    return {'SLICES': len(idx), 'INDEX': idx,
            'NOT_ASKED_IS_NOT_NOT_READY': 'a ausência de um recorte aqui significa '
                                          'que ninguém perguntou, não que não há voz'}


FASES = {'classificar': classificar, 'fichas': fichas, 'entrega': entrega}

if __name__ == '__main__':
    fase = sys.argv[1] if len(sys.argv) > 1 else 'classificar'
    if fase not in FASES:
        print('fase desconhecida: %s · disponíveis: %s' % (fase, ', '.join(FASES)))
        raise SystemExit(1)
    FASES[fase]()
