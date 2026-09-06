#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O PORTAO DE CONVERGENCIA do `UNIVERSE_ACERVO_IT`.

    py -3 scripts/it_acervo_convergencia.py [--raiz .] [--json saida.json]

Corre os DOIS leitores independentes e compara. Enquanto discordarem em
qualquer dimensao, `UNIVERSE_ACERVO_IT_CANONICAL = NAO` — e nenhum numero deste
universo pode ser declarado.

    codigo de saida 0   os dois concordam E o acervo passa no portao
                    1   os dois concordam, mas o acervo REPROVA (chave por
                        reconhecer, ficheiro ilegivel, invariante partida)
                    2   OS DOIS DISCORDAM — nao ha universo

SOMENTE LEITURA. Nao escreve dentro de `data/`.

Por que 1 e 2 sao codigos diferentes: discordar e defeito NOSSO, no leitor;
reprovar e o acervo a pedir uma decisao. Colapsar os dois num so numero
esconderia qual dos dois aconteceu, e sao coisas opostas.
"""
import argparse
import importlib.util
import json
import os
import sys
from collections import OrderedDict

AQUI = os.path.dirname(os.path.abspath(__file__))

# As cinco dimensoes do contrato, mais as duas listas que provam que a
# coincidencia nao e por acaso.
DIMENSOES = ('FILES', 'RECORDS', 'COLLECTIONS', 'UNKNOWN_KEYS', 'FINGERPRINT')
LISTAS = ('FILE_LIST', 'PER_KEY', 'PER_FAMILY')


def _carrega(nome, ficheiro):
    """Importa cada leitor pelo ficheiro, para nao haver modulo partilhado."""
    spec = importlib.util.spec_from_file_location(nome, os.path.join(AQUI, ficheiro))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def comparar(a, b):
    """Devolve (concordam, [divergencias]). Nao le ficheiro nenhum."""
    divergencias = []
    for d in DIMENSOES:
        if a.get(d) != b.get(d):
            divergencias.append({'DIMENSAO': d, 'A': a.get(d), 'B': b.get(d)})
    for d in LISTAS:
        va, vb = a.get(d), b.get(d)
        if va != vb:
            if isinstance(va, list) and isinstance(vb, list):
                sa, sb = set(va), set(vb)
                detalhe = {'SO_EM_A': sorted(sa - sb)[:20], 'SO_EM_B': sorted(sb - sa)[:20]}
            else:
                ka = set(va or {})
                kb = set(vb or {})
                detalhe = {
                    'SO_EM_A': sorted(ka - kb)[:20],
                    'SO_EM_B': sorted(kb - ka)[:20],
                    'VALOR_DIFERENTE': sorted(
                        k for k in (ka & kb) if (va or {})[k] != (vb or {})[k])[:20],
                }
            divergencias.append({'DIMENSAO': d, 'DETALHE': detalhe})
    return (not divergencias), divergencias


def veredicto(a, b):
    concordam, divergencias = comparar(a, b)
    reprova_acervo = bool(a.get('UNKNOWN_COLLECTION_KEY')) or bool(a.get('ILEGIVEL')) \
        or not a.get('INVARIANT_FAMILY_SUM_OK') or a.get('FILES') == 0
    motivos = []
    if a.get('FILES') == 0:
        motivos.append('ENTRADA_VAZIA')
    if a.get('UNKNOWN_COLLECTION_KEY'):
        motivos.append('UNKNOWN_COLLECTION_KEY=%d' % len(a['UNKNOWN_COLLECTION_KEY']))
    if a.get('ILEGIVEL'):
        motivos.append('ILEGIVEL=%d' % len(a['ILEGIVEL']))
    if not a.get('INVARIANT_FAMILY_SUM_OK'):
        motivos.append('INVARIANTE_DAS_FAMILIAS_PARTIDA')

    return OrderedDict([
        ('UNIVERSE', 'UNIVERSE_ACERVO_IT'),
        ('INDEPENDENT_READERS_AGREE', 'SIM' if concordam else 'NAO'),
        ('DIVERGENCIAS', divergencias),
        ('CANONICAL_FILES', a.get('FILES') if concordam else None),
        ('CANONICAL_RECORDS', a.get('RECORDS') if concordam else None),
        ('CANONICAL_COLLECTIONS', a.get('COLLECTIONS') if concordam else None),
        ('CANONICAL_UNKNOWN_KEYS', a.get('UNKNOWN_KEYS') if concordam else None),
        ('CANONICAL_FINGERPRINT', a.get('FINGERPRINT') if concordam else None),
        ('ACERVO_PASSA_NO_PORTAO', 'NAO' if reprova_acervo else 'SIM'),
        ('MOTIVOS_DE_REPROVACAO', motivos),
        ('UNIVERSE_ACERVO_IT_CANONICAL',
         'SIM' if (concordam and not reprova_acervo) else 'NAO'),
        ('CANONICAL_RULE_PROVED', 'SIM' if concordam else 'NAO'),
    ])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--raiz', default='.')
    ap.add_argument('--json', default=None)
    a = ap.parse_args()

    leitor_a = _carrega('leitor_a', 'it_acervo_leitor_a.py')
    leitor_b = _carrega('leitor_b', 'it_acervo_leitor_b.py')
    ra = leitor_a.ler(a.raiz)
    rb = leitor_b.ler(a.raiz)
    v = veredicto(ra, rb)

    print('== CONVERGENCIA · UNIVERSE_ACERVO_IT ==')
    print('   %-28s %s' % ('leitor', 'A            B'))
    for d in DIMENSOES:
        marca = '  ' if ra.get(d) == rb.get(d) else ' <-- DIVERGE'
        if d == 'FINGERPRINT':
            print('   %-28s %s%s' % (d, str(ra.get(d))[:16] + '…', marca))
            print('   %-28s %s' % ('', str(rb.get(d))[:16] + '…'))
        else:
            print('   %-28s %-12s %-12s%s' % (d, ra.get(d), rb.get(d), marca))
    print()
    for k in ('INDEPENDENT_READERS_AGREE', 'CANONICAL_RULE_PROVED',
              'ACERVO_PASSA_NO_PORTAO', 'UNIVERSE_ACERVO_IT_CANONICAL'):
        print('   %-30s %s' % (k, v[k]))
    if v['MOTIVOS_DE_REPROVACAO']:
        print('   %-30s %s' % ('MOTIVOS', ' · '.join(v['MOTIVOS_DE_REPROVACAO'])))
    if v['DIVERGENCIAS']:
        print('\n   DIVERGENCIAS:')
        for d in v['DIVERGENCIAS']:
            print('    · %s' % json.dumps(d, ensure_ascii=False)[:300])

    if a.json:
        assert '/data/' not in a.json.replace(os.sep, '/'), 'portao nao escreve em data/'
        json.dump(v, open(a.json, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print('\n   gravado: %s' % a.json)

    if v['INDEPENDENT_READERS_AGREE'] == 'NAO':
        return 2
    return 0 if v['ACERVO_PASSA_NO_PORTAO'] == 'SIM' else 1


if __name__ == '__main__':
    raise SystemExit(main())
