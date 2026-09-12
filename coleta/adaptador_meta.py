#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ADAPTADOR DA META — a superfície de transparência pública, e só ela.

    Ad Library            `graph:/ads_archive`
    Branded Content       `graph:/branded_content_search`

POR QUE `META` NÃO É UM GUARDA-CHUVA
-------------------------------------
Instagram, Facebook e Threads continuam a ser plataformas próprias, com os seus
adaptadores próprios. Nada deles se move para aqui.

    META = ONDE O OBJETO VIVE.   `publisher_platforms` = ONDE ELE APARECE.

Um anúncio da Ad Library aparece em Facebook, Instagram, Threads ou nas quatro
ao mesmo tempo. Declará-lo como observação de Instagram mentiria sobre metade
dos casos; como de Facebook, sobre a outra metade.

E ISTO NÃO É UM SEGUNDO RUNTIME
--------------------------------
Não há `meta_executor`, não há `meta_runtime`, não há orquestrador próprio. O
caminho é o mesmo de todas as outras plataformas desta casa:

    scrap_executor -> social_rotas -> scrap_registo -> ESTE ficheiro -> rota oficial

Este módulo não abre RUN, não liga checkpoint, não decide política e não conhece
Apify. Ele sabe UMA coisa que mais ninguém sabe: a semântica de um anúncio
público e de uma parceria paga na Meta.

O QUE ESTE ADAPTADOR RECUSA A FAZER
------------------------------------
    META AD != SALES          não diz venda
    META AD != MARKET SHARE   não diz participação
    META AD != CAMPAIGN SUCCESS  não diz que funcionou

Ele diz que o anúncio EXISTIU, quando, com que texto e em que superfícies. Ler
intenção nisso é Intelligence, e Intelligence não nasce aqui.

CAMPO AUSENTE É `UNKNOWN`, NUNCA `0` E NUNCA `false`
-----------------------------------------------------
A Meta não publica gasto comercial em país nenhum. `spend` e `impressions` são
só-político, e sempre em FAIXA. Escrever `0` onde a API não devolveu nada seria
inventar uma medição; escrever `false` seria pior, porque parece um facto.

    UNKNOWN != 0.   AUSENTE != FALSO.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import _gavetas  # noqa: E402,F401
import scrap_http as http      # noqa: E402
import scrap_registo as reg    # noqa: E402
import social_envelope as env  # noqa: E402

NOME = 'adaptador_meta'
PLATAFORMA = 'META'

#: O host oficial. Vive aqui e em mais lado nenhum — dois sítios com o mesmo
#: endereço são dois endereços no dia em que um deles mudar.
GRAPH = 'https://graph.facebook.com'
VERSAO = 'v21.0'

# ══════════════════════════════════════════════════════════════════════════
# O CONTRATO DE JANELA — E ELE É DO CALLER, NÃO NOSSO
# ══════════════════════════════════════════════════════════════════════════
# A janela comercial da Ad Library na UE é de UM ANO a contar da última
# impressão. O que não for colhido enquanto está lá desaparece e não volta.
#
#     DELTA AQUI NÃO É POUPANÇA. É A ÚNICA FORMA DE HAVER HISTÓRICO.
#
# Por isso o adaptador ACEITA janela. Ele não a inventa, não a guarda e não abre
# checkpoint: quem sabe o que já viu é quem chama. `conteudo_persistido()` em
# `coleta/coleta_checkpoint.py` é a resposta canônica de `KNOWN_IDS`, e continua
# a ser dele — este ficheiro só recebe o conjunto pronto.
#
#     O CALLER FORNECE JANELA E ESTADO. O SCRAP RESPEITA.
JANELA = ('SINCE', 'UNTIL', 'LAST_SEEN_TIME', 'KNOWN_IDS', 'MAX_ITEMS')

#: Quem impôs a janela: a FONTE (a API filtrou) ou NÓS (filtrámos cá).
#: Sem este campo, «5 objetos» não se distingue de «5 objetos novos».
POR_FONTE = 'SOURCE'
POR_NOS = 'LOCAL'


class JanelaInvalida(ValueError):
    """Parâmetro de janela fora do vocabulário fechado."""


def conferir_janela(janela):
    """Recusa nome de janela inventado. → o dicionário, validado."""
    j = dict(janela or {})
    for k in j:
        if k not in JANELA:
            raise JanelaInvalida(
                '%r nao esta no contrato de janela. Os cinco sao %s. Inventar um '
                'sexto nome aqui faria o proximo adaptador inventar um setimo.'
                % (k, ', '.join(JANELA)))
    ids = j.get('KNOWN_IDS')
    if ids is not None and not isinstance(ids, (set, frozenset, list, tuple)):
        raise JanelaInvalida('KNOWN_IDS tem de ser um conjunto de ids, nao %r'
                             % type(ids).__name__)
    return j


def _ja_conhecido(nativo, janela):
    """Este id já está em casa? `KNOWN_IDS` ausente é «não perguntei»."""
    ids = janela.get('KNOWN_IDS')
    if ids is None:
        return False
    return str(nativo) in {str(x) for x in ids}


def _fonte_dos_conhecidos(janela):
    """De onde veio `KNOWN_IDS`. Conjunto vazio NÃO é «nada conhecido»."""
    if janela.get('KNOWN_IDS') is None:
        return 'NOT_ASKED'
    return 'CALLER'


# ══════════════════════════════════════════════════════════════════════════
# AD LIBRARY
# ══════════════════════════════════════════════════════════════════════════
# OS CAMPOS SÃO OS QUE A DOCUMENTAÇÃO SUPORTA, E MAIS NENHUM.
#
# Medidos na META-DEEP-01 contra a referência primária do nó `ArchivedAd`. Os
# quatro primeiros são os únicos que voltam sem se pedir `fields`.
#
# ⚠️ O NOME DO CAMPO DE IDENTIDADE É `id`, NÃO `ad_archive_id`. O segundo é o
# nome do endpoint INTERNO que a UI chama, e é o que as bibliotecas de scraping
# usam. Carimbá-lo no nosso esquema seria gravar, no contrato oficial, o nome de
# uma rota que não é a oficial.
CAMPOS_ANUNCIO = (
    'id', 'page_id', 'page_name',
    'ad_creative_bodies', 'ad_creative_link_titles',
    'ad_creative_link_descriptions', 'ad_creative_link_captions',
    'ad_snapshot_url',
    'ad_delivery_start_time', 'ad_delivery_stop_time', 'ad_creation_time',
    'publisher_platforms', 'languages',
)

#: Campos que SÓ existem para anúncio entregue na UE. Viajam com rótulo próprio
#: — um campo de UE que perde o rótulo vira um campo global que não existe.
CAMPOS_UE = ('eu_total_reach', 'beneficiary_payers', 'target_ages',
             'target_gender', 'target_locations',
             'age_country_gender_reach_breakdown', 'total_reach_by_location')

#: Campos que NUNCA voltam para anúncio comercial. Estão aqui para serem
#: RECUSADOS, não pedidos: pedi-los devolve erro ou silêncio, e o silêncio é o
#: que vira `0` na cabeça de quem lê.
SO_POLITICO = ('spend', 'impressions', 'currency', 'estimated_audience_size',
               'demographic_distribution', 'delivery_by_region', 'bylines')


def _url_ads(*, paises, page_ids=None, termos=None, estado='ACTIVE', janela=None):
    """Monta a consulta. `ad_reached_countries` é obrigatório pela Meta."""
    if not paises:
        raise ValueError('ad_reached_countries e OBRIGATORIO na Ad Library. '
                         'Sem pais nao ha consulta — a Meta recusa.')
    j = janela or {}
    campos = ','.join(CAMPOS_ANUNCIO + CAMPOS_UE)
    q = ['ad_reached_countries=%s' % json.dumps(list(paises)),
         'ad_active_status=%s' % estado, 'fields=%s' % campos]
    if page_ids:
        # A Meta aceita ATÉ DEZ. Cortar em silêncio esconderia metade do alvo.
        if len(page_ids) > 10:
            raise ValueError('search_page_ids aceita ate 10 ids; vieram %d. '
                             'Dividir o lote e do caller, nao deste ficheiro.'
                             % len(page_ids))
        q.append('search_page_ids=%s' % json.dumps([str(i) for i in page_ids]))
    if termos:
        if len(termos) > 100:
            raise ValueError('search_terms tem limite de 100 caracteres; vieram %d'
                             % len(termos))
        q.append('search_terms=%s' % termos)
    # A JANELA VAI PARA A FONTE QUANDO A FONTE A SABE APLICAR.
    if j.get('SINCE'):
        q.append('ad_delivery_date_min=%s' % j['SINCE'])
    if j.get('UNTIL'):
        q.append('ad_delivery_date_max=%s' % j['UNTIL'])
    return '%s/%s/ads_archive?%s' % (GRAPH, VERSAO, '&'.join(q))


def _anuncio(item, *, run_id, country_scope, rota):
    """Um anúncio observado → envelope canônico. Campo ausente vira UNKNOWN."""
    corpos = item.get('ad_creative_bodies') or []
    return env.envelope(
        platform=PLATAFORMA,
        native_id=item.get('id'),
        url=item.get('ad_snapshot_url') or env.DESCONHECIDO,
        # A espécie é ADVERTISEMENT, e não POST. Somar os dois daria um número
        # que não é nem um nem outro.
        content_type='ADVERTISEMENT',
        route=rota, executor='coleta/adaptador_meta.py',
        run_id=run_id, country_scope=country_scope,
        source_account=item.get('page_name') or env.DESCONHECIDO,
        published_at=item.get('ad_delivery_start_time') or None,
        # O texto do criativo é uma LISTA — um por cartão de carrossel. Juntar
        # com quebra de linha preserva a contagem; juntar com espaço perdia-a.
        text='\n'.join(corpos) if corpos else None,
        title=(item.get('ad_creative_link_titles') or [None])[0],
        raw=item)


def ads_search(*, run_id, country_scope='IT', medida=None, etapa=None,
               paises=None, page_ids=None, termos=None, estado='ACTIVE',
               janela=None, transporte=None, **_):
    """`SEARCH_ADS` — anúncios públicos de concorrente, pela Ad Library.

    `transporte` existe para a prova OFFLINE: é o mesmo contrato de
    `scrap_http.buscar`, e o padrão continua a ser ele. Um adaptador que só
    funcionasse com rede real não poderia ser provado sem gastar.
    """
    j = conferir_janela(janela)
    buscar = transporte or http.buscar
    url = _url_ads(paises=paises or [country_scope], page_ids=page_ids,
                   termos=termos, estado=estado, janela=j)
    corpo = buscar(url)
    dados = json.loads(corpo) if isinstance(corpo, str) else corpo
    itens = dados.get('data') or []
    # ── A JANELA QUE A FONTE NÃO APLICOU, APLICAMOS NÓS — E DIZEMOS QUAL ────
    por = POR_FONTE if (j.get('SINCE') or j.get('UNTIL')) else POR_NOS
    saida, pulados = [], 0
    for it in itens:
        if _ja_conhecido(it.get('id'), j):
            pulados += 1
            continue
        if j.get('LAST_SEEN_TIME') and it.get('ad_delivery_start_time'):
            if str(it['ad_delivery_start_time']) <= str(j['LAST_SEEN_TIME']):
                pulados += 1
                por = POR_NOS
                continue
        saida.append(_anuncio(it, run_id=run_id, country_scope=country_scope,
                              rota='graph:/ads_archive'))
        if j.get('MAX_ITEMS') and len(saida) >= int(j['MAX_ITEMS']):
            break
    if medida is not None:
        medida['IMPLEMENTACAO'] = 'coleta/adaptador_meta.py'
        medida['ROUTE_CLASS'] = 'OFFICIAL_API_FREE'
        medida['APIFY_RUNS'] = 0
        medida['COST_USD'] = 0
        medida['WINDOW_ENFORCED_BY'] = por
        medida['KNOWN_IDS_SOURCE'] = _fonte_dos_conhecidos(j)
        medida['SKIPPED_ALREADY_KNOWN'] = pulados
        # `MAX_ITEMS` atingido é um RESULTADO, não um fim. Quem para no tecto e
        # não o diz abre um buraco que ninguém vê.
        medida['TRUNCATED_BY_MAX_ITEMS'] = bool(
            j.get('MAX_ITEMS') and len(saida) >= int(j['MAX_ITEMS'])
            and len(itens) - pulados > len(saida))
    return saida


# ══════════════════════════════════════════════════════════════════════════
# BRANDED CONTENT
# ══════════════════════════════════════════════════════════════════════════
# CINCO CAMPOS. NEM UM A MAIS.
#
# A doc do nó devolve `creation_date`, `creator`, `partners`, `type` e `url`.
# NÃO devolve legenda, mídia, país nem métrica — e a ausência é parte do achado,
# não um defeito a tapar. Enriquecer daqui seria adivinhar.
CAMPOS_BRANDED = ('creation_date', 'creator', 'partners', 'type', 'url')

#: O que a Meta NÃO devolve neste nó. Existe para que ninguém tente pedir.
BRANDED_AUSENTES = ('caption', 'media', 'country', 'metrics', 'spend')


def _branded(item, *, run_id, country_scope, rota):
    """Uma parceria observada → envelope. O AUTOR e o PAGADOR são pessoas diferentes."""
    criador = item.get('creator') or {}
    parceiros = item.get('partners') or []
    return env.envelope(
        platform=PLATAFORMA,
        # Não há id próprio no nó: a identidade é o permalink do post.
        native_id=item.get('url') or env.DESCONHECIDO,
        url=item.get('url') or env.DESCONHECIDO,
        content_type='BRANDED_CONTENT',
        route=rota, executor='coleta/adaptador_meta.py',
        run_id=run_id, country_scope=country_scope,
        # `SOURCE_ACCOUNT` é quem PUBLICOU — o criador. A marca que pagou vive
        # no RAW, em `partners`, e não se promove a autor.
        #     BRAND_PARTNER != POST_AUTHOR.
        source_account=criador.get('name') or env.DESCONHECIDO,
        published_at=item.get('creation_date') or None,
        # SEM legenda. A Meta não a devolve aqui, e inventar `text` a partir do
        # nome do criador seria fabricar conteúdo.
        text=None,
        title=None,
        raw={'creator': criador, 'partners': parceiros,
             'type': item.get('type') or env.DESCONHECIDO,
             'creation_date': item.get('creation_date') or env.DESCONHECIDO,
             'url': item.get('url') or env.DESCONHECIDO,
             # O que a fonte NÃO deu fica dito, para que ninguém leia a ausência
             # como um zero.
             'NOT_RETURNED_BY_SOURCE': list(BRANDED_AUSENTES)})


def branded_search(*, run_id, country_scope='IT', medida=None, etapa=None,
                   ig_username=None, page_url=None, janela=None,
                   transporte=None, **_):
    """`SEARCH_BRANDED_CONTENT` — parcerias pagas em que a marca aparece.

    A frase que torna isto uma ferramenta de concorrência está na doc da Meta:
    «Search for an Instagram account that posted branded content OR WAS A BRAND
    PARTNER». Passa-se o endereço do concorrente e voltam os criadores que ele
    pagou.
    """
    j = conferir_janela(janela)
    if not (ig_username or page_url):
        raise ValueError('branded_content_search precisa de ig_username OU page_url')
    if not (j.get('SINCE') and j.get('UNTIL')):
        # Os dois são OBRIGATÓRIOS na Meta. Inventar um default aqui esconderia
        # a obrigação e produziria uma janela que ninguém escolheu.
        raise JanelaInvalida(
            'creation_date_min e creation_date_max sao OBRIGATORIOS neste no. '
            'Passe SINCE e UNTIL — um default inventado aqui seria uma janela '
            'que ninguem escolheu.')
    buscar = transporte or http.buscar
    q = ['creation_date_min=%s' % j['SINCE'], 'creation_date_max=%s' % j['UNTIL'],
         'fields=%s' % ','.join(CAMPOS_BRANDED)]
    q.append('ig_username=%s' % ig_username if ig_username else 'page_url=%s' % page_url)
    url = '%s/%s/branded_content_search?%s' % (GRAPH, VERSAO, '&'.join(q))
    corpo = buscar(url)
    dados = json.loads(corpo) if isinstance(corpo, str) else corpo
    saida, pulados = [], 0
    for it in (dados.get('data') or []):
        if _ja_conhecido(it.get('url'), j):
            pulados += 1
            continue
        saida.append(_branded(it, run_id=run_id, country_scope=country_scope,
                              rota='graph:/branded_content_search'))
        if j.get('MAX_ITEMS') and len(saida) >= int(j['MAX_ITEMS']):
            break
    if medida is not None:
        medida['IMPLEMENTACAO'] = 'coleta/adaptador_meta.py'
        medida['ROUTE_CLASS'] = 'OFFICIAL_API_FREE'
        medida['APIFY_RUNS'] = 0
        medida['COST_USD'] = 0
        # Aqui a janela é SEMPRE da fonte: os dois campos são obrigatórios.
        medida['WINDOW_ENFORCED_BY'] = POR_FONTE
        medida['KNOWN_IDS_SOURCE'] = _fonte_dos_conhecidos(j)
        medida['SKIPPED_ALREADY_KNOWN'] = pulados
    return saida


# ══════════════════════════════════════════════════════════════════════════
# A SONDA GRATUITA — «consigo chegar lá AGORA?», sem gastar nada
# ══════════════════════════════════════════════════════════════════════════
# Ela lê configuração e NUNCA chama rota. É do adaptador porque só ele sabe o
# que a sua plataforma precisa ter em mãos.
#
# A Ad Library não se abre com uma chave de API: a Meta exige CONFIRMAÇÃO DE
# IDENTIDADE do utilizador, um app, e um token gerado a partir disso. E a
# página do nó `branded_content_search` não documenta sequer QUE token aceita.
#
#     O PREÇO DESTAS DUAS ROTAS NÃO É DINHEIRO. É IDENTIDADE CONFIRMADA.
#
# Enquanto não houver variável de ambiente com esse token, a resposta honesta é
# `CREDENTIAL_MISSING` — e é ela que impede o roteador de sair para a rede por
# uma porta que não abre.
#
# A sonda NUNCA devolve o valor do segredo. Devolve `(bool, estado)`.
TOKEN_ENV = 'META_GRAPH_TOKEN'


def credencial_presente():
    """Há token da Graph API neste ambiente? Zero rede, zero dólar, zero segredo."""
    return bool(os.environ.get(TOKEN_ENV, '').strip())


def pronto_para_graph(**_):
    """→ (consigo?, estado). O estado é escrito aqui, nunca derivado do segredo."""
    return (credencial_presente(), 'CREDENTIAL_MISSING')


# ══════════════════════════════════════════════════════════════════════════
# O QUE ESTE ADAPTADOR DECLARA
# ══════════════════════════════════════════════════════════════════════════
# As duas têm `rota`, e não `executa`: a matriz conhece-as, logo elas entram
# pelo caminho canônico — executor, roteador, portão — e o trace nasce do
# registo que o roteador sela.
#
# E as duas estão `NOT_EXECUTED` em `scrap_capacidades.py`. Registá-las NÃO as
# promove: o `CHECK` recusa-as com `CAPABILITY_STATE_PROMISES_NOTHING` até que
# gente as corra ao vivo e escreva a prova.
#
#     UM ADAPTADOR PODE EXISTIR SEM PROMETER. Não pode é existir prometendo.
reg.registar(PLATAFORMA, 'meta.ads.search', adaptador=NOME,
             rota=ads_search, pronto=pronto_para_graph,
             nota='Ad Library oficial; zero dolar e credencial em falta. '
                  'Janela comercial UE = 1 ano da ultima impressao.')
reg.registar(PLATAFORMA, 'meta.branded_content.search', adaptador=NOME,
             rota=branded_search, pronto=pronto_para_graph,
             nota='parceria paga pelo lado da marca; AUTH nao documentada pela Meta')
