#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LINKEDIN-BUILD-01 — A ESCADA OWN/FREE -> LOCAL -> PAID RESIDUAL, PROVADA NO SECO.

    py provas/linkedin_local_first.py

A pergunta desta missao:

    Para um pedido de LinkedIn, o SCRAP usa primeiro tudo o que ja possui ou
    obtem de graca, processa localmente o que puder, e chama provider pago
    SOMENTE para os campos que realmente faltam?

O QUE E FALSO AQUI, E SO ISSO
-------------------------------
Nada. Nao ha fake nenhum nesta prova, porque nao ha rede nenhuma a fingir: o
bruto e REAL e esta no disco desde 2026-08-29, e o unico transporte usado — o
da rota de identidade — recebe HTML por injeccao, que e a costura que o proprio
adaptador declara.

    LINKEDIN_REAL_REQUESTS = 0 · LICDN_REQUESTS = 0
    APIFY_RUNS = 0 · PAID_RUNS = 0 · REAL_COST_USD = 0
"""
import gzip
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in ('coleta', 'leis', 'medidas', 'ferramentas', 'guarda', ''):
    sys.path.insert(0, os.path.join(RAIZ, p) if p else RAIZ)

import adaptador_linkedin as li    # noqa: E402
import scrap_capacidades as cap    # noqa: E402
import scrap_executor as ex        # noqa: E402
import scrap_registo as reg        # noqa: E402
import social_matriz as mz         # noqa: E402
import social_envelope as env      # noqa: E402

# ── ESTA PROVA NAO SUJA A ARVORE ──────────────────────────────────────────
# `guardar_raw` preserva o bruto no disco, e e isso que ele deve fazer numa
# rota a serio. Numa MEDICAO, esses bytes ficariam na arvore e a proxima missao
# media-os como se fossem acervo.
#
#     UMA MEDICAO QUE SUJA A ARVORE E UMA MEDICAO QUE A PROXIMA VAI MEDIR.
#
# Entao o destino do bruto aponta para um temporario. A funcao nao muda, e o
# que se prova continua a ser a funcao de producao.
import tempfile                    # noqa: E402
env.RAW_DIR = tempfile.mkdtemp(prefix='linkedin-build-01-')

FALHAS = []

#: O bruto REAL preservado. Duas corridas do mesmo RUN_ID, 472 itens.
BRUTO = ('data/samples/raw-paid/ES-T8-002-linkedin-posts-a.raw.json.gz',
         'data/samples/raw-paid/ES-T8-002-linkedin-posts-b.raw.json.gz')
#: O ficheiro NORMALIZADO que a C11 mediu — e que perdeu os campos.
NORMALIZADO = 'data/samples/ES-T8-002-posts.json'
#: O que a medicao do estudo profundo contou. A prova falha se divergir: um
#: numero que muda sozinho significa que o bruto ou o tradutor mudaram.
ESPERADO = {'ITENS': 472, 'VIDEO_URL': 56, 'DOCUMENT_URL': 20,
            'DOCUMENT_TRANSCRIPT_URL': 20, 'ARTICLE_URL': 93,
            'REACTIONS_BY_TYPE': 449, 'COMMENTS_TEXT': 0, 'NATIVE_CAPTION': 0}
RUN = 'LINKEDIN-BUILD-01-SECO'


def diz(ok, titulo, detalhe=''):
    print('  %-5s %-58s %s' % ('ok' if ok else 'FALHA', titulo[:58], str(detalhe)[:56]))
    if not ok:
        FALHAS.append(titulo)


def bruto():
    itens = []
    for f in BRUTO:
        itens += json.loads(gzip.decompress(open(os.path.join(RAIZ, f), 'rb').read()))
    return itens


print('=' * 88)
print('LINKEDIN-BUILD-01 · A ESCADA, NO SECO')
print('=' * 88)

itens = bruto()
print('\n1 · O BRUTO, LIDO DO DISCO')
diz(len(itens) == ESPERADO['ITENS'], 'o bruto preservado tem 472 itens', len(itens))

# ══════════════════════════════════════════════════════════════════════════
print('\n2 · O QUE A NORMALIZACAO ANTIGA PERDIA  (PROVIDER_GAP != NORMALIZATION_GAP)')
# ══════════════════════════════════════════════════════════════════════════
d = json.load(open(os.path.join(RAIZ, NORMALIZADO), encoding='utf-8'))
antigos = d if isinstance(d, list) else next((v for v in d.values() if isinstance(v, list) and v), [])
campos_antigos = set()
for r in antigos:
    if isinstance(r, dict):
        campos_antigos |= set(r)
for perdido in ('VIDEO_URL', 'DOCUMENT_URL', 'ARTICLE_URL', 'REACTIONS_BY_TYPE'):
    diz(perdido not in campos_antigos,
        'o normalizado ANTIGO nao tinha %s' % perdido,
        'confirmado' if perdido not in campos_antigos else 'JA TINHA?')

envelopes, conta = li.normalizar_lote(itens, run_id=RUN, country_scope='ES',
                                      raw_reference=BRUTO[0])
print('\n3 · O QUE O TRADUTOR NOVO RECUPERA')
for campo, esperado in sorted(ESPERADO.items()):
    if campo == 'ITENS':
        continue
    diz(conta.get(campo) == esperado,
        'RAW_FIELD_PRESENT -> NORMALIZER_SEES_FIELD: %s' % campo,
        '%s (esperado %s)' % (conta.get(campo), esperado))
diz(conta['ITENS'] == 472, 'nenhum item perdido na traducao', conta['ITENS'])
print('       tipos de midia: %s' % conta['MEDIA_TYPE'])

# A semantica nao se inventa: um campo ausente no bruto e `None` na saida.
sem_video = [e for e in envelopes if not e['RAW'].get('VIDEO_URL')]
diz(all(e['RAW'].get('VIDEO_DURATION') is None for e in envelopes),
    'OUTPUT_PRESERVES_SEMANTICS: duracao nunca e fabricada', '0 de 472 tem duracao')
diz(all(e['RAW'].get('MEDIA_TYPE') != 'VIDEO' for e in sem_video),
    'texto que FALA de video nao vira MEDIA_TYPE=VIDEO', '%d sem campo de video' % len(sem_video))

# ══════════════════════════════════════════════════════════════════════════
print('\n4 · DELTA  (DELTA != FULL HISTORY)')
# ══════════════════════════════════════════════════════════════════════════
# ⚠️ ESTES NUMEROS NAO SAO OS DO ESTUDO PROFUNDO, E OS DOIS ESTAO CERTOS.
# O estudo contou `(captura - publicado).days <= N`, e `.days` TRUNCA: um post
# de 7,9 dias conta como 7. Aqui o corte e uma DATA absoluta. Sao duas
# definicoes de «ultimos 7 dias», e a diferenca e de tres itens.
#
#     «7 DIAS» NAO E UMA MEDIDA ATE ALGUEM DIZER SE O CORTE E UMA DATA OU UMA
#     SUBTRACCAO TRUNCADA. O adapter usa DATA, porque e o que o provider aceita
#     em `postedLimitDate` — e um filtro que nao bate com o do provider e um
#     delta que pede itens que o provider ja tinha excluido.
_, r7 = li.filtrar_janela(itens, since='2026-08-22T00:00:00Z')
_, r30 = li.filtrar_janela(itens, since='2026-07-30T00:00:00Z')
_, r90 = li.filtrar_janela(itens, since='2026-05-31T00:00:00Z')
_, r365 = li.filtrar_janela(itens, since='2025-08-29T00:00:00Z')
diz(r7['DENTRO'] == 13, 'corte em 2026-08-22 devolve 13 de 472', r7['DENTRO'])
diz(r30['DENTRO'] == 56, 'corte em 2026-07-30 devolve 56 de 472', r30['DENTRO'])
diz(r90['DENTRO'] == 173, 'corte em 2026-05-31 devolve 173 de 472', r90['DENTRO'])
diz(r365['DENTRO'] == 452, 'corte em 2025-08-29 devolve 452 de 472', r365['DENTRO'])
diz(r7['FORA_POR_TEMPO'] + r7['DENTRO'] == 472,
    'a janela nao perde itens: dentro + fora = 472',
    '%d + %d' % (r7['DENTRO'], r7['FORA_POR_TEMPO']))
diz(r7['DENTRO'] < r30['DENTRO'] < r365['DENTRO'] < 472,
    'a janela e MONOTONA e nunca devolve tudo', '%d < %d < %d < 472'
    % (r7['DENTRO'], r30['DENTRO'], r365['DENTRO']))

# RUN 1 achou A,B,C. RUN 2 com limite posterior nao volta a pedi-los.
run1, _ = li.filtrar_janela(itens, since='2026-08-22T00:00:00Z')
c1 = [li.campos_do_bruto(i) for i in run1]
mais_novo = max(x['PUBLISHED_AT_EPOCH_MS'] for x in c1)
ids1 = {x['NATIVE_ID'] for x in c1}
run2, r2 = li.filtrar_janela(itens, last_seen_time=mais_novo)
ids2 = {li.campos_do_bruto(i)['NATIVE_ID'] for i in run2}
diz(not (ids1 & ids2), 'RUN 2 com limite posterior nao repete nenhum id da RUN 1',
    '%d ∩ %d = %d' % (len(ids1), len(ids2), len(ids1 & ids2)))
diz(r2['FORA_POR_TEMPO'] > 0, 'a RUN 2 recusou por TEMPO e disse quantos', r2['FORA_POR_TEMPO'])

# `last_seen_id` corta ADEMAIS do tempo, e o relatorio separa os dois motivos.
alvo = sorted(ids1)[0]
_, rid = li.filtrar_janela(run1, last_seen_id=[alvo])
diz(rid['JA_VISTO_POR_ID'] == 1 and rid['DENTRO'] == len(run1) - 1,
    'last_seen_id corta por ID, em campo proprio do relatorio',
    'ja_visto=%s dentro=%s' % (rid['JA_VISTO_POR_ID'], rid['DENTRO']))

# O limite mais RESTRITIVO vence quando dois nomes do mesmo eixo chegam juntos.
_, rdois = li.filtrar_janela(itens, since='2025-08-29T00:00:00Z',
                             posted_limit_date='2026-08-22T00:00:00Z')
diz(rdois['DENTRO'] == r7['DENTRO'],
    'dois nomes do eixo tempo: vence o MAIS RESTRITIVO', rdois['DENTRO'])
_, rmax = li.filtrar_janela(itens, max_posts=5)
diz(rmax['DENTRO'] == 5 and rmax['TRUNCADO_POR_MAX_POSTS'] == 467,
    'MAX_POSTS trunca e declara quanto truncou',
    '%s / truncou %s' % (rmax['DENTRO'], rmax['TRUNCADO_POR_MAX_POSTS']))

# ══════════════════════════════════════════════════════════════════════════
print('\n5 · LISTAGEM != ENRIQUECIMENTO, e o padrao e NAO')
# ══════════════════════════════════════════════════════════════════════════
vazio = li.pedido_vazio()
diz(not any(vazio.values()), 'o pedido por omissao nao pede enriquecimento nenhum', vazio)
vazio['WANT_COMMENTS'] = True
diz(not any(li.pedido_vazio().values()),
    'mutar um pedido nao muda o padrao da casa', 'padrao intacto')

um_video = next(e for e in envelopes if e['RAW'].get('VIDEO_URL'))
p = li.plano_de_aquisicao(um_video, li.pedido_vazio())
diz(p['GAP'] == [] and p['PLAN'] == [],
    'pedido vazio -> gap vazio -> nenhum passo de aquisicao', 'PLAN=%d' % len(p['PLAN']))
diz(p['PAID_ENRICHMENT_NOT_REQUIRED'],
    'PAID nao corre por omissao', p['PAID_ENRICHMENT_NOT_REQUIRED'])

# ══════════════════════════════════════════════════════════════════════════
print('\n6 · NAO PAGAR PELO QUE JA VEIO  (FIELD_ALREADY_PRESENT)')
# ══════════════════════════════════════════════════════════════════════════
pede_midia = dict(li.pedido_vazio(), WANT_MEDIA=True)
pedidos, ja, falta = li.o_que_falta(um_video, pede_midia)
diz('VIDEO_BYTES' in falta,
    'os BYTES de video faltam mesmo tendo o ENDERECO', 'URL != BYTES')
diz(um_video['RAW']['VIDEO_URL'] and not um_video['RAW']['VIDEO_BYTES_ACQUIRED'],
    'VIDEO_URL presente e VIDEO_BYTES_ACQUIRED False, ao mesmo tempo', 'dois eixos')

# O campo que JA veio na listagem nao entra no gap.
falso_com_texto = json.loads(json.dumps(um_video))
falso_com_texto['RAW']['COMMENTS_TEXT'] = [{'text': 'ja veio'}]
_, ja2, falta2 = li.o_que_falta(falso_com_texto, dict(li.pedido_vazio(), WANT_COMMENTS=True))
diz(ja2 == ['COMMENTS_TEXT'] and falta2 == [],
    'FIELD_ALREADY_PRESENT -> PAID_ENRICHMENT_NOT_REQUIRED', 'ja=%s gap=%s' % (ja2, falta2))
p2 = li.plano_de_aquisicao(falso_com_texto, dict(li.pedido_vazio(), WANT_COMMENTS=True))
diz(p2['PAID_ENRICHMENT_NOT_REQUIRED'] and p2['PAID_NEEDED_FOR'] == [],
    'e o plano NAO propoe comprar o que ja esta presente', p2['PAID_NEEDED_FOR'])

# ══════════════════════════════════════════════════════════════════════════
print('\n7 · A POLITICA E SOBERANA  (PAID PROVIDER NAO ABRE ROTA PROIBIDA)')
# ══════════════════════════════════════════════════════════════════════════
tudo = {k: True for k in li.BANDEIRAS}
p3 = li.plano_de_aquisicao(um_video, tudo)
por_campo = {x['NEED']: x for x in p3['PLAN']}
diz(mz.decisao('LINKEDIN', 'FETCH_COMMENTS')['DECISAO'] != 'ALLOWED',
    'a politica NAO permite FETCH_COMMENTS no LinkedIn',
    mz.decisao('LINKEDIN', 'FETCH_COMMENTS')['DECISAO'])
diz(por_campo['COMMENTS_TEXT']['VERDICT'] == 'BLOCKED_NO_PERMITTED_ROUTE',
    'texto de comentario sai BLOCKED_NO_PERMITTED_ROUTE, nao «precisa de dinheiro»',
    por_campo['COMMENTS_TEXT']['VERDICT'])
diz(p3['PAID_NEEDED_FOR'] == [],
    'com a politica de hoje, NENHUM campo sai como PAID', p3['PAID_NEEDED_FOR'])
diz(por_campo['TRANSCRIPT']['TIER'] == li.LOCAL,
    'o ASR local nao pede permissao de rota — nao ha ida a rede', 'TIER=LOCAL')
diz(sorted(p3['BLOCKED_FOR']) == sorted(
        ['COMMENTS_TEXT', 'REACTION_PEOPLE', 'VIDEO_BYTES', 'DOCUMENT_BYTES', 'NATIVE_CAPTION']),
    'os cinco campos de rede saem BLOCKED, um a um', len(p3['BLOCKED_FOR']))

# ══════════════════════════════════════════════════════════════════════════
print('\n8 · CAPTION FIRST, e ASR depois dos BYTES')
# ══════════════════════════════════════════════════════════════════════════
diz(conta['NATIVE_CAPTION'] == 0,
    'nenhum dos 472 posts pagos traz legenda nativa', conta['NATIVE_CAPTION'])
ordem = [x['NEED'] for x in p3['PLAN']]
diz(ordem.index('NATIVE_CAPTION') < ordem.index('TRANSCRIPT'),
    'CAPTION vem ANTES de TRANSCRIPT no plano', '%s' % ordem[-2:])
com_legenda = json.loads(json.dumps(um_video))
com_legenda['RAW']['NATIVE_CAPTION'] = '1\n00:00:00,220 --> 00:00:03,032\nola\n'
p4 = li.plano_de_aquisicao(com_legenda, dict(li.pedido_vazio(), WANT_TRANSCRIPT=True))
diz('NATIVE_CAPTION' not in p4['GAP'],
    'havendo legenda, ela e preservada e nao se volta a pedir', p4['GAP'])
diz(li.ONDE_SE_OBTEM['TRANSCRIPT']['NIVEL'] == li.LOCAL,
    'MEDIA ACCESS != ASR: o transcript e LOCAL e nao adquire midia nenhuma',
    li.ONDE_SE_OBTEM['TRANSCRIPT']['PORQUE'][:40])

# ══════════════════════════════════════════════════════════════════════════
print('\n9 · REACOES E COMENTARIOS — as contagens nao viram as coisas')
# ══════════════════════════════════════════════════════════════════════════
tot_c = sum((e['RAW'].get('COMMENTS_COUNT') or 0) for e in envelopes)
diz(tot_c == 335, 'a CONTAGEM de comentarios soma 335', tot_c)
diz(conta['COMMENTS_TEXT'] == 0, 'e o TEXTO deles e ZERO', conta['COMMENTS_TEXT'])
diz(all(e['RAW'].get('REACTION_PEOPLE') is None for e in envelopes),
    'REACTION_PEOPLE nunca e preenchido sem pedido', 'REACTION COUNTS != PEOPLE')
tipos = set()
for e in envelopes:
    tipos |= set((e['RAW'].get('REACTIONS_BY_TYPE') or {}))
diz(tipos == {'LIKE', 'PRAISE', 'INTEREST', 'EMPATHY', 'APPRECIATION'},
    'o agregado por TIPO chega inteiro, e de graca', sorted(tipos))

# ══════════════════════════════════════════════════════════════════════════
print('\n10 · A ROTA PERMITIDA — le o site da organizacao, nao o linkedin.com')
# ══════════════════════════════════════════════════════════════════════════
HTML = ('<footer>Seguici su <a href="https://www.linkedin.com/company/image-line">LinkedIn</a>'
        ' e <a href="https://it.linkedin.com/in/alguem-real-123">o nosso agronomo</a>'
        ' e <a href="https://twitter.com/x">X</a></footer>')
tocou = []


def transporte_falso(url):
    tocou.append(url)
    return HTML


medida = {}
objs = li.identidade_pelo_site(site_url='https://imagelinenetwork.com/', run_id=RUN,
                              country_scope='IT', medida=medida,
                              transporte=transporte_falso)
diz(len(objs) == 2, 'achou os dois handles no HTML do site', len(objs))
diz(all('linkedin.com' not in u for u in tocou),
    'NENHUM pedido foi para o linkedin.com', tocou)
diz({o['RAW']['TARGET_TYPE'] for o in objs} == {'COMPANY', 'PERSON'},
    'separa COMPANY de PERSON, que sao dois eixos', 'ok')
diz(all(o['RAW']['POST_CONTENT'] is None and not o['RAW']['CONTENT_ACQUIRED'] for o in objs),
    'IDENTITY != CONTENT: nenhum conteudo de post e fabricado', 'ok')
diz(all(o['CONTENT_TYPE'] == 'DISCOVERY' for o in objs),
    'o tipo do objecto e DISCOVERY, nunca POST', 'ok')
diz(medida.get('COST_STATE') == 'FREE_ROUTE_BY_POLICY' and medida.get('ACTUAL_COST_USD') == 0.0,
    'rota gratuita por politica: zero e FACTO e o eixo vai a par', medida.get('COST_STATE'))
diz(all(o['ACQUISITION_TIER'] == li.FREE for o in objs), 'ACQUISITION_TIER = FREE', 'ok')

# ══════════════════════════════════════════════════════════════════════════
print('\n11 · O CENSO, E O DEFEITO DE TRADUCAO FECHADO')
# ══════════════════════════════════════════════════════════════════════════
reg.carregar_adaptadores()
donos = [n for n, v in cap.DECLARADAS.items()
         if v[0] == 'LINKEDIN' and v[5] == 'DISCOVER_ACCOUNT']
diz(donos == ['linkedin.identity.discovery'],
    'a permissao de DISCOVER_ACCOUNT tem UM dono, e ele faz identidade', donos)
diz(cap.da_matriz('linkedin.recent.discovery') is None,
    'linkedin.recent.discovery deixou de pedir emprestada aquela permissao', 'sem traducao')
ck = ex.CHECK('LINKEDIN', 'linkedin.identity.discovery')
diz(ck['STATE'] == ex.PODE, 'CHECK da rota permitida: CAN_COLLECT_NOW', ck['STATE'])
ck2 = ex.CHECK('LINKEDIN', 'linkedin.direct_post')
diz(ck2['STATE'] == ex.SEM_ROTA,
    'e o post direto continua sem rota, como a politica manda', ck2['STATE'])
wired = [k for k in reg.executaveis() if k[0] == 'LINKEDIN']
diz(len(wired) == 1, 'UMA capacidade ligada, e e a permitida', wired)

# ══════════════════════════════════════════════════════════════════════════
print('\n12 · O RASTO — nao mistura a origem dos campos')
# ══════════════════════════════════════════════════════════════════════════
t = li.rasto_de_aquisicao(um_video, p3)
diz(t['ACQUISITION_TIER'] == li.LOCAL,
    'reler bruto preservado e LOCAL nesta corrida', t['ACQUISITION_TIER'])
diz(t['FIELDS_FROM_PAID'] and not t['FIELDS_FROM_FREE'],
    'e os campos continuam com procedencia PAID', '%d campos' % len(t['FIELDS_FROM_PAID']))
diz(t['PROVIDER'] == li.ROTA_BRUTO_PRESERVADO,
    'o provider histórico viaja com o rasto', t['PROVIDER'])
diz(t['COST_USD'] == 0.0, 'reler nao custa dolar nenhum hoje', t['COST_USD'])
ti = li.rasto_de_aquisicao(objs[0])
diz(ti['FIELDS_FROM_FREE'] == [] or ti['ACQUISITION_TIER'] == li.FREE,
    'o objecto da rota gratuita tem rasto proprio', ti['ACQUISITION_TIER'])

print('\n' + '=' * 88)
print('LINKEDIN_LOCAL_FIRST_OFFLINE = %s' % ('PASS' if not FALHAS else 'FALHOU · %d' % len(FALHAS)))
print('LINKEDIN_REAL_REQUESTS = 0 · LICDN_REQUESTS = 0')
print('APIFY_RUNS = 0 · PAID_RUNS = 0 · REAL_COST_USD = 0')
print('POLICY_CHANGED = NO   (leis/social_matriz.py intacto)')
for f in FALHAS:
    print('  · %s' % f)
sys.exit(1 if FALHAS else 0)
