#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CONFERE UM ARQUIVO .sql SEM BANCO DE DADOS.

    python3 scripts/sql_conferir.py supabase/importacoes/IT-LASTMILE-2026-09-02.sql

POR QUE ISTO EXISTE
--------------------
O `psql` não existe nesta máquina, e as credenciais do Supabase só vivem como
segredo do GitHub Actions. Um arquivo de importação de 2,8 MB gerado por script
vai para o Git sem ninguém ter olhado — e o primeiro a olhar seria a produção.

Isto não substitui o banco. Ele não valida tipo, nem chave estrangeira, nem
enum. Valida a classe de erro que um GERADOR comete, e que quebra tudo:

    ASPA DESBALANCEADA. Uma apóstrofe não escapada num texto italiano
    («dell'olivo», «l'annata») transforma o resto do arquivo em lixo, e o
    erro do psql aponta para uma linha centenas de statements adiante.

    O QUE UM GERADOR ERRA É SINTAXE, NÃO SEMÂNTICA. E sintaxe dá para
    conferir sem banco.

Confere também:
  · statement sem `;`
  · `begin` sem `commit`
  · parêntese desbalanceado
  · `insert` sem `on conflict` (neste repositório, importação tem de ser
    idempotente — a cadeia pode rodar duas vezes)
"""
import os
import re
import sys


def aspas_balanceadas(s):
    """Conta apóstrofes fora de escape. `''` é uma aspa escapada em SQL."""
    return s.replace("''", '').count("'") % 2 == 0


def main():
    if len(sys.argv) < 2:
        print('uso: sql_conferir.py <arquivo.sql>')
        return 1
    p = sys.argv[1]
    bruto = open(p, encoding='utf-8').read()

    # tira comentários de linha inteira, que podem ter apóstrofe em prosa
    linhas = [l for l in bruto.split('\n') if not l.lstrip().startswith('--')]
    corpo = '\n'.join(linhas)

    problemas = []

    # ── statements ────────────────────────────────────────────────────────
    stmts, buf = [], []
    for l in corpo.split('\n'):
        buf.append(l)
        if l.rstrip().endswith(';') and aspas_balanceadas('\n'.join(buf)):
            stmts.append('\n'.join(buf))
            buf = []
    if [x for x in buf if x.strip()]:
        problemas.append(('SEM_PONTO_E_VIRGULA',
                          'sobrou texto depois do ultimo `;`: %s'
                          % ' '.join(buf)[:160]))

    for i, st in enumerate(stmts, 1):
        if not aspas_balanceadas(st):
            problemas.append(('ASPA_DESBALANCEADA',
                              'statement %d: %s' % (i, st[:200])))
        # parênteses fora de string
        semstr = re.sub(r"'(?:[^']|'')*'", "''", st)
        if semstr.count('(') != semstr.count(')'):
            problemas.append(('PARENTESE_DESBALANCEADO',
                              'statement %d: %d abre, %d fecha · %s'
                              % (i, semstr.count('('), semstr.count(')'), st[:160])))

    # ── transação ─────────────────────────────────────────────────────────
    nb, nc = len(re.findall(r'(?im)^\s*begin\s*;', corpo)), \
        len(re.findall(r'(?im)^\s*commit\s*;', corpo))
    if nb != nc:
        problemas.append(('TRANSACAO_ABERTA', '%d begin para %d commit' % (nb, nc)))

    # ── idempotência ──────────────────────────────────────────────────────
    # ⚠️ NAO usar regex ate o primeiro `;`. Este arquivo tem 4.120 pontos e
    # virgulas DENTRO de string -- texto italiano como «erbacee interrompida;
    # vite e olivo seguem». Um regex ingenuo corta o statement no meio e
    # acusa 240 inserts «sem on conflict» que tem on conflict.
    #
    #     O VALIDADOR QUASE ME FEZ CONSERTAR CODIGO CERTO.
    #
    # A lista `stmts` acima ja foi montada contando aspas. Usa-se ela.
    ins = [x for x in stmts if re.search(r'insert into public\.', x)]
    sem_conflito = [x for x in ins if 'on conflict' not in x.lower()]
    if sem_conflito:
        problemas.append(('INSERT_SEM_ON_CONFLICT',
                          '%d de %d inserts nao sao idempotentes. Ex.: %s'
                          % (len(sem_conflito), len(ins), sem_conflito[0][:160])))

    print('arquivo: %s · %.0f KB' % (os.path.basename(p), os.path.getsize(p) / 1024))
    print('statements: %d · inserts: %d' % (len(stmts), len(ins)))
    print('begin/commit: %d/%d' % (nb, nc))
    print()
    if not problemas:
        print('SQL_CONFERIDO=PASS  (sintaxe de gerador; nao substitui o banco)')
        return 0
    print('SQL_CONFERIDO=FAIL')
    for tipo, det in problemas[:12]:
        print('  [%s] %s' % (tipo, det))
    if len(problemas) > 12:
        print('  ... e mais %d' % (len(problemas) - 12))
    return 1


if __name__ == '__main__':
    sys.exit(main())
