#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A PROMOÇÃO TUDO-OU-NADA · auditar antes de consertar.

    python3 scripts/v21_auditoria_da_promocao.py

`promover_research` (passo 5d) sobe a prosa de `RESEARCH` para os campos de
tela. A guarda dele é tudo-ou-nada:

    if not r.get('CLIENT_SAFE') or any(r.get(c) for c in TELA):
        return 0

Basta UM campo de tela preenchido — e `PERMANENT_CAVEAT` é um deles — para que
NENHUMA prosa suba. Um boletim com ressalva declarada entra no acervo com
`WHAT_IT_IS = None`, e o extrator de pares não tem texto para ler.

    UM REGISTRO IGNORADO EM SILÊNCIO É PIOR QUE UM RECUSADO EM VOZ ALTA.

A REGRA QUE SEPARA OS CASOS — e é ela que esta auditoria testa
------------------------------------------------------------
A guarda protege contra SOBRESCREVER. Mas a guarda por campo já existe, uma
linha abaixo: `if res.get(origem) and not r.get(destino)`. A guarda de cima é
larga demais — recusa promover `o_que` porque `PERMANENT_CAVEAT` existe, e as
duas coisas não ocupam o mesmo lugar na tela.

    RESSALVA NÃO É DESCRIÇÃO. UMA NÃO PODE BLOQUEAR A OUTRA.

    DEVERIA_PROMOVER      → o DESTINO está vazio e a origem tem texto
    NAO_DEVERIA_PROMOVER  → o destino já está preenchido: nada mudaria
    UNKNOWN               → o destino está vazio, mas outro campo DESCRITIVO
                            já fala pela tela — promover duplicaria a leitura

Esta auditoria NÃO altera nada. Ela mede quantos registros mudariam, quantas
oportunidades poderiam mudar, e qual é o risco de cada grupo.
"""
import json
import os
import sys
from collections import Counter, defaultdict
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import v21_dominio_da_alegacao as DA  # noqa: E402

ING = os.path.join(ROOT, 'build', 'ITALY-REALITY-HANDOFF-V2.1', 'DESIGN-INGEST')
SAIDA = os.path.join(ROOT, 'data', 'samples', 'AUDITORIA-SOMBRA',
                     'V113-AUDITORIA-DA-PROMOCAO.json')

# Os campos de tela que a guarda larga consulta hoje.
TELA = ('WHAT_IT_IS', 'WHAT_IT_PROVES', 'WHAT_IT_DOES_NOT_PROVE',
        'INTERPRETATION', 'SO_WHAT', 'NOTE', 'CAVEAT', 'PERMANENT_CAVEAT',
        'INTERVENTION_GUIDANCE', 'LINK_MEANS', 'ROLE_EVIDENCE')

# Destes, os que DESCREVEM o registro. `PERMANENT_CAVEAT` e `CAVEAT` ressalvam;
# `LINK_MEANS` e `ROLE_EVIDENCE` explicam um vínculo. Nenhum descreve o fato.
DESCRITIVOS = ('WHAT_IT_IS', 'INTERPRETATION', 'SO_WHAT', 'NOTE',
               'INTERVENTION_GUIDANCE')

MAPA = {'o_que': 'WHAT_IT_IS', 'o_que_prova': 'WHAT_IT_PROVES',
        'o_que_nao_prova': 'WHAT_IT_DOES_NOT_PROVE'}


def colecoes():
    for a in sorted(os.listdir(ING)):
        if not a.endswith('.json') or a == 'APP-MANIFEST.json':
            continue
        d = json.load(open(os.path.join(ING, a), encoding='utf-8'))
        if isinstance(d, dict) and isinstance(d.get('RECORDS'), list):
            yield a, d['RECORDS']


def classificar(r):
    """→ (classe, campos que subiriam, o que bloqueia hoje)."""
    res = r.get('RESEARCH')
    if not r.get('CLIENT_SAFE') or not isinstance(res, dict):
        return None, [], []
    bloqueio = [c for c in TELA if r.get(c)]
    if not bloqueio:
        return None, [], []          # a guarda nem entra: já promove
    subiriam = [d for o, d in MAPA.items() if res.get(o) and not r.get(d)]
    if not subiriam:
        return 'NAO_DEVERIA_PROMOVER', [], bloqueio
    if any(c in DESCRITIVOS for c in bloqueio):
        return 'UNKNOWN', subiriam, bloqueio
    return 'DEVERIA_PROMOVER', subiriam, bloqueio


def main():
    linhas = []
    for arq, recs in colecoes():
        for r in recs:
            if not isinstance(r, dict) or not r.get('ID'):
                continue
            classe, subiriam, bloqueio = classificar(r)
            if not classe:
                continue
            linhas.append({'FILE': arq, 'ID': r['ID'],
                           'ENTITY_TYPE': r.get('ENTITY_TYPE'),
                           'CLASS': classe, 'WOULD_PROMOTE': subiriam,
                           'BLOCKED_BY': bloqueio,
                           'CROP_IDS': r.get('CROP_IDS') or [],
                           'REGION_IDS': r.get('REGION_IDS') or []})

    print('=' * 78)
    print('REGISTROS QUE A GUARDA LARGA ALCANCA: %d' % len(linhas))
    for k, n in Counter(x['CLASS'] for x in linhas).most_common():
        print('  %-24s %d' % (k, n))
    print('=' * 78)

    por_arq = defaultdict(Counter)
    for x in linhas:
        por_arq[x['FILE']][x['CLASS']] += 1
    print('\nPOR COLECAO')
    for a in sorted(por_arq):
        print('  %-36s %s' % (a, dict(por_arq[a])))

    sinais = [x for x in linhas if x['ENTITY_TYPE'] == 'FIELD_SIGNAL']
    print('\nSINAIS DE CAMPO — os unicos que o motor le como texto de par')
    for x in sinais:
        print('  %-20s %-22s subiria %s · bloqueado por %s'
              % (x['ID'], x['CLASS'], x['WOULD_PROMOTE'], x['BLOCKED_BY']))
        print('      culturas %s · regioes %s' % (x['CROP_IDS'], x['REGION_IDS']))

    print('\nRISCO, POR GRUPO')
    print('  DEVERIA_PROMOVER      texto novo na tela; nos sinais de campo, '
          'pares e direcoes novas — e por isso oportunidades novas.')
    print('  UNKNOWN               a tela ja tem descricao: promover duplicaria '
          'a leitura no cartao.')
    print('  NAO_DEVERIA_PROMOVER  nada mudaria: o destino ja esta cheio.')

    fora = {
        'COLLECTION': 'V113-AUDITORIA-DA-PROMOCAO',
        'SOURCE': 'build/ITALY-REALITY-HANDOFF-V2.1/DESIGN-INGEST · '
                  'regra de scripts/v21_dominio_da_alegacao.py',
        'CAPTURED_AT': date.today().isoformat(),
        'LAW': 'auditoria, nao correcao. Nenhum registro foi alterado.',
        'RULE_THAT_SEPARATES': (
            'a guarda larga recusa promover porque QUALQUER campo de tela '
            'existe; a guarda estreita, uma linha abaixo, ja impede '
            'sobrescrever. Ressalva nao e descricao, e uma nao pode bloquear '
            'a outra.'),
        'SCREEN_FIELDS_CHECKED': list(TELA),
        'DESCRIPTIVE_FIELDS': list(DESCRITIVOS),
        'TOTAL': len(linhas),
        'BY_CLASS': dict(Counter(x['CLASS'] for x in linhas)),
        'FIELD_SIGNALS': sinais,
        'RECORDS': linhas,
    }
    os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
    json.dump(fora, open(SAIDA, 'w', encoding='utf-8'), ensure_ascii=False,
              indent=1)
    print('\ngravado em %s' % os.path.relpath(SAIDA, ROOT))
    return 0


if __name__ == '__main__':
    sys.exit(main())
