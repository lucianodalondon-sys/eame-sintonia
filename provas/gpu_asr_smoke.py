#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O SMOKE TÉCNICO DA PLACA — e o que ele NUNCA prova.

    py provas/gpu_asr_smoke.py --device GPU
    py provas/gpu_asr_smoke.py --device GPU --audio C:\\caminho\\voz.wav

O QUE ISTO É
-------------
A prova de que ESTA máquina consegue levar uma inferência do reconhecedor até ao
fim NA PLACA: dispositivo pedido, acelerador CUDA, tipo de cálculo, estado do
texto, e o trace inteiro que o dono do reconhecedor devolveu.

A prova manual no PowerShell passou a 2026-09-11. Uma prova que só existe no
histórico de um terminal não é prova: ninguém a repete, e ela morre com a janela.

    O QUE NAO CORRE OUTRA VEZ NAO E PROVA. E UMA LEMBRANCA.

O QUE ISTO NÃO É, E A CONFUSÃO É FÁCIL
---------------------------------------
    GPU TECHNICAL SMOKE != GPU QUALITY BENCHMARK.

O áudio daqui é SINTETIZADO na própria máquina, e é uma frase só. Ele serve para
mostrar que a cadeia CUDA → cuBLAS → CTranslate2 → faster-whisper fecha. Não diz
nada sobre acerto de termo agronómico, nome de marca ou estabilidade de língua em
italiano, espanhol, francês ou inglês — isso é `provas/asr_banco.py`, e esse
precisa do corpus real com verdade de referência declarada.

Quem quiser ler qualidade daqui está a ler a coisa errada, e por isso o artefato
carrega `QUALITY_BENCHMARK = NOT_RUN` escrito por dentro.

O QUE ISTO NÃO FAZ
-------------------
Não baixa mídia. Não baixa modelo — se o modelo não estiver já nesta máquina,
PARA, porque um banco de prova que descarrega 1,5 GB em silêncio deixou de medir
a máquina e passou a medir a rede. Não instala nada, não mexe no PATH e não toca
na placa senão para a usar. Não instancia `WhisperModel`: quem o faz é
`ferramentas/fala_local.py`, e um segundo sítio seria um segundo dono.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import wave

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas                      # noqa: E402,F401
import fala_local as fl              # noqa: E402

FRASE = 'Sintonia prova tecnica de transcricao local por GPU.'

#: estados desta prova — fechados, como tudo o que a casa publica
PASSOU = 'PASS'
FALHOU = 'FAIL'
SEM_MODELO = 'MODEL_NOT_PRESENT'
SEM_AUDIO = 'NO_LOCAL_AUDIO_SOURCE'
SEM_ASR = 'ASR_UNAVAILABLE'


def modelo_esta_local(nome):
    """→ (bool, porquê). Pergunta ao cache, NUNCA à rede.

    `local_files_only=True` é a diferença entre «está cá» e «eu vou buscá-lo».
    Sem ele, a primeira corrida numa máquina nova mediria o download — e foi
    exactamente esse o defeito que a C4 já tinha apanhado uma vez, quando 204 s
    de descarregamento saíram carimbados como `TRANSCRIPTION_TIMEOUT` do áudio.
    """
    fl._caminho_das_libs()
    try:
        from huggingface_hub import snapshot_download            # noqa: PLC0415
    except ImportError as e:                                     # noqa: BLE001
        return False, 'sem huggingface_hub para perguntar ao cache (%s)' % type(e).__name__
    if os.path.isdir(nome):
        return True, 'modelo em pasta local: %s' % nome
    for repo in ('Systran/faster-whisper-%s' % nome, nome):
        try:
            p = snapshot_download(repo, local_files_only=True)
            return True, 'ja em cache: %s' % p
        except Exception:                                        # noqa: BLE001
            continue
    return False, ('o modelo %r nao esta nesta maquina. Esta prova NAO o descarrega: '
                   'um banco que baixa 1,5 GB mede a rede, nao a placa.' % nome)


def audio_local(destino):
    """Uma frase falada, sintetizada NESTA máquina. → (caminho, como) ou (None, porquê).

    Windows tem sintetizador embutido e offline. É o mesmo caminho pelo qual a
    prova manual passou, e não traz um único byte de fora.
    """
    if sys.platform == 'win32':
        ps = ("Add-Type -AssemblyName System.Speech; "
              "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
              "$s.SetOutputToWaveFile('%s'); $s.Speak('%s'); $s.Dispose()"
              % (destino.replace("'", "''"), FRASE.replace("'", "''")))
        r = subprocess.run(['powershell', '-NoProfile', '-Command', ps],
                           capture_output=True, text=True)
        if r.returncode == 0 and os.path.exists(destino) and os.path.getsize(destino) > 1000:
            return destino, 'System.Speech (Windows, offline)'
        return None, 'o sintetizador do Windows nao produziu audio: %s' % (r.stderr or '')[:160]
    return None, ('nesta plataforma (%s) nao ha sintetizador local declarado. '
                  'Passe --audio com um .wav ja preservado.' % sys.platform)


def _silencio(destino, segundos=1):
    """Um .wav mudo — só para o red team, nunca para afirmar qualidade."""
    with wave.open(destino, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(16000)
        w.writeframes(b'\x00\x00' * 16000 * segundos)
    return destino


def medir(*, device, modelo, audio=None):
    """→ o corpo do relatório. Uma corrida, um artefato, sem efeitos colaterais."""
    fora = {
        'PROVA': 'GPU_ASR_TECHNICAL_SMOKE',
        'O_QUE_ISTO_NAO_E': ('nao e benchmark de qualidade. O audio e sintetizado e '
                             'nao tem verdade de referencia declarada.'),
        'QUALITY_BENCHMARK': 'NOT_RUN',
        'RUNNER_NAME': os.environ.get('RUNNER_NAME') or fl.NAO_SEI,
        'DEVICE_REQUESTED': device,
        'ASR_MODEL': modelo,
        'ASR_OWNER': 'ferramentas/fala_local.py',
    }

    ha, porque = fl.disponivel()
    if not ha:
        return dict(fora, RESULT=SEM_ASR, WHY=porque)

    n, porque_cuda = fl.cuda_disponivel()
    fora['CUDA_DEVICE_COUNT'] = n
    fora['CUDA_WHY'] = porque_cuda or None
    try:
        import ctranslate2                                       # noqa: PLC0415
        fora['CTRANSLATE2_VERSION'] = getattr(ctranslate2, '__version__', fl.NAO_SEI)
        fora['COMPUTE_TYPES_CUDA'] = (list(ctranslate2.get_supported_compute_types('cuda'))
                                      if n else [])
    except Exception as e:                                       # noqa: BLE001
        fora['CTRANSLATE2_VERSION'] = fl.NAO_SEI
        fora['COMPUTE_TYPES_CUDA'] = []
        fora['CTRANSLATE2_WHY'] = type(e).__name__

    ok, porque_modelo = modelo_esta_local(modelo)
    fora['MODEL_PRESENT'] = 'YES' if ok else 'NO'
    fora['MODEL_WHY'] = porque_modelo
    if not ok:
        return dict(fora, RESULT=SEM_MODELO, WHY=porque_modelo)

    tmp = tempfile.mkdtemp(prefix='gpu-smoke-')
    wav = audio
    if wav:
        fora['AUDIO_SOURCE'] = 'declarado pelo chamador: %s' % os.path.basename(wav)
    else:
        wav, como = audio_local(os.path.join(tmp, 'frase.wav'))
        fora['AUDIO_SOURCE'] = como
        if not wav:
            return dict(fora, RESULT=SEM_AUDIO, WHY=como)

    r = fl.transcrever(wav, idioma='pt', modelo_nome=modelo, dispositivo=device)
    for campo in ('TRANSCRIPT_STATE', 'TRANSCRIPT', 'TRANSCRIPT_CHARS',
                  'ASR_DEVICE_REQUESTED', 'ASR_DEVICE_SELECTED', 'ASR_DEVICE_EXECUTION',
                  'ASR_DEVICE_USED', 'ASR_ACCELERATOR', 'ASR_ACCELERATOR_SELECTED',
                  'ASR_DEVICE', 'ASR_WHY_FALLBACK', 'ASR_ENGINE_VERSION',
                  'MACHINE_SECONDS', 'MODEL_PREPARE_SECONDS', 'ERROR'):
        fora[campo] = r.get(campo)

    # ── O VEREDITO, E ELE EXIGE OS CINCO AO MESMO TEMPO ──────────────────
    # Qualquer um em falta e a placa nao ficou provada. Em especial
    # `ASR_DEVICE_EXECUTION`: sem ele, «escolheu GPU» passaria por «correu na
    # GPU» — que foi o defeito que esta missao encontrou.
    passou = (r.get('TRANSCRIPT_STATE') == fl.OK
              and r.get('ASR_DEVICE_EXECUTION') == fl.EXECUCAO_PROVADA
              and r.get('ASR_DEVICE_USED') == fl.GPU
              and r.get('ASR_ACCELERATOR') == 'CUDA'
              and r.get('ASR_WHY_FALLBACK') is None
              and not r.get('ERROR')
              and (r.get('TRANSCRIPT_CHARS') or 0) > 0)
    fora['RESULT'] = PASSOU if passou else FALHOU
    if not passou:
        fora['WHY'] = ('faltou pelo menos um dos cinco: estado OK, execucao PROVEN, '
                       'dispositivo GPU, acelerador CUDA, sem queda e texto nao vazio')
    return fora


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--device', default=fl.GPU, choices=list(fl.DISPOSITIVOS))
    ap.add_argument('--modelo', default=fl.MODELO_PADRAO)
    ap.add_argument('--audio', default=None,
                    help='um .wav ja preservado. Sem isto, sintetiza-se um local.')
    ap.add_argument('--json', action='store_true')
    a = ap.parse_args()

    d = medir(device=a.device, modelo=a.modelo, audio=a.audio)
    if a.json:
        print(json.dumps(d, ensure_ascii=False, indent=1))
    else:
        print('\nSMOKE TECNICO DA PLACA — nao e benchmark de qualidade')
        print('=' * 72)
        for k, v in d.items():
            if k in ('O_QUE_ISTO_NAO_E',):
                continue
            print('  %-28s %s' % (k, str(v)[:120]))
        print('\n  QUALITY_BENCHMARK = NOT_RUN — e continua, sem corpus real.')
    # PASS e a unica saida verde. `MODEL_NOT_PRESENT` sai vermelho de proposito:
    # e uma medicao valida da maquina, e nao um sucesso.
    return 0 if d.get('RESULT') == PASSOU else 1


if __name__ == '__main__':
    raise SystemExit(main())
