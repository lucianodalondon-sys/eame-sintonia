#!/usr/bin/env python3
"""
ASR LOCAL — a camada técnica que transforma ÁUDIO em TEXTO, e não sabe mais nada.

    py scripts/asr_local.py estado             # o motor existe nesta máquina?
    py scripts/asr_local.py ouvir <arquivo> es # transcreve um arquivo, e mostra o tempo

O QUE ESTE ARQUIVO É, E O QUE ELE NUNCA VAI SER
=================================================
Ele recebe `audio_path`, `language` e uma configuração, e devolve texto, segmentos com
tempo e os metadados do reconhecimento. Só isso.

Ele **não sabe** o que é Instagram, o que é YouTube, o que é uma fonte, o que é uma
legenda, o que é relevância nem quem merece hora de máquina. Não escolhe vídeo, não
baixa mídia, não grava artefato em `data/samples`, não decide fila.

    ESTA CAMADA NÃO É DONA DE COLETA. ELA É UM OUVIDO ALUGADO.

A razão é a que esta casa já pagou para aprender em outro lugar: quando o motor sabe
quem ele está ouvindo, ele começa a decidir quem vale ouvir — e aí existem dois donos
da mesma decisão, e eles divergem em silêncio.

DE ONDE VÊM OS NÚMEROS DAQUI — E POR QUE NENHUM DELES É MEU
=============================================================
Nada nesta camada foi escolhido a gosto. Tudo veio de `instagram_transcrever.py`, que
cronometrou o motor nesta casa em 2026-09-02, num reel real de 110 s da @basf_agroes,
com 16 núcleos:

    modelo    velocidade      qualidade do texto
    tiny      18,7x           "Pirar Pascal", "agro-imfluencia" — inutilizável
    base       9,4x           "Pilar Pasqual", "ingeniero-agricula" — média
    small      3,2x           "Pilar Pascual", "ingeniero agrícola" — boa   ← o padrão

E as duas descobertas que custaram medição, e que continuam valendo aqui:

  1. **Os núcleos não vêm de graça.** O padrão da biblioteca usa 4 threads. Declarar
     `cpu_threads` deu ~4x; sem isso a primeira medição deu 0,3x — 63 horas para mil
     vídeos em vez de 6.
  2. **`beam_size=5` custa o dobro e entrega o mesmo texto.** Medido: 1,16x contra
     2,31x, com 2.079 e 2.054 caracteres praticamente idênticos.

E a terceira, que é a mais silenciosa das três:

  3. **`condition_on_previous_text=False` é obrigatório.** Sem isso, áudio repetitivo
     (música, refrão, ruído de motor) faz o decodificador se alimentar do próprio texto
     anterior e entrar em laço: ele não erra, ele NÃO TERMINA.

MEDIDO DE NOVO, NESTE CONTÊINER, EM 2026-09-04
------------------------------------------------
Contra 60 s de fala espanhola real (LibriVox, domínio público), com estes mesmos
parâmetros e **4 núcleos**:

    modelo carregado ....... 11,4 s
    60,0 s de áudio ........ 14,1 s de máquina  →  4,26x
    idioma ................. es, confiança 1,00
    segmentos .............. 2, com tempo de início e fim

Quatro núcleos deram 4,26x onde dezesseis deram 3,2x. Isso NÃO quer dizer que a
máquina pequena é mais rápida: quer dizer que a velocidade depende do áudio, e que
qualquer número de velocidade sem o áudio ao lado é propaganda. Por isso
`transcrever()` devolve `REALTIME_FACTOR` medido NAQUELE arquivo, sempre.

O IDIOMA É DECLARADO, NUNCA ADIVINHADO POR VÍDEO
==================================================
Três segundos de abertura com música fazem o detector escolher errado, e o resto sai
lixo — em silêncio, com o texto parecendo normal. Medido nesta casa: dois reels
voltaram `en` com confiança 0,37, sendo espanhóis.

    IDIOMA ADIVINHADO POR VÍDEO É UM ERRO QUE NÃO AVISA.

Quem chama sabe o país da conta desde o lote congelado. `IDIOMA_DO_PAIS` mora aqui
porque é lei do RECONHECIMENTO, não de coleta — mas quem decide o país é quem chama.

    E a lei que anda junto: IDIOMA ≠ LUGAR. Isto escolhe o decodificador, nunca o fato.

POR QUE A EXTRAÇÃO PAROU AQUI, E O INSTAGRAM NÃO FOI TOCADO
=============================================================
Esta camada nasceu de `instagram_transcrever.py`, que está **medido e funcionando**.
Reescrevê-lo para passar a chamar daqui traria risco sem trazer medição nova nesta
rodada. Então ele ficou como está, e esta camada serve o YouTube primeiro.

    MOTOR QUE FUNCIONA NÃO SE MEXE PARA FICAR BONITO.

Migrar o Instagram para cá é uma decisão de outra rodada, e ela precisa vir com a
mesma prova de tempo que a original trouxe.

ONDE MORA A BIBLIOTECA
========================
Fora do repositório, em `~/.sintonia-libs` (ou `SINTONIA_LIBS`). A memória desta casa
registra o acidente: `pip` sem `--target` criou `C:\\eame-sintonia\\Scripts`, e apagar
`Scripts` apagou `scripts` — no Windows os dois nomes são a MESMA pasta.

    py -m pip install --target ~/.sintonia-libs faster-whisper

`ffmpeg` NÃO é exigido aqui. O `faster-whisper` decodifica o áudio pelo PyAV, que vem
com as bibliotecas dele próprias — medido neste contêiner, que não tem `ffmpeg` no
PATH e transcreveu mp3 e wav do mesmo jeito.
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))

# As bibliotecas pesadas vivem FORA do repositório. Ver a prosa acima sobre `Scripts/`.
LIBS = os.environ.get('SINTONIA_LIBS') or os.path.join(
    os.path.expanduser('~'), '.sintonia-libs')
if os.path.isdir(LIBS) and LIBS not in sys.path:
    sys.path.insert(0, LIBS)

NAO_SEI = 'NOT_KNOWN'

# ══════════════════════════════════════════════════ A CONFIGURAÇÃO MEDIDA, EM UM LUGAR
ENGINE = 'faster-whisper'
MODELO_PADRAO = os.environ.get('ASR_MODELO') or 'small'
DEVICE = 'cpu'
COMPUTE_TYPE = 'int8'
BEAM = int(os.environ.get('ASR_BEAM') or 1)
# Medido com aquecimento e 3 repetições: sequencial 2,49x · lote 8 → 4,13x · lote 16 →
# 4,03x. O lote dá 1,66x de graça, e 16 não é melhor que 8.
LOTE = int(os.environ.get('ASR_LOTE') or 8)
VAD_FILTER = True

# ── PAÍS → IDIOMA ─────────────────────────────────────────────────────────────────
# Não é tradução nem geografia: é a escolha do decodificador a partir de um fato que
# já foi provado de graça na fase de identidade. Quem não souber o país passa `None`
# e ACEITA a autodetecção — e a resposta virá marcada como detectada, não declarada.
IDIOMA_DO_PAIS = {'ES': 'es', 'IT': 'it', 'FR': 'fr', 'PT': 'pt', 'BR': 'pt'}

# Teto de tempo por arquivo. Áudio repetitivo pode fazer o decodificador entrar em
# laço. Seis vezes a duração é folga larga sobre os ~4x medidos.
TETO_FATOR = 6
TETO_MINIMO_S = 120

# ── OS ESTADOS. SÃO ESTADOS, NÃO GRAUS DE FRACASSO ────────────────────────────────
# Cada um pede conduta diferente de quem chamou, e NENHUM deles significa "o vídeo não
# tem fala". Confundir os dois é o erro que este arquivo existe para impedir.
OK = 'WHISPER_OK'
SEM_MOTOR = 'WHISPER_ENGINE_MISSING'
AUDIO_ILEGIVEL = 'WHISPER_AUDIO_FAILURE'
FALHOU = 'WHISPER_TRANSCRIPTION_FAILURE'
VAZIO = 'WHISPER_REQUESTED_EMPTY'
ESTOUROU = 'WHISPER_TRANSCRIPTION_TIMEOUT'


def idioma_do_pais(pais):
    """'ES' → 'es'. País desconhecido → None, e aí a detecção decide (e é registrada)."""
    return IDIOMA_DO_PAIS.get(str(pais or '').upper().strip())


def config(modelo=None, beam=None, lote=None, nucleos=None):
    """A configuração que vai viajar JUNTO do texto. Sem ela, o texto não é reproduzível."""
    return {
        'ASR_ENGINE': ENGINE,
        'ASR_MODEL': modelo or MODELO_PADRAO,
        'ASR_DEVICE': DEVICE,
        'ASR_COMPUTE_TYPE': COMPUTE_TYPE,
        'ASR_BEAM': int(BEAM if beam is None else beam),
        'ASR_BATCH': int(LOTE if lote is None else lote),
        'ASR_VAD_FILTER': VAD_FILTER,
        'ASR_CPU_THREADS': int(nucleos or os.cpu_count() or 4),
    }


def chave(video_ou_objeto_id, cfg, idioma):
    """A CHAVE MÍNIMA DO CACHE, e ela é mínima de propósito.

    Trocar de modelo produz outro texto; trocar de idioma produz outro texto. Os dois
    precisam estar na chave, ou a segunda execução devolve o resultado da primeira e
    ninguém percebe que a configuração mudou.

    O que NÃO entra: beam, lote e número de núcleos. Eles mudam o TEMPO, não o texto —
    e uma chave que muda com o número de núcleos transforma "trocar de máquina" em
    "transcrever tudo de novo".
    """
    return '%s|%s|%s|%s' % (video_ou_objeto_id, cfg['ASR_ENGINE'], cfg['ASR_MODEL'],
                            idioma or 'AUTO')


# ═══════════════════════════════════════════════════════════════════════ O MOTOR

def disponivel():
    """→ (SIM/NÃO, motivo). Perguntar antes custa um segundo; descobrir depois custa o lote.

    O `except` é largo de propósito. Instalação meio-quebrada do `ctranslate2` não
    levanta `ImportError`: levanta `OSError` de biblioteca compartilhada ausente. Um
    `except ImportError` sozinho deixaria essa passar como exceção não tratada, e o
    lote inteiro morreria com traceback em vez de virar um estado — sem gravar o
    artefato daquela corrida.

        MOTOR QUEBRADO TEM DE VIRAR ESTADO, NUNCA TRACEBACK.
    """
    try:
        import faster_whisper                                  # noqa: F401
    except Exception as e:                                     # noqa: BLE001
        return False, ('faster-whisper indisponível (%s: %s). Instale FORA do '
                       'repositório:\n  py -m pip install --target %s faster-whisper\n'
                       'NUNCA sem --target: no Windows o pip cria `Scripts/`, que é a '
                       'MESMA pasta que `scripts/`.'
                       % (type(e).__name__, str(e)[:160], LIBS))
    return True, 'faster-whisper importável a partir de %s' % LIBS


def duracao_s(audio_path):
    """Duração do áudio SEM `ffprobe`, pelo mesmo PyAV que o motor já usa. → segundos ou NOT_KNOWN.

    Serve para medir minutos de áudio antes de transcrever — e para não chamar de
    "áudio de 0 s" um arquivo que o decodificador simplesmente não abriu.
    """
    try:
        import av
    except ImportError:
        return NAO_SEI
    try:
        with av.open(audio_path) as c:
            if c.duration:
                return round(c.duration / 1000000.0, 2)
            fluxos = [s for s in c.streams if s.type == 'audio']
            if fluxos and fluxos[0].duration and fluxos[0].time_base:
                return round(float(fluxos[0].duration * fluxos[0].time_base), 2)
    except Exception:                                          # noqa: BLE001
        return NAO_SEI
    return NAO_SEI


class Motor:
    """O modelo carregado. Carregar custa dezenas de segundos: carrega-se UMA vez por lote."""

    def __init__(self, modelo=None, nucleos=None, beam=None, lote=None):
        from faster_whisper import BatchedInferencePipeline, WhisperModel
        self.cfg = config(modelo=modelo, beam=beam, lote=lote, nucleos=nucleos)
        t0 = time.time()
        self._m = WhisperModel(self.cfg['ASR_MODEL'], device=DEVICE,
                               compute_type=COMPUTE_TYPE,
                               cpu_threads=self.cfg['ASR_CPU_THREADS'])
        self._pipe = BatchedInferencePipeline(model=self._m)
        self.segundos_de_carga = round(time.time() - t0, 1)

    def transcrever(self, audio_path, language=None, duracao_esperada_s=None):
        """→ dict. NUNCA levanta exceção por causa do áudio: falha vira ESTADO.

        O dicionário devolvido é a resposta inteira desta camada:

            ESTADO ............ um dos WHISPER_* declarados no topo
            TRANSCRIPT ........ o texto corrido, ou None
            TRANSCRIPT_SEGMENTS [{START_S, END_S, TEXT}] — os tempos ficam, sempre
            ASR_* ............. a configuração que produziu este texto
            AUDIO_SECONDS / MACHINE_SECONDS / REALTIME_FACTOR
            COST_USD .......... 0, porque é esta máquina
            MACHINE_SECONDS ... o custo REAL, que não é dólar e não é zero

        Os tempos de cada trecho ficam porque sem eles uma citação não pode ser
        conferida contra o segundo exato do vídeo — e citação que não se confere não
        é evidência.
        """
        fora = dict(self.cfg)
        fora.update({
            'ASR_LANGUAGE': language or NAO_SEI,
            'ASR_LANGUAGE_DECLARADO': bool(language),
            'AUDIO_PATH': audio_path,
            'COST_USD': 0,
            'PAID_API_COST_USD': 0,
        })
        if not audio_path or not os.path.exists(audio_path):
            fora.update({'ESTADO': AUDIO_ILEGIVEL, 'TRANSCRIPT': None,
                         'WHY': 'arquivo de áudio inexistente: %s' % audio_path,
                         'NAO_SIGNIFICA': 'que o vídeo não tem fala. Eu não ouvi.'})
            return fora
        if os.path.getsize(audio_path) < 1000:
            fora.update({'ESTADO': AUDIO_ILEGIVEL, 'TRANSCRIPT': None,
                         'WHY': 'arquivo de áudio com %d bytes — não é áudio'
                                % os.path.getsize(audio_path),
                         'NAO_SIGNIFICA': 'que o vídeo não tem fala. Eu não ouvi.'})
            return fora

        dur = duracao_esperada_s if isinstance(duracao_esperada_s, (int, float)) else None
        if dur is None:
            d = duracao_s(audio_path)
            dur = d if isinstance(d, (int, float)) else None
        teto = max(TETO_MINIMO_S, int(dur * TETO_FATOR)) if dur else TETO_MINIMO_S

        t = time.time()
        try:
            segs, info = self._pipe.transcribe(
                audio_path, batch_size=self.cfg['ASR_BATCH'],
                beam_size=self.cfg['ASR_BEAM'], vad_filter=VAD_FILTER,
                language=language,
                # OBRIGATÓRIO — ver a prosa do topo sobre o laço que não termina.
                condition_on_previous_text=False)
            trechos, estourou = [], False
            for s in segs:
                if time.time() - t > teto:
                    estourou = True
                    break
                # ── OS TRÊS SINAIS QUE DENUNCIAM TEXTO INVENTADO ────────────────
                # O Whisper NÃO fica em silêncio diante de silêncio: ele preenche.
                # Ruído de motor vira "Suscríbete al canal", música vira a letra que
                # ele acha que reconheceu. O texto sai limpo, gramatical e falso.
                #
                #     ALUCINAÇÃO DE ASR NÃO PARECE ERRO. PARECE FRASE.
                #
                # Os três números que a denunciam já vêm calculados no segmento e não
                # custam nada para guardar. Jogá-los fora seria destruir a única prova
                # de que aquela frase não foi dita.
                trecho = {'START_S': round(s.start, 2), 'END_S': round(s.end, 2),
                          'TEXT': s.text.strip()}
                for campo, nome in (('no_speech_prob', 'NO_SPEECH_PROB'),
                                    ('avg_logprob', 'AVG_LOGPROB'),
                                    ('compression_ratio', 'COMPRESSION_RATIO')):
                    v = getattr(s, campo, None)
                    if isinstance(v, (int, float)):
                        trecho[nome] = round(float(v), 3)
                trechos.append(trecho)
        except Exception as e:                                 # noqa: BLE001
            # Decodificador que não abre o arquivo é ÁUDIO ilegível, não reconhecedor
            # quebrado. Os dois pedem conduta diferente: um manda baixar de novo, o
            # outro manda olhar a instalação. Guardá-los sob o mesmo nome esconderia
            # um download corrompido atrás de "o whisper falhou".
            de_audio = ('InvalidData', 'ffmpeg', 'av.error', 'Invalid data',
                        'moov atom', 'EOFError', 'PermissionError', 'FileNotFoundError',
                        'IsADirectoryError', 'UnicodeDecodeError')
            texto_do_erro = '%s: %s' % (type(e).__name__, str(e))
            e_audio = any(m.lower() in texto_do_erro.lower() for m in de_audio)
            fora.update({'ESTADO': AUDIO_ILEGIVEL if e_audio else FALHOU,
                         'TRANSCRIPT': None,
                         'MACHINE_SECONDS': round(time.time() - t, 2),
                         'WHY': texto_do_erro[:200],
                         'NAO_SIGNIFICA': ('que o vídeo não tem fala. %s'
                                           % ('O arquivo de áudio é que não abriu.'
                                              if e_audio else 'O reconhecedor é que caiu.'))})
            return fora

        gasto = time.time() - t
        texto = ' '.join(x['TEXT'] for x in trechos).strip()
        audio_s = round(float(getattr(info, 'duration', 0) or (dur or 0)), 2)
        fora.update({
            'TRANSCRIPT': texto or None,
            'TRANSCRIPT_SEGMENTS': trechos,
            'TRANSCRIPT_CHARS': len(texto),
            'ASR_LANGUAGE': language or getattr(info, 'language', NAO_SEI),
            'LANGUAGE_DETECTED': getattr(info, 'language', NAO_SEI),
            'LANGUAGE_CONFIDENCE': round(float(getattr(info, 'language_probability', 0)), 3),
            'AUDIO_SECONDS': audio_s,
            'MACHINE_SECONDS': round(gasto, 2),
            'REALTIME_FACTOR': round(audio_s / gasto, 2) if gasto else NAO_SEI,
        })
        if estourou:
            # Passou do teto: os trechos que vieram podem estar em laço. Marcar, nunca
            # descartar em silêncio e nunca tratar como "vídeo sem fala".
            fora.update({'ESTADO': ESTOUROU, 'TIMEOUT_LIMIT_S': teto,
                         'WHY': ('levou mais de %ds para %s s de áudio. Texto preservado, '
                                 'mas pode conter repetição em laço.' % (teto, audio_s)),
                         'NAO_SIGNIFICA': 'ausência de fala.'})
        elif not texto:
            fora.update({'ESTADO': VAZIO,
                         'WHY': 'o reconhecedor rodou e não devolveu palavra alguma',
                         'NAO_SIGNIFICA': ('que o vídeo não tem conteúdo. É um ESTADO do '
                                           'reconhecimento, não um veredito sobre o vídeo.')})
        else:
            fora['ESTADO'] = OK
        # Confiança baixa de idioma muda tudo num corpus que compara ES, IT e FR.
        if not language and isinstance(fora.get('LANGUAGE_CONFIDENCE'), float):
            fora['LANGUAGE_STATE'] = ('CONFIAVEL' if fora['LANGUAGE_CONFIDENCE'] >= 0.6
                                      else 'BAIXA_CONFIANCA — pode estar na língua errada')
        return fora


def carregar(modelo=None, nucleos=None, beam=None, lote=None):
    """→ (Motor, None) ou (None, motivo). Quem chama não precisa saber importar nada."""
    ok, motivo = disponivel()
    if not ok:
        return None, motivo
    try:
        return Motor(modelo=modelo, nucleos=nucleos, beam=beam, lote=lote), None
    except Exception as e:                                     # noqa: BLE001
        return None, '%s: %s' % (type(e).__name__, str(e)[:200])


# ═══════════════════════════════════════════════════════════════════ LINHA DE COMANDO

def _estado():
    ok, motivo = disponivel()
    print('SINTONIA_LIBS ............ %s' % LIBS)
    print('LIBS_EXISTE .............. %s' % ('SIM' if os.path.isdir(LIBS) else 'NÃO'))
    print('WHISPER_ENGINE_AVAILABLE . %s' % ('SIM' if ok else 'NÃO'))
    print('  %s' % motivo)
    print('NUCLEOS .................. %d' % (os.cpu_count() or 4))
    print('CONFIG_MEDIDA ............ %s' % json.dumps(config(), ensure_ascii=False))
    print()
    print('esta camada não coleta, não escolhe vídeo e não grava artefato.')
    return 0 if ok else 1


def _ouvir(caminho, idioma=None, modelo=None):
    motor, motivo = carregar(modelo=modelo)
    if not motor:
        print('sem motor: %s' % motivo)
        return 1
    print('modelo %s carregado em %.1f s · %d núcleos'
          % (motor.cfg['ASR_MODEL'], motor.segundos_de_carga, motor.cfg['ASR_CPU_THREADS']))
    r = motor.transcrever(caminho, language=idioma)
    print('ESTADO ........... %s' % r['ESTADO'])
    print('AUDIO_SECONDS .... %s' % r.get('AUDIO_SECONDS', NAO_SEI))
    print('MACHINE_SECONDS .. %s' % r.get('MACHINE_SECONDS', NAO_SEI))
    print('REALTIME_FACTOR .. %s' % r.get('REALTIME_FACTOR', NAO_SEI))
    print('SEGMENTOS ........ %d' % len(r.get('TRANSCRIPT_SEGMENTS') or []))
    print('PAID_API_COST_USD  0 — o custo é o MACHINE_SECONDS acima, e ele não é zero')
    for s in (r.get('TRANSCRIPT_SEGMENTS') or [])[:5]:
        print('  [%7.2f → %7.2f] %s' % (s['START_S'], s['END_S'], s['TEXT'][:70]))
    if r.get('WHY'):
        print('POR QUE .......... %s' % r['WHY'])
    return 0 if r['ESTADO'] == OK else 1


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'estado'
    if cmd == 'estado':
        raise SystemExit(_estado())
    if cmd == 'ouvir':
        if len(sys.argv) < 3:
            print('uso: asr_local.py ouvir <arquivo-de-audio> [idioma] [modelo]')
            raise SystemExit(2)
        raise SystemExit(_ouvir(sys.argv[2],
                                sys.argv[3] if len(sys.argv) > 3 else None,
                                sys.argv[4] if len(sys.argv) > 4 else None))
    print('uso: asr_local.py {estado|ouvir <arquivo> [idioma] [modelo]}')
    raise SystemExit(2)
