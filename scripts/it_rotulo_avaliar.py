#!/usr/bin/env python3
"""Mede o parser contra o GABARITO MANUAL. Sem isto, 'mais pares' nao quer dizer nada.

O gabarito foi escrito lendo o documento, e nao rodando o parser. Por isso ele pode
reprovar o parser — que e o unico jeito de a medicao valer alguma coisa.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from it_rotulo_parser import parse, alvos_em                    # noqa: E402

GAB = os.path.join(ROOT, 'data/samples/IT-ROTULOS-V1/IT-ROTULOS-GABARITO-V1.json')


def canon_alvo(nome):
    """Traz o alvo do gabarito para o MESMO espaco de nomes do parser.

    Eu escrevi o gabarito com o literal do rotulo ('MOSCA DELLA FRUTTA', 'RUGGINE
    GIALLA', 'CIMICE VERDE') e o parser emite o nome canonico ('MOSCA', 'RUGGINE',
    'CIMICI'). Comparar os dois espacos direto media a MINHA nomenclatura, e nao o
    parser: dava falso positivo em par que estava certo. Isto e conserto da MEDICAO,
    e nao do parser — o parser nao foi tocado por causa disto.
    """
    c = alvos_em(nome)
    return c[0] if len(c) == 1 else (nome if not c else sorted(c)[0])


def avaliar(pdf_dir, publicavel=('SUPPORTED_PAIR',)):
    gab = json.load(open(GAB, encoding='utf-8'))['GOLD']
    tp = fp = fn = 0
    det = []
    trap_viol = []
    for L in gab:
        rid = L['REGISTRATION_ID']
        # NENHUM rotulo do gabarito e pulado. Se o parser nao devolve nada, isso e
        # falha de recall e conta como FN — pular seria melhorar a metrica escondendo
        # exatamente os casos que o parser nao sabe ler. Cheguei a escrever a versao
        # que pulava, e ela subiu o recall de 0,63 para 0,77 sem o parser mudar nada.
        pdf = os.path.join(pdf_dir, '%s.pdf' % rid)
        got = parse(pdf, rid, cache_dir=pdf_dir)
        pub = {(p['CROP'], p['TARGET']) for p in got if p['RELATION'] in publicavel}
        esperado = {(pa['CROP'], canon_alvo(t)) for pa in L['PAIRS'] for t in pa['TARGETS']}
        acertos = pub & esperado
        perdidos = esperado - pub
        extras = pub - esperado
        tp += len(acertos)
        fn += len(perdidos)
        fp += len(extras)
        det.append({'REGISTRATION_ID': rid, 'PRODUCT': L['PRODUCT'],
                    'ESTRUTURA': L.get('ESTRUTURA'),
                    'EXPECTED': len(esperado), 'RECOVERED': len(acertos),
                    'MISSED': sorted('%s x %s' % x for x in perdidos),
                    'EXTRA': sorted('%s x %s' % x for x in extras)})
        for mn in L.get('MUST_NOT_PRODUCE', []):
            for c, t in pub:
                if c == mn['CROP'] and (mn['TARGET'] == '*' or t == mn['TARGET']):
                    trap_viol.append({'REGISTRATION_ID': rid, 'PAIR': '%s x %s' % (c, t),
                                      'WHY': mn['WHY']})
    prec = tp / (tp + fp) if tp + fp else 0.0
    rec = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
    return {'TP': tp, 'FP': fp, 'FN': fn,
            'PRECISION': round(prec, 4), 'RECALL': round(rec, 4), 'F1': round(f1, 4),
            'TRAP_VIOLATIONS': trap_viol, 'BY_LABEL': det}


if __name__ == '__main__':
    d = sys.argv[1]
    r = avaliar(d)
    print('TP=%d FP=%d FN=%d' % (r['TP'], r['FP'], r['FN']))
    print('PRECISION=%.3f  RECALL=%.3f  F1=%.3f' % (r['PRECISION'], r['RECALL'], r['F1']))
    print('violacoes de armadilha: %d' % len(r['TRAP_VIOLATIONS']))
    for t in r['TRAP_VIOLATIONS']:
        print('   !! %s %s' % (t['REGISTRATION_ID'], t['PAIR']))
    print()
    for b in r['BY_LABEL']:
        if b['MISSED'] or b['EXTRA']:
            print('%s %-20s esperados=%d recuperados=%d' % (b['REGISTRATION_ID'],
                                                           b['PRODUCT'][:20],
                                                           b['EXPECTED'], b['RECOVERED']))
            if b['MISSED']:
                print('   FN: %s' % ', '.join(b['MISSED'][:8]))
            if b['EXTRA']:
                print('   FP: %s' % ', '.join(b['EXTRA'][:8]))
