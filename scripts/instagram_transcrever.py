#!/usr/bin/env python3
"""
TRANSCRIÇÃO DOS VÍDEOS — a fala vira texto, aqui na máquina, sem pagar por minuto.

    py scripts/instagram_transcrever.py alvos          # GRÁTIS: o que seria transcrito
    py scripts/instagram_transcrever.py rodar          # transcreve o que falta
    py scripts/instagram_transcrever.py rodar base 20  # modelo e teto de objetos

POR QUE LOCAL, E NÃO PAGO
---------------------------
Medido nesta máquina em 2026-09-02, num reel real de 110 s da @basf_agroes, com os 16
núcleos e o modo em lote:

    modelo    velocidade      qualidade do texto
    tiny      18,7x           "Pirar Pascal", "agro-imfluencia" — inutilizável
    base       9,4x           "Pilar Pasqual", "ingeniero-agricula" — média
    small      3,2x           "Pilar Pascual", "ingeniero agrícola" — boa

`small` em lote leva ~6 horas para 1.000 vídeos (~19 h de áudio) e custa **zero dólar**.
A rota paga cobra por MINUTO — e há ator que cobra por minuto INICIADO, onde um reel de
61 s paga 2 minutos.

    O CUSTO DE TRANSCREVER AQUI É TEMPO DE MÁQUINA, NÃO FATURA.

DUAS COISAS QUE CUSTARAM MEDIÇÃO PARA DESCOBRIR
-------------------------------------------------
1. **Os núcleos não vêm de graça.** O padrão da biblioteca usa 4 threads. Nesta máquina de
   16, declarar `cpu_threads` deu ~4x. A primeira medição, sem isso, deu 0,3x — e 0,3x
   levaria 63 horas para os mesmos mil vídeos.
2. **`beam_size=5` custa o dobro e entrega o mesmo texto.** Medido: 1,16x contra 2,31x,
   com 2.079 e 2.054 caracteres praticamente idênticos. O padrão aqui é 1, de propósito.

A URL DO MP4 EXPIRA, E ISSO NÃO É "O VÍDEO SUMIU"
---------------------------------------------------
`VIDEO_URL_TEMPORARY` é assinada pela CDN da Meta e morre em horas. Quando ela morre, este
arquivo **relê o embed** (grátis) para pegar uma URL nova. O que ele NUNCA faz é registrar
o vídeo como ausente:

    URL EXPIRADA ≠ VÍDEO INEXISTENTE.

O QUE ESTE ARQUIVO NÃO FAZ
----------------------------
Não classifica assunto, não resume, não traduz, não decide se a fala é relevante. Ele
transcreve e preserva — inclusive os tempos de cada trecho, para que qualquer citação
futura possa ser conferida contra o segundo exato do vídeo.
"""
import json
import os
import subprocess
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

# As bibliotecas pesadas vivem FORA do repositório. A memória desta casa registra o
# acidente: `pip` sem `--target` criou `C:\eame-sintonia\Scripts`, e apagar `Scripts`
# apagou `scripts` — no Windows os dois nomes são a MESMA pasta.
LIBS = os.environ.get('SINTONIA_LIBS') or os.path.join(
    os.path.expanduser('~'), '.sintonia-libs')
if os.path.isdir(LIBS):
    sys.path.insert(0, LIBS)

SAMPLES = os.path.join(ROOT, 'data', 'samples')
JANELA = os.path.join(SAMPLES, 'INSTAGRAM-JANELA')
SAIDA = os.path.join(SAMPLES, 'INSTAGRAM-TRANSCRICOES')
MEDIA = os.path.join(SAIDA, 'audio-cache')

MISSION = '14-COMUNICACAO-PUBLICA-DO-CONCORRENTE'
RUNNER = os.environ.get('RUNNER_NAME') or 'NOT_KNOWN'
NAO_SEI = 'NOT_KNOWN'

MODELO_PADRAO = os.environ.get('IG_MODELO') or 'small'
# Medido: 5 custa o dobro do tempo e devolve o mesmo texto.
BEAM = int(os.environ.get('IG_BEAM') or 1)
# Medido com aquecimento e 3 repetições: sequencial 2,49x · lote 8 → 4,13x · lote 16 → 4,03x.
# O lote dá 1,66x de graça, e 16 não é melhor que 8.
LOTE = int(os.environ.get('IG_LOTE') or 8)

# ── O IDIOMA É DECLARADO, NUNCA DETECTADO POR VÍDEO ─────────────────────────────
# Três segundos de abertura com música fazem o detector escolher errado, e o resto do
# vídeo sai lixo — em silêncio, com o texto parecendo normal. Medido nesta casa: dois
# reels voltaram `en` com confiança 0,37, sendo espanhóis.
#
#     IDIOMA ADIVINHADO POR VÍDEO É UM ERRO QUE NÃO AVISA.
#
# O país da CONTA é conhecido desde o lote congelado. Usar isso não é suposição — é
# usar o que já foi provado de graça na fase de identidade.
IDIOMA_DO_PAIS = {'ES': 'es', 'IT': 'it', 'FR': 'fr', 'PT': 'pt', 'BR': 'pt'}

# Teto de tempo por vídeo. Áudio repetitivo faz o decodificador entrar em laço e um lote
# noturno morre sem ninguém saber. 6x a duração é folga larga sobre os ~4x medidos.
TETO_FATOR = 6
TETO_MINIMO_S = 120


def agora():
    import datetime
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + 'Z'


def _ler(pasta, nome):
    p = os.path.join(pasta, nome)
    if not os.path.exists(p):
        return None
    with open(p, encoding='utf-8') as f:
        return json.load(f)


def _gravar(nome, corpo):
    os.makedirs(SAIDA, exist_ok=True)
    with open(os.path.join(SAIDA, nome), 'w', encoding='utf-8') as f:
        json.dump(corpo, f, ensure_ascii=False, indent=1)
    return 'data/samples/INSTAGRAM-TRANSCRICOES/' + nome


# ─────────────────────────────────────────────────────────────── quem entra na fila
def alvos():
    """Os vídeos que valem transcrever, e o motivo de cada exclusão. Custo zero.

    Excluir em silêncio é o defeito clássico: quem lê o artefato depois não sabe se o
    objeto não tinha fala ou se ninguém tentou.
    """
    objs = _ler(JANELA, 'OBJETOS.json')
    if not objs:
        print('sem OBJETOS.json — rode `py scripts/instagram_janela.py tudo` antes')
        return None, []
    dentro, fora = [], []
    for o in objs['ITEMS']:
        if o.get('IS_VIDEO') != 'YES':
            fora.append((o, 'NAO_E_VIDEO'))
            continue
        # Reel com música de catálogo costuma não ter fala: transcrever devolveria a letra
        # da música ou silêncio. Não é regra de ouro, é sinal — e por isso o objeto sai
        # marcado, não descartado.
        audio = str(o.get('AUDIO_NAME') or '')
        if audio and audio != NAO_SEI and 'riginal' not in audio:
            fora.append((o, 'AUDIO_DE_CATALOGO:%s' % audio[:30]))
            continue
        if o.get('VIDEO_URL_TEMPORARY') in (None, NAO_SEI):
            fora.append((o, 'SEM_URL_DE_VIDEO'))
            continue
        dentro.append(o)
    return objs, (dentro, fora)


def fase_alvos():
    objs, par = alvos()
    if not objs:
        return 1
    dentro, fora = par
    dur = sum(o['VIDEO_DURATION_S'] for o in dentro
              if isinstance(o.get('VIDEO_DURATION_S'), (int, float)))
    print('objetos no acervo : %d' % len(objs['ITEMS']))
    print('entram na fila    : %d  (%.1f min de áudio)' % (len(dentro), dur / 60))
    print('ficam de fora     : %d' % len(fora))
    from collections import Counter
    for motivo, n in Counter(m.split(':')[0] for _o, m in fora).most_common():
        print('    %-22s %d' % (motivo, n))
    print()
    for v in ('small', 'base', 'tiny'):
        x = {'small': 3.21, 'base': 9.36, 'tiny': 18.68}[v]
        print('  com `%-5s` em lote (%.2fx medido aqui): %.1f min de máquina'
              % (v, x, dur / x / 60))
    print()
    print('custo em dólar: 0,00 — o custo é tempo de máquina ligada.')
    return 0


# ─────────────────────────────────────────────────────────────────────── o trabalho
def _baixar(url, destino):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=120) as r, open(destino, 'wb') as f:
        f.write(r.read())
    return os.path.getsize(destino)


def _url_nova(shortcode):
    """Relê o embed para pegar uma URL de MP4 viva. Grátis, e é o conserto do vencimento."""
    import cdp
    import instagram_janela as ij
    try:
        cdp.subir(ij.PORTA, perfil=ij.PERFIL)
        aba, _h = cdp.abrir('https://www.instagram.com/p/%s/embed/captioned/' % shortcode,
                            porta=ij.PORTA, espera=4)
        try:
            e = aba.js(ij.JS_EMBED) or {}
            return e.get('VIDEO_URL')
        finally:
            aba.fechar()
    except Exception:                                        # noqa: BLE001
        return None


def _audio(shortcode, url):
    """MP4 → WAV 16 kHz mono. → (caminho, motivo_da_falha)."""
    os.makedirs(MEDIA, exist_ok=True)
    wav = os.path.join(MEDIA, '%s.wav' % shortcode)
    if os.path.exists(wav) and os.path.getsize(wav) > 1000:
        return wav, None
    mp4 = os.path.join(MEDIA, '%s.mp4' % shortcode)
    if not (os.path.exists(mp4) and os.path.getsize(mp4) > 10000):
        try:
            _baixar(url, mp4)
        except Exception as e:                               # noqa: BLE001
            # A URL assinada morreu. Reler o embed é grátis e resolve.
            nova = _url_nova(shortcode)
            if not nova:
                return None, ('URL_EXPIRADA_E_NAO_RENOVOU: %s. Isto NÃO é vídeo '
                              'inexistente — é endereço vencido.' % type(e).__name__)
            try:
                _baixar(nova, mp4)
            except Exception as e2:                          # noqa: BLE001
                return None, 'DOWNLOAD_FALHOU: %s' % type(e2).__name__
    r = subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', mp4, '-vn', '-ac', '1',
                        '-ar', '16000', '-c:a', 'pcm_s16le', wav],
                       capture_output=True, text=True)
    if r.returncode != 0 or not os.path.exists(wav):
        return None, 'FFMPEG_FALHOU: %s' % (r.stderr or '')[:120]
    return wav, None


def fase_rodar(modelo=None, teto=None):
    modelo = modelo or MODELO_PADRAO
    objs, par = alvos()
    if not objs:
        return 1
    dentro, fora = par
    if teto:
        dentro = dentro[:int(teto)]

    try:
        from faster_whisper import BatchedInferencePipeline, WhisperModel
    except ImportError:
        print('falta a biblioteca de transcrição. Instale FORA do repositório:\n'
              '  py -m pip install --target %s faster-whisper\n'
              'e rode de novo. NUNCA instalar sem --target: no Windows o pip cria '
              '`Scripts/`, que é a MESMA pasta que `scripts/`.' % LIBS)
        return 1

    nucleos = os.cpu_count() or 4
    print('modelo %s · %d núcleos · lote %d · beam %d' % (modelo, nucleos, LOTE, BEAM))
    t0 = time.time()
    m = WhisperModel(modelo, device='cpu', compute_type='int8', cpu_threads=nucleos)
    pipe = BatchedInferencePipeline(model=m)
    print('carregado em %.1f s' % (time.time() - t0))

    # Retomar de onde parou: transcrição é cara em TEMPO, e refazer o que já está pronto
    # é o mesmo desperdício que pagar duas vezes por um item.
    feito = {}
    antigo = _ler(SAIDA, 'TRANSCRICOES.json')
    if antigo:
        feito = {i['OBJECT_ID']: i for i in antigo.get('ITEMS', [])
                 if i.get('TRANSCRIPT_STATE') == 'OK'}
        print('já transcritos antes: %d (serão preservados)' % len(feito))

    itens, seg_audio, seg_maquina = [], 0.0, 0.0
    for n, o in enumerate(dentro, 1):
        sc = o['SHORTCODE']
        if sc in feito:
            itens.append(feito[sc])
            continue
        wav, motivo = _audio(sc, o['VIDEO_URL_TEMPORARY'])
        base = {
            'OBJECT_ID': sc, 'SHORTCODE': sc,
            'ACCOUNT_HANDLE': o.get('ACCOUNT_HANDLE'),
            'COMPANY': o.get('COMPANY'), 'COUNTRY_SCOPE': o.get('COUNTRY_SCOPE'),
            'SOURCE_URL': o.get('SOURCE_URL'),
            'PUBLISHED_AT': o.get('PUBLISHED_AT', NAO_SEI),
            'VIDEO_DURATION_S': o.get('VIDEO_DURATION_S', NAO_SEI),
            'AUDIO_NAME': o.get('AUDIO_NAME', NAO_SEI),
            'ASR_ENGINE': 'faster-whisper',
            'ASR_MODEL': modelo, 'ASR_BEAM': BEAM, 'ASR_BATCH': LOTE,
            'ASR_DEVICE': 'cpu/int8/%d threads' % nucleos,
            'CAPTURED_AT': agora(), 'MISSION': MISSION, 'RUNNER_NAME': RUNNER,
            'COST_USD': 0,
        }
        if not wav:
            itens.append(dict(base, **{
                'TRANSCRIPT': None, 'TRANSCRIPT_STATE': 'AUDIO_NAO_OBTIDO',
                'WHY': motivo,
                'NAO_SIGNIFICA': 'que o vídeo não tem fala. Significa que eu não ouvi.'}))
            print('  %3d/%d %-13s SEM ÁUDIO — %s' % (n, len(dentro), sc, str(motivo)[:60]))
            continue

        # O idioma vem do PAÍS DA CONTA, provado de graça na fase de identidade.
        idioma = IDIOMA_DO_PAIS.get(str(o.get('COUNTRY_SCOPE') or '').upper())
        dur = o.get('VIDEO_DURATION_S')
        teto = max(TETO_MINIMO_S,
                   int(dur * TETO_FATOR) if isinstance(dur, (int, float)) else TETO_MINIMO_S)
        t = time.time()
        try:
            segs, info = pipe.transcribe(
                wav, batch_size=LOTE, beam_size=BEAM, vad_filter=True,
                language=idioma,
                # OBRIGATÓRIO. Sem isto, áudio repetitivo (música, refrão, ruído de
                # motor) faz o decodificador se alimentar do próprio texto anterior e
                # entrar em laço: ele não erra, ele NÃO TERMINA. Medido aqui antes do
                # conserto: um vídeo de 30 s levou 112 s, e um de 47 s levou 87 s —
                # enquanto os outros faziam 3x o tempo real.
                condition_on_previous_text=False)
            segs = list(segs)
        except Exception as e:                               # noqa: BLE001
            itens.append(dict(base, **{
                'TRANSCRIPT': None, 'TRANSCRIPT_STATE': 'ASR_FALHOU',
                'WHY': '%s: %s' % (type(e).__name__, str(e)[:160]),
                'NAO_SIGNIFICA': 'que o vídeo não tem fala. O reconhecedor é que caiu.'}))
            print('  %3d/%d %-13s ASR FALHOU — %s' % (n, len(dentro), sc, type(e).__name__))
            continue
        dt = time.time() - t
        if dt > teto:
            # Passou do teto: os segmentos que vieram podem estar em laço. Marcar, nunca
            # descartar em silêncio e nunca tratar como "vídeo sem fala".
            itens.append(dict(base, **{
                'TRANSCRIPT': ' '.join(s.text.strip() for s in segs).strip() or None,
                'TRANSCRIPT_STATE': 'TRANSCRIPTION_TIMEOUT',
                'MACHINE_SECONDS': round(dt, 2), 'TIMEOUT_LIMIT_S': teto,
                'WHY': ('levou %.0fs para %.0fs de áudio (teto %ds). Texto preservado, '
                        'mas pode conter repetição em laço.' % (dt, info.duration, teto)),
                'NAO_SIGNIFICA': 'ausência de fala.'}))
            print('  %3d/%d %-13s ESTOUROU O TETO (%.0fs > %ds)' % (n, len(dentro), sc, dt, teto))
            continue
        seg_audio += info.duration
        seg_maquina += dt
        texto = ' '.join(s.text.strip() for s in segs).strip()
        itens.append(dict(base, **{
            'TRANSCRIPT': texto or None,
            'TRANSCRIPT_STATE': 'OK' if texto else 'REQUESTED_EMPTY',
            'TRANSCRIPT_CHARS': len(texto),
            # A língua é DETECTADA, não declarada — e a confiança vem junto. Abaixo de
            # 0,6 o texto pode estar sendo lido na língua errada, e isso muda tudo num
            # corpus que compara Itália, Espanha e França.
            'LANGUAGE_DETECTED': info.language,
            'LANGUAGE_CONFIDENCE': round(float(info.language_probability), 3),
            'LANGUAGE_STATE': ('CONFIAVEL' if info.language_probability >= 0.6
                               else 'BAIXA_CONFIANCA — pode estar na língua errada'),
            'AUDIO_SECONDS': round(float(info.duration), 2),
            'MACHINE_SECONDS': round(dt, 2),
            'REALTIME_FACTOR': round(info.duration / dt, 2) if dt else NAO_SEI,
            # Os tempos ficam: sem eles, uma citação não pode ser conferida contra o
            # segundo exato do vídeo, e citação que não se confere não é evidência.
            'SEGMENTS': [{'start': round(s.start, 2), 'end': round(s.end, 2),
                          'text': s.text.strip()} for s in segs],
            'SPEECH_TYPE': 'NOT_CLASSIFIED',
        }))
        print('  %3d/%d %-13s %-3s %4.2f  %5.0fs áudio em %5.0fs  %s'
              % (n, len(dentro), sc, info.language, info.language_probability,
                 info.duration, dt, (texto[:42] + '…') if texto else '(sem fala)'))

    com = sum(1 for i in itens if i.get('TRANSCRIPT_STATE') == 'OK')
    caminho = _gravar('TRANSCRICOES.json', {
        'SOURCE_ID': 'INSTAGRAM-TRANSCRICOES/TRANSCRICOES',
        'source': 'reconhecimento de fala LOCAL sobre o áudio dos vídeos públicos',
        'SOURCE_LOCATION': 'Instagram (vídeo) + máquina local (reconhecimento)',
        'FACT_LOCATION': 'NOT_KNOWN — o lugar do fato sai do conteúdo, nunca da conta',
        'EVIDENCE_CLASS': 'COMPETITOR_PUBLIC_COMMUNICATION_OBSERVED',
        'CAPTURED_AT': agora(), 'MISSION': MISSION, 'RUNNER_NAME': RUNNER,
        'APIFY_RUNS': 0, 'COST_USD': 0,
        'COST_NOTE': ('custo em dólar é zero: o reconhecimento roda nesta máquina. '
                      'O custo real é TEMPO DE MÁQUINA, e está medido abaixo.'),
        'ASR_ENGINE': 'faster-whisper', 'ASR_MODEL': modelo,
        'ASR_PARAMS': {'beam_size': BEAM, 'batch_size': LOTE,
                       'compute_type': 'int8', 'cpu_threads': nucleos,
                       'vad_filter': True},
        'OBJECTS_IN_QUEUE': len(dentro),
        'OBJECTS_EXCLUDED': len(fora),
        'EXCLUSION_REASONS': sorted({m.split(':')[0] for _o, m in fora}),
        'TRANSCRIBED_OK': com,
        'AUDIO_SECONDS_TOTAL': round(seg_audio, 1),
        'MACHINE_SECONDS_TOTAL': round(seg_maquina, 1),
        'REALTIME_FACTOR': round(seg_audio / seg_maquina, 2) if seg_maquina else NAO_SEI,
        'LEI': ('transcrição vazia é REQUESTED_EMPTY, um estado — nunca "o vídeo não tem '
                'conteúdo". E áudio não obtido é AUDIO_NAO_OBTIDO, nunca ausência de fala.'),
        'ITEMS': itens})
    print()
    print('gravado: %s' % caminho)
    print('  transcritos=%d/%d · %.1f min de áudio em %.1f min de máquina (%.2fx)'
          % (com, len(dentro), seg_audio / 60, seg_maquina / 60,
             seg_audio / seg_maquina if seg_maquina else 0))
    print('  custo=0,00 USD')
    return 0


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'alvos'
    if cmd == 'alvos':
        raise SystemExit(fase_alvos())
    if cmd == 'rodar':
        raise SystemExit(fase_rodar(sys.argv[2] if len(sys.argv) > 2 else None,
                                    sys.argv[3] if len(sys.argv) > 3 else None))
    print('uso: instagram_transcrever.py {alvos|rodar [modelo] [teto]}')
    raise SystemExit(2)
