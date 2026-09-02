#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LÊ O PAR (ato, veredito) DA SAÍDA COMPLETA DO WORKFLOW.

    python3 scripts/ler_saida_leque.py <arquivo .output do task>

⚠️ POR QUE ISTO, E NÃO O `journal.jsonl`
------------------------------------------
O journal guarda o resultado de cada AGENTE, isolado. O par (ato lido, veredito do
refutador) só existe no valor de RETORNO do estágio do pipeline — e esse valor está no
arquivo `.output` da tarefa, não no journal.

Tentei antes reconstruir o par por heurística, casando o CELEX que o refutador cita. Ela
errou: os dois atos mais importantes (32026R1421 e 32026R1353, os que trazem as duas
refutações graves) ficaram SEM_VEREDITO_CASADO, e outros casaram com margem 1.

    RECONSTRUIR UM VÍNCULO QUE A FONTE JÁ TEM É INVENTAR ERRO DE GRAÇA.

O vínculo verdadeiro estava a um arquivo de distância.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ABRE, FECHA, ASPAS, BARRA = '{', '}', '"', chr(92)


def objeto_em(texto, inicio):
    """O objeto JSON que começa em `inicio`, por balanceamento de chaves fora de string."""
    prof = 0
    dentro = False
    escapa = False
    for k in range(inicio, len(texto)):
        c = texto[k]
        if escapa:
            escapa = False
            continue
        if c == BARRA:
            escapa = True
            continue
        if c == ASPAS:
            dentro = not dentro
            continue
        if dentro:
            continue
        if c == ABRE:
            prof += 1
        elif c == FECHA:
            prof -= 1
            if prof == 0:
                return texto[inicio:k + 1]
    return None


def main():
    if len(sys.argv) < 2:
        print(__doc__); return 2
    t = open(sys.argv[1], encoding='utf-8', errors='replace').read()
    marca = '"bruto_atos"'
    i = t.find(marca)
    if i < 0:
        print('NAO_ACHEI bruto_atos'); return 1
    # a raiz é a última abertura de objeto antes da marca cuja análise fecha bem
    inicio = t.rfind(ABRE + '"atos_lidos"', 0, i)
    if inicio < 0:
        inicio = t.rfind(ABRE, 0, i)
    bruto = objeto_em(t, inicio)
    if not bruto:
        print('NAO_FECHOU o objeto'); return 1
    try:
        d = json.loads(bruto)
    except ValueError as e:
        print('PARSE_FALHOU: %s' % e); return 1

    pares = d.get('bruto_atos') or []
    print('pares (ato, veredito): %d' % len(pares))
    for a in pares:
        v = a.get('veredito') or {}
        print('  %-12s refutado=%s' % (a.get('celex'), v.get('refuted')))
    os.makedirs(os.path.join(ROOT, '.tmp'), exist_ok=True)
    with open(os.path.join(ROOT, '.tmp', 'wf.json'), 'w', encoding='utf-8') as f:
        json.dump(d, f, ensure_ascii=False)
    print('\ngravado .tmp/wf.json')
    return 0


if __name__ == '__main__':
    sys.exit(main())
