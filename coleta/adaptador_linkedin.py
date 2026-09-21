#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ADAPTADOR DO LINKEDIN — a melhor midia das cinco, e o teto mais baixo.

E a unica plataforma onde o video e MP4 progressivo com endereco de vida longa
observada, e onde a legenda vem servida ao lado, com marcacao temporal. A
cadeia fecha sem login, sem navegador e sem rota paga.

O teto nao e acesso — e PROFUNDIDADE. A pagina da empresa entrega as ultimas
publicacoes e nao expoe endereco de pagina seguinte.

    `LINKEDIN_DISCOVERY_RECENT = PROVEN`.  `DEPTH = SHALLOW`.

Sao dois factos, e o segundo nao revoga o primeiro. Escrever
`LINKEDIN_DISCOVERY = BLOCKED` foi erro medido e ja corrigido, e nao se repete.

A LEGENDA NATIVA E DE MAQUINA, NAO DE GENTE
---------------------------------------------
O endereco da legenda di-lo em claro: `video-auto-caption-srt-acs-singleton`. E
SRT, nao WebVTT — numeracao de sequencia e virgula decimal, verificado nos
bytes. E automatica, o que significa ASR de outra casa.

    ISSO NAO A DESQUALIFICA. TORNA-A BARATA, NAO CONFIAVEL.

Uma legenda de maquina erra onde a nossa erra: termo agronomico e nome de
marca. Usa-se, e guarda-se de onde veio. Quando `TEXT_KIND` ganhar o valor
`NATIVE_CAPTION`, o ASR deles deixa de se confundir com o nosso.

═══════════════════════════════════════════════════════════════════════════
A C11 MEDIU O FICHEIRO ERRADO, E A LINKEDIN-BUILD-01 CORRIGE ISSO
═══════════════════════════════════════════════════════════════════════════
A C11 concluiu que o fornecedor pago «nao detecta video». Contou dezanove
campos — em `data/samples/ES-T8-002-posts.json`, que e o ficheiro
NORMALIZADO. O bruto esta ao lado, e tem vinte e seis:

    postVideo   em  56 de 472 posts     o endereco do MP4
    document    em  20 de 472           PDF + manifesto de transcricao
    article     em  93 de 472           link externo
    engagement.reactions[]  em 449      agregado por TIPO de reacao

    O CAMPO QUE A NORMALIZACAO NAO GUARDOU NAO E UM CAMPO QUE O PROVIDER
    NAO ENTREGOU.   `PROVIDER_GAP != NORMALIZATION_GAP`.

Este ficheiro passa a ser o dono dessa traducao, e a traducao nao deita nada
fora. Prova: `provas/linkedin_local_first.py`, contra o bruto preservado.

═══════════════════════════════════════════════════════════════════════════
LISTAGEM NAO E ENRIQUECIMENTO, E A DIFERENCA E DINHEIRO
═══════════════════════════════════════════════════════════════════════════
A listagem traz de graca — no mesmo item que ja se pagou — texto, autor, data
exacta, likes, partilhas, CONTAGEM de comentarios, TIPOS de reacao, endereco
de video, endereco de PDF e link externo.

O que ela NAO traz, medido em 472 de 472: legenda, duracao, texto de
comentario e lista de quem reagiu.

    LISTING != ENRICHMENT. E o enriquecimento e caro exactamente nos quatro
    campos que a listagem nao tem.

Por isso o enriquecimento e EXPLICITO e o seu valor por omissao e NAO. O SCRAP
nao decide se um post importa; quem pede diz o que quer. E antes de pedir
qualquer coisa a um provider pago, este ficheiro pergunta uma coisa so:

    FIELD_ALREADY_PRESENT  ->  PAID_ENRICHMENT_NOT_REQUIRED

═══════════════════════════════════════════════════════════════════════════
O DEFEITO DE TRADUCAO QUE ESTA MISSAO ENCONTROU — E FECHOU
═══════════════════════════════════════════════════════════════════════════
`linkedin.recent.discovery` estava traduzida para a capacidade grossa
`DISCOVER_ACCOUNT`. Medido: `mz.decisao('LINKEDIN','DISCOVER_ACCOUNT')`
devolve **ALLOWED**.

E a unica rota que vive debaixo dessa permissao e
`descoberta-indireta:site-da-organizacao` — ler o site DA PROPRIA
ORGANIZACAO para lhe achar o endereco no LinkedIn. A propria matriz escreve o
limite: «Guarda DISCOVERY_SOURCE, DISCOVERED_URL, TARGET_TYPE,
DISCOVERED_AT, e nunca conteudo de post fabricado.»

    «AS PUBLICACOES RECENTES DA PAGINA» E «O ENDERECO DA CONTA» SAO DOIS
    ACTOS. A TRADUCAO FAZIA O PRIMEIRO PEDIR EMPRESTADA A PERMISSAO DO
    SEGUNDO.   `IDENTITY != CONTENT`, violado na camada de traducao.

Nenhum codigo explorava isto — porque nenhuma das sete tinha rota. Mas a
permissao estava concedida e a porta ficava destrancada por dentro. Fechada:
`linkedin.recent.discovery` deixa de ter traducao, e a permissao de
`DISCOVER_ACCOUNT` passa a ter um dono que faz exactamente aquilo —
`linkedin.identity.discovery`.

    ISTO NAO ABRE ROTA NENHUMA. RETIRA UMA QUE ESTAVA ABERTA PELO NOME
    ERRADO.

═══════════════════════════════════════════════════════════════════════════
O QUE ESTA MISSAO NAO FEZ
═══════════════════════════════════════════════════════════════════════════
Nao mexeu em `leis/social_matriz.py`. Nao ligou rota nenhuma ao
`linkedin.com`. Nao baixou byte nenhum. `linkedin.history.discovery` continua
`UNKNOWN` — ver a nota do registo, que diz de que profundidade ela fala.
"""
import html as html_mod
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(HERE)
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401
import scrap_registo as reg  # noqa: E402
import social_envelope as env  # noqa: E402
import scrap_http as http  # noqa: E402

#: A confissão honesta, uma vez, para todo o ficheiro. Importada de quem já a
#: define seria melhor; ela vive aqui porque o adaptador já a usava neste
#: sentido antes desta missão, e mudar-lhe o dono não é deste dia.
NOT_KNOWN = 'NOT_KNOWN'

NOME = 'adaptador_linkedin'
PLATAFORMA = 'LINKEDIN'

#: A rota permitida, com o nome que a politica lhe deu. Nao se inventa outro:
#: um nome novo aqui seria uma segunda rota a fingir-se da primeira.
ROTA_IDENTIDADE = 'descoberta-indireta:site-da-organizacao'

#: A rota que produziu o bruto preservado. Ela esta `ROUTE_NOT_ALLOWED` na
#: matriz, e o nome dela viaja com os objectos para que ninguem leia um
#: envelope destes como se tivesse vindo de rota permitida.
ROTA_BRUTO_PRESERVADO = 'apify:harvestapi~linkedin-post-search'


# ══════════════════════════════════════════════════════════════════════════
# OS TRES NIVEIS DE AQUISICAO, E ELES NAO SE SOMAM
# ══════════════════════════════════════════════════════════════════════════
# `FREE` e `LOCAL` nao sao sinonimos. Uma rota gratuita gasta REDE; um
# processamento local gasta CPU e nao gasta ida nenhuma. Colapsa-los faria o
# relatorio dizer «de graca» sobre uma coisa que teve teto de rede, e faria o
# teto de rede parecer aplicavel a um ffmpeg.
#
#     FREE = ida a rede permitida e sem dolar.
#     LOCAL = sem ida a rede nenhuma.
#     PAID = dolar.
FREE = 'FREE'
LOCAL = 'LOCAL'
PAID = 'PAID'
BLOCKED = 'BLOCKED'
NIVEIS = (FREE, LOCAL, PAID, BLOCKED)


# ══════════════════════════════════════════════════════════════════════════
# O OBJECTO MINIMO DE UM POST — A LISTAGEM
# ══════════════════════════════════════════════════════════════════════════
#: O que a listagem entrega. Medido no bruto preservado, nao lido num folheto.
CAMPOS_DA_LISTAGEM = (
    'NATIVE_ID', 'URL', 'TEXT', 'PUBLISHED_AT', 'DECLARED_AUTHOR', 'AUTHOR_URL',
    'AUTHOR_KIND', 'MEDIA_TYPE', 'LIKES', 'COMMENTS_COUNT', 'SHARES',
    'REACTIONS_BY_TYPE', 'VIDEO_URL', 'VIDEO_THUMBNAIL', 'DOCUMENT_URL',
    'DOCUMENT_PAGES', 'DOCUMENT_TRANSCRIPT_URL', 'ARTICLE_URL', 'ARTICLE_TITLE',
    'IMAGE_URLS', 'SHARE_URN', 'IS_REPOST', 'RAW_REFERENCE',
)

#: O que a listagem NAO entrega, medido em 472 de 472. Cada um destes custa uma
#: acao PROPRIA — e tres dos quatro custam dinheiro.
CAMPOS_DE_ENRIQUECIMENTO = (
    'COMMENTS_TEXT', 'REACTION_PEOPLE', 'VIDEO_BYTES', 'DOCUMENT_BYTES',
    'NATIVE_CAPTION', 'TRANSCRIPT', 'VIDEO_DURATION',
)

#: As bandeiras do pedido. O valor por omissao de TODAS e `False`, e isso e a
#: lei desta camada e nao uma escolha de estilo.
#:
#:     O SCRAP NAO DECIDE SE O POST IMPORTA. QUEM PEDE E QUE DIZ.
BANDEIRAS = {
    'WANT_COMMENTS': ('COMMENTS_TEXT',),
    'WANT_REACTION_PEOPLE': ('REACTION_PEOPLE',),
    'WANT_MEDIA': ('VIDEO_BYTES',),
    'WANT_DOCUMENT': ('DOCUMENT_BYTES',),
    'WANT_TRANSCRIPT': ('NATIVE_CAPTION', 'TRANSCRIPT'),
}


def pedido_vazio():
    """→ o pedido por omissao: nenhum enriquecimento.

    Existe como funcao e nao como constante de modulo para que ninguem consiga
    mutar o padrao de toda a casa escrevendo numa chave de um dicionario
    partilhado. Um padrao mutavel nao e um padrao.
    """
    return {k: False for k in BANDEIRAS}


# ══════════════════════════════════════════════════════════════════════════
# BRUTO -> ENVELOPE. O tradutor que nao deita nada fora.
# ══════════════════════════════════════════════════════════════════════════
def _tipo_de_midia(item):
    """→ o tipo, por PRESENCA de campo e nunca por adivinhacao de texto.

    A ordem e deliberada: um post com video E imagem de capa e um post de
    video. Onze dos 472 posts preservados FALAM de video no texto e nao tem
    campo de video nenhum — e continuam a ser `TEXT`, porque o texto nao e
    prova de midia.
    """
    if item.get('postVideo'):
        return 'VIDEO'
    if item.get('document'):
        return 'DOCUMENT'
    if item.get('article'):
        return 'ARTICLE'
    if item.get('newsletterUrl'):
        return 'NEWSLETTER'
    if item.get('postImages'):
        return 'IMAGE'
    return 'TEXT'


def _autor(item):
    a = item.get('author') or {}
    return {
        'DECLARED_AUTHOR': a.get('name') or None,
        'AUTHOR_URL': a.get('linkedinUrl') or None,
        # `profile` e `company` sao dois eixos de negocio diferentes e um deles
        # traz dado pessoal. Guardar o tipo e o que permite nunca os misturar
        # depois.
        'AUTHOR_KIND': (a.get('type') or None),
    }


def _engajamento(item):
    e = item.get('engagement')
    e = e if isinstance(e, dict) else {}
    tipos = e.get('reactions') or []
    return {
        'LIKES': e.get('likes'),
        # A CONTAGEM. E so ela: o texto nao vem aqui, e chamar-lhe
        # «comentarios» seria a mentira que esta casa ja escreveu uma vez.
        #
        #     COMMENTS COUNT != COMMENTS TEXT.
        'COMMENTS_COUNT': e.get('comments'),
        'SHARES': e.get('shares'),
        # O agregado por TIPO — que diz se a comunicacao gerou interesse
        # tecnico ou so cortesia. Ja vinha pago e a normalizacao deitava-o
        # fora. NAO e a lista de pessoas.
        #
        #     REACTION COUNTS != REACTION PEOPLE.
        'REACTIONS_BY_TYPE': ({r.get('type'): r.get('count') for r in tipos
                               if isinstance(r, dict)} or None),
    }


def _video(item):
    """→ o que o bruto diz do video. Nada mais, e nenhum byte.

    Quatro campos que o bruto NAO tem, em 472 de 472: legenda, faixa de audio,
    duracao e manifesto. Escreve-los como `None` e a resposta; omiti-los faria
    parecer que ninguem perguntou.
    """
    v = item.get('postVideo')
    if not isinstance(v, dict):
        return {}
    url = v.get('videoUrl') or None
    return {
        'VIDEO_URL': url,
        'VIDEO_THUMBNAIL': v.get('thumbnailUrl') or None,
        # O endereco e ASSINADO e tem prazo. Guardar a URL nao e guardar a
        # midia, e o prazo do bruto preservado ja passou.
        #
        #     RAW_REFERENCE PARA ASSET EXPIRADO NAO E MIDIA ADQUIRIDA.
        'VIDEO_URL_SIGNED': bool(url and 'e=' in url),
        'VIDEO_URL_EXPIRES_AT': _prazo(url),
        'VIDEO_RENDITIONS_DECLARED': 1 if url else 0,
        'VIDEO_CAPTION_URL': None,
        'VIDEO_AUDIO_URL': None,
        'VIDEO_DURATION': None,
        'VIDEO_MANIFEST_URL': None,
        # Os bytes sao outra acao. Este campo existe para que o trace consiga
        # dizer «tenho o endereco e nao tenho o ficheiro» sem prosa.
        'VIDEO_BYTES_ACQUIRED': False,
    }


def _documento(item):
    """→ o que o bruto diz do carrossel/PDF, incluindo a rota do TEXTO dele."""
    d = item.get('document')
    if not isinstance(d, dict):
        return {}
    m = d.get('manifest') if isinstance(d.get('manifest'), dict) else {}
    pdf = d.get('transcribedDocumentUrl') or m.get('transcribedDocumentUrl') or None
    return {
        'DOCUMENT_TITLE': d.get('title') or None,
        'DOCUMENT_URL': pdf,
        'DOCUMENT_PAGES': d.get('totalPageCount'),
        'DOCUMENT_MANIFEST_URL': d.get('manifestUrl') or None,
        # O texto do documento tem endereco proprio. `linkedin.documents` dizia
        # «nunca tentado», e era verdade sobre a REDE — nao sobre o disco.
        'DOCUMENT_TRANSCRIPT_URL': m.get('transcriptManifestUrl') or None,
        'DOCUMENT_ASSET_URN': m.get('asset') or None,
        'DOCUMENT_SCAN_REQUIRED': m.get('scanRequiredForDownload'),
        'DOCUMENT_URL_EXPIRES_AT': _prazo(pdf),
        'DOCUMENT_COVER_IMAGES': [u for p in (d.get('coverPages') or [])
                                  if isinstance(p, dict)
                                  for u in (p.get('imageUrls') or [])] or None,
        'DOCUMENT_BYTES_ACQUIRED': False,
    }


def _artigo(item):
    """→ o link externo. E descoberta de FONTE, nao conteudo do LinkedIn.

    Noventa e tres dos 472 posts preservados carregam um endereco de site de
    terceiro ou da propria organizacao. Isso e descoberta ja paga, no disco, e
    ate aqui nunca usada. Baixar o artigo e outra aquisicao e nao acontece
    nesta capacidade.
    """
    a = item.get('article')
    if not isinstance(a, dict):
        return {}
    img = a.get('image') if isinstance(a.get('image'), dict) else {}
    return {
        'ARTICLE_URL': a.get('link') or None,
        'ARTICLE_TITLE': a.get('title') or None,
        # `subtitle` do LinkedIn e o DOMINIO, nao um subtitulo. Chamar-lhe
        # descricao seria inventar semantica que o campo nao tem.
        'ARTICLE_DOMAIN': a.get('subtitle') or None,
        'ARTICLE_DESCRIPTION': a.get('description') or None,
        'ARTICLE_THUMBNAIL': img.get('url') or None,
        'ARTICLE_BODY_ACQUIRED': False,
    }


_PRAZO = re.compile(r'[?&]e=(\d+)')


def _prazo(url):
    """→ o `e=` do endereco assinado como inteiro, ou None. Zero rede."""
    if not url:
        return None
    m = _PRAZO.search(url)
    return int(m.group(1)) if m else None


def campos_do_bruto(item):
    """→ o dicionario PLANO de tudo o que o bruto de um post entrega.

    Publico de proposito: e isto que a prova conta campo a campo, e e isto que
    um mutante que apague `postVideo` do mapeamento faz encolher.
    """
    if not isinstance(item, dict):
        raise ValueError('um item de post e um dicionario, nao %s' % type(item).__name__)
    pa = item.get('postedAt') if isinstance(item.get('postedAt'), dict) else {}
    fora = {
        'NATIVE_ID': str(item.get('id') or item.get('entityId') or '') or None,
        'URL': item.get('linkedinUrl') or None,
        'TEXT': item.get('content') or None,
        'PUBLISHED_AT': pa.get('date') or None,
        'PUBLISHED_AT_EPOCH_MS': pa.get('timestamp'),
        'MEDIA_TYPE': _tipo_de_midia(item),
        'SHARE_URN': item.get('shareUrn') or None,
        'IS_REPOST': bool(item.get('repost') or item.get('repostId')),
        'IMAGE_URLS': [i.get('url') for i in (item.get('postImages') or [])
                       if isinstance(i, dict) and i.get('url')] or None,
        'NEWSLETTER_URL': item.get('newsletterUrl') or None,
        'NEWSLETTER_TITLE': item.get('newsletterTitle') or None,
        # A VISIBILIDADE QUE A PLATAFORMA DECLARA. Guarda-se porque e um facto
        # do payload — e NAO se le como autorizacao.
        #
        #     «VISIBLE TO ANYONE» E VISIBILIDADE. NAO E PERMISSAO.
        'DECLARED_VISIBILITY': pa.get('postedAgoText') or None,
        # Os quatro que a listagem nunca tem. Explicitos para que o plano de
        # aquisicao consiga distinguir «nao veio» de «ninguem perguntou».
        'COMMENTS_TEXT': None,
        'REACTION_PEOPLE': None,
        'NATIVE_CAPTION': None,
        'TRANSCRIPT': None,
    }
    fora.update(_autor(item))
    fora.update(_engajamento(item))
    fora.update(_video(item))
    fora.update(_documento(item))
    fora.update(_artigo(item))
    return fora


def normalizar_post(item, *, run_id, country_scope='IT', route=None,
                    raw_reference=None, origem=PAID):
    """Um item de bruto -> um envelope canonico, sem perder campo nenhum.

    `origem` e o NIVEL da rota que produziu este bruto, e viaja com o objecto.
    O valor por omissao e `PAID` porque o unico bruto de posts que esta casa
    tem veio de rota paga: um `FREE` por omissao aqui escreveria, em cada
    objecto, que o dado foi de graca.

        O NIVEL DESTA ACAO E O NIVEL DA ORIGEM DO CAMPO SAO DOIS EIXOS.
        Reler um bruto preservado e `LOCAL` hoje e continua a ser `PAID` na
        procedencia — e o rasto guarda os dois.
    """
    if origem not in NIVEIS:
        raise ValueError('nivel de aquisicao fora do vocabulario: %r' % origem)
    c = campos_do_bruto(item)
    e = env.envelope(
        platform=PLATAFORMA,
        native_id=c['NATIVE_ID'] or env.DESCONHECIDO,
        url=c['URL'] or env.DESCONHECIDO,
        content_type='POST',
        route=route or ROTA_BRUTO_PRESERVADO,
        executor='adaptador_linkedin.normalizar_post',
        run_id=run_id, country_scope=country_scope,
        source_account=c['AUTHOR_URL'],
        published_at=c['PUBLISHED_AT'],
        # LINGUA E LUGAR NAO SE DEDUZEM. O payload nao declara nenhum dos dois,
        # e inferi-los do texto ou da localizacao da empresa seria fabricar.
        language=None, source_location=None,
        # Reler bruto que ja esta no disco custa zero DOLARES hoje. O que se
        # pagou, pagou-se uma vez, e esta na procedencia — nao neste campo.
        cost_usd=0.0,
        raw_reference=raw_reference,
        text=c['TEXT'],
        raw=c)
    e['ACQUISITION_TIER'] = LOCAL if raw_reference else origem
    e['FIELD_ORIGIN_TIER'] = origem
    e['LISTING_FIELDS_PRESENT'] = sorted(k for k in CAMPOS_DA_LISTAGEM
                                         if c.get(k) not in (None, [], {}, ''))
    e['ENRICHMENT_FIELDS_PRESENT'] = sorted(k for k in CAMPOS_DE_ENRIQUECIMENTO
                                            if c.get(k) not in (None, [], {}, ''))
    return e


def normalizar_lote(itens, **kw):
    """→ (envelopes, relatorio). O relatorio conta o que o bruto trazia.

    Existe porque «normalizei 472» e «recuperei 56 videos» sao frases
    diferentes, e a segunda e a unica que vira numero num relatorio.
    """
    saida = [normalizar_post(i, **kw) for i in itens]
    conta = {'ITENS': len(saida)}
    for campo in ('VIDEO_URL', 'DOCUMENT_URL', 'DOCUMENT_TRANSCRIPT_URL',
                  'ARTICLE_URL', 'REACTIONS_BY_TYPE', 'IMAGE_URLS',
                  'COMMENTS_TEXT', 'NATIVE_CAPTION'):
        conta[campo] = sum(1 for e in saida
                           if (e['RAW'].get(campo) not in (None, [], {}, '')))
    conta['MEDIA_TYPE'] = {}
    for e in saida:
        t = e['RAW'].get('MEDIA_TYPE')
        conta['MEDIA_TYPE'][t] = conta['MEDIA_TYPE'].get(t, 0) + 1
    return saida, conta


# ══════════════════════════════════════════════════════════════════════════
# A JANELA — DELTA, e ela vem de FORA
# ══════════════════════════════════════════════════════════════════════════
# O checkpoint NAO nasce aqui. Quem sabe o que ja viu e quem guarda o que viu, e
# isso vive acima do SCRAP. Este ficheiro faz uma coisa so: OBEDECE ao recorte.
#
#     O ADAPTER NAO TEM MEMORIA. UM ADAPTER COM MEMORIA E UM SEGUNDO DONO DO
#     CHECKPOINT, E O SEGUNDO DONO E SEMPRE O QUE NINGUEM ATUALIZA.
#
# Medido no bruto preservado, contando para tras a partir da captura:
#     7 dias  16/472 = 3,4%   ·  30 dias 60/472 = 12,7%
#    90 dias 175/472 = 37,1%  ·  365 dias 452/472 = 95,8%
#
# Uma corrida semanal com janela paga 3,4% do que a recolha total pagou.
JANELA = ('SINCE', 'POSTED_LIMIT_DATE', 'LAST_SEEN_TIME', 'LAST_SEEN_ID', 'MAX_POSTS')


def _ms(v):
    """→ epoch em milissegundos, de ISO-8601 ou de numero. None fica None."""
    if v is None:
        return None
    if isinstance(v, (int, float)):
        # Segundos e milissegundos distinguem-se pela ordem de grandeza. Um
        # limite escrito em segundos comparado contra milissegundos deixaria
        # passar tudo — que e exactamente o modo de falhar em silencio.
        return int(v) * 1000 if int(v) < 10 ** 12 else int(v)
    import datetime
    s = str(v).strip().replace('Z', '+00:00')
    d = datetime.datetime.fromisoformat(s)
    if d.tzinfo is None:
        d = d.replace(tzinfo=datetime.timezone.utc)
    return int(d.timestamp() * 1000)


def filtrar_janela(itens, *, since=None, posted_limit_date=None,
                   last_seen_time=None, last_seen_id=None, max_posts=None):
    """→ (itens dentro da janela, relatorio). Zero rede, zero dolar.

    `since`, `posted_limit_date` e `last_seen_time` sao TRES nomes do mesmo
    eixo — o tempo — porque tres fornecedores lhes dao tres nomes. O mais
    RESTRITIVO dos que vierem e o que vale: aceitar o mais largo faria um
    pedido de delta recolher historia inteira sempre que dois nomes chegassem
    juntos.

        DELTA != FULL HISTORY. E juntar dois limites pelo maximo e um delta
        que se transforma em historia sem ninguem pedir.

    `last_seen_id` corta ADEMAIS do tempo, nunca em vez dele: o mesmo instante
    pode ter mais de um post, e um id visto nao diz nada sobre os vizinhos.
    """
    limites = [_ms(x) for x in (since, posted_limit_date, last_seen_time)]
    limites = [x for x in limites if x is not None]
    corte = max(limites) if limites else None
    vistos = {str(x) for x in (last_seen_id or ())} if not isinstance(last_seen_id, str) \
        else {last_seen_id}
    dentro, fora_do_tempo, ja_visto, sem_data = [], 0, 0, 0
    for it in itens:
        c = campos_do_bruto(it) if isinstance(it, dict) and 'postedAt' in it else None
        if c is None:
            # Um item que nao declara data nao entra numa janela de tempo. Deixar
            # entrar seria tratar ausencia de prova como prova de recencia.
            sem_data += 1
            continue
        nid = c.get('NATIVE_ID')
        if nid and nid in vistos:
            ja_visto += 1
            continue
        t = c.get('PUBLISHED_AT_EPOCH_MS')
        if corte is not None:
            if t is None:
                sem_data += 1
                continue
            if t <= corte:
                fora_do_tempo += 1
                continue
        dentro.append(it)
    relatorio = {
        'ENTRADA': len(itens), 'DENTRO': len(dentro),
        'FORA_POR_TEMPO': fora_do_tempo, 'JA_VISTO_POR_ID': ja_visto,
        'SEM_DATA': sem_data,
        'CORTE_EPOCH_MS': corte, 'MAX_POSTS': max_posts,
        'TRUNCADO_POR_MAX_POSTS': 0,
    }
    if max_posts is not None and max_posts >= 0 and len(dentro) > max_posts:
        relatorio['TRUNCADO_POR_MAX_POSTS'] = len(dentro) - max_posts
        dentro = dentro[:max_posts]
        relatorio['DENTRO'] = len(dentro)
    return dentro, relatorio


# ══════════════════════════════════════════════════════════════════════════
# O GAP — o que falta, e SO o que falta
# ══════════════════════════════════════════════════════════════════════════
#: Onde cada campo de enriquecimento pode ser obtido, e com que nivel. O `None`
#: em `ROTA` significa que a politica canonica nao declara rota nenhuma — e
#: nesse caso o nivel e `BLOCKED`, que nao e o mesmo que caro.
ONDE_SE_OBTEM = {
    'COMMENTS_TEXT': {'NIVEL': PAID, 'MATRIZ': 'FETCH_COMMENTS',
                      'PORQUE': 'medido: 0 de 472 na listagem; texto e evento cobrado a parte'},
    'REACTION_PEOPLE': {'NIVEL': PAID, 'MATRIZ': 'FETCH_METRICS',
                        'PORQUE': 'dado pessoal; a CONTAGEM e o AGREGADO ja vem de graca na listagem'},
    'VIDEO_BYTES': {'NIVEL': FREE, 'MATRIZ': 'FETCH_VIDEO_BYTES',
                    'PORQUE': 'o endereco vem na listagem; os bytes sao uma ida propria ao CDN'},
    'DOCUMENT_BYTES': {'NIVEL': FREE, 'MATRIZ': 'FETCH_POST',
                       'PORQUE': 'o endereco do PDF vem na listagem; os bytes sao uma ida propria'},
    'NATIVE_CAPTION': {'NIVEL': FREE, 'MATRIZ': 'FETCH_TRANSCRIPT',
                       'PORQUE': 'nenhum fornecedor pago a entrega; 0 de 472. So a superficie publica a teve'},
    'TRANSCRIPT': {'NIVEL': LOCAL, 'MATRIZ': None,
                   'PORQUE': 'ASR local, e SO depois de haver bytes de audio nesta casa'},
    'VIDEO_DURATION': {'NIVEL': BLOCKED, 'MATRIZ': None,
                       'PORQUE': 'nao esta em rota nenhuma conhecida: 0 de 472, e a API oficial e de escrita'},
}


def _politica(matriz_cap):
    """→ a DECISAO da politica canonica para uma capacidade grossa. Zero rede.

    Le `leis/social_matriz.py`, que e o dono. Este ficheiro nao tem opiniao
    sobre permissao e nao guarda copia de nenhuma: uma copia divergiria no dia
    em que a politica mudasse, e a copia e sempre a que fica.
    """
    if not matriz_cap:
        return 'NOT_DECLARED'
    import social_matriz as mz
    return mz.decisao(PLATAFORMA, matriz_cap)['DECISAO']


def o_que_falta(envelope, pedido=None):
    """→ (pedidos, ja_presentes, falta). O que se quer, o que ja se tem, o gap.

    A sentinela que impede pagar duas vezes vive aqui, e ela e uma linha:

        FIELD_ALREADY_PRESENT  ->  PAID_ENRICHMENT_NOT_REQUIRED

    Sem ela, um enriquecimento pedido depois de uma listagem compraria outra
    vez o texto, a data e o endereco do video — campos que o mesmo item ja
    trazia. Isso nao e um risco teorico: e o modo normal de usar um provider
    que cobra por resultado.
    """
    pedido = dict(pedido or {})
    desconhecidas = [k for k in pedido if k not in BANDEIRAS]
    if desconhecidas:
        # Uma bandeira com o nome errado e um pedido que nunca se cumpre e
        # ninguem ve. Rebentar aqui e mais barato do que um relatorio a menos.
        raise ValueError('bandeira fora do vocabulario: %s. Aceitas: %s'
                         % (', '.join(sorted(desconhecidas)), ', '.join(sorted(BANDEIRAS))))
    bruto = envelope.get('RAW') or {}
    pedidos, ja, falta = [], [], []
    for bandeira, campos in sorted(BANDEIRAS.items()):
        if not pedido.get(bandeira):
            continue
        for campo in campos:
            pedidos.append(campo)
            if bruto.get(campo) not in (None, [], {}, ''):
                ja.append(campo)
            else:
                falta.append(campo)
    return pedidos, ja, falta


def plano_de_aquisicao(envelope, pedido=None):
    """→ o plano: para cada campo que FALTA, o nivel, a rota e a politica.

    Este e o degrau que a missao inteira existe para provar. Ele nao chama
    ninguem, nao gasta nada e nao decide se vale a pena — devolve o mapa da
    escada para aquele item, naquele pedido, com a politica de hoje lida do
    dono dela.

        PAID PROVIDER NAO TRANSFORMA ROTA PROIBIDA EM ROTA PERMITIDA.

    Por isso um campo cujo unico caminho e uma rota que a politica recusa sai
    como `BLOCKED_NO_PERMITTED_ROUTE` — e NAO como «precisa de dinheiro».
    """
    pedidos, ja, falta = o_que_falta(envelope, pedido)
    passos = []
    for campo in falta:
        onde = ONDE_SE_OBTEM.get(campo) or {'NIVEL': BLOCKED, 'MATRIZ': None,
                                            'PORQUE': 'campo sem rota conhecida'}
        decisao = _politica(onde['MATRIZ'])
        nivel = onde['NIVEL']
        # A POLITICA VEM DEPOIS DO NIVEL, E POR CIMA DELE. Um campo barato numa
        # rota recusada continua recusado, e um campo local nao precisa de
        # permissao de rota porque nao ha ida a rede nenhuma.
        if nivel != LOCAL and decisao != 'ALLOWED':
            nivel = BLOCKED
        passos.append({
            'NEED': campo, 'TIER': nivel,
            'MATRIZ_CAPABILITY': onde['MATRIZ'],
            'POLICY': decisao,
            'WHY': onde['PORQUE'],
            'VERDICT': ('BLOCKED_NO_PERMITTED_ROUTE' if nivel == BLOCKED
                        else 'READY' if nivel == LOCAL else 'NEEDS_' + nivel),
        })
    return {
        'WANTED': pedidos,
        'ALREADY_PRESENT': ja,
        'GAP': falta,
        'PLAN': passos,
        # A conclusao em dois booleanos, para que um teste nao tenha de reler prosa.
        'PAID_ENRICHMENT_NOT_REQUIRED': not any(p['TIER'] == PAID for p in passos),
        'PAID_NEEDED_FOR': sorted(p['NEED'] for p in passos if p['TIER'] == PAID),
        'BLOCKED_FOR': sorted(p['NEED'] for p in passos if p['TIER'] == BLOCKED),
        'LOCAL_FOR': sorted(p['NEED'] for p in passos if p['TIER'] == LOCAL),
        'FREE_FOR': sorted(p['NEED'] for p in passos if p['TIER'] == FREE),
    }


def rasto_de_aquisicao(envelope, plano=None):
    """→ o rasto por ORIGEM DE CAMPO. Nao mistura de onde veio o que.

    `ACQUISITION_TIER` e o nivel DESTA acao. `FIELDS_FROM_PAID` e a procedencia
    dos campos, que pode ser mais antiga que esta corrida — e e, sempre, quando
    se rele um bruto preservado.
    """
    bruto = envelope.get('RAW') or {}
    presentes = [k for k in CAMPOS_DA_LISTAGEM if bruto.get(k) not in (None, [], {}, '')]
    origem = envelope.get('FIELD_ORIGIN_TIER', PAID)
    return {
        'ACQUISITION_TIER': envelope.get('ACQUISITION_TIER'),
        'FIELDS_FROM_FREE': sorted(presentes) if origem == FREE else [],
        'FIELDS_FROM_PAID': sorted(presentes) if origem == PAID else [],
        'FIELDS_FROM_LOCAL': sorted(presentes) if origem == LOCAL else [],
        'LOCAL_DERIVATIONS': [],
        'PROVIDER': (ROTA_BRUTO_PRESERVADO if origem == PAID else None),
        'ROUTE': envelope.get('ROUTE'),
        'COST_USD': envelope.get('COST_USD'),
        'RAW_REFERENCE': envelope.get('RAW_REFERENCE'),
        'GAP': (plano or {}).get('GAP', []),
        'PAID_NEEDED_FOR': (plano or {}).get('PAID_NEEDED_FOR', []),
        'BLOCKED_FOR': (plano or {}).get('BLOCKED_FOR', []),
    }


# ══════════════════════════════════════════════════════════════════════════
# A UNICA ROTA PERMITIDA — e ela nao toca no linkedin.com
# ══════════════════════════════════════════════════════════════════════════
# `descoberta-indireta:site-da-organizacao`, `DIRECT_HTTP`, `PERMITIDA = SIM`.
#
# Ler o site DA PROPRIA ORGANIZACAO para lhe achar o endereco no LinkedIn. O
# §8.2(4) do User Agreement alcanca informacao obtida «from the Services,
# whether directly or through third parties (such as search tools or data
# aggregators or brokers)» — e o site da empresa nao e «the Services», nem e um
# buscador. E por isso que esta rota e a unica que a matriz permite.
#
#     PERGUNTAR AO GOOGLE NAO E ESTA ROTA. §8.2(4) NOMEIA «SEARCH TOOLS».
#
# E o que ela devolve e o HANDLE, nunca as publicacoes.
#
#     IDENTITY != CONTENT. Esta rota fica do lado da identidade, e o nome dela
#     no registo di-lo.
_HANDLE = re.compile(
    r'https?://(?:[a-z]{2,3}\.)?linkedin\.com/(company|school|in)/([A-Za-z0-9\-_%.]{2,100})',
    re.I)


def handles_no_html(corpo):
    """→ lista de (tipo, slug, url) achados no HTML. Pura, zero rede.

    Publica porque e o coracao testavel desta rota: a prova injecta HTML e conta
    o que sai, sem nunca abrir um socket.
    """
    fora, vistos = [], set()
    for m in _HANDLE.finditer(corpo or ''):
        tipo = m.group(1).lower()
        slug = m.group(2).rstrip('/').rstrip('.,)"\'')
        if not slug or slug.lower() in ('company', 'school', 'in'):
            continue
        chave = (tipo, slug.lower())
        if chave in vistos:
            continue
        vistos.add(chave)
        fora.append((('COMPANY' if tipo in ('company', 'school') else 'PERSON'),
                     slug, 'https://www.linkedin.com/%s/%s' % (tipo, slug)))
    return fora


#: Os hosts que esta rota NUNCA visita, com as palavras da propria politica:
#: «DESCOBERTA INDIRETA, e nenhum acesso automatizado ao linkedin.com»
#: (`leis/social_matriz.py`, LINKEDIN/_NOTA). `licdn` e a CDN de media do
#: LinkedIn — o mesmo dono, outro nome.
#:
#: Eles vivem aqui, e nao na matriz, porque a matriz declara ROTAS e este e o
#: alvo de UM pedido. Quem decide que a rota existe continua a ser a matriz;
#: quem recusa um alvo que a contradiz e a propria rota.
HOSTS_QUE_ESTA_ROTA_NUNCA_VISITA = (
    'linkedin.com', 'www.linkedin.com', 'licdn.com', 'dms.licdn.com',
    'media.licdn.com', 'static.licdn.com')


def _host_proibido(url):
    """→ o host proibido que esta URL alcanca, ou None. Puro, zero rede.

    Pergunta-se ao dono do transporte. Um `urlsplit` aqui poria `urllib` no
    espaco deste adaptador, e `test_M10_provider_direto` reprova-o com razao: um
    adaptador com `urllib` a mao esta a um passo de abrir a sua propria ligacao,
    e entao o portao, o teto de rede e o teto de gasto deixam de estar no
    caminho. A sentinela apanhou exactamente isto durante esta missao.

        A LISTA E DESTA ROTA. A PERGUNTA «QUE HOST E ESTE?» NAO E.
    """
    return http.host_na_lista(url, HOSTS_QUE_ESTA_ROTA_NUNCA_VISITA)


def identidade_pelo_site(*, site_url, run_id, country_scope='IT', medida=None,
                         transporte=None, **_):
    """A rota permitida. Le o site da organizacao. → lista de envelopes.

    `transporte` existe para que esta rota seja exercivel sem rede: um teste que
    depende da internet nao corre quando mais se precisa. Em producao ninguem o
    passa e o portao do `scrap_http` entra na frente, como para todas.

    O ALVO E CONFERIDO AQUI, E ANTES DO TRANSPORTE
    -----------------------------------------------
    Medido na LINKEDIN-OP-01, e era um buraco: passar
    `site_url = https://www.linkedin.com/company/image-line` fazia esta rota ir
    ao **linkedin.com** e devolver identidade com `RESULT = OK`.

    Havia uma defesa em producao — `scrap_http.buscar` chama `permitido()`, que
    le o robots do host — mas ela nao serve para este alvo, por duas razoes:

        1. ela PERGUNTA AO LINKEDIN se pode ler o LinkedIn, e a pergunta e ela
           mesma um pedido ao linkedin.com. O gate desta missao e
           `LINKEDIN_HTTP_REQUESTS = 0`, e zero inclui o robots.txt;
        2. `transporte` passa por fora dela, e `transporte` chega aqui vindo do
           `**extra` do `COLLECT`.

        UMA PROIBICAO QUE SE CONFIRMA PELA REDE DEPENDE DA REDE.
        ESTA E ESTATICA, PORQUE A POLITICA JA E ESTATICA.

    E a recusa e `RotaNaoPermitida`, que `social_rotas` ja traduz para
    `ROUTE_NOT_ALLOWED` — nao se inventa vocabulario nem segundo dono. O que ela
    NUNCA pode virar e `ZERO_RESULTS`: antes desta guarda, o alvo proibido saia
    como «zero resultados», e isso e uma medicao a mentir sobre uma recusa.

        UM ALVO RECUSADO NAO E UMA BUSCA VAZIA.
    """
    # ── E O ALVO TEM DE SER UM ENDERECO, ANTES DE SER PERMITIDO ────────────
    # Medido na LINKEDIN-OP-01: `site_url=''` devolvia `RESULT = OK`. Com o
    # transporte real isso rebentaria mais adiante com o nome do transporte; com
    # um transporte injectado, seguia em frente e o trace dizia OK sobre um
    # pedido que nunca teve alvo.
    #
    #     UM ALVO QUE NAO E UM ENDERECO NAO E UM ALVO PROIBIDO NEM PERMITIDO:
    #     E UM PEDIDO SEM ALVO, E ISSO TEM NOME PROPRIO.
    alvo = str(site_url or '').strip()
    if not alvo.lower().startswith(('http://', 'https://')) or not http.host_de(alvo):
        raise ValueError(
            'ALVO_AUSENTE_OU_MALFORMADO: esta rota le o SITE DA ORGANIZACAO e '
            'precisa de um endereco http(s) com host. Recebeu %r.' % (site_url,))
    mau = _host_proibido(site_url)
    if mau is not None:
        raise http.RotaNaoPermitida(
            'ESTA ROTA NAO VISITA %s. Ela le o site da PROPRIA organizacao e '
            'extrai dali o endereco que a organizacao publicou — '
            'DESCOBERTA INDIRETA. Pedir o linkedin.com como «site da '
            'organizacao» e a rota proibida com o nome da permitida. '
            'Ver leis/social_matriz.py LINKEDIN/_NOTA. · %s' % (mau, site_url))
    # E O ALVO NAO E O UNICO ENDERECO DESTE PEDIDO
    # ---------------------------------------------
    # Um site que responda `302 Location: linkedin.com` levava este pedido ao
    # host proibido sem ninguem perguntar nada — o `urlopen` segue saltos em
    # silencio. A rota declara a sua lista ao transporte, e o transporte recusa
    # cada salto ANTES de ler o robots do destino: ler o robots de um host que
    # esta rota nunca visita ja seria um pedido a ele.
    #
    #     UM REDIRECIONAMENTO E UM PEDIDO NOVO.
    #     UMA PROIBICAO QUE PERGUNTA AO PROIBIDO NAO CHEGOU A ZERO PEDIDOS.
    #
    # Quem sabe POR QUE estes hosts sao proibidos e esta rota; quem os recusa e o
    # dono do transporte. Dois papeis da mesma trava, e nenhum copia o outro.
    buscar = transporte or (lambda u: http.buscar(u, aceitar_json=False))
    with http.hosts_proibidos(*HOSTS_QUE_ESTA_ROTA_NUNCA_VISITA):
        corpo = buscar(site_url)
    achados = handles_no_html(corpo)
    ref = env.guardar_raw(PLATAFORMA, 'identidade-%s' % site_url, corpo)
    if medida is not None:
        medida['IMPLEMENTACAO'] = 'coleta/adaptador_linkedin.identidade_pelo_site'
        medida['ROUTE_CLASS'] = 'DIRECT_HTTP'
        medida['REQUESTS'] = 1
        medida['HANDLES_FOUND'] = len(achados)
        # Rota que a politica declara gratuita: zero e FACTO, nao palpite. E o
        # eixo do conhecimento vai a par do numero, como manda o roteador.
        medida['COST_STATE'] = 'FREE_ROUTE_BY_POLICY'
        medida['ACTUAL_COST_USD'] = 0.0
    saida = []
    for tipo, slug, url in achados:
        e = env.envelope(
            platform=PLATAFORMA, native_id=slug, url=url,
            content_type='DISCOVERY', route=ROTA_IDENTIDADE,
            executor='adaptador_linkedin.identidade_pelo_site',
            run_id=run_id, country_scope=country_scope,
            source_account=url, cost_usd=0.0,
            raw_reference=ref['PATH'],
            raw={
                # Os quatro campos que a propria matriz manda guardar, com os
                # nomes que ela usa.
                'DISCOVERY_SOURCE': site_url,
                'DISCOVERED_URL': url,
                'TARGET_TYPE': tipo,
                'DISCOVERED_AT': env.agora(),
                'RAW_SHA256': ref['SHA256'],
                # E o que ela manda NAO haver, dito em claro para que um
                # relatorio nunca leia identidade como publicacao.
                'POST_CONTENT': None,
                'CONTENT_ACQUIRED': False,
            })
        e['ACQUISITION_TIER'] = FREE
        e['FIELD_ORIGIN_TIER'] = FREE
        saida.append(e)
    return saida


def pronto_para_identidade(**_):
    """→ (consigo?, estado). Zero rede, zero dolar, zero credencial.

    Esta rota nao precisa de chave nenhuma: le um site publico. A sonda diz
    `True` porque a unica coisa que a poderia impedir — o robots do site da
    organizacao — so se sabe indo la, e ir la nao e uma sonda gratuita.
    """
    return True, 'NO_CREDENTIAL_REQUIRED'


# ══════════════════════════════════════════════════════════════════════════
# A MÍDIA PÚBLICA — o post público, objeto a objeto
# ══════════════════════════════════════════════════════════════════════════
#: A rota da mídia, com o nome que a política lhe deu. Não se inventa outro.
ROTA_MIDIA = 'public-post-media:linkedin-mp4'

#: A capacidade GROSSA que esta rota atravessa no dono da política. Não é
#: `FETCH_POST` — essa continua fechada, e reabri-la por baixo seria a tradução
#: desonesta que esta casa já corrigiu duas vezes.
CAPACIDADE_MIDIA = 'FETCH_PUBLIC_MEDIA'

#: Os hosts que ESTA rota visita. É a lista oposta à da identidade, e é de
#: propósito: aquela lê o site da organização; esta lê a página pública que a
#: plataforma serve a qualquer visitante.
HOSTS_DA_MIDIA_PUBLICA = ('linkedin.com', 'www.linkedin.com', 'licdn.com',
                          'dms.licdn.com', 'media.licdn.com')

#: O endereço de um post do LinkedIn, nas duas formas que a plataforma serve.
_RE_POST_PUBLICO = re.compile(
    r'^https?://(?:[a-z]{2,3}\.)?linkedin\.com/'
    r'(?:posts/[^\s"\'?#]+-activity-(\d+)-\w{4}|feed/update/urn:li:activity:(\d+))',
    re.I)
_RE_TAG_VIDEO = re.compile(r'<video\b[^>]*>', re.I)
_RE_ATRIBUTO = re.compile(r'([a-zA-Z][a-zA-Z0-9_-]*)\s*=\s*"([^"]*)"')


def id_do_post(post_url):
    """→ o activity id da plataforma, lido do endereço. Ou None.

    Este id NÃO é `SOURCE_ID` e não é `DOCUMENT_ID`: é a identidade do OBJETO na
    plataforma, e vale enquanto tal. Chamar-lhe outra coisa seria fabricar
    identidade a partir de um endereço.
    """
    m = _RE_POST_PUBLICO.match(str(post_url or '').strip())
    return (m.group(1) or m.group(2)) if m else None


def rendicoes_na_pagina(pagina):
    """→ (rendições, caption_url). Puro: zero rede, zero escrita.

    A página pública do post carrega um `<video>` cujo atributo `data-sources` é
    o JSON das rendições — `src`, `type`, `data-bitrate`. Foi assim que o
    extractor público do `yt-dlp` leu o LinkedIn por anos, e é o mesmo caminho
    que o actor pago usa. O que NÃO se lê aqui: nenhum manifesto, porque não há.

        O CAMINHO NÃO SE INVENTA: ELE LÊ-SE NA PÁGINA QUE A PLATAFORMA SERVE.

    `data-captions-url` vem ao lado quando o post tem legenda nativa — e não
    todos têm. Ausência de legenda é ausência, não falha.
    """
    m = _RE_TAG_VIDEO.search(pagina or '')
    if not m:
        return [], None
    attrs = dict(_RE_ATRIBUTO.findall(m.group(0)))
    bruto = html_mod.unescape(attrs.get('data-sources') or '')
    try:
        lista = json.loads(bruto)
    except (ValueError, TypeError):
        lista = []
    rendicoes = []
    for i, s in enumerate(lista if isinstance(lista, list) else []):
        if not isinstance(s, dict) or not s.get('src'):
            continue
        tbr = s.get('data-bitrate')
        try:
            tbr = int(tbr) if tbr is not None else None
        except (TypeError, ValueError):
            tbr = None
        rendicoes.append({'INDICE': i, 'URL': str(s['src']),
                          'MIME': s.get('type') or None, 'BITRATE_BPS': tbr})
    caption = html_mod.unescape(attrs.get('data-captions-url') or '') or None
    return rendicoes, caption


def escolher_rendicao(rendicoes, pedida=None):
    """→ (a escolhida, porquê). A MENOR que sirva, e a ordem é a economia.

    A pergunta é de fala, e o LinkedIn só oferece MP4 com a imagem dentro. As
    três rendições trazem a MESMA faixa de som; pedir 720p para transcrever é
    pagar banda por pixéis que ninguém vai ver.

        PARA OUVIR, A MENOR. A IMAGEM NÃO ENTRA NO TRANSCRIPT.

    A ordem é: a pedida, se houver e existir; senão a de menor `data-bitrate`
    DECLARADO. Sem bitrate declarado, mantém-se a ordem da página e assume-se a
    primeira — e o `WHY_SELECTED` diz que foi assim, para que a escolha possa ser
    contestada em vez de adivinhada.
    """
    if not rendicoes:
        return None, 'a pagina nao declara rendicao nenhuma'
    if pedida is not None:
        for r in rendicoes:
            if r['INDICE'] == pedida or r['URL'] == pedida:
                return r, 'rendicao pedida por quem chamou'
            try:
                if r['BITRATE_BPS'] == int(pedida):
                    return r, 'rendicao escolhida pelo bitrate pedido'
            except (TypeError, ValueError):
                pass
        return None, 'RENDICAO_PEDIDA_AUSENTE: a pagina nao serve %r' % (pedida,)
    com_taxa = [r for r in rendicoes if r['BITRATE_BPS']]
    if com_taxa:
        return (min(com_taxa, key=lambda r: r['BITRATE_BPS']),
                'a de MENOR data-bitrate declarado entre as %d rendicoes'
                % len(rendicoes))
    return rendicoes[0], ('a pagina nao declara bitrate em nenhuma das %d '
                          'rendicoes; ficou a primeira, pela ordem servida'
                          % len(rendicoes))


def midia_do_post_publico(*, post_url, run_id, country_scope='IT', rendicao=None,
                          medida=None, transporte=None, transporte_bytes=None,
                          **_):
    """A mídia de UM post público. → lista de envelopes (zero ou um).

    A ESCADA, e cada degrau diz o seu nome
    ---------------------------------------
        1 · PERGUNTA À POLÍTICA — antes de qualquer socket.
        2 · GET da página pública, pelo portão, com a autorização declarada.
        3 · LÊ as rendições do `<video data-sources>`.
        4 · ESCOLHE a menor.
        5 · GET DOS BYTES — e os bytes são o RAW.
        6 · MEDE o que chegou com `ffprobe` (o dono é `ferramenta/fala_local`).

    O QUE ESTA ROTA NÃO FAZ
    ------------------------
    · Não usa o fornecedor pago: medido, ele devolve o MESMO endereço que a
      página pública já entrega. Pagar por isto seria pagar duas vezes pelo
      mesmo endereço.
    · Não abre navegador, não usa login, não usa cookie, não usa proxy.
    · Não inventa `SOURCE_ID` nem `DOCUMENT_ID` — eles chegam de quem pediu.
    · Não deriva áudio nem transcreve: quem faz isso é a Ponte de Mídia da
      Collection, que recebe bytes e não sabe de onde vieram.
    """
    alvo = str(post_url or '').strip()
    nid = id_do_post(alvo)
    if not nid:
        # Um alvo que não é um endereço de post não é um alvo proibido nem
        # permitido: é um pedido sem alvo, e isso tem nome próprio.
        raise ValueError(
            'ALVO_AUSENTE_OU_MALFORMADO: esta rota le a pagina PUBLICA de um '
            'post do LinkedIn (posts/<slug>-activity-<id>-<4> ou '
            'feed/update/urn:li:activity:<id>). Recebeu %r.' % (post_url,))

    # ── DEGRAU 1 · A POLÍTICA, ANTES DE QUALQUER SOCKET ────────────────────
    import social_matriz as mz
    d = mz.decisao(PLATAFORMA, CAPACIDADE_MIDIA)
    if d['DECISAO'] != mz.PERMITIDA_SIM:
        raise http.RotaNaoPermitida(
            '%s · %s/%s · decisao %s' % (d['PORQUE'], PLATAFORMA,
                                         CAPACIDADE_MIDIA, d['DECISAO']))
    autorizacao = d.get('AUTORIZACAO_DO_PROJETO') or 'NAO DECLARADA'
    plataforma_politica = d.get('POLITICA_DA_PLATAFORMA') or 'NAO SEI'

    buscar = transporte or (lambda u: http.buscar(u, aceitar_json=False))
    buscar_bytes = transporte_bytes or http.buscar_bytes
    pedidos = 0

    # ── DEGRAU 2 · A PÁGINA, E A AUTORIZAÇÃO DITA AO PORTÃO ────────────────
    # O portão continua a ler o robots vivo, e continua a dizer que ele barra.
    # O que este bloco acrescenta é QUEM assume o risco — e a frase do portão
    # fica com as duas coisas, para que o artefacto não possa ser lido como
    # «a plataforma autorizou».
    with http.autorizado_pelo_dono(*HOSTS_DA_MIDIA_PUBLICA, porque=autorizacao):
        pagina = buscar(alvo)
        pedidos += 1
        rendicoes, caption_url = rendicoes_na_pagina(pagina)
        ref_pagina = env.guardar_raw(PLATAFORMA, 'post-%s-pagina' % nid, pagina)

        escolhida, porque = escolher_rendicao(rendicoes, rendicao)
        if escolhida is None:
            return []  # sem rendição não há mídia; o envelope abaixo não existe
        dados = buscar_bytes(escolhida['URL'])
        pedidos += 1
        ref_midia = env.guardar_raw_bytes(
            PLATAFORMA, 'post-%s-midia' % nid, dados, ext='mp4')

    # ── DEGRAU 6 · O QUE CHEGOU, MEDIDO NOS BYTES ──────────────────────────
    # `ffprobe` no ficheiro GRAVADO, não no que se pediu: `-f bestaudio` e um
    # nome `.m4a` dizem o que se quis, e nenhum dos dois abre o ficheiro.
    import fala_local as fl
    caminho = os.path.join(RAIZ, ref_midia['PATH'])
    v, a, porque_ff = fl.fluxos(caminho)
    duracao = fl.duracao(caminho) if not porque_ff else NOT_KNOWN

    if medida is not None:
        medida['IMPLEMENTACAO'] = 'coleta/adaptador_linkedin.midia_do_post_publico'
        medida['ROUTE_CLASS'] = 'DIRECT_HTTP'
        medida['REQUESTS'] = pedidos
        medida['COST_STATE'] = 'FREE_ROUTE_BY_POLICY'
        medida['ACTUAL_COST_USD'] = 0.0
        medida['RENDITIONS_FOUND'] = len(rendicoes)
        medida['SELECTED_RENDITION'] = escolhida['URL'].split('?')[0]
        medida['WHY_SELECTED'] = porque

    e = env.envelope(
        platform=PLATAFORMA, native_id=nid, url=alvo,
        content_type='VIDEO', route=ROTA_MIDIA,
        executor='adaptador_linkedin.midia_do_post_publico',
        run_id=run_id, country_scope=country_scope,
        source_account=None, cost_usd=0.0,
        raw_reference=ref_midia['PATH'],
        raw={
            # ── A MÍDIA: o que se pediu, o que se escolheu, o que chegou ───
            'VIDEO_URL': escolhida['URL'],
            'VIDEO_URL_HOST': http.host_de(escolhida['URL']),
            'VIDEO_URL_SIGNED': bool('e=' in escolhida['URL']),
            'VIDEO_URL_EXPIRES_AT': _prazo(escolhida['URL']),
            'RENDITIONS_FOUND': len(rendicoes),
            'RENDITIONS': [{'BITRATE_BPS': r['BITRATE_BPS'], 'MIME': r['MIME'],
                            'URL': r['URL'].split('?')[0]} for r in rendicoes],
            'SELECTED_RENDITION': escolhida['URL'].split('?')[0],
            'WHY_SELECTED': porque,
            'MEDIA_BYTES': ref_midia['BYTES'],
            'RAW_SHA256': ref_midia['SHA256'],
            'RAW_REFERENCE': ref_midia['PATH'],
            'VIDEO_STREAMS': v,
            'AUDIO_STREAMS': a,
            'FFPROBE_WHY': porque_ff,
            'VIDEO_DURATION': duracao,
            # ── O QUE OS BYTES SÃO, SEM SE CONFUNDIR COM ARQUIVO ───────────
            'VIDEO_BYTES_ACQUIRED': True,
            # O LinkedIn não serve faixa de som sozinha: o áudio DESTA mídia é
            # derivado por quem a processar, nunca «adquirido em separado».
            'AUDIO_ONLY_ACQUIRED': False,
            'AUDIO_DERIVED_EXPECTED': 'YES — MP4 progressivo com som muxado',
            # ── A LEGENDA NATIVA, QUANDO O POST A TEM ──────────────────────
            'NATIVE_CAPTION_URL': caption_url,
            'NATIVE_CAPTION_KIND': ('WEBVTT' if caption_url else None),
            'CAPTION_IS_NOT_TRANSCRIPT': (
                'CAPTION_TEXT e o que a plataforma legendou; TRANSCRIPT_TEXT e '
                'o que esta casa ouviu. Sao especies diferentes.'),
            # ── A PÁGINA DE ONDE TUDO SAIU ─────────────────────────────────
            'PAGE_BYTES': ref_pagina['BYTES'],
            'PAGE_SHA256': ref_pagina['SHA256'],
            'PAGE_RAW_REFERENCE': ref_pagina['PATH'],
            # ── OS TRÊS EIXOS, SEPARADOS COMO A LEI MANDA ──────────────────
            'TECHNICALLY_WORKS': 'YES',
            'PROJECT_OWNER_AUTHORIZED': autorizacao,
            'PLATFORM_POLICY_STATUS': plataforma_politica,
            'PROVIDER_USED': None,
            'APIFY_RUNS': 0,
            'REQUESTS': pedidos,
            # ── CELL: o carimbo é do envelope, e nenhum destes se inventa ──
            'SOURCE_ID': None,
            'DOCUMENT_ID': None,
        })
    e['ACQUISITION_TIER'] = FREE
    e['FIELD_ORIGIN_TIER'] = FREE
    return [e]


def pronto_para_midia(**_):
    """→ (consigo?, estado). Zero rede, zero dólar, zero credencial.

    Consigo se a política permitir esta capacidade. A pergunta é feita ao dono,
    e não respondida aqui: uma sonda que decide sozinha é uma segunda política.
    """
    import social_matriz as mz
    d = mz.decisao(PLATAFORMA, CAPACIDADE_MIDIA)
    if d['DECISAO'] != mz.PERMITIDA_SIM:
        return False, d['DECISAO']
    return True, 'FREE_ROUTE_BY_POLICY'


# ══════════════════════════════════════════════════════════════════════════
# O QUE ESTE ADAPTADOR DECLARA
# ══════════════════════════════════════════════════════════════════════════
# Sete capacidades medidas e uma nova. A nova e a unica com rota ligada, e ela
# e a unica que a politica permite.
#
#     UM ADAPTADOR PODE EXISTIR SEM EXECUTAR NADA. NAO PODE E EXISTIR DIZENDO
#     QUE EXECUTA.
reg.registar(PLATAFORMA, 'linkedin.identity.discovery', adaptador=NOME,
             pronto=pronto_para_identidade, rota=identidade_pelo_site,
             nota='A UNICA ROTA PERMITIDA: le o site da organizacao, nunca o linkedin.com '
                  'e nunca um buscador. Devolve HANDLE, nao publicacoes. E a dona da '
                  'permissao de DISCOVER_ACCOUNT, que `linkedin.recent.discovery` '
                  'pedia emprestada.')
reg.registar(PLATAFORMA, 'linkedin.recent.discovery', adaptador=NOME,
             nota='11, 13 e 10 activity ids em tres company pages; sem pagina seguinte. '
                  'DEIXOU de traduzir para DISCOVER_ACCOUNT na LINKEDIN-BUILD-01: posts '
                  'nao sao identidade, e a permissao daquela capacidade nao e desta.')
reg.registar(PLATAFORMA, 'linkedin.history.discovery', adaptador=NOME,
             nota='UNKNOWN fala da PAGINA DE EMPRESA: «Show more» nao expoe URL. NAO fala '
                  'do eixo de busca por palavra-chave, que o bruto preservado mostra a '
                  'alcancar 2018-01-09 a 2026-08-28 por rota hoje ROUTE_NOT_ALLOWED. '
                  'Dois eixos, e so um esta medido como desconhecido.')
reg.registar(PLATAFORMA, 'linkedin.direct_post', adaptador=NOME,
             nota='HTTP 200 a convidado, com <video data-sources>')
reg.registar(PLATAFORMA, 'linkedin.native_video', adaptador=NOME,
             nota='tres MP4 progressivos na pagina publica; UM na rota paga, com prazo de '
                  '~7 dias. URL LONG_LIVED_OBSERVED numa observacao e TEMPORARY noutra, '
                  'na mesma semana — nunca «permanente»')
reg.registar(PLATAFORMA, 'linkedin.native_caption', adaptador=NOME,
             nota='LEGENDA DE MAQUINA, E OS BYTES DIZEM WEBVTT. Medido em '\
                  '2026-09-18 no post publico 7151241570371948544: HTTP 200, 4283 B, '\
                  'cabecalho `WEBVTT`, `00:00.000 --> 00:03.240`. Existe POR POST: o '\
                  'post do canario nao tinha `data-captions-url`. O docstring do topo '\
                  'afirmava SRT — os bytes medidos dizem WEBVTT, e onde documento e '\
                  'bytes discordam, os bytes vencem (achado entregue, nao corrigido '\
                  'aqui). ZERO ocorrencias em 472 posts de rota paga: nenhum fornecedor '\
                  'a entrega')
reg.registar(PLATAFORMA, 'linkedin.comments', adaptador=NOME,
             nota='a CONTAGEM vem na listagem (335 em 95 de 472 posts); o TEXTO nao vem '
                  '(0 de 472) e e evento cobrado a parte. COUNT != TEXT')
reg.registar(PLATAFORMA, 'linkedin.documents', adaptador=NOME,
             nota='carrossel em PDF. Os ENDERECOS foram observados em 20 de 472 no bruto '
                  'preservado — PDF, manifesto e transcriptUrl. Os BYTES nunca '
                  'foram pedidos, e as URLs preservadas expiraram')

# ══════════════════════════════════════════════════════════════════════════
# A CAPACIDADE DA MÍDIA PÚBLICA — a única com rota que SAI à rede
# ══════════════════════════════════════════════════════════════════════════
# O nome é novo de propósito. NÃO é `linkedin.native_video` nem
# `linkedin.direct_post`: essas duas são MEDIÇÕES de superfície, e dar-lhes uma
# rota seria promover uma observação a capacidade sem passar pelo dono.
#
#     UMA MEDIÇÃO NÃO VIRA ROTA POR DECRETO.
#
# `FETCH_PUBLIC_MEDIA` é a capacidade GROSSA que a matriz passa a declarar, com
# os TRÊS EIXOS separados: a casa PERMITE (decisão do dono, escrita), o dono
# AUTORIZA (escopo: posts públicos), e a plataforma continua RESTRICTED.
reg.registar(PLATAFORMA, 'linkedin.public_post.media_resolution', adaptador=NOME,
             pronto=pronto_para_midia, rota=midia_do_post_publico,
             nota='A ROTA DA MIDIA PUBLICA: le a pagina que a plataforma serve a '
                  'qualquer visitante, tira dali o endereco do MP4 e os BYTES, e mede '
                  'o que chegou com ffprobe. Nao usa provedor pago — medido, ele '
                  'devolve o MESMO endereco. Nao usa login, cookie, navegador nem '
                  'proxy. Escopo: POSTS PUBLICOS, e so isso.')
# ⚠️ O QUE NAO SE DECLARA AQUI, E PORQUE
# ----------------------------------------
# O ASR local nao vira capacidade do LinkedIn. Ele ja tem DONO unico nesta casa
# — `ferramentas/fala_local.py` ouca, `coleta/executor_transcricao_midia.py`
# encaminha — e a Ponte de Midia recebe um CAMINHO e nao sabe de onde ele veio.
#
#     UMA CAPACIDADE POR PLATAFORMA PARA O MESMO MOTOR SERIA UMA SEGUNDA DONA
#     DO MESMO ACTO. E um dono que nao tem funcao registada aqui prometeria
#     resultado sem funcao — que e exactamente o que a A15 mede.
#
# O que esta rota prova sobre a fala esta no envelope e no relatorio: os bytes
# foram adquiridos aqui, e a Collection derivou deles o transcript com o motor
# da casa. `NATIVE_CAPTION != LOCAL_ASR_TRANSCRIPT`, e nenhum dos dois precisa
# de uma capacidade nova para ser dito.

