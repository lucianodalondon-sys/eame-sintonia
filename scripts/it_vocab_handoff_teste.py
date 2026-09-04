#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O TESTE MINIMO QUE PROVA QUE O MOTOR PASSOU A RECONHECER OS CASOS.

    python3 scripts/it_vocab_handoff_teste.py

Este ficheiro existe para ser LIDO PELO DONO DO MOTOR e copiado para a suite
dele. Aqui ele roda contra uma copia EM MEMORIA do motor (lida da branch dele
com git show) mais os 38 ISSUE_ID propostos — prova que o teste passa ANTES de
alguem tocar em v21_normalizar.py.

    UM HANDOFF QUE NAO TRAZ O TESTE JA VERDE E UM PEDIDO, NAO UMA ENTREGA.

Cada asserto e ancorado numa FRASE REAL do acervo italiano, com o SOURCE_ID ao
lado. Nao ha frase inventada para o teste passar: se o acervo nao nomeia o alvo,
o ID entra sem asserto e aparece na lista dos mudos, que e a verdade sobre ele.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

from it_vocab_handoff import motor, aprovados, alias_vivos, SAIDA  # noqa: E402


def alias_por_id():
    """Os apelidos como ficam DEPOIS do reparo — os do handoff, nao os da proposta."""
    h = json.load(open(os.path.join(ROOT, SAIDA)))
    return {r['ISSUE_ID_PROPOSTO']: r['APELIDOS_PROPOSTOS'] for r in h['ROWS']}, h


def main():
    M, ref, sha = motor()
    novos, h = alias_por_id()
    VELHO = {k: list(v) for k, v in M.ISSUE_ALIAS.items()}
    NOVA = dict(VELHO)
    NOVA.update({k: v for k, v in novos.items() if v})

    falhas = []

    # 1 · cada ID novo que o acervo nomeia tem de sair da frase real que o nomeia
    for t in h['TESTE_MINIMO']:
        achados = M._todos(t['FRASE'], NOVA)
        if t['ISSUE_ID'] not in achados:
            falhas.append('NAO RECONHECE %s em %s: %r -> %s'
                          % (t['ISSUE_ID'], t['SOURCE_ID'], t['FRASE'][:90], achados))

    # 2 · nenhum ID existente pode perder o que ja reconhecia
    for t in h['TESTE_MINIMO']:
        antes = set(M._todos(t['FRASE'], VELHO))
        depois = set(M._todos(t['FRASE'], NOVA))
        perdidos = antes - depois
        # o sequestro declarado e o unico caso legitimo de troca
        legitimos = {s['ISSUE_ID_ANTIGO'] for s in h['SEQUESTROS']}
        for p in perdidos - legitimos:
            falhas.append('PERDA NAO DECLARADA: %s deixou de sair de %s' % (p, t['SOURCE_ID']))

    # 3 · nenhum apelido novo pode ser expressao regular: o motor casa literal
    for iid, apel in novos.items():
        for a in apel:
            if any(c in a for c in '(?[]{}*+^$\\|'):
                falhas.append('APELIDO NAO LITERAL sobreviveu ao reparo: %s %r' % (iid, a))

    # 4 · nenhum apelido pode ter dois donos
    dono = {}
    for iid, apel in NOVA.items():
        for a in apel:
            na = M._n(a)
            if na in dono and dono[na] != iid:
                falhas.append('DOIS DONOS do apelido %r: %s e %s' % (na, dono[na], iid))
            dono[na] = iid

    print('MOTOR      ', ref, sha[:12])
    print('IDS ANTES  ', len(VELHO))
    print('IDS DEPOIS ', len(NOVA))
    print('ASSERTOS   ', len(h['TESTE_MINIMO']), 'ancorados em frase real')
    print('MUDOS      ', len(h['IDS_NOVOS_MUDOS_NO_ACERVO_DE_FALA']),
          '(entram pelos rotulos, nao pelo acervo de fala)')
    if falhas:
        print('FALHAS     ', len(falhas))
        for f in falhas:
            print('   ', f)
        raise SystemExit(1)
    print('RESULTADO   PASS')


if __name__ == '__main__':
    main()
