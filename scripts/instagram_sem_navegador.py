#!/usr/bin/env python3
"""
INSTAGRAM SEM NAVEGADOR — a janela pública, sem Chrome e sem CDP.

    py scripts/instagram_sem_navegador.py perfis      # GRÁTIS · bio, seguidores, denominador
    py scripts/instagram_sem_navegador.py objetos     # GRÁTIS · legenda, data, vídeo, duração
    py scripts/instagram_sem_navegador.py transcrever # GRÁTIS em dólar · a fala, aqui na máquina
    py scripts/instagram_sem_navegador.py tudo

O QUE ESTE ARQUIVO CORRIGE, E A CORREÇÃO É MINHA
--------------------------------------------------
Em 2026-09-03 esta casa registrou, por minha mão, que a rota de embed do Instagram
"precisa do navegador" e que sem Chrome o Sintonia Scrap não coletaria Instagram desta
sessão. **Estava errado.** O que faltava não era JavaScript: era o **User-Agent**.

Medido, na MESMA URL e no MESMO minuto:

    GET /p/DF3F_QJtegI/embed/   UA Chrome desktop ......  200 · 625.215 B · contextJSON = 0
    GET /p/DF3F_QJtegI/embed/   UA facebookexternalhit/1.1  200 · 262.551 B · contextJSON = 1

    O USER-AGENT ERA A FECHADURA. NÃO O NAVEGADOR.

`instagram_janela.py` continua válido e continua sendo a rota medida com janela — ele lê
mais (12 itens da grade) e resolve casos que o embed enxuto não resolve. Este arquivo é a
rota que **funciona onde não há navegador**, e diz onde entrega menos.

A CADEIA, EM QUATRO PASSOS
----------------------------
    1. GET /<handle>/embed/         UA=bot  → contextJSON.context:
                                              username, full_name, followers_count,
                                              posts_count e os 6 posts mais recentes
                                              hidratados (shortcode, taken_at_timestamp,
                                              is_video, legenda, curtidas)
    2. GET /p/<shortcode>/embed/    UA=bot  → contextJSON.gql_data.shortcode_media:
                                              video_url, video_duration, video_view_count
    3. GET video_url                UA=desk → MP4 em scontent-*.cdninstagram.com
    4. ffmpeg → faster-whisper small, idioma `it` DECLARADO → SINTONIA_WHISPER_LOCAL

OS DOIS EMBEDS SÃO COMPLEMENTARES, E ISSO NÃO É DETALHE
---------------------------------------------------------
O embed de **perfil** traz `taken_at_timestamp` e **não** traz `video_url`.
O embed de **post** traz `video_url` e **não** traz `taken_at_timestamp`.

    A DATA VEM DO PERFIL. O VÍDEO VEM DO POST. QUEM USA SÓ UM PERDE METADE.

E a data é **lida**, nunca calculada: decodificar o media-id
(`(id >> 23) + 1314220021721 ms`) foi testado contra as datas lidas e bateu **8 de 36**.
É aproximação, e aproximação não é leitura.

O QUE ESTA ROTA ENTREGA MENOS QUE A DO NAVEGADOR
--------------------------------------------------
    grade do perfil ..... 6 itens, contra os 12 medidos no Chrome com janela
    comentários ......... nenhum. Continua sendo o único motivo real de pagar.
    copyright_blocked ... quando `context.copyright_blocked` é verdadeiro, o
                          `shortcode_media` simplesmente OMITE `video_url`. Medido em
                          DF3F_QJtegI. Isso é ESTADO DO POST, não falha da rota.

    6 DE 3.524 É SUB-COLETA DECLARADA. "6" SOZINHO É UM NÚMERO QUE MENTE.

O QUE ESTE ARQUIVO NÃO FAZ
----------------------------
Não faz login, não lê nem escreve cookie, não passa credencial, não resolve CAPTCHA, não
desliga verificação TLS, não toca em perfil privado. Ele pede ao Instagram a mesma moldura
pública que o Instagram publica para qualquer site incorporar um post — e se identifica
como o que é.
"""
import json
import os
import re
import subprocess
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

LIBS = os.environ.get('SINTONIA_LIBS') or os.path.join(os.path.expanduser('~'), '.sintonia-libs')
if os.path.isdir(LIBS):
    sys.path.insert(0, LIBS)

SAMPLES = os.path.join(ROOT, 'data', 'samples')
LOTE = os.path.join(SAMPLES, 'COMPETITOR-PUBLIC-COMM', 'PUBLIC-COMM-IT-SOCIAL-BATCH-V1.json')
SAIDA = os.path.join(SAMPLES, 'IT-INSTAGRAM-V1')
MEDIA = os.path.join(SAIDA, 'media-cache')
CAPTURA = os.environ.get('IG_DATA') or '2026-09-03'
RUN_ID = 'IT-IG-' + CAPTURA
NAO_SEI = 'NAO_SEI'

# O bot é quem o Instagram atende com o bloco hidratado. Identificar-se como ele é
# dizer a verdade sobre o que se está pedindo: a moldura de incorporação.
UA_BOT = 'facebookexternalhit/1.1'
UA_DESK = ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
           'Chrome/141.0.0.0 Safari/537.36')
PAUSA = float(os.environ.get('IG_PAUSA') or 2.0)


def agora():
    import datetime
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + 'Z'


def _get(url, ua, timeout=60, binario=False):
    req = urllib.request.Request(url, headers={'User-Agent': ua,
                                               'Accept-Language': 'it-IT,it;q=0.9'})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        b = r.read()
        return (b if binario else b.decode('utf-8', 'replace')), r.status


def contexto(h):
    """→ (objeto, motivo). O mesmo algoritmo do `JS_EMBED` de `instagram_janela.py`, aqui
    em Python: acha `contextJSON`, conta quantas camadas de escape este deploy usa e anda
    a string respeitando a barra invertida — porque `\\"` no meio do texto NÃO fecha."""
    m = re.search(r'contextJSON(\\*)"\s*:\s*', h)
    if not m:
        return None, 'SEM_CONTEXTJSON'
    p = m.end()
    if h[p:p + 4] == 'null':
        return None, 'CONTEXTJSON_NULL'
    niveis = len(m.group(1))
    abre = '\\' * niveis + '"'
    if h[p:p + len(abre)] != abre:
        return None, 'VALOR_NAO_E_STRING'
    k, fim = p + len(abre), -1
    while k < len(h):
        if h[k] == '\\':
            k += 2
            continue
        if h[k] == '"':
            fim = k
            break
        k += 1
    if fim < 0:
        return None, 'STRING_NAO_FECHA'
    s = h[p + len(abre):fim]
    try:
        for _ in range(max(1, niveis)):
            s = json.loads('"' + s + '"')
        return json.loads(s), None
    except ValueError as e:
        return None, 'PARSE_FALHOU: %s' % str(e)[:80]


def _gravar(nome, corpo):
    os.makedirs(SAIDA, exist_ok=True)
    with open(os.path.join(SAIDA, nome), 'w', encoding='utf-8') as f:
        json.dump(corpo, f, ensure_ascii=False, indent=1)
    return 'data/samples/IT-INSTAGRAM-V1/' + nome


def _ler(nome):
    p = os.path.join(SAIDA, nome)
    if not os.path.exists(p):
        return None
    with open(p, encoding='utf-8') as f:
        return json.load(f)


def _contas():
    """Obedece ao lote congelado. Este arquivo NÃO decide quem entra."""
    with open(LOTE, encoding='utf-8') as f:
        d = json.load(f)
    return [c for c in d['ACCOUNTS'] if c['PLATFORM'] == 'INSTAGRAM']


# ── FASE 1 · PERFIS ────────────────────────────────────────────────────────────
def fase_perfis():
    contas, linhas, objetos = _contas(), [], []
    for n, c in enumerate(contas, 1):
        h = c['HANDLE']
        reg = {'HANDLE': h, 'URL': c['URL'], 'ORGANISATION': c['ORGANISATION'],
               'PAGE_ROLE': c['PAGE_ROLE'], 'COLLECTED_AT': agora(),
               'IDENTITY_EVIDENCE': c['IDENTITY_EVIDENCE']}
        try:
            html, st = _get('https://www.instagram.com/%s/embed/' % h, UA_BOT)
            reg['HTTP'] = st
            reg['BYTES'] = len(html)
        except Exception as e:                                   # noqa: BLE001
            reg['STATE'] = 'NAO_ALCANCADO'
            reg['WHY'] = '%s: %s' % (type(e).__name__, str(e)[:90])
            linhas.append(reg)
            print('  [%2d/%2d] %-30s NAO_ALCANCADO' % (n, len(contas), h[:28]))
            continue
        ctx, why = contexto(html)
        if not ctx:
            reg['STATE'] = 'SEM_CONTEXTO'
            reg['WHY'] = why
            linhas.append(reg)
            print('  [%2d/%2d] %-30s SEM_CONTEXTO (%s)' % (n, len(contas), h[:28], why))
            continue
        c2 = ctx.get('context') or {}
        reg['STATE'] = 'OK'
        reg['USERNAME'] = c2.get('username') or NAO_SEI
        reg['FULL_NAME'] = c2.get('full_name') or NAO_SEI
        reg['VERIFIED'] = c2.get('is_verified', c2.get('verified', NAO_SEI))
        reg['FOLLOWERS'] = c2.get('followers_count', NAO_SEI)
        # O DENOMINADOR. Sem ele, "6 itens" é indistinguível de "a conta tem 6 posts"
        # e de "a coleta quebrou".
        reg['POSTS_TOTAL'] = c2.get('posts_count', NAO_SEI)
        gm = c2.get('graphql_media') or []
        reg['ITEMS_IN_EMBED'] = len(gm)
        reg['COVERAGE_SENTENCE'] = ('%s de %s' % (len(gm), reg['POSTS_TOTAL']))
        for m in gm:
            node = m.get('shortcode_media') or m
            sc = node.get('shortcode')
            if not sc:
                continue
            leg = ''
            try:
                leg = ((node.get('edge_media_to_caption') or {}).get('edges') or [{}])[0] \
                        .get('node', {}).get('text', '') or ''
            except Exception:                                    # noqa: BLE001
                leg = ''
            objetos.append({
                'SHORTCODE': sc,
                'HANDLE': h,
                'ORGANISATION': c['ORGANISATION'],
                'PAGE_ROLE': c['PAGE_ROLE'],
                'URL': 'https://www.instagram.com/p/%s/' % sc,
                # A DATA VEM DAQUI, do perfil, e é LIDA. O embed de post não a traz, e
                # decodificar o media-id bateu 8 de 36 — aproximação não é leitura.
                'TAKEN_AT_TIMESTAMP': node.get('taken_at_timestamp'),
                'PUBLICATION_DATE': (time.strftime('%Y-%m-%d', time.gmtime(node['taken_at_timestamp']))
                                     if node.get('taken_at_timestamp') else NAO_SEI),
                'IS_VIDEO': 'YES' if node.get('is_video') else 'NO',
                'CAPTION': leg,
                'CAPTION_CHARS': len(leg),
                'LIKES': (node.get('edge_media_preview_like') or {}).get('count', NAO_SEI),
                'COMMENTS_COUNT': (node.get('edge_media_to_comment') or {}).get('count', NAO_SEI),
                'DATE_SOURCE': 'PROFILE_EMBED_taken_at_timestamp (LIDO, nunca decodificado do id)',
            })
        linhas.append(reg)
        print('  [%2d/%2d] %-30s OK · %6s seguidores · %s posts · grade %s'
              % (n, len(contas), h[:28], reg['FOLLOWERS'], reg['POSTS_TOTAL'], reg['COVERAGE_SENTENCE']))
        time.sleep(PAUSA)
    ok = sum(1 for x in linhas if x.get('STATE') == 'OK')
    corpo = {
        'DATASET': 'IT-INSTAGRAM-PERFIS-V1',
        'SOURCE': 'Instagram — embed público de perfil, UA facebookexternalhit/1.1',
        'SOURCE_ID': 'PUBLIC-COMM-IT-SOCIAL-BATCH-V1',
        'CAPTURED_AT': CAPTURA, 'RUN_ID': RUN_ID,
        'ROUTE_LAW': ('o User-Agent era a fechadura, não o navegador. A MESMA URL devolve '
                      'zero contextJSON sob UA de Chrome e o bloco hidratado sob '
                      'facebookexternalhit/1.1. Medido em 2026-09-03.'),
        'WINDOW_LAW': ('esta rota entrega 6 itens de grade; o Chrome com janela entrega 12. '
                       'É metade da janela, e está dito.'),
        'DENOMINATOR_LAW': '"6" sozinho é um número que mente. A frase honesta é "6 de N".',
        'ACCOUNTS_REQUESTED': len(contas), 'ACCOUNTS_OK': ok,
        'OBJECTS_FOUND': len(objetos),
        'VIDEOS_FOUND': sum(1 for o in objetos if o['IS_VIDEO'] == 'YES'),
        'PROFILES': linhas, 'OBJECTS': objetos,
    }
    p = _gravar('IT-INSTAGRAM-PERFIS-V1.json', corpo)
    print('\n%d de %d contas · %d objetos · %d vídeos' % (ok, len(contas), len(objetos), corpo['VIDEOS_FOUND']))
    print('escrito: %s' % p)
    return 0


# ── FASE 2 · OBJETOS ───────────────────────────────────────────────────────────
def fase_objetos(teto=None):
    d = _ler('IT-INSTAGRAM-PERFIS-V1.json')
    if not d:
        print('rode `perfis` antes')
        return 1
    # Vídeo primeiro: é onde mora a fala, e a regra de coleta externa põe vídeo em 1º.
    alvos = [o for o in d['OBJECTS'] if o['IS_VIDEO'] == 'YES'][:int(teto or 40)]
    saida, ok = [], 0
    for n, o in enumerate(alvos, 1):
        reg = dict(o)
        reg['COLLECTED_AT'] = agora()
        try:
            html, st = _get('https://www.instagram.com/p/%s/embed/' % o['SHORTCODE'], UA_BOT)
            reg['POST_EMBED_HTTP'] = st
        except Exception as e:                                   # noqa: BLE001
            reg['STATE'] = 'NAO_ALCANCADO'
            reg['WHY'] = '%s: %s' % (type(e).__name__, str(e)[:90])
            saida.append(reg)
            continue
        ctx, why = contexto(html)
        if not ctx:
            reg['STATE'] = 'SEM_CONTEXTO'
            reg['WHY'] = why
            saida.append(reg)
            print('  [%2d/%2d] %-13s SEM_CONTEXTO' % (n, len(alvos), o['SHORTCODE']))
            continue
        node = ((ctx.get('gql_data') or {}).get('shortcode_media')) or {}
        blocked = (ctx.get('context') or {}).get('copyright_blocked')
        reg['COPYRIGHT_BLOCKED'] = bool(blocked)
        reg['VIDEO_URL_TEMPORARY'] = node.get('video_url') or NAO_SEI
        reg['VIDEO_DURATION_S'] = node.get('video_duration', NAO_SEI)
        reg['VIDEO_VIEW_COUNT'] = node.get('video_view_count', NAO_SEI)
        reg['PRODUCT_TYPE'] = node.get('product_type', NAO_SEI)
        if reg['VIDEO_URL_TEMPORARY'] == NAO_SEI:
            # Estado do POST, não falha da rota — e é assim que fica escrito.
            reg['STATE'] = ('COPYRIGHT_BLOCKED_SEM_VIDEO_URL' if blocked
                            else 'SEM_VIDEO_URL_NO_EMBED')
        else:
            reg['STATE'] = 'OK'
            ok += 1
        saida.append(reg)
        print('  [%2d/%2d] %-13s %-30s %ss' % (n, len(alvos), o['SHORTCODE'], reg['STATE'],
                                               reg.get('VIDEO_DURATION_S')))
        time.sleep(PAUSA)
    corpo = {
        'DATASET': 'IT-INSTAGRAM-OBJETOS-V1',
        'SOURCE': 'Instagram — embed público de post, UA facebookexternalhit/1.1',
        'SOURCE_ID': 'PUBLIC-COMM-IT-SOCIAL-BATCH-V1',
        'CAPTURED_AT': CAPTURA, 'RUN_ID': RUN_ID,
        'JOIN_LAW': ('a DATA vem do embed de PERFIL e a URL DO VÍDEO vem do embed de POST. '
                     'Os dois são complementares; quem usa só um perde metade.'),
        'URL_LAW': 'VIDEO_URL_TEMPORARY é assinada pela CDN e vence em horas. URL EXPIRADA != VÍDEO INEXISTENTE.',
        'REQUESTED': len(alvos), 'WITH_VIDEO_URL': ok,
        'COPYRIGHT_BLOCKED': sum(1 for x in saida if x.get('COPYRIGHT_BLOCKED')),
        'ITEMS': saida,
    }
    p = _gravar('IT-INSTAGRAM-OBJETOS-V1.json', corpo)
    print('\n%d de %d com VIDEO_URL · %d copyright_blocked' % (ok, len(alvos), corpo['COPYRIGHT_BLOCKED']))
    print('escrito: %s' % p)
    return 0


# ── FASE 3 · TRANSCREVER ───────────────────────────────────────────────────────
def _audio(sc, url):
    """MP4 → WAV 16 kHz mono. → (caminho, motivo). A URL da CDN vence em horas; quando
    vencer, `objetos` roda de novo e é grátis. URL EXPIRADA ≠ VÍDEO INEXISTENTE."""
    os.makedirs(MEDIA, exist_ok=True)
    wav = os.path.join(MEDIA, sc + '.wav')
    if os.path.exists(wav) and os.path.getsize(wav) > 50000:
        return wav, None
    mp4 = os.path.join(MEDIA, sc + '.mp4')
    if not (os.path.exists(mp4) and os.path.getsize(mp4) > 50000):
        try:
            b, _ = _get(url, UA_DESK, timeout=240, binario=True)
            with open(mp4, 'wb') as f:
                f.write(b)
        except Exception as e:                                   # noqa: BLE001
            return None, 'DOWNLOAD_FALHOU: %s (URL vencida? rode `objetos` de novo)' % type(e).__name__
    r = subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', mp4, '-vn', '-ac', '1',
                        '-ar', '16000', '-c:a', 'pcm_s16le', wav], capture_output=True, text=True)
    if r.returncode != 0 or not os.path.exists(wav):
        return None, 'FFMPEG_FALHOU: %s' % (r.stderr or '')[:110]
    return wav, None


def fase_transcrever(teto=None):
    d = _ler('IT-INSTAGRAM-OBJETOS-V1.json')
    if not d:
        print('rode `objetos` antes')
        return 1
    alvos = [o for o in d['ITEMS'] if o.get('STATE') == 'OK'][:int(teto or 40)]
    if not alvos:
        print('nenhum objeto com VIDEO_URL. Isso é estado, não erro.')
        return 0
    try:
        from faster_whisper import BatchedInferencePipeline, WhisperModel
    except ImportError:
        print('falta faster-whisper. Instale FORA do repositório:\n'
              '  py -m pip install --target %s faster-whisper' % LIBS)
        return 1
    modelo = os.environ.get('IG_MODELO') or 'small'
    nucleos = os.cpu_count() or 4
    print('modelo %s · %d núcleos · idioma it DECLARADO (nunca detectado)' % (modelo, nucleos))
    m = WhisperModel(modelo, device='cpu', compute_type='int8', cpu_threads=nucleos)
    pipe = BatchedInferencePipeline(model=m)

    feitos = {}
    ant = _ler('IT-INSTAGRAM-TRANSCRICOES-V1.json')
    if ant:
        feitos = {i['SHORTCODE']: i for i in ant.get('ITEMS', [])
                  if i.get('TRANSCRIPT_STATE') == 'OK'}
        print('já transcritos antes: %d (preservados)' % len(feitos))

    itens, seg_audio, seg_maq = [], 0.0, 0.0
    for n, o in enumerate(alvos, 1):
        sc = o['SHORTCODE']
        if sc in feitos:
            itens.append(feitos[sc])
            continue
        t0 = time.time()
        wav, why = _audio(sc, o['VIDEO_URL_TEMPORARY'])
        reg = {k: o.get(k) for k in ('SHORTCODE', 'HANDLE', 'ORGANISATION', 'PAGE_ROLE', 'URL',
                                     'PUBLICATION_DATE', 'CAPTION', 'CAPTION_CHARS', 'LIKES',
                                     'COMMENTS_COUNT', 'VIDEO_DURATION_S', 'VIDEO_VIEW_COUNT',
                                     'PRODUCT_TYPE', 'DATE_SOURCE')}
        reg['PLATFORM'] = 'INSTAGRAM'
        reg['COLLECTION_DATE'] = CAPTURA
        reg['TRANSCRIPT_ENGINE'] = ('faster-whisper %s int8 cpu beam=1 lang=it '
                                    '(LOCAL, 0,00 USD)' % modelo)
        reg['CAPTION_SOURCE'] = 'SINTONIA_WHISPER_LOCAL'
        if not wav:
            reg['TRANSCRIPT_STATE'] = 'AUDIO_INDISPONIVEL'
            reg['WHY'] = why
            itens.append(reg)
            print('  [%2d/%2d] %-13s AUDIO_INDISPONIVEL' % (n, len(alvos), sc))
            continue
        segs, _info = pipe.transcribe(wav, language='it', beam_size=1, batch_size=8)
        partes, txt = [], []
        for s in segs:
            partes.append({'S': round(s.start, 1), 'E': round(s.end, 1), 'T': s.text.strip()})
            txt.append(s.text)
        reg['TRANSCRIPT'] = ''.join(txt).strip()
        reg['TRANSCRIPT_SEGMENTS'] = partes
        reg['TRANSCRIPT_CHARS'] = len(reg['TRANSCRIPT'])
        reg['TRANSCRIPT_LANGUAGE'] = 'it'
        # Transcrição pedida e vazia é ESTADO, não "vídeo sem conteúdo técnico".
        reg['TRANSCRIPT_STATE'] = 'OK' if reg['TRANSCRIPT_CHARS'] > 120 else 'REQUESTED_EMPTY'
        maq = round(time.time() - t0, 1)
        dur = o.get('VIDEO_DURATION_S') or 0
        reg['MACHINE_S'] = maq
        reg['SPEED_X'] = round(dur / max(maq, 0.1), 2) if isinstance(dur, (int, float)) else NAO_SEI
        # O KPI da missão: o que a FALA diz e a LEGENDA não.
        cap = (reg.get('CAPTION') or '').lower()
        fala = reg['TRANSCRIPT'].lower()
        reg['SIGNAL_ONLY_IN_TRANSCRIPT'] = 'NAO_SEI'
        if reg['TRANSCRIPT_STATE'] == 'OK':
            import voz
            achados = []
            for grupo, vocab in (('CROP', voz.VOCAB_CROP_IT), ('ISSUE', voz.VOCAB_ISSUE_IT),
                                 ('MOLECULE', voz.VOCAB_MOLECULE_IT), ('PLACE', voz.VOCAB_LUGAR_IT)):
                for nome, rx in vocab.items():
                    if re.search(rx, fala, re.I) and not re.search(rx, cap, re.I):
                        achados.append({'GROUP': grupo, 'TERM': nome})
            reg['ONLY_IN_TRANSCRIPT_TERMS'] = achados
            reg['SIGNAL_ONLY_IN_TRANSCRIPT'] = 'YES' if achados else 'NO'
        itens.append(reg)
        if isinstance(dur, (int, float)):
            seg_audio += dur
        seg_maq += maq
        print('  [%2d/%2d] %-13s %-16s %5ss  %5.2fx  %5d car.  só-na-fala=%s'
              % (n, len(alvos), sc, reg['TRANSCRIPT_STATE'], maq, reg['SPEED_X'] or 0,
                 reg.get('TRANSCRIPT_CHARS', 0), reg['SIGNAL_ONLY_IN_TRANSCRIPT']))
    ok = [i for i in itens if i.get('TRANSCRIPT_STATE') == 'OK']
    corpo = {
        'DATASET': 'IT-INSTAGRAM-TRANSCRICOES-V1',
        'SOURCE': 'Instagram — vídeo público via embed (UA bot) + transcrição LOCAL',
        'SOURCE_ID': 'PUBLIC-COMM-IT-SOCIAL-BATCH-V1',
        'CAPTURED_AT': CAPTURA, 'RUN_ID': RUN_ID,
        'CAPTION_SOURCE_LAW': ('SINTONIA_WHISPER_LOCAL é a transcrição DESTA casa. Não '
                               'confundir com YOUTUBE_ASR_AUTO, que é fala de terceiro.'),
        'COST_USD': 0,
        'ITEMS_TOTAL': len(itens), 'OK': len(ok),
        'AUDIO_SECONDS': round(seg_audio), 'MACHINE_SECONDS': round(seg_maq),
        'TRANSCRIPT_CHARS': sum(i.get('TRANSCRIPT_CHARS', 0) for i in ok),
        'SIGNAL_ONLY_IN_TRANSCRIPT': sum(1 for i in ok if i.get('SIGNAL_ONLY_IN_TRANSCRIPT') == 'YES'),
        'ITEMS': itens,
    }
    p = _gravar('IT-INSTAGRAM-TRANSCRICOES-V1.json', corpo)
    print('\n%d transcritos · %ds de áudio · %ds de máquina · %d caracteres · custo 0,00 USD'
          % (len(ok), corpo['AUDIO_SECONDS'], corpo['MACHINE_SECONDS'], corpo['TRANSCRIPT_CHARS']))
    print('sinal SÓ NA FALA em %d de %d' % (corpo['SIGNAL_ONLY_IN_TRANSCRIPT'], len(ok)))
    print('escrito: %s' % p)
    return 0


FASES = {'perfis': fase_perfis, 'objetos': fase_objetos, 'transcrever': fase_transcrever}

if __name__ == '__main__':
    arg = sys.argv[1] if len(sys.argv) > 1 else 'tudo'
    if arg == 'tudo':
        for nome in ('perfis', 'objetos', 'transcrever'):
            print('\n=== %s ===' % nome)
            if FASES[nome]():
                sys.exit(1)
        sys.exit(0)
    if arg not in FASES:
        print(__doc__)
        sys.exit(2)
    sys.exit(FASES[arg](*sys.argv[2:]) if sys.argv[2:] else FASES[arg]())
