#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A RECONCILIAÇÃO DE LINHAGEM — os 43 casos, nas três árvores, campo a campo.

    python3 scripts/v21_reconciliacao_de_linhagem.py <dir_e7c154c> <dir_d83f6f3>

    (cada dir é a raiz de um worktree onde `v21_cadeia.sh` já rodou)

POR QUE ESTE ARQUIVO EXISTE
----------------------------
Duas linhas de trabalho saíram do mesmo commit `0ddf52d` e trabalharam ao mesmo
tempo na mesma pergunta. Uma construiu a inteligência de janela e o contrato do
cartão DENTRO do motor; a outra construiu a catraca de publicação POR CIMA dele
— e, sem saber, uma segunda cópia do contrato do cartão.

    QUANDO DUAS LINHAS RESPONDEM À MESMA PERGUNTA, A RECONCILIAÇÃO NÃO É
    ESCOLHER UM LADO: É PROVAR, CASO A CASO, O QUE CADA UMA DECIDIU.

Nenhum caso pode desaparecer em silêncio, e nenhuma diferença pode ficar sem
razão nomeada. Este script não conserta nada e não grava no pacote: ele MEDE, e
a medição é o que autoriza (ou não) chamar a árvore reconciliada de canônica.

O QUE ELE CLASSIFICA
--------------------
Para cada campo de cada caso, uma de cinco razões:

    IGUAL_NOS_TRES            ninguém mexeu
    DA_LINHAGEM_NOVA          o reconciliado adotou o valor de e7c154c
    DA_CATRACA                campo que só existe porque a catraca entrou
    CAMPO_NOVO_DA_LINHAGEM    não existia em d83f6f3; nasceu em e7c154c
    DIVERGENCIA_SEM_DONO      ⚠️ o reconciliado não bate com nenhum dos dois

A última é a única que reprova. Se ela aparecer, alguma coisa foi decidida na
fusão em vez de herdada — e decidir na fusão é exatamente o que a missão proíbe.
"""
import json
import os
import sys
from collections import Counter, OrderedDict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REL = os.path.join('build', 'ITALY-REALITY-HANDOFF-V2.1', 'DESIGN-INGEST',
                   'OPPORTUNITIES.json')
SAIDA = os.path.join(ROOT, 'data', 'samples', 'AUDITORIA-SOMBRA',
                     'RECONCILIACAO-DE-LINHAGEM.json')

# Os campos que a missão mandou comparar, mais os que a catraca acrescenta.
CAMPOS = ('STATUS', 'COMMERCIAL_PRIORITY', 'WHY_NOW_CODES', 'WINDOW_DEFINED',
          'WINDOW_OPEN_NOW', 'WINDOW_TYPE', 'ACTION_CHAIN_LINKS',
          'PORTFOLIO_MATCHES', 'PRIMARY_MATCH', 'ACTION_BY_DEPARTMENT',
          'ACTION_MAP', 'EVIDENCE_ROLES', 'WHAT_IS_MISSING',
          'EXTERNAL_MATERIAL_READY', 'PUBLICATION_STATE', 'TRAIL_STATE')

# Campos cujo dono é a catraca — não existiam em e7c154c, e é correto que o
# reconciliado os tenha e a linhagem nova não.
DA_CATRACA = ('PUBLICATION_STATE', 'TRAIL_STATE')

AUSENTE = '<CAMPO_AUSENTE>'


def _carrega(raiz):
    p = os.path.join(raiz, REL)
    if not os.path.exists(p):
        print('pacote nao construido em %s — rode bash scripts/v21_cadeia.sh la'
              % raiz, file=sys.stderr)
        raise SystemExit(2)
    d = json.load(open(p, encoding='utf-8'))
    return d['BUILD_ID'], {r['ID']: r for r in d['RECORDS']}


def _v(rec, campo):
    """O valor comparável. Lista de dicionário vira contagem + chaves estáveis."""
    if rec is None or campo not in rec:
        return AUSENTE
    v = rec[campo]
    if isinstance(v, list) and v and isinstance(v[0], dict):
        # PORTFOLIO_MATCHES e EVIDENCE_ROLES: o que importa comparar é QUEM
        # está na lista e com que papel — não a prosa de cada item.
        chave = ('PRODUCT_ID' if 'PRODUCT_ID' in v[0] else
                 'EVIDENCE_ID' if 'EVIDENCE_ID' in v[0] else None)
        papel = ('MATCH_STATE' if 'MATCH_STATE' in v[0] else
                 'ROLE' if 'ROLE' in v[0] else None)
        if chave:
            return sorted('%s:%s' % (x.get(chave), x.get(papel)) for x in v)
    if isinstance(v, dict):
        return json.dumps(v, sort_keys=True, ensure_ascii=False)
    return v


def razao(campo, novo, meu, rec):
    if campo in DA_CATRACA:
        return 'DA_CATRACA' if rec != AUSENTE else 'DIVERGENCIA_SEM_DONO'
    if novo == meu == rec:
        return 'IGUAL_NOS_TRES'
    if rec == novo:
        return 'CAMPO_NOVO_DA_LINHAGEM' if meu == AUSENTE else 'DA_LINHAGEM_NOVA'
    if rec == meu:
        return 'DA_MINHA_LINHA'
    return 'DIVERGENCIA_SEM_DONO'


def main():
    if len(sys.argv) < 3:
        print(__doc__.strip().splitlines()[3], file=sys.stderr)
        return 2
    id_novo, novo = _carrega(sys.argv[1])
    id_meu, meu = _carrega(sys.argv[2])
    id_rec, rec = _carrega(ROOT)

    todos = sorted(set(novo) | set(meu) | set(rec))
    linhas, contagem, sem_dono, sumidos = [], Counter(), [], []

    for oid in todos:
        presenca = {'E7C154C': oid in novo, 'D83F6F3': oid in meu,
                    'RECONCILIADO': oid in rec}
        if not presenca['RECONCILIADO']:
            sumidos.append(oid)
        campos = OrderedDict()
        for c in CAMPOS:
            a, b, r = _v(novo.get(oid), c), _v(meu.get(oid), c), _v(rec.get(oid), c)
            rz = razao(c, a, b, r)
            contagem[rz] += 1
            if rz in ('IGUAL_NOS_TRES', 'DA_CATRACA'):
                continue
            campos[c] = {'E7C154C': a, 'D83F6F3': b, 'RECONCILIADO': r,
                         'RAZAO': rz}
            if rz == 'DIVERGENCIA_SEM_DONO':
                sem_dono.append('%s · %s' % (oid, c))
        linhas.append({'OPPORTUNITY_ID': oid, 'PRESENCA': presenca,
                       'CAMPOS_QUE_MUDARAM': campos})

    r = {
        'WHAT_IT_IS': 'os 43 casos nas tres arvores, campo a campo',
        'BUILD_ID_E7C154C': id_novo,
        'BUILD_ID_D83F6F3': id_meu,
        'BUILD_ID_RECONCILIADO': id_rec,
        'COUNT': {'E7C154C': len(novo), 'D83F6F3': len(meu),
                  'RECONCILIADO': len(rec)},
        'CASOS_QUE_SUMIRAM': sumidos,
        'CAMPOS_COMPARADOS': list(CAMPOS),
        'POR_RAZAO': dict(contagem),
        'DIVERGENCIA_SEM_DONO': sem_dono,
        'LEI': 'nenhum caso pode desaparecer em silencio e nenhuma diferenca pode '
               'ficar sem razao nomeada. DIVERGENCIA_SEM_DONO significa que o '
               'reconciliado nao bate com nenhuma das duas linhas — ou seja, algo '
               'foi DECIDIDO na fusao em vez de herdado. Isso reprova.',
        'RECORDS': linhas,
    }
    os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
    json.dump(r, open(SAIDA, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    print('== RECONCILIACAO DE LINHAGEM ==')
    print('casos        : e7c154c %d · d83f6f3 %d · reconciliado %d'
          % (len(novo), len(meu), len(rec)))
    print('sumiram      : %d %s' % (len(sumidos), sumidos[:5]))
    for k, v in sorted(contagem.items(), key=lambda x: -x[1]):
        print('  %-26s %d' % (k, v))
    print('gravado: %s' % SAIDA)
    if sumidos or sem_dono:
        print('\n  PARADO:')
        for s in sumidos[:10]:
            print('   caso sumiu: %s' % s)
        for s in sem_dono[:15]:
            print('   divergencia sem dono: %s' % s)
        return 1
    print('\n  CASOS PERDIDOS: 0 · DIVERGENCIAS SEM DONO: 0')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
