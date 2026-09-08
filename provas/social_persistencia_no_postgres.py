#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O CONTRATO DE PERSISTENCIA SOCIAL contra um PostgreSQL 16 de verdade.

DESIGNED nao e DB_TESTED. Esta prova existe para que a distancia entre os dois
seja percorrida por uma maquina, e nao por uma frase num relatorio.

Ela aplica as migrations 001..016 mais a 023, e entao corre a suite
`tests/test_social_persistencia_pg.py` contra o banco resultante — o mesmo
Postgres 16, as mesmas constraints, os mesmos erros. Sem banco, a suite e
PULADA; e teste pulado nao prova nada, e por isso o CI a corre aqui.

    COMMENT_ID NAO E COMMENT_TEXT.
    REPLY NAO E TOP-LEVEL.
    SEEN NAO E PERSISTED.

A TRAVA CONTRA O ACIDENTE E REUTILIZADA, NAO REESCRITA
------------------------------------------------------
`_e_descartavel()` vive em `provas/preservar_coleta_no_postgres.py` e ja foi
endurecida uma vez nesta casa: a versao anterior procurava PEDACOS DE TEXTO
(`localhost`, `@db:`) em qualquer sitio da URL, e por isso aceitava
`localhost.atacante.example`. Escrever uma segunda trava aqui criaria duas
verdades sobre «o que e um banco descartavel», e a segunda divergiria na
primeira pressa — provavelmente voltando a comparar substring.
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

# So o necessario para identidade, conteudo, comentario e checkpoint. A 008 e
# uma VERIFICACAO do estado apos a 007 e falha se corrida antes das seguintes;
# ela roda no fim, como conferencia, e nao no meio, como passo.
MIGRATIONS = ['001', '002', '003', '004', '005', '006', '007', '009', '010',
              '011', '012', '013', '014', '015', '016', '023']


def aplicar(url):
    caminhos = []
    pasta = os.path.join(RAIZ, 'supabase', 'migrations')
    for n in MIGRATIONS:
        achados = [f for f in sorted(os.listdir(pasta)) if f.startswith(n + '_')]
        if not achados:
            raise SystemExit('migration %s nao encontrada' % n)
        caminhos.append(os.path.join(pasta, achados[0]))
    for c in caminhos:
        r = subprocess.run(['psql', url, '-v', 'ON_ERROR_STOP=1', '-q', '-f', c],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print('FALHOU a aplicar %s' % os.path.basename(c))
            print(r.stderr.strip()[:1500])
            raise SystemExit(1)
        print('  aplicada  %s' % os.path.basename(c))


def main():
    url = os.environ.get('BANCO_DESCARTAVEL_URL') or ''
    if not _e_descartavel(url):
        raise SystemExit(
            "RECUSADO: '%s' nao parece um banco descartavel local. "
            "Esta prova nunca corre contra producao." % url)
    print('MIGRATIONS')
    aplicar(url)
    print('\nA SUITE, contra o banco que acabou de nascer')
    # `discover()` exige pacote importavel e `tests/` nao tem __init__.py.
    # Carregar pelo caminho do ficheiro evita acrescentar um so para isto.
    sys.path.insert(0, os.path.join(RAIZ, 'tests'))
    carregador = unittest.TestLoader()
    suite = carregador.loadTestsFromName('test_social_persistencia_pg')
    resultado = unittest.TextTestRunner(verbosity=2).run(suite)
    if resultado.testsRun == 0:
        raise SystemExit('NENHUM teste correu — uma suite vazia nao e uma prova')
    if resultado.skipped:
        raise SystemExit('teste PULADO nesta prova nao vale: %d pulado(s)'
                         % len(resultado.skipped))
    if not resultado.wasSuccessful():
        raise SystemExit(1)
    print('\n%d provas verdes contra Postgres 16 real.' % resultado.testsRun)
    print('SOCIAL_PERSISTENCE = DB_TESTED. NAO e LIVE: nada foi escrito em producao.')


if __name__ == '__main__':
    main()
