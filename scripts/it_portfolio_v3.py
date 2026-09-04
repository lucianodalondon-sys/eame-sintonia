#!/usr/bin/env python3
"""Reexecuta a camada de PORTFOLIO das oportunidades contra o conjunto publicado.

So roda depois do portao passar — e o portao passou. O que esta camada faz e uma
pergunta so: para a CULTURA x ALVO de cada oportunidade, existe agora um rotulo ADAMA
autorizado que a sustente?

O que ela NAO faz, e nao vai fazer:
  - nao transforma PORTFOLIO RELATION em LABEL AUTHORIZATION;
  - nao promove ausencia de par a "a ADAMA nao tem produto para X";
  - nao inventa oportunidade nova, nem reordena as existentes;
  - nao toca em limiar, nem cria um segundo motor.
Ela recalcula um campo e mostra o antes e o depois.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V21 = os.path.join(ROOT, 'data/samples/IT-RADAR-V21')
NOVO = os.path.join(ROOT, 'data/samples/IT-ROTULOS-V1/IT-ROTULOS-PARES-V3.json')
DEST = os.path.join(ROOT, 'data/samples/IT-ROTULOS-V1/IT-PORTFOLIO-DELTA-V3.json')

# CULTURA e ALVO da oportunidade, no vocabulario controlado. Escrito a mao: a
# oportunidade fala em portugues ('Videira', 'Milho grao') e o conjunto fala no
# canonico italiano. Traduzir por parecenca seria fuzzy match, que esta proibido.
CHAVE = {
    'IT-OPP-001': {'CROP': 'VITE', 'TARGETS': ['CICALINE'],
                   'POR_QUE': 'a oportunidade e o VETOR Scaphoideus titanus, que os '
                              'rotulos KLARTAN/MAVRIK nomeiam dentro de "cicaline '
                              '(Empoasca vitis, Scaphoideus titanus)". A flavescencia '
                              'dourada em si e fitoplasma e NAO tem produto: o par lido '
                              'e contra o vetor, e nao contra a doenca.'},
    'IT-OPP-002': {'CROP': 'MAIS', 'TARGETS': ['PIRALIDE', 'DIABROTICA'],
                   'POR_QUE': 'os dois alvos estao nomeados na propria oportunidade'},
    'IT-OPP-003': {'CROP': None, 'TARGETS': [],
                   'POR_QUE': 'transversal ao portfolio; nao tem cultura x alvo para '
                              'consultar'},
}


def main():
    ops = json.load(open(os.path.join(V21, 'opportunities.json'),
                         encoding='utf-8'))['OPPORTUNITIES']
    velho = json.load(open(os.path.join(V21, 'productRelationships.json'),
                           encoding='utf-8'))['PAIRS']
    novo = json.load(open(NOVO, encoding='utf-8'))['PAIRS']

    def achar(pares, crop, tgt):
        return sorted({(p['REGISTRATION_ID'], p.get('PRODUCT'))
                       for p in pares if p.get('CROP') == crop
                       and p.get('TARGET') == tgt})

    linhas, mudaram = [], 0
    for o in ops:
        k = CHAVE[o['ID']]
        antes, depois = {}, {}
        for t in k['TARGETS']:
            antes[t] = achar(velho, k['CROP'], t)
            depois[t] = achar(novo, k['CROP'], t)
        mudou = antes != depois
        mudaram += 1 if mudou else 0
        linhas.append({
            'OPPORTUNITY_ID': o['ID'], 'TITLE': o['TITLE'],
            'CASE_LABEL': o['CASE_LABEL'], 'FORBIDDEN_LABEL': o['FORBIDDEN_LABEL'],
            'CROP_CANONICAL': k['CROP'], 'TARGETS_CANONICAL': k['TARGETS'],
            'MAPEAMENTO_ESCRITO_A_MAO': k['POR_QUE'],
            'LABEL_AUTHORIZATION_BEFORE': {t: [f'{r} {p}' for r, p in v]
                                           for t, v in antes.items()},
            'LABEL_AUTHORIZATION_AFTER': {t: [f'{r} {p}' for r, p in v]
                                          for t, v in depois.items()},
            'CHANGED': mudou,
            'RANK_CHANGED': False,
            'THRESHOLD_CHANGED': False,
        })

    out = {
        'DATASET': 'IT-PORTFOLIO-DELTA-V3',
        'LAYER': 'NATIONAL PRODUCT AUTHORIZATION',
        'COUNTRY': 'IT',
        'SOURCE_ID': 'IT-T4-001-ETICHETTA',
        'CAPTURED_AT': '2026-09-04',
        'SOURCE': 'recalculo da camada de portfolio das oportunidades contra '
                  'IT-ROTULOS-PARES-V3, depois do portao de publicacao passar',
        'QUANTAS_OPORTUNIDADES_EXISTEM': len(ops),
        'RESSALVA_SOBRE_O_NUMERO': (
            'a missao fala em 43 oportunidades. O que esta versionado neste '
            'repositorio sao 3 registros em IT-RADAR-V21/opportunities.json. Nao '
            'inventei os outros 40 nem criei um motor para gera-los: recalculei os '
            'que existem e declaro o numero que encontrei.'),
        'OPPORTUNITIES_CHANGED': mudaram,
        'RANK_CHANGED': 0,
        'THRESHOLD_CHANGED': 0,
        'SECOND_ENGINE_CREATED': 'NO',
        'PORTFOLIO_RELATION_NEVER_BECAME_LABEL_AUTHORIZATION': True,
        'DISCREPANCIA_ENCONTRADA_E_NAO_CORRIGIDA': (
            'IT-OPP-002 traz ADAMA_PRODUCTS = [] no registro da oportunidade, mas o '
            'conjunto ANTIGO ja listava cinco rotulos para MAIS x PIRALIDE e MAIS x '
            'DIABROTICA (LAMDEX EXTRA, FORZA, NINJA, DURAVIS, ELTIRA), e o novo lista '
            'os mesmos cinco. Ou seja: o campo da oportunidade esta desatualizado '
            'desde antes desta rodada, e nao por causa dela. NAO corrigi o campo — '
            'mexer no registro da oportunidade e mexer no motor, o que esta missao '
            'proibe. Fica registrado para quem for dono dele.'),
        'ROWS': linhas,
    }
    json.dump(out, open(DEST, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('OPPORTUNITIES_EXISTING = %d' % len(ops))
    print('OPPORTUNITIES_CHANGED  = %d' % mudaram)
    for r in linhas:
        print('  %s  changed=%s' % (r['OPPORTUNITY_ID'], r['CHANGED']))
        for t in r['TARGETS_CANONICAL']:
            print('     %-12s antes=%d  depois=%d' % (
                t, len(r['LABEL_AUTHORIZATION_BEFORE'][t]),
                len(r['LABEL_AUTHORIZATION_AFTER'][t])))
            for x in r['LABEL_AUTHORIZATION_AFTER'][t][:6]:
                print('        %s' % x)
    return out


if __name__ == '__main__':
    main()
