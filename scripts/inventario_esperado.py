#!/usr/bin/env python3
"""O QUE O GIT DIZ QUE EXISTE — derivado, para o pré-voo não ser um número mágico.

O pré-voo do supabase-migrate.yml aceitava escrever num banco cujo `public`
tivesse 0, 23, 26 ou 30 tabelas. Era uma lista fixa que envelhecia a cada
migration, e que já estava para trás: o core passou de 30.

Contar tabelas nunca foi a pergunta certa. A pergunta é a cicatriz do
Brasil — "quem for montar este banco do zero amanhã monta um banco que não
funciona", porque lá havia coluna e função criadas à mão no painel, fora de
qualquer .sql. A pergunta certa é:

    o `public` do banco contém alguma coisa que ESTE repositório não cria?

Se contém, o estado não é o que o Git descreve, e escrever nele é escrever
por cima de algo que ninguém declarou. Isso é derivável: as migrations
dizem quais tabelas elas criam.

    python3 scripts/inventario_esperado.py            # imprime a lista
    python3 scripts/inventario_esperado.py --sql      # SQL que devolve o excedente
"""
import glob
import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def tabelas_declaradas():
    achadas = set()
    for f in sorted(glob.glob(os.path.join(RAIZ, 'supabase', 'migrations', '*.sql'))):
        with open(f, encoding='utf-8') as h:
            texto = h.read()
        for m in re.finditer(r'create table (?:if not exists )?public\.([a-z_]+)', texto):
            achadas.add(m.group(1))
        # Uma migration pode aposentar o que outra criou. A 018 não derruba
        # tabela, mas a regra tem de existir antes de precisar dela.
        for m in re.finditer(r'drop table (?:if exists )?public\.([a-z_]+)', texto):
            achadas.discard(m.group(1))
    return sorted(achadas)


def sql_do_excedente():
    lista = ', '.join("'%s'" % t for t in tabelas_declaradas())
    return ("select coalesce(string_agg(tablename, ', ' order by tablename), '') "
            "from pg_tables where schemaname='public' and tablename not in (%s)" % lista)


if __name__ == '__main__':
    if '--sql' in sys.argv:
        print(sql_do_excedente())
    else:
        t = tabelas_declaradas()
        print('TABELAS_DECLARADAS_NAS_MIGRATIONS=%d' % len(t))
        for x in t:
            print('  ' + x)
