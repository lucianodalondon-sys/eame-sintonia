#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FENOLOGIA CORRENTE — a camada que o pacote declarava como sua MAIOR lacuna.

    python3 scripts/pacote_fenologia.py .tmp/madrugada.json

O que mudou
------------
Até 02/09/2026 o pacote dizia, com todas as letras:

    «REAL_CURRENT_PHENOLOGY_SIGNALS = 0. Não há boletim de estádio fenológico lido para
     setembro de 2026. É a maior lacuna do pacote.»

A varredura noturna alcançou **6 regiões, todas GREEN**, e trouxe boletins com data de
26/08 a 01/09/2026. A lacuna fecha — mas fecha com as ressalvas que a fonte impõe, e elas
viajam no dado:

    ⚠️ CULTURA INFERIDA          alguns boletins não nomeiam a cultura; ela foi deduzida
                                 das avversità citadas. Isso vai marcado, item a item.
    ⚠️ REGIÃO != PROVÍNCIA       um boletim provincial não representa a região.
    ⚠️ FASE DECLARADA != MEDIDA  a fase fenológica é o que o boletim escreve, não uma
                                 medição nossa.
"""
import json
import os
import sys
from collections import Counter, OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from pacote_normalizar import grava, env, novo_id, DR  # noqa: E402


def camada_fenologia(caminho=None):
    caminho = caminho or (sys.argv[1] if len(sys.argv) > 1 else '.tmp/madrugada.json')
    if not os.path.exists(caminho):
        print('FALTA %s' % caminho); return 1
    d = json.load(open(caminho, encoding='utf-8'))

    fen, fontes_reg = [], []
    for reg in d.get('boletins', []):
        nome = str(reg.get('regiao') or '').split('(')[0].split('—')[0].strip()
        fontes_reg.append(OrderedDict([
            ('ID', novo_id('IT-SRC-BOLL')), ('REGION', nome),
            ('SOURCE', reg.get('fonte')), ('URL', reg.get('url_base')),
            ('ACCESS_STATUS', reg.get('alcancada')),
            ('ACCESS_EVIDENCE', str(reg.get('evidencia_de_acesso'))[:900]),
            ('BULLETINS_READ', len(reg.get('boletins') or [])),
            ('WHAT_IT_DOES_NOT_PROVE', reg.get('o_que_nao_prova') or []),
            ('PROVENANCE', 'REAL_SOURCE')]))
        for b in (reg.get('boletins') or []):
            culturas = b.get('culturas') or []
            inferida = any('INFERID' in str(c).upper() for c in culturas)
            fen.append(OrderedDict([
                ('ID', novo_id('IT-PHEN')),
                ('REGION', nome),
                ('BULLETIN_TITLE', b.get('titulo')),
                ('BULLETIN_NUMBER', b.get('numero')),
                ('PUBLICATION_DATE', b.get('data_publicacao')),
                ('CROPS', culturas),
                ('CROP_STATE', 'INFERRED_FROM_PESTS' if inferida else 'DECLARED_BY_SOURCE'),
                ('PHENOLOGICAL_STAGE_DECLARED', b.get('fase_fenologica_declarada')
                 or 'NAO SEI'),
                ('STAGE_LAW', 'e o que o boletim ESCREVE, nao uma medicao nossa'),
                ('PESTS_AND_DISEASES_CITED', b.get('avversita_citadas') or []),
                ('INTERVENTION_GUIDANCE', b.get('indicacao_de_intervencao') or 'NAO SEI'),
                ('CITATION', str(b.get('citacao_literal') or '')[:700]),
                ('URL', b.get('url')),
                ('GEOGRAPHY_LAW', 'boletim provincial NAO representa a regiao, e a regiao '
                                  'NAO representa o pais'),
                ('SOURCE_ID', 'IT-SRC-BOLL-REGIONAL'),
                ('PROVENANCE', 'REAL_SOURCE')]))

    fen.sort(key=lambda x: str(x['PUBLICATION_DATE']), reverse=True)
    datas = [x['PUBLICATION_DATE'] for x in fen if str(x['PUBLICATION_DATE'])[:2] == '20']
    grava('CROP-WINDOWS', 'current-phenology.json', OrderedDict(list(env(
        'CURRENT_PHENOLOGY',
        'varredura noturna de boletins fitossanitarios regionais, 2026-09-02',
        'REAL_SOURCE',
        'Esta camada FECHA a lacuna que o pacote declarava como a maior: '
        'REAL_CURRENT_PHENOLOGY_SIGNALS era 0.').items()) + [
        ('COUNT', len(fen)),
        ('REGIONS_REACHED', len(fontes_reg)),
        ('MOST_RECENT', max(datas) if datas else 'NAO SEI'),
        ('OLDEST', min(datas) if datas else 'NAO SEI'),
        ('BY_REGION', dict(Counter(x['REGION'] for x in fen))),
        ('BY_CROP_STATE', dict(Counter(x['CROP_STATE'] for x in fen))),
        ('WITH_STAGE_DECLARED', sum(1 for x in fen
                                    if x['PHENOLOGICAL_STAGE_DECLARED'] != 'NAO SEI')),
        ('WHAT_CHANGED', {
            'ANTES': 'REAL_CURRENT_PHENOLOGY_SIGNALS = 0; o boletim mais novo do acervo '
                     'era de 2026-08-18 (Modena) e o resto parava em maio',
            'AGORA': '%d boletins de %d regioes, o mais recente de %s'
                     % (len(fen), len(fontes_reg), max(datas) if datas else '?'),
            'O_QUE_NAO_MUDOU': 'continua sendo COBERTURA e nao censo. 6 regioes de 20, e '
                               'nenhuma delas fala pelo pais.'}),
        ('PHENOLOGY', fen)]))

    grava('CROP-WINDOWS', 'regional-bulletin-sources.json', OrderedDict(list(env(
        'REGIONAL_BULLETIN_SOURCES', 'varredura noturna 2026-09-02', 'REAL_SOURCE',
        'HTTP 200 NAO E FONTE VIVA — ACCESS_EVIDENCE guarda o que foi realmente lido.'
    ).items()) + [('COUNT', len(fontes_reg)), ('SOURCES', fontes_reg)]))

    # relatorios em texto
    dd = os.path.join(DR, 'CROP-WINDOWS')
    os.makedirs(dd, exist_ok=True)
    open(os.path.join(dd, 'ROUTE-TEST-ISMEA-ISTAT.md'), 'w', encoding='utf-8').write(
        str(d.get('rota_bloqueada') or ''))
    for p in d.get('pendencias', []):
        nome = 'PENDING-%s.md' % str(p['id']).lower()
        open(os.path.join(DR, 'CROP-WINDOWS', nome) if p['id'] == 'TRENTINO-ER'
             else os.path.join(DR, 'SCIENCE' if 'GIRE' in p['id'] else 'ARCHIVE', nome),
             'w', encoding='utf-8').write(str(p.get('texto') or ''))
    d2 = os.path.join(DR, 'CROP-WINDOWS')
    open(os.path.join(d2, 'OVERNIGHT-SYNTHESIS.md'), 'w', encoding='utf-8').write(
        str(d.get('sintese') or ''))
    print('  CROP-WINDOWS/ROUTE-TEST-ISMEA-ISTAT.md · OVERNIGHT-SYNTHESIS.md · 4 pendencias')
    return 0


if __name__ == '__main__':
    sys.exit(camada_fenologia() if 'fenologia' in __file__ else camada_mercado())
