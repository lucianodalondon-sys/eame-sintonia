#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""C10.6C — A DURABILIDADE É DO RUNTIME COMUM, E PROVA-SE COM MAIS DE UM ADAPTER.

    BANCO_DESCARTAVEL_URL=postgresql://... py provas/runtime_comum_no_postgres.py

A C10.6B provou o estado durável na cadeia de Reel. Provou-o LÁ dentro: era o
adaptador do Instagram que abria a RUN, ligava o checkpoint e passava o relator.

    UMA INFRAESTRUTURA COMUM NÃO É PROVADA POR UM ÚNICO ADAPTER USANDO-A.

Esta prova atravessa `scrap_executor.COLLECT` — o boundary comum — com TRÊS
classes de execução diferentes, e confere no banco que as três deixaram a mesma
espécie de rasto:

    MEDIA      `executa` · Instagram Reel sobre mídia já preservada
    API        `rota` + roteador · YouTube com transporte injetado
    JSON       `rota` + roteador · Mastodon com transporte falso

NENHUMA TOCA A REDE. `scrap_http` é substituído por um transporte que grita se
alguém o chamar com um endereço que a fixture não conhece — uma prova de «não
saiu» que não consegue detetar saída não prova nada.

    NETWORK_REAL = 0
"""
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in ('coleta', 'leis', 'medidas', 'ferramentas', 'guarda', ''):
    sys.path.insert(0, os.path.join(RAIZ, p) if p else RAIZ)

DSN = (os.environ.get('BANCO_DESCARTAVEL_URL') or '').strip()
LOCAL = ('localhost', '127.0.0.1', '::1', '@postgres', '/var/run/postgresql')
TOCOU = []


def _local(dsn):
    return bool(dsn) and any(m in dsn for m in LOCAL)


# ── O TRANSPORTE FALSO ────────────────────────────────────────────────────
FIXTURES = {
    'mastodon': json.dumps([{
        'id': '1', 'uri': 'https://mastodon.uno/users/agro/statuses/1',
        'url': 'https://mastodon.uno/@agro/1', 'content': '<p>fungicida</p>',
        'created_at': '2026-09-01T10:00:00.000Z', 'language': 'it',
        'account': {'acct': 'agro@mastodon.uno'}}]),
}


def _sem_rede(url, *a, **k):
    if 'timelines/tag' in url:
        return FIXTURES['mastodon']
    TOCOU.append(url)
    raise AssertionError('esta prova tentou sair para a rede: %s' % url[:80])


class TransporteYouTube:
    """O transporte injetado da `Sessao`. Devolve a fixture e conta as chamadas."""

    def __init__(self):
        self.chamadas = []

    def __call__(self, url, *a, **k):
        self.chamadas.append(url)
        if 'search' in url:
            return {'items': [{'id': {'kind': 'youtube#channel',
                                      'channelId': 'UCPROVA'},
                               'snippet': {'title': 'Canal da Prova',
                                           'publishedAt': '2026-01-01T00:00:00Z',
                                           'description': 'fixture'}}],
                    'pageInfo': {'totalResults': 1}}
        return {'items': []}


def main():
    if not DSN:
        print('BANCO_DESCARTAVEL_URL ausente — esta prova nao inventa banco.')
        print('RUNTIME_COMUM=NOT_RUN')
        return 0
    if not _local(DSN):
        print('RUNTIME_COMUM=RECUSADA_ENDERECO_NAO_LOCAL')
        return 1

    import coleta_checkpoint as ck
    import scrap_http as http
    import scrap_executor as sx
    import scrap_registo as reg

    banco = ck.Banco(DSN)
    try:
        banco.executa('select 1 from public.collection_run limit 1')
    except Exception:                                             # noqa: BLE001
        print('schema ausente. A cadeia de migrations tem de correr antes.')
        print('RUNTIME_COMUM=NOT_RUN')
        return 0
    reg.carregar_adaptadores()
    # ⚠️ O ACERVO REAL NÃO RECEBE PROVA. É lei da casa desde a C2, e esta prova
    # atravessa rotas que GRAVAM bruto antes de normalizar. Sem isto, correr a
    # prova deixava ficheiros em `data/samples/` — e os guardas da casa
    # apanharam-nos, que é o que eles existem para fazer.
    #
    #     UMA PROVA QUE SUJA O ACERVO MEDE-SE A SI PRÓPRIA DEPOIS.
    import tempfile
    import social_envelope as env
    env.RAW_DIR = tempfile.mkdtemp(prefix='c106c-raw-')

    # O portao de transporte inteiro passa a ser fixture. `permitido` tambem:
    # ele le `robots.txt` VIVO, e ler robots e sair.
    http.buscar = _sem_rede
    http.permitido = lambda url: (True, 'fixture: esta prova nao sai')

    falhas_ = []
    RESULTADOS = []

    def conferir(nome, classe, run_id, objetos, trace, espera_checkpoint,
                 espera_etapas=('CHECK',)):
        linhas = banco.executa(
            "select status::text, coalesce(checkpoint_id::text,'-'),"
            " coalesce(item_count_raw::text,'-')"
            " from public.collection_run where run_id = %s" % ck._lit(run_id))
        etapas = banco.executa(
            "select etapa::text, estado::text, tentativa::text"
            " from public.etapa_da_corrida where run_id = %s order by id"
            % ck._lit(run_id))
        if not linhas or not linhas[0] or not linhas[0][0]:
            falhas_.append('%s: nao nasceu RUN nenhuma' % nome)
            RESULTADOS.append((nome, classe, '—', '—', 0, 'SEM RUN'))
            return
        status, cid, itens = linhas[0][:3]
        tem_cp = cid != '-'
        if status == 'rodando':
            falhas_.append('%s: a RUN ficou aberta depois de COLLECT voltar' % nome)
        if not etapas:
            falhas_.append('%s: nenhuma etapa foi registada' % nome)
        vistas = [e[0] for e in etapas]
        # ⚠️ EXIGIR AS ETAPAS QUE ESTA CLASSE REALMENTE ATRAVESSA.
        # A primeira versao desta prova pedia so `CHECK` — e passou com as tres
        # classes a produzir UMA linha cada, incluindo a que devia ter quatro.
        #
        #     UMA PROVA QUE ACEITA O MINIMO MEDE O MINIMO.
        for esperada in espera_etapas:
            if esperada not in vistas:
                falhas_.append('%s: a etapa %s nao foi escrita (vistas: %s)'
                               % (nome, esperada, vistas))
        if tem_cp != espera_checkpoint:
            falhas_.append('%s: checkpoint=%s, esperado=%s'
                           % (nome, tem_cp, espera_checkpoint))
        RESULTADOS.append((nome, classe, status, cid, len(etapas),
                           ' · '.join('%s/%s' % (e[0], e[1]) for e in etapas)))

    print('═══ TRÊS CLASSES DE EXECUÇÃO, UM BOUNDARY ═══')

    # ── 1 · MEDIA · Instagram Reel, `executa`, midia ja preservada ─────────
    midia = os.path.join(RAIZ, 'data', 'raw', 'REEL-MIDIA', 'C-FanW_CYMz.wav')
    if os.path.exists(midia):
        oficina = os.path.join(RAIZ, 'data', 'raw', 'C10-6C-OFICINA')
        # `instagram.reel.transcribe` tem `rota`, e o roteador RECUSA-A: a
        # decisao da C10.5D poe `INSTAGRAM/FETCH_TRANSCRIPT` em
        # `ROUTE_NOT_ALLOWED`. Isso e a politica a funcionar, e nao ha nada a
        # consertar. A classe MEDIA prova-se por `instagram.reel.capture`, que
        # tem `executa` e a mesma unidade de trabalho.
        objetos, trace = sx.COLLECT(
            platform='INSTAGRAM', capability='instagram.reel.capture',
            run_id='RT-MEDIA', banco=banco,
            ident={'PLATFORM': 'INSTAGRAM', 'POST_ID': 'C10-6C-MEDIA'},
            midia_ficheiro=midia, model_hint='tiny', guardar=False,
            oficina=oficina)
        conferir('instagram.reel.capture', 'MEDIA (executa)', 'RT-MEDIA',
                 objetos, trace, espera_checkpoint=True,
                 espera_etapas=('CHECK', 'FETCH', 'RAW', 'DERIVED'))
    else:
        print('  (sem midia preservada nesta arvore — a classe MEDIA nao corre)')
        RESULTADOS.append(('instagram.reel.capture', 'MEDIA (executa)',
                           'NOT_RUN', '—', 0, 'sem fixture de midia'))

    # ── 2 · API · YouTube, `rota` + roteador, transporte injetado ──────────
    import youtube_oficial as yt
    tp = TransporteYouTube()
    sessao = yt.Sessao(api_key='FIXTURE', transporte=tp)
    # `youtube.search` e a capacidade que recebe `termo`. `channel.discovery`
    # recebe `channel_id` — passar-lhe `termo` da `PARSER_DRIFT`, que foi o que
    # a primeira versao desta prova mediu: o defeito da sonda, nao da casa.
    objetos, trace = sx.COLLECT(
        platform='YOUTUBE', capability='youtube.search',
        run_id='RT-API', banco=banco, termo='fungicida', country_scope='IT',
        limit=1, sessao=sessao)
    conferir('youtube.search', 'API (rota)', 'RT-API', objetos, trace,
             espera_checkpoint=False)
    if not tp.chamadas:
        falhas_.append('youtube.search: o transporte injetado nunca foi chamado — '
                       'a prova nao chegou a exercer a rota')

    # ── 3 · JSON · Mastodon, `rota` + roteador, transporte falso ───────────
    objetos, trace = sx.COLLECT(
        platform='MASTODON', capability='mastodon.hashtag.search',
        run_id='RT-JSON', banco=banco, instancia='mastodon.uno', tag='agri',
        limit=1, country_scope='IT')
    conferir('mastodon.hashtag.search', 'JSON (rota)', 'RT-JSON', objetos, trace,
             espera_checkpoint=False)

    print()
    print('%-32s %-18s %-11s %-6s %s'
          % ('CAPACIDADE', 'CLASSE', 'RUN', 'CHKPT', 'ETAPAS'))
    print('─' * 104)
    for nome, classe, status, cid, n, etapas in RESULTADOS:
        print('%-32s %-18s %-11s %-6s %s'
              % (nome[:32], classe, status, cid, etapas[:38]))

    # ── 4 · ISOLAMENTO: UM ADAPTER NAO MEXE NO ESTADO DO OUTRO ────────────
    print()
    print('═══ FASE 12 · ISOLAMENTO ENTRE ADAPTERS ═══')
    cruz = banco.executa(
        "select e.run_id, count(distinct r.platform)::text"
        " from public.etapa_da_corrida e join public.collection_run r"
        " on r.run_id = e.run_id where e.run_id like 'RT-%' group by 1")
    for l in cruz:
        if l and len(l) > 1 and l[1] != '1':
            falhas_.append('%s: etapas de mais de uma plataforma na mesma RUN' % l[0])
    plats = banco.executa(
        "select platform, count(*)::text from public.collection_run"
        " where run_id like 'RT-%' group by 1 order by 1")
    print('  plataformas distintas, cada uma na sua RUN: %s'
          % ', '.join('%s=%s' % (p[0], p[1]) for p in plats if p and p[0]))
    partilham = banco.executa(
        "select checkpoint_id::text, count(distinct platform)::text"
        " from public.collection_run where run_id like 'RT-%'"
        " and checkpoint_id is not null group by 1 having count(distinct platform) > 1")
    if partilham:
        falhas_.append('duas plataformas partilham checkpoint: %s' % partilham)
    print('  checkpoints partilhados entre plataformas: %d' % len(partilham))

    # ══════════════════════════════════════════════════════════════════════
    # FASE 10 · CRASH CROSS-ADAPTER
    # ══════════════════════════════════════════════════════════════════════
    # A C10.6B matou processos numa cadeia. A pergunta desta missao e outra: a
    # infraestrutura parte-se IGUAL nas tres classes?
    #
    #     A PROVA DE QUE A INFRAESTRUTURA E COMUM E ELA PARTIR-SE IGUAL EM TODAS.
    import subprocess
    FILHO = os.path.join(RAIZ, 'provas', '_c106c_filho.py')
    print()
    print('═══ FASE 10 · CRASH CROSS-ADAPTER ═══')
    formas = set()
    for classe in ('MEDIA', 'API', 'JSON'):
        run = 'RTC-%s' % classe
        r_ = subprocess.run([sys.executable, FILHO, classe, run, 'MORRER'],
                            cwd=RAIZ, capture_output=True, text=True, timeout=600,
                            env=dict(os.environ))
        if r_.returncode != 97:
            falhas_.append('%s: exit %s, esperado 97 (%s)'
                           % (classe, r_.returncode, (r_.stderr or '')[:140]))
            continue
        l_ = banco.executa(
            "select r.status::text, coalesce(r.checkpoint_id::text,'-'),"
            " coalesce((select string_agg(e.etapa::text||'/'||e.estado::text, ' ')"
            "   from public.etapa_da_corrida e where e.run_id = r.run_id),'-')"
            " from public.collection_run r where r.run_id = %s" % ck._lit(run))
        if not l_ or not l_[0] or len(l_[0]) < 3:
            falhas_.append('%s: o processo novo nao viu a corrida morta' % classe)
            continue
        status, cid, etapas = l_[0][:3]
        print('  %-6s exit=97 · RUN=%s · checkpoint=%s · %s'
              % (classe, status, cid, etapas))
        if status != 'rodando':
            falhas_.append('%s: alguem fechou a corrida morta (%s)' % (classe, status))
        if etapas != 'CHECK/PASS':
            falhas_.append('%s: o rasto da morte nao e o esperado (%s)'
                           % (classe, etapas))
        formas.add(etapas)
    if len(formas) > 1:
        falhas_.append('as classes partiram-se de formas diferentes: %s' % formas)
    print('  CROSS_ADAPTER_CRASH_PROOF = %s'
          % ('PROVEN' if len(formas) == 1 and not falhas_ else 'VER FALHAS'))

    # ══════════════════════════════════════════════════════════════════════
    # FASE 11 · CONCORRENCIA, NO BOUNDARY COMUM
    # ══════════════════════════════════════════════════════════════════════
    print()
    print('═══ FASE 11 · CONCORRENCIA ═══')
    RONDAS = int(os.environ.get('C106C_RONDAS') or 20)
    achados = {'DUPLICATE_ADVANCE': 0, 'LOST_RUN': 0, 'DOUBLE_CLOSE': 0,
               'DEADLOCK': 0, 'SERIALIZATION_FAILURE': 0}
    for i in range(RONDAS):
        alvo = 'CONC%03d' % i
        ps = [subprocess.Popen(
            [sys.executable, FILHO, 'JSON', 'RTX-%s-%s' % (alvo, lado)],
            cwd=RAIZ, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, env=dict(os.environ))
            for lado in ('A', 'B')]
        for pp in ps:
            _o, e_ = pp.communicate(timeout=300)
            if 'deadlock' in (e_ or '').lower():
                achados['DEADLOCK'] += 1
            if 'could not serialize' in (e_ or '').lower():
                achados['SERIALIZATION_FAILURE'] += 1
    # As duas rondas partilham nada: cada uma tem o seu `run_id`. O que se mede
    # e que duas execucoes simultaneas nao se pisam no rasto.
    dup = banco.executa(
        "select run_id, etapa::text, tentativa::text, count(*)::text"
        " from public.etapa_da_corrida where run_id like 'RTX-%'"
        " group by 1,2,3 having count(*) > 1")
    runs = banco.executa("select count(distinct run_id)::text from"
                         " public.collection_run where run_id like 'RTX-%'")
    abertas = banco.executa("select count(*)::text from public.collection_run"
                            " where run_id like 'RTX-%' and status = 'rodando'")
    print('  rondas=%d · corridas distintas=%s · linhas de etapa duplicadas=%d'
          ' · corridas por fechar=%s'
          % (RONDAS, runs[0][0] if runs else '?', len(dup),
             abertas[0][0] if abertas else '?'))
    if dup:
        falhas_.append('concorrencia: %d (run,etapa,tentativa) duplicados' % len(dup))
        achados['DUPLICATE_ADVANCE'] += len(dup)
    if abertas and abertas[0][0] != '0':
        falhas_.append('concorrencia: %s corrida(s) ficaram `rodando`' % abertas[0][0])
    for k, v in achados.items():
        if v:
            falhas_.append('concorrencia: %s = %d' % (k, v))
    print('  %s' % ' · '.join('%s=%d' % (k, v) for k, v in achados.items()))

    print()
    print('NETWORK_REAL = %d  (%s)' % (len(TOCOU), TOCOU[:2] or 'nenhuma saida'))
    if TOCOU:
        falhas_.append('a prova saiu para a rede')
    for f in falhas_:
        print('  ✗ %s' % f)
    print('RUNTIME_COMUM=%s' % ('PASS' if not falhas_ else 'FAIL'))
    return 0 if not falhas_ else 1


if __name__ == '__main__':
    raise SystemExit(main())
