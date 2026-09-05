#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CARIMBA A CAMADA DE ORIGEM em todo registro que ainda não a declara.

    python3 scripts/v21_carimbar_origem.py

POR QUE ISTO EXISTE
--------------------
O registro central tinha um `or 'DERIVED_V2_1'`: quem chegasse sem carimbo era
chamado de derivado. Isso apagou a origem de 2.945 linhas do ISTAT, que vieram
de coleta externa e não de cálculo meu.

    UM DADO QUE VEIO DE FORA NÃO PODE APARECER COMO SE EU O TIVESSE DEDUZIDO.

O default silencioso é pior que o campo vazio: o campo vazio se vê, o default
mente com confiança.

A REGRA
--------
A procedência já dizia a verdade; ninguém a lia.

    REAL_SOURCE_LAST_MILE  → LAST_MILE         (coletado na missão last-mile)
    REAL_SOURCE            → PREVIOUS_HANDOFF  (veio do pacote anterior)
    DERIVED_*              → DERIVED_V2_1      (construído aqui)

Cruzamento e ligação são os únicos que esta versão realmente construiu — e são
DERIVED por definição, porque não existiam em fonte nenhuma.
"""
import json
import os
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ING = os.path.join(ROOT, 'build', 'ITALY-REALITY-HANDOFF-V2.1', 'DESIGN-INGEST')

# ⚠️ PROCEDÊNCIA E CAMADA RESPONDEM A PERGUNTAS DIFERENTES, e confundi-las já
# custou 981 registros carimbados como «origem desconhecida»:
#
#     PROVENANCE  → o valor foi LIDO numa fonte, ou CALCULADO a partir dela?
#     ORIGIN_LAYER→ o registro entrou neste pacote por qual camada?
#
# `REAL_DERIVED` é o rendimento (produção ÷ área): calculado, sim — mas calculado
# LÁ, na coleta last-mile, não aqui. As duas coisas convivem sem contradição, e
# apagar uma para caber na outra é perder informação de propósito.
DE_PROCEDENCIA = {
    'REAL_SOURCE_LAST_MILE': 'LAST_MILE',
    'REAL_DERIVED': 'LAST_MILE',
    'REAL_SOURCE': 'PREVIOUS_HANDOFF',
    'REAL_SOURCE_PREVIOUS_HANDOFF': 'PREVIOUS_HANDOFF',
    # A camada de substancia ativa entrou por uma terceira porta: o pacote
    # research/adama-italy-product-intelligence-deep, que nao e a last-mile nem o
    # handoff anterior. Enfia-la em LAST_MILE deixaria o numero certo e a
    # procedencia errada — e e a procedencia que responde de onde o dado veio.
    'EVIDENCE_SOURCED': 'PRODUCT_INTELLIGENCE_DEEP',
    'EVIDENCE_DOCUMENTED': 'PRODUCT_INTELLIGENCE_DEEP',
}

# ⚠️ Estes dois NASCERAM aqui. Não há fonte que os publique — são leitura minha
# sobre dado de outros. Por isso DERIVED, e por isso o cliente vê a ressalva.
NASCEU_AQUI = {'CLIENT-SAFE-CROSSINGS.json', 'RELATIONSHIPS.json'}


def main():
    total, mudou = 0, Counter()
    for arq in sorted(os.listdir(ING)):
        if not arq.endswith('.json') or arq.startswith('CANONICAL'):
            continue
        p = os.path.join(ING, arq)
        d = json.load(open(p, encoding='utf-8'))
        regs = d.get('RECORDS') or []
        n = 0
        for r in regs:
            if not isinstance(r, dict) or not r.get('ID') or r.get('ORIGIN_LAYER'):
                continue
            proc = str(r.get('PROVENANCE') or '')
            if arq in NASCEU_AQUI:
                r['ORIGIN_LAYER'] = 'DERIVED_V2_1'
            elif proc in DE_PROCEDENCIA:
                r['ORIGIN_LAYER'] = DE_PROCEDENCIA[proc]
            elif proc.startswith('DERIVED'):
                r['ORIGIN_LAYER'] = 'DERIVED_V2_1'
            else:
                # ⚠️ Não invento. Sem procedência conhecida, o campo fica marcado
                # como desconhecido — e desconhecido se vê no relatório.
                r['ORIGIN_LAYER'] = 'UNKNOWN_ORIGIN'
                r['ORIGIN_LAYER_NOTE'] = (
                    'a procedencia deste registro (%r) nao mapeia para nenhuma '
                    'camada conhecida. Nao foi adivinhada.' % proc)
            n += 1
            mudou[r['ORIGIN_LAYER']] += 1
        if n:
            d['BY_ORIGIN'] = dict(Counter(x.get('ORIGIN_LAYER') for x in regs
                                          if isinstance(x, dict) and x.get('ID')))
            json.dump(d, open(p, 'w', encoding='utf-8'),
                      ensure_ascii=False, indent=1)
            print('%-34s %5d carimbados' % (arq, n))
        total += n

    print('\ntotal carimbado: %d · %s' % (total, dict(mudou)))
    if mudou.get('UNKNOWN_ORIGIN'):
        print('ATENCAO: %d registros sem origem dedutivel — veja ORIGIN_LAYER_NOTE.'
              % mudou['UNKNOWN_ORIGIN'])
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
