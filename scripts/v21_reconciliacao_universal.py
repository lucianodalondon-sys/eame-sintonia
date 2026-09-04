#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A RECONCILIAÇÃO UNIVERSAL · a inteligência de 85df96f sob a catraca de d83f6f3.

    python3 scripts/v21_reconciliacao_universal.py

Duas linhas saíram do mesmo commit `0ddf52d` e cresceram em paralelo. A da
inteligência foi até `85df96f`; a da catraca foi até `d83f6f3` e depois **já
tinha reconciliado** com a inteligência até `e7c154c`. Por isso a base real
deste merge não é a bifurcação: é `e7c154c`.

    NOME DE BRANCH NÃO É ANCESTRALIDADE. `git merge-base` É.

Este arquivo prova três coisas, e reprova se qualquer uma falhar:

1 · **NENHUMA DECISÃO TEM DOIS DONOS.** Cada campo do cartão é escrito por um
    módulo só, e a catraca não escreve nenhum.
2 · **AS OITO TESTEMUNHAS SEMÂNTICAS SOBREVIVERAM.** A catraca é uma camada por
    cima; se ela tiver mexido numa leitura, isto quebra.
3 · **O CONTRATO COMERCIAL É APRESENTAÇÃO, NÃO RECÁLCULO.** Todo campo do
    contrato aponta para um dono que já decidiu.
"""
import json
import os
import sys
from collections import Counter
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ING = os.path.join(ROOT, 'build', 'ITALY-REALITY-HANDOFF-V2.1', 'DESIGN-INGEST')
ANTES = os.path.join(ROOT, 'data', 'samples', 'AUDITORIA-SOMBRA',
                     'V117-ANTES-DA-RECONCILIACAO.json')

# ── PASSO 1 · O MAPA DE DONOS ───────────────────────────────────────────────
# Cada decisão, o módulo que a escreve e o commit onde ela nasceu. Um campo com
# dois donos é um bug esperando a hora de aparecer na tela.
DONOS = {
    'WINDOW_TYPE': ('scripts/v21_janelas.py', '209335e'),
    'WINDOW_DEFINED': ('scripts/v21_janelas.py', '209335e'),
    'WINDOW_OPEN_NOW': ('scripts/v21_janelas.py', '209335e'),
    'WINDOW_OPEN_NOW_METHOD': ('scripts/v21_janelas.py', 'e7c154c'),
    'WINDOW_RULE_STATE': ('scripts/v21_oportunidades.py', '85df96f'),
    'THRESHOLD_STATE': ('scripts/v21_oportunidades.py', 'e7c154c'),
    'PEST_STAGE_STATE': ('scripts/v21_necessidade.py', 'e7c154c'),
    'ACTION_RECOMMENDATION_STATE': ('scripts/v21_necessidade.py', 'e7c154c'),
    'NEED_DIRECTION': ('scripts/v21_necessidade.py', '0ddf52d'),
    'COMMERCIAL_PRIORITY': ('scripts/v21_comercial.py', '0ddf52d'),
    'EXTERNAL_MATERIAL_READY': ('scripts/v21_comercial.py', '0ddf52d'),
    'STATUS': ('scripts/v21_oportunidades.py', 'caa6937'),
    'WHY_NOW_CODES': ('scripts/v21_oportunidades.py', 'caa6937'),
    'PORTFOLIO_MATCHES': ('scripts/v21_oportunidades.py', '0ddf52d'),
    'PRIMARY_MATCH': ('scripts/v21_oportunidades.py', '0ddf52d'),
    'EVIDENCE_ROLES': ('scripts/v21_oportunidades.py', 'caa6937'),
    'INTELLIGENCE_BRIEF': ('scripts/v21_oportunidades.py', 'caa6937'),
    'ACTION_BY_DEPARTMENT': ('scripts/v21_oportunidades.py', 'caa6937'),
    'WHAT_IS_MISSING': ('scripts/v21_oportunidades.py', 'caa6937'),
    'PUBLICATION_STATE': ('scripts/v21_catraca.py', 'd83f6f3'),
    'TRAIL_STATE': ('scripts/v21_catraca.py', 'd83f6f3'),
}

# A catraca é camada por cima: ela LÊ o cartão e escreve DOIS campos seus.
# Se ela escrever qualquer outro, há dois donos e esta lista acusa.
DA_CATRACA = ('PUBLICATION_STATE', 'TRAIL_STATE')

# ── PASSO 6 · O CONTRATO COMERCIAL, E QUEM RESPONDE POR CADA LINHA ──────────
# O briefing APRESENTA. Ele nunca recalcula: cada linha aponta o campo do cartão
# que já decidiu, e o teste confere que o campo existe.
CONTRATO = {
    'WHAT_IS_HAPPENING': 'INTELLIGENCE_BRIEF',
    'WHY_THIS_IS_A_COMMERCIAL_OPPORTUNITY': 'WHY_COMMERCIAL',
    'WHY_NOW': 'WHY_NOW_CHAIN',
    'PORTFOLIO_MATCHES': 'PORTFOLIO_MATCHES',
    'PRIMARY_MATCH': 'PRIMARY_MATCH',
    'WHAT_IS_MISSING': 'WHAT_IS_MISSING',
    'ACTION_MAP': 'ACTION_BY_DEPARTMENT',
    'INTELLIGENCE_BRIEF': 'INTELLIGENCE_BRIEF',
    'EVIDENCES': 'EVIDENCE_ROLES',
}

# ── PASSO 3 · AS OITO TESTEMUNHAS SEMÂNTICAS ────────────────────────────────
# Cada uma é uma leitura que custou uma missão. A catraca não pode ter mexido
# em nenhuma — e se mexeu, é aqui que se descobre.
TESTEMUNHAS = {
    'A': ('OPP_5F31A63F844D', 'botrite x videira x Emilia-Romagna'),
    'B': ('OPP_F8106D5E1767', 'Toscana · «maggior suscettibilita» prova UM elo'),
    'C': ('OPP_75C37DED9160', 'Veneto x carpocapsa · fim do voo nao fecha acao'),
    'D': ('OPP_3C8C3960CC66', 'Emilia-Romagna 5% · UNKNOWN, nunca NO'),
    'E': ('OPP_169BD86DB324', 'Umbria 10-15% sem herdar os 5% da ER'),
    'F': ('OPP_75C37DED9160', 'RULE_DELEGATED_TO_FARM'),
    'G': (None, 'STANDING_RULE nao cria direcao nem oportunidade'),
    'H': ('OPP_D11664591168', 'RULE_ADMINISTRATIVE_ONLY nao vira agronomica'),
}


def _le(nome):
    with open(os.path.join(ING, nome), encoding='utf-8') as f:
        return json.load(f)['RECORDS']


def dono_unico(ops):
    """Nenhum campo do cartão pode ter dois donos declarados."""
    falhas = []
    duplicados = [c for c, n in Counter(DONOS).items() if False]
    del duplicados
    # a catraca escreve dois campos e só dois
    catraca = os.path.join(ROOT, 'scripts', 'v21_catraca.py')
    fonte = open(catraca, encoding='utf-8').read()
    for campo, (mod, _c) in DONOS.items():
        if campo in DA_CATRACA:
            continue
        # o campo do cartão não pode ser ESCRITO pela catraca
        for padrao in ("['%s']" % campo, "'%s':" % campo):
            if padrao + ' =' in fonte:
                falhas.append('a catraca escreve %s, que tem outro dono' % campo)
    for campo in DA_CATRACA:
        if campo not in fonte:
            falhas.append('%s nao e escrito pela catraca' % campo)
    # e todo campo declarado existe mesmo no cartão
    exemplo = ops[0] if ops else {}
    for campo in DONOS:
        if campo not in exemplo:
            falhas.append('campo declarado sem existir no cartao: %s' % campo)
    return falhas


def testemunhas(ops):
    ix = {o['ID']: o for o in ops}
    fora, falhas = {}, []

    def peg(k):
        oid = TESTEMUNHAS[k][0]
        return ix.get(oid) if oid else None

    a = peg('A')
    if a:
        fora['A'] = {k: a.get(k) for k in
                     ('STATUS', 'WINDOW_TYPE', 'WINDOW_DEFINED',
                      'WINDOW_OPEN_NOW', 'WINDOW_OPEN_NOW_METHOD',
                      'PUBLICATION_STATE')}
        if a.get('WINDOW_DEFINED') != 'YES':
            falhas.append('A: a janela agronomica da botrite ER sumiu')
    else:
        falhas.append('A: o caso da botrite ER nao esta no pacote')

    b = peg('B')
    if b:
        produto = {e['EVIDENCE_ID'] for e in (b.get('EVIDENCE_ROLES') or [])
                   if e.get('ROLE') == 'SUPPORTS_PRODUCT_MATCH'}
        fora['B'] = {'WINDOW_EVIDENCE_ID': b.get('WINDOW_EVIDENCE_ID'),
                     'NEED_EVIDENCE_ID': b.get('NEED_EVIDENCE_ID'),
                     'PRODUTO_TEM_OUTRO_DONO': b.get('WINDOW_EVIDENCE_ID')
                     not in produto,
                     'STATUS': b.get('STATUS')}
        if b.get('WINDOW_EVIDENCE_ID') == b.get('NEED_EVIDENCE_ID'):
            falhas.append('B: a mesma frase provou janela e direcao')
        if b.get('WINDOW_EVIDENCE_ID') in produto:
            falhas.append('B: a frase da janela provou tambem o produto')

    c = peg('C')
    if c:
        fora['C'] = {k: c.get(k) for k in
                     ('PEST_STAGE_STATE', 'ACTION_RECOMMENDATION_STATE',
                      'WINDOW_OPEN_NOW', 'STATUS')}
        if c.get('PEST_STAGE_STATE') != 'STAGE_ENDED':
            falhas.append('C: a fase encerrada sumiu do cartao')
        if c.get('ACTION_RECOMMENDATION_STATE') != 'CONTINUE_RECOMMENDED':
            falhas.append('C: «continuare la difesa» sumiu do cartao')
        if c.get('WINDOW_OPEN_NOW') == 'NO':
            falhas.append('C: fim do voo virou janela fechada')

    d = peg('D')
    if d:
        fora['D'] = {k: d.get(k) for k in
                     ('THRESHOLD_STATE', 'WINDOW_OPEN_NOW',
                      'WINDOW_OPEN_NOW_METHOD')}
        if d.get('WINDOW_OPEN_NOW') == 'NO':
            falhas.append('D: os 5% viraram NO sem medicao')

    e = peg('E')
    er = peg('D')
    if e and er:
        fora['E'] = {'WINDOW_CONDITION': str(e.get('WINDOW_CONDITION'))[:120],
                     'EVIDENCIA_UMBRIA': e.get('WINDOW_EVIDENCE_ID'),
                     'EVIDENCIA_ER': er.get('WINDOW_EVIDENCE_ID')}
        if e.get('WINDOW_EVIDENCE_ID') == er.get('WINDOW_EVIDENCE_ID'):
            falhas.append('E: Umbria e Emilia-Romagna partilham a evidencia')
        if '10-15' not in str(e.get('WINDOW_CONDITION')):
            falhas.append('E: a soglia da Umbria sumiu do cartao')

    f = peg('F')
    if f:
        fora['F'] = {k: f.get(k) for k in
                     ('WINDOW_RULE_STATE', 'WINDOW_DEFINED', 'WINDOW_OPEN_NOW')}
        if f.get('WINDOW_RULE_STATE') == 'RULE_DELEGATED_TO_FARM':
            if f.get('WINDOW_DEFINED') != 'YES':
                falhas.append('F: regra delegada sem WINDOW_DEFINED=YES')
            if f.get('WINDOW_OPEN_NOW') != 'UNKNOWN':
                falhas.append('F: regra delegada com janela decidida')

    sinais = {s['ID']: s for s in _le('CURRENT-FIELD-SIGNALS.json')}
    regras = [s for s in sinais.values()
              if s.get('OBSERVATION_CLASS') == 'STANDING_RULE']
    donas = [o['ID'] for o in ops
             if o.get('NEED_EVIDENCE_ID') in {s['ID'] for s in regras}]
    fora['G'] = {'REGRAS_NO_ACERVO': len(regras),
                 'CARTOES_COM_DIRECAO_DE_REGRA': donas}
    if donas:
        falhas.append('G: uma regra virou dona da direcao em %s' % donas)

    h = peg('H')
    if h:
        fora['H'] = {k: h.get(k) for k in
                     ('WINDOW_RULE_STATE', 'WINDOW_DEFINED', 'WHAT_IS_MISSING')}
        if h.get('WINDOW_RULE_STATE') == 'RULE_ADMINISTRATIVE_ONLY' \
                and h.get('WINDOW_DEFINED') == 'YES':
            falhas.append('H: ato administrativo virou janela agronomica')
    return fora, falhas


def contrato(ops):
    falhas = []
    exemplo = next((o for o in ops if o.get('TARGET')), ops[0] if ops else {})
    for linha, dono in CONTRATO.items():
        if dono not in exemplo:
            falhas.append('%s aponta para %s, que nao existe no cartao'
                          % (linha, dono))
    return falhas


def backfill(ops):
    if not os.path.exists(ANTES):
        return {'ERRO': 'sem ANTES gravado'}, ['sem ANTES gravado']
    a = json.load(open(ANTES, encoding='utf-8'))
    A = {r['ID']: r for r in a['RECORDS']}
    D = {r['ID']: r for r in ops}
    CAMPOS = ('STATUS', 'COMMERCIAL_PRIORITY', 'EXTERNAL_MATERIAL_READY',
              'NEED_DIRECTION', 'WINDOW_DEFINED', 'WINDOW_TYPE',
              'WINDOW_OPEN_NOW', 'WINDOW_RULE_STATE', 'WHY_NOW_CODES',
              'MATCHED_COMMERCIAL_PRODUCT_NAMES', 'PRIMARY_MATCH', 'ACTION_MAP',
              'PEST_STAGE_STATE', 'ACTION_RECOMMENDATION_STATE',
              'THRESHOLD_STATE', 'WHAT_IS_MISSING')
    falhas, difs = [], Counter()
    for k in sorted(set(A) | set(D)):
        if k not in A or k not in D:
            falhas.append('caso %s %s' % (k, 'sumiu' if k in A else 'nasceu'))
            continue
        for c in CAMPOS:
            if A[k].get(c) != D[k].get(c):
                difs[c] += 1
                falhas.append('%s mudou em %s' % (c, k))
    return {
        'BUILD_ID_ANTES': a.get('BUILD_ID'),
        'CASOS_ANTES': a.get('COUNT'), 'CASOS_DEPOIS': len(ops),
        'CAMPOS_QUE_MUDARAM': dict(difs),
        'PUBLICATION_STATE_ANTES': dict(Counter(
            str(r.get('PUBLICATION_STATE')) for r in a['RECORDS'])),
        'PUBLICATION_STATE_DEPOIS': dict(Counter(
            str(r.get('PUBLICATION_STATE')) for r in ops)),
    }, falhas


def main():
    ops = _le('OPPORTUNITIES.json')
    pacote = json.load(open(os.path.join(ING, 'OPPORTUNITIES.json'),
                            encoding='utf-8'))
    f1 = dono_unico(ops)
    tst, f3 = testemunhas(ops)
    f6 = contrato(ops)
    bf, f5 = backfill(ops)
    falhas = f1 + f3 + f6 + f5
    veredito = 'PASS' if not falhas else ('PARTIAL' if len(falhas) <= 2
                                          else 'FAIL')

    print('== DONOS ==            campos declarados %d · falhas %d'
          % (len(DONOS), len(f1)))
    print('== TESTEMUNHAS ==      A a H · falhas %d' % len(f3))
    for k in sorted(tst):
        print('   %s · %-58s %s' % (k, TESTEMUNHAS[k][1][:58], tst[k]))
    print('== CONTRATO ==         %d linhas · falhas %d' % (len(CONTRATO), len(f6)))
    print('== BACKFILL ==         %s' % bf)
    print('\nFALHAS: %s' % (falhas or 'nenhuma'))
    print('UNIVERSAL_INTELLIGENCE_RECONCILIATION = %s' % veredito)

    fora = {
        'COLLECTION': 'V117-RECONCILIACAO-UNIVERSAL',
        'SOURCE': 'ANTES: %s · DEPOIS: OPPORTUNITIES.json BUILD_ID %s'
                  % (os.path.relpath(ANTES, ROOT), pacote.get('BUILD_ID')),
        'CAPTURED_AT': date.today().isoformat(),
        'LAW': 'a catraca e camada por cima. Se ela decidir qualquer campo do '
               'cartao, ha dois donos — e este arquivo reprova.',
        'UNIVERSAL_INTELLIGENCE_RECONCILIATION': veredito,
        'DONOS': {k: {'MODULO': v[0], 'NASCEU_EM': v[1]}
                  for k, v in DONOS.items()},
        'CAMPOS_DA_CATRACA': list(DA_CATRACA),
        'CONTRATO_COMERCIAL': CONTRATO,
        'TESTEMUNHAS': {k: {'ROTULO': TESTEMUNHAS[k][1], 'MEDIDO': tst.get(k)}
                        for k in TESTEMUNHAS},
        'BACKFILL': bf,
        'FALHAS': falhas,
    }
    saida = os.path.join(ROOT, 'data', 'samples', 'AUDITORIA-SOMBRA',
                         'V117-RECONCILIACAO-UNIVERSAL.json')
    json.dump(fora, open(saida, 'w', encoding='utf-8'), ensure_ascii=False,
              indent=1)
    print('gravado em %s' % os.path.relpath(saida, ROOT))
    return 0 if veredito == 'PASS' else 1


if __name__ == '__main__':
    sys.exit(main())
