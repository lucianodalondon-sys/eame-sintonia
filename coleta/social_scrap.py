#!/usr/bin/env python3
"""
SINTONIA SCRAP — o executor composto. Uma fase por comando, sempre auditável.

    py scripts/social_scrap.py censo                 # GRÁTIS · a matriz inteira
    py scripts/social_scrap.py portao <url>          # GRÁTIS · o robots.txt vivo diz o quê?
    py scripts/social_scrap.py video                 # GRÁTIS · de onde sai vídeo italiano
    py scripts/social_scrap.py gap                   # GRÁTIS · onde a Apify ainda é precisa
    py scripts/social_scrap.py piloto                # GRÁTIS · a prova pequena, ao vivo
    py scripts/social_scrap.py ledger                # GRÁTIS · o que a missão rodou e gastou
    py scripts/social_scrap.py sessao                # GRÁTIS · preflight da sessão local
    py scripts/social_scrap.py politica              # GRÁTIS · onde LOCAL_SESSION é permitida
    py scripts/social_scrap.py guarda                # GRÁTIS · nenhum segredo entrou no Git
    py scripts/social_scrap.py authmodes             # GRÁTIS · o raio-X para o System Map

O SINTONIA SCRAP NÃO É UM ORQUESTRADOR
----------------------------------------
Ele não decide o que vale a pena olhar, não prioriza país, não abre missão e não
julga achado. Ele é um EXECUTOR COMPOSTO: recebe (plataforma, capacidade, alvo),
escolhe a rota permitida mais barata e devolve objeto canônico com proveniência.

    QUEM DECIDE O QUE OLHAR ESTÁ ACIMA DELE. ELE SÓ SABE OLHAR.

Por isso `piloto` não é "a coleta italiana". É a PROVA de que as portas abrem —
com o número honesto do que passou por cada uma.

CAPACIDADE NÃO É COLETA
-------------------------
Existir adaptador prova CÓDIGO. Só execução real prova OBSERVADO. Esta é a
distinção que faz um relatório valer alguma coisa, e o `ledger` é onde ela vive:
ele conta o que REALMENTE rodou, não o que está declarado na matriz.

    32 CAPACIDADES DECLARADAS != 32 CAPACIDADES COLETADAS.

TESTE ADVERSARIAL É FASE, NÃO NOTA DE RODAPÉ
----------------------------------------------
`piloto` inclui de propósito alvos que vão FALHAR: um canal de Telegram que não
existe, uma rota que o robots barra, uma busca que devolve zero. Uma bateria que
só passa não mediu nada — ela só confirmou o caminho feliz.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(HERE)
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401 — poe as gavetas do processo no caminho
import social_envelope as env      # noqa: E402
import social_matriz as mz         # noqa: E402
import social_rotas as sr          # noqa: E402
import social_sessao as ss
import falhas         # noqa: E402

LEDGER = 'LEDGER-SOCIAL-IT.json'


def _run_id(fase):
    return 'SOCIAL-IT-%s-%s' % (fase.upper(), env.agora().replace(':', '').replace('-', ''))


def _registrar(registros, objetos, nome_artefato):
    led = env.ler(LEDGER, {'MISSAO': 'SINTONIA SCRAP · SOCIAL IT', 'EXECUCOES': []})
    led['EXECUCOES'].extend(registros)
    led['ATUALIZADO_EM'] = env.agora()
    led['CUSTO_TOTAL_USD'] = round(sum(r.get('COST_USD') or 0 for r in led['EXECUCOES']), 6)
    env.gravar(LEDGER, led)
    if objetos:
        distintos, rel = env.dedupe(objetos)
        env.gravar(nome_artefato, {'GERADO_EM': env.agora(), 'DEDUPE': rel,
                                   'OBJETOS': distintos})
        return rel
    return None


# ══════════════════════════════════════════════════════════════════════════
# O PILOTO — pequeno de propósito, e com fracasso planejado dentro.
# ══════════════════════════════════════════════════════════════════════════
# Termos italianos do agro. Não são palavras traduzidas do português: são os
# termos que a conversa técnica italiana usa de verdade.
TERMOS_IT = ['agricoltura', 'agronomia', 'fitosanitari', 'agricoltura4', 'viticoltura']

ALVOS = {
    'MASTODON': {
        # mastodon.uno é a maior instância italiana. A tag é o caminho público
        # que a doc oficial marca "Public".
        'instancias': ['mastodon.uno', 'mastodon.social'],
        'tags': ['agricoltura', 'agronomia', 'viticoltura'],
    },
    'BLUESKY': {'termos': ['agricoltura', 'agronomo', 'viticoltura']},
    # YouTube entra por TERMO, não por canal: esta casa ainda não tem nenhum
    # channelId italiano no acervo, e descobrir um exige `search.list` — que
    # exige a chave. Declarar canais inventados aqui seria fingir um alvo.
    'YOUTUBE': {'termos': ['agricoltura', 'trattore', 'viticoltura',
                           'agronomia', 'fitosanitari'],
                'canais': []},
    'TELEGRAM': {
        # Os dois primeiros são teste ADVERSARIAL declarado: eu não sei se
        # existem. O piloto precisa registrar a diferença entre "canal vazio" e
        # "canal inexistente" — e essa diferença só aparece se eu tentar.
        'canais': ['agronotizie', 'terraevita'],
    },
}


def piloto():
    run = _run_id('piloto')
    registros, objetos = [], []
    print('\nPILOTO SOCIAL ITÁLIA · run=%s\n%s' % (run, '─' * 74))

    for inst in ALVOS['MASTODON']['instancias']:
        for tag in ALVOS['MASTODON']['tags']:
            o, reg = sr.executar(platform='MASTODON', capability='SEARCH_HASHTAG',
                                 run_id=run, country_scope='IT',
                                 instancia=inst, tag=tag, limit=20)
            registros.append(reg); objetos.extend(o)
            _linha('MASTODON', '%s #%s' % (inst, tag), reg)

    for termo in ALVOS['BLUESKY']['termos']:
        o, reg = sr.executar(platform='BLUESKY', capability='DISCOVER_ACCOUNT',
                             run_id=run, country_scope='IT', termo=termo, limit=25)
        registros.append(reg); objetos.extend(o)
        _linha('BLUESKY', 'contas ~ %s' % termo, reg)

    for canal in ALVOS['TELEGRAM']['canais']:
        o, reg = sr.executar(platform='TELEGRAM', capability='INCREMENTAL',
                             run_id=run, country_scope='IT', canal=canal)
        registros.append(reg); objetos.extend(o)
        _linha('TELEGRAM', '@%s' % canal, reg)

    # ADVERSARIAL EXPLÍCITO: rotas que a matriz declara proibidas ou sem
    # adaptador. Elas TÊM que falhar; se um dia passarem, algo quebrou.
    print('\n  ── teste adversarial (estes DEVEM recusar) ──')
    for plat, cap, extra in (('YOUTUBE', 'INCREMENTAL', {}),
                             ('LINKEDIN', 'FETCH_POST', {}),
                             ('X', 'SEARCH_KEYWORD', {}),
                             ('TIKTOK', 'DISCOVER_ACCOUNT', {})):
        o, reg = sr.executar(platform=plat, capability=cap, run_id=run,
                             country_scope='IT', **extra)
        registros.append(reg); objetos.extend(o)
        _linha(plat, cap, reg)

    rel = _registrar(registros, objetos, 'PILOTO-SOCIAL-IT.json')
    print('\n%s' % ('─' * 74))
    print('  execuções           %d' % len(registros))
    print('  objetos brutos      %d' % len(objetos))
    if rel:
        print('  objetos distintos   %d  (fundidos por PLATFORM+NATIVE_ID: %d)'
              % (rel['DISTINTOS'], rel['FUNDIDOS']))
    estados = {}
    for r in registros:
        estados[r['ESTADO']] = estados.get(r['ESTADO'], 0) + 1
    print('  por estado          %s' % estados)
    print('  custo               US$ %.4f   (APIFY_USAGE desta missão: 0)'
          % sum(r.get('COST_USD') or 0 for r in registros))
    print('  artefato            data/samples/SOCIAL-IT/PILOTO-SOCIAL-IT.json')
    _honestidade_de_pais(objetos)


def _honestidade_de_pais(objetos):
    """O número que impede o piloto de mentir sobre a Itália.

    Medido no piloto de 2026-09-08: a busca por "agronomo" no Bluesky devolveu
    agrônomos espanhóis e brasileiros, porque `agronomo/agrónomo/agrônomo` não
    é uma palavra italiana — é uma palavra latina. E NENHUM dos 99 objetos veio
    com país declarado pela rota.

        COUNTRY_SCOPE=IT É O QUE EU PEDI. NÃO É O QUE EU PROVEI.

    Por isso os dois campos aparecem separados aqui, sempre, mesmo quando o
    número é feio — principalmente quando é feio.
    """
    if not objetos:
        return
    distintos, _ = env.dedupe(list(objetos))
    idiomas, locais = {}, {}
    for o in distintos:
        idiomas[o['LANGUAGE']] = idiomas.get(o['LANGUAGE'], 0) + 1
        locais[o['SOURCE_LOCATION']] = locais.get(o['SOURCE_LOCATION'], 0) + 1
    it = idiomas.get('it', 0)
    print('\n  ── país != idioma (a régua da Bíblia, aplicada ao próprio piloto) ──')
    print('    LANGUAGE declarado    %s' % dict(sorted(idiomas.items(), key=lambda x: -x[1])))
    print('    SOURCE_LOCATION       %s' % dict(sorted(locais.items(), key=lambda x: -x[1])))
    print('    italiano declarado    %d de %d objetos' % (it, len(distintos)))
    print('    Itália PROVADA        0 de %d — nenhuma rota gratuita desta missão' % len(distintos))
    print('                          declara país. `COUNTRY_SCOPE=IT` é o recorte do')
    print('                          PEDIDO, nunca uma propriedade provada do objeto.')


def _linha(plat, alvo, reg):
    marca = {'OK': '✓', 'ZERO_RESULTS': '·', 'BLOCKED': '✗',
             'ROUTE_NOT_ALLOWED': '⊘', 'PAID_ROUTE_REFUSED': '$',
             'CREDENTIAL_MISSING': '?', 'POSSIBLE_NOT_PROVED': '?'}.get(reg['ESTADO'], '!')
    print('  %s %-9s %-28s %-20s n=%-4s %s'
          % (marca, plat, alvo[:28], reg['ESTADO'], reg['OBJETOS'],
             (reg['ERRO'] or '')[:70]))


def video():
    """VIDEO CAPABILITY — de onde o SINTONIA consegue trazer vídeo italiano hoje."""
    print('\nVIDEO CAPABILITY · medido em %s\n%s' % (mz.MEDIDO_EM, '═' * 78))
    print('  %-11s %-9s %-9s %-9s %-11s %s'
          % ('PLATAFORMA', 'DESCOBRE', 'METADATA', 'MÍDIA', 'TRANSCRIÇÃO', 'ROTA PADRÃO'))
    print('  ' + '─' * 76)
    for plat in ('YOUTUBE', 'INSTAGRAM', 'TIKTOK', 'FACEBOOK', 'MASTODON',
                 'TELEGRAM', 'BLUESKY', 'X', 'LINKEDIN', 'THREADS'):
        caps = mz.MATRIZ.get(plat) or {}
        def st(nome):
            rotas = caps.get(nome)
            if not rotas:
                return '—'
            d = mz._rota_padrao(rotas)
            return {'PROVED': 'SIM', 'CREDENTIAL_MISSING': 'chave',
                    'POSSIBLE_NOT_PROVED': 'talvez'}.get(d['ESTADO'], d['ESTADO'][:9]) if d else 'NÃO'
        descobre = st('SEARCH_KEYWORD') if caps.get('SEARCH_KEYWORD') else st('DISCOVER_ACCOUNT')
        meta = st('FETCH_VIDEO_METADATA')
        midia = st('FETCH_VIDEO_BYTES')
        trans = st('FETCH_TRANSCRIPT')
        d = mz._rota_padrao(caps.get('FETCH_VIDEO_METADATA') or
                            caps.get('INCREMENTAL') or
                            caps.get('SEARCH_KEYWORD') or [])
        print('  %-11s %-9s %-9s %-9s %-11s %s'
              % (plat, descobre, meta, midia, trans, (d['ROTA'] if d else 'nenhuma')[:32]))
    print('\n  TRANSCRIÇÃO — a ordem é sempre a mesma, e ela já existe nesta casa:')
    print('    1. legenda pública        → só YouTube tem, e SÓ para o dono do vídeo')
    print('    2. faster-whisper local   → scripts/instagram_transcrever.py, custo ZERO dólar')
    print('    3. transcrição paga       → último, com motivo canônico declarado')
    print('\n  O buraco honesto: para vídeo de canal de TERCEIRO no YouTube não existe')
    print('  rota permitida até o áudio. Sem áudio, o Whisper local não tem o que fazer.')
    print('  Isso não é limite do Whisper — é limite de permissão, e é anterior a ele.')


def authmodes():
    """RAIO-X DOS AUTH MODES — o que o System Map mostra por plataforma.

    Uma coluna por modo de autenticação, uma linha por plataforma. O valor de
    cada célula é o ESTADO daquele modo, não um "sim/não": `AVAILABLE` e
    `NOT_ALLOWED` são respostas diferentes e a diferença é o assunto inteiro
    desta missão.

    E ele nunca mostra caminho de perfil, usuário, cookie ou token. O mapa diz
    QUE existe sessão; nunca DE QUEM nem ONDE.
    """
    modos = ('PUBLIC', 'OFFICIAL_API', 'LOCAL_SESSION', 'OFFICIAL_PAID_API', 'APIFY')
    print('\nRAIO-X DOS AUTH MODES · medido em %s\n%s' % (mz.MEDIDO_EM, '═' * 78))
    print('  %-11s %-14s %-14s %-14s %-14s %s'
          % ('PLATAFORMA', 'PUBLIC', 'OFFICIAL_API', 'LOCAL_SESSION', 'PAID_API', 'APIFY'))
    print('  ' + '─' * 76)
    for plat in sorted(mz.MATRIZ):
        caps = mz.MATRIZ[plat]
        # Que modos aparecem em alguma rota declarada e permitida?
        disponiveis = set()
        for cap, rotas in caps.items():
            if cap.startswith('_'):
                continue
            for x in rotas:
                if x['PERMITIDA'] in ('SIM', 'CONDICIONAL') and x['ESTADO'] != 'ROUTE_NOT_ALLOWED':
                    disponiveis.add(mz.auth_mode(x))
        celulas = []
        for m in modos:
            # AVAILABLE e USABLE sao coisas diferentes e aparecem separadas.
            # A rota EXISTIR nesta casa nao e a rota PODER ser usada — pintar as
            # duas com a mesma cor foi como "estou logado" virou "posso".
            if m == 'LOCAL_SESSION':
                if plat in ss.POLITICA:
                    r = ss.usabilidade(plat, '*', 'LOCAL_SESSION', ss.THIRD_PARTY)
                    celulas.append({ss.USABLE: 'AVAIL+USABLE',
                                    ss.NEEDS_REVIEW: 'AVAIL/REVIEW',
                                    ss.NOT_USABLE: 'AVAIL/NOT_USE'}[r['ROUTE_STATUS']])
                else:
                    celulas.append('—')
            elif m in disponiveis:
                r = ss.usabilidade(plat, '*', m, ss.THIRD_PARTY)
                celulas.append('AVAIL+USABLE' if r['ROUTE_STATUS'] == ss.USABLE
                               else 'AVAIL/REVIEW')
            else:
                celulas.append('—')
        print('  %-11s %-14s %-14s %-14s %-14s %s' % (plat, *celulas))
    print('\n  AVAIL = a rota existe nesta casa. USABLE = ela pode ser usada.')
    print('  As duas colunas são separadas de propósito: rota disponível não é')
    print('  rota autorizada, e revisão pendente (REVIEW) não é licença.')
    print('  LOCAL_SESSION contra TERCEIRO é NOT_USABLE nas sete prioritárias;')
    print('  contra conta PRÓPRIA é REVIEW — nenhuma cláusula abre exceção ao dono.')
    print('  E mesmo onde fosse permitida, a API oficial costuma ser a rota melhor.')
    print('\n  O mapa nunca mostra caminho de perfil, usuário, cookie ou token.')
    print('  Ele diz QUE existe sessão. Nunca DE QUEM, nem ONDE.\n')


def youtube():
    """A estrada oficial do YouTube, ponta a ponta — inclusive quando não roda.

    Esta fase percorre o caminho REAL de decisão para as quatro capacidades:
    a capacidade existe na matriz? a rota está declarada? os termos permitem?
    há credencial? Só então executa.

    Sem chave ela para em `CREDENTIAL_MISSING` — e isso é resultado, não erro.
    O que ela NUNCA faz é cair para scraping porque a chave faltou.
    """
    import youtube_oficial as yt
    caps = ('SEARCH_KEYWORD', 'INCREMENTAL', 'FETCH_VIDEO_METADATA', 'FETCH_COMMENTS')
    sess = yt.Sessao()
    print('\nYOUTUBE · ESTRADA OFICIAL · country_scope=IT\n%s' % ('═' * 78))
    print('  CREDENCIAL  %s (%s)' % ('PRESENTE' if sess.disponivel() else 'AUSENTE',
                                     yt.ENV_CHAVE))
    print('  COST_BASIS  %s · QUOTA MODEL %s' % (yt.COST_BASIS, yt.QUOTA_MODEL_VERSION))
    # Dois buckets, DECLARADOS pela documentação — não observados. Enquanto não
    # houver run real, "observado" é zero e dizer outra coisa seria invenção.
    print('  QUOTA       %s %s chamadas/dia · %s %s unidades/dia  (DECLARED/DOC CURRENT)'
          % (yt.SEARCH, yt.LIMITE_PADRAO[yt.SEARCH],
             yt.GENERAL, yt.LIMITE_PADRAO[yt.GENERAL]))
    print('  OBSERVED    SEARCH_CALLS=%d · GENERAL_UNITS=%d · REMAINING=UNKNOWN\n'
          % (sess.usado[yt.SEARCH], sess.usado[yt.GENERAL]))
    print('  %-22s %-14s %-11s %-20s %s'
          % ('CAPACIDADE', 'TERMOS', 'ROTA', 'BLOQUEIO', 'RECUPERAÇÃO'))
    print('  ' + '─' * 76)
    registros = []
    for cap in caps:
        u = ss.usabilidade('YOUTUBE', cap, 'OFFICIAL_API', ss.THIRD_PARTY)
        tech = u['TECHNICAL_STATUS']
        rec = falhas.recuperacao(tech if tech in falhas.NOMES else 'CREDENTIAL_MISSING')
        print('  %-22s %-14s %-11s %-20s %s'
              % (cap, u['TERMS_STATUS'], u['ROUTE_STATUS'], tech, rec))
        registros.append({'CAPABILITY': cap, 'AUTH_MODE': 'OFFICIAL_API',
                          'TERMS_STATUS': u['TERMS_STATUS'],
                          'ROUTE_STATUS': u['ROUTE_STATUS'],
                          'TECHNICAL_STATUS': tech,
                          'RECOVERY_ACTION': rec,
                          'SOURCE_HEALTH': falhas.HEALTHY,
                          'ROUTE_HEALTH': falhas.UNAVAILABLE if not sess.disponivel()
                          else falhas.HEALTHY,
                          'EXECUTOR_HEALTH': falhas.HEALTHY,
                          'SEARCH_CALLS_USED': 0, 'GENERAL_UNITS_USED': 0,
                          'QUOTA_BUCKET': (yt.SEARCH if cap == 'SEARCH_KEYWORD'
                                           else yt.GENERAL),
                          'COST_USD': 0.0, 'COST_BASIS': yt.COST_BASIS})
    # As duas que NÃO entram nesta missão, e por quê — declaradas, não omitidas.
    # RAIO-X: DECLARED (documentação) · CODE (implementado e testado) · OBSERVED
    # (rodou de verdade). As três colunas existem porque CAN DO != DID DO, e
    # enquanto não houver run real a terceira é honestamente vazia.
    import youtube_oficial as _yt
    obs = 'OBSERVED' if sess.disponivel() else 'NOT_OBSERVED'
    print('\n  RAIO-X            DECLARED                CODE          %s' % 'OBSERVED')
    print('  ' + '─' * 76)
    for nome, decl in (
            ('SEARCH BUCKET', '%d chamadas/dia' % _yt.LIMITE_PADRAO[_yt.SEARCH]),
            ('GENERAL BUCKET', '%d unidades/dia' % _yt.LIMITE_PADRAO[_yt.GENERAL]),
            ('UPLOADS PLAYLIST', 'channels.list oficial'),
            ('CHECKPOINT', 'por canal, em disco'),
            ('COMMENTS', 'threads + replies')):
        print('  %-17s %-23s %-13s %s' % (nome, decl, 'IMPLEMENTED+TESTED', obs))
    print('\n  A capacidade INCREMENTAL resolve a playlist de uploads por')
    print('  channels.list#contentDetails.relatedPlaylists.uploads — rota OFICIAL.')
    print('  UC->UU sobrevive só como DERIVED_HINT, e sai carimbado como palpite.')
    for cap in ('FETCH_TRANSCRIPT', 'FETCH_VIDEO_BYTES'):
        u = ss.usabilidade('YOUTUBE', cap, 'OFFICIAL_API', ss.THIRD_PARTY)
        print('  %-22s %-14s %-11s %-20s %s'
              % (cap, u['TERMS_STATUS'], u['ROUTE_STATUS'], u['TECHNICAL_STATUS'],
                 'NO_RETRY'))
    print('\n  SOURCE_HEALTH do YouTube: %s — falta de chave é da ROTA, não da FONTE.'
          % falhas.HEALTHY)
    if not sess.disponivel():
        print('  ROUTE_HEALTH: %s · RECOVERY: %s'
              % (falhas.UNAVAILABLE, falhas.recuperacao('CREDENTIAL_MISSING')))
        print('\n  As quatro rotas estão DECLARADAS, PERMITIDAS e LIGADAS.')
        print('  O que falta é uma chave — e falta de chave não autoriza scraping.')
    env.gravar('YOUTUBE-OFICIAL-ESTADO.json', {
        'QUANDO': env.agora(), 'PLATFORM': 'YOUTUBE', 'COUNTRY_SCOPE': 'IT',
        'CREDENCIAL_PRESENTE': sess.disponivel(), 'CAPACIDADES': registros,
        'QUOTA_MODEL_VERSION': yt.QUOTA_MODEL_VERSION,
        'QUOTA_BASIS': yt.QUOTA_BASIS,
        'SEARCH_CALLS_USED': sess.usado[yt.SEARCH],
        'GENERAL_UNITS_USED': sess.usado[yt.GENERAL],
        'SEARCH_CALLS_PROJECT_LIMIT_DEFAULT': yt.LIMITE_PADRAO[yt.SEARCH],
        'GENERAL_UNITS_PROJECT_LIMIT_DEFAULT': yt.LIMITE_PADRAO[yt.GENERAL],
        'REMAINING': 'UNKNOWN',
        'QUOTA_EVIDENCE_LEVEL': 'DECLARED_DOC_CURRENT',
        'APIFY_CHAMADA': False,
        'PORQUE': ('nenhuma chamada paga: a rota oficial é a padrão nas quatro '
                   'capacidades, e quando ela não roda a resposta é parar, '
                   'não trocar por uma rota proibida.')})
    return 0


# Os cinco alvos italianos do piloto. NÃO foram inventados: saíram do acervo, de
# `data/samples/SENSOR-PILOT/`, onde entraram pela coleta PAGA de 2026-08 — a
# mesma que custou US$ 12,33 na Apify. São imprensa técnica, marca de agroquímico
# e um criador de viticultura: três naturezas diferentes, de propósito, porque um
# piloto com cinco canais iguais não prova nada sobre o quinto.
#
# Guardados como HANDLE porque é assim que o acervo os tem. Resolver handle custa
# 1 unidade do balde GERAL; resolver por busca custaria uma das 100 do dia.
ALVOS_YOUTUBE_IT = [
    ('@agronotizietv', 'imprensa técnica agrícola'),
    ('@informatoreagrario', 'imprensa técnica agrícola'),
    ('@viticolturariccardocastaldi', 'criador — viticultura'),
    ('@BayerCropScienceIT', 'marca de agroquímico'),
    ('@SyngentaItaly', 'marca de agroquímico'),
]


# Os dois modos, e a diferença entre eles é o assunto inteiro desta fase.
#
#     OPERATIONAL   usa o checkpoint canônico, persiste, e PODE alegar retomada.
#     ONE_SHOT      prova a estrada uma vez, e NÃO alega retomada nenhuma.
#
# Um ONE-SHOT rotulado OPERATIONAL seria a mentira mais cara desta casa: alguém
# confiaria numa memória que não existe, e a coleta seguinte refaria tudo — ou,
# pior, pularia o que ninguém salvou.
OPERATIONAL = 'OPERATIONAL'
ONE_SHOT = 'ONE_SHOT'


def youtube_piloto(modo=OPERATIONAL, limite_videos=3, limite_threads=20):
    """O piloto real. Recusa rodar em modo OPERATIONAL sem o dono do checkpoint.

    Ordem, e ela é a lei:

        resolver canal (oficial) -> incremental -> metadata -> comentários
        -> PERSISTIR -> só então avançar o checkpoint.

    SEARCH fica em ZERO: os alvos já são conhecidos, e busca é 100/dia.
    """
    import youtube_oficial as yt
    sess = yt.Sessao()
    pre = _preflight_youtube(sess, modo)
    if pre is not None:
        return pre
    if modo == ONE_SHOT:
        print('\n  MODO ONE_SHOT — esta execução NÃO usa checkpoint, NÃO escreve')
        print('  checkpoint e NÃO alega retomada. Ela prova API, quota, comentários,')
        print('  custo e rota. Não prova incremental observado.')

    # UMA sessão para a corrida toda (um contador de quota, dois baldes) e UM
    # cache — para não repetir `channels.list` do mesmo canal dentro da corrida.
    cache = yt.cache_da_execucao()
    run_id = 'YT-IT-%s' % env.agora().replace(':', '').replace('-', '')[:15]
    rel = {'RUN_ID': run_id, 'MODE': modo, 'STARTED_AT': env.agora(),
           'COUNTRY_SCOPE': 'IT', 'TARGETS_REQUESTED': len(ALVOS_YOUTUBE_IT),
           'CANAIS': [], 'CHANNELS_RESOLVED': 0, 'CHANNELS_FAILED': 0,
           'VIDEO_IDS': [], 'VIDEOS_EXAMINED': 0, 'VIDEOS_RETURNED': 0,
           'THREADS': 0, 'TOP_LEVEL': 0, 'REPLIES': 0, 'COMMENTS_TOTAL': 0,
           'FEATURE_DISABLED': 0, 'ZERO_RESULTS': 0, 'ERRORS': [],
           'APIFY_CALLS': 0, 'APIFY_SPEND_USD': 0.0,
           'AUTHOR_LOCATION_PROVED_COUNT': 0, 'SOURCE_LOCATION_PROVED_COUNT': 0}
    objetos = []

    print('\n  CANAL                          CHANNEL_ID              VÍD  COM  ESTADO')
    print('  ' + '─' * 76)
    for handle, natureza in ALVOS_YOUTUBE_IT:
        linha = {'HANDLE': handle, 'NATUREZA': natureza, 'STATE': None,
                 'CHANNEL_ID': None, 'API_METHODS': []}
        try:
            # 1 · o handle vira identidade REAL. Antes da API devolver, ele é só
            #     um handle — nunca uma identidade canônica pré-inventada.
            cid, pl, proc = yt.resolver_handle(handle=handle, sessao=sess, cache=cache)
            linha.update({'CHANNEL_ID': cid, 'UPLOADS_PLAYLIST_ID': pl,
                          'CHANNEL_TITLE': proc.get('CHANNEL_TITLE'),
                          'PROVENANCE': proc['PROVENANCE'],
                          'PLAYLIST_REUSED': proc.get('REUSED', False)})
            linha['API_METHODS'].append('channels.list')
            rel['CHANNELS_RESOLVED'] += 1

            # 2 · uploads recentes. No ONE_SHOT `conhecidos` fica vazio DE
            #     PROPÓSITO e isso é declarado: não há memória a consultar, e
            #     fingir que há seria alegar retomada que não existe.
            novos, sess, r = yt.uploads_recentes(
                channel_id=cid, run_id=run_id, country_scope='IT',
                limit=limite_videos, conhecidos=(), sessao=sess, cache=cache)
            linha['API_METHODS'].append('playlistItems.list')
            linha.update({k: r[k] for k in ('UPLOADS_EXAMINED', 'NEW')})
            linha['KNOWN_SOURCE'] = 'NENHUMA — ONE_SHOT não consulta memória'
            rel['VIDEOS_EXAMINED'] += r['UPLOADS_EXAMINED']
            objetos.extend(novos)
            ids = [o['NATIVE_ID'] for o in novos][:limite_videos]
            rel['VIDEO_IDS'].extend(ids)

            # 3 · metadata em lote.
            if ids:
                metas, sess, rm = yt.metadata(video_ids=ids, run_id=run_id,
                                              country_scope='IT', sessao=sess)
                linha['API_METHODS'].append('videos.list')
                linha['METADATA_RETURNED'] = rm['RETURNED']
                linha['METADATA_MISSING'] = rm['MISSING']
                rel['VIDEOS_RETURNED'] += rm['RETURNED']
                objetos.extend(metas)

            # 4 · comentários dos vídeos REALMENTE devolvidos.
            linha['COMENTARIOS'] = []
            for vid in ids:
                cs, sess, rc = yt.comentarios(
                    video_id=vid, run_id=run_id, country_scope='IT',
                    limite_threads=limite_threads, sessao=sess)
                linha['API_METHODS'].append('commentThreads.list')
                topo = sum(1 for c in cs if not c['RAW']['IS_REPLY'])
                rel['THREADS'] += rc['THREADS']
                rel['TOP_LEVEL'] += topo
                rel['REPLIES'] += len(cs) - topo
                rel['COMMENTS_TOTAL'] += len(cs)
                if rc.get('REPLIES_COMPLETED'):
                    linha['API_METHODS'].append('comments.list')
                # As três ausências, separadas. Nunca unidas.
                if rc.get('COMMENTS_DISABLED'):
                    rel['FEATURE_DISABLED'] += 1
                elif rc['STATE'] == 'ZERO_RESULTS':
                    rel['ZERO_RESULTS'] += 1
                elif rc['STATE'] not in ('OK',):
                    rel['ERRORS'].append({'VIDEO_ID': vid, 'STATE': rc['STATE'],
                                          'NATIVE_REASON': rc.get('NATIVE_REASON')})
                objetos.extend(cs)
                linha['COMENTARIOS'].append(
                    {'VIDEO_ID': vid, 'STATE': rc['STATE'], 'COMMENTS': len(cs),
                     'THREADS': rc['THREADS'], 'REPLIES_MISSING': rc['REPLIES_MISSING'],
                     'NATIVE_REASON': rc.get('NATIVE_REASON')})
            linha['STATE'] = 'OK'
        except Exception as e:                                     # noqa: BLE001
            # Um canal falhar não apaga os outros quatro. E AUTH, QUOTA e REDE
            # NUNCA viram ZERO_RESULTS: o estado canônico diz o que houve.
            nativo = getattr(e, 'code', None)
            linha['STATE'] = (falhas.classificar(http=nativo) if nativo
                              else falhas.classificar(nativo=type(e).__name__))
            linha['NATIVE_REASON'] = type(e).__name__
            linha['ERRO'] = ss.redigir('%s: %s' % (type(e).__name__, e))[:300]
            linha['RECOVERY_ACTION'] = falhas.recuperacao(linha['STATE'])
            rel['CHANNELS_FAILED'] += 1
            rel['ERRORS'].append({'HANDLE': handle, 'STATE': linha['STATE']})
            if falhas.recuperacao(linha['STATE']) in (falhas.NO_RETRY,
                                                      falhas.NEEDS_HUMAN_FIX):
                pass          # segue para o próximo canal
            elif linha['STATE'] in ('QUOTA_EXHAUSTED', 'BUDGET_EXHAUSTED',
                                    'AUTH_EXPIRED'):
                # Continuar aqui só queimaria o resto do orçamento por nada.
                rel['PARADO_EM'] = handle
                rel['CANAIS'].append(linha)
                break
        m_parcial = sess.metricas()
        linha['QUOTA_ACUMULADA'] = {'SEARCH': m_parcial['SEARCH_CALLS_USED'],
                                    'GENERAL': m_parcial['GENERAL_UNITS_USED']}
        rel['CANAIS'].append(linha)
        print('  %-30s %-23s %3s %4s  %s'
              % (handle, linha.get('CHANNEL_ID') or '—', linha.get('NEW', '—'),
                 rel['COMMENTS_TOTAL'], linha['STATE']))

    # GEOGRAFIA: nada aqui prova lugar. Handle italiano não é autor italiano.
    rel['AUTHOR_LOCATION_PROVED_COUNT'] = 0
    rel['SOURCE_LOCATION_PROVED_COUNT'] = 0
    rel['GEOGRAFIA'] = ('COUNTRY_SCOPE=IT é o recorte do PEDIDO. A API não devolve '
                        'lugar de autor, então AUTHOR_LOCATION e SOURCE_LOCATION '
                        'saem UNKNOWN — em 100% dos objetos, de propósito.')

    unicos, dedupe_rel = env.dedupe(objetos)
    m = sess.metricas()
    rel.update({'FINISHED_AT': env.agora(),
                'OBJETOS': len(objetos), 'OBJETOS_UNICOS': len(unicos),
                'DEDUPE': dedupe_rel,
                'SEARCH_CALLS_USED': m['SEARCH_CALLS_USED'],
                'GENERAL_UNITS_USED': m['GENERAL_UNITS_USED'],
                'POR_METODO': m['POR_METODO'],
                'COST_USD': m['COST_USD'], 'COST_BASIS': m['COST_BASIS'],
                'QUOTA_MODEL_VERSION': m['QUOTA_MODEL_VERSION'],
                'CHECKPOINT_USAGE': 'NOT_OBSERVED — ONE_SHOT não usa checkpoint',
                'OPERATIONAL_OBSERVED': False})
    rel.update(_raw_do_piloto(run_id))
    env.gravar('YOUTUBE-PILOTO-IT.json', rel)
    _imprimir_piloto(rel, m)
    return 0 if rel['CHANNELS_RESOLVED'] else 5


def _raw_do_piloto(run_id):
    """Inventaria o RAW da corrida e diz ONDE a prova está — sem mentir.

    O runner morre no fim do job. Um `PATH` sozinho seria promessa que ele não
    cumpre, então o manifesto carrega hash e tamanho de cada arquivo, e o estado
    de preservação depende do artefato do Actions ter subido.

        PILOT_PROOF NÃO É OPERATIONAL_STORAGE.
    """
    import hashlib
    base = os.path.join(env.RAW_DIR, 'YOUTUBE')
    arquivos, total = [], 0
    for raiz, _sub, nomes in os.walk(base) if os.path.isdir(base) else []:
        for n in sorted(nomes):
            caminho = os.path.join(raiz, n)
            dados = open(caminho, 'rb').read()
            total += len(dados)
            arquivos.append({'FILE': os.path.relpath(caminho, env.ROOT).replace('\\', '/'),
                             'SHA256': hashlib.sha256(dados).hexdigest(),
                             'BYTES': len(dados)})
    # Quem sobe o artefato é o workflow; o script só declara o que produziu.
    dentro_do_actions = bool(os.environ.get('GITHUB_RUN_ID'))
    return {
        'RAW_FILE_COUNT': len(arquivos), 'RAW_TOTAL_BYTES': total,
        'RAW_FILES': arquivos,
        'RAW_ARTIFACT_NAME': ('youtube-piloto-raw-%s' % run_id) if dentro_do_actions
                             else None,
        'ACTIONS_RUN_ID': os.environ.get('GITHUB_RUN_ID'),
        'RETENTION_CLASS': 'ACTIONS_ARTIFACT_DEFAULT' if dentro_do_actions else 'NENHUMA',
        'RAW_PROOF_STATE': ('PILOT_PROOF_ACTIONS_ARTIFACT' if dentro_do_actions
                            else 'PARTIAL_PROOF — fora do Actions, o RAW morre com o processo'),
        'RAW_PRESERVATION_NOTE': ('PILOT_PROOF, não OPERATIONAL_STORAGE. O dono '
                                  'forward do G-42 (Storage + raw_asset) NÃO recebeu '
                                  'estes bytes.'),
    }


def _preflight_youtube(sess, modo):
    """Portão antes de gastar UMA unidade de quota. Devolve None se pode seguir.

    Nunca imprime host, usuário, senha ou DSN — só veredito.
    """
    import youtube_oficial as yt
    print('\nPRÉ-VOO DO PILOTO · modo %s\n%s' % (modo, '═' * 78))
    chave_ok = sess.disponivel()
    print('  %-42s %s' % ('YOUTUBE_DATA_API_KEY presente', 'SIM' if chave_ok else 'NÃO'))
    if modo == ONE_SHOT:
        if not chave_ok:
            print('\n  LIVE_PILOT_BLOCKED_BY_CREDENTIAL — e isto NÃO autoriza scraping.')
            return 2
        return None

    estado_cp, banco = yt.checkpoint_disponivel()
    print('  %-42s %s' % ('SUPABASE_DB_URL presente',
                          'SIM' if banco is not None else 'NÃO'))
    if banco is None:
        print('\n  CHECKPOINT_CANONICAL_UNAVAILABLE')
        print('  O dono da durabilidade é `coleta/coleta_checkpoint.py` sobre')
        print('  `checkpoint_coleta`. Sem DSN não há retomada — e esta casa NÃO cai')
        print('  para JSON, filesystem, Git nem Apify. YouTube calls: 0.')
        print('  Saída honesta disponível: fase `youtube-piloto-oneshot`.')
        return 3
    ok, veredito = yt.preflight_banco(banco)
    for nome, valor in veredito:
        print('  %-42s %s' % (nome, valor))
    if not ok:
        print('\n  CHECKPOINT_CANONICAL_UNAVAILABLE — o schema não confirmou.')
        return 3
    if not chave_ok:
        print('\n  LIVE_PILOT_BLOCKED_BY_CREDENTIAL — e isto NÃO autoriza scraping.')
        return 2
    return None


def _imprimir_piloto(rel, m):
    print('\n  OBJETOS %d (únicos %d) · VÍDEOS exam %d / devolvidos %d'
          % (rel['OBJETOS'], rel['OBJETOS_UNICOS'], rel['VIDEOS_EXAMINED'],
             rel['VIDEOS_RETURNED']))
    print('  THREADS %d · TOP-LEVEL %d · REPLIES %d · COMENTÁRIOS %d'
          % (rel['THREADS'], rel['TOP_LEVEL'], rel['REPLIES'], rel['COMMENTS_TOTAL']))
    # As três ausências, sempre nas três colunas. Juntá-las apagaria a diferença
    # entre «ninguém falou», «não havia onde falar» e «não consegui medir».
    print('  FEATURE_DISABLED %d · ZERO_RESULTS %d · ERROS %d'
          % (rel['FEATURE_DISABLED'], rel['ZERO_RESULTS'], len(rel['ERRORS'])))
    print('\n  QUOTA — dois baldes, e eles NÃO se somam')
    print('    SEARCH_CALLS_USED   %d (teto run %d · padrão projeto %d/dia)'
          % (m['SEARCH_CALLS_USED'], m['SEARCH_CALLS_RUN_LIMIT'],
             m['SEARCH_CALLS_PROJECT_LIMIT_DEFAULT']))
    print('    GENERAL_UNITS_USED  %d (teto run %d · padrão projeto %d/dia)'
          % (m['GENERAL_UNITS_USED'], m['GENERAL_UNITS_RUN_LIMIT'],
             m['GENERAL_UNITS_PROJECT_LIMIT_DEFAULT']))
    for met, d in sorted(m['POR_METODO'].items()):
        print('      %-22s %-8s %3d requests · %3d unid'
              % (met, d['BUCKET'], d['REQUESTS'], d['UNITS']))
    print('    REMAINING           UNKNOWN — a API não devolve saldo')
    print('\n  COST_USD %.2f (%s) · APIFY_CALLS %d · APIFY_SPEND US$ %.2f'
          % (rel['COST_USD'], rel['COST_BASIS'], rel['APIFY_CALLS'],
             rel['APIFY_SPEND_USD']))
    print('  RAW  %d arquivos · %d bytes · %s'
          % (rel['RAW_FILE_COUNT'], rel['RAW_TOTAL_BYTES'], rel['RAW_PROOF_STATE']))
    print('\n  CHECKPOINT %s' % rel['CHECKPOINT_USAGE'])
    print('  AUTHOR_LOCATION provados: %d · SOURCE_LOCATION provados: %d'
          % (rel['AUTHOR_LOCATION_PROVED_COUNT'], rel['SOURCE_LOCATION_PROVED_COUNT']))
    print('  %s' % rel['GEOGRAFIA'])


def portao(url):
    ok, motivo = sr.permitido(url)
    print('\n  URL       %s' % url)
    print('  AGENTE    %s' % sr.AGENTE)
    print('  VEREDITO  %s' % ('PERMITIDO' if ok else 'RECUSADO'))
    print('  MOTIVO    %s\n' % motivo)


def ledger():
    led = env.ler(LEDGER)
    if not led:
        print('\n  nenhuma execução registrada ainda — rode `piloto`.\n')
        return
    ex = led['EXECUCOES']
    print('\nLEDGER · %s\n%s' % (led.get('ATUALIZADO_EM'), '═' * 78))
    estados, plats = {}, {}
    for r in ex:
        estados[r['ESTADO']] = estados.get(r['ESTADO'], 0) + 1
        k = r['PLATFORM']
        plats.setdefault(k, {'exec': 0, 'obj': 0})
        plats[k]['exec'] += 1
        plats[k]['obj'] += r['OBJETOS']
    print('  execuções reais     %d' % len(ex))
    print('  custo total         US$ %.4f' % (led.get('CUSTO_TOTAL_USD') or 0))
    print('  por estado          %s' % estados)
    print('\n  CAN DO != DID DO — o que REALMENTE trouxe objeto:')
    for k, v in sorted(plats.items(), key=lambda x: -x[1]['obj']):
        marca = 'OBSERVADO' if v['obj'] else 'sem objeto'
        print('    %-11s execuções=%-3d objetos=%-5d %s' % (k, v['exec'], v['obj'], marca))


def main():
    args = sys.argv[1:]
    cmd = args[0] if args else 'censo'
    if cmd == 'censo':
        mz.main()
    elif cmd == 'gap':
        sys.argv = ['x', '--gap']; mz.main()
    elif cmd == 'video':
        video()
    elif cmd == 'portao':
        portao(args[1])
    elif cmd == 'piloto':
        piloto()
    elif cmd == 'ledger':
        ledger()
    elif cmd in ('sessao', 'politica'):
        sys.argv = ['x', 'preflight' if cmd == 'sessao' else 'politica']
        ss.main()
    elif cmd == 'youtube':
        youtube()
    elif cmd == 'youtube-piloto':
        return youtube_piloto(OPERATIONAL)
    elif cmd == 'youtube-piloto-oneshot':
        return youtube_piloto(ONE_SHOT)
    elif cmd == 'authmodes':
        authmodes()
    elif cmd == 'guarda':
        import social_guarda
        sys.exit(social_guarda.main())
    else:
        print(__doc__)


if __name__ == '__main__':
    # O código de saída importa: uma fase BLOQUEADA não pode parecer sucesso no CI.
    raise SystemExit(main() or 0)
