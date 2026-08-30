#!/usr/bin/env python3
"""
ITÁLIA — cruzamento ADAMA × CULTURA × ALVO, a partir do rótulo oficial.

Este é o único lugar do repositório onde `ADAMA REGISTERED RESPONSE` para a Itália
pode ser afirmado, e a razão é simples: o rótulo é o documento que diz o que a
autorização permite. Site de fabricante diria outra coisa — diria o que o fabricante
comunica — e as duas coisas não se misturam.

    REGULATORY_FACT              o rótulo autorizado (aqui)
    MANUFACTURER_TECHNICAL_CLAIM o que o fabricante afirma tecnicamente
    MANUFACTURER_COMMERCIAL_CLAIM o que o fabricante comunica comercialmente
    DERIVED_INTERPRETATION       o que nós derivamos

O que sai daqui é a PRIMEIRA classe. As outras três não foram coletadas para a Itália
nesta rodada — e a razão está declarada no relatório: `adama.com` responde 403 a este
ambiente, inclusive em `/robots.txt`. Bloqueio de origem não é ausência de portfólio,
e não autoriza preencher a lacuna com o que se imagina que o site diria.

`CROP_TERM_PRESENT` NÃO é `AUTHORIZED_ON_CROP`: o rótulo cita a cultura, mas a
associação cultura↔alvo mora numa coluna de tabela que a extração de PDF perde.
O nome do campo carrega essa ressalva de propósito.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import italia_rotulo_parse as rp  # noqa: E402

PDF_DIR = os.path.join(ROOT, 'data', 'raw', 'IT', 'etichette')
MANIFESTO = os.path.join(ROOT, 'data', 'samples', 'IT-T4-001',
                         'IT-T4-001-etichette-manifest.json')


def indice_manifesto():
    if not os.path.exists(MANIFESTO):
        return {}
    d = json.load(open(MANIFESTO, encoding='utf-8'))
    return {r['REGISTRATION_ID']: r for r in d.get('LABELS', []) if r.get('STATE') == 'OK'}


def analisar_todos():
    idx = indice_manifesto()
    produtos, falhas = [], []
    for f in sorted(os.listdir(PDF_DIR)):
        if not f.endswith('.pdf'):
            continue
        reg = f.split('_')[0]
        try:
            r = rp.analisar(os.path.join(PDF_DIR, f))
        except Exception as e:                                  # noqa: BLE001
            falhas.append({'REGISTRATION_ID': reg, 'ERROR': str(e)[:120]})
            continue
        m = idx.get(reg, {})
        produtos.append({
            'REGISTRATION_ID': reg,
            'PRODUCT': m.get('PRODUCT'), 'HOLDER': m.get('HOLDER'),
            'ACTIVE_SUBSTANCE': m.get('ACTIVE_SUBSTANCE'),
            'EXPIRY': m.get('EXPIRY'), 'STATUS': m.get('STATUS'),
            'LABEL_DATE': m.get('LABEL_DATE'), 'LABEL_URL': m.get('LABEL_URL'),
            'EXTRACTION_STATE': r['EXTRACTION_STATE'],
            'CROP_TERMS_PRESENT': sorted(r['CROP_TERMS_PRESENT']),
            'ISSUES_FROM_SOURCE': r['ISSUES_FROM_SOURCE'],
        })
    return produtos, falhas


def por_cultura(produtos):
    out = {}
    for p in produtos:
        for c in p['CROP_TERMS_PRESENT']:
            d = out.setdefault(c, {'PRODUCTS': [], 'SUBSTANCES': set(), 'ISSUES': {}})
            d['PRODUCTS'].append(p['PRODUCT'])
            for s in (p['ACTIVE_SUBSTANCE'] or '').split('|'):
                if s.strip() and s.strip() != '-':
                    d['SUBSTANCES'].add(s.strip())
            for i in p['ISSUES_FROM_SOURCE']:
                k = i['SCIENTIFIC_NAME']
                e = d['ISSUES'].setdefault(k, {'SCIENTIFIC_NAME': k,
                                               'VERNACULAR_IT': i['ISSUE_VERNACULAR_IT'],
                                               'PRODUCTS': 0})
                e['PRODUCTS'] += 1
    for c, d in out.items():
        d['PRODUCT_COUNT'] = len(d['PRODUCTS'])
        d['SUBSTANCES'] = sorted(d['SUBSTANCES'])
        d['ISSUES'] = sorted(d['ISSUES'].values(), key=lambda x: -x['PRODUCTS'])
        d['CONTRACT'] = ('CROP_TERM_PRESENT no rótulo. NÃO significa autorização para '
                         'todos os alvos listados: a coluna cultura↔alvo não foi reconstruída.')
    return dict(sorted(out.items(), key=lambda kv: -kv[1]['PRODUCT_COUNT']))


def main():
    produtos, falhas = analisar_todos()
    pc = por_cultura(produtos)
    print('ETICHETTAS ANALISADAS: %d (falhas %d)' % (len(produtos), len(falhas)))
    print('\nCULTURA (presença de termo)      PRODUTOS  SUBSTÂNCIAS  ALVOS')
    for c, d in pc.items():
        print('  %-28s %6d %10d %8d' % (c, d['PRODUCT_COUNT'], len(d['SUBSTANCES']),
                                        len(d['ISSUES'])))
    if 'MAIZE' in pc:
        d = pc['MAIZE']
        print('\nMILHO — %d produtos, %d substâncias' % (d['PRODUCT_COUNT'], len(d['SUBSTANCES'])))
        print('  substâncias:', ', '.join(d['SUBSTANCES'][:14]))
        print('  alvos mais recorrentes:')
        for i in d['ISSUES'][:12]:
            print('    %-30s %s (%d produtos)' % (i['VERNACULAR_IT'][:30],
                                                  i['SCIENTIFIC_NAME'], i['PRODUCTS']))


if __name__ == '__main__':
    main()
