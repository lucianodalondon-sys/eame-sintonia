#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CAPACIDADES DO SINTONIA SCRAP — o que ele sabe fazer, e com que prova.

    import scrap_capacidades as cap
    cap.estado('instagram.reel.capture')      # 'PROVEN'
    cap.onde('youtube.media')                 # ('LOCAL', 'DATACENTER_BLOCKED')
    cap.da_plataforma('LINKEDIN')             # as sete, com estado

POR QUE ISTO NAO E O `social_matriz.py`
----------------------------------------
Sao dois conceitos, e cada um tem um dono so.

    social_matriz.py       POLITICA DE ROTA     que porta e permitida
    scrap_capacidades.py   DECLARACAO           o que sabemos fazer, e onde

A matriz responde «esta rota pode ser usada?». Esta lei responde «esta
capacidade existe, foi provada, e em que ambiente ela corre?». Juntar as duas
parece economia e nao e: no dia em que uma rota nova for permitida e ainda nao
tiver sido provada, a resposta certa e PERMITIDA e NOT_EXECUTED ao mesmo tempo.
Um campo so nao consegue dizer isso.

COL-LAW-014 pede capacidade DECLARADA. Este ficheiro e essa declaracao.

O VOCABULARIO E FECHADO, E ISSO E DE PROPOSITO
-----------------------------------------------
    PROVEN         correu, com comando registado e saida guardada
    PARTIAL        funciona com teto medido
    BLOCKED        medido e recusado pela plataforma
    UNKNOWN        nao medido
    NOT_EXECUTED   nunca tentado

    NAO HA ESTADO PARA «ACHO QUE DA». Capacidade que ninguem mediu e UNKNOWN,
    e UNKNOWN nao vira sucesso porque existe um adaptador para ela.

O QUE NAO ESTA DECLARADO AQUI TAMBEM DIZ ALGUMA COISA
------------------------------------------------------
`instagram.native_caption` nao existe nesta lista. Nao e esquecimento: o
Instagram NAO serve legenda nativa. A legenda que ele serve e o texto do autor,
que e CAPTION, nao TRANSCRIPT. E por isso que o Instagram e a unica das cinco
plataformas onde o reconhecimento de fala e indispensavel.

O AMBIENTE E UM EIXO PROPRIO
-----------------------------
    PROVIDER              com que ferramenta
    EXECUTION_TARGET      onde corre

Nao se deduz um do outro. O `yt-dlp` traz metadados do YouTube ONLINE e leva
403 nos bytes de midia do mesmo YouTube, do mesmo IP, no mesmo minuto. Mesmo
fornecedor, capacidades diferentes, resultados diferentes.

    A REGRA DO AMBIENTE E UMA SO:
    USAR O MAIS BARATO E MAIS SIMPLES QUE CUMPRA A CAPACIDADE.

E `WHY_LOCAL` e obrigatorio quando o alvo e LOCAL ou HYBRID — porque «sempre
fizemos assim» nao e um motivo, e sem o campo ninguem percebe que nao era.

A PROVA DE CADA LINHA VIVE NOS DOCUMENTOS DO BENCHMARK
-------------------------------------------------------
Nenhum estado aqui foi escrito de memoria. Cada um cita o documento que o
mediu, e o validador recusa linha sem prova citada.
"""

# ── OS CINCO ESTADOS ──────────────────────────────────────────────────────
PROVEN = 'PROVEN'
PARTIAL = 'PARTIAL'
BLOCKED = 'BLOCKED'
UNKNOWN = 'UNKNOWN'
NOT_EXECUTED = 'NOT_EXECUTED'

ESTADOS = (PROVEN, PARTIAL, BLOCKED, UNKNOWN, NOT_EXECUTED)

#: Estados que NAO autorizam ninguem a esperar resultado.
SEM_PROMESSA = (BLOCKED, UNKNOWN, NOT_EXECUTED)

# ── O AMBIENTE DE EXECUCAO ────────────────────────────────────────────────
ONLINE = 'ONLINE'
LOCAL = 'LOCAL'
EITHER = 'EITHER'
HYBRID = 'HYBRID'
AMBIENTE_DESCONHECIDO = 'UNKNOWN'

AMBIENTES = (ONLINE, LOCAL, EITHER, HYBRID, AMBIENTE_DESCONHECIDO)

#: Alvos que EXIGEM `WHY_LOCAL` preenchido.
EXIGEM_PORQUE = (LOCAL, HYBRID)

# ── POR QUE LOCAL ─────────────────────────────────────────────────────────
DATACENTER_BLOCKED = 'DATACENTER_BLOCKED'
AUTHORIZED_LOCAL_SESSION = 'AUTHORIZED_LOCAL_SESSION'
HEAVY_MEDIA_PROCESSING = 'HEAVY_MEDIA_PROCESSING'
GPU_REQUIRED = 'GPU_REQUIRED'
BROWSER_REAL_REQUIRED = 'BROWSER_REAL_REQUIRED'
LOWER_COST = 'LOWER_COST'

PORQUE_LOCAL = (DATACENTER_BLOCKED, AUTHORIZED_LOCAL_SESSION, HEAVY_MEDIA_PROCESSING,
                GPU_REQUIRED, BROWSER_REAL_REQUIRED, LOWER_COST)

#: O hardware do runner local NUNCA foi medido nesta linhagem. Enquanto estiver
#: assim, `GPU_REQUIRED` e uma promessa sobre maquina que ninguem viu, e o
#: validador recusa-a. Medir primeiro; declarar depois.
LOCAL_HARDWARE_STATUS = 'NOT_MEASURED'
PROIBIDOS_ENQUANTO_HARDWARE_NAO_MEDIDO = (GPU_REQUIRED,)


class CapacidadeInvalida(ValueError):
    """A declaracao nao respeita o vocabulario fechado."""


# ══════════════════════════════════════════════════════════════════════════
# A DECLARACAO
# ══════════════════════════════════════════════════════════════════════════
#   nome pontuado -> (PLATAFORMA, ESTADO, EXECUTION_TARGET, WHY_LOCAL, PROVA, MATRIZ)
#
# PROVA  e o documento que mediu. Linha sem prova nao passa no validador.
# MATRIZ e o nome grosso da mesma capacidade em `social_matriz.py`, ou None.
#        Existe porque a matriz ja tinha vocabulario proprio — `INCREMENTAL`,
#        `SEARCH_KEYWORD` — e renomear o que ja esta gravado em artefatos seria
#        reescrever historia. O campo traduz em vez de renomear.
_B = 'docs/sintonia-scrap/BENCHMARK-V1-FINAL.md'
_AP = 'docs/sintonia-scrap/AP-DISCOVERY-VS-CAPTURA-V1.md'
_ER = 'docs/sintonia-scrap/ESTADO-REAL-V1.md'
_CE = 'docs/sintonia-scrap/CENSO-DOS-ACTORS-E-CUSTO-V1.md'
_RE = 'docs/operacao/O-REEL-DEIXA-DE-SER-MUDO.md'
_MZ = 'leis/social_matriz.py'
_C3 = 'docs/sintonia-scrap/C3-YOUTUBE-RUNTIME-CUTOVER.md'

DECLARADAS = {
    # ── INSTAGRAM ─────────────────────────────────────────────────────────
    'instagram.reel.capture': ('INSTAGRAM', PROVEN, EITHER, None, _RE, None),
    'instagram.reel.audio': ('INSTAGRAM', PROVEN, EITHER, None, _RE, None),
    # A UNICA DAS TRES QUE A MATRIZ CONHECE. O acto que ela executa — ir
    # buscar a media e reconhecer a fala aqui — e o que `social_matriz`
    # chama FETCH_TRANSCRIPT, e ali ele esta PERMITIDA=SIM, PROVED. Sem
    # esta traducao o roteador nunca encontrava a cadeia, e a cadeia
    # entrava pelo `executa` — que e a porta de quem NAO tem portao.
    'instagram.reel.transcribe': ('INSTAGRAM', PROVEN, EITHER, None, _RE, 'FETCH_TRANSCRIPT'),
    'instagram.profile.discovery': ('INSTAGRAM', PARTIAL, LOCAL, DATACENTER_BLOCKED, _AP, 'INCREMENTAL'),
    'instagram.post.comments': ('INSTAGRAM', BLOCKED, AMBIENTE_DESCONHECIDO, None, _AP, 'FETCH_COMMENTS'),
    'instagram.story.capture': ('INSTAGRAM', UNKNOWN, LOCAL, AUTHORIZED_LOCAL_SESSION, _ER, None),
    'instagram.story.transcribe': ('INSTAGRAM', NOT_EXECUTED, LOCAL, AUTHORIZED_LOCAL_SESSION, _B, None),

    # ── LINKEDIN ──────────────────────────────────────────────────────────
    # A janela recente esta PROVEN e e RASA. Sao dois factos, e o segundo nao
    # revoga o primeiro: `LINKEDIN_DISCOVERY = BLOCKED` foi erro ja corrigido.
    'linkedin.recent.discovery': ('LINKEDIN', PROVEN, ONLINE, None, _ER, 'DISCOVER_ACCOUNT'),
    'linkedin.history.discovery': ('LINKEDIN', UNKNOWN, AMBIENTE_DESCONHECIDO, None, _B, None),
    'linkedin.direct_post': ('LINKEDIN', PROVEN, ONLINE, None, _ER, 'FETCH_POST'),
    'linkedin.native_video': ('LINKEDIN', PROVEN, ONLINE, None, _ER, None),
    # SRT automatica, nao WebVTT humana. E ASR de outra casa: mais barata, nao melhor.
    'linkedin.native_caption': ('LINKEDIN', PROVEN, ONLINE, None, _B, None),
    'linkedin.comments': ('LINKEDIN', UNKNOWN, AMBIENTE_DESCONHECIDO, None, _B, None),
    'linkedin.documents': ('LINKEDIN', NOT_EXECUTED, AMBIENTE_DESCONHECIDO, None, _B, None),

    # ── YOUTUBE ───────────────────────────────────────────────────────────
    # Resolver o endereco de uma conta ate ao `channelId` e o degrau que faltava
    # para a comunicacao publica largar a rota paga: o lote congelado guarda
    # URLs, e `playlistItems.list` precisa de id. Nao ha capacidade grossa na
    # matriz para isto, entao ela vive como `executa` — que e exatamente o caso
    # que a C2 declarou para esse papel.
    'youtube.channel.resolve': ('YOUTUBE', PARTIAL, ONLINE, None, _C3, None),
    'youtube.channel.discovery': ('YOUTUBE', PROVEN, ONLINE, None, _CE, 'INCREMENTAL'),
    'youtube.search': ('YOUTUBE', PROVEN, ONLINE, None, _CE, 'SEARCH_KEYWORD'),
    'youtube.video.metadata': ('YOUTUBE', PROVEN, ONLINE, None, _CE, 'FETCH_VIDEO_METADATA'),
    'youtube.comments': ('YOUTUBE', PROVEN, ONLINE, None, _CE, 'FETCH_COMMENTS'),
    'youtube.native_caption': ('YOUTUBE', PROVEN, ONLINE, None, _CE, 'FETCH_TRANSCRIPT'),
    # O unico 403 da lista. Descobrir e livre; o byte e que e o muro.
    'youtube.media': ('YOUTUBE', BLOCKED, LOCAL, DATACENTER_BLOCKED, _AP, None),

    # ── X / TWITTER ───────────────────────────────────────────────────────
    'x.direct_post': ('X', PROVEN, ONLINE, None, _B, None),
    'x.media': ('X', PROVEN, ONLINE, None, _B, None),
    'x.metrics': ('X', PROVEN, ONLINE, None, _B, None),
    # A legenda existe e veio VAZIA: «could not transcribe the audio».
    'x.native_caption': ('X', PARTIAL, ONLINE, None, _B, None),
    'x.discovery': ('X', UNKNOWN, AMBIENTE_DESCONHECIDO, None, _B, 'SEARCH_KEYWORD'),

    # ── FACEBOOK ──────────────────────────────────────────────────────────
    # Granularidade preservada: identidade sai, conteudo nao sai nenhum.
    'facebook.identity.discovery': ('FACEBOOK', PARTIAL, ONLINE, None, _AP, 'DISCOVER_ACCOUNT'),
    'facebook.content': ('FACEBOOK', BLOCKED, AMBIENTE_DESCONHECIDO, None, _AP, 'FETCH_POST'),
    'facebook.media': ('FACEBOOK', BLOCKED, AMBIENTE_DESCONHECIDO, None, _AP, 'FETCH_VIDEO_METADATA'),
    'facebook.metrics': ('FACEBOOK', BLOCKED, AMBIENTE_DESCONHECIDO, None, _AP, None),
    # ── SOCIAL ABERTA — o que o roteador ja servia antes deste benchmark ──
    # NAO foram medidas por mim. O estado vem de `leis/social_matriz.py`, que e
    # onde esta casa ja o tinha declarado, e o campo PROVA di-lo em claro.
    # Carregar uma declaracao existente citando a fonte nao e inventar; nao a
    # carregar seria deixar sem dono o mapa de rotas que ja correm.
    'mastodon.hashtag.search': ('MASTODON', PROVEN, ONLINE, None, _MZ, 'SEARCH_HASHTAG'),
    'mastodon.account.incremental': ('MASTODON', NOT_EXECUTED, ONLINE, None, _MZ, 'INCREMENTAL'),
    'bluesky.account.discovery': ('BLUESKY', PROVEN, ONLINE, None, _MZ, 'DISCOVER_ACCOUNT'),
    'bluesky.author.incremental': ('BLUESKY', NOT_EXECUTED, ONLINE, None, _MZ, 'INCREMENTAL'),
    'telegram.channel.incremental': ('TELEGRAM', PROVEN, ONLINE, None, _MZ, 'INCREMENTAL'),
}


# ══════════════════════════════════════════════════════════════════════════
# LEITURA
# ══════════════════════════════════════════════════════════════════════════
def existe(nome):
    """A capacidade esta declarada? Nome nao declarado NAO e erro — e UNKNOWN."""
    return nome in DECLARADAS


def estado(nome):
    """O estado medido. Capacidade nao declarada e UNKNOWN, nunca sucesso."""
    linha = DECLARADAS.get(nome)
    return linha[1] if linha else UNKNOWN


def plataforma(nome):
    linha = DECLARADAS.get(nome)
    return linha[0] if linha else None


def onde(nome):
    """→ (EXECUTION_TARGET, WHY_LOCAL). Capacidade desconhecida corre em lado nenhum."""
    linha = DECLARADAS.get(nome)
    return (linha[2], linha[3]) if linha else (AMBIENTE_DESCONHECIDO, None)


def prova(nome):
    linha = DECLARADAS.get(nome)
    return linha[4] if linha else None


def da_matriz(nome):
    """→ o nome grosso em `social_matriz`, ou None quando nao ha equivalente."""
    linha = DECLARADAS.get(nome)
    return linha[5] if linha else None


def pela_matriz(plat, capacidade_grossa):
    """O caminho inverso: da lingua da matriz para a capacidade declarada.

    E por aqui que o roteador — que fala `INCREMENTAL` — encontra o adaptador
    que se registou como `youtube.channel.discovery`. Sem esta traducao, ou o
    roteador aprendia nomes novos, ou a declaracao aprendia nomes velhos. As
    duas seriam a mesma coisa: um vocabulario a impor-se ao outro.
    """
    plat = (plat or '').upper()
    for n, v in DECLARADAS.items():
        if v[0] == plat and v[5] == capacidade_grossa:
            return n
    return None


def promete_resultado(nome):
    """Alguem tem direito de esperar objeto desta capacidade?

    E a pergunta que impede um adaptador de existir e fingir. BLOCKED, UNKNOWN
    e NOT_EXECUTED respondem NAO — e a resposta nao muda porque foi escrito
    codigo para ela.
    """
    return estado(nome) not in SEM_PROMESSA


def da_plataforma(plat):
    """Todas as capacidades declaradas de uma plataforma, ordenadas."""
    plat = (plat or '').upper()
    return {n: v for n, v in sorted(DECLARADAS.items()) if v[0] == plat}


def plataformas():
    return tuple(sorted({v[0] for v in DECLARADAS.values()}))


def por_ambiente(alvo):
    return {n: v for n, v in sorted(DECLARADAS.items()) if v[2] == alvo}


# ══════════════════════════════════════════════════════════════════════════
# O VALIDADOR
# ══════════════════════════════════════════════════════════════════════════
def conferir(nome=None):
    """Levanta `CapacidadeInvalida` na primeira linha que nao respeite a lei.

    Corre sobre tudo quando `nome` e None. E chamado no fim deste modulo: uma
    declaracao invalida rebenta ao importar, nao no dia em que alguem colher.
    """
    alvo = {nome: DECLARADAS[nome]} if nome else DECLARADAS
    for n, linha in alvo.items():
        if len(linha) != 6:
            raise CapacidadeInvalida('%s: a linha precisa de 6 campos, tem %d' % (n, len(linha)))
        plat, est, amb, porque, pv, grosso = linha
        if '.' not in n:
            raise CapacidadeInvalida('%s: o nome tem de ser pontuado (plataforma.capacidade)' % n)
        if not n.startswith(plat.lower().split('/')[0] + '.'):
            raise CapacidadeInvalida('%s: o nome nao comeca pela plataforma %s' % (n, plat))
        if est not in ESTADOS:
            raise CapacidadeInvalida('%s: estado %r fora do vocabulario' % (n, est))
        if amb not in AMBIENTES:
            raise CapacidadeInvalida('%s: ambiente %r fora do vocabulario' % (n, amb))
        if amb in EXIGEM_PORQUE and not porque:
            raise CapacidadeInvalida(
                '%s: alvo %s sem WHY_LOCAL. «sempre fizemos assim» nao e motivo.' % (n, amb))
        if porque is not None and porque not in PORQUE_LOCAL:
            raise CapacidadeInvalida('%s: WHY_LOCAL %r fora do vocabulario' % (n, porque))
        if porque in PROIBIDOS_ENQUANTO_HARDWARE_NAO_MEDIDO:
            raise CapacidadeInvalida(
                '%s: %s declarado com LOCAL_HARDWARE_STATUS=%s. Medir a maquina '
                'antes de prometer o acelerador dela.' % (n, porque, LOCAL_HARDWARE_STATUS))
        if not pv:
            raise CapacidadeInvalida('%s: estado sem documento de prova citado' % n)
        if grosso is not None and not str(grosso).isupper():
            raise CapacidadeInvalida(
                '%s: o nome da matriz e MAIUSCULO por convencao dela: %r' % (n, grosso))
    return True


conferir()
