# -*- coding: utf-8 -*-
"""O CLIENTE DO NAVEGADOR, FALSO. É o único ficheiro trocado nesta prova.

Ele tem a mesma superfície do verdadeiro para quem o usa — `contas`, `perfis`,
`objetos`, `_ler`, `SAIDA` — e não abre porta nenhuma para o mundo.

    META_REQUESTS = 0. Nenhum socket, nenhum navegador, nenhum instagram.com.
"""
import json
import os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAIDA = os.path.join(RAIZ, 'data', 'samples', 'INSTAGRAM-JANELA')

#: A marca de que o falso correu. O verdadeiro nunca escreve isto.
MARCA = os.path.join(os.environ.get('FLOW01_MARCA') or RAIZ, 'IDAS-AO-MUNDO.json')

ITENS = [{
    'PLATFORM': 'INSTAGRAM', 'SOURCE_ACCOUNT': 'basf_italia',
    'NATIVE_ID': '17900000000000001',
    'URL': 'https://www.instagram.com/p/AAAAAAAAAAA/',
    'CONTENT_TYPE': 'POST', 'TITLE': None, 'TEXT': 'texto observado',
    'PUBLISHED_AT': '2026-09-01T10:00:00Z',
    'COLLECTED_AT': '2026-09-12T00:00:00Z',
    'LANGUAGE': 'it', 'SOURCE_LOCATION': 'IT', 'COUNTRY_SCOPE': 'IT',
    'ROUTE': 'instagram_janela.py:grade', 'EXECUTOR': 'adaptador_instagram',
    'COST_USD': 0.0, 'RAW_REFERENCE': None, 'RAW': {'observado': True},
}]


def _marcar(qual):
    idas = []
    if os.path.isfile(MARCA):
        try:
            with open(MARCA, encoding='utf-8') as f:
                idas = json.load(f)
        except Exception:                                         # noqa: BLE001
            idas = []
    idas.append(qual)
    with open(MARCA, 'w', encoding='utf-8') as f:
        json.dump(idas, f)


def contas():
    return ['basf_italia']


def perfis():
    _marcar('perfis')
    return 0


def objetos(limite_por_conta=None):
    _marcar('objetos')
    return 0


def _ler(nome):
    return {'ITEMS': list(ITENS)}
