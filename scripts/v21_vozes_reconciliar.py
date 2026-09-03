#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
§13 · RECONCILIA O QA DAS VOZES — sem promover ninguém automaticamente.

    python3 scripts/v21_vozes_reconciliar.py

O QUE A MISSÃO APONTOU
-----------------------
O V2 mostrava `PUBLIC_VOICES = 21` com apenas **2 client-safe**, enquanto a
conferência tinha relatado que **5 dos 8** amostrados sobreviveram.

A DIFERENÇA TEM CAUSA, E ELA NÃO É UM BUG
------------------------------------------
O bloco de vozes tinha **uma queda sem dono**: o conferente derrubou 3 e
numerou 2. A regra do V2 é dura de propósito:

    QUANDO SOBRA UMA QUEDA SEM DONO, NINGUÉM NAQUELE BLOCO GANHA QA_PASS.

Com uma queda anônima solta, qualquer um dos cinco não-listados podia ser ela.
Chamar de aprovado um registro que talvez seja o que caiu é exatamente o erro
que o portão existe para impedir.

O QUE MUDOU AGORA
------------------
A missão V2 **identificou** aquele órfão por conteúdo — era o índice 4, a frase
que o jornal montou em `<blockquote>` e que não é fala do rizicultor — e o
**rejeitou**. Identificado o dono, o bloco deixa de ter queda anônima.

    ISTO NÃO É PROMOÇÃO AUTOMÁTICA. É a condição da regra deixando de valer,
    porque a incerteza que a motivava foi resolvida com evidência.

Os cinco que ganham `QA_PASS` são exatamente os que a conferência disse ter
sobrevivido: índices 0, 3, 5, 6 e 7.
"""
import json
import os
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ING = os.path.join(ROOT, 'build', 'ITALY-REALITY-HANDOFF-V2.1', 'DESIGN-INGEST')
V2 = os.path.join(ROOT, 'build', 'ITALY-REALITY-HANDOFF-V2')
QA = os.path.join(ROOT, 'data', 'samples', 'IT-V2', 'IT-V2-QA-ATRIBUIDO.json')

# ⚠️ Só o bloco de vozes tinha queda sem dono, e ela foi resolvida.
# Nenhum outro bloco muda: onde a incerteza continua, o QA continua.
BLOCO = 'vozes'
ORFAO_RESOLVIDO = 4
SOBREVIVENTES = [0, 3, 5, 6, 7]


def main():
    qa = json.load(open(QA, encoding='utf-8'))
    b = [x for x in qa['BLOCOS'] if x['BLOCO'] == BLOCO][0]
    caidos = set(b['INDICES_CAIDOS']) | {ORFAO_RESOLVIDO}
    amostra = min(b['TETO_DA_AMOSTRA'], b['VERIFICADOS'])
    esperados = [i for i in range(amostra) if i not in caidos]
    if sorted(esperados) != sorted(SOBREVIVENTES):
        print('PARADO: a lista de sobreviventes calculada (%s) nao bate com a '
              'declarada (%s). Nao se promove ninguem no escuro.'
              % (esperados, SOBREVIVENTES))
        return 1

    # a canônica do V2 é a fonte dos índices
    can = json.load(open(os.path.join(V2, 'CANONICAL-INTELLIGENCE.json'),
                         encoding='utf-8'))['RECORDS']
    alvo = {r['CANONICAL_RECORD_ID']: r for r in can
            if r.get('BLOCO') == BLOCO and r.get('INDICE_NO_BLOCO') in SOBREVIVENTES}

    p = os.path.join(ING, 'PUBLIC-VOICES.json')
    d = json.load(open(p, encoding='utf-8'))
    mudados = []
    for r in d['RECORDS']:
        if r['ID'] in alvo and r.get('QA_STATUS') == 'QA_UNREVIEWED':
            r['QA_STATUS'] = 'QA_PASS'
            r['CLIENT_SAFE'] = True
            r['QA_RECONCILIATION'] = (
                'reconciliado no V2.1. O bloco tinha UMA queda sem dono, e por isso '
                'nenhum nao-listado podia ser aprovado. A missao V2 identificou esse '
                'orfao por conteudo (indice 4 — a frase em <blockquote> que nao e '
                'fala do rizicultor) e o rejeitou. Identificado o dono, a condicao da '
                'regra deixou de valer. NAO e promocao automatica: e a incerteza '
                'sendo resolvida com evidencia.')
            mudados.append(r['ID'])

    d['COUNT_CLIENT_SAFE'] = sum(1 for x in d['RECORDS'] if x.get('CLIENT_SAFE'))
    d['BY_QA'] = dict(Counter(x.get('QA_STATUS') for x in d['RECORDS']))
    d['QA_RECONCILIATION_13'] = {
        'VOICE_CONFERENCE_SAMPLED': b['VERIFICADOS'],
        'VOICE_QA_PASS': sum(1 for x in d['RECORDS'] if x.get('QA_STATUS') == 'QA_PASS'),
        'VOICE_QA_CORRECTED': sum(1 for x in d['RECORDS']
                                  if x.get('QA_STATUS') == 'QA_CORRECTED'),
        'VOICE_QA_REJECTED': 1,
        'VOICE_QA_UNREVIEWED': sum(1 for x in d['RECORDS']
                                   if x.get('QA_STATUS') == 'QA_UNREVIEWED'),
        'DIFERENCA_EXPLICADA':
            'a conferencia relatou 5 de 8 sobreviventes. O V2 mostrava 2 client-safe '
            'porque o bloco tinha UMA queda sem dono identificado, e a regra proibe '
            'QA_PASS nesse caso. O orfao foi identificado e rejeitado; os 5 '
            'sobreviventes (indices 0, 3, 5, 6, 7) recebem QA_PASS.',
        'REJEICAO_MANTIDA':
            'a atribuicao de fala errada continua REJEITADA. A frase esta dentro de '
            '<blockquote> sem aspas: e destaque editorial do jornal, nao fala do '
            'rizicultor. Reescrever campo nao devolve frase a boca de ninguem.',
        'IDS_RECONCILIADOS': mudados,
    }
    json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    r = d['QA_RECONCILIATION_13']
    print('VOICE CONFERENCE SAMPLED = %d' % r['VOICE_CONFERENCE_SAMPLED'])
    print('VOICE QA_PASS            = %d' % r['VOICE_QA_PASS'])
    print('VOICE QA_CORRECTED       = %d' % r['VOICE_QA_CORRECTED'])
    print('VOICE QA_REJECTED        = %d' % r['VOICE_QA_REJECTED'])
    print('VOICE QA_UNREVIEWED      = %d' % r['VOICE_QA_UNREVIEWED'])
    print()
    print('reconciliados: %d · total client-safe no arquivo: %d de %d'
          % (len(mudados), d['COUNT_CLIENT_SAFE'], d['COUNT_TOTAL']))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
