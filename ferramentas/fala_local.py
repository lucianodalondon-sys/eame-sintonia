#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A FALA VIRA TEXTO, NESTA MÁQUINA — e este ficheiro é o ÚNICO dono disso.

    import fala_local as fl
    r = fl.transcrever('/caminho/audio.wav', idioma='it')
    r['TRANSCRIPT_STATE']   # OK · REQUESTED_EMPTY · ASR_FALHOU · TRANSCRIPTION_TIMEOUT

POR QUE ESTE FICHEIRO NASCEU, E O QUE ELE **NÃO** É
-----------------------------------------------------
Ele não é reconhecedor novo. É o reconhecedor que a casa JÁ TINHA, tirado de
dentro de dois programas de lote para poder ser CHAMADO.

Até aqui a mesma lógica vivia duas vezes:

    ferramentas/instagram_transcrever.py   ← mediu os parâmetros, em 2026-09-02
    ferramentas/youtube_transcrever.py     ← copiou-os, e o cabeçalho dele diz isso

Duas cópias da mesma lei são duas leis: no dia em que uma aprende alguma coisa, a
outra continua a errar — e ninguém sabe qual das duas produziu o texto que está a
ler. O terceiro chamador (o Reel) não podia virar a terceira cópia.

    UMA CAPACIDADE, UM DONO. O QUE FOI MEDIDO UMA VEZ MEDE-SE PARA TODOS.

Os números abaixo NÃO são meus. Foram cronometrados na máquina do SINTONIA em
2026-09-02, num reel real de 110 s, e estão aqui porque uma constante sem a
medição que a justifica volta a ser mexida por palpite.

OS QUATRO PARÂMETROS QUE CUSTARAM MEDIÇÃO
-------------------------------------------
1. **`cpu_threads` declarado.** O padrão da biblioteca usa 4 threads. Na máquina
   de 16, declarar os núcleos deu ~4x. Sem isso: 0,3x — 63 horas para mil vídeos.
2. **`beam_size=1`.** Medido: 5 custa o dobro (1,16x contra 2,31x) e devolve
   2.079 contra 2.054 caracteres praticamente idênticos.
3. **`condition_on_previous_text=False`.** OBRIGATÓRIO. Sem isto, áudio
   repetitivo (música, refrão, motor) faz o decodificador alimentar-se do próprio
   texto e entrar em laço: ele não erra, ele NÃO TERMINA.
4. **Lote de 8.** Medido com aquecimento e 3 repetições: sequencial 2,49x ·
   lote 8 → 4,13x · lote 16 → 4,03x. O lote dá 1,66x de graça, e 16 não é melhor.

O QUE ESTE FICHEIRO NUNCA DIZ
-------------------------------
Nunca diz «este vídeo não tem fala». Ele diz o que mediu:

    REQUESTED_EMPTY   pedi, corri até ao fim, e não saiu texto.
    ASR_FALHOU        o reconhecedor caiu. Não sei se havia fala.
    TRANSCRIPTION_TIMEOUT  passou do teto; o que saiu pode estar em laço.

«Não saiu texto» e «não há fala» são coisas diferentes, e a segunda é uma
afirmação sobre o vídeo que um reconhecedor não tem autoridade para fazer. O que
ele pode dar é EVIDÊNCIA — `NO_SPEECH_PROB_MEAN`, `VOICED_SEGMENTS` — para uma
camada de cima decidir. Decidir não é desta gaveta.

    AUSÊNCIA DE TEXTO != AUSÊNCIA DE FALA.

E NUNCA CLASSIFICA, NÃO RESUME, NÃO TRADUZ, NÃO DECIDE LUGAR NEM TEMPO DO FATO.
Ouvir «Puglia» num vídeo não é prova de que o fato aconteceu na Puglia — é prova
de que alguém disse «Puglia». Transcrição não é julgamento.
"""
from __future__ import annotations

import os
import re
import time

# ── A VERSÃO DESTE EXECUTOR ─────────────────────────────────────────────────
# Sobe quando muda alguma coisa que possa mudar o TEXTO. Fica no artefato para
# que dois textos diferentes do mesmo áudio se expliquem sem adivinhação.
VERSAO = '1.0.0'
MOTOR = 'faster-whisper'

NAO_SEI = 'NOT_KNOWN'

# ── OS ESTADOS, E SÃO O VOCABULÁRIO DA CASA ─────────────────────────────────
OK = 'OK'
REQUESTED_EMPTY = 'REQUESTED_EMPTY'
ASR_FALHOU = 'ASR_FALHOU'
TRANSCRIPTION_TIMEOUT = 'TRANSCRIPTION_TIMEOUT'
ASR_INDISPONIVEL = 'ASR_INDISPONIVEL'

ESTADOS = (OK, REQUESTED_EMPTY, ASR_FALHOU, TRANSCRIPTION_TIMEOUT, ASR_INDISPONIVEL)

# ── OS PADRÕES MEDIDOS ──────────────────────────────────────────────────────
MODELO_PADRAO = os.environ.get('SINTONIA_ASR_MODELO') or 'small'
BEAM = int(os.environ.get('SINTONIA_ASR_BEAM') or 1)
LOTE = int(os.environ.get('SINTONIA_ASR_LOTE') or 8)

# Teto de tempo por peça. Áudio repetitivo faz o decodificador entrar em laço e
# um lote noturno morre sem ninguém saber. 6x a duração é folga larga sobre os
# ~4x medidos.
TETO_FATOR = 6
TETO_MINIMO_S = 120

# Abaixo disto, o texto pode estar a ser lido na língua errada — e isso muda tudo
# num corpus que compara Itália, Espanha e França.
CONFIANCA_MINIMA = 0.6

# As bibliotecas pesadas vivem FORA do repositório. A memória desta casa regista
# o acidente: `pip` sem `--target` criou `C:\eame-sintonia\Scripts`, e apagar
# `Scripts` apagou `scripts` — no Windows os dois nomes são a MESMA pasta.
LIBS = os.environ.get('SINTONIA_LIBS') or os.path.join(
    os.path.expanduser('~'), '.sintonia-libs')

_CACHE = {}


def _caminho_das_libs():
    import sys
    if os.path.isdir(LIBS) and LIBS not in sys.path:
        sys.path.insert(0, LIBS)


def disponivel():
    """→ (bool, motivo). Pergunta barata, feita ANTES de prometer transcrição.

    Sem isto, quem chama descobre que falta a biblioteca já depois de ter baixado
    o vídeo — e o custo do download fica pago por nada.
    """
    _caminho_das_libs()
    try:
        import faster_whisper  # noqa: F401
    except ImportError as e:                                   # noqa: BLE001
        return False, ('falta a biblioteca de transcrição (%s). Instale FORA do '
                       'repositório:\n  py -m pip install --target %s faster-whisper'
                       % (e, LIBS))
    return True, ''


def nucleos():
    return os.cpu_count() or 4


def carimbo(modelo=None):
    """A ficha do reconhecedor, para ir dentro do artefato derivado.

    Um texto sem isto não se explica: dois textos diferentes do mesmo áudio, um
    de `tiny` e outro de `small`, ficariam indistinguíveis.
    """
    return {
        'ASR_ENGINE': MOTOR,
        'ASR_ENGINE_VERSION': _versao_do_motor(),
        'ASR_MODEL': modelo or MODELO_PADRAO,
        'ASR_BEAM': BEAM,
        'ASR_BATCH': LOTE,
        'ASR_DEVICE': 'cpu/int8/%d threads' % nucleos(),
        'ASR_VAD': 'YES',
        'ASR_CONDITION_ON_PREVIOUS_TEXT': 'NO',
        'TRANSCRIBER_ID': 'ferramentas/fala_local.py',
        'TRANSCRIBER_VERSION': VERSAO,
    }


def _versao_do_motor():
    _caminho_das_libs()
    try:
        from importlib.metadata import version
        return version('faster-whisper')
    except Exception:                                          # noqa: BLE001
        return NAO_SEI


def modelo(nome=None):
    """O modelo carregado, uma vez por processo.

    Carregar custa segundos; num lote de mil, carregar mil vezes custaria horas.
    """
    nome = nome or MODELO_PADRAO
    if nome in _CACHE:
        return _CACHE[nome]
    _caminho_das_libs()
    from faster_whisper import BatchedInferencePipeline, WhisperModel
    m = WhisperModel(nome, device='cpu', compute_type='int8', cpu_threads=nucleos())
    _CACHE[nome] = BatchedInferencePipeline(model=m)
    return _CACHE[nome]


def transcrever(wav, *, idioma=None, modelo_nome=None, duracao_s=None):
    """O áudio vira texto. → dict com o texto, o estado, os tempos e a evidência.

    `idioma` É DECLARADO QUANDO SE SABE, NUNCA ADIVINHADO POR VÍDEO
    ---------------------------------------------------------------
    Três segundos de abertura com música fazem o detector escolher errado, e o
    resto sai lixo — em silêncio, com o texto a parecer normal. Medido nesta
    casa: dois reels voltaram `en` com confiança 0,37, sendo espanhóis.

        IDIOMA ADIVINHADO POR VÍDEO É UM ERRO QUE NÃO AVISA.

    Quando o chamador SABE (porque a identidade da conta já o provou de graça),
    declara. Quando não sabe, passa `None` — e aí o campo `LANGUAGE_SOURCE` diz
    `DETECTED`, com a confiança ao lado, para quem lê poder desconfiar.
    """
    ha, porque = disponivel()
    if not ha:
        return _resposta(ASR_INDISPONIVEL, modelo_nome, erro=porque,
                         nao_significa='que o áudio não tem fala. A ferramenta é '
                                       'que não está aqui.')

    teto = max(TETO_MINIMO_S,
               int(duracao_s * TETO_FATOR) if isinstance(duracao_s, (int, float))
               else TETO_MINIMO_S)
    t0 = time.time()
    try:
        pipe = modelo(modelo_nome)
        segs, info = pipe.transcribe(
            wav, batch_size=LOTE, beam_size=BEAM, vad_filter=True,
            language=idioma,
            # OBRIGATÓRIO — ver o cabeçalho. Sem isto o decodificador não termina.
            condition_on_previous_text=False)
        # ── O TETO MORDE DURANTE, NÃO DEPOIS ────────────────────────────
        # O gerador é preguiçoso: os segmentos só são decodificados enquanto se
        # itera. Esperar o fim para depois medir o tempo deixaria um vídeo em
        # laço correr até ao fim de qualquer maneira — e um lote noturno morre
        # sem ninguém saber. Cortar AQUI é o que torna o teto uma trava e não
        # um comentário.
        trechos, truncou = [], False
        for seg in segs:
            trechos.append(seg)
            if time.time() - t0 > teto:
                truncou = True
                break
        segs = trechos
    except Exception as e:                                     # noqa: BLE001
        return _resposta(ASR_FALHOU, modelo_nome,
                         erro='%s: %s' % (type(e).__name__, str(e)[:200]),
                         maquina_s=round(time.time() - t0, 2),
                         nao_significa='que o áudio não tem fala. O reconhecedor '
                                       'é que caiu.')
    dt = time.time() - t0
    texto = ' '.join(s.text.strip() for s in segs).strip()

    # ── O TEXTO QUE NÃO É TEXTO ─────────────────────────────────────────────
    # Medido em 2026-09-10, num Reel real: sobre música sem fala o reconhecedor
    # devolveu `...` — três pontos, `TRANSCRIPT_STATE = OK`, e nada mais. Sem
    # esta trava, esses três pontos seguiriam para a camada de classificação
    # como se fossem a fala do vídeo.
    #
    # No mesmo teste, com o detetor de voz DESLIGADO, o mesmo motor devolveu
    # «Music» e «Thank you for watching!» — frases inteiras, inventadas, sobre
    # dez segundos de música corporativa.
    #
    #     ALUCINAÇÃO EM SILÊNCIO NÃO AVISA. ELA SAI COM CARA DE TEXTO NORMAL.
    #
    # A regra é mecânica e não interpreta conteúdo: sem UMA letra ou algarismo,
    # não é fala escrita. O que veio fica preservado em `DISCARDED_OUTPUT`,
    # porque apagar a prova do descarte seria trocar um defeito por outro.
    descartado = None
    if texto and not _tem_conteudo(texto):
        descartado, texto = texto, ''

    # A EVIDÊNCIA DE SILÊNCIO, e é evidência — não veredito.
    probs = [float(getattr(s, 'no_speech_prob', 0) or 0) for s in segs]
    fora = _resposta(
        OK if texto else REQUESTED_EMPTY, modelo_nome,
        texto=texto or None,
        maquina_s=round(dt, 2),
        audio_s=round(float(info.duration), 2),
        segmentos=[{'start': round(s.start, 2), 'end': round(s.end, 2),
                    'text': s.text.strip()} for s in segs],
        idioma_pedido=idioma,
        idioma_detectado=info.language,
        confianca=round(float(info.language_probability), 3),
        voiced=len(segs),
        no_speech=round(sum(probs) / len(probs), 3) if probs else NAO_SEI,
    )
    if descartado is not None:
        fora['DISCARDED_OUTPUT'] = descartado
        fora['WHY'] = ('o reconhecedor devolveu %r — sem uma letra ou algarismo. '
                       'Nao e fala escrita, e por isso nao entra como transcricao.'
                       % descartado[:60])
        fora['NAO_SIGNIFICA'] = ('que o video nao tem fala. Significa que o que saiu '
                                 'nao era texto.')

    if truncou or dt > teto:
        # Passou do teto: os segmentos que vieram podem estar em laço. Marcar,
        # nunca descartar em silêncio e nunca tratar como «vídeo sem fala».
        fora['TRANSCRIPT_STATE'] = TRANSCRIPTION_TIMEOUT
        fora['TIMEOUT_LIMIT_S'] = teto
        fora['TRUNCATED_BY_TIME'] = 'YES' if truncou else 'NO'
        fora['WHY'] = ('levou %.0fs para %.0fs de áudio (teto %ds). Texto '
                       'preservado, mas pode conter repetição em laço.'
                       % (dt, info.duration, teto))
        fora['NAO_SIGNIFICA'] = 'ausência de fala.'
    return fora


def _resposta(estado, modelo_nome, *, texto=None, maquina_s=NAO_SEI,
              audio_s=NAO_SEI, segmentos=None, idioma_pedido=None,
              idioma_detectado=NAO_SEI, confianca=NAO_SEI, voiced=NAO_SEI,
              no_speech=NAO_SEI, erro='', nao_significa=''):
    if estado not in ESTADOS:                                  # pragma: no cover
        raise ValueError('estado fora do vocabulário: %s' % estado)
    rtf = NAO_SEI
    if isinstance(audio_s, (int, float)) and isinstance(maquina_s, (int, float)) and maquina_s:
        rtf = round(audio_s / maquina_s, 2)
    fora = {
        'TRANSCRIPT': texto,
        'TRANSCRIPT_STATE': estado,
        'TRANSCRIPT_CHARS': len(texto) if texto else 0,
        # QUEM OUVIU, e com quê. Sem isto o texto não se explica.
        **carimbo(modelo_nome),
        # A LÍNGUA. `LANGUAGE_SOURCE` é o campo que impede a confusão entre
        # «eu declarei» e «a máquina achou» — são graus de prova diferentes.
        'LANGUAGE': idioma_pedido or (idioma_detectado if idioma_detectado != NAO_SEI else NAO_SEI),
        'LANGUAGE_SOURCE': 'DECLARED' if idioma_pedido else 'DETECTED',
        'LANGUAGE_DETECTED': idioma_detectado,
        'LANGUAGE_CONFIDENCE': confianca,
        'LANGUAGE_STATE': _estado_da_lingua(idioma_pedido, confianca),
        # OS TEMPOS DA MÁQUINA — não são o tempo do fato, e por isso têm nome próprio.
        'AUDIO_SECONDS': audio_s,
        'MACHINE_SECONDS': maquina_s,
        'REALTIME_FACTOR': rtf,
        # OS TEMPOS DENTRO DO ÁUDIO. Sem eles, uma citação não se confere contra
        # o segundo exato do vídeo — e citação que não se confere não é evidência.
        'SEGMENTS': segmentos or [],
        # EVIDÊNCIA DE SILÊNCIO — para quem decide, não é decisão.
        'VOICED_SEGMENTS': voiced,
        'NO_SPEECH_PROB_MEAN': no_speech,
        'SPEECH_TYPE': 'NOT_CLASSIFIED',
        # O QUE ESTA GAVETA NUNCA DECIDE.
        'FACT_LOCATION': 'NOT_KNOWN — ouvir um nome não é prova de onde o fato '
                         'aconteceu. Quem decide isso é uma camada acima.',
        'COST_USD': 0,
        'COST_NOTE': 'o custo desta rota é TEMPO DE MÁQUINA, não fatura.',
    }
    if erro:
        fora['ERROR'] = erro
    if nao_significa:
        fora['NAO_SIGNIFICA'] = nao_significa
    return fora


_RE_CONTEUDO = re.compile(r'[0-9A-Za-z\u00c0-\u024f\u0370-\u04ff]')


def _tem_conteudo(texto):
    """Ha pelo menos UMA letra ou algarismo aqui dentro?

    A classe inclui os alfabetos que este corpus toca — latino com acentos,
    grego e cirilico. Contar so `a-z` diria que «Ήταν» nao tem letras, e isso
    seria descartar fala real de um idioma inteiro.
    """
    return bool(_RE_CONTEUDO.search(texto or ''))


def _estado_da_lingua(pedido, confianca):
    if pedido:
        return 'DECLARADO — a identidade da conta já o provou de graça'
    if not isinstance(confianca, (int, float)):
        return NAO_SEI
    return ('CONFIAVEL' if confianca >= CONFIANCA_MINIMA
            else 'BAIXA_CONFIANCA — pode estar na língua errada')


# ── O ÁUDIO SAI DO VÍDEO AQUI, E SÓ AQUI ────────────────────────────────────
def extrair_audio(entrada, wav):
    """MP4/qualquer → WAV 16 kHz mono. → (caminho, motivo_da_falha).

    16 kHz mono não é gosto: é o que o modelo espera. Entregar 48 kHz estéreo
    faz a biblioteca reamostrar por dentro, mais devagar e sem dizer.
    """
    import subprocess
    os.makedirs(os.path.dirname(os.path.abspath(wav)) or '.', exist_ok=True)
    if os.path.exists(wav) and os.path.getsize(wav) > 1000:
        return wav, None
    try:
        r = subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', entrada, '-vn',
                            '-ac', '1', '-ar', '16000', '-c:a', 'pcm_s16le', wav],
                           capture_output=True, text=True, timeout=900)
    except FileNotFoundError:
        return None, ('FFMPEG_AUSENTE: o extrator de áudio não está instalado '
                      'nesta máquina. Isto NÃO é vídeo sem som.')
    except Exception as e:                                     # noqa: BLE001
        return None, 'FFMPEG_FALHOU: %s' % type(e).__name__
    if r.returncode != 0 or not os.path.exists(wav) or os.path.getsize(wav) <= 1000:
        return None, 'FFMPEG_FALHOU: %s' % (r.stderr or '')[:160]
    return wav, None


def duracao(caminho):
    """Segundos de mídia, medidos — nunca estimados pelo tamanho do ficheiro."""
    import subprocess
    try:
        r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries',
                            'format=duration', '-of', 'csv=p=0', caminho],
                           capture_output=True, text=True, timeout=120)
        return round(float(r.stdout.strip()), 2)
    except Exception:                                          # noqa: BLE001
        return NAO_SEI


if __name__ == '__main__':
    import json
    import sys
    ha, porque = disponivel()
    print('MOTOR              = %s %s' % (MOTOR, _versao_do_motor()))
    print('DISPONIVEL         = %s%s' % ('YES' if ha else 'NO',
                                         '' if ha else ' — ' + porque))
    print('NUCLEOS            = %d' % nucleos())
    print('MODELO_PADRAO      = %s' % MODELO_PADRAO)
    print('PARAMETROS MEDIDOS = beam=%d lote=%d vad=YES condition=NO' % (BEAM, LOTE))
    if len(sys.argv) > 1:
        alvo = sys.argv[1]
        idi = sys.argv[2] if len(sys.argv) > 2 else None
        if not alvo.lower().endswith('.wav'):
            novo = os.path.splitext(alvo)[0] + '.wav'
            alvo, motivo = extrair_audio(alvo, novo)
            if not alvo:
                print('SEM AUDIO: %s' % motivo)
                raise SystemExit(1)
        r = transcrever(alvo, idioma=idi, duracao_s=duracao(alvo))
        r.pop('SEGMENTS', None)
        print(json.dumps(r, ensure_ascii=False, indent=1))
