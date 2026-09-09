#!/usr/bin/env python3
"""
TRANSCRIÇÃO DE STORY — o transcritor que recebe o byte, e não sabe buscá-lo.

    from story_transcrever import transcrever
    r = transcrever('data/.../STORY-conta-123.mp4')

POR QUE UM PONTO DE ENTRADA NOVO, E NÃO UM `if` NO TRANSCRITOR DE REEL
------------------------------------------------------------------------
`instagram_transcrever.py` é ótimo e continua o dono do modelo. Mas ele é
indexado por `shortcode`, e a sua recuperação de URL vencida relê o EMBED
público do post. Story não tem shortcode e não tem embed: forçar Story a fingir
ser Reel para caber ali colocaria, no caminho de recuperação, uma chamada que
para Story SEMPRE falha — e falharia em silêncio, devolvendo «sem áudio» para
um vídeo que tinha fala.

A separação é a correção mínima e ela é conceitual, não cosmética:

    AQUISIÇÃO DA MÍDIA   é de quem conhece a plataforma e o prazo
    TRANSCRIÇÃO          é de quem tem o arquivo na mão

Este arquivo faz só o segundo. Ele não baixa, não renova URL, não conhece
Instagram. Se o arquivo não está no disco, a resposta é `MEDIA_MISSING` — e
isso é um estado sobre a NOSSA cadeia, nunca sobre a fala da pessoa.

O IDIOMA NÃO SE ADIVINHA PELO PAÍS
------------------------------------
O transcritor de Reel passa `language=` derivado do `COUNTRY_SCOPE`, o que é
razoável num lote de um país só. Para Story de pesquisador não é: um agrônomo
italiano fala inglês num congresso, e um espanhol legenda em italiano. Aqui o
idioma é o que o modelo DETECTOU, com a probabilidade junto — e se a confiança
for baixa, o campo continua sendo o que o modelo disse, com o número ao lado
para quem ler decidir.

    IDIOMA DETECTADO != IDIOMA DO PAÍS DA CONTA.

E o resultado é DERIVED, sempre:

    RAW MEDIA != TRANSCRIPT.
"""
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(HERE)
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401

MODELO_PADRAO = os.environ.get('STORY_MODELO') or 'small'

OK = 'OK'
MEDIA_MISSING = 'MEDIA_MISSING'
NO_AUDIO_TRACK = 'NO_AUDIO_TRACK'
FFMPEG_FALHOU = 'FFMPEG_FALHOU'
ASR_INDISPONIVEL = 'ASR_INDISPONIVEL'
ASR_FALHOU = 'ASR_FALHOU'


def _resultado(estado, **extra):
    base = {'TRANSCRIPT_STATE': estado, 'TRANSCRIPT': None, 'LANGUAGE': None,
            'LANGUAGE_PROBABILITY': None, 'DURATION_S': None,
            'LOCAL_COMPUTE_S': None, 'USD_COST': 0.0,
            'DERIVED_FROM': None, 'MODEL': None}
    base.update(extra)
    return base


def extrair_audio(caminho_midia, wav=None):
    """MP4 -> WAV 16 kHz mono. (caminho, estado). Não levanta."""
    if not caminho_midia or not os.path.exists(caminho_midia):
        return None, MEDIA_MISSING
    wav = wav or (os.path.splitext(caminho_midia)[0] + '.wav')
    if os.path.exists(wav) and os.path.getsize(wav) > 1000:
        return wav, OK
    r = subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', caminho_midia,
                        '-vn', '-ac', '1', '-ar', '16000', '-c:a', 'pcm_s16le', wav],
                       capture_output=True, text=True)
    if r.returncode != 0 or not os.path.exists(wav) or os.path.getsize(wav) < 1000:
        erro = (r.stderr or '').lower()
        # Vídeo mudo é um FATO sobre o Story. Ferramenta quebrada é um fato
        # sobre nós. Juntar os dois faria «não tinha fala» esconder «não rodou».
        if 'does not contain any stream' in erro or 'no audio' in erro:
            return None, NO_AUDIO_TRACK
        return None, FFMPEG_FALHOU
    return wav, OK


def transcrever(caminho_midia, modelo=None):
    """O arquivo já adquirido vira texto. Devolve sempre um dicionário de estado."""
    modelo = modelo or MODELO_PADRAO
    wav, estado = extrair_audio(caminho_midia)
    if estado != OK:
        return _resultado(estado, DERIVED_FROM=caminho_midia)

    try:
        from faster_whisper import WhisperModel
    except ImportError:
        # A ausência da biblioteca é um fato sobre a MÁQUINA, e ele não pode
        # virar «o Story não tinha fala».
        return _resultado(ASR_INDISPONIVEL, DERIVED_FROM=caminho_midia,
                          MODEL=modelo)

    t0 = time.time()
    try:
        m = WhisperModel(modelo, device='cpu', compute_type='int8',
                         cpu_threads=os.cpu_count() or 4)
        segs, info = m.transcribe(
            wav, beam_size=5, vad_filter=True,
            # Sem isto, áudio repetitivo faz o decodificador se alimentar do
            # próprio texto e entrar em laço: ele não erra, ele NÃO TERMINA.
            # A lei é do transcritor de Reel desta casa, e continua valendo.
            condition_on_previous_text=False)
        texto = ' '.join(s.text.strip() for s in segs).strip()
    except Exception as e:                                   # noqa: BLE001
        return _resultado(ASR_FALHOU, DERIVED_FROM=caminho_midia, MODEL=modelo,
                          WHY='%s: %s' % (type(e).__name__, str(e)[:160]),
                          NAO_SIGNIFICA='que o Story não tem fala. O reconhecedor caiu.')

    return _resultado(
        OK, TRANSCRIPT=texto or '',
        # O que o MODELO detectou. Nunca o idioma do país da conta.
        LANGUAGE=getattr(info, 'language', None),
        LANGUAGE_PROBABILITY=getattr(info, 'language_probability', None),
        DURATION_S=getattr(info, 'duration', None),
        LOCAL_COMPUTE_S=round(time.time() - t0, 2),
        USD_COST=0.0,                # local: zero dólar. Tempo de máquina é outro campo.
        DERIVED_FROM=caminho_midia, MODEL=modelo)


def anexar(objeto_story, modelo=None):
    """Transcreve o vídeo já preservado e pendura o DERIVED no objeto Story."""
    if objeto_story.get('MEDIA_TYPE') != 'VIDEO':
        return objeto_story
    if objeto_story.get('MEDIA_DURABILITY') != 'MEDIA_PRESERVED':
        # Sem byte preservado não há o que transcrever, e enfileirar para
        # «depois» é justamente o que não funciona com Story.
        objeto_story['DERIVED_TRANSCRIPT'] = _resultado(MEDIA_MISSING)
        return objeto_story
    caminho = os.path.join(RAIZ, objeto_story['MEDIA_PATH'])
    objeto_story['DERIVED_TRANSCRIPT'] = transcrever(caminho, modelo=modelo)
    return objeto_story
