#!/usr/bin/env python3
"""
ROTAS SOCIAIS — a política que escolhe a porta, e os adaptadores que a atravessam.

Quem pede coleta diz PLATAFORMA e CAPACIDADE. Nunca diz FERRAMENTA.

    pedido = {'platform': 'MASTODON', 'capability': 'SEARCH_HASHTAG',
              'query': 'agricoltura', 'country_scope': 'IT', 'limit': 20}

A escolha da rota é desta casa, não de quem chama. Se amanhã o Mastodon fechar
a prévia pública e a rota certa virar outra, o chamador não muda uma linha.

O PORTÃO QUE TORNA A DECLARAÇÃO EXECUTÁVEL
--------------------------------------------
`social_matriz.py` DECLARA que uma rota é permitida. Declaração não impede
ninguém de nada. Então toda rota de HTTP direto passa, antes da primeira
requisição, por `permitido()` — que busca o `robots.txt` REAL do host, com o
`User-agent` REAL desta coleta, e recusa o caminho barrado.

    O ROBOTS É LIDO NA HORA, NÃO DECORADO NO CÓDIGO.

Isso existe porque a coisa mais provável de acontecer com este arquivo é
alguém acrescentar uma rota nova daqui a três meses sem reler os Termos. O
portão pega isso. Um comentário não pegaria.

E o portão já REPROVOU rota que funcionava: o `feeds/videos.xml` do YouTube
devolveu 15 vídeos italianos com descrição inteira nesta máquina, e está em
`Disallow`. Ele não entrou. É para isso que o portão serve — se ele só
aprovasse, não seria portão.

O QUE ESTE ARQUIVO NÃO FAZ
----------------------------
Não faz login, não manda cookie, não resolve CAPTCHA, não troca de IP para
escapar de bloqueio, não finge ser navegador de gente. Quando a plataforma diz
não, a resposta é `ROUTE_NOT_ALLOWED` ou `BLOCKED` no artefato — nunca uma
tentativa mais esperta.

E não julga conteúdo. Ele traz o objeto e preserva o bruto. Se é relevante
para a ADAMA, se é ameaça, se é oportunidade — isso é decisão de outra camada,
que roda de graça sobre o artefato e pode ser refeita sem recoletar.
"""
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import social_envelope as env      # noqa: E402
import social_matriz as mz         # noqa: E402
import falhas                      # noqa: E402  — a lingua unica do erro
import social_sessao as ss         # noqa: E402  — LOCAL_SESSION é rota, não motor

# O agente se identifica. Não há ganho em mentir e há perda: um host que quer
# nos barrar tem direito de nos reconhecer, e um host que nos permite precisa
# conseguir nos medir.
AGENTE = 'SintoniaScrap/1.0 (+EAME; social capability census; contato via repositório)'

TIMEOUT = 25
PAUSA_ENTRE_CHAMADAS = 1.0   # cortesia; nenhum host desta missão pede menos

_ROBOTS = {}


class RotaNaoPermitida(RuntimeError):
    """A rota existe, responderia, e nós não vamos usá-la."""


class RotaBloqueada(RuntimeError):
    """A plataforma nos impediu. Diferente de não permitida."""


# ══════════════════════════════════════════════════════════════════════════
# O PORTÃO
# ══════════════════════════════════════════════════════════════════════════
def permitido(url):
    """Lê o robots.txt vivo do host e responde (bool, motivo).

    Host que não publica robots.txt é permissivo por omissão — é o caso
    medido do t.me. Host que responde HTML em vez de robots (Instagram e
    Threads, deste IP) é `UNKNOWN`: não afirmamos permissão que não lemos.
    """
    partes = urllib.parse.urlsplit(url)
    base = '%s://%s' % (partes.scheme, partes.netloc)
    if base not in _ROBOTS:
        _ROBOTS[base] = _carregar_robots(base)
    rp, estado = _ROBOTS[base]
    if estado == 'AUSENTE':
        return True, 'host não publica robots.txt (permissivo por omissão)'
    if estado == 'ILEGIVEL':
        return False, 'robots.txt ilegível deste host — não afirmamos permissão que não lemos'
    ok = rp.can_fetch(AGENTE, url)
    if not ok:
        return False, 'robots.txt do host barra este caminho para %s' % AGENTE.split('/')[0]
    return True, 'robots.txt do host permite este caminho'


def _carregar_robots(base):
    rp = urllib.robotparser.RobotFileParser()
    try:
        req = urllib.request.Request(base + '/robots.txt', headers={'User-Agent': AGENTE})
        with urllib.request.urlopen(req, timeout=TIMEOUT) as f:
            corpo = f.read().decode('utf-8', 'replace')
    except urllib.error.HTTPError as e:
        if e.code in (404, 410):
            return rp, 'AUSENTE'
        return rp, 'ILEGIVEL'
    except Exception:
        return rp, 'ILEGIVEL'
    # Um host que devolve HTML no lugar do robots não está publicando regra:
    # está nos mandando para uma página. Isso não é "pode".
    if corpo.lstrip()[:9].lower().startswith('<!doctype') or corpo.lstrip()[:5].lower() == '<html':
        return rp, 'ILEGIVEL'
    rp.parse(corpo.splitlines())
    return rp, 'LIDO'


def _get(url, *, aceitar_json=True):
    """GET com o portão na frente. Nenhuma rota escapa dele."""
    ok, motivo = permitido(url)
    if not ok:
        raise RotaNaoPermitida('%s · %s' % (motivo, url))
    req = urllib.request.Request(url, headers={
        'User-Agent': AGENTE,
        'Accept': 'application/json' if aceitar_json else 'text/html',
    })
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as f:
            corpo = f.read().decode('utf-8', 'replace')
    except urllib.error.HTTPError as e:
        raise RotaBloqueada('HTTP %s em %s' % (e.code, url))
    except Exception as e:
        raise RotaBloqueada('%s em %s' % (type(e).__name__, url))
    finally:
        time.sleep(PAUSA_ENTRE_CHAMADAS)
    return corpo


# ══════════════════════════════════════════════════════════════════════════
# ADAPTADORES — um por rota permitida. Pequenos de propósito.
# ══════════════════════════════════════════════════════════════════════════
def mastodon_tag(*, instancia, tag, limit, run_id, country_scope):
    """Timeline pública de uma hashtag numa instância Mastodon."""
    url = 'https://%s/api/v1/timelines/tag/%s?limit=%d' % (
        instancia, urllib.parse.quote(tag), min(int(limit), 40))
    corpo = _get(url)
    raw = env.guardar_raw('MASTODON', '%s-tag-%s' % (instancia, tag), corpo)
    saida = []
    for p in json.loads(corpo):
        conta = p.get('account') or {}
        saida.append(env.envelope(
            # O `id` do Mastodon é LOCAL: o mesmo post federado ganha um id
            # diferente em cada instância que o recebe. Medido no piloto de
            # 2026-09-08: 19 dos 118 objetos eram o MESMO post contado duas
            # vezes, porque mastodon.uno e mastodon.social numeram cada um o
            # seu. A identidade global é o `uri` do ActivityPub.
            #     ID LOCAL NÃO É IDENTIDADE. FEDERAÇÃO INFLA CONTAGEM.
            platform='MASTODON', native_id=p.get('uri') or p.get('id'),
            url=p.get('url') or p.get('uri'),
            content_type='POST', route='mastodon:/api/v1/timelines/tag',
            executor='social_rotas.mastodon_tag', run_id=run_id,
            country_scope=country_scope,
            source_account=conta.get('acct'),
            published_at=p.get('created_at'),
            # `language` vem DECLARADO pelo autor. Não inferimos do texto, e a
            # instância ser italiana não faz o autor ser da Itália.
            language=p.get('language'),
            source_location=None,
            text=_sem_tags(p.get('content') or ''),
            raw_reference=raw,
            raw={'instancia': instancia, 'id_local': p.get('id'),
                 'replies_count': p.get('replies_count'),
                 'reblogs_count': p.get('reblogs_count'),
                 'favourites_count': p.get('favourites_count'),
                 'account_url': conta.get('url'),
                 'media': [m.get('type') for m in (p.get('media_attachments') or [])]}))
    return saida


def mastodon_conta_statuses(*, instancia, acct_id, limit, run_id, country_scope):
    """Posts recentes de uma conta conhecida — a rota de MONITORAMENTO."""
    url = 'https://%s/api/v1/accounts/%s/statuses?limit=%d&exclude_replies=true' % (
        instancia, urllib.parse.quote(str(acct_id)), min(int(limit), 40))
    corpo = _get(url)
    raw = env.guardar_raw('MASTODON', '%s-acct-%s' % (instancia, acct_id), corpo)
    saida = []
    for p in json.loads(corpo):
        conta = p.get('account') or {}
        saida.append(env.envelope(
            platform='MASTODON', native_id=p.get('uri') or p.get('id'),
            url=p.get('url') or p.get('uri'),
            content_type='POST', route='mastodon:/api/v1/accounts/{id}/statuses',
            executor='social_rotas.mastodon_conta_statuses', run_id=run_id,
            country_scope=country_scope, source_account=conta.get('acct'),
            published_at=p.get('created_at'), language=p.get('language'),
            text=_sem_tags(p.get('content') or ''), raw_reference=raw,
            raw={'instancia': instancia, 'id_local': p.get('id')}))
    return saida


def bluesky_buscar_contas(*, termo, limit, run_id, country_scope):
    """Descoberta de contas na AppView pública do Bluesky."""
    url = ('https://public.api.bsky.app/xrpc/app.bsky.actor.searchActors'
           '?q=%s&limit=%d' % (urllib.parse.quote(termo), min(int(limit), 50)))
    corpo = _get(url)
    raw = env.guardar_raw('BLUESKY', 'searchActors-%s' % termo, corpo)
    saida = []
    for a in (json.loads(corpo).get('actors') or []):
        saida.append(env.envelope(
            platform='BLUESKY', native_id=a.get('did'),
            url='https://bsky.app/profile/%s' % a.get('handle'),
            content_type='PROFILE', route='bsky:app.bsky.actor.searchActors',
            executor='social_rotas.bluesky_buscar_contas', run_id=run_id,
            country_scope=country_scope, source_account=a.get('handle'),
            title=a.get('displayName'), text=a.get('description'),
            raw_reference=raw, raw={'did': a.get('did')}))
    return saida


def bluesky_feed_autor(*, handle, limit, run_id, country_scope):
    url = ('https://public.api.bsky.app/xrpc/app.bsky.feed.getAuthorFeed'
           '?actor=%s&limit=%d' % (urllib.parse.quote(handle), min(int(limit), 50)))
    corpo = _get(url)
    raw = env.guardar_raw('BLUESKY', 'authorFeed-%s' % handle, corpo)
    saida = []
    for item in (json.loads(corpo).get('feed') or []):
        p = item.get('post') or {}
        rec = p.get('record') or {}
        saida.append(env.envelope(
            platform='BLUESKY', native_id=p.get('uri'), url=_bsky_url(p),
            content_type='POST', route='bsky:app.bsky.feed.getAuthorFeed',
            executor='social_rotas.bluesky_feed_autor', run_id=run_id,
            country_scope=country_scope,
            source_account=(p.get('author') or {}).get('handle'),
            published_at=rec.get('createdAt'),
            language=(rec.get('langs') or [None])[0],
            text=rec.get('text'), raw_reference=raw,
            raw={'likeCount': p.get('likeCount'), 'repostCount': p.get('repostCount'),
                 'replyCount': p.get('replyCount')}))
    return saida


def telegram_canal(*, canal, run_id, country_scope):
    """Prévia pública de canal do Telegram — página, não API."""
    import re
    url = 'https://t.me/s/%s' % urllib.parse.quote(canal)
    corpo = _get(url, aceitar_json=False)
    raw = env.guardar_raw('TELEGRAM', 'canal-%s' % canal, corpo)
    blocos = re.findall(
        r'data-post="([^"]+)".*?(?:<time datetime="([^"]+)")?.*?'
        r'class="tgme_widget_message_text[^"]*"[^>]*>(.*?)</div>', corpo, re.S)
    saida = []
    for post_id, quando, html in blocos:
        saida.append(env.envelope(
            platform='TELEGRAM', native_id=post_id, url='https://t.me/%s' % post_id,
            content_type='POST', route='telegram:t.me/s/{canal}',
            executor='social_rotas.telegram_canal', run_id=run_id,
            country_scope=country_scope, source_account=canal,
            published_at=quando or None, text=_sem_tags(html)[:4000],
            raw_reference=raw, raw={'canal': canal}))
    if not saida:
        # Canal inexistente e canal sem prévia devolvem a MESMA página curta.
        # Zero mensagens não é "canal vazio" — é indefinido, e vai declarado.
        raise RotaBloqueada(
            'nenhuma mensagem na prévia de @%s — canal inexistente, privado ou sem '
            'prévia pública. Isto NÃO é "canal vazio".' % canal)
    return saida


def _bsky_url(post):
    uri = post.get('uri') or ''
    rkey = uri.rsplit('/', 1)[-1]
    handle = (post.get('author') or {}).get('handle')
    return 'https://bsky.app/profile/%s/post/%s' % (handle, rkey)


def _sem_tags(html):
    import re
    txt = re.sub(r'<br\s*/?>', '\n', html)
    txt = re.sub(r'</p>', '\n\n', txt)
    txt = re.sub(r'<[^>]+>', '', txt)
    import html as _h
    return _h.unescape(txt).strip()


# ══════════════════════════════════════════════════════════════════════════
# POLÍTICA DE ROTA
# ══════════════════════════════════════════════════════════════════════════
# ── YOUTUBE, ESTRADA OFICIAL ───────────────────────────────────────────────
# Os adaptadores abaixo só chegam a rodar depois de `social_matriz` declarar a
# capacidade e a política aprovar a rota. Eles NÃO decidem se podem — executam.
def youtube_buscar(*, termo, run_id, country_scope, limit=25, **_):
    import youtube_oficial as yt
    objs, _s = yt.buscar(termo=termo, run_id=run_id, country_scope=country_scope,
                         limit=limit, regiao=country_scope, idioma='it')
    return objs


def youtube_uploads(*, channel_id, run_id, country_scope, limit=25, conhecidos=(), **_):
    import youtube_oficial as yt
    objs, _s, _rel = yt.uploads_recentes(
        channel_id=channel_id, run_id=run_id, country_scope=country_scope,
        limit=limit, conhecidos=conhecidos)
    return objs


def youtube_metadata(*, video_ids, run_id, country_scope, **_):
    import youtube_oficial as yt
    objs, _s, _rel = yt.metadata(video_ids=video_ids, run_id=run_id,
                                 country_scope=country_scope)
    return objs


def youtube_comentarios(*, video_id, run_id, country_scope, limite_threads=100, **_):
    import youtube_oficial as yt
    objs, _s, rel = yt.comentarios(video_id=video_id, run_id=run_id,
                                   country_scope=country_scope,
                                   limite_threads=limite_threads)
    # Comentário desativado NÃO é coleta vazia: é um fato sobre o vídeo, e sobe
    # como estado próprio para não virar ZERO_RESULTS no registro.
    if rel.get('STATE') not in (None, 'OK', 'ZERO_RESULTS'):
        raise RotaBloqueada('%s (razão nativa: %s)' % (rel['STATE'], rel.get('NATIVE_REASON'))
                            ) if rel['STATE'] == 'BLOCKED' else _EstadoDaApi(rel)
    return objs


class _EstadoDaApi(RuntimeError):
    """Carrega o estado canônico que a própria API declarou, sem reinterpretar."""

    def __init__(self, rel):
        self.rel = rel
        super().__init__('%s (razão nativa: %s)' % (rel.get('STATE'),
                                                    rel.get('NATIVE_REASON')))


ADAPTADORES = {
    ('MASTODON', 'SEARCH_HASHTAG'): mastodon_tag,
    ('MASTODON', 'INCREMENTAL'): mastodon_conta_statuses,
    ('BLUESKY', 'DISCOVER_ACCOUNT'): bluesky_buscar_contas,
    ('BLUESKY', 'INCREMENTAL'): bluesky_feed_autor,
    ('TELEGRAM', 'INCREMENTAL'): telegram_canal,
    ('YOUTUBE', 'SEARCH_KEYWORD'): youtube_buscar,
    ('YOUTUBE', 'INCREMENTAL'): youtube_uploads,
    ('YOUTUBE', 'FETCH_VIDEO_METADATA'): youtube_metadata,
    ('YOUTUBE', 'FETCH_COMMENTS'): youtube_comentarios,
}


def _executar(*, platform, capability, run_id, country_scope='IT',
            permitir_pago=False, motivo_pago=None, ownership=None, **kwargs):
    """Escolhe a rota declarada e executa. Devolve (objetos, registro).

    O registro é gravado MESMO quando a rota falha — recusa e bloqueio são
    resultado de medição, não ausência de resultado.
    """
    plat, cap = platform.upper(), capability.upper()
    # O padrão é TERCEIRO. Ler dado de outra empresa é o caso perigoso, então é
    # ele que precisa ser o padrão — quem for ler conta PRÓPRIA declara.
    ownership = ownership or ss.THIRD_PARTY
    rotas = (mz.MATRIZ.get(plat) or {}).get(cap)
    registro = {
        'PLATFORM': plat, 'CAPABILITY': cap, 'RUN_ID': run_id,
        'COUNTRY_SCOPE': country_scope, 'QUANDO': env.agora(),
        'ROTA_ESCOLHIDA': None, 'AUTH_MODE': None, 'ESTADO': None, 'OBJETOS': 0,
        'COST_USD': 0.0, 'ERRO': None, 'MOTIVO_PAGO': None,
    }
    if not rotas:
        registro['ESTADO'] = 'NOT_APPLICABLE'
        registro['ERRO'] = 'capacidade não declarada na matriz para esta plataforma'
        return [], registro

    escolhida = mz._rota_padrao(rotas)
    if escolhida is None:
        registro['ESTADO'] = 'ROUTE_NOT_ALLOWED'
        registro['ERRO'] = 'nenhuma rota permitida para %s/%s' % (plat, cap)
        return [], registro
    registro['ROTA_ESCOLHIDA'] = escolhida['ROTA']

    registro['AUTH_MODE'] = mz.auth_mode(escolhida)

    # ── A TRAVA DA SESSÃO ────────────────────────────────────────────────────
    # Estar logado não autoriza automatizar. A pergunta é sobre o CONTRATO com
    # a plataforma e sobre DE QUEM É a conta alvo — nunca sobre o que a máquina
    # consegue fazer. Por isso ela roda ANTES de qualquer navegação, e nem
    # sequer consulta o preflight: recusa por termo não depende de ter Chrome.
    if escolhida['CLASSE'] == 'LOCAL_SESSION':
        ok_auto, porque = ss.automacao_permitida(plat, ownership)
        registro['OWNERSHIP'] = ownership
        if not ok_auto:
            registro['ESTADO'] = ss.AUTOMATION_NOT_ALLOWED
            registro['ERRO'] = ss.redigir(porque)
            return [], registro
        pre = ss.preflight()
        # O preflight vai para o registro REDIGIDO e sem caminho de perfil.
        registro['SESSION_STATE'] = pre['ESTADO']
        if pre['ESTADO'] != ss.SESSION_AVAILABLE:
            registro['ESTADO'] = pre['ESTADO']
            registro['ERRO'] = ss.redigir(pre['PORQUE'])
            return [], registro

    # A trava do gasto. Rota paga só passa com motivo do vocabulário fechado —
    # e "a Apify já estava configurada" não está no vocabulário.
    if escolhida['CLASSE'] in ('APIFY', 'OFFICIAL_API_PAID'):
        if not permitir_pago:
            registro['ESTADO'] = 'PAID_ROUTE_REFUSED'
            registro['ERRO'] = ('a rota padrão é PAGA (%s) e esta execução não autorizou '
                                'gasto' % escolhida['CLASSE'])
            return [], registro
        if motivo_pago not in mz.MOTIVOS_PAGOS:
            registro['ESTADO'] = 'PAID_ROUTE_REFUSED'
            registro['ERRO'] = ('motivo de gasto fora do vocabulário canônico: %r. '
                                'Aceitos: %s' % (motivo_pago, ', '.join(mz.MOTIVOS_PAGOS)))
            return [], registro
        registro['MOTIVO_PAGO'] = motivo_pago

    fn = ADAPTADORES.get((plat, cap))
    if fn is None:
        registro['ESTADO'] = ('CREDENTIAL_MISSING'
                              if escolhida['ESTADO'] == 'CREDENTIAL_MISSING'
                              else 'POSSIBLE_NOT_PROVED')
        registro['ERRO'] = ('rota declarada e permitida, mas sem adaptador nesta missão: %s'
                            % escolhida['ROTA'])
        return [], registro

    try:
        objetos = fn(run_id=run_id, country_scope=country_scope, **kwargs)
    except RotaNaoPermitida as e:
        registro['ESTADO'] = 'ROUTE_NOT_ALLOWED'
        registro['ERRO'] = ss.redigir(str(e))
        return [], registro
    except _EstadoDaApi as e:
        # A API disse o que houve. Não reinterpretamos: gravamos o que ela disse.
        registro['ESTADO'] = e.rel.get('STATE')
        registro['NATIVE_REASON'] = e.rel.get('NATIVE_REASON')
        registro['RECOVERY_ACTION'] = e.rel.get('RECOVERY_ACTION')
        registro['ERRO'] = ss.redigir(str(e))
        return [], registro
    except RotaBloqueada as e:
        registro['ESTADO'] = 'BLOCKED'
        registro['ERRO'] = ss.redigir(str(e))
        return [], registro
    except urllib.error.HTTPError as e:
        # O código da resposta é a melhor prova que existe. 401/403 não é vazio,
        # 429 não é fonte caída, 5xx é a FONTE e 4xx é PEDIDO NOSSO.
        registro['ESTADO'] = falhas.classificar(http=e.code)
        registro['ERRO'] = ss.redigir('HTTP %s: %s' % (e.code, e))
        return [], registro
    except (urllib.error.URLError, TimeoutError, ConnectionError, OSError) as e:
        # Transporte caiu. NÃO é rota morta e NÃO é fonte vazia.
        registro['ESTADO'] = 'TRANSIENT_NETWORK_ERROR'
        registro['ERRO'] = ss.redigir('%s: %s' % (type(e).__name__, e))
        return [], registro
    except (KeyError, IndexError, AttributeError, TypeError, ValueError) as e:
        # A fonte respondeu e o NOSSO extrator não achou o campo. Este é o estado
        # que o balde `FAILED` escondia — e o único aqui que pede gente.
        #
        #     PARSER QUEBRADO NÃO É FONTE VAZIA.
        registro['ESTADO'] = 'PARSER_DRIFT'
        registro['ERRO'] = ss.redigir('%s: %s' % (type(e).__name__, e))
        return [], registro
    except Exception as e:
        # A exceção é REDIGIDA antes de virar registro. Um traceback de urllib
        # carrega a URL, e a URL pode carregar o token — foi assim que segredo
        # vazou em casa alheia sem ninguém ter escrito `print(cookie)`.
        registro['ESTADO'] = 'UNKNOWN_ERROR'
        registro['ERRO'] = ss.redigir('%s: %s' % (type(e).__name__, e))
        return [], registro

    registro['ESTADO'] = 'OK' if objetos else 'ZERO_RESULTS'
    registro['OBJETOS'] = len(objetos)
    return objetos, registro


def executar(**kwargs):
    """Porta única. Sela TODA saída com a taxonomia canônica — nenhum caminho escapa.

    O selo é aplicado aqui, e não em cada `return`, porque um `return` novo daqui a
    três meses esqueceria de selar. Envolver é a única forma que não depende de
    alguém lembrar.
    """
    objetos, registro = _executar(**kwargs)
    return objetos, selar(registro)


def selar(registro):
    """Traduz o estado para o vocabulário canônico e anexa o que ele significa."""
    bruto = registro.get('ESTADO')
    if bruto is None:
        return registro
    canon = falhas.traduzir(bruto)
    registro['ESTADO'] = canon
    if bruto != canon:
        registro['ESTADO_ORIGINAL'] = bruto
    camada, saude = falhas.saude(canon)
    registro['FAILURE_LAYER'] = camada
    registro['EXPECTED'] = falhas.esperado(canon)
    registro['DEGRADES_SOURCE'] = falhas.degrada_fonte(canon)
    registro.setdefault('RECOVERY_ACTION',
                        falhas.recuperacao(canon, registro.get('NATIVE_REASON')))
    registro['SOURCE_HEALTH'] = saude if camada == falhas.SOURCE else falhas.HEALTHY
    registro['ROUTE_HEALTH'] = saude if camada == falhas.ROUTE else falhas.HEALTHY
    registro['EXECUTOR_HEALTH'] = saude if camada == falhas.EXECUTOR else falhas.HEALTHY
    return registro
