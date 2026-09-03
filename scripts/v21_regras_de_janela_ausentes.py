#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OS CASOS SEM REGRA DE JANELA · a tabela antes da coleta, sempre.

    python3 scripts/v21_regras_de_janela_ausentes.py

`WINDOW_RULE_MISSING` não quer dizer «não sabemos quando agir». Quer dizer uma
coisa mais precisa e mais honesta:

    NENHUMA FONTE DO ACERVO DECLARA QUAL CONDIÇÃO DEFINE O MOMENTO DE INTERVIR
    NESTE PAR CULTURA × ALVO, NESTA REGIÃO.

A diferença importa para a coleta. `WINDOW_STATE_UNKNOWN` pede uma MEDIÇÃO — o
limiar já existe, falta o número de hoje. `WINDOW_RULE_MISSING` pede a REGRA —
o disciplinare, o boletim que escreve «intervenire quando…». São duas perguntas
diferentes, e uma fonte que responde a primeira não responde a segunda.

    A TABELA VEM ANTES DA COLETA. QUEM COLETA SEM A PERGUNTA ESCRITA VOLTA COM
    O QUE ENCONTROU, NÃO COM O QUE PRECISAVA.

A ordem é por DEFENSABILIDADE COMERCIAL, não por facilidade da fonte: primeiro
os que já têm produto do catálogo com rótulo no par e direção que manda agir.
"""
import json
import os
import sys
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ING = os.path.join(ROOT, 'build', 'ITALY-REALITY-HANDOFF-V2.1', 'DESIGN-INGEST')
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import v21_necessidade as NE  # noqa: E402

# A classe de fonte que responde à pergunta de cada caso. É escolha declarada:
# um boletim semanal diz o que está a acontecer; um disciplinare diz a regra.
CLASSE_DE_FONTE = {
    'DEFAULT': 'BOLETIM_FITOSSANITARIO_REGIONAL_CORRENTE',
    'ADMIN': 'DETERMINACAO_OU_DISCIPLINARE_REGIONAL',
    'NACIONAL': 'DISCIPLINARE_DE_PRODUCAO_INTEGRADA_NACIONAL_OU_REGIONAL',
}

# Alvos cujo momento é fixado por NORMA, não por observação: a pergunta é para o
# ato administrativo, e a resposta dele NUNCA vira janela agronômica sozinha.
ALVOS_DE_NORMA = ('ISSUE_SCAPHOIDEUS', 'ISSUE_DIABROTICA')


def _le(nome):
    with open(os.path.join(ING, nome), encoding='utf-8') as f:
        return json.load(f)['RECORDS']


def prioridade(r):
    """Ordem por defensabilidade comercial — nunca por facilidade da fonte."""
    porta_aberta = r.get('NEED_DIRECTION') in (NE.POSITIVE_PRESSURE, NE.MONITOR)
    return (0 if r.get('COMMERCIAL_PRIORITY') == 'SALES_READY' else 1,
            0 if porta_aberta else 1,
            -(r.get('COMMERCIAL_PRODUCT_COUNT') or 0),
            r['ID'])


def linha(r):
    alvo = r.get('TARGET') or ''
    if alvo in ALVOS_DE_NORMA:
        classe = CLASSE_DE_FONTE['ADMIN']
    elif str(r.get('GEOGRAPHY') or '').startswith('GEO_'):
        classe = CLASSE_DE_FONTE['NACIONAL']
    else:
        classe = CLASSE_DE_FONTE['DEFAULT']
    return {
        'CROP': r.get('CROP'),
        'TARGET': alvo,
        'REGION': r.get('GEOGRAPHY'),
        'OPPORTUNITY_ID': r['ID'],
        'WHY_COMMERCIAL': r.get('WHY_COMMERCIAL'),
        'COMMERCIAL_PRIORITY': r.get('COMMERCIAL_PRIORITY'),
        'NEED_DIRECTION': r.get('NEED_DIRECTION'),
        'PORTFOLIO_MATCH': r.get('MATCHED_COMMERCIAL_PRODUCT_NAMES') or [],
        'PRODUCT_LINK_STATE': r.get('PRODUCT_LINK_STATE'),
        'EXACT_WINDOW_RULE_MISSING':
            'qual condicao agronomica declarada define o momento de intervir '
            'contra %s em %s nesta regiao' % (alvo.replace('ISSUE_', '').lower(),
                                              (r.get('CROP') or '').replace('CROP_', '').lower()),
        'SOURCE_CLASS_NEEDED': classe,
        'PERGUNTA_EXATA': 'QUAL REGRA AGRONOMICA DEFINE QUANDO AGIR contra %s '
                          'em %s na %s?' % (alvo.replace('ISSUE_', '').lower(),
                                            (r.get('CROP') or '').replace('CROP_', '').lower(),
                                            (r.get('GEOGRAPHY') or '').replace('REGION_', '')),
    }


def main():
    regs = [r for r in _le('OPPORTUNITIES.json')
            if 'WINDOW_RULE_MISSING' in (r.get('WHAT_IS_MISSING') or [])]
    regs.sort(key=prioridade)
    linhas = [linha(r) for r in regs]
    print('WINDOW_RULE_MISSING: %d casos\n' % len(linhas))
    for i, l in enumerate(linhas, 1):
        print('%2d · %-10s %-16s %-22s %-16s %s' % (
            i, l['CROP'].replace('CROP_', ''), l['TARGET'].replace('ISSUE_', ''),
            str(l['REGION']).replace('REGION_', ''), l['COMMERCIAL_PRIORITY'],
            l['NEED_DIRECTION']))
        print('     produto : %s' % (l['PORTFOLIO_MATCH'] or 'nenhum'))
        print('     fonte   : %s' % l['SOURCE_CLASS_NEEDED'])
        print('     pergunta: %s' % l['PERGUNTA_EXATA'])
    fora = {
        'COLLECTION': 'V115-REGRAS-DE-JANELA-AUSENTES',
        'SOURCE': 'build/ITALY-REALITY-HANDOFF-V2.1/DESIGN-INGEST/OPPORTUNITIES.json',
        'CAPTURED_AT': date.today().isoformat(),
        'LAW': 'a tabela vem antes da coleta. WINDOW_RULE_MISSING pede a REGRA; '
               'WINDOW_STATE_UNKNOWN pede a MEDICAO. Sao perguntas diferentes.',
        'COUNT': len(linhas),
        'ROWS': linhas,
    }
    saida = os.path.join(ROOT, 'data', 'samples', 'AUDITORIA-SOMBRA',
                         'V115-REGRAS-DE-JANELA-AUSENTES.json')
    json.dump(fora, open(saida, 'w', encoding='utf-8'), ensure_ascii=False,
              indent=1)
    print('\ngravado em %s' % os.path.relpath(saida, ROOT))
    return 0


if __name__ == '__main__':
    sys.exit(main())
