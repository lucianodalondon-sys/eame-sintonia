#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O MEDIDOR DE DRIFT DO MOTOR DE OPORTUNIDADES.

    python3 scripts/v21_opp_drift.py ANTES/OPPORTUNITIES.json DEPOIS/OPPORTUNITIES.json

POR QUE ESTE FICHEIRO EXISTE
----------------------------
Uma correção de motor só é defensável se alguém puder dizer, campo a campo, o
que mudou e o que não mudou. «Rodei e pareceu igual» não é medição: é impressão.

    UMA CORREÇÃO QUE NÃO SE MEDE NÃO SE DISTINGUE DE UMA REGRESSÃO.

O medidor separa três coisas que a pressa costuma juntar:

  CHAVES NOVAS        campos que não existiam antes. Acrescentar não é mudar.
  DRIFT COMPORTAMENTAL mudança nos campos que decidem o que se vê e o que se
                      promete — a lista servida, o veredito, o estado, o score.
  DRIFT INFORMATIVO   mudança em campos de contabilidade/declaração.

O conjunto COMPORTAMENTAL é fechado e está escrito aqui embaixo, não é
adivinhado por heurística: é exatamente a lista que o handoff mediu.
"""
import json
import sys
from collections import OrderedDict

# ── OS CAMPOS QUE DECIDEM. Mudança aqui é drift comportamental, sempre. ──────
COMPORTAMENTAIS = (
    'PORTFOLIO_MATCHES', 'PRODUCT_RELATIONSHIPS', 'PRIMARY_MATCH',
    'PRIMARY_MATCH_REASON', 'STATUS', 'OPPORTUNITY_STATE', 'OPPORTUNITY_SCORE',
    'COMMERCIAL_PRIORITY', 'BLOCKING_GATES', 'RED_TEAM_FINDINGS',
    'EVIDENCE_IDS', 'EVIDENCE_COUNT', 'WINDOW_STATE', 'CROP', 'TARGET',
    'GEOGRAPHY', 'MATCHED_COMMERCIAL_PRODUCT_IDS',
    'MATCHED_COMMERCIAL_PRODUCT_NAMES', 'COMMERCIAL_PRODUCT_COUNT',
    'PRODUCT_LINK_STATE', 'ARCHETYPE',
)

# ── A ORDEM NÃO É SEMÂNTICA AQUI ────────────────────────────────────────────
# EVIDENCE_IDS é um CONJUNTO de apoios: dois cartões com os mesmos apoios em
# ordem diferente afirmam a mesma coisa. Compará-los como LISTA foi um defeito
# do próprio teste — reportava mudança onde não havia afirmação nova.
#
#     COMPARAR COMO LISTA O QUE SE AFIRMA COMO CONJUNTO INVENTA DIFERENÇA.
#
# Onde a ordem É semântica (uma lista servida ao ecrã, por exemplo), ela fica
# de fora desta tabela e continua comparada como lista.
SEM_ORDEM_SEMANTICA = frozenset((
    'EVIDENCE_IDS', 'EVIDENCE_FAMILIES', 'BLOCKING_GATES',
    'RED_TEAM_FINDINGS', 'CROP_IDS', 'ISSUE_IDS', 'REGION_IDS',
    'SOURCE_IDS', 'MATCHED_COMMERCIAL_PRODUCT_IDS',
    'MATCHED_COMMERCIAL_PRODUCT_NAMES', 'ACTIVE_INGREDIENT_IDS',
    'ACTIVE_INGREDIENT_NAMES', 'MODE_OF_ACTION_CODES',
))


def _norm(campo, valor):
    """O valor como ele se AFIRMA — conjunto onde a ordem não diz nada."""
    if campo in SEM_ORDEM_SEMANTICA and isinstance(valor, list):
        return sorted(json.dumps(x, sort_keys=True, ensure_ascii=False)
                      for x in valor)
    return valor


def _regs(caminho):
    d = json.load(open(caminho, encoding='utf-8'))
    return OrderedDict((r['ID'], r) for r in (d.get('RECORDS') or []))


def comparar(antes, depois):
    A, D = _regs(antes), _regs(depois)
    r = {
        'IDS_ANTES': len(A), 'IDS_DEPOIS': len(D),
        'IDS_SUMIRAM': sorted(set(A) - set(D)),
        'IDS_NOVOS': sorted(set(D) - set(A)),
        'CHAVES_NOVAS': [], 'CHAVES_REMOVIDAS': [],
        'DRIFT_COMPORTAMENTAL': [], 'DRIFT_INFORMATIVO': [],
    }
    comuns = [i for i in A if i in D]
    ka = {k for i in comuns for k in A[i]}
    kd = {k for i in comuns for k in D[i]}
    r['CHAVES_NOVAS'] = sorted(kd - ka)
    r['CHAVES_REMOVIDAS'] = sorted(ka - kd)
    for i in comuns:
        a, d = A[i], D[i]
        for k in sorted(set(a) & set(d)):
            va, vd = _norm(k, a[k]), _norm(k, d[k])
            if va == vd:
                continue
            linha = {'OPPORTUNITY_ID': i, 'FIELD_CHANGED': k,
                     'BEFORE': a[k], 'AFTER': d[k]}
            (r['DRIFT_COMPORTAMENTAL'] if k in COMPORTAMENTAIS
             else r['DRIFT_INFORMATIVO']).append(linha)
    return r


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    r = comparar(sys.argv[1], sys.argv[2])
    print('== DRIFT DO MOTOR ==')
    print('  registos      %d → %d' % (r['IDS_ANTES'], r['IDS_DEPOIS']))
    print('  IDs sumiram   %d %s' % (len(r['IDS_SUMIRAM']), r['IDS_SUMIRAM'][:5] or ''))
    print('  IDs novos     %d %s' % (len(r['IDS_NOVOS']), r['IDS_NOVOS'][:5] or ''))
    print('  chaves novas  %d' % len(r['CHAVES_NOVAS']))
    for k in r['CHAVES_NOVAS']:
        print('      + %s' % k)
    for k in r['CHAVES_REMOVIDAS']:
        print('      - %s' % k)
    print('  DRIFT COMPORTAMENTAL  %d' % len(r['DRIFT_COMPORTAMENTAL']))
    for x in r['DRIFT_COMPORTAMENTAL'][:40]:
        print('      %s · %s' % (x['OPPORTUNITY_ID'], x['FIELD_CHANGED']))
        print('        antes  %s' % json.dumps(x['BEFORE'], ensure_ascii=False)[:220])
        print('        depois %s' % json.dumps(x['AFTER'], ensure_ascii=False)[:220])
    print('  drift informativo     %d' % len(r['DRIFT_INFORMATIVO']))
    for x in r['DRIFT_INFORMATIVO'][:20]:
        print('      %s · %s' % (x['OPPORTUNITY_ID'], x['FIELD_CHANGED']))
    if len(sys.argv) > 3:
        json.dump(r, open(sys.argv[3], 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=1)
        print('  ledger em %s' % sys.argv[3])
    return 0


if __name__ == '__main__':
    sys.exit(main())
