#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SOC3 · PROPOSTA — «O YOUTUBE É SEMPRE O SCRAP», MEDIDA SEM APLICAR.

    py provas/roteamento_youtube_proposta.py

`pedido/receitas.py::resolver` escolhe o executor pelo TERRITÓRIO do pedido
(`EXECUTORES[p.alvo]`), e `scrap-colheita` só está registado em T8 e T9. Um
pedido de `fase=canal-youtube` para uma fonte de T2, T5, T7, T10, T11 ou T12 não
encontra quem o sirva: o orquestrador abre `executores[0]`, que não consome a
fase, e o filtro morre em `FILTRO_NAO_CONSUMIDO`.

Esta prova NÃO muda `pedido/receitas.py` — o writeset dele é do engenheiro do
Scrap (`scrap-portas-v1`). Ela mede os 50 canais da tabela do coletor duas vezes:

    HOJE      com o `resolver` que está na árvore;
    PROPOSTA  com o `resolver` embrulhado em `promover_o_scrap`, o bloco EXACTO
              que se propõe colar no fim do `resolver` (ver RELATORIO-SOC3).

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


# ── O BLOCO PROPOSTO (colar no fim de `resolver`, antes do `return Plano`) ──
def promover_o_scrap(execs, fase, executores=None):
    """Se a fase pedida é uma fase do Scrap, o executor do Scrap vem primeiro —
    em QUALQUER território. Não inventa fase: a lista é a que o próprio registo
    `scrap-colheita` declara em `serve_fases`. Um pedido sem fase, ou com uma fase
    que não é do Scrap, fica exactamente como estava."""
    executores = R.EXECUTORES if executores is None else executores
    scrap = next((e for e in executores.get('T9', []) if e.get('id') == 'scrap-colheita'), None)
    if not scrap or fase not in (scrap.get('serve_fases') or ()):
        return execs
    return [scrap] + [e for e in execs if e.get('id') != 'scrap-colheita']


def canais():
    d = json.load(open(TABELA, encoding='utf-8'))
    return [x for x in d['FONTES'] if x.get('SOURCE_NATIVE_ID_KIND') == 'YOUTUBE_CHANNEL_ID']


def plano(sid, territorio, canal, proposta):
    p = PD.Pedido(alvo=territorio, filtros={'fase': 'canal-youtube', 'fonte': sid,
                                            'canal_id': canal, 'pais': 'IT'})
    pl = R.resolver(p)
    execs = promover_o_scrap(pl.executores, 'canal-youtube') if proposta else pl.executores
    primeiro = execs[0] if execs else {}
    consome = R.filtros_consumidos(primeiro) if primeiro else set()
    sobra = {'fonte', 'canal_id'} - consome
    return (primeiro.get('id') or 'NENHUM',
            'FILTRO_NAO_CONSUMIDO=%s' % ','.join(sorted(sobra)) if sobra else 'OK')


def medir():
    linhas = []
    for x in canais():
        sid, t, canal = x['SOURCE_ID'], x['TERRITORY'], x['SOURCE_NATIVE_ID']
        hoje, proposta = plano(sid, t, canal, False), plano(sid, t, canal, True)
        linhas.append({'SOURCE_ID': sid, 'TERRITORY': t, 'HOJE': hoje, 'PROPOSTA': proposta})
    return linhas


def main():
    linhas = medir()
    for l in linhas:
        print('%-11s %-4s hoje=%-22s %-34s proposta=%-15s %s' % (
            l['SOURCE_ID'], l['TERRITORY'], l['HOJE'][0], l['HOJE'][1], l['PROPOSTA'][0], l['PROPOSTA'][1]))
    print('HOJE     ', dict(Counter(l['HOJE'] for l in linhas)))
    print('PROPOSTA ', dict(Counter(l['PROPOSTA'] for l in linhas)))
    # E o que NÃO pode mudar: um pedido sem fase continua igual em todo território.
    iguais = all(R.resolver(PD.Pedido(alvo=t, filtros={})).executores
                 == promover_o_scrap(R.resolver(PD.Pedido(alvo=t, filtros={})).executores, '')
                 for t in R.EXECUTORES)
    print('SEM_FASE_INALTERADO', iguais)
    return 0


if __name__ == '__main__':
    sys.exit(main())
