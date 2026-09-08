#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O RASTRO DA COLETA contra um PostgreSQL 16 de verdade.

DESIGNED nao e DB_TESTED. Esta prova percorre essa distancia com uma maquina.

Aplica a cadeia canonica mais a migration 024 e corre
`tests/test_rastro_pg.py`. Sem banco a suite e PULADA, e teste pulado nao prova
nada — por isso o CI a corre aqui, e recusa a corrida se algum for pulado.

    NAO E OBRIGATORIO QUE 100% CHEGUE AO FIM.
    E OBRIGATORIO QUE 100% TENHA EXPLICACAO.

A trava contra o acidente e REUTILIZADA de `preservar_coleta_no_postgres.py`,
que ja foi endurecida uma vez nesta casa. Escrever uma segunda criaria duas
verdades sobre «o que e um banco descartavel».
"""
import os
import subprocess
import sys
import unittest

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
sys.path.insert(0, AQUI)
sys.path.insert(0, RAIZ)

from preservar_coleta_no_postgres import _e_descartavel   # noqa: E402

# A 008 e CONFERENCIA e nao criacao: ela corre no fim, pelo chamador.
MIGRATIONS = ['001', '002', '003', '004', '005', '006', '007', '009', '010',
              '011', '012', '013', '014', '015', '016', '017', '018', '019',
              '020', '021', '022', '023', '024']


def aplicar(url):
    pasta = os.path.join(RAIZ, 'supabase', 'migrations')
    for n in MIGRATIONS:
        achados = [f for f in sorted(os.listdir(pasta)) if f.startswith(n + '_')]
        if not achados:
            raise SystemExit('migration %s nao encontrada' % n)
        c = os.path.join(pasta, achados[0])
        r = subprocess.run(['psql', url, '-v', 'ON_ERROR_STOP=1', '-q', '-f', c],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print('FALHOU a aplicar %s' % achados[0])
            print(r.stderr.strip()[:1500])
            raise SystemExit(1)
        print('  aplicada  %s' % achados[0])


def main():
    url = os.environ.get('BANCO_DESCARTAVEL_URL') or ''
    if not _e_descartavel(url):
        raise SystemExit(
            "RECUSADO: '%s' nao parece um banco descartavel local. "
            "Esta prova nunca corre contra producao." % url)
    print('MIGRATIONS')
    aplicar(url)
    print('\nO RED TEAM DO RASTRO, contra o banco que acabou de nascer')
    sys.path.insert(0, os.path.join(RAIZ, 'tests'))
    suite = unittest.TestLoader().loadTestsFromName('test_rastro_pg')
    res = unittest.TextTestRunner(verbosity=2).run(suite)
    if res.testsRun == 0:
        raise SystemExit('NENHUM teste correu — suite vazia nao e prova')
    if res.skipped:
        raise SystemExit('teste PULADO nao vale aqui: %d pulado(s)' % len(res.skipped))
    if not res.wasSuccessful():
        raise SystemExit(1)
    print('\n%d provas verdes contra PostgreSQL 16 real.' % res.testsRun)
    print('OBSERVABILITY = DB_TESTED. NAO e LIVE: nada foi escrito em producao.')


if __name__ == '__main__':
    main()
