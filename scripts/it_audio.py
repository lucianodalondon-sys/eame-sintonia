#!/usr/bin/env python3
"""
CAMADA DE ÁUDIO ITÁLIA — a fala que não tem legenda para comparar.

    py scripts/it_audio.py descobrir     # quem publica, com data e duração
    py scripts/it_audio.py transcrever   # baixa, converte e transcreve LOCALMENTE
    py scripts/it_audio.py              # as duas

POR QUE ESTA ROTA EXISTE, DEPOIS DE O INSTAGRAM TER FALHADO
-------------------------------------------------------------
Três lotes de Instagram foram coletados nesta missão e a medição foi sempre a mesma:

    sinal SÓ NA FALA    V1 5/28    V2 2/15    V3 0/5

O veredito ficou escrito: `ROUTE_OPEN_CONTENT_LOW_YIELD`. A rota abre, é barata e
permanente — e o conteúdo italiano de Instagram deste acervo não carrega sinal de
campo. O reel dura 30 segundos e fala de instituição.

O podcast agronômico é o oposto: 20 a 40 minutos, com pesquisador, técnico e produtor
no mesmo áudio, e uma descrição de duas linhas. Foi o que a primeira leva mediu no
Agricast — 9 episódios, 151,7 minutos, 130.935 caracteres de fala, e o sinal estava
SÓ NA FALA por construção, porque não existe legenda para comparar.

    ÁUDIO SEM LEGENDA NÃO É `TRANSCRIPT_ONLY` POR MÉRITO. É POR AUSÊNCIA DE ALTERNATIVA.
    A comparação honesta é entre FALA e DESCRIÇÃO DO EPISÓDIO, e é isso que se mede aqui.

AS DUAS ROTAS, E O QUE CADA UMA RENDEU
----------------------------------------
ROTA A · API pública do Spreaker, sem chave: `api.spreaker.com/v2/shows/<id>/episodes`.
         Entrega título, descrição, data, duração e a URL do MP3. É a rota boa.

ROTA B · feed do site → página do artigo → arquivo de mídia hospedado pela própria casa.
         Medida nesta sessão em 4 sites italianos e 37 artigos: DOIS artigos com mídia,
         e três das quatro peças eram embed de YouTube, que a rota de vídeo já cobre.
         Fica registrada com o rendimento medido, e não com o rendimento esperado.

O QUE ESTE ARQUIVO NÃO FAZ
----------------------------
Não decide janela, não promove nada e não fala com o portal. Transcrição é EVIDÊNCIA,
e o que ela sustenta é decidido na camada de cruzamento, com a régua de lá.
"""
import json
import os
import re
import subprocess
import sys
import time
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
# O mesmo endereco de biblioteca que instagram_sem_navegador.py usa. Uma casa, um lugar.
LIBS = os.environ.get('SINTONIA_LIBS') or os.path.join(os.path.expanduser('~'), '.sintonia-libs')
if os.path.isdir(LIBS):
    sys.path.insert(0, LIBS)

SAIDA = os.path.join(ROOT, 'data', 'samples', 'IT-VOZ-AUDIO-V2')
CACHE = os.path.join(SAIDA, 'audio-cache')
CAPTURA = os.environ.get('IT_AUDIO_DATA') or '2026-09-03'
JANELA = os.environ.get('IT_AUDIO_JANELA') or '2026-06-05'   # 90 dias
UA = ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
      'Chrome/141.0.0.0 Safari/537.36')
NAO_SEI = 'NAO_SEI'

# ── OS PROGRAMAS, DECLARADOS ───────────────────────────────────────────────────
# DECLARED_ROLE nunca é inferido do conteúdo. Ele vem de quem publica, lido no próprio
# canal. A razão ADAMA é escrita ANTES da coleta — se ela não se sustenta, o programa
# não entra, mesmo que o áudio seja bom.
PROGRAMAS = [
    {'SHOW_ID': 6623075, 'NAME': 'Terra di Denari',
     'DECLARED_ROLE': 'AGRICULTURAL_TRADE_MEDIA',
     'REGION': 'ITALIA',
     'CROPS': ['FRUMENTO', 'VITE', 'OLIVO'],
     'ADAMA_REASON': ('programa de cadeia agrícola com episódios de ~30 min e publicação viva '
                      'em 2026. Entra pelo formato: meia hora de fala é onde cabe a frase '
                      'técnica que um reel de 30 segundos nunca comporta.')},
    {'SHOW_ID': 7026131, 'NAME': 'AGRINET4TECH: storie di sostenibilità',
     'DECLARED_ROLE': 'INNOVATION_NETWORK_PODCAST',
     'REGION': 'ITALIA (episódios por território)',
     'CROPS': ['FRAGOLA', 'BASILICO', 'POMODORO', 'MAIS'],
     'ADAMA_REASON': ('cada episódio é um TERRITÓRIO nomeado — Metapontino e a fragola, '
                      'Ponente Ligure e o basilico, Delta do Pó, Piana di Sibari, Bassa '
                      'Mantovana. Geografia declarada pelo próprio programa é exatamente o que '
                      'falta na maior parte da voz pública: sinal sem lugar não cruza com nada.')},
    {'SHOW_ID': 4600385, 'NAME': 'Cia Umbria Agripodcast',
     'DECLARED_ROLE': 'PRODUCER_ORGANISATION_VOICE',
     'REGION': 'Umbria',
     'CROPS': ['OLIVO', 'VITE', 'TABACCO', 'FRUMENTO'],
     'ADAMA_REASON': ('é a voz de uma organização de produtores, e a Umbria não aparece em '
                      'nenhuma das 37 oportunidades do radar. Entra como CONTRASTE DELIBERADO: '
                      'sem uma região de fora, "a fonte fala das regiões da ADAMA" é uma '
                      'afirmação sem controle.')},
]

# Medidos e DEIXADOS DE FORA, com o motivo — que é sempre uma data, e não uma opinião.
FORA_POR_MEDICAO = [
    {'SHOW_ID': 5619070, 'NAME': 'MINUTI DI RISO (BASF Agricultural Solutions Italia)',
     'STATE': 'CONGELADO',
     'MEASURED': ('último episódio 2023-12-07, intitulado "28 - Arrivederci". O programa se '
                  'despediu. 28 episódios existem e são passado.'),
     'WHY_IT_MATTERS': ('a ficha IT-SRCX-080 registra este podcast como canal de concorrente e '
                        'dizia UPDATE_FREQUENCY=PERIODIC. A medição corrige para STATIC: é '
                        'acervo histórico da BASF sobre Clearfield e Provisia, não um canal '
                        'vivo. Ver a correção FIX-03 em scripts/it_fontes.py.')},
    {'SHOW_ID': 5837404, 'NAME': 'Lezioni di Vite',
     'STATE': 'CONGELADO_MAS_TEMATICAMENTE_EXATO',
     'MEASURED': 'último episódio em 2023; títulos como "Peronospora della vite, come e quando intervenire".',
     'WHY_IT_MATTERS': ('assunto perfeito, relógio parado. Fica registrado para colheita '
                        'histórica, e NÃO entra na janela corrente — misturar as duas coisas é '
                        'como uma fonte de 1995 vira "tendência de 2026".')},
    {'SHOW_ID': 6634834, 'NAME': 'La settimana del riso',
     'STATE': 'CONGELADO', 'MEASURED': 'último episódio 2025-07-26.',
     'WHY_IT_MATTERS': 'RISO é o eixo de ECHINOCHLOA; o canal semanal que existia parou há mais de um ano.'},
    {'SHOW_ID': 6411513, 'NAME': 'Just Agronomo Podcast',
     'STATE': 'CONGELADO', 'MEASURED': 'último episódio 2024-12-24.'},
]

# ROTA B · sites que hospedam a própria mídia. O rendimento medido está no artefato.
SITES_MIDIA_PROPRIA = [
    {'NAME': 'AIPP', 'FEED': 'https://www.aipp.it/feed/'},
    {'NAME': 'OlivoNews', 'FEED': 'https://www.olivonews.it/feed/'},
    {'NAME': 'Terra e Vita (Edagricole)', 'FEED': 'https://terraevita.edagricole.it/feed/'},
    {'NAME': 'Consorzio Fitosanitario di Parma', 'FEED': 'https://www.fitosanitario.pr.it/feed/'},
]


def _get(url, timeout=60, binario=False, json_=False):
    req = urllib.request.Request(url, headers={
        'User-Agent': UA, 'Accept-Language': 'it-IT,it;q=0.9',
        'Accept': 'application/json' if json_ else '*/*',
        'Accept-Encoding': 'identity'})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        b = r.read()
        if json_:
            return json.loads(b)
        return b if binario else b.decode('utf-8', 'replace')


def escrever(nome, corpo):
    os.makedirs(SAIDA, exist_ok=True)
    corpo.setdefault('SOURCE_ID', 'IT-VOZ-AUDIO-V2')
    corpo.setdefault('CAPTURED_AT', CAPTURA)
    p = os.path.join(SAIDA, nome)
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(corpo, f, ensure_ascii=False, indent=1)
    return p


# ── FASE 1 · DESCOBRIR ─────────────────────────────────────────────────────────
def fase_descobrir():
    eps, falhas = [], []
    for pr in PROGRAMAS:
        try:
            d = _get('https://api.spreaker.com/v2/shows/%d/episodes?limit=50' % pr['SHOW_ID'],
                     json_=True)
        except Exception as e:
            falhas.append({'SHOW_ID': pr['SHOW_ID'], 'ERRO': str(e)[:200]})
            print('  %-34s ERRO %s' % (pr['NAME'][:34], str(e)[:60]))
            continue
        itens = d['response'].get('items', [])
        na_janela = [e for e in itens if (e.get('published_at') or '')[:10] >= JANELA]
        for e in na_janela:
            eps.append({
                'EXTERNAL_ID': str(e['episode_id']),
                'PLATFORM': 'SPREAKER',
                'SHOW_ID': pr['SHOW_ID'],
                'ORIGIN': pr['NAME'],
                'DECLARED_ROLE': pr['DECLARED_ROLE'],
                'REGION_DECLARED': pr['REGION'],
                'ADAMA_RELEVANCE_REASON': pr['ADAMA_REASON'],
                'TITLE': e.get('title') or NAO_SEI,
                'DESCRIPTION': (e.get('description') or '').strip(),
                'PUBLICATION_DATE': (e.get('published_at') or '')[:10] or NAO_SEI,
                'DURATION_S': round((e.get('duration') or 0) / 1000),
                'AUDIO_URL': e.get('download_url') or e.get('playback_url') or NAO_SEI,
                'PAGE_URL': e.get('site_url') or NAO_SEI,
                'COUNTRY': 'ITALY',
                'ORIGINAL_LANGUAGE': 'it',
                'LANGUAGE_LAW': 'declarado, NUNCA detectado',
            })
        print('  %-34s %2d na janela de %2d publicados' % (pr['NAME'][:34], len(na_janela), len(itens)))
    corpo = {
        'DATASET': 'IT-VOZ-AUDIO-DESCOBERTA-V2',
        'LAYER': 'VOICE_AUDIO_ITALY',
        'COUNTRY': 'IT',
        'SOURCE': ('API pública do Spreaker (api.spreaker.com/v2), sem chave e sem raspagem. '
                   'Programas DECLARADOS em scripts/it_audio.py, com a razão ADAMA escrita antes '
                   'da coleta.'),
        'WINDOW_FROM': JANELA,
        'WINDOW_LAW': ('a janela é de 90 dias. Episódio fora dela NÃO entra, mesmo quando o '
                       'assunto é melhor — misturar relógios é como um trabalho de 1995 vira '
                       '"tendência de 2026".'),
        'SHOWS_DECLARED': len(PROGRAMAS),
        'EPISODES_IN_WINDOW': len(eps),
        'AUDIO_SECONDS_IN_WINDOW': sum(e['DURATION_S'] for e in eps),
        'FETCH_FAILURES': falhas,
        'MEASURED_AND_LEFT_OUT': FORA_POR_MEDICAO,
        'EPISODES': eps,
    }
    p = escrever('IT-VOZ-AUDIO-DESCOBERTA-V2.json', corpo)
    print('\n%d episódios · %d min de áudio na janela' % (len(eps), corpo['AUDIO_SECONDS_IN_WINDOW'] // 60))
    print('escrito: %s' % os.path.relpath(p, ROOT))
    return 0


# ── FASE 2 · TRANSCREVER ───────────────────────────────────────────────────────
def _wav(mp3, wav):
    r = subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', mp3, '-vn', '-ac', '1',
                        '-ar', '16000', wav], capture_output=True)
    return r.returncode == 0 and os.path.exists(wav) and os.path.getsize(wav) > 1024


def fase_transcrever():
    d = json.load(open(os.path.join(SAIDA, 'IT-VOZ-AUDIO-DESCOBERTA-V2.json'), encoding='utf-8'))
    eps = d['EPISODES']
    if not eps:
        print('nada a transcrever'); return 0
    try:
        from faster_whisper import BatchedInferencePipeline, WhisperModel
    except ImportError:
        print('faster-whisper ausente. NÃO transcrevo, e NÃO invento transcrição.')
        return 1
    # Mesmo motor e mesma configuração de scripts/instagram_sem_navegador.py. Uma casa, um
    # motor: se a velocidade mudar, muda para as duas rotas ao mesmo tempo.
    nucleos = os.cpu_count() or 4
    modelo = os.environ.get('IT_AUDIO_MODELO') or 'small'
    print('modelo %s · %d núcleos · idioma it DECLARADO (nunca detectado)' % (modelo, nucleos))
    m = WhisperModel(modelo, device='cpu', compute_type='int8', cpu_threads=nucleos)
    pipe = BatchedInferencePipeline(model=m)
    os.makedirs(CACHE, exist_ok=True)

    # Retomada: episódio já transcrito com sucesso é PRESERVADO e não roda de novo. Uma hora
    # de máquina desperdiçada não é neutra — ela desencoraja a próxima execução.
    feitos = {}
    antes = os.path.join(SAIDA, 'IT-VOZ-AUDIO-TRANSCRICOES-V2.json')
    if os.path.exists(antes):
        feitos = {r['EXTERNAL_ID']: r for r in json.load(open(antes, encoding='utf-8'))['RECORDS']
                  if r.get('TRANSCRIPT_STATE') == 'OK'}
        if feitos:
            print('já transcritos antes: %d (preservados)' % len(feitos))

    import voz
    registros, audio_s, maq_s = [], 0, 0
    for i, e in enumerate(eps, 1):
        eid = e['EXTERNAL_ID']
        if eid in feitos:
            registros.append(feitos[eid])
            audio_s += e['DURATION_S']
            print('  [%2d/%2d] %-10s PRESERVADO' % (i, len(eps), eid))
            continue
        mp3 = os.path.join(CACHE, eid + '.mp3')
        wav = os.path.join(CACHE, eid + '.wav')
        t0 = time.time()
        try:
            if not os.path.exists(wav):
                if not os.path.exists(mp3):
                    with open(mp3, 'wb') as fh:
                        fh.write(_get(e['AUDIO_URL'], timeout=300, binario=True))
                if not _wav(mp3, wav):
                    raise RuntimeError('ffmpeg falhou')
            segs, _info = pipe.transcribe(wav, language='it', beam_size=1, batch_size=8)
            texto = ' '.join(s.text.strip() for s in segs).strip()
        except Exception as ex:
            registros.append(dict(e, TRANSCRIPT='', TRANSCRIPT_STATE='FAILED_WITH_REASON',
                                  FAILURE=str(ex)[:200]))
            print('  [%2d/%2d] %-10s FALHOU  %s' % (i, len(eps), eid, str(ex)[:50]))
            continue
        dt = time.time() - t0
        audio_s += e['DURATION_S']; maq_s += dt
        r = dict(e)
        r.update({
            'TRANSCRIPT': texto,
            'TRANSCRIPT_CHARS': len(texto),
            'TRANSCRIPT_STATE': 'OK' if len(texto) > 200 else 'REQUESTED_EMPTY',
            'TRANSCRIPT_ENGINE': 'faster-whisper %s int8 cpu beam=1 lang=it (LOCAL, 0,00 USD)' % modelo,
            'CAPTION_SOURCE': 'SINTONIA_WHISPER_LOCAL',
            'COLLECTION_DATE': CAPTURA,
        })
        # Assunto lido DUAS VEZES com o mesmo vocabulário italiano: uma só com título e
        # descrição, outra incluindo a fala. A diferença entre as duas é a única coisa que
        # justifica o custo de transcrever — e é medida, não afirmada.
        sem_fala = voz.marcar_assunto({'TITLE': e['TITLE'], 'DESCRIPTION': e['DESCRIPTION']},
                                      vocab_crop=voz.VOCAB_CROP_IT, vocab_issue=voz.VOCAB_ISSUE_IT)
        com_fala = voz.marcar_assunto({'TITLE': e['TITLE'], 'DESCRIPTION': e['DESCRIPTION'],
                                       'TRANSCRIPT': texto},
                                      vocab_crop=voz.VOCAB_CROP_IT, vocab_issue=voz.VOCAB_ISSUE_IT,
                                      ler_transcricao=True)
        r = voz.marcar_molecula_e_lugar(r, vocab_molecule=voz.VOCAB_MOLECULE_IT,
                                        vocab_lugar=voz.VOCAB_LUGAR_IT, ler_transcricao=True)
        r['CROP_FROM_DESCRIPTION'] = sem_fala.get('CROP', NAO_SEI)
        r['ISSUE_FROM_DESCRIPTION'] = sem_fala.get('ISSUE', NAO_SEI)
        r['CROP_WITH_TRANSCRIPT'] = com_fala.get('CROP', NAO_SEI)
        r['ISSUE_WITH_TRANSCRIPT'] = com_fala.get('ISSUE', NAO_SEI)
        novos = [k for k in ('CROP', 'ISSUE')
                 if com_fala.get(k) and com_fala.get(k) != sem_fala.get(k)]
        r['SUBJECT_ONLY_IN_TRANSCRIPT'] = novos
        r['SIGNAL_ONLY_IN_TRANSCRIPT'] = 'YES' if novos else 'NO'
        registros.append(r)
        print('  [%2d/%2d] %-10s %-6s %6.0fs %5.2fx %7d car.  só-na-fala=%s'
              % (i, len(eps), eid, r['TRANSCRIPT_STATE'], dt,
                 (e['DURATION_S'] / dt) if dt else 0, len(texto), r['SIGNAL_ONLY_IN_TRANSCRIPT']))

    ok = [r for r in registros if r.get('TRANSCRIPT_STATE') == 'OK']
    so = sum(1 for r in ok if r['SIGNAL_ONLY_IN_TRANSCRIPT'] == 'YES')
    corpo = {
        'DATASET': 'IT-VOZ-AUDIO-TRANSCRICOES-V2',
        'LAYER': 'VOICE_AUDIO_ITALY',
        'COUNTRY': 'IT',
        'SOURCE': ('MP3 público do Spreaker, convertido com ffmpeg e transcrito LOCALMENTE com '
                   'o mesmo faster-whisper de scripts/instagram_transcrever.py. Nenhuma chave, '
                   'nenhum serviço externo, 0,00 USD.'),
        'ENGINE': 'faster-whisper %s int8 cpu · idioma it DECLARADO' % modelo,
        'WHY_LANGUAGE_IS_DECLARED': ('detecção automática de idioma erra em áudio curto e em '
                                     'fala com termo técnico estrangeiro, e o erro entra no '
                                     'texto sem aviso. O idioma vem do canal, que o declara.'),
        'COST_USD': 0,
        'ITEMS': len(registros),
        'OK': len(ok),
        'AUDIO_SECONDS': audio_s,
        'MACHINE_SECONDS': round(maq_s),
        'TRANSCRIPT_CHARS': sum(r.get('TRANSCRIPT_CHARS', 0) for r in registros),
        'SIGNAL_ONLY_IN_TRANSCRIPT': so,
        'WHAT_THE_MEASURE_MEANS': ('assunto (cultura ou avversità do vocabulário italiano) que '
                                   'aparece na FALA e NÃO aparece na descrição do episódio. É a '
                                   'única medida que justifica o custo de transcrever.'),
        'WHAT_IT_DOES_NOT_MEAN': ('não é sinal de campo verificado, não tem limiar e não '
                                  'promove nada. É evidência para a camada de cruzamento.'),
        'RECORDS': registros,
    }
    p = escrever('IT-VOZ-AUDIO-TRANSCRICOES-V2.json', corpo)
    print('\n%d transcritos · %ds de áudio · %ds de máquina · %d caracteres · custo 0,00 USD'
          % (len(ok), audio_s, round(maq_s), corpo['TRANSCRIPT_CHARS']))
    print('sinal SÓ NA FALA em %d de %d' % (so, len(ok)))
    print('escrito: %s' % os.path.relpath(p, ROOT))
    return 0


# ── ROTA B · mídia hospedada pela própria casa ─────────────────────────────────
def fase_rota_b():
    achados, artigos = [], 0
    for s in SITES_MIDIA_PROPRIA:
        try:
            x = _get(s['FEED'])
        except Exception as e:
            achados.append({'SITE': s['NAME'], 'STATE': 'FEED_NOT_REACHED', 'REASON': str(e)[:160]})
            print('  %-34s feed NÃO ALCANÇADO' % s['NAME'][:34]); continue
        links = [l for l in re.findall(r'<link>\s*([^<\s]+)\s*</link>', x) if '/feed' not in l][:14]
        com = 0
        for l in links:
            artigos += 1
            try:
                h = _get(l)
            except Exception:
                continue
            med = {m for m in re.findall(r'https?://[^"\'<> ]+\.(?:mp3|m4a|mp4)', h)
                   if 'logo' not in m and 'icon' not in m}
            yt = set(re.findall(r'(?:youtube\.com/embed/|youtu\.be/)([A-Za-z0-9_-]{11})', h))
            if med or yt:
                com += 1
                achados.append({'SITE': s['NAME'], 'ARTICLE': l,
                                'SELF_HOSTED_MEDIA': sorted(med), 'YOUTUBE_EMBEDS': sorted(yt)})
        print('  %-34s %2d artigos · %d com mídia' % (s['NAME'][:34], len(links), com))
    corpo = {
        'DATASET': 'IT-VOZ-ROTA-B-V2',
        'SOURCE': 'feed RSS de cada site → página do artigo → arquivo de mídia, lido por mim',
        'ARTICLES_READ': artigos,
        'ARTICLES_WITH_MEDIA': len([a for a in achados if a.get('ARTICLE')]),
        'THE_HONEST_YIELD': ('esta rota foi desenhada esperando áudio próprio de casa italiana e '
                             'entregou pouco. O número acima é o rendimento MEDIDO, e não o '
                             'esperado. A maior parte do que existe é embed de YouTube, que a '
                             'rota de vídeo (scripts/it_video.py) já cobre.'),
        'FINDINGS': achados,
    }
    p = escrever('IT-VOZ-ROTA-B-V2.json', corpo)
    print('\n%d artigos lidos · escrito: %s' % (artigos, os.path.relpath(p, ROOT)))
    return 0


FASES = {'descobrir': fase_descobrir, 'transcrever': fase_transcrever, 'rota-b': fase_rota_b}

if __name__ == '__main__':
    arg = sys.argv[1] if len(sys.argv) > 1 else 'tudo'
    if arg == 'tudo':
        for nome in ('descobrir', 'rota-b', 'transcrever'):
            print('\n=== %s ===' % nome)
            if FASES[nome]():
                sys.exit(1)
        sys.exit(0)
    if arg not in FASES:
        print(__doc__); sys.exit(2)
    sys.exit(FASES[arg]())
