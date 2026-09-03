#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AS DUAS TESTEMUNHAS · o que o vínculo perdia, medido no pacote construído.

    python3 scripts/v21_defeitos_do_vinculo.py

Este arquivo NÃO conserta nada. Ele mostra os dois defeitos que a revisão de
`e0a813d` nomeou, lendo o pacote que a cadeia acabou de construir — e imprime a
prova de cada um com o registro na mão.

    UM DEFEITO QUE SÓ EXISTE NA PROSA DO RELATÓRIO É UMA OPINIÃO.
    UM DEFEITO QUE SE EXECUTA É UM DEFEITO.

DEFEITO 1 · A JANELA ERA HERDADA POR COINCIDÊNCIA DE CULTURA
    O índice era `{cultura: [janelas]}`. O registro de janela declara três
    eixos — cultura, alvo e região — e dois eram descartados no índice.

DEFEITO 2 · A DIREÇÃO ERA REPARTIDA ENTRE OS ALVOS DA MESMA ORAÇÃO
    Uma oração que nomeia três alvos e traz uma palavra de direção dava a
    mesma direção aos três.

Depois do conserto, este arquivo continua rodando: as duas listas saem VAZIAS,
e é assim que se sabe que o conserto está de pé.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import v21_necessidade as NE  # noqa: E402
import v21_normalizar as N  # noqa: E402

ING = os.path.join(ROOT, 'build', 'ITALY-REALITY-HANDOFF-V2.1', 'DESIGN-INGEST')


def _le(nome):
    return json.load(open(os.path.join(ING, nome), encoding='utf-8'))['RECORDS']


def defeito_1():
    """→ casos que carregam janela cujos eixos declarados não são os do caso."""
    janelas = {w['ID']: w for w in _le('CROP-WINDOWS.json')}
    fora = []
    for r in _le('OPPORTUNITIES.json'):
        for i in r.get('EVIDENCE_IDS') or []:
            w = janelas.get(i)
            if not w:
                continue
            razoes = []
            if r['CROP'] not in (w.get('CROP_IDS') or []):
                razoes.append('cultura')
            if (w.get('ISSUE_IDS') or []) and r['TARGET'] not in w['ISSUE_IDS']:
                razoes.append('alvo')
            if (w.get('REGION_IDS') or []) and r['GEOGRAPHY'] not in w['REGION_IDS']:
                razoes.append('regiao')
            if razoes:
                fora.append((r, w, razoes))
    return fora


def defeito_2():
    """→ pinos que AFIRMAM direção a partir de um trecho com vários alvos.

    ⚠️ A medição é sobre o que foi ATRIBUÍDO, não sobre o que o texto contém.
    `direcao()` continua reconhecendo «suspensao» dentro da oração corrida — o
    padrão está lá. O defeito era dar essa direção aos três alvos nomeados.

        O DEFEITO NUNCA FOI LER A PALAVRA. FOI DECIDIR DE QUEM ELA ERA.
    """
    fora = []
    for s in [x for x in _le('CURRENT-FIELD-SIGNALS.json') if x.get('CLIENT_SAFE')]:
        for p in NE.pares_observados(s):
            if p['NEED_DIRECTION'] in (NE.NEUTRAL_MENTION, NE.UNKNOWN):
                continue
            alvos = N.issues_no_texto(p['NEED_EXCERPT'])
            if len(alvos) > 1:
                fora.append((s, p['NEED_FIELD'], p['NEED_EXCERPT'], alvos,
                             '%s atribuido a %s' % (p['NEED_DIRECTION'],
                                                    p['ISSUE_ID'])))
    return fora


def main():
    d1 = defeito_1()
    print('=' * 74)
    print('DEFEITO 1 · JANELA HERDADA POR COINCIDENCIA DE CULTURA')
    print('=' * 74)
    print('ocorrencias: %d' % len(d1))
    for r, w, razoes in d1:
        print('  %s  %s x %s em %s' % (r['ID'], r['CROP'], r['TARGET'], r['GEOGRAPHY']))
        print('      carrega %s — que declara %s x %s em %s  (diverge em: %s)'
              % (w['ID'], w.get('CROP_IDS'), w.get('ISSUE_IDS'),
                 w.get('REGION_IDS'), ', '.join(razoes)))

    d2 = defeito_2()
    print()
    print('=' * 74)
    print('DEFEITO 2 · DIRECAO REPARTIDA ENTRE OS ALVOS DA MESMA ORACAO')
    print('=' * 74)
    print('ocorrencias: %d' % len(d2))
    for s, campo, o, alvos, est in d2:
        print('  %s · %s · %s, a partir de um trecho que nomeia %d alvos: %s'
              % (s['ID'], campo, est, len(alvos),
                 ', '.join(a.replace('ISSUE_', '') for a in alvos)))
        print('      «%s»' % o[:170])

    print()
    print('TOTAL DE OCORRENCIAS: %d' % (len(d1) + len(d2)))
    return 0 if not (d1 or d2) else 1


if __name__ == '__main__':
    sys.exit(main())
