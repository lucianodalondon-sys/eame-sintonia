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
            # Só entra como presença quem tem contexto de USO. Quem só aparece em
            # cláusula de sucessão vai para outro campo e NUNCA se soma ao primeiro.
            'CROP_TERMS_PRESENT': sorted(c for c, d in r['CROP_TERMS_PRESENT'].items()
                                         if d['STATE'] == 'CROP_TERM_PRESENT'),
            'CROP_TERMS_ROTATION_ONLY': sorted(c for c, d in r['CROP_TERMS_PRESENT'].items()
                                               if d['STATE'] == 'ROTATION_CONTEXT_ONLY'),
            'MODE_OF_ACTION_DECLARED': r['MODE_OF_ACTION_DECLARED'],
            'MODE_OF_ACTION_EXTRACTION': r['MODE_OF_ACTION_EXTRACTION'],
            'CATEGORY_REGULATORY': (m.get('CATEGORY') or ''),
            'ISSUES_FROM_SOURCE': r['ISSUES_FROM_SOURCE'],
        })
    return produtos, falhas


def artefato():
    """Escreve o gêmeo REGULATÓRIO do portfólio italiano. Não é o gêmeo do site."""
    import datetime
    produtos, falhas = analisar_todos()
    pc = por_cultura(produtos)
    moa = {}
    for p in produtos:
        for esq, gs in (p.get('MODE_OF_ACTION_DECLARED') or {}).items():
            for g in gs:
                moa['%s %s' % (esq, g)] = moa.get('%s %s' % (esq, g), 0) + 1
    d = json.load(open(MANIFESTO, encoding='utf-8')) if os.path.exists(MANIFESTO) else {}
    out = {
        'COUNTRY': 'IT', 'SOURCE_ID': 'IT-T4-001-ETICHETTA',
        'CAPTURED_AT': datetime.date.today().isoformat(),
        'EVIDENCE_CLASS': 'REGULATORY_FACT',
        'WHAT_THIS_IS': ('Gêmeo REGULATÓRIO do portfólio ADAMA italiano, lido no rótulo '
                         'autorizado. NÃO é o gêmeo do site do fabricante: adama.com '
                         'devolve 403 a este ambiente e a camada de afirmação comercial '
                         'continua NOT_COLLECTED.'),
        'LABEL_COVERAGE': {'TARGET': d.get('TARGET_TOTAL'), 'OBTAINED': d.get('LABELS_OBTAINED'),
                           'PCT': d.get('COVERAGE_PCT'), 'STATE': d.get('STATE')},
        'LABELS_PARSED': len(produtos), 'PARSE_FAILURES': len(falhas),
        'CROP_TERM_CONTRACT': ('CROP_TERM_PRESENT = o termo aparece em contexto de uso. '
                               'NÃO É AUTHORIZED_ON_CROP: a coluna cultura↔alvo da tabela '
                               'de doses não foi reconstruída a partir do PDF.'),
        'BY_CROP_TERM': pc,
        'MODE_OF_ACTION_GROUPS_DECLARED': dict(sorted(moa.items(), key=lambda kv: -kv[1])),
        'PRODUCTS': produtos,
    }
    dest = os.path.join(ROOT, 'data', 'samples', 'IT-T4-001',
                        'IT-T4-001-portfolio-rotulo.json')
    with open(dest, 'w', encoding='utf-8') as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    return dest, out


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
    if '--artefato' in sys.argv:
        dest, out = artefato()
        print('escrito %s' % os.path.relpath(dest, ROOT))
        print('rotulos %d | cobertura %s%%' % (out['LABELS_PARSED'],
                                               out['LABEL_COVERAGE']['PCT']))
        return
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
