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
import time

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
    # Isto é instrução OPERACIONAL: quem a lê vai correr o que ela nomeia.
    # Até a C10.4C nomeava a rota de vídeo inteiro, que hoje está aposentada.
    print('    2. faster-whisper local   → ferramentas/reel_transcricao.py (audio-only), custo ZERO dólar')
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
           # CONVERSA TRUNCADA NAO E ERRO NEM COLETA LIMPA — e o terceiro fato.
           'PARTIAL_RESULTS': 0, 'PARTIAIS': [], 'COMPLETION_ERRORS': [],
           'THREADS_TOTAL': 0, 'THREADS_COMPLETE': 0, 'THREADS_PARTIAL': 0,
           'REPLIES_DECLARED': 0, 'REPLIES_OBSERVED': 0, 'REPLIES_MISSING': 0,
           'COMPLETION_ATTEMPTS': 0, 'THREADS_COMPLETED': 0,
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
                # O metodo foi CHAMADO — e isso que `API_METHODS` registra. Se ele
                # completou a thread e outra pergunta, e tem contador proprio.
                if rc.get('COMPLETION_ATTEMPTS'):
                    linha['API_METHODS'].append('comments.list')
                for k in ('THREADS_TOTAL', 'THREADS_COMPLETE', 'THREADS_PARTIAL',
                          'REPLIES_DECLARED', 'REPLIES_OBSERVED', 'REPLIES_MISSING',
                          'COMPLETION_ATTEMPTS', 'THREADS_COMPLETED'):
                    rel[k] = rel.get(k, 0) + (rc.get(k) or 0)
                rel['COMPLETION_ERRORS'].extend(rc.get('COMPLETION_ERRORS') or [])
                # As QUATRO ausências, separadas. Nunca unidas. `PARTIAL_RESULTS`
                # entrou aqui porque conversa truncada nao e erro de coleta nem
                # coleta limpa — e um terceiro fato, e some se cair em qualquer
                # um dos outros baldes.
                if rc.get('COMMENTS_DISABLED'):
                    rel['FEATURE_DISABLED'] += 1
                elif rc['STATE'] == 'ZERO_RESULTS':
                    rel['ZERO_RESULTS'] += 1
                elif rc['STATE'] == 'PARTIAL_RESULTS':
                    rel['PARTIAL_RESULTS'] += 1
                    rel['PARTIAIS'].append(
                        {'VIDEO_ID': vid, 'REPLIES_MISSING': rc['REPLIES_MISSING'],
                         'PARTIAL_CAUSE': rc.get('PARTIAL_CAUSE'),
                         'OBSERVED_DISCREPANCY':
                             rc.get('PARTIAL_CAUSE_IS_OBSERVED_DISCREPANCY')})
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


# ══════════════════════════════════════════════════════════════════════════
# A EVIDÊNCIA QUE ATRAVESSA A FRONTEIRA DO JOB
# ══════════════════════════════════════════════════════════════════════════
# A C10.8B-LIVE pagou por 59.743 bytes, escreveu-os, releu-os e assinou-os —
# tudo dentro do mesmo processo. O job seguinte não os encontrou: o `.gitignore`
# ignora `data/samples/**/*.gz` e o `actions/checkout` limpa o que o `.gitignore`
# ignora.
#
#     RAW CAPTURADO NO PROCESSO
#       != RAW QUE SOBREVIVE AO JOB
#       != RAW DEVOLVIDO PARA INVESTIGAÇÃO
#       != PRESERVAÇÃO FORWARD CANÔNICA.
#
# Quatro estados. Esta função fecha o TERCEIRO, e só ele.
#
# O MECANISMO NÃO É NOVO
# ------------------------
# `_raw_do_piloto`, aqui abaixo, já inventaria RAW com SHA e já decide o estado
# da prova a partir do artefato do Actions — incluindo a lei
# `UPLOAD STEP SUCCESS != ARTIFACT EXISTS`. O que não existia era a METADE DA
# VOLTA: `download-artifact` não aparece em nenhum workflow desta casa. Um
# mecanismo que só sobe é um mecanismo que ninguém provou.
#
#     GUARDAR SEM NUNCA TER IDO BUSCAR NÃO É GUARDAR. É ESPERAR.
#
#     WORKFLOW ARTIFACT != CANONICAL FORWARD STORAGE.
GAVETA_EVIDENCIA = os.path.join('.tmp', 'scrap-evidencia')

#: Retenção do mecanismo. FINITA, e dizê-lo é metade do contrato.
EVIDENCIA_RETENCAO_DIAS = 30
EVIDENCIA_RETENCAO = 'TEMPORARY'

#: O que NUNCA pode viajar dentro de um pacote de evidência. A busca é sobre os
#: BYTES, não sobre a intenção de quem os escreveu.
#:
#:     MELHOR FALHAR ALTO DO QUE REDIGIR EM SILÊNCIO: apagar evidência para o
#:     pacote passar destrói a coisa que o pacote existe para guardar.
PROIBIDO_NA_EVIDENCIA = ('apify_api_', 'Authorization:', 'Bearer ',
                         'set-cookie', 'X-Api-Key', 'SUPABASE_SERVICE_ROLE')


class EvidenciaComSegredo(RuntimeError):
    """O pacote levava algo com cara de credencial. Ele NÃO é escrito."""


def _sha_e_bytes(caminho):
    import hashlib
    with open(caminho, 'rb') as f:
        dados = f.read()
    return hashlib.sha256(dados).hexdigest(), len(dados), dados


def _tipo_do_ficheiro(nome):
    """O tipo pelo que o nome declara. `None` quando não se sabe — não se chuta."""
    baixo = nome.lower()
    if baixo.endswith('.json.gz'):
        return 'application/json+gzip'
    if baixo.endswith('.gz'):
        return 'application/gzip'
    if baixo.endswith('.json'):
        return 'application/json'
    if baixo.endswith('.txt'):
        return 'text/plain'
    return None


def _cheira_a_segredo(dados):
    """→ o termo proibido encontrado, ou None. Lê os bytes, não a intenção.

    O bruto pago nasce COMPRIMIDO: `coletor` grava `.json.gz`. Uma sonda que
    lesse só os bytes do ficheiro nunca veria um token dentro do gzip — ela
    daria verde sobre um pacote com credencial lá dentro.

        UMA SONDA QUE NÃO DESCOMPRIME DÁ VERDE AO QUE NÃO CONSEGUE LER.

    Por isso: descomprime quando é gzip, e olha as DUAS formas. Falhar a
    descompressão não é «limpo» — é `GZIP_ILEGIVEL`, e quem chama decide.
    """
    formas = [dados]
    if dados[:2] == b'\x1f\x8b':
        import gzip
        try:
            formas.append(gzip.decompress(dados))
        except Exception:                                         # noqa: BLE001
            return 'GZIP_ILEGIVEL'
    for forma in formas:
        texto = forma.decode('utf-8', 'ignore')
        for termo in PROIBIDO_NA_EVIDENCIA:
            if termo in texto:
                return termo
    return None


def evidencia_publicar(run_id, *, platform=None, capability=None, rota=None,
                       provider=None, ficheiros=None, gaveta=None):
    """Empacota o RAW DESTA corrida para atravessar a fronteira do job.

    → o estado da transferência. NÃO levanta por falha de transporte: uma
    aquisição que aconteceu não deixa de ter acontecido porque o pacote não
    subiu.

        ACQUISITION_RESULT != EVIDENCE_TRANSFER_RESULT.

    A chave do pacote é o `RUN_ID`, e só ele. «O último artefato» recuperaria o
    de outra corrida com a cara desta.
    """
    import shutil
    alvo = os.path.join(gaveta or GAVETA_EVIDENCIA, str(run_id))
    origem = list(ficheiros if ficheiros is not None else env.produzidos())
    itens, faltaram = [], []
    for caminho in origem:
        if not os.path.isfile(caminho):
            faltaram.append(os.path.basename(caminho))
            continue
        sha, tam, dados = _sha_e_bytes(caminho)
        termo = _cheira_a_segredo(dados)
        if termo:
            raise EvidenciaComSegredo(
                'o pacote de %s levava %r em %s — nada foi escrito'
                % (run_id, termo, os.path.basename(caminho)))
        itens.append({'RAW_FILENAME': os.path.basename(caminho),
                      'RAW_BYTES': tam, 'SHA256': sha,
                      'CONTENT_TYPE': _tipo_do_ficheiro(caminho)})
    if not itens:
        return {'EVIDENCE_TRANSFERRED': 'NO_RAW_PRODUCED',
                'EVIDENCE_REFERENCE': None,
                'EVIDENCE_RETENTION': EVIDENCIA_RETENCAO,
                'EVIDENCE_RETENTION_DAYS': EVIDENCIA_RETENCAO_DIAS,
                'EVIDENCE_FILES': [], 'EVIDENCE_FILES_VANISHED': faltaram,
                'CANONICAL_FORWARD_PRESERVATION': 'NO'}
    if os.path.isdir(alvo):
        shutil.rmtree(alvo)
    os.makedirs(alvo)
    for caminho in origem:
        if os.path.isfile(caminho):
            shutil.copy2(caminho, os.path.join(alvo, os.path.basename(caminho)))
    manifesto = {
        'RUN_ID': str(run_id),
        'CAPTURED_AT': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'PLATFORM': platform, 'CAPABILITY': capability,
        'ROUTE': rota, 'PROVIDER': provider,
        'FILES': itens,
        # O que este pacote É, e o que ele NÃO é. As duas frases viajam juntas.
        'EVIDENCE_CLASS': 'DIAGNOSTIC_JOB_TO_JOB',
        'EVIDENCE_RETENTION': EVIDENCIA_RETENCAO,
        'EVIDENCE_RETENTION_DAYS': EVIDENCIA_RETENCAO_DIAS,
        'CANONICAL_FORWARD_PRESERVATION': 'NO',
        'NOTA': ('WORKFLOW ARTIFACT != CANONICAL FORWARD STORAGE. Este pacote '
                 'fecha a investigacao entre jobs por %d dias. O dono forward '
                 '(Storage + raw_asset) NAO recebeu estes bytes, e o RUN_ID '
                 'daqui NAO e um RAW_OBSERVATION_ID.' % EVIDENCIA_RETENCAO_DIAS),
    }
    with open(os.path.join(alvo, 'MANIFESTO.json'), 'w', encoding='utf-8') as f:
        f.write(json.dumps(manifesto, ensure_ascii=False, indent=1,
                           sort_keys=True) + '\n')
    return {'EVIDENCE_TRANSFERRED': 'STAGED',
            'EVIDENCE_REFERENCE': alvo.replace('\\', '/'),
            'EVIDENCE_RETENTION': EVIDENCIA_RETENCAO,
            'EVIDENCE_RETENTION_DAYS': EVIDENCIA_RETENCAO_DIAS,
            'EVIDENCE_FILES': itens, 'EVIDENCE_FILES_VANISHED': faltaram,
            'CANONICAL_FORWARD_PRESERVATION': 'NO'}


def evidencia_recuperar(run_id, *, de):
    """Lê um pacote recuperado e RECALCULA o SHA de cada ficheiro.

    → o estado da recuperação. O SHA do manifesto é uma AFIRMAÇÃO; o SHA
    recalculado é a medição. Aceitar a primeira sem a segunda seria confiar
    numa etiqueta colada pelo próprio pacote.

        UM SHA QUE SÓ VEM DO MANIFESTO NÃO PROVA OS BYTES.
    """
    pasta = os.path.join(de, str(run_id))
    if not os.path.isdir(pasta):
        # Sem fallback para «o último». Um pacote de outra corrida com o mesmo
        # formato pareceria este, e a investigacao leria os bytes errados.
        return {'RECOVERED': 'NO', 'WHY': 'nenhum pacote para %s em %s'
                % (run_id, de), 'SHA_MATCH': 'NOT_APPLICABLE', 'FILES': []}
    caminho_man = os.path.join(pasta, 'MANIFESTO.json')
    if not os.path.isfile(caminho_man):
        return {'RECOVERED': 'NO', 'WHY': 'pacote sem MANIFESTO.json',
                'SHA_MATCH': 'NOT_APPLICABLE', 'FILES': []}
    with open(caminho_man, encoding='utf-8') as f:
        manifesto = json.load(f)
    if str(manifesto.get('RUN_ID')) != str(run_id):
        return {'RECOVERED': 'NO',
                'WHY': 'o manifesto diz RUN_ID=%s e pediram %s'
                       % (manifesto.get('RUN_ID'), run_id),
                'SHA_MATCH': 'NO', 'FILES': []}
    conferidos, todos_batem = [], True
    for decl in (manifesto.get('FILES') or []):
        alvo = os.path.join(pasta, decl['RAW_FILENAME'])
        if not os.path.isfile(alvo):
            conferidos.append(dict(decl, RECOVERED='NO', SHA_MATCH='NO',
                                   RECOVERED_BYTES=None, RECOVERED_SHA256=None))
            todos_batem = False
            continue
        sha, tam, _d = _sha_e_bytes(alvo)
        bate = (sha == decl['SHA256']) and (tam == decl['RAW_BYTES'])
        todos_batem = todos_batem and bate
        conferidos.append(dict(decl, RECOVERED='YES',
                               RECOVERED_BYTES=tam, RECOVERED_SHA256=sha,
                               SHA_MATCH='YES' if bate else 'NO'))
    return {'RECOVERED': 'YES' if conferidos else 'NO',
            'RUN_ID': manifesto.get('RUN_ID'),
            'PLATFORM': manifesto.get('PLATFORM'),
            'CAPABILITY': manifesto.get('CAPABILITY'),
            'ROUTE': manifesto.get('ROUTE'),
            'PROVIDER': manifesto.get('PROVIDER'),
            'EVIDENCE_RETENTION': manifesto.get('EVIDENCE_RETENTION'),
            'CANONICAL_FORWARD_PRESERVATION':
                manifesto.get('CANONICAL_FORWARD_PRESERVATION'),
            'SHA_MATCH': 'YES' if todos_batem else 'NO',
            'FILES': conferidos}


#: Os bytes que a prova da fronteira usa. REAIS, do acervo versionado desta
#: casa, e de uma corrida paga que já aconteceu — não bytes fabricados para o
#: teste passar.
#:
#: Os 59.743 bytes da C10.8B-LIVE não servem: eles já não existem. É essa a
#: razão de esta missão existir.
FIXTURE_DA_FRONTEIRA = 'data/samples/raw-paid/ES-T8-001-youtube-transcripts.raw.json.gz'


def evidencia_publicar_prova(run_id, *, gaveta=None):
    """JOB A — escreve o RAW DESTA corrida e publica o pacote. → código de saída.

    O ficheiro nasce com o `run_id` no nome, dentro de `RAW_DIR`, que o
    `.gitignore` ignora. Por isso ele NÃO existe no checkout do job seguinte —
    e é exactamente essa a fronteira que a C10.8B-LIVE não atravessou.
    """
    import gzip
    import hashlib
    origem = os.path.join(env.ROOT, FIXTURE_DA_FRONTEIRA)
    if not os.path.isfile(origem):
        print('FIXTURE_AUSENTE=%s' % FIXTURE_DA_FRONTEIRA)
        return 1
    with open(origem, 'rb') as f:
        bytes_gz = f.read()
    pasta = os.path.join(env.RAW_DIR, 'YOUTUBE')
    os.makedirs(pasta, exist_ok=True)
    alvo_gz = os.path.join(pasta, '%s.raw.json.gz' % run_id)
    with open(alvo_gz, 'wb') as f:
        f.write(bytes_gz)
    # E um segundo, NÃO comprimido: o mecanismo tem de aceitar ficheiro opaco,
    # e provar-se só com `.gz` provaria o gzip.
    alvo_json = os.path.join(pasta, '%s.raw.json' % run_id)
    with open(alvo_json, 'wb') as f:
        f.write(gzip.decompress(bytes_gz))
    env.esquecer_produzidos()
    for caminho in (alvo_gz, alvo_json):
        env.registar_produzido(caminho)
    # ── RAW ESCRITO → RELIDO → SHA CONFIRMADO → SÓ ENTÃO TRANSFERIDO ───────
    #     RAW BEFORE NORMALIZATION — e transferência DEPOIS da releitura.
    print('RAW_CAPTURED=YES')
    for caminho in (alvo_gz, alvo_json):
        with open(caminho, 'rb') as f:
            dados = f.read()
        print('  %-48s %8d bytes  %s'
              % (os.path.basename(caminho), len(dados),
                 hashlib.sha256(dados).hexdigest()))
    print('RAW_READ_BACK=YES')
    estado = evidencia_publicar(run_id, platform='YOUTUBE',
                                capability='youtube.native_caption',
                                rota='apify:transcricao', provider='APIFY',
                                gaveta=gaveta)
    for chave in ('EVIDENCE_TRANSFERRED', 'EVIDENCE_REFERENCE',
                  'EVIDENCE_RETENTION', 'EVIDENCE_RETENTION_DAYS',
                  'CANONICAL_FORWARD_PRESERVATION'):
        print('%s=%s' % (chave, estado.get(chave)))
    return 0 if estado.get('EVIDENCE_TRANSFERRED') == 'STAGED' else 1


def evidencia_recuperar_prova(run_id, *, de):
    """JOB B — confere que o workspace NÃO tem o RAW, recupera e reprocessa.

    → código de saída. Zero rede: se alguma linha daqui abrisse ligação, o
    teto de rede a zero levantava.
    """
    import gzip
    import scrap_http as http
    pasta_raw = os.path.join(env.RAW_DIR, 'YOUTUBE')
    locais = [n for n in (os.listdir(pasta_raw) if os.path.isdir(pasta_raw) else [])
              if n.startswith(str(run_id))]
    print('WORKSPACE_RAW_BEFORE=%s' % ('PRESENT %s' % locais if locais else 'ABSENT'))
    if locais:
        # O job B tem de começar SEM os bytes. Se os tem, a prova mediria o
        # workspace e não a recuperação.
        #
        #     UM JOB QUE JA TEM O FICHEIRO NAO PROVA QUE O FOI BUSCAR.
        print('PROVA_INVALIDA=o job B já tinha o RAW antes de recuperar')
        return 1
    estado = evidencia_recuperar(run_id, de=de)
    print('RECOVERED=%s' % estado.get('RECOVERED'))
    print('SHA_MATCH=%s' % estado.get('SHA_MATCH'))
    print('EVIDENCE_RETENTION=%s' % estado.get('EVIDENCE_RETENTION'))
    print('CANONICAL_FORWARD_PRESERVATION=%s'
          % estado.get('CANONICAL_FORWARD_PRESERVATION'))
    for f in estado.get('FILES') or []:
        print('  %-48s %8s bytes  match=%s'
              % (f['RAW_FILENAME'], f.get('RECOVERED_BYTES'), f['SHA_MATCH']))
    if estado.get('RECOVERED') != 'YES' or estado.get('SHA_MATCH') != 'YES':
        return 1
    # ── REPROCESSAR OS BYTES RECUPERADOS, SEM REDE E SEM PROVIDER ─────────
    # Isto é literalmente o que a C10.8B-LIVE não conseguiu fazer.
    alvo = os.path.join(de, str(run_id))
    with http.orcamento_de_rede(0) as orcamento:
        itens = None
        for f in estado['FILES']:
            caminho = os.path.join(alvo, f['RAW_FILENAME'])
            if f['RAW_FILENAME'].endswith('.gz'):
                with open(caminho, 'rb') as fh:
                    itens = json.loads(gzip.decompress(fh.read()).decode('utf-8'))
            elif f['RAW_FILENAME'].endswith('.json'):
                with open(caminho, encoding='utf-8') as fh:
                    itens = json.load(fh)
        chaves = sorted(itens[0]) if isinstance(itens, list) and itens else []
    print('REPROCESS_ITEMS=%d' % (len(itens) if isinstance(itens, list) else 0))
    print('REPROCESS_KEYS=%s' % chaves)
    print('REPROCESS_NETWORK_USED=%d' % orcamento.usados)
    print('PROVIDER_CALLS=0')
    return 0 if (itens and orcamento.usados == 0) else 1


def _raw_do_piloto(run_id):
    """Inventaria o RAW da corrida e diz ONDE a prova está — sem mentir.

    O runner morre no fim do job. Um `PATH` sozinho seria promessa que ele não
    cumpre, então o manifesto carrega hash e tamanho de cada arquivo, e o estado
    de preservação depende do artefato do Actions ter subido.

        PILOT_PROOF NÃO É OPERATIONAL_STORAGE.
    """
    import hashlib
    # ── O INVENTARIO E DO QUE ESTA CORRIDA ESCREVEU ───────────────────────
    # A versao anterior varria `RAW_DIR/YOUTUBE` inteiro. So que o checkout ja
    # traz 23 arquivos RAW versionados de corridas antigas — entao uma corrida
    # que nao chegou a chamar a API contava esses 23 como colheita propria, e o
    # relatorio saia dizendo "houve RAW". Foi exatamente o que aconteceu na
    # corrida 34257202987, com o passo da fase SKIPPED.
    #
    #     CHECKOUT NAO E COLETA.
    #
    # Agora a fonte e o registro do envelope, que so cresce quando ESTE processo
    # escreve. Processo que nao colheu inventaria zero.
    arquivos, total, sumiram = [], 0, []
    for caminho in env.produzidos():
        if os.sep + 'YOUTUBE' + os.sep not in caminho + os.sep:
            continue
        if not os.path.isfile(caminho):
            # A corrida escreveu e o arquivo nao esta mais la. Isso e um FATO
            # sobre a prova, nao um motivo para o relatorio inteiro morrer.
            sumiram.append(os.path.relpath(caminho, env.ROOT).replace('\\', '/'))
            continue
        dados = open(caminho, 'rb').read()
        total += len(dados)
        arquivos.append({'FILE': os.path.relpath(caminho, env.ROOT).replace('\\', '/'),
                         'SHA256': hashlib.sha256(dados).hexdigest(),
                         'BYTES': len(dados)})
    # ── O ESTADO DA PROVA NÃO PODE SER OTIMISTA ───────────────────────────
    # A versão anterior decidia isto só por `GITHUB_RUN_ID` existir: dentro do
    # Actions, dizia `PILOT_PROOF_ACTIONS_ARTIFACT` — mesmo com ZERO arquivos, e
    # mesmo antes de qualquer upload ter acontecido.
    #
    #     UPLOAD STEP SUCCESS ≠ ARTIFACT EXISTS.
    #     ZERO RAW FILES NÃO PODE VIRAR PILOT_PROOF_COMPLETE.
    #
    # Agora são TRÊS condições, e todas medidas: houve arquivo, o upload passou,
    # e o Actions devolveu um `artifact-id`. O workflow injeta as duas últimas em
    # `SCRAP_ARTIFACT_*`; sem elas o estado é honestamente parcial.
    dentro_do_actions = bool(os.environ.get('GITHUB_RUN_ID'))
    upload_ok = (os.environ.get('SCRAP_ARTIFACT_OUTCOME') or '') == 'success'
    artifact_id = (os.environ.get('SCRAP_ARTIFACT_ID') or '').strip()

    if not arquivos:
        # Nem PARTIAL: não houve prova a preservar. Isso é um FATO sobre a
        # corrida, não uma falha do upload.
        estado = 'NO_RAW_PRODUCED'
    elif upload_ok and artifact_id:
        estado = 'PILOT_PROOF_ACTIONS_ARTIFACT'
    elif dentro_do_actions:
        estado = ('PARTIAL_PROOF — houve RAW e o artefato não foi confirmado '
                  '(outcome=%s, artifact-id=%s)'
                  % (os.environ.get('SCRAP_ARTIFACT_OUTCOME') or 'DESCONHECIDO',
                     artifact_id or 'VAZIO'))
    else:
        estado = 'PARTIAL_PROOF — fora do Actions, o RAW morre com o processo'

    return {
        'RAW_FILE_COUNT': len(arquivos), 'RAW_TOTAL_BYTES': total,
        'RAW_FILES_VANISHED': sumiram,
        'RAW_FILES': arquivos,
        'RAW_ARTIFACT_NAME': (os.environ.get('SCRAP_ARTIFACT_NAME')
                              or ('youtube-piloto-raw-%s' % run_id
                                  if dentro_do_actions else None)),
        # NUNCA um ID inventado: ou o Actions devolveu, ou o campo não existe.
        'ARTIFACT_ID': artifact_id or None,
        'ACTIONS_RUN_ID': os.environ.get('GITHUB_RUN_ID'),
        'RETENTION_CLASS': 'ACTIONS_ARTIFACT_30D' if dentro_do_actions else 'NENHUMA',
        'RAW_PROOF_STATE': estado,
        'RAW_PROOF_COMPLETE': estado == 'PILOT_PROOF_ACTIONS_ARTIFACT',
        'RAW_PRESERVATION_NOTE': ('PILOT_PROOF, não OPERATIONAL_STORAGE. O dono '
                                  'forward do G-42 (Storage + raw_asset) NÃO recebeu '
                                  'estes bytes.'),
    }


NAO_EXECUTADO = 'NOT_EXECUTED'


def _selar_prova(rel, fase_rodou):
    """Carimba no relatorio o destino do artefato — sem recontar nada.

    Esta funcao roda num processo separado, DEPOIS do upload, so para dizer se a
    prova bruta sobreviveu ao runner. Ela nao pode inventariar RAW: o processo
    dela nao colheu nada, e recontar aqui apagaria o inventario verdadeiro que a
    fase escreveu.

        NOT_EXECUTED NAO E EXECUTED_ZERO_RESULTS.

    Duas recusas explicitas, porque as duas ja mentiram uma vez:

    1 · a fase nao rodou (skipped/failed) — entao nao ha coleta, e o relatorio
        que estava no disco e de OUTRA corrida, trazido pelo checkout;
    2 · o relatorio existe mas o `ACTIONS_RUN_ID` dele nao e o desta corrida —
        mesmo caso, so que descoberto pelo proprio relatorio.

    Nos dois, o estado e NOT_EXECUTED e nenhum numero de coleta e tocado.
    """
    corrida = os.environ.get('GITHUB_RUN_ID')
    if not fase_rodou:
        return {'RAW_PROOF_STATE': NAO_EXECUTADO,
                'RAW_PROOF_COMPLETE': False,
                'ARTIFACT_ID': None,
                'NOT_EXECUTED_REASON': 'a fase nao rodou nesta corrida',
                'REPORT_IS_FROM_THIS_RUN': False}
    if corrida and str(rel.get('ACTIONS_RUN_ID') or '') != str(corrida):
        return {'RAW_PROOF_STATE': NAO_EXECUTADO,
                'RAW_PROOF_COMPLETE': False,
                'ARTIFACT_ID': None,
                'NOT_EXECUTED_REASON': ('o relatorio no disco e de outra corrida '
                                        '(%s), veio do checkout'
                                        % (rel.get('ACTIONS_RUN_ID') or 'SEM_ID')),
                'REPORT_IS_FROM_THIS_RUN': False}

    n = int(rel.get('RAW_FILE_COUNT') or 0)
    upload_ok = (os.environ.get('SCRAP_ARTIFACT_OUTCOME') or '') == 'success'
    artifact_id = (os.environ.get('SCRAP_ARTIFACT_ID') or '').strip()
    if not n:
        estado = 'NO_RAW_PRODUCED'
    elif upload_ok and artifact_id:
        estado = 'PILOT_PROOF_ACTIONS_ARTIFACT'
    else:
        estado = ('PARTIAL_PROOF — houve RAW e o artefato nao foi confirmado '
                  '(outcome=%s, artifact-id=%s)'
                  % (os.environ.get('SCRAP_ARTIFACT_OUTCOME') or 'DESCONHECIDO',
                     artifact_id or 'VAZIO'))
    return {'RAW_PROOF_STATE': estado,
            'RAW_PROOF_COMPLETE': estado == 'PILOT_PROOF_ACTIONS_ARTIFACT',
            'ARTIFACT_ID': artifact_id or None,
            'REPORT_IS_FROM_THIS_RUN': True}


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



# ══════════════════════════════════════════════════════════════════════════
# YOUTUBE OFICIAL — a prova de que a rota canonica atravessa, ponta a ponta
# ══════════════════════════════════════════════════════════════════════════
# Esta fase NAO e um segundo motor de YouTube. Ela nao chama `youtube_oficial`
# e nao chama `social_rotas`. Ela chama o EXECUTOR, e deixa o caminho acontecer:
#
#     scrap_executor.COLLECT
#             -> social_rotas (portao do robots, trava de sessao, trava do gasto)
#                     -> adaptador_youtube (a rota crua)
#                             -> youtube_oficial (a API v3, contando quota)
#
# A fase `youtube` que ja existia chama `youtube_oficial` DIRETO. Ela continua a
# servir — mede a API sem atravessar o resto. Esta prova a cadeia inteira, que e
# outra pergunta:
#
#     MODULE EXISTS != EDGE EXISTS != FLOW EXISTS.
#
# A C1 declarou as quatro capacidades e registou os executores. Medido nesta
# missao, antes de mexer: `COLLECT` NAO conseguia chamar nenhuma delas —
# faltava `country_scope` e a forma do retorno era outra. A declaracao estava
# certa e o fluxo nunca tinha corrido. Esta fase existe para que isso nao volte
# a ser possivel sem alguem reparar.
#
# O QUE ELA NAO FAZ
# ------------------
# Nao imprime a chave. Nao imprime tamanho, prefixo nem hash da chave. Nao faz
# coleta ampla: uma busca, um canal, um lote de metadata e uma pagina de
# comentarios. E nao cai para a Apify se a API recusar — a recusa E o resultado.
ALVO_OFICIAL = {
    # Vindos do acervo desta casa, nao inventados: `YOUTUBE-PILOTO-IT.json`
    # guardou-os numa corrida autenticada anterior.
    'TERMO': 'agricoltura di precisione',
    'CANAL': 'UCUs2Mg7jvUTRt7_MSOFYM5Q',      # @agronotizietv
    'VIDEOS': ['MCnd9c2pzd8', '7Ps4g3juOIU', 'GpmfcN5huug'],
}

#: As quatro desta missao, na ordem em que uma alimenta a seguinte.
QUATRO = ('youtube.search', 'youtube.channel.discovery',
          'youtube.video.metadata', 'youtube.comments')


def youtube_oficial_prova():
    """As quatro capacidades pela rota canonica. → 0 se todas usarem a API oficial."""
    import scrap_executor as scrap
    import scrap_fornecedores as forn
    import youtube_oficial as yt

    run_id = 'C2-YT-OFICIAL-%s' % time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())
    print('\nYOUTUBE OFICIAL — a rota canonica, ponta a ponta')
    print('=' * 74)
    print('RUN_ID  %s' % run_id)

    # ── 1 · O CHECK, QUE NAO GASTA ────────────────────────────────────────
    print('\n  CHECK — de graca, antes de qualquer chamada')
    prontas = []
    for c in QUATRO:
        v = scrap.CHECK('YOUTUBE', c)
        print('    %-28s CAN=%-5s %-22s alvo=%s' % (c, v['CAN'], v['STATE'],
                                                    v['EXECUTION_TARGET']))
        if v['CAN']:
            prontas.append(c)
    if not prontas:
        print('\n  NENHUMA capacidade pronta neste ambiente.')
        print('  Isto NAO e defeito: e o CHECK a fazer o trabalho dele antes de gastar.')
        return 1

    # ── 2 · O COLLECT, PELO CAMINHO CANONICO ──────────────────────────────
    pedidos = {
        'youtube.search': dict(termo=ALVO_OFICIAL['TERMO'], limit=5),
        'youtube.channel.discovery': dict(channel_id=ALVO_OFICIAL['CANAL'], limit=5),
        'youtube.video.metadata': dict(video_ids=ALVO_OFICIAL['VIDEOS']),
        'youtube.comments': dict(video_id=ALVO_OFICIAL['VIDEOS'][0], limite_threads=5),
    }
    print('\n  CAPABILITY                   API_METHOD              ITENS  RESULT')
    print('  ' + '-' * 70)
    linhas, tudo_oficial, amostras = [], True, {}
    for c in QUATRO:
        if c not in prontas:
            linhas.append({'CAPABILITY': c, 'RESULT': 'NOT_RUN',
                           'WHY': 'CHECK recusou antes de gastar'})
            print('  %-28s %-22s %5s  NOT_RUN' % (c, '-', '-'))
            continue
        objetos, trace = scrap.COLLECT(platform='YOUTUBE', capability=c,
                                       run_id=run_id, country_scope='IT',
                                       **pedidos[c])
        # ── COMENTARIO: ZERO NAO E DESLIGADO, E UM VIDEO SO NAO PROVA NENHUM ──
        # Um video sem comentario devolve ZERO_RESULTS legitimo, e isso nao
        # prova a capacidade. Um video com comentario DESLIGADO devolve
        # FEATURE_DISABLED, e isso e um fato sobre o video — nao uma coleta
        # vazia. Sao tres coisas, e colapsa-las apagaria a diferenca para
        # sempre.
        #
        #     ZERO_RESULTS != FEATURE_DISABLED != ERROR.
        if c == 'youtube.comments':
            # A CADEIA ESCOLHE O PROPRIO ALVO, e isso e mais do que conveniencia.
            # `videos.list` ja devolveu COMMENT_COUNT por video. Perguntar
            # comentarios a um video que a propria API diz ter zero produziria um
            # ZERO_RESULTS verdadeiro e uma prova falsa: provaria que a chamada
            # atravessa, nao que a capacidade traz comentario.
            #
            #     ZERO LEGITIMO NAO PROVA CAPACIDADE. Prova que aquele video esta
            #     calado.
            candidatos = []
            for o in (amostras.get('_metadata_todos') or []):
                n = ((o.get('RAW') or {}).get('COMMENT_COUNT') or 0)
                try:
                    n = int(n)
                except (TypeError, ValueError):
                    n = 0
                if n > 0:
                    candidatos.append((n, (o.get('RAW') or {}).get('VIDEO_ID')
                                       or o.get('NATIVE_ID')))
            candidatos.sort(reverse=True)
            if candidatos:
                print('      videos com comentario, segundo a propria API: %s'
                      % ', '.join('%s(%d)' % (v, n) for n, v in candidatos[:3]))
                pedidos[c] = dict(video_id=candidatos[0][1], limite_threads=5)
            else:
                print('      a API diz COMMENT_COUNT=0 em todos os videos deste lote')
            objetos, trace = scrap.COLLECT(platform='YOUTUBE', capability=c,
                                           run_id=run_id, country_scope='IT',
                                           **pedidos[c])
        t = scrap.TRACE(trace)
        metodo = (trace.get('ROUTE') or '').split(':')[-1] or '-'
        if objetos:
            amostras[c] = objetos[0]
            if c == 'youtube.video.metadata':
                amostras['_metadata_todos'] = objetos
            # A DESCOBERTA ALIMENTA O RESTO, que e como a coleta de verdade anda:
            # descobrir, medir, e so entao perguntar comentario. Usar uma lista
            # fixa provaria que a chamada atravessa, e nao que a cadeia funciona.
            if c in ('youtube.search', 'youtube.channel.discovery'):
                ids = [o.get('NATIVE_ID') for o in objetos
                       if (o.get('CONTENT_TYPE') or '').upper() == 'VIDEO'
                       and o.get('NATIVE_ID')]
                if ids:
                    achados = amostras.setdefault('_ids_descobertos', [])
                    for i in ids:
                        if i not in achados:
                            achados.append(i)
                    pedidos['youtube.video.metadata'] = dict(
                        video_ids=achados[:5])
                    print('      %d video(s) descobertos alimentam o metadata' % len(ids))
        print('  %-28s %-22s %5d  %s' % (c, metodo, len(objetos), t['RESULT']))
        if t['PROVIDER_USED'] not in (None, forn.API_OFICIAL):
            tudo_oficial = False
            print('      FORNECEDOR INESPERADO: %s' % t['PROVIDER_USED'])
        if t['PAID_PROVIDER_USED']:
            tudo_oficial = False
            print('      ROTA PAGA USADA — isto reprova esta fase')
        linhas.append({'CAPABILITY': c, 'API_METHOD': metodo,
                       'RESULT': t['RESULT'], 'ITEM_COUNT': len(objetos),
                       'PROVIDER_REQUESTED': t['PROVIDER_REQUESTED'],
                       'PROVIDER_USED': t['PROVIDER_USED'],
                       'WHY_FALLBACK': t['WHY_FALLBACK'],
                       'PAID_PROVIDER_USED': t['PAID_PROVIDER_USED'],
                       'COST_USD': trace.get('COST_USD'),
                       'ROUTE': trace.get('ROUTE'),
                       'ROUTE_CLASS': trace.get('ROUTE_CLASS'),
                       'NATIVE_REASON': trace.get('NATIVE_REASON')})

    # ── 3 · A QUOTA, QUE E GRATIS E NAO E INFINITA ────────────────────────
    # O contador vive na sessao, e cada chamada abriu a sua. Entao o que se pode
    # dizer aqui e o MODELO e o custo POR METODO — nao o gasto somado, que
    # ninguem mediu.
    #
    #     US$ 0,00 NAO QUER DIZER «A VONTADE».
    # ── BATCHING · UMA CHAMADA PARA N IDENTIFICADORES ────────────────────
    # `videos.list` aceita ate 50 ids por chamada e custa 1 unidade seja qual
    # for o numero. Fazer N chamadas para N videos gasta N vezes a mesma coisa
    # e devolve o mesmo — e a diferenca entre 1 e 50 e o dia inteiro de quota.
    lote = [l for l in linhas if l['CAPABILITY'] == 'youtube.video.metadata']
    if lote and lote[0]['RESULT'] == 'OK':
        n = len(pedidos['youtube.video.metadata']['video_ids'])
        print('\n  BATCHING — %d identificadores, 1 chamada, 1 unidade de quota' % n)
        print('    MAX_IDS_PER_CALL   50 (limite da API)')
        print('    QUOTA_PER_CALL     1 unidade, independente de quantos ids')
        print('    objetos devolvidos %d' % lote[0]['ITEM_COUNT'])
        for o in (amostras.get('_metadata_todos') or []):
            r = o.get('RAW') or {}
            print('      %-13s views=%-9s likes=%-6s comentarios=%s'
                  % (r.get('VIDEO_ID') or o.get('NATIVE_ID'), r.get('VIEW_COUNT'),
                     r.get('LIKE_COUNT'), r.get('COMMENT_COUNT')))

    # ── OUTPUT COMPATIBILITY · o que o objeto realmente carrega ──────────
    # Nenhum campo que alguem consome pode desaparecer em silencio. Aqui sai a
    # lista, para que a diferenca seja vista e nao suposta.
    if amostras:
        print('\n  CAMPOS DO OBJETO NORMALIZADO, por capacidade')
        for c, obj in sorted(amostras.items()):
            if c.startswith('_'):
                continue
            campos = sorted(obj) if isinstance(obj, dict) else []
            bruto = sorted((obj or {}).get('RAW') or {}) if isinstance(obj, dict) else []
            print('    %-28s envelope=%d campos' % (c, len(campos)))
            if bruto:
                print('      RAW: %s' % ', '.join(bruto))

    print('\n  QUOTA — modelo oficial, dois baldes que nao se somam')
    for c in linhas:
        m = c.get('API_METHOD')
        if m and m in yt.QUOTA:
            balde, custo = yt.QUOTA[m]
            print('    %-22s balde=%-8s %s unidade(s) por chamada' % (m, balde, custo))
    print('    limite do projeto: %s' % yt.LIMITE_PADRAO)
    print('    fonte: %s' % yt.QUOTA_FONTE)

    print('\n  COST_USD 0.00 (%s) · APIFY_CALLS 0' % yt.COST_BASIS)
    print('  quota: MEASURED = a sessao contou esta chamada. PARTIAL = piso,')
    print('         alguma rota nao declarou. E os baldes nao se somam: SEARCH')
    print('         conta CHAMADAS (100/dia), GENERAL conta UNIDADES (10.000/dia).')
    print('  TODAS PELA API OFICIAL: %s' % ('SIM' if tudo_oficial else 'NAO'))
    if not tudo_oficial:
        print('  Uma das quatro saiu por outra porta. Isto reprova de proposito.')
        return 1
    executadas = [l for l in linhas if l['RESULT'] != 'NOT_RUN']
    print('  capacidades executadas: %d de %d' % (len(executadas), len(QUATRO)))
    return 0 if len(executadas) == len(QUATRO) else 1



# ══════════════════════════════════════════════════════════════════════════
# CUTOVER — a prova de que os callers antigos atravessam o SCRAP
# ══════════════════════════════════════════════════════════════════════════
# A C2 provou a API. Esta fase prova outra coisa: que o caminho de QUEM CHAMA
# passou a atravessar o executor. Sao perguntas diferentes, e a segunda e a
# unica que fecha a contradicao que a C3 existe para acabar:
#
#     A CAPACIDADE JA NAO PRECISAVA DO ATOR. OS CALLERS AINDA CONSEGUIAM
#     CHAMA-LO.
#
# Ela e BOUNDED de proposito: uma conta da comunicacao publica, um termo do
# sensor, um video de comentarios. Nao amplia coleta nenhuma para gerar prova —
# ampliar para provar seria gastar quota a fingir de rigor.
def cutover_prova():
    """Os tres callers, pelo caminho canonico, no menor tamanho possivel."""
    import scrap_executor as scrap
    import comunicacao_coleta as cc
    import sensor_coleta as sc
    import youtube_oficial as yt

    run_id = 'C3-CUTOVER-%s' % time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())
    print('\nCUTOVER — os tres callers pela rota canonica')
    print('=' * 74)
    print('RUN_ID  %s' % run_id)

    print('\n  CHECK — de graca, antes de qualquer chamada')
    for c in ('youtube.channel.resolve', 'youtube.search', 'youtube.comments'):
        v = scrap.CHECK('YOUTUBE', c)
        print('    %-28s CAN=%-5s %s' % (c, v['CAN'], v['STATE']))
        if not v['CAN']:
            print('\n  o CHECK recusou antes de gastar. Isto nao e defeito.')
            return 1

    linhas = []

    # ── 1 · COMUNICACAO PUBLICA ──────────────────────────────────────────
    # DUAS coisas precisam de prova, nao uma: que uma conta resolvivel COLHE, e
    # que uma conta `/c/` RECUSA com estado proprio. Provar so a primeira
    # esconderia o teto; provar so a segunda esconderia a capacidade.
    #
    # Vai por TRES contas no maximo. Isto e prova, nao coleta.
    contas = list(cc.contas_autorizadas('YOUTUBE'))[:3]
    itens, mans = cc._colher_pelo_scrap('YOUTUBE', contas, 30)
    print('\n  1 · COMUNICACAO PUBLICA  (%d contas, prova limitada)' % len(contas))
    colheu = None
    for m in mans:
        print('      %-46s %-26s geral=%s/%s itens~%s'
              % (str(m.get('ACCOUNT_URL'))[:46], m.get('STATUS'),
                 m.get('OFFICIAL_API_QUOTA_USED'),
                 m.get('OFFICIAL_API_QUOTA_STATE'), m.get('CHANNEL_ID') or '-'))
        if m.get('STATUS') == 'OK':
            colheu = m
    m = colheu or (mans[0] if mans else {})
    print('      provider=%-14s pago=%-6s itens no total=%d'
          % (m.get('COLLECTION_PROVIDER'), m.get('PAID'), len(itens)))
    if itens:
        print('      ACTOR no item = %r  ·  COLLECTION_PROVIDER = %r'
              % (itens[0].get('ACTOR'), itens[0].get('COLLECTION_PROVIDER')))
    nao_resolvidas = [x for x in mans if x.get('STATUS') == 'CHANNEL_IDENTITY_UNRESOLVED']
    if nao_resolvidas:
        print('      %d conta(s) sem resolvedor oficial — estado proprio, nao zero'
              % len(nao_resolvidas))
    linhas.append(('comunicacao.youtube', m.get('COLLECTION_PROVIDER'),
                   m.get('PAID'), len(itens), m.get('STATUS')))

    # ── 2 · SENSOR · BUSCA ───────────────────────────────────────────────
    it2, m2, _p = sc._rodar_scrap(sc.CAPACIDADES_SCRAP['YOUTUBE_SEARCH'],
                                  run_id=run_id, platform='YOUTUBE', country='IT',
                                  query='fusariosi grano', lote='C3',
                                  termo='fusariosi grano', limit=3)
    print('\n  2 · SENSOR BUSCA')
    print('      provider=%-14s pago=%-6s geral=%s busca=%s/%s itens=%-4d estado=%s'
          % (m2.get('COLLECTION_PROVIDER'), m2.get('PAID'),
             m2.get('OFFICIAL_API_QUOTA_USED'),
             m2.get('OFFICIAL_API_SEARCH_CALLS'),
             m2.get('OFFICIAL_API_QUOTA_STATE'), len(it2), m2.get('STATUS')))
    prov2 = sc._proveniencia(m2, None, 'C3', 'BATCH-C3')
    print('      APIFY_ACTOR = %r  ·  PAID = %r'
          % (prov2['APIFY_ACTOR'], prov2['PAID']))
    linhas.append(('sensor.search', m2.get('COLLECTION_PROVIDER'), m2.get('PAID'),
                   len(it2), m2.get('STATUS')))

    # ── 3 · SENSOR · COMENTARIOS ─────────────────────────────────────────
    # O MESMO CUIDADO DA C2: perguntar comentario a um video que a API diz ter
    # zero produz um ZERO_RESULTS verdadeiro e uma prova falsa.
    alvo = None
    ids = [o.get('NATIVE_ID') for o in it2
           if (o.get('CONTENT_TYPE') or '').upper() == 'VIDEO' and o.get('NATIVE_ID')]
    if ids:
        meta, _t = scrap.COLLECT(platform='YOUTUBE',
                                 capability='youtube.video.metadata',
                                 run_id=run_id, country_scope='IT', video_ids=ids)
        com = sorted(((int((o.get('RAW') or {}).get('COMMENT_COUNT') or 0),
                       (o.get('RAW') or {}).get('VIDEO_ID') or o.get('NATIVE_ID'))
                      for o in meta), reverse=True)
        if com and com[0][0] > 0:
            alvo = com[0][1]
            print('\n      video escolhido pela propria API: %s (%d comentarios)'
                  % (alvo, com[0][0]))
        else:
            print('\n      a API diz COMMENT_COUNT=0 em todos os videos da busca')
    if alvo is None and ids:
        alvo = ids[0]
    if alvo:
        it3, m3, _p = sc._rodar_scrap(sc.CAPACIDADES_SCRAP['YOUTUBE_COMMENTS'],
                                      run_id=run_id, platform='YOUTUBE',
                                      country='MULTI', query=alvo, lote='C3',
                                      video_id=alvo, limite_threads=5)
        print('\n  3 · SENSOR COMENTARIOS  video=%s' % alvo)
        print('      provider=%-14s pago=%-6s geral=%s busca=%s/%s itens=%-4d estado=%s'
              % (m3.get('COLLECTION_PROVIDER'), m3.get('PAID'),
                 m3.get('OFFICIAL_API_QUOTA_USED'),
                 m3.get('OFFICIAL_API_SEARCH_CALLS'),
                 m3.get('OFFICIAL_API_QUOTA_STATE'), len(it3), m3.get('STATUS')))
        if it3:
            rc = it3[0].get('RAW') or {}
            print('      campos do comentario: DATE=%s UPDATED=%s IS_REPLY=%s'
                  % (bool(rc.get('PUBLISHED_AT')), bool(rc.get('UPDATED_AT')),
                     rc.get('IS_REPLY')))
        linhas.append(('sensor.comments', m3.get('COLLECTION_PROVIDER'),
                       m3.get('PAID'), len(it3), m3.get('STATUS')))

    # ── O VEREDICTO ──────────────────────────────────────────────────────
    print('\n  CALLER                 PROVIDER        PAGO   ITENS  ESTADO')
    print('  ' + '-' * 62)
    todos_oficiais = True
    for nome, prov, pago, n, estado in linhas:
        print('  %-22s %-15s %-6s %-6d %s' % (nome, prov, pago, n, estado))
        if pago:
            todos_oficiais = False
        if prov not in (None, 'OFFICIAL_API'):
            todos_oficiais = False
    print('\n  COST_USD 0.00 (%s) · APIFY_CALLS 0' % yt.COST_BASIS)
    print('  TODOS PELA API OFICIAL, NENHUM PAGO: %s'
          % ('SIM' if todos_oficiais else 'NAO'))
    return 0 if todos_oficiais else 1


# ══════════════════════════════════════════════════════════════════════════
# A ENTRADA OPERACIONAL CANÔNICA — UMA CLI FINA, NÃO UM MOTOR NOVO
# ══════════════════════════════════════════════════════════════════════════
# A C10.6C encontrou o boundary comum e provou-o. A C10.6D mediu quem passa por
# ele: as fases de `sintonia-scrap.yml` corriam as IMPLEMENTAÇÕES diretamente —
# `instagram_janela.py`, `youtube_janela.py`, `youtube_transcrever.py` — e
# **nenhuma delas importa `social_matriz`**. Seis portas de produção, e nenhuma
# perguntava à dona da decisão se podia.
#
#     UMA DECISÃO QUE UMA PORTA NÃO CONHECE NÃO É UMA DECISÃO. É UM DESEJO.
#
# WORKFLOW É DISPARADOR, NÃO MOTOR
# ----------------------------------
# Um workflow diz O QUE quer. Não escolhe provedor, não escolhe rota, não decide
# política. Esta função é a tradução mínima entre as duas coisas:
#
#     parsear o pedido → montar o pedido canônico → chamar o dono
#
# E mais nada. Nenhuma lógica de plataforma vive aqui: o mapa de fase para
# capacidade é uma tabela, e o que cada capacidade faz é assunto do adaptador.
#
#     CLI != OWNER. UMA CLI QUE DECIDE ALGUMA COISA JÁ É UM SEGUNDO MOTOR.
#
# O QUE NÃO ESTÁ NESTA TABELA NÃO ENTRA POR AQUI
# ------------------------------------------------
# Uma fase que não tem rota canônica NÃO ganha uma entrada aqui para «fazer a
# convergência passar». Ela fica de fora, e o workflow recusa — que é o que a
# C10.6D decidiu para as quatro fases do YouTube e as quatro pagas do Instagram.
#
#     FABRICAR CAPACIDADE PARA BAIXAR O NÚMERO DE BYPASSES É MENTIR COM MÉTRICA.
#: fase do workflow → (plataforma, capacidade, argumentos fixos da fase)
FASES_CANONICAS = {
    'janela':         ('INSTAGRAM', 'instagram.profile.discovery', {'camada': 'tudo'}),
    'janela-perfis':  ('INSTAGRAM', 'instagram.profile.discovery', {'camada': 'perfis'}),
    'janela-objetos': ('INSTAGRAM', 'instagram.profile.discovery', {'camada': 'objetos'}),
    # ── A ÚNICA FASE PAGA DESTA CLI ──────────────────────────────────────────
    # Ela é canônica como as outras: entra pelo `COLLECT` e por mais nada. O que
    # a distingue vive em `FASES_PAGAS`, logo abaixo.
    'yt-legenda-paga': ('YOUTUBE', 'youtube.native_caption',
                        {'video_id': 'EAkcA_2FDN8'}),
}

#: O QUE TORNA UMA FASE PAGA, DECLARADO AQUI E NÃO NO WORKFLOW
#: ------------------------------------------------------------
#: O workflow diz um nome de fase. Tudo o resto — a autorização, o motivo, o
#: teto de dinheiro e o teto de acessos — vive em Python versionado, que se lê
#: num commit e não se muda num campo de formulário.
#:
#:     UM TETO QUE VIVE NO DISPARADOR É UM TETO QUE QUEM DISPARA ESCOLHE.
#:
#: A C10.8A-R já pagou por um teto que vivia fora do runtime. Um teto que vive
#: no YAML do workflow é a mesma família: quem despacha escolheria o número.
#:
#: O `TETO_DE_REDE` não é um palpite: foi medido na C10.8B contra a API falsa —
#: 1 POST de criação, até uma consulta de estado, 1 leitura do dataset e 2 do
#: armazém de chave-valor.
FASES_PAGAS = {
    'yt-legenda-paga': {
        'MODO': 'TRIAL',
        'MOTIVO_PAGO': 'ROUTE_NOT_ALLOWED',
        'TETO_DE_GASTO_USD': 0.10,
        'TETO_DE_REDE': 5,
        'AUTORIZACAO': ('C10.8B-LIVE · autorização humana explícita · US$0,10 no '
                        'total da missão · 1 provider run · 1 POST de criação'),
        'ALVO_PORQUE': ('sentinela do acervo: SENSOR-TR-B-3-p3, mesmo ator, '
                        'transcrição histórica preservada em '
                        'data/samples/SENSOR-PILOT/TRANSCRICOES-B.json'),
    },
}


def _banco_se_houver():
    """O dono da durabilidade, se houver DSN. `None` NÃO é falha.

    Sem banco a coleta corre e não alega retomada — exactamente o que
    `youtube_oficial.checkpoint_disponivel` já decidiu para o YouTube. O que não
    se faz é abrir um segundo dono durável em JSON porque o primeiro não estava.

        SEM CHECKPOINT NÃO SE INVENTA CHECKPOINT. DIZ-SE QUE NÃO HÁ.
    """
    dsn = (os.environ.get('SUPABASE_DB_URL') or '').strip()
    if not dsn:
        return None
    import coleta_checkpoint as ck
    return ck.Banco(dsn)


#: Onde uma fase paga deixa o registo dela. O RAW em si fica onde o dono o
#: escreveu; o que volta ao repositório é o RECORD.
GAVETA_PAGA = os.path.join('data', 'samples', 'SCRAP-YOUTUBE')


def _registar_fase_paga(fase, paga, corrida, objetos, trace):
    """Grava o registo REDIGIDO da corrida paga. → o caminho, ou None.

    POR QUE O RAW NÃO VOLTA, E POR QUE ISSO SE ESCREVE
    ----------------------------------------------------
    `coletor.executar` grava o bruto em `data/samples/raw-paid/*.raw.json.gz`, e
    o `.gitignore` desta casa ignora `data/samples/**/*.gz`. Numa corrida de
    runner, o bruto existe na máquina e NÃO volta ao repositório — e chamar a
    isso «preservado» sem dizer onde seria a mesma confusão que a casa já
    nomeou noutro sítio.

        RAW CAPTURADO NO RUNNER != RAW DEVOLVIDO AO REPOSITÓRIO
        != PRESERVAÇÃO FORWARD CANÔNICA.

    Três estados, três campos. O SHA-256 viaja mesmo quando os bytes não
    viajam: é ele que permite reconhecer os bytes se alguém os trouxer depois.
    """
    import hashlib
    med = (trace.get('ROUTER_RECORD') or {}).get('MEDIDA') or {}
    caminho_raw = med.get('SCRAP_RAW_REFERENCE')
    lido, bytes_lidos, sha_lido, forma = 'NO', None, None, None
    # O manifesto guarda o caminho CANÔNICO. Quem sabe onde os bytes foram
    # parar é o dono do bruto — e numa prova a seco a gaveta dele é outra.
    # Reler pelo caminho escrito mediria a gaveta, e não os bytes.
    if caminho_raw:
        import coletor as _ct
        caminho_raw = os.path.join(_ct.RAW_DIR, os.path.basename(caminho_raw))
    if caminho_raw and os.path.exists(caminho_raw):
        with open(caminho_raw, 'rb') as f:
            bruto = f.read()
        bytes_lidos = len(bruto)
        import gzip as _gz
        import json as _json
        try:
            itens = _json.loads(_gz.decompress(bruto).decode('utf-8'))
            sha_lido = hashlib.sha256(_json.dumps(
                itens, ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()
            lido = 'YES'
            # ── A FORMA DO BRUTO VIAJA MESMO QUE OS BYTES NÃO VIAGEM ──────
            # A C10.8B-LIVE pagou por 59.743 bytes e o objeto veio sem
            # transcrição. Para saber se o ator mudou de esquema ou se o vídeo
            # deixou de ter legenda, era preciso reler os bytes — e eles já não
            # existiam: `actions/checkout` limpa o que o `.gitignore` ignora.
            #
            #     RAW CAPTURADO NO PROCESSO != RAW QUE SOBREVIVE AO JOB.
            #
            # A forma é barata, cabe no registo e responde à pergunta sem
            # comprar outra vez.
            forma = []
            for it in (itens if isinstance(itens, list) else [itens])[:3]:
                if not isinstance(it, dict):
                    forma.append({'TIPO': type(it).__name__})
                    continue
                forma.append({k: {
                    'TIPO': type(v).__name__,
                    'TAMANHO': (len(v) if isinstance(v, (str, list, dict))
                                else None),
                    'VAZIO': (v is None or v == '' or v == [] or v == {}),
                } for k, v in sorted(it.items())})
        except Exception:                                         # noqa: BLE001
            lido = 'UNREADABLE'
    registo = {
        'SOURCE_ID': 'SCRAP-YOUTUBE/%s' % fase,
        'MISSION': 'C10.8B-LIVE',
        'CAPTURED_AT': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'RUN_ID': corrida,
        'AUTORIZACAO': paga['AUTORIZACAO'],
        'RESULT': trace.get('RESULT'),
        'ROUTE': trace.get('ROUTE'),
        'ROUTE_CLASS': trace.get('ROUTE_CLASS'),
        'PROVIDER_USED': trace.get('PROVIDER_USED'),
        'PAID_PROVIDER_USED': trace.get('PAID_PROVIDER_USED'),
        'MOTIVO_PAGO': (trace.get('ROUTER_RECORD') or {}).get('MOTIVO_PAGO'),
        'PROVIDER_RUN_ID': med.get('PROVIDER_RUN_ID'),
        'PROVIDER_STATUS': med.get('PROVIDER_STATUS'),
        'OBJETOS': len(objetos or []),
        'COST_STATE': trace.get('COST_STATE'),
        'ACTUAL_COST_USD': trace.get('ACTUAL_COST_USD'),
        'SETTLED_COST_USD': 'UNKNOWN',
        'SCRAP_RAW_CAPTURED_ON_RUNNER': med.get('SCRAP_RAW_STATE') or 'NOT_RUN',
        'SCRAP_RAW_REFERENCE': caminho_raw,
        'SCRAP_RAW_SHA256': med.get('SCRAP_RAW_SHA256'),
        'SCRAP_RAW_READ_BACK': lido,
        'SCRAP_RAW_BYTES': bytes_lidos,
        'SCRAP_RAW_SHA256_READ_BACK': sha_lido,
        'SCRAP_RAW_ITEM_SHAPE': forma,
        'SCRAP_RAW_RETURNED_TO_REPO': 'NO',
        'SCRAP_RAW_WHY_NOT_RETURNED': ('.gitignore ignora data/samples/**/*.gz — '
                                       'o bruto fica na máquina que colheu'),
        'CANONICAL_FORWARD_PRESERVATION': 'NO',
    }
    for campo in ('FINANCIAL_BUDGET_AUTHORIZED_USD', 'FINANCIAL_BUDGET_COMMITTED_USD',
                  'FINANCIAL_BUDGET_ACTUAL_USD', 'FINANCIAL_BUDGET_UNKNOWN_USD',
                  'FINANCIAL_BUDGET_REMAINING_USD', 'FINANCIAL_CALLS_REFUSED',
                  'NETWORK_BUDGET_LIMIT', 'NETWORK_REQUESTS_USED'):
        registo[campo] = trace.get(campo)
    registo['FINANCIAL_ATTEMPTS'] = trace.get('FINANCIAL_ATTEMPTS')
    registo['NETWORK_ATTEMPTS'] = trace.get('NETWORK_ATTEMPTS')
    registo['ITEMS'] = [{
        'NATIVE_ID': o.get('NATIVE_ID'), 'URL': o.get('URL'),
        'LANGUAGE': o.get('LANGUAGE'), 'CHARS': (o.get('RAW') or {}).get('CHARS'),
        'SPECIES': (o.get('RAW') or {}).get('SPECIES'),
        'TIMESTAMPS': (o.get('RAW') or {}).get('TIMESTAMPS'),
        'TRANSCRIPT_PRESENT': (o.get('RAW') or {}).get('TRANSCRIPT_PRESENT'),
        'TEXT_HEAD': (o.get('TEXT') or '')[:400] or None,
    } for o in (objetos or [])]
    os.makedirs(GAVETA_PAGA, exist_ok=True)
    alvo = os.path.join(GAVETA_PAGA, '%s.json' % fase)
    texto = json.dumps(registo, ensure_ascii=False, indent=1, sort_keys=True)
    # Um registo de corrida paga NUNCA leva credencial. A trava é aqui, e não
    # na esperança de que nada a tenha posto no rasto.
    if 'apify_api_' in texto:
        raise RuntimeError('o registo da fase paga levava credencial — abortado')
    with open(alvo, 'w', encoding='utf-8') as f:
        f.write(texto + '\n')
    print('\n  REGISTO     %s' % alvo)
    return alvo


def bruto(run_id=None):
    """Lê o BRUTO já pago e diz que FORMA ele tem. Zero rede, zero dólar.

    POR QUE ISTO EXISTE, E POR QUE NÃO É UMA SEGUNDA COMPRA
    --------------------------------------------------------
    A corrida real da C10.8B-LIVE trouxe um objeto SEM transcrição nos campos
    que o adaptador lê — `transcript` e `chars`. O bruto tem 59.743 bytes, o
    que não é o tamanho de uma resposta vazia. Ou o ator mudou o esquema de
    SAÍDA, ou o vídeo deixou de ter legenda: são duas conclusões diferentes e
    só os bytes as separam.

        UM OBJETO VAZIO NÃO DIZ SE A FONTE CALOU OU SE O CAMPO MUDOU DE NOME.

    Estes bytes já foram pagos. Lê-los é o contrário de comprar outra vez — é
    usar o que se comprou em vez de deitar fora e repetir.

        RELER O QUE JÁ SE PAGOU NÃO É PAGAR OUTRA VEZ.

    Esta função não importa o coletor, não abre socket e não conhece provider.
    """
    import gzip
    gaveta = os.path.join('data', 'samples', 'raw-paid')
    if not os.path.isdir(gaveta):
        print('SEM_GAVETA=%s' % gaveta)
        return 1
    # O run_id vem do REGISTO da corrida, e não de «o último ficheiro da
    # pasta». A gaveta guarda brutos de várias missões, e escolher pelo nome
    # mais recente leria o bruto de outra corrida com a cara desta.
    #
    #     «O ÚLTIMO DA PASTA» NÃO É «O DESTA CORRIDA».
    if run_id is None:
        registo = os.path.join(GAVETA_PAGA, 'yt-legenda-paga.json')
        if os.path.exists(registo):
            with open(registo, encoding='utf-8') as f:
                run_id = json.load(f).get('RUN_ID')
            print('RUN_ID_DO_REGISTO=%s' % run_id)
    nomes = sorted(n for n in os.listdir(gaveta) if n.endswith('.raw.json.gz')
                   and (run_id is None or n.startswith(run_id)))
    if not nomes:
        print('SEM_BRUTO_DESTA_CORRIDA=%s · gaveta com %d ficheiro(s)'
              % (run_id, len(os.listdir(gaveta))))
        return 1
    alvo = os.path.join(gaveta, nomes[-1])
    with open(alvo, 'rb') as f:
        comprimido = f.read()
    itens = json.loads(gzip.decompress(comprimido).decode('utf-8'))
    print('BRUTO         %s' % nomes[-1])
    print('BYTES_GZ      %d' % len(comprimido))
    print('ITENS         %d' % (len(itens) if isinstance(itens, list) else 1))
    if isinstance(itens, list) and itens and isinstance(itens[0], dict):
        it = itens[0]
        print('CHAVES        %s' % sorted(it))
        for k in sorted(it):
            v = it[k]
            forma = type(v).__name__
            tam = len(v) if isinstance(v, (str, list, dict)) else ''
            amostra = str(v)[:120].replace('\n', ' ')
            print('  %-22s %-6s %-7s %s' % (k, forma, tam, amostra))
    else:
        print('FORMA         %s' % type(itens).__name__)
        print('AMOSTRA       %s' % str(itens)[:300])
    return 0


def coletar(fase, *, teto=None, run_id=None, banco=None):
    """A entrada operacional. → código de saída.

    Não sabe o que é um Reel, um canal ou uma grade. Sabe traduzir uma fase num
    pedido e entregá-lo ao executor.
    """
    import scrap_executor as scrap
    if fase not in FASES_CANONICAS:
        print('FASE_SEM_ROTA_CANONICA=%s' % fase)
        print('  Esta fase não tem capacidade registada com rota. Ela NÃO corre')
        print('  por aqui, e NÃO deve correr a implementação directamente.')
        print('  As fases com rota canônica: %s'
              % ', '.join(sorted(FASES_CANONICAS)))
        return 2
    plataforma, capacidade, fixos = FASES_CANONICAS[fase]
    kw = dict(fixos)
    if teto not in (None, '', '0'):
        kw['teto'] = teto
    # ── UMA FASE PAGA LEVA OS DOIS TETOS, E ELES VÊM DA TABELA ───────────────
    # Nem desta função, nem do workflow, nem de uma variável de ambiente: da
    # declaração versionada da fase. E quem RECUSA continua a ser o `CHECK`
    # dentro do `COLLECT` — esta CLI imprime o estado, não decide por ele.
    #
    #     O PORTÃO É DE QUEM JÁ O TEM. IMPRIMIR NÃO É DECIDIR.
    paga = FASES_PAGAS.get(fase)
    if paga is not None:
        kw.update({'modo': paga['MODO'], 'permitir_pago': True,
                   'motivo_pago': paga['MOTIVO_PAGO'],
                   'teto_de_gasto': paga['TETO_DE_GASTO_USD'],
                   'teto_de_rede': paga['TETO_DE_REDE']})
    # O `RUN_ID` vem do chamador canônico. Sem um, cunha-se aqui UM por execução
    # — e diz-se que foi aqui. Inventar um `run_id` em silêncio seria fabricar
    # proveniência; declará-lo é o contrário disso.
    corrida = run_id or ('SCRAP-%s-%s' % (fase, time.strftime('%Y%m%dT%H%M%SZ',
                                                              time.gmtime())))
    print('PEDIDO CANONICO')
    print('  fase        %s' % fase)
    print('  plataforma  %s' % plataforma)
    print('  capacidade  %s' % capacidade)
    print('  run_id      %s' % corrida)
    if paga is not None:
        pronto = scrap.CHECK(plataforma, capacidade, modo=paga['MODO'])
        print('\nESTADO ANTES DO GASTO')
        print('  autorizacao        %s' % paga['AUTORIZACAO'])
        print('  alvo               %s' % fixos)
        print('  alvo porque        %s' % paga['ALVO_PORQUE'])
        print('  motivo pago        %s' % paga['MOTIVO_PAGO'])
        print('  teto de gasto USD  %s' % paga['TETO_DE_GASTO_USD'])
        print('  teto de rede       %s' % paga['TETO_DE_REDE'])
        print('  capability state   %s' % pronto.get('CAPABILITY_STATE'))
        print('  CHECK.CAN          %s' % pronto.get('CAN'))
        print('  CHECK.STATE        %s' % pronto.get('STATE'))
        print('  READY_TO_SPEND     %s' % ('YES' if pronto.get('CAN') else 'NO'))
        print('  (quem recusa e o CHECK, dentro do COLLECT — nao esta impressao)')
    objetos, trace = scrap.COLLECT(platform=plataforma, capability=capacidade,
                                   run_id=corrida, banco=banco, **kw)
    print('\nRESULTADO')
    print('  objetos     %d' % len(objetos or []))
    print('  resultado   %s' % trace.get('RESULT'))
    print('  rota        %s' % (trace.get('ROTA_ESCOLHIDA') or trace.get('ROUTE') or '—'))
    print('  executor    %s' % trace.get('EXECUTOR_ID'))
    print('  run durável %s' % trace.get('RUN_STATE_PERSISTED', 'NOT_REQUESTED'))
    if paga is not None:
        # O que uma fase paga TEM de publicar, mesmo quando nao gastou nada.
        # Um relatorio que so fala de dinheiro quando houve dinheiro obriga
        # quem le a deduzir o zero pela ausencia — e ausencia nao e valor.
        print('\nDINHEIRO E REDE')
        for campo in ('FINANCIAL_BUDGET_AUTHORIZED_USD',
                      'FINANCIAL_BUDGET_COMMITTED_USD',
                      'FINANCIAL_BUDGET_ACTUAL_USD',
                      'FINANCIAL_BUDGET_UNKNOWN_USD',
                      'FINANCIAL_BUDGET_REMAINING_USD',
                      'FINANCIAL_CALLS_REFUSED', 'COST_STATE',
                      'NETWORK_BUDGET_LIMIT', 'NETWORK_REQUESTS_USED'):
            print('  %-34s %s' % (campo, trace.get(campo)))
        for t in (trace.get('FINANCIAL_ATTEMPTS') or []):
            print('  tentativa  %s' % {k: v for k, v in t.items()
                                       if k != 'ROUTE'})
        med = (trace.get('ROUTER_RECORD') or {}).get('MEDIDA') or {}
        for campo in ('PROVIDER_RUN_ID', 'PROVIDER_STATUS', 'SCRAP_RAW_REFERENCE',
                      'SCRAP_RAW_STATE', 'SCRAP_RAW_SHA256'):
            if campo in med:
                print('  %-34s %s' % (campo, med[campo]))
        _registar_fase_paga(fase, paga, corrida, objetos, trace)
    estado = trace.get('RESULT')
    if estado in ('ROUTE_NOT_ALLOWED', 'AUTOMATION_NOT_ALLOWED'):
        print('\n  A POLÍTICA RECUSOU, E ISSO É UM RESULTADO — não um erro desta CLI.')
        return 3
    return 0 if objetos else 1


#: As fases desta CLI que ADQUIREM e que NÃO atravessam `scrap_executor.COLLECT`.
#:
#: A C10.6D mediu o alcance de cada fase por CHAMADA — não por import, que já
#: mentiu uma vez nesta casa. Das 16 fases, 3 chegam ao boundary e 13 não; de
#: entre as 13, estas quatro adquirem, e as outras nove leem o que já está cá
#: dentro ou imprimem política.
#:
#: E NÃO se converteram, de propósito. `youtube` existe para medir a API
#: DIRETAMENTE, e `youtube-oficial` existe para medir a MESMA API pelo
#: executor. O par é a medição: fazer as duas entrarem pela mesma porta apagava
#: exactamente a pergunta que elas respondem —
#:
#:     MODULE EXISTS != EDGE EXISTS != FLOW EXISTS.
#:
#: O que se corrigiu foi o silêncio. Uma fase que salta o boundary passa a
#: DIZÊ-LO na saída, para que ninguém a leia como porta de produção:
#:
#:     UM DESVIO DECLARADO É UMA MEDIÇÃO. UM DESVIO CALADO É UM BURACO.
FASES_QUE_NAO_ATRAVESSAM_O_BOUNDARY = {
    'youtube': 'mede a YouTube Data API DIRETO; o par canonico e `youtube-oficial`',
    'youtube-piloto': 'piloto real sobre a mesma estrada direta',
    'youtube-piloto-oneshot': 'o mesmo piloto, uma volta so',
    'piloto': 'prova adversarial CONTRA o roteador, incluindo rotas que devem recusar',
}


def _avisar_se_salta_o_boundary(cmd):
    """Diz, na saida, que esta fase nao atravessa a casa. → True se saltou."""
    porque = FASES_QUE_NAO_ATRAVESSAM_O_BOUNDARY.get(cmd)
    if not porque:
        return False
    print('DESVIO_DECLARADO=%s' % cmd)
    print('  Esta fase ADQUIRE e NAO atravessa `scrap_executor.COLLECT`.')
    print('  PORQUE: %s' % porque)
    print('  Sem RUN duravel, sem rasto de etapa, sem checkpoint. E medicao,')
    print('  nao e porta de producao — e esta linha existe para que ninguem a')
    print('  confunda com uma.')
    return True


def main():
    args = sys.argv[1:]
    cmd = args[0] if args else 'censo'
    _avisar_se_salta_o_boundary(cmd)
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
    elif cmd == 'youtube-oficial':
        return youtube_oficial_prova()
    elif cmd == 'cutover':
        return cutover_prova()
    elif cmd == 'youtube-piloto':
        return youtube_piloto(OPERATIONAL)
    elif cmd == 'youtube-piloto-oneshot':
        return youtube_piloto(ONE_SHOT)
    elif cmd == 'authmodes':
        authmodes()
    elif cmd == 'evidencia-publicar':
        # JOB A. Le ficheiro do acervo, escreve, rele e publica. Zero rede.
        if len(args) < 2:
            print('uso: evidencia-publicar <run_id>')
            return 2
        return evidencia_publicar_prova(args[1])
    elif cmd == 'evidencia-recuperar':
        # JOB B. Confere o workspace, recupera por RUN_ID e reprocessa. Zero rede.
        if len(args) < 2:
            print('uso: evidencia-recuperar <run_id> [pasta]')
            return 2
        return evidencia_recuperar_prova(
            args[1], de=args[2] if len(args) > 2 else GAVETA_EVIDENCIA)
    elif cmd == 'bruto':
        # Leitura de ficheiro local. Nao adquire, nao gasta e nao toca rede.
        return bruto(args[1] if len(args) > 1 else None)
    elif cmd == 'coletar':
        # `coletar <fase> [teto]` — a entrada que os workflows usam.
        if len(args) < 2:
            print('uso: coletar <fase> [teto]')
            return 2
        return coletar(args[1], teto=args[2] if len(args) > 2 else None,
                       banco=_banco_se_houver())
    elif cmd == 'guarda':
        import social_guarda
        sys.exit(social_guarda.main())
    else:
        print(__doc__)


if __name__ == '__main__':
    # O código de saída importa: uma fase BLOQUEADA não pode parecer sucesso no CI.
    raise SystemExit(main() or 0)
