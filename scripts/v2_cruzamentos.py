#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CALCULA OS CRUZAMENTOS AGORA POSSÍVEIS (§19) e as LIGAÇÕES.

    python3 scripts/v2_cruzamentos.py

⚠️ A REGRA QUE O §19 ESCREVE COM TODAS AS LETRAS
-------------------------------------------------
    «Do NOT manufacture an opportunity.»

Um cruzamento não é uma conclusão. É a constatação de que duas camadas falam
do mesmo par cultura × região — e nada mais. Quem decide se aquilo é
oportunidade é uma pessoa, olhando os IDs.

Por isso cada cruzamento devolve os IDs canônicos EXATOS de cada lado, e uma
frase do que ele NÃO prova.

⚠️ E O PORTÃO DO §4, APLICADO AQUI
-----------------------------------
Só `QA_PASS` e `QA_CORRECTED` entram no lado que SUSTENTA a afirmação. Um
registro `QA_UNREVIEWED` pode aparecer como CONTEXTO — marcado — mas nunca
como base. Sem isso, o portão do §4 vazaria pela porta dos fundos: o
cruzamento afirmaria o que o registro sozinho não pode afirmar.
"""
import json
import os
import re
import unicodedata
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PKG = os.path.join(ROOT, 'build', 'ITALY-REALITY-HANDOFF-V2')
ANT = os.path.join(ROOT, 'build', 'SINTONIA-ITALY-PILOT-REALITY-HANDOFF',
                   '01-DESIGN-READY')
SEGURO = ('QA_PASS', 'QA_CORRECTED')

CULTURA = {
    'VITE': ['vite', 'vigneto', 'uva', 'grape', 'vine', 'videira', 'vino'],
    'MAIS': ['mais', 'granoturco', 'maize', 'corn', 'milho'],
    'FRUMENTO': ['frumento', 'grano', 'wheat', 'durum', 'cereal', 'trigo'],
    'RISO': ['riso', 'risaia', 'rice', 'arroz'],
    'OLIVO': ['olivo', 'olive', 'oliveto', 'oliva'],
    'POMODORO': ['pomodoro', 'tomato', 'tomate'],
    'MELO': ['melo', 'mela', 'apple', 'pomacee', 'maca'],
    'BARBABIETOLA': ['barbabietola', 'bietola', 'beet'],
    'SOIA': ['soia', 'soybean', 'soja'],
    'ORZO': ['orzo', 'barley'],
}


def _n(t):
    t = ''.join(c for c in unicodedata.normalize('NFD', str(t or ''))
                if unicodedata.category(c) != 'Mn')
    return re.sub(r'[^a-z0-9 ]+', ' ', t.lower())


def cultura_de(*campos):
    t = _n(' '.join(str(c) for c in campos))
    for k, ws in CULTURA.items():
        if any(re.search(r'(?<![a-z])%s' % w, t) for w in ws):
            return k
    return None


def le(nome, chave='RECORDS'):
    p = os.path.join(PKG, nome)
    return json.load(open(p, encoding='utf-8')).get(chave, []) if os.path.exists(p) else []


def le_ant(rel, chave):
    p = os.path.join(ANT, rel.replace('/', os.sep))
    return json.load(open(p, encoding='utf-8')).get(chave, []) if os.path.exists(p) else []


def idx_por_cultura(regs, *campos):
    d = defaultdict(list)
    for r in regs:
        c = cultura_de(*[r.get(k) for k in campos])
        if c:
            d[c].append(r)
    return d


def main():
    campo = le('CURRENT-FIELD-SIGNALS.json')
    peso = le('CROP-ECONOMIC-WEIGHT.json')
    merc = le('MARKET-OBSERVATIONS.json')
    regu = le('REGULATORY-FUTURE.json')
    cat = le('COMMERCIAL-CATALOG.json')
    vozes = le('PUBLIC-VOICES.json')
    herb = le('HERBICIDE-CURRENT-CONTEXT.json')
    comp = le('COMPETITOR-PUBLIC-SIGNALS.json')

    rot = le_ant('LABEL-USE/label-use-pairs.json', 'PAIRS')
    res = le_ant('SCIENCE/herbicide-resistance.json', 'RESISTANCES')
    sci = le_ant('SCIENCE/scientific-records.json', 'RECORDS')
    conv = le_ant('CONVERGENCE/convergence.json', 'CONVERGENCE')

    ic = {
        'campo': idx_por_cultura(campo, 'crop', 'o_que'),
        'peso': idx_por_cultura(peso, 'crop', 'o_que'),
        'merc': idx_por_cultura(merc, 'crop', 'o_que'),
        'vozes': idx_por_cultura(vozes, 'crop', 'o_que'),
        'herb': idx_por_cultura(herb, 'crop', 'o_que'),
        'comp': idx_por_cultura(comp, 'crop', 'o_que'),
    }
    rot_c = defaultdict(list)
    for p in rot:
        c = cultura_de(p.get('CROP'))
        if c:
            rot_c[c].append(p)
    res_c = defaultdict(list)
    for p in res:
        c = cultura_de(p.get('CROP_DECLARED'), p.get('SPECIES_IT'))
        if c:
            res_c[c].append(p)
    sci_c = defaultdict(list)
    for p in sci:
        c = cultura_de(p.get('CROP'), p.get('TITLE'))
        if c:
            sci_c[c].append(p)

    def ids(lst, n=8):
        return [x.get('CANONICAL_RECORD_ID') or x.get('ID') for x in lst[:n]]

    def seguros(lst):
        return [x for x in lst if x.get('QA_STATUS') in SEGURO]

    cruz = []

    # 1 · sinal de campo × peso econômico × relação de produto verificada
    for c in sorted(set(ic['campo']) & set(ic['peso'])):
        base = seguros(ic['campo'][c])
        if not base or not rot_c.get(c):
            continue
        cruz.append({
            'CROSSING': 'FIELD_SIGNAL × CROP_ECONOMIC_WEIGHT × VERIFIED_LABEL_USE',
            'CROP': c,
            'FIELD_SIGNAL_IDS': ids(base), 'FIELD_SIGNAL_QA': [x['QA_STATUS'] for x in base[:8]],
            'ECONOMIC_WEIGHT_IDS': ids(ic['peso'][c]),
            'LABEL_USE_IDS': ids(rot_c[c], 6),
            'O_QUE_PERMITE_PERGUNTAR':
                'este sinal de campo esta numa cultura cujo peso de area agora se '
                'conhece, e o rotulo da ADAMA tem uso lido para ela',
            'O_QUE_NAO_PROVA':
                'nao e oportunidade. Nao prova demanda, nao prova que o produto '
                'resolve o problema, e nao diz que a regiao do sinal e a regiao do peso.',
        })

    # 2 · futuro regulatório × substância × produto de catálogo
    for r in seguros(regu):
        sub = _n(r.get('crop') or r.get('o_que'))
        casa = [p for p in cat
                if any(w and w in _n(json.dumps(p, ensure_ascii=False))
                       for w in sub.split()[:3] if len(w) > 5)]
        if casa:
            cruz.append({
                'CROSSING': 'REGULATORY_FUTURE × ACTIVE_INGREDIENT × CATALOG_PRODUCT',
                'REGULATORY_ID': r['CANONICAL_RECORD_ID'], 'REGULATORY_QA': r['QA_STATUS'],
                'CATALOG_IDS': ids(casa, 6),
                'O_QUE_PERMITE_PERGUNTAR':
                    'um sinal regulatorio europeu toca uma substancia que aparece no '
                    'catalogo comercial',
                'O_QUE_NAO_PROVA':
                    'PRORROGACAO NAO E RENOVACAO e rascunho nao e decisao. E titular '
                    'de registro nao e vendedor: o vinculo comercial continua DESCONHECIDO.',
            })

    # 3 · voz pública × cultura/problema × ciência × resistência
    for c in sorted(ic['vozes']):
        base = seguros(ic['vozes'][c])
        if not base:
            continue
        cruz.append({
            'CROSSING': 'PUBLIC_VOICE × CROP_ISSUE × SCIENCE × RESISTANCE',
            'CROP': c,
            'VOICE_IDS': ids(base), 'VOICE_QA': [x['QA_STATUS'] for x in base[:8]],
            'SCIENCE_IDS': ids(sci_c.get(c, []), 6),
            'RESISTANCE_IDS': ids(res_c.get(c, []), 6),
            'O_QUE_PERMITE_PERGUNTAR':
                'gente com nome e cargo falou desta cultura, e ha ciencia e '
                'resistencia registradas sobre ela',
            'O_QUE_NAO_PROVA':
                'VOZ NAO E INCIDENCIA. Uma declaracao nao mede quanto do campo esta '
                'afetado, e quatro pessoas numa mesma materia nao sao quatro fontes '
                'independentes.',
        })

    # 4 · fase corrente do herbicida × uso de rótulo × resistência
    for c in sorted(ic['herb']):
        base = seguros(ic['herb'][c])
        if not base:
            continue
        cruz.append({
            'CROSSING': 'CURRENT_HERBICIDE_PHASE × VERIFIED_LABEL_USE × RESISTANCE',
            'CROP': c,
            'HERBICIDE_CONTEXT_IDS': ids(base),
            'LABEL_USE_IDS': ids([p for p in rot_c.get(c, [])
                                  if p.get('TARGET_KIND') == 'PLANTA_INFESTANTE'], 8),
            'RESISTANCE_IDS': ids(res_c.get(c, []), 6),
            'O_QUE_PERMITE_PERGUNTAR':
                'a fase de diserbo declarada por boletim datado encontra o uso de '
                'rotulo lido e a resistencia confirmada pelo GIRE',
            'O_QUE_NAO_PROVA':
                'JANELA SAZONAL NAO E SURTO. E a fase corrente medida na '
                'Emilia-Romagna NAO se generaliza para a Italia — o escopo e do '
                'boletim que a declarou.',
        })

    # 5 · sinal de concorrente × janela futura × portfólio
    for c in sorted(ic['comp']):
        base = seguros(ic['comp'][c])
        if not base:
            continue
        cruz.append({
            'CROSSING': 'COMPETITOR_SIGNAL × CROP_WINDOW × ADAMA_PORTFOLIO',
            'CROP': c,
            'COMPETITOR_IDS': ids(base),
            'CONVERGENCE_IDS': ids([x for x in conv if cultura_de(x.get('CROP')) == c], 6),
            'LABEL_USE_IDS': ids(rot_c.get(c, []), 6),
            'O_QUE_PERMITE_PERGUNTAR':
                'um concorrente comunicou publicamente sobre uma cultura em que a '
                'ADAMA tem posicao de rotulo lida',
            'O_QUE_NAO_PROVA':
                'COMUNICACAO NAO E PARTICIPACAO DE MERCADO, e nao ha inferencia de '
                'impacto comercial.',
        })

    # 6 · contexto de mercado × peso da região × sinal de campo
    for c in sorted(set(ic['merc']) & set(ic['peso']) & set(ic['campo'])):
        base = seguros(ic['merc'][c])
        if not base:
            continue
        cruz.append({
            'CROSSING': 'MARKET_CONTEXT × REGION_CROP_WEIGHT × CURRENT_FIELD_SIGNAL',
            'CROP': c,
            'MARKET_IDS': ids(base), 'MARKET_QA': [x['QA_STATUS'] for x in base[:8]],
            'ECONOMIC_WEIGHT_IDS': ids(ic['peso'][c]),
            'FIELD_SIGNAL_IDS': ids(seguros(ic['campo'][c])),
            'O_QUE_PERMITE_PERGUNTAR':
                'ha preco corrente, peso de area e sinal de campo para a mesma cultura',
            'O_QUE_NAO_PROVA':
                'preco alto de cultura nao e lucro do produtor, e nem preco nem area '
                'dizem se o problema fitossanitario esta ocorrendo.',
        })

    saida = {
        'LAYER': 'TOP_CROSSINGS', 'COUNTRY': 'IT', 'HANDOFF': 'V2',
        'BUILT_AT': '2026-09-02',
        'LAW': 'DO NOT MANUFACTURE AN OPPORTUNITY. Um cruzamento e a constatacao de '
               'que duas camadas falam do mesmo par cultura x regiao. Quem decide se '
               'e oportunidade e uma pessoa, olhando os IDs.',
        'QA_GATE_APLICADO':
            'so QA_PASS e QA_CORRECTED entram no lado que SUSTENTA. Sem isso o '
            'portao do §4 vazaria pela porta dos fundos.',
        'COUNT': len(cruz),
        'BY_TYPE': {k: sum(1 for x in cruz if x['CROSSING'] == k)
                    for k in sorted({x['CROSSING'] for x in cruz})},
        'CROSSINGS': cruz,
    }
    json.dump(saida, open(os.path.join(PKG, 'TOP-CROSSINGS.json'), 'w',
                          encoding='utf-8'), ensure_ascii=False, indent=1)

    # ── RELATIONSHIPS: só IDs, como a casa faz ────────────────────────────────
    rel = []
    for c in cruz:
        rel.append({k: v for k, v in c.items()
                    if k.endswith('_IDS') or k in ('CROSSING', 'CROP')})
    json.dump({
        'LAYER': 'RELATIONSHIPS', 'COUNTRY': 'IT', 'HANDOFF': 'V2',
        'BUILT_AT': '2026-09-02', 'COUNT': len(rel),
        'HOW_TO_RESOLVE': 'todo ID resolve em CANONICAL-INTELLIGENCE.json ou, quando '
                          'comeca com IT-PRD/IT-SCI/IT-RES/IT-CONV, no pacote '
                          'anterior preservado em PREVIOUS-HANDOFF/.',
        'LAW': 'as relacoes carregam SO IDs. Copiar o objeto para dentro da relacao '
               'cria dois donos do mesmo fato.',
        'LINKS': rel,
    }, open(os.path.join(PKG, 'RELATIONSHIPS.json'), 'w', encoding='utf-8'),
        ensure_ascii=False, indent=1)

    print('cruzamentos: %d' % len(cruz))
    for k, v in saida['BY_TYPE'].items():
        print('  %-62s %d' % (k, v))
    print('relacoes: %d' % len(rel))


if __name__ == '__main__':
    main()
