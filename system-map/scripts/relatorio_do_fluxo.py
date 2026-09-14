#!/usr/bin/env python3
"""RELATORIO DO FLUXO — o que o sistema consegue contar hoje, e o que nao.

    python3 system-map/scripts/relatorio_do_fluxo.py

    SEM DADO NAO E ZERO. E NOT_INSTRUMENTED.

Um relatorio que mostra `0` onde ninguem mediu e pior do que nao existir: ele
convida a concluir que nada aconteceu. Este relatorio prefere ficar feio a
ficar bonito com silencio.

O QUE ELE LE
------------
So o que ja existe, hoje, neste repositorio: o ledger de coleta italiano
(`runs.ndjson` e `observations.ndjson`). Nao inventa telemetria, nao abre banco,
nao vai a rede.

O QUE ELE VAI ACHAR, E E O PONTO
--------------------------------
O ledger sabe RUN, SOURCE e CONTAGEM. Nao sabe ETAPA, CUSTO nem DURACAO — e por
isso essas colunas saem `NOT_INSTRUMENTED`, com o nome de quem teria de as
emitir. Esse buraco e o produto deste relatorio, nao um defeito dele.

    MODULE WORKS != EDGE WORKS != FLOW WORKS.

E A CONTA QUE TEM DE FECHAR
---------------------------
Para cada corrida, todo documento observado sai por uma porta com nome
(`NEW_DOCUMENT`, `SEEN_AGAIN`, `BASELINE_DOCUMENT`, ...). O que nao sai por
nenhuma e `UNACCOUNTED`, e e isso que se caca — nao o rendimento.
"""
import collections
import json
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401
import telemetria as t  # noqa: E402

LEDGER = os.path.join(RAIZ, 'data', 'collection-ledger', 'italy')
SAIDA = os.path.join(RAIZ, 'system-map', 'data', 'fluxo.generated.json')

# ⚠️ O QUE FALTA TEM DE TER NOME E DONO.
# «Nao instrumentado» sem dizer quem teria de emitir e uma queixa. Com o dono
# escrito, e uma tarefa.
NAO_INSTRUMENTADO = {
    'STAGE': ('o ledger regista a observacao, nao a etapa que a produziu. '
              'Quem teria de emitir: o coletor recorrente (coleta/*.mjs).'),
    'DURATION': ('ha STARTED_AT e FINISHED_AT por corrida, e nada por etapa. '
                 'Quem teria de emitir: cada executor.'),
    'COST': ('nenhuma rota italiana e paga hoje, e por isso ninguem emite '
             'custo. Quando houver rota paga, quem teria de emitir e o '
             'executor dela.'),
    'EXECUTOR': ('o ledger nao guarda o nome de quem correu. Quem teria de '
                 'emitir: o orquestrador, em pedido/receitas.py.'),
}


def _linhas(nome):
    caminho = os.path.join(LEDGER, nome)
    if not os.path.exists(caminho):
        return []
    fora = []
    with open(caminho, encoding='utf-8') as f:
        for linha in f:
            linha = linha.strip()
            if linha:
                try:
                    fora.append(json.loads(linha))
                except ValueError:
                    continue
    return fora


def _duracao_ms(corrida):
    """Só se as duas pontas existirem. Meia medida não é medida."""
    import datetime as dt
    a, b = corrida.get('STARTED_AT'), corrida.get('FINISHED_AT')
    if not a or not b:
        return None
    try:
        fa = dt.datetime.fromisoformat(a.replace('Z', '+00:00'))
        fb = dt.datetime.fromisoformat(b.replace('Z', '+00:00'))
    except ValueError:
        return None
    return int((fb - fa).total_seconds() * 1000)


def relatorio():
    corridas = _linhas('runs.ndjson')
    obs = _linhas('observations.ndjson')

    por_corrida = collections.defaultdict(list)
    for o in obs:
        por_corrida[o.get('RUN_ID')].append(o)

    linhas = []
    for c in corridas:
        rid = c.get('RUN_ID')
        meus = por_corrida.get(rid, [])
        destinos = collections.Counter(o.get('OBSERVATION_RESULT')
                                       for o in meus)
        # Cada observacao sai por uma porta com nome. Se alguma nao tiver
        # resultado, ela e UNACCOUNTED — e e esse o numero que importa.
        sem_porta = sum(1 for o in meus if not o.get('OBSERVATION_RESULT'))
        linhas.append({
            'RUN_ID': rid,
            'STARTED_AT': c.get('STARTED_AT'),
            'FINISHED_AT': c.get('FINISHED_AT'),
            'DURATION_MS': _duracao_ms(c),
            'EGRESS_COUNTRY': c.get('VPN_COUNTRY'),
            'CODE_VERSION': c.get('COLLECTOR_VERSION'),
            'POLICY_VERSION': c.get('SOURCE_CONTRACT_VERSION'),
            'INPUT_GRAIN': 'documento observado',
            'OUTPUT_GRAIN': 'documento observado',
            'INPUT_COUNT': len(meus),
            'DESTINOS': dict(sorted(destinos.items())),
            'UNACCOUNTED_INPUT': sem_porta,
            'FONTES': len({o.get('SOURCE_ID') for o in meus}),
            'STAGE': 'NOT_INSTRUMENTED',
            'COST': 'NOT_INSTRUMENTED',
            'EXECUTOR': 'NOT_INSTRUMENTED',
        })

    por_fonte = collections.Counter(o.get('SOURCE_ID') for o in obs)
    por_destino = collections.Counter(o.get('OBSERVATION_RESULT') for o in obs)
    por_mime = collections.Counter(o.get('MIME_ASSINATURA') for o in obs)
    por_hora = collections.Counter(
        (o.get('CAPTURED_AT') or '')[:13] for o in obs if o.get('CAPTURED_AT'))

    return {
        'SCHEMA': 'fluxo/v1',
        'CONTRATO': t.CONTRATO,
        'O_QUE_E': ('o que o sistema consegue contar HOJE sobre o proprio '
                    'fluxo, lendo so o que ja existe no repositorio.'),
        'DE_ONDE_VEM': 'data/collection-ledger/italy/{runs,observations}.ndjson',
        'SEM_DADO_NAO_E_ZERO': (
            'onde ninguem mediu, escreve-se NOT_INSTRUMENTED. Um relatorio que '
            'mostra 0 onde ninguem mediu convida a concluir que nada '
            'aconteceu — e pior do que nao existir.'),
        'CORRIDAS': len(corridas),
        'OBSERVACOES': len(obs),
        'POR_CORRIDA': linhas,
        'POR_FONTE': dict(sorted(por_fonte.items())),
        'POR_DESTINO': dict(sorted(por_destino.items())),
        'POR_MIME': dict(sorted(por_mime.items())),
        'POR_HORA': dict(sorted(por_hora.items())),
        'POR_ROTA': {'RC-9': len(obs),
                     'NOTA': ('todo este ledger e da RC-9 (GIT_LEDGER), que e '
                              'DIVIDA e nao estrada a fechar. As outras rotas '
                              'nao emitem nada — nao e que tenham emitido '
                              'zero.')},
        'POR_ETAPA': {'ESTADO': 'NOT_INSTRUMENTED',
                      'PORQUE': NAO_INSTRUMENTADO['STAGE']},
        'POR_EXECUTOR': {'ESTADO': 'NOT_INSTRUMENTED',
                         'PORQUE': NAO_INSTRUMENTADO['EXECUTOR']},
        'CUSTO': {'ESTADO': 'NOT_INSTRUMENTED',
                  'PORQUE': NAO_INSTRUMENTADO['COST']},
        'O_QUE_FALTA_INSTRUMENTAR': NAO_INSTRUMENTADO,
        'A_CONTA_FECHA': all(l['UNACCOUNTED_INPUT'] == 0 for l in linhas),
        'PORQUE_A_CONTA_IMPORTA_MAIS_QUE_O_RENDIMENTO': (
            '100% NAO PRECISA CHEGAR — 100% PRECISA SER EXPLICADO. O que se '
            'caca e o item sem destino com nome, nao o numero baixo.'),
    }


def main():
    r = relatorio()
    with open(SAIDA, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(r, f, ensure_ascii=False, indent=1)
        f.write('\n')
    print('CORRIDAS %d · OBSERVACOES %d · FONTES %d'
          % (r['CORRIDAS'], r['OBSERVACOES'], len(r['POR_FONTE'])))
    print('')
    print('  %-34s %5s %6s %s' % ('RUN_ID', 'ENTR', 'S/PORTA', 'DURACAO'))
    for l in r['POR_CORRIDA']:
        print('  %-34s %5d %6d %s'
              % (l['RUN_ID'], l['INPUT_COUNT'], l['UNACCOUNTED_INPUT'],
                 ('%d ms' % l['DURATION_MS']) if l['DURATION_MS'] is not None
                 else 'NOT_INSTRUMENTED'))
    print('')
    print('  destinos: %s' % r['POR_DESTINO'])
    print('  a conta fecha: %s' % ('SIM' if r['A_CONTA_FECHA'] else 'NAO'))
    print('')
    print('  NOT_INSTRUMENTED: etapa · executor · custo')
    print('  (sem dado nao e zero — cada um diz quem teria de emitir)')
    print('\nescrito em %s' % os.path.relpath(SAIDA, RAIZ).replace('\\', '/'))
    return 0


if __name__ == '__main__':
    sys.exit(main())
