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
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import _gavetas  # noqa: E402,F401
import scrap_registo as reg  # noqa: E402
import social_envelope as env  # noqa: E402
import scrap_http as http  # noqa: E402
# ⚠️ O DONO DA ESPECIE DO TEXTO, E NAO UMA SEGUNDA COPIA DELA.
# `regras/proveniencia.py` governa a especie de um texto derivado. Este
# adaptador NAO redeclara o vocabulario: importa-o. Duas listas para o mesmo
# vocabulario divergem no dia em que alguem acrescentar uma especie a uma delas
# — e a que fica e sempre a que ninguem atualiza.
import proveniencia as pv  # noqa: E402

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
# D23 · O VIDEO DA PAGINA PUBLICA DE ORGANIZACAO — a porta que o dono abriu
# ══════════════════════════════════════════════════════════════════════════
# MEDIDO em 2026-09-23, desta maquina, egresso italiano (AS212238, Palermo),
# sem conta, sem cookie, sem login, sem navegador e sem rota paga:
#
#     /company/<slug>/                      200 · 10 a 18 activity ids
#     <video data-sources="…">               MP4 progressivo declarado
#     dms.licdn.com                         206 · video/mp4 · 7,4 MB medidos
#     data-captions-url                     200 · WebVTT e SRT, texto legivel
#
# O QUE A AQUISICAO FAZ, EM QUATRO PASSOS, E POR QUE NESTA ORDEM
# ---------------------------------------------------------------
#   1 · DESCOBERTA   a landing publica da organizacao serve os cartoes das
#                    publicacoes recentes; cada cartao com video traz o
#                    activity id, o endereco canonico do post e a etiqueta
#                    `<video data-sources>`.
#   2 · IDENTIDADE   a pagina publica do POST traz um JSON-LD `VideoObject`
#                    com `datePublished`, `duration`, `description` e as
#                    contagens de reaccao — tudo DECLARADO PELA PLATAFORMA.
#   3 · BYTES        o MP4 progressivo, escolhido pela rendicao mais LEVE (o
#                    que interessa e o texto e a prova; a banda e do dono).
#   4 · TEXTO        a legenda, quando o video a declara — com a especie
#                    preservada, porque e ASR de outra casa.
#
# A LEGENDA NAO E "MAIS UM CAMPO": E OUTRA ESPECIE DE TEXTO
# ---------------------------------------------------------
# `NATIVE_CAPTION` + `ORIGINAL` + base `DECLARED_BY_PROVIDER`, e nunca
# `TRANSCRIPT`. A casa ja escreveu por que:
#
#     CAPTION != TRANSCRIPT. E ASR DE OUTRA CASA E MAIS BARATA, NAO MELHOR.
#
# O endereco di-lo em claro — `video-auto-caption-srt-…` ou
# `video-auto-caption-webvtt-…` — e os BYTES confirmam o formato. Guardam-se os
# dois: o que a plataforma declara e o que se mediu, porque ja divergiram nesta
# casa (a medicao anterior escreveu «WebVTT» sobre bytes SRT).
#
# E NAO EXISTE EM TODO VIDEO. Medido: 2 de 5 videos numa organizacao, zero de 2
# noutra. Ausencia de legenda e RESULTADO, e o objeto sai com
# `DERIVED_TEXT = ASR_REQUIRED` e o dono do ASR nomeado — nunca mudo.
RAIZ_ADAPTADOR = os.path.dirname(HERE)

#: Os nomes das rotas, e eles sao os MESMOS de `leis/social_matriz.py`. Um
#: segundo nome aqui seria uma segunda rota a fingir-se da primeira.
ROTA_PAGINA_PUBLICA = 'linkedin:pagina-publica-da-organizacao'
ROTA_VIDEO_BYTES = 'linkedin:data-sources-mp4'
ROTA_LEGENDA_NATIVA = 'linkedin:data-captions-url'


#: A decisao do dono, com o nome e o ficheiro dela. Ela viaja em cada objeto:
#: um dado adquirido por uma excecao tem de dizer QUAL excecao o autorizou.
DECISAO_DO_DONO = 'D23'
DECISAO_DO_DONO_REF = 'DECISOES-DONO-2026-09-23.md'
AUTORIZACAO_ESCRITA = ('%s · %s · OWNER_AUTHORIZED=SIM · '
                       'PLATFORM_POLICY_STATUS=DISALLOWED'
                       % (DECISAO_DO_DONO, DECISAO_DO_DONO_REF))

# ── D24 · OS MESMOS TRES PAPEIS, PARA A PESSOA ──────────────────────────
# ⚠️ PORQUE HA TRES NOMES NOVOS E NAO SE REUSA OS DE CIMA. Uma rota e o que a
# casa DECLAROU na matriz, e o nome dela viaja em cada objeto. Se a aquisicao
# de uma pessoa saisse carimbada com o nome da rota de ORGANIZACAO, o objeto
# diria que veio de uma porta onde ele nao passou — e a auditoria acreditaria.
#
#     UM OBJETO TEM DE NOMEAR A PORTA POR ONDE PASSOU, E NAO A PARECIDA.
ROTA_POST_PUBLICO = 'linkedin:post-publico-de-pessoa'
ROTA_VIDEO_BYTES_PESSOA = 'linkedin:data-sources-mp4-de-pessoa'
ROTA_LEGENDA_PESSOA = 'linkedin:data-captions-url-de-pessoa'
DECISAO_DO_DONO_D24 = 'D24'
LIMITE_DA_PESSOA = 'PUBLIC_PERSON_VIDEO_ONLY'
AUTORIZACAO_ESCRITA_D24 = ('%s · %s · OWNER_AUTHORIZED=SIM · '
                           'PLATFORM_POLICY_STATUS=DISALLOWED'
                           % (DECISAO_DO_DONO_D24, DECISAO_DO_DONO_REF))

#: O QUE MUDA quando o alvo e uma pessoa. Um dicionario, e nao tres parametros
#: soltos: o que muda anda junto, e quem lê a chamada ve o conjunto.
DECISAO_DA_PESSOA = {
    'DECISAO': DECISAO_DO_DONO_D24,
    'REF': DECISAO_DO_DONO_REF,
    'AUTORIZACAO': AUTORIZACAO_ESCRITA_D24,
    'ROTA_PAGINA': ROTA_POST_PUBLICO,
    'ROTA_BYTES': ROTA_VIDEO_BYTES_PESSOA,
    'ROTA_LEGENDA': ROTA_LEGENDA_PESSOA,
    'LIMITE': LIMITE_DA_PESSOA,
    'EXECUTOR': 'adaptador_linkedin.video_de_post_publico',
}

#: As portas que NAO se abrem, com o nome de cada uma. A lista e a mesma que o
#: dono escreveu no D24: o que ele autorizou foi o VIDEO, e nao a pessoa.
_CONTEUDO_PESSOAL = re.compile(
    r'linkedin\.com/(?:'
    r'(?:in|pub)/[^/?#]+/(?:detail/)?(?:contact-info|followers|following|connections|people)'
    r'|overlay/(?:contact-info|followers|following)'
    r'|messaging'
    r'|feed/update/[^/?#]+/comments'
    r'|comments?(?:[/?#]|$)'
    r'|search/results/(?:people|connections)'
    r')', re.I)

#: A forma CANONICA do post publico — e ela carrega o activity id, que e a
#: identidade real da publicacao.
_POST_PUBLICO = re.compile(
    r'^https?://(?:[a-z]{2,3}\.)?linkedin\.com/posts/[A-Za-z0-9\-_%\.]+'
    r'-activity-(\d{15,25})-[A-Za-z0-9_\-]+/?$', re.I)
#: Os hosts que ESTA aquisicao pode alcancar. O portao abre so para estes, e
#: so enquanto ela corre — e `scrap_http.permitido()` continua a ler o robots
#: de cada um, porque e essa leitura que sustenta o `DISALLOWED` que se escreve.
HOSTS_DA_AQUISICAO = ('linkedin.com', 'www.linkedin.com', 'it.linkedin.com',
                      'dms.licdn.com', 'media.licdn.com')

#: Onde ficam os bytes. Ao lado do RAW de texto da casa (`data/raw/...`), e
#: nunca dentro do Git: midia nao se versiona.
PASTA_DOS_BYTES = os.path.join(RAIZ_ADAPTADOR, 'data', 'raw', 'LINKEDIN')

#: O dono unico do reconhecimento de fala desta casa. Nomeado aqui para que um
#: video sem legenda diga PARA QUEM falta o texto, em vez de ficar mudo.
DONO_DO_ASR = 'ferramentas/fala_local.py (via coleta/executor_transcricao_midia.py)'

_VIDEO_TAG = re.compile(r'<video\b[^>]*>', re.I | re.S)
_ATRIBUTO = re.compile(r'([A-Za-z0-9_:.-]+)="([^"]*)"')
_ACTIVITY_URN = re.compile(r'urn:li:activity:(\d{15,25})')
_POST_URL = re.compile(r'https://(?:[a-z]{2,3}\.)?linkedin\.com/posts/[A-Za-z0-9\-_%\.]+')
_PAGINA_ORGANIZACAO = re.compile(
    r'^https?://(?:[a-z]{2,3}\.)?linkedin\.com/company/([A-Za-z0-9\-_%\.]{2,100})/?$', re.I)
_PAGINA_PESSOA = re.compile(r'linkedin\.com/(?:in|pub)/', re.I)
_LOGIN = re.compile(r'linkedin\.com/(?:uas/login|login|signup|checkpoint)', re.I)
_JSON_LD = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.S)
_FORMATO_NO_ENDERECO = re.compile(r'video-auto-caption-(srt|webvtt)', re.I)
_SRT_EM_BYTES = re.compile(b'\\s*1\\s*[\\x0d\\x0a]{1,2}\\s*\\d\\d:\\d\\d:\\d\\d[,.]\\d\\d\\d')
_NAO_SEI = 'NAO SEI'


def valor_json_do_atributo(etiqueta, nome):
    """→ o valor de um atributo cujo conteudo e JSON, com aspas cruas ou escapadas.

    ⚠️ PORQUE NAO BASTA UM REGEX DE ASPAS. O `data-sources` chega de duas
    formas na mesma plataforma, e as duas foram medidas nesta casa:

        forma SERVIDA  `data-sources="[{&quot;src&quot;:&quot;…&quot;}]"`
                       └ as aspas do JSON estao escapadas — e por isso um
                         `="([^\"]*)"` funciona
        forma JA LIMPA `data-sources="[{"src":"…"}]"`
                       └ o valor tem aspas CRUAS dentro do atributo, e o mesmo
                         regex corta no primeiro `"` e nao apanha nada

    E o que acontece a seguir e o defeito que isto fecha: sem valor nenhum, o
    cartao sai como «video sem rendicoes declaradas» — um parse que falhou
    parece um facto sobre a plataforma.

        UM PARSE QUE FALHA NAO E UM FACTO SOBRE A FONTE.

    Por isso, quando o valor comeca por `[`, le-se ate ao `]` correspondente —
    o delimitador passa a ser a ESTRUTURA e nao a aspa.
    """
    i = etiqueta.find('%s="' % nome)
    if i < 0:
        return None
    ini = i + len(nome) + 2
    if etiqueta[ini:ini + 1] == '[':
        profundidade = 0
        for k in range(ini, len(etiqueta)):
            if etiqueta[k] == '[':
                profundidade += 1
            elif etiqueta[k] == ']':
                profundidade -= 1
                if profundidade == 0:
                    return etiqueta[ini:k + 1]
        return None
    fim = etiqueta.find('"', ini)
    return etiqueta[ini:fim] if fim > 0 else None


def atributos(etiqueta):
    """→ os atributos de uma etiqueta HTML, ja descodificados. Puro.

    `html.unescape` e obrigatorio e nao e detalhe: o `data-sources` chega com
    `&quot;` no lugar das aspas e `&amp;` no lugar do `&` dos enderecos. Ler
    sem descodificar devolve um JSON que nao abre — e um JSON que nao abre
    parece «este video nao declara rendicoes».
    """
    import html as _html
    return {k: _html.unescape(v) for k, v in _ATRIBUTO.findall(etiqueta or '')}


def rendicoes_do_data_sources(cru):
    """→ a lista de rendicoes declaradas, ou [] quando nao ha o que ler.

    Devolve o que a PLATAFORMA declarou, na ordem em que o declarou. Nao
    ordena por qualidade: quem escolhe e quem adquire, e escolhe com motivo.
    """
    import html as _html
    import json as _json
    texto = _html.unescape(cru or '')
    if not texto.strip():
        return []
    try:
        itens = _json.loads(texto)
    except ValueError:
        return []
    if not isinstance(itens, list):
        return []
    fora = []
    for i in itens:
        if not isinstance(i, dict) or not i.get('src'):
            continue
        fora.append({'SRC': i.get('src'),
                     'TYPE': i.get('type'),
                     'BITRATE': i.get('data-bitrate')})
    return fora


def formato_declarado_no_endereco(url):
    """→ 'SRT' | 'WEBVTT' | None — o que o PROPRIO endereco diz do formato.

    Nao e adivinhacao: o caminho da legenda traz `video-auto-caption-srt-…` ou
    `video-auto-caption-webvtt-…`. E uma declaracao da plataforma, e por isso
    ela e guardada ao lado da medicao dos bytes — as duas ja divergiram.
    """
    m = _FORMATO_NO_ENDERECO.search(str(url or ''))
    return m.group(1).upper() if m else None


def formato_pelos_bytes(corpo):
    """→ 'WEBVTT' | 'SRT' | 'DESCONHECIDO' — medido, nunca suposto."""
    if not corpo:
        return 'DESCONHECIDO'
    if corpo.lstrip()[:6] == b'WEBVTT':
        return 'WEBVTT'
    if _SRT_EM_BYTES.match(corpo):
        return 'SRT'
    return 'DESCONHECIDO'


def cartoes_com_video(corpo):
    """→ os cartoes da pagina que trazem video. Puro, zero rede.

    Cada cartao e o que a pagina publica entrega, lido da propria estrutura:

        ACTIVITY_ID      o `urn:li:activity:<id>` do cartao — identidade real
        POST_URL         o endereco canonico `/posts/<slug>-activity-<id>-<hash>`
        VIDEO_RENDICOES  o `data-sources` da etiqueta `<video>`
        CAPTION_URL      o `data-captions-url`, quando existe
        ASSET_URN        `data-digitalmedia-asset-urn` — a identidade da midia
        DECLARED_LANGUAGE o `data-language` — a lingua DECLARADA, nunca inferida
        POSTER_URL       a capa
        ASPECT_RATIO     a proporcao declarada

    ⚠️ A LIGACAO ENTRE O VIDEO E O POST E POSICIONAL, E ISSO E UMA LIMITACAO
    DECLARADA. O cartao nao traz um `data-urn` proprio; o que existe e a ordem
    do documento — o endereco do post e o `urn:li:activity` aparecem ANTES da
    etiqueta `<video>` do mesmo cartao. A ligacao e, portanto, «o ultimo
    endereco de post que apareceu antes desta etiqueta», e o cartao guarda o
    `urn` E o endereco para que os dois possam ser conferidos: quando os dois
    discordam do activity id, o cartao sai com `LIGACAO = CONFLITO` e nao e
    adquirido. Um casamento por posicao que se declara e melhor do que um
    casamento por posicao que se esconde.
    """
    fora = []
    for m in _VIDEO_TAG.finditer(corpo or ''):
        etiqueta = m.group(0)
        attrs = atributos(etiqueta)
        cru = valor_json_do_atributo(etiqueta, 'data-sources')
        rendicoes = rendicoes_do_data_sources(cru)
        if not rendicoes and cru is None:
            # Sem `data-sources` nenhum isto nao e um cartao de video: e outra
            # coisa qualquer que usa uma etiqueta `<video>`. Fora.
            continue
        antes = corpo[:m.start()]
        urns = _ACTIVITY_URN.findall(antes)
        urn = urns[-1] if urns else None
        # ── A LIGACAO E POR IDENTIDADE, E A POSICAO E SO O RECURSO ─────────
        # ⚠️ ISTO ESTAVA ERRADO E FOI MEDIDO. A primeira versao ligava o video
        # ao «ultimo endereco de post que apareceu antes da etiqueta». Em duas
        # organizacoes isso deu `CONFLITO` em 2 de 2 cartoes, e o cartao era
        # DESCARTADO — a pagina tinha la o video e a colheita ficava a zero.
        #
        # O que se faz agora, por ordem de forca da prova:
        #
        #   1 · IDENTIDADE  o endereco canonico CONTEM o activity id
        #                   (`/posts/<slug>-activity-<id>-<hash>`). Se existe um
        #                   endereco no documento que carrega ESTE id, e ele.
        #                   E a ligacao mais forte: duas provas que concordam.
        #   2 · POSICAO     o ultimo endereco antes da etiqueta, QUANDO o id
        #                   dele e o mesmo do urn. Concordam, e vale.
        #   3 · NADA        nem uma nem outra: o cartao sai `SO_URN` e o
        #                   endereco do post fica por saber. Nao se inventa.
        #
        #     LIGAR POR POSICAO E ADIVINHAR COM BOA SORTE.
        #     LIGAR POR IDENTIDADE E PROVAR.
        url = None
        ligacao = 'SEM_LIGACAO'
        if urn:
            for candidato in _POST_URL.findall(corpo):
                if 'activity-%s-' % urn in candidato:
                    url, ligacao = candidato, 'IDENTIDADE'
                    break
        if url is None and urn:
            antes_urls = _POST_URL.findall(antes)
            ultimo = antes_urls[-1] if antes_urls else None
            m3 = re.search(r'activity-(\d{15,25})-', ultimo or '')
            if ultimo and m3 and m3.group(1) == urn:
                url, ligacao = ultimo, 'POSICAO_CONCORDA'
            elif ultimo:
                ligacao = 'CONFLITO_DE_POSICAO'
        if url is None and not urn:
            antes_urls = _POST_URL.findall(antes)
            if antes_urls:
                url, ligacao = antes_urls[-1], 'SO_URL'
        id_do_url = None
        if url:
            m2 = re.search(r'activity-(\d{15,25})-', url)
            id_do_url = m2.group(1) if m2 else None
        if urn is None:
            urn = id_do_url
        fora.append({
            'ACTIVITY_ID': urn or id_do_url,
            'ACTIVITY_ID_DO_URN': urn,
            'ACTIVITY_ID_DO_URL': id_do_url,
            'POST_URL': url,
            'LIGACAO': ligacao,
            'VIDEO_RENDICOES': rendicoes,
            'DATA_SOURCES_UNPARSABLE': bool(cru is not None and not rendicoes),
            'CAPTION_URL': attrs.get('data-captions-url') or None,
            'ASSET_URN': attrs.get('data-digitalmedia-asset-urn') or None,
            'DECLARED_LANGUAGE': attrs.get('data-language') or None,
            'POSTER_URL': attrs.get('data-poster-url') or None,
            'ASPECT_RATIO': attrs.get('data-aspect-ratio') or None,
        })
    # Um cartao por activity id: a mesma publicacao pode aparecer duas vezes
    # na pagina (a versao "vista" e a completa), e contar duas vezes o mesmo
    # video inflaria a medicao.
    vistos, unicos = set(), []
    for c in fora:
        chave = c['ACTIVITY_ID'] or c['POST_URL'] or id(c)
        if chave in vistos:
            continue
        vistos.add(chave)
        unicos.append(c)
    return unicos


def video_do_post(corpo):
    """→ o que a pagina publica do POST declara do video. Puro, zero rede.

    Le o JSON-LD `VideoObject`. Ele e a unica fonte desta casa para
    `datePublished` — e `PUBLISHED_AT` NAO se deduz do nosso relogio nem do
    `postedAgoText` do cartao.
    """
    import json as _json
    for cru in _JSON_LD.findall(corpo or ''):
        try:
            d = _json.loads(cru.strip())
        except ValueError:
            continue
        if not isinstance(d, dict) or d.get('@type') != 'VideoObject':
            continue
        inter = d.get('interactionStatistic')
        inter = inter if isinstance(inter, list) else ([inter] if inter else [])
        contas = {}
        for i in inter:
            if not isinstance(i, dict):
                continue
            tipo = str(i.get('interactionType') or '').rsplit('/', 1)[-1]
            contas[tipo] = i.get('userInteractionCount')
        return {
            'PUBLISHED_AT': d.get('datePublished') or None,
            'PUBLISHED_AT_SOURCE': 'JSON_LD_VideoObject.datePublished',
            'UPLOAD_DATE': d.get('uploadDate') or None,
            'DURATION': d.get('duration') or None,
            'HEADLINE': d.get('headline') or None,
            'NAME': d.get('name') or None,
            'DESCRIPTION': d.get('description') or None,
            'KEYWORDS': d.get('keywords') or None,
            'WIDTH': d.get('width'),
            'HEIGHT': d.get('height'),
            'EMBED_URL': d.get('embedUrl') or None,
            'CONTENT_URL': d.get('contentUrl') or None,
            'THUMBNAIL_URL': d.get('thumbnailUrl') or None,
            'IS_FAMILY_FRIENDLY': d.get('isFamilyFriendly'),
            'LIKE_COUNT': contas.get('LikeAction'),
            'COMMENT_COUNT': contas.get('CommentAction'),
            'CREATOR_NAME': ((d.get('creator') or {}).get('name')
                             if isinstance(d.get('creator'), dict) else None),
            'CREATOR_URL': ((d.get('creator') or {}).get('url')
                            if isinstance(d.get('creator'), dict) else None),
        }
    return {}


def _slug(s):
    """→ texto limpo para nome de ficheiro. Mesmo formato do resto da casa.

    Vive aqui, e nao se importa de `social_envelope`, porque importar um nome
    privado (`_slug`) de outro modulo e construir sobre o que ninguem prometeu
    manter. Sao quatro linhas; a copia e mais honesta do que a dependencia.
    """
    return ''.join(c if (c.isalnum() or c in '-_.') else '-' for c in str(s)).strip('-')


def _guardar_bytes(corpo, pasta, nome_base, extensao):
    """Grava bytes medidos e devolve o que se MEDIU deles. Nada se interpreta.

    O nome carrega o sha: o mesmo byte gravado duas vezes nao cria dois
    ficheiros, e um ficheiro diferente nunca sobrescreve o anterior.
    """
    h = hashlib.sha256(corpo).hexdigest()
    destino = os.path.join(PASTA_DOS_BYTES, pasta)
    os.makedirs(destino, exist_ok=True)
    caminho = os.path.join(destino, '%s__%s.%s' % (_slug(nome_base)[:48], h[:16], extensao))
    if not os.path.exists(caminho):
        with open(caminho, 'wb') as f:
            f.write(corpo)
    return {'PATH': caminho,
            'RELATIVO': os.path.relpath(caminho, RAIZ_ADAPTADOR).replace('\\', '/'),
            'SHA256': h, 'BYTES': len(corpo)}


def _alvo_e_organizacao(pagina_url):
    """→ o slug, ou levanta. O alvo desta aquisicao e uma PAGINA DE ORGANIZACAO.

    Tres recusas, cada uma com o nome do que recusou — porque «nao deu» nao
    distingue um alvo proibido de um alvo mal escrito:

        PERFIL DE PESSOA   dado pessoal, fora do limite declarado (D23)
        ECRÃ DE LOGIN      contornar controlo de acesso esta fora do limite
        ALVO MAL FORMADO   um pedido sem alvo nao e um alvo proibido

    E a recusa e ESTATICA: nao se confirma pela rede. Uma proibicao que
    pergunta ao proibido ja fez um pedido a ele.
    """
    alvo = str(pagina_url or '').strip()
    if _LOGIN.search(alvo):
        raise http.RotaNaoPermitida(
            'ALVO_RECUSADO: ecra de login. Esta aquisicao NAO contorna controlo '
            'de acesso — nem login wall, nem CAPTCHA, nem bloqueio. · %s' % alvo)
    if _PAGINA_PESSOA.search(alvo):
        raise http.RotaNaoPermitida(
            'ALVO_RECUSADO: perfil de PESSOA. O limite autorizado pelo dono (D23) '
            'cobre PAGINAS DE ORGANIZACAO; perfil de pessoa e dado pessoal e fica '
            'fora. · %s' % alvo)
    m = _PAGINA_ORGANIZACAO.match(alvo)
    if not m:
        raise ValueError(
            'ALVO_AUSENTE_OU_MALFORMADO: esta aquisicao le a PAGINA PUBLICA de '
            'uma organizacao e precisa de um endereco '
            '`https://www.linkedin.com/company/<slug>/`. Recebeu %r.' % (pagina_url,))
    return m.group(1).lower()


def _alvo_e_post_publico(post_url):
    """A TRAVA DO D24. → (url, activity_id). Recusa e ESTATICA: zero rede.

    O dono autorizou, por escrito, o VIDEO de pessoas do agro (D24). O que essa
    autorizacao fez foi tirar o limite «perfil de PESSOA fora» — NAO abriu o
    resto, e nao abriu o que a plataforma fecha. Por isso:

        POST PUBLICO DE PESSOA   passa. `/posts/<slug>-activity-<id>-<hash>`
                                 responde 200 a convidado (medido).
        PAGINA DE PERFIL         recusada, e o motivo e MEDIDO, nao suposto:
                                 `linkedin.com/in/<slug>/` responde HTTP 999
                                 com `authwall`, com a UA desta casa e com UA
                                 de navegador. Nao se contorna.
        CONTEUDO PESSOAL         contatos, seguidores, mensagens e comentarios
                                 de terceiros ficam fora — o D24 nomeia-os um
                                 a um na lista do que NAO autoriza.
        ECRA DE LOGIN            contornar controlo de acesso continua fora.

    Uma recusa que nao diz QUAL coisa recusou nao serve para decidir nada.
    """
    alvo = str(post_url or '').strip()
    if _LOGIN.search(alvo):
        raise http.RotaNaoPermitida(
            'ALVO_RECUSADO: ecra de login. Esta aquisicao NAO contorna controlo '
            'de acesso — nem login wall, nem CAPTCHA, nem bloqueio. · %s' % alvo)
    if _CONTEUDO_PESSOAL.search(alvo):
        raise http.RotaNaoPermitida(
            'ALVO_RECUSADO: conteudo PESSOAL (contato, seguidor, mensagem ou '
            'comentario de terceiro). A D24 autoriza o VIDEO publico da pessoa e '
            'nomeia o resto como fora: contatos, seguidores, mensagens e '
            'comentarios de terceiros. · %s' % alvo)
    m = _POST_PUBLICO.match(alvo)
    if m:
        return alvo, m.group(1)
    if _PAGINA_PESSOA.search(alvo):
        raise http.RotaNaoPermitida(
            'ALVO_RECUSADO: pagina de PERFIL DE PESSOA. MEDIDO em 2026-09-23: '
            'responde HTTP 999 com `authwall` — com a UA desta casa E com UA de '
            'navegador, no egresso IT/datacenter, sem conta e sem cookie. A '
            'plataforma fechou esta porta, e NAO se contorna. O alvo desta porta '
            'e a pagina do POST publico: `/posts/<slug>-activity-<id>-<hash>`. · %s'
            % alvo)
    if _PAGINA_ORGANIZACAO.match(alvo):
        raise ValueError(
            'ALVO_TROCADO_DE_PORTA: esta e a pagina de ORGANIZACAO, e a porta '
            'dela e `video_da_pagina_publica` (D23), que descobre as publicacoes '
            'na propria landing. Aqui o alvo e a pagina de um POST publico. · %s'
            % alvo)
    raise ValueError(
        'ALVO_AUSENTE_OU_MALFORMADO: esta aquisicao le a PAGINA PUBLICA DE UM '
        'POST e precisa de um endereco '
        '`https://www.linkedin.com/posts/<slug>-activity-<id>-<hash>`. Recebeu %r.'
        % (post_url,))


def _buscar_texto(url, transporte, autorizacao=None):
    if transporte is not None:
        return transporte(url)
    return http.buscar(url, aceitar_json=False)


def _url_do_post(cartao):
    """→ o endereco canonico do post. Preferido o que a pagina publicou."""
    if cartao.get('POST_URL'):
        return cartao['POST_URL']
    if cartao.get('ACTIVITY_ID'):
        return 'https://www.linkedin.com/feed/update/urn:li:activity:%s/' % cartao['ACTIVITY_ID']
    return None


def _rendicao_escolhida(rendicoes):
    """→ (a rendicao, o motivo). A MAIS LEVE que declare `video/mp4`.

    O criterio e declarado e nao e gosto: o que se procura neste objeto e o
    TEXTO e a PROVA de que o video existe; a banda e do dono. Quando nao ha
    bitrate declarado, a primeira da lista e a resposta — e o motivo di-lo.
    """
    mp4 = [r for r in rendicoes if 'mp4' in str(r.get('TYPE') or '').lower()]
    if not mp4:
        return None, 'NENHUMA_RENDICAO_MP4_DECLARADA'
    com_peso = [r for r in mp4 if isinstance(r.get('BITRATE'), (int, float))]
    if not com_peso:
        return mp4[0], 'PRIMEIRA_DECLARADA_SEM_BITRATE'
    return min(com_peso, key=lambda r: r['BITRATE']), 'MENOR_BITRATE_DECLARADO'


def posts_com_video(*, pagina_url, run_id, country_scope='IT', teto=None,
                    transporte=None, medida=None, **_):
    """A DESCOBERTA. → (cartoes, contexto). Nao adquire bytes nenhuns.

    Devolve o que a pagina publica serve, com o rasto dos pedidos feitos. Nao
    grava RAW e nao monta envelope: quem faz isso e a aquisicao, e separar as
    duas coisas e o que permite provar a descoberta sem tocar num byte de
    midia.
    """
    slug = _alvo_e_organizacao(pagina_url)
    pedidos = []

    def _um_pedido(url, tipo='ROUTE'):
        pedidos.append({'TYPE': tipo, 'TARGET': http.host_de(url), 'URL': url})

    autorizacao = http.autorizacao_actual()
    with http.autorizacao_do_dono(ROTA_PAGINA_PUBLICA, HOSTS_DA_AQUISICAO,
                                 decisao=AUTORIZACAO_ESCRITA, plataforma=PLATAFORMA):
        _um_pedido(pagina_url)
        corpo = _buscar_texto(pagina_url, transporte)
    cartoes = [c for c in cartoes_com_video(corpo) if c['LIGACAO'] != 'CONFLITO']
    if teto is not None and int(teto) >= 0:
        cartoes = cartoes[:int(teto)]
    contexto = {
        'PAGINA': pagina_url, 'SLUG': slug, 'PEDIDOS': pedidos,
        'PEDIDOS_TOTAIS': len(pedidos),
        'CARTOES_COM_VIDEO': len(cartoes),
        'AUTORIZACAO_ATRAVESSADA': AUTORIZACAO_ESCRITA,
        'AUTORIZACAO_VIVA': autorizacao is not None,
        'PLATFORM_POLICY_STATUS': 'DISALLOWED',
        'OWNER_AUTHORIZED': 'SIM',
        'ROTA': ROTA_PAGINA_PUBLICA,
    }
    if medida is not None:
        medida.update({'IMPLEMENTACAO': 'coleta/adaptador_linkedin.posts_com_video',
                       'ROUTE_CLASS': 'DIRECT_HTTP', 'REQUESTS': len(pedidos),
                       'HANDLES_FOUND': len(cartoes),
                       'COST_STATE': 'FREE_ROUTE_BY_OWNER_DECISION',
                       'ACTUAL_COST_USD': 0.0,
                       'OWNER_AUTHORIZED': 'SIM',
                       'PLATFORM_POLICY_STATUS': 'DISALLOWED',
                       'DECISAO_DO_DONO': DECISAO_DO_DONO})
    return cartoes, contexto


def legenda_do_video(*, caption_url, run_id, country_scope='IT', transporte=None,
                     nome_base='legenda', medida=None, **_):
    """A LEGENDA NATIVA, sozinha. → (o texto, a ficha do que se mediu).

    Existe como rota propria porque a capacidade e propria: a legenda tem
    dono, especie e limite declarados na matriz, e esconder a aquisicao dela
    dentro de outra rota faria a politica nao poder ser perguntada sobre ela.
    """
    autorizacao = http.autorizacao_actual()
    with http.autorizacao_do_dono(ROTA_LEGENDA_NATIVA, HOSTS_DA_AQUISICAO,
                                 decisao=AUTORIZACAO_ESCRITA, plataforma=PLATAFORMA):
        if transporte is not None:
            corpo = transporte(caption_url)
            if isinstance(corpo, str):
                corpo = corpo.encode('utf-8')
            meta = {'CONTENT_TYPE': None, 'STATUS': None}
        else:
            corpo, meta = http.buscar_bytes(caption_url, aceitar='*/*')
    declarado = formato_declarado_no_endereco(caption_url)
    medido = formato_pelos_bytes(corpo)
    extensao = (medido if medido in ('SRT', 'WEBVTT') else 'txt').lower()
    ficha = _guardar_bytes(corpo, 'legenda', nome_base, extensao)
    ficha.update({'CAPTION_URL': caption_url,
                  'FORMAT_DECLARED_BY_URL': declarado,
                  'FORMAT_MEASURED_IN_BYTES': medido,
                  'CONTENT_TYPE_SERVED': meta.get('CONTENT_TYPE'),
                  'STATUS': meta.get('STATUS'),
                  'AUTORIZACAO_ATRAVESSADA': AUTORIZACAO_ESCRITA,
                  'ROTA': ROTA_LEGENDA_NATIVA,
                  'DIVERGE': bool(declarado and medido not in (declarado, 'DESCONHECIDO')
                                  and declarado != medido)})
    if medida is not None:
        medida.update({'IMPLEMENTACAO': 'coleta/adaptador_linkedin.legenda_do_video',
                       'REQUESTS': 1, 'CAPTION_BYTES': ficha['BYTES'],
                       'CAPTION_FORMAT': medido, 'CAPTION_SHA256': ficha['SHA256'],
                       'ACTUAL_COST_USD': 0.0,
                       'PLATFORM_POLICY_STATUS': 'DISALLOWED',
                       'OWNER_AUTHORIZED': 'SIM'})
    return corpo.decode('utf-8', 'replace'), ficha


def video_da_pagina_publica(*, pagina_url, run_id, country_scope='IT', teto=3,
                            transporte=None, egresso=None, medida=None, **_):
    """A AQUISICAO COMPLETA. → lista de envelopes, um por publicacao com video.

    `pagina_url` e o endereco da pagina de ORGANIZACAO — e nunca o SOURCE_ID.
    A identidade da fonte desce pelo pedido, como em todas as fases desta casa.

        URL NAO E SOURCE_ID.

    `teto` e o numero maximo de videos ADQUIRIDOS nesta corrida. Ele existe
    porque o custo desta aquisicao e BANDA e CORTESIA, e nao dolares: pedir a
    pagina inteira de uma organizacao com trinta videos nao e o mesmo acto que
    pedir tres.
    """
    cartoes, contexto = posts_com_video(pagina_url=pagina_url, run_id=run_id,
                                       country_scope=country_scope, teto=teto,
                                       transporte=transporte)
    pedidos = list(contexto['PEDIDOS'])
    envelopes = []
    for cartao in cartoes:
        _adquirir_um(cartao, run_id=run_id, country_scope=country_scope,
                    transporte=transporte, egresso=egresso,
                    pedidos=pedidos, envelopes=envelopes)
    if medida is not None:
        medida.update({'IMPLEMENTACAO': 'coleta/adaptador_linkedin.video_da_pagina_publica',
                       'REQUESTS': len(pedidos),
                       'VIDEOS_ADQUIRIDOS': len(envelopes),
                       'CARTOES_COM_VIDEO': contexto['CARTOES_COM_VIDEO'],
                       'COST_STATE': 'FREE_ROUTE_BY_OWNER_DECISION',
                       'ACTUAL_COST_USD': 0.0,
                       'OWNER_AUTHORIZED': 'SIM',
                       'PLATFORM_POLICY_STATUS': 'DISALLOWED',
                       'DECISAO_DO_DONO': DECISAO_DO_DONO,
                       'PEDIDOS': pedidos})
    return envelopes


def video_de_post_publico(*, post_url, run_id, country_scope='IT', transporte=None,
                           egresso=None, medida=None, **_):
    """A AQUISICAO DO VIDEO DE UMA PESSOA (D24), pela pagina PUBLICA do POST.

    PORQUE ESTA PORTA EXISTE, e nao a do perfil: medido, a pagina do PERFIL de
    uma pessoa responde 999 com `authwall`, e a pagina do POST dela responde
    200. A plataforma fecha a porta que fala da pessoa e deixa aberta a que
    fala da publicacao — e esta casa obedece ao que a plataforma serve, sem
    contornar nada.

    A cadeia e a MESMA da D23, e isso e o ponto:
    a pagina do post entrega o cartao, `cartoes_com_video` monta-o, e o
    `_adquirir_um` faz o resto — MP4, legenda, texto do autor, JSON-LD.

    Um post SEM video e RESULTADO, e nao falha: o objeto sai sem bytes, com o
    texto do autor e o `PUBLISHED_AT` que a propria pagina declara.
    """
    url, ident = _alvo_e_post_publico(post_url)
    pedidos = [{'TYPE': 'ROUTE', 'TARGET': http.host_de(url), 'URL': url}]
    envelopes = []
    # ⚠️ O PORTAO PRECISA DA DECISAO DO DONO PARA ABRIR ESTE CAMINHO — e ela
    # vai NOMEADA, como na D23. O `robots.txt` do LinkedIn barra o caminho; o
    # que o portao aceita nao e «uma excecao», e a excecao COM NOME: D24,
    # `DECISOES-DONO-2026-09-23.md`, escrita e assumida pelo dono.
    with http.autorizacao_do_dono(ROTA_POST_PUBLICO, HOSTS_DA_AQUISICAO,
                                 decisao=AUTORIZACAO_ESCRITA_D24,
                                 plataforma=PLATAFORMA):
        corpo = _buscar_texto(url, transporte)
    cartoes = cartoes_com_video(corpo)
    tem_video = bool(cartoes)
    if not cartoes:
        # Sem `data-sources` na pagina, o cartao monta-se do que a pagina TEM:
        # a identidade vem do proprio endereco pedido, e nao de uma posicao.
        cartoes = [{
            'ACTIVITY_ID': ident, 'ACTIVITY_ID_DO_URN': None,
            'ACTIVITY_ID_DO_URL': ident, 'POST_URL': url,
            'LIGACAO': 'IDENTIDADE_NO_ENDERECO_PEDIDO',
            'VIDEO_RENDICOES': [], 'DATA_SOURCES_UNPARSABLE': False,
            'CAPTION_URL': None, 'ASSET_URN': None, 'DECLARED_LANGUAGE': None,
            'POSTER_URL': None, 'ASPECT_RATIO': None,
        }]
    for cartao in cartoes:
        _adquirir_um(cartao, run_id=run_id, country_scope=country_scope,
                     transporte=transporte, egresso=egresso,
                     pedidos=pedidos, envelopes=envelopes,
                     decisao=DECISAO_DA_PESSOA)
    if medida is not None:
        medida.update({
            'IMPLEMENTACAO': 'coleta/adaptador_linkedin.video_de_post_publico',
            'REQUESTS': len(pedidos), 'POST_SEM_VIDEO': not tem_video,
            'POST_URL_PEDIDO': url, 'ACTIVITY_ID_DO_ENDERECO': ident,
            'ENVELOPES': len(envelopes),
            'COST_STATE': 'FREE_ROUTE_BY_OWNER_DECISION', 'ACTUAL_COST_USD': 0.0,
            'OWNER_AUTHORIZED': 'SIM', 'PLATFORM_POLICY_STATUS': 'DISALLOWED',
            'DECISAO_DO_DONO': DECISAO_DO_DONO_D24,
            'LIMITE': LIMITE_DA_PESSOA, 'PEDIDOS': pedidos})
    return envelopes


def _adquirir_um(cartao, *, run_id, country_scope, transporte, egresso, pedidos, envelopes,
                 decisao=None):
    """Um cartao -> um envelope. Aquisicao dos bytes, texto e prova.

    `decisao` e o que MUDA quando o alvo e uma PESSOA (D24): o nome da decisao,
    a rota, o executor e o limite. Ausente, tudo fica como estava — e e por isso
    que a rota de ORGANIZACAO (D23) nao muda por causa desta porta.
    """
    dec = decisao or {}
    nome_decisao = dec.get('DECISAO', DECISAO_DO_DONO)
    ref_decisao = dec.get('REF', DECISAO_DO_DONO_REF)
    autorizacao = dec.get('AUTORIZACAO', AUTORIZACAO_ESCRITA)
    rota_pagina = dec.get('ROTA_PAGINA', ROTA_PAGINA_PUBLICA)
    rota_bytes = dec.get('ROTA_BYTES', ROTA_VIDEO_BYTES)
    rota_legenda = dec.get('ROTA_LEGENDA', ROTA_LEGENDA_NATIVA)
    executor = dec.get('EXECUTOR', 'adaptador_linkedin.video_da_pagina_publica')
    limite = dec.get('LIMITE')
    ident = cartao.get('ACTIVITY_ID')
    url_do_post = _url_do_post(cartao)
    raw = {
        'PLATFORM': PLATAFORMA,
        'PAGE_URL': cartao.get('POST_URL') or None,
        'POST_URL': url_do_post,
        'ACTIVITY_ID': ident,
        'ACTIVITY_ID_DO_URN': cartao.get('ACTIVITY_ID_DO_URN'),
        'ACTIVITY_ID_DO_URL': cartao.get('ACTIVITY_ID_DO_URL'),
        'CARD_LINK': cartao.get('LIGACAO'),
        'ASSET_URN': cartao.get('ASSET_URN'),
        'VIDEO_RENDITIONS_DECLARED': cartao.get('VIDEO_RENDICOES') or [],
        'DECLARED_LANGUAGE': cartao.get('DECLARED_LANGUAGE'),
        'DECLARED_LANGUAGE_BASIS': ('DECLARED_BY_PLATFORM:data-language da etiqueta '
                                    '<video> — nunca inferida do texto'),
        'POSTER_URL': cartao.get('POSTER_URL'),
        'ASPECT_RATIO': cartao.get('ASPECT_RATIO'),
        'OWNER_AUTHORIZED': 'SIM',
        'PLATFORM_POLICY_STATUS': 'DISALLOWED',
        'DECISAO_DO_DONO': nome_decisao,
        'DECISAO_DO_DONO_REF': ref_decisao,
        'EGRESS_MEASURED': egresso,
        'URL_EXPIRY_OBSERVED': None,
    }
    # ── 2 · a pagina do POST: identidade temporal e texto do autor ─────────
    prosa = {}
    if url_do_post:
        with http.autorizacao_do_dono(rota_pagina, HOSTS_DA_AQUISICAO,
                                     decisao=autorizacao, plataforma=PLATAFORMA):
            pedidos.append({'TYPE': 'ROUTE', 'TARGET': http.host_de(url_do_post),
                            'URL': url_do_post})
            try:
                prosa = video_do_post(_buscar_texto(url_do_post, transporte))
            except Exception as e:                                    # noqa: BLE001
                raw['POST_PAGE_ERROR'] = '%s: %s' % (type(e).__name__, str(e)[:200])
    # ── A CONTRAPROVA DA IDENTIDADE ───────────────────────────────────────
    # ⚠️ A LIGACAO DO CARTAO PODE SER POSICIONAL (ver `cartoes_com_video`), e
    # uma ligacao posicional merece contraprova. Ela existe, e e barata: o
    # JSON-LD do post declara `contentUrl`, e esse endereco carrega o MESMO
    # identificador de midia que o cartao declarou no `asset`.
    #
    #     DOIS IDENTIFICADORES INDEPENDENTES QUE CONCORDAM PROVAM A LIGACAO.
    #     UM SO, E UMA POSICAO NA PAGINA.
    #
    # Sem `contentUrl` nao se inventa concordancia: o campo diz que nao houve
    # o que conferir, e isso e diferente de ter conferido e divergido.
    if prosa.get('CONTENT_URL') and cartao.get('ASSET_URN'):
        _asset = str(cartao['ASSET_URN']).rsplit(':', 1)[-1]
        raw['IDENTITY_CROSSCHECK'] = (
            'CONFIRMADA_PELO_ASSET_DO_JSON_LD' if _asset in prosa['CONTENT_URL']
            else 'DIVERGE_DO_ASSET_DO_JSON_LD')
    elif prosa.get('CONTENT_URL'):
        raw['IDENTITY_CROSSCHECK'] = 'SEM_ASSET_DECLARADO_PARA_CONFERIR'
    else:
        raw['IDENTITY_CROSSCHECK'] = 'SEM_JSON_LD_NA_PAGINA_DO_POST'
    raw.update({k: v for k, v in prosa.items() if k != 'CONTENT_URL'})
    # ── 3 · os BYTES do video ─────────────────────────────────────────────
    rendicao, porque = _rendicao_escolhida(cartao.get('VIDEO_RENDICOES') or [])
    unidades = []
    if prosa.get('DESCRIPTION'):
        unidades.append(pv.unidade_de_texto(
            texto=prosa['DESCRIPTION'], kind=pv.AUTHOR_TEXT,
            kind_basis=pv.DECLARED_BY_PROVIDER, relation=pv.ORIGINAL,
            language=cartao.get('DECLARED_LANGUAGE'),
            unit_id='%s:AUTHOR' % (ident or 'sem-id'),
            # ⚠️ O METODO VEM DO DONO DO VOCABULARIO, E NAO DE UMA FRASE MINHA.
            # A primeira versao escrevia 'PLATAFORMA_PUBLICOU_NO_JSON_LD' — um
            # nome inventado, fora da lista fechada de `regras/proveniencia.py`.
            # O ingresso recusou as DUAS observacoes com
            # `INGRESS_CONTRATO_QUEBRADO`, e a medicao foi essa que o apanhou.
            #
            #     UM NOME INVENTADO NUM CAMPO DE VOCABULARIO FECHADO
            #     NAO E UM DETALHE DE ESTILO: E UMA OBSERVACAO QUE NAO ENTRA.
            derivation_method=pv.LIDO_DO_CAMPO,
            tool='adaptador_linkedin.video_do_post'))
    if rendicao:
        raw['RENDITION_CHOSEN'] = rendicao['SRC']
        raw['RENDITION_CHOSEN_BY'] = porque
        raw['RENDITION_CHOSEN_BITRATE'] = rendicao.get('BITRATE')
        try:
            with http.autorizacao_do_dono(rota_bytes, HOSTS_DA_AQUISICAO,
                                         decisao=autorizacao, plataforma=PLATAFORMA):
                pedidos.append({'TYPE': 'ROUTE', 'TARGET': http.host_de(rendicao['SRC']),
                                'URL': rendicao['SRC']})
                corpo, meta = http.buscar_bytes(rendicao['SRC'], aceitar='video/mp4')
            ficha = _guardar_bytes(corpo, 'video', ident or 'sem-id', 'mp4')
            raw.update({'VIDEO_STORAGE_LOCATION': ficha['RELATIVO'],
                        'STORAGE_LOCATION': ficha['RELATIVO'],
                        'CONTENT_TYPE': meta.get('CONTENT_TYPE') or 'video/mp4',
                        'VIDEO_SHA256': ficha['SHA256'],
                        'VIDEO_BYTES': ficha['BYTES'],
                        'VIDEO_BYTES_ACQUIRED': True,
                        'VIDEO_URL_SERVED': meta.get('URL'),
                        'VIDEO_CONTENT_TYPE_SERVED': meta.get('CONTENT_TYPE')})
        except Exception as e:                                        # noqa: BLE001
            raw['VIDEO_BYTES_ACQUIRED'] = False
            raw['VIDEO_ERROR'] = '%s: %s' % (type(e).__name__, str(e)[:200])
    else:
        raw['VIDEO_BYTES_ACQUIRED'] = False
        raw['VIDEO_ERROR'] = 'NENHUMA_RENDICAO_MP4_DECLARADA'

    # ── 4 · a LEGENDA, e a especie do texto ───────────────────────────────
    legenda = {}
    if cartao.get('CAPTION_URL'):
        try:
            with http.autorizacao_do_dono(rota_legenda, HOSTS_DA_AQUISICAO,
                                         decisao=autorizacao, plataforma=PLATAFORMA):
                pedidos.append({'TYPE': 'ROUTE',
                                'TARGET': http.host_de(cartao['CAPTION_URL']),
                                'URL': cartao['CAPTION_URL']})
                texto, ficha = legenda_do_video(caption_url=cartao['CAPTION_URL'],
                                                run_id=run_id, nome_base=ident or 'legenda',
                                                transporte=transporte)
            legenda = dict(ficha)
            raw.update({'CAPTION_URL': cartao['CAPTION_URL'],
                        'CAPTION_FORMAT_DECLARED_BY_URL': ficha['FORMAT_DECLARED_BY_URL'],
                        'CAPTION_FORMAT_MEASURED': ficha['FORMAT_MEASURED_IN_BYTES'],
                        'CAPTION_BYTES': ficha['BYTES'],
                        'CAPTION_SHA256': ficha['SHA256'],
                        'CAPTION_STORAGE_LOCATION': ficha['RELATIVO'],
                        'CAPTION_CONTENT_TYPE': ficha['CONTENT_TYPE_SERVED'],
                        'CAPTION_FORMAT_DIVERGENCE': ficha['DIVERGE'],
                        'NATIVE_CAPTION': texto,
                        'DERIVED_TEXT': 'NATIVE_CAPTION',
                        'DERIVED_TEXT_BASIS': ('ASR de outra casa, declarada pela '
                                               'plataforma — mais barata, nao melhor')})
            unidades.append(pv.unidade_de_texto(
                texto=texto, kind=pv.NATIVE_CAPTION,
                kind_basis=pv.DECLARED_BY_PROVIDER, relation=pv.ORIGINAL,
                language=cartao.get('DECLARED_LANGUAGE'),
                unit_id='%s:NATIVE_CAPTION' % (ident or 'sem-id'),
                # A legenda automatica E o ASR do PROVEDOR: foi ele que ouviu a
                # fala e escreveu o texto. `PROVIDER_ASR` e o nome que o dono do
                # vocabulario ja tinha para exactamente isto.
                #
                #     ASR DE OUTRA CASA TEM NOME PROPRIO — E NAO E `ASR_LOCAL`.
                derivation_method=pv.ASR_DO_PROVEDOR,
                tool='adaptador_linkedin.legenda_do_video'))
        except Exception as e:                                        # noqa: BLE001
            raw['CAPTION_ERROR'] = '%s: %s' % (type(e).__name__, str(e)[:200])
            raw['DERIVED_TEXT'] = 'CAPTION_FALHOU_ASR_REQUIRED'
    else:
        raw.update({'CAPTION_URL': None,
                    'CAPTION_FORMAT_DECLARED_BY_URL': None,
                    'NATIVE_CAPTION': None,
                    'DERIVED_TEXT': 'ASR_REQUIRED',
                    'DERIVED_TEXT_BASIS': ('o video nao declara faixa de legenda. '
                                           'O texto teria de vir do dono unico do '
                                           'ASR: %s' % DONO_DO_ASR)})

    # ── A LINGUA DECLARADA != A LINGUA DO TEXTO, E ISSO MEDIU-SE ─────────
    # ⚠️ MEDIDO no canario: a etiqueta `<video>` das paginas do `gruppocaviro`
    # declara `data-language="en"` E SERVE LEGENDA EM ITALIANO — o texto das
    # legendas e dos posts e italiano legivel.
    #
    # A resposta continua a ser a declarada, e nao a que eu acho: a lei desta
    # casa e «LINGUA DECLARADA, NUNCA INFERIDA DO TEXTO», e inferir `it` do
    # texto seria exactamente o que ela proibe.
    #
    #     MANTER O `en` NÃO É UM ERRO: É O CAMPO A DIZER A VERDADE QUE A
    #     PLATAFORMA DECLARA. O QUE SERIA ERRO E ESCREVER `it` POR CONTA PRÓPRIA.
    #
    # O que se faz é guardar a divergencia AO LADO, para que a Inteligencia
    # saiba que este campo precisa de companhia antes de decidir lingua.
    raw['DECLARED_LANGUAGE_NOTE'] = (
        'a plataforma DECLARA esta lingua no atributo data-language da etiqueta '
        '<video>; o texto da legenda e o texto do autor sao servidos na lingua '
        'da publicacao. Medido no canario D23: declarado `en`, texto italiano. '
        'O campo guarda o que a plataforma declarou — inferir do texto seria '
        'fabricar.')
    raw['TEXT_UNITS_MADE'] = [u['TEXT_KIND'] for u in unidades]
    ref = env.guardar_raw(PLATAFORMA, 'post-%s' % (ident or url_do_post),
                          json.dumps(raw, ensure_ascii=False, indent=1, default=str))
    envelope = env.envelope(
        platform=PLATAFORMA,
        native_id=ident or env.DESCONHECIDO,
        url=url_do_post or env.DESCONHECIDO,
        content_type='VIDEO',
        route=rota_bytes,
        executor=executor,
        run_id=run_id, country_scope=country_scope,
        source_account=cartao.get('POST_URL') or None,
        published_at=prosa.get('PUBLISHED_AT'),
        language=cartao.get('DECLARED_LANGUAGE'),
        source_location=None,
        cost_usd=0.0,
        raw_reference=ref['PATH'],
        title=prosa.get('NAME') or prosa.get('HEADLINE'),
        text=None,
        text_units=unidades or None,
        raw=raw)
    envelope['ACQUISITION_TIER'] = FREE
    envelope['FIELD_ORIGIN_TIER'] = FREE
    envelope['OWNER_AUTHORIZED'] = 'SIM'
    envelope['PLATFORM_POLICY_STATUS'] = 'DISALLOWED'
    envelope['DECISAO_DO_DONO'] = nome_decisao
    if limite:
        envelope['LIMITE'] = limite
    envelope['RAW_SHA256'] = ref['SHA256']
    envelope['EGRESS_MEASURED'] = egresso
    envelopes.append(envelope)


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
             nota='SRT AUTOMATICA: ASR de outra casa, mais barata e nao melhor. ZERO '
                  'ocorrencias em 472 posts de rota paga — nenhum fornecedor a entrega')
reg.registar(PLATAFORMA, 'linkedin.comments', adaptador=NOME,
             nota='a CONTAGEM vem na listagem (335 em 95 de 472 posts); o TEXTO nao vem '
                  '(0 de 472) e e evento cobrado a parte. COUNT != TEXT')
reg.registar(PLATAFORMA, 'linkedin.documents', adaptador=NOME,
             nota='carrossel em PDF. Os ENDERECOS foram observados em 20 de 472 no bruto '
                  'preservado — PDF, manifesto e transcriptManifestUrl. Os BYTES nunca '
                  'foram pedidos, e as URLs preservadas expiraram')


# ══════════════════════════════════════════════════════════════════════════
# D23 · AS TRES ROTAS DO VIDEO DE ORGANIZACAO
# ══════════════════════════════════════════════════════════════════════════
def pronto_para_video_publico(**_):
    """→ (consigo?, estado). Zero rede, zero dólar, zero credencial.

    Nao falta chave nem conta nenhuma: esta aquisicao le uma pagina publica.
    O que ela EXIGE nao e credencial — e a decisao do dono, e ela ja esta
    escrita (D23) e viaja em cada objeto que sai daqui.
    """
    return True, 'NO_CREDENTIAL_REQUIRED · OWNER_AUTHORIZED=SIM (%s)' % DECISAO_DO_DONO


reg.registar(PLATAFORMA, 'linkedin.org.posts', adaptador=NOME,
             pronto=pronto_para_video_publico, rota=posts_com_video,
             nota='D23: a pagina PUBLICA da organizacao serve os cartoes das '
                  'publicacoes recentes — activity id, endereco canonico, texto do '
                  'autor e a etiqueta <video data-sources> quando o post tem video. '
                  'MEDIDO em 18 organizacoes italianas: 10 a 18 activity ids cada, 9 '
                  'com video. Teto conhecido: PROFUNDIDADE — nao ha endereco de pagina '
                  'seguinte. Plataforma PROIBE (robots.txt); dono autorizou (D23).')
reg.registar(PLATAFORMA, 'linkedin.org.video', adaptador=NOME,
             pronto=pronto_para_video_publico, rota=video_da_pagina_publica,
             nota='D23: MP4 PROGRESSIVO servido a convidado pelo CDN, HTTP 206 e '
                  '`video/mp4` medidos em 7 464 653 e 14 687 975 bytes. Endereco com '
                  '`e=2147483647` = LONG_LIVED_OBSERVED — observacao, nao garantia. '
                  'A rendicao escolhida e a MAIS LEVE, e o motivo viaja no objeto. '
                  'Plataforma PROIBE; dono autorizou (D23).')
reg.registar(PLATAFORMA, 'linkedin.org.caption', adaptador=NOME,
             pronto=pronto_para_video_publico, rota=legenda_do_video,
             nota='D23: a faixa de legenda que a publicacao declara em '
                  '`data-captions-url`. MEDIDO: SRT e WebVTT reais, 529 a 3 587 bytes, '
                  'texto legivel; o endereco declara o formato e os BYTES confirmam — '
                  'as duas guardam-se. E AUTOMATICA: ASR de outra casa, mais barata e '
                  'nao melhor, e por isso a especie viaja declarada. NAO EXISTE EM TODO '
                  'VIDEO, e ausencia de legenda e resultado. Plataforma PROIBE; dono '
                  'autorizou (D23).')
