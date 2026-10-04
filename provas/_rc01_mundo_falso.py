#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O MUNDO EXTERNO, FALSO — E SÓ ELE.

Este ficheiro substitui `urllib.request.urlopen`, que é o ponto EXACTO onde o
socket abre. Nada acima dele é tocado:

    portão do `robots.txt`     real — e corre contra o robots que este ficheiro serve
    teto de rede               real — `orcamento_de_rede` captura o `urlopen` À ENTRADA
                                      do bloco, portanto embrulha ESTE, e conta na mesma
    taxonomia de falha         real — `HTTPError` e `URLError` sobem daqui como sobem de lá
    roteador · política        real
    adaptador · executor       real
    guarda de gasto            real
    contrato de retorno        real
    ingresso · admissão        real

    UM FAKE ACIMA DO GATE MEDE O FAKE. ESTE VIVE DEBAIXO DE TODOS ELES.

E TEM DE SER UM FICHEIRO, E NÃO UM `monkeypatch` NO PAI
--------------------------------------------------------
A `SCRAP-FLOW-01` já pagou essa lição: o orquestrador corre o executor como
PROCESSO SEPARADO, e o processo filho importa o módulo verdadeiro.

    UM FALSO QUE VIVE NA MEMÓRIA DO PAI NÃO EXISTE PARA O FILHO.

O QUE ELE RECUSA É O QUE FAZ DELE UMA PROVA
--------------------------------------------
Um endereço que este ficheiro não conhece NÃO passa: levanta. Assim, uma árvore
que tentasse sair para a internet a sério falha alto, em vez de sair em silêncio
e a prova dar verde com `REAL_NETWORK` mentido.

    UM FALSO PERMISSIVO É UMA PORTA ABERTA COM OUTRO NOME.
"""
import json
import os
import urllib.error
import urllib.request

#: Onde se regista cada ida ao «mundo». O pai lê isto para contar as idas —
#: contá-las em memória mediria o processo errado.
MARCA = os.environ.get('RC01_MARCA') or '.'
IDAS = os.path.join(MARCA, 'IDAS-AO-MUNDO.json')

ROBOTS = 'User-agent: *\nAllow: /\n'

#: A resposta da AppView pública do Bluesky a `app.bsky.feed.getAuthorFeed`,
#: na FORMA que a rota verdadeira devolve. Os valores são inventados e dizem-no
#: no próprio texto: uma prova que finge conteúdo real convida a citá-lo.
FEED = {
    'feed': [{
        'post': {
            'uri': 'at://did:plc:CANARIOFALSO/app.bsky.feed.post/rc01aaaa',
            'cid': 'bafyreiCANARIOFALSO',
            'author': {'did': 'did:plc:CANARIOFALSO',
                       'handle': 'canario-do-scrap.exemplo.invalido',
                       'displayName': 'CANÁRIO FALSO — SCRAP-RC-01'},
            'record': {
                '$type': 'app.bsky.feed.post',
                'text': 'OBSERVACAO FABRICADA PELA PROVA SCRAP-RC-01. '
                        'Nao e conteudo real e nao veio da internet.',
                'createdAt': '2026-09-12T10:00:00.000Z',
                'langs': ['it'],
            },
            'likeCount': 0, 'repostCount': 0, 'replyCount': 0,
        },
    }],
}


class _Resposta:
    """O que `urlopen` devolve: um gestor de contexto com `read()` e `status`."""

    def __init__(self, corpo, status=200):
        self._corpo = corpo.encode('utf-8')
        self.status = status

    def read(self):
        return self._corpo

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False


def _registar(url):
    idas = []
    if os.path.isfile(IDAS):
        try:
            with open(IDAS, encoding='utf-8') as f:
                idas = json.load(f)
        except Exception:                                         # noqa: BLE001
            idas = []
    idas.append(url)
    with open(IDAS, 'w', encoding='utf-8') as f:
        json.dump(idas, f, ensure_ascii=False, indent=1)


def _url_de(req):
    return req if isinstance(req, str) else getattr(req, 'full_url', str(req))


def urlopen_falso(req, *_a, **_k):
    url = _url_de(req)
    _registar(url)
    if url == 'https://public.api.bsky.app/robots.txt':
        return _Resposta(ROBOTS)
    if url.startswith('https://public.api.bsky.app/xrpc/app.bsky.feed.getAuthorFeed'):
        return _Resposta(json.dumps(FEED, ensure_ascii=False))
    # ── NÃO CONHEÇO ESTE ENDEREÇO, LOGO NÃO O SIRVO ──────────────────────
    # `URLError` e não `HTTPError`: um host que não respondeu é exactamente o
    # que aconteceu aqui, e mentir «404» faria o portão do robots ler AUSENTE
    # e dar passagem permissiva a um host que a prova nunca autorizou.
    raise urllib.error.URLError(
        'SCRAP-RC-01 · endereço fora do mundo falso: %s' % url)


def instalar():
    """Troca o socket, e devolve o que estava lá antes."""
    antigo = urllib.request.urlopen
    urllib.request.urlopen = urlopen_falso
    return antigo
