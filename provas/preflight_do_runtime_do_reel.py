#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PREFLIGHT DO RUNTIME DA CADEIA DE REEL — uma pergunta, seis respostas.

    py -3.12 provas/preflight_do_runtime_do_reel.py

POR QUE ISTO EXISTE
-------------------
Uma sessão inteira foi gasta a descobrir, por tentativa, que o descarregador e o
reconhecedor viviam em runtimes diferentes e que o modelo declarado para Reel
(`medium`) não estava na cache. Nada disso era invisível: era **não medido**.

    O QUE UMA SESSÃO DESCOBRIU À MÃO, A SEGUINTE MEDE EM DOIS SEGUNDOS.

Ele NÃO instala nada, NÃO baixa nada e NÃO sai à rede. Baixar modelo durante uma
corrida de coleta seria trocar uma falha visível por um atraso imprevisível.

    MODELO CONFIGURADO != MODELO DISPONIVEL.

O segundo é um ficheiro em disco. É esse que decide se a fala sai.
"""
import os
import shutil
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in ('ferramentas', 'leis', 'coleta'):
    sys.path.insert(0, os.path.join(RAIZ, _p))

FALHAS = []


def diz(chave, ok, valor):
    print('%-26s %s%s' % (chave, valor, '' if ok else '   ← FALHA'))
    if not ok:
        FALHAS.append(chave)


def _modelo_em_cache(nome):
    """→ (esta?, onde). Olha o disco da cache do HuggingFace. Zero rede."""
    base = os.environ.get('HF_HOME') or os.path.join(
        os.path.expanduser('~'), '.cache', 'huggingface', 'hub')
    alvo = 'models--Systran--faster-whisper-%s' % nome
    caminho = os.path.join(base, alvo)
    return os.path.isdir(caminho), base


def main():
    print('=' * 74)
    print('PREFLIGHT DO RUNTIME — INSTAGRAM REEL (audio-only -> ASR)')
    print('=' * 74)
    print('PYTHON_VERSION             %s' % sys.version.split()[0])

    import fala_local as fl

    # ── O MODELO DECLARADO PARA ESTE CHAMADOR, E A POLITICA NAO SE ESCREVE AQUI
    chamador = 'reel'
    modelo = fl.modelo_de(chamador)

    # ── 1 · AS FERRAMENTAS
    ytdlp = shutil.which('yt-dlp')
    ffmpeg = shutil.which('ffmpeg')
    ffprobe = shutil.which('ffprobe')
    diz('YTDLP_AVAILABLE', bool(ytdlp), ytdlp or 'AUSENTE')
    diz('FFMPEG_AVAILABLE', bool(ffmpeg), ffmpeg or 'AUSENTE')
    diz('FFPROBE_AVAILABLE', bool(ffprobe), ffprobe or 'AUSENTE')

    # ── 2 · O MOTOR DE FALA (biblioteca) — nao o modelo
    ha_motor, porque = fl.disponivel()
    diz('ASR_AVAILABLE', ha_motor, 'SIM' if ha_motor else str(porque)[:70])

    # ── 3 · O MODELO — o ficheiro que decide se a fala sai
    diz('REEL_MODEL_CONFIGURED', True, modelo)
    tem_modelo, cache = _modelo_em_cache(modelo)
    diz('REEL_MODEL_AVAILABLE', tem_modelo,
        ('SIM  (%s)' % cache) if tem_modelo else 'NAO')

    if not tem_modelo:
        print()
        print('MODEL_MISSING = %s' % modelo)
        print('  PROCEDIMENTO DE PREPARO (ja validado, correr UMA vez, FORA da coleta):')
        print('    set PYTHONPATH=C:\\Users\\London1\\.sintonia-libs')
        print('    set HF_HUB_OFFLINE=0')
        print('    py -3.12 -c "from faster_whisper import WhisperModel; '
              "WhisperModel('%s', device='cpu', compute_type='int8')\"" % modelo)
        print('  Depois volte HF_HUB_OFFLINE=1: a coleta NUNCA baixa modelo a correr.')

    print()
    if FALHAS:
        print('RUNTIME_READY = NO   (falhas: %s)' % ', '.join(FALHAS))
        return 1
    print('RUNTIME_READY = YES')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
