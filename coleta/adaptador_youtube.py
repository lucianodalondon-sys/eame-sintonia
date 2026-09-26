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
import social_envelope as env  # noqa: E402  — o envelope canonico

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
# ── O MEDIDOR — dois baldes, e eles NAO se somam ──────────────────────────
# `youtube_oficial.Sessao` ja conta o que gastou, e o ficheiro dele diz porque
# sao dois contadores e nao um: «um contador unico faria a busca comer o
# orcamento de comentarios — e, pior, faria o relatorio somar dois numeros que
# nao se somam».
#
#     SEARCH  conta CHAMADAS   ·  100 por dia
#     GENERAL conta UNIDADES   ·  10.000 por dia
#
# A conta morria aqui: a sessao era local a chamada e o numero ia com ela. Quem
# lia o artefato via um campo de quota escrito a mao pelo caller — e escrito a
# mao e suposto, por melhor que seja o palpite.
#
#     QUEM GASTA E QUEM SABE QUANTO. O CALLER SO PODE COPIAR OU INVENTAR.
#
# O balde `medida` vem do roteador e e generico: ele nao sabe o nome «YouTube»
# nem o nome «unidade». Quem o enche e o dono da chamada.
def _medir(medida, sessao, antes):
    """Escreve no balde o que ESTA chamada gastou. Nunca o acumulado da sessao."""
    if medida is None or sessao is None:
        return
    usado = getattr(sessao, 'usado', None)
    if not usado:
        return
    import youtube_oficial as yt
    antes = antes or {}
    geral = usado.get(yt.GENERAL, 0) - antes.get(yt.GENERAL, 0)
    busca = usado.get(yt.SEARCH, 0) - antes.get(yt.SEARCH, 0)
    # O campo historico `QUOTA_UNITS` E o balde GENERAL, e continua a se-lo.
    # A busca ganha campo PROPRIO: somar as duas daria um numero que nao existe.
    medida['QUOTA_UNITS'] = geral
    medida['QUOTA_SEARCH_CALLS'] = busca


def _antes(sessao):
    return dict(getattr(sessao, 'usado', {}) or {}) if sessao is not None else {}


@_traduzido
def youtube_buscar(*, termo, run_id, country_scope, limit=25, sessao=None,
                   medida=None, **_):
    import youtube_oficial as yt
    antes, s = _antes(sessao), sessao
    try:
        objs, s = yt.buscar(termo=termo, run_id=run_id, country_scope=country_scope,
                            limit=limit, regiao=country_scope, idioma='it',
                            sessao=sessao)
    finally:
        # `finally` porque QUEM GASTOU E LEVOU 403 GASTOU NA MESMA. Apagar a
        # medida na recusa faria a execucao parecer de graca.
        _medir(medida, s, antes)
    return objs


@_traduzido
def youtube_uploads(*, channel_id, run_id, country_scope, limit=25, conhecidos=(),
                    sessao=None, medida=None, **_):
    import youtube_oficial as yt
    antes, s = _antes(sessao), sessao
    try:
        objs, s, _rel = yt.uploads_recentes(
            channel_id=channel_id, run_id=run_id, country_scope=country_scope,
            limit=limit, conhecidos=conhecidos, sessao=sessao)
    finally:
        _medir(medida, s, antes)
    return objs


@_traduzido
def youtube_metadata(*, video_ids, run_id, country_scope, sessao=None,
                     medida=None, **_):
    import youtube_oficial as yt
    antes, s = _antes(sessao), sessao
    try:
        objs, s, _rel = yt.metadata(video_ids=video_ids, run_id=run_id,
                                    country_scope=country_scope, sessao=sessao)
    finally:
        _medir(medida, s, antes)
    return objs


@_traduzido
def youtube_comentarios(*, video_id, run_id, country_scope, limite_threads=100,
                        sessao=None, medida=None, **_):
    import youtube_oficial as yt
    antes, s = _antes(sessao), sessao
    try:
        objs, s, rel = yt.comentarios(video_id=video_id, run_id=run_id,
                                      country_scope=country_scope,
                                      limite_threads=limite_threads, sessao=sessao)
    finally:
        _medir(medida, s, antes)
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
# A LEGENDA PAGA — O ADAPTADOR SABE YOUTUBE, QUEM PAGA E O COLETOR
# ══════════════════════════════════════════════════════════════════════════
# A matriz declara `apify:transcricao` como a UNICA rota restante para legenda
# de canal de terceiro: `captions.download` exige ser dono do video,
# `captions.list` exige autorizacao, e `timedtext` sem assinatura devolve corpo
# vazio. Nenhuma delas e uma rota que esta casa possa andar.
#
# TRES PAPEIS, E ELES NAO SE MISTURAM
# -------------------------------------
#     ADAPTER   sabe o que e um video do YouTube e como se le uma legenda
#     PROVIDER  e a Apify, e quem fala com ela e `coleta/coletor.py`
#     ROUTER    decide se a rota paga esta autorizada e com que motivo
#
#     ADAPTER != PROVIDER != EXECUTION ENVIRONMENT.
#
# Por isso esta funcao NAO conhece `api.apify.com`, nao monta cabecalho, nao le
# `usageTotalUsd` e nao sabe o que e `maxTotalChargeUsd`. Ela monta a entrada do
# ator, chama o dono pago, e traduz a saida para o envelope canonico.
#
# O CONTRATO DA ENTRADA MUDOU, E A CASA MEDIU ISSO
# --------------------------------------------------
# `videoUrls` (plural, uma lista) foi o que rodou em Espanha e esta no
# RUN-MANIFEST. Hoje o ator exige `videoUrl` no SINGULAR — e quem descobriu
# isso foi a propria recusa da API, `HTTP 400 invalid-input`, gravada inteira no
# manifesto por `regras/sensor_coleta.py`.
#
#     ENTRADA PROVADA ONTEM != ENTRADA VALIDA HOJE.
#
# UMA CHAVE, E NAO A ROTACAO
# ----------------------------
# `apify_pool` roda chaves quando uma esgota. Rodar aqui seria um SEGUNDO POST
# de criacao de execucao — e um segundo POST e uma segunda execucao paga, mesmo
# que a primeira nao tenha devolvido `run_id`.
#
#     ROTACAO DE CHAVE E UMA SEGUNDA COMPRA.
#
# Entao esta rota usa a primeira posicao e para. Quem quiser rotacao numa rota
# paga tem de declarar quantas compras autoriza, e isso e decisao de gente.
ATOR_TRANSCRICAO = 'pintostudio~youtube-transcript-scraper'
ROTA_TRANSCRICAO = 'apify:transcricao'

#: O que o ator devolve, medido nos bytes preservados de
#: `data/samples/raw-paid/ES-T8-001-youtube-transcripts.raw.json.gz`:
#: uma lista de `{url, transcript, chars}`. Sem campo de lingua, sem marcas de
#: tempo e sem dizer se o texto veio da legenda do YouTube ou de um ASR dele.
#:
#:     O QUE O PROVIDER NAO DECLARA, A CASA NAO INVENTA.
CAMPOS_DO_ATOR = ('url', 'transcript', 'chars')

#: A especie do texto. O ator nao a declara, e chamar-lhe `TRANSCRIPT` seria
#: afirmar uma origem que ninguem mediu.
#:
#:     CAPTION != TRANSCRIPT != ASR.
ESPECIE_NAO_DECLARADA = 'NOT_DECLARED_BY_PROVIDER'


def _url_de_video(video_url=None, video_id=None):
    """→ a URL `watch?v=` do alvo. Uma so, e nunca uma lista."""
    if video_url:
        return video_url
    if not video_id:
        raise ValueError('a legenda paga precisa de `video_url` ou `video_id`')
    return 'https://www.youtube.com/watch?v=%s' % video_id


def _id_do_video(url):
    m = re.search(r'[?&]v=([A-Za-z0-9_-]{6,})', url or '')
    return m.group(1) if m else None


def credencial_paga_presente():
    """→ (ha chave?, estado). Le o ambiente pelo dono unico. Zero rede, zero dolar.

    Nunca devolve a chave, nem o tamanho, nem um prefixo dela. Um comprimento
    com prefixo e meio segredo, e meio segredo num log e um segredo num log.
    """
    import apify_pool as ap
    return (bool(ap.pool()), 'CREDENTIAL_MISSING')


def youtube_legenda_paga(*, run_id, country_scope='IT', video_url=None,
                         video_id=None, medida=None, teto_usd=None,
                         modo=None, autorizacao=None, source_id=None,
                         proposito=None, **_):
    """A rota paga da legenda. → lista de envelopes canonicos.

    O `teto_usd` por omissao e `None`, e quando o chamador nao o nomeia pede-se
    o que a AUTORIZACAO permite — que e o maximo que se poderia pedir, e nao um
    numero escrito aqui. O orcamento financeiro rebaixa-o depois ao saldo.

        PROVIDER CAP <= AUTORIZADO <= EXECUTION REMAINING.
    """
    import apify_pool as ap
    import coletor as ct
    url = _url_de_video(video_url, video_id)

    # ── A CREDENCIAL E UM PORTAO, E ELE VEM ANTES DO DINHEIRO ──────────────
    # Sem chave nao ha compra nenhuma para autorizar. Levantar aqui faz a
    # recusa chegar ao roteador como ESTADO — `CREDENTIAL_MISSING`, cuja
    # recuperacao canonica e `HUMAN_PROVISION_CREDENTIAL` — em vez de morrer
    # como excecao de um `except` largo.
    chaves = ap.pool()
    if not chaves:
        raise http.EstadoDaApi({
            'STATE': 'CREDENTIAL_MISSING',
            'NATIVE_REASON': 'APIFY_TOKEN_POOL vazio neste ambiente',
            'RECOVERY_ACTION': 'HUMAN_PROVISION_CREDENTIAL'})

    itens, man = ct.executar(
        ATOR_TRANSCRICAO, {'videoUrl': url},
        token=chaves[0],                      # a primeira, e so ela — ver acima
        run_id=run_id, platform=PLATAFORMA, country=country_scope,
        mission='C10-8B', query=url,
        # ── A AUTORIZACAO DESCE, E NAO NASCE AQUI ─────────────────────────
        # Um adaptador que fabricasse a sua propria autorizacao seria um
        # adaptador que se autoriza a si proprio a gastar.
        #
        #     QUEM PEDE A COMPRA NAO E QUEM A AUTORIZA.
        #
        # `modo=None` vira o default do `coletor` (NORMAL), que exige o «sim»
        # da relevancia. Nunca se inventa TRIAL aqui para atalhar.
        **({'modo': modo} if modo else {}),
        # O PROPOSITO vem da autorizacao quando o chamador nao o nomeia: e o
        # mesmo objecto que autoriza, e ler dele nao e inventar.
        autorizacao=autorizacao, source_id=source_id,
        proposito=proposito or getattr(autorizacao, 'proposito', None),
        # ── O TETO DO LADO DO FORNECEDOR, PEDIDO E NAO ASSUMIDO ───────────
        # `teto_usd` nascia `None` aqui de proposito, para o orcamento
        # financeiro decidir. Desde a SCRAP-OWNER-01 ha um numero anterior a
        # ele: o que foi AUTORIZADO. Pedir esse e pedir o maximo que se
        # poderia pedir — e o orcamento continua a rebaixa-lo ao saldo.
        #
        #     PROVIDER CAP <= AUTORIZADO <= EXECUTION REMAINING.
        teto_usd=(teto_usd if teto_usd is not None
                  else getattr(autorizacao, 'max_usd', None)),
        source_version='ator %s, captura de %s' % (ATOR_TRANSCRICAO,
                                                   ct.agora()[:10]),
        # A ROTA e o nome que a matriz lhe da. Mandar o caminho da evidencia
        # punha um ficheiro no campo que devia ter uma rota.
        rota=ROTA_TRANSCRICAO,
        evidence_path='data/samples/SCRAP-YOUTUBE/LEGENDA-PAGA.json',
        # ── O `wait` E O QUE DECIDE O TETO DE REDE DESTA ROTA ──────────────
        # A plataforma concede 60 s no proprio POST. Tudo acima disso vira
        # CONSULTA, e cada consulta e uma ida a rede. Com `wait=60` o resto e
        # zero e ha no maximo UMA consulta; com 120 haveria ate treze.
        #
        #     UM `wait` MAIOR NAO E MAIS PACIENCIA. E MAIS IDAS A REDE.
        #
        # As corridas historicas deste ator terminaram em segundos, entao 60 s
        # cobrem o caso medido — e se nao cobrirem, o retrato sai marcado como
        # `PARTIAL_RUN_WAS_NOT_TERMINAL`, que e a verdade, e NAO se compra
        # outra vez.
        wait=60)

    # ── A MEDIDA SOBE PELO BALDE, QUE E O CANAL QUE JA EXISTE ──────────────
    # O roteador nao sabe o preco de uma chamada; quem sabe e quem a fez. E o
    # que sobe e o que o dono do dinheiro escreveu, nao um numero deste
    # ficheiro.
    if medida is not None:
        r = man.get('FINANCIAL_RESERVATION') or {}
        medida['IMPLEMENTACAO'] = 'coleta/coletor.py'
        medida['ROUTE_CLASS'] = 'APIFY'
        medida['APIFY_RUNS'] = 1
        medida['PROVIDER_RUN_ID'] = man.get('RUN_ID')
        medida['PROVIDER_STATUS'] = man.get('PLATFORM_STATUS')
        medida['SCRAP_RAW_REFERENCE'] = man.get('RAW_EVIDENCE_PATH')
        medida['SCRAP_RAW_STATE'] = man.get('RAW_EVIDENCE_STATE')
        medida['SCRAP_RAW_SHA256'] = man.get('RAW_SHA256')
        medida['COST_STATE'] = r.get('COST_STATE', 'UNKNOWN')
        medida['ACTUAL_COST_USD'] = r.get('ACTUAL_COST_USD')
        medida['PROVIDER_SIDE_CAP_USD'] = r.get('PROVIDER_SIDE_CAP')
        medida['FINANCIAL_RESERVATION'] = r

    if man.get('STATUS') == 'FAILED':
        # Falha da rota e ESTADO, e o estado tem o nome que a plataforma deu.
        raise http.EstadoDaApi({
            'STATE': 'ROUTE_UNAVAILABLE',
            'NATIVE_REASON': str(man.get('ERROR'))[:200],
            'RECOVERY_ACTION': 'NEEDS_HUMAN_FIX'})

    saida = []
    for it in (itens or []):
        if not isinstance(it, dict):
            continue
        texto = it.get('transcript')
        alvo = it.get('url') or url
        saida.append(env.envelope(
            platform=PLATAFORMA, native_id=_id_do_video(alvo) or alvo, url=alvo,
            content_type='VIDEO', route=ROTA_TRANSCRICAO,
            executor='adaptador_youtube.youtube_legenda_paga',
            run_id=run_id, country_scope=country_scope,
            # O ator nao devolve lingua. Deixar `None` faz o envelope escrever
            # o desconhecido dele, que e o unico valor honesto aqui.
            language=None, text=texto or None,
            raw_reference=man.get('RAW_EVIDENCE_PATH'),
            raw={'CHARS': it.get('chars'),
                 'TRANSCRIPT_PRESENT': bool(texto),
                 'SPECIES': ESPECIE_NAO_DECLARADA,
                 'TIMESTAMPS': False,
                 'PROVIDER': 'APIFY', 'ACTOR': ATOR_TRANSCRICAO}))
    return saida


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
# AUDIO PUBLICO — a rota do C13, ligada pelo caminho canonico
# ══════════════════════════════════════════════════════════════════════════
# A IMPLEMENTACAO NAO VIVE AQUI, E NAO FOI RECRIADA. Ela ja existia em
# `ferramentas/youtube_transcrever.py::_audio`, ja foi provada ponta a ponta no
# C13 (bytes, SHA, ffprobe, ASR), e esta rota LIMITA-SE A CHAMA-LA.
#
#     UM DOWNLOADER NOVO SERIA UMA SEGUNDA VERDADE SOBRE A MESMA AQUISICAO.
#
# O que esta funcao acrescenta e o que faltava: o EDGE. Resolver o alvo,
# MEDIR o que chegou, montar o objeto da capability e — quando falha — dizer
# QUAL foi a falha, em vez de devolver uma lista vazia que o roteador leria
# como `ZERO_RESULTS`.
#
#     AUDIO_NAO_OBTIDO != ZERO_RESULTS.
#     «NAO CONSEGUI O SOM» NAO E «ESTE VIDEO ESTA CALADO».
ROTA_AUDIO_PUBLICO = 'yt-dlp:public_audio'
LIMITE_AUDIO_PUBLICO = 'PUBLIC_AUDIO_ONLY'

#: Estados proprios desta rota. NAO sao estados canonicos de falha — sao o
#: nome nativo que viaja ao lado do canonico, em `NATIVE_REASON`.
AUDIO_ADQUIRIDO = 'AUDIO_ADQUIRIDO'
AUDIO_NAO_OBTIDO = 'AUDIO_NAO_OBTIDO'
VIDEO_ID_AUSENTE = 'VIDEO_ID_AUSENTE'
MEDIA_KIND_DIVERGE = 'MEDIA_KIND_MISMATCH'

#: O VIDEO_ID do YouTube tem 11 caracteres desta familia. Validar a FORMA nao
#: e fabricar identidade: e recusar o que nao tem forma de id.
_ID_DO_YOUTUBE = re.compile(r'^[A-Za-z0-9_-]{11}$')


def _video_id_de(video_id=None, video_url=None):
    """→ o VIDEO_ID comprovado, ou None. NUNCA fabrica identidade.

    Aceita o id dado, ou extrai-o do `v=` de um endereco de video. O que ele
    NAO faz — e nao pode fazer — e derivar um id de um titulo, de um slug, de
    um caminho ou de um hash. Sem id comprovado, a resposta e `None`, e quem
    chamou recebe uma recusa com nome.
    """
    if video_id:
        v = str(video_id).strip()
        return v if _ID_DO_YOUTUBE.match(v) else None
    if video_url:
        import urllib.parse as up
        alvo = str(video_url).strip()
        v = (up.parse_qs(up.urlparse(alvo).query).get('v') or [''])[0].strip()
        return v if _ID_DO_YOUTUBE.match(v) else None
    return None


def pronto_para_audio_publico(**_):
    """→ (consigo?, estado). ZERO rede, ZERO download, ZERO dolar.

    A pergunta que este CHECK responde e «consigo chegar la AGORA», e uma rota
    local sem as ferramentas dela nao chega a lado nenhum. Descobrir que falta
    o `yt-dlp` DEPOIS de tentar baixar seria descobri-lo tarde.

    Nao toca a rede: so olha para o que esta instalado.
    """
    import shutil
    faltam = [n for n in ('yt-dlp', 'ffmpeg', 'ffprobe') if not shutil.which(n)]
    if faltam:
        return (False, 'EXECUTOR_UNAVAILABLE')
    return (True, '')


def _classificar_falha(motivo):
    """Traduz a falha da aquisicao para o vocabulario canonico de `leis/falhas`.

    Tres causas, tres nomes, e nenhuma delas e `ZERO_RESULTS`:

        o video nao existe / e privado / foi removido   -> SOURCE_GONE
        a ferramenta local nao respondeu                -> EXECUTOR_UNAVAILABLE
        o resto (a fonte nao serviu o som agora)        -> SOURCE_UNAVAILABLE
    """
    m = str(motivo or '').lower()
    if any(x in m for x in ('unavailable', 'private', 'removed', 'deleted',
                            'terminated', 'does not exist')):
        return 'SOURCE_GONE'
    if any(x in m for x in ('estourou o tempo', 'not found', 'no such file',
                            'command not found')):
        return 'EXECUTOR_UNAVAILABLE'
    return 'SOURCE_UNAVAILABLE'


def youtube_audio_publico(*, run_id, country_scope, video_id=None, video_url=None,
                          medida=None, **_):
    """A rota do audio publico. → lista de objetos da capability.

    FRONTEIRA, e ela sobrevive na declaracao da matriz: so alvo PUBLICO. Sem
    conta, sem cookie de terceiro, sem CAPTCHA, sem token de sessao, sem
    contornar paywall ou acesso privado. Esta funcao nao tem — e nao pode
    ganhar — parametro de sessao.
    """
    import youtube_transcrever as ytv
    import fala_local as fl

    vid = _video_id_de(video_id=video_id, video_url=video_url)
    if not vid:
        # FALHA FECHADO, e sem inventar identidade. O roteador grava o estado
        # declarado aqui em vez de o reinterpretar.
        raise _EstadoDaApi({
            'STATE': 'CONTRACT_DRIFT',
            'NATIVE_REASON': VIDEO_ID_AUSENTE,
            'DETALHE': ('a rota de audio publico exige um VIDEO_ID comprovado; '
                        'sem ele nao ha alvo, e derivar um seria fabricar identidade')})

    url = 'https://www.youtube.com/watch?v=' + vid
    caminho, motivo = ytv._audio(vid)
    # OS PEDIDOS DO `yt-dlp` ENTRAM NA CONTA DA CORRIDA, tambem quando falhou:
    # falhar nao e nao ter batido a porta. Do cache nao saiu pedido nenhum.
    # Sem contagem legivel, a corrida declara-o (e a prova-teto diz NAO_SEI).
    if motivo != 'CACHE':
        http.contar_de_fora(getattr(ytv, 'ULTIMO_TRAFEGO', None), quem='yt-dlp')
    if not caminho:
        raise _EstadoDaApi({
            'STATE': _classificar_falha(motivo),
            'NATIVE_REASON': AUDIO_NAO_OBTIDO,
            'DETALHE': str(motivo)[:300]})

    # ── O QUE CHEGOU, MEDIDO NOS BYTES ──────────────────────────────────────
    # `-f bestaudio` diz o que foi PEDIDO; so o dono do `ffprobe` diz o que
    # CHEGOU. E o dono e `fala_local` — um segundo sitio a chamar `ffprobe`
    # seria um segundo dono da mesma pergunta.
    video_streams, audio_streams, porque = fl.fluxos(caminho)
    if porque:
        raise _EstadoDaApi({
            'STATE': 'EXECUTOR_UNAVAILABLE',
            'NATIVE_REASON': MEDIA_KIND_DIVERGE,
            'DETALHE': 'o ficheiro obtido nao pode ser medido: %s' % porque})
    if video_streams:
        # AUDIO_ONLY != VIDEO. O que veio traz imagem, e chama-lo de audio
        # seria a primeira mentira do objeto.
        raise _EstadoDaApi({
            'STATE': 'CONTRACT_DRIFT',
            'NATIVE_REASON': MEDIA_KIND_DIVERGE,
            'DETALHE': 'pediu-se som e o ficheiro traz %d fluxo(s) de imagem'
                       % video_streams})

    import hashlib
    with open(caminho, 'rb') as f:
        corpo = f.read()
    sha = hashlib.sha256(corpo).hexdigest()
    dur = fl.duracao(caminho)
    _v, _a, _p = fl.fluxos(caminho)

    # ── O QUE A PLATAFORMA DECLARA DO VIDEO ────────────────────────────────
    # ⚠️ ISTO FALTAVA, E A SOC-ONDA2 MEDIU-O EM 11 CANAIS: 11/11 trouxeram som e
    # transcricao, e ZERO chegaram a READY — porque o item entrava sem data de
    # publicacao, sem dizer de que canal veio e sem o carimbo do dono.
    #
    #     O SOM PROVA QUE ALGUEM DISSE AQUILO. NAO PROVA QUANDO, NEM ONDE.
    #
    # Os tres tempos ficam SEPARADOS e nenhum se deduz do outro:
    #
    #     FACT_TIME      quando o FACTO aconteceu       -> NAO SEI, e fica escrito
    #     PUBLISHED_AT   o que a PLATAFORMA declara     -> medido, com precisao
    #     COLLECTED_AT   o relogio DESTA casa, na hora  -> medido
    #
    #     PUBLICACAO NAO VIRA FACT_TIME.
    #
    # Sem metadados, o objeto sai com `NAO SEI` E COM O MOTIVO — nunca com uma
    # data aproximada, que entraria no acervo com cara de facto.
    md, porque_md = ytv.metadados(vid)
    publicado_em, precisao = ytv.declarado_em(md)
    agora = env.agora()

    # ── O CARIMBO VEM DA MATRIZ, QUE E A DONA DA POLITICA ──────────────────
    # Escrever `SIM` aqui dentro seria uma segunda lei, escrita por quem so
    # executa. Quem decide se ha autorizacao do dono e a matriz; esta funcao
    # copia a decisao para o objeto que viaja — e copia tambem a plataforma.
    import social_matriz as mz                                       # noqa: PLC0415
    try:
        decisao = mz.decisao(PLATAFORMA, 'FETCH_AUDIO_BYTES')
    except Exception as e:                                           # noqa: BLE001
        decisao = {'PORQUE': 'DECISAO_ILEGIVEL: %s' % str(e)[:120]}

    return [{
        'OBJECT_KIND': 'PUBLIC_AUDIO',
        # O VIDEO_ID e identidade NATIVA da publicacao, preservada como veio.
        # Nao e SOURCE_ID: quem governa essa identidade e outra camada.
        'VIDEO_ID': vid,
        'SOURCE_URL': url,
        'RUN_ID': run_id,
        'ROUTE': ROTA_AUDIO_PUBLICO,
        'EXECUTOR': 'adaptador_youtube.youtube_audio_publico',
        # O eixo da especie. Nao se deduz do fornecedor nem da extensao.
        'MEDIA_KIND': 'AUDIO',
        'ACQUISITION_STATE': AUDIO_ADQUIRIDO,
        # ── A ESPÉCIE DOS BYTES, DECLARADA POR QUEM OS MEDIU ─────────────────
        # ⚠️ ISTO FALTAVA, E O PRIMEIRO CANÁRIO REAL PAGOU O PREÇO.
        #
        # A aquisição correu bem: 7.112.072 bytes de WAV real, 222,25 s, um
        # fluxo de som e zero de imagem. Mas o objeto não dizia O QUE os bytes
        # ERAM, e por isso `ingresso.ficha()` caiu no seu fallback e preservou
        # o **envelope JSON** (1232 bytes) em vez do som. `media_type` saiu
        # `application/json`, `ingresso._cabe_na_capacidade` não encontrou
        # derivador para JSON, e a Admissão respondeu `NAO_SEI` a um documento
        # que nunca teve texto porque ninguém o transcreveu.
        #
        #     ADQUIRIR O FICHEIRO NÃO É ENTREGAR O FICHEIRO.
        #
        # `leis/artefato.py::raw_do_disco` já respeita a declaração do coletor
        # desde o defeito do `.mp4` (a tabela de extensões dele só conhece
        # quatro, e `.wav` não é uma delas) — a lei existia e estava certa,
        # e continuava sem receber o dado de que precisa.
        #
        # E declara-se AQUI, depois de `fl.fluxos()` ter provado
        # `VIDEO_STREAMS == 0` e `AUDIO_STREAMS >= 1`, e não no ingresso: quem
        # sabe que `_audio()` corre com `--audio-format wav -ac 1 -ar 16000` é
        # o dono da aquisição. O ingresso a adivinhar pela extensão seria a
        # espécie decidida por quem nunca viu os bytes.
        'CONTENT_TYPE': 'audio/wav',
        'AUDIO_REFERENCE': caminho,
        'AUDIO_BYTES': len(corpo),
        'AUDIO_SHA256': sha,
        'AUDIO_DURATION_S': dur,
        'STREAMS': {'AUDIO': audio_streams, 'VIDEO': video_streams},
        'LIMITE': LIMITE_AUDIO_PUBLICO,
        'COUNTRY_SCOPE': country_scope,
        'CAPTURED_AT': agora,
        # ── A IDENTIDADE NATIVA DA PUBLICACAO ──────────────────────────────
        # `VIDEO_ID` ja viajava; `NATIVE_ID` e o nome que a PORTA usa para a
        # mesma coisa, e sem ele o item chegava a Sala sem identidade.
        'NATIVE_ID': vid,
        # ── OS TRES TEMPOS, SEPARADOS, NENHUM DEDUZIDO DO OUTRO ────────────
        'PUBLISHED_AT': publicado_em,
        'PUBLISHED_AT_PRECISION': precisao,
        'PUBLISHED_AT_SOURCE': ('PLATAFORMA — yt-dlp `timestamp`/`upload_date`, '
                                'sem chave e sem conta'),
        'PUBLISHED_AT_COMO_OBTIDO': porque_md,
        'COLLECTED_AT': agora,
        'FACT_TIME': 'NAO SEI',
        'FACT_TIME_PORQUE': ('a publicacao nao e o facto: o video fala de um dia '
                             'que nao tem de ser o da publicacao'),
        # ── DE QUE CANAL VEIO (a fonte de onde a publicacao saiu) ──────────
        'CHANNEL_ID': md.get('channel_id'),
        'CHANNEL_URL': md.get('channel_url') or md.get('uploader_url'),
        'CHANNEL_NAME': md.get('channel') or md.get('uploader'),
        'CHANNEL_ID_ESTADO': 'DECLARADO_PELA_PLATAFORMA' if md.get('channel_id')
                             else 'NAO SEI',
        # ── O CARIMBO DO DONO, COPIADO DA MATRIZ ───────────────────────────
        # DUAS FRASES, SEMPRE LADO A LADO: quem autorizou, e quem proibe.
        'OWNER_AUTHORIZED': decisao.get('OWNER_AUTHORIZED'),
        'PLATFORM_POLICY_STATUS': decisao.get('PLATFORM_POLICY_STATUS'),
        'AUTORIZACAO_DE': 'leis/social_matriz.py',
        # ── O QUE A REGUA LE PARA CONFERIR O AUTOR ────────────────────────
        # `curadoria/regua_social.py::autor()` le `OBSERVACAO.RAW.CREATOR_*`.
        # Sem isto, o item de um canal do YouTube chegava sem autor — e uma
        # republicacao de outra organizacao passaria por publicacao da fonte.
        'RAW': {'CREATOR_NAME': md.get('channel') or md.get('uploader'),
                'CREATOR_URL': md.get('channel_url') or md.get('uploader_url'),
                'CHANNEL_ID': md.get('channel_id'),
                'NATIVE_ID': vid,
                'TITLE': md.get('title'),
                'PUBLISHED_AT': publicado_em},
        # A LINHAGEM ATE AO VIDEO PAI. O som e DERIVADO do video: guardar o pai
        # e o que permite a quem ler daqui a um ano saber de que video estes
        # bytes sao o som.
        'PARENT': {'KIND': 'VIDEO', 'VIDEO_ID': vid, 'SOURCE_URL': url,
                   'MEDIA_KIND': 'AUDIO_ONLY'},
        'NOT_A_TRANSCRIPT': ('estes sao BYTES DE SOM. Texto reconhecido e outra '
                             'capacidade, com outro dono.'),
    }]


# ══════════════════════════════════════════════════════════════════════════
# A LISTA DE VIDEOS DE UM CANAL SEM CHAVE — a pagina publica, e so ela
# ══════════════════════════════════════════════════════════════════════════
ROTA_CANAL_PUBLICO = 'youtube:pagina-publica-do-canal'
LIMITE_CANAL_PUBLICO = 'PUBLIC_CHANNEL_LISTING_ONLY'
#: A pagina publica do canal. `/channel/<id>/videos` NAO esta em `Disallow` —
#: medido em 2026-09-24 no `robots.txt` vivo; e o feed `/feeds/videos.xml` ESTA,
#: e por isso NAO se usa (a matriz ja o declara `ROUTE_NOT_ALLOWED`).
PAGINA_DO_CANAL = 'https://www.youtube.com/channel/%s/videos'


def youtube_canal_publico(*, run_id, country_scope, canal_id=None, canal_url=None,
                          limit=25, medida=None, **_):
    """A LISTA de videos de um canal, SEM CHAVE DE API e sem conta.

    POR QUE ESTA ROTA EXISTE
    ------------------------
    A SOC-ONDA2 mediu 11 canais novos: a receita deles usa o coletor de CANAIS
    (Data API), que so corre onde esta a chave — e a chave so existe no GitHub.
    Localmente o orquestrador responde `CREDENTIAL_MISSING` e o canal nunca vira
    READY. Esta rota tira essa dependencia do caminho.

    QUEM LE A PAGINA E O DONO, E NAO ESTA FUNCAO
    --------------------------------------------
    A leitura e o parsing da pagina publica sao de `coleta/youtube_janela.py`
    (as duas portas: `urllib` primeiro, navegador quando ela nao serve). Aqui
    so se compoe e se veste o resultado na lingua da porta.

        UM LEITOR SO PARA A MESMA PERGUNTA. Um segundo `re` da grade do YouTube
        daria dois resultados para a mesma duvida — e o dia em que o formato
        mudar, um deles fica para tras em silencio.

    O QUE ESTA ROTA **NAO** FAZ
    ---------------------------
    Nao usa chave, conta, cookie de sessao, navegador logado nem rota paga; nao
    toca o feed `/feeds/videos.xml` (proibido no `robots.txt`, medido) e nao
    contorna bloqueio nenhum. Sem a pagina, a resposta e uma lista VAZIA com o
    motivo escrito — nunca uma lista inventada.
    """
    import youtube_janela as jan    # noqa: PLC0415 — o dono da janela publica

    alvo = canal_url or (PAGINA_DO_CANAL % canal_id if canal_id else '')
    if not alvo:
        raise ValueError('canal ausente: sem `canal_id` nem `canal_url` nao ha alvo')
    if '/feeds/videos.xml' in alvo:
        # FRONTEIRA, e ela nao se negocia: o feed esta em `Disallow`.
        raise ValueError('o feed do canal esta proibido no robots.txt (medido)')

    html, porta, motivo = jan._abrir(alvo)
    if not html:
        return []
    videos, porque = jan._videos_do_html(html)
    if not videos:
        return []

    import social_matriz as mz                                       # noqa: PLC0415
    try:
        decisao = mz.decisao(PLATAFORMA, 'INCREMENTAL')
    except Exception as e:                                           # noqa: BLE001
        decisao = {'PORQUE': 'DECISAO_ILEGIVEL: %s' % str(e)[:120]}
    agora = env.agora()

    objetos = []
    for v in videos[:int(limit or 25)]:
        vid = v.get('VIDEO_ID') or v.get('VIDEOID') or v.get('videoId')
        if not vid:
            continue
        objetos.append({
            'OBJECT_KIND': 'PUBLIC_CHANNEL_LISTING',
            'NATIVE_ID': vid,
            'SOURCE_URL': 'https://www.youtube.com/watch?v=' + vid,
            'CANAL_URL': alvo,
            'CHANNEL_ID': canal_id or '',
            'TITLE': v.get('TITLE') or v.get('title') or '',
            'RUN_ID': run_id,
            'ROUTE': ROTA_CANAL_PUBLICO,
            'EXECUTOR': 'adaptador_youtube.youtube_canal_publico',
            'PORTA_USADA': porta,
            'LIMITE': LIMITE_CANAL_PUBLICO,
            'COUNTRY_SCOPE': country_scope,
            'COLLECTED_AT': agora,
            'OWNER_AUTHORIZED': decisao.get('OWNER_AUTHORIZED'),
            'PLATFORM_POLICY_STATUS': decisao.get('PLATFORM_POLICY_STATUS'),
            'AUTORIZACAO_DE': 'leis/social_matriz.py',
            # ⚠️ A LISTA NAO TRAZ DATA. Medido: em `--flat-playlist` o yt-dlp
            # devolve `upload_date = None`; e a pagina do canal nao declara a
            # data de cada video na grade. Quem a tem e o METADADO do video,
            # que e outra chamada — e por isso a data NAO se inventa aqui.
            'PUBLISHED_AT': 'NAO SEI',
            'PUBLISHED_AT_PORQUE': ('a grade do canal nao declara a data de cada '
                                    'video; ela vem do metadado do video'),
            'FACT_TIME': 'NAO SEI',
            'NAO_E_UMA_OBSERVACAO_DO_VIDEO': (
                'uma LISTA de videos nao e uma observacao deles: o item do video '
                'nasce na fase que o adquire'),
        })
    if medida is not None:
        medida['ROUTE'] = ROTA_CANAL_PUBLICO
        medida['PORTA_USADA'] = porta
        medida['VIDEOS_NA_PAGINA'] = len(videos)
    return objetos


def pronto_para_canal_publico(**_):
    """A rota publica nao tem credencial nenhuma para estar pronta.

    A pergunta que ela responde e outra: o ambiente tem como falar com a pagina
    publica? Sem rede, a fase falha ao abrir — e falha com o motivo, nao com um
    silencio.
    """
    return (True, '')


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
             pronto=credencial_paga_presente, rota=youtube_legenda_paga,
             nota='ROTA PAGA: captions.download exige ser dono do video e captions.list '
                  'exige autorizacao, entao a matriz deixa `apify:transcricao` como unica. '
                  'A sonda le a chave paga e nao a do YouTube — sao dois donos diferentes.')
reg.registar(PLATAFORMA, 'youtube.media', adaptador=NOME,
             nota='403 de IP de datacenter; so o runner local pode fechar esta medicao')
reg.registar(PLATAFORMA, 'youtube.public_audio', adaptador=NOME,
             pronto=pronto_para_audio_publico, rota=youtube_audio_publico,
             nota='Rota LOCAL: `yt-dlp` + `ffmpeg` na maquina, custo zero. Reusa '
                  '`ferramentas/youtube_transcrever.py::_audio` — nao ha segundo '
                  'descarregador. A sonda olha so para o que esta instalado e nao '
                  'toca a rede: sem as ferramentas, a resposta e EXECUTOR_UNAVAILABLE '
                  'antes de se tentar baixar. LIMITE=PUBLIC_AUDIO_ONLY — sem sessao, '
                  'sem cookie de terceiro, sem token de conta. AUDIO_ONLY != VIDEO: '
                  'o objeto sai com MEDIA_KIND=AUDIO, e um ficheiro com imagem seria '
                  'recusado em vez de rebatizado.')
