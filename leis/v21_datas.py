#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""R6 · O CONTRATO TEMPORAL. Data é data, não texto que parece data.

O DEFEITO
---------
`FUTURE-EVENTS.json` declarava ser «subconjunto com data a partir de 02/09/2026»
e 21 dos 23 registros não tinham campo de data nenhum. O filtro real era:

    fut = [x for x in ev if str(x.get('REFERENCE_DATE') or '') >= '2026-09-02']

Comparação de STRING sobre um campo de procedência em prosa livre. Qualquer valor
começando por letra — «NAO_SEI — pagina sem data de publicacao visivel» — é
lexicograficamente maior que "2026-09-02" e entrava como evento futuro.

    'N' > '2' EM ORDEM DE TEXTO, E ISSO NÃO É UMA DATA NO FUTURO.

Aqui a data é analisada de verdade, e o que não se analisa vira UNKNOWN — que
NUNCA entra em «próximos» nem em «passados». Não saber é uma resposta.
"""
import re
from datetime import date

EXACT, MONTH_ONLY, RANGE, UNKNOWN = 'EXACT', 'MONTH_ONLY', 'RANGE', 'UNKNOWN'

_ISO = re.compile(r'(\d{4})-(\d{2})-(\d{2})')
_ISO_MES = re.compile(r'^\s*(\d{4})-(\d{2})\s*$')
_BR = re.compile(r'(\d{2})/(\d{2})/(\d{4})')


def _d(a, m, d):
    try:
        return date(int(a), int(m), int(d))
    except ValueError:
        return None


def analisar(*campos):
    """→ dict com START_DATE, END_DATE, DATE_PRECISION, DATE_SOURCE,
    DATE_PARSE_STATE. Só campos declarados; prosa nunca vira data."""
    for nome, valor in campos:
        t = str(valor or '').strip()
        if not t:
            continue
        iso = _ISO.findall(t)
        br = _BR.findall(t)
        if len(iso) >= 2:
            a, b = _d(*iso[0]), _d(*iso[1])
            if a and b:
                return _r(a, b, RANGE, nome, RANGE)
        if len(iso) == 1:
            a = _d(*iso[0])
            if a:
                return _r(a, a, EXACT, nome, EXACT)
        if len(br) >= 2:
            a, b = _d(br[0][2], br[0][1], br[0][0]), _d(br[1][2], br[1][1], br[1][0])
            if a and b:
                return _r(a, b, RANGE, nome, RANGE)
        if len(br) == 1:
            a = _d(br[0][2], br[0][1], br[0][0])
            if a:
                return _r(a, a, EXACT, nome, EXACT)
        m = _ISO_MES.match(t)
        if m:
            a = _d(m.group(1), m.group(2), 1)
            if a:
                return _r(a, a, MONTH_ONLY, nome, MONTH_ONLY)
    return {'START_DATE': None, 'END_DATE': None, 'DATE_PRECISION': None,
            'DATE_SOURCE': None, 'DATE_PARSE_STATE': UNKNOWN,
            'DATE_PARSE_WHY': 'nenhum campo declarado trouxe data analisavel. '
                              'Prosa nao vira data.'}


def _r(a, b, prec, origem, estado):
    return {'START_DATE': a.isoformat(), 'END_DATE': b.isoformat(),
            'DATE_PRECISION': prec, 'DATE_SOURCE': origem,
            'DATE_PARSE_STATE': estado}


def e_futuro(reg, corte):
    """SÓ data estruturada decide. UNKNOWN nunca entra.

        O QUE NÃO SE SABE QUANDO É NÃO ENTRA NA LISTA DO QUE VEM AÍ.
    """
    if reg.get('DATE_PARSE_STATE') == UNKNOWN:
        return False
    fim = reg.get('END_DATE') or reg.get('START_DATE')
    if not fim:
        return False
    try:
        return date.fromisoformat(fim) >= corte
    except ValueError:
        return False
