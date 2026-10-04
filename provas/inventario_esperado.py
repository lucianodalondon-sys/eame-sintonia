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

    python3 provas/inventario_esperado.py            # imprime a lista
    python3 provas/inventario_esperado.py --sql      # SQL que devolve o excedente
"""
import glob
import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# O livro-razão do aplicador não é schema de domínio e não nasce de uma
# migration: ele nasce em motor/cadeia_canonica.sh, porque é ele que
# precisa existir ANTES da primeira migration para saber o que não aplicar.
# Fica declarado aqui pelo nome, para que o pré-voo não o trate como objeto
# criado à mão no painel — que é exatamente o que ele existe para detectar.
INFRAESTRUTURA_DO_APLICADOR = ('schema_migracao',)


def tabelas_declaradas():
    achadas = set(INFRAESTRUTURA_DO_APLICADOR)
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


# ═════════════════════════════════════════════════════════════════════════
# O QUE AS MIGRATIONS DECLARAM COMO UNICO
#
# A mesma pergunta do resto deste ficheiro — «o que e que o Git diz que
# existe?» — aplicada a outra coisa: as CHAVES UNICAS.
#
# Ela existe porque um `on conflict do nothing` sem uma constraint unica que o
# sustente NAO DEDUPLICA NADA, e passa despercebido: o SQL e valido, o insert
# corre, e cada chamada acrescenta outra linha.
#
#     ON CONFLICT DO NOTHING SEM CONSTRAINT RELEVANTE != DEDUPLICACAO.
#
# Foi MEDIDO nesta casa, duas vezes: em `tests/test_m2_rota_forward.py:146`
# (23 organizacoes e 23 origens ao fim de uma suite) e outra vez em
# `provas/a_rota_m2_atravessa.py`, onde a forma partida sobreviveu ao conserto
# do teste. Quem consome isto e `provas/o_dedupe_tem_constraint.py`.
#
# ⚠️ O QUE ISTO NAO E. Nao e o esquema do banco: e o que as migrations
# DECLARAM. Um indice criado a mao no painel nao aparece aqui — e nao deve,
# porque a cicatriz do Brasil e exatamente essa.


def _colunas(txt):
    return frozenset(c.strip().strip('"').lower()
                     for c in txt.split(',') if c.strip())


def uniques_declaradas():
    """{tabela: {frozenset(colunas), ...}} — so o que as migrations declaram.

    Cobre as quatro formas usadas neste repositorio:

        create table public.X ( ... unique (a, b) ... )
        create table public.X ( ... constraint nome unique (a, b) ... )
        create table public.X ( ... col tipo unique ... )   -- unique de coluna
        create unique index nome on public.X (a, b)
        alter table public.X add constraint nome unique (a, b)

    `nulls not distinct` e ruido para esta pergunta e e removido: ele muda o
    tratamento do NULL, nao QUAIS colunas formam a chave.

    PRIMARY KEY tambem entra. Uma PK e unica, e um `on conflict` pode
    legitimamente apoiar-se nela — `registro_substancia` faz isso.
    """
    fora = {}

    def por(tab, cols):
        if cols:
            fora.setdefault(tab, set()).add(cols)

    for f in sorted(glob.glob(os.path.join(RAIZ, 'supabase', 'migrations', '*.sql'))):
        with open(f, encoding='utf-8') as h:
            txt = re.sub(r'--[^\n]*', '', h.read())
        baixo_original = txt.lower()
        baixo = baixo_original.replace('nulls not distinct', '')

        # 1 · o corpo de cada `create table` — do parentese ate ao `;`
        for m in re.finditer(r'create table (?:if not exists )?public\.([a-z_]+)\s*\((.*?)\n\s*\)\s*;',
                             baixo, re.S):
            tab, corpo = m.group(1), m.group(2)
            for u in re.finditer(r'(?:constraint\s+[a-z_]+\s+)?unique\s*\(([^)]*)\)', corpo):
                por(tab, _colunas(u.group(1)))
            # a MESMA tabela, relida com o texto original, so para saber quais
            # dessas chaves sao NULLS NOT DISTINCT
            mo = re.search(
                r'create table (?:if not exists )?public\.' + tab
                + r'\s*\((.*?)\n\s*\)\s*;', baixo_original, re.S)
            if mo:
                for u in re.finditer(
                        r'(?:constraint\s+[a-z_]+\s+)?unique\s+nulls not distinct\s*\(([^)]*)\)',
                        mo.group(1)):
                    por(tab + NND, _colunas(u.group(1)))
            for u in re.finditer(r'primary key\s*\(([^)]*)\)', corpo):
                por(tab, _colunas(u.group(1)))
            # unique DE COLUNA: `ror_id text unique` — e `primary key` na coluna
            for linha in corpo.split('\n'):
                l = linha.strip().rstrip(',')
                if re.search(r'\bunique\b', l) and '(' not in l:
                    nome = l.split()[0].strip('"')
                    if nome not in ('constraint', 'unique', 'primary'):
                        por(tab, frozenset([nome]))
                if re.search(r'\bprimary key\b', l) and '(' not in l:
                    nome = l.split()[0].strip('"')
                    if nome not in ('constraint', 'unique', 'primary'):
                        por(tab, frozenset([nome]))

        # 2 · indices unicos. O `where ...` de um indice PARCIAL fica de fora
        #     das colunas de proposito: um indice parcial arbitra `on conflict`
        #     so quando a clausula repete o mesmo predicado, e este inventario
        #     nao promete essa nuance. Quem consome trata-o como PARCIAL.
        for m in re.finditer(
                r'create unique index (?:if not exists )?[a-z_]+\s+on\s+public\.([a-z_]+)\s*\(([^)]*)\)([^;]*)',
                baixo):
            tab, cols, resto = m.group(1), m.group(2), m.group(3)
            if 'where' in resto:
                fora.setdefault(tab + PARCIAL, set()).add(_colunas(cols))
            else:
                por(tab, _colunas(cols))

        # 3 · constraints acrescentadas depois
        for m in re.finditer(
                r'alter table (?:only )?public\.([a-z_]+)[^;]*?add constraint\s+[a-z_]+\s+unique\s*\(([^)]*)\)',
                baixo, re.S):
            por(m.group(1), _colunas(m.group(2)))

        # 4 · o que uma migration derruba, deixa de valer
        for m in re.finditer(r'drop table (?:if exists )?public\.([a-z_]+)', baixo):
            fora.pop(m.group(1), None)
            fora.pop(m.group(1) + PARCIAL, None)

    return fora


# Sufixo de chave para «este unique existe, mas e PARCIAL». Guardado separado
# porque UNICO TOTAL != UNICO PARCIAL: o segundo so arbitra dentro do proprio
# predicado, e chamar-lhe cobertura seria dizer mais do que se mediu.
PARCIAL = '\x1f?'

# Sufixo para «esta chave e NULLS NOT DISTINCT». A distincao importa quando um
# insert OMITE uma das colunas da chave: com NULLS NOT DISTINCT o NULL compara
# igual a NULL e a chave AINDA arbitra o `on conflict`; com o unique normal do
# SQL, dois NULLs sao distintos e a clausula nunca dispara. Duas semanticas
# opostas com a mesma palavra, e por isso nao se achatam numa so.
NND = '\x1f!'


def sql_do_excedente():
    lista = ', '.join("'%s'" % t for t in tabelas_declaradas())
    return ("select coalesce(string_agg(tablename, ', ' order by tablename), '') "
            "from pg_tables where schemaname='public' and tablename not in (%s)" % lista)


if __name__ == '__main__':
    if '--sql' in sys.argv:
        print(sql_do_excedente())
    elif '--uniques' in sys.argv:
        u = uniques_declaradas()
        totais = {k: v for k, v in u.items()
                  if not k.endswith(PARCIAL) and not k.endswith(NND)}
        print('TABELAS_COM_UNIQUE_DECLARADO=%d' % len(totais))
        for t in sorted(u):
            marca = (' (PARCIAL)' if t.endswith(PARCIAL)
                     else ' (NULLS NOT DISTINCT)' if t.endswith(NND) else '')
            for cols in sorted(u[t], key=sorted):
                print('  %-34s %s%s' % (t.replace(PARCIAL, '').replace(NND, ''),
                                        ', '.join(sorted(cols)), marca))
    else:
        t = tabelas_declaradas()
        print('TABELAS_DECLARADAS_NAS_MIGRATIONS=%d' % len(t))
        for x in t:
            print('  ' + x)
