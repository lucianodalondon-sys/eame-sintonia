#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BACKFILL PREVIEW · o que os 43 casos seriam se reconstruíssemos hoje.

    python3 scripts/v21_backfill_preview.py --gravar-antes <OPPORTUNITIES.json>
    python3 scripts/v21_backfill_preview.py

NÃO publica. NÃO toca o portal. Ele compara a informação que ALIMENTARIA o
portal — estado, janela, produtos, mapa de ações, briefing — entre o pacote
anterior e o reprocessado, caso a caso, e classifica cada diferença.

    NÃO SE COMPARA LAYOUT. COMPARA-SE O QUE A TELA LERIA.

O ANTES sai de um arquivo, e o arquivo sai de um `git worktree` no commit
anterior — não de memória.
"""
import json
import os
import sys
from collections import Counter
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ING = os.path.join(ROOT, 'build', 'ITALY-REALITY-HANDOFF-V2.1', 'DESIGN-INGEST')
ANTES = os.path.join(ROOT, 'data', 'samples', 'AUDITORIA-SOMBRA',
                     'V113-ANTES-DO-REPROCESSAMENTO.json')
SAIDA = os.path.join(ROOT, 'data', 'samples', 'AUDITORIA-SOMBRA',
                     'V113-BACKFILL-PREVIEW.json')

CAMPOS = ('ID', 'ARCHETYPE', 'CROP', 'TARGET', 'GEOGRAPHY', 'STATUS',
          'OPPORTUNITY_STATE', 'COMMERCIAL_PRIORITY', 'EXTERNAL_MATERIAL_READY',
          'NEED_DIRECTION', 'WINDOW_TYPE', 'WINDOW_DEFINED', 'WINDOW_OPEN_NOW',
          'WINDOW_CONDITION', 'COMMERCIAL_WINDOW', 'MATCHED_COMMERCIAL_PRODUCT_NAMES',
          'PRIMARY_MATCH', 'WHY_NOW_CODES', 'WHY_COMMERCIAL_CODES',
          'ACTION_BY_DEPARTMENT', 'INTELLIGENCE_BRIEF', 'BLOCKING_GATES')

# Quanto cada estado AFIRMA. Serve só para dizer se a mudança subiu ou desceu.
FORCA = {'ACT_NOW': 5, 'PREPARE_NOW': 4, 'VALIDATE_NOW': 3,
         'FUTURE_PREPARATION': 2, 'WATCH': 1, 'TO_VALIDATE': 0}

CLASSES = ('CORRECAO', 'ENRIQUECIMENTO', 'REBAIXAMENTO', 'PROMOCAO',
           'SEM_MUDANCA')


def _chave(r):
    return '%s|%s|%s|%s' % (r['ARCHETYPE'], r.get('CROP'), r.get('TARGET'),
                            r.get('GEOGRAPHY'))


def _resumo(r):
    return {c: r.get(c) for c in CAMPOS}


def gravar_antes(caminho):
    d = json.load(open(caminho, encoding='utf-8'))
    fora = {
        'COLLECTION': 'V113-ANTES-DO-REPROCESSAMENTO',
        'SOURCE': 'git worktree --detach do commit anterior + scripts/v21_cadeia.sh · '
                  'BUILD_ID %s' % d.get('BUILD_ID'),
        'CAPTURED_AT': date.today().isoformat(),
        'LAW': 'o ANTES sai de um pacote reconstruido no commit anterior, nao '
               'de memoria. Recorte dos campos comparados.',
        'BUILD_ID': d.get('BUILD_ID'),
        'FIELDS': list(CAMPOS),
        'RECORDS': [_resumo(r) for r in d['RECORDS']],
    }
    os.makedirs(os.path.dirname(ANTES), exist_ok=True)
    json.dump(fora, open(ANTES, 'w', encoding='utf-8'), ensure_ascii=False,
              indent=1)
    print('gravado %s · %d casos' % (os.path.relpath(ANTES, ROOT),
                                     len(d['RECORDS'])))
    return 0


def _mapa(dep):
    return {d: v.get('ACTION') for d, v in (dep or {}).items()}


def classificar(a, b):
    """→ (classe, razões). A ordem é lei: estado primeiro, enriquecimento por último."""
    r = []
    fa, fb = FORCA.get(a['STATUS'], -1), FORCA.get(b['STATUS'], -1)
    if a['STATUS'] != b['STATUS']:
        r.append('ESTADO %s -> %s' % (a['STATUS'], b['STATUS']))
    if set(a.get('MATCHED_COMMERCIAL_PRODUCT_NAMES') or []) != \
            set(b.get('MATCHED_COMMERCIAL_PRODUCT_NAMES') or []):
        r.append('PRODUTOS %s -> %s' % (a.get('MATCHED_COMMERCIAL_PRODUCT_NAMES'),
                                        b.get('MATCHED_COMMERCIAL_PRODUCT_NAMES')))
    # ⚠️ Campo que NAO EXISTIA antes nao e resposta diferente: e resposta nova.
    # So e CORRECAO quando o reprocessamento ACHA uma janela onde o pacote
    # anterior afirmava nao haver nenhuma.
    janela_nova = (b.get('WINDOW_DEFINED') == 'YES'
                   and a.get('WINDOW_DEFINED') != 'YES')
    if janela_nova:
        r.append('JANELA ENCONTRADA NO ACERVO: %s · aberta agora=%s'
                 % (b.get('WINDOW_TYPE'), b.get('WINDOW_OPEN_NOW')))
    elif a.get('WINDOW_DEFINED') != b.get('WINDOW_DEFINED'):
        r.append('JANELA %s -> %s (campo novo, mesma resposta)'
                 % (a.get('WINDOW_DEFINED'), b.get('WINDOW_DEFINED')))
    if _mapa(a.get('ACTION_BY_DEPARTMENT')) != _mapa(b.get('ACTION_BY_DEPARTMENT')):
        r.append('MAPA DE ACOES mudou')
    novo = [c for c in ('PORTFOLIO_MATCHES', 'INTELLIGENCE_BRIEF',
                        'EVIDENCE_ROLES', 'WINDOW_TYPE')
            if not a.get(c) and b.get(c)]
    if novo:
        r.append('INTELIGENCIA NOVA: ' + ', '.join(novo))

    if a['STATUS'] != b['STATUS']:
        return ('PROMOCAO' if fb > fa else 'REBAIXAMENTO'), r
    if any(x.startswith('PRODUTOS') for x in r) or janela_nova:
        return 'CORRECAO', r
    if r:
        return 'ENRIQUECIMENTO', r
    return 'SEM_MUDANCA', r


def main():
    if len(sys.argv) > 2 and sys.argv[1] == '--gravar-antes':
        return gravar_antes(sys.argv[2])
    A = {_chave(r): r for r in json.load(open(ANTES, encoding='utf-8'))['RECORDS']}
    d = json.load(open(os.path.join(ING, 'OPPORTUNITIES.json'), encoding='utf-8'))
    B = {_chave(r): _resumo(r) for r in d['RECORDS']}
    regras = json.load(open(os.path.join(ING, 'OPPORTUNITY-RULES.json'),
                            encoding='utf-8'))
    tpl = regras.get('INTELLIGENCE_BRIEF_TEMPLATES') or {}

    linhas = []
    for k in sorted(set(A) | set(B)):
        a, b = A.get(k), B.get(k)
        if not a or not b:
            linhas.append({'KEY': k, 'CLASS': 'CORRECAO',
                           'WHY': ['caso so existe em um dos lados'],
                           'ANTES': a, 'DEPOIS': b})
            continue
        classe, por = classificar(a, b)
        linhas.append({'KEY': k, 'OPPORTUNITY_ID_ANTES': a['ID'],
                       'OPPORTUNITY_ID_DEPOIS': b['ID'], 'CLASS': classe,
                       'WHY': por,
                       'ESTADO_ATUAL': a['STATUS'], 'ESTADO_REPROCESSADO': b['STATUS'],
                       'PRODUTOS_ATUAIS': a.get('MATCHED_COMMERCIAL_PRODUCT_NAMES'),
                       'PRODUTOS_REPROCESSADOS': b.get('MATCHED_COMMERCIAL_PRODUCT_NAMES'),
                       'PRIMARY_MATCH': b.get('PRIMARY_MATCH'),
                       'WINDOW_ATUAL': {'DEFINED': a.get('WINDOW_DEFINED'),
                                        'OPEN_NOW': a.get('WINDOW_OPEN_NOW'),
                                        'TYPE': a.get('WINDOW_TYPE')},
                       'WINDOW_REPROCESSADA': {'DEFINED': b.get('WINDOW_DEFINED'),
                                               'OPEN_NOW': b.get('WINDOW_OPEN_NOW'),
                                               'TYPE': b.get('WINDOW_TYPE'),
                                               'CONDITION': b.get('WINDOW_CONDITION')},
                       'ACTION_MAP_ATUAL': _mapa(a.get('ACTION_BY_DEPARTMENT')),
                       'ACTION_MAP_REPROCESSADO': _mapa(b.get('ACTION_BY_DEPARTMENT')),
                       'WHY_NOW_CODES': b.get('WHY_NOW_CODES'),
                       'WHY_COMMERCIAL_CODES': b.get('WHY_COMMERCIAL_CODES'),
                       'BRIEF_ATUAL': a.get('INTELLIGENCE_BRIEF'),
                       'BRIEF_REPROCESSADO': b.get('INTELLIGENCE_BRIEF')})

    print('=' * 78)
    print('BACKFILL PREVIEW · %d casos' % len(linhas))
    for c, n in Counter(x['CLASS'] for x in linhas).most_common():
        print('  %-16s %d' % (c, n))
    print('=' * 78)
    for x in linhas:
        if x['CLASS'] == 'SEM_MUDANCA':
            continue
        print('\n%s  [%s]' % (x['KEY'], x['CLASS']))
        for p in x['WHY']:
            print('    · %s' % p)
        if x.get('BRIEF_REPROCESSADO'):
            print('    BRIEFING:')
            for seg in x['BRIEF_REPROCESSADO']:
                frase = tpl.get(seg['CODE'], seg['CODE'])
                try:
                    frase = frase.format(**seg['VALUES'])
                except Exception:
                    pass
                print('      %s' % frase)

    fora = {
        'COLLECTION': 'V113-BACKFILL-PREVIEW',
        'SOURCE': 'ANTES: %s · DEPOIS: build/.../OPPORTUNITIES.json BUILD_ID %s'
                  % (os.path.relpath(ANTES, ROOT), d.get('BUILD_ID')),
        'CAPTURED_AT': date.today().isoformat(),
        'LAW': 'preview, nao publicacao. Nada aqui foi ao portal.',
        'BY_CLASS': dict(Counter(x['CLASS'] for x in linhas)),
        'BY_STATUS_ANTES': dict(Counter(x.get('ESTADO_ATUAL') for x in linhas)),
        'BY_STATUS_DEPOIS': dict(Counter(x.get('ESTADO_REPROCESSADO')
                                         for x in linhas)),
        'BRIEF_TEMPLATES': tpl,
        'CASES': linhas,
    }
    os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
    json.dump(fora, open(SAIDA, 'w', encoding='utf-8'), ensure_ascii=False,
              indent=1)
    print('\ngravado em %s' % os.path.relpath(SAIDA, ROOT))
    return 0


if __name__ == '__main__':
    sys.exit(main())
