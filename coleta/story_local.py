#!/usr/bin/env python3
"""
STORY POR SESSÃO LOCAL — a rota própria. Zero Apify, zero API paga, zero cookie.

    O GITHUB DESPACHA. O PC LOCAL EXECUTA. A SESSÃO NÃO VIAJA.

Este arquivo é o dono da AQUISIÇÃO de Story ativo pela rota que já pertence ao
SINTONIA: o Chrome da própria pessoa, já autenticado, falando por CDP. Ele não
faz login, não lê cookie, não exporta sessão, não resolve CAPTCHA, não troca de
IP e não emula dispositivo. Se a plataforma barrar, o estado é o nome da barreira.

POR QUE OBSERVAR, E NÃO CHAMAR ENDPOINT INTERNO
--------------------------------------------------
A tentação é escrever à mão o endereço interno que a página usa para montar a
bandeja de Stories. Endereço interno muda sem aviso e sem versão, e no dia em que
mudar, o nosso pedido devolve vazio — que se lê como «a conta não tem Story».
Erro silencioso na direção errada é o pior defeito possível para conteúdo que
não volta.

Então a rota é: o navegador abre o perfil como qualquer pessoa abriria, e nós
OBSERVAMOS o que ele já pediu.

    NÃO PEDIR NADA QUE A PÁGINA JÁ NÃO FOSSE PEDIR.

A MEDIÇÃO QUE MUDOU A LEI DE MÍDIA
------------------------------------
A ordem era: se houver texto nativo, guarda o texto e não baixa nada. Medindo
as três bibliotecas maduras em 2026-09-09, a primeira porta quase nunca abre:

    Instaloader   `StoryItem.caption` existe desde a 4.10, mas NÃO expõe texto
                  de tela; não há propriedade de `tappable_objects` nem de
                  sticker de texto em lugar nenhum do código.
    gallery-dl    o ramo de Story não preenche `description`; a legenda só é
                  extraída em post normal.
    instagrapi    idem — só texto de enquete e de sticker de link.

O motivo é da plataforma, não das bibliotecas: no Story, a palavra escrita na
tela é PIXEL QUEIMADO NA IMAGEM. Ler isso exigiria OCR, e OCR está fora desta
missão por decisão do dono.

    NO STORY, TEXTO DE TELA NÃO É TEXTO. É IMAGEM.

Consequência prática, e ela precisa estar escrita para ninguém se surpreender: o
caminho do ÁUDIO deixa de ser exceção e passa a ser o caminho normal do conteúdo.
A porta de texto continua no código porque quando ela abre é a rota mais barata
que existe — mas planejar como se ela fosse a comum seria planejar errado.

A LEI DE MÍDIA — E ELA É O CONTRÁRIO DE UM ACERVO
---------------------------------------------------
A casa NÃO quer um arquivo de vídeos de Instagram. O valor do Story é o SINAL,
não a imagem. Então a cadeia decide pelo conteúdo, nesta ordem:

    tem texto nativo útil?   -> guarda texto + metadados. FIM. Não baixa nada.
    não tem, e tem áudio?    -> baixa o vídeo TEMPORARIAMENTE, extrai só o áudio,
                                faz o hash, transcreve, e APAGA O VÍDEO.
    não tem nem um nem outro -> VISUAL_ONLY. Não inventa conteúdo, não faz OCR.

    ORIGINAL_VIDEO_RETAINED = NO.

O vídeo temporário tem prazo de vida em minutos, e morre inclusive quando o
processamento falha — senão o `finally` que não existe vira o acervo que
ninguém pediu.

O QUE ESTE ARQUIVO NUNCA FAZ
------------------------------
Highlights. Arquivo. Backfill. Story expirado. A janela é a de agora:

    ACTIVE STORY, CURRENT 24H WINDOW, OBSERVED NOW.

E a lei de sempre continua valendo: publicar hoje não prova que aconteceu hoje.

    STORY_PUBLISHED_AT != FACT_TIME.
"""
import hashlib
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(HERE)
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401
import social_envelope as env   # noqa: E402

# ── ESTADOS ───────────────────────────────────────────────────────────────
OK = 'OK'
NO_ACTIVE_STORIES = 'NO_ACTIVE_STORIES'
PRIVATE_PROFILE = 'PRIVATE_PROFILE'
SESSION_MISSING = 'SESSION_MISSING'
SESSION_EXPIRED = 'AUTH_EXPIRED'
AUTH_INTERVENTION_REQUIRED = 'AUTH_INTERVENTION_REQUIRED'
RATE_LIMITED = 'RATE_LIMITED'
BROWSER_NOT_REACHED = 'BROWSER_NOT_REACHED'
TARGET_NOT_FOUND = 'SOURCE_GONE'

# ── TEXTO ─────────────────────────────────────────────────────────────────
TEXT_NATIVE = 'NATIVE'
TEXT_ABSENT = 'ABSENT'

# ── ÁUDIO ─────────────────────────────────────────────────────────────────
AUDIO_NOT_NEEDED = 'NOT_NEEDED'      # havia texto nativo; não se baixa nada
AUDIO_EXTRACTED = 'EXTRACTED'
AUDIO_NO_STREAM = 'VIDEO_NO_AUDIO'
AUDIO_ACQUISITION_FAILED = 'ACQUISITION_FAILED'
VISUAL_ONLY = 'VISUAL_ONLY'

# O vídeo é MEIO, nunca produto. Ele existe o tempo de virar áudio.
TEMP_VIDEO_MAX_LIFETIME_MINUTES = 10
CONCURRENCY = 1                      # uma sessão local, uma corrida. Nunca duas.


class SemSessao(RuntimeError):
    """Não há Chrome autenticado alcançável. Isto NÃO é «a conta não tem Story»."""


# ══════════════════════════════════════════════════════════════════════════
# TEXTO NATIVO — a pergunta que evita baixar qualquer byte
# ══════════════════════════════════════════════════════════════════════════
def texto_nativo(item):
    """O texto que a própria plataforma devolveu. NUNCA OCR.

    Ordem de preferência: legenda, depois os stickers de texto que o autor
    escreveu na tela. Ambos são texto REAL vindo da estrutura — não uma leitura
    nossa de pixels, que seria outra frente inteira e outra classe de erro.
    """
    partes = []
    cap = item.get('caption')
    if isinstance(cap, dict):
        cap = cap.get('text')
    if isinstance(cap, str) and cap.strip():
        partes.append(cap.strip())
    for chave in ('story_text', 'text_metadata', 'story_bloks_stickers'):
        for st in (item.get(chave) or []):
            t = (st or {}).get('text') if isinstance(st, dict) else None
            if isinstance(t, str) and t.strip():
                partes.append(t.strip())
    texto = '\n'.join(dict.fromkeys(partes)).strip()
    return (texto, TEXT_NATIVE) if texto else (None, TEXT_ABSENT)


# ══════════════════════════════════════════════════════════════════════════
# ÁUDIO — e o vídeo que morre depois
# ══════════════════════════════════════════════════════════════════════════
def tem_trilha_de_audio(caminho_video):
    """Pergunta ao ffprobe. Vídeo mudo é FATO sobre o Story; ferramenta ausente
    é fato sobre a máquina, e as duas não podem virar a mesma resposta."""
    if not shutil.which('ffprobe'):
        return None
    r = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'a',
                        '-show_entries', 'stream=codec_name', '-of', 'csv=p=0',
                        caminho_video], capture_output=True, text=True)
    return bool((r.stdout or '').strip())


def extrair_audio(caminho_video, destino):
    """Só o áudio, sem recomprimir quando o container deixa. (caminho, motivo).

    `-c:a copy` preserva o áudio original; se o container recusar, cai para um
    formato só — e um só, de propósito. Cinco formatos seriam cinco maneiras de
    a transcrição receber algo que não esperava.
    """
    if not shutil.which('ffmpeg'):
        return None, 'FFMPEG_AUSENTE'
    tentativas = (
        (['-vn', '-c:a', 'copy'], destino + '.m4a'),
        (['-vn', '-ac', '1', '-ar', '16000', '-c:a', 'pcm_s16le'], destino + '.wav'),
    )
    for args, saida in tentativas:
        r = subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', caminho_video]
                           + args + [saida], capture_output=True, text=True)
        if r.returncode == 0 and os.path.exists(saida) and os.path.getsize(saida) > 512:
            return saida, None
    return None, 'FFMPEG_FALHOU'


def sha256_do_arquivo(caminho):
    h = hashlib.sha256()
    with open(caminho, 'rb') as f:
        for bloco in iter(lambda: f.read(1 << 20), b''):
            h.update(bloco)
    return h.hexdigest()


def apagar_temporario(caminho):
    """O vídeo morre. Sempre. Inclusive quando o processamento falhou.

    Sem isto, a única coisa que sobra de uma corrida com defeito é exatamente o
    que a casa decidiu NÃO guardar — e um acervo de vídeo nasce por acidente,
    nunca por decisão.
    """
    try:
        if caminho and os.path.exists(caminho):
            os.remove(caminho)
        return True
    except OSError:
        return False


def videos_temporarios_restantes(pasta):
    """A prova de que a lei foi cumprida. Zero é o único número aceitável."""
    if not os.path.isdir(pasta):
        return 0
    return len([f for f in os.listdir(pasta)
                if f.lower().endswith(('.mp4', '.mov', '.webm'))])


def processar_midia(item_objeto, baixar, pasta_temp):
    """A lei de mídia inteira, num lugar só. `baixar(url, destino)` é injetado.

    Devolve o objeto com AUDIO_STATE resolvido. NUNCA levanta: falha de
    aquisição é estado do objeto, não interrupção da varredura — e o vídeo é
    apagado nos dois caminhos.
    """
    if item_objeto.get('TEXT_STATE') == TEXT_NATIVE:
        # Texto resolve. Não se baixa um byte.
        item_objeto['AUDIO_STATE'] = AUDIO_NOT_NEEDED
        item_objeto['ORIGINAL_VIDEO_RETAINED'] = 'NO'
        return item_objeto

    if item_objeto.get('MEDIA_TYPE') != 'VIDEO':
        item_objeto['AUDIO_STATE'] = VISUAL_ONLY
        item_objeto['ORIGINAL_VIDEO_RETAINED'] = 'NO'
        return item_objeto

    os.makedirs(pasta_temp, exist_ok=True)
    temp = os.path.join(pasta_temp, 'TEMP-%s.mp4' % item_objeto['NATIVE_ID'])
    item_objeto['TEMP_VIDEO_CREATED'] = 'YES'
    try:
        if not baixar(item_objeto.get('MEDIA_URL'), temp):
            # A URL assinada pode ter morrido entre observar e baixar. Esse é o
            # ataque central do conteúdo efêmero, e ele não pode virar «sem áudio».
            item_objeto['AUDIO_STATE'] = AUDIO_ACQUISITION_FAILED
            return item_objeto
        tem = tem_trilha_de_audio(temp)
        if tem is False:
            item_objeto['AUDIO_STATE'] = AUDIO_NO_STREAM
            return item_objeto
        audio, porque = extrair_audio(temp, os.path.join(
            pasta_temp, 'STORY-%s' % item_objeto['NATIVE_ID']))
        if not audio:
            item_objeto['AUDIO_STATE'] = AUDIO_ACQUISITION_FAILED
            item_objeto['AUDIO_FAILURE'] = porque
            return item_objeto
        item_objeto['AUDIO_STATE'] = AUDIO_EXTRACTED
        item_objeto['AUDIO_REFERENCE'] = os.path.basename(audio)
        item_objeto['AUDIO_BYTES'] = os.path.getsize(audio)
        item_objeto['AUDIO_SHA256'] = sha256_do_arquivo(audio)
        item_objeto['AUDIO_PATH'] = audio
        return item_objeto
    finally:
        # O `finally` é a lei. Sucesso ou falha, o vídeo não sobrevive à função.
        item_objeto['TEMP_VIDEO_DELETED'] = 'YES' if apagar_temporario(temp) else 'NO'
        item_objeto['ORIGINAL_VIDEO_RETAINED'] = 'NO'


# ══════════════════════════════════════════════════════════════════════════
# FRESCOR
# ══════════════════════════════════════════════════════════════════════════
def idade_minutos(publicado_iso, agora_iso=None):
    """Quantos minutos o Story já tinha quando o SINTONIA o viu.

    É OBSERVAÇÃO, não julgamento. Nada aqui decide que um Story recente é
    importante — isso é da Intelligence, e chamar de «descoberta» o que é só
    «recente» seria inventar significado.
    """
    import datetime
    if not publicado_iso or publicado_iso == env.DESCONHECIDO:
        return None
    try:
        p = datetime.datetime.fromisoformat(str(publicado_iso))
        a = (datetime.datetime.fromisoformat(agora_iso) if agora_iso
             else datetime.datetime.now(datetime.timezone.utc))
        if p.tzinfo is None:
            p = p.replace(tzinfo=datetime.timezone.utc)
        if a.tzinfo is None:
            a = a.replace(tzinfo=datetime.timezone.utc)
        return max(0, int((a - p).total_seconds() // 60))
    except (TypeError, ValueError):
        return None


NEW = 'NEW'
RESEEN = 'RESEEN'


def novidade(story_ids_agora, vistos_antes):
    """NEW vs RESEEN por NATIVE_ID. O mesmo Story visto três vezes é UM Story.

    Emite fato, não alerta: `NEW_STORY_DETECTED` é uma observação para o
    downstream decidir o que fazer. O Scrap não diz que algo é importante.
    """
    novos = [i for i in story_ids_agora if i not in vistos_antes]
    revistos = [i for i in story_ids_agora if i in vistos_antes]
    return {'NEW': novos, 'RESEEN': revistos,
            'NEW_STORY_DETECTED': bool(novos)}
