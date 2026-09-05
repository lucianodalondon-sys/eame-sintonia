#!/usr/bin/env python3
"""
VIDEO ITALIA — a camada de vídeo do Sintonia, pela rota que esta máquina alcança.

    py scripts/it_video.py canais       # GRÁTIS · o que cada canal declara no feed
    py scripts/it_video.py fala         # GRÁTIS · baixa a fala dos vídeos da janela
    py scripts/it_video.py montar       # GRÁTIS · aplica voz.pipeline_video e grava
    py scripts/it_video.py tudo         # os três, na ordem

POR QUE ESTE ARQUIVO EXISTE, E POR QUE ELE NÃO É UM SCRAPER NOVO
------------------------------------------------------------------
O Sintonia Scrap já resolve Instagram: `instagram_janela.py` lê pelo navegador,
`instagram_transcrever.py` transcreve LOCALMENTE, e `sintonia-scrap.yml` despacha os dois.
Nada disso é reescrito aqui.

O que falta é a outra metade da regra de coleta externa, que põe **VÍDEO em primeiro lugar**
e manda começar pelo **YouTube**. Esta é essa metade — e ela usa o MESMO contrato de campos
(`voz.CAMPOS_VIDEO`, 32 campos) e o MESMO pipeline (`voz.pipeline_video`), porque um segundo
contrato seria uma segunda verdade.

    O MOTOR DE TRANSCRIÇÃO NÃO MUDA. O QUE MUDA É DE ONDE VEM O ÁUDIO.

AS DUAS ROTAS DE FALA, E POR QUE ELAS NÃO SE MISTURAM
-------------------------------------------------------
    SINTONIA_WHISPER_LOCAL   o áudio entra na máquina e o `faster-whisper` transcreve.
                             Medido nesta sessão: 118,7 min de áudio italiano, 8,6x–10,2x
                             tempo real, **0,00 USD**. É a transcrição DESTA casa.

    YOUTUBE_ASR_AUTO         a legenda automática do YouTube, servida por
                             `youtube.com/api/timedtext`. É a fala, e **não** é transcrição
                             nossa. Vem de terceiro, com os erros dele.

`CAPTION_SOURCE` existe no contrato exatamente para que ninguém confunda as duas depois.
Chamar ASR de terceiro de "transcrição Sintonia" seria a mesma classe de erro que contar
funcionário de empresa como canal da empresa.

POR QUE A ROTA LOCAL NÃO RODA NO YOUTUBE DESTA SESSÃO
-------------------------------------------------------
Medido em 2026-09-03: os METADADOS e as LEGENDAS vêm de `youtube.com` e respondem HTTP 200.
O BINÁRIO de áudio vem de `googlevideo.com` e a política de saída desta sessão devolve
**HTTP 403**.

    ROTA BLOQUEADA PARA ESTA SESSÃO ≠ ROTA INEXISTENTE.

Na máquina do runner, `IT_VIDEO_AUDIO=1` faz este arquivo baixar o áudio e chamar o mesmo
`faster-whisper` de `instagram_transcrever.py` — e o `CAPTION_SOURCE` passa a
`SINTONIA_WHISPER_LOCAL` sem que nada mais mude.

O QUE ESTE ARQUIVO NÃO FAZ
----------------------------
Não faz login, não passa credencial, não resolve CAPTCHA, não desliga verificação TLS, não
toca em conteúdo privado. Não decide o papel do canal a partir do vídeo — `DECLARED_ROLE`
vem da lista declarada abaixo, e um vídeo técnico num canal promocional continua sendo um
canal promocional.
"""
import json
import os
import re
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import voz  # noqa: E402

LIBS = os.environ.get('SINTONIA_LIBS') or os.path.join(os.path.expanduser('~'), '.sintonia-libs')
if os.path.isdir(LIBS):
    sys.path.insert(0, LIBS)

SAIDA = os.path.join(ROOT, 'data', 'samples', 'IT-VIDEO-V1')
FALAS = os.path.join(SAIDA, 'falas')
CAPTURA = os.environ.get('IT_VIDEO_DATA') or '2026-09-03'
RUN_ID = 'IT-VIDEO-' + CAPTURA
JANELA_DIAS = int(os.environ.get('IT_VIDEO_JANELA') or 90)
TETO = int(os.environ.get('IT_VIDEO_TETO') or 40)
UA = ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
      'Chrome/141.0.0.0 Safari/537.36')
NAO_SEI = voz.NAO_SEI


def C(cid, nome, papel, org, razao):
    """Um canal. `papel` é DECLARADO aqui, e nunca lido do conteúdo do vídeo."""
    return {'CHANNEL_ID': cid, 'CHANNEL_NAME': nome, 'DECLARED_ROLE': papel,
            'ORGANIZATION': org, 'ADAMA_RELEVANCE_REASON': razao, 'COUNTRY': 'IT'}


# ── OS CANAIS ──────────────────────────────────────────────────────────────────
# Entram por RELEVÂNCIA AO RADAR, nunca por audiência. Os canais de horticultura doméstica
# que o acervo canônico carrega (Passione Orto, Orto Da Coltivare, Piccoli Orti Grandi
# Raccolti, Your Hobby, Dall'Orto alla Tavola) e os que não são italianos (Cornell SIPS,
# INTA Chubut, Aragón TV, Laderas del Naranco) ficam FORA — e ficam registrados como fora,
# em `EXCLUIDOS`, porque exclusão silenciosa é indistinguível de esquecimento.
CANAIS = [
    C('UCktJyIUm3qJJpThrTa8nsHQ', 'AIPP — Associazione Italiana Protezione Piante',
      'SCIENTIFIC_SOCIETY', 'AIPP',
      'sociedade científica italiana da proteção das plantas — o próprio negócio da ADAMA'),
    C('UCWjrNnyRiWOtCM0zKUcsK5A', 'FMC Agro Italia', 'COMPANY', 'FMC',
      'comunicação técnica de concorrente em italiano, declarada no site da própria empresa'),
    C('UCoA303PgO9oOBWgZ3Nl5GvQ', 'Agrintesa', 'COOPERATIVE', 'Agrintesa Soc. Coop.',
      'cooperativa das pomáceas da Romagna — mesma área de OPP_20D89B04F64D e OPP_DA4B5954F72A'),
    C('UCJ8RdeFgPyGA8eyVHulEiOg', 'CREA', 'RESEARCH_INSTITUTION', 'CREA',
      'centro nacional de pesquisa agrícola italiano'),
    C('UCDNXhv9mPzYo5FQKkg_oSWw', 'UNIBO DISTAL', 'UNIVERSITY_DEPARTMENT', 'Università di Bologna',
      'a mesma universidade que opera a rede de trappole da cimice em big.csr.unibo.it'),
    C('@agraliastudio', 'Agralia Studio Agronomico', 'TECHNICAL_ADVISORY', 'Agralia s.r.l.',
      'estúdio agronômico privado que publica bollettino de vite na Lombardia'),
    C('@SIRFI-k9x', 'SIRFI', 'SCIENTIFIC_SOCIETY', 'SIRFI',
      'sociedade italiana de flora infestante — erbicidi são 26 dos 51 produtos ADAMA Italia'),
    C('@rinovaricerche', 'Ri.Nova', 'RESEARCH_COOPERATIVE', 'Ri.Nova soc. coop.',
      'coordena os Gruppi Operativi da Emilia-Romagna e alimenta a rede de trappole'),
    C('@fondazionemach', 'Fondazione Edmund Mach', 'RESEARCH_INSTITUTION', 'FEM',
      'o CTT assina os bollettini de difesa integrata do Trentino — melo e vite'),
    C('@Apofruit', 'Apofruit Italia', 'COOPERATIVE', 'Apofruit Italia Soc. Coop.',
      'uma das maiores OP de fruta da Itália; fragola e pomacee'),
    C('user/GowanItalia', 'Gowan Italia', 'COMPANY', 'Gowan Italia',
      'concorrente italiano ausente do acervo, com comunicação sobre difesa della vite'),
    C('user/TerremerseCoop', 'Terremerse', 'COOPERATIVE_DISTRIBUTOR', 'Terremerse Soc. Coop.',
      'cooperativa que também distribui agrofármaco nas culturas de maior peso de rótulo'),
    C('@myfruitvideo', 'Myfruit', 'TECHNICAL_MEDIA', 'Myfruit',
      'vídeo de ortofrutta italiana'),
    C('user/agronotizietv', 'AgroNotizie', 'TECHNICAL_MEDIA', 'Image Line s.r.l.',
      'principal mídia técnica agrícola italiana — a editora é Image Line s.r.l., '
      'em imagelinenetwork.com, e NÃO a image-line.com, que é a FL Studio'),
    C('@informatoreagrario', "L'Informatore Agrario", 'TECHNICAL_MEDIA', 'Edizioni L\'Informatore Agrario',
      'revista técnica agrícola italiana desde 1945'),
    C('@SyngentaItaly', 'Syngenta Italia', 'COMPANY', 'Syngenta',
      'concorrente; o site italiano recusa esta sessão com HTTP 403 e o canal não'),
    C('@BayerCropScienceIT', 'Bayer Crop Science Italia', 'COMPANY', 'Bayer',
      'idem — cropscience.bayer.it devolve 403 e o canal responde'),
    C('@UPLItalia', 'UPL Italia', 'COMPANY', 'UPL',
      'concorrente; upl-ltd.com/it devolveu HTTP 500 nesta sessão'),
    C('@EnteNazionaleRisi', 'Ente Nazionale Risi', 'PUBLIC_BODY', 'Ente Nazionale Risi',
      'riso e resistência de Echinochloa — liga a OPP_4C39CCC05EEB; enterisi.it hoje '
      'falha TLS com DH_KEY_TOO_SMALL e o canal responde'),
    C('@certiseuropeitalia4825', 'Certis Europe Italia', 'COMPANY', 'Certis Belchim',
      'concorrente cujo feed publica usi di emergenza'),
]

EXCLUIDOS = [
    {'CHANNEL': 'Passione Orto · Orto Da Coltivare · Piccoli Orti Grandi Raccolti · Your Hobby · '
                "Dall'Orto alla Tavola · ColtivoBio · Bosco di Ogigia · Sweety Farm",
     'REASON': 'HORTICULTURA_DOMESTICA — não observam cultura, alvo, molécula ou região do radar'},
    {'CHANNEL': 'Cornell SIPS · INTA Chubut · El campo es nuestro Aragón TV · Laderas del Naranco',
     'REASON': 'NOT_ITALIAN — estão no acervo canônico entre os 62 canais e não são italianos'},
    {'CHANNEL': 'Telenorba · Qdpnews · Rovigo IN Diretta · Milano Pavia TV · NOCI24',
     'REASON': 'MEDIA_GENERALISTA_LOCAL — cobrem agricultura por notícia, não por técnica. '
               'Não é rejeição definitiva: é fora do recorte desta passagem'},
]


def agora():
    import datetime
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + 'Z'


def _get(url, timeout=60):
    req = urllib.request.Request(url, headers={'User-Agent': UA,
                                               'Accept-Language': 'it-IT,it;q=0.9'})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read(), r.status


def _gravar(nome, corpo):
    os.makedirs(SAIDA, exist_ok=True)
    with open(os.path.join(SAIDA, nome), 'w', encoding='utf-8') as f:
        json.dump(corpo, f, ensure_ascii=False, indent=1)
    return os.path.join('data', 'samples', 'IT-VIDEO-V1', nome)


def _ler(nome):
    p = os.path.join(SAIDA, nome)
    if not os.path.exists(p):
        return None
    with open(p, encoding='utf-8') as f:
        return json.load(f)


# ── FASE 1 · CANAIS ────────────────────────────────────────────────────────────
def _feed_url(cid):
    """O feed do canal. Só o `channel_id` tem rota de XML; o handle precisa ser resolvido
    antes, e resolver handle exige ler a página — que é o que `fase_canais` faz."""
    if cid.startswith('UC'):
        return 'https://www.youtube.com/feeds/videos.xml?channel_id=' + cid
    return None


def _resolver_handle(cid):
    """@handle ou user/nome -> channel_id, lendo a página pública do canal.

    Handle não é identidade estável: o dono pode trocar. `channel_id` é. Guardar os dois e
    dizer qual resolveu qual é o que impede o acervo de perder a conta quando o handle muda.
    """
    caminho = cid if cid.startswith('user/') else cid
    url = 'https://www.youtube.com/' + caminho + '/videos'
    try:
        b, _ = _get(url, timeout=45)
    except Exception as e:                                       # noqa: BLE001
        return None, '%s: %s' % (type(e).__name__, str(e)[:90])
    h = b.decode('utf-8', 'replace')
    m = re.search(r'"(?:channelId|externalChannelId)":"(UC[A-Za-z0-9_-]{20,24})"', h)
    if m:
        return m.group(1), None
    m = re.search(r'channel/(UC[A-Za-z0-9_-]{20,24})', h)
    return (m.group(1), None) if m else (None, 'CHANNEL_ID_NAO_ENCONTRADO_NA_PAGINA')


def fase_canais():
    import datetime
    limite = (datetime.date.fromisoformat(CAPTURA)
              - datetime.timedelta(days=JANELA_DIAS)).isoformat()
    linhas, brutos = [], []
    for c in CANAIS:
        cid, motivo = c['CHANNEL_ID'], None
        resolvido_de = None
        if not cid.startswith('UC'):
            resolvido_de = cid
            cid, motivo = _resolver_handle(cid)
        reg = dict(c)
        reg['RESOLVED_FROM_HANDLE'] = resolvido_de
        reg['CHANNEL_ID_RESOLVED'] = cid or NAO_SEI
        if not cid:
            reg['FEED_STATE'] = 'HANDLE_NAO_RESOLVIDO'
            reg['WHY'] = motivo
            reg['ITEMS_IN_WINDOW'] = 0
            linhas.append(reg)
            print('  %-46s HANDLE_NAO_RESOLVIDO  %s' % (c['CHANNEL_NAME'][:44], motivo))
            continue
        try:
            b, st = _get(_feed_url(cid))
            h = b.decode('utf-8', 'replace')
            reg['FEED_STATE'] = 'OK'
            reg['FEED_HTTP'] = st
            reg['FEED_BYTES'] = len(b)
        except Exception as e:                                   # noqa: BLE001
            reg['FEED_STATE'] = 'FEED_NAO_ALCANCADO'
            reg['WHY'] = '%s: %s' % (type(e).__name__, str(e)[:90])
            reg['ITEMS_IN_WINDOW'] = 0
            linhas.append(reg)
            print('  %-46s FEED_NAO_ALCANCADO' % c['CHANNEL_NAME'][:44])
            continue
        itens = []
        for m in re.finditer(r'<entry>(.*?)</entry>', h, re.S):
            e = m.group(1)
            def g(tag):
                mm = re.search(r'<%s[^>]*>(.*?)</%s>' % (tag, tag), e, re.S)
                return mm.group(1).strip() if mm else None
            vid = g('yt:videoId')
            pub = (g('published') or '')[:10]
            if not vid or not pub:
                continue
            itens.append({'id': vid, 'title': g('title'), 'date': pub,
                          'channelId': cid, 'channelName': c['CHANNEL_NAME'],
                          'url': 'https://www.youtube.com/watch?v=' + vid})
        na_janela = [i for i in itens if i['date'] >= limite]
        reg['ITEMS_IN_FEED'] = len(itens)
        reg['ITEMS_IN_WINDOW'] = len(na_janela)
        reg['LATEST_IN_FEED'] = max((i['date'] for i in itens), default=NAO_SEI)
        linhas.append(reg)
        brutos.extend(na_janela)
        print('  %-46s feed %2d · janela %2d · mais recente %s'
              % (c['CHANNEL_NAME'][:44], len(itens), len(na_janela), reg['LATEST_IN_FEED']))
    corpo = {
        'DATASET': 'IT-VIDEO-CANAIS-V1',
        'SOURCE': 'YouTube — feed público por channel_id (videos.xml), sem chave',
        'SOURCE_ID': 'IT-SRCX-036',
        'CAPTURED_AT': CAPTURA,
        'RUN_ID': RUN_ID,
        'WINDOW_DAYS': JANELA_DIAS,
        'WINDOW_FROM': limite,
        'CHANNELS_DECLARED': len(CANAIS),
        'CHANNELS_WITH_FEED': sum(1 for x in linhas if x.get('FEED_STATE') == 'OK'),
        'ITEMS_IN_WINDOW': len(brutos),
        'EXCLUDED_AND_WHY': EXCLUIDOS,
        'ZERO_MEANS': ('feed com 0 itens na janela significa NENHUM ITEM PUBLICADO NA JANELA '
                       'por este canal, nesta leitura. Nunca "o canal parou".'),
        'CHANNELS': linhas,
        'ITEMS': brutos,
    }
    p = _gravar('IT-VIDEO-CANAIS-V1.json', corpo)
    print('\n%d canais · %d com feed · %d objetos na janela de %d dias'
          % (len(CANAIS), corpo['CHANNELS_WITH_FEED'], len(brutos), JANELA_DIAS))
    print('escrito: %s' % p)
    return 0


# ── FASE 2 · FALA ──────────────────────────────────────────────────────────────
def _fala_youtube(vid):
    """→ (texto, idioma, fonte, motivo). Nunca levanta.

    Duas rotas, nesta ordem de preferência, e a escolhida fica registrada em CAPTION_SOURCE:
      1. IT_VIDEO_AUDIO=1 → baixa o áudio e chama o `faster-whisper` desta casa.
      2. legenda automática do YouTube, via `youtube.com/api/timedtext`.
    """
    try:
        import yt_dlp
    except ImportError:
        return None, None, None, 'YT_DLP_AUSENTE'
    try:
        with yt_dlp.YoutubeDL({'quiet': True, 'skip_download': True,
                               'no_warnings': True}) as y:
            info = y.extract_info('https://www.youtube.com/watch?v=' + vid, download=False)
    except Exception as e:                                       # noqa: BLE001
        return None, None, None, 'META_FALHOU: %s' % str(e)[:110]

    if os.environ.get('IT_VIDEO_AUDIO') == '1':
        t = _fala_local(vid, info)
        if t:
            return t, 'it', 'SINTONIA_WHISPER_LOCAL', None

    auto = info.get('automatic_captions') or {}
    manual = info.get('subtitles') or {}
    for fonte, mapa, marca in (('manual', manual, 'YOUTUBE_SUBTITLES_MANUAL'),
                               ('auto', auto, 'YOUTUBE_ASR_AUTO')):
        for lang in ('it', 'it-IT'):
            fmts = [f for f in mapa.get(lang, []) if f.get('ext') == 'json3']
            if not fmts:
                continue
            try:
                b, _ = _get(fmts[0]['url'], timeout=60)
                d = json.loads(b.decode('utf-8', 'replace'))
            except Exception as e:                               # noqa: BLE001
                return None, lang, marca, 'LEGENDA_NAO_BAIXOU: %s' % str(e)[:90]
            txt = ''.join(seg.get('utf8', '')
                          for ev in (d.get('events') or [])
                          for seg in (ev.get('segs') or []))
            txt = re.sub(r'\s+', ' ', txt).strip()
            if txt:
                return txt, lang, marca, None
            return None, lang, marca, 'REQUESTED_EMPTY'
    # Idioma é DECLARADO: um canal italiano sem legenda italiana não vira legenda inglesa.
    return None, None, None, ('SEM_LEGENDA_IT (línguas oferecidas: %s)'
                              % ','.join(sorted(set(list(manual) + list(auto)))[:6]))


def _fala_local(vid, info):
    """Áudio → WAV → `faster-whisper`. Só roda com IT_VIDEO_AUDIO=1, e só onde a mídia abre.

    Medido em 2026-09-03 nesta sessão: o binário vem de `googlevideo.com` e a política de
    saída devolve HTTP 403. Na máquina do runner, abre.
    """
    import subprocess
    try:
        import yt_dlp
        from faster_whisper import BatchedInferencePipeline, WhisperModel
    except ImportError:
        return None
    os.makedirs(os.path.join(SAIDA, 'audio-cache'), exist_ok=True)
    wav = os.path.join(SAIDA, 'audio-cache', vid + '.wav')
    if not (os.path.exists(wav) and os.path.getsize(wav) > 100000):
        alvo = os.path.join(SAIDA, 'audio-cache', vid + '.%(ext)s')
        try:
            with yt_dlp.YoutubeDL({'quiet': True, 'no_warnings': True,
                                   'format': 'bestaudio/best', 'outtmpl': alvo}) as y:
                y.download(['https://www.youtube.com/watch?v=' + vid])
        except Exception:                                        # noqa: BLE001
            return None
        import glob
        cand = [f for f in glob.glob(os.path.join(SAIDA, 'audio-cache', vid + '.*'))
                if not f.endswith('.wav')]
        if not cand:
            return None
        r = subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', cand[0], '-vn', '-ac', '1',
                            '-ar', '16000', '-c:a', 'pcm_s16le', wav],
                           capture_output=True, text=True)
        if r.returncode != 0:
            return None
    m = WhisperModel(os.environ.get('IT_VIDEO_MODELO') or 'small', device='cpu',
                     compute_type='int8', cpu_threads=os.cpu_count() or 4)
    pipe = BatchedInferencePipeline(model=m)
    segs, _ = pipe.transcribe(wav, language='it', beam_size=1, batch_size=8)
    return re.sub(r'\s+', ' ', ''.join(s.text for s in segs)).strip()


def fase_fala(teto=None):
    d = _ler('IT-VIDEO-CANAIS-V1.json')
    if not d:
        print('rode `canais` antes'); return 1
    os.makedirs(FALAS, exist_ok=True)
    itens = d['ITEMS'][:int(teto or TETO)]
    feitas = {}
    ant = _ler('IT-VIDEO-FALAS-V1.json')
    if ant:
        feitas = {i['EXTERNAL_ID']: i for i in ant.get('ITEMS', []) if i.get('CHARS')}
        print('já baixadas antes: %d (preservadas)' % len(feitas))
    saida, ok, vazias, falhas = [], 0, 0, 0
    for n, it in enumerate(itens, 1):
        vid = it['id']
        if vid in feitas:
            saida.append(feitas[vid]); ok += 1; continue
        txt, lang, marca, motivo = _fala_youtube(vid)
        reg = {'EXTERNAL_ID': vid, 'URL': it['url'], 'TITLE': it['title'],
               'PUBLICATION_DATE': it['date'], 'CHANNEL_NAME': it['channelName'],
               'CHANNEL_ID': it['channelId'], 'CAPTION_SOURCE': marca or NAO_SEI,
               'TRANSCRIPT_LANGUAGE': lang or NAO_SEI, 'COLLECTED_AT': agora()}
        if txt:
            reg['CHARS'] = len(txt)
            nome = '%s.json' % vid
            with open(os.path.join(FALAS, nome), 'w', encoding='utf-8') as f:
                json.dump({
                    # Cada arquivo de fala declara sozinho de onde veio. Um arquivo solto
                    # que não diz a origem é indistinguível de um arquivo inventado — e o
                    # guardião de proveniência do repositório reprova, com razão.
                    'SOURCE': 'YouTube — %s' % marca,
                    'SOURCE_ID': 'IT-SRCX-036',
                    'CAPTURED_AT': CAPTURA,
                    'RUN_ID': RUN_ID,
                    'EXTERNAL_ID': vid, 'URL': it['url'], 'TITLE': it['title'],
                    'PUBLICATION_DATE': it['date'], 'CHANNEL_NAME': it['channelName'],
                    'CHANNEL_ID': it['channelId'],
                    'CAPTION_SOURCE': marca, 'TRANSCRIPT_LANGUAGE': lang,
                    'TRANSCRIPT': txt}, f, ensure_ascii=False, indent=1)
            reg['FALA_PATH'] = 'data/samples/IT-VIDEO-V1/falas/' + nome
            reg['STATE'] = 'OK'
            ok += 1
        elif motivo == 'REQUESTED_EMPTY':
            reg['STATE'] = 'REQUESTED_EMPTY'; reg['WHY'] = motivo; vazias += 1
        else:
            reg['STATE'] = 'NAO_OBTIDA'; reg['WHY'] = motivo; falhas += 1
        saida.append(reg)
        print('  [%2d/%2d] %-11s %-28s %s' % (n, len(itens), reg['STATE'],
                                              (it['channelName'] or '')[:26],
                                              (it['title'] or '')[:44]))
        time.sleep(float(os.environ.get('IT_VIDEO_PAUSA') or 1.5))
    corpo = {
        'DATASET': 'IT-VIDEO-FALAS-V1',
        'SOURCE': 'YouTube — legenda automática italiana via youtube.com/api/timedtext, '
                  'ou faster-whisper local quando IT_VIDEO_AUDIO=1',
        'SOURCE_ID': 'IT-SRCX-036',
        'CAPTURED_AT': CAPTURA, 'RUN_ID': RUN_ID,
        'CAPTION_SOURCE_LAW': ('YOUTUBE_ASR_AUTO é a fala transcrita por TERCEIRO. '
                               'SINTONIA_WHISPER_LOCAL é a transcrição DESTA casa. '
                               'As duas são fala e NÃO são a mesma coisa.'),
        'EMPTY_LAW': 'REQUESTED_EMPTY é estado, não ausência de conteúdo técnico.',
        'REQUESTED': len(itens), 'OK': ok, 'REQUESTED_EMPTY': vazias, 'NAO_OBTIDA': falhas,
        'CHARS_TOTAL': sum(i.get('CHARS', 0) for i in saida),
        'ITEMS': saida,
    }
    p = _gravar('IT-VIDEO-FALAS-V1.json', corpo)
    print('\nfala obtida em %d de %d · %d REQUESTED_EMPTY · %d não obtida · %d caracteres'
          % (ok, len(itens), vazias, falhas, corpo['CHARS_TOTAL']))
    print('escrito: %s' % p)
    return 0


# ── FASE 3 · MONTAR ────────────────────────────────────────────────────────────
def fase_montar():
    """RAW → `voz.pipeline_video` → registro de 32 campos, com dedupe e cobertura.

    O pipeline é o mesmo da Espanha. O que muda é o vocabulário DECLARADO — e o relatório
    diz qual vocabulário rodou, porque dois países produzindo o campo `CROP` com réguas
    diferentes e sem dizer qual é exatamente o defeito que a cobertura por campo existe
    para impedir.
    """
    canais = _ler('IT-VIDEO-CANAIS-V1.json')
    falas = _ler('IT-VIDEO-FALAS-V1.json')
    if not canais:
        print('rode `canais` antes'); return 1
    papel = {c['CHANNEL_ID_RESOLVED']: c['DECLARED_ROLE'] for c in canais['CHANNELS']
             if c.get('CHANNEL_ID_RESOLVED') and c['CHANNEL_ID_RESOLVED'] != NAO_SEI}
    org = {c['CHANNEL_ID_RESOLVED']: c.get('ORGANIZATION') for c in canais['CHANNELS']
           if c.get('CHANNEL_ID_RESOLVED') and c['CHANNEL_ID_RESOLVED'] != NAO_SEI}

    transcricoes = {}
    if falas:
        for i in falas['ITEMS']:
            if i.get('STATE') == 'OK' and i.get('FALA_PATH'):
                with open(os.path.join(ROOT, i['FALA_PATH']), encoding='utf-8') as f:
                    t = json.load(f)
                transcricoes[i['URL']] = {'transcript': t['TRANSCRIPT'],
                                          'language': t.get('TRANSCRIPT_LANGUAGE'),
                                          'caption_source': t.get('CAPTION_SOURCE')}
            elif i.get('STATE') == 'REQUESTED_EMPTY':
                transcricoes[i['URL']] = {'transcript': None}

    registros, relatorio = voz.pipeline_video(
        canais['ITEMS'], source_id='IT-SRCX-036', run_id=RUN_ID, capture_date=CAPTURA,
        papel_por_canal=papel, transcricoes=transcricoes,
        evidence_path='data/samples/IT-VIDEO-V1/',
        vocab_crop=voz.VOCAB_CROP_IT, vocab_issue=voz.VOCAB_ISSUE_IT,
        vocab_molecule=voz.VOCAB_MOLECULE_IT, vocab_lugar=voz.VOCAB_LUGAR_IT,
        ler_transcricao=True)

    # ORGANIZATION e COUNTRY vêm da lista DECLARADA de canais, nunca do conteúdo do vídeo.
    for r in registros:
        if r['CHANNEL_ID'] in org and org[r['CHANNEL_ID']]:
            r['ORGANIZATION'] = org[r['CHANNEL_ID']]
            r['COUNTRY'] = 'IT'

    # O KPI da missão: o assunto que existe na FALA e não existe na DESCRIÇÃO.
    so_na_fala = []
    for r in registros:
        if r.get('TRANSCRIPT') in (NAO_SEI, None):
            continue
        cabeca = ' '.join(str(r.get(k) or '') for k in ('TITLE', 'DESCRIPTION'))
        fala = str(r.get('TRANSCRIPT') or '')
        achados = []
        for grupo, vocab in (('CROP', voz.VOCAB_CROP_IT), ('ISSUE', voz.VOCAB_ISSUE_IT),
                             ('MOLECULE', voz.VOCAB_MOLECULE_IT), ('PLACE', voz.VOCAB_LUGAR_IT)):
            for nome, rx in vocab.items():
                if re.search(rx, fala, re.I) and not re.search(rx, cabeca, re.I):
                    achados.append({'GROUP': grupo, 'TERM': nome})
        if achados:
            so_na_fala.append({'CONTENT_ID': r['CONTENT_ID'], 'URL': r['URL'],
                               'TITLE': r['TITLE'], 'PUBLICATION_DATE': r['PUBLICATION_DATE'],
                               'CHANNEL_NAME': r['CHANNEL_NAME'],
                               'CAPTION_SOURCE': r.get('CAPTION_SOURCE'),
                               'ONLY_IN_SPOKEN': achados})

    com_fala = [r for r in registros if r.get('TRANSCRIPT') not in (NAO_SEI, None)]
    corpo = {
        'DATASET': 'IT-VIDEO-V1',
        'LAYER': 'PUBLIC_VIDEO_ITALY',
        'SOURCE': 'YouTube — feed público por channel_id e legenda por youtube.com/api/timedtext',
        'SOURCE_ID': 'IT-SRCX-036',
        'CAPTURED_AT': CAPTURA, 'RUN_ID': RUN_ID,
        'CONTRACT': 'scripts/voz.py · CAMPOS_VIDEO · 32 campos · campo ausente vira NAO_SEI',
        'PIPELINE': 'voz.pipeline_video — o mesmo da Espanha; muda o vocabulário declarado',
        'ROLE_LAW': ('DECLARED_ROLE vem da lista declarada de canais. O papel da origem nunca '
                     'sai do conteúdo do vídeo: um vídeo técnico num canal promocional '
                     'continua sendo um canal promocional.'),
        'REPORT': relatorio,
        'WITH_SPOKEN_TEXT': len(com_fala),
        'SPOKEN_CHARS_TOTAL': sum(len(str(r.get('TRANSCRIPT') or '')) for r in com_fala),
        'BY_CAPTION_SOURCE': {},
        'SIGNAL_ONLY_IN_SPOKEN_COUNT': len(so_na_fala),
        'SIGNAL_ONLY_IN_SPOKEN': so_na_fala,
        'RECORDS': registros,
    }
    for r in com_fala:
        k = r.get('CAPTION_SOURCE') or NAO_SEI
        corpo['BY_CAPTION_SOURCE'][k] = corpo['BY_CAPTION_SOURCE'].get(k, 0) + 1
    p = _gravar('IT-VIDEO-V1.json', corpo)

    print('RAW %d · únicos %d · duplicatas %d · origens %d'
          % (relatorio['RAW_COUNT'], relatorio['UNIQUE_CONTENT_COUNT'],
             relatorio['DUPLICATE_COUNT'], relatorio['UNIQUE_ORIGIN_COUNT']))
    print('com fala %d · %d caracteres · por fonte %s'
          % (len(com_fala), corpo['SPOKEN_CHARS_TOTAL'], corpo['BY_CAPTION_SOURCE']))
    print('tipos: %s' % relatorio['CONTENT_TYPE_COUNTS'])
    print('vocabulário: %s' % relatorio['VOCAB_DECLARED'])
    print('sinal SÓ NA FALA em %d objetos' % len(so_na_fala))
    declarados = sum(1 for c, v in relatorio['FIELD_COVERAGE'].items() if v['DECLARED'])
    print('cobertura: %d dos 32 campos com ao menos um registro declarado' % declarados)
    print('escrito: %s' % p)
    return 0


FASES = {'canais': fase_canais, 'fala': fase_fala, 'montar': fase_montar}

if __name__ == '__main__':
    arg = sys.argv[1] if len(sys.argv) > 1 else 'tudo'
    if arg == 'tudo':
        for nome in ('canais', 'fala', 'montar'):
            print('\n=== %s ===' % nome)
            if FASES[nome]():
                sys.exit(1)
        sys.exit(0)
    if arg not in FASES:
        print(__doc__)
        sys.exit(2)
    extra = sys.argv[2:]
    sys.exit(FASES[arg](*extra) if extra else FASES[arg]())
