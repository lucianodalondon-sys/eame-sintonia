# -*- coding: utf-8 -*-
"""O CLIENTE DO NAVEGADOR, FALSO — com DOIS posts, para o retry ter o que salvar.

    META_REQUESTS = 0. Nenhum socket, nenhum navegador, nenhum instagram.com.

POR QUE DOIS, E NÃO UM
----------------------
A prova do retry precisa de uma falha que aconteça DEPOIS de a corrida já ter
estado persistida. Com um post só, a primeira tentativa ou preserva tudo ou não
preserva nada — e «não preservou nada» não é uma corrida que falhou a meio: é
uma corrida que não começou.

    UMA FALHA NO PRIMEIRO PASSO NÃO MEDE RECUPERAÇÃO:
    MEDE ARRANQUE.

Com dois, a primeira tentativa preserva o A, tropeça no B, e a corrida fica
onde uma corrida real fica quando o disco recusa: com parte no acervo e parte
por fazer. É esse o estado que o retry tem de saber continuar — sem duplicar o
A e sem inventar que o B já lá estava.

O texto dos dois é do universo T9 e traz espécie declarada, pela mesma razão
que em `_e2e01_janela_admissivel.py`: para a estrada chegar ao fim e a matriz
do texto ser mensurável.
"""
import json
import os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAIDA = os.path.join(RAIZ, 'data', 'samples', 'INSTAGRAM-JANELA')
MARCA = os.path.join(os.environ.get('FLOW01_MARCA') or RAIZ, 'IDAS-AO-MUNDO.json')


def _post(native_id, slug, legenda):
    return {
        'PLATFORM': 'INSTAGRAM', 'SOURCE_ACCOUNT': 'basf_italia',
        'NATIVE_ID': native_id,
        'URL': 'https://www.instagram.com/p/%s/' % slug,
        'CONTENT_TYPE': 'POST', 'TITLE': None, 'TEXT': legenda,
        'TEXT_UNITS': [{
            'TEXT_UNIT_ID': 'TU-1', 'TEXT': legenda,
            'TEXT_KIND': 'NATIVE_CAPTION',
            'TEXT_KIND_BASIS': 'DECLARED_BY_PROVIDER',
            'TEXT_RELATION': 'ORIGINAL', 'LANGUAGE': 'it',
            'TRANSLATED_FROM_TEXT_UNIT_ID': None,
            'LINEAGE': {'RAW_OBSERVATION_ID': 'UNKNOWN',
                        'SOURCE_ARTIFACT': 'https://www.instagram.com/p/%s/' % slug,
                        'DERIVATION_METHOD': 'UNKNOWN',
                        'TOOL': 'UNKNOWN', 'MODEL': 'UNKNOWN'}}],
        'PUBLISHED_AT': '2026-09-01T10:00:00Z',
        'COLLECTED_AT': '2026-09-12T00:00:00Z',
        'LANGUAGE': 'it', 'SOURCE_LOCATION': 'IT', 'COUNTRY_SCOPE': 'IT',
        'ROUTE': 'instagram_janela.py:grade', 'EXECUTOR': 'adaptador_instagram',
        'COST_USD': 0.0, 'RAW_REFERENCE': None, 'RAW': {'observado': True},
    }


ITENS = [
    _post('17900000000000011', 'CCCCCCCCCCC',
          'Nuovo prodotto per la difesa del frumento: la campagna parte '
          'dalla fiera di Bologna.'),
    _post('17900000000000012', 'DDDDDDDDDDD',
          'Annuncio del lancio: il prodotto per la vite arriva in campagna '
          'dopo la fiera.'),
]


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
    return {'ITEMS': [dict(i) for i in ITENS]}
