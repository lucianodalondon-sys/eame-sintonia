#!/usr/bin/env python3
"""FASE 2 e 5 — censo do acervo, e o que dele NAO chega a nenhuma inteligencia.

A pergunta e uma so: quanto do que foi coletado vira superficie, e quanto fica
guardado? E, para o que fica, a causa e "a fonte nao diz" ou "o pipeline perdeu"?

    AUSENCIA DE DESCOBERTA NAO E AUSENCIA DE DADO.
    Nao encontrei -> NOT_FOUND. Nao posso saber -> UNKNOWN.
"""
import collections
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from it_futuro_corpus import candidatos, corpus                  # noqa: E402
from it_futuro_inteligencia import SINAIS                        # noqa: E402

S = os.path.join(ROOT, 'data', 'samples')
DEST = os.path.join(ROOT, 'data/samples/IT-FUTURO-V1')


def _consumidos_pela_inteligencia(wt):
    """IDs de fonte que JA aparecem em alguma superficie de inteligencia."""
    ids = set()
    # 1 · sinais de campo verificados (IT-CAMPO)
    for nome in ('IT-CAMPO-SINAIS-VERIFICADOS-V2.json',
                 'IT-CAMPO-SINAIS-VERIFICADOS-V1.json'):
        p = os.path.join(S, 'IT-CAMPO-V1', nome)
        if os.path.exists(p):
            for x in json.load(open(p, encoding='utf-8')).get('SIGNALS', []):
                u = x.get('source_url') or ''
                if u:
                    ids.add(u.rsplit('=', 1)[-1])
    # 2 · as 43 do motor, se a worktree estiver montada
    op = os.path.join(wt, 'build', 'ITALY-REALITY-HANDOFF-V2.1',
                      'DESIGN-INGEST', 'OPPORTUNITIES.json')
    if os.path.exists(op):
        d = json.load(open(op, encoding='utf-8'))
        for r in d['RECORDS']:
            for u in (r.get('SOURCE_URLS') or []):
                ids.add(str(u).rsplit('=', 1)[-1])
            for i in (r.get('SOURCE_IDS') or []):
                ids.add(str(i))
    # 3 · o radar futuro desta rodada
    for s in SINAIS:
        ids.add(s['SOURCE_ID'])
        for c in (s.get('CORROBORATING_SOURCES') or []):
            ids.add(c['SOURCE_ID'])
    return ids


def familias():
    """Cada familia do acervo, com o que dela se pode medir."""
    fam = collections.defaultdict(lambda: collections.Counter())
    for d in corpus():
        f = d['SOURCE_TYPE']
        fam[f]['TOTAL'] += 1
        fam[f]['COM_TEXTO'] += 1 if len(d['TEXT']) > 400 else 0
        fam[f]['COM_DATA'] += 1 if d['SOURCE_DATE'] not in ('UNKNOWN', '', None) else 0
    return fam


def main(wt='/home/user/wt-canonica'):
    os.makedirs(DEST, exist_ok=True)
    docs = list(corpus())
    cands = list(candidatos())
    usados = _consumidos_pela_inteligencia(wt)
    por_doc = collections.defaultdict(list)
    for c in cands:
        por_doc[c['SOURCE_ID']].append(c)

    linhas = []
    for d in docs:
        sid = d['SOURCE_ID']
        cs = por_doc.get(sid, [])
        tocado = sid in usados or any(sid in u for u in usados)
        crops = sorted({x for c in cs for x in c['CROPS']})
        issues = sorted({x for c in cs for x in c['ISSUES']})
        regs = sorted({x for c in cs for x in c['REGIONS']})
        if tocado:
            estado, porque = 'USADO', None
        elif not cs:
            estado, porque = 'NAO_USADO', ('NOT_IN_SOURCE — nenhuma expressao de '
                                           'futuro no documento')
        elif not (crops and issues):
            estado, porque = 'NAO_USADO', ('NEEDS_CROSSING — ha expressao de futuro '
                                           'mas falta cultura ou alvo no mesmo '
                                           'contexto')
        else:
            estado, porque = 'CANDIDATO_NAO_PROMOVIDO', (
                'NOT_EXTRACTED — tem cultura, alvo e marca de futuro, e ainda nao '
                'foi lido a mao nesta rodada')
        linhas.append({
            'SOURCE_ID': sid, 'SOURCE_TYPE': d['SOURCE_TYPE'],
            'SOURCE_DATE': d['SOURCE_DATE'], 'TITLE': (d.get('TITLE') or '')[:120],
            'CHARS': len(d['TEXT']),
            'HAS_DATE': d['SOURCE_DATE'] not in ('UNKNOWN', '', None),
            'FUTURE_CANDIDATES': len(cs),
            'CROPS_SEEN': crops[:8], 'ISSUES_SEEN': issues[:8],
            'REGIONS_SEEN': regs[:5],
            'REACHES_INTELLIGENCE': tocado,
            'CAN_BECOME_INTELLIGENCE': ('YES' if estado == 'CANDIDATO_NAO_PROMOVIDO'
                                        else 'NO' if estado == 'NAO_USADO' and not cs
                                        else 'PARTIAL' if estado == 'NAO_USADO'
                                        else 'ALREADY'),
            'STATE': estado, 'WHY_NOT_IF_NO': porque,
        })

    fam = familias()
    nao = [x for x in linhas if not x['REACHES_INTELLIGENCE']]
    prio = sorted([x for x in nao if x['STATE'] == 'CANDIDATO_NAO_PROMOVIDO'],
                  key=lambda z: -z['FUTURE_CANDIDATES'])

    out = {
        'DATASET': 'IT-ACERVO-CENSO-V1',
        'LAYER': 'ARCHIVE CENSUS',
        'COUNTRY': 'IT',
        'SOURCE_ID': 'IT-FUTURO-V1',
        'CAPTURED_AT': '2026-09-04',
        'SOURCE': 'censo do acervo italiano VERSIONADO em git, com o estado de cada '
                  'documento em relacao as superficies de inteligencia existentes',
        'SO_CONTA_O_QUE_ESTA_EM_GIT': (
            'transcricao que morreu com o conteiner nao entra. Varrer o que nao '
            'existe mais produziria censo mentiroso — e esta missao ja perdeu '
            'trabalho tres vezes por disco efemero.'),
        'ARCHIVE_ITEMS_SCANNED': len(docs),
        'ARCHIVE_CHARS': sum(len(d['TEXT']) for d in docs),
        'REACHING_INTELLIGENCE': sum(1 for x in linhas if x['REACHES_INTELLIGENCE']),
        'NOT_REACHING_INTELLIGENCE': len(nao),
        'UNUSED_WITH_FUTURE_CANDIDATES': len(prio),
        'BY_FAMILY': {k: dict(v) for k, v in sorted(fam.items())},
        'BY_STATE': dict(collections.Counter(x['STATE'] for x in linhas)),
        'BY_CAN_BECOME': dict(collections.Counter(x['CAN_BECOME_INTELLIGENCE']
                                                  for x in linhas)),
        'TOP_UNUSED_WITH_SIGNAL': prio[:20],
        'ITEMS': linhas,
    }
    json.dump(out, open(os.path.join(DEST, 'IT-ACERVO-CENSO-V1.json'), 'w',
                        encoding='utf-8'), ensure_ascii=False, indent=1)
    print('ARCHIVE_ITEMS_SCANNED          = %d' % out['ARCHIVE_ITEMS_SCANNED'])
    print('ARCHIVE_CHARS                  = %d' % out['ARCHIVE_CHARS'])
    print('REACHING_INTELLIGENCE          = %d' % out['REACHING_INTELLIGENCE'])
    print('NOT_REACHING_INTELLIGENCE      = %d' % out['NOT_REACHING_INTELLIGENCE'])
    print('UNUSED_WITH_FUTURE_CANDIDATES  = %d' % out['UNUSED_WITH_FUTURE_CANDIDATES'])
    print()
    print('por familia:')
    for k, v in out['BY_FAMILY'].items():
        print('  %-34s %s' % (k, dict(v)))
    print()
    print('por estado:', out['BY_STATE'])
    print()
    print('os nao usados com mais sinal de futuro:')
    for x in prio[:10]:
        print('  %-14s %-11s %3d cand  %s' % (x['SOURCE_ID'], x['SOURCE_DATE'],
                                              x['FUTURE_CANDIDATES'],
                                              x['TITLE'][:56]))
    return out


if __name__ == '__main__':
    main()
