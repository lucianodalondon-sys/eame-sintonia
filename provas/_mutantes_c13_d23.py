#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A PROVA DOS MUTANTES: `test_c13_route_gate` tem de MORRER quando uma rota muda.

    py provas/_mutantes_c13_d23.py

Tres mutacoes, uma de cada vez, e a expectativa e sempre a mesma: se o teste
continua verde depois de uma rota mudar, ele nao guarda nada.

  1 · uma rota ANTIGA muda de estado            -> tem de morrer
  2 · a rota NOVA do D23 muda de estado         -> tem de morrer
  3 · uma rota NOVA aparece sem ser declarada   -> tem de morrer
"""
import io
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for g in ('coleta', 'leis', 'regras', 'pedido', ''):
    sys.path.insert(0, os.path.join(RAIZ, g) if g else RAIZ)
import _gavetas  # noqa: F401
import social_matriz as mz

ALVO_ANTIGO = ('MASTODON', 'SEARCH_HASHTAG', 0)
ALVO_NOVO = ('LINKEDIN', 'FETCH_VIDEO_BYTES', 0)


def corre():
    suite = unittest.TestLoader().loadTestsFromName('tests.test_c13_route_gate')
    r = unittest.TextTestRunner(verbosity=0, stream=io.StringIO()).run(suite)
    return len(r.failures) + len(r.errors)


def muta(chave, campo, valor):
    rota = mz.MATRIZ[chave[0]][chave[1]][chave[2]]
    antes = rota.get(campo)
    rota[campo] = valor
    return antes


falhas = 0
print('MUTANTE 1 · uma rota ANTIGA muda de estado')
antes = muta(ALVO_ANTIGO, 'ESTADO', 'BLOCKED')
morta = corre()
print('   %s.%s ESTADO: %r -> BLOCKED · testes que morreram: %d' % (ALVO_ANTIGO[0], ALVO_ANTIGO[1], antes, morta))
falhas += 0 if morta else 1
muta(ALVO_ANTIGO, 'ESTADO', antes)

print('MUTANTE 2 · a rota NOVA do D23 muda de estado')
antes = muta(ALVO_NOVO, 'ESTADO', 'BLOCKED')
morta = corre()
print('   %s.%s ESTADO: %r -> BLOCKED · testes que morreram: %d' % (ALVO_NOVO[0], ALVO_NOVO[1], antes, morta))
falhas += 0 if morta else 1
muta(ALVO_NOVO, 'ESTADO', antes)

print('MUTANTE 3 · uma rota NOVA aparece sem estar declarada')
mz.MATRIZ['LINKEDIN']['SEARCH_KEYWORD'] = [mz.r('linkedin:busca-inventada', 'DIRECT_HTTP',
                                                'SIM', 'PROVED', 'zero', 'mutante')]
morta = corre()
print('   LINKEDIN.SEARCH_KEYWORD acrescentada · testes que morreram: %d' % morta)
falhas += 0 if morta else 1
del mz.MATRIZ['LINKEDIN']['SEARCH_KEYWORD']

print('\nMUTANTES = %d · SOBREVIVERAM = %d' % (3, falhas))
raise SystemExit(1 if falhas else 0)
