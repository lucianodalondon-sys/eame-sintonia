#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A CONTAGEM DA SUÍTE · a equação que fecha o denominador.

    python3 scripts/v21_contagem_da_suite.py

O relatório dizia «737 descobertos · 732 executados · 6 falhas · 2 erros» e os
números não fechavam. Não fechavam porque são DOIS UNIVERSOS, e ninguém tinha
dito qual era qual.

    UM NÚMERO SEM DENOMINADOR NÃO É UMA MEDIDA: É UM ADJETIVO.

UNIVERSO 1 · CASOS DESCOBERTOS
    O que `unittest.defaultTestLoader.discover()` conta ANTES de rodar. É o
    número que o ledger publica em `TEST_COUNT_CURRENT`.

UNIVERSO 2 · CASOS EXECUTADOS
    O que o runner conta em `testsRun`. Menor, e a diferença tem nome: uma
    classe cujo `setUpClass` levanta exceção NÃO executa nenhum dos seus
    métodos. O unittest registra UM `_ErrorHolder` — que não é um teste e não
    entra em `testsRun` — e os métodos ficam sem rodar.

E os «2 erros» também são duas coisas diferentes:
    · `_FailedTest`  — módulo que não importa. É um caso, roda e dá erro.
    · `_ErrorHolder` — falha de `setUpClass`. NÃO é um caso e não é contado.

Este arquivo não conserta teste nenhum. Ele imprime a equação e falha se ela
não fechar.
"""
import contextlib
import io
import os
import sys
import unittest
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAIDA = os.path.join(ROOT, 'data', 'samples', 'AUDITORIA-SOMBRA',
                     'V113-CONTAGEM-DA-SUITE.json')


def medir():
    loader = unittest.defaultTestLoader
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        suite = loader.discover(os.path.join(ROOT, 'tests'))
        total = suite.countTestCases()
        r = unittest.TextTestRunner(stream=buf, verbosity=0).run(suite)
    erros_de_caso = [(str(t), type(t).__name__) for t, _tb in r.errors
                     if isinstance(t, unittest.TestCase)]
    erros_de_classe = [(str(t), type(t).__name__) for t, _tb in r.errors
                       if not isinstance(t, unittest.TestCase)]
    passou = (r.testsRun - len(r.failures) - len(erros_de_caso)
              - len(r.skipped) - len(r.expectedFailures)
              - len(r.unexpectedSuccesses))
    return {
        'TOTAL_DISCOVERED': total,
        'RAN': r.testsRun,
        'NEVER_RAN': total - r.testsRun,
        'PASSED': passou,
        'FAILED': len(r.failures),
        'ERROR_AS_TEST': len(erros_de_caso),
        'ERROR_AS_CLASS_SETUP': len(erros_de_classe),
        'SKIPPED': len(r.skipped),
        'XFAIL': len(r.expectedFailures),
        'XPASS': len(r.unexpectedSuccesses),
        'ERRORS_REPORTED': len(r.errors),
        'ERROR_DETAIL': erros_de_caso + erros_de_classe,
        'FAILED_DETAIL': [str(t) for t, _tb in r.failures],
    }


def main():
    m = medir()
    ok_dentro = (m['RAN'] == m['PASSED'] + m['FAILED'] + m['ERROR_AS_TEST']
                 + m['SKIPPED'] + m['XFAIL'] + m['XPASS'])
    ok_fora = m['TOTAL_DISCOVERED'] == m['RAN'] + m['NEVER_RAN']

    print('=' * 74)
    print('UNIVERSO 1 · DESCOBERTOS            %d' % m['TOTAL_DISCOVERED'])
    print('   menos NUNCA EXECUTADOS          -%d   (classe abortada no setUpClass)'
          % m['NEVER_RAN'])
    print('UNIVERSO 2 · EXECUTADOS (testsRun)  %d' % m['RAN'])
    print('=' * 74)
    print('   PASSOU                           %d' % m['PASSED'])
    print('   FALHOU                           %d' % m['FAILED'])
    print('   ERRO (o caso rodou e deu erro)   %d' % m['ERROR_AS_TEST'])
    print('   PULADOS                          %d' % m['SKIPPED'])
    print('   XFAIL / XPASS                    %d / %d' % (m['XFAIL'], m['XPASS']))
    print('   ' + '-' * 44)
    print('   soma                             %d'
          % (m['PASSED'] + m['FAILED'] + m['ERROR_AS_TEST'] + m['SKIPPED']
             + m['XFAIL'] + m['XPASS']))
    print()
    print('ERROS RELATADOS PELO RUNNER          %d' % m['ERRORS_REPORTED'])
    print('   dos quais SAO CASOS               %d  (entram em testsRun)'
          % m['ERROR_AS_TEST'])
    print('   dos quais SAO setUpClass          %d  (NAO entram em testsRun)'
          % m['ERROR_AS_CLASS_SETUP'])
    for t, k in m['ERROR_DETAIL']:
        print('     %-12s %s' % (k, t))
    print()
    print('EQUACAO DE FORA  %s' % ('FECHA' if ok_fora else 'NAO FECHA'))
    print('EQUACAO DE DENTRO %s' % ('FECHA' if ok_dentro else 'NAO FECHA'))

    m.update({'COLLECTION': 'V113-CONTAGEM-DA-SUITE',
              'SOURCE': 'unittest.defaultTestLoader.discover("tests") + '
                        'TextTestRunner, nesta arvore',
              'CAPTURED_AT': date.today().isoformat(),
              'LAW': 'dois universos: o descoberto e o executado. A diferenca '
                     'tem nome — classe cujo setUpClass aborta nao executa os '
                     'seus metodos, e o _ErrorHolder que ela gera nao e um '
                     'caso.',
              'EQUATION_OUTER': 'TOTAL_DISCOVERED = RAN + NEVER_RAN',
              'EQUATION_INNER': 'RAN = PASSED + FAILED + ERROR_AS_TEST + '
                                'SKIPPED + XFAIL + XPASS'})
    os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
    import json
    json.dump(m, open(SAIDA, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('gravado em %s' % os.path.relpath(SAIDA, ROOT))
    return 0 if (ok_fora and ok_dentro) else 1


if __name__ == '__main__':
    sys.exit(main())
