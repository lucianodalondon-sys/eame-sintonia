#!/usr/bin/env python3
"""LABEL_PARSER_SURVIVES_NEW_CONTAINER.

Prova que um processo NOVO — sem /tmp anterior, sem scratchpad, sem os PDFs e sem rede —
consegue localizar as fontes, rodar o parser e reproduzir o conjunto de pares e o digest.

Tres vezes nesta missao um resultado essencial morreu por viver so em disco efemero:
as tres transcricoes, o pacote canonico V2.1, e os 163 rotulos baixados. A geometria
dos rotulos esta versionada em git justamente para essa historia nao se repetir.
"""
import hashlib
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from it_rotulo_parser import (GEOMETRIA_VERSIONADA, PARSER_VERSION,  # noqa: E402
                              parse)

CAND = os.path.join(ROOT, 'data/samples/IT-ROTULOS-V1/IT-ROTULOS-PARES-V2-CANDIDATO.json')
REG = os.path.join(ROOT, 'data/samples/IT-RADAR-V21/productsRegulatory.json')


def digest(pares):
    ch = sorted('%s|%s|%s' % (p['REGISTRATION_ID'], p['CROP'], p['TARGET']) for p in pares)
    return hashlib.sha256('\n'.join(ch).encode()).hexdigest()


def main():
    print('LABEL_PARSER_SURVIVES_NEW_CONTAINER')
    print('  cwd ......................... %s' % os.getcwd())
    print('  parser ...................... %s' % PARSER_VERSION)
    geo = sorted(f for f in os.listdir(GEOMETRIA_VERSIONADA) if f.endswith('.xml.gz'))
    print('  geometria versionada ........ %d arquivos' % len(geo))
    depende_de_efemero = any(x in GEOMETRIA_VERSIONADA for x in ('/tmp/', 'scratchpad'))
    print('  depende de /tmp|scratchpad .. %s' % ('SIM — FALHOU' if depende_de_efemero
                                                  else 'NAO'))
    pdfs = [f for f in geo if os.path.exists(os.path.join(GEOMETRIA_VERSIONADA,
                                                          f.replace('.xml.gz', '.pdf')))]
    print('  precisa de PDF .............. %s' % ('SIM' if pdfs else 'NAO'))

    P = json.load(open(REG, encoding='utf-8'))['PRODUCTS']
    pares = []
    for p in P:
        pares.extend([x for x in parse('', p['REGISTRATION_ID'], produto=p['PRODUCT'],
                                       ai=p.get('ACTIVE_INGREDIENTS'))
                      if x['RELATION'] == 'SUPPORTED_PAIR'])
    dg = digest(pares)
    print('  rotulos processados ......... %d' % len(P))
    print('  pares SUPPORTED reproduzidos  %d' % len(pares))
    print('  digest ...................... %s' % dg[:32])

    esperado = json.load(open(CAND, encoding='utf-8'))
    dg_esperado = digest(esperado['PAIRS'])
    bate = dg == dg_esperado
    print('  digest do conjunto publicado   %s' % dg_esperado[:32])
    print('  REPRODUZ IDENTICO ........... %s' % bate)
    ok = (not depende_de_efemero) and len(geo) == 163 and bate and not pdfs
    print('  VEREDITO .................... %s' % ('PASS' if ok else 'FAIL'))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
