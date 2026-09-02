#!/usr/bin/env python3
"""Verifica o freeze da Espanha V1.

O freeze registra o sha256 de cada artefato canonico no momento em que a
demo foi congelada. Se um artefato mudar depois, este script reprova — e
essa e a unica coisa que separa um freeze de um adjetivo.
"""
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLES = os.path.join(ROOT, 'data', 'samples')
PACK = os.path.join(SAMPLES, 'SPAIN-DEMO-CONTENT-V1.json')


def verificar():
    with open(PACK, encoding='utf-8') as f:
        pack = json.load(f)
    freeze = pack['FREEZE']
    divergentes, ausentes = [], []
    for nome, meta in sorted(freeze['ARTEFATOS_CANONICOS'].items()):
        p = os.path.join(SAMPLES, nome)
        if not os.path.exists(p):
            ausentes.append(nome)
            continue
        with open(p, 'rb') as f:
            atual = hashlib.sha256(f.read()).hexdigest()
        if atual != meta['sha256']:
            divergentes.append((nome, meta['sha256'][:12], atual[:12]))
    print('FREEZE_HEAD           = %s' % freeze['HEAD_CURTO'])
    print('ARTEFATOS_CANONICOS   = %d' % len(freeze['ARTEFATOS_CANONICOS']))
    print('AUSENTES              = %d' % len(ausentes))
    print('DIVERGENTES           = %d' % len(divergentes))
    for nome, esperado, atual in divergentes:
        print('   %s  esperado %s  atual %s' % (nome, esperado, atual))
    for nome in ausentes:
        print('   AUSENTE: %s' % nome)
    ok = not divergentes and not ausentes
    print('FREEZE_INTACTO        = %s' % ('YES' if ok else 'NO'))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(verificar())
