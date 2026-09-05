#!/usr/bin/env python3
"""Mede o parser contra o GABARITO COMPLETO.

Diferencas em relacao a medicao anterior, que estava errada duas vezes:
1. NENHUM rotulo do gabarito e pulado. Antes eu pulava rotulo sem PDF — e como a
   geometria versionada dispensa o PDF, eu pulava justamente os rotulos onde o parser
   devolve zero. O recall subia sem o parser mudar nada.
2. Gabarito e parser sao comparados no MESMO espaco de nomes (o canonico). Antes eu
   comparava 'MOSCA DELLA FRUTTA' do gabarito com 'MOSCA' do parser e contava par
   certo como falso positivo.

E uma diferenca nova: o gabarito distingue par que o vocabulario SABE nomear de par
que ele NAO sabe (VOCAB_GAP). Publicar so o recall in-vocab esconderia a lacuna;
publicar so o total misturaria falha de estrutura com falha de dicionario. Saem os
dois.
"""
import collections
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from it_rotulo_gabarito import (EXCLUIDOS, GABARITO,           # noqa: E402
                                equivalentes)
from it_rotulo_parser import (PARSER_VERSION, alvos_em,        # noqa: E402
                              culturas_em, geometria_de, ler_geometria, parse)

REG = os.path.join(ROOT, 'data/samples/IT-RADAR-V21/productsRegulatory.json')


def _cat():
    P = json.load(open(REG, encoding='utf-8'))['PRODUCTS']
    return {p['REGISTRATION_ID']: p for p in P}


def medir(cache_dir):
    cat = _cat()
    tp, fp, fn = [], [], []
    gap_hit, gap_total = [], []
    no_pair_violado, amb_promovido, sup_rebaixado = [], [], []
    zero_com_alvo, zero_com_ambos = [], []
    por_rotulo = {}

    for rid, d in sorted(GABARITO.items()):
        p = cat.get(rid, {})
        saida = parse(os.path.join(cache_dir, '%s.pdf' % rid), rid,
                      produto=p.get('PRODUCT'), ai=p.get('ACTIVE_INGREDIENTS'),
                      cache_dir=cache_dir, categoria=p.get('REGULATORY_CATEGORY'))
        sup = {(x['CROP'], x['TARGET']) for x in saida
               if x['RELATION'] == 'SUPPORTED_PAIR'}
        amb = {(x['CROP'], x['TARGET']) for x in saida
               if x['RELATION'] == 'AMBIGUOUS_ROW'}

        ouro_v = {(c, a) for c, _, a in d['PAIRS'] if a}          # com termo canonico
        ouro_g = {(c, r) for c, r, a in d['PAIRS'] if not a}      # sem termo canonico

        # Um par de ouro conta como acerto se o parser devolveu QUALQUER nome
        # canonico equivalente ao que eu enumerei (ver ALVO_EQUIVALENTE).
        casados = set()
        for c, a in sorted(ouro_v):
            alt = {(c, x) for x in equivalentes(a)}
            hit = alt & sup
            if hit:
                tp.append((rid, c, a))
                casados |= hit
            else:
                fn.append((rid, c, a))
                if alt & amb:
                    sup_rebaixado.append((rid, c, a))
        for par in sorted(sup - casados):
            fp.append((rid,) + par)
        gap_total.extend((rid,) + g for g in sorted(ouro_g))

        # EXPECTED_NO_PAIR: ('CULTURA', 'ALVO' ou '*', motivo)
        for c, a, _por in d.get('EXPECTED_NO_PAIR', []):
            for (sc, sa) in sup:
                if sc == c and (a == '*' or sa == a):
                    no_pair_violado.append((rid, sc, sa))
        for c, _por in d.get('EXPECTED_AMBIGUOUS', []):
            for (sc, sa) in sup:
                if sc == c:
                    amb_promovido.append((rid, sc, sa))

        if not sup:
            bs = ler_geometria(geometria_de(rid, os.path.join(cache_dir, '%s.pdf' % rid),
                                            cache_dir)) or []
            txt = ' '.join(b['text'] for b in bs)
            if alvos_em(txt):
                zero_com_alvo.append(rid)
                if culturas_em(txt):
                    zero_com_ambos.append(rid)

        por_rotulo[rid] = {
            'PRODUCT': d['PRODUCT'], 'FAMILY': d['FAMILY'],
            'GOLD_PAIRS_IN_VOCAB': len(ouro_v), 'GOLD_PAIRS_VOCAB_GAP': len(ouro_g),
            'PARSER_SUPPORTED': len(sup), 'PARSER_AMBIGUOUS': len(amb),
            'TP': sum(1 for x in tp if x[0] == rid),
            'FP': sum(1 for x in fp if x[0] == rid),
            'FN': sum(1 for x in fn if x[0] == rid),
            'PARSER_SUPPORTED_UNMATCHED': sorted(sup - casados)[:8],
        }

    ntp, nfp, nfn = len(tp), len(fp), len(fn)
    prec = ntp / (ntp + nfp) if ntp + nfp else 0.0
    rec = ntp / (ntp + nfn) if ntp + nfn else 0.0
    f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
    total_ouro = ntp + nfn + len(gap_total)
    rec_total = ntp / total_ouro if total_ouro else 0.0

    return {
        'PARSER_VERSION': PARSER_VERSION,
        'GOLD': 'IT-ROTULOS-GOLD-COMPLETE-V1',
        'GOLD_LABELS': len(GABARITO),
        'GOLD_LABELS_EXCLUDED': len(EXCLUIDOS),
        'GOLD_PAIRS_TOTAL': total_ouro,
        'GOLD_PAIRS_IN_VOCAB': ntp + nfn,
        'GOLD_PAIRS_VOCAB_GAP': len(gap_total),
        'TP': ntp, 'FP': nfp, 'FN': nfn,
        'PRECISION': round(prec, 3), 'RECALL': round(rec, 3), 'F1': round(f1, 3),
        'RECALL_INCLUDING_VOCAB_GAP': round(rec_total, 3),
        'FALSE_POSITIVE_PAIR_COUNT': nfp,
        'FALSE_NEGATIVE_PAIR_COUNT': nfn,
        'EXPECTED_NO_PAIR_VIOLATIONS': len(no_pair_violado),
        'EXPECTED_NO_PAIR_VIOLATION_LIST': no_pair_violado,
        'AMBIGUOUS_PROMOTED_TO_PAIR': len(amb_promovido),
        'AMBIGUOUS_PROMOTED_LIST': amb_promovido,
        'SUPPORTED_PAIR_DROPPED_TO_AMBIGUOUS': len(sup_rebaixado),
        'ZERO_PAIR_WITH_TARGET_TEXT': len(zero_com_alvo),
        'ZERO_PAIR_WITH_TARGET_TEXT_LIST': zero_com_alvo,
        'ZERO_PAIR_WITH_CROP_AND_TARGET_TEXT': len(zero_com_ambos),
        'ZERO_PAIR_WITH_CROP_AND_TARGET_TEXT_LIST': zero_com_ambos,
        'BY_LABEL': por_rotulo,
        'FP_SAMPLE': fp[:60],
        'FN_SAMPLE': fn[:60],
        'BY_FAMILY': {
            fam: {
                'LABELS': sum(1 for r in por_rotulo.values() if r['FAMILY'] == fam),
                'TP': sum(r['TP'] for r in por_rotulo.values() if r['FAMILY'] == fam),
                'FP': sum(r['FP'] for r in por_rotulo.values() if r['FAMILY'] == fam),
                'FN': sum(r['FN'] for r in por_rotulo.values() if r['FAMILY'] == fam),
            }
            for fam in sorted({r['FAMILY'] for r in por_rotulo.values()})
        },
        'EXCLUDED': EXCLUIDOS,
    }


if __name__ == '__main__':
    cache = sys.argv[1] if len(sys.argv) > 1 else \
        os.path.join(ROOT, 'data/samples/IT-ROTULOS-V1/geometria')
    m = medir(cache)
    for k in ('PARSER_VERSION', 'GOLD_LABELS', 'GOLD_PAIRS_TOTAL',
              'GOLD_PAIRS_IN_VOCAB', 'GOLD_PAIRS_VOCAB_GAP', 'TP', 'FP', 'FN',
              'PRECISION', 'RECALL', 'F1', 'RECALL_INCLUDING_VOCAB_GAP',
              'EXPECTED_NO_PAIR_VIOLATIONS', 'AMBIGUOUS_PROMOTED_TO_PAIR',
              'SUPPORTED_PAIR_DROPPED_TO_AMBIGUOUS',
              'ZERO_PAIR_WITH_TARGET_TEXT', 'ZERO_PAIR_WITH_CROP_AND_TARGET_TEXT'):
        print('%-38s %s' % (k, m[k]))
    print()
    print('%-32s %5s %5s %5s %5s' % ('FAMILIA', 'ROT', 'TP', 'FP', 'FN'))
    for fam, v in m['BY_FAMILY'].items():
        print('%-32s %5d %5d %5d %5d' % (fam, v['LABELS'], v['TP'], v['FP'], v['FN']))
    if len(sys.argv) > 2:
        json.dump(m, open(sys.argv[2], 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=1)
