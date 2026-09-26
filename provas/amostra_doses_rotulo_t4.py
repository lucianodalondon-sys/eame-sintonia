#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SORTEIA doses lidas pelo parser canónico nos 163 rótulos reais, para leitura humana.

    python provas/amostra_doses_rotulo_t4.py PASTA_DOS_PDF [N=25] [SEMENTE=26092026]

Imprime, para cada dose sorteada, o rótulo, a cultura, o alvo, a dose e a frase
da linha. Quem lê decide CERTA / ERRADA / NAO_SEI e escreve o veredicto no
relatório com a semente — a amostra repete-se igual com a mesma semente.

Existe porque o leitor geométrico (IT-DOSES) só cobre 21 rótulos e, neles, o
parser dá quase nenhuma dose: a precisão nos blocos de prosa não tem outra régua.
"""
import hashlib
import json
import logging
import os
import random
import sys
import warnings

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'coleta'))
import rotulo_t4_it as R  # noqa: E402

MANIFESTO = os.path.join(ROOT, 'data', 'raw', 'IT-ROTULOS', '_MANIFESTO.json')


def main(argv):
    logging.disable(logging.CRITICAL)
    warnings.filterwarnings('ignore')
    pasta = argv[0]
    n = int(argv[1]) if len(argv) > 1 else 25
    semente = int(argv[2]) if len(argv) > 2 else 26092026
    with open(MANIFESTO, encoding='utf-8') as f:
        man = json.load(f)
    reg = R.ler_registo()
    universo = []
    for it in man['ITENS']:
        with open(os.path.join(pasta, it['ARQUIVO']), 'rb') as f:
            dados = f.read()
        if hashlib.sha256(dados).hexdigest() != it['SHA256']:
            continue
        r = R.ler_rotulo(dados, R.ficha_do_registo(reg, it['REGISTRATION_ID']))
        for l in r['LINHAS_DE_USO']:
            if l['DOSE']['ESTADO'] == R.ENCONTRADO:
                universo.append((it['REGISTRATION_ID'], it['PRODUCT'], l))
    print('UNIVERSO: %d linhas com dose · amostra %d · semente %d' % (len(universo), n, semente))
    for i, (rid, prod, l) in enumerate(random.Random(semente).sample(universo, min(n, len(universo))), 1):
        print('\n#%02d %s %s · %s × %s · %s · %s' % (
            i, rid, prod, l['CULTURA']['VALOR']['CANONICA'], l['ALVO']['VALOR']['LITERAL'],
            l['LIGACAO_NIVEL'], [(d['LITERAL'].replace('\n', ' '), d['UNIDADE']) for d in l['DOSE']['VALOR']]))
        print('    ' + ' '.join(l['CITACAO_DA_LINHA'].split())[:420])
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
