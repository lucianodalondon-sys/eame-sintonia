# -*- coding: utf-8 -*-
"""O CLIENTE DO NAVEGADOR, FALSO — E COM TEXTO QUE A PORTA CONSEGUE JULGAR.

    META_REQUESTS = 0. Nenhum socket, nenhum navegador, nenhum instagram.com.

POR QUE EXISTE UM SEGUNDO FALSO, E NÃO UM SÓ
---------------------------------------------
`_flow01_janela_falsa.py` devolve `TEXT = 'texto observado'` — um marcador
escolhido para provar a ESTRADA, numa prova que nunca chegou à admissão. A
palavra não pertence ao vocabulário de nenhum universo desta casa, e por isso
a porta responde `NAO_SEI` — com razão, e dizendo-o:

    «não encontrei nada de «T9» — nem de nenhum outro universo. Isso NÃO
     prova que o item não pertence: prova que o vocabulário não lhe chegou.»

Medir a estrada com esse texto mede o LÉXICO DA PORTA, e não a estrada.

    UM MARCADOR QUE NENHUM UNIVERSO RECONHECE NÃO MEDE A ADMISSÃO:
    MEDE O DICIONÁRIO.

O QUE ESTE FALSO MUDA, E É TUDO O QUE ELE MUDA
------------------------------------------------
Duas coisas, e nenhuma delas está abaixo do portão:

 1. O TEXTO é uma legenda italiana plausível de um concorrente — `prodotto`,
    `campagna`, `fiera` — que é o que a rota T9 existe para colher.
 2. A ESPÉCIE DO TEXTO vem DECLARADA (`TEXT_UNITS`), como um provedor que
    declara legenda a declararia: `NATIVE_CAPTION` · `ORIGINAL` · `it`, com
    `TEXT_KIND_BASIS = DECLARED_BY_PROVIDER`.

O (2) não é conveniência: é o que torna a MATRIZ DO TEXTO mensurável. Com
tudo `UNKNOWN` dos dois lados não há como distinguir «nunca foi declarado» de
«foi declarado e perdeu-se» — e são estados diferentes, com donos diferentes.

    UNKNOWN DOS DOIS LADOS NÃO PROVA PRESERVAÇÃO: PROVA SILÊNCIO.

O QUE ISTO NÃO AFIRMA
---------------------
Não afirma que uma conta real publica este texto. Afirma o que acontece à
estrada QUANDO o texto é do universo pedido — que é a pergunta desta fase.
A fronteira externa continua falsa, e continua a ser o único ficheiro falso.
"""
import json
import os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAIDA = os.path.join(RAIZ, 'data', 'samples', 'INSTAGRAM-JANELA')

MARCA = os.path.join(os.environ.get('FLOW01_MARCA') or RAIZ, 'IDAS-AO-MUNDO.json')

#: A legenda. Italiana, do universo T9, e declarada como legenda nativa.
LEGENDA = ('Nuovo prodotto per la difesa del frumento: la campagna parte '
           'dalla fiera di Bologna.')

#: A unidade de texto, DECLARADA pelo provedor. Escrita à mão de propósito:
#: importar `proveniencia` aqui poria o contrato a testemunhar a favor de si
#: próprio. O falso declara em JSON puro; quem tem de reconhecer a forma é a
#: máquina do outro lado.
#:
#:     UM FALSO QUE USA O CONTRATO PARA FALAR NÃO TESTA O CONTRATO.
UNIDADE = {
    'TEXT_UNIT_ID': 'TU-1',
    'TEXT': LEGENDA,
    'TEXT_KIND': 'NATIVE_CAPTION',
    'TEXT_KIND_BASIS': 'DECLARED_BY_PROVIDER',
    'TEXT_RELATION': 'ORIGINAL',
    'LANGUAGE': 'it',
    'TRANSLATED_FROM_TEXT_UNIT_ID': None,
    'LINEAGE': {
        'RAW_OBSERVATION_ID': 'UNKNOWN',
        'SOURCE_ARTIFACT': 'https://www.instagram.com/p/BBBBBBBBBBB/',
        'DERIVATION_METHOD': 'UNKNOWN',
        'TOOL': 'UNKNOWN',
        'MODEL': 'UNKNOWN',
    },
}

ITENS = [{
    'PLATFORM': 'INSTAGRAM', 'SOURCE_ACCOUNT': 'basf_italia',
    'NATIVE_ID': '17900000000000002',
    'URL': 'https://www.instagram.com/p/BBBBBBBBBBB/',
    'CONTENT_TYPE': 'POST', 'TITLE': None, 'TEXT': LEGENDA,
    'TEXT_UNITS': [dict(UNIDADE)],
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
    return {'ITEMS': [dict(i) for i in ITENS]}
