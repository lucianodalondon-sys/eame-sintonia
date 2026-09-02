#!/usr/bin/env python3
"""
CORPUS DO PESQUISADOR — o que as 12 identidades PROVADAS publicam, explicam e apresentam.

    python3 scripts/corpus_pesquisador.py coletar   # busca e guarda o cru (rota gratuita)
    python3 scripts/corpus_pesquisador.py medir     # classifica, dedupe, mede, publica
    python3 scripts/corpus_pesquisador.py resumo    # relê o publicado e imprime o quadro

O QUE ESTA MISSÃO É, E O QUE ELA NÃO REABRE
---------------------------------------------
O `SPEAKER-UNIVERSE-PILOT-V1` parou no PRIMEIRO estado: identidade provada. O sensor de
voz técnica pessoal foi medido no `SENSOR-PILOT` e saiu `NOT_PROVED` — 431 vídeos, 23
itens tecnicamente relevantes, 6 vozes de campo. Este arquivo **não tenta desfazer esse
veredito**. Ele responde outra pergunta, que é complementar:

    não "esta pessoa fala todo dia?" — e sim
    "o que esta pessoa SABE, e onde isso está escrito de forma verificável?"

O produto é PROFUNDIDADE sobre quem já está provado, não LARGURA sobre gente nova.
Nenhuma pessoa entra aqui: o universo é fechado nos 12 provados.

DUAS ROTAS, E POR QUE NENHUMA DELAS É APIFY
---------------------------------------------
A lei da casa é SOURCE-FIRST, TOOL-SECOND. Para paper, DOI e ORCID a rota apropriada é o
próprio registro — e ela é gratuita:

    OpenAlex   obra indexada, com data, tipo, veículo e DOI. Traz a AUTORIA declarada
               obra a obra, com o ORCID de cada autor quando existe.
    ORCID      o que a própria pessoa declarou: página oficial, laboratório, projeto,
               e (quando ela preencheu) a lista de obras dela.

Apify continua autorizada para YouTube e LinkedIn, mas **não neste lote**. O motivo é
medido, não estético: no `SENSOR-PILOT` a rota de vídeo devolveu 220 NOISE em 431 itens.
Gastar o primeiro lote nela é comprar ruído antes de ter o esqueleto científico.

    APIFY_RUNS = 0 · COST_USD = 0 · RUNNER = nenhum.

NAME_MATCH ALONE != PERSON_PROOF — e aqui isso é executado obra a obra
-----------------------------------------------------------------------
O id de autor do OpenAlex já conflagrou homônimos nesta casa (o `Nikolaos Papadopoulos`
com 58 organizações). Então não basta pedir "as obras do autor A5046191184" e acreditar.

    A PRIMEIRA VERSÃO DESTE ARQUIVO ERRAVA AQUI, E O ERRO FOI MEDIDO.
    Ela tratava "o ORCID aparece na autoria" como prova, e aprovou 763 de 763 obras —
    prova que aprova tudo não é prova. O motivo: o OpenAlex HERDA o ORCID do perfil do
    autor e o carimba em toda obra atribuída àquele id. A obra *"Pages de fin"*, uma
    página final de revista de ciências humanas no Cairn.info, saía com o ORCID de
    Frédéric Suffert carimbado nela.

O que é evidência DA OBRA, e não herança do perfil, são dois campos:

    ORCID_SELF_DECLARED   o DOI está na lista de obras do registro ORCID da pessoa.
                          Ela mesma declarou. É a prova mais forte disponível de graça.
    AFFILIATION_ON_WORK   a autoria daquela obra declara uma instituição, e ela bate com
                          a instituição provada (pelo nome) ou pelo menos com o país
                          dela. Afiliação é escrita obra a obra — não é herdada.
    NAME_MATCH_ONLY       nem uma coisa nem outra. Só o id do OpenAlex sustenta.

`NAME_MATCH_ONLY` **entra no acervo mas sai rebaixado**, e nunca conta nas métricas de
evidência. Separado disso, cada obra recebe `DOMAIN_STATE`: uma obra sem tópico ou fora
das ciências agrárias/biológicas é marcada `OFF_DOMAIN` e também fica fora da evidência.
`Pages de fin` cai pelos dois lados: sem instituição declarada e sem tópico.

PAÍS DA PESSOA != PAÍS DO FATO
--------------------------------
Lei obrigatória, e a mais fácil de quebrar sem perceber. A afiliação do autor é
geografia da INSTITUIÇÃO. O idioma é geografia de NADA. `COUNTRY_OF_FACT` só é
preenchido quando o título ou o resumo do material NOMEIA o lugar — e o trecho que
sustentou fica gravado em `COUNTRY_OF_FACT_EVIDENCE`. Sem trecho, sai `NÃO SEI`.

CONSULTA != PROVA
-------------------
A pessoa herdou CROP e ISSUE do recorte que a trouxe. Isso é `QUERY_CROP` / `QUERY_ISSUE`
e fica no registro da PESSOA. No MATERIAL, `PROVED_CROP` e `PROVED_ISSUE` só existem se
o texto do próprio material sustentar. Um fitopatologista de septoriose publica sobre
ferrugem também — e essa obra não vira septoriose por causa de quem assina.

O QUE ESTE ARQUIVO NÃO FAZ
----------------------------
Não cria EARLY_SIGNAL. Não pontua autoridade. Não ordena por seguidores. Não transcreve
vídeo. Não amplia o universo de pessoas. Não escreve em nenhum owner que não seja
`RESEARCHER_CORPUS_EAME`.
"""
import json
import os
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLES = os.path.join(ROOT, 'data', 'samples')
RAWDIR = os.path.join(ROOT, 'data', 'raw', 'RESEARCHER-CORPUS')
FONTE = os.path.join(SAMPLES, 'SPEAKER-UNIVERSE-PILOT-V1.json')
DEST = os.path.join(SAMPLES, 'RESEARCHER-CORPUS-EAME-V1.json')
DIRETORIO = os.path.join(SAMPLES, 'EXPERT-DIRECTORY-EAME-V1.json')

OPENALEX = 'https://api.openalex.org/works'
ORCID_API = 'https://pub.orcid.org/v3.0/%s/%s'
MAILTO = 'sintonia-eame@example.invalid'
PAUSA = 1.2

DATASET_OWNER = 'RESEARCHER_CORPUS_EAME'
NAO_SEI = 'NÃO SEI'

# A data de referência das janelas de recência. Fica DECLARADA e no artefato: "últimos
# 30 dias" sem dizer 30 dias contados de quando é uma frase, não uma medida.
REF_DATE = '2026-08-30'

# Janela de coleta. Não é a carreira inteira: o árbitro pediu um lote pequeno e de alta
# qualidade primeiro, e só depois decidir onde aprofundar.
DESDE = '2019-01-01'
POR_PAGINA = 200

# ------------------------------------------------------------------ léxicos sustentados
# Cada termo abaixo é o que precisa APARECER NO TEXTO do material para que o campo seja
# preenchido. Nenhum deles é inferido da pessoa, da instituição ou do idioma.
CROP_LEX = {
    'OLIVE': ('olive', 'olives', 'olea europaea', 'olivar', 'olivo', 'olivicoltura'),
    # nada de raiz solta aqui: "vid" e "mais" são palavras comuns em espanhol e francês
    # e entrariam por ruído. Só termo que só significa uma coisa.
    'VINE': ('grapevine', 'grapevines', 'vitis vinifera', 'vineyard', 'vineyards',
             'viticulture', 'viticoltura', 'vignoble', 'grape', 'grapes', 'vigne'),
    'DURUM_WHEAT': ('durum', 'triticum durum', 'triticum turgidum', 'trigo duro',
                    'grano duro', 'blé dur'),
    'CEREAL': ('wheat', 'triticum aestivum', 'barley', 'hordeum', 'cereal', 'cereals',
               'trigo', 'frumento', 'oat', 'oats', 'rye', 'triticale'),
    'MAIZE': ('maize', 'corn', 'zea mays', 'maíz'),
}
ISSUE_LEX = {
    'REPILO': ('venturia oleaginea', 'spilocaea oleagina', 'peacock spot', 'repilo',
               'fusicladium oleagineum'),
    'SEPTORIA': ('zymoseptoria', 'septoria tritici', 'mycosphaerella graminicola',
                 'septoria leaf blotch', 'septoriose'),
    'FLAVESCENCE': ('flavescence', 'phytoplasma', 'scaphoideus titanus', 'grapevine yellows',
                    'bois noir'),
    'FUSARIUM': ('fusarium', 'head blight', 'deoxynivalenol', 'mycotoxin', 'micotossin',
                 'zearalenone', 'fumonisin'),
    'DOWNY_MILDEW': ('plasmopara viticola', 'downy mildew', 'mildiou', 'peronospora'),
    'POWDERY_MILDEW': ('erysiphe necator', 'powdery mildew', 'oidium', 'oïdium'),
    'RUST': ('puccinia', 'leaf rust', 'yellow rust', 'stripe rust', 'roya'),
    'XYLELLA': ('xylella fastidiosa',),
    'VERTICILLIUM': ('verticillium',),
    'OLIVE_PESTS': ('bactrocera oleae', 'olive fruit fly', 'prays oleae'),
    'HERBICIDE_RESISTANCE': ('herbicide resistance', 'herbicide-resistant'),
}
# País do FATO. Região entra junto para dar lastro, mas quem manda é o país.
PAIS_LEX = {
    'ES': ('spain', 'spanish', 'españa', 'espagne', 'andalusia', 'andalucía', 'andalucia',
           'catalonia', 'cataluña', 'aragon', 'aragón', 'extremadura', 'castilla',
           'valencia', 'murcia', 'jaén', 'jaen', 'córdoba', 'cordoba', 'sevilla'),
    'IT': ('italy', 'italian', 'italia', 'italie', 'apulia', 'puglia', 'piedmont',
           'piemonte', 'veneto', 'sicily', 'sicilia', 'sardinia', 'sardegna', 'tuscany',
           'toscana', 'emilia-romagna', 'lombardy', 'lombardia', 'marche', 'abruzzo'),
    'FR': ('france', 'french', 'français', 'francia', 'bordeaux', 'champagne', 'burgundy',
           'bourgogne', 'alsace', 'occitanie', 'beaujolais', 'languedoc', 'aquitaine',
           'brittany', 'bretagne', 'normandy', 'normandie'),
    'PT': ('portugal', 'portuguese', 'alentejo', 'trás-os-montes'),
    'GR': ('greece', 'greek', 'grecia', 'crete', 'cretan', 'peloponnese'),
    'DE': ('germany', 'german', 'deutschland', 'bavaria'),
    'CH': ('switzerland', 'swiss', 'suisse'),
    'GB': ('united kingdom', 'england', 'british', 'ireland'),
    'TN': ('tunisia', 'tunisian'),
    'MA': ('morocco', 'moroccan', 'maroc'),
    'TR': ('türkiye', 'turkey', 'turkish'),
    'AR': ('argentina',), 'BR': ('brazil', 'brasil'), 'US': ('united states', 'california'),
    'AU': ('australia', 'australian'), 'CN': ('china', 'chinese'),
}

# Papel do material (§9). A ordem importa: o primeiro que casar manda, e o motivo do
# casamento fica gravado. Isto é classificador LEXICAL — o limite está declarado.
PAPEL_LEX = [
    ('REVIEW_SYNTHESIS', ('review', 'meta-analysis', 'meta analysis', 'synthesis',
                          'state of the art', 'perspective', 'overview')),
    ('DISEASE_PEST_MONITORING', ('first report', 'outbreak', 'survey', 'monitoring',
                                 'surveillance', 'occurrence', 'incidence', 'epidemic',
                                 'spread of')),
    ('METHOD_MECHANISM', ('mechanism', 'mechanisms', 'effector', 'effectors', 'gene',
                          'genes', 'genome', 'transcriptome', 'qtl', 'method', 'assay',
                          'detection', 'model', 'pathway')),
    ('MANAGEMENT_GUIDANCE', ('management', 'control of', 'fungicide', 'efficacy',
                             'application timing', 'integrated pest', 'cultivar choice',
                             'biocontrol', 'resistance management')),
    ('EXPERIMENT_RESULT', ('field trial', 'field experiment', 'trial', 'inoculation',
                           'experiment')),
]

RECORTES = {
    'ES-OLIVE-REPILO': ('ES', 'OLIVE', 'REPILO'),
    'ES-CEREAL-SEPTORIA': ('ES', 'CEREAL', 'SEPTORIA'),
    'IT-VINE-FLAVESCENCE': ('IT', 'VINE', 'FLAVESCENCE'),
    'IT-DURUM_WHEAT-FUSARIUM': ('IT', 'DURUM_WHEAT', 'FUSARIUM'),
    'FR-VINE-DOWNY_MILDEW': ('FR', 'VINE', 'DOWNY_MILDEW'),
    'FR-CEREAL-SEPTORIA': ('FR', 'CEREAL', 'SEPTORIA'),
}

ESTADOS_PROVADOS = ('IDENTITY_PROVED', 'IDENTITY_PROVED_COUNTRY_SINGLE_SOURCE')

# Campo do tópico do OpenAlex que mantém a obra dentro do assunto desta casa. Fora daqui
# a obra fica no acervo, mas marcada, e não conta como evidência.
DOMINIOS_ACEITOS = ('Agricultural and Biological Sciences', 'Environmental Science',
                    'Biochemistry, Genetics and Molecular Biology', 'Veterinary')

PROVAS_FORTES = ('ORCID_SELF_DECLARED', 'AFFILIATION_ON_WORK', 'AFFILIATION_COUNTRY_ON_WORK')


def evidencia(m):
    """A obra conta como evidência? Precisa ser DA PESSOA e DO ASSUNTO — as duas coisas."""
    return m['PERSON_PROOF'] in PROVAS_FORTES and m['DOMAIN_STATE'] == 'IN_DOMAIN'


# --------------------------------------------------------------------------- utilidades
def _texto(s):
    """Minúsculo, sem acento, sem travessão exótico — para BUSCAR termo, não para exibir."""
    s = unicodedata.normalize('NFKD', str(s or ''))
    s = ''.join(c for c in s if not unicodedata.combining(c))
    for t in ('‐', '‑', '‒', '–', '—', '−'):
        s = s.replace(t, '-')
    return re.sub(r'\s+', ' ', s.lower())


def _get(url, headers=None):
    """→ (json, None) ou (None, motivo). NUNCA levanta: FALHA DE FONTE != ZERO."""
    h = {'User-Agent': 'SintoniaEAME (mailto:%s)' % MAILTO, 'Accept': 'application/json'}
    h.update(headers or {})
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=90) as r:
            return json.loads(r.read().decode('utf-8')), None
    except urllib.error.HTTPError as e:
        return None, 'HTTP %d' % e.code
    except Exception as e:                                       # noqa: BLE001
        return None, type(e).__name__


def _resumo_do_indice(inv):
    """OpenAlex guarda o resumo como índice invertido. Aqui ele volta a ser frase."""
    if not inv:
        return ''
    pos = {}
    for palavra, ondes in inv.items():
        for o in ondes:
            pos[o] = palavra
    return ' '.join(pos[i] for i in sorted(pos))[:4000]


def pessoas_provadas():
    d = json.load(open(FONTE, encoding='utf-8'))
    return [p for p in d['PEOPLE'] if p.get('IDENTITY_STATE') in ESTADOS_PROVADOS]


# -------------------------------------------------------------------------- 1 · COLETAR
def coletar():
    os.makedirs(os.path.join(RAWDIR, 'openalex'), exist_ok=True)
    os.makedirs(os.path.join(RAWDIR, 'orcid'), exist_ok=True)
    pessoas = pessoas_provadas()
    print('pessoas provadas no universo congelado: %d' % len(pessoas))
    chamadas, falhas = 0, []

    for p in pessoas:
        orcid = p['ORCID']
        autor = p['PERSON_ID'].rsplit('/', 1)[-1]

        # (a) obras indexadas — a rota do paper é o registro do paper, não um scraper
        alvo = os.path.join(RAWDIR, 'openalex', '%s.json' % autor)
        if not os.path.exists(alvo):
            url = '%s?%s' % (OPENALEX, urllib.parse.urlencode({
                'filter': 'author.id:%s,from_publication_date:%s' % (autor, DESDE),
                'per-page': POR_PAGINA, 'sort': 'publication_date:desc', 'mailto': MAILTO}))
            d, err = _get(url)
            chamadas += 1
            time.sleep(PAUSA)
            if err:
                falhas.append(('openalex', p['NAME'], err))
            else:
                json.dump(d, open(alvo, 'w', encoding='utf-8'), ensure_ascii=False)
                print('  OpenAlex %-28s %d obras' % (p['NAME'][:28], len(d['results'])))

        # (b) o que a PESSOA declarou dela mesma: página oficial, lab, projeto, obras
        for parte in ('researcher-urls', 'works'):
            alvo = os.path.join(RAWDIR, 'orcid', '%s-%s.json' % (orcid, parte))
            if os.path.exists(alvo):
                continue
            d, err = _get(ORCID_API % (orcid, parte))
            chamadas += 1
            time.sleep(PAUSA)
            if err:
                falhas.append(('orcid/%s' % parte, p['NAME'], err))
            else:
                json.dump(d, open(alvo, 'w', encoding='utf-8'), ensure_ascii=False)

    print('chamadas: %d · falhas: %d' % (chamadas, len(falhas)))
    for f in falhas:
        print('  FALHA %s %s %s' % f)


# --------------------------------------------------------------- 2 · classificar 1 obra
def _janela(data):
    """LAST_30D … OLDER_ARCHIVE. Material velho bom continua bom — só não é NOVO."""
    if not data:
        return NAO_SEI
    from datetime import date
    y, m, d = (int(x) for x in REF_DATE.split('-'))
    try:
        yy, mm, dd = (int(x) for x in data.split('-')[:3])
    except ValueError:
        return NAO_SEI
    dias = (date(y, m, d) - date(yy, mm, dd)).days
    if dias < 0:
        return 'FUTURE_DATED'
    for limite, nome in ((30, 'LAST_30D'), (90, 'LAST_90D'), (180, 'LAST_180D'),
                         (365, 'LAST_365D')):
        if dias <= limite:
            return nome
    return 'OLDER_ARCHIVE'


_RX = {}


def _tem(termo, texto):
    """O termo aparece como PALAVRA INTEIRA?

    A primeira versão comparava por pedaço de string e produziu um erro medido: "crete"
    casava dentro de "secreted", e 21 dos 22 materiais marcados COUNTRY_OF_FACT = GR
    eram artigos de efetor fúngico que nunca falaram da Grécia. Busca por pedaço de
    palavra não é evidência de lugar — é sorteio.
    """
    rx = _RX.get(termo)
    if rx is None:
        # o termo passa pela MESMA normalização do texto: "maíz" nunca acharia nada
        # contra um texto onde o acento já foi removido.
        rx = _RX[termo] = re.compile(r'(?<![a-z0-9])%s(?![a-z0-9])'
                                     % re.escape(_texto(termo).strip()).replace(r'\ ', r'\s+'))
    return bool(rx.search(texto))


def _acha(lex, texto, prefira=None):
    """→ (chave, termo que sustentou) ou (NÃO SEI, ''). O termo fica como prova.

    Um texto pode sustentar MAIS DE UMA chave — um artigo de trigo duro fala de trigo,
    um de micotoxina fala de fusário. `prefira` faz a do recorte congelado ganhar QUANDO
    ELA TAMBÉM ESTÁ NO TEXTO. Isso não é herdar do recorte: se o termo não aparecer, a
    preferência não vale nada.
    """
    achados = []
    for chave, termos in lex.items():
        t = next((t for t in termos if _tem(t, texto)), None)
        if t:
            achados.append((chave, t))
    if not achados:
        return NAO_SEI, ''
    for chave, t in achados:
        if chave == prefira:
            return chave, t
    return achados[0]


def _tipo_material(w):
    tipo = (w.get('type') or '').lower()
    fonte = ((w.get('primary_location') or {}).get('source') or {})
    fonte_tipo = (fonte.get('type') or '').lower()
    if tipo == 'preprint' or fonte_tipo == 'repository':
        return 'PREPRINT'
    if tipo in ('proceedings-article', 'proceedings'):
        return 'CONFERENCE_PAPER'
    if tipo == 'book-chapter':
        return 'BOOK_CHAPTER'
    if tipo == 'review':
        return 'REVIEW'
    if tipo == 'dataset':
        return 'DATASET'
    if tipo == 'report':
        return 'TECHNICAL_ARTICLE'
    if tipo == 'article' and fonte_tipo == 'journal':
        return 'PEER_REVIEWED_PAPER'
    return 'OTHER_TECHNICAL_PUBLICATION'


def classificar(w, pessoa, orcid_declarados):
    titulo = w.get('title') or w.get('display_name') or ''
    resumo = _resumo_do_indice(w.get('abstract_inverted_index'))
    texto = _texto(titulo + ' . ' + resumo)

    # --- PROVA DE PESSOA, obra a obra. Sem isto, o acervo é do id, não da pessoa.
    # O ORCID na autoria NÃO entra aqui: o OpenAlex o herda do perfil e carimba em tudo.
    doi = (w.get('doi') or '').replace('https://doi.org/', '').lower() or None
    minha = next((a for a in w.get('authorships', [])
                  if pessoa['ORCID'] in ((a.get('author') or {}).get('orcid') or '')), None)
    insts = (minha or {}).get('institutions') or []
    alvo_nome = _texto(pessoa['INSTITUTION'])
    alvo_orcid = _texto(pessoa.get('ORCID_EMPLOYER') or '')
    bate_nome = next((i.get('display_name') for i in insts
                      if _texto(i.get('display_name')) in (alvo_nome, alvo_orcid)
                      or alvo_nome in _texto(i.get('display_name'))), None)
    bate_pais = next((i.get('display_name') for i in insts
                      if (i.get('country_code') or '').upper() == pessoa['COUNTRY']), None)

    if doi and doi in orcid_declarados:
        prova = 'ORCID_SELF_DECLARED'
        prova_txt = 'o DOI está na lista de obras do próprio registro ORCID da pessoa'
    elif bate_nome:
        prova = 'AFFILIATION_ON_WORK'
        prova_txt = 'a autoria desta obra declara "%s", a instituição já provada' % bate_nome
    elif bate_pais:
        prova = 'AFFILIATION_COUNTRY_ON_WORK'
        prova_txt = ('a autoria desta obra declara "%s", instituição do mesmo país provado '
                     '(%s) — mais fraco que o nome bater' % (bate_pais, pessoa['COUNTRY']))
    else:
        prova = 'NAME_MATCH_ONLY'
        prova_txt = ('nenhuma instituição declarada nesta obra bate, e o DOI não está no '
                     'ORCID da pessoa — só o id do OpenAlex sustenta. REBAIXADO')

    # --- DOMÍNIO. Separado da pessoa: "é ela mesma" e "é do assunto" são duas perguntas.
    topico = w.get('primary_topic') or {}
    campo = ((topico.get('field') or {}).get('display_name') or '')
    if not campo:
        dominio = 'NO_TOPIC'
    elif campo in DOMINIOS_ACEITOS:
        dominio = 'IN_DOMAIN'
    else:
        dominio = 'OFF_DOMAIN'

    caso = pessoa['CASE_ID']
    _, q_crop, q_issue = RECORTES[caso]
    crop, crop_t = _acha(CROP_LEX, texto, prefira=q_crop)
    # DURUM_WHEAT é mais específico que CEREAL e precisa ganhar dele quando aparece.
    if _tem('durum', texto) or _tem('triticum turgidum', texto):
        crop, crop_t = 'DURUM_WHEAT', 'durum'
    issue, issue_t = _acha(ISSUE_LEX, texto, prefira=q_issue)
    pais, pais_t = _acha(PAIS_LEX, texto)

    papel, papel_t = 'NEW_SCIENTIFIC_EVIDENCE', 'artigo original sem marcador de outro papel'
    for nome, termos in PAPEL_LEX:
        achou = next((t for t in termos if _tem(t, texto)), None)
        if achou:
            papel, papel_t = nome, 'o texto traz "%s"' % achou.strip()
            break

    tipo = _tipo_material(w)
    if papel == 'REVIEW_SYNTHESIS':
        origem = 'REVIEW_SYNTHESIS'
    elif tipo in ('PEER_REVIEWED_PAPER', 'PREPRINT', 'CONFERENCE_PAPER'):
        origem = 'ORIGINAL_RESEARCH'
    else:
        origem = 'OTHER'

    if crop == q_crop and issue == q_issue:
        aderencia = 'ON_FROZEN_CASE'
    elif issue == q_issue:
        aderencia = 'ISSUE_ONLY'
    elif crop == q_crop:
        aderencia = 'CROP_ONLY'
    else:
        aderencia = 'OFF_CASE'

    fonte = ((w.get('primary_location') or {}).get('source') or {})
    data = w.get('publication_date') or ''
    return {
        'DATASET_OWNER': DATASET_OWNER,
        'MATERIAL_ID': w.get('id'),
        'DOI': doi,
        'PERSON_ID': pessoa['PERSON_ID'],
        'NAME': pessoa['NAME'],
        'ORCID': pessoa['ORCID'],
        'INSTITUTION': pessoa['INSTITUTION'],
        'INSTITUTION_COUNTRY': pessoa['COUNTRY'],
        'PERSON_COUNTRY': NAO_SEI,          # nacionalidade NUNCA foi medida. Não se inventa.
        'CASE_ID': caso,
        'QUERY_CROP': q_crop,
        'QUERY_ISSUE': q_issue,
        'SOURCE_ROUTE': 'OPENALEX',
        'SOURCE_URL': w.get('doi') or w.get('id'),
        'TITLE': titulo,
        'PUBLISHED_AT': data,
        'RECENCY_BUCKET': _janela(data),
        'LANGUAGE': w.get('language') or NAO_SEI,
        'VENUE': fonte.get('display_name') or NAO_SEI,
        'VENUE_KIND': (fonte.get('type') or NAO_SEI).upper(),
        'MATERIAL_TYPE': tipo,
        'MATERIAL_ROLE': papel,
        'MATERIAL_ROLE_EVIDENCE': papel_t,
        'ORIGINALITY': origem,
        'PERSON_PROOF': prova,
        'PERSON_PROOF_EVIDENCE': prova_txt,
        'DOMAIN_STATE': dominio,
        'DOMAIN_FIELD': campo or NAO_SEI,
        'AFFILIATION_ON_WORK': [i.get('display_name') for i in insts] or [],
        'PROVED_CROP': crop,
        'PROVED_CROP_EVIDENCE': ('o texto traz "%s"' % crop_t) if crop_t else NAO_SEI,
        'PROVED_ISSUE': issue,
        'PROVED_ISSUE_EVIDENCE': ('o texto traz "%s"' % issue_t) if issue_t else NAO_SEI,
        'COUNTRY_OF_FACT': pais,
        'COUNTRY_OF_FACT_EVIDENCE': ('o texto nomeia "%s"' % pais_t) if pais_t
                                    else 'nenhum lugar nomeado no texto — afiliação NÃO conta',
        'REGION_OF_FACT': NAO_SEI,
        'CASE_ADHERENCE': aderencia,
        'COMPLETE_KEY': bool(pais != NAO_SEI and crop != NAO_SEI and issue != NAO_SEI and data),
        'TRANSCRIPT_AVAILABLE': False,
        'TRANSCRIPT_SOURCE': 'NOT_COLLECTED_THIS_BATCH',
        'ABSTRACT_AVAILABLE': bool(resumo),
        'ABSTRACT': resumo[:1200],
        'CITED_BY': w.get('cited_by_count', 0),
        'IS_RETRACTED': bool(w.get('is_retracted')),
    }


# ----------------------------------------------------------------------------- 3 · MEDIR
def _orcid_urls(orcid):
    """Página oficial, laboratório, projeto — declarados pela própria pessoa."""
    alvo = os.path.join(RAWDIR, 'orcid', '%s-researcher-urls.json' % orcid)
    if not os.path.exists(alvo):
        return []
    d = json.load(open(alvo, encoding='utf-8'))
    return [{'URL_NAME': u.get('url-name') or NAO_SEI,
             'URL': (u.get('url') or {}).get('value') or NAO_SEI,
             'DECLARED_BY': 'ORCID_SELF_DECLARED'}
            for u in (d.get('researcher-url') or [])]


def _orcid_dois(orcid):
    alvo = os.path.join(RAWDIR, 'orcid', '%s-works.json' % orcid)
    if not os.path.exists(alvo):
        return set(), 0
    d = json.load(open(alvo, encoding='utf-8'))
    dois, n = set(), 0
    for g in (d.get('group') or []):
        n += 1
        for ids in ((g.get('external-ids') or {}).get('external-id') or []):
            if (ids.get('external-id-type') or '').lower() == 'doi':
                v = (ids.get('external-id-value') or '').lower()
                dois.add(v.replace('https://doi.org/', ''))
    return dois, n


def medir():
    pessoas = pessoas_provadas()
    materiais, por_pessoa, vistos, dup = [], [], set(), 0

    for p in pessoas:
        autor = p['PERSON_ID'].rsplit('/', 1)[-1]
        alvo = os.path.join(RAWDIR, 'openalex', '%s.json' % autor)
        if not os.path.exists(alvo):
            por_pessoa.append({'NAME': p['NAME'], 'CASE_ID': p['CASE_ID'],
                               'STATE': 'SOURCE_NOT_COLLECTED'})
            continue
        obras = json.load(open(alvo, encoding='utf-8'))['results']
        dois_orcid, grupos_orcid = _orcid_dois(p['ORCID'])
        meus = []
        for w in obras:
            m = classificar(w, p, dois_orcid)
            # DEDUPE: DOI quando existe, id do OpenAlex quando não. Um paper citado no
            # ORCID, no site do lab e num congresso continua sendo UM material.
            chave = m['DOI'] or m['MATERIAL_ID']
            if chave in vistos:
                dup += 1
                continue
            vistos.add(chave)
            materiais.append(m)
            meus.append(m)

        fortes = [m for m in meus if evidencia(m)]
        por_pessoa.append({
            'PERSON_ID': p['PERSON_ID'], 'NAME': p['NAME'], 'ORCID': p['ORCID'],
            'CASE_ID': p['CASE_ID'], 'INSTITUTION': p['INSTITUTION'],
            'INSTITUTION_COUNTRY': p['COUNTRY'],
            'IDENTITY_STATE': p['IDENTITY_STATE'],
            'MATERIALS_FOUND': len(meus),
            'MATERIALS_AS_EVIDENCE': len(fortes),
            'MATERIALS_NAME_MATCH_ONLY': sum(1 for m in meus
                                             if m['PERSON_PROOF'] == 'NAME_MATCH_ONLY'),
            'MATERIALS_OFF_DOMAIN': sum(1 for m in meus if m['DOMAIN_STATE'] != 'IN_DOMAIN'),
            'ON_FROZEN_CASE': sum(1 for m in fortes if m['CASE_ADHERENCE'] == 'ON_FROZEN_CASE'),
            'RECENT_180D': sum(1 for m in fortes
                               if m['RECENCY_BUCKET'] in ('LAST_30D', 'LAST_90D', 'LAST_180D')),
            'COMPLETE_KEY': sum(1 for m in fortes if m['COMPLETE_KEY']),
            'ORCID_WORKS_DECLARED': grupos_orcid,
            'PUBLIC_CHANNELS_DECLARED': _orcid_urls(p['ORCID']),
            'STATE': 'CORPUS_COLLECTED',
        })

    fortes = [m for m in materiais if evidencia(m)]
    janelas = Counter(m['RECENCY_BUCKET'] for m in fortes)
    corpo = {
        'SOURCE_ID': 'RESEARCHER-CORPUS-EAME-V1',
        'DATASET_OWNER': DATASET_OWNER,
        'source': 'OpenAlex (rota REST gratuita) + pub.orcid.org — nenhuma execução paga',
        'SOURCE_LOCATION': 'derivado',
        'FACT_LOCATION': 'ver por item — COUNTRY_OF_FACT só quando o texto nomeia o lugar',
        'ORIGINAL_LANGUAGE': 'pt',
        'EVIDENCE_CLASS': 'DERIVED_MATERIAL_CORPUS',
        'captured_at': REF_DATE,
        'REFERENCE_DATE': REF_DATE,
        'COLLECTION_WINDOW_FROM': DESDE,
        'APIFY_RUNS': 0,
        'COST_USD': 0,
        'RUNNER_NAME': 'LOCAL — nenhum runner de missão bloqueante foi ocupado',
        'O_QUE_ISTO_E': ('o acervo de MATERIAIS PÚBLICOS das 12 identidades já provadas, '
                         'para responder "o que esta pessoa sabe sobre este assunto" — '
                         'não para provar que ela fala hoje.'),
        'O_QUE_ISTO_NAO_E': [
            'não é EARLY_SIGNAL: material de pesquisador não é confirmação de campo',
            'não reabre TECHNICAL_PERSON_SENSOR = NOT_PROVED — aquele veredito continua de pé',
            'não é a carreira inteira: a janela começa em %s e é o PRIMEIRO lote' % DESDE,
            'não é ranking: não há score, não há seguidores, não há autoridade',
            'não é geografia do autor: INSTITUTION_COUNTRY nunca virou COUNTRY_OF_FACT',
            'não tem vídeo nem post: YouTube e LinkedIn estão NOT_COLLECTED neste lote',
        ],
        'LIMITE_DO_CLASSIFICADOR': ('lexical. CROP, ISSUE, COUNTRY_OF_FACT e MATERIAL_ROLE '
                                    'saem de termo encontrado no título/resumo. Polissemia '
                                    'produz falso positivo e nenhum portão automático pega '
                                    'isso — por isso cada campo carrega o trecho que o '
                                    'sustentou, e a conferência é humana.'),
        'PERSON_PROOF_RULE': ('NAME_MATCH ALONE != PERSON_PROOF. O ORCID que o OpenAlex '
                              'mostra na autoria é HERDADO do perfil e não prova nada: ele '
                              'aprovava 763 de 763. Vale como prova só o DOI declarado no '
                              'ORCID da pessoa ou a instituição escrita naquela obra.'),
        'EVIDENCE_RULE': ('conta como evidência a obra que passa nas DUAS portas: '
                          'PERSON_PROOF forte E DOMAIN_STATE = IN_DOMAIN.'),
        'FROZEN_CASES': list(RECORTES),
        'PEOPLE_ATTEMPTED': len(pessoas),
        'MATERIALS_FOUND': len(materiais),
        'MATERIALS_AS_EVIDENCE': len(fortes),
        'BY_PERSON_PROOF': dict(Counter(m['PERSON_PROOF'] for m in materiais)),
        'BY_DOMAIN_STATE': dict(Counter(m['DOMAIN_STATE'] for m in materiais)),
        'MATERIALS_NAME_MATCH_ONLY': sum(1 for m in materiais
                                         if m['PERSON_PROOF'] == 'NAME_MATCH_ONLY'),
        'MATERIALS_OFF_DOMAIN': sum(1 for m in materiais if m['DOMAIN_STATE'] != 'IN_DOMAIN'),
        'DUPLICATES_INTERCEPTED': dup,
        'BY_TYPE': dict(Counter(m['MATERIAL_TYPE'] for m in fortes)),
        'BY_ROLE': dict(Counter(m['MATERIAL_ROLE'] for m in fortes)),
        'BY_ORIGINALITY': dict(Counter(m['ORIGINALITY'] for m in fortes)),
        'BY_RECENCY': dict(janelas),
        'RECENT_180D': sum(janelas[k] for k in ('LAST_30D', 'LAST_90D', 'LAST_180D')),
        'RECENT_365D': sum(janelas[k] for k in ('LAST_30D', 'LAST_90D', 'LAST_180D',
                                                'LAST_365D')),
        'WITH_COUNTRY_OF_FACT': sum(1 for m in fortes if m['COUNTRY_OF_FACT'] != NAO_SEI),
        'WITH_CROP': sum(1 for m in fortes if m['PROVED_CROP'] != NAO_SEI),
        'WITH_ISSUE': sum(1 for m in fortes if m['PROVED_ISSUE'] != NAO_SEI),
        'WITH_COMPLETE_KEY': sum(1 for m in fortes if m['COMPLETE_KEY']),
        'WITH_ABSTRACT': sum(1 for m in fortes if m['ABSTRACT_AVAILABLE']),
        'WITH_TRANSCRIPT': 0,
        'ON_FROZEN_CASE': sum(1 for m in fortes if m['CASE_ADHERENCE'] == 'ON_FROZEN_CASE'),
        'BY_ADHERENCE': dict(Counter(m['CASE_ADHERENCE'] for m in fortes)),
        'COUNTRY_OF_FACT_DISTRIBUTION': dict(Counter(
            m['COUNTRY_OF_FACT'] for m in fortes if m['COUNTRY_OF_FACT'] != NAO_SEI)),
        'BY_PERSON': por_pessoa,
        'MATERIALS': materiais,
    }
    json.dump(corpo, open(DEST, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('publicado %s — %d materiais (%d com prova de pessoa)'
          % (os.path.basename(DEST), len(materiais), len(fortes)))
    diretorio(corpo)
    return corpo


# ------------------------------------------------------- 4 · o artefato derivado do caso
def diretorio(corpo):
    """COUNTRY × CROP × ISSUE → pesquisadores → materiais. É o que o caso vai abrir.

    Um material só aparece embaixo de um recorte quando ele PRÓPRIO sustenta o recorte
    (aderência ON_FROZEN_CASE ou ISSUE_ONLY). A pessoa aparece por identidade; o material,
    por evidência. São duas portas diferentes, e elas não se misturam.
    """
    porcaso = defaultdict(lambda: defaultdict(list))
    for m in corpo['MATERIALS']:
        if not evidencia(m):
            continue
        if m['CASE_ADHERENCE'] in ('ON_FROZEN_CASE', 'ISSUE_ONLY'):
            porcaso[m['CASE_ID']][m['NAME']].append(m)

    saida = []
    for caso, (pais, crop, issue) in RECORTES.items():
        pessoas = [p for p in corpo['BY_PERSON'] if p.get('CASE_ID') == caso]
        blocos = []
        for p in pessoas:
            mats = sorted(porcaso[caso].get(p['NAME'], []),
                          key=lambda x: x['PUBLISHED_AT'], reverse=True)
            blocos.append({
                'NAME': p['NAME'], 'PERSON_ID': p['PERSON_ID'], 'ORCID': p['ORCID'],
                'INSTITUTION': p['INSTITUTION'],
                'INSTITUTION_COUNTRY': p['INSTITUTION_COUNTRY'],
                'INSTITUTION_COUNTRY_IS_NOT_FACT_COUNTRY': True,
                'PUBLIC_CHANNELS_DECLARED': p.get('PUBLIC_CHANNELS_DECLARED', []),
                'RELEVANT_MATERIALS': len(mats),
                'MOST_RECENT': mats[0]['PUBLISHED_AT'] if mats else NAO_SEI,
                'TOP_MATERIALS': [{
                    'TITLE': m['TITLE'], 'PUBLISHED_AT': m['PUBLISHED_AT'],
                    'DOI': m['DOI'], 'URL': m['SOURCE_URL'],
                    'MATERIAL_TYPE': m['MATERIAL_TYPE'], 'MATERIAL_ROLE': m['MATERIAL_ROLE'],
                    'RECENCY_BUCKET': m['RECENCY_BUCKET'],
                    'COUNTRY_OF_FACT': m['COUNTRY_OF_FACT'],
                    'COUNTRY_OF_FACT_EVIDENCE': m['COUNTRY_OF_FACT_EVIDENCE'],
                    'PERSON_PROOF': m['PERSON_PROOF'],
                } for m in mats[:5]],
                'CASE_READINESS': ('READY_WITH_RECENT_MATERIAL'
                                   if any(m['RECENCY_BUCKET'] in
                                          ('LAST_30D', 'LAST_90D', 'LAST_180D', 'LAST_365D')
                                          for m in mats)
                                   else ('READY_ARCHIVE_ONLY' if mats else 'IDENTITY_ONLY')),
            })
        saida.append({'CASE_ID': caso, 'COUNTRY': pais, 'CROP': crop, 'ISSUE': issue,
                      'RESEARCHERS': blocos,
                      'RELEVANT_MATERIALS': sum(b['RELEVANT_MATERIALS'] for b in blocos)})

    corpo2 = {
        'SOURCE_ID': 'EXPERT-DIRECTORY-EAME-V1',
        'DATASET_OWNER': DATASET_OWNER,
        'source': 'derivado de RESEARCHER-CORPUS-EAME-V1 — nenhuma coleta nova',
        'SOURCE_LOCATION': 'derivado',
        'FACT_LOCATION': 'ver por material',
        'ORIGINAL_LANGUAGE': 'pt',
        'EVIDENCE_CLASS': 'DERIVED_DIRECTORY',
        'captured_at': REF_DATE,
        'O_QUE_ISTO_E': ('a camada RESEARCHER / SCIENCE CONTEXT do caso: abrindo um '
                         'COUNTRY × CROP × ISSUE, quem entende disso e qual material '
                         'sustenta.'),
        'O_QUE_ISTO_NAO_E': [
            'não é confirmação de campo — material de pesquisador nunca é isso',
            'não é convergência: juntar duas fontes ainda depende das regras do Early Signal',
            'a pessoa entra pelo recorte que provou a identidade dela; o material entra '
            'pela evidência dele. As duas portas são diferentes.',
        ],
        'CASES': saida,
    }
    json.dump(corpo2, open(DIRETORIO, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('publicado %s' % os.path.basename(DIRETORIO))


# ---------------------------------------------------------------------------- 5 · RESUMO
def resumo():
    c = json.load(open(DEST, encoding='utf-8'))
    print('CORPUS RESEARCHER EAME — referência %s' % c['REFERENCE_DATE'])
    print('  pessoas tentadas ............ %d' % c['PEOPLE_ATTEMPTED'])
    print('  materiais achados ........... %d' % c['MATERIALS_FOUND'])
    print('  valem como evidência ........ %d' % c['MATERIALS_AS_EVIDENCE'])
    print('  só nome (rebaixados) ........ %d' % c['MATERIALS_NAME_MATCH_ONLY'])
    print('  fora do assunto (marcados) .. %d' % c['MATERIALS_OFF_DOMAIN'])
    print('  duplicados interceptados .... %d' % c['DUPLICATES_INTERCEPTED'])
    print('  prova: %s' % json.dumps(c['BY_PERSON_PROOF'], ensure_ascii=False))
    print('  recentes 180d / 365d ........ %d / %d' % (c['RECENT_180D'], c['RECENT_365D']))
    print('  com CROP / ISSUE ............ %d / %d' % (c['WITH_CROP'], c['WITH_ISSUE']))
    print('  com COUNTRY_OF_FACT ......... %d' % c['WITH_COUNTRY_OF_FACT'])
    print('  com CHAVE COMPLETA .......... %d' % c['WITH_COMPLETE_KEY'])
    print('  no recorte congelado ........ %d' % c['ON_FROZEN_CASE'])
    print('  tipos: %s' % json.dumps(c['BY_TYPE'], ensure_ascii=False))
    print('  papéis: %s' % json.dumps(c['BY_ROLE'], ensure_ascii=False))
    print('  país do fato: %s' % json.dumps(c['COUNTRY_OF_FACT_DISTRIBUTION'], ensure_ascii=False))
    print('  janelas: %s' % json.dumps(c['BY_RECENCY'], ensure_ascii=False))
    print('\n  por pessoa (achados / evidência / no recorte / 180d / chave completa):')
    for p in c['BY_PERSON']:
        print('    %-24s %-24s %4d %4d %4d %4d %4d' % (
            p['NAME'][:24], p.get('CASE_ID', '')[:24], p.get('MATERIALS_FOUND', 0),
            p.get('MATERIALS_AS_EVIDENCE', 0), p.get('ON_FROZEN_CASE', 0),
            p.get('RECENT_180D', 0), p.get('COMPLETE_KEY', 0)))


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'resumo'
    if cmd == 'coletar':
        coletar()
    elif cmd == 'medir':
        medir()
    elif cmd == 'resumo':
        resumo()
    else:
        print(__doc__)
