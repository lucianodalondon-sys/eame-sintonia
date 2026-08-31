#!/usr/bin/env python3
"""
LIMPAR O ACERVO PROPRIO DA ADAMA — sem coletar nada de novo.

O acervo `OWN_PUBLIC_META_ACTIVITY` tinha 40 cartoes, e 33 deles eram do
`Instytut Adama Mickiewicza`, instituto cultural polones que entrou por
casamento nominal. Oitenta e dois por cento do dataset da propria casa era
outra entidade.

Este arquivo aplica a guarda de `meta_identidade.py`, grava o acervo limpo e
PRESERVA os recusados num arquivo a parte. Preservar importa: apagar tornaria
impossivel auditar depois por que 33 cartoes sumiram, e um dia alguem
reintroduziria o mesmo erro sem saber que ja tinha acontecido.

    RECUSADO != APAGADO
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import meta_identidade as identidade  # noqa: E402

PASTA = os.path.join(ROOT, 'data', 'samples', 'META-EAME')
ORIGEM = os.path.join(PASTA, 'META-OWN-ADS-ENTITIES-ADAMA-V1.json')
LIMPO = os.path.join(PASTA, 'META-OWN-ADS-ENTITIES-ADAMA-CLEAN-V1.json')
RECUSADOS = os.path.join(PASTA, 'META-OWN-ADS-REJECTED-IDENTITY-V1.json')


def rodar():
    with open(ORIGEM, encoding='utf-8') as f:
        d = json.load(f)
    aceitos, recusados = identidade.filtrar_por_identidade(d.get('entities', {}),
                                                           'ADAMA')
    paginas_recusadas = sorted({e.get('page_name_resolved') for e in recusados.values()})
    limpo = dict(d)
    limpo['entities'] = aceitos
    limpo['identity_guard'] = {
        'guard': 'ADAMA_ADVERTISER_IDENTITY_GUARD',
        'rule': 'o token da empresa precisa ABRIR o nome da pagina',
        'adama_false_cards_rejected': len(recusados),
        'adama_real_cards_remaining': len(aceitos),
        'rejected_pages': paginas_recusadas,
        'rejected_preserved_in': os.path.basename(RECUSADOS),
    }
    with open(LIMPO, 'w', encoding='utf-8') as f:
        json.dump(limpo, f, ensure_ascii=False, indent=2)
    with open(RECUSADOS, 'w', encoding='utf-8') as f:
        json.dump({'dataset_owner': 'META_COMPETITOR_EAME',
                   'why': 'preservado para auditoria; NAO e acervo da ADAMA',
                   'rejected_pages': paginas_recusadas,
                   'entities': recusados}, f, ensure_ascii=False, indent=2)
    return limpo['identity_guard']


if __name__ == '__main__':
    print(json.dumps(rodar(), ensure_ascii=False, indent=2))
