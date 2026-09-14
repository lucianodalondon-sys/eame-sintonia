#!/usr/bin/env python3
"""Portao: recusa a consulta do censo se ela nao for puramente de leitura.

A primeira versao usava lista negra de palavras e reprovou a propria consulta,
porque has_table_privilege(c.oid, 'INSERT') pergunta POR um privilegio de
escrita sem escrever nada. A palavra estava la; a mutacao nao.

    PROCURAR A PALAVRA != PROCURAR O ACTO.

Passa a lista branca: depois de remover comentarios e literais, cada instrucao
tem de comecar por select, with ou set. Tudo o resto e recusado, incluindo o
que ainda nao sabemos nomear. Uma lista branca falha fechada; uma lista negra
falha aberta.

Uso: python3 provas/rls_censo_portao.py provas/rls_censo_metadados.sql
"""
import re, sys, pathlib

PERMITIDO = ("select", "with", "set")


def limpar(sql):
    sql = re.sub(r"--[^\n]*", " ", sql)          # comentarios de linha
    sql = re.sub(r"/\*.*?\*/", " ", sql, flags=re.S)  # comentarios de bloco
    sql = re.sub(r"'(?:[^']|'')*'", "''", sql)   # literais: '...INSERT...' vira ''
    sql = re.sub(r"^\s*\\[^\n]*", " ", sql, flags=re.M)  # meta-comandos psql (\pset)
    return sql


def main(caminho):
    bruto = pathlib.Path(caminho).read_text(encoding="utf-8")
    recusas = []
    for i, instr in enumerate(limpar(bruto).split(";"), 1):
        instr = instr.strip()
        if not instr:
            continue
        primeira = instr.split()[0].lower()
        if primeira not in PERMITIDO:
            recusas.append(f"instrucao {i} comeca por {primeira!r}, e so se permite {PERMITIDO}")

    for r in recusas:
        print("RECUSADO:", r)
    if recusas:
        return 1
    print("SQL_READ_ONLY=PROVED  (lista branca: so select/with/set)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
