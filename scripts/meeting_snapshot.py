#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O SNAPSHOT DA REUNIÃO · a única fonte de inteligência da interface.

    python3 scripts/meeting_snapshot.py --source-head <sha> [--cutoff ISO8601]

    lê     build/ITALY-REALITY-HANDOFF-V2.1/DESIGN-INGEST/OPPORTUNITIES.json
    grava  italia-portale/client/meeting-intelligence-snapshot.json
           italia-portale/client/meeting-intelligence-snapshot.js

POR QUE UM SNAPSHOT, E NÃO O PACOTE
------------------------------------
O portal não pode ler arquivo intermediário. Se ele lê o pacote, ele passa a
depender de quando o pacote foi construído — e uma reunião não pode depender de
um build que ninguém sabe se terminou.

    O QUE A REUNIÃO MOSTRA TEM DE SER IMUTÁVEL, IDENTIFICADO E DATADO.

O snapshot carrega o `SOURCE_HEAD` do commit da inteligência, o `BUILD_ID` do
pacote e o `MEETING_CUTOFF`. Se qualquer um dos três não bater, a régua reprova.

O QUE ATRAVESSA — E O QUE NÃO
------------------------------
A mesma lei de `site_v21_ingest.py`: LISTA DE PERMISSÃO, campo a campo. Fato e
CÓDIGO atravessam; prosa de pesquisa em português NÃO.

    PROSA QUE NÃO EMBARCA NÃO VAZA.

`WINDOW_CONDITION` é a oração original do boletim, em português de pesquisa.
Ela **não** atravessa como texto: atravessa `WINDOW_CONDITION__PT_ONLY: true` e
a identificação do documento que a contém. A tela diz «a condição está declarada
no documento X» — que é verdade — em vez de mostrar português a um italiano.

E O MOTOR NÃO VAI JUNTO
-----------------------
Nenhuma regra é recalculada aqui. Este arquivo COPIA campos já decididos e
recusa os que não estão na lista. Se um dia ele começar a decidir alguma coisa,
haverá dois donos — e o gate `NO_RAW_BYPASS` existe para isso não acontecer em
silêncio.
"""
import json
import os
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ING = os.path.join(ROOT, 'build', 'ITALY-REALITY-HANDOFF-V2.1', 'DESIGN-INGEST')
OUT = os.path.join(ROOT, 'italia-portale', 'client')

# ── CAMPOS QUE ATRAVESSAM · fato, código, número. Nunca prosa de pesquisa. ──
CAMPOS = (
    'ID', 'ARCHETYPE', 'CROP', 'TARGET', 'GEOGRAPHY', 'GEOGRAPHIC_SCOPE',
    'STATUS', 'OPPORTUNITY_STATE', 'RENDERABLE_WITH_METHOD',
    # a régua comercial
    'COMMERCIAL_PRIORITY', 'WHY_COMMERCIAL_CODES',
    'EXTERNAL_MATERIAL_READY', 'EXTERNAL_BLOCKER_CODES',
    # a cadeia do agora
    'WHY_NOW_CODES', 'WHY_NOW_CHAIN', 'ACTION_CHAIN_LINKS',
    'SIGNAL_DATE', 'SIGNAL_AGE_DAYS', 'SIGNAL_CURRENCY',
    'COMMERCIAL_TIMING_BASIS',
    # a janela
    'WINDOW_TYPE', 'WINDOW_DEFINED', 'WINDOW_OPEN_NOW',
    'WINDOW_OPEN_NOW_METHOD', 'WINDOW_EVIDENCE_ID',
    'WINDOW_RULE_STATE', 'WINDOW_RULE_EVIDENCE_ID',
    'WINDOW_START', 'WINDOW_END', 'DAYS_REMAINING', 'WINDOW_STATE',
    # os três estados declarados, com dono separado
    'PEST_STAGE_STATE', 'PEST_STAGE_EVIDENCE_ID',
    'ACTION_RECOMMENDATION_STATE', 'ACTION_RECOMMENDATION_EVIDENCE_ID',
    'THRESHOLD_STATE', 'THRESHOLD_STATE_EVIDENCE_ID',
    'NEED_DIRECTION', 'NEED_EVIDENCE_ID', 'NEED_METHOD', 'NEED_AMBIGUITY_CODES',
    # o portfólio, produto a produto
    'PORTFOLIO_MATCHES', 'PRIMARY_MATCH', 'PRIMARY_MATCH_REASON',
    'PRODUCT_LINK_STATE', 'MATCHED_COMMERCIAL_PRODUCT_IDS',
    'MATCHED_COMMERCIAL_PRODUCT_NAMES', 'COMMERCIAL_PRODUCT_COUNT',
    'ACTIVE_INGREDIENT_NAMES', 'MODE_OF_ACTION_CODES', 'MODE_OF_ACTION_STATE',
    'PRODUCT_RESTRICTIONS', 'APPLICATION_STATE',
    # o que falta, quem age, e o papel de cada evidência
    'WHAT_IS_MISSING', 'ACTION_BY_DEPARTMENT', 'EVIDENCE_ROLES',
    'INTELLIGENCE_BRIEF', 'EVIDENCE_IDS', 'EVIDENCE_COUNT',
    'EVIDENCE_FAMILIES',
    # tamanho e confiança
    'COMMERCIAL_MAGNITUDE', 'COMMERCIAL_MAGNITUDE_DIMENSIONS',
    'SIGNAL_CONFIDENCE', 'WINDOW_CONFIDENCE', 'PRODUCT_MATCH_CONFIDENCE',
    'CONFIDENCE', 'OPPORTUNITY_SCORE',
    # a catraca
    'PUBLICATION_STATE', 'TRAIL_STATE',
    # a geografia da afirmação
    'CLAIM_GEOGRAPHY', 'CLAIM_GEOGRAPHY_HOLDS',
    'SOURCE_IDS', 'SOURCE_URLS', 'REFERENCE_DATE',
)

# Campos localizáveis: só atravessam com o par IT+EN aprovado.
LOCALIZAVEIS = ('WHY_COMMERCIAL', 'WHAT_IT_PROVES', 'WHAT_IT_DOES_NOT_PROVE',
                'COMMERCIAL_DOES_NOT_PROVE')

# Prosa de pesquisa que NÃO atravessa como texto — só como declaração de que
# existe, e do documento que a contém.
SO_DECLARADOS = ('WINDOW_CONDITION', 'NEED_EXCERPT', 'PEST_STAGE_EXCERPT',
                 'ACTION_RECOMMENDATION_EXCERPT')


def cabeca_do_commit(argv):
    """→ o HEAD da INTELIGÊNCIA, não o do checkout de agora.

    O pacote é construído na branch canônica e o snapshot é gerado na branch da
    reunião — `git rev-parse HEAD` aqui devolveria a casca visual, e o snapshot
    passaria a declarar uma procedência que não é a sua.

        UM SNAPSHOT QUE DECLARA O COMMIT ERRADO É PIOR QUE UM SEM COMMIT:
        ELE PARECE AUDITÁVEL.
    """
    if '--source-head' in argv:
        sha = argv[argv.index('--source-head') + 1]
        try:
            subprocess.check_output(['git', 'cat-file', '-e', sha + '^{commit}'],
                                    cwd=ROOT, stderr=subprocess.DEVNULL)
        except Exception:
            raise SystemExit('--source-head %s nao e um commit deste repositorio'
                             % sha)
        return sha
    raise SystemExit('faltou --source-head <sha da inteligencia canonica>')


def linha(o):
    r = {}
    for c in CAMPOS:
        if c in o:
            r[c] = o[c]
    for c in LOCALIZAVEIS:
        it, en = o.get(c + '_IT'), o.get(c + '_EN')
        if it and en:
            r[c + '_IT'], r[c + '_EN'] = it, en
        elif o.get(c):
            r[c + '__PT_ONLY'] = True
    for c in SO_DECLARADOS:
        if o.get(c):
            r[c + '__PT_ONLY'] = True
    return r


def main():
    cutoff = None
    if '--cutoff' in sys.argv:
        cutoff = sys.argv[sys.argv.index('--cutoff') + 1]
    cutoff = cutoff or datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

    with open(os.path.join(ING, 'OPPORTUNITIES.json'), encoding='utf-8') as f:
        pac = json.load(f)
    regras_p = os.path.join(ING, 'OPPORTUNITY-RULES.json')
    with open(regras_p, encoding='utf-8') as f:
        regras = json.load(f)

    casos = [linha(o) for o in pac['RECORDS']]
    conta = lambda k: dict(Counter(str(c.get(k)) for c in casos))  # noqa: E731

    snap = {
        'COLLECTION': 'MEETING-INTELLIGENCE-SNAPSHOT',
        'LAW': 'esta e a UNICA fonte de inteligencia da interface. O portal '
               'apresenta; ele nao recalcula STATUS, COMMERCIAL_PRIORITY, '
               'WHY_NOW, janela, produto, papel de evidencia, mapa de acao nem '
               'PUBLICATION_STATE.',
        'SOURCE_HEAD': cabeca_do_commit(sys.argv),
        'BUILD_ID': pac.get('BUILD_ID'),
        'ENGINE_VERSION': 'scripts/v21_oportunidades.py + v21_janelas.py + '
                          'v21_necessidade.py + v21_comercial.py',
        'RULE_VERSION': regras.get('BUILD_ID') or pac.get('BUILD_ID'),
        'GENERATED_AT': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'MEETING_CUTOFF': cutoff,
        'TOTAL_CASES': len(casos),
        'BY_STATUS': conta('STATUS'),
        'BY_COMMERCIAL_PRIORITY': conta('COMMERCIAL_PRIORITY'),
        'BY_PUBLICATION_STATE': conta('PUBLICATION_STATE'),
        'BY_WINDOW_DEFINED': conta('WINDOW_DEFINED'),
        'BY_WINDOW_OPEN_NOW': conta('WINDOW_OPEN_NOW'),
        'BY_WINDOW_RULE_STATE': conta('WINDOW_RULE_STATE'),
        'BRIEF_TEMPLATES': regras.get('INTELLIGENCE_BRIEF_TEMPLATES') or {},
        'WINDOW_TYPES_AGRONOMIC': regras.get('WINDOW_TYPES_AGRONOMIC') or [],
        'CASES': casos,
    }

    os.makedirs(OUT, exist_ok=True)
    pj = os.path.join(OUT, 'meeting-intelligence-snapshot.json')
    with open(pj, 'w', encoding='utf-8') as f:
        json.dump(snap, f, ensure_ascii=False, indent=1)
    pjs = os.path.join(OUT, 'meeting-intelligence-snapshot.js')
    with open(pjs, 'w', encoding='utf-8') as f:
        f.write('/* GERADO por scripts/meeting_snapshot.py — NAO EDITAR A MAO.\n'
                '   SOURCE_HEAD %s · BUILD_ID %s · MEETING_CUTOFF %s */\n'
                % (snap['SOURCE_HEAD'], snap['BUILD_ID'], snap['MEETING_CUTOFF']))
        f.write('window.MEETING_INTELLIGENCE = ')
        json.dump(snap, f, ensure_ascii=False, separators=(',', ':'))
        f.write(';\n')

    print('SOURCE_HEAD     %s' % snap['SOURCE_HEAD'])
    print('BUILD_ID        %s' % snap['BUILD_ID'])
    print('MEETING_CUTOFF  %s' % snap['MEETING_CUTOFF'])
    print('TOTAL_CASES     %d' % snap['TOTAL_CASES'])
    for k in ('BY_STATUS', 'BY_COMMERCIAL_PRIORITY', 'BY_PUBLICATION_STATE',
              'BY_WINDOW_DEFINED', 'BY_WINDOW_OPEN_NOW', 'BY_WINDOW_RULE_STATE'):
        print('%-24s %s' % (k, snap[k]))
    print('\ngravado: %s' % os.path.relpath(pj, ROOT))
    print('gravado: %s (%.0f KB)'
          % (os.path.relpath(pjs, ROOT), os.path.getsize(pjs) / 1024.0))
    return 0


if __name__ == '__main__':
    sys.exit(main())
