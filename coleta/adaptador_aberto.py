#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ADAPTADOR DA SOCIAL ABERTA — Mastodon, Bluesky e Telegram.

Tres plataformas, um adaptador, e isso tem um motivo: as tres servem conteudo
publico por API aberta, sem sessao e sem contrato de uso que exija conta. A
semantica e a mesma — perfil publico, cronologia publica, etiqueta publica — e
separa-las em tres modulos seria tres ficheiros a repetir a mesma forma.

    A LINHA NAO E «QUANTAS PLATAFORMAS», E «QUANTAS SEMANTICAS».

Instagram, LinkedIn, X, Facebook e YouTube tem cada um a sua, e por isso tem um
modulo cada. Estas tres partilham a delas.

O ESTADO DELAS NAO FOI MEDIDO POR MIM
--------------------------------------
O benchmark do SINTONIA SCRAP mediu cinco plataformas, e nenhuma destas estava
entre elas. O estado declarado em `scrap_capacidades.py` vem de
`leis/social_matriz.py`, que e onde esta casa ja o tinha escrito, e o campo de
prova di-lo em claro.

    CARREGAR UMA DECLARACAO EXISTENTE CITANDO A FONTE NAO E MEDIR. Nao esta
    escrito aqui que eu provei isto, porque nao provei.

O corpo das rotas nao foi reescrito: foi mudado de sitio, para que o roteador
deixe de conhecer o nome das plataformas.
"""
import json
import os
import sys
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import _gavetas  # noqa: E402,F401
import scrap_http as http      # noqa: E402
import scrap_registo as reg    # noqa: E402
import social_envelope as env  # noqa: E402

NOME = 'adaptador_aberto'


def mastodon_tag(*, instancia, tag, limit, run_id, country_scope):
    """Timeline pública de uma hashtag numa instância Mastodon."""
    url = 'https://%s/api/v1/timelines/tag/%s?limit=%d' % (
        instancia, urllib.parse.quote(tag), min(int(limit), 40))
    corpo = http.buscar(url)
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
    corpo = http.buscar(url)
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
    corpo = http.buscar(url)
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
    corpo = http.buscar(url)
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
    corpo = http.buscar(url, aceitar_json=False)
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
        raise http.RotaBloqueada(
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


# ══════════════════════════════════════════════════════════════════════════
# O QUE ESTE ADAPTADOR DECLARA
# ══════════════════════════════════════════════════════════════════════════
reg.registar('MASTODON', 'mastodon.hashtag.search', adaptador=NOME, rota=mastodon_tag)
reg.registar('MASTODON', 'mastodon.account.incremental', adaptador=NOME,
             rota=mastodon_conta_statuses)
reg.registar('BLUESKY', 'bluesky.account.discovery', adaptador=NOME,
             rota=bluesky_buscar_contas)
reg.registar('BLUESKY', 'bluesky.author.incremental', adaptador=NOME,
             rota=bluesky_feed_autor)
reg.registar('TELEGRAM', 'telegram.channel.incremental', adaptador=NOME, rota=telegram_canal)
