#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ADAPTADOR DO YOUTUBE — onde esta quase todo o dinheiro, e o inverso de todos.

O YouTube e a unica das cinco plataformas onde DESCOBRIR e livre e o que barra
e o BYTE DA MIDIA. Nas outras e ao contrario: a listagem pede sessao e o objeto
individual responde a convidado.

    96,2% DO GASTO MEDIDO COM ROTA PAGA ESTA AQUI — e as quatro capacidades que
    os actors vendem sairam de graca neste contentor, sem login e sem cookies.

Isto NAO autoriza desligar nada. Desligar actor e a missao seguinte, e depende
de politica que ninguem levantou: o `robots.txt` do YouTube barra `/youtubei/`,
`/results`, `/comment` e `/get_video`, que sao exatamente os caminhos por onde
o `yt-dlp` passa. `ROBOTS_STATUS = RESTRICTED` NAO E UM PARECER JURIDICO — e um
dos cinco documentos, e o unico que foi lido.

O QUE ESTE FICHEIRO CONTEM
---------------------------
As quatro rotas oficiais que ja viviam dentro do roteador. Nao foram
reescritas: foram MUDADAS DE SITIO, para que o roteador deixe de conhecer o
nome das plataformas. O corpo e o mesmo, linha por linha.
"""
import os
import re
import sys
import urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import _gavetas  # noqa: E402,F401
import scrap_http as http     # noqa: E402
import scrap_fornecedores as forn  # noqa: E402
import scrap_registo as reg   # noqa: E402

NOME = 'adaptador_youtube'
PLATAFORMA = 'YOUTUBE'

#: O estado que a API declarou vive no transporte, para que roteador e
#: adaptador falem dele sem se importarem um ao outro.
_EstadoDaApi = http.EstadoDaApi


# ══════════════════════════════════════════════════════════════════════════
# O TRADUTOR — porque «nao tenho chave» nao pode chegar como «erro desconhecido»
# ══════════════════════════════════════════════════════════════════════════
# Medido nesta missao, antes de mexer: com a chave ausente, `social_rotas`
# devolvia `UNKNOWN_ERROR` para `SEARCH_KEYWORD`. A mensagem dizia, por extenso,
# «Isto e CREDENTIAL_MISSING» — e o ESTADO dizia outra coisa.
#
#     UMA MENSAGEM QUE SABE E UM ESTADO QUE NAO SABE VALEM MENOS QUE NENHUM
#     DOS DOIS: quem le por maquina le o estado.
#
# O roteador nao pode aprender as excecoes do YouTube — ele deixou de conhecer
# plataformas na C1 e nao volta atras. Entao a traducao acontece AQUI, no dono
# da semantica, e sobe pelo carregador de estado que o transporte ja tem.
#
# As tres sao coisas diferentes e nao se colapsam:
#
#     CREDENTIAL_MISSING   nao ha chave no ambiente
#     QUOTA_EXHAUSTED      a quota DELES acabou
#     BUDGET_EXHAUSTED     o teto NOSSO desta execucao acabou
#
# A terceira e nossa decisao, nao limite da plataforma. Chamar-lhe quota seria
# culpar o Google por uma trava que esta casa pos.
def _traduzido(fn):
    """Chama a rota e converte a recusa em estado canonico, nunca em surpresa."""
    def dentro(**kw):
        import youtube_oficial as yt
        try:
            return fn(**kw)
        except yt.SemCredencial as e:
            raise _EstadoDaApi({'STATE': 'CREDENTIAL_MISSING',
                                'NATIVE_REASON': 'YOUTUBE_DATA_API_KEY ausente',
                                'RECOVERY_ACTION': 'HUMAN_PROVISION_CREDENTIAL'}) from e
        except yt.QuotaEstourada as e:
            raise _EstadoDaApi({'STATE': 'QUOTA_EXHAUSTED',
                                'NATIVE_REASON': 'quota do projeto no YouTube',
                                'RECOVERY_ACTION': 'WAIT'}) from e
        except yt.TetoDaExecucao as e:
            raise _EstadoDaApi({'STATE': 'BUDGET_EXHAUSTED',
                                'NATIVE_REASON': 'teto desta execucao, posto por nos',
                                'RECOVERY_ACTION': 'NO_RETRY'}) from e
        except urllib.error.HTTPError as e:
            # A API DIZ A RAZAO NO CORPO, E O CODIGO HTTP E O ULTIMO RECURSO.
            # `403` sozinho e tres coisas ao mesmo tempo: quota acabada,
            # comentario desligado e chave barrada por IP. O corpo distingue-as,
            # `youtube_oficial.estado_do_erro` ja sabe le-lo, e quem subia por
            # aqui perdia isso pelo caminho — o roteador via um HTTPError nu e
            # classificava so pelo numero.
            #
            #     PERDER A RAZAO DECLARADA E ESCOLHER ADIVINHAR TENDO A RESPOSTA.
            estado, razao = yt.estado_do_erro(e)
            raise _EstadoDaApi({'STATE': estado, 'NATIVE_REASON': razao}) from e
    dentro.__name__ = fn.__name__
    dentro.__doc__ = fn.__doc__
    return dentro


# ── POR QUE A SESSAO ATRAVESSA ────────────────────────────────────────────
# `youtube_oficial.Sessao` aceita transporte injetado, e o ficheiro dele diz
# porque: «um teste que depende da internet nao roda quando mais se precisa».
# Mas a sessao morria AQUI — as quatro rotas engoliam-na em `**_` e abriam uma
# nova por dentro. O resultado e que quota estourada, video apagado e
# comentario desativado so podiam ser exercidos contra a API de verdade, que e
# exatamente quando nao se quer exercer nenhum dos tres.
#
#     UMA COSTURA QUE PARA A MEIO DO CAMINHO NAO E UMA COSTURA.
#
# A sessao passa a atravessar ate ao dono. Em producao ninguem a passa, e cada
# chamada abre a sua — o comportamento nao mudou.
@_traduzido
def youtube_buscar(*, termo, run_id, country_scope, limit=25, sessao=None, **_):
    import youtube_oficial as yt
    objs, _s = yt.buscar(termo=termo, run_id=run_id, country_scope=country_scope,
                         limit=limit, regiao=country_scope, idioma='it',
                         sessao=sessao)
    return objs


@_traduzido
def youtube_uploads(*, channel_id, run_id, country_scope, limit=25, conhecidos=(),
                    sessao=None, **_):
    import youtube_oficial as yt
    objs, _s, _rel = yt.uploads_recentes(
        channel_id=channel_id, run_id=run_id, country_scope=country_scope,
        limit=limit, conhecidos=conhecidos, sessao=sessao)
    return objs


@_traduzido
def youtube_metadata(*, video_ids, run_id, country_scope, sessao=None, **_):
    import youtube_oficial as yt
    objs, _s, _rel = yt.metadata(video_ids=video_ids, run_id=run_id,
                                 country_scope=country_scope, sessao=sessao)
    return objs


@_traduzido
def youtube_comentarios(*, video_id, run_id, country_scope, limite_threads=100,
                        sessao=None, **_):
    import youtube_oficial as yt
    objs, _s, rel = yt.comentarios(video_id=video_id, run_id=run_id,
                                   country_scope=country_scope,
                                   limite_threads=limite_threads, sessao=sessao)
    # Comentário desativado NÃO é coleta vazia: é um fato sobre o vídeo, e sobe
    # como estado próprio para não virar ZERO_RESULTS no registro.
    if rel.get('STATE') not in (None, 'OK', 'ZERO_RESULTS'):
        raise http.RotaBloqueada('%s (razão nativa: %s)' % (rel['STATE'], rel.get('NATIVE_REASON'))
                            ) if rel['STATE'] == 'BLOCKED' else _EstadoDaApi(rel)
    return objs




# ══════════════════════════════════════════════════════════════════════════
# RESOLVER A CONTA — o degrau que faltava para a comunicacao publica
# ══════════════════════════════════════════════════════════════════════════
# O lote congelado guarda ENDERECO de conta, e `playlistItems.list` precisa de
# `channelId`. Enquanto a rota era paga, o ator engolia a URL e resolvia por
# dentro. A rota oficial nao engole: ela pergunta pelo id.
#
# Medido nas sete contas de YouTube do lote, e sao QUATRO formas de endereco:
#
#     /@handle          resolve por `channels.list?forHandle`     1 unidade
#     /user/NOME        resolve por `channels.list?forUsername`   1 unidade
#     /channel/UC...    o id ESTA na URL                          0 unidades
#     /c/NOME e /NOME   NAO TEM ROTA OFICIAL GRATUITA
#
# A quarta forma e a que importa declarar bem. O caminho «facil» seria mandar o
# nome para `search.list` e ficar com o primeiro resultado. Duas coisas erradas
# nisso, e a segunda e pior que a primeira:
#
#     1. custa uma das 100 buscas do dia para resolver UM canal;
#     2. o primeiro resultado da busca NAO E o canal — e o mais bem ranqueado
#        para aquele texto. Aceita-lo seria FABRICAR IDENTIDADE.
#
#     UM PALPITE COM ID VALIDO E PIOR QUE UM ESTADO HONESTO: o palpite entra no
#     acervo com a cara de facto e ninguem volta a perguntar.
#
# Por isso a quarta forma sai `CHANNEL_IDENTITY_UNRESOLVED`, e a capacidade
# inteira esta declarada PARTIAL — nao PROVEN. Ela resolve tres das quatro.
URL_CANAL = re.compile(
    r'youtube\.com/(?:(?P<tipo>channel|user|c)/)?(?P<nome>@?[^/?#]+)', re.I)

RESOLVIDO = 'OK'
NAO_RESOLVIDO = 'CHANNEL_IDENTITY_UNRESOLVED'


@_traduzido
def youtube_resolver_canal(*, account_url, run_id, country_scope='IT',
                           sessao=None, cache=None, **_):
    """Endereco de conta -> (objetos, trace). Um objeto, ou nenhum com estado.

    NUNCA levanta por endereco que nao resolve: nao resolver e um facto sobre a
    forma do endereco, nao uma falha da rota.
    """
    import youtube_oficial as yt
    m = URL_CANAL.search(account_url or '')
    if not m:
        return [], {'STATE': NAO_RESOLVIDO, 'WHY': 'nao parece um endereco de canal',
                    'ACCOUNT_URL': account_url}
    tipo = (m.group('tipo') or '').lower()
    nome = m.group('nome')
    s = sessao or yt.Sessao()

    if tipo == 'channel' and nome.startswith('UC'):
        # O id esta na propria URL. Zero unidades, e zero duvida.
        return [{'CHANNEL_ID': nome, 'ACCOUNT_URL': account_url,
                 'RESOLVED_BY': 'URL', 'QUOTA_UNITS': 0}], {'STATE': RESOLVIDO}

    if nome.startswith('@') or tipo == '':
        # Um nome nu depois do dominio pode ser handle sem o arroba. Tentar como
        # handle custa 1 unidade e NAO inventa nada: ou o handle existe, ou nao.
        try:
            cid, _pl, proc = yt.resolver_handle(handle=nome, sessao=s, cache=cache)
            return [{'CHANNEL_ID': cid, 'ACCOUNT_URL': account_url,
                     'RESOLVED_BY': 'forHandle', 'QUOTA_UNITS': 1,
                     'CHANNEL_TITLE': proc.get('CHANNEL_TITLE')}], {'STATE': RESOLVIDO}
        except yt.CanalNaoEncontrado:
            return [], {'STATE': NAO_RESOLVIDO,
                        'WHY': 'nao e handle; e /c/ ou nome antigo sem rota oficial',
                        'ACCOUNT_URL': account_url}

    if tipo == 'user':
        d = s.chamar('channels.list', {'part': 'contentDetails,snippet',
                                       'forUsername': nome})
        itens = d.get('items') or []
        if itens and itens[0].get('id'):
            return [{'CHANNEL_ID': itens[0]['id'], 'ACCOUNT_URL': account_url,
                     'RESOLVED_BY': 'forUsername', 'QUOTA_UNITS': 1,
                     'CHANNEL_TITLE': (itens[0].get('snippet') or {}).get('title')}], {
                        'STATE': RESOLVIDO}
        return [], {'STATE': NAO_RESOLVIDO,
                    'WHY': 'forUsername nao devolveu nada — nome legado aposentado',
                    'ACCOUNT_URL': account_url}

    # `/c/NOME`: nao ha rota oficial gratuita, e a busca nao e resolucao.
    return [], {'STATE': NAO_RESOLVIDO,
                'WHY': 'endereco /c/ nao tem resolvedor oficial; search.list daria '
                       'ranking, nao identidade',
                'ACCOUNT_URL': account_url}


def resolver_canal(*, account_url, run_id, country_scope='IT', **kw):
    """O papel `executa`: devolve (objetos, trace) ja no vocabulario do SCRAP."""
    objetos, estado = youtube_resolver_canal(
        account_url=account_url, run_id=run_id, country_scope=country_scope, **kw)
    p = forn.Percurso('youtube.channel.resolve', pedido=forn.API_OFICIAL)
    p.degrau(forn.API_OFICIAL, estado.get('STATE'),
             estado.get('WHY') or (objetos[0].get('RESOLVED_BY') if objetos else None))
    trace = p.selar(resultado=estado.get('STATE'))
    trace['ACCOUNT_URL'] = account_url
    trace['QUOTA_UNITS'] = sum(o.get('QUOTA_UNITS', 0) for o in objetos)
    trace['COST_USD'] = 0.0
    return objetos, trace


# ══════════════════════════════════════════════════════════════════════════
# A SONDA — de graca, e sem nunca tocar no valor
# ══════════════════════════════════════════════════════════════════════════
# `CHECK` pergunta «consigo chegar la agora, sem gastar?». Para uma rota oficial
# a resposta depende de uma coisa que se le em memoria: a credencial esta no
# ambiente?
#
#     LER UMA VARIAVEL DE AMBIENTE NAO E COLETAR. Nao chama a API, nao gasta
#     quota, nao abre navegador e nao acorda a Apify.
#
# E o que sai daqui e um BOOLEANO e um ESTADO. Nunca o valor, nunca o tamanho,
# nunca um prefixo, nunca um hash. Um comprimento com prefixo e meio segredo, e
# meio segredo num log e um segredo num log.
#
#     A PROVA DE QUE A CHAVE SERVE E A CHAMADA FUNCIONAR. Nao e a impressao dela.
#
# E a distincao que o coordenador pediu, e ela importa: a chave EXISTE nos
# Secrets do GitHub. Se ela nao chegar ao processo, isso e `SECRET_WIRING_GAP` —
# um defeito de ligacao — e nao «nao temos credencial». Deste lado do processo
# as duas parecem iguais, entao esta sonda diz o que consegue provar:
# CREDENTIAL_MISSING NESTE AMBIENTE. Quem distingue e o workflow.
def pronto_para_api(**_):
    """→ (consigo?, estado). Zero chamadas, zero quota, zero dolar."""
    import youtube_oficial as yt
    return (bool(yt.chave()), 'CREDENTIAL_MISSING')


# ══════════════════════════════════════════════════════════════════════════
# O QUE ESTE ADAPTADOR DECLARA
# ══════════════════════════════════════════════════════════════════════════
reg.registar(PLATAFORMA, 'youtube.channel.resolve', adaptador=NOME,
             pronto=pronto_para_api, executa=resolver_canal,
             nota='tres das quatro formas de endereco; /c/ nao tem rota oficial')
reg.registar(PLATAFORMA, 'youtube.search', adaptador=NOME,
             pronto=pronto_para_api, rota=youtube_buscar,
             nota='API oficial search.list; `ytsearch` do yt-dlp esta ROUTE_NOT_ALLOWED na matriz')
reg.registar(PLATAFORMA, 'youtube.channel.discovery', adaptador=NOME,
             pronto=pronto_para_api, rota=youtube_uploads,
             nota='playlistItems.list; o feeds/videos.xml foi reprovado pelo portao')
reg.registar(PLATAFORMA, 'youtube.video.metadata', adaptador=NOME,
             pronto=pronto_para_api, rota=youtube_metadata,
             nota='videos.list custa 1 unidade de quota; oembed esta PROVED na matriz')
reg.registar(PLATAFORMA, 'youtube.comments', adaptador=NOME,
             pronto=pronto_para_api, rota=youtube_comentarios,
             nota='comentario desativado sobe como estado proprio, nunca como ZERO_RESULTS')
reg.registar(PLATAFORMA, 'youtube.native_caption', adaptador=NOME,
             nota='captions.download exige ser dono do video; a rota grata do yt-dlp nao esta classificada na matriz')
reg.registar(PLATAFORMA, 'youtube.media', adaptador=NOME,
             nota='403 de IP de datacenter; so o runner local pode fechar esta medicao')
