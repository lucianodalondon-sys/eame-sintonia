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

# ── ONDE ISTO CORRE, E QUEM DECIDE ──────────────────────────────────────────
# `device` e `compute_type` viviam CRAVADOS na chamada da biblioteca, uma linha,
# dois literais. Enquanto so havia uma resposta possivel isso era honesto. Deixa
# de ser no dia em que a maquina tem placa: um literal nao se pergunta nada.
#
# A decisao e DESTA GAVETA. Nao e do adaptador do Instagram, nao e do adaptador
# do YouTube, nao e de quem chama. Quem chama pede TEXTO; com que ferro o texto
# se faz e politica do dono.
#
#     ENGINE != MODEL != RUNTIME != DEVICE != ACCELERATOR.
#
# Cinco eixos, cinco campos. Fundi-los num so — «GPU» — parece simplificacao e
# custa a verdade: `faster-whisper` continua a ser o motor e `CTranslate2` o
# runtime tanto no processador como na placa. A placa e ACELERADOR, nao motor.
#
# TRES VALORES, E O DO MEIO E O PERIGOSO
# ---------------------------------------
#     CPU    corre no processador. Sempre possivel.
#     GPU    corre na placa. PEDIDO, nao promessa — pode nao haver placa.
#     AUTO   pergunta a biblioteca e usa a placa SE ela existir de verdade.
#
# `AUTO` nao pode fingir. Ele nao le a ficha do fabricante nem a variavel de
# ambiente de ninguem: pergunta ao `CTranslate2` quantos dispositivos CUDA ele
# VE, que e a unica resposta que conta.
#
#     UM «AUTO» QUE ASSUME GPU NAO E DETECAO: E UM PALPITE COM CARA DE POLITICA.
#
# O PADRAO CONTINUA `CPU`, E ISSO E DELIBERADO
# ---------------------------------------------
# Este ficheiro ganha a CAPACIDADE de usar a placa nesta missao; ele nao ganha a
# DECISAO de a usar. Trocar o padrao antes de a prova existir seria exatamente o
# que esta casa nao faz — medir depois de decidir.
DISPOSITIVO = 'AUTO'
CPU = 'CPU'
GPU = 'GPU'
DISPOSITIVOS = (DISPOSITIVO, CPU, GPU)

DISPOSITIVO_PADRAO = (os.environ.get('SINTONIA_ASR_DEVICE') or CPU).upper()

#: O tipo de calculo. `None` = o dono escolhe pelo dispositivo que saiu.
#: Na placa o padrao medido e `float16`; no processador continua `int8`.
COMPUTE_PADRAO = os.environ.get('SINTONIA_ASR_COMPUTE') or None
COMPUTE_CPU = 'int8'
COMPUTE_GPU = 'float16'

#: Por que a placa nao foi usada. Vocabulario fechado — `None` quer dizer «nao
#: houve queda», e nunca «nao sei».
GPU_INDISPONIVEL = 'GPU_UNAVAILABLE'
GPU_SEM_MEMORIA = 'GPU_OOM'

# Teto de tempo por peça. Áudio repetitivo faz o decodificador entrar em laço e
# um lote noturno morre sem ninguém saber. 6x a duração é folga larga sobre os
# ~4x medidos.
TETO_FATOR = 6
TETO_MINIMO_S = 120

# Abaixo disto, o texto pode estar a ser lido na língua errada — e isso muda tudo
# num corpus que compara Itália, Espanha e França.
CONFIANCA_MINIMA = 0.6

# ── O DESCARTE POR SILÊNCIO, QUE O MODO EM LOTE **NÃO** FAZ ─────────────────
# Lido no código de `faster_whisper 1.2.1`, não na documentação:
#
#   · `WhisperModel.generate_segments` aplica a regra: descarta o trecho quando
#     `no_speech_prob > no_speech_threshold`, a menos que `avg_logprob` esteja
#     acima de `log_prob_threshold` — «não descartes se o modelo estava seguro».
#   · `BatchedInferencePipeline._batched_segments_generator` NÃO aplica regra
#     nenhuma. Ele só REPORTA `no_speech_prob` e `avg_logprob` por trecho.
#     Também fixa `hallucination_silence_threshold=None` e
#     `temperatures=temperature[:1]` — sem recuo de temperatura.
#
# Ou seja: passar os limiares em modo lote não os liga. Quem os quiser tem de
# os aplicar por fora — e é o que se faz aqui, com a MESMA conjunção do caminho
# sequencial, para os dois modos darem a mesma resposta.
#
#     PASSAR UM PARÂMETRO NÃO É O MESMO QUE ELE SER APLICADO.
#
# E AGORA A PARTE QUE INTERESSA, PORQUE FOI MEDIDA E CONTRARIA O ÓBVIO
# --------------------------------------------------------------------
# Esta trava, sozinha, NÃO teria salvo o caso real. Em 2026-09-10, com o detetor
# de voz desligado, dez segundos de música corporativa (@syngentaus, Reel
# `C6TiLBCCBz8`) devolveram a palavra «Music» — e os números dela foram:
#
#     no_speech_prob = 0,380      →  ABAIXO do limiar de 0,6
#     avg_logprob    = -1,509     →  abaixo de -1,0
#
# A conjunção da biblioteca exige as DUAS, e a primeira não se verificou. A
# alucinação passaria.
#
#     QUEM SALVOU FOI O DETETOR DE VOZ. Com `vad_filter=True` o mesmo áudio deu
#     ZERO trechos, e o estado saiu REQUESTED_EMPTY.
#
# Por isso a ordem de defesa é esta, e por esta ordem: (1) VAD, que é o que
# realmente mordeu; (2) esta trava, que é a rede que o modo em lote não estende
# sozinho; (3) `_tem_conteudo`, para o `...` que escapa às duas.
#
# E por isso esta trava NÃO foi endurecida para apanhar o «Music»: bastaria
# descartar por `avg_logprob` sozinho — e isso deitaria fora fala real gravada
# ao vento, num trator, no meio de um campo, que é metade do que este corpus
# tem. Uma trava que apaga o sinal é pior do que a alucinação que ela evita.
NO_SPEECH_LIMITE = float(os.environ.get('SINTONIA_ASR_NO_SPEECH') or 0.6)
LOGPROB_LIMITE = float(os.environ.get('SINTONIA_ASR_LOGPROB') or -1.0)

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


def cuda_disponivel():
    """→ (n_dispositivos, porque). PERGUNTA a biblioteca. Nao le ficha nem palpite.

    Quem responde e o `CTranslate2`, e nao o `nvidia-smi`: no Windows a placa
    pode estar perfeita, o driver a declarar CUDA, e a biblioteca a ver ZERO
    porque lhe faltam as DLL de cuBLAS/cuDNN ao lado.

        PLACA PRESENTE != DRIVER COM CUDA != BIBLIOTECA A VER A PLACA.

    Confundir os tres produz o pior diagnostico que existe: «nao da», sem dizer
    porque — e alguem vai comprar hardware que ja esta na maquina.
    """
    _caminho_das_libs()
    try:
        import ctranslate2                                      # noqa: PLC0415
    except ImportError as e:                                    # noqa: BLE001
        return 0, 'sem ctranslate2 neste ambiente (%s)' % type(e).__name__
    try:
        n = int(ctranslate2.get_cuda_device_count())
    except Exception as e:                                      # noqa: BLE001
        return 0, 'o ctranslate2 nao soube responder: %s' % type(e).__name__
    if n > 0:
        return n, ''
    return 0, ('o ctranslate2 ve zero dispositivos CUDA — placa ausente, ou '
               'biblioteca sem as DLL de CUDA ao lado dela')


def resolver_dispositivo(pedido=None):
    """→ (device, compute_type, trace). A politica inteira, num sitio so.

    O TRACE NAO E ENFEITE. Sem ele, «pedi GPU e correu no processador» fica
    indistinguivel de «pedi processador» — e o texto sai igual nos dois casos,
    so que tres vezes mais devagar sem ninguem perceber.

        QUEDA SILENCIOSA E MENTIRA COM OUTRO NOME.

    Por isso tres campos, sempre, mesmo quando nao houve queda:

        DEVICE_REQUESTED   o que se pediu
        DEVICE_USED        o que correu
        WHY_FALLBACK       por que o pedido nao serviu (None se serviu)
    """
    pedido = (pedido or DISPOSITIVO_PADRAO or CPU).upper()
    if pedido not in DISPOSITIVOS:
        raise ValueError('dispositivo fora do vocabulario: %r. Os tres sao %s'
                         % (pedido, ', '.join(DISPOSITIVOS)))
    trace = {'DEVICE_REQUESTED': pedido, 'DEVICE_USED': None,
             'WHY_FALLBACK': None, 'ACCELERATOR': None}

    if pedido == CPU:
        trace.update({'DEVICE_USED': CPU, 'ACCELERATOR': 'NONE'})
        return 'cpu', COMPUTE_PADRAO or COMPUTE_CPU, trace

    n, porque = cuda_disponivel()
    if n > 0:
        trace.update({'DEVICE_USED': GPU, 'ACCELERATOR': 'CUDA',
                      'CUDA_DEVICE_COUNT': n})
        return 'cuda', COMPUTE_PADRAO or COMPUTE_GPU, trace

    # ── A PLACA NAO ESTA LA. E ISSO NAO E ERRO DA FONTE ──────────────────
    # `AUTO` cai para o processador porque foi isso que se pediu: «usa a placa
    # se houver». `GPU` explicito tambem cai — mas o trace grava o pedido, e
    # por isso a queda aparece no artefato em vez de desaparecer nele.
    #
    # Nenhum dos dois vira `ASR_FALHOU`: o reconhecedor nao caiu, o audio esta
    # bom, e a fonte nao tem culpa nenhuma disto.
    trace.update({'DEVICE_USED': CPU, 'ACCELERATOR': 'NONE',
                  'WHY_FALLBACK': GPU_INDISPONIVEL,
                  'WHY_FALLBACK_DETAIL': porque})
    return 'cpu', COMPUTE_PADRAO or COMPUTE_CPU, trace


def carimbo(modelo=None, trace=None):
    """A ficha do reconhecedor, para ir dentro do artefato derivado.

    Um texto sem isto não se explica: dois textos diferentes do mesmo áudio, um
    de `tiny` e outro de `small`, ficariam indistinguíveis.

    ⚠️ `ASR_DEVICE` ERA UM LITERAL, E O LITERAL IA MENTIR
    -----------------------------------------------------
    Ate esta missao este campo dizia, sempre, `cpu/int8/N threads` — escrito a
    mao, ao lado de uma chamada que tambem tinha `cpu` escrito a mao. As duas
    concordavam por coincidencia de teclado, nao por construcao.

        NO DIA EM QUE UMA MUDASSE, A OUTRA CONTINUARIA A JURAR O CONTRARIO,
        E O ARTEFATO LEVARIA A ASSINATURA DA ERRADA.

    Agora o campo vem do `trace` que o resolvedor devolveu: ele diz o que
    CORREU, e nao o que alguem esperava que corresse.
    """
    t = trace or {}
    usado = t.get('DEVICE_USED')
    if usado == GPU:
        ferro = 'cuda/%s' % (COMPUTE_PADRAO or COMPUTE_GPU)
    elif usado == CPU:
        ferro = 'cpu/%s/%d threads' % (COMPUTE_PADRAO or COMPUTE_CPU, nucleos())
    else:
        # Sem trace nao se inventa: um carimbo que adivinha o ferro e pior do
        # que um carimbo que confessa nao saber.
        ferro = NAO_SEI
    return {
        'ASR_ENGINE': MOTOR,
        'ASR_ENGINE_VERSION': _versao_do_motor(),
        'ASR_MODEL': modelo or MODELO_PADRAO,
        'ASR_BEAM': BEAM,
        'ASR_BATCH': LOTE,
        # ── CINCO EIXOS, CINCO CAMPOS ────────────────────────────────────
        # `faster-whisper` continua a ser o MOTOR e o `CTranslate2` o RUNTIME
        # tanto no processador como na placa. A placa e ACELERADOR. Fundir os
        # cinco num «GPU» parece simplificacao e apaga a distincao que permite
        # explicar dois textos diferentes do mesmo audio.
        'ASR_RUNTIME': 'CTranslate2',
        'ASR_DEVICE': ferro,
        'ASR_DEVICE_REQUESTED': t.get('DEVICE_REQUESTED', NAO_SEI),
        'ASR_DEVICE_USED': usado or NAO_SEI,
        'ASR_ACCELERATOR': t.get('ACCELERATOR', NAO_SEI),
        # `None` aqui quer dizer «nao houve queda», e NUNCA «nao sei». Os dois
        # colapsados fariam uma queda silenciosa parecer ausencia de queda.
        'ASR_WHY_FALLBACK': t.get('WHY_FALLBACK'),
        'ASR_VAD': 'YES',
        # Em modo lote a biblioteca FIXA isto em False por dentro; declaramos na
        # mesma, porque o carimbo tem de dizer com que regra o texto nasceu.
        'ASR_CONDITION_ON_PREVIOUS_TEXT': 'NO',
        'ASR_NO_SPEECH_THRESHOLD': NO_SPEECH_LIMITE,
        'ASR_LOGPROB_THRESHOLD': LOGPROB_LIMITE,
        'ASR_SILENCE_DISCARD': 'APLICADO_POR_FORA — o modo em lote da biblioteca '
                               'nao aplica os limiares que recebe',
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


def modelo(nome=None, dispositivo=None):
    """O modelo carregado, uma vez por processo e POR DISPOSITIVO. → (pipe, trace).

    Carregar custa segundos; num lote de mil, carregar mil vezes custaria horas.

    A CHAVE DO CACHE LEVA O DISPOSITIVO, E ISSO NAO E DETALHE
    ---------------------------------------------------------
    Antes a chave era so o nome do modelo. Num processo que medisse `small` no
    processador e depois `small` na placa, a segunda medicao receberia o objeto
    da primeira — e o benchmark publicaria o tempo do processador com a etiqueta
    da placa, sem erro nenhum a apitar.

        UM CACHE QUE IGNORA UMA DIMENSAO DA CHAVE NAO ACELERA: FALSIFICA.

    E o `WhisperModel` continua a nascer AQUI, e so aqui. Este ficheiro e o dono
    do reconhecedor desta casa; um segundo sitio a instanciar seria um segundo
    dono, e dois donos da mesma pergunta divergem no terceiro mes.
    """
    nome = nome or MODELO_PADRAO
    device, compute, trace = resolver_dispositivo(dispositivo)
    chave = (nome, device, compute)
    if chave in _CACHE:
        return _CACHE[chave], trace
    _caminho_das_libs()
    from faster_whisper import BatchedInferencePipeline, WhisperModel
    extra = {'cpu_threads': nucleos()} if device == 'cpu' else {}
    try:
        m = WhisperModel(nome, device=device, compute_type=compute, **extra)
    except Exception as e:                                      # noqa: BLE001
        # ── A PLACA RECUSOU DEPOIS DE DIZER QUE EXISTIA ──────────────────
        # `get_cuda_device_count()` pode contar a placa e o carregamento cair a
        # seguir: memoria cheia, DLL em falta, driver a meio de uma atualizacao.
        # Sao coisas diferentes e tem nomes diferentes — e nenhuma e culpa do
        # audio nem da fonte.
        if device != 'cuda' or trace['DEVICE_REQUESTED'] == GPU_SEM_MEMORIA:
            raise
        porque = GPU_SEM_MEMORIA if _parece_sem_memoria(e) else GPU_INDISPONIVEL
        trace.update({'DEVICE_USED': CPU, 'ACCELERATOR': 'NONE',
                      'WHY_FALLBACK': porque,
                      'WHY_FALLBACK_DETAIL': '%s: %s' % (type(e).__name__,
                                                         str(e)[:200])})
        device, compute = 'cpu', COMPUTE_PADRAO or COMPUTE_CPU
        chave = (nome, device, compute)
        if chave in _CACHE:
            return _CACHE[chave], trace
        m = WhisperModel(nome, device=device, compute_type=compute,
                         cpu_threads=nucleos())
    _CACHE[chave] = BatchedInferencePipeline(model=m)
    return _CACHE[chave], trace


def _parece_sem_memoria(e):
    """Memoria da placa cheia tem nome proprio, e nao e «o reconhecedor caiu».

    A biblioteca nao levanta um tipo dedicado: ela deixa subir o erro do CUDA
    com o texto dentro. Ler o texto e feio e e o que ha — e e MUITO melhor do
    que deixar `GPU_OOM` sair como erro opaco, que foi o defeito que o red team
    desta missao atacou.
    """
    t = ('%s %s' % (type(e).__name__, e)).lower()
    return any(p in t for p in ('out of memory', 'oom', 'cuda_error_out_of_memory',
                                'cublas_status_alloc_failed'))


def transcrever(wav, *, idioma=None, modelo_nome=None, duracao_s=None,
                dispositivo=None):
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
    trace_do_ferro = {}
    try:
        pipe, trace_do_ferro = modelo(modelo_nome, dispositivo)
        segs, info = pipe.transcribe(
            wav, batch_size=LOTE, beam_size=BEAM, vad_filter=True,
            language=idioma,
            # Em modo LOTE a biblioteca já força isto a False por dentro — logo
            # o laço não acontece por construção, e não por esta linha. Ela fica
            # à mesma: o dia em que este ficheiro chamar o caminho sequencial,
            # aqui é que a proteção passa a depender de alguém a ter escrito.
            condition_on_previous_text=False,
            # PASSADOS, E MEDIDOS INERTES. `_batched_segments_generator` recebe
            # estes três e nunca os usa para descartar nada — só os reporta por
            # trecho. `_sem_os_mudos()` é quem os aplica, logo abaixo.
            no_speech_threshold=NO_SPEECH_LIMITE,
            log_prob_threshold=LOGPROB_LIMITE)
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
        # ── SEM PLACA != ERRO DO RECONHECEDOR != ERRO DA FONTE ───────────
        # Um `GPU_OOM` que chega aqui como `ASR_FALHOU` generico apaga a unica
        # informacao que permitiria consertar: era o modelo grande demais para
        # esta placa, e o modelo menor passaria.
        estado, porque = ASR_FALHOU, ('que o áudio não tem fala. O reconhecedor '
                                      'é que caiu.')
        if _parece_sem_memoria(e):
            trace_do_ferro = dict(trace_do_ferro or {})
            trace_do_ferro['WHY_FALLBACK'] = GPU_SEM_MEMORIA
            porque = ('que o áudio não tem fala, nem que a placa não serve. '
                      'Este modelo é que não coube nesta placa.')
        return _resposta(estado, modelo_nome,
                         erro='%s: %s' % (type(e).__name__, str(e)[:200]),
                         maquina_s=round(time.time() - t0, 2),
                         trace_do_ferro=trace_do_ferro,
                         nao_significa=porque)
    dt = time.time() - t0

    # O descarte que o modo em lote não faz. Cada trecho descartado fica
    # contado: descartar em silêncio é o mesmo defeito que aceitar em silêncio.
    segs, mudos = _sem_os_mudos(segs)
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
    # `getattr(..., 0) or 0` colapsaria tres casos num so: campo ausente, campo
    # None, e uma probabilidade genuinamente 0,0 — que quer dizer «o modelo tem
    # a certeza de que ha fala aqui», o oposto de nao saber.
    probs = [float(s.no_speech_prob) for s in segs
             if getattr(s, 'no_speech_prob', None) is not None]
    logps = [float(s.avg_logprob) for s in segs
             if getattr(s, 'avg_logprob', None) is not None]
    fora = _resposta(
        OK if texto else REQUESTED_EMPTY, modelo_nome,
        trace_do_ferro=trace_do_ferro,
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
    # A confianca media do que ficou. Sozinha nao decide nada — e evidencia para
    # uma camada acima, como o resto desta ficha.
    fora['AVG_LOGPROB_MEAN'] = (round(sum(logps) / len(logps), 3) if logps
                                else NAO_SEI)
    # ⚠️ EM MODO LOTE, todos os subtrechos partidos do mesmo bloco de 30 s
    # carregam O MESMO `no_speech_prob`. A media acima nao e uma media de
    # medicoes independentes, e nao se deve ler como tal.
    fora['NO_SPEECH_PROB_NOTE'] = ('em modo lote os subtrechos do mesmo bloco de '
                                   '30 s partilham o valor: nao sao medicoes '
                                   'independentes')
    fora['SEGMENTS_DISCARDED_AS_SILENCE'] = len(mudos)
    if mudos:
        # O TEXTO DESCARTADO FICA À VISTA. Sem isto, «o vídeo não tinha fala» e
        # «eu deitei fora o que ele disse» leem-se exactamente igual.
        fora['DISCARDED_AS_SILENCE'] = [
            {'start': round(x.start, 2), 'end': round(x.end, 2),
             'text': x.text.strip(),
             'no_speech_prob': round(float(getattr(x, 'no_speech_prob', 0) or 0), 3),
             'avg_logprob': round(float(getattr(x, 'avg_logprob', 0) or 0), 3)}
            for x in mudos[:20]]
        fora['DISCARD_RULE'] = (
            'no_speech_prob > %s E avg_logprob <= %s — a mesma conjuncao que o '
            'caminho sequencial do faster-whisper usa, e que o modo em lote nao '
            'aplica sozinho.' % (NO_SPEECH_LIMITE, LOGPROB_LIMITE))
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


def _sem_os_mudos(segs):
    """→ (trechos com fala, trechos descartados). A regra é a do caminho sequencial.

    A conjunção importa e não é redundante: `no_speech_prob` alto sozinho não
    basta. Quando o modelo esteve SEGURO do que ouviu (`avg_logprob` alto), a
    biblioteca não descarta — e nós também não. Descartar por um sinal só
    deitaria fora fala real gravada em ambiente barulhento, que é metade do que
    um vídeo de campo tem.
    """
    fica, fora = [], []
    for s in segs:
        nsp = getattr(s, 'no_speech_prob', None)
        alp = getattr(s, 'avg_logprob', None)
        if nsp is None or nsp <= NO_SPEECH_LIMITE:
            fica.append(s)
            continue
        if alp is not None and alp > LOGPROB_LIMITE:
            # o modelo estava seguro apesar do silencio aparente: fica.
            fica.append(s)
            continue
        fora.append(s)
    return fica, fora


def _resposta(estado, modelo_nome, *, texto=None, maquina_s=NAO_SEI,
              audio_s=NAO_SEI, segmentos=None, idioma_pedido=None,
              idioma_detectado=NAO_SEI, confianca=NAO_SEI, voiced=NAO_SEI,
              no_speech=NAO_SEI, erro='', nao_significa='',
              trace_do_ferro=None):
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
        **carimbo(modelo_nome, trace_do_ferro),
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
