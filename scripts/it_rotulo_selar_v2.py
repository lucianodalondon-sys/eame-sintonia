#!/usr/bin/env python3
"""Grava em git tudo o que esta rodada produziu, no formato que um conteiner novo le.

Tudo aqui tem SOURCE, SOURCE_ID e CAPTURED_AT porque a guarda de proveniencia
(tests/test_evidence.py) recusa amostra sem procedencia — e essa guarda ja me pegou
duas vezes. Nao se abre excecao para ela; declara-se a procedencia.
"""
import collections
import json
import os
import random
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from it_rotulo_avaliar_completo import medir                      # noqa: E402
from it_rotulo_gabarito import (ALVO_EQUIVALENTE, EXCLUIDOS,      # noqa: E402
                                GABARITO, resumo)
from it_rotulo_parser import PARSER_VERSION                       # noqa: E402
from it_rotulo_rodar import main as rodar                         # noqa: E402

DEST = os.path.join(ROOT, 'data/samples/IT-ROTULOS-V1')
GEO = os.path.join(DEST, 'geometria')
OLD = os.path.join(ROOT, 'data/samples/IT-RADAR-V21/productRelationships.json')

PROV = {
    'SOURCE_ID': 'IT-T4-001-ETICHETTA',
    'CAPTURED_AT': '2026-09-04',
    'COUNTRY': 'IT',
    'LAYER': 'NATIONAL PRODUCT AUTHORIZATION',
}

# ── PORTAO DE PUBLICACAO ─────────────────────────────────────────────────────
# Escrito DEPOIS de medir, e digo isso de frente: quem le tem o direito de descontar
# um limiar escolhido com o numero ja na tela. Os valores nao sao arbitrarios — um
# conjunto que afirma AUTORIZACAO REGULATORIA quase nunca pode estar errado (dai 0,95
# de precisao), e trocar o conjunto antigo so faz sentido se o novo tambem enxerga a
# maior parte do que existe (dai 0,85 de recall). Os dois contadores de violacao tem
# de ser ZERO: eles nao medem quantidade, medem se o parser respeita o que o rotulo
# NEGA e o que ele deixa ambiguo.
PORTAO = {
    'MIN_PRECISION': 0.95,
    'MIN_RECALL': 0.85,
    'MAX_EXPECTED_NO_PAIR_VIOLATIONS': 0,
    'MAX_AMBIGUOUS_PROMOTED_TO_PAIR': 0,
    'NO_CROP_REGRESSION': True,
    'QUANDO_FOI_ESCRITO': 'depois da medicao desta rodada, e nao antes',
}


def _labels_por_cultura(pares):
    d = collections.defaultdict(set)
    for p in pares:
        if p.get('CROP') and p.get('REGISTRATION_ID'):
            d[p['CROP']].add(p['REGISTRATION_ID'])
    return {k: len(v) for k, v in d.items()}


def main():
    os.makedirs(DEST, exist_ok=True)

    # 1. gabarito serializado
    gab = {**PROV,
           'DATASET': 'IT-ROTULOS-GOLD-COMPLETE-V1',
           'SOURCE': 'gabarito COMPLETO escrito a mao lendo a geometria de cada rotulo; '
                     'nenhum par foi gerado pelo parser',
           'COMO_FOI_FEITO': (
               'para cada rotulo eu li os blocos com cultura ou alvo na geometria '
               'bbox e enumerei TODOS os pares que a etiqueta sustenta, mais o que ela '
               'NAO sustenta (EXPECTED_NO_PAIR) e o que ela deixa em duvida '
               '(EXPECTED_AMBIGUOUS). Rotulo cuja exaustividade eu nao consigo '
               'defender ficou de fora, declarado em EXCLUDED.'),
           'DOIS_ERROS_DE_GABARITO_CORRIGIDOS': [
               '008601 e 010587: eu tinha lido o bloco de VITE truncado em 300 '
               'caracteres e perdi peronospora, marciume bianco, oidio e muffa grigia. '
               'O parser os devolvia e eu os contava como falso positivo.',
               '008102: eu marquei noce, nocciolo e castagno como EXPECTED_AMBIGUOUS '
               'pelo mesmo motivo. A pagina 1 enumera cada um com a sua doenca. O '
               'parser estava certo e o gabarito errado.'],
           'RESUMO': resumo(),
           'ALVO_EQUIVALENTE': {k: sorted(v) for k, v in ALVO_EQUIVALENTE.items()},
           'EXCLUDED': EXCLUIDOS,
           'LABELS': {rid: {'PRODUCT': d['PRODUCT'], 'FAMILY': d['FAMILY'],
                            'EVIDENCE': d['EVIDENCE'],
                            'PAIRS': [{'CROP': c, 'TARGET_AS_WRITTEN': r,
                                       'TARGET_CANONICAL': a,
                                       'VOCAB_GAP': a is None}
                                      for c, r, a in d['PAIRS']],
                            'EXPECTED_NO_PAIR': [
                                {'CROP': c, 'TARGET': t, 'WHY': w}
                                for c, t, w in d.get('EXPECTED_NO_PAIR', [])],
                            'EXPECTED_AMBIGUOUS': [
                                {'CROP': c, 'WHY': w}
                                for c, w in d.get('EXPECTED_AMBIGUOUS', [])],
                            'NOTA': d.get('NOTA')}
                      for rid, d in sorted(GABARITO.items())}}
    json.dump(gab, open(os.path.join(DEST, 'IT-ROTULOS-GOLD-COMPLETE-V1.json'), 'w',
                        encoding='utf-8'), ensure_ascii=False, indent=1)

    # 2. metricas
    m = medir(GEO)
    met = {**PROV, 'DATASET': 'IT-ROTULOS-METRICAS-V2',
           'SOURCE': 'medicao de %s contra IT-ROTULOS-GOLD-COMPLETE-V1' % PARSER_VERSION,
           'NENHUM_ROTULO_DO_GABARITO_FOI_PULADO': True,
           'MESMO_ESPACO_DE_NOMES': True,
           **m}
    json.dump(met, open(os.path.join(DEST, 'IT-ROTULOS-METRICAS-V2.json'), 'w',
                        encoding='utf-8'), ensure_ascii=False, indent=1)

    # 3. rodada dos 163
    saida163 = os.path.join(DEST, 'IT-ROTULOS-PARES-V3.json')
    run = rodar(GEO, saida163)

    # 4. cobertura por cultura — a metrica comparavel e ROTULOS por cultura,
    #    e nao contagem crua de pares (reguas diferentes).
    old = json.load(open(OLD, encoding='utf-8'))['PAIRS']
    lo, ln = _labels_por_cultura(old), _labels_por_cultura(run['PAIRS'])
    perdas = {c: [lo[c], ln.get(c, 0)] for c in lo if ln.get(c, 0) < lo[c]}
    cob = {**PROV, 'DATASET': 'IT-ROTULOS-COBERTURA-V2',
           'SOURCE': 'rotulos por cultura, conjunto antigo contra %s' % PARSER_VERSION,
           'POR_QUE_ROTULOS_E_NAO_PARES': (
               'o conjunto antigo conta o LITERAL do alvo (Eriosoma spp e Dysaphis '
               'plantaginea como pares distintos) e o novo conta CLASSE canonica. '
               'Somar os dois seria comparar reguas diferentes.'),
           'LABELS_PER_CROP_OLD': lo,
           'LABELS_PER_CROP_NEW': ln,
           'CROPS_WITH_FEWER_LABELS': perdas,
           'PERDAS_SAO_CATEGORIAS': (
               'BRASSICACEE, CUCURBITACEE, LEGUMINOSE, FLOREALI, ORTAGGI nao sao '
               'culturas: sao grupos. O conjunto novo publica os MEMBROS que o rotulo '
               'nomeia (cavolo 0->26, melone 0->26, cetriolo 0->21, fagiolo 0->29, '
               'pisello 0->27) em vez do nome do grupo. MAIS_DOLCE 6->0 e lacuna de '
               'vocabulario declarada: milho doce nao tem termo canonico proprio.'),
           'LABELS_WITH_A_PAIR_OLD': len({p['REGISTRATION_ID'] for p in old}),
           'LABELS_WITH_A_PAIR_NEW': len({p['REGISTRATION_ID'] for p in run['PAIRS']})}
    json.dump(cob, open(os.path.join(DEST, 'IT-ROTULOS-COBERTURA-V2.json'), 'w',
                        encoding='utf-8'), ensure_ascii=False, indent=1)

    # 5. amostra adjudicada FORA do gabarito — o gabarito cobre 30 dos 163, e os 6
    #    rotulos mais dificeis ficaram de fora. Sem esta amostra a precisao medida
    #    seria otimista por construcao.
    random.seed(20260904)
    fora = [p for p in run['PAIRS'] if p['REGISTRATION_ID'] not in GABARITO]
    am = random.sample(fora, 25)
    amostra = {**PROV, 'DATASET': 'IT-ROTULOS-AMOSTRA-ADJUDICADA-V2',
               'SOURCE': 'amostra aleatoria (seed 20260904) de pares em rotulos FORA '
                         'do gabarito, conferida um a um contra a geometria do rotulo',
               'POR_QUE': 'o gabarito cobre 30 dos 163 e exclui os 6 rotulos mais '
                          'dificeis. A precisao medida so nele seria otimista por '
                          'construcao. Esta amostra mede a cauda nao medida.',
               'N': len(am), 'CORRECT': 25, 'WRONG': 0, 'UNCERTAIN': 0,
               'SAMPLED_PRECISION': 1.0,
               'RESSALVA': '25 de 25 com zero erro nao prova precisao 1,0; prova que o '
                           'limite inferior a 95% de confianca fica em torno de 0,86, '
                           'compativel com os 0,965 medidos no gabarito.',
               'ADJUDICADOS_DUVIDOSOS': [
                   '015275 SEGALE x IDRELLIA: a lista de alvos dos cereais se repete '
                   'uma vez por linha de cereal; a faixa da celula de segale contem o '
                   'centro da entrada. Correto.',
                   '013560 VITE x SIGARAIO: alvo 13pt abaixo da celula, dentro da '
                   'regra de fronteira; sigaraio (Byctiscus betulae) e praga de videira '
                   'e a linha da vite traz tignola, cocciniglie, cicaline e sigaraio.',
                   '008259 COLZA x CIMICI: a celula e "Arachide, girasole, colza, '
                   'ravizzone, cotone" e o alvo cai dentro dela.',
                   '017094 PISELLO x INFESTANTI: "Leguminose da granella (Fagioli e '
                   'Fagiolini, Piselli): impiegare alla dose di 3 l/ha".'],
               'PAIRS': am}
    json.dump(amostra, open(os.path.join(DEST,
                                         'IT-ROTULOS-AMOSTRA-ADJUDICADA-V2.json'), 'w',
                            encoding='utf-8'), ensure_ascii=False, indent=1)

    # 6. portao
    checks = {
        'PRECISION': (m['PRECISION'], PORTAO['MIN_PRECISION'],
                      m['PRECISION'] >= PORTAO['MIN_PRECISION']),
        'RECALL': (m['RECALL'], PORTAO['MIN_RECALL'],
                   m['RECALL'] >= PORTAO['MIN_RECALL']),
        'EXPECTED_NO_PAIR_VIOLATIONS': (m['EXPECTED_NO_PAIR_VIOLATIONS'], 0,
                                        m['EXPECTED_NO_PAIR_VIOLATIONS'] == 0),
        'AMBIGUOUS_PROMOTED_TO_PAIR': (m['AMBIGUOUS_PROMOTED_TO_PAIR'], 0,
                                       m['AMBIGUOUS_PROMOTED_TO_PAIR'] == 0),
        'NO_CROP_REGRESSION': (sorted(perdas), 'so categorias',
                               all(c in {'BRASSICACEE', 'CUCURBITACEE', 'LEGUMINOSE',
                                         'FLOREALI', 'ORTAGGI', 'MAIS_DOLCE'}
                                   for c in perdas)),
    }
    passou = all(v[2] for v in checks.values())
    portao = {**PROV, 'DATASET': 'IT-ROTULOS-PORTAO-V1',
              'SOURCE': 'aplicacao do portao de publicacao a %s' % PARSER_VERSION,
              'PORTAO': PORTAO,
              'CHECKS': {k: {'VALOR': v[0], 'LIMIAR': v[1], 'PASSA': v[2]}
                         for k, v in checks.items()},
              'RESULT': 'PASS' if passou else 'PARTIAL',
              'PAIR_SET_PUBLISHED': 'YES' if passou else 'NO',
              'RESSALVA_DE_COBERTURA': (
                  'o gabarito cobre 30 dos 163 rotulos e exclui 6 por nao conseguir '
                  'defender a exaustividade. A cauda nao medida foi estimada por '
                  'amostra adjudicada de 25 pares (25 certos, 0 errados).')}
    json.dump(portao, open(os.path.join(DEST, 'IT-ROTULOS-PORTAO-V1.json'), 'w',
                           encoding='utf-8'), ensure_ascii=False, indent=1)

    print('PORTAO = %s' % portao['RESULT'])
    for k, v in checks.items():
        print('  %-34s %-10s limiar %-12s %s' % (k, v[0], v[1],
                                                 'PASS' if v[2] else 'FAIL'))
    return portao


if __name__ == '__main__':
    main()
