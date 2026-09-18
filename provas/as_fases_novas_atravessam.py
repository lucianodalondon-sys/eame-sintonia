#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AS IRMAS DA FORMA CHEGAM A PORTA — o caminho canonico das fases novas.

    py provas/as_fases_novas_atravessam.py

NAO mede aquisicao: isso a prova da capacidade ja mediu, e uma capacidade
`PROVEN` nao volta a UNKNOWN por passar tempo. Mede a ARESTA que faltava:

    PEDIDO -> ORQUESTRADOR -> scrap_colheita -> scrap_executor -> ENVELOPE

com a rota substituida por um duble, porque o que esta em causa aqui e o
CAMINHO e nao a rede. Uma prova que precisa de internet para dizer se uma
tabela tem tres linhas mede a internet, nao a tabela.

    DUBLE NA ROTA E HONESTO QUANDO O QUE SE MEDE E O CAMINHO.
    DUBLE NO RESULTADO SERIA FABRICAR OBSERVACAO.

As quatro perguntas, e nenhuma e de opiniao:

  1. a fase existe e o orquestrador sabe abri-la (`serve_fases`);
  2. o filtro de cada fase desce com o NOME que a rota espera;
  3. um nome que nao e da fase e RECUSADO, e nao engolido;
  4. a especie declarada manda: COLHEITA atravessa, CATALOG sai por SUPORTE.
"""
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
sys.path.insert(0, os.path.join(RAIZ, 'coleta'))
sys.path.insert(0, os.path.join(RAIZ, 'pedido'))
sys.path.insert(0, os.path.join(RAIZ, 'leis'))
sys.path.insert(0, RAIZ)

import scrap_colheita as sc            # noqa: E402
import retorno_da_coleta as rc         # noqa: E402
import receitas                        # noqa: E402

FALHAS = []
CONTA = [0]


def diz(ok, o_que, detalhe=''):
    CONTA[0] += 1
    print('  %s  %-58s %s' % ('PASS' if ok else 'FAIL', o_que, detalhe))
    if not ok:
        FALHAS.append(o_que)


# ── AS TRES FASES QUE ESTA MISSAO LIGOU ────────────────────────────────────
# `contas-bluesky` e CATALOG de proposito: discovery devolve entidades DE ONDE
# SE PODE COLHER, e nao o que elas publicaram.
NOVAS = {
    'canal-telegram': ('TELEGRAM', 'telegram.channel.incremental',
                       rc.COLHEITA, {'canal': 'canal'}),
    'tag-mastodon':   ('MASTODON', 'mastodon.hashtag.search',
                       rc.COLHEITA, {'instancia': 'instancia', 'tag': 'tag'}),
    'contas-bluesky': ('BLUESKY', 'bluesky.account.discovery',
                       rc.CATALOG, {'termo': 'termo'}),
}


def main():
    print('=' * 74)
    print('AS IRMAS DA FORMA CHEGAM A PORTA')
    print('=' * 74)

    # ── 1 · A FASE EXISTE, E A RECEITA SABE ABRI-LA ────────────────────────
    print('\n1 · a fase existe e o orquestrador sabe pedi-la')
    receita = None
    for ex in receitas.EXECUTORES.get('T9', []):
        if ex.get('id') == 'scrap-colheita':
            receita = ex
    diz(receita is not None, 'a receita `scrap-colheita` existe')
    servidas = set(receita.get('serve_fases') or ()) if receita else set()
    abertos = set(receita.get('filtros_nomeados') or ()) if receita else set()
    for fase, (plat, cap, especie, nomeados) in sorted(NOVAS.items()):
        diz(fase in sc.FASES, 'FASES declara `%s`' % fase,
            '%s/%s' % (plat, cap))
        diz(fase in servidas, '`serve_fases` inclui `%s`' % fase)
        diz(fase in sc.NOMEADOS, 'NOMEADOS declara `%s`' % fase)

    # ── 2 · O FILTRO DESCE COM O NOME QUE A ROTA ESPERA ────────────────────
    # Nao basta o nome existir: ele tem de estar aberto na receita, senao o
    # orquestrador nunca o poe na linha de comando.
    print('\n2 · cada filtro desce pelo nome da sua propria rota')
    import inspect
    import scrap_registo as reg
    reg.carregar_adaptadores()
    for fase, (plat, cap, especie, nomeados) in sorted(NOVAS.items()):
        d = reg._MAPA.get((plat, cap)) or {}
        alvo = d.get('ROTA')
        params = set(inspect.signature(alvo).parameters) if alvo else set()
        for publico, interno in nomeados.items():
            diz(publico in abertos,
                '`%s` esta aberto na receita' % publico, fase)
            diz(interno in params,
                '`%s` e parametro real da rota' % interno,
                '%s%s' % (cap, sorted(params - {'run_id', 'country_scope'})))

    # ── 3 · UM NOME FORA DA FASE E RECUSADO, E NAO ENGOLIDO ────────────────
    # `telegram` nao aceita `limit`. Se a fase o engolisse, a corrida daria
    # verde com um argumento que ninguem usou.
    print('\n3 · um nome que nao e da fase e recusado')
    diz('limit' not in sc.NOMEADOS['canal-telegram'],
        '`canal-telegram` NAO aceita `limit`',
        'a assinatura de telegram_canal nao o tem')
    diz('handle' not in sc.NOMEADOS['canal-telegram'],
        '`canal-telegram` NAO herdou `handle` do vizinho')
    diz('canal' not in sc.NOMEADOS['canario-bluesky'],
        '`canario-bluesky` NAO ganhou `canal`',
        'a fase antiga ficou como estava')

    # ── 4 · A ESPECIE DECLARADA MANDA ──────────────────────────────────────
    print('\n4 · a especie decide quem atravessa a porta')
    for fase, (plat, cap, especie, _n) in sorted(NOVAS.items()):
        real = sc.FASES[fase][3]
        diz(real == especie, '`%s` declara %s' % (fase, especie), real)
    diz(sc.FASES['contas-bluesky'][3] == rc.CATALOG,
        'discovery e CATALOG, e nao COLHEITA',
        'DISCOVERY != CONTENT')
    diz(rc.COLHEITA in rc.ENTRAM_NO_INGRESSO
        and rc.CATALOG not in rc.ENTRAM_NO_INGRESSO,
        'so COLHEITA atravessa o ingresso',
        'CATALOG sai por SUPORTE')

    # ── 5 · SOURCE_ID NAO SE FABRICA DO ENDERECO ───────────────────────────
    print('\n5 · a identidade vem do pedido, nunca do endereco')
    for fase, (_p, _c, _e, nomeados) in sorted(NOVAS.items()):
        maus = [n for n in nomeados if n in ('fonte', 'source_id', 'SOURCE_ID')]
        diz(not maus, '`%s` nao trata o endereco como fonte' % fase,
            'CANAL/TAG/TERMO SAO ENDERECOS')
    diz('fonte' in (receita.get('argumentos_de_filtros') or ()),
        '`--fonte` continua a descer do pedido',
        receita.get('argumentos_de_filtros'))

    print('\n' + '=' * 74)
    print('TESTES = %d · FALHAS = %d' % (CONTA[0], len(FALHAS)))
    print('=' * 74)
    return 1 if FALHAS else 0


if __name__ == '__main__':
    raise SystemExit(main())
