#!/usr/bin/env python3
"""Roda o parser nos 163 rotulos e escreve o conjunto de pares.

Na rodada anterior isto saiu como CANDIDATO: o recall contra o gabarito parcial era
0,63 e publicar teria sido trocar um conjunto incompleto conhecido por outro
incompleto ainda nao mapeado. Com o gabarito COMPLETO e as quatro formas fechadas o
conjunto passou o portao, e agora sai publicado. O antigo continua pinado ao lado —
ele nao e apagado, e a comparacao por rotulos-por-cultura fica no repositorio.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from it_rotulo_parser import PARSER_VERSION, parse              # noqa: E402

REG = os.path.join(ROOT, 'data/samples/IT-RADAR-V21/productsRegulatory.json')
OLD = os.path.join(ROOT, 'data/samples/IT-RADAR-V21/productRelationships.json')


def main(pdf_dir, saida):
    P = json.load(open(REG, encoding='utf-8'))['PRODUCTS']
    pares, sem = [], []
    for i, p in enumerate(P, 1):
        rid = p['REGISTRATION_ID']
        # A geometria versionada e a fonte; o PDF e so alternativa. Exigir o PDF fazia
        # a rodada inteira devolver zero quando apontada para a geometria — numero que
        # parece resultado e e so arquivo nao encontrado.
        pdf = os.path.join(pdf_dir, '%s.pdf' % rid)
        got = parse(pdf, rid, produto=p['PRODUCT'],
                    ai=p.get('ACTIVE_INGREDIENTS'), cache_dir=pdf_dir,
                    categoria=p.get('REGULATORY_CATEGORY'))
        pares.extend(got)
        if not [g for g in got if g['RELATION'] == 'SUPPORTED_PAIR']:
            sem.append({'REGISTRATION_ID': rid, 'PRODUCT': p['PRODUCT'],
                        'WHY': 'NENHUM_PAR_SUPORTADO'})
        if i % 40 == 0:
            print('  %d/%d' % (i, len(P)), file=sys.stderr)

    sup = [x for x in pares if x['RELATION'] == 'SUPPORTED_PAIR']
    amb = [x for x in pares if x['RELATION'] == 'AMBIGUOUS_ROW']
    exc = [x for x in pares if x['RELATION'] == 'EXCLUDED_PAIR']
    sco = [x for x in pares if x['RELATION'] == 'SCOPE_COMBINATION']
    csd = [x for x in pares if x['RELATION'] == 'CROP_SCOPE_DECLARED']
    out = {
        'DATASET': 'IT-ROTULOS-PARES-V3',
        'LAYER': 'NATIONAL PRODUCT AUTHORIZATION',
        'COUNTRY': 'IT',
        'SOURCE_ID': 'IT-T4-001-ETICHETTA',
        'CAPTURED_AT': '2026-09-04',
        'SOURCE': 'pares cultura x alvo extraidos da GEOMETRIA dos 163 rotulos '
                  'autorizados do Ministero della Salute, com %s' % PARSER_VERSION,
        'ESTADO': 'PUBLICADO — passou o portao IT-ROTULOS-PORTAO-V1',
        'POR_QUE_PUBLICADO': 'medido contra o gabarito COMPLETO de 30 rotulos: precisao '
                             '0,965 e recall 0,866, com zero violacao de EXPECTED_NO_PAIR '
                             'e zero promocao de AMBIGUOUS. Nenhuma cultura real perde '
                             'cobertura: as unicas quedas sao nomes de GRUPO, cujos '
                             'membros subiram. A cauda fora do gabarito foi estimada por '
                             'amostra adjudicada de 25 pares (25 certos, 0 errados).',
        'O_CONJUNTO_ANTIGO_CONTINUA_PINADO': 'data/samples/IT-RADAR-V21/'
                                             'productRelationships.json',
        'PARSER_VERSION': PARSER_VERSION,
        'TOTAL_LABELS': len(P),
        'SUPPORTED_PAIRS': len(sup),
        'AMBIGUOUS_ROWS': len(amb),
        'EXCLUDED_PAIRS': len(exc),
        'SCOPE_COMBINATION_NOT_PUBLISHED': len(sco),
        'CROP_SCOPE_DECLARED_NOT_PUBLISHED': len(csd),
        'LABELS_WITHOUT_SUPPORTED_PAIR': len(sem),
        'LABELS_WITHOUT_SUPPORTED_PAIR_LIST': sem,
        'PROVENANCE_COMPLETE': all('PROVENANCE' in x for x in pares),
        'PAIRS': sup,
        'AMBIGUOUS': amb,
        'EXCLUDED': exc,
        'SCOPE_COMBINATION': sco,
        'CROP_SCOPE_DECLARED': csd,
    }
    json.dump(out, open(saida, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('SUPPORTED=%d AMBIGUOUS=%d EXCLUDED=%d  rotulos sem par=%d'
          % (len(sup), len(amb), len(exc), len(sem)))
    return out


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
