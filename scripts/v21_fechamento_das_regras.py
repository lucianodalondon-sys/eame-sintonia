#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FECHAMENTO DAS REGRAS DE JANELA · onze vãos, um a um, com a fonte ao lado.

    python3 scripts/v21_fechamento_das_regras.py

`WINDOW_RULE_MISSING` dizia uma coisa só — «ninguém declarou a condição» — e
essa frase estava errada de quatro maneiras diferentes ao mesmo tempo:

    a regra existe e é agronômica          → RULE_DECLARED
    a regra existe e é uma obrigação       → RULE_ADMINISTRATIVE_ONLY
    a regra existe e manda medir no pomar  → RULE_DELEGATED_TO_FARM
    ninguém declarou nada                  → RULE_NOT_DECLARED

Só o último pede coleta. Os outros três já foram respondidos por quem publica a
regra, e continuar a chamá-los de «ausentes» é pedir a uma equipe que vá buscar
um documento que ninguém vai escrever.

    «NÃO ACHAMOS A REGRA» E «A REGRA DIZ OUTRA COISA» SÃO RESPOSTAS DIFERENTES.

O ANTES sai de `V116-ANTES-DAS-REGRAS.json`, gerado repondo a árvore de
`e7c154c` e rodando a cadeia real — nunca de lembrança.
"""
import json
import os
import sys
from collections import Counter
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ING = os.path.join(ROOT, 'build', 'ITALY-REALITY-HANDOFF-V2.1', 'DESIGN-INGEST')
ANTES = os.path.join(ROOT, 'data', 'samples', 'AUDITORIA-SOMBRA',
                     'V116-ANTES-DAS-REGRAS.json')

# Os onze vãos, na ordem de prioridade declarada em
# `scripts/v21_regras_de_janela_ausentes.py`. A lista é fixa de propósito: se um
# caso sumir do pacote, o relatório quebra em vez de calar.
VAOS = [
    ('OPP_D9B21D005CC3', 'videira x peronospora · Friuli-Venezia Giulia'),
    ('OPP_48C2731BAFD1', 'videira x escafoideo · Umbria'),
    ('OPP_4C39CCC05EEB', 'arroz x giavone · Italia'),
    ('OPP_DF0C3648893A', 'videira x peronospora · Umbria'),
    ('OPP_E138ECDFD7D2', 'videira x peronospora · Emilia-Romagna'),
    ('OPP_81C053E9DCD3', 'milho x piralide · Lombardia'),
    ('OPP_D11664591168', 'videira x escafoideo · Toscana'),
    ('OPP_F6EEF5B32F65', 'milho x diabrotica · Lombardia'),
    ('OPP_195919127658', 'videira x oidio · Friuli-Venezia Giulia'),
    ('OPP_C1735138E362', 'videira x oidio · Umbria'),
    ('OPP_C5F7888EC524', 'videira x oidio · Toscana'),
]

CAMPOS = ('WINDOW_DEFINED', 'WINDOW_TYPE', 'WINDOW_CONDITION', 'WINDOW_OPEN_NOW',
          'STATUS', 'WHAT_IS_MISSING')

COMPARADOS = ('STATUS', 'COMMERCIAL_PRIORITY', 'EXTERNAL_MATERIAL_READY',
              'NEED_DIRECTION', 'WINDOW_DEFINED', 'WINDOW_TYPE',
              'WINDOW_OPEN_NOW', 'WINDOW_RULE_STATE', 'WHAT_IS_MISSING')

FECHA_A_PERGUNTA = ('RULE_DECLARED', 'RULE_ADMINISTRATIVE_ONLY',
                    'RULE_DELEGATED_TO_FARM')


def _le(nome):
    with open(os.path.join(ING, nome), encoding='utf-8') as f:
        return json.load(f)['RECORDS']


def bloco(r):
    return {c: r.get(c) for c in CAMPOS}


def fonte(r, sinais):
    """→ a fonte que respondeu, com data, citação e papel — ou nada."""
    sid = r.get('WINDOW_RULE_EVIDENCE_ID') or r.get('WINDOW_EVIDENCE_ID')
    s = sinais.get(sid)
    if not s:
        return None
    papel = {'RULE_DECLARED': 'DECLARA_A_CONDICAO_AGRONOMICA',
             'RULE_ADMINISTRATIVE_ONLY': 'DECLARA_A_OBRIGACAO_DE_NORMA',
             'RULE_DELEGATED_TO_FARM': 'DECLARA_QUE_A_DECISAO_E_DO_POMAR'}
    return {
        'SOURCE': s.get('BULLETIN_TITLE') or (s.get('SOURCE_IDS') or [None])[0],
        'SOURCE_ID': sid,
        'SOURCE_URLS': s.get('SOURCE_URLS'),
        'DATE': s.get('REFERENCE_DATE'),
        'OBSERVATION_CLASS': s.get('OBSERVATION_CLASS'),
        'REGION': s.get('REGION_IDS'),
        'EXACT_QUOTE': (s.get('RESEARCH') or {}).get('citacao_literal'),
        'SOURCE_ROLE': papel.get(r.get('WINDOW_RULE_STATE'), 'NAO_RESPONDEU'),
    }


def main():
    if not os.path.exists(ANTES):
        print('sem ANTES gravado — nada a comparar')
        return 1
    a = json.load(open(ANTES, encoding='utf-8'))
    antes = {r['ID']: r for r in a['RECORDS']}
    ops = _le('OPPORTUNITIES.json')
    depois = {r['ID']: r for r in ops}
    sinais = {s['ID']: s for s in _le('CURRENT-FIELD-SIGNALS.json')}
    pacote = json.load(open(os.path.join(ING, 'OPPORTUNITIES.json'),
                            encoding='utf-8'))

    itens, falhas = [], []
    for oid, rotulo in VAOS:
        x, y = antes.get(oid), depois.get(oid)
        if not (x and y):
            falhas.append('caso %s %s' % (oid, 'sumiu' if x else 'nao existia'))
            continue
        f = fonte(y, sinais)
        mudou = y.get('WINDOW_RULE_STATE') != x.get('WINDOW_RULE_STATE')
        item = {'OPPORTUNITY_ID': oid, 'ROTULO': rotulo,
                'ANTES': bloco(x), 'FONTE': f, 'DEPOIS': bloco(y),
                'WINDOW_RULE_STATE_ANTES': x.get('WINDOW_RULE_STATE'),
                'WINDOW_RULE_STATE_DEPOIS': y.get('WINDOW_RULE_STATE'),
                'COMMERCIAL_PRIORITY_ANTES': x.get('COMMERCIAL_PRIORITY'),
                'COMMERCIAL_PRIORITY_DEPOIS': y.get('COMMERCIAL_PRIORITY')}
        if mudou:
            item['WHY_CHANGED'] = (
                'a fonte regional declarou a regra, e ela entrou pela mesma '
                'porta e pela mesma cadeia dos boletins')
        else:
            item['WHY_NOT_CHANGED'] = (
                'nenhuma fonte oficial declara a condicao para este par NESTA '
                'geografia; e a geografia do caso nao e regional')
        # ⚠️ A REGRA NAO PODE MOVER O ESTADO COMERCIAL. Ela informa o momento;
        # quem manda agir continua a ser o boletim.
        for c in ('STATUS', 'COMMERCIAL_PRIORITY', 'EXTERNAL_MATERIAL_READY',
                  'NEED_DIRECTION'):
            if x.get(c) != y.get(c):
                falhas.append('%s: a regra mexeu em %s (%s -> %s)'
                              % (oid, c, x.get(c), y.get(c)))
        itens.append(item)

    ganharam = [i for i in itens
                if i['WINDOW_RULE_STATE_DEPOIS'] in FECHA_A_PERGUNTA]
    delegadas = [i for i in itens
                 if i['WINDOW_RULE_STATE_DEPOIS'] == 'RULE_DELEGATED_TO_FARM']
    administrativas = [i for i in itens
                       if i['WINDOW_RULE_STATE_DEPOIS'] == 'RULE_ADMINISTRATIVE_ONLY']
    abertos = [i for i in itens
               if i['WINDOW_RULE_STATE_DEPOIS'] == 'RULE_NOT_DECLARED']

    # ── o acervo inteiro, contado dos dois lados ─────────────────────────────
    def conta(regs):
        c = Counter()
        for r in regs:
            c['CASES'] += 1
            c[r.get('STATUS')] += 1
            if r.get('COMMERCIAL_PRIORITY') == 'SALES_READY':
                c['SALES_READY'] += 1
            if r.get('WINDOW_DEFINED') == 'YES':
                c['WINDOW_DEFINED'] += 1
            c['WINDOW_OPEN_NOW_' + str(r.get('WINDOW_OPEN_NOW'))] += 1
            if r.get('WINDOW_RULE_STATE') == 'RULE_DELEGATED_TO_FARM':
                c['RULE_DELEGATED_TO_FARM'] += 1
            if r.get('WINDOW_RULE_STATE') == 'RULE_ADMINISTRATIVE_ONLY':
                c['RULE_ADMINISTRATIVE_ONLY'] += 1
            if 'WINDOW_RULE_MISSING' in (r.get('WHAT_IS_MISSING') or []):
                c['WINDOW_RULE_MISSING'] += 1
        return dict(c)

    ca, cd = conta(a['RECORDS']), conta(ops)
    veredito = ('FAIL' if falhas else
                'PASS' if len(abertos) <= 1 else 'PARTIAL')

    for i in itens:
        print('── %-42s %s -> %s' % (i['ROTULO'], i['WINDOW_RULE_STATE_ANTES'],
                                     i['WINDOW_RULE_STATE_DEPOIS']))
        if i['FONTE']:
            print('   fonte : %s' % str(i['FONTE']['SOURCE'])[:96])
            print('   papel : %s · %s' % (i['FONTE']['SOURCE_ROLE'],
                                          i['FONTE']['DATE']))
        print('   janela: %s %s · aberta=%s' % (i['DEPOIS']['WINDOW_DEFINED'],
                                                i['DEPOIS']['WINDOW_TYPE'],
                                                i['DEPOIS']['WINDOW_OPEN_NOW']))
    print('\nganharam regra          : %d de %d' % (len(ganharam), len(itens)))
    print('  agronomica            : %d' % (len(ganharam) - len(delegadas)
                                            - len(administrativas)))
    print('  administrativa        : %d' % len(administrativas))
    print('  delegada ao pomar     : %d' % len(delegadas))
    print('continuam sem regra     : %d' % len(abertos))
    print('\nACERVO  ANTES %s' % ca)
    print('ACERVO  DEPOIS %s' % cd)
    print('\nFALHAS: %s' % (falhas or 'nenhuma'))
    print('WINDOW_RULE_CLOSURE = %s' % veredito)

    fora = {
        'COLLECTION': 'V116-FECHAMENTO-DAS-REGRAS',
        'SOURCE': 'ANTES: data/samples/AUDITORIA-SOMBRA/V116-ANTES-DAS-REGRAS.json '
                  '(BUILD_ID %s) · DEPOIS: build/ITALY-REALITY-HANDOFF-V2.1/'
                  'DESIGN-INGEST/OPPORTUNITIES.json (BUILD_ID %s)'
                  % (a.get('BUILD_ID'), pacote.get('BUILD_ID')),
        'CAPTURED_AT': date.today().isoformat(),
        'LAW': 'a regra declara QUANDO agir. Se ela mexer em STATUS, '
               'COMMERCIAL_PRIORITY, EXTERNAL_MATERIAL_READY ou NEED_DIRECTION, '
               'e defeito — e este arquivo reprova.',
        'WINDOW_RULE_CLOSURE': veredito,
        'BUILD_ID_ANTES': a.get('BUILD_ID'),
        'BUILD_ID_DEPOIS': pacote.get('BUILD_ID'),
        'GAPS_INICIAIS': len(itens),
        'GANHARAM_REGRA': len(ganharam),
        'REGRA_ADMINISTRATIVA': len(administrativas),
        'REGRA_DELEGADA_AO_POMAR': len(delegadas),
        'CONTINUAM_SEM_REGRA': len(abertos),
        'BACKFILL_ANTES': ca,
        'BACKFILL_DEPOIS': cd,
        'FALHAS': falhas,
        'ITENS': itens,
    }
    saida = os.path.join(ROOT, 'data', 'samples', 'AUDITORIA-SOMBRA',
                         'V116-FECHAMENTO-DAS-REGRAS.json')
    json.dump(fora, open(saida, 'w', encoding='utf-8'), ensure_ascii=False,
              indent=1)
    print('gravado em %s' % os.path.relpath(saida, ROOT))
    return 0 if veredito != 'FAIL' else 1


if __name__ == '__main__':
    sys.exit(main())
