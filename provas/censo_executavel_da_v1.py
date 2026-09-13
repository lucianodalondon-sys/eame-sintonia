#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NIGHT-SHIFT-01 §6 — CADA CAPACIDADE `READY` É EXERCIDA, E NÃO SÓ CONTADA.

    python3 provas/censo_executavel_da_v1.py

A superfície diz `READY`. Esta prova pergunta outra coisa:

    SE EU PEDIR ESTA CAPACIDADE PELO CAMINHO REAL, ELA ANDA?

E NÃO SE ACEITA COMO PROVA
----------------------------
que a função importe, que o módulo exista, que o registo tenha o nome, nem que
o adaptador responda quando chamado DIRETAMENTE. Nenhuma dessas quatro coisas é
uma aresta operacional.

    MODULE EXISTS != EDGE EXISTS != FLOW OBSERVED.
    CHAMAR O ADAPTADOR À MÃO PROVA O ADAPTADOR, E MAIS NADA.

Então cada capacidade entra por `scrap_executor.COLLECT` — o portão, o
roteador, a política, o teto de rede e a guarda de gasto correm todos — e o
único falso vive DEBAixo de tudo: o socket.

O QUE É FALSO AQUI, E SÓ ISSO
-------------------------------
`urllib.request.urlopen`, e para a cadeia de Reel o `subprocess`. Nada acima.

    REAL_NETWORK = 0 · APIFY_RUNS = 0 · COST_USD = 0
"""
import json
import os
import sys
import tempfile
import urllib.error

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in ('provas', 'coleta', 'leis', 'medidas', 'ferramentas', 'guarda', ''):
    sys.path.insert(0, os.path.join(RAIZ, _p) if _p else RAIZ)

BANCO = tempfile.mkdtemp(prefix='censo-v1-')
os.environ['RC01_MARCA'] = BANCO

import scrap_capacidades as cap                                   # noqa: E402
import scrap_executor as sx                                       # noqa: E402
import scrap_registo as reg                                       # noqa: E402
import social_envelope as env                                     # noqa: E402
import superficie_do_scrap_v1 as sup                              # noqa: E402
import scrap_colheita as sc                                       # noqa: E402

env.RAW_DIR = os.path.join(BANCO, 'raw')

#: Os argumentos MÍNIMOS de cada rota, lidos da assinatura dela e não
#: inventados: o que falta aqui é o que a rota declara como obrigatório.
#:
#:     UM ARGUMENTO QUE A PROVA ESCOLHE É UM ARGUMENTO QUE A ROTA NÃO PEDIU.
ALVOS = {
    'bluesky.account.discovery':   {'termo': 'agricoltura', 'limit': 1},
    'bluesky.author.incremental':  {'handle': 'conta.exemplo.invalido', 'limit': 1},
    'mastodon.hashtag.search':     {'instancia': 'exemplo.invalido', 'tag': 'agri',
                                    'limit': 1},
    'telegram.channel.incremental': {'canal': 'canal_exemplo'},
    'linkedin.identity.discovery': {'site_url': 'https://exemplo.invalido/'},
    'instagram.profile.discovery': {'camada': 'perfis'},
    'instagram.reel.capture':      {'url': 'https://www.instagram.com/reel/EXEMPLO/'},
    'instagram.reel.audio':        {'url': 'https://www.instagram.com/reel/EXEMPLO/'},
    'instagram.reel.transcribe':   {},
}

#: O que o mundo falso devolve a cada endereço. A forma é a da resposta
#: verdadeira; os valores dizem no próprio texto que são inventados.
MUNDO = {
    'robots.txt': 'User-agent: *\nAllow: /\n',
    'searchActors': json.dumps({'actors': [
        {'did': 'did:plc:CENSOFALSO', 'handle': 'censo.exemplo.invalido',
         'displayName': 'CENSO FALSO', 'description': 'observacao fabricada'}]}),
    'getAuthorFeed': json.dumps({'feed': [{'post': {
        'uri': 'at://did:plc:CENSOFALSO/app.bsky.feed.post/censo1',
        'cid': 'bafyCENSO',
        'author': {'did': 'did:plc:CENSOFALSO', 'handle': 'conta.exemplo.invalido'},
        'record': {'$type': 'app.bsky.feed.post', 'langs': ['it'],
                   'text': 'OBSERVACAO FABRICADA PELO CENSO',
                   'createdAt': '2026-09-13T00:00:00.000Z'},
        'likeCount': 0, 'repostCount': 0, 'replyCount': 0}}]}),
    'timelines/tag': json.dumps([
        {'uri': 'https://exemplo.invalido/users/x/statuses/1', 'id': '1',
         'url': 'https://exemplo.invalido/@x/1', 'language': 'it',
         'created_at': '2026-09-13T00:00:00.000Z',
         'content': '<p>OBSERVACAO FABRICADA PELO CENSO</p>',
         'account': {'acct': 'x@exemplo.invalido', 'url': 'https://exemplo.invalido/@x'},
         'replies_count': 0, 'reblogs_count': 0, 'favourites_count': 0,
         'media_attachments': []}]),
    't.me/s/': ('<div data-post="canal_exemplo/1">'
                '<time datetime="2026-09-13T00:00:00+00:00"></time>'
                '<div class="tgme_widget_message_text">OBSERVACAO FABRICADA</div>'
                '</div>'),
    'linkedin-site': ('<html><body><a href="https://www.linkedin.com/company/'
                      'exemplo-censo/">LinkedIn</a></body></html>'),
}


class _Resposta(object):
    def __init__(self, corpo):
        self._c = corpo.encode('utf-8')
        self.status = 200

    def read(self):
        return self._c

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False


IDAS = []


def urlopen_falso(req, *_a, **_k):
    url = req if isinstance(req, str) else getattr(req, 'full_url', str(req))
    IDAS.append(url)
    if url.endswith('/robots.txt'):
        return _Resposta(MUNDO['robots.txt'])
    for chave in ('searchActors', 'getAuthorFeed', 'timelines/tag', 't.me/s/'):
        if chave in url:
            return _Resposta(MUNDO[chave])
    if 'exemplo.invalido' in url:
        return _Resposta(MUNDO['linkedin-site'])
    # ── O QUE ESTE MUNDO NÃO CONHECE, ELE NÃO SERVE ──────────────────────
    # Um falso permissivo é uma porta aberta com outro nome: a prova daria
    # verde a uma rota que, na vida real, saía para a internet.
    raise urllib.error.URLError('censo: endereço fora do mundo falso: %s' % url)


def exercer(linha):
    """Pede a capacidade pelo caminho real. → a ficha do que aconteceu."""
    capacidade, plat = linha['CAPABILITY'], linha['PLATFORM']
    antes = len(IDAS)
    ficha = {'CAPABILITY': capacidade, 'PLATFORM': plat,
             'REQUEST_PATH': linha['FLOW_OBSERVED'],
             'FIRST_BREAK': linha['FIRST_BREAK']}
    if capacidade not in ALVOS:
        ficha.update({'FAKE_FLOW': 'SEM_ALVO_DECLARADO', 'OBJETOS': 0,
                      'RESULT': None})
        return ficha
    try:
        objetos, trace = sx.COLLECT(platform=plat, capability=capacidade,
                                    run_id='CENSO-V1', **ALVOS[capacidade])
        ficha.update({
            'FAKE_FLOW': 'CORREU' if objetos else 'CORREU_SEM_OBJETO',
            'OBJETOS': len(objetos or []),
            'RESULT': trace.get('RESULT'),
            'COST_STATE': trace.get('COST_STATE'),
            'PAID': bool(trace.get('PAID_PROVIDER_USED')),
            'IDAS': len(IDAS) - antes,
        })
    except Exception as e:                                        # noqa: BLE001
        ficha.update({'FAKE_FLOW': 'REBENTOU', 'OBJETOS': 0,
                      'RESULT': '%s: %s' % (type(e).__name__, str(e)[:70]),
                      'IDAS': len(IDAS) - antes})
    return ficha


def main():
    import urllib.request
    urllib.request.urlopen = urlopen_falso
    reg.carregar_adaptadores()
    linhas = [l for l in sup.medir() if l['V1'] == sup.READY]
    print(__doc__.strip().splitlines()[0])
    print('=' * 104)
    print('%-32s %-19s %-5s %-26s %s'
          % ('CAPABILITY', 'FAKE_FLOW', 'OBJ', 'RESULT', 'REQUEST_PATH'))
    print('-' * 104)
    fichas = []
    for l in sorted(linhas, key=lambda x: x['CAPABILITY']):
        f = exercer(l)
        fichas.append(f)
        print('%-32s %-19s %-5s %-26s %s'
              % (f['CAPABILITY'][:32], f['FAKE_FLOW'], f.get('OBJETOS'),
                 str(f.get('RESULT'))[:26], f['REQUEST_PATH']))
    quebradas = [f for f in fichas if f['FAKE_FLOW'] == 'REBENTOU']
    sem_alvo = [f for f in fichas if f['FAKE_FLOW'] == 'SEM_ALVO_DECLARADO']
    pagas = [f for f in fichas if f.get('PAID')]
    print('=' * 104)
    print('READY_CAPABILITIES_TESTED                  %d' % len(fichas))
    print('READY_CAPABILITIES_WITH_BROKEN_IMPLEMENTATION %d' % len(quebradas))
    for f in quebradas:
        print('   · %s — %s' % (f['CAPABILITY'], f['RESULT']))
    print('SEM_ALVO_DECLARADO                         %d' % len(sem_alvo))
    # ── O PORTÃO DA §6, MEDIDO E NÃO ARBITRADO ────────────────────────────
    # «REQUIRED_V1_CAPABILITY» não é uma lista que esta prova escolhe: é o que
    # `scrap_colheita.FASES` — o único sítio onde a V1 declara o que se pede —
    # nomeia. Escrever aqui uma segunda lista faria a prova medir a opinião
    # dela sobre o que a V1 devia ter.
    #
    #     UMA LISTA ESCRITA NA SONDA MEDE A SONDA.
    #
    # As restantes capacidades `READY` existem e não têm pedido — e isso é um
    # facto sobre a V1, não um defeito dela: CAPABILITY READY != CAPABILITY
    # PEDIDA.
    exigidas = {c for _p, c, _f, _e in sc.FASES.values()}
    por_nome = {f['CAPABILITY']: f for f in fichas}
    sem_pedido = sorted(c for c in exigidas
                        if (por_nome.get(c) or {}).get('REQUEST_PATH') == 'NO'
                        or c not in por_nome)
    print('CAPACIDADES PEDIDAS PELA V1 (scrap_colheita.FASES)  %d' % len(exigidas))
    print('REQUIRED_V1_CAPABILITY_WITHOUT_REQUEST_PATH        %d' % len(sem_pedido))
    for c in sem_pedido:
        print('   · %s' % c)
    prontas_sem_pedido = sorted(f['CAPABILITY'] for f in fichas
                                if f['REQUEST_PATH'] == 'NO')
    print('READY_SEM_PEDIDO (existe, ninguem pede)            %d · %s'
          % (len(prontas_sem_pedido), ', '.join(prontas_sem_pedido)))
    print('PAID_PROVIDER_USED                         %d' % len(pagas))
    print('REAL_NETWORK = 0 · idas ao mundo falso = %d' % len(IDAS))
    if os.environ.get('CENSO_JSON'):
        print(json.dumps(fichas, ensure_ascii=False, indent=1))
    return 0 if not quebradas else 1


if __name__ == '__main__':
    sys.exit(main())
