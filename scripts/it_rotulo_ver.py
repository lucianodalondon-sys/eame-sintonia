#!/usr/bin/env python3
"""Visor de rotulo: mostra a GEOMETRIA de um rotulo para leitura humana.

Visor, nao parser. Serve para alguem (ou algum agente) ler o rotulo e decidir o
que ele autoriza, sem passar pelo extrator que esta sendo julgado.

  python3 scripts/it_rotulo_ver.py 009757            blocos com cultura ou alvo
  python3 scripts/it_rotulo_ver.py 009757 --linhas   linhas com coordenada
  python3 scripts/it_rotulo_ver.py 009757 --parser   o que o parser devolve hoje
  python3 scripts/it_rotulo_ver.py 009757 --tudo     as tres coisas
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from it_rotulo_parser import (SECAO_PROIBIDA, alvos_em, culturas_em,   # noqa: E402
                              geometria_de, ler_geometria, parse)

GEO = os.path.join(ROOT, 'data/samples/IT-ROTULOS-V1/geometria')
REG = os.path.join(ROOT, 'data/samples/IT-RADAR-V21/productsRegulatory.json')


def _prod(rid):
    for p in json.load(open(REG, encoding='utf-8'))['PRODUCTS']:
        if p['REGISTRATION_ID'] == rid:
            return p
    return {}


def blocos(rid, mostrar_proibida=False):
    bs = ler_geometria(geometria_de(rid, '', GEO))
    print('#### %s  %s  (%d blocos)' % (rid, _prod(rid).get('PRODUCT') or '?', len(bs)))
    for b in sorted(bs, key=lambda z: (z['page'], z['y0'])):
        t = re.sub(r'\s+', ' ', b['text']).strip()
        c, a = culturas_em(t), alvos_em(t)
        if not (c or a):
            continue
        proib = bool(SECAO_PROIBIDA.search(t))
        if proib and not mostrar_proibida:
            continue
        print('--- p%d y=%.0f-%.0f x=%.0f-%.0f len=%d %s' % (
            b['page'], b['y0'], b['y1'], b['x0'], b['x1'], len(t),
            '[SECAO_PROIBIDA]' if proib else ''))
        print('    c=%s  a=%s' % (c, a))
        print('    %s' % t[:1400])


def linhas(rid):
    bs = ler_geometria(geometria_de(rid, '', GEO))
    for b in sorted(bs, key=lambda z: (z['page'], z['y0'])):
        for l in b['lines']:
            t = re.sub(r'\s+', ' ', l['text']).strip()
            if t:
                print('p%d y=%7.1f x=%7.1f | %s' % (b['page'], l['y0'], b['x0'],
                                                    t[:160]))


def do_parser(rid):
    p = _prod(rid)
    out = parse('', rid, produto=p.get('PRODUCT'),
                ai=p.get('ACTIVE_INGREDIENTS'), cache_dir=GEO,
                categoria=p.get('REGULATORY_CATEGORY'))
    print('#### PARSER %s (%s, %s)' % (rid, p.get('PRODUCT'),
                                       p.get('REGULATORY_CATEGORY')))
    if not out:
        print('    (nada)')
    for x in out:
        print('    %-14s %-16s %-18s %s' % (x['CROP'], x['TARGET'], x['RELATION'],
                                            x['ROUTE']))


if __name__ == '__main__':
    rid = sys.argv[1]
    modo = sys.argv[2] if len(sys.argv) > 2 else '--blocos'
    if modo in ('--blocos', '--tudo'):
        blocos(rid, mostrar_proibida=('--proibida' in sys.argv))
    if modo in ('--linhas', '--tudo'):
        print()
        linhas(rid)
    if modo in ('--parser', '--tudo'):
        print()
        do_parser(rid)
