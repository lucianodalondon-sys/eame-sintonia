#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SOC3→SOC4 · «O YOUTUBE É SEMPRE O SCRAP», MEDIDO NOS 50 CANAIS DA TABELA.

    py provas/roteamento_youtube_proposta.py

`pedido/receitas.py::resolver` escolhia o executor pelo TERRITÓRIO do pedido, e
`scrap-colheita` só estava registado em T8 e T9. Desde a SOC4 o `resolver` chama
`receitas.promover_o_scrap`: uma fase que o registo do Scrap declara em
`serve_fases` abre o Scrap em QUALQUER território.

Esta prova mede os 50 canais da tabela do coletor duas vezes:

    SEM_PROMOCAO   o `resolver` com `promover_o_scrap` desligado (o de antes);
    COM_PROMOCAO   o `resolver` tal como está na árvore.

    A PLATAFORMA DECIDE O EXECUTOR; O TERRITÓRIO DECIDE O ASSUNTO.

Sem rede, sem gasto, sem correr nenhum executor: só planos.
"""
import json
import os
import sys
from collections import Counter

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in ('pedido', 'coleta', 'leis', ''):
    sys.path.insert(0, os.path.join(RAIZ, _p) if _p else RAIZ)

import pedido as PD      # noqa: E402
import receitas as R     # noqa: E402

TABELA = os.path.join(RAIZ, 'regras', 'italy_contracts_onboarded.json')


def canais():
    d = json.load(open(TABELA, encoding='utf-8'))
    return [x for x in d['FONTES'] if x.get('SOURCE_NATIVE_ID_KIND') == 'YOUTUBE_CHANNEL_ID']


def plano(sid, territorio, canal, com_promocao=True):
    p = PD.Pedido(alvo=territorio, filtros={'fase': 'canal-youtube', 'fonte': sid,
                                            'canal_id': canal, 'pais': 'IT'})
    original = R.promover_o_scrap
    if not com_promocao:
        R.promover_o_scrap = lambda execs, fase, executores=None: execs
    try:
        execs = R.resolver(p).executores
    finally:
        R.promover_o_scrap = original
    primeiro = execs[0] if execs else {}
    sobra = {'fonte', 'canal_id'} - (R.filtros_consumidos(primeiro) if primeiro else set())
    return (primeiro.get('id') or 'NENHUM',
            'FILTRO_NAO_CONSUMIDO=%s' % ','.join(sorted(sobra)) if sobra else 'OK')


def medir():
    return [{'SOURCE_ID': x['SOURCE_ID'], 'TERRITORY': x['TERRITORY'],
             'SEM_PROMOCAO': plano(x['SOURCE_ID'], x['TERRITORY'], x['SOURCE_NATIVE_ID'], False),
             'COM_PROMOCAO': plano(x['SOURCE_ID'], x['TERRITORY'], x['SOURCE_NATIVE_ID'], True)}
            for x in canais()]


def main():
    linhas = medir()
    for l in linhas:
        print('%-11s %-4s sem=%-22s %-34s com=%-15s %s' % (
            l['SOURCE_ID'], l['TERRITORY'], l['SEM_PROMOCAO'][0], l['SEM_PROMOCAO'][1],
            l['COM_PROMOCAO'][0], l['COM_PROMOCAO'][1]))
    print('SEM_PROMOCAO ', dict(Counter(l['SEM_PROMOCAO'] for l in linhas)))
    print('COM_PROMOCAO ', dict(Counter(l['COM_PROMOCAO'] for l in linhas)))
    iguais = all(R.resolver(PD.Pedido(alvo=t, filtros={})).executores == list(R.EXECUTORES.get(t, []))
                 for t in R.EXECUTORES)
    print('SEM_FASE_INALTERADO', iguais)
    return 0


if __name__ == '__main__':
    sys.exit(main())
