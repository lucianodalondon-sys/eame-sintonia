#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A MUTAÇÃO DIZ SE A LINHAGEM DO READY ESTÁ MESMO GUARDADA.

    BANCO_DESCARTAVEL_URL=postgresql://postgres@127.0.0.1:5433/descartavel \\
        python3 provas/mutacao_da_linhagem_do_ready.py

Vinte e nove casos verdes só provam que eles passaram. A pergunta é outra:

    SE EU PARTIR A PONTE, ALGUM FICA VERMELHO?

Muta-se uma CÓPIA da árvore, e cada mutante corre contra um banco
descartável NOVO — dois mutantes a partilhar banco partilhariam o estado que
o primeiro deixou, e o segundo mediria a sujidade do primeiro.

    REAL_NETWORK = 0 · PAID_USD = 0 · A ÁRVORE REAL NÃO É TOCADA.
"""
import os
import shutil
import subprocess
import sys
import tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROVA = 'provas/a_linhagem_do_ready.py'

ADM = 'admissao/admissao.py'
ING = 'coleta/ingresso.py'
ROTA = 'coleta/rota_forward_documento.py'

MUTACOES = [
    ('M1 · o contrato deixa de levar a observacao', ADM,
     '        "RAW_OBSERVATION_ID": "NAO SEI" if observacao is None else observacao,\n',
     '',
     'sem o campo, o READY nao consegue nomear o bruto de onde veio'),

    ('M2 · a observacao e trocada pela CORRIDA', ADM,
     '        "RAW_OBSERVATION_ID": "NAO SEI" if observacao is None else observacao,',
     '        "RAW_OBSERVATION_ID": decisao.corrida,',
     'RUN != OBSERVATION: a corrida nomeia a passagem, nao a observacao'),

    ('M3 · a observacao e trocada pelo SHA do item', ADM,
     '        "RAW_OBSERVATION_ID": "NAO SEI" if observacao is None else observacao,',
     '        "RAW_OBSERVATION_ID": decisao.item,',
     'SHA256 identifica BYTES, e nunca a observacao'),

    ('M4 · a observacao e fabricada quando falta', ADM,
     '        "RAW_OBSERVATION_ID": "NAO SEI" if observacao is None else observacao,',
     '        "RAW_OBSERVATION_ID": observacao or 1,',
     'ausencia diz-se; um id inventado aponta para o bruto de outra pessoa'),

    ('M5 · a rota deixa de entregar a observacao a porta', ROTA,
     "        'raw_asset_id': unidade.get('RAW_ASSET_ID'),\n",
     '',
     'o valor ja estava em maos; deixar de o passar reabre o buraco'),

    ('M6 · a especie do texto passa a ser inferida', ING,
     '# ⚠️ `RAW_OBSERVATION_ID` NAO ENTRA AQUI, e a ausencia e deliberada. Ele e',
     '# MUTANTE: a especie do texto deixa de vir declarada.\n'
     '# ⚠️ `RAW_OBSERVATION_ID` NAO ENTRA AQUI, e a ausencia e deliberada. Ele e',
     'este mutante e um NO-OP de proposito: ele prova que a bateria nao'
     ' morre por qualquer mudanca, so pelas que partem a ponte'),
]


def _copia(destino):
    pesadas = {'.git', 'node_modules', '__pycache__', '.venv', '.tmp',
               'build', 'data'}
    for nome in os.listdir(RAIZ):
        if nome in pesadas:
            continue
        o, a = os.path.join(RAIZ, nome), os.path.join(destino, nome)
        if os.path.isdir(o):
            shutil.copytree(o, a, symlinks=True,
                            ignore=shutil.ignore_patterns('__pycache__',
                                                          'node_modules'))
        else:
            shutil.copy2(o, a)
    for nome in ('.git', 'data'):
        os.symlink(os.path.join(RAIZ, nome), os.path.join(destino, nome))


def _banco_novo(base_url, nome):
    """Um banco por mutante. `descartavel` e `derivado` sao os nomes que a
    trava de `_e_descartavel` permite — e ela esta certa: nao se corre isto
    contra um nome qualquer."""
    from urllib.parse import urlparse, urlunparse
    u = urlparse(base_url)
    admin = urlunparse(u._replace(path='/postgres'))
    subprocess.run(['psql', '-q', '-c',
                    'drop database if exists %s' % nome, admin],
                   capture_output=True, text=True)
    subprocess.run(['psql', '-q', '-c', 'create database %s' % nome, admin],
                   capture_output=True, text=True)
    return urlunparse(u._replace(path='/' + nome))


def _correr(arvore, url):
    amb = dict(os.environ, BANCO_DESCARTAVEL_URL=url)
    p = subprocess.run([sys.executable, PROVA], cwd=arvore,
                       capture_output=True, text=True, env=amb, timeout=600)
    return p.returncode, (p.stdout or '') + (p.stderr or '')


def main():
    base_url = os.environ.get('BANCO_DESCARTAVEL_URL')
    if not base_url:
        print('SEM BANCO DESCARTAVEL — e SKIP != PASS.')
        print('MUTACAO_DA_LINHAGEM=NOT_MEASURED')
        return 2

    print('A MUTAÇÃO DA LINHAGEM DO READY')
    print('=' * 74)
    base = tempfile.mkdtemp(prefix='linhagem-mut-')
    arvore = os.path.join(base, 'arvore')
    os.makedirs(arvore)
    try:
        _copia(arvore)
        codigo, saida = _correr(arvore, _banco_novo(base_url, 'descartavel'))
        if codigo != 0:
            print('A CÓPIA JÁ NASCE VERMELHA — a mutação não mediria nada.')
            print(saida[-2500:])
            return 3
        print('cópia limpa: prova VERDE\n')

        sobreviventes, noop = [], []
        for nome, rel, velho, novo, garantia in MUTACOES:
            alvo = os.path.join(arvore, rel)
            with open(alvo, encoding='utf-8') as f:
                original = f.read()
            if velho not in original:
                print('%-52s ALVO_AUSENTE' % nome[:52])
                sobreviventes.append((nome, 'ALVO_AUSENTE'))
                continue
            with open(alvo, 'w', encoding='utf-8') as f:
                f.write(original.replace(velho, novo, 1))
            try:
                url = _banco_novo(base_url, 'derivado')
                codigo, saida = _correr(arvore, url)
            finally:
                with open(alvo, 'w', encoding='utf-8') as f:
                    f.write(original)
            morta = codigo != 0
            quantas = saida.count('  FAIL ')
            esperado_vivo = nome.startswith('M6')
            marca = 'MORTA    ' if morta else 'SOBREVIVE'
            print('%-52s %s (%d casos vermelhos)' % (nome[:52], marca, quantas))
            print('%-52s   guarda: %s' % ('', garantia[:66]))
            if esperado_vivo:
                noop.append((nome, morta))
            elif not morta:
                sobreviventes.append((nome, garantia))

        print('=' * 74)
        reais = [m for m in MUTACOES if not m[0].startswith('M6')]
        print('MUTANTS           = %d' % len(reais))
        print('MUTANT_SURVIVORS  = %d' % len(sobreviventes))
        for nome, esperado in noop:
            print('CONTRAPROVA       · %s -> %s'
                  % (nome[:44], 'MORREU (e nao devia!)' if esperado
                     else 'sobreviveu, como tinha de ser'))
        for nome, porque in sobreviventes:
            print('  SOBREVIVEU · %s — ninguem guarda: %s' % (nome, porque))
        mau_noop = [n for n, m in noop if m]
        return 0 if not sobreviventes and not mau_noop else 1
    finally:
        shutil.rmtree(base, ignore_errors=True)


if __name__ == '__main__':
    raise SystemExit(main())
