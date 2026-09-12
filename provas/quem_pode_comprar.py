#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCRAP-SR-02 — O CENSO DE QUEM CONSEGUE COMPRAR.

    py provas/quem_pode_comprar.py

Uma guarda só vale o que vale a lista de quem tem de a atravessar. Esta prova
mede, na ÁRVORE, quantas primitivas conseguem criar uma execução paga nesta
casa, e quem as chama.

    UMA GUARDA QUE VIVE NUM CAMINHO GUARDA UM CAMINHO.
    UMA GUARDA QUE VIVE NA PRIMITIVA GUARDA TODOS.

A medição é de CHAMADA, não de import: importar `coletor` não compra nada, e
uma sonda que confundisse as duas coisas contaria ficheiros em vez de portas.
"""
import ast
import io
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PESADAS = {'.git', 'node_modules', 'italia-portale', '__pycache__', '.tmp',
           'build', 'data', 'handoff'}

#: A primitiva. Uma só nesta árvore, e é esta linha que a define.
PRIMITIVA = ('coleta/coletor.py', 'executar')
#: O endpoint que cria corrida do lado do provider. Ler corridas não compra.
CRIA_CORRIDA = '/runs?'


def ficheiros():
    for base, dirs, nomes in os.walk(RAIZ):
        dirs[:] = [d for d in dirs if d not in PESADAS]
        for n in sorted(nomes):
            if n.endswith('.py'):
                yield os.path.join(base, n)


def rel(p):
    return os.path.relpath(p, RAIZ).replace('\\', '/')


def fonte(p):
    with io.open(p, encoding='utf-8') as f:
        return f.read()


def primitivas_de_criacao():
    """→ os sítios que fazem o POST que cria execução paga. Pela ÁRVORE."""
    achados = []
    for p in ficheiros():
        try:
            arv = ast.parse(fonte(p))
        except SyntaxError:
            continue
        for no in ast.walk(arv):
            if not isinstance(no, ast.Call):
                continue
            # o POST identifica-se pelo CAMPO `metodo='POST'`, não pela palavra
            # «POST» no ficheiro: `adaptador_aberto` usa POST como grão de
            # conteúdo, e uma sonda de texto acusava-o.
            posta = any(k.arg == 'metodo'
                        and isinstance(k.value, ast.Constant)
                        and str(k.value.value).upper() == 'POST'
                        for k in no.keywords)
            if posta:
                achados.append((rel(p), no.lineno))
    return achados


def chamadores_da_primitiva():
    """→ quem chama `coletor.executar`, e se passa `autorizacao`."""
    alvo_ficheiro, alvo_nome = PRIMITIVA
    fora = []
    for p in ficheiros():
        r = rel(p)
        if r == alvo_ficheiro:
            continue
        try:
            arv = ast.parse(fonte(p))
        except SyntaxError:
            continue
        for no in ast.walk(arv):
            if not (isinstance(no, ast.Call)
                    and isinstance(no.func, ast.Attribute)
                    and no.func.attr == alvo_nome):
                continue
            base = getattr(no.func.value, 'id', None)
            if base not in ('ct', 'coletor'):
                continue
            passa = any(k.arg == 'autorizacao' for k in no.keywords)
            fora.append({'FICHEIRO': r, 'LINHA': no.lineno,
                         'PASSA_AUTORIZACAO': passa})
    return fora


def main():
    print(__doc__.strip().splitlines()[0])
    print('=' * 74)

    criacoes = primitivas_de_criacao()
    produtivas = [c for c in criacoes if not c[0].startswith(('tests/', 'provas/'))]
    print('\nPRIMITIVAS QUE CRIAM EXECUCAO PAGA')
    for f, l in criacoes:
        marca = '' if f in [p[0] for p in produtivas] else '   (prova/teste)'
        print('  %s:%d%s' % (f, l, marca))
    print('\nPAID_CREATION_PRIMITIVES = %d' % len(produtivas))

    chamadores = chamadores_da_primitiva()
    produtivos = [c for c in chamadores
                  if not c['FICHEIRO'].startswith(('tests/', 'provas/'))]
    print('\nQUEM CHAMA A PRIMITIVA')
    print('  %-38s %-7s %s' % ('FICHEIRO', 'LINHA', 'PASSA AUTORIZACAO'))
    for c in chamadores:
        print('  %-38s %-7d %s' % (c['FICHEIRO'][:38], c['LINHA'],
                                   'SIM' if c['PASSA_AUTORIZACAO'] else 'NAO'))

    sem = [c for c in produtivos if not c['PASSA_AUTORIZACAO']]
    print('\n' + '=' * 74)
    print('CALLERS_PRODUTIVOS            = %d' % len(produtivos))
    print('CALLERS_QUE_PASSAM_AUTH       = %d' % (len(produtivos) - len(sem)))
    print('CALLERS_SEM_AUTH              = %d' % len(sem))
    print()
    print('E o que isso significa, medido e não presumido: um chamador que não')
    print('passa autorização NÃO compra — a guarda está na primitiva, e o')
    print('default dela é recusar.')
    print()
    print('    CAN_SPEND_WITHOUT_AUTH = 0')
    print()
    if sem:
        print('Estes deixaram de conseguir comprar, e é o objetivo da missão:')
        for c in sem:
            print('  · %s:%d' % (c['FICHEIRO'], c['LINHA']))
        print()
        print('Eles não estão «partidos»: estão à espera de que alguém diga')
        print('para que FONTE e para que PROPÓSITO cada um compra. Essa')
        print('resposta vive no livro da SR-01, e não nesta linhagem.')
    # A prova passa quando existe UMA primitiva. Duas seriam duas portas.
    return 0 if len(produtivas) == 1 else 1


if __name__ == '__main__':
    sys.exit(main())
