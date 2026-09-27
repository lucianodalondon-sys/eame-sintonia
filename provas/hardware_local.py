#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O QUE ESTA MÁQUINA TEM — medido, nunca lido da ficha do fabricante.

    py provas/hardware_local.py            # a tabela, para o log do workflow
    py provas/hardware_local.py --json     # o mesmo, para artefato

POR QUE ISTO EXISTE
---------------------
Até esta missão, o estado do hardware local desta casa era uma frase:

    LOCAL_HARDWARE_STATUS = NOT_MEASURED

Essa frase é honesta e é inútil para decidir. A decisão «CPU ou GPU» não pode
sair de memória de quem montou a máquina, nem da caixa da placa, nem de um
benchmark de outra pessoa com a mesma placa.

    A FICHA DO FABRICANTE DIZ O QUE A PEÇA PODE FAZER.
    ELA NÃO DIZ O QUE ESTA MÁQUINA, HOJE, COM ESTES DRIVERS, FAZ.

O QUE ESTE FICHEIRO **NÃO** FAZ
---------------------------------
Não instala nada. Não muda driver, PATH, BIOS nem sistema. Não pede admin. Ele
só pergunta e escreve o que ouviu. Uma prova que altera a máquina que está a
medir deixou de ser uma medição.

E NÃO RECOLHE O QUE NÃO PRECISA
---------------------------------
Nome de utilizador, caminho da pasta pessoal, número de série de disco, MAC,
IP, token, cookie e sessão **não entram**. A pergunta desta missão é «esta
máquina consegue correr o reconhecedor por GPU?» — e nenhuma dessas coisas
ajuda a responder.

    MEDIR O QUE A MISSÃO PRECISA NÃO AUTORIZA MEDIR O RESTO.

O VOCABULÁRIO DA AUSÊNCIA
---------------------------
Três palavras, e não se misturam:

    NOT_MEASURED    não tentei medir aqui
    UNKNOWN         tentei, e a máquina não respondeu
    NOT_APPLICABLE  a pergunta não faz sentido nesta máquina
"""
from __future__ import annotations

import json
import os
import platform
import re
import shutil
import subprocess
import sys

NAO_MEDIDO = 'NOT_MEASURED'
DESCONHECIDO = 'UNKNOWN'
NAO_SE_APLICA = 'NOT_APPLICABLE'

#: Onde as bibliotecas pesadas vivem, FORA do repositório. O dono desta
#: constante é `ferramentas/fala_local.py`; aqui só se lê, para não criar um
#: segundo sítio que decida o mesmo.
LIBS = os.environ.get('SINTONIA_LIBS') or os.path.join(
    os.path.expanduser('~'), '.sintonia-libs')


def _correr(cmd, timeout=25):
    """→ (saida, estado). NUNCA levanta: máquina que não responde é medição."""
    exe = shutil.which(cmd[0])
    if exe is None:
        return '', NAO_SE_APLICA
    try:
        r = subprocess.run([exe] + list(cmd[1:]), capture_output=True, text=True,
                           timeout=timeout, encoding='utf-8', errors='replace')
    except (OSError, subprocess.SubprocessError):
        return '', DESCONHECIDO
    if r.returncode != 0:
        return (r.stdout or '') + (r.stderr or ''), DESCONHECIDO
    return r.stdout or '', 'OK'


# ══════════════════════════════════════════════════════════════════════════
# A MÁQUINA
# ══════════════════════════════════════════════════════════════════════════
def sistema():
    return {
        'OS': '%s %s' % (platform.system(), platform.release()),
        'OS_VERSION': platform.version() or DESCONHECIDO,
        'ARCH': platform.machine() or DESCONHECIDO,
        'PYTHON': platform.python_version(),
    }


def cpu():
    """Núcleos LÓGICOS, que é o número que `cpu_threads` usa.

    O modelo do processador sai de `platform`, que no Windows devolve uma linha
    curta. Não se vai buscar mais: para esta decisão o que conta é o número de
    núcleos, e o nome comercial é enfeite.
    """
    nome = platform.processor() or DESCONHECIDO
    return {
        'CPU': nome.strip() or DESCONHECIDO,
        'CPU_LOGICAL_CORES': os.cpu_count() or DESCONHECIDO,
    }


def memoria():
    """RAM total e disponível, em GiB. Os dois números, e não só o total.

    Total diz o que a máquina tem. DISPONÍVEL diz com o que se pode contar
    enquanto o resto do Windows corre — e é esse que decide se um modelo cabe.
    """
    fora = {'RAM_TOTAL_GB': NAO_MEDIDO, 'RAM_AVAILABLE_GB': NAO_MEDIDO}
    try:
        sys.path.insert(0, LIBS) if os.path.isdir(LIBS) else None
        import psutil                                          # noqa: PLC0415
        v = psutil.virtual_memory()
        return {'RAM_TOTAL_GB': round(v.total / 2**30, 1),
                'RAM_AVAILABLE_GB': round(v.available / 2**30, 1)}
    except Exception:                                          # noqa: BLE001
        pass
    if platform.system() == 'Windows':
        # `wmic` sai do Windows moderno; o PowerShell responde na mesma. Duas
        # tentativas, e a ausência das duas é UNKNOWN — não zero.
        saida, st = _correr(['powershell', '-NoProfile', '-Command',
                             '(Get-CimInstance Win32_OperatingSystem) | '
                             'ForEach-Object { "$($_.TotalVisibleMemorySize) '
                             '$($_.FreePhysicalMemory)" }'])
        if st == 'OK':
            n = re.findall(r'\d+', saida)
            if len(n) >= 2:                     # os dois vêm em KiB
                return {'RAM_TOTAL_GB': round(int(n[0]) / 2**20, 1),
                        'RAM_AVAILABLE_GB': round(int(n[1]) / 2**20, 1)}
        return {'RAM_TOTAL_GB': DESCONHECIDO, 'RAM_AVAILABLE_GB': DESCONHECIDO}
    try:
        with open('/proc/meminfo', encoding='utf-8') as f:
            t = f.read()
        tot = re.search(r'MemTotal:\s+(\d+)', t)
        dis = re.search(r'MemAvailable:\s+(\d+)', t)
        if tot and dis:
            return {'RAM_TOTAL_GB': round(int(tot.group(1)) / 2**20, 1),
                    'RAM_AVAILABLE_GB': round(int(dis.group(1)) / 2**20, 1)}
    except OSError:
        pass
    return fora


def disco():
    """Espaço livre onde o trabalho acontece. Um modelo que não cabe não corre."""
    try:
        u = shutil.disk_usage(os.getcwd())
        return {'FREE_DISK_GB': round(u.free / 2**30, 1)}
    except OSError:
        return {'FREE_DISK_GB': DESCONHECIDO}


# ══════════════════════════════════════════════════════════════════════════
# A GPU — e a pergunta tem TRÊS degraus, não um
# ══════════════════════════════════════════════════════════════════════════
# «Tem GPU» não responde nada sozinho. Três coisas diferentes podem falhar, e
# confundi-las produz o pior diagnóstico possível — «não dá», sem dizer porquê:
#
#     1. existe placa?                        → GPU_VENDOR / GPU_MODEL
#     2. o driver expõe CUDA?                 → CUDA_DRIVER_SUPPORT
#     3. a biblioteca VÊ a placa?             → CTRANSLATE2_CUDA_DEVICE_COUNT
#
# O terceiro é o que decide, e é o que mais falha sozinho: no Windows o
# CTranslate2 precisa das DLL de cuBLAS e cuDNN ao lado, e a placa pode estar
# perfeita com a biblioteca a ver zero dispositivos.
#
#     PLACA PRESENTE != DRIVER COM CUDA != BIBLIOTECA A VER A PLACA.
def gpu_nvidia():
    """O que o `nvidia-smi` declara. Ausência do comando NÃO é ausência de placa."""
    fora = {'GPU_VENDOR': NAO_MEDIDO, 'GPU_MODEL': NAO_MEDIDO,
            'GPU_COUNT': NAO_MEDIDO, 'VRAM_TOTAL_MB': NAO_MEDIDO,
            'VRAM_AVAILABLE_MB': NAO_MEDIDO, 'GPU_DRIVER': NAO_MEDIDO,
            'CUDA_DRIVER_SUPPORT': NAO_MEDIDO}
    saida, st = _correr(['nvidia-smi', '--query-gpu=name,memory.total,memory.free,'
                         'driver_version', '--format=csv,noheader,nounits'])
    if st == NAO_SE_APLICA:
        # Sem `nvidia-smi` no PATH. Isto é «não consegui perguntar à NVIDIA»,
        # e não «não há placa» — pode haver placa de outro fabricante, ou o
        # utilitário pode não estar no caminho deste processo.
        fora.update({'GPU_VENDOR': DESCONHECIDO,
                     'GPU_WHY': 'nvidia-smi ausente do PATH deste processo'})
        return fora
    if st != 'OK' or not saida.strip():
        fora.update({'GPU_VENDOR': DESCONHECIDO,
                     'GPU_WHY': 'nvidia-smi respondeu sem dados'})
        return fora
    linhas = [ln.strip() for ln in saida.splitlines() if ln.strip()]
    placas, vram_t, vram_l, driver = [], 0, 0, DESCONHECIDO
    for ln in linhas:
        p = [x.strip() for x in ln.split(',')]
        if len(p) < 4:
            continue
        placas.append(p[0])
        for alvo, i in (('t', 1), ('l', 2)):
            try:
                v = int(float(p[i]))
            except ValueError:
                continue
            if alvo == 't':
                vram_t += v
            else:
                vram_l += v
        driver = p[3]
    if not placas:
        fora.update({'GPU_VENDOR': DESCONHECIDO})
        return fora
    # A versão de CUDA que o DRIVER suporta é o tecto, e não diz que o runtime
    # está instalado. São duas perguntas, e esta responde só a primeira.
    cuda, stc = _correr(['nvidia-smi'])
    m = re.search(r'CUDA Version:\s*([\d.]+)', cuda) if stc == 'OK' else None
    return {
        'GPU_VENDOR': 'NVIDIA',
        'GPU_MODEL': ' · '.join(placas),
        'GPU_COUNT': len(placas),
        'VRAM_TOTAL_MB': vram_t or DESCONHECIDO,
        'VRAM_AVAILABLE_MB': vram_l or DESCONHECIDO,
        'GPU_DRIVER': driver,
        'CUDA_DRIVER_SUPPORT': m.group(1) if m else DESCONHECIDO,
    }


def bibliotecas():
    """As versões que realmente vão correr, e o que o CTranslate2 VÊ.

    `CTRANSLATE2_CUDA_DEVICE_COUNT` é a resposta que decide a missão. Ela vem
    da biblioteca, não do driver: é a única que sabe se as DLL certas estão ao
    lado dela.
    """
    if os.path.isdir(LIBS) and LIBS not in sys.path:
        sys.path.insert(0, LIBS)
    fora = {'LOCAL_LIB_PATH': LIBS, 'LOCAL_LIB_PATH_EXISTS': os.path.isdir(LIBS)}

    def _versao(nome):
        try:
            from importlib.metadata import version                # noqa: PLC0415
            return version(nome)
        except Exception:                                         # noqa: BLE001
            return DESCONHECIDO

    try:
        import faster_whisper                                     # noqa: F401,PLC0415
        fora['FASTER_WHISPER_VERSION'] = _versao('faster-whisper')
    except Exception as e:                                        # noqa: BLE001
        fora['FASTER_WHISPER_VERSION'] = DESCONHECIDO
        fora['FASTER_WHISPER_WHY'] = type(e).__name__

    try:
        import ctranslate2                                        # noqa: PLC0415
        fora['CTRANSLATE2_VERSION'] = getattr(ctranslate2, '__version__',
                                              _versao('ctranslate2'))
        try:
            n = ctranslate2.get_cuda_device_count()
            fora['CTRANSLATE2_CUDA_DEVICE_COUNT'] = n
            fora['GPU_SUPPORT_AVAILABLE'] = 'YES' if n > 0 else 'NO'
        except Exception as e:                                    # noqa: BLE001
            fora['CTRANSLATE2_CUDA_DEVICE_COUNT'] = DESCONHECIDO
            fora['GPU_SUPPORT_AVAILABLE'] = DESCONHECIDO
            fora['CTRANSLATE2_CUDA_WHY'] = '%s: %s' % (type(e).__name__, e)
        try:
            fora['CTRANSLATE2_COMPUTE_TYPES_CUDA'] = sorted(
                ctranslate2.get_supported_compute_types('cuda'))
        except Exception:                                         # noqa: BLE001
            fora['CTRANSLATE2_COMPUTE_TYPES_CUDA'] = NAO_SE_APLICA
        try:
            fora['CTRANSLATE2_COMPUTE_TYPES_CPU'] = sorted(
                ctranslate2.get_supported_compute_types('cpu'))
        except Exception:                                         # noqa: BLE001
            fora['CTRANSLATE2_COMPUTE_TYPES_CPU'] = DESCONHECIDO
    except Exception as e:                                        # noqa: BLE001
        fora['CTRANSLATE2_VERSION'] = DESCONHECIDO
        fora['CTRANSLATE2_WHY'] = type(e).__name__
        fora['CTRANSLATE2_CUDA_DEVICE_COUNT'] = NAO_SE_APLICA
        fora['GPU_SUPPORT_AVAILABLE'] = DESCONHECIDO

    saida, st = _correr(['ffmpeg', '-version'])
    if st == 'OK':
        m = re.search(r'ffmpeg version (\S+)', saida)
        fora['FFMPEG_VERSION'] = m.group(1) if m else DESCONHECIDO
    else:
        fora['FFMPEG_VERSION'] = DESCONHECIDO if st == DESCONHECIDO else NAO_SE_APLICA
    return fora


def medir():
    """A ficha inteira. Uma chamada, um dicionário, nenhum efeito na máquina."""
    d = {'RUNNER_NAME': os.environ.get('RUNNER_NAME') or NAO_SE_APLICA}
    for parte in (sistema(), cpu(), memoria(), disco(), gpu_nvidia(), bibliotecas()):
        d.update(parte)
    # ── O VEREDITO, E ELE É DERIVADO, NUNCA ESCRITO À MÃO ────────────────────
    # Três estados, e o do meio é o que costuma faltar nos relatórios: a placa
    # existe e a biblioteca não a vê. Chamar isso de «sem GPU» mandaria alguém
    # comprar hardware que já está na máquina.
    n = d.get('CTRANSLATE2_CUDA_DEVICE_COUNT')
    tem_placa = d.get('GPU_VENDOR') not in (NAO_MEDIDO, DESCONHECIDO, None)
    if isinstance(n, int) and n > 0:
        d['LOCAL_GPU_AVAILABLE'] = 'YES'
        d['LOCAL_GPU_WHY'] = 'o CTranslate2 declara %d dispositivo(s) CUDA' % n
    elif isinstance(n, int) and n == 0 and tem_placa:
        d['LOCAL_GPU_AVAILABLE'] = 'NO'
        d['LOCAL_GPU_WHY'] = ('ha placa e o CTranslate2 ve ZERO dispositivos — '
                              'isto e biblioteca sem CUDA, nao maquina sem placa')
    elif isinstance(n, int) and n == 0:
        d['LOCAL_GPU_AVAILABLE'] = 'NO'
        d['LOCAL_GPU_WHY'] = 'o CTranslate2 ve zero dispositivos CUDA'
    else:
        d['LOCAL_GPU_AVAILABLE'] = DESCONHECIDO
        d['LOCAL_GPU_WHY'] = 'nao foi possivel perguntar ao CTranslate2'
    d['LOCAL_HARDWARE_STATUS'] = 'MEASURED'
    return d


def _linha(k, v):
    return '  %-34s %s' % (k, v)


def main():
    d = medir()
    if '--json' in sys.argv:
        print(json.dumps(d, ensure_ascii=False, indent=1, sort_keys=True))
        return 0
    print('\nO QUE ESTA MAQUINA TEM — medido agora, nesta corrida')
    print('=' * 74)
    grupos = (
        ('MAQUINA', ('RUNNER_NAME', 'OS', 'ARCH', 'PYTHON', 'CPU',
                     'CPU_LOGICAL_CORES', 'RAM_TOTAL_GB', 'RAM_AVAILABLE_GB',
                     'FREE_DISK_GB')),
        ('PLACA', ('GPU_VENDOR', 'GPU_MODEL', 'GPU_COUNT', 'VRAM_TOTAL_MB',
                   'VRAM_AVAILABLE_MB', 'GPU_DRIVER', 'CUDA_DRIVER_SUPPORT',
                   'GPU_WHY')),
        ('BIBLIOTECAS', ('LOCAL_LIB_PATH_EXISTS', 'FASTER_WHISPER_VERSION',
                         'CTRANSLATE2_VERSION', 'CTRANSLATE2_CUDA_DEVICE_COUNT',
                         'CTRANSLATE2_COMPUTE_TYPES_CUDA',
                         'CTRANSLATE2_COMPUTE_TYPES_CPU',
                         'CTRANSLATE2_CUDA_WHY', 'FFMPEG_VERSION')),
    )
    for titulo, campos in grupos:
        print('\n  %s' % titulo)
        for c in campos:
            if c in d:
                print(_linha(c, d[c]))
    print('\n  VEREDITO')
    print(_linha('LOCAL_HARDWARE_STATUS', d['LOCAL_HARDWARE_STATUS']))
    print(_linha('LOCAL_GPU_AVAILABLE', d['LOCAL_GPU_AVAILABLE']))
    print(_linha('LOCAL_GPU_WHY', d['LOCAL_GPU_WHY']))
    print('')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
