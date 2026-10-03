#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RED TEAM do wiring YouTube — doze ataques, e nenhum pode passar.

    py provas/red_team_wiring_youtube.py

Nao repete a prova de aquisicao: a C2 mediu a YouTube Data API v3 e uma
capacidade PROVEN nao volta a UNKNOWN por passar tempo. Ataca a ARESTA NOVA
— a que esta missao acrescentou — e as confusoes que ela torna possiveis.

    COMPOSICAO DA PROVA, declarada:
      aquisicao   -> prova historica (CENSO-DOS-ACTORS-E-CUSTO-V1)
      credencial  -> wiring do secret em scrap-social.yml:311
      ARESTA      -> esta prova, com duble no transporte

O ataque central e o que originou a missao:

    CREDENCIAL AUSENTE NESTE PROCESSO != CREDENCIAL AUSENTE NO SISTEMA.

Nenhum segredo e lido, impresso, medido em comprimento ou derivado. O unico
valor usado e o literal `FIXTURE-NAO-E-SEGREDO`, que nao abre nada.
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

BLOQUEIOS = []
N = [0]

#: Nao e segredo e nao abre nada. Existe so para provar que o estado muda com
#: a PRESENCA da variavel, e nunca com o seu valor.
FIXTURE = 'FIXTURE-NAO-E-SEGREDO'

OFICIAIS = ('busca-youtube', 'canal-youtube', 'video-youtube',
            'comentarios-youtube')


def ataque(n, o_que, defendido, detalhe=''):
    N[0] += 1
    print('  %s  %-56s %s' % ('DEFENDIDO' if defendido else 'PASSOU!!!',
                              o_que, detalhe))
    if not defendido:
        BLOQUEIOS.append('%d · %s' % (n, o_que))


def main():
    print('=' * 76)
    print('RED TEAM — O WIRING OFICIAL DO YOUTUBE')
    print('=' * 76)

    receita = None
    for ex in receitas.EXECUTORES.get('T9', []):
        if ex.get('id') == 'scrap-colheita':
            receita = ex
    servidas = set(receita.get('serve_fases') or ())

    # ── 1 · A FASE CHAMA A CAPACIDADE ERRADA ───────────────────────────────
    print('\n1-4 · cada fase chama a sua propria capacidade')
    esperado = {
        'busca-youtube': 'youtube.search',
        'canal-youtube': 'youtube.channel.discovery',
        'video-youtube': 'youtube.video.metadata',
        'comentarios-youtube': 'youtube.comments',
    }
    for i, (fase, cap) in enumerate(sorted(esperado.items()), 1):
        real = sc.FASES[fase][1]
        ataque(i, '`%s` -> %s' % (fase, cap), real == cap, real)

    # ── 5 · SEARCH RECEBE PARAMETRO DE COMMENTS (e vice-versa) ─────────────
    print('\n5-8 · um parametro de uma rota nao entra noutra')
    ataque(5, 'search NAO aceita `video`',
           'video' not in sc.NOMEADOS['busca-youtube'],
           sorted(sc.NOMEADOS['busca-youtube']))
    ataque(6, 'comments NAO aceita `videos` (a lista da metadata)',
           'videos' not in sc.NOMEADOS['comentarios-youtube'],
           sorted(sc.NOMEADOS['comentarios-youtube']))
    ataque(7, 'metadata NAO aceita `video` (o id unico)',
           'video' not in sc.NOMEADOS['video-youtube'],
           sorted(sc.NOMEADOS['video-youtube']))
    ataque(8, 'canal NAO aceita `termo`',
           'termo' not in sc.NOMEADOS['canal-youtube'],
           sorted(sc.NOMEADOS['canal-youtube']))

    # ── 9 · SOURCE_ID DERIVADO DE VIDEO/CHANNEL ID ─────────────────────────
    print('\n9 · a identidade nunca se deriva do endereco')
    maus = []
    for fase in OFICIAIS:
        for nome in sc.NOMEADOS[fase]:
            if nome in ('fonte', 'source_id', 'SOURCE_ID'):
                maus.append((fase, nome))
    ataque(9, 'nenhuma fase trata o endereco como fonte', not maus,
           'canal_id/video/videos/termo SAO ENDERECOS')

    # ── 10 · CATALOG ENTRA COMO COLHEITA ───────────────────────────────────
    print('\n10 · search e CATALOG, e CATALOG nao atravessa a porta')
    ataque(10, '`busca-youtube` declara CATALOG',
           sc.FASES['busca-youtube'][3] == rc.CATALOG,
           sc.FASES['busca-youtube'][3])
    ataque(10, 'so COLHEITA entra no ingresso',
           rc.CATALOG not in rc.ENTRAM_NO_INGRESSO,
           'SEARCH DEVOLVE ONDE PROCURAR')

    # ── 11 · NATIVE_CAPTION ENTRA DE CARONA ────────────────────────────────
    print('\n11 · a rota paga nao entra na wave gratuita')
    ataque(11, '`youtube.native_caption` NAO tem fase',
           not any(v[1] == 'youtube.native_caption'
                   for v in sc.FASES.values()),
           'rota = apify:transcricao')
    ataque(11, 'nenhuma fase servida pede native_caption',
           not any('caption' in f for f in servidas),
           'CAPTION != TRANSCRIPT')

    # ── 12 · «SEM CHAVE AQUI» VIRA «NAO EXISTE NO PROJETO» ─────────────────
    # O ataque que originou a missao. O estado tem de mudar com a PRESENCA da
    # variavel — e `native_caption` tem de continuar fechada, porque a chave
    # dela e outra.
    print('\n12 · credencial local != credencial do sistema')
    import importlib
    import scrap_executor as sx
    guardado = os.environ.pop('YOUTUBE_DATA_API_KEY', None)
    importlib.reload(sx)
    sem = {c: sx.CHECK('YOUTUBE', c).get('STATE')
           for c in list(esperado.values()) + ['youtube.native_caption']}
    os.environ['YOUTUBE_DATA_API_KEY'] = FIXTURE
    importlib.reload(sx)
    com = {c: sx.CHECK('YOUTUBE', c).get('STATE')
           for c in list(esperado.values()) + ['youtube.native_caption']}
    if guardado is None:
        os.environ.pop('YOUTUBE_DATA_API_KEY', None)
    else:
        os.environ['YOUTUBE_DATA_API_KEY'] = guardado

    for cap in esperado.values():
        ataque(12, '%s abre com a chave declarada' % cap.split('.', 1)[1],
               sem[cap] == 'CREDENTIAL_MISSING'
               and com[cap] == 'CAN_COLLECT_NOW',
               '%s -> %s' % (sem[cap], com[cap]))
    ataque(12, 'native_caption NAO abre com a chave do YouTube',
           com['youtube.native_caption'] != 'CAN_COLLECT_NOW',
           'dono da credencial = APIFY_TOKEN_POOL')

    # ── 13 · O SEGREDO E LOGADO ────────────────────────────────────────────
    # ⚠️ A PRIMEIRA VERSAO DESTA ASSERCAO ACUSOU-SE A SI PROPRIA: procurava as
    # strings de leitura no proprio ficheiro, e elas la estavam — dentro da
    # string que as procura. Um detector que se deteta a si mesmo nao mede
    # nada, e faze-lo passar ignorando o proprio ficheiro seria mexer a regua.
    #
    #     NAO SE PROCURA O NOME DA DOENCA: MEDE-SE O DOENTE.
    #
    # Entao mede-se o que importa de facto: o que esta prova IMPRIME. Injeta-se
    # um valor sentinela no ambiente, corre-se tudo, e verifica-se que ele
    # nunca aparece na saida — nem inteiro, nem em pedaco.
    print('\n13 · nenhum segredo chega a saida')
    import io
    import contextlib
    SENTINELA = 'ZZ-SENTINELA-DO-RED-TEAM-99'
    anterior = os.environ.get('YOUTUBE_DATA_API_KEY')
    os.environ['YOUTUBE_DATA_API_KEY'] = SENTINELA
    capturado = io.StringIO()
    try:
        with contextlib.redirect_stdout(capturado):
            importlib.reload(sx)
            for cap in list(esperado.values()) + ['youtube.native_caption']:
                sx.CHECK('YOUTUBE', cap)
    finally:
        if anterior is None:
            os.environ.pop('YOUTUBE_DATA_API_KEY', None)
        else:
            os.environ['YOUTUBE_DATA_API_KEY'] = anterior
    saida = capturado.getvalue()
    ataque(13, 'o valor do secret nunca aparece na saida',
           SENTINELA not in saida and SENTINELA[:12] not in saida,
           '%d caracteres inspeccionados' % len(saida))

    # ── 14 · UMA CAPACIDADE FALHA E CONTAMINA AS OUTRAS ────────────────────
    print('\n14 · uma fase que falha nao derruba as vizinhas')
    def duble_que_falha(*, platform, capability, run_id, banco=None, **kw):
        if capability == 'youtube.comments':
            raise RuntimeError('rota em baixo, de proposito')
        return ([{'URL': 'https://youtube.test/1', 'COUNTRY_SCOPE': 'IT',
                  'LANGUAGE': 'it', 'PUBLISHED_AT': '2026-09-18T00:00:00Z',
                  'COLLECTED_AT': '2026-09-18T12:00:00Z', 'TEXT': 'ok'}],
                {'RESULT': 'OK', 'COST_STATE': 'FREE', 'PROVIDER_USED': 'duble'})
    guardar = sx.COLLECT
    sx.COLLECT = duble_que_falha
    sc.sx = sx
    try:
        env = sc.colher('video-youtube', run_id='RT-0001',
                        fonte='IT-T9-002', videos='v1')
        ataque(14, 'metadata colhe apesar de comments estar em baixo',
               len(env['COLHEITA']) == 1, 'COLHEITA=%d' % len(env['COLHEITA']))
    finally:
        sx.COLLECT = guardar
        sc.sx = sx

    print('\n' + '=' * 76)
    print('ATAQUES = %d · RED_TEAM_BLOCKERS = %d' % (N[0], len(BLOQUEIOS)))
    for b in BLOQUEIOS:
        print('   !!! %s' % b)
    print('=' * 76)
    return 1 if BLOQUEIOS else 0


if __name__ == '__main__':
    raise SystemExit(main())
