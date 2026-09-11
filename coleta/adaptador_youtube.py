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
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import _gavetas  # noqa: E402,F401
import scrap_http as http     # noqa: E402
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
    dentro.__name__ = fn.__name__
    dentro.__doc__ = fn.__doc__
    return dentro


@_traduzido
def youtube_buscar(*, termo, run_id, country_scope, limit=25, **_):
    import youtube_oficial as yt
    objs, _s = yt.buscar(termo=termo, run_id=run_id, country_scope=country_scope,
                         limit=limit, regiao=country_scope, idioma='it')
    return objs


@_traduzido
def youtube_uploads(*, channel_id, run_id, country_scope, limit=25, conhecidos=(), **_):
    import youtube_oficial as yt
    objs, _s, _rel = yt.uploads_recentes(
        channel_id=channel_id, run_id=run_id, country_scope=country_scope,
        limit=limit, conhecidos=conhecidos)
    return objs


@_traduzido
def youtube_metadata(*, video_ids, run_id, country_scope, **_):
    import youtube_oficial as yt
    objs, _s, _rel = yt.metadata(video_ids=video_ids, run_id=run_id,
                                 country_scope=country_scope)
    return objs


@_traduzido
def youtube_comentarios(*, video_id, run_id, country_scope, limite_threads=100, **_):
    import youtube_oficial as yt
    objs, _s, rel = yt.comentarios(video_id=video_id, run_id=run_id,
                                   country_scope=country_scope,
                                   limite_threads=limite_threads)
    # Comentário desativado NÃO é coleta vazia: é um fato sobre o vídeo, e sobe
    # como estado próprio para não virar ZERO_RESULTS no registro.
    if rel.get('STATE') not in (None, 'OK', 'ZERO_RESULTS'):
        raise http.RotaBloqueada('%s (razão nativa: %s)' % (rel['STATE'], rel.get('NATIVE_REASON'))
                            ) if rel['STATE'] == 'BLOCKED' else _EstadoDaApi(rel)
    return objs



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
