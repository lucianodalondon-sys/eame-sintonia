#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ANTES E DEPOIS · o que a camada comercial V1.1 mudou, medido.

    python3 scripts/v21_antes_e_depois.py

O ANTES é o pacote versionado em `build/SINTONIA-ITALY-REALITY-HANDOFF-V2.1.zip`
— o estado do motor V1 no commit da auditoria. O DEPOIS é o que a cadeia acabou
de reconstruir. Nenhum dos dois é digitado à mão.

    UM «ANTES» QUE NÃO SAI DE UM ARQUIVO É UMA LEMBRANÇA, NÃO UMA MEDIÇÃO.

O total NÃO precisa continuar 37. Se mudou, cada diferença tem de ter razão
factual — e é isso que este arquivo imprime, ID por ID.
"""
import io
import json
import os
import sys
import zipfile
from collections import Counter
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ING = os.path.join(ROOT, 'build', 'ITALY-REALITY-HANDOFF-V2.1', 'DESIGN-INGEST')
ZIP = os.path.join(ROOT, 'build', 'SINTONIA-ITALY-REALITY-HANDOFF-V2.1.zip')
NO_ZIP = 'ITALY-REALITY-HANDOFF-V2.1/DESIGN-INGEST/OPPORTUNITIES.json'
SAIDA = os.path.join(ROOT, 'data', 'samples', 'AUDITORIA-SOMBRA',
                     'V11-ANTES-E-DEPOIS.json')

# Famílias que são a ADAMA falando de si mesma. Não corroboram: respondem
# «com o quê». É a mesma definição da auditoria da régua comercial, para que os
# dois números sejam comparáveis.
#
# ⚠️ `REGULATORY_FUTURE_FACT` NÃO entra aqui: um ato do Jornal Oficial da UE é
# fato de terceiro, não a empresa testemunhando a favor de si.
LADO_ADAMA = {'LABEL_USE_RELATIONSHIP', 'REGULATORY_PRODUCT', 'ACTIVE_INGREDIENT',
              'COMMERCIAL_PRODUCT'}


def antes():
    with zipfile.ZipFile(ZIP) as z, z.open(NO_ZIP) as fh:
        return json.load(io.TextIOWrapper(fh, encoding='utf-8'))


def depois():
    return json.load(open(os.path.join(ING, 'OPPORTUNITIES.json'), encoding='utf-8'))


def familias_externas(r):
    return sorted(set(r.get('EVIDENCE_FAMILIES') or []) - LADO_ADAMA)


def _rotulo(r):
    c = (r.get('CROP') or '—').replace('CROP_', '')
    t = (r.get('TARGET') or '—').replace('ISSUE_', '')
    return '%s × %s' % (c, t)


def main():
    A, D = antes(), depois()
    ra = {r['ID']: r for r in A['RECORDS']}
    rd = {r['ID']: r for r in D['RECORDS']}
    saiu, entrou, ficou = set(ra) - set(rd), set(rd) - set(ra), set(ra) & set(rd)

    print('=' * 74)
    print('TOTAL   antes %d · depois %d' % (len(ra), len(rd)))
    print('        saíram %d · entraram %d · permanecem %d'
          % (len(saiu), len(entrou), len(ficou)))
    print('=' * 74)

    print('\nIDs QUE SAÍRAM — e por quê')
    for i in sorted(saiu):
        r = ra[i]
        print('  - %s  %-28s %s' % (i, _rotulo(r), r['ARCHETYPE']))
    print('\nIDs QUE ENTRARAM — e por quê')
    for i in sorted(entrou):
        r = rd[i]
        print('  + %s  %-28s %s' % (i, _rotulo(r), r['ARCHETYPE']))
        print('      necessidade %s · método %s · apoio %s'
              % (r.get('NEED_DIRECTION'), r.get('NEED_METHOD'),
                 r.get('NEED_EVIDENCE_ID')))

    print('\n' + '=' * 74)
    print('OPPORTUNITY_STATE   antes %s' % dict(Counter(
        r['OPPORTUNITY_STATE'] for r in ra.values())))
    print('                    depois %s' % dict(Counter(
        r['OPPORTUNITY_STATE'] for r in rd.values())))
    print('\nCOMMERCIAL_PRIORITY (só existe depois)')
    for k, v in sorted(Counter(r['COMMERCIAL_PRIORITY']
                               for r in rd.values()).items()):
        print('  %-24s %d' % (k, v))

    # ── os antigos VERIFIED ─────────────────────────────────────────────────
    verificados = [i for i, r in ra.items()
                   if r['OPPORTUNITY_STATE'] == 'OPPORTUNITY_CONFIRMED']
    print('\n' + '=' * 74)
    print('OS %d VERIFIED DO V1, na régua comercial' % len(verificados))
    for i in sorted(verificados):
        r = rd.get(i)
        if not r:
            print('  %s  %-26s SAIU DO MOTOR' % (i, _rotulo(ra[i])))
            continue
        print('  %s  %-26s %-22s %s' % (i, _rotulo(r), r['COMMERCIAL_PRIORITY'],
                                        r['ARCHETYPE']))

    subiram = [i for i in sorted(ficou)
               if ra[i]['OPPORTUNITY_STATE'] == 'OPPORTUNITY_CANDIDATE'
               and rd[i]['COMMERCIAL_PRIORITY'] in ('SALES_READY', 'SALES_PREPARE',
                                                    'COMMERCIAL_WATCH')]
    print('\nOS QUE ERAM TO_VALIDATE NO V1 E SUBIRAM COMERCIALMENTE')
    for i in subiram:
        print('  %s  %-26s %-22s %s' % (i, _rotulo(rd[i]),
                                        rd[i]['COMMERCIAL_PRIORITY'],
                                        rd[i]['ARCHETYPE']))

    # ── famílias externas ───────────────────────────────────────────────────
    print('\n' + '=' * 74)
    print('CASOS POR NÚMERO DE FAMÍLIAS EXTERNAS')
    fa = Counter(len(familias_externas(r)) for r in ra.values())
    fd = Counter(len(familias_externas(r)) for r in rd.values())
    print('  famílias   antes   depois')
    for n in sorted(set(fa) | set(fd)):
        print('  %-10s %-7d %d' % ('4+' if n >= 4 else n, fa.get(n, 0), fd.get(n, 0)))

    sr = [r for r in rd.values() if r['COMMERCIAL_PRIORITY'] == 'SALES_READY']
    print('\nSALES_READY sustentado por')
    c = Counter(len(familias_externas(r)) for r in sr)
    for n in sorted(c):
        print('  %s família(s) forte(s): %d' % ('3+' if n >= 3 else n, c[n]))

    # ── os dez melhores casos comerciais ────────────────────────────────────
    ordem = {'SALES_READY': 0, 'SALES_PREPARE': 1, 'COMMERCIAL_WATCH': 2,
             'STRATEGIC_OPPORTUNITY': 3, 'TO_VALIDATE': 4}
    top = sorted(rd.values(),
                 key=lambda r: (ordem[r['COMMERCIAL_PRIORITY']],
                                -r['OPPORTUNITY_SCORE'],
                                -(r.get('COMMERCIAL_PRODUCT_COUNT') or 0)))[:10]
    print('\n' + '=' * 74)
    print('OS DEZ MELHORES CASOS COMERCIAIS')
    print('  %-18s %-26s %-20s %-5s %s' % ('ID', 'CULTURA × ALVO', 'PRIORIDADE',
                                           'SCORE', 'PRODUTOS COMERCIAIS'))
    for r in top:
        print('  %-18s %-26s %-20s %-5d %s'
              % (r['ID'], _rotulo(r), r['COMMERCIAL_PRIORITY'],
                 r['OPPORTUNITY_SCORE'],
                 ', '.join(r['MATCHED_COMMERCIAL_PRODUCT_NAMES'][:3]) or '—'))

    fora = {
        'COLLECTION': 'V11-ANTES-E-DEPOIS',
        # o contrato de `data/samples/` vale para o que eu mesmo produzo
        'SOURCE': 'build/SINTONIA-ITALY-REALITY-HANDOFF-V2.1.zip (ANTES) · '
                  'build/ITALY-REALITY-HANDOFF-V2.1/DESIGN-INGEST (DEPOIS)',
        'CAPTURED_AT': date.today().isoformat(),
        'LAW': 'o ANTES sai do zip versionado do V1; o DEPOIS, da cadeia '
               'reconstruida. Nenhum numero foi digitado a mao.',
        'BUILD_ID_ANTES': A.get('BUILD_ID'), 'BUILD_ID_DEPOIS': D.get('BUILD_ID'),
        'TOTAL_ANTES': len(ra), 'TOTAL_DEPOIS': len(rd),
        'IDS_QUE_SAIRAM': sorted(saiu), 'IDS_QUE_ENTRARAM': sorted(entrou),
        'BY_OPPORTUNITY_STATE_ANTES': dict(Counter(
            r['OPPORTUNITY_STATE'] for r in ra.values())),
        'BY_OPPORTUNITY_STATE_DEPOIS': dict(Counter(
            r['OPPORTUNITY_STATE'] for r in rd.values())),
        'BY_COMMERCIAL_PRIORITY': dict(Counter(
            r['COMMERCIAL_PRIORITY'] for r in rd.values())),
        'FAMILIAS_EXTERNAS_ANTES': {str(k): v for k, v in sorted(fa.items())},
        'FAMILIAS_EXTERNAS_DEPOIS': {str(k): v for k, v in sorted(fd.items())},
        'VERIFIED_DO_V1': {i: (rd[i]['COMMERCIAL_PRIORITY'] if i in rd
                               else 'SAIU_DO_MOTOR') for i in sorted(verificados)},
        'SUBIRAM_COMERCIALMENTE': {i: rd[i]['COMMERCIAL_PRIORITY'] for i in subiram},
        'TOP_10_COMERCIAIS': [
            {'ID': r['ID'], 'PAR': _rotulo(r),
             'COMMERCIAL_PRIORITY': r['COMMERCIAL_PRIORITY'],
             'NEED_DIRECTION': r.get('NEED_DIRECTION'),
             'PRODUTOS': r['MATCHED_COMMERCIAL_PRODUCT_NAMES'],
             'SCORE': r['OPPORTUNITY_SCORE']} for r in top],
    }
    os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
    json.dump(fora, open(SAIDA, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('\ngravado em %s' % os.path.relpath(SAIDA, ROOT))
    return 0


if __name__ == '__main__':
    sys.exit(main())
