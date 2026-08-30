#!/usr/bin/env python3
"""
MEDIÇÃO DA ROTA TERRITORIAL — e a comparação direta com a rota pessoal/social.

    python3 scripts/territorial_medir.py

DEDUPE GLOBAL, E POR QUE ELE PRECISA EXISTIR AQUI
---------------------------------------------------
O contrato manda não duplicar fonte entre runners. Mas uma fonte territorial serve mais de
um recorte por natureza: o RAIF cobre olivar E cereal; o BSV cobre vinha E cereal. Separar
por recorte faz a MESMA fonte ser consultada nos dois lotes.

A duplicata não está na fonte — está no ITEM, se ele for contado duas vezes. Por isso a
chave é a URL do item, e a rota de descoberta vira proveniência em vez de multiplicar
evidência. É a mesma lei da rodada anterior: rota de descoberta não multiplica evidência.

INDEPENDÊNCIA NÃO É "DUAS PÁGINAS DIFERENTES"
-----------------------------------------------
Duas páginas da mesma entidade não são duas fontes. E duas entidades do mesmo aparelho
regional podem não ser independentes entre si. Aqui a independência é declarada por
ENTIDADE e por TIPO, e cada par carrega o motivo — nunca um `YES` sem razão escrita.
"""
import json
import os
import sys
import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TER = os.path.join(ROOT, 'data', 'samples', 'TERRITORIAL')
PILOT = os.path.join(ROOT, 'data', 'samples', 'SENSOR-PILOT')
NAO_SEI = 'NOT_KNOWN'


def _ler(p):
    if not os.path.exists(p):
        return None
    with open(p, encoding='utf-8') as f:
        return json.load(f)


def medir():
    hoje = datetime.date.today()
    inv = _ler(os.path.join(TER, 'INVENTARIO-DE-FONTES.json'))
    # A MEDIDA VALE SOBRE O CORPO DO DOCUMENTO, NAO SOBRE A LISTAGEM.
    # A primeira passagem leu a listagem e capturou menu de site — "Videointerpretacion",
    # "Sectores de actividad". Medir sobre aquilo teria reprovado a rota territorial por
    # um defeito do meu extrator. DOCUMENTOS.json e a passagem que le o documento.
    fontes_itens = [_ler(os.path.join(TER, 'DOCUMENTOS.json')) or {'ITEMS': []}]
    itens, vistos, dups = [], set(), 0
    for d in fontes_itens:
        for it in d['ITEMS']:
            if it['SOURCE_URL'] in vistos:
                dups += 1
                continue
            vistos.add(it['SOURCE_URL'])
            itens.append(it)

    n = len(itens) or 1
    def cont(f):
        return sum(1 for i in itens if f(i))

    com_pais = cont(lambda i: i['COUNTRY_OF_FACT'] != NAO_SEI)
    com_reg = cont(lambda i: i['REGION_OF_FACT'] != NAO_SEI)
    com_crop = cont(lambda i: i['CROP'] != NAO_SEI)
    com_issue = cont(lambda i: i['ISSUE'] != NAO_SEI)
    chave = cont(lambda i: i['COUNTRY_OF_FACT'] != NAO_SEI
                 and i['CROP'] != NAO_SEI and i['ISSUE'] != NAO_SEI)

    def janela(dias):
        c = 0
        for i in itens:
            p = i['PUBLISHED_AT']
            if p == NAO_SEI:
                continue
            try:
                d = datetime.date.fromisoformat(p)
            except ValueError:
                continue
            if (hoje - d).days <= dias:
                c += 1
        return c

    tipos, base, por_fonte, por_tipo_fonte = {}, {}, {}, {}
    for i in itens:
        tipos[i['OBSERVATION_TYPE']] = tipos.get(i['OBSERVATION_TYPE'], 0) + 1
        base[i['LOCALITY_BASIS']] = base.get(i['LOCALITY_BASIS'], 0) + 1
        por_fonte[i['SOURCE_ENTITY_ID']] = por_fonte.get(i['SOURCE_ENTITY_ID'], 0) + 1
        por_tipo_fonte[i['SOURCE_TYPE']] = por_tipo_fonte.get(i['SOURCE_TYPE'], 0) + 1

    # ── SOBREPOSIÇÕES ────────────────────────────────────────────────────────────
    # Duas entidades DIFERENTES falando do mesmo país×cultura×problema. Independência
    # exige entidade diferente E tipo de fonte diferente — duas páginas do mesmo
    # aparelho regional não são duas testemunhas.
    chaves = {}
    for i in itens:
        if i['COUNTRY_OF_FACT'] == NAO_SEI or i['CROP'] == NAO_SEI or i['ISSUE'] == NAO_SEI:
            continue
        for c in (i['CROP'] if isinstance(i['CROP'], list) else [i['CROP']]):
            for s in (i['ISSUE'] if isinstance(i['ISSUE'], list) else [i['ISSUE']]):
                chaves.setdefault((i['COUNTRY_OF_FACT'], c, s), []).append(i)

    multi, independentes = [], []
    for (pais, crop, issue), grupo in sorted(chaves.items()):
        ents = {g['SOURCE_ENTITY_ID']: g for g in grupo}
        if len(ents) < 2:
            continue
        lista = list(ents.values())
        for a in range(len(lista)):
            for b in range(a + 1, len(lista)):
                A, B = lista[a], lista[b]
                mesmo_tipo = A['SOURCE_TYPE'] == B['SOURCE_TYPE']
                ind = 'NO' if mesmo_tipo else 'YES'
                razao = ('mesmo TIPO de fonte (%s): duas entidades do mesmo aparelho '
                         'não são duas camadas' % A['SOURCE_TYPE']) if mesmo_tipo else (
                    'entidades distintas E tipos distintos: %s vs %s'
                    % (A['SOURCE_TYPE'], B['SOURCE_TYPE']))
                par = {
                    'COUNTRY': pais, 'REGION_A': A['REGION_OF_FACT'],
                    'REGION_B': B['REGION_OF_FACT'], 'CROP': crop, 'ISSUE': issue,
                    'TIME_WINDOW': '%s .. %s' % (A['PUBLISHED_AT'], B['PUBLISHED_AT']),
                    'SOURCE_A': A['SOURCE_NAME'], 'SOURCE_A_TYPE': A['SOURCE_TYPE'],
                    'OBSERVATION_A': A['OBSERVATION_TEXT'][:150],
                    'URL_A': A['SOURCE_URL'],
                    'SOURCE_B': B['SOURCE_NAME'], 'SOURCE_B_TYPE': B['SOURCE_TYPE'],
                    'OBSERVATION_B': B['OBSERVATION_TEXT'][:150],
                    'URL_B': B['SOURCE_URL'],
                    'INDEPENDENT': ind, 'INDEPENDENCE_REASON': razao,
                }
                multi.append(par)
                if ind == 'YES':
                    independentes.append(par)

    fontes_com_item = {i['SOURCE_ENTITY_ID'] for i in itens}
    corpo = {
        'SOURCE_ID': 'TERRITORIAL/MEDICAO',
        'DATASET_OWNER': 'EARLY_SIGNAL_EAME', 'MISSION_ID': '16-ROTA-TERRITORIAL',
        'source': 'derivado dos itens coletados — nenhuma execução nova',
        'SOURCE_LOCATION': 'derivado', 'FACT_LOCATION': 'ver por item',
        'ORIGINAL_LANGUAGE': 'pt', 'EVIDENCE_CLASS': 'DERIVED_MEASUREMENT',
        'captured_at': hoje.isoformat(), 'CAPTURED_AT': hoje.isoformat(),
        'A_SOURCES_ATTEMPTED': inv['SOURCES_ATTEMPTED'],
        'A2_SOURCES_REACHABLE': inv['SOURCES_REACHABLE'],
        'B_SOURCES_PROVED': len(fontes_com_item),
        'C_SOURCES_BY_TYPE': por_tipo_fonte,
        'D_ITEMS_BY_SOURCE': dict(sorted(por_fonte.items(), key=lambda kv: -kv[1])),
        'E_ITEMS_LAST_30D': janela(30),
        'F_ITEMS_LAST_90D': janela(90),
        'G_ITEMS_LAST_180D': janela(180),
        'ITEMS_WITHOUT_DATE': cont(lambda i: i['PUBLISHED_AT'] == NAO_SEI),
        'H_ITEMS_WITH_COUNTRY': com_pais,
        'I_ITEMS_WITH_REGION': com_reg,
        'J_ITEMS_WITH_CROP': com_crop,
        'K_ITEMS_WITH_ISSUE': com_issue,
        'L_COMPLETE_KEY': chave,
        'TOTAL_ITEMS': len(itens),
        'DUPLICATES_INTERCEPTED': dups,
        'PCT': {
            'ITEMS_WITH_COUNTRY': round(100 * com_pais / n),
            'ITEMS_WITH_REGION': round(100 * com_reg / n),
            'ITEMS_WITH_CROP': round(100 * com_crop / n),
            'ITEMS_WITH_ISSUE': round(100 * com_issue / n),
            'COMPLETE_KEY_RATE': round(100 * chave / n),
        },
        'LOCALITY_BASIS': base,
        'OBSERVATION_TYPES': dict(sorted(tipos.items(), key=lambda kv: -kv[1])),
        # Agora o CORPO foi lido, entao a originalidade e derivavel: boletim publicado
        # pelo proprio servico com mandato e observacao propria da rede dele. Imprensa
        # tecnica relata observacao de terceiros e fica NOT_KNOWN.
        'M_ORIGINAL_TECHNICAL_OBSERVATIONS': cont(
            lambda i: i.get('ORIGINAL_OBSERVATION') == 'YES'),
        'M2_ORIGINALITY_NOT_KNOWN': cont(
            lambda i: i.get('ORIGINAL_OBSERVATION') != 'YES'),
        'N_FIELD_OBSERVATIONS': tipos.get('FIELD_OBSERVATION', 0),
        'O_MULTI_SOURCE_OVERLAPS': len(multi),
        'P_INDEPENDENT_LAYER_OVERLAPS': len(independentes),
        'OVERLAP_PAIRS': multi,
        'APIFY_RUNS': 0, 'TOTAL_COST_USD': 0,
        'ITEMS': itens,
    }
    with open(os.path.join(TER, 'MEDICAO.json'), 'w', encoding='utf-8') as f:
        json.dump(corpo, f, ensure_ascii=False, indent=1)
    return corpo


if __name__ == '__main__':
    d = medir()
    p = d['PCT']
    print('ITENS %d (dup interceptadas %d) · fontes provadas %d de %d tentadas'
          % (d['TOTAL_ITEMS'], d['DUPLICATES_INTERCEPTED'],
             d['B_SOURCES_PROVED'], d['A_SOURCES_ATTEMPTED']))
    print()
    print('%-28s %-12s %-12s %s' % ('INDICADOR', 'TERRITORIAL', 'PESSOAL', 'PISO'))
    for rot, k, ant, piso in (
            ('ITEMS_WITH_COUNTRY', 'ITEMS_WITH_COUNTRY', '26%', '70%'),
            ('ITEMS_WITH_CROP', 'ITEMS_WITH_CROP', '100%', '70%'),
            ('ITEMS_WITH_ISSUE', 'ITEMS_WITH_ISSUE', '100%', '70%'),
            ('COMPLETE_KEY_RATE', 'COMPLETE_KEY_RATE', '26%', '50%')):
        v = '%d%%' % p[k]
        print('%-28s %-12s %-12s %s' % (rot, v, ant, piso))
    print('%-28s %-12s %-12s' % ('ITEMS_WITH_REGION', '%d%%' % p['ITEMS_WITH_REGION'], 'n/a'))
    print()
    print('janela  30d=%d  90d=%d  180d=%d  (sem data: %d)'
          % (d['E_ITEMS_LAST_30D'], d['F_ITEMS_LAST_90D'], d['G_ITEMS_LAST_180D'],
             d['ITEMS_WITHOUT_DATE']))
    print('base da localidade:', d['LOCALITY_BASIS'])
    print('tipos de observacao:', d['OBSERVATION_TYPES'])
    print('sobreposicoes: multi=%d  independentes=%d'
          % (d['O_MULTI_SOURCE_OVERLAPS'], d['P_INDEPENDENT_LAYER_OVERLAPS']))
