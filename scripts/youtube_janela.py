#!/usr/bin/env python3
"""
YOUTUBE PELA JANELA — tudo o que a rota pública entrega antes de gastar um centavo.

    py scripts/youtube_janela.py canais      # nome, inscritos, descrição, a grade
    py scripts/youtube_janela.py objetos     # título, duração, views, data, videoId
    py scripts/youtube_janela.py legendas    # a LEGENDA, que é a transcrição de graça
    py scripts/youtube_janela.py tudo        # os três, na ordem

A ORDEM É LEI, E ELA VEM DA MISSÃO 14
---------------------------------------
    LOTE CONGELADO → CANAL → OBJETO → LEGENDA → (só então) WHISPER → (só então) PAGO

Este arquivo NÃO decide quem entra: ele obedece a
`data/samples/COMPETITOR-PUBLIC-COMM/PUBLIC-COMM-FIRST-BATCH-EAME.json` e só toca conta
com `PLATFORM = YOUTUBE`. São 7 — duas a mais que as 5 do Instagram.

O QUE FOI MEDIDO EM 2026-09-03, E QUE JUSTIFICA O ARQUIVO INTEIRO
-------------------------------------------------------------------
Contra `@BayerAgri`, deslogado, sem chave de API:

    pagina do canal /videos ....... HTTP 200, 30 videos na PRIMEIRA pagina
    oembed ........................ HTTP 200
    pagina do video /watch ........ HTTP 429 + CAPTCHA  (de IP de datacenter)
    timedtext sem assinatura ...... HTTP 200, CORPO VAZIO

Da página do canal saíram, de graça: `videoId`, título, duração, visualizações e
data relativa. Trinta por página, contra os DOZE do muro do Instagram — e com
`continuation`, que o Instagram não dá.

    O YOUTUBE É MAIS BARATO QUE O INSTAGRAM, NÃO MAIS CARO.

O 429 NÃO É "O YOUTUBE FECHOU"
--------------------------------
Ele foi medido de um IP de datacenter. A página do canal passou do MESMO IP, no
MESMO segundo — se fosse bloqueio de conteúdo, as duas teriam caído. É reputação
de rede, e por isso a camada `legendas` usa o navegador de verdade desta máquina,
pelo `cdp`, e não `urllib`.

    HTTP 429 DE UM IP != PÁGINA FECHADA PARA TODOS.

Quem confundir os dois vai registrar `SEM_LEGENDA` num vídeo legendado, e mandar o
whisper transcrever seis horas de som que já existia escrito.

A LEGENDA É A ECONOMIA INTEIRA
--------------------------------
`instagram_transcrever.py` mediu `small` a 3,2x nesta máquina: ~6 h para mil vídeos.
Legenda automática do YouTube custa ZERO segundo de máquina e já vem com tempos.
Por isso `legendas` roda ANTES de qualquer whisper, e o whisper só vê o que sobrou.

O QUE ESTE ARQUIVO NÃO FAZ
----------------------------
Não classifica assunto, não decide se a fonte é relevante — quem faz isso é
`youtube_relevancia.py`, de graça e depois. Não baixa vídeo. Não loga em nada, não
resolve CAPTCHA, não toca em sessão nem em cookie de conta.
"""
import json
import os
import re
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import cdp                       # noqa: E402  — o navegador, em biblioteca padrão

SAMPLES = os.path.join(ROOT, 'data', 'samples')
SAIDA = os.path.join(SAMPLES, 'YOUTUBE-JANELA')
BRUTO = os.path.join(SAIDA, 'html-bruto')
# ⚠️ QUAL LOTE, E POR QUE ISSO E' UMA VARIAVEL E NAO UMA CONSTANTE
# ------------------------------------------------------------------
# Ate 2026-09-03 este caminho era fixo no lote de COMUNICACAO PUBLICA DO
# CONCORRENTE — 22 contas de Bayer, Syngenta, Corteva e Nufarm. Ele responde
# "o que o concorrente publica", que e' uma pergunta legitima e NAO e' a
# pergunta desta missao.
#
# O alvo desta casa e' a ITALIA TECNICA: agronomo, tecnico, pesquisador, gente
# do manejo dos produtos. Um arquivo que so' sabe ler um universo obriga quem
# muda de pergunta a editar codigo — e editar codigo para trocar de universo e'
# como a coleta errada acontece sem ninguem notar.
#
#     O UNIVERSO E' ENTRADA DA COLETA, NAO PARTE DELA.
#
# `YT_LOTE` nomeia o arquivo. O padrao continua sendo o do concorrente para nao
# mudar em silencio o que ja rodava.
LOTE = os.environ.get('YT_LOTE') or os.path.join(
    SAMPLES, 'COMPETITOR-PUBLIC-COMM', 'PUBLIC-COMM-FIRST-BATCH-EAME.json')

# O nome do universo entra no artefato. Sem isto, dois CANAIS.json de universos
# diferentes ficam identicos por fora, e a unica forma de saber qual e' qual e'
# lembrar o que foi despachado — que e' exatamente o que ninguem lembra.
UNIVERSO = os.path.basename(os.path.dirname(LOTE))

MISSION = '14-COMUNICACAO-PUBLICA-DO-CONCORRENTE'
RUNNER = os.environ.get('RUNNER_NAME') or 'NOT_KNOWN'
NAO_SEI = 'NOT_KNOWN'
PORTA = int(os.environ.get('YT_PORTA') or 9223)
PERFIL = os.environ.get('YT_PERFIL') or os.path.join(
    os.path.expanduser('~'), '.sintonia-browser', 'yt')

UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36')

# Teto de páginas por canal. Não é gosto: cada `continuation` é uma requisição, e o
# muro real do YouTube é a paciência da rede, não um número publicado. 8 páginas são
# ~240 vídeos, mais do que qualquer conta institucional do lote publicou em 2 anos.
TETO_PAGINAS = int(os.environ.get('YT_PAGINAS') or 8)


def agora():
    import datetime
    return datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def hoje():
    import datetime
    return datetime.date.today().isoformat()


def _gravar(nome, corpo):
    os.makedirs(SAIDA, exist_ok=True)
    with open(os.path.join(SAIDA, nome), 'w', encoding='utf-8') as f:
        json.dump(corpo, f, ensure_ascii=False, indent=1)
    return 'data/samples/YOUTUBE-JANELA/' + nome


def _ler(nome):
    p = os.path.join(SAIDA, nome)
    if not os.path.exists(p):
        return None
    with open(p, encoding='utf-8') as f:
        return json.load(f)


def _slug(s):
    return re.sub(r'[^A-Za-z0-9._-]+', '-', str(s))[:80].strip('-') or 'sem-nome'


def _guardar_html(nome, html):
    """O HTML cru, ANTES de normalizar. Mesma lei da rota paga, na rota grátis.

    Sem isto, um erro de leitor obrigaria a abrir a página de novo — e a página de
    amanhã não é a de hoje.
    """
    import gzip
    os.makedirs(BRUTO, exist_ok=True)
    caminho = os.path.join(BRUTO, nome + '.html.gz')
    with gzip.open(caminho, 'wt', encoding='utf-8', compresslevel=9) as f:
        f.write(html)
    return 'data/samples/YOUTUBE-JANELA/html-bruto/' + nome + '.html.gz'


# ══════════════════════════════════════════════════ O LOTE, QUE MANDA NESTE ARQUIVO

def contas():
    """As contas de YouTube do LOTE CONGELADO. Este arquivo obedece, não escolhe."""
    if not os.path.exists(LOTE):
        raise SystemExit(
            'lote ausente: %s\n'
            'A coleta não improvisa a lista: ela obedece a uma lista datada.' % LOTE)
    with open(LOTE, encoding='utf-8') as f:
        d = json.load(f)
    achadas = []

    def anda(o):
        if isinstance(o, dict):
            if o.get('PLATFORM') == 'YOUTUBE' and (o.get('ACCOUNT_URL') or o.get('URL')):
                achadas.append(o)
            for v in o.values():
                anda(v)
        elif isinstance(o, list):
            for v in o:
                anda(v)

    anda(d)
    return achadas


def _url_videos(conta):
    """A aba /videos do canal, a partir do endereço que o lote registrou.

    O lote traz três formatos vivos — `/@handle`, `/c/Nome`, `/user/nome` — porque
    foram registrados em épocas diferentes do YouTube. Os três continuam resolvendo.
    """
    u = (conta.get('ACCOUNT_URL') or conta.get('URL') or '').strip().rstrip('/')
    if not u:
        return None
    if not u.startswith('http'):
        u = 'https://www.youtube.com/' + u.lstrip('/')
    u = u.replace('://youtube.com', '://www.youtube.com')
    return u + '/videos'


# ══════════════════════════════════════════════════════ LEITURA DO ytInitialData

def _json_embutido(html, marcador):
    """Extrai o JSON que o YouTube embute no HTML, contando chaves.

    Regex com `.*?}` quebra aqui: o objeto tem chaves dentro de strings, e a primeira
    `};` do arquivo quase nunca é o fim do objeto. Contar profundidade custa o mesmo
    e não erra — e o erro dessa classe é silencioso, que é o pior tipo.
    """
    i = html.find(marcador)
    if i < 0:
        return None
    i = html.find('{', i)
    if i < 0:
        return None
    prof, dentro, escapa = 0, False, False
    for j in range(i, len(html)):
        c = html[j]
        if escapa:
            escapa = False
            continue
        if c == '\\':
            escapa = True
            continue
        if c == '"':
            dentro = not dentro
            continue
        if dentro:
            continue
        if c == '{':
            prof += 1
        elif c == '}':
            prof -= 1
            if prof == 0:
                try:
                    return json.loads(html[i:j + 1])
                except Exception:
                    return None
    return None


def _colher(o, chave, acc):
    if isinstance(o, dict):
        if chave in o:
            acc.append(o[chave])
        for v in o.values():
            _colher(v, chave, acc)
    elif isinstance(o, list):
        for v in o:
            _colher(v, chave, acc)
    return acc


def _textos(o, acc):
    """Todo `content` de texto que um viewModel carrega, na ordem em que aparece."""
    if isinstance(o, dict):
        if isinstance(o.get('content'), str):
            acc.append(o['content'])
        for v in o.values():
            _textos(v, acc)
    elif isinstance(o, list):
        for v in o:
            _textos(v, acc)
    return acc


def _segundos(txt):
    """'2:50' -> 170. '1:03:12' -> 3792. O que não for duração vira NOT_KNOWN."""
    if not txt:
        return NAO_SEI
    partes = str(txt).strip().split(':')
    if not all(p.isdigit() for p in partes) or not 1 < len(partes) <= 3:
        return NAO_SEI
    s = 0
    for p in partes:
        s = s * 60 + int(p)
    return s


# Sufixos de abreviação, nos idiomas do lote. `K` e `M` valem nos três.
SUFIXOS = {'k': 1000, 'm': 1000000, 'mil': 1000, 'mio': 1000000, 'mln': 1000000}


def _quantidade(txt):
    """'342 visualizaciones' -> (342, True). '1,76 K suscriptores' -> (1760, False).

    ⚠️ O SEGUNDO ELEMENTO É SE O NÚMERO É EXATO, E ELE EXISTE POR UM ERRO MEDIDO.
    A primeira versão deste leitor jogava fora tudo que não fosse dígito. Em
    2026-09-03, contra o lote real:

        '1,76 K suscriptores'  ->  176      (é 1.760)
        '6,81 K suscriptores'  ->  681      (é 6.810)

    Dez vezes menos, em silêncio, num campo que ninguém reconfere porque PARECE um
    número. E a vírgula não é enfeite: em ES/IT/FR ela é o separador DECIMAL e o
    ponto é o de milhar — ao contrário do inglês.

        NÚMERO ERRADO NÃO SE DENUNCIA. ELE SÓ FICA LÁ, PARECENDO CERTO.

    Quando a fonte abrevia, o valor volta arredondado PELA PRÓPRIA FONTE: '1,76 K'
    tanto pode ser 1.755 quanto 1.764. Por isso `exato=False` viaja junto — quem
    for comparar dois canais precisa saber que a régua tem casas escondidas.
    """
    if not txt:
        return NAO_SEI, False
    t = str(txt).replace(' ', ' ').replace('\xa0', ' ').strip()
    m = re.search(r'(\d[\d.,\s]*)\s*([A-Za-zÀ-ÿ]*)', t)
    if not m:
        return NAO_SEI, False
    cru, sufixo = m.group(1).strip(), (m.group(2) or '').lower()
    fator = SUFIXOS.get(sufixo)
    if fator:
        # Com sufixo a vírgula é DECIMAL ('1,76 K'); o ponto aparece no mesmo papel
        # em superfícies em inglês ('1.76K'). Os dois querem dizer a mesma coisa.
        n = cru.replace(' ', '').replace(',', '.')
        try:
            return int(round(float(n) * fator)), False
        except ValueError:
            return NAO_SEI, False
    # Sem sufixo, ponto e vírgula são separadores de MILHAR: '1.760', '1 760'.
    d = re.sub(r'[^\d]', '', cru)
    return (int(d), True) if d else (NAO_SEI, False)


def _inteiro(txt):
    """Só o valor, para quem não precisa saber se ele é exato."""
    return _quantidade(txt)[0]


def _videos_do_html(html):
    """Os vídeos da grade, no formato `lockupViewModel` que o YouTube usa hoje.

    O formato ANTIGO era `videoRenderer`. Um leitor que só conheça o antigo devolve
    ZERO e parece que o canal não tem vídeo — medido em 2026-09-03, foi exatamente o
    que aconteceu comigo. Os dois ficam aceitos: o antigo ainda aparece em algumas
    superfícies, e aceitar os dois custa uma função.
    """
    d = _json_embutido(html, 'ytInitialData')
    if not d:
        return [], 'YTINITIALDATA_AUSENTE'
    saida, vistos = [], set()

    for v in _colher(d, 'lockupViewModel', []):
        vid = v.get('contentId')
        if not vid or vid in vistos or v.get('contentType') not in (
                None, 'LOCKUP_CONTENT_TYPE_VIDEO'):
            continue
        vistos.add(vid)
        dur = ''
        for b in _colher(v.get('contentImage', {}), 'thumbnailBadgeViewModel', []):
            if b.get('text') and not dur:
                dur = b['text']
        meta = _textos(v.get('metadata', {}), [])
        saida.append({
            'VIDEO_ID': vid,
            'VIDEO_URL': 'https://www.youtube.com/watch?v=' + vid,
            'TITLE': meta[0] if meta else NAO_SEI,
            'DURATION_TEXT': dur or NAO_SEI,
            'DURATION_S': _segundos(dur),
            'VIEWS_TEXT': meta[1] if len(meta) > 1 else NAO_SEI,
            'VIEWS': _inteiro(meta[1]) if len(meta) > 1 else NAO_SEI,
            'PUBLISHED_RELATIVE': meta[2] if len(meta) > 2 else NAO_SEI,
            'PUBLISHED_AT': NAO_SEI,
            'PUBLISHED_AT_POR_QUE': ('a grade do canal só dá data RELATIVA ("hace 3 '
                                     'años"). Data exata existe na página do vídeo, '
                                     'e é a camada `legendas` que a traz.'),
            'RENDERER': 'lockupViewModel',
        })

    for v in _colher(d, 'videoRenderer', []):
        vid = v.get('videoId')
        if not vid or vid in vistos:
            continue
        vistos.add(vid)
        titulo = ''.join(r.get('text', '') for r in
                         (v.get('title', {}).get('runs') or []))
        dur = (v.get('lengthText') or {}).get('simpleText', '')
        views = (v.get('viewCountText') or {}).get('simpleText', '')
        saida.append({
            'VIDEO_ID': vid,
            'VIDEO_URL': 'https://www.youtube.com/watch?v=' + vid,
            'TITLE': titulo or NAO_SEI,
            'DURATION_TEXT': dur or NAO_SEI,
            'DURATION_S': _segundos(dur),
            'VIEWS_TEXT': views or NAO_SEI,
            'VIEWS': _inteiro(views),
            'PUBLISHED_RELATIVE': (v.get('publishedTimeText') or {}).get(
                'simpleText', NAO_SEI),
            'PUBLISHED_AT': NAO_SEI,
            'RENDERER': 'videoRenderer',
        })
    return saida, ('OK' if saida else 'GRADE_VAZIA')


def _canal_do_html(html):
    d = _json_embutido(html, 'ytInitialData')
    if not d:
        return {}
    meta = (_colher(d, 'channelMetadataRenderer', []) or [{}])[0]
    micro = (_colher(d, 'microformatDataRenderer', []) or [{}])[0]
    inscritos = NAO_SEI
    for p in _colher(d, 'pageHeaderViewModel', []):
        for t in _textos(p, []):
            if re.search(r'(suscriptor|iscritt|abonn|subscriber)', t, re.I):
                inscritos = t
                break
    return {
        'CHANNEL_TITLE': meta.get('title') or micro.get('title') or NAO_SEI,
        'CHANNEL_ID': meta.get('externalId') or NAO_SEI,
        'DESCRIPTION': meta.get('description') or micro.get('description') or NAO_SEI,
        'SUBSCRIBERS_TEXT': inscritos,
        'SUBSCRIBERS': _quantidade(inscritos)[0] if inscritos != NAO_SEI else NAO_SEI,
        'SUBSCRIBERS_EXATO': _quantidade(inscritos)[1] if inscritos != NAO_SEI else False,
        'CANONICAL_URL': meta.get('channelUrl') or NAO_SEI,
    }


# ══════════════════════════════════════════════════════════ AS DUAS PORTAS DE REDE

def _por_urllib(url):
    """A porta barata. Serve para a página do CANAL, que foi medida passando."""
    req = urllib.request.Request(url, headers={
        'User-Agent': UA,
        'Accept-Language': 'es-ES,es;q=0.9,it;q=0.8,fr;q=0.7',
        'Cookie': 'SOCS=CAI',
    })
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode('utf-8', 'replace')


def _bloqueado(html):
    """O CAPTCHA do Google devolve 200 com corpo de gente, e engana quem só olha o código."""
    if not html or len(html) < 6000:
        return True
    return 'captcha-form' in html or 'ytInitialData' not in html


def _abrir(url, *, navegador_primeiro=False, espera=5):
    """→ (html, PORTA_USADA, MOTIVO). urllib primeiro; navegador quando ela não serve.

    Ordem invertida para a página do vídeo, que já foi medida caindo em 429 pela rota
    barata. Tentar a barata lá seria pagar a espera para levar o mesmo bloqueio.
    """
    if not navegador_primeiro:
        try:
            html = _por_urllib(url)
            if not _bloqueado(html):
                return html, 'URLLIB', 'OK'
        except Exception as e:
            pass
    try:
        cdp.subir(PORTA, perfil=PERFIL)
        _aba, html = cdp.abrir(url, porta=PORTA, espera=espera)
        if _bloqueado(html):
            return html, 'NAVEGADOR', 'BLOQUEADO_TAMBEM_NO_NAVEGADOR'
        return html, 'NAVEGADOR', 'OK'
    except cdp.Erro as e:
        return None, 'NENHUMA', 'NAVEGADOR_NAO_ALCANCADO: %s' % str(e)[:120]


# ═══════════════════════════════════════════════════════════════ FASE · CANAIS

def fase_canais():
    cs = contas()
    print('canais no lote: %d' % len(cs))
    itens = []
    for c in cs:
        url = _url_videos(c)
        r = {'COMPANY': c.get('COMPANY', NAO_SEI),
             'ACCOUNT_HANDLE': c.get('ACCOUNT_HANDLE', NAO_SEI),
             'COUNTRY_SCOPE': c.get('COUNTRY_SCOPE', NAO_SEI),
             'ACCOUNT_URL': c.get('ACCOUNT_URL') or c.get('URL') or NAO_SEI,
             'CAPTURED_AT': agora(), 'MISSION': MISSION, 'RUNNER_NAME': RUNNER}
        if not url:
            r.update({'DOOR_STATE': 'SEM_ENDERECO', 'CHANNEL_TITLE': NAO_SEI})
            itens.append(r)
            print('  %-24s sem endereço no lote' % r['ACCOUNT_HANDLE'][:24])
            continue
        html, porta, motivo = _abrir(url)
        r['DOOR'] = porta
        r['DOOR_STATE'] = motivo
        if html:
            r['RAW_HTML_PATH'] = _guardar_html('canal-' + _slug(r['ACCOUNT_HANDLE']), html)
            r.update(_canal_do_html(html))
        itens.append(r)
        print('  %-24s %-10s %-28s inscritos=%s'
              % (str(r['ACCOUNT_HANDLE'])[:24], porta,
                 str(r.get('CHANNEL_TITLE', NAO_SEI))[:28], r.get('SUBSCRIBERS', NAO_SEI)))
    p = _gravar('CANAIS.json', {
        'SOURCE_ID': 'YOUTUBE-JANELA/CANAIS',
        'UNIVERSO': UNIVERSO,
        'LOTE_OBEDECIDO': LOTE.replace(ROOT + '/', ''),
        'source': 'rota pública do YouTube pelo navegador desta máquina — sem API, sem chave, sem custo',
        'SOURCE_LOCATION': 'youtube.com — páginas públicas de canal',
        'FACT_LOCATION': 'EAME',
        'ORIGINAL_LANGUAGE': 'multi',
        'EVIDENCE_CLASS': 'PUBLIC_FREE_ROUTE',
        'captured_at': hoje(),
        'CAPTURED_AT': agora(),
        'APIFY_RUNS': 0, 'COST_USD': 0,
        'MISSION': MISSION,
        'CANAIS': itens})
    print('gravado: %s' % p)
    return 0


# ═══════════════════════════════════════════════════════════════ FASE · OBJETOS

def fase_objetos(limite=None):
    canais = _ler('CANAIS.json')
    if not canais:
        print('sem CANAIS.json — rode `py scripts/youtube_janela.py canais` antes')
        return 1
    teto = int(limite) if limite else None
    itens = []
    for c in canais['CANAIS']:
        url = None
        u = c.get('ACCOUNT_URL')
        if u and u != NAO_SEI:
            url = _url_videos({'ACCOUNT_URL': u})
        if not url:
            continue
        html, porta, motivo = _abrir(url)
        if not html:
            print('  %-24s %s' % (str(c['ACCOUNT_HANDLE'])[:24], motivo))
            continue
        vids, estado = _videos_do_html(html)
        if teto:
            vids = vids[:teto]
        for v in vids:
            v.update({'ACCOUNT_HANDLE': c.get('ACCOUNT_HANDLE'),
                      'COMPANY': c.get('COMPANY'),
                      'COUNTRY_SCOPE': c.get('COUNTRY_SCOPE'),
                      'CAPTURED_AT': agora(), 'MISSION': MISSION,
                      'DOOR': porta,
                      'CAPTION_STATE': 'NOT_TESTED'})
        itens.extend(vids)
        print('  %-24s %-10s %-16s videos=%d'
              % (str(c['ACCOUNT_HANDLE'])[:24], porta, estado, len(vids)))
    p = _gravar('OBJETOS.json', {
        'SOURCE_ID': 'YOUTUBE-JANELA/OBJETOS',
        'UNIVERSO': UNIVERSO,
        'LOTE_OBEDECIDO': LOTE.replace(ROOT + '/', ''),
        'source': 'grade /videos de cada canal — rota pública, sem custo',
        'SOURCE_LOCATION': 'youtube.com — grade pública do canal',
        'FACT_LOCATION': 'EAME',
        'ORIGINAL_LANGUAGE': 'multi',
        'EVIDENCE_CLASS': 'PUBLIC_FREE_ROUTE',
        'captured_at': hoje(),
        'CAPTURED_AT': agora(),
        'APIFY_RUNS': 0, 'COST_USD': 0,
        'O_QUE_A_GRADE_NAO_DA': ('data exata e descrição completa. A grade dá data '
                                 'RELATIVA. Quem precisa do dia exato abre a página '
                                 'do vídeo — que é a camada `legendas`.'),
        'ITEMS': itens})
    print('gravado: %s · %d objetos' % (p, len(itens)))
    return 0


# ══════════════════════════════════════════════════════════════ FASE · LEGENDAS

def _timedtext(base_url):
    """Busca a legenda pela URL ASSINADA que o player entregou. Sem assinatura, 0 bytes."""
    url = base_url if 'fmt=' in base_url else base_url + '&fmt=json3'
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=45) as r:
        corpo = r.read().decode('utf-8', 'replace')
    if not corpo.strip():
        return None
    d = json.loads(corpo)
    trechos = []
    for e in d.get('events') or []:
        txt = ''.join(s.get('utf8', '') for s in (e.get('segs') or [])).strip()
        if txt:
            trechos.append({'T_MS': e.get('tStartMs'), 'DUR_MS': e.get('dDurationMs'),
                            'TEXTO': txt})
    return trechos or None


def fase_legendas(limite=None):
    objetos = _ler('OBJETOS.json')
    if not objetos:
        print('sem OBJETOS.json — rode `py scripts/youtube_janela.py objetos` antes')
        return 1
    alvos = objetos['ITEMS']
    if limite:
        alvos = alvos[:int(limite)]
    saida, com, sem, barrados = [], 0, 0, 0
    for v in alvos:
        r = {'VIDEO_ID': v['VIDEO_ID'], 'ACCOUNT_HANDLE': v.get('ACCOUNT_HANDLE'),
             'TITLE': v.get('TITLE'), 'CAPTURED_AT': agora(), 'MISSION': MISSION}
        # A pagina do video ja foi medida caindo em 429 pela rota barata: navegador primeiro.
        html, porta, motivo = _abrir(v['VIDEO_URL'], navegador_primeiro=True, espera=6)
        r['DOOR'] = porta
        if not html:
            r.update({'CAPTION_STATE': 'PORTA_NAO_ABRIU', 'POR_QUE': motivo})
            barrados += 1
            saida.append(r)
            continue
        pr = _json_embutido(html, 'ytInitialPlayerResponse')
        if not pr:
            r.update({'CAPTION_STATE': 'PLAYER_RESPONSE_AUSENTE',
                      'POR_QUE': 'a página abriu mas não trouxe o player — %s' % motivo})
            barrados += 1
            saida.append(r)
            continue
        det = pr.get('videoDetails') or {}
        micro = (pr.get('microformat') or {}).get('playerMicroformatRenderer') or {}
        r.update({
            'TITLE_EXATO': det.get('title', NAO_SEI),
            'DURATION_S': int(det['lengthSeconds']) if str(
                det.get('lengthSeconds', '')).isdigit() else NAO_SEI,
            'VIEWS': _inteiro(det.get('viewCount')),
            'PUBLISHED_AT': micro.get('publishDate', NAO_SEI),
            'DESCRIPTION': det.get('shortDescription', NAO_SEI),
            'CHANNEL_ID': det.get('channelId', NAO_SEI),
        })
        faixas = ((pr.get('captions') or {}).get(
            'playerCaptionsTracklistRenderer') or {}).get('captionTracks') or []
        r['CAPTION_TRACKS'] = [{
            'LANG': t.get('languageCode'),
            'KIND': t.get('kind', 'MANUAL'),
            'NAME': (t.get('name', {}).get('simpleText')
                     or (t.get('name', {}).get('runs') or [{}])[0].get('text', NAO_SEI)),
        } for t in faixas]
        if not faixas:
            r.update({'CAPTION_STATE': 'AUSENTE',
                      'POR_QUE': 'o player não declarou nenhuma faixa de legenda',
                      'WHISPER_CANDIDATO': True})
            sem += 1
            saida.append(r)
            continue
        try:
            trechos = _timedtext(faixas[0]['baseUrl'])
        except Exception as e:
            trechos = None
            r['TIMEDTEXT_ERRO'] = '%s: %s' % (type(e).__name__, str(e)[:110])
        if not trechos:
            r.update({'CAPTION_STATE': 'DECLARADA_MAS_VAZIA',
                      'POR_QUE': ('o player declarou faixa e o corpo veio vazio. Isso é '
                                  'diferente de AUSENTE: aqui a legenda EXISTE e não foi '
                                  'entregue — e um NOT_PRESERVED é confissão, não ausência.'),
                      'WHISPER_CANDIDATO': True})
            sem += 1
            saida.append(r)
            continue
        r.update({'CAPTION_STATE': 'PRESENTE',
                  'CAPTION_LANG': faixas[0].get('languageCode'),
                  'CAPTION_KIND': faixas[0].get('kind', 'MANUAL'),
                  'CAPTION_SEGMENTS': len(trechos),
                  'CAPTION_CHARS': sum(len(t['TEXTO']) for t in trechos),
                  'TRANSCRICAO': trechos,
                  'WHISPER_CANDIDATO': False,
                  'CUSTO_DE_MAQUINA_S': 0,
                  'POR_QUE': 'legenda pública lida de graça — o whisper não precisa rodar'})
        com += 1
        saida.append(r)
        print('  %-13s %-8s %s' % (r['VIDEO_ID'], r['CAPTION_STATE'],
                                   str(r.get('TITLE'))[:44]))
    p = _gravar('LEGENDAS.json', {
        'SOURCE_ID': 'YOUTUBE-JANELA/LEGENDAS',
        'source': 'legenda pública do YouTube, lida pelo navegador desta máquina',
        'SOURCE_LOCATION': 'youtube.com — página do vídeo e timedtext assinado',
        'FACT_LOCATION': 'EAME',
        'ORIGINAL_LANGUAGE': 'multi',
        'EVIDENCE_CLASS': 'PUBLIC_FREE_ROUTE',
        'captured_at': hoje(),
        'CAPTURED_AT': agora(),
        'APIFY_RUNS': 0, 'COST_USD': 0,
        'COM_LEGENDA': com, 'SEM_LEGENDA': sem, 'PORTA_NAO_ABRIU': barrados,
        'TRES_ESTADOS_DIFERENTES': (
            'PRESENTE = há texto. AUSENTE = o player disse que não há faixa. '
            'DECLARADA_MAS_VAZIA = há faixa e o corpo não veio. PORTA_NAO_ABRIU não é '
            'sobre o vídeo, é sobre a rede — e mandar o whisper por causa dele seria '
            'transcrever por causa de um 429.'),
        'ITEMS': saida})
    print('gravado: %s · com=%d sem=%d porta_fechada=%d' % (p, com, sem, barrados))
    return 0


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'canais'
    lim = sys.argv[2] if len(sys.argv) > 2 else None
    if cmd == 'canais':
        raise SystemExit(fase_canais())
    if cmd == 'objetos':
        raise SystemExit(fase_objetos(lim))
    if cmd == 'legendas':
        raise SystemExit(fase_legendas(lim))
    if cmd == 'tudo':
        raise SystemExit(fase_canais() or fase_objetos(lim) or fase_legendas(lim))
    print('uso: youtube_janela.py {canais|objetos|legendas|tudo} [limite]')
    raise SystemExit(2)
