#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O REEL DEIXA DE SER MUDO — a cadeia que liga o vídeo público à fala escrita.

    py ferramentas/reel_transcricao.py censo
    py ferramentas/reel_transcricao.py um --url=https://www.instagram.com/reel/XXXX/
    py ferramentas/reel_transcricao.py um --url=... --midia=/caminho/ou/URL.mp4
    py ferramentas/reel_transcricao.py posts INSTAGRAM        # sobre o que já foi coletado

O BURACO QUE ISTO FECHA
-------------------------
Um Reel pode falar noventa segundos sobre pressão de septoriose, produto, estágio
de aplicação e região — e trazer como legenda apenas «Confira nosso dia de campo».
`coleta/comunicacao_classificar.py` lê `TITLE` e `TEXT`, e `TEXT` é a LEGENDA. Logo,
até aqui, todo o conteúdo técnico falado era invisível para o SINTONIA.

    LEGENDA != FALA. São dois textos, de dois autores diferentes do mesmo minuto.

E é por isso que este ficheiro NUNCA escreve a fala por cima da legenda. Ele cria
um campo próprio, `TRANSCRIPT_TEXT`, ao lado de `CAPTION_TEXT`. Se amanhã uma
classificação nascer de uma frase falada, tem de continuar a ser possível prová-lo
— e isso é impossível depois de somar os dois num campo só.

O QUE ESTE FICHEIRO É, E O QUE ELE NÃO É
------------------------------------------
Ele é a CADEIA. Não é reconhecedor (esse é `ferramentas/fala_local.py`, dono
único), não é rotação de chave (`ferramentas/apify_pool.py`), não é porta de rota
paga (`coleta/coletor.py`), não é contrato de artefato (`leis/artefato.py`) e não é
a porta de entrada do pedido (`orquestrador/orquestrador.py`). Ele liga essas peças
na ordem certa e responde às perguntas de proveniência no fim.

    UMA CAPACIDADE, UM DONO. Este ficheiro não duplica nenhum deles.

A ORDEM, E O QUE CADA DEGRAU PRESERVA
---------------------------------------
    IDENTIDADE DO REEL      quem é a publicação (URL, shortcode, conta)
      ↓
    MÍDIA                   um endereço de vídeo, de onde quer que venha
      ↓
    RAW                     os BYTES, com SHA256 e caminho — artefato, com ficha
      ↓
    ÁUDIO                   WAV 16 kHz mono, meio de trabalho, não é artefato
      ↓
    DERIVED                 a fala escrita, com PAI DECLARADO e tempos

    RAW É IMUTÁVEL. O texto nasce AO LADO, nunca por cima.

TRÊS CONFUSÕES QUE ESTE FICHEIRO SE RECUSA A FAZER
----------------------------------------------------
1. **SHA256 não é identidade de observação.** O `ARTIFACT_ID` sai dos bytes, e
   dois RUNs que trazem os mesmos bytes produzem o MESMO nome — é assim que o
   retry não mente. Mas `RAW_OBSERVATION_ID` é outra coisa: é a linha em
   `raw_asset`, e só existe quando a fundação de Collection a criou. Aqui ele
   nasce `NOT_KNOWN` e só é preenchido por quem tenha a prova.

       SHA256 IDENTIFICA CONTEÚDO. NÃO IDENTIFICA OBSERVAÇÃO.

2. **URL vencida não é vídeo inexistente.** O endereço do MP4 é assinado pela CDN
   e morre em horas. Quando morre, o estado é `MEDIA_URL_EXPIRED` — e há uma
   segunda tentativa grátis pela rota do embed público.

       ENDEREÇO VENCIDO != CONTEÚDO AUSENTE.

3. **Legenda não é transcrição.** Se a plataforma devolver um transcript pronto,
   ele entra com `TRANSCRIPT_PROVIDER = SOURCE_PLATFORM` e os campos de motor
   ficam `NAO_SE_APLICA` — nunca fingindo que esta máquina ouviu.

O QUE ELE NUNCA DECIDE
------------------------
Não decide `FACT_LOCATION` nem `FACT_TIME`. Ouvir «Puglia» é prova de que alguém
disse «Puglia», não de que o fato aconteceu lá. A fala é EVIDÊNCIA para uma camada
acima; esta gaveta entrega evidência, não veredito.
"""
from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
import _gavetas  # noqa: E402,F401 — poe as gavetas do processo no caminho

import artefato as art          # noqa: E402 — o contrato de artefato, dono único
import fala_local as fl         # noqa: E402 — o reconhecedor, dono único

VERSAO = '1.0.0'
PIPELINE = 'REEL-TRANSCRICAO-V1'
NAO_SEI = art.NAO_SEI                 # "NAO SEI"
NAO_SE_APLICA = art.NAO_SE_APLICA
NOT_KNOWN = 'NOT_KNOWN'               # o dialecto da camada de comunicação

# ── ONDE CADA COISA MORA ────────────────────────────────────────────────────
# O byte pesado NUNCA entra no Git. `data/raw/` já é ignorado pelo .gitignore
# desta casa, e a decisão D-003 diz porquê: um MP4 entra no pack pelo tamanho
# integral, para sempre, sem delta.
#
#     O GIT NÃO É DEPÓSITO DE VÍDEO.
MIDIA = os.path.join(ROOT, 'data', 'raw', 'REEL-MIDIA')
# O TEXTO é leve e é a entrega. Esse vive em samples, versionado, como a casa
# já faz com as outras transcrições.
SAIDA = os.path.join(ROOT, 'data', 'samples', 'REEL-TRANSCRICOES')

# ── QUAL MODELO, E POR QUE NÃO O MAIS BARATO ────────────────────────────────
# Medido em 2026-09-10, nesta máquina (4 núcleos, sem GPU), sobre TRÊS Reels
# reais — não sobre um teste sintético:
#
#   termo dito           `small`            `medium`
#   ------------------   ----------------   ----------------
#   mais (a cultura)     «MICE»             «mais»
#   maiscoltori          «mai scoltori»     «maiscoltori»
#   Discovery Seeds      «Discovery Seats»  «Discovery Seeds»
#   Syngenta (ES)        «Singentha»        «Syngenta»
#   eventi               «venti»            «eventi»
#
#   velocidade           4,5x-5,1x          1,5x-2,5x  (≈2,8x mais lento)
#
# `small` acerta a frase e ERRA EXATAMENTE O QUE INTERESSA: o nome da cultura e
# o nome da marca. Num corpus que existe para saber de que cultura e de que
# produto o concorrente fala, «MICE» em vez de «mais» não é uma imprecisão de
# transcrição — é o sinal perdido.
#
#     BARATO QUE PERDE O SINAL NÃO É BARATO.
#
# `medium` continua a correr mais depressa do que o tempo real mesmo sem GPU:
# um Reel de 90 s custa ~40-60 s de máquina, e zero dólares. Por isso o padrão
# DESTA cadeia sobe, enquanto `fala_local.MODELO_PADRAO` fica em `small` — os
# dois programas de lote que ja existem foram orcados nele, e mudar o orcamento
# deles nao e desta missao.
# A POLITICA VIVE NO DONO. Este ficheiro diz QUEM E, nunca QUAL MODELO — a
# tabela, a medicao que a justifica e a variavel de ambiente estao todas em
# `fala_local.MODELOS_POR_CHAMADOR`. O valor nao mudou: continua `medium`,
# e continua por medicao.
MODELO_PADRAO = fl.modelo_de('reel')

MISSION = os.environ.get('SINTONIA_MISSION') or '14-COMUNICACAO-PUBLICA-DO-CONCORRENTE'
RUNNER = os.environ.get('RUNNER_NAME') or NOT_KNOWN

# ── OS PROVEDORES, DECLARADOS — NUNCA UM FALLBACK EM SILÊNCIO ───────────────
# Um fallback que não se declara transforma «a rota paga falhou» em «o vídeo não
# tinha fala», e ninguém descobre até a conclusão já ter sido usada.
CAPTURA_FORNECIDA = 'MEDIA_FORNECIDA'   # alguém já tinha o endereço ou o ficheiro
# O byte JÁ ESTAVA CÁ, de uma corrida anterior. Merece nome próprio: dizer
# «fornecida» esconderia que ninguém foi buscar nada nesta corrida, e é
# exatamente isso que faz o retry ser barato.
CAPTURA_JA_PRESERVADA = 'MEDIA_JA_PRESERVADA'
CAPTURA_YTDLP = 'LOCAL_YTDLP'           # a rota grátis que HOJE funciona
CAPTURA_EMBED = 'LOCAL_EMBED'           # o embed público, grátis, sem navegador
CAPTURA_APIFY = 'APIFY'                 # a rota paga, pelo dono canónico
CAPTURAS = (CAPTURA_FORNECIDA, CAPTURA_JA_PRESERVADA, CAPTURA_YTDLP,
            CAPTURA_EMBED, CAPTURA_APIFY)

# ── A ESCADA DE CAPTURA, E ELA É DECLARADA ──────────────────────────────────
# Medido em 2026-09-10, deste contentor:
#   · listar o PERFIL  → 302 para /accounts/login/ e HTTP 429 no extractor de perfil
#   · ler o EMBED por HTTP → 200 com 624 KB e ZERO endereço de vídeo (é casca JS)
#   · abrir com NAVEGADOR → ERR_CONNECTION_RESET em qualquer sítio (rede fechada
#     ao browser neste ambiente; não é a Instagram que recusa)
#   · pedir a PUBLICAÇÃO DIRETA com yt-dlp → FUNCIONA, com metadados e MP4
#
# É por isso que a escada começa no endereço direto. E é por isso que ela é uma
# ESCADA e não um `try/except` mudo: cada degrau que falha fica escrito em
# `CAPTURE_ATTEMPTS`, para ninguém confundir «não consegui buscar» com «não há».
#
#     FALLBACK EM SILÊNCIO TRANSFORMA FALHA DE ROTA EM AUSÊNCIA DE CONTEÚDO.
YTDLP_TENTATIVAS = int(os.environ.get('SINTONIA_YTDLP_TENTATIVAS') or 4)

ASR_LOCAL = 'LOCAL_ASR'                 # esta máquina ouviu
FONTE = 'SOURCE_PLATFORM'               # a plataforma entregou pronto
NAO_PEDIDO = 'NOT_REQUESTED'

# ── OS ESTADOS DA MÍDIA ─────────────────────────────────────────────────────
MEDIA_OK = 'MEDIA_OK'
MEDIA_SEM_ENDERECO = 'MEDIA_URL_ABSENT'
MEDIA_VENCIDA = 'MEDIA_URL_EXPIRED'
MEDIA_FALHOU = 'MEDIA_DOWNLOAD_FAILED'
MEDIA_NAO_E_VIDEO = 'NOT_A_VIDEO'
MEDIA_SEM_AUDIO_SO = 'AUDIO_ONLY_UNAVAILABLE'
# Os bytes vieram e traziam imagem quando ninguem pediu imagem. NAO e falha de
# rede e NAO e ausencia de fala: e a rota a entregar mais do que foi pedido.
MEDIA_KIND_DIVERGE = 'MEDIA_KIND_MISMATCH'
ESTADOS_DE_MIDIA = (MEDIA_OK, MEDIA_SEM_ENDERECO, MEDIA_VENCIDA, MEDIA_FALHOU,
                    MEDIA_NAO_E_VIDEO, MEDIA_SEM_AUDIO_SO, MEDIA_KIND_DIVERGE)

# ── O QUE SE PEDE A ROTA, QUE NAO E O MESMO QUE COM QUE FERRAMENTA ──────────
# A C8 fechou a lei e a C9 mediu que ninguem a cumpria:
#
#     TRANSCRIPTION NEED != VIDEO DOWNLOAD.
#
# Ate aqui esta cadeia pedia ao `yt-dlp` o formato PADRAO — que e o melhor video
# MAIS o melhor audio — e so depois deitava fora a imagem com `ffmpeg -vn`. O
# resultado era verdadeiro e o nome estava errado:
#
#     AQUISICAO DE VIDEO + DERIVACAO DE AUDIO  !=  AQUISICAO SO DE AUDIO.
#
# Medido nesta casa em 2026-09-11, no Reel `C-63RfHoJTU`: o formato padrao pede
# DOIS fluxos (`...v` a 2218,712 kbps e `...a` a 75,941 kbps); pedir so audio
# pede UM, e esse um e exatamente o segundo dos dois que ja eram pedidos.
#
#     A ROTA NOVA E UM SUBCONJUNTO ESTRITO DA ROTA VELHA. Ela nao alcanca
#     endereco novo, nao alcanca host novo e nao alarga superficie nenhuma:
#     deixa de pedir uma das duas coisas que ja pedia.
#
# `MEDIA_KIND` e um eixo PROPRIO, e nao se deduz do fornecedor. O `yt-dlp` traz
# video e traz audio; dizer `LOCAL_YTDLP` nao diz o que veio. Por isso o
# fornecedor continua a ser o que era — inventar `LOCAL_YTDLP_AUDIO` seria
# fundir FERRAMENTA com CARGA, que e o erro que `scrap_fornecedores` existe
# para impedir.
MIDIA_AUDIO = 'AUDIO'
MIDIA_VIDEO = 'VIDEO'
MIDIA_KINDS = (MIDIA_AUDIO, MIDIA_VIDEO)

#: O seletor que pede SOMENTE a faixa de audio. Na lingua do `yt-dlp`,
#: `bestaudio` e «o melhor formato SEM video» — e quando nao existir nenhum ele
#: FALHA, que e o comportamento certo: cair para o video inteiro seria a
#: mentira que esta missao veio acabar.
SELETOR_SO_AUDIO = 'bestaudio'

#: A bandeira nao e a prova. Um seletor pode mudar de significado numa versao
#: nova do `yt-dlp`, e uma extensao `.m4a` nao garante que dentro nao venha
#: imagem. Por isso os bytes sao SEMPRE conferidos depois de chegarem, e e essa
#: conferencia — nao a bandeira — que decide se houve aquisicao so de audio.
#:
#:     PEDIR AUDIO != TER RECEBIDO SO AUDIO.

UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')


# ═══════════════════════════════════════════════════ IDENTIDADE DA PUBLICAÇÃO
_RE_IG = re.compile(
    r'instagram\.com/(?:([A-Za-z0-9_.]+)/)?(?:reel|reels|p|tv)/([A-Za-z0-9_-]+)')


def identidade_do_url(url):
    """→ a identidade mínima de uma publicação, tirada do endereço. Nunca inventa.

    Se o endereço não for de uma publicação reconhecível, o shortcode fica
    `NOT_KNOWN` — e quem chamar decide o que fazer. Fabricar um identificador a
    partir de um endereço que não o contém seria criar um `POST_ID` falso, e um
    identificador falso contamina tudo o que se ligar a ele depois.
    """
    url = (url or '').strip()
    m = _RE_IG.search(url)
    if m:
        handle, post = m.group(1), m.group(2)
        return {
            'PLATFORM': 'INSTAGRAM', 'POST_ID': post,
            # O endereço canónico é o curto: é o que a plataforma serve a qualquer
            # um, sem depender de o autor ter mudado de nome de utilizador.
            'SOURCE_URL': 'https://www.instagram.com/reel/%s/' % post,
            'URL_AS_GIVEN': url,
            # O @ que veio DENTRO do endereço. Não é a conta «provada» do lote
            # congelado — é o que o endereço declara — e por isso tem nome próprio.
            'ACCOUNT_HANDLE_FROM_URL': handle or NOT_KNOWN,
            'ACCOUNT_URL': ('https://www.instagram.com/%s/' % handle
                            if handle else NOT_KNOWN),
        }
    return {'PLATFORM': NOT_KNOWN, 'POST_ID': NOT_KNOWN,
            'SOURCE_URL': url or NOT_KNOWN, 'URL_AS_GIVEN': url,
            'ACCOUNT_HANDLE_FROM_URL': NOT_KNOWN, 'ACCOUNT_URL': NOT_KNOWN}


def de_item_de_comunicacao(item):
    """O item já normalizado por `coleta/comunicacao_coleta.py` vira identidade.

    Esta é a porta que evita recolher outra vez o que já foi pago: um Reel que já
    passou pela coleta tem `POST_ID`, `URL`, conta e país — e o único que falta é
    a fala.
    """
    ident = identidade_do_url(item.get('URL') or '')
    if item.get('POST_ID') not in (None, '', NOT_KNOWN):
        ident['POST_ID'] = item['POST_ID']
    ident.update({
        'PLATFORM': item.get('PLATFORM') or ident['PLATFORM'],
        'ACCOUNT_ID': item.get('ACCOUNT_ID', NOT_KNOWN),
        'ACCOUNT_URL': item.get('ACCOUNT_URL', NOT_KNOWN),
        'COMPANY': item.get('COMPANY', NOT_KNOWN),
        'COUNTRY_SCOPE': item.get('COUNTRY_SCOPE', NOT_KNOWN),
        'PUBLISHED_AT': item.get('PUBLISHED_AT', NOT_KNOWN),
        # A LEGENDA, marcada como legenda. Ela viaja junto para que a camada de
        # cima possa comparar — nunca para ser somada à fala.
        'CAPTION_TEXT': item.get('TEXT', NOT_KNOWN),
        'MEDIA_TYPE': item.get('MEDIA_TYPE', NOT_KNOWN),
        # O endereco ASSINADO que a coleta guardou. Chama-se TEMPORARY porque
        # e: morre em horas, e quando morre isso NAO e o video ter sumido.
        'MEDIA_URL': item.get('MEDIA_URL_TEMPORARY',
                              item.get('MEDIA_URL', NOT_KNOWN)),
        'MEDIA_DURATION_S': item.get('MEDIA_DURATION_S', NOT_KNOWN),
        # A cadeia da coleta, se ela existir. NUNCA inventada aqui.
        'COLLECTION_RUN_ID': item.get('COLLECTION_RUN_ID', NOT_KNOWN),
        'RAW_OBSERVATION_ID': item.get('RAW_OBSERVATION_ID', NOT_KNOWN),
        'RAW_REFERENCE': item.get('RAW_REFERENCE', NOT_KNOWN),
    })
    return ident


# ── A LÍNGUA VEM DO PAÍS DA CONTA, QUANDO ELE FOI PROVADO ───────────────────
# Isto não é suposição: o país da CONTA é conhecido desde o lote congelado, de
# graça, na fase de identidade. Usar o que já foi provado é diferente de adivinhar.
# E é o remédio para o defeito medido nesta casa: dois reels espanhóis voltaram
# `en` com confiança 0,37 porque a abertura tinha música.
IDIOMA_DO_PAIS = {'ES': 'es', 'IT': 'it', 'FR': 'fr', 'PT': 'pt', 'BR': 'pt',
                  'UK': 'en', 'GB': 'en', 'US': 'en', 'DE': 'de', 'RO': 'ro'}


def idioma_provado(country_scope):
    return IDIOMA_DO_PAIS.get(str(country_scope or '').upper())


# ═══════════════════════════════════════════════════════════ ONDE ESTÁ A MÍDIA
_RE_VIDEO = re.compile(r'"video_url"\s*:\s*"([^"]+)"')
_RE_VIDEO2 = re.compile(r'<meta\s+property="og:video"\s+content="([^"]+)"')


def midia_do_embed(post_id, timeout=45):
    """A rota grátis: o embed público devolve o endereço do MP4? → (url, motivo).

    ATENÇÃO A UMA ARMADILHA MEDIDA: o embed responde **HTTP 200 com página cheia
    mesmo para um shortcode que não existe**. Verificado em 2026-09-10 — um pedido
    a `/p/ZZZZZZZZZZZ/embed/captioned/` devolveu 200 com 624 KB. Portanto o código
    de estado NÃO é prova de nada aqui; a prova é haver endereço de vídeo dentro.

        HTTP 200 NÃO É PROVA DE QUE A PUBLICAÇÃO EXISTE.
    """
    url = 'https://www.instagram.com/p/%s/embed/captioned/' % post_id
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            html = r.read().decode('utf-8', 'replace')
    except urllib.error.HTTPError as e:
        return None, 'EMBED_HTTP_%s — a plataforma recusou este pedido' % e.code
    except Exception as e:                                      # noqa: BLE001
        return None, 'EMBED_FALHOU: %s' % type(e).__name__
    for rx in (_RE_VIDEO, _RE_VIDEO2):
        m = rx.search(html)
        if m:
            return m.group(1).encode().decode('unicode_escape'), None
    if 'loginForm' in html or 'accounts/login' in html:
        return None, ('EMBED_PEDE_LOGIN — este endereço de saída está a ser tratado '
                      'como não-público. Isto NÃO é conteúdo privado nem publicação '
                      'ausente: é o IP desta máquina.')
    return None, ('EMBED_SEM_VIDEO — a página abriu (%d bytes) e não tinha endereço '
                  'de vídeo. Pode ser publicação de imagem, pode ser removida, pode '
                  'ser bloqueio. NÃO se sabe qual.' % len(html))


def baixar(url, destino, timeout=180):
    """→ (bytes_gravados, motivo_da_falha). Só isto: não interpreta, não decide."""
    os.makedirs(os.path.dirname(os.path.abspath(destino)) or '.', exist_ok=True)
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r, open(destino, 'wb') as f:
            while True:
                bloco = r.read(1 << 20)
                if not bloco:
                    break
                f.write(bloco)
    except urllib.error.HTTPError as e:
        # 403 e 410 na CDN da Meta são a assinatura de endereço vencido.
        if e.code in (403, 410):
            return 0, 'HTTP_%d — endereço assinado vencido' % e.code
        return 0, 'HTTP_%d' % e.code
    except Exception as e:                                      # noqa: BLE001
        return 0, '%s' % type(e).__name__
    n = os.path.getsize(destino)
    if n < 10000:
        # Download parcial ou página de erro gravada como se fosse vídeo.
        return n, ('CORPO_PEQUENO_DEMAIS: %d bytes. Um vídeo não pesa isto — o que '
                   'veio provavelmente é uma página de erro.' % n)
    return n, None


def ytdlp_disponivel():
    try:
        import yt_dlp  # noqa: F401
        return True
    except ImportError:
        import shutil
        return bool(shutil.which('yt-dlp'))


def _ytdlp(args, timeout=300):
    """Chama o yt-dlp como PROCESSO, e não como biblioteca importada.

    De propósito: o extractor dele muda depressa, e uma exceção interna a subir
    pelo nosso processo derrubaria um lote inteiro. Como processo, o pior que
    acontece é um código de saída — que é um estado, e estado a casa sabe tratar.
    """
    import subprocess
    base = [sys.executable, '-m', 'yt_dlp', '--no-warnings', '--no-progress']
    try:
        return subprocess.run(base + args, capture_output=True, text=True,
                              encoding='utf-8', errors='replace', timeout=timeout)
    except Exception as e:                                      # noqa: BLE001
        class _R:                                               # pragma: no cover
            returncode, stdout, stderr = 1, '', '%s' % type(e).__name__
        return _R()


def metadados_ytdlp(url, tentativas=None):
    """Os METADADOS da publicação, de graça, sem baixar o vídeo. → (dict, motivo).

    Isto é a segunda perna do pedido — «coletar metadados» — e ela é separada do
    download de propósito: saber a duração ANTES de baixar é o que permite dizer
    quanto vai custar em tempo de máquina, e recusar o que não vale.

    A PLATAFORMA RESPONDE VAZIO DE VEZ EM QUANDO, E ISSO NÃO É «NÃO EXISTE».
    Medido em 2026-09-10: o mesmo endereço devolveu «Instagram sent an empty media
    response» à primeira e metadados completos à segunda, sem nada ter mudado.
    Tratar a primeira resposta como veredito apagaria publicações reais do corpus.
    """
    for _ in range(tentativas or YTDLP_TENTATIVAS):
        r = _ytdlp(['-J', url])
        if r.returncode == 0 and (r.stdout or '').strip() not in ('', 'null'):
            try:
                d = json.loads(r.stdout)
            except ValueError:
                continue
            if not d:
                continue
            return {
                'POST_ID': d.get('id') or NOT_KNOWN,
                'TITLE': d.get('title') or NOT_KNOWN,
                # `description` do yt-dlp É A LEGENDA. Fica com o nome que diz isso.
                'CAPTION_TEXT': d.get('description') or NOT_KNOWN,
                'ACCOUNT_ID': d.get('uploader_id') or d.get('channel_id') or NOT_KNOWN,
                'ACCOUNT_NAME': d.get('uploader') or NOT_KNOWN,
                'PUBLISHED_AT': _iso_de_epoch(d.get('timestamp')) or (
                    _iso_de_data(d.get('upload_date')) or NOT_KNOWN),
                'MEDIA_DURATION_S': d.get('duration') if d.get('duration') else NOT_KNOWN,
                'MEDIA_TYPE': 'VIDEO' if d.get('ext') == 'mp4' else (d.get('ext') or NOT_KNOWN),
                'WIDTH': d.get('width') or NOT_KNOWN,
                'HEIGHT': d.get('height') or NOT_KNOWN,
                'VIEW_COUNT': d.get('view_count') if d.get('view_count') is not None else NOT_KNOWN,
                'LIKE_COUNT': d.get('like_count') if d.get('like_count') is not None else NOT_KNOWN,
                'METADATA_PROVIDER': CAPTURA_YTDLP,
            }, None
        erro = (r.stderr or '').strip().splitlines()[-1:] or ['']
    return None, ('YTDLP_SEM_METADADOS apos %d tentativas: %s'
                  % (tentativas or YTDLP_TENTATIVAS, erro[0][:200]))


def _iso_de_epoch(ts):
    if not ts:
        return None
    import datetime
    return datetime.datetime.fromtimestamp(
        int(ts), datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def _iso_de_data(d):
    if not d or len(str(d)) != 8:
        return None
    d = str(d)
    return '%s-%s-%s' % (d[:4], d[4:6], d[6:])


def midia_por_ytdlp(url, alvo, tentativas=None, *, kind=MIDIA_AUDIO):
    """Baixa a mídia pública pelo endereço DIRETO. → (caminho, motivo).

    A rota do PERFIL está fechada a esta máquina (302 para login, 429 no extractor).
    A rota da PUBLICAÇÃO DIRETA não está. São duas rotas diferentes e medem coisas
    diferentes — confundi-las faria concluir «Instagram bloqueado» quando o que
    está bloqueado é a listagem.

        DESCOBRIR != BUSCAR. O que falha aqui é o descobrir.

    E `kind` decide O QUE se pede, não com que ferramenta. Com `MIDIA_AUDIO`
    entra `-f bestaudio` e a imagem nunca é pedida; sem ele o `yt-dlp` escolhe
    o padrão, que é o melhor vídeo MAIS o melhor áudio.

        NÃO HÁ QUEDA DE AUDIO PARA VIDEO AQUI. Se `bestaudio` não existir, o
        `yt-dlp` falha e o estado sai `AUDIO_ONLY_UNAVAILABLE`. Tentar o vídeo
        inteiro a seguir seria transformar falha de rota em autorização para
        pedir mais — que é exatamente o que a lei da C8 proíbe.
    """
    modelo_saida = os.path.splitext(alvo)[0] + '.%(ext)s'
    os.makedirs(os.path.dirname(os.path.abspath(alvo)) or '.', exist_ok=True)
    seletor = ['-f', SELETOR_SO_AUDIO] if kind == MIDIA_AUDIO else []
    erro = ['']
    for _ in range(tentativas or YTDLP_TENTATIVAS):
        r = _ytdlp(seletor + ['-o', modelo_saida, url], timeout=600)
        achado = _achar_saida(alvo, kind=kind)
        if achado:
            if kind == MIDIA_AUDIO:
                # A CONFERENCIA E QUE DECIDE, NAO A BANDEIRA. Ver `SELETOR_SO_AUDIO`.
                limpo, porque = fl.so_audio(achado)
                if not limpo:
                    return None, 'MEDIA_KIND_MISMATCH: pediu-se audio e %s' % porque
            return achado, None
        erro = (r.stderr or '').strip().splitlines()[-1:] or ['']
    fim = erro[0][:200] if erro and erro[0] else NOT_KNOWN
    if kind == MIDIA_AUDIO and 'format is not available' in fim.lower():
        return None, 'AUDIO_ONLY_UNAVAILABLE: %s' % fim
    return None, 'YTDLP_SEM_MIDIA: %s' % fim


#: As extensoes por ordem de PREFERENCIA, e a ordem depende do que se pediu.
#: Quando se pede audio, um `.m4a` ao lado de um `.mp4` e a escolha certa — e a
#: ordem antiga, que punha `.mp4` primeiro, devolveria o video.
EXT_AUDIO = ('.m4a', '.opus', '.webm', '.mp3', '.aac', '.ogg')
EXT_VIDEO = ('.mp4', '.mkv', '.webm')


def _achar_saida(alvo, *, kind=None):
    base = os.path.splitext(alvo)[0]
    if kind == MIDIA_AUDIO:
        ordem = EXT_AUDIO + tuple(e for e in EXT_VIDEO if e not in EXT_AUDIO)
    elif kind == MIDIA_VIDEO:
        ordem = EXT_VIDEO + tuple(e for e in EXT_AUDIO if e not in EXT_VIDEO)
    else:
        ordem = EXT_VIDEO + EXT_AUDIO
    vistos = []
    for ext in ordem:
        if ext in vistos:
            continue
        vistos.append(ext)
        p = base + ext
        if os.path.exists(p) and os.path.getsize(p) > 10000:
            return p
    return None


def obter_midia(ident, *, midia_url=None, midia_ficheiro=None, tentativas=None,
                kind=MIDIA_AUDIO, midia_url_kind=None):
    """Põe os bytes no disco. → (caminho, provedor, estado, motivo, degraus).

    A ORDEM É DECLARADA, E CADA DEGRAU DIZ O SEU NOME. Nada de cair para a rota
    seguinte sem registar que caiu.

    `kind` diz O QUE se quer, e a escada inteira obedece. Com `MIDIA_AUDIO`:

        · o degrau do `yt-dlp` pede `-f bestaudio` e confere os bytes;
        · um endereço entregue por quem chama só é usado se ele DECLARAR que
          é áudio — `midia_url_kind`. Sem declaração, não se baixa;
        · o embed é saltado, porque o que ele serve é o MP4 inteiro.

    Os dois últimos não são zelo a mais. Um endereço de vídeo baixado em
    silêncio dentro de uma cadeia de transcrição faria `VIDEO_BYTES > 0` numa
    rota que jurou não pedir imagem — e a jura passaria no teste do seletor.

        FALHA DE ROTA NÃO É AUTORIZAÇÃO PARA PEDIR MAIS.
    """
    post_id = ident.get('POST_ID') or NOT_KNOWN
    seguro = re.sub(r'[^A-Za-z0-9_.-]', '_', post_id)
    ext_alvo = '.m4a' if kind == MIDIA_AUDIO else '.mp4'
    alvo = os.path.join(MIDIA, '%s%s' % (seguro, ext_alvo))
    degraus = []

    if midia_ficheiro:
        if not os.path.exists(midia_ficheiro):
            degraus.append({'PROVIDER': CAPTURA_FORNECIDA, 'RESULT': MEDIA_FALHOU,
                            'WHY': 'o ficheiro indicado não existe'})
            return None, CAPTURA_FORNECIDA, MEDIA_FALHOU, (
                'o ficheiro indicado não existe: %s' % midia_ficheiro), degraus
        degraus.append({'PROVIDER': CAPTURA_FORNECIDA, 'RESULT': MEDIA_OK,
                        'WHY': 'ficheiro entregue por quem chamou'})
        return midia_ficheiro, CAPTURA_FORNECIDA, MEDIA_OK, None, degraus

    ja = _achar_saida(alvo, kind=kind)
    if ja:
        # Já cá está. Rebaixar seria pagar duas vezes pelo mesmo byte — e, na rota
        # paga, pagar mesmo.
        #
        # MAS REUSAR NÃO É ADQUIRIR. Se o que está no disco é o MP4 de uma
        # corrida antiga, isto é `REUSED_VIDEO + AUDIO_DERIVATION` — continua a
        # servir, e continua a NÃO ser aquisição só de áudio. O degrau diz qual
        # dos dois foi, e quem lê decide; nenhuma prova de audio-only pode
        # apoiar-se neste caminho.
        limpo, _porque = fl.so_audio(ja) if kind == MIDIA_AUDIO else (False, None)
        degraus.append({'PROVIDER': CAPTURA_JA_PRESERVADA, 'RESULT': MEDIA_OK,
                        'MEDIA_KIND': MIDIA_AUDIO if limpo else MIDIA_VIDEO,
                        'WHY': 'os bytes já estavam no disco desta casa (%s)'
                               % ('áudio' if limpo else 'reuso de vídeo antigo')})
        return (ja, CAPTURA_JA_PRESERVADA, MEDIA_OK,
                'já preservado numa corrida anterior', degraus)

    ultimo = NOT_KNOWN
    # DEGRAU 1 · o endereço que alguém já pagou para descobrir
    if midia_url and midia_url != NOT_KNOWN:
        if kind == MIDIA_AUDIO and midia_url_kind != MIDIA_AUDIO:
            porque = ('endereço entregue sem declarar `MEDIA_KIND=AUDIO`. Pedido é '
                      'de fala; baixar sem saber o que vem lá dentro seria adquirir '
                      'vídeo em silêncio.')
            degraus.append({'PROVIDER': CAPTURA_FORNECIDA,
                            'RESULT': MEDIA_KIND_DIVERGE, 'WHY': porque})
            ultimo = porque
        else:
            n, motivo = baixar(midia_url, alvo)
            if not motivo and kind == MIDIA_AUDIO:
                limpo, mau = fl.so_audio(alvo)
                if not limpo:
                    motivo = 'MEDIA_KIND_MISMATCH: declarou áudio e %s' % mau
            degraus.append({'PROVIDER': CAPTURA_FORNECIDA,
                            'RESULT': MEDIA_OK if not motivo else MEDIA_VENCIDA,
                            'WHY': motivo or 'baixou %d bytes' % n})
            if not motivo:
                return alvo, CAPTURA_FORNECIDA, MEDIA_OK, None, degraus
            ultimo = motivo

    # DEGRAU 2 · o endereço DIRETO da publicação, grátis
    if ident.get('SOURCE_URL') not in (None, '', NOT_KNOWN) and ytdlp_disponivel():
        p, motivo = midia_por_ytdlp(ident['SOURCE_URL'], alvo, tentativas, kind=kind)
        degraus.append({'PROVIDER': CAPTURA_YTDLP,
                        'RESULT': MEDIA_OK if p else (
                            MEDIA_SEM_AUDIO_SO
                            if str(motivo).startswith('AUDIO_ONLY_UNAVAILABLE')
                            else MEDIA_KIND_DIVERGE
                            if str(motivo).startswith('MEDIA_KIND_MISMATCH')
                            else MEDIA_FALHOU),
                        'MEDIA_KIND': kind,
                        'WHY': motivo or 'baixou %d bytes' % os.path.getsize(p)})
        if p:
            return p, CAPTURA_YTDLP, MEDIA_OK, None, degraus
        ultimo = motivo

    # DEGRAU 3 · o embed público por HTTP puro, grátis
    if post_id != NOT_KNOWN and ident.get('PLATFORM') == 'INSTAGRAM':
        if kind == MIDIA_AUDIO:
            # O embed serve o MP4 inteiro. Usá-lo aqui seria a queda silenciosa
            # para vídeo que esta cadeia deixou de fazer.
            porque = ('o embed só serve o MP4 inteiro; pedido é de áudio e não '
                      'há queda para vídeo.')
            degraus.append({'PROVIDER': CAPTURA_EMBED,
                            'RESULT': MEDIA_SEM_AUDIO_SO, 'WHY': porque})
            ultimo = porque
        else:
            nova, porque = midia_do_embed(post_id)
            if nova:
                n, motivo = baixar(nova, alvo)
                degraus.append({'PROVIDER': CAPTURA_EMBED,
                                'RESULT': MEDIA_OK if not motivo else MEDIA_FALHOU,
                                'WHY': motivo or 'baixou %d bytes' % n})
                if not motivo:
                    return alvo, CAPTURA_EMBED, MEDIA_OK, None, degraus
                ultimo = motivo
            else:
                degraus.append({'PROVIDER': CAPTURA_EMBED,
                                'RESULT': MEDIA_SEM_ENDERECO, 'WHY': porque})
                ultimo = porque

    if not degraus:
        return None, CAPTURA_FORNECIDA, MEDIA_SEM_ENDERECO, (
            'nenhum endereço foi dado e não há rota grátis para esta '
            'plataforma. Isto é ausência de ENDEREÇO, não ausência de mídia.'), degraus
    estado = MEDIA_FALHOU
    if any(d.get('RESULT') == MEDIA_SEM_AUDIO_SO for d in degraus):
        estado = MEDIA_SEM_AUDIO_SO
    return None, degraus[-1]['PROVIDER'], estado, (
        'todos os degraus falharam. Ultimo: %s. Isto NÃO prova que o vídeo deixou '
        'de existir nem que não tem fala.' % ultimo), degraus


# ══════════════════════════════════════════════════════════════════ A CADEIA
def _ficha_raw(caminho, ident, *, run_id, capture_provider, media_kind=NOT_KNOWN):
    """A ficha do byte bruto. O `ARTIFACT_ID` sai do CONTEÚDO, e é por isso que
    correr duas vezes sobre o mesmo vídeo não cria dois artefatos.

    `SOURCE_ID` E `SOURCE_URL` SÃO DOIS CAMPOS PORQUE SÃO DUAS COISAS
    -------------------------------------------------------------------
        SOURCE_ID    a identidade canônica da fonte, atribuída por quem a tem
        SOURCE_URL   o endereço por onde se chegou a ela

    Até à C10 esta função punha o endereço nos dois. A C10 pôs ao lado uma
    etiqueta a dizer que era um substituto — e uma etiqueta não transforma um
    URL em identidade. O que ela fazia era pedir desculpa pela mentira sem a
    desfazer.

    E o dano não era teórico. `guarda/preservar_coleta._identifica()` recusa as
    confissões — `NAO SEI`, `UNKNOWN`, vazio — e aceita tudo o resto. Medido:

        _identifica('https://www.instagram.com/reel/ABC')  →  True
        _identifica('NAO SEI')                             →  False

    Ou seja: o endereço COMPRAVA um `IDENTITY_STATE` que ninguém tinha provado,
    e comprava-o precisamente no sítio onde a casa põe a trava.

        CAN ENTER NÃO SE COMPRA COM IDENTIDADE FALSA.

    Agora `SOURCE_ID` só chega aqui se vier provado em `ident`. Não vindo, o
    campo fica no sentinela do contrato — que `_identifica()` reconhece e
    recusa, e que a Collection traduz para ausência quando escreve.

        NÃO SABER QUAL É A FONTE != NÃO HAVER OBSERVAÇÃO.

    Tudo o resto continua a fechar: RUN, endereço, POST_ID, bytes, SHA256,
    caminho, fornecedor, espécie de mídia e o texto derivado com pai declarado.
    """
    return art.raw_do_disco(
        os.path.abspath(caminho), ROOT,
        # NUNCA `ident.get('SOURCE_URL')`. Ver a docstring: o endereço passa no
        # `_identifica()` e o sentinela não, e é essa a diferença inteira.
        SOURCE_ID=ident.get('SOURCE_ID', NAO_SEI),
        SOURCE_URL=ident.get('SOURCE_URL', NAO_SEI),
        PUBLISHER=ident.get('ACCOUNT_ID', NAO_SEI),
        # O RECORTE DE TRABALHO, E SÓ ISSO. `COUNTRY_SCOPE=IT` quer dizer «isto
        # está a ser trabalhado na frente Itália» — não «a fonte está em
        # Itália» e muito menos «o facto aconteceu em Itália».
        #
        #     COUNTRY_SCOPE É O QUE EU PEDI. NÃO É O QUE EU PROVEI.
        COUNTRY_SCOPE=ident.get('COUNTRY_SCOPE', NAO_SEI),
        # ── QUATRO EIXOS, E NENHUM ENCHE O OUTRO ────────────────────────────
        #   PLATFORM         o sistema onde a publicação existe     INSTAGRAM
        #   COUNTRY_SCOPE    a frente de trabalho desta casa        IT
        #   SOURCE_LOCATION  onde a fonte está, quando provado
        #   FACT_LOCATION    onde o facto aconteceu, quando provado
        #
        # Até aqui a linha de baixo dizia `SOURCE_LOCATION=ident.get('PLATFORM')`
        # — e produzia `SOURCE_LOCATION = INSTAGRAM`, que é semanticamente
        # impossível: o Instagram é um sistema, não um sítio no mundo. O
        # comentário que estava aqui já dizia a lei certa e a linha abaixo dele
        # fazia o contrário.
        #
        #     CONTRACT_TEXT != IMPLEMENTATION. O comentário não corrige o código.
        #
        # E esta casa já tinha decidido isto, em quatro sítios vizinhos:
        # `youtube_oficial.buscar` recusa-se a derivar país do `regionCode`;
        # `social_envelope` diz que língua italiana não prova Itália;
        # `golden_path_pdf` diz que `fact_location` não sai de `COUNTRY_SCOPE`;
        # e `social_scrap` escreve «COUNTRY_SCOPE=IT É O QUE EU PEDI, NÃO É O
        # QUE EU PROVEI». A cadeia de Reel era a única que não obedecia.
        #
        # Agora cada eixo só transporta a SUA evidência. Sem ela, o sentinela —
        # que é um dado, não um buraco.
        #
        #     UNKNOWN É MAIS BARATO QUE ERRADO.
        SOURCE_LOCATION=_ou(ident.get('SOURCE_LOCATION'), NAO_SEI),
        # E provar onde a fonte está NUNCA prova onde o facto aconteceu: uma
        # revista italiana noticia uma praga espanhola sem deixar de ser
        # italiana. Este campo só se enche com prova sua — e esta cadeia não
        # produz nenhuma, porque extrair geografia do conteúdo é outra missão,
        # com outro dono.
        FACT_LOCATION=_ou(ident.get('FACT_LOCATION'), NAO_SEI),
        PUBLISHED_AT=_ou(ident.get('PUBLISHED_AT'), NAO_SEI),
        COLLECTED_AT=art.agora(),
        RUN_ID=run_id,
        EXECUTOR_ID='ferramentas/reel_transcricao.py',
        EXECUTOR_VERSION=VERSAO,
        PIPELINE_VERSION=PIPELINE,
        STATE=MEDIA_OK,
        NOTES={'CAPTURE_PROVIDER': capture_provider,
               # QUE ESPECIE DE BYTES ESTE SHA RESUME. Sem este campo, um SHA de
               # audio e um SHA de video sao indistinguiveis na ficha, e quem ler
               # assume video porque a cadeia se chama «reel».
               'MEDIA_KIND': media_kind,
               # A PLATAFORMA CONTINUA RESPONDIDA — no campo dela, ao lado do
               # outro metadado de plataforma. Ela só saiu de `SOURCE_LOCATION`,
               # onde nunca devia ter estado; não foi apagada. Quem dedupla
               # objectos sociais por `PLATFORM + NATIVE_ID` é
               # `coleta/social_envelope.py`, e o conceito continua com ele.
               'PLATFORM': ident.get('PLATFORM', NAO_SEI),
               'POST_ID': ident.get('POST_ID', NAO_SEI),
               'RAW_OBSERVATION_ID': ident.get('RAW_OBSERVATION_ID', NOT_KNOWN),
               'RAW_OBSERVATION_ID_LEI': (
                   'RAW_OBSERVATION_ID e raw_asset.id. O SHA256 identifica os BYTES, '
                   'nao a observacao — dois RUNs que tragam o mesmo video tem o mesmo '
                   'SHA256 e sao duas observacoes.'),
               # `SOURCE_ID_KIND = URL_AS_PLACEHOLDER` viveu aqui entre a C10
               # e a C10.1, e foi removido em vez de renomeado: depois de o
               # endereco sair do campo, nao ha substituto nenhum a descrever, e
               # um campo que descreve um arranjo que deixou de existir e a
               # proxima pessoa a acreditar que ele ainda existe.
               #
               #     UMA ETIQUETA NAO TRANSFORMA UM URL EM IDENTIDADE.
               'SOURCE_ID_LEI': (
                   'SOURCE_ID e a identidade canonica da fonte e SOURCE_URL e o '
                   'endereco. Este campo nunca nasce do endereco: sem prova fica '
                   'no sentinela, que `_identifica()` recusa.')})


def _ou(v, alt):
    return v if v not in (None, '', NOT_KNOWN, 'NAO SEI') else alt


def transcrever_reel(ident, *, run_id, midia_url=None, midia_ficheiro=None,
                     idioma=None, modelo=None, transcript_da_fonte=None,
                     guardar=True, midia_url_kind=None):
    """A cadeia inteira, para UMA publicação. → o registo, sempre.

    Devolve registo mesmo quando falha — porque «não tentei», «tentei e o endereço
    venceu» e «ouvi e não havia texto» são três coisas diferentes, e um `None`
    apagaria a diferença.
    """
    ident = dict(ident)

    # ── DEGRAU 0 · OS METADADOS, DE GRAÇA, ANTES DE BAIXAR NADA ─────────────
    # Quem chega só com um endereço não tem legenda, nem conta, nem data. Buscar
    # isso primeiro custa zero e é o que permite comparar depois LEGENDA com FALA
    # — que é a pergunta inteira desta missão.
    meta_why = None
    if (ident.get('CAPTION_TEXT') in (None, '', NOT_KNOWN)
            and ident.get('SOURCE_URL') not in (None, '', NOT_KNOWN)
            and ytdlp_disponivel()):
        meta, meta_why = metadados_ytdlp(ident['SOURCE_URL'])
        if meta:
            for k, v in meta.items():
                if ident.get(k) in (None, '', NOT_KNOWN):
                    ident[k] = v

    idioma = idioma or idioma_provado(ident.get('COUNTRY_SCOPE'))

    base = {
        'REEL': {k: ident.get(k, NOT_KNOWN) for k in (
            'PLATFORM', 'POST_ID', 'SOURCE_URL', 'ACCOUNT_ID', 'ACCOUNT_NAME',
            'ACCOUNT_HANDLE_FROM_URL', 'ACCOUNT_URL', 'COMPANY', 'COUNTRY_SCOPE',
            'PUBLISHED_AT', 'MEDIA_TYPE', 'TITLE', 'VIEW_COUNT', 'LIKE_COUNT')},
        # A LEGENDA VIAJA MARCADA COMO LEGENDA. Nunca entra em TRANSCRIPT_TEXT.
        'CAPTION_TEXT': ident.get('CAPTION_TEXT', NOT_KNOWN),
        'CAPTION_IS_NOT_TRANSCRIPT': (
            'CAPTION_TEXT e o que o autor escreveu. TRANSCRIPT_TEXT e o que foi '
            'falado. Somar os dois apaga qual deles sustentou uma classificacao.'),
        'RUN_ID': run_id,
        'MISSION': MISSION,
        'RUNNER_NAME': RUNNER,
        'PIPELINE_VERSION': PIPELINE,
        'METADATA_PROVIDER': ident.get('METADATA_PROVIDER', NOT_KNOWN),
        'METADATA_WHY': meta_why or '',
        'MEDIA_DURATION_S': ident.get('MEDIA_DURATION_S', NOT_KNOWN),
    }

    # ── DEGRAU 1 · A FONTE JÁ TROUXE A FALA PRONTA? ─────────────────────────
    if transcript_da_fonte:
        return _fechar(base, ident, run_id=run_id, capture=CAPTURA_APIFY,
                       midia=None, raw=None,
                       fala={'TRANSCRIPT': transcript_da_fonte,
                             'TRANSCRIPT_STATE': fl.OK,
                             'TRANSCRIPT_CHARS': len(transcript_da_fonte),
                             'SEGMENTS': [],
                             'LANGUAGE': idioma or NOT_KNOWN,
                             'LANGUAGE_SOURCE': ('DECLARED' if idioma
                                                 else NOT_KNOWN),
                             'ASR_ENGINE': NAO_SE_APLICA,
                             'ASR_MODEL': NAO_SE_APLICA,
                             'TRANSCRIBER_ID': NAO_SE_APLICA},
                       provider=FONTE, guardar=guardar,
                       nota=('a fala veio PRONTA da plataforma. Esta maquina nao '
                             'ouviu o audio — e por isso os campos de motor sao '
                             'NAO_SE_APLICA em vez de fingirem uma medicao.'))

    # ── DEGRAU 2 · OS BYTES ─────────────────────────────────────────────────
    # A NECESSIDADE DECLARADA DESTA CADEIA E FALA, E SO FALA. Por isso ela pede
    # `MIDIA_AUDIO` — nao por economia, mas porque pedir a imagem de um video que
    # ninguem vai olhar e adquirir o que nao se precisa.
    #
    #     PIXELS_NEEDED = NO  ->  VIDEO_DOWNLOAD = PROIBIDO.
    caminho, capture, estado, motivo, degraus = obter_midia(
        ident, midia_url=midia_url or ident.get('MEDIA_URL'),
        midia_ficheiro=midia_ficheiro,
        kind=MIDIA_AUDIO, midia_url_kind=midia_url_kind)
    base['CAPTURE_ATTEMPTS'] = degraus
    base['MEDIA_KIND_REQUESTED'] = MIDIA_AUDIO
    if not caminho:
        base.update({
            'CAPTURE_PROVIDER': capture,
            'MEDIA_STATE': estado,
            'MEDIA_WHY': motivo,
            'TRANSCRIPT_PROVIDER': NAO_PEDIDO,
            'TRANSCRIPT_TEXT': None,
            'TRANSCRIPT_STATE': NAO_PEDIDO,
            'MEDIA_KIND_USED': NOT_KNOWN,
            'AUDIO_ONLY_ACQUISITION': 'NOT_ATTEMPTED',
            'NAO_SIGNIFICA': ('que o video nao tem fala. Significa que ninguem '
                              'chegou a ouvi-lo.'),
            'RAW': None, 'DERIVED': None,
        })
        return base

    # ── DEGRAU 2.5 · QUE ESPECIE DE BYTES CHEGARAM, MEDIDA NOS BYTES ────────
    # Nao no seletor, nao na extensao, nao no nome do fornecedor. Aqui abre-se o
    # ficheiro. E o resultado e um FACTO sobre a aquisicao, que sobe ate ao
    # transcript — porque quem ler `MEDIA_SHA256` daqui a um ano tem o direito
    # de saber de que e que aquele SHA e o resumo.
    #
    #     RAW != VIDEO. RAW e a observacao bruta ADQUIRIDA NESTA ROTA.
    e_so_audio, porque_kind = fl.so_audio(caminho)
    kind_usado = MIDIA_AUDIO if e_so_audio else MIDIA_VIDEO
    reusado = capture == CAPTURA_JA_PRESERVADA
    base['MEDIA_KIND_USED'] = kind_usado
    base['MEDIA_KIND_WHY'] = porque_kind or 'bytes conferidos: som sem imagem'
    base['AUDIO_ONLY_ACQUISITION'] = (
        'PROVEN' if (e_so_audio and not reusado) else
        'REUSED_NOT_ACQUIRED' if reusado else 'NO')
    if reusado:
        # REUSAR MP4 ANTIGO E COMPATIBILIDADE HISTORICA, NAO ROTA NOVA.
        base['AUDIO_ONLY_WHY'] = (
            'os bytes vieram do disco desta casa; reuso nao prova aquisicao. '
            'REUSED_VIDEO + AUDIO_DERIVATION != AUDIO_ONLY_ACQUISITION.')

    # ── DEGRAU 3 · O RAW GANHA FICHA ────────────────────────────────────────
    raw = _ficha_raw(caminho, ident, run_id=run_id, capture_provider=capture,
                     media_kind=kind_usado)

    # ── DEGRAU 4 · O ÁUDIO (meio de trabalho, não artefato) ─────────────────
    wav = os.path.join(MIDIA, os.path.splitext(os.path.basename(caminho))[0] + '.wav')
    wav, porque = fl.extrair_audio(caminho, wav)
    if not wav:
        base.update({
            'CAPTURE_PROVIDER': capture, 'MEDIA_STATE': MEDIA_OK,
            'TRANSCRIPT_PROVIDER': ASR_LOCAL,
            'TRANSCRIPT_TEXT': None,
            'TRANSCRIPT_STATE': fl.ASR_FALHOU,
            'ERROR': porque,
            'NAO_SIGNIFICA': 'que o video nao tem fala. O audio e que nao saiu.',
            'RAW': raw.para_json(), 'DERIVED': None,
        })
        return base

    # ── DEGRAU 5 · A FALA ───────────────────────────────────────────────────
    dur = fl.duracao(wav)
    fala = fl.transcrever(wav, idioma=idioma, modelo_nome=modelo or MODELO_PADRAO,
                          duracao_s=dur if isinstance(dur, (int, float)) else None)
    return _fechar(base, ident, run_id=run_id, capture=capture, midia=caminho,
                   raw=raw, fala=fala, provider=ASR_LOCAL, guardar=guardar)


def _fechar(base, ident, *, run_id, capture, midia, raw, fala, provider,
            guardar=True, nota=''):
    """Escreve o texto no disco e dá-lhe PAI. Um .txt sem pai não sai daqui."""
    post_id = re.sub(r'[^A-Za-z0-9_.-]', '_', str(ident.get('POST_ID') or 'SEM_ID'))
    derived_json = None

    if fala.get('TRANSCRIPT') and raw is not None and guardar:
        os.makedirs(SAIDA, exist_ok=True)
        txt = os.path.join(SAIDA, '%s.txt' % post_id)
        with open(txt, 'w', encoding='utf-8') as f:
            f.write(fala['TRANSCRIPT'])
        der = art.derivado_de(
            raw, os.path.abspath(txt), ROOT,
            derivacao=art.SPEECH_TRANSCRIPTION,
            executor='ferramentas/fala_local.py',
            executor_versao=fl.VERSAO,
            pipeline_versao=PIPELINE,
            run_id=run_id,
            estado=fala.get('TRANSCRIPT_STATE', NAO_SEI),
            erro=fala.get('ERROR', ''),
            notas={
                'TRANSCRIPT_PROVIDER': provider,
                'ASR_ENGINE': fala.get('ASR_ENGINE', NAO_SE_APLICA),
                'ASR_ENGINE_VERSION': fala.get('ASR_ENGINE_VERSION', NAO_SE_APLICA),
                'ASR_MODEL': fala.get('ASR_MODEL', NAO_SE_APLICA),
                'LANGUAGE': fala.get('LANGUAGE', NAO_SEI),
                'LANGUAGE_SOURCE': fala.get('LANGUAGE_SOURCE', NAO_SEI),
                'LANGUAGE_CONFIDENCE': fala.get('LANGUAGE_CONFIDENCE', NAO_SEI),
                'HAS_TIMESTAMPS': 'YES' if fala.get('SEGMENTS') else 'NO',
                'SEGMENTS': len(fala.get('SEGMENTS') or []),
                'CAPTURE_PROVIDER': capture,
                'MEDIA_SHA256': raw.SHA256,
                # O SHA nao diz de que e. Este campo diz, e por isso viaja
                # colado a ele: `MEDIA_SHA256` de uma rota audio-only e o
                # resumo do AUDIO, e nunca de um video que nao foi adquirido.
                'MEDIA_KIND': base.get('MEDIA_KIND_USED', NOT_KNOWN),
                'AUDIO_ONLY_ACQUISITION': base.get('AUDIO_ONLY_ACQUISITION',
                                                   NOT_KNOWN),
                'MEDIA_STORAGE': raw.STORAGE_LOCATION,
                'RAW_OBSERVATION_ID': ident.get('RAW_OBSERVATION_ID', NOT_KNOWN),
                # A LEI, dentro do artefato e não só no cabeçalho do ficheiro.
                'NAO_E_CAPTION': ('este texto e FALA reconhecida no audio. A legenda '
                                  'escrita pelo autor viaja noutro campo.'),
            })
        quebras = art.conferir(der)
        if quebras:
            # A lei tem dentes: um derivado que quebra o contrato não sai fingindo
            # que está bem. Ele sai marcado, com as quebras à vista.
            der.STATE = 'CONTRATO_QUEBRADO'
            der.ERROR = ' | '.join(quebras)
        derived_json = der.para_json()

    # ── UM TEXTO SEM PAI PRESERVADO DIZ QUE NAO TEM PAI ─────────────────────
    # A rota paga pode devolver a fala PRONTA e nenhum byte de video. Nesse caso
    # nao ha ficheiro para preservar, logo nao ha artefato pai — e isso e uma
    # diferenca real de forca de prova: o texto existe, mas ninguem nesta casa
    # consegue voltar ao audio e conferir a citacao contra o segundo exato.
    #
    #     TEXTO SEM PAI NAO E TEXTO ERRADO. E TEXTO QUE NAO SE CONFERE.
    #
    # Deixar isso implicito seria o pior dos mundos: dois textos lado a lado no
    # mesmo livro, um conferivel e outro nao, sem nada a distingui-los.
    sem_pai = fala.get('TRANSCRIPT') and raw is None
    base.update({
        'CAPTURE_PROVIDER': capture,
        'TRANSCRIPT_WITHOUT_PRESERVED_PARENT': 'YES' if sem_pai else 'NO',
        'TRANSCRIPT_WITHOUT_PRESERVED_PARENT_WHY': (
            'a fala veio pronta da fonte e nenhum byte de video foi preservado. '
            'Nao ha artefato pai, logo nenhuma citacao deste texto se confere '
            'contra o audio.') if sem_pai else '',
        'MEDIA_STATE': MEDIA_OK if raw is not None else NAO_SE_APLICA,
        'TRANSCRIPT_PROVIDER': provider,
        'TRANSCRIPT_TEXT': fala.get('TRANSCRIPT'),
        'TRANSCRIPT_STATE': fala.get('TRANSCRIPT_STATE', NAO_SEI),
        'TRANSCRIPT_CHARS': fala.get('TRANSCRIPT_CHARS', 0),
        'SEGMENTS': fala.get('SEGMENTS', []),
        'LANGUAGE': fala.get('LANGUAGE', NOT_KNOWN),
        'LANGUAGE_SOURCE': fala.get('LANGUAGE_SOURCE', NOT_KNOWN),
        'LANGUAGE_CONFIDENCE': fala.get('LANGUAGE_CONFIDENCE', NOT_KNOWN),
        'LANGUAGE_STATE': fala.get('LANGUAGE_STATE', NOT_KNOWN),
        'AUDIO_SECONDS': fala.get('AUDIO_SECONDS', NOT_KNOWN),
        'MACHINE_SECONDS': fala.get('MACHINE_SECONDS', NOT_KNOWN),
        'REALTIME_FACTOR': fala.get('REALTIME_FACTOR', NOT_KNOWN),
        'VOICED_SEGMENTS': fala.get('VOICED_SEGMENTS', NOT_KNOWN),
        'NO_SPEECH_PROB_MEAN': fala.get('NO_SPEECH_PROB_MEAN', NOT_KNOWN),
        'COST_USD': 0 if provider == ASR_LOCAL else NOT_KNOWN,
        'RAW': raw.para_json() if raw is not None else None,
        'DERIVED': derived_json,
        'PROVENANCE': proveniencia(ident, raw, derived_json, fala, capture, provider),
    })
    for k in ('DISCARDED_OUTPUT', 'WHY', 'TIMEOUT_LIMIT_S'):
        if fala.get(k) is not None:
            base[k] = fala[k]
    if fala.get('ERROR'):
        base['ERROR'] = fala['ERROR']
    if fala.get('NAO_SIGNIFICA'):
        base['NAO_SIGNIFICA'] = fala['NAO_SIGNIFICA']
    if nota:
        base['NOTA'] = nota
    return base


def proveniencia(ident, raw, derived, fala, capture, provider):
    """As perguntas que um texto derivado tem de saber responder — e as respostas.

    Se alguma delas não tiver resposta, ela sai `NOT_KNOWN` à vista. Um quadro de
    proveniência com buracos visíveis é útil; um quadro cheio de valores inventados
    é pior do que nenhum, porque parece confiável.
    """
    return {
        'QUAL_REEL': ident.get('SOURCE_URL', NOT_KNOWN),
        'QUAL_POST_ID': ident.get('POST_ID', NOT_KNOWN),
        'QUAL_RAW_OBSERVATION_ID': ident.get('RAW_OBSERVATION_ID', NOT_KNOWN),
        'RAW_OBSERVATION_ID_LEI': (
            'e raw_asset.id, e so a fundacao de Collection o cria. O SHA256 abaixo '
            'identifica BYTES, nunca observacao.'),
        'QUAL_MIDIA': raw.STORAGE_LOCATION if raw is not None else NOT_KNOWN,
        'QUAL_SHA256_DA_MIDIA': raw.SHA256 if raw is not None else NOT_KNOWN,
        'QUAL_ARTEFATO_PAI': raw.ARTIFACT_ID if raw is not None else NOT_KNOWN,
        'QUAL_ARTEFATO_FILHO': (derived or {}).get('ARTIFACT_ID', NOT_KNOWN),
        'TEM_PAI_PRESERVADO': 'YES' if raw is not None else (
            'NO — a fala veio pronta e nenhum byte ficou preservado nesta casa'),
        'QUEM_TRANSCREVEU': fala.get('TRANSCRIBER_ID', NAO_SE_APLICA),
        'QUAL_MOTOR': fala.get('ASR_ENGINE', NAO_SE_APLICA),
        'QUAL_MODELO': fala.get('ASR_MODEL', NAO_SE_APLICA),
        'QUAL_VERSAO': fala.get('ASR_ENGINE_VERSION', NAO_SE_APLICA),
        'QUANDO_FOI_TRANSCRITO': (derived or {}).get('DERIVED_AT', NOT_KNOWN),
        'QUAL_IDIOMA': fala.get('LANGUAGE', NOT_KNOWN),
        'IDIOMA_DECLARADO_OU_DETECTADO': fala.get('LANGUAGE_SOURCE', NOT_KNOWN),
        'FALA_DA_FONTE_OU_NOSSA': provider,
        'COMO_A_MIDIA_FOI_OBTIDA': capture,
        'HOUVE_TIMESTAMPS': 'YES' if fala.get('SEGMENTS') else 'NO',
        'HOUVE_ERRO': fala.get('ERROR', 'NO'),
        'FACT_LOCATION': ('NOT_KNOWN — transcricao nao e julgamento. Ouvir um nome '
                          'nao prova onde o fato aconteceu.'),
        'FACT_TIME': ('NOT_KNOWN — PUBLISHED_AT e quando se publicou, e publicar nao '
                      'e acontecer.'),
    }


# ═══════════════════════════════════════════════════════════════ O ARMAZÉM
def gravar_lote(registos, nome='TRANSCRICOES-REEL.json'):
    """O livro do lote. Os itens são indexados por ARTEFATO, e é isso que faz o
    retry não duplicar: os mesmos bytes têm o mesmo nome próprio."""
    os.makedirs(SAIDA, exist_ok=True)
    caminho = os.path.join(SAIDA, nome)
    antigos = {}
    if os.path.exists(caminho):
        with open(caminho, encoding='utf-8') as f:
            for i in json.load(f).get('ITEMS', []):
                antigos[_chave(i)] = i
    for r in registos:
        k = _chave(r)
        # REOBSERVAR NAO DUPLICA CONTEUDO, MAS TAMBEM NAO APAGA A OBSERVACAO.
        # A linha e uma so — o conteudo e o mesmo — e a lista de corridas que
        # passaram por ela cresce. Guardar so a ultima faria parecer que este
        # video foi visto uma vez, quando foi visto tres.
        vistos = list((antigos.get(k) or {}).get('RUN_IDS_SEEN') or [])
        if (antigos.get(k) or {}).get('RUN_ID') and not vistos:
            vistos = [antigos[k]['RUN_ID']]
        if r.get('RUN_ID') and r['RUN_ID'] not in vistos:
            vistos.append(r['RUN_ID'])
        r = dict(r, RUN_IDS_SEEN=vistos, TIMES_OBSERVED=len(vistos))
        antigos[k] = r
    itens = sorted(antigos.values(), key=lambda i: str(i.get('REEL', {}).get('POST_ID')))
    ok = sum(1 for i in itens if i.get('TRANSCRIPT_STATE') == fl.OK)
    corpo = {
        'SOURCE_ID': 'REEL-TRANSCRICOES/TRANSCRICOES-REEL',
        'DATASET_OWNER': 'COMPETITOR_PUBLIC_COMMUNICATION_EAME',
        'source': 'fala reconhecida sobre o audio de video publico, com pai declarado',
        'EVIDENCE_CLASS': 'COMPETITOR_PUBLIC_COMMUNICATION_OBSERVED',
        'SOURCE_LOCATION': 'a plataforma onde o video esta publicado',
        'FACT_LOCATION': 'NOT_KNOWN — o lugar do fato sai do conteudo, nunca da conta',
        'PIPELINE_VERSION': PIPELINE,
        'CAPTURED_AT': art.agora(),
        'MISSION': MISSION, 'RUNNER_NAME': RUNNER,
        'ITEM_COUNT': len(itens),
        'TRANSCRIBED_OK': ok,
        'LEI': ('CAPTION_TEXT e legenda do autor; TRANSCRIPT_TEXT e fala reconhecida. '
                'Um derivado sem PARENT_ARTIFACT_ID nao entra aqui.'),
        'ITEMS': itens,
    }
    with open(caminho, 'w', encoding='utf-8') as f:
        json.dump(corpo, f, ensure_ascii=False, indent=1)
    return caminho, corpo


def _chave(registo):
    """A chave do livro, e a escolha dela custou um defeito real.

    A primeira versão indexava pelo DERIVADO. Parece certo e não é: quando a
    mesma publicação corre outra vez e o resultado MUDA de estado — foi o que
    aconteceu ao apertar a trava de alucinação, e `...` virou REQUESTED_EMPTY —
    a corrida nova não tem derivado nenhum, cai noutra chave, e o livro fica com
    DUAS linhas para o mesmo vídeo: a antiga a afirmar um texto que já se sabe
    que era lixo, e a nova a dizer a verdade.

        INDEXAR PELO RESULTADO FAZ O RESULTADO ANTIGO SOBREVIVER À CORREÇÃO.

    A chave é o CONTEÚDO OBSERVADO — o RAW, que sai dos bytes e não muda quando
    o reconhecedor melhora. Sem RAW (nem se chegou a baixar), cai para o
    `POST_ID`: uma falha também tem de ter lugar no livro.
    """
    r = registo.get('RAW') or {}
    if r.get('ARTIFACT_ID'):
        return 'RAW:%s' % r['ARTIFACT_ID']
    return 'POST:%s' % (registo.get('REEL', {}).get('POST_ID') or 'SEM_ID')


# ═══════════════════════════════════════════════════════════════════ AS FASES
def fase_censo():
    """GRÁTIS. O que esta máquina consegue fazer hoje, medido — não prometido."""
    ha, porque = fl.disponivel()
    import shutil
    ff = shutil.which('ffmpeg')
    print('RECONHECEDOR   = %s %s' % (fl.MOTOR, fl._versao_do_motor()))
    print('DISPONIVEL     = %s%s' % ('YES' if ha else 'NO', '' if ha else ' — ' + porque))
    print('FFMPEG         = %s' % (ff or 'AUSENTE — sem ele nao ha audio'))
    print('NUCLEOS        = %d' % fl.nucleos())
    print('MODELO_PADRAO  = %s  (medido: `small` diz «MICE» onde se disse «mais»)'
          % MODELO_PADRAO)
    print('MIDIA (RAW)    = data/raw/REEL-MIDIA        (fora do Git, por decisao D-003)')
    print('TEXTO (DERIV.) = data/samples/REEL-TRANSCRICOES')
    print('CAPTURAS       = %s' % ', '.join(CAPTURAS))
    print()
    print('O QUE ISTO NAO PROVA: que a plataforma responde a esta maquina. Isso so')
    print('se mede tentando, e o estado sai em MEDIA_STATE, item a item.')
    return 0 if (ha and ff) else 1


def fase_um(url, midia=None, idioma=None, modelo=None, run_id=None):
    ident = identidade_do_url(url)
    if ident['POST_ID'] == NOT_KNOWN:
        print('nao reconheco publicacao neste endereco: %s' % url)
        print('NAO invento POST_ID a partir de um endereco que nao o tem.')
        return 2
    run_id = run_id or _run_id_local()
    if midia and not os.path.exists(midia):
        r = transcrever_reel(ident, run_id=run_id, midia_url=midia,
                             idioma=idioma, modelo=modelo)
    else:
        r = transcrever_reel(ident, run_id=run_id, midia_ficheiro=midia,
                             idioma=idioma, modelo=modelo)
    caminho, _ = gravar_lote([r])
    _imprimir(r)
    print('gravado: %s' % os.path.relpath(caminho, ROOT))
    return 0 if r.get('TRANSCRIPT_STATE') == fl.OK else 1


def fase_posts(plataforma, teto=None, modelo=None, run_id=None):
    """Sobre o que a coleta JÁ pagou. Nenhuma execucao paga nova acontece aqui."""
    caminho = os.path.join(ROOT, 'data', 'samples', 'COMPETITOR-PUBLIC-COMM',
                           'POSTS-%s.json' % plataforma)
    if not os.path.exists(caminho):
        print('nao ha coleta desta plataforma ainda: %s' % os.path.relpath(caminho, ROOT))
        print('Isto NAO e "a empresa nao publica la" — e "a coleta ainda nao rodou".')
        return 2
    with open(caminho, encoding='utf-8') as f:
        itens = json.load(f).get('ITEMS', [])
    # QUEM ENTRA NA FILA, e o motivo de cada exclusao fica dito no artefato.
    # Excluir em silencio e o defeito classico: quem le depois nao sabe se o
    # objeto nao tinha video ou se ninguem tentou.
    def e_video(i):
        return (str(i.get('IS_VIDEO', '')).upper() == 'YES'
                or str(i.get('MEDIA_TYPE', '')).upper() in ('VIDEO', 'REEL', 'CLIPS', 'IGTV')
                or i.get('MEDIA_URL_TEMPORARY') not in (None, '', NOT_KNOWN)
                or i.get('MEDIA_URL') not in (None, '', NOT_KNOWN))
    alvos = [i for i in itens if e_video(i)]
    fora_da_fila = [i for i in itens if not e_video(i)]
    if teto:
        alvos = alvos[:int(teto)]
    run_id = run_id or _run_id_local()
    registos = []
    for n, item in enumerate(alvos, 1):
        r = transcrever_reel(de_item_de_comunicacao(item), run_id=run_id, modelo=modelo)
        registos.append(r)
        print('  %3d/%d %-14s %-22s %s'
              % (n, len(alvos), r['REEL']['POST_ID'], r.get('TRANSCRIPT_STATE'),
                 (r.get('TRANSCRIPT_TEXT') or '')[:40]))
    caminho, corpo = gravar_lote(registos)
    print('objetos com video : %d de %d itens coletados' % (len(alvos), len(itens)))
    print('fora da fila      : %d (sem marca de video e sem endereco de midia — '
          'isto e ausencia de ENDERECO, nao ausencia de fala)' % len(fora_da_fila))
    print('transcritos OK    : %d' % corpo['TRANSCRIBED_OK'])
    print('gravado           : %s' % os.path.relpath(caminho, ROOT))
    return 0


def _run_id_local():
    """Uma corrida local, marcada como local. Quando o orquestrador manda, ele
    passa a SUA — e esta função nem é chamada."""
    import datetime
    return 'REEL-LOCAL-%s' % datetime.datetime.now(
        datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')


def _imprimir(r):
    print('REEL              %s' % r['REEL']['SOURCE_URL'])
    print('CAPTURE_PROVIDER  %s' % r.get('CAPTURE_PROVIDER'))
    print('MEDIA_STATE       %s %s' % (r.get('MEDIA_STATE'), r.get('MEDIA_WHY') or ''))
    print('TRANSCRIPT_STATE  %s' % r.get('TRANSCRIPT_STATE'))
    print('LANGUAGE          %s (%s, conf=%s)'
          % (r.get('LANGUAGE'), r.get('LANGUAGE_SOURCE'), r.get('LANGUAGE_CONFIDENCE')))
    if r.get('RAW'):
        print('RAW               %s  sha=%s' % (r['RAW']['ARTIFACT_ID'],
                                                r['RAW']['SHA256'][:16]))
    if r.get('DERIVED'):
        print('DERIVED           %s  pai=%s' % (r['DERIVED']['ARTIFACT_ID'],
                                                r['DERIVED']['PARENT_ARTIFACT_ID']))
    if r.get('TRANSCRIPT_TEXT'):
        print('TEXTO             %s…' % r['TRANSCRIPT_TEXT'][:120])
    if r.get('NAO_SIGNIFICA'):
        print('NAO SIGNIFICA     %s' % r['NAO_SIGNIFICA'])


def main(argv):
    cmd = argv[1] if len(argv) > 1 else 'censo'
    op = {}
    for a in argv[2:]:
        if a.startswith('--') and '=' in a:
            k, v = a[2:].split('=', 1)
            op[k.replace('-', '_')] = v
    if cmd == 'censo':
        return fase_censo()
    if cmd == 'um':
        if not op.get('url'):
            print('uso: reel_transcricao.py um --url=<endereco do reel> [--midia=...]')
            return 2
        return fase_um(op['url'], midia=op.get('midia'), idioma=op.get('idioma'),
                       modelo=op.get('modelo'), run_id=op.get('run_id'))
    if cmd == 'posts':
        if len(argv) < 3:
            print('uso: reel_transcricao.py posts INSTAGRAM [--teto=N]')
            return 2
        return fase_posts(argv[2].upper(), teto=op.get('teto'),
                          modelo=op.get('modelo'), run_id=op.get('run_id'))
    print(__doc__.strip().splitlines()[0])
    print('uso: reel_transcricao.py {censo|um --url=...|posts PLATAFORMA}')
    return 2


if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
