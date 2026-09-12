#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O ADAPTER DO SCRAP PARA A PORTA CANÔNICA — traduz, e mais nada.

    python3 coleta/scrap_colheita.py --run-id=<RUN_ID> --fonte=<SOURCE_ID> <FASE>

POR QUE ESTE FICHEIRO EXISTE
-----------------------------
Medido nesta árvore, antes desta missão:

    orquestrador/orquestrador.py    é o dono único da orquestração
    coleta/scrap_executor.py        é o executor canônico do SCRAP
    ARESTA ENTRE OS DOIS            NÃO EXISTIA

O SCRAP tinha uma porta (`COLLECT`), tetos, guarda de gasto e preservação de
RAW — e ninguém a chamava a partir de um `COLLECTION_REQUEST`. O disparador ia
direto a `coleta/social_scrap.py`, que corria `COLLECT` e parava ali: o que a
corrida colheu nunca chegava a `coleta/ingresso.py`, e portanto nunca chegava à
admissão.

    MODULE EXISTS != EDGE EXISTS != FLOW EXISTS.

Este ficheiro é a aresta. Ele **não** é um segundo orquestrador: não decide que
missão correr, que fonte colher, que rota usar nem que ator chamar. Recebe uma
fase já decidida, chama `COLLECT` uma vez, e declara o que voltou.

    AS QUATRO TRADUÇÕES

      1  corre `scrap_executor.COLLECT` com o RUN_ID que o orquestrador cunhou
      2  lê o que a corrida devolveu — objetos e trace
      3  separa COLHEITA de SUPORTE pela espécie DECLARADA (COL-LAW-505)
      4  escreve o envelope no balcão, na língua da porta

    E O QUE ELE NÃO PODE FAZER

      cunhar RUN_ID · inventar SOURCE_ID · fabricar DOCUMENT_ID ·
      derivar RAW_OBSERVATION_ID · escolher ator, rota ou provider ·
      julgar tema, relevância ou qualidade

O `--run-id` É OBRIGATÓRIO, E O `--fonte` TAMBÉM
-------------------------------------------------
O primeiro, porque `RUN != PROVIDER RUN`: se este adapter cunhasse corrida, a
corrida do orquestrador e a da coleta eram duas, e o `raw_asset` ficaria ligado
a uma que o manifesto não conhece. É a mesma lei que `coleta/italy_executor.py`
já obedece.

O segundo, porque **o SCRAP não conhece `SOURCE_ID`**. Medido: o envelope
canônico de `coleta/social_envelope.py` tem `PLATFORM`, `SOURCE_ACCOUNT`,
`NATIVE_ID` e `URL` — e nenhum deles é uma fonte provada. Derivar `SOURCE_ID` de
qualquer um seria fabricar identidade.

    URL NÃO É SOURCE_ID. HANDLE NÃO É SOURCE_ID. PLATAFORMA NÃO É FONTE.

A identidade desce COM O PEDIDO, e nunca sobe da observação. Quem pede nomeia a
fonte do atlas; este adapter carimba-a e diz que a carimbou. Sem `--fonte`, ele
NÃO inventa: declara zero colheita, escreve porquê, e tudo o que a corrida
produziu sai como SUPORTE — que nunca atravessa a porta.

    O QUE NÃO SE DECLAROU NÃO ENTRA.

O BALCÃO NÃO É ARQUIVO
----------------------
`data/colheita/scrap/` é reescrito a cada corrida, e não acumulado — a mesma
escolha (e a mesma razão) de `coleta/italy_executor.py`: um balcão que guarda o
que já entregou entrega a colheita da corrida anterior outra vez.
"""
from __future__ import annotations

import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in ('coleta', 'leis', 'medidas', 'ferramentas', 'guarda', 'regras', ''):
    sys.path.insert(0, os.path.join(RAIZ, _p) if _p else RAIZ)

import retorno_da_coleta as rc                                    # noqa: E402
import scrap_executor as sx                                       # noqa: E402

EXECUTOR_ID = 'scrap-colheita'
EXECUTOR_VERSION = 'adapter-v1'

BALCAO = os.path.join('data', 'colheita', 'scrap')
ENVELOPE = os.path.join(BALCAO, 'ENVELOPE.json')

#: As fases que este adapter sabe pedir ao `COLLECT`. O nome vem do disparador;
#: a plataforma, a capacidade e os argumentos vivem AQUI, em Python versionado.
#:
#:     UM DISPARADOR QUE ESCOLHE A CAPACIDADE ESCOLHE O QUE SE COLHE.
FASES = {
    'janela':         ('INSTAGRAM', 'instagram.profile.discovery', {'camada': 'tudo'}),
    'janela-perfis':  ('INSTAGRAM', 'instagram.profile.discovery', {'camada': 'perfis'}),
    'janela-objetos': ('INSTAGRAM', 'instagram.profile.discovery', {'camada': 'objetos'}),
}

#: O que o envelope canônico do SCRAP responde, com o nome que a porta usa.
#: `coleta/ingresso.py::DO_COLETOR` tem treze campos; o SCRAP responde a estes,
#: e os outros chegam em falta — e a porta escreve «NAO SEI», que é honesto.
#:
#:     TRADUZIR NOME E FORMA É TRABALHO DE ADAPTER.
#:     PREENCHER UM CAMPO QUE A OBSERVAÇÃO NÃO TROUXE NÃO É.
DO_SCRAP_PARA_A_PORTA = {
    'URL': 'SOURCE_URL',
    'COUNTRY_SCOPE': 'COUNTRY_SCOPE',
    'SOURCE_LOCATION': 'SOURCE_LOCATION',
    'LANGUAGE': 'ITEM_LANGUAGE',
    'PUBLISHED_AT': 'PUBLISHED_AT',
    'COLLECTED_AT': 'OBSERVED_AT',
}

DESCONHECIDO = 'UNKNOWN'


def _limpo(v):
    """→ o valor, ou None quando ele é uma confissão de ausência."""
    s = str(v or '').strip()
    return None if not s or s in (DESCONHECIDO, rc.NAO_SEI) else v


def unidade(objeto, *, run_id, fonte):
    """Um objeto do SCRAP na língua da porta. → a unidade de COLHEITA.

    `DOCUMENT_ID` sai `NAO SEI` de propósito e por lei: o SCRAP não tem
    identidade documental para dar, e um identificador tirado do `sha` ou do
    caminho seria uma mentira com forma de dado.

        UNKNOWN PERMANECE UNKNOWN.
    """
    fora = {'ESPECIE': rc.COLHEITA, 'RUN_ID': run_id, 'SOURCE_ID': fonte,
            'DOCUMENT_ID': rc.NAO_SEI}
    for de, para in DO_SCRAP_PARA_A_PORTA.items():
        v = _limpo(objeto.get(de))
        if v is not None:
            fora[para] = v
    # O corpo da observação viaja inteiro: a porta assina o que recebeu, e
    # normalizar aqui faria a impressão digital ser de outra coisa.
    #
    #     RAW BEFORE NORMALIZATION.
    fora['OBSERVACAO'] = objeto
    # Sem ficheiro separado: a observação É o item, e isso diz-se.
    fora['PAYLOAD'] = {'ONDE': '', 'ESTADO': rc.PAYLOAD_NAO_SE_APLICA}
    return fora


def suporte_do_trace(trace):
    """O que a corrida produziu e que NÃO é colheita. → lista de suporte.

    O trace é a prova da execução — é `RUN_RECEIPT`, e nunca observação.
    Declará-lo aqui é o que impede que ele entre pela porta por distração.

        O RECIBO DE UMA COLHEITA NÃO É A COLHEITA.
    """
    return [{'ESPECIE': rc.RUN_RECEIPT, 'ONDE': '',
             'O_QUE_E': 'o trace da corrida do SCRAP: rota escolhida, estado, '
                        'tetos e custo. Prova da execução, não material observado.',
             'PAYLOAD': {'ONDE': '', 'ESTADO': rc.PAYLOAD_NAO_SE_APLICA},
             'RESUMO': {k: trace.get(k) for k in
                        ('RESULT', 'EXECUTOR_ID', 'EXECUTION_MODE',
                         'NETWORK_REQUESTS_USED', 'COST_STATE')
                        if k in trace}}]


def colher(fase, *, run_id, fonte, banco=None, **extra):
    """Uma fase, uma corrida do `COLLECT`. → o envelope do COL-LAW-505.

    NÃO levanta por rota recusada: recusa é resultado de medição, e desce como
    estado. O envelope diz o que a corrida devolveu — inclusive «nada, e porquê».
    """
    plataforma, capacidade, fixos = FASES[fase]
    objetos, trace = sx.COLLECT(platform=plataforma, capability=capacidade,
                                run_id=run_id, banco=banco,
                                **dict(fixos, **extra))
    objetos = objetos or []
    estado = rc.SUCCESS if trace.get('RESULT') in (None, 'OK', 'SUCCESS') else rc.PARTIAL
    erros = []
    porque_zero = ''

    if not fonte:
        # ── SEM FONTE PROVADA NÃO HÁ COLHEITA, E ISSO NÃO É UM ERRO ────────
        # É a resposta certa. O SCRAP não sabe de que fonte do atlas veio o que
        # colheu, e inventá-la seria fabricar identidade.
        porque_zero = (
            'o pedido não nomeou fonte. O SCRAP observa PLATAFORMAS e a porta '
            'fala em FONTES; sem o SOURCE_ID vindo do pedido, estas %d '
            'observações são CANDIDATAS e não observações de uma fonte provada. '
            'URL não é SOURCE_ID.' % len(objetos))
        colheita = []
        suporte = suporte_do_trace(trace) + [
            {'ESPECIE': rc.ESPECIE_DESCONHECIDA, 'ONDE': '',
             'O_QUE_E': 'o que a corrida observou, sem fonte provada que o ancore',
             'PAYLOAD': {'ONDE': '', 'ESTADO': rc.PAYLOAD_NAO_SE_APLICA},
             'QUANTOS': len(objetos)}]
    else:
        colheita = [unidade(o, run_id=run_id, fonte=fonte) for o in objetos]
        suporte = suporte_do_trace(trace)
        if not colheita:
            porque_zero = ('a corrida correu e não observou nada. ZERO LEGÍTIMO '
                           'NÃO É FALHA: %s' % (trace.get('RESULT') or 'sem estado'))

    envelope = {
        'RUN_ID': run_id, 'EXECUTOR_ID': EXECUTOR_ID,
        'EXECUTOR_VERSION': EXECUTOR_VERSION, 'ESTADO': estado,
        'COLHEITA': colheita, 'SUPORTE': suporte, 'ERROS': erros,
        'FASE': fase, 'PLATFORM': plataforma, 'CAPABILITY': capacidade,
        'SOURCE_ID_DO_PEDIDO': fonte or rc.NAO_SEI,
    }
    if porque_zero:
        envelope['PORQUE_ZERO_COLHEITA'] = porque_zero
    return envelope


def escrever(envelope, raiz=RAIZ):
    alvo = os.path.join(raiz, BALCAO)
    os.makedirs(alvo, exist_ok=True)
    caminho = os.path.join(raiz, ENVELOPE)
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(json.dumps(envelope, ensure_ascii=False, indent=1,
                           sort_keys=True) + '\n')
    return caminho


def main(argv=None):
    args = list(argv if argv is not None else sys.argv[1:])
    run_id = fonte = None
    resto = []
    for a in args:
        if a.startswith('--run-id='):
            run_id = a.split('=', 1)[1].strip()
        elif a.startswith('--fonte='):
            fonte = a.split('=', 1)[1].strip() or None
        else:
            resto.append(a)
    # Os filtros chegam POSICIONAIS, sem nome: e assim que o orquestrador
    # traduz `argumentos_de_filtros` para linha de comando, e e assim que o
    # `comunicacao-publica` ja os recebe. A ordem esta na receita.
    if resto and resto[0] in FASES:
        fase = resto[0]
        if fonte is None and len(resto) > 1:
            fonte = resto[1].strip() or None
    else:
        fase = resto[0] if resto else 'janela'
    if fase not in FASES:
        print('FASE_DESCONHECIDA=%s · as que existem: %s'
              % (fase, ', '.join(sorted(FASES))))
        return 2
    if not run_id:
        # Cunhar um aqui daria DUAS corridas canônicas para o mesmo acto.
        print('SEM_RUN_ID=o orquestrador é quem cunha a corrida; este adapter '
              'não a inventa')
        return 2

    envelope = colher(fase, run_id=run_id, fonte=fonte)
    caminho = escrever(envelope)
    mal = rc.conferir(envelope, RAIZ)

    print('SCRAP_COLHEITA')
    print('  fase          %s' % fase)
    print('  run_id        %s' % run_id)
    print('  source_id     %s' % (fonte or rc.NAO_SEI))
    print('  colheita      %d' % len(envelope['COLHEITA']))
    print('  suporte       %d' % len(envelope['SUPORTE']))
    print('  envelope      %s' % os.path.relpath(caminho, RAIZ))
    if envelope.get('PORQUE_ZERO_COLHEITA'):
        print('  porque zero   %s' % envelope['PORQUE_ZERO_COLHEITA'])
    for m in mal:
        print('  CONTRATO      %s' % m)
    return 0 if not mal else 1


if __name__ == '__main__':
    sys.exit(main())
