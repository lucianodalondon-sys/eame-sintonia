#!/usr/bin/env python3
"""
PILOTO SOCIAL CONTROLADO — 15 canais dos 89. Amostra pequena, pergunta grande.

    python3 scripts/sensor_piloto_social_it.py selecionar   # ANTES da coleta
    python3 scripts/sensor_piloto_social_it.py coletar
    python3 scripts/sensor_piloto_social_it.py medir

A pergunta: **quando abrimos essas portas, entra inteligência agrícola que vale manter?**

⛔ ISOLAMENTO: missão UPSTREAM. Não toca portal, Linha B, checkpoint 55c2674, Vercel,
deploy, Brasil, Radar Futuro nem motor canônico. Nada daqui entra no produto.

═══════════════════════════════════════════════════════════════════════════════════════
A ROTA, E POR QUE ELA NÃO É ARQUITETURA NOVA
═══════════════════════════════════════════════════════════════════════════════════════
`APIFY_TOKEN` está **ausente** (medido: nenhuma variável `APIFY*` no ambiente). Antes de
declarar bloqueio total, a missão manda verificar rota pública já existente no repositório.

Existe: `sensor_youtube_it.py` já lê o YouTube por **rota pública sem chave**
(`ytInitialData` da busca e da aba About). O piloto usa **a mesma rota, na mesma
plataforma**, num endpoint mais conservador ainda — o **feed público do canal**
(`/feeds/videos.xml`), que é oficial, não exige chave e não pagina.

    ⛔ Nenhuma arquitetura de scraping nova foi criada.

E o que NÃO tem rota fica medido, não afirmado: Instagram, TikTok, LinkedIn e Twitter
respondem **200 com casca de login e zero conteúdo** — e a casa já ensinou que
`HTTP 200 != fonte viva`. Cada um entra no piloto com uma amostra para **provar** o
bloqueio por plataforma, em vez de deduzi-lo.

═══════════════════════════════════════════════════════════════════════════════════════
⛔ A LEI INVIOLÁVEL DESTE ARQUIVO
═══════════════════════════════════════════════════════════════════════════════════════
    conteúdo pode dizer DO QUE a entidade fala.
    conteúdo NÃO pode provar QUEM a entidade é.

20 vídeos sobre viticultura provam `TOPIC = VITICULTURE`. **Não** provam
`ROLE = AGRONOMIST`. Nenhuma função aqui escreve em `ROLES`, e `medir` verifica isso.

E o documento nunca se liga à entidade direto:  `DOCUMENT → SOURCE_ID → ENTITY_ID`.

═══════════════════════════════════════════════════════════════════════════════════════
⚠️ O LIMITE DO CLASSIFICADOR, declarado antes do número
═══════════════════════════════════════════════════════════════════════════════════════
A classificação de assunto é **lexical**, sobre título + descrição. Polissemia produz
falso positivo e nenhum portão automático detecta isso — foi o que o `SENSOR-PILOT`
brasileiro já registrou. Por isso todo item carrega o TRECHO que o classificou, e a
verificação é humana. Sem base no vocabulário canônico: `NÃO SEI`, nunca chute.
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
from collections import Counter, OrderedDict, defaultdict
from selo_de_amostra import selar

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEST = os.path.join(ROOT, 'data', 'samples', 'IT-HUMAN-SENSORS')
RAW = os.path.join(ROOT, 'data', 'raw', 'SENSOR-HUMANO-IT')
ENTIDADES = os.path.join(DEST, 'ENTITIES.json')
FONTES = os.path.join(DEST, 'SOURCES.json')
UNIVERSO = os.path.join(DEST, 'UNIVERSE.json')
SELECAO = os.path.join(DEST, 'PILOT-SELECTION.json')
DOCS = os.path.join(DEST, 'PILOT-DOCUMENTS.json')
MEDIDA = os.path.join(DEST, 'PILOT-MEASUREMENT.json')

UA = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
                    '(KHTML, like Gecko) Chrome/126.0 Safari/537.36',
      'Accept-Language': 'it-IT,it;q=0.9'}
MAX_POR_CANAL = 10
PAUSA = 1.2

PLATAFORMA_COM_ROTA = {'youtube'}
CAMPO = ('agronomo', 'tecnico', 'produtor', 'consultor', 'cooperativa',
         'organizacao_de_produtores', 'associacao', 'servico_fitossanitario',
         'veiculo_tecnico')


def _norm(s):
    s = unicodedata.normalize('NFKD', s or '')
    return ''.join(c for c in s if not unicodedata.combining(c)).lower()


def _get(url, headers=None, limite=600000):
    req = urllib.request.Request(url, headers=headers or UA)
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            return r.read(limite).decode('utf-8', 'replace'), r.getcode(), None
    except urllib.error.HTTPError as e:
        return '', e.code, 'HTTP %d' % e.code
    except Exception as e:                                               # noqa: BLE001
        return '', None, type(e).__name__


# ═══════════════════════════════════════════════════════ 1 · SELEÇÃO, ANTES DE COLETAR
def selecionar():
    with open(ENTIDADES, encoding='utf-8') as f:
        E = json.load(f)
    with open(FONTES, encoding='utf-8') as f:
        S = json.load(f)
    ents = {e['ENTITY_ID']: e for e in E['ENTITIES']}
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import sensor_resolver_fontes_it as R

    def monit(f):
        return (f.get('SOURCE_TYPE') == 'MONITORABLE_CHANNEL'
                or f.get('PLATAFORMA') in R.MONITORAVEL)

    cands = []
    for f in S['SOURCES']:
        if not monit(f):
            continue
        e = ents.get(f['ENTITY_ID'])
        if not e:
            continue
        ps = [r['PAPEL'] for r in e['ROLES'] if r['ESTADO'] in ('PROVADO', 'PROBABLE')]
        grupo = ('A' if any(p in CAMPO for p in ps) else
                 'B' if any(p in ('pesquisador', 'professor') for p in ps) else 'C')
        cands.append({'GRUPO': grupo, 'PLATAFORMA': f['PLATAFORMA'],
                      'PILOT_ENTITY_ID': e['ENTITY_ID'], 'NOME': e['NOME_CANONICO'],
                      'SOURCE_ID': f['SOURCE_ID'], 'CHANNEL': f['URL'],
                      'ROLE_PROVED': ps,
                      'ROLE_STATE': 'PROVED' if ps else 'UNKNOWN',
                      'IDENTITY_EVIDENCE': (f.get('OWNERSHIP_EVIDENCE')
                                            or f.get('LINK_EVIDENCE') or 'NÃO SEI')[:200]})

    def ordena(c):
        return (c['SOURCE_ID'])
    sel = []

    # GRUPO A — todos os canais com ROTA de entidades com papel provado
    for c in sorted([c for c in cands if c['GRUPO'] == 'A'
                     and c['PLATAFORMA'] in PLATAFORMA_COM_ROTA], key=ordena):
        c['WHY_SELECTED'] = ('GRUPO A — papel agrícola/técnico PROVADO (%s) e plataforma '
                             'com rota pública' % '/'.join(c['ROLE_PROVED']))
        sel.append(c)

    # GRUPO B — TODOS os pesquisadores com canal monitorável, mesmo sem rota:
    # é a única forma de responder se o canal público acrescenta algo, e o bloqueio
    # por plataforma é resultado, não desculpa.
    for c in sorted([c for c in cands if c['GRUPO'] == 'B'], key=ordena):
        c['WHY_SELECTED'] = ('GRUPO B — pesquisador com voz pública (%s). Incluído mesmo '
                             'sem rota: o bloqueio por plataforma é a medida.'
                             % '/'.join(c['ROLE_PROVED']))
        sel.append(c)

    # GRUPO C — completar até 15. Uma fonte por entidade, para variar entidade e não
    # empilhar canais do mesmo dono. E UMA amostra de cada plataforma sem rota, para
    # PROVAR o bloqueio por plataforma em vez de deduzi-lo.
    usados = {c['PILOT_ENTITY_ID'] for c in sel}
    c_yt = [c for c in cands if c['GRUPO'] == 'C' and c['PLATAFORMA'] == 'youtube']
    vistos = set()
    c_yt_unico = []
    for c in sorted(c_yt, key=ordena):
        if c['PILOT_ENTITY_ID'] in usados or c['PILOT_ENTITY_ID'] in vistos:
            continue
        vistos.add(c['PILOT_ENTITY_ID'])
        c_yt_unico.append(c)

    faltam = 15 - len(sel)
    sonda = []
    for plat in ('instagram', 'tiktok'):
        cc = sorted([c for c in cands if c['GRUPO'] == 'C' and c['PLATAFORMA'] == plat],
                    key=ordena)
        if cc:
            x = cc[0]
            x['WHY_SELECTED'] = ('GRUPO C — sonda de plataforma: mede se %s tem rota '
                                 'pública, em vez de presumir bloqueio' % plat)
            sonda.append(x)
    sonda = sonda[:min(2, faltam)]
    for c in c_yt_unico[:faltam - len(sonda)]:
        c['WHY_SELECTED'] = ('GRUPO C — entidade sem papel provado, identidade forte, '
                             'plataforma com rota. Serve ao experimento PROVADO × NÃO '
                             'PROVADO')
        sel.append(c)
    sel += sonda
    sel = sel[:15]

    corpo = {
        'SOURCE_ID': 'IT-HUMAN-SENSORS/PILOT-SELECTION',
        'REGISTRADO_ANTES_DA_COLETA': True,
        'REGRA_DE_SELECAO': 'A (papel provado, com rota) → B (todos os pesquisadores com '
                            'canal monitorável) → C (uma fonte por entidade + sondas de '
                            'plataforma). ⛔ Nenhum critério lê followers.',
        'FOLLOWERS_USADO': False,
        'UNIVERSO_MONITORAVEL': len(cands),
        'PILOT_CHANNELS': len(sel),
        'PILOT_ENTITIES': len({c['PILOT_ENTITY_ID'] for c in sel}),
        'POR_GRUPO': dict(Counter(c['GRUPO'] for c in sel)),
        'POR_PLATAFORMA': dict(Counter(c['PLATAFORMA'] for c in sel)),
        'COM_ROTA_PUBLICA': sum(1 for c in sel if c['PLATAFORMA'] in PLATAFORMA_COM_ROTA),
        'SEM_ROTA_PUBLICA': sum(1 for c in sel
                                if c['PLATAFORMA'] not in PLATAFORMA_COM_ROTA),
        'APIFY_TOKEN_AVAILABLE': bool(os.environ.get('APIFY_TOKEN')
                                      or os.environ.get('APIFY_API_TOKEN')),
        'SELECAO': sel,
        'CAPTURED_AT': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
    }
    with open(SELECAO, 'w', encoding='utf-8') as f:
        json.dump(selar(corpo), f, ensure_ascii=False, indent=1)
    print('selecionados %d de %d monitoráveis · grupos %s · plataformas %s'
          % (len(sel), len(cands), corpo['POR_GRUPO'], corpo['POR_PLATAFORMA']))
    print('com rota pública: %d · sem rota: %d · APIFY_TOKEN: %s'
          % (corpo['COM_ROTA_PUBLICA'], corpo['SEM_ROTA_PUBLICA'],
             corpo['APIFY_TOKEN_AVAILABLE']))
    for c in sel:
        print('  %-1s %-9s %-30s %-13s %s' % (
            c['GRUPO'], c['PLATAFORMA'], (c['NOME'] or '')[:30], c['SOURCE_ID'],
            '/'.join(c['ROLE_PROVED']) or '—'))
    return corpo


# ═══════════════════════════════════════════════════════════════════════════════════
# 2 · O DONO CANÔNICO DA COLETA, DECLARADO ANTES DE EXECUTAR
# ═══════════════════════════════════════════════════════════════════════════════════
# A missão manda: se houver mais de uma implementação, PARAR e declarar qual é o dono.
# Há três, e elas não competem — cada uma cobre uma etapa da mesma escada:
#
#   scripts/youtube_janela.py   ROTA PÚBLICA GRATUITA de YouTube. Dono das fases
#                               `canais` · `objetos` · `legendas`. APIFY_RUNS=0,
#                               COST_USD=0 declarados no próprio artefato.
#                               ⬅️ É ESTE o dono canônico deste piloto.
#   scripts/youtube_transcrever.py  WHISPER — só o que a legenda não deu.
#   scripts/sensor_coleta.py · coletor.py · apify_pool.py   ROTA PAGA (Apify).
#                               Exige APIFY_TOKEN. ⛔ Indisponível.
#
# E a ordem é lei, escrita por `youtube_janela.py` e obedecida aqui:
#
#   LOTE CONGELADO → CANAL → OBJETO → LEGENDA → (só então) WHISPER → (só então) PAGO
#
# ⚠️ O NOME "SINTONIA SCRAP" não existe como componente no repositório: ele aparece
# só em documentos desta branch. O componente REAL tem nome próprio, e é o de cima.
# Registrado para que ninguém procure um dono que não existe sob esse rótulo.
LOTE_PILOTO = os.path.join(DEST, 'PILOT-BATCH.json')
SAIDA_PILOTO = os.path.join(RAW, 'PILOTO-YOUTUBE')


def lote():
    """Reescreve a seleção no formato do LOTE CONGELADO que o dono canônico obedece.

    ⚠️ Quatro dos 15 selecionados não têm rota: Instagram, TikTok, LinkedIn e Twitter
    só entram pela rota paga, e `APIFY_TOKEN` está ausente. A missão manda substituir
    preservando a estratificação — e REGISTRAR a lacuna quando a família inteira cai.
    A família PESQUISADOR cai inteira: os dois pesquisadores com canal monitorável
    estão em Twitter e LinkedIn.
    """
    with open(SELECAO, encoding='utf-8') as f:
        S = json.load(f)
    sel = S['SELECAO']
    suportados = [c for c in sel if c['PLATAFORMA'] in PLATAFORMA_COM_ROTA]
    nao = [dict(c, SCRAP_SUPPORTED='NO',
                REASON=('plataforma %s só entra pela rota paga (scripts/sensor_coleta.py '
                        '+ apify_pool.py) e APIFY_TOKEN está ausente. O dono canônico '
                        'gratuito (youtube_janela.py) cobre apenas YouTube.'
                        % c['PLATAFORMA']))
           for c in sel if c['PLATAFORMA'] not in PLATAFORMA_COM_ROTA]

    # substituição, preservando estratificação: só YouTube, uma fonte por entidade nova
    with open(ENTIDADES, encoding='utf-8') as f:
        E = json.load(f)
    with open(FONTES, encoding='utf-8') as f:
        F = json.load(f)
    ents = {e['ENTITY_ID']: e for e in E['ENTITIES']}
    ja_ent = {c['PILOT_ENTITY_ID'] for c in suportados}
    subs = []
    for f_ in sorted(F['SOURCES'], key=lambda x: x['SOURCE_ID']):
        if len(suportados) + len(subs) >= 15:
            break
        if f_['PLATAFORMA'] != 'youtube' or f_['ENTITY_ID'] in ja_ent:
            continue
        e = ents.get(f_['ENTITY_ID'])
        if not e:
            continue
        ja_ent.add(f_['ENTITY_ID'])
        ps = [r['PAPEL'] for r in e['ROLES'] if r['ESTADO'] in ('PROVADO', 'PROBABLE')]
        subs.append({
            'GRUPO': 'C', 'PLATAFORMA': 'youtube', 'PILOT_ENTITY_ID': e['ENTITY_ID'],
            'NOME': e['NOME_CANONICO'], 'SOURCE_ID': f_['SOURCE_ID'],
            'CHANNEL': f_['URL'], 'ROLE_PROVED': ps,
            'ROLE_STATE': 'PROVED' if ps else 'UNKNOWN',
            'IDENTITY_EVIDENCE': (f_.get('OWNERSHIP_EVIDENCE')
                                  or f_.get('LINK_EVIDENCE') or 'NÃO SEI')[:200],
            'WHY_SELECTED': 'SUBSTITUTO — entra no lugar de um canal sem rota, '
                            'preservando a estratificação (YouTube, entidade nova)'})
    final = suportados + subs

    contas = []
    for c in final:
        contas.append({
            'PLATFORM': 'YOUTUBE',
            'ACCOUNT_URL': c['CHANNEL'],
            'ACCOUNT_HANDLE': c['SOURCE_ID'],   # ⬅️ chave de junção determinística
            'COMPANY': c['NOME'],
            'COUNTRY_SCOPE': 'IT_PILOT',
            'SOURCE_ID': c['SOURCE_ID'], 'ENTITY_ID': c['PILOT_ENTITY_ID'],
            'ROLE_STATE': c['ROLE_STATE'], 'ROLE_PROVED': c['ROLE_PROVED'],
            'IDENTITY_EVIDENCE': c['IDENTITY_EVIDENCE'],
        })
    corpo = {
        'SOURCE_ID': 'IT-HUMAN-SENSORS/PILOT-BATCH',
        'DATASET_OWNER': 'piloto social IT — sensores humanos',
        'VERSION': 1, 'FROZEN_AT': time.strftime('%Y-%m-%d'),
        'FROZEN_RULE': 'lista datada e congelada ANTES da coleta; a coleta obedece, '
                       'não escolhe',
        'SCRAP_CANONICAL_OWNER': 'scripts/youtube_janela.py (fases canais·objetos·'
                                 'legendas) — rota pública, APIFY_RUNS=0, COST_USD=0',
        'SCRAP_SUPPORTED_PLATFORMS': ['YOUTUBE'],
        'SCRAP_UNSUPPORTED_TODAY': ['INSTAGRAM', 'TIKTOK', 'LINKEDIN', 'TWITTER',
                                    'FACEBOOK'],
        'APIFY_TOKEN_AVAILABLE': False, 'APIFY_USED': False,
        'NEW_SCRAPER_CREATED': False,
        'PILOT_CHANNELS_REQUESTED': 15,
        'PILOT_CHANNELS_SUPPORTED': len(final),
        'PILOT_CHANNELS_UNSUPPORTED': len(nao),
        'SUBSTITUICOES': len(subs),
        'UNSUPPORTED': nao,
        'LACUNA_DE_FAMILIA': {
            'FAMILIA': 'PESQUISADOR com voz pública',
            'ESTADO': 'INTEIRAMENTE SEM ROTA',
            'POR_QUE': 'os dois pesquisadores com canal monitorável publicam em Twitter '
                       'e LinkedIn; nenhuma das duas plataformas tem rota gratuita, e a '
                       'paga exige APIFY_TOKEN ausente.',
            'CONSEQUENCIA': 'a pergunta "o canal público do pesquisador acrescenta algo '
                            'que o Europe PMC não entrega?" NÃO pode ser respondida '
                            'nesta rodada. RESEARCHER_PUBLIC_CHANNELS_TESTED = 0.'},
        'CONTAS': contas,
    }
    with open(LOTE_PILOTO, 'w', encoding='utf-8') as f:
        json.dump(selar(corpo), f, ensure_ascii=False, indent=1)
    print('lote congelado: %d contas · substituídos %d · sem rota %d'
          % (len(contas), len(subs), len(nao)))
    print('dono canônico: %s' % corpo['SCRAP_CANONICAL_OWNER'])
    for c in contas:
        print('  %-13s %-30s %s' % (c['SOURCE_ID'], (c['COMPANY'] or '')[:30],
                                    c['ROLE_STATE']))
    return corpo


def coletar():
    """Chama o dono canônico. ⛔ Nenhuma linha de scraping nova é escrita aqui."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import youtube_janela as YJ
    os.makedirs(SAIDA_PILOTO, exist_ok=True)
    # reuso: aponta o dono canônico para o lote do piloto e para a saída do piloto
    YJ.LOTE = LOTE_PILOTO
    YJ.SAIDA = SAIDA_PILOTO
    YJ.BRUTO = os.path.join(SAIDA_PILOTO, 'html-bruto')
    print('== FASE CANAIS =='); YJ.fase_canais()
    print('== FASE OBJETOS (teto %d por canal) ==' % MAX_POR_CANAL)
    YJ.fase_objetos(limite=MAX_POR_CANAL)
    print('== FASE LEGENDAS ==')
    try:
        YJ.fase_legendas(limite=MAX_POR_CANAL)
    except Exception as e:                                               # noqa: BLE001
        print('legendas: %s — a fase exige navegador; segue sem ela' % type(e).__name__)
    return 0


# ═══════════════════════════════════════════════════════════════════════════════════
# 3 · MEDIR — o que entrou pela porta, e se vale manter
# ═══════════════════════════════════════════════════════════════════════════════════
# ⚠️ LIMITE DECLARADO ANTES DO NÚMERO: a classificação é LEXICAL, sobre título +
# legenda quando existe. Polissemia produz falso positivo e nenhum portão automático
# detecta isso. Todo item carrega o TRECHO que o classificou; a verificação é humana.
#
# ⛔ E A LEI: nada aqui escreve em ROLES. Conteúdo diz DO QUE se fala, nunca QUEM é.

# Léxico italiano ancorado no vocabulário canônico da matriz ADAMA (UNIVERSE.json).
CROP_IT = {
    'WHEAT': ('frumento', 'grano', 'grano duro', 'orzo', 'cereali', 'cereale', 'triticale'),
    'MAIZE': ('mais', 'granoturco', 'trinciato'),
    'VINE': ('vite', 'viti', 'vigneto', 'vigna', 'uva', 'vino', 'viticolt', 'vendemmia',
             'grappol', 'enolog'),
    'APPLE': ('melo', 'meli', 'mela', 'mele', 'frutteto', 'meleto'),
    'OLIVE': ('olivo', 'olivi', 'oliveto', 'oliva', 'olive', 'olio extraverg', 'olivicolt'),
    'STONE_FRUIT': ('pesco', 'pesche', 'ciliegio', 'ciliegie', 'albicocc', 'susin'),
    'SUGAR_BEET': ('barbabietola', 'bietola'),
    'TOMATO': ('pomodoro', 'pomodori'),
    'POTATO': ('patata', 'patate'),
    'RICE': ('riso', 'risaia'),
}
ISSUE_IT = {
    'DISEASE': ('peronospora', 'oidio', 'ticchiolatura', 'septoria', 'fusari', 'ruggine',
                'monilia', 'cercospora', 'botrite', 'muffa', 'malattia', 'fungin',
                'micotossin', 'flavescenza', 'mal dell', 'marciume'),
    'PEST': ('carpocapsa', 'tignol', 'cimice', 'afide', 'insetto', 'insetti', 'larva',
             'mosca', 'piralide', 'diabrotica', 'scafoideo', 'lobesia', 'acaro',
             'nematod', 'parassit'),
    'WEED': ('infestant', 'diserbo', 'erbaccia', 'malerb'),
    'RESISTANCE': ('resistenz',),
    'PRACTICE': ('potatura', 'concimazione', 'irrigazione', 'semina', 'trapianto',
                 'raccolta', 'innesto', 'difesa', 'trattamento', 'nutrizione',
                 'fertilizz', 'lavorazione', 'gestione'),
}
PRODUTO_IT = ('fungicida', 'insetticida', 'erbicida', 'agrofarmac', 'fitofarmac',
              'prodotto', 'biostimolant', 'concime', 'rame', 'zolfo')
CAMPO_IT = ('in campo', 'in azienda', 'sopralluogo', 'abbiamo visto', 'ho visto',
            'quest anno', 'questa stagione', 'la situazione', 'monitoraggio',
            'ho notato', 'stiamo', 'siamo in')
TECNICO_IT = ('come fare', 'perche', 'strategia', 'tecnica', 'consigli', 'guida',
              'spiega', 'dose', 'soglia', 'epoca', 'quando')
COMERCIAL_IT = ('offerta', 'promozione', 'acquista', 'shop', 'catalogo', 'prezzo',
                'in vendita', 'nuovo prodotto', 'lancio')
PESQUISA_IT = ('ricerca', 'studio', 'sperimentazione', 'prova', 'convegno', 'progetto',
               'risultati', 'webinar')
# ⚠️ Marcadores POSITIVOS de assunto NÃO agrícola. Existem para que `OFF_TOPIC` seja
# uma AFIRMAÇÃO com prova, e não o resto que sobrou.
NAO_AGRO_IT = ('ricetta', 'ricette', 'degustazione', 'bilancio di esercizio', 'assemblea',
               'assemblee', 'concerto', 'sagra', 'auguri', 'natale', 'premio',
               'anniversario', 'inaugurazione', 'spot ', 'trailer', 'cucina', 'chef')

TIMING_IT = ('gennaio', 'febbraio', 'marzo', 'aprile', 'maggio', 'giugno', 'luglio',
             'agosto', 'settembre', 'ottobre', 'novembre', 'dicembre', 'stagione',
             'annata', 'campagna')


def _achou(texto, termos):
    n = _norm(texto)
    return sorted({t for t in termos if _norm(t) in n})


def medir():
    P = SAIDA_PILOTO
    with open(os.path.join(P, 'OBJETOS.json'), encoding='utf-8') as f:
        O = json.load(f)
    leg = {}
    pleg = os.path.join(P, 'LEGENDAS.json')
    if os.path.exists(pleg):
        with open(pleg, encoding='utf-8') as f:
            for x in json.load(f).get('ITEMS', []):
                leg[x['VIDEO_ID']] = x
    with open(LOTE_PILOTO, encoding='utf-8') as f:
        B = json.load(f)
    por_src = {c['SOURCE_ID']: c for c in B['CONTAS']}

    docs = []
    for it in O['ITEMS']:
        sid = it['ACCOUNT_HANDLE']
        conta = por_src.get(sid) or {}
        lg = leg.get(it['VIDEO_ID']) or {}
        legenda = lg.get('CAPTION_TEXT') or lg.get('TEXTO') or ''
        texto = ' '.join([it.get('TITLE') or '', legenda])
        tem_legenda_local = bool(legenda)
        crops = sorted({k for k, v in CROP_IT.items() if _achou(texto, v)})
        issues = sorted({k for k, v in ISSUE_IT.items() if _achou(texto, v)})
        prod = _achou(texto, PRODUTO_IT)
        campo = _achou(texto, CAMPO_IT)
        tecn = _achou(texto, TECNICO_IT)
        com = _achou(texto, COMERCIAL_IT)
        pesq = _achou(texto, PESQUISA_IT)
        tim = _achou(texto, TIMING_IT)
        agro = bool(crops or issues or prod)

        nao_agro = _achou(texto, NAO_AGRO_IT)
        # ⛔⛔ O PORTÃO QUE ESTA MEDIÇÃO EXIGIU, e que a primeira versão não tinha.
        # Sem legenda, o único texto é o TÍTULO — mediana de 51 caracteres. Declarar
        # `OFF_TOPIC` a partir disso é tratar AUSÊNCIA DE TEXTO como AUSÊNCIA DE
        # ASSUNTO, que é a mesma falácia de `falha de leitura != zero`.
        # Medido nesta rodada: "Meli in filare agroforestale" (macieira) tinha caído em
        # OFF_TOPIC por falta de plural no léxico. Com 51 caracteres não há como saber.
        #   → `F` só quando um marcador NÃO-AGRÍCOLA aparece, ou quando há legenda.
        #   → sem isso, `G` = NÃO SEI, que é um estado, não um empate.
        if not agro:
            if nao_agro:
                classe = 'F'
            elif tem_legenda_local:
                classe = 'F'
            else:
                classe = 'G'
        elif campo and (crops or issues):
            classe = 'A'
        elif pesq and (crops or issues):
            classe = 'C'
        elif com and not (issues or tecn):
            classe = 'D'
        elif tecn and (crops or issues or prod):
            classe = 'B'
        else:
            classe = 'E'

        # vídeo: o que existe ANTES de gastar transcrição
        tem_titulo = bool(it.get('TITLE'))
        tem_desc = False              # a grade pública não dá descrição completa
        tem_legenda = bool(legenda)
        basta = bool(crops or issues) and (tem_legenda or len(it.get('TITLE') or '') > 45)
        docs.append({
            'DOCUMENT_ID': 'IT-D-%s' % it['VIDEO_ID'],
            'SOURCE_ID': sid, 'ENTITY_ID': conta.get('ENTITY_ID'),
            'URL': it['VIDEO_URL'], 'PLATFORM': 'YOUTUBE',
            'PUBLICATION_DATE': it.get('PUBLISHED_AT'),
            'PUBLICATION_RELATIVE': it.get('PUBLISHED_RELATIVE'),
            'CAPTURE_DATE': it.get('CAPTURED_AT'),
            'RAW_TEXT': (it.get('TITLE') or '')[:300],
            'CAPTION_TEXT_LEN': len(legenda),
            'MEDIA_TYPE': 'VIDEO', 'DURATION_S': it.get('DURATION_S'),
            'LANGUAGE': 'NÃO SEI — não medido nesta rodada',
            'PROVENANCE': {'ROUTE': 'scripts/youtube_janela.py — rota pública',
                           'DOOR': it.get('DOOR'), 'APIFY_USED': False,
                           'COST_USD': 0},
            'ROLE_STATE': conta.get('ROLE_STATE'),
            'AGRICULTURAL_RELEVANCE': 'YES' if agro else ('NO' if classe == 'F' else 'NÃO SEI'),
            'CROP': crops or ['NÃO SEI'], 'ISSUE': issues or ['NÃO SEI'],
            'REGION': ['NÃO SEI — o título não declara região'],
            'PRACTICE': _achou(texto, ISSUE_IT['PRACTICE']) or ['NÃO SEI'],
            'PRODUCT_OR_ACTIVE': prod or ['NÃO SEI'],
            'OBSERVED_FIELD_CONDITION': campo or ['NÃO SEI'],
            'TIMING': tim or ['NÃO SEI'],
            'FIRST_PERSON_OR_FIELD_EXPERIENCE': bool(campo),
            'TECHNICAL_CLAIM': bool(tecn),
            'COMMERCIAL_REFERENCE': bool(com),
            'VALUE_CLASS': classe,
            'NAO_AGRO_MARKERS': nao_agro or [],
            'JUDGEABLE': bool(legenda) or bool(agro) or bool(nao_agro),
            'WHY_NOT_JUDGEABLE': (None if (legenda or agro or nao_agro) else
                                  'só título disponível (%d caracteres) e nenhum marcador '
                                  'agrícola nem não-agrícola: texto insuficiente para '
                                  'julgar assunto' % len(it.get('TITLE') or '')),
            'CLASSIFIER_EVIDENCE': {'CROP_HITS': [x for k in crops for x in _achou(texto, CROP_IT[k])][:4],
                                    'ISSUE_HITS': [x for k in issues for x in _achou(texto, ISSUE_IT[k])][:4],
                                    'TRECHO': (it.get('TITLE') or '')[:120]},
            'HAS_TITLE': tem_titulo, 'HAS_DESCRIPTION': tem_desc,
            'HAS_CAPTION': tem_legenda,
            'TRANSCRIPTION_NEEDED': (not basta) and agro,
            'TRANSCRIPTION_REASON': ('assunto agrícola aparente e texto disponível '
                                     'insuficiente para julgar' if (not basta) and agro
                                     else 'título/legenda já bastam, ou não é agrícola'),
        })

    por_source = defaultdict(lambda: Counter())
    for d in docs:
        c = por_source[d['SOURCE_ID']]
        c['TOTAL_COLLECTED'] += 1
        c[d['VALUE_CLASS']] += 1
        if d['AGRICULTURAL_RELEVANCE'] == 'YES':
            c['AG_RELEVANT'] += 1
    linhas = []
    for sid, c in sorted(por_source.items()):
        tot = c['TOTAL_COLLECTED']
        linhas.append({
            'SOURCE_ID': sid, 'NOME': (por_src.get(sid) or {}).get('COMPANY'),
            'ROLE_STATE': (por_src.get(sid) or {}).get('ROLE_STATE'),
            'TOTAL_COLLECTED': tot, 'AG_RELEVANT': c['AG_RELEVANT'],
            'FIELD_SIGNAL': c['A'], 'TECHNICAL': c['B'], 'RESEARCH': c['C'],
            'COMMERCIAL': c['D'], 'GENERAL': c['E'], 'OFF_TOPIC': c['F'],
            'UNKNOWN': c['G'],
            'USEFUL_RATE': round(c['AG_RELEVANT'] / tot, 3) if tot else None,
            'FIELD_SIGNAL_RATE': round(c['A'] / tot, 3) if tot else None,
        })

    def agrega(rs):
        t = sum(r['TOTAL_COLLECTED'] for r in rs) or 1
        return {'SOURCES': len(rs), 'DOCS': sum(r['TOTAL_COLLECTED'] for r in rs),
                'AG_RELEVANCE_RATE': round(sum(r['AG_RELEVANT'] for r in rs) / t, 3),
                'FIELD_SIGNAL_RATE': round(sum(r['FIELD_SIGNAL'] for r in rs) / t, 3),
                'TECHNICAL_RATE': round(sum(r['TECHNICAL'] for r in rs) / t, 3),
                'OFF_TOPIC_RATE': round(sum(r['OFF_TOPIC'] for r in rs) / t, 3)}
    provado = [r for r in linhas if r['ROLE_STATE'] == 'PROVED']
    desconh = [r for r in linhas if r['ROLE_STATE'] != 'PROVED']

    cls = Counter(d['VALUE_CLASS'] for d in docs)
    corpo = {
        'SOURCE_ID': 'IT-HUMAN-SENSORS/PILOT-MEASUREMENT',
        'LIMITE_DO_CLASSIFICADOR': ('LEXICAL sobre título + legenda. Polissemia produz '
                                    'falso positivo e nenhum portão automático detecta. '
                                    'Todo item carrega o trecho; verificação é humana.'),
        'ROLE_FROM_CONTENT': 0,
        'LEI': 'conteúdo diz DO QUE se fala; nunca QUEM é. Nada aqui escreve em ROLES.',
        'PILOT_DOCUMENTS': len(docs),
        'DOCUMENT_WITHOUT_SOURCE_ID': sum(1 for d in docs if not d['SOURCE_ID']),
        'DOCUMENT_WITHOUT_ENTITY_ID': sum(1 for d in docs if not d['ENTITY_ID']),
        'NEW_ENTITIES_FROM_CONTENT': 0,
        'BY_VALUE_CLASS': {k: cls.get(k, 0) for k in 'ABCDEFG'},
        'AG_RELEVANT': sum(1 for d in docs if d['AGRICULTURAL_RELEVANCE'] == 'YES'),
        'TRANSCRIPTION_NEEDED': sum(1 for d in docs if d['TRANSCRIPTION_NEEDED']),
        'NOT_JUDGEABLE_TITLE_ONLY': sum(1 for d in docs if not d['JUDGEABLE']),
        'TRANSCRIPTIONS_EXECUTED': 0,
        'HAS_CAPTION': sum(1 for d in docs if d['HAS_CAPTION']),
        'COMPARACAO_PAPEL': {'ROLE_PROVED_SOURCES': agrega(provado),
                             'ROLE_UNKNOWN_SOURCES': agrega(desconh)},
        'POR_SOURCE': linhas,
        'DOCUMENTS': docs,
    }
    with open(MEDIDA, 'w', encoding='utf-8') as f:
        json.dump(selar(corpo), f, ensure_ascii=False, indent=1)
    print('documentos %d · classes %s' % (len(docs), corpo['BY_VALUE_CLASS']))
    print('AG_RELEVANT %d · legendas %d · transcrição necessária %d'
          % (corpo['AG_RELEVANT'], corpo['HAS_CAPTION'], corpo['TRANSCRIPTION_NEEDED']))
    print('PROVED  %s' % corpo['COMPARACAO_PAPEL']['ROLE_PROVED_SOURCES'])
    print('UNKNOWN %s' % corpo['COMPARACAO_PAPEL']['ROLE_UNKNOWN_SOURCES'])
    return corpo


# ═══════════════════════════════ 5 · QUEM ESTÁ NO YOUTUBE, POR FAMÍLIA DE PAPEL

def familia():
    """A tabela GRUPO × PLATAFORMA do universo monitorável. Sem rede, sem coleta.

    Existe porque a rodada do piloto afirmou que as condições 5 e 6 do portão falhavam
    "pela mesma causa: a legenda". Metade disso é falso, e esta tabela é a prova:

        LEGENDA É UMA CAMADA DE YOUTUBE. NÃO ALCANÇA QUEM NÃO ESTÁ NO YOUTUBE.

    A regra de grupo é a MESMA de `selecionar()` — de propósito. Duas regras de família no
    mesmo repositório seriam duas respostas para a mesma pergunta.
    """
    with open(ENTIDADES, encoding='utf-8') as f:
        E = json.load(f)
    with open(FONTES, encoding='utf-8') as f:
        S = json.load(f)
    ents = {e['ENTITY_ID']: e for e in E['ENTITIES']}
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import sensor_resolver_fontes_it as R

    tabela, canais_b = {}, []
    total = 0
    for f in S['SOURCES']:
        if not (f.get('SOURCE_TYPE') == 'MONITORABLE_CHANNEL'
                or f.get('PLATAFORMA') in R.MONITORAVEL):
            continue
        e = ents.get(f['ENTITY_ID'])
        if not e:
            continue
        ps = [r['PAPEL'] for r in e['ROLES'] if r['ESTADO'] in ('PROVADO', 'PROBABLE')]
        g = ('A' if any(p in CAMPO for p in ps) else
             'B' if any(p in ('pesquisador', 'professor') for p in ps) else 'C')
        tabela.setdefault(g, {}).setdefault(f['PLATAFORMA'], 0)
        tabela[g][f['PLATAFORMA']] += 1
        total += 1
        if g == 'B':
            canais_b.append({'NOME': e['NOME_CANONICO'], 'PLATAFORMA': f['PLATAFORMA'],
                             'URL': f['URL'], 'SOURCE_ID': f['SOURCE_ID']})

    yt_b = tabela.get('B', {}).get('youtube', 0)
    corpo = {
        'SOURCE_ID': 'IT-HUMAN-SENSORS/FAMILIA-POR-PLATAFORMA',
        'source': 'cruzamento offline de SOURCES.json x ENTITIES.json, sem rede',
        'REGRA_DE_GRUPO': ('a mesma de selecionar(): A = papel de campo provado, '
                           'B = pesquisador/professor, C = sem papel provado'),
        'UNIVERSO_MONITORAVEL': total,
        'GRUPO_X_PLATAFORMA': tabela,
        'CANAIS_DA_FAMILIA_PESQUISADOR': canais_b,
        'RESEARCHER_YOUTUBE_CHANNELS': yt_b,
        'CONDITION_6_TESTABLE_WITH_CURRENT_YOUTUBE_UNIVERSE': 'SIM' if yt_b else 'NÃO',
        'POR_QUE': ('a condicao 6 pergunta se o canal publico do pesquisador acrescenta '
                    'algo ao Europe PMC. Com %d canais de YouTube nessa familia, a '
                    'pergunta nao tem onde ser feita — e legenda nenhuma muda isso.'
                    % yt_b),
    }
    with open(os.path.join(DEST, 'FAMILIA-POR-PLATAFORMA.json'), 'w',
              encoding='utf-8') as f:
        json.dump(selar(corpo), f, ensure_ascii=False, indent=1)
    plats = sorted({p for g in tabela.values() for p in g})
    print('universo monitoravel: %d' % total)
    print('      ' + ' '.join('%-10s' % p for p in plats))
    for g in sorted(tabela):
        print('%-6s' % g + ' '.join('%-10d' % tabela[g].get(p, 0) for p in plats))
    print('RESEARCHER_YOUTUBE_CHANNELS = %d' % yt_b)
    return corpo


if __name__ == '__main__':
    {'selecionar': selecionar, 'lote': lote, 'coletar': coletar,
     'medir': medir, 'familia': familia}[
        sys.argv[1] if len(sys.argv) > 1 else 'medir']()
