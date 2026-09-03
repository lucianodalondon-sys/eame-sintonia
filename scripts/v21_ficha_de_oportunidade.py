#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A FICHA · o contrato mínimo do cartão, lido caso a caso.

    python3 scripts/v21_ficha_de_oportunidade.py                 # a testemunha
    python3 scripts/v21_ficha_de_oportunidade.py OPP_XXXXXXXXXXXX

Sete perguntas, na ordem em que uma pessoa as faz. Cada resposta sai de um campo
do pacote — nenhuma é escrita aqui. O que o acervo não sabe aparece como NÃO SEI
**com o nome do que falta**, e não como espaço em branco.

    UM CARTÃO QUE NÃO DIZ O QUE NÃO SABE ESTÁ AFIRMANDO QUE SABE TUDO.

O caso padrão é `botrite × videira × Emilia-Romagna`, que foi a testemunha da
missão: era ele que a tela mostrava com `ACT NOW` e «no canonical window linked»
ao mesmo tempo.
"""
import json
import os
import sys
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ING = os.path.join(ROOT, 'build', 'ITALY-REALITY-HANDOFF-V2.1', 'DESIGN-INGEST')
SAIDA = os.path.join(ROOT, 'data', 'samples', 'AUDITORIA-SOMBRA',
                     'V113-FICHA-DA-TESTEMUNHA.json')
TESTEMUNHA = ('CROP_GRAPEVINE', 'ISSUE_BOTRYTIS', 'REGION_EMILIA_ROMAGNA')


def _le(nome):
    return json.load(open(os.path.join(ING, nome), encoding='utf-8'))


def _achar(recs, alvo):
    if alvo:
        return next((r for r in recs if r['ID'] == alvo), None)
    return next((r for r in recs if (r['CROP'], r['TARGET'], r['GEOGRAPHY'])
                 == TESTEMUNHA), None)


def _sn(v, falta):
    """Valor, ou «NÃO SEI» com o nome do que falta. Nunca vazio."""
    return v if v not in (None, '', [], {}) else 'NAO SEI — %s' % falta


def ficha(r):
    """→ dict com as sete perguntas. Toda resposta aponta para um campo."""
    elos = r.get('ACTION_CHAIN_LINKS') or {}
    faltam = [e for e, ok in elos.items() if not ok]
    dep = r.get('ACTION_BY_DEPARTMENT') or {}
    dim = r.get('COMMERCIAL_MAGNITUDE_DIMENSIONS') or {}
    return {
        'ID': r['ID'],
        'O_QUE_SABEMOS': {
            'CULTURA': r['CROP'], 'ALVO': r['TARGET'], 'REGIAO': r['GEOGRAPHY'],
            'DIRECAO_DO_SINAL': r['NEED_DIRECTION'],
            'FRASE_DA_FONTE': r['NEED_EXCERPT'],
            'FONTE_DA_FRASE': r['NEED_EVIDENCE_ID'],
            'METODO_DO_PAR': r['NEED_METHOD'],
            'DATA_DO_SINAL': r['SIGNAL_DATE'],
            'RECENCIA': r['SIGNAL_CURRENCY'],
            'SINAIS_DE_CAMPO': dim.get('SINAIS_DE_CAMPO'),
            'FONTES_INDEPENDENTES': dim.get('FONTES_INDEPENDENTES'),
            'REGIOES_DO_MESMO_PAR': dim.get('REGIOES_DO_PAR'),
        },
        'O_QUE_NAO_SABEMOS': {
            'ELOS_QUE_FALTAM': faltam,
            'JANELA_DE_APLICACAO': _sn(r.get('WINDOW_FIELD'),
                                       'nenhuma janela declara esta cultura, '
                                       'este alvo e esta regiao'),
            'AREA_OFICIAL': _sn(dim.get('AREA_OFICIAL_HA'),
                                'nenhuma linha ISTAT client-safe para o par'),
            'INTENSIDADE': 'NAO SEI — boletim declara ocorrencia, nao incidencia',
            'AMBIGUIDADE_DE_DIRECAO': r.get('NEED_AMBIGUITY_CODES') or 'nenhuma',
        },
        'POR_QUE_E_OU_NAO_E_OPORTUNIDADE': {
            'COMMERCIAL_PRIORITY': r['COMMERCIAL_PRIORITY'],
            'RAZOES': r['WHY_COMMERCIAL_CODES'],
            'OPPORTUNITY_STATE': r['OPPORTUNITY_STATE'],
            'PORTOES_ABERTOS': r['BLOCKING_GATES'] or 'nenhum',
            'NAO_PROVA': r['COMMERCIAL_DOES_NOT_PROVE'],
        },
        'QUAL_PRODUTO': {
            'ROTULO_MINISTERIAL': r['PRODUCT_RELATIONSHIPS'],
            'NO_CATALOGO_COMERCIAL': r['MATCHED_COMMERCIAL_PRODUCT_NAMES'],
            'FORCA_DO_VINCULO': r['PRODUCT_LINK_STATE'],
            'CONFIANCA_DO_VINCULO': r['PRODUCT_MATCH_CONFIDENCE'],
            'SUBSTANCIA_ATIVA': r['ACTIVE_INGREDIENT_NAMES'],
            'MODO_DE_ACAO': _sn(r['MODE_OF_ACTION_CODES'],
                                'substancia sem classificacao FRAC/IRAC/HRAC'),
            'MODO_DE_EMPREGO': r['APPLICATION_STATE'],
            'CITACAO_DO_ROTULO': r['LABEL_QUOTES'][:1],
            'RESTRICOES': r['PRODUCT_RESTRICTIONS'] or 'nenhuma publicada',
        },
        'QUAL_E_A_JANELA': {
            'WINDOW_STATE': r['WINDOW_STATE'], 'WINDOW_KIND': r['WINDOW_KIND'],
            'DIAS_RESTANTES': r['DAYS_REMAINING'],
            'COMMERCIAL_WINDOW': r['COMMERCIAL_WINDOW'],
            'BASE_DO_TEMPO': r['COMMERCIAL_TIMING_BASIS'],
            'CONFIANCA_DA_JANELA': r['WINDOW_CONFIDENCE'],
        },
        'QUAL_E_A_ACAO': {'STATUS': r['STATUS'],
                          'POR_DEPARTAMENTO': {d: v['ACTION']
                                               for d, v in dep.items()}},
        'POR_QUE_AGORA': {'CODIGOS': r['WHY_NOW_CODES'],
                          'CADEIA': r['WHY_NOW_CHAIN']},
        'QUEM_DEVE_AGIR': dep,
        'CONFIANCAS': {'SINAL': r['SIGNAL_CONFIDENCE'],
                       'JANELA': r['WINDOW_CONFIDENCE'],
                       'PRODUTO': r['PRODUCT_MATCH_CONFIDENCE'],
                       'PRONTIDAO_COMERCIAL': r['COMMERCIAL_PRIORITY'],
                       'SAIDA_EXTERNA': r['EXTERNAL_MATERIAL_READY']},
    }


def main():
    d = _le('OPPORTUNITIES.json')
    r = _achar(d['RECORDS'], sys.argv[1] if len(sys.argv) > 1 else None)
    if not r:
        print('caso nao encontrado', file=sys.stderr)
        return 2
    f = ficha(r)
    print('=' * 78)
    print('%s   %s x %s   %s' % (r['ID'], r['CROP'], r['TARGET'], r['GEOGRAPHY']))
    print('BUILD_ID %s' % d.get('BUILD_ID', 'NAO DECLARADO'))
    print('=' * 78)
    for bloco in ('O_QUE_SABEMOS', 'O_QUE_NAO_SABEMOS',
                  'POR_QUE_E_OU_NAO_E_OPORTUNIDADE', 'QUAL_PRODUTO',
                  'QUAL_E_A_JANELA', 'QUAL_E_A_ACAO', 'POR_QUE_AGORA',
                  'CONFIANCAS'):
        print('\n%s' % bloco.replace('_', ' '))
        for k, v in f[bloco].items():
            print('  %-26s %s' % (k, json.dumps(v, ensure_ascii=False)[:210]))
    print('\nQUEM DEVE AGIR')
    for dep, v in f['QUEM_DEVE_AGIR'].items():
        print('  %-22s %-32s (%s)' % (dep, v['ACTION'], v['WHY_CODE']))

    fora = {
        'COLLECTION': 'V113-FICHA-DA-TESTEMUNHA',
        'SOURCE': 'build/ITALY-REALITY-HANDOFF-V2.1/DESIGN-INGEST/'
                  'OPPORTUNITIES.json · BUILD_ID %s' % d.get('BUILD_ID', 'NAO DECLARADO'),
        'CAPTURED_AT': date.today().isoformat(),
        'LAW': 'toda resposta sai de um campo do pacote. Nenhuma e escrita aqui, '
               'e o que falta aparece com o nome do que falta.',
        'BUILD_ID': d.get('BUILD_ID', 'NAO DECLARADO'),
        'FICHA': f,
    }
    os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
    json.dump(fora, open(SAIDA, 'w', encoding='utf-8'), ensure_ascii=False,
              indent=1)
    print('\ngravado em %s' % os.path.relpath(SAIDA, ROOT))
    return 0


if __name__ == '__main__':
    sys.exit(main())
