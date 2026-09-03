#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""REGRESSÃO DO CONSERTO DOS DOIS VÍNCULOS · caso a caso, com a razão factual.

    python3 scripts/v21_regressao_do_vinculo.py --gravar-antes <OPPORTUNITIES.json>
    python3 scripts/v21_regressao_do_vinculo.py

O ANTES é o pacote construído em `e0a813d` — o commit que a revisão auditou —
guardado em `data/samples/AUDITORIA-SOMBRA/V112-ANTES-DO-CONSERTO.json`. O
DEPOIS é o que a cadeia acabou de reconstruir.

    UM «ANTES» QUE NÃO SAI DE UM ARQUIVO É UMA LEMBRANÇA, NÃO UMA MEDIÇÃO.

O par é feito por IDENTITY_KEY sem a data de janela — porque a data de janela
entra no identificador, e consertar o vínculo muda a data. Casar por ID daria
«43 saíram, 43 entraram», que é verdade sobre o hash e mentira sobre o caso.

    O CASO É O ARQUÉTIPO, A CULTURA, O ALVO E A REGIÃO.
    O HASH É COMO ELE SE CHAMA HOJE.
"""
import json
import os
import sys
from collections import Counter
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ING = os.path.join(ROOT, 'build', 'ITALY-REALITY-HANDOFF-V2.1', 'DESIGN-INGEST')
ANTES = os.path.join(ROOT, 'data', 'samples', 'AUDITORIA-SOMBRA',
                     'V112-ANTES-DO-CONSERTO.json')

CAMPOS = ('ID', 'ARCHETYPE', 'CROP', 'TARGET', 'GEOGRAPHY', 'OPPORTUNITY_STATE',
          'BLOCKING_GATES', 'STATUS', 'WINDOW_FIELD', 'WINDOW_KIND',
          'DAYS_REMAINING', 'OPPORTUNITY_SCORE', 'COMMERCIAL_PRIORITY',
          'WHY_COMMERCIAL_CODES', 'EXTERNAL_MATERIAL_READY',
          'EXTERNAL_BLOCKER_CODES', 'NEED_DIRECTION', 'NEED_EVIDENCE_ID',
          'NEED_EXCERPT', 'COMMERCIAL_WINDOW', 'EVIDENCE_IDS',
          'MATCHED_COMMERCIAL_PRODUCT_NAMES')

# O que se compara caso a caso. Fora daqui ficam os textos de lei e as
# traduções: eles não medem o conserto, e enchem o relatório de ruído.
COMPARADOS = ('OPPORTUNITY_STATE', 'BLOCKING_GATES', 'STATUS', 'WINDOW_FIELD',
              'WINDOW_KIND', 'DAYS_REMAINING', 'OPPORTUNITY_SCORE',
              'COMMERCIAL_PRIORITY', 'EXTERNAL_MATERIAL_READY',
              'EXTERNAL_BLOCKER_CODES', 'NEED_DIRECTION', 'COMMERCIAL_WINDOW',
              'EVIDENCE_IDS')


def chave(r):
    return '%s|%s|%s|%s' % (r['ARCHETYPE'], r.get('CROP'), r.get('TARGET'),
                            r.get('GEOGRAPHY'))


def _resumo(r):
    return {c: r.get(c) for c in CAMPOS}


def gravar_antes(caminho):
    recs = json.load(open(caminho, encoding='utf-8'))['RECORDS']
    fora = {
        'COLLECTION': 'V112-ANTES-DO-CONSERTO',
        'SOURCE': 'build/ITALY-REALITY-HANDOFF-V2.1/DESIGN-INGEST/'
                  'OPPORTUNITIES.json construido no commit e0a813d',
        'CAPTURED_AT': date.today().isoformat(),
        'LAW': 'recorte dos campos auditados, nao o pacote inteiro. O pacote '
               'nao e versionado; este recorte e, para que a regressao possa '
               'ser refeita por quem herdar o repositorio.',
        'FIELDS': list(CAMPOS),
        'RECORDS': [_resumo(r) for r in recs],
    }
    os.makedirs(os.path.dirname(ANTES), exist_ok=True)
    json.dump(fora, open(ANTES, 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print('gravado %s · %d casos' % (os.path.relpath(ANTES, ROOT), len(recs)))
    return 0


def main():
    if len(sys.argv) > 2 and sys.argv[1] == '--gravar-antes':
        return gravar_antes(sys.argv[2])
    if not os.path.exists(ANTES):
        print('sem o ANTES: rode --gravar-antes primeiro', file=sys.stderr)
        return 2
    A = {chave(r): r for r in json.load(open(ANTES, encoding='utf-8'))['RECORDS']}
    D = {chave(r): _resumo(r) for r in json.load(
        open(os.path.join(ING, 'OPPORTUNITIES.json'), encoding='utf-8'))['RECORDS']}

    print('=' * 74)
    print('CASOS   antes %d · depois %d · mesmos %d · so antes %d · so depois %d'
          % (len(A), len(D), len(set(A) & set(D)), len(set(A) - set(D)),
             len(set(D) - set(A))))
    print('=' * 74)
    for k in sorted(set(A) - set(D)):
        print('  CASO QUE DEIXOU DE EXISTIR: %s' % k)
    for k in sorted(set(D) - set(A)):
        print('  CASO NOVO: %s' % k)

    mudou = []
    for k in sorted(set(A) & set(D)):
        dif = {c: (A[k].get(c), D[k].get(c)) for c in COMPARADOS
               if A[k].get(c) != D[k].get(c)}
        if dif:
            mudou.append((k, dif))

    print('\nCASOS QUE MUDARAM: %d de %d' % (len(mudou), len(A)))
    for k, dif in mudou:
        print('\n  %s' % k)
        print('    %s -> %s' % (A[k]['ID'], D[k]['ID']))
        for c, (a, d) in sorted(dif.items()):
            if c == 'EVIDENCE_IDS':
                saiu = [x for x in (a or []) if x not in (d or [])]
                entrou = [x for x in (d or []) if x not in (a or [])]
                if saiu:
                    print('    apoios que sairam : %s' % ', '.join(saiu))
                if entrou:
                    print('    apoios que entraram: %s' % ', '.join(entrou))
                continue
            print('    %-24s %s  ->  %s' % (c, a, d))

    for campo in ('OPPORTUNITY_STATE', 'COMMERCIAL_PRIORITY',
                  'EXTERNAL_MATERIAL_READY', 'NEED_DIRECTION'):
        ca = Counter(r.get(campo) for r in A.values())
        cd = Counter(r.get(campo) for r in D.values())
        print('\n%s' % campo)
        for v in sorted(set(ca) | set(cd), key=lambda x: str(x)):
            marca = '' if ca.get(v, 0) == cd.get(v, 0) else '   <<'
            print('  %-26s %3d -> %3d%s' % (v, ca.get(v, 0), cd.get(v, 0), marca))
    return 0


if __name__ == '__main__':
    sys.exit(main())
