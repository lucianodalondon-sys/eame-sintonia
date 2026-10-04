#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O ADAPTER DO SCRAP PARA A PORTA CANÔNICA — traduz, e mais nada.

    python3 coleta/scrap_colheita.py --run-id=<RUN_ID> --fonte=<SOURCE_ID> <FASE>

POR QUE ESTE FICHEIRO EXISTE
-----------------------------
Medido nesta árvore, antes desta missão:

    orquestrador/orquestrador.py    é o dono único da orquestração
    coleta/scrap_executor.py        é o executor canônico do SCRAP
    ARESTA ENTRE OS DOIS            NÃO EXISTIA

O SCRAP tinha uma porta (`COLLECT`), tetos, guarda de gasto e preservação de
RAW — e ninguém a chamava a partir de um `COLLECTION_REQUEST`. O disparador ia
direto a `coleta/social_scrap.py`, que corria `COLLECT` e parava ali: o que a
corrida colheu nunca chegava a `coleta/ingresso.py`, e portanto nunca chegava à
admissão.

    MODULE EXISTS != EDGE EXISTS != FLOW EXISTS.

Este ficheiro é a aresta. Ele **não** é um segundo orquestrador: não decide que
missão correr, que fonte colher, que rota usar nem que ator chamar. Recebe uma
fase já decidida, chama `COLLECT` uma vez, e declara o que voltou.

    AS QUATRO TRADUÇÕES

      1  corre `scrap_executor.COLLECT` com o RUN_ID que o orquestrador cunhou
      2  lê o que a corrida devolveu — objetos e trace
      3  separa COLHEITA de SUPORTE pela espécie DECLARADA (COL-LAW-505)
      4  escreve o envelope no balcão, na língua da porta

    E O QUE ELE NÃO PODE FAZER

      cunhar RUN_ID · inventar SOURCE_ID · fabricar DOCUMENT_ID ·
      derivar RAW_OBSERVATION_ID · escolher ator, rota ou provider ·
      julgar tema, relevância ou qualidade

O `--run-id` É OBRIGATÓRIO, E O `--fonte` TAMBÉM
-------------------------------------------------
O primeiro, porque `RUN != PROVIDER RUN`: se este adapter cunhasse corrida, a
corrida do orquestrador e a da coleta eram duas, e o `raw_asset` ficaria ligado
a uma que o manifesto não conhece. É a mesma lei que `coleta/italy_executor.py`
já obedece.

O segundo, porque **o SCRAP não conhece `SOURCE_ID`**. Medido: o envelope
canônico de `coleta/social_envelope.py` tem `PLATFORM`, `SOURCE_ACCOUNT`,
`NATIVE_ID` e `URL` — e nenhum deles é uma fonte provada. Derivar `SOURCE_ID` de
qualquer um seria fabricar identidade.

    URL NÃO É SOURCE_ID. HANDLE NÃO É SOURCE_ID. PLATAFORMA NÃO É FONTE.

A identidade desce COM O PEDIDO, e nunca sobe da observação. Quem pede nomeia a
fonte do atlas; este adapter carimba-a e diz que a carimbou. Sem `--fonte`, ele
NÃO inventa: declara zero colheita, escreve porquê, e tudo o que a corrida
produziu sai como SUPORTE — que nunca atravessa a porta.

    O QUE NÃO SE DECLAROU NÃO ENTRA.

O BALCÃO NÃO É ARQUIVO
----------------------
`data/colheita/scrap/` é reescrito a cada corrida, e não acumulado — a mesma
escolha (e a mesma razão) de `coleta/italy_executor.py`: um balcão que guarda o
que já entregou entrega a colheita da corrida anterior outra vez.
"""
from __future__ import annotations

import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in ('coleta', 'leis', 'medidas', 'ferramentas', 'guarda', 'regras', ''):
    sys.path.insert(0, os.path.join(RAIZ, _p) if _p else RAIZ)

import fonte_do_atlas as fa                                       # noqa: E402  — quem diz se a fonte existe
import proveniencia as pv                                        # noqa: E402  — o dono do texto
import retorno_da_coleta as rc                                    # noqa: E402
import scrap_executor as sx                                       # noqa: E402

EXECUTOR_ID = 'scrap-colheita'
EXECUTOR_VERSION = 'adapter-v1'

BALCAO = os.path.join('data', 'colheita', 'scrap')
ENVELOPE = os.path.join(BALCAO, 'ENVELOPE.json')

#: As fases que este adapter sabe pedir ao `COLLECT`. O nome vem do disparador;
#: a plataforma, a capacidade e os argumentos vivem AQUI, em Python versionado.
#:
#:     UM DISPARADOR QUE ESCOLHE A CAPACIDADE ESCOLHE O QUE SE COLHE.
#:
#: E CADA FASE DIZ QUE ESPECIE DE RETORNO PRODUZ — quarta posicao, OBRIGATORIA,
#: sem valor por omissao. Chegou da LINKEDIN-OP-01, e e o campo que a
#: `leis/retorno_da_coleta.py` nasceu a dizer que faltava.
#:
#:     UMA ESPECIE POR OMISSAO E UMA DECISAO QUE NINGUEM TOMOU.
FASES = {
    'janela':         ('INSTAGRAM', 'instagram.profile.discovery', {'camada': 'tudo'}, rc.COLHEITA),
    'janela-perfis':  ('INSTAGRAM', 'instagram.profile.discovery', {'camada': 'perfis'}, rc.COLHEITA),
    'janela-objetos': ('INSTAGRAM', 'instagram.profile.discovery', {'camada': 'objetos'}, rc.COLHEITA),

    # ── A IDENTIDADE DO LINKEDIN, E POR QUE ELA E CATALOGO ─────────────────
    # Esta fase le o site DA PROPRIA ORGANIZACAO e traz de la o endereco que a
    # organizacao publicou. O que ela devolve nao e uma observacao da fonte: e
    # uma ENTIDADE DE ONDE SE PODE COLHER — a definicao literal de `CATALOG`.
    #
    #     IDENTITY != CONTENT. UM ENDERECO NAO E UMA PUBLICACAO.
    #     E `ENTRAM_NO_INGRESSO = (COLHEITA,)`: CATALOGO NAO ATRAVESSA A PORTA.
    #
    # O terminal canonico desta fase e o ENVELOPE, na lista de SUPORTE — e nao
    # a Sala de Espera. Empurra-la para a Admissao completava uma seta no
    # desenho e metia gasolina na mangueira da agua.
    'identidade-linkedin': ('LINKEDIN', 'linkedin.identity.discovery', {}, rc.CATALOG),
    # ── O CANARIO DA RELEASE V1 ────────────────────────────────────────────
    # As tres fases acima correm `instagram.profile.discovery`, que a
    # `scrap_capacidades.py` declara `PARTIAL` e `LOCAL/DATACENTER_BLOCKED`:
    # ela precisa de maquina residencial e nao corre de um datacenter. Medido,
    # nao presumido — e por isso a unica fase que o caminho canonico sabia
    # pedir era uma que este ambiente nao consegue executar.
    #
    #     UMA ARVORE QUE SO SABE PEDIR O QUE NAO CONSEGUE CORRER
    #     NAO SE CONSEGUE PROVAR A CORRER.
    #
    # `bluesky.author.incremental` e o oposto em todos os eixos que a escolha
    # do canario pesa: `PROVEN` com trial ao vivo citado, `ONLINE`, gratuita,
    # sem credencial, sem navegador autenticado e sem fornecedor pago. O
    # adaptador, o registo da rota e a linha da matriz ja existiam todos antes
    # desta missao — o que faltava era a fase que os pede.
    #
    #     ISTO NAO ABRE PLATAFORMA NENHUMA. A PLATAFORMA JA ESTAVA ABERTA;
    #     O QUE NAO EXISTIA ERA A ARESTA DO PEDIDO ATE ELA.
    'canario-bluesky': ('BLUESKY', 'bluesky.author.incremental', {'limit': 1},
                        rc.COLHEITA),

    # ── AS IRMAS DA MESMA FORMA DE INTEGRACAO ──────────────────────────────
    # `canario-bluesky` nao era um caso especial: era o PRIMEIRO caso de uma
    # forma. O registo do SCRAP declara-a, e ela le-se em tres campos:
    #
    #     ADAPTADOR = adaptador_aberto  ·  campo = ROTA  ·  ALVO = ONLINE
    #
    # Quatro capacidades PROVEN partilham exactamente esses tres, e o
    # `scrap_executor.CHECK` responde `CAN_COLLECT_NOW` a todas as quatro:
    # sem credencial, sem navegador autenticado, sem fornecedor pago. O que
    # faltava as outras tres nao era rota, adaptador nem prova — era a fase.
    #
    #     UMA CAPACIDADE PROVADA SEM FASE E UM MOTOR SEM CABO.
    #     A PROVA DIZ QUE ELA COLHE; A FASE E QUE DIZ QUE ALGUEM PODE PEDIR.
    #
    # ⚠️ PARTILHAR A FORMA NAO E PARTILHAR OS PARAMETROS, e por isso NENHUMA
    # destas linhas foi copiada da de cima. Medido nas assinaturas reais:
    #
    #     bluesky.author.incremental    (*, handle,          limit, run_id, ...)
    #     bluesky.account.discovery     (*, termo,           limit, run_id, ...)
    #     telegram.channel.incremental  (*, canal,                  run_id, ...)
    #     mastodon.hashtag.search       (*, instancia, tag,   limit, run_id, ...)
    #
    # Sao quatro enderecos diferentes de observacao — e cada um entra pelo seu
    # nome em `NOMEADOS`, nunca pelo nome do vizinho. `telegram` nem sequer
    # aceita `limit`: passa-lo seria um argumento que a rota engole sem usar.
    #
    # ESPECIE, medida e nao presumida:
    #   · `telegram.channel.incremental` e `mastodon.hashtag.search` devolvem o
    #     que a conta/tag PUBLICOU — material observado. COLHEITA.
    #   · `bluesky.account.discovery` devolve CONTAS que existem para um termo:
    #     entidades DE ONDE SE PODE COLHER, nao o que elas disseram. CATALOG,
    #     pela mesma razao que `identidade-linkedin` o e.
    #
    #     DISCOVERY != CONTENT. UMA LISTA DE CONTAS NAO E UMA OBSERVACAO DELAS.
    'canal-telegram':   ('TELEGRAM', 'telegram.channel.incremental', {},
                         rc.COLHEITA),
    'tag-mastodon':     ('MASTODON', 'mastodon.hashtag.search', {'limit': 1},
                         rc.COLHEITA),
    'contas-bluesky':   ('BLUESKY', 'bluesky.account.discovery', {'limit': 1},
                         rc.CATALOG),

    # ── AS QUATRO OFICIAIS DO YOUTUBE ──────────────────────────────────────
    # Outra FORMA: `adaptador_youtube` / campo ROTA / ONLINE. Ela nao estava
    # ligada por uma razao que se leu mal a primeira vez — e a correcao vale
    # mais do que as fases:
    #
    #     `scrap_executor.CHECK` respondia `CREDENTIAL_MISSING` aqui, e isso foi
    #     lido como «o projeto nao tem a chave». Nao tem: o PROCESSO LOCAL nao
    #     tem. `.github/workflows/scrap-social.yml:311` injecta
    #     `YOUTUBE_DATA_API_KEY` por `secrets`, e `youtube_oficial.ENV_CHAVE`
    #     le exactamente esse nome. Medido: com a chave declarada no ambiente,
    #     as quatro passam a `CAN_COLLECT_NOW` sem tocar em codigo.
    #
    #     CREDENCIAL AUSENTE NESTE SHELL != CREDENCIAL AUSENTE NO SISTEMA.
    #     UM ESTADO DE AMBIENTE NAO E UM ESTADO DE CAPACIDADE.
    #
    # ⚠️ `youtube.native_caption` NAO entra aqui, e a medicao e que o diz: com
    # a mesma chave declarada ela CONTINUA `CREDENTIAL_MISSING`, porque a rota
    # dela e `apify:transcricao` e o dono da credencial e `APIFY_TOKEN_POOL`.
    # Ela pertence a porta que gasta, e essa porta tem outro gate.
    #
    #     CAPTION != TRANSCRIPT. E UMA CHAVE NAO ABRE A FECHADURA DA OUTRA.
    #
    # PARAMETROS, lidos um a um em `coleta/adaptador_youtube.py` — sao quatro
    # contratos diferentes e nenhum foi copiado do vizinho:
    #
    #     youtube_buscar       (*, termo,      run_id, country_scope, limit, ...)
    #     youtube_uploads      (*, channel_id, run_id, country_scope, limit, ...)
    #     youtube_metadata     (*, video_ids,  run_id, country_scope, ...)
    #     youtube_comentarios  (*, video_id,   run_id, country_scope, ...)
    #
    # `video_ids` e PLURAL e `video_id` e SINGULAR: sao rotas diferentes, e
    # trocar um pelo outro passaria uma lista onde se espera um id.
    #
    # ESPECIE, decidida pelo que cada rota devolve e nao por omissao:
    #   · `search` devolve CANDIDATOS a partir de um termo — videos que podem
    #     existir para aquela busca, e nao o que uma fonte publicou. CATALOG.
    #   · `channel.discovery` devolve os uploads RECENTES de um canal: material
    #     que aquele canal publicou. COLHEITA.
    #   · `video.metadata` devolve o que o video declara de si. COLHEITA.
    #   · `comments` devolve o que pessoas escreveram no video. COLHEITA.
    #
    #     SEARCH DEVOLVE ONDE PROCURAR; UPLOADS DEVOLVEM O QUE FOI PUBLICADO.
    'busca-youtube':    ('YOUTUBE', 'youtube.search', {'limit': 25},
                         rc.CATALOG),
    'canal-youtube':    ('YOUTUBE', 'youtube.channel.discovery', {'limit': 25},
                         rc.COLHEITA),
    'video-youtube':    ('YOUTUBE', 'youtube.video.metadata', {},
                         rc.COLHEITA),
    'comentarios-youtube': ('YOUTUBE', 'youtube.comments', {},
                            rc.COLHEITA),

    # ── A QUINTA: O SOM. E POR QUE ELA NAO VEIO COM AS OUTRAS QUATRO ───────
    # `youtube.public_audio` foi provada ponta a ponta pelo C13, tem rota no
    # `scrap_registo._MAPA`, e o `CHECK` responde `CAN_COLLECT_NOW`. Mesmo
    # assim a Collection nao conseguia pedi-la: **nao havia fase**. O canario
    # real parou aqui, e o diagnostico e exactamente o §151:
    #
    #     CAPABILITY PROVEN != EDGE WIRED != COLLECTION REACHABLE
    #
    # O C13 provou o degrau `scrap_executor -> adaptador_youtube`. Faltava o
    # degrau ANTERIOR — `REQUEST -> scrap_colheita` — e ninguem tinha olhado
    # para ele porque o edge ja estava verde.
    #
    # ESPECIE: COLHEITA, e nao CATALOG. O som de um video e o que aquele canal
    # PUBLICOU — material observado, nao uma lista de onde procurar. A mesma
    # regra que poe `busca-youtube` em CATALOG poe esta aqui em COLHEITA.
    #
    # FIXOS = {}: nao ha `limit`. Esta fase colhe UM video, o que o pedido
    # nomear. Pedir um teto a uma rota que recebe um `video_id` seria um
    # argumento que ela engole sem usar — o erro que o Telegram ja ensinou.
    'audio-youtube':    ('YOUTUBE', 'youtube.public_audio', {},
                         rc.COLHEITA),

    # ── AS TRES DO REEL, E POR QUE ELAS ENTRAM AGORA ───────────────────────
    # `instagram.reel.capture`, `instagram.reel.audio` e
    # `instagram.reel.transcribe` estao PROVEN desde a C10, tem adaptador
    # (`adaptador_instagram`), tem unidade de trabalho (o Reel) e o `CHECK`
    # responde `CAN_COLLECT_NOW` as tres — sem credencial, sem conta e sem
    # fornecedor pago. O que faltava era o degrau de CIMA, e e o §154 outra vez:
    #
    #     CAPABILITY PROVEN != EDGE WIRED != COLLECTION REACHABLE
    #
    # A Collection sabia pedir dez capabilities e estas tres nao estavam entre
    # elas. Uma capacidade provada sem fase e um motor sem cabo: a prova diz que
    # ele colhe; a fase e que diz que alguem pode pedir.
    #
    # ESPECIE: COLHEITA nas tres. O que volta e material observado — a media do
    # Reel, o som dela e a fala reconhecida —, e nao uma lista de onde procurar.
    # A mesma regra que poe `busca-youtube` em CATALOG.
    #
    # FIXOS = {}: nao ha `limit`. Estas rotas colhem UM Reel, o que o pedido
    # nomear. Pedir um teto a uma rota que recebe uma URL seria um argumento que
    # ela engole sem usar — o erro que o Telegram ja ensinou.
    #
    # ⚠️ A URL E O ENDERECO, E NAO A IDENTIDADE. `--fonte` continua a descer o
    # SOURCE_ID provado; a URL diz A QUE PUBLICACAO se vai bater. A mesma lei
    # que separa `handle` de SOURCE_ID no `canario-bluesky`.
    #
    #     URL NAO E SOURCE_ID.
    #
    # ⚠️ E `profile.discovery` NAO ENTRA AQUI. Ela e `PARTIAL` e
    # `LOCAL/DATACENTER_BLOCKED` — precisa de maquina residencial e nao corre de
    # um datacenter (a fase `janela` ja o declara). A ausencia dela nesta lista e
    # uma medicao, e nao um esquecimento: quem quiser a janela pede `janela`.
    'captura-reel':     ('INSTAGRAM', 'instagram.reel.capture', {},
                         rc.COLHEITA),
    'audio-reel':       ('INSTAGRAM', 'instagram.reel.audio', {},
                         rc.COLHEITA),
    'transcricao-reel': ('INSTAGRAM', 'instagram.reel.transcribe', {},
                         rc.COLHEITA),

    # ── D23 · O VIDEO DE ORGANIZACAO NO LINKEDIN ──────────────────────────
    # Tres actos numa fase so, e por que: descobrir as publicacoes com video
    # nao serve de nada sem os bytes, e os bytes sem o post nao dizem de que
    # publicacao sao. A cadeia e DESCOBERTA -> IDENTIDADE -> BYTES -> TEXTO,
    # e ela corre DENTRO do adaptador (`video_da_pagina_publica`), que e quem
    # tem a autorizacao do dono viva enquanto atravessa o portao.
    #
    #     UMA FASE POR ACTO SO SERVE QUANDO O ACTO ANTERIOR PODE ACABAR
    #     SEM O SEGUINTE. Aqui nao pode: o endereco do MP4 vive na pagina e
    #     morre com ela.
    #
    # ESPECIE: COLHEITA. O que volta e material observado — o video que a
    # organizacao publicou e o texto da legenda que ela serve. A mesma regra
    # que poe `canal-youtube` em COLHEITA e `busca-youtube` em CATALOG.
    #
    # FIXOS = {}: nao ha teto fixo aqui. O teto desce como FILTRO nomeado,
    # porque quem pede e que decide quantos videos se pedem — e a rota tem um
    # valor por omissao declarado para quando ninguem o disser.
    #
    # ⚠️ A CAPACIDADE E `linkedin.org.video` E NAO `.posts`: a fase existe
    # para TRAZER O VIDEO. A descoberta e um degrau dela, e nao um fim.
    'video-linkedin': ('LINKEDIN', 'linkedin.org.video', {},
                       rc.COLHEITA),
}

#: Que filtros NOMEADOS cada fase aceita, e so ela. O orquestrador traduz
#: `filtros_nomeados` da receita em `--nome=valor`, e sem uma lista por fase um
#: nome que a rota nao conhece chega la dentro e morre no `**_` do adaptador,
#: em silencio, com a corrida a dar verde.
#:
#:     UM ARGUMENTO QUE A ROTA ENGOLE SEM USAR NAO E OPCIONAL: E UMA ARMADILHA.
#:
#: Entao um nome fora da lista da fase RECUSA a corrida, e diz qual era a lista.
#: Fail closed: o silencio nao autoriza.
#: A forma e `{fase: {nome publico: nome que a rota recebe}}`. Os dois lados sao
#: quase sempre iguais — e quando nao sao, a traducao mora AQUI, a vista, e nao
#: escondida num `if fase ==` la dentro.
#:
#:     UMA TRADUCAO QUE NAO SE VE E UMA TRADUCAO QUE NINGUEM CONFERE.
NOMEADOS = {
    'janela':          {'teto': 'teto'},
    'janela-perfis':   {'teto': 'teto'},
    'janela-objetos':  {'teto': 'teto'},
    # `handle` e o ENDERECO da observacao, e nunca a identidade da fonte. Ele
    # diz A QUE CONTA se vai bater; `--fonte` diz DE QUE FONTE PROVADA o
    # pedido fala. Sao dois campos porque sao duas coisas.
    #
    #     HANDLE NAO E SOURCE_ID. Derivar um do outro seria fabricar identidade.
    'canario-bluesky': {'handle': 'handle'},
    # `site` e o endereco do site DA ORGANIZACAO, de onde se le o handle que
    # ela propria publicou. Nao e o SOURCE_ID, e nao e o handle: e onde se vai
    # perguntar. A rota chama-lhe `site_url`, e a traducao e esta linha.
    'identidade-linkedin': {'site': 'site_url'},
    # ── UM ENDERECO POR ROTA, E NENHUM EMPRESTADO ──────────────────────────
    # As quatro rotas de `adaptador_aberto` partilham a FORMA e nao os NOMES.
    # Cada linha abaixo saiu da assinatura real da funcao que a rota executa,
    # lida em `scrap_registo._MAPA[(plat, cap)]['ROTA']` — nao do vizinho:
    #
    #     telegram_canal    (*, canal,            run_id, country_scope, **_)
    #     mastodon_tag      (*, instancia, tag,   limit, run_id, ...)
    #     bluesky_contas    (*, termo,            limit, run_id, ...)
    #
    # `mastodon` precisa de DOIS: a instancia diz EM QUE SERVIDOR se pergunta
    # (o Mastodon nao tem um so), e a tag diz O QUE se pergunta la. Sao duas
    # perguntas, e por isso dois nomes.
    #
    # ⚠️ NENHUM destes e o SOURCE_ID. `--fonte` continua a descer a identidade
    # provada da fonte; estes dizem apenas ONDE bater. A mesma lei que separa
    # `handle` de SOURCE_ID no `canario-bluesky` separa-os aqui.
    #
    #     CANAL, TAG E TERMO SAO ENDERECOS. IDENTIDADE VEM DO PEDIDO.
    'canal-telegram':    {'canal': 'canal'},
    'tag-mastodon':      {'instancia': 'instancia', 'tag': 'tag'},
    'contas-bluesky':    {'termo': 'termo'},
    # ── OS QUATRO ENDERECOS DO YOUTUBE, E NENHUM E O SOURCE_ID ─────────────
    # Lidos em `coleta/adaptador_youtube.py`. `busca-youtube` reusa o nome
    # publico `termo` porque a pergunta e a mesma — uma palavra de busca — mas
    # a fase e outra e a lista dela e que fecha: `contas-bluesky` continua a
    # nao aceitar `channel`, e vice-versa.
    #
    # ⚠️ `video` e `videos` sao NOMES DIFERENTES de proposito: a rota de
    # metadata recebe `video_ids` (uma lista) e a de comentarios recebe
    # `video_id` (um so). Um nome unico para os dois obrigaria a adivinhar a
    # forma la dentro, e adivinhar e o que esta lista existe para impedir.
    #
    #     UM ID NAO E UMA LISTA DE IDS.
    #     E NENHUM DELES E A FONTE: `--fonte` desce o SOURCE_ID provado.
    'busca-youtube':        {'termo': 'termo'},
    'canal-youtube':        {'canal_id': 'channel_id'},
    'video-youtube':        {'videos': 'video_ids'},
    'comentarios-youtube':  {'video': 'video_id'},
    # `video`, e nunca `fonte`. A fase NAO pode derivar o video da source: uma
    # fonte YouTube tem milhares de videos, e escolher um deles e uma decisao
    # do PEDIDO. Sem `--video` a fase falha fechado, antes da rede.
    #
    #     VIDEO_ID != SOURCE_ID. HANDLE != SOURCE_ID.
    'audio-youtube':        {'video': 'video_id'},
    # ── O ENDERECO DO REEL, E ELE E UM SO PARA AS TRES ─────────────────────
    # `capturar_reel` recebe `url` (ou um `ident` ja resolvido), e a assinatura
    # dela e a mesma nas tres capacidades — sao tres nomes do mesmo acto, e o
    # proprio adaptador o escreve. Um nome publico por fase que apontasse para
    # rotas diferentes seria a traducao a inventar o que a rota nao tem.
    #
    #     TRES NOMES PARA UM ACTO NAO SAO TRES ENDERECOS.
    'captura-reel':         {'url': 'url'},
    'audio-reel':           {'url': 'url'},
    'transcricao-reel':     {'url': 'url'},
    # ── A PAGINA DA ORGANIZACAO, E O TETO DE VIDEOS ───────────────────────
    # `pagina` e o ENDERECO da pagina publica da ORGANIZACAO. Nao e o
    # SOURCE_ID (`--fonte` desce ao lado) e nao e o `site` da descoberta de
    # identidade: e o lugar onde as publicacoes com video sao servidas.
    #
    # `teto` e o numero maximo de videos ADQUIRIDOS nesta corrida. Ele e
    # filtro e nao constante porque a banda e do dono: a mesma fase que pede
    # tres videos para provar a cadeia pediria tres de uma pagina com trinta
    # publicacoes so com alguem a decidir isso.
    #
    #     UM TETO QUE SE PEDE E UM TETO QUE SE VE NO PEDIDO.
    'video-linkedin':      {'pagina': 'pagina_url', 'teto': 'teto'},
}

#: O que o envelope canônico do SCRAP responde, com o nome que a porta usa.
#: `coleta/ingresso.py::DO_COLETOR` tem treze campos; o SCRAP responde a estes,
#: e os outros chegam em falta — e a porta escreve «NAO SEI», que é honesto.
#:
#:     TRADUZIR NOME E FORMA É TRABALHO DE ADAPTER.
#:     PREENCHER UM CAMPO QUE A OBSERVAÇÃO NÃO TROUXE NÃO É.
DO_SCRAP_PARA_A_PORTA = {
    'URL': 'SOURCE_URL',
    'COUNTRY_SCOPE': 'COUNTRY_SCOPE',
    'SOURCE_LOCATION': 'SOURCE_LOCATION',
    'LANGUAGE': 'ITEM_LANGUAGE',
    'PUBLISHED_AT': 'PUBLISHED_AT',
    'COLLECTED_AT': 'OBSERVED_AT',
    # ── D61/D63: A DATA DE PUBLICACAO VIAJA COM A BASE E A PRECISAO ────────────
    # `PUBLISHED_AT` ja atravessava; a base (como a plataforma o declarou) e a
    # precisao (SECOND/MINUTE/DAY) ficavam no bruto. Quem conta «ieri» a partir da
    # publicacao so o pode fazer com a publicacao PROVADA — data E base.
    'PUBLISHED_AT_SOURCE': 'PUBLISHED_AT_BASIS',
    'PUBLISHED_AT_PRECISION': 'PUBLISHED_AT_PRECISION',
    # O lugar de QUEM PUBLICA, com a base e a precisao (SOURCE_LOCATION != FACT_LOCATION).
    'SOURCE_LOCATION_BASIS': 'SOURCE_LOCATION_BASIS',
    'SOURCE_LOCATION_PRECISION': 'SOURCE_LOCATION_PRECISION',
}

DESCONHECIDO = 'UNKNOWN'

#: O valor de nascenca de `COST_STATE` em `coleta/social_rotas.py`: a rota nao
#: correu. So quem corre o sobrescreve.
NAO_CORREU = 'NOT_RUN'


def _limpo(v):
    """→ o valor, ou None quando ele é uma confissão de ausência."""
    s = str(v or '').strip()
    return None if not s or s in (DESCONHECIDO, rc.NAO_SEI) else v


def _valores_de_identidade(objeto):
    """Os valores que a OBSERVAÇÃO declara e que um molde de identidade pode usar.

    ⚠️ NÃO É UMA LISTA DE CANDIDATOS, É UM CENSO DO QUE VEM. Só entram campos
    que a observação de facto traz, com o nome que ela lhes deu. Nada é
    derivado do sha, do caminho, da URL ou da data — um id montado com um
    desses seria uma mentira com forma de dado.

        O CONTRATO DIZ QUE IDENTIDADE ISTO TEM.
        A OBSERVAÇÃO DIZ QUAIS DOS VALORES DELA EXISTEM.
    """
    if not isinstance(objeto, dict):
        return {}
    return {k: v for k, v in objeto.items()
            if isinstance(k, str) and v not in (None, '')}


def _referencia_e_especie(objeto):
    """→ (caminho do ficheiro, espécie dos bytes) tal como o COLETOR os declarou.

    ⚠️ DUAS FORMAS DECLARADAS, E NENHUMA ADIVINHADA. Medido no HEAD:

        YouTube · `youtube_audio_publico`   AUDIO_REFERENCE + CONTENT_TYPE
                                            no TOPO do objeto
        Reel    · `reel_transcricao`        RAW.STORAGE_LOCATION + RAW.CONTENT_TYPE
                                            dentro da ficha que a cadeia escreveu

    São duas maneiras de o dono da aquisição dizer a MESMA coisa, e a fronteira
    lê as duas em vez de obrigar uma delas a mudar de forma. O que ela NÃO faz
    continua a ser o essencial: não deriva nenhuma das duas da extensão do
    ficheiro, e não aceita uma sem a outra.

        TRADUZIR NOME E FORMA E TRABALHO DE ADAPTER.
        DECIDIR O QUE A COISA E, NAO E.
    """
    fora = objeto if isinstance(objeto, dict) else {}
    if _limpo(fora.get('AUDIO_REFERENCE')):
        return _limpo(fora.get('AUDIO_REFERENCE')), _limpo(fora.get('CONTENT_TYPE'))
    raw = fora.get('RAW') if isinstance(fora.get('RAW'), dict) else {}
    return _limpo(raw.get('STORAGE_LOCATION')), _limpo(raw.get('CONTENT_TYPE'))


def unidade(objeto, *, run_id, fonte):
    """Um objeto do SCRAP na língua da porta. → a unidade de COLHEITA.

    ⚠️ O `DOCUMENT_ID` DEIXOU DE SER SEMPRE `NAO SEI`, E ISSO É UMA CORREÇÃO.
    Ele era `NAO SEI` «de propósito e por lei» enquanto NENHUM owner
    materializava a regra que o contrato de fonte já declarava. Medido:

        regras/italy_contracts.mjs::IT-T8-001
            DOCUMENT_ID_RULE = "AGRONOTIZIE:YT:{VIDEO_ID}  —  o video_id …"
        e a unidade saía `DOCUMENT_ID = NAO SEI`.

    Isso não era honestidade: era uma identidade que ficou por ligar. O dono do
    contrato é o contrato, e quem o lê é `regras/contratos_de_fonte.py` — é lá
    que o molde se preenche, e é daqui que se lhe passam os valores.

        UM `NAO SEI` ONDE O CONTRATO DECLARA UM ID NÃO É HONESTIDADE:
        É UMA IDENTIDADE QUE FICOU POR LIGAR.

    E o que NÃO mudou: sem contrato legível, sem regra, ou com um molde a que
    falte um valor, a resposta continua a ser `NAO SEI` — com o motivo escrito
    ao lado, em `DOCUMENT_ID_BASE`. Um id a meio é pior do que nenhum, porque
    entra no acervo com a cara de facto e ninguém volta a perguntar.
    """
    fora = {'ESPECIE': rc.COLHEITA, 'RUN_ID': run_id, 'SOURCE_ID': fonte,
            'DOCUMENT_ID': rc.NAO_SEI}
    # ── O `DOCUMENT_ID`, PELO DONO DO CONTRATO ─────────────────────────────
    # A importação é local e protegida de propósito: numa árvore sem a gaveta
    # `regras/` (ou sem `node`), a resposta honesta é `NAO SEI` — e não uma
    # coleta que pára por causa de uma pergunta sobre identidade.
    #
    #     FERRAMENTA QUE FALTA NÃO É DOCUMENTO QUEBRADO.  (COL-LAW-503)
    try:
        import contratos_de_fonte as cf                            # noqa: PLC0415
        if fonte:
            _id = cf.document_id_declarado(fonte, _valores_de_identidade(objeto))
            fora['DOCUMENT_ID'] = _id['DOCUMENT_ID']
            fora['DOCUMENT_ID_BASE'] = _id['BASE']
            fora['DOCUMENT_ID_REGRA'] = _id['REGRA_ORIGINAL']
    except Exception as e:                                         # noqa: BLE001
        fora['DOCUMENT_ID_BASE'] = (
            'CONTRATO_ILEGIVEL: nao se conseguiu ler o contrato de fonte (%s: %s). '
            'Sem o dono do contrato nao se materializa identidade nenhuma.'
            % (type(e).__name__, str(e)[:160]))
    for de, para in DO_SCRAP_PARA_A_PORTA.items():
        v = _limpo(objeto.get(de))
        if v is not None:
            fora[para] = v
    # Uma base sem o valor que ela prova nao e prova de nada: sem data, sem base;
    # sem lugar, sem base do lugar. A precisao fica (ela diz «nao declarada»).
    if 'PUBLISHED_AT' not in fora:
        fora.pop('PUBLISHED_AT_BASIS', None)
    # ── D61: o lugar de QUEM PUBLICA, quando a observacao nao o traz ─────────
    # O dono e o CONTRATO da fonte (como no DOCUMENT_ID acima); aqui so se le.
    # Nunca o COUNTRY_SCOPE nem o egresso: esses dizem onde NOS estavamos.
    if 'SOURCE_LOCATION' not in fora and fonte:
        try:
            import lugar_da_organizacao as lo                         # noqa: PLC0415
            do_contrato = lo.do_contrato(fonte, RAIZ)
        except Exception:                                            # noqa: BLE001
            do_contrato = None
        if do_contrato:
            for k, v in do_contrato.items():
                if _limpo(v) is not None:
                    fora[k] = v
    if 'SOURCE_LOCATION' not in fora:
        fora.pop('SOURCE_LOCATION_BASIS', None)
    # O corpo da observação viaja inteiro: a porta assina o que recebeu, e
    # normalizar aqui faria a impressão digital ser de outra coisa.
    #
    #     RAW BEFORE NORMALIZATION.
    fora['OBSERVACAO'] = objeto
    # ── O TEXTO, COM ESPECIE, ATRAVESSA AQUI ────────────────────────────
    # ⚠️ ESTA LINHA ESTAVA PENDENTE POR DESENHO, E NAO POR ESQUECIMENTO.
    # O ensaio do SCRAP contra a Collection parou exactamente aqui e disse
    # porque: `BLOCKED_BY_HUMAN = VOCABULARIO_DO_TEXTO_NA_PORTA`. O texto
    # existia dos dois lados e nao atravessava, porque liga-lo sem especie
    # entregaria texto de autor e fala reconhecida no MESMO campo,
    # indistinguiveis — a soma que a casa proibe.
    #
    #     CAPTION != TRANSCRIPT.
    #
    # O vocabulario chegou com o contrato do texto (COL-E7-01), e com ele a
    # linha deixou de ser um atalho e passou a ser uma traducao.
    #
    # E ELA VIVE AQUI, no adapter, e nao na fronteira comum: `para_a_porta`
    # SELECCIONA entre unidades que ja existem; quem as CRIA a partir de um
    # envelope social e `proveniencia.unidades_do_envelope`, cujo docstring
    # nomeia este mapeador como quem a le. Duas funcoes, dois trabalhos, um
    # dono so — e nenhuma regra de texto reescrita aqui dentro.
    #
    #     TRADUZIR NOME E FORMA E TRABALHO DE ADAPTER.
    #     DECIDIR O QUE O TEXTO E, NAO E.
    #
    # Um envelope legado, so com `TEXT`, sai daqui `UNKNOWN` — e continua
    # `UNKNOWN` do outro lado. A ausencia nao e promovida.
    fora[pv.CAMPO_DAS_UNIDADES] = pv.unidades_do_envelope(objeto)
    # ── QUANDO A OBSERVAÇÃO TEM CORPO, O CORPO É QUE SE PRESERVA ────────────
    # ⚠️ ATÉ AQUI ESTA FUNÇÃO ASSUMIA QUE A OBSERVAÇÃO **É** O ITEM. Para um
    # post, uma legenda ou um perfil isso é verdade: os bytes são o JSON. Para
    # mídia adquirida é **falso**, e o primeiro canário real do YouTube mediu
    # o preço: um WAV de 7.112.072 bytes ficou no disco enquanto o RAW
    # preservava 1232 bytes de envelope, com `media_type=application/json`.
    # Sem espécie de áudio, `ingresso` não achou derivador; sem derivado, a
    # Admissão respondeu `NAO_SEI` a um documento que nunca teve texto.
    #
    #     A OBSERVAÇÃO DESCREVE O ITEM. QUANDO HÁ FICHEIRO,
    #     ELA NÃO É O ITEM — ELA APONTA PARA ELE.
    #
    # Esta é uma TRADUÇÃO, e não uma decisão: quem diz que o ficheiro existe e
    # o que ele é foi o dono da aquisição, que o mediu com `ffprobe` antes de
    # o declarar. Este adapter só põe esse facto no campo que a porta lê —
    # `STORAGE_LOCATION` — e nunca inventa nenhum dos dois.
    #
    #     TRADUZIR NOME E FORMA != DECIDIR O QUE A COISA É.
    #
    # Fail-closed em três pontos, porque cada um já foi um defeito noutra
    # família: sem referência declarada não há caminho; um caminho que não
    # existe no disco não vira RAW de áudio; e sem `CONTENT_TYPE` do coletor
    # não se adivinha pela extensão — ficaria `NAO SEI`, que o ingresso trata
    # como «tenta», e foi assim que um `.mp4` foi parar ao `pdftotext`.
    referencia, especie = _referencia_e_especie(objeto)
    if referencia and especie and os.path.isfile(referencia):
        # Relativo à raiz, que é a língua de `STORAGE_LOCATION`. O caminho é
        # ENDEREÇO, nunca identidade: quem identifica os bytes é o `sha256`
        # que `raw_do_disco` calcula ao lê-los.
        try:
            rel = os.path.relpath(referencia, RAIZ).replace('\\', '/')
        except ValueError:                       # noutro volume: fica absoluto
            rel = referencia
        fora['STORAGE_LOCATION'] = rel
        fora['CONTENT_TYPE'] = especie
        # `PRESENTE` é do vocabulário canónico de `leis/retorno_da_coleta.py`
        # (`ESTADOS_DO_PAYLOAD`), e não uma palavra escolhida aqui: o payload
        # existe, está no disco, e o endereço dele é este.
        fora['PAYLOAD'] = {'ONDE': rel, 'ESTADO': rc.PRESENTE}
        return fora
    # Sem ficheiro separado: a observação É o item, e isso diz-se.
    fora['PAYLOAD'] = {'ONDE': '', 'ESTADO': rc.PAYLOAD_NAO_SE_APLICA}
    return fora


def suporte_do_trace(trace):
    """O que a corrida produziu e que NÃO é colheita. → lista de suporte.

    O trace é a prova da execução — é `RUN_RECEIPT`, e nunca observação.
    Declará-lo aqui é o que impede que ele entre pela porta por distração.

        O RECIBO DE UMA COLHEITA NÃO É A COLHEITA.
    """
    return [{'ESPECIE': rc.RUN_RECEIPT, 'ONDE': '',
             'O_QUE_E': 'o trace da corrida do SCRAP: rota escolhida, estado, '
                        'tetos e custo. Prova da execução, não material observado.',
             'PAYLOAD': {'ONDE': '', 'ESTADO': rc.PAYLOAD_NAO_SE_APLICA},
             'RESUMO': resumo_do_trace(trace)}]


#: Os eixos que o recibo leva, e por que sao estes.
#:
#: ⚠️ MEDIDO NA SCRAP-MORNING-01, no portao §2B. A NIGHT-SHIFT-01 consertou o
#: TRACE — sem Chrome, `instagram.profile.discovery` passou a dizer
#: `EXECUTOR_UNAVAILABLE` em vez de `UNKNOWN_ERROR`. Mas o recibo que atravessa
#: para quem le carregava CINCO chaves, e nenhuma delas era a recuperacao nem a
#: frase. Quem lesse o envelope via um estado sem saber de quem era a culpa nem
#: o que fazer a seguir:
#:
#:     RESULT EXECUTOR_UNAVAILABLE  ·  e mais nada
#:
#: Um estado que sabe, num recibo que nao o leva, volta a ser «nao sei» para
#: quem le.
#:
#:     CONSERTAR O TRACE E CONSERTAR O TRACE.
#:     O QUE ATRAVESSA E O RECIBO.
#:
#: Os quatro eixos novos nao sao inventados aqui: `leis/falhas.py` ja os deriva
#: todos a partir do estado canonico, e `social_rotas.selar()` ja os escreve.
#: Este ficheiro so deixa de os deitar fora.
EIXOS_DO_RECIBO = (
    'RESULT',                 # o estado canonico
    'EXECUTOR_ID',
    'EXECUTION_MODE',
    'NETWORK_REQUESTS_USED',
    'COST_STATE',             # NOT_RUN != COST 0
    'FAILURE_LAYER',          # de quem e a culpa — ROTA CAIDA NAO E FONTE CAIDA
    'RECOVERY_ACTION',        # o que fazer a seguir
    'NATIVE_REASON',          # o nome nativo, de maquina
)


def resumo_do_trace(trace):
    """O que o recibo leva de uma corrida. → o resumo, sem nada inventado.

    A frase de gente viaja ao lado dos nomes, e nunca dentro deles:

        STATE          o estado canonico       EXECUTOR_UNAVAILABLE
        NATIVE_REASON  o nome, de maquina      BROWSER_NOT_REACHED
        PORQUE         a frase, de gente       «sem Chrome nesta maquina: ...»

    UM NOME E UMA FRASE NAO CABEM NO MESMO CAMPO.

    A frase vem de `ROUTER_RECORD.ERRO`, que `social_rotas` ja REDIGIU — um
    traceback de `urllib` carrega a URL, e a URL pode carregar o token. Copia-la
    de outro sitio seria copia-la por redigir.
    """
    resumo = {k: trace.get(k) for k in EIXOS_DO_RECIBO if k in trace}
    porque = ((trace.get('ROUTER_RECORD') or {}).get('ERRO'))
    if porque:
        resumo['PORQUE'] = porque
    return resumo


def colher(fase, *, run_id, fonte, banco=None, **extra):
    """Uma fase, uma corrida do `COLLECT`. → o envelope do COL-LAW-505.

    NÃO levanta por rota recusada: recusa é resultado de medição, e desce como
    estado. O envelope diz o que a corrida devolveu — inclusive «nada, e porquê».
    """
    plataforma, capacidade, fixos, especie = FASES[fase]
    objetos, trace = sx.COLLECT(platform=plataforma, capability=capacidade,
                                run_id=run_id, banco=banco,
                                **dict(fixos, **extra))
    objetos = objetos or []
    estado = rc.SUCCESS if trace.get('RESULT') in (None, 'OK', 'SUCCESS') else rc.PARTIAL
    erros = []
    porque_zero = ''

    # ── UMA ROTA QUE NAO CORREU NAO OBSERVOU NADA ──────────────────────────
    # ⚠️ MEDIDO NA NIGHT-SHIFT-01, e reproduzido antes de corrigido:
    #
    #     instagram.reel.capture · RESULT = ROUTE_NOT_ALLOWED
    #     PROVIDER_USED = None  ·  COST_STATE = NOT_RUN
    #     -> e mesmo assim UM objeto voltava, e virava UMA unidade de COLHEITA
    #        carimbada com um SOURCE_ID verdadeiro.
    #
    # O objeto era um esqueleto: todos os campos em `NOT_KNOWN`. Ele nasce de
    # proposito — a cadeia de Reel distingue REUSAR de ADQUIRIR e devolve o que
    # sabe mesmo quando a aquisicao e recusada, o que esta certo LA. O que
    # estava errado era aqui: quem decide o que e COLHEITA e este ficheiro, e
    # ele contava o esqueleto como observacao.
    #
    #     UMA ROTA QUE NAO CORREU NAO OBSERVOU NADA.
    #     UM ESQUELETO COM SOURCE_ID E UMA OBSERVACAO FABRICADA.
    #
    # O sinal nao e o estado de falha — uma rota que colheu dez e depois levou
    # `RATE_LIMITED` colheu dez de verdade. O sinal e o do dono do custo, que
    # nasce `NOT_RUN` e so quem corre sobrescreve:
    #
    #     NOT_RUN != COST 0. UNKNOWN COST != COST 0.  (`coleta/social_rotas.py`)
    if objetos and trace.get('COST_STATE') == NAO_CORREU:
        suporte = suporte_do_trace(trace) + [
            {'ESPECIE': rc.ESPECIE_DESCONHECIDA, 'ONDE': '',
             'O_QUE_E': 'o que a rota devolveu sem ter corrido: %s'
                        % (trace.get('RESULT') or 'sem estado'),
             'PAYLOAD': {'ONDE': '', 'ESTADO': rc.PAYLOAD_NAO_SE_APLICA},
             'QUANTOS': len(objetos)}]
        return {
            'RUN_ID': run_id, 'EXECUTOR_ID': EXECUTOR_ID,
            'EXECUTOR_VERSION': EXECUTOR_VERSION, 'ESTADO': rc.PARTIAL,
            'COLHEITA': [], 'SUPORTE': suporte, 'ERROS': erros,
            'FASE': fase, 'PLATFORM': plataforma, 'CAPABILITY': capacidade,
            'ESPECIE_DA_FASE': especie,
            'SOURCE_ID_DO_PEDIDO': fonte or rc.NAO_SEI,
            'PORQUE_ZERO_COLHEITA': (
                'a rota nao correu (COST_STATE=%s, RESULT=%s) e, mesmo assim, '
                'devolveu %d objeto(s). Eles NAO sao observacoes: saem por '
                'SUPORTE. Uma rota que nao correu nao observou nada, e um '
                'esqueleto carimbado com SOURCE_ID seria observacao fabricada.'
                % (NAO_CORREU, trace.get('RESULT'), len(objetos))),
        }

    if especie != rc.COLHEITA:
        # ── A FASE DECLAROU QUE NAO PRODUZ COLHEITA, E ISSO E UM FACTO ──────
        # `ENTRAM_NO_INGRESSO = (COLHEITA,)`. Esta fase devolve uma entidade DE
        # ONDE SE PODE COLHER, nao material observado — entao ela sai por
        # SUPORTE, com a especie escrita, e a COLHEITA fica vazia porque e
        # vazia. Zero aqui nao e falha nem e ausencia de dados: e a especie.
        #
        #     UM ZERO QUE VEM DA ESPECIE NAO SE LE COMO UM ZERO QUE VEM DA FONTE.
        #
        # E nao se escolhe por `if plataforma == ...`: escolhe-se pelo que a
        # fase DECLAROU em `FASES`, que e o unico sitio onde isso se decide.
        suporte = suporte_do_trace(trace) + [
            {'ESPECIE': especie, 'ONDE': '',
             'O_QUE_E': 'o que esta fase produz, pela especie que ela declara: '
                        '%s de %s/%s' % (especie, plataforma, capacidade),
             'PAYLOAD': {'ONDE': '', 'ESTADO': rc.PAYLOAD_NAO_SE_APLICA},
             'QUANTOS': len(objetos),
             'ITENS': objetos}]
        return {
            'RUN_ID': run_id, 'EXECUTOR_ID': EXECUTOR_ID,
            'EXECUTOR_VERSION': EXECUTOR_VERSION, 'ESTADO': estado,
            'COLHEITA': [], 'SUPORTE': suporte, 'ERROS': erros,
            'FASE': fase, 'PLATFORM': plataforma, 'CAPABILITY': capacidade,
            'ESPECIE_DA_FASE': especie,
            'SOURCE_ID_DO_PEDIDO': fonte or rc.NAO_SEI,
            'PORQUE_ZERO_COLHEITA': (
                'esta fase produz %s, e nao COLHEITA. So %s atravessa o '
                'ingresso, entao %d resultado(s) sairam por SUPORTE com a '
                'especie declarada. IDENTITY != CONTENT: um endereco de conta '
                'nao e uma observacao dela, e empurra-lo para a Admissao seria '
                'falsa colheita.'
                % (especie, ', '.join(rc.ENTRAM_NO_INGRESSO), len(objetos))),
        }

    # ── E UMA FONTE QUE NINGUÉM EMITIU NÃO É UMA FONTE ────────────────────
    # ⚠️ MEDIDO NO `1222d97d`, antes do portão da FASE 1D:
    #
    #     unidade(..., fonte='IT-T99-999')  ->  SOURCE_ID = 'IT-T99-999'
    #     _identifica('IT-T99-999')         ->  True
    #     quem lia o atlas para validar     ->  NINGUÉM
    #
    # `_identifica()` recusa as confissões e aceita tudo o resto — e está certa
    # para o que mede: distingue «veio um valor» de «veio uma desculpa». Não
    # distingue, nem deve, um valor verdadeiro de um inventado.
    #
    #     UM SOURCE_ID QUE NINGUÉM EMITIU NÃO É UMA IDENTIDADE FRACA.
    #     É UMA IDENTIDADE QUE NÃO EXISTE.
    #
    # Uma letra trocada — `IT-T3-O13` com a letra O — produziria uma corrida
    # verde, com recibo, carimbada com uma fonte que o atlas nunca conheceu. E
    # a certificação diria «a identidade atravessou intacta»: intacta e falsa.
    #
    # A resposta é a MESMA de quem não nomeou fonte, porque o facto é o mesmo:
    # não há fonte provada que ancore estas observações. Quem responde pela
    # população é `leis/fonte_do_atlas.py`, e ele levanta em vez de cair para
    # uma lista de reserva.
    desconhecida = bool(fonte) and not fa.conhece(fonte)
    if not fonte or desconhecida:
        # ── SEM FONTE PROVADA NÃO HÁ COLHEITA, E ISSO NÃO É UM ERRO ────────
        # É a resposta certa. O SCRAP não sabe de que fonte do atlas veio o que
        # colheu, e inventá-la seria fabricar identidade.
        porque_zero = (
            ('o pedido nomeou uma fonte que o atlas não conhece: %s Estas %d '
             'observações não têm fonte provada que as ancore, e carimbá-las '
             'com um SOURCE_ID inventado seria fabricar identidade.'
             % (fa.porque_nao(fonte), len(objetos)))
            if desconhecida else
            ('o pedido não nomeou fonte. O SCRAP observa PLATAFORMAS e a porta '
             'fala em FONTES; sem o SOURCE_ID vindo do pedido, estas %d '
             'observações são CANDIDATAS e não observações de uma fonte provada. '
             'URL não é SOURCE_ID.' % len(objetos)))
        colheita = []
        suporte = suporte_do_trace(trace) + [
            {'ESPECIE': rc.ESPECIE_DESCONHECIDA, 'ONDE': '',
             'O_QUE_E': 'o que a corrida observou, sem fonte provada que o ancore',
             'PAYLOAD': {'ONDE': '', 'ESTADO': rc.PAYLOAD_NAO_SE_APLICA},
             'QUANTOS': len(objetos)}]
    else:
        colheita = [unidade(o, run_id=run_id, fonte=fonte) for o in objetos]
        # FREIO-SOCIAL (dedup): o MESMO video partilhado por duas contas. Nas fases
        # sociais, cada unidade diz a identidade do video (ou NAO SEI, que nunca funde)
        # e, se o video ja foi visto noutra publicacao, de quem e (`MESMO_VIDEO_QUE`).
        # Nada se apaga: a partilha e um facto.
        if fase in FASES_CONTADAS:
            import identidade_do_video as IV                     # noqa: PLC0415
            IV.marcar(colheita, objetos, registo=os.path.join(
                os.environ.get('ITALY_OPS_ROOT') or RAIZ, IV.REGISTO))
        suporte = suporte_do_trace(trace)
        if not colheita:
            porque_zero = ('a corrida correu e não observou nada. ZERO LEGÍTIMO '
                           'NÃO É FALHA: %s' % (trace.get('RESULT') or 'sem estado'))

    envelope = {
        'RUN_ID': run_id, 'EXECUTOR_ID': EXECUTOR_ID,
        'EXECUTOR_VERSION': EXECUTOR_VERSION, 'ESTADO': estado,
        'COLHEITA': colheita, 'SUPORTE': suporte, 'ERROS': erros,
        'FASE': fase, 'PLATFORM': plataforma, 'CAPABILITY': capacidade,
        'ESPECIE_DA_FASE': especie,
        'SOURCE_ID_DO_PEDIDO': fonte or rc.NAO_SEI,
    }
    if porque_zero:
        envelope['PORQUE_ZERO_COLHEITA'] = porque_zero
    return envelope


def escrever(envelope, raiz=RAIZ):
    """O envelope DESTA corrida, na morada que a lei do retorno decide.

    ⚠️ ANTES ISTO ESCREVIA SEMPRE NO MESMO SITIO, e o defeito so morde quando
    duas corridas do mesmo executor se cruzam: a segunda escrevia por cima da
    primeira, e perguntar pela colheita de uma delas devolvia a da ultima —
    sem nota e sem recusa. Em serie nao aparece; a coleta grande e que o faz
    aparecer.
    O SCRAP nasceu antes desse conserto, e por isso trazia a morada fixa.

        UM ENVELOPE POR EXECUTOR NAO E UM ENVELOPE POR CORRIDA.

    A morada NAO se calcula aqui. Quem a decide e `endereco_do_envelope` em
    `leis/retorno_da_coleta.py`, que ja e o dono dela para os outros
    executores — e era essa a diferenca entre o que o SCRAP escrevia e o que o
    orquestrador procurava. Medido: sem isto, `COLHEITA_ENCONTRADA = 0`.

        DOIS SITIOS A CALCULAR A MESMA MORADA SAO DUAS MORADAS.
    """
    run_id = str((envelope or {}).get('RUN_ID') or '').strip()
    caminho = os.path.join(raiz, rc.endereco_do_envelope(ENVELOPE, run_id))
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(json.dumps(envelope, ensure_ascii=False, indent=1,
                           sort_keys=True) + '\n')
    return caminho


# ── A LINHA DA CORRIDA NO LIVRO DE CORRIDAS (PROVA-TETO-SOCIAL) ─────────────
# ⚠️ A PROVA-TETO (`provas/prova_teto_dominio.py`) NAO VIA AS CORRIDAS DO SCRAP.
# Ela le uma linha por corrida em `data/collection-ledger/italy/runs.ndjson`, com
# `CORTESIA.PEDIDOS_POR_HOST` — o transporte web escreve-a, tambem quando rebenta a
# meio (FECHAR-ONDA2, `ABORTED`); o Scrap nao escrevia nada, e uma onda social
# passava sem que ninguem pudesse provar o teto depois.
#
#     PEDIDO FEITO E PEDIDO CONTADO, MESMO QUANDO A CORRIDA MORRE.
#
# Quem conta e o portao (`scrap_http`), no sitio onde o pedido sai. Esta funcao so
# escreve. Uma fase cujos pedidos nao passam todos pelo portao (Instagram: janela,
# navegador, Reels) NAO leva `PEDIDOS_POR_HOST`: leva `PEDIDOS_NAO_CONTADOS`, e a
# prova diz NAO_SEI — contar so metade e dar zero ao resto.
FASES_CONTADAS = frozenset(f for f, v in FASES.items() if v[0] in ('LINKEDIN', 'YOUTUBE'))
LIVRO_DE_CORRIDAS = os.path.join('data', 'collection-ledger', 'italy', 'runs.ndjson')


def _agora():
    import datetime                                              # noqa: PLC0415
    return datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%fZ')


def linha_da_corrida(*, run_id, fase, fonte, inicio, abortada=None):
    """A linha desta corrida, com o que o portao contou ate agora."""
    import scrap_http as http                                    # noqa: PLC0415
    por_host, de_fora = http.pedidos_por_host()
    linha = {'RUN_ID': run_id, 'EXECUTOR_ID': EXECUTOR_ID, 'FASE': fase,
             'SOURCE_ID': fonte or rc.NAO_SEI, 'STARTED_AT': inicio,
             'FINISHED_AT': _agora()}
    nao_contados = list(de_fora)
    if fase not in FASES_CONTADAS:
        nao_contados.append('fase %s: os pedidos nao passam todos pelo portao' % fase)
    if nao_contados:
        linha['CORTESIA'] = {'PEDIDOS_NAO_CONTADOS': nao_contados,
                             'PEDIDOS_CONTADOS_PELO_PORTAO': por_host}
    else:
        linha['CORTESIA'] = {'PEDIDOS_POR_HOST': por_host,
                             'CONTADO_POR': 'scrap_http._ContaCadaPedido + yt-dlp --print-traffic'}
    # FREIO-SOCIAL: o que o freio recusou (nao saiu) fica escrito na linha, com o porque.
    import teto_da_onda as teto                                  # noqa: PLC0415
    recusadas = teto.recusas()
    if recusadas:
        linha['CORTESIA']['RECUSAS'] = recusadas
        linha['CORTESIA']['TETO_POR_DOMINIO'] = teto.teto()
    if abortada is not None:
        # Presente SO quando a corrida rebentou: a linha existe, mas nao e de sucesso.
        linha['ABORTED'] = {'SOURCE_ID': fonte or rc.NAO_SEI,
                            'ERRO': ('%s: %s' % (type(abortada).__name__, abortada))[:500]}
    return linha


def _livro_da_corrida_se_faltar(fase, run_id):
    """FREIO-SOCIAL: numa fase social SEM livro da onda, a corrida ganha um livro PROPRIO.

    O freio (`teto_da_onda`) so trava com livro. A onda nomeia o dela; uma corrida social
    pedida sozinha continua com o teto de 5 por dominio — no livro dela, que morre com ela.
    As outras fases nao mudam. → o caminho do livro criado aqui, ou None."""
    import re                                                    # noqa: PLC0415
    import tempfile                                              # noqa: PLC0415
    import teto_da_onda as teto                                  # noqa: PLC0415
    if fase not in FASES_CONTADAS or teto.livro():
        return None
    d = tempfile.mkdtemp(prefix='teto-corrida-')
    f = os.path.join(d, 'TETO-CORRIDA-%s.json' % re.sub(r'[^A-Za-z0-9_-]', '_', str(run_id)))
    os.environ[teto.ENV_LIVRO] = f
    return f


def _largar_livro_proprio(f):
    import shutil                                                # noqa: PLC0415
    import teto_da_onda as teto                                  # noqa: PLC0415
    if f and os.environ.get(teto.ENV_LIVRO) == f:
        os.environ.pop(teto.ENV_LIVRO, None)
        shutil.rmtree(os.path.dirname(f), True)


def escrever_linha(linha, raiz=None):
    """Acrescenta a linha ao livro de corridas (o mesmo do coletor web)."""
    raiz = raiz or os.environ.get('ITALY_OPS_ROOT') or RAIZ
    p = os.path.join(raiz, LIVRO_DE_CORRIDAS)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'a', encoding='utf-8') as f:
        f.write(json.dumps(linha, ensure_ascii=False) + '\n')
    return p


def main(argv=None):
    args = list(argv if argv is not None else sys.argv[1:])
    run_id = fonte = None
    nomeados = {}
    resto = []
    for a in args:
        if a.startswith('--run-id='):
            run_id = a.split('=', 1)[1].strip()
        elif a.startswith('--fonte='):
            fonte = a.split('=', 1)[1].strip() or None
        elif a.startswith('--') and '=' in a:
            # Um filtro nomeado qualquer. Nao se julga aqui se ele serve: a
            # fase ainda nao esta escolhida, e julgar antes de saber a fase
            # seria julgar contra a lista errada. Vazio = nao foi dado, e isso
            # e um valor (o teto vazio quer dizer «sem teto»).
            k, v = a[2:].split('=', 1)
            v = v.strip()
            if v:
                nomeados[k.strip().replace('-', '_')] = v
        else:
            resto.append(a)
    # Os filtros chegam POSICIONAIS, sem nome: e assim que o orquestrador
    # traduz `argumentos_de_filtros` para linha de comando, e e assim que o
    # `comunicacao-publica` ja os recebe. A ordem esta na receita.
    if resto and resto[0] in FASES:
        fase = resto[0]
        if fonte is None and len(resto) > 1:
            fonte = resto[1].strip() or None
    else:
        fase = resto[0] if resto else 'janela'
    if fase not in FASES:
        print('FASE_DESCONHECIDA=%s · as que existem: %s'
              % (fase, ', '.join(sorted(FASES))))
        return 2
    # ── AGORA SIM: A FASE ESTA ESCOLHIDA, E A LISTA DELA E QUE JULGA ───────
    aceites = NOMEADOS.get(fase, ())
    sobra = sorted(k for k in nomeados if k not in aceites)
    if sobra:
        print('FILTRO_NAO_ACEITE_NESTA_FASE=%s · a fase «%s» aceita: %s'
              % (', '.join(sobra), fase, ', '.join(aceites) or 'nenhum'))
        return 2
    falta = sorted(k for k in aceites if k not in nomeados and k != 'teto')
    if falta:
        # Um alvo em falta NAO se inventa a partir da fonte nem do nome da
        # fase. Sem ele nao ha a que bater, e isso diz-se antes de a corrida
        # comecar — e nao depois, com zero objetos e uma razao adivinhada.
        print('FILTRO_EM_FALTA=%s · a fase «%s» precisa dele para saber a que '
              'conta bater, e o adapter nao o deriva de --fonte' % (', '.join(falta), fase))
        return 2
    if not run_id:
        # Cunhar um aqui daria DUAS corridas canônicas para o mesmo acto.
        print('SEM_RUN_ID=o orquestrador é quem cunha a corrida; este adapter '
              'não a inventa')
        return 2

    # Os nomes publicos viram os nomes que a rota recebe, pela tabela da fase.
    # A contagem comeca do zero AQUI: e o que esta corrida pediu, e so isso.
    import scrap_http as http                                    # noqa: PLC0415
    import teto_da_onda as teto                                  # noqa: PLC0415
    http.zerar_contagem()
    teto.zerar()
    inicio = _agora()
    livro_proprio = _livro_da_corrida_se_faltar(fase, run_id)
    try:
        envelope = colher(fase, run_id=run_id, fonte=fonte,
                          **{aceites[k]: v for k, v in nomeados.items()})
    except BaseException as e:
        # A excepcao sobe na mesma DEPOIS da linha escrita: o codigo de saida
        # continua a dizer que falhou.
        escrever_linha(linha_da_corrida(run_id=run_id, fase=fase, fonte=fonte,
                                        inicio=inicio, abortada=e))
        _largar_livro_proprio(livro_proprio)
        raise
    escrever_linha(linha_da_corrida(run_id=run_id, fase=fase, fonte=fonte,
                                    inicio=inicio))
    _largar_livro_proprio(livro_proprio)
    caminho = escrever(envelope)
    mal = rc.conferir(envelope, RAIZ)

    print('SCRAP_COLHEITA')
    print('  fase          %s' % fase)
    print('  run_id        %s' % run_id)
    print('  source_id     %s' % (fonte or rc.NAO_SEI))
    print('  especie       %s' % envelope.get('ESPECIE_DA_FASE', rc.COLHEITA))
    for k in sorted(aceites):
        print('  %-13s %s' % (k, nomeados.get(k) or ('sem teto' if k == 'teto'
                                                     else rc.NAO_SEI)))
    print('  colheita      %d' % len(envelope['COLHEITA']))
    print('  suporte       %d' % len(envelope['SUPORTE']))
    print('  envelope      %s' % os.path.relpath(caminho, RAIZ))
    if envelope.get('PORQUE_ZERO_COLHEITA'):
        print('  porque zero   %s' % envelope['PORQUE_ZERO_COLHEITA'])
    for m in mal:
        print('  CONTRATO      %s' % m)
    return 0 if not mal else 1


if __name__ == '__main__':
    sys.exit(main())
