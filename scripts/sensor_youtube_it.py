#!/usr/bin/env python3
"""
ROTA DE CANAL PÚBLICO — YouTube Itália, busca pública, SEM rota paga.

    python3 scripts/sensor_youtube_it.py buscar
    python3 scripts/sensor_youtube_it.py identidade
    python3 scripts/sensor_youtube_it.py resumo

POR QUE NÃO É O SINTONIA SCRAP
-------------------------------
O SINTONIA SCRAP existe e não é reescrito aqui: `scripts/sensor_coleta.py`,
`youtube_janela.py`, `youtube_transcrever.py`, `instagram_coleta.py` já fazem coleta e
transcrição por Apify. **Todos exigem `APIFY_TOKEN`, e este ambiente não tem nenhuma
chave** (medido: nenhuma variável `APIFY*` no ambiente, 2026-09-04).

Portanto: coleta de conteúdo e transcrição saem desta missão como `NOT_REACHED — NO_KEY`,
com o nome do script que a faria. Isso é `FAIL CLOSED`: chave ausente **não** é "canal sem
conteúdo", e nenhum campo de sinal é preenchido por dedução.

O que este arquivo faz é **descoberta de canal**, que é outra camada: achar QUEM existe,
com identidade declarada, para que a coleta — quando houver chave — saiba a quem ir. A
página pública de busca do YouTube responde 200 e traz `ytInitialData` com canal, título e
tempo relativo. Uma requisição por consulta, com pausa. Não é varredura.

A IDENTIDADE VEM DA DESCRIÇÃO DECLARADA PELO CANAL — NUNCA DO VÍDEO
--------------------------------------------------------------------
`MODELO-DE-IDENTIDADE-EAME.md` já fechou isso e custou uma medição: prosa livre
classificando papel produziu `Oleo Revista -> RESEARCHER`. Aqui o papel só sai de:

    canal   -> a descrição que o PRÓPRIO canal declara na aba About

e o vídeo só contribui com ASSUNTO (`CROP`, `ISSUE`), que vem da CONSULTA, não do título.
Sem descrição legível, o canal sai `ROLE = NOT_DECLARED` — que é um estado, não um empate.

O TEMPO RELATIVO NÃO VIRA DATA
-------------------------------
A busca devolve "3 mesi fa", não data. `LAST_CONTENT_DATE` fica `NÃO SEI` e
`LAST_CONTENT_RELATIVE` preserva o que a fonte disse — a mesma regra que os comentários
espanhóis já obrigaram a escrever. Converter um no outro inventaria precisão.
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
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, 'data', 'raw', 'SENSOR-HUMANO-IT')
BUSCA = 'https://www.youtube.com/results'
UA = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
                    '(KHTML, like Gecko) Chrome/126.0 Safari/537.36',
      'Accept-Language': 'it-IT,it;q=0.9'}
PAUSA = 2.0

# --------------------------------------------------------------------------- as consultas
# Em italiano, e ancoradas na matriz ADAMA (`sensor_descoberta_it.MATRIZ`). CROP e ISSUE
# saem da CONSULTA. A consulta é o registro de proveniência: `DISCOVERY_QUERY`.
CONSULTAS = [
    ('agronomo difesa frumento septoria', 'WHEAT', 'SEPTORIA'),
    ('fusariosi spiga frumento difesa tecnico', 'WHEAT', 'FUSARIUM_HEAD_BLIGHT'),
    ('diserbo cereali resistenza graminacee', 'CEREAL', 'HERBICIDE_RESISTANCE'),
    ('agronomo campo grano duro puglia', 'WHEAT', 'RUST'),
    ('piralide mais difesa tecnico', 'MAIZE', 'CORN_BORER'),
    ('diabrotica mais monitoraggio', 'MAIZE', 'ROOTWORM'),
    ('micotossine mais aflatossine tecnico', 'MAIZE', 'MYCOTOXIN'),
    ('diserbo mais sorghetta tecnico', 'MAIZE', 'MAIZE_WEEDS'),
    ('cercospora barbabietola difesa', 'SUGAR_BEET', 'CERCOSPORA'),
    ('peronospora vite difesa agronomo', 'VINE', 'DOWNY_MILDEW'),
    ('flavescenza dorata vite scafoideo', 'VINE', 'FLAVESCENCE_DOREE'),
    ('tignoletta vite lobesia difesa', 'VINE', 'GRAPE_MOTH'),
    ('ticchiolatura melo difesa tecnico', 'APPLE', 'SCAB'),
    ('carpocapsa melo difesa tecnico', 'APPLE', 'CODLING_MOTH'),
    ('diradamento melo brevis metamitron', 'APPLE', 'FRUIT_THINNING'),
    ('monilia pesco difesa tecnico', 'STONE_FRUIT', 'BROWN_ROT'),
    ('cimice asiatica frutteto danni tecnico', 'STONE_FRUIT',
     'BROWN_MARMORATED_STINK_BUG'),
    ('mosca olive bactrocera difesa tecnico', 'OLIVE', 'OLIVE_FRUIT_FLY'),
    ('occhio di pavone olivo difesa', 'OLIVE', 'OLIVE_DISEASE'),
    ('peronospora patata difesa tecnico', 'POTATO', 'LATE_BLIGHT'),
    ('pomodoro industria difesa agronomo', 'TOMATO', 'TOMATO_DISEASE'),
    ('brusone riso difesa tecnico', 'RICE', 'RICE_PROTECTION'),
    ('bollettino difesa integrata tecnico regione', 'MULTI', 'BULLETIN'),
    ('consorzio fitosanitario tecnico campo', 'MULTI', 'BULLETIN'),
    ('agronomo consulente aziendale campo italia', 'MULTI', 'FIELD_ADVISORY'),
    ('resistenza fungicidi SDHI strobilurine', 'MULTI', 'FUNGICIDE_RESISTANCE'),
]

# Um canal com estes termos na descrição DECLARADA anuncia papel técnico. A lista é
# conservadora de propósito: o custo de um falso positivo aqui é promover lifestyle a
# sensor. Termo ausente => NOT_DECLARED, nunca "provavelmente técnico".
TERMOS_PAPEL = [
    ('agronomo', 'AGRONOMIST'), ('agronomi', 'AGRONOMIST'),
    ('dottore agronomo', 'AGRONOMIST'), ('agronomia', 'AGRONOMIST'),
    ('tecnico agricolo', 'FIELD_TECHNICIAN'), ('tecnici', 'FIELD_TECHNICIAN'),
    ('assistenza tecnica', 'FIELD_TECHNICIAN'), ('consulente', 'TECHNICAL_ADVISER'),
    ('ricerca', 'RESEARCH_ORGANIZATION'), ('ricercatore', 'RESEARCHER'),
    ('universit', 'UNIVERSITY'), ('fondazione', 'RESEARCH_ORGANIZATION'),
    ('servizio fitosanitario', 'PLANT_HEALTH_SERVICE'),
    ('consorzio', 'CONSORTIUM'), ('cooperativa', 'COOPERATIVE'),
    ('azienda agricola', 'PRODUCER'), ('agricoltore', 'PRODUCER'),
    ('coltivatore', 'PRODUCER'), ('vivaio', 'NURSERY'),
    ('difesa delle colture', 'CROP_PROTECTION'),
    ('protezione delle piante', 'CROP_PROTECTION'),
    ('fitopatolog', 'PLANT_PATHOLOGIST'), ('entomolog', 'ENTOMOLOGIST'),
    ('cantina', 'WINERY'), ('viticolt', 'VITICULTURE'),
    ('frutticolt', 'FRUIT_GROWING'), ('olivicolt', 'OLIVE_GROWING'),
]

# Canal de EMPRESA de defensivo é concorrente/indústria, não sensor humano. Ele é
# marcado, não descartado em silêncio — a camada COMPETITOR já existe no repositório.
INDUSTRIA = ('syngenta', 'bayer', 'basf', 'corteva', 'adama', 'upl', 'fmc',
             'sumitomo', 'nufarm', 'certis', 'gowan', 'isagro', 'sipcam',
             'biolchim', 'compo', 'k-adriatica', 'chimiberg', 'cifo')


def _norm(s):
    s = unicodedata.normalize('NFKD', s or '')
    return ''.join(c for c in s if not unicodedata.combining(c)).lower()


def _get(url, headers=None):
    req = urllib.request.Request(url, headers=headers or UA)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.read().decode('utf-8', 'replace'), None
    except urllib.error.HTTPError as e:
        return None, 'HTTP %d' % e.code
    except Exception as e:                                               # noqa: BLE001
        return None, type(e).__name__


def _initial_data(t):
    m = re.search(r'var ytInitialData = (\{.*?\});</script>', t, re.S)
    if not m:
        m = re.search(r'ytInitialData"\]\s*=\s*(\{.*?\});', t, re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(1))
    except json.JSONDecodeError:
        return None


def _videos(d):
    out = []

    def walk(o):
        if isinstance(o, dict):
            v = o.get('videoRenderer')
            if isinstance(v, dict):
                titulo = ''.join(r.get('text', '') for r in
                                 ((v.get('title') or {}).get('runs') or []))
                dono = ((v.get('ownerText') or {}).get('runs') or [{}])[0]
                nav = ((dono.get('navigationEndpoint') or {}).get('commandMetadata')
                       or {}).get('webCommandMetadata') or {}
                out.append({
                    'VIDEO_ID': v.get('videoId'), 'TITLE': titulo,
                    'CHANNEL_NAME': dono.get('text'),
                    'CHANNEL_PATH': nav.get('url'),
                    'PUBLISHED_RELATIVE': (v.get('publishedTimeText') or {}).get('simpleText'),
                    'VIEW_TEXT': (v.get('viewCountText') or {}).get('simpleText'),
                })
            for x in o.values():
                walk(x)
        elif isinstance(o, list):
            for x in o:
                walk(x)
    walk(d)
    return out


def buscar():
    os.makedirs(RAW, exist_ok=True)
    canais, consultas = {}, []
    for q, crop, issue in CONSULTAS:
        url = '%s?%s' % (BUSCA, urllib.parse.urlencode(
            {'search_query': q, 'sp': 'CAI%3D'}))       # sp = ordenar por data
        t, err = _get(url)
        d = _initial_data(t) if t else None
        if err or d is None:
            # FAIL CLOSED: nenhuma consulta sai com zero por falha de leitura.
            consultas.append({'QUERY': q, 'CROP': crop, 'ISSUE': issue,
                              'STATE': 'FAILED_WITH_REASON',
                              'REASON': err or 'YTINITIALDATA_NOT_FOUND',
                              'VIDEOS_SEEN': None, 'CHANNELS_SEEN': None})
            print('%-46s FAILED %s' % (q[:46], err or 'NO_YTINITIALDATA'))
            time.sleep(PAUSA)
            continue
        vs = _videos(d)
        vistos = set()
        for v in vs:
            caminho = v['CHANNEL_PATH'] or ''
            if not caminho.startswith('/@'):
                continue
            vistos.add(caminho)
            c = canais.setdefault(caminho, {
                'CHANNEL_PATH': caminho, 'CHANNEL_NAME': v['CHANNEL_NAME'],
                'CHANNEL_URL': 'https://www.youtube.com' + caminho,
                'HITS': 0, 'SCOPES': set(), 'QUERIES': set(), 'SAMPLES': [],
            })
            c['HITS'] += 1
            c['SCOPES'].add('%s|%s' % (crop, issue))
            c['QUERIES'].add(q)
            if len(c['SAMPLES']) < 4:
                c['SAMPLES'].append({k: v[k] for k in
                                     ('VIDEO_ID', 'TITLE', 'PUBLISHED_RELATIVE')})
        consultas.append({'QUERY': q, 'CROP': crop, 'ISSUE': issue, 'STATE': 'COLLECTED',
                          'REASON': None, 'VIDEOS_SEEN': len(vs),
                          'CHANNELS_SEEN': len(vistos)})
        print('%-46s ok  videos=%-3d canais=%d' % (q[:46], len(vs), len(vistos)))
        time.sleep(PAUSA)

    saida = []
    for c in canais.values():
        saida.append({
            'CHANNEL_PATH': c['CHANNEL_PATH'], 'CHANNEL_NAME': c['CHANNEL_NAME'],
            'CHANNEL_URL': c['CHANNEL_URL'], 'HITS': c['HITS'],
            'SCOPES': sorted(c['SCOPES']), 'DISCOVERY_QUERIES': sorted(c['QUERIES']),
            'SAMPLE_VIDEOS': c['SAMPLES'],
        })
    saida.sort(key=lambda c: (-c['HITS'], c['CHANNEL_NAME'] or ''))
    corpo = {
        'SOURCE_ID': 'SENSOR-HUMANO-IT/YOUTUBE-DISCOVERY',
        'source': 'youtube.com/results — página pública de busca, rota gratuita, sem chave',
        'SOURCE_LOCATION': 'global',
        'FACT_LOCATION': 'NÃO SEI',
        'ORIGINAL_LANGUAGE': 'IT (consultas)',
        'WHAT_THIS_IS': 'DESCOBERTA DE CANAL. Não é coleta de conteúdo nem transcrição.',
        'CONTENT_COLLECTION_STATE': 'NOT_REACHED — NO_KEY. scripts/sensor_coleta.py e '
                                    'scripts/youtube_transcrever.py exigem APIFY_TOKEN, '
                                    'ausente neste ambiente (medido 2026-09-04).',
        'DATE_POLICY': 'a busca devolve tempo relativo; LAST_CONTENT_DATE = NÃO SEI e '
                       'LAST_CONTENT_RELATIVE preserva o que a fonte disse',
        'QUERIES': consultas,
        'QUERIES_FAILED': [c['QUERY'] for c in consultas if c['STATE'] != 'COLLECTED'],
        'CHANNELS_COUNT': len(saida),
        'CHANNELS': saida,
        'CAPTURED_AT': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
    }
    p = os.path.join(RAW, 'youtube-IT.json')
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(corpo, f, ensure_ascii=False, indent=1)
    print('\n%d canais -> %s' % (len(saida), p))
    return corpo


def _descricao_canal(caminho):
    """Descrição DECLARADA pelo canal, da própria aba About. Nunca do vídeo."""
    t, err = _get('https://www.youtube.com%s/about' % caminho)
    if err or not t:
        return None, err or 'EMPTY'
    d = _initial_data(t)
    if d is None:
        return None, 'YTINITIALDATA_NOT_FOUND'
    achado = {}

    def walk(o):
        if isinstance(o, dict):
            if 'aboutChannelViewModel' in o:
                v = o['aboutChannelViewModel']
                achado.setdefault('DESCRIPTION', v.get('description'))
                achado.setdefault('COUNTRY', v.get('country'))
                achado.setdefault('SUBSCRIBERS_TEXT', v.get('subscriberCountText'))
                achado.setdefault('VIDEOS_TEXT', v.get('videoCountText'))
                achado.setdefault('CANONICAL_URL', v.get('canonicalChannelUrl'))
                achado.setdefault('LINKS', [
                    (x.get('channelExternalLinkViewModel') or {}).get('title', {}).get('content')
                    for x in (v.get('links') or [])])
                achado.setdefault('LINK_URLS', [
                    ((x.get('channelExternalLinkViewModel') or {}).get('link') or {})
                    .get('content') for x in (v.get('links') or [])])
            for x in o.values():
                walk(x)
        elif isinstance(o, list):
            for x in o:
                walk(x)
    walk(d)
    return (achado or None), (None if achado else 'ABOUT_BLOCK_NOT_FOUND')


def papel_declarado(desc, nome):
    """Papel a partir da DESCRIÇÃO declarada. Nome do canal não decide papel."""
    if not desc:
        return 'NOT_DECLARED', 'NO_DESCRIPTION_READ'
    n = _norm(desc)
    achados = sorted({p for termo, p in TERMOS_PAPEL if _norm(termo) in n})
    if not achados:
        return 'NOT_DECLARED', 'NO_DECLARED_ROLE_TERM_IN_DESCRIPTION'
    if len(achados) > 1:
        return 'AMBIGUOUS:' + '|'.join(achados), 'MULTIPLE_ROLE_TERMS_DECLARED'
    return achados[0], 'DECLARED_IN_CHANNEL_DESCRIPTION'


# O YouTube devolve o país na LÍNGUA do Accept-Language. Com `it-IT` vem "Italia". O
# valor bruto é preservado em DECLARED_COUNTRY_RAW; este mapa só normaliza a forma, e
# país fora do mapa fica como veio — traduzir por semelhança inventaria país.
PAIS_ISO = {
    'italia': 'IT', 'italy': 'IT', 'germania': 'DE', 'germany': 'DE',
    'francia': 'FR', 'france': 'FR', 'spagna': 'ES', 'spain': 'ES',
    'stati uniti': 'US', 'united states': 'US', 'danimarca': 'DK', 'denmark': 'DK',
    'svizzera': 'CH', 'switzerland': 'CH', 'regno unito': 'GB', 'united kingdom': 'GB',
    'paesi bassi': 'NL', 'netherlands': 'NL', 'belgio': 'BE', 'austria': 'AT',
    'portogallo': 'PT', 'brasile': 'BR', 'brazil': 'BR', 'argentina': 'AR',
    'messico': 'MX', 'mexico': 'MX', 'india': 'IN', 'grecia': 'GR', 'greece': 'GR',
    'polonia': 'PL', 'poland': 'PL', 'romania': 'RO', 'turchia': 'TR',
    'israele': 'IL', 'israel': 'IL', 'canada': 'CA', 'australia': 'AU',
}


def identidade():
    """Abre a aba About de cada canal. Uma requisição por canal, com pausa.

    Grava a cada bloco: uma execução interrompida preserva o que já resolveu, e a
    próxima retoma. Canal já resolvido não é rebuscado.
    """
    p = os.path.join(RAW, 'youtube-IT.json')
    with open(p, encoding='utf-8') as f:
        d = json.load(f)

    def salvar():
        cont = __import__('collections').Counter
        d['IDENTITY_RESOLVED_AT'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        feitos = [c for c in d['CHANNELS'] if 'ABOUT_STATE' in c]
        d['IDENTITY_RESOLVED_COUNT'] = len(feitos)
        d['IDENTITY_PENDING_COUNT'] = len(d['CHANNELS']) - len(feitos)
        d['DECLARED_COUNTRY_DISTRIBUTION'] = dict(sorted(
            cont(c.get('DECLARED_COUNTRY', 'NOT_RESOLVED') for c in d['CHANNELS']).items(),
            key=lambda kv: -kv[1]))
        d['DECLARED_ROLE_DISTRIBUTION'] = dict(sorted(
            cont(c.get('DECLARED_ROLE', 'NOT_RESOLVED') for c in d['CHANNELS']).items(),
            key=lambda kv: -kv[1]))
        with open(p, 'w', encoding='utf-8') as g:
            json.dump(d, g, ensure_ascii=False, indent=1)

    feitos = 0
    for c in d['CHANNELS']:
        if 'ABOUT_STATE' in c:
            continue
        info, err = _descricao_canal(c['CHANNEL_PATH'])
        c['ABOUT_STATE'] = 'READ' if info else 'FAILED_WITH_REASON'
        c['ABOUT_REASON'] = err
        c['DESCRIPTION'] = (info or {}).get('DESCRIPTION')
        bruto = (info or {}).get('COUNTRY')
        c['DECLARED_COUNTRY_RAW'] = bruto or 'NOT_DECLARED'
        c['DECLARED_COUNTRY'] = PAIS_ISO.get(_norm(bruto or ''), bruto or 'NOT_DECLARED')
        c['SUBSCRIBERS_TEXT'] = (info or {}).get('SUBSCRIBERS_TEXT')
        c['VIDEOS_TEXT'] = (info or {}).get('VIDEOS_TEXT')
        c['EXTERNAL_LINKS'] = [x for x in ((info or {}).get('LINK_URLS') or []) if x]
        papel, base = papel_declarado(c['DESCRIPTION'], c['CHANNEL_NAME'])
        c['DECLARED_ROLE'] = papel
        c['DECLARED_ROLE_BASIS'] = base
        c['IS_INDUSTRY'] = any(x in _norm('%s %s' % (c['CHANNEL_NAME'], c['DESCRIPTION'] or ''))
                               for x in INDUSTRIA)
        print('%-34s %-8s %-26s %s' % (
            (c['CHANNEL_NAME'] or '')[:34], c['DECLARED_COUNTRY'],
            papel[:26], c['SUBSCRIBERS_TEXT'] or '-'))
        feitos += 1
        if feitos % 10 == 0:
            salvar()
        time.sleep(PAUSA)
    salvar()
    print('\npaíses declarados: %s' % d['DECLARED_COUNTRY_DISTRIBUTION'])
    return d


def resumo():
    with open(os.path.join(RAW, 'youtube-IT.json'), encoding='utf-8') as f:
        d = json.load(f)
    print('%d canais · consultas falhas: %s' % (
        d['CHANNELS_COUNT'], d['QUERIES_FAILED'] or 'nenhuma'))
    for c in d['CHANNELS'][:30]:
        print('  %-34s hits=%-2d %-8s %s' % (
            (c['CHANNEL_NAME'] or '')[:34], c['HITS'],
            c.get('DECLARED_COUNTRY', '?'), c.get('DECLARED_ROLE', '?')))


if __name__ == '__main__':
    {'buscar': buscar, 'identidade': identidade,
     'resumo': resumo}[sys.argv[1] if len(sys.argv) > 1 else 'resumo']()
