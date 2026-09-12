#!/usr/bin/env python3
"""
MATRIZ SOCIAL — o que o SINTONIA SCRAP pode fazer em cada plataforma, e por quê.

    py scripts/social_matriz.py                 # a matriz inteira
    py scripts/social_matriz.py YOUTUBE         # só uma plataforma
    py scripts/social_matriz.py --gap           # onde a Apify ainda é necessária
    py scripts/social_matriz.py --json          # para o System Map

Este arquivo é DECLARAÇÃO, não execução. Ele custa zero e não toca a rede.
Quem executa é `social_rotas.py`; quem decide a ordem é a escada declarada aqui.

O CAMPO QUE MUDOU A MISSÃO INTEIRA: `PERMITIDA`
-------------------------------------------------
A missão pedia FREE-FIRST. Medindo, a pergunta útil não era "isto é grátis?" —
era **"isto é permitido?"**. As duas não coincidem, e onde elas divergem é
exatamente onde uma casa apressada constrói o que vai ter que jogar fora.

Medido em 2026-09-08, desta máquina, lendo o `robots.txt` de cada plataforma:

    youtube.com/robots.txt      `Disallow: /feeds/videos.xml`, `/results`,
                                `/youtubei/`, `/api/`
    tiktok.com/robots.txt       `User-agent: ClaudeBot` … `Disallow: /`
                                (e anthropic-ai, Claude-User, Claude-SearchBot)
    facebook.com/robots.txt     `User-agent: *` → `Disallow: /`
    x.com/robots.txt            `User-agent: *` → `Disallow: /`
    cdn.syndication.twimg.com   `User-agent: *` → `Disallow: /`
    linkedin.com/robots.txt     "The use of robots or other automated means to
                                access LinkedIn without the express permission
                                of LinkedIn is strictly prohibited."
    mastodon.uno/robots.txt     só `/media_proxy/`, `/interact/` e um endpoint
                                de instância — a API pública NÃO está barrada
    bsky.app/robots.txt         `Allow: /`
    t.me/robots.txt             30 bytes, sem restrição

E o §3 dos Termos do YouTube proíbe "access the Service using any automated
means (such as robots, botnets or scrapers)" fora de `robots.txt` ou permissão
escrita.

    ROTA QUE FUNCIONA NÃO É ROTA PERMITIDA.

Isto tem consequência direta e cara: **as três rotas gratuitas de YouTube que
esta missão MEDIU funcionando — o RSS `/feeds/videos.xml`, a busca por termo e
a extração por vídeo — estão as três em caminho `Disallow`.** Elas devolveram
dado italiano real nesta máquina. Elas não podem ser o padrão. Ficam
registradas como `ROUTE_NOT_ALLOWED`, com a medição preservada, para que
ninguém volte a "descobrir" daqui a três meses o que já custou medição hoje.

O QUE SOBRA QUANDO SÓ O PERMITIDO CONTA
-----------------------------------------
    grátis E permitido, HOJE, sem credencial:   MASTODON · BLUESKY · TELEGRAM
    permitido, mas exige credencial/aprovação:  YOUTUBE (Data API v3)
                                                THREADS (keyword_search)
                                                FACEBOOK/INSTAGRAM (PPCA/PPMA)
                                                X (API paga por volume)
    permitido só como DESCOBERTA indireta:      LINKEDIN
    sem rota própria permitida:                 TIKTOK

`DISCOVER != FETCH` NÃO É CONSOLO, É ARQUITETURA
--------------------------------------------------
LinkedIn entra nesta casa como plataforma de DESCOBERTA: a URL, a identidade e
a evidência pública de que a conta existe, vindas de fora do linkedin.com. Isso
não é uma coleta capenga — é a metade da capacidade que é permitida obter, e
ela é a metade que o negócio mais precisa (saber QUEM existe).

    URL DESCOBERTA NÃO É POST COLETADO. GUARDAR AS DUAS SEPARADAS É O QUE
    IMPEDE O RELATÓRIO DE MENTIR.
"""
import json
import sys

MEDIDO_EM = '2026-09-08'

# O preço de referência desta casa NÃO é um preço de tabela: é o que os 84 runs
# pagos já registrados em `data/samples/**/RUNS-*.json` custaram de verdade.
#     84 runs · 6.878 itens · US$ 12,81  →  US$ 1,86 por 1.000 itens
# Por ator, medido: youtube-comments 2,07 · youtube-scraper 3,81 ·
#                   youtube-transcript 4,64 · linkedin-profile-scraper 4,03
# Toda comparação "oficial vs Apify" nesta matriz usa ESTE número, não estimativa.
APIFY_USD_POR_1000_MEDIDO = 1.863

# Classes de rota, em ordem de preferência. O número é a prioridade: quem
# decide é este inteiro, nunca o gosto de quem chama.
CLASSES = {
    'PUBLIC_NATIVE': 0,      # endpoint público da própria plataforma, sem chave
    'OFFICIAL_API_FREE': 1,  # API oficial com quota gratuita
    'DIRECT_HTTP': 2,        # HTTP direto sobre superfície pública permitida
    'PUBLIC_BROWSER': 3,     # navegador público, DESLOGADO
    'LOCAL_EXECUTOR': 4,     # executor local maduro (ex.: faster-whisper)
    'LOCAL_SESSION': 5,      # navegador local JÁ LOGADO — ver social_sessao.py
    'OFFICIAL_API_PAID': 6,  # API oficial paga
    'APIFY': 7,              # último recurso, sempre com motivo declarado
}

# O AUTH MODE canônico de cada classe. É o vocabulário que o System Map mostra,
# e ele responde uma pergunta diferente da classe: a classe diz QUAL PORTA, o
# auth mode diz COM QUE CREDENCIAL — e é o segundo que decide o risco.
AUTH_MODE_DA_CLASSE = {
    'PUBLIC_NATIVE': 'PUBLIC', 'DIRECT_HTTP': 'PUBLIC', 'PUBLIC_BROWSER': 'PUBLIC',
    'LOCAL_EXECUTOR': 'PUBLIC', 'OFFICIAL_API_FREE': 'OFFICIAL_API',
    'LOCAL_SESSION': 'LOCAL_SESSION', 'OFFICIAL_API_PAID': 'OFFICIAL_PAID_API',
    'APIFY': 'APIFY',
}


def auth_mode(rota):
    return AUTH_MODE_DA_CLASSE.get(rota['CLASSE'], 'UNAVAILABLE')

# Estados de capacidade. `ROUTE_NOT_ALLOWED` é diferente de `BLOCKED`:
# BLOCKED = a plataforma me impediu tecnicamente.
# ROUTE_NOT_ALLOWED = ela permitiria tecnicamente, e eu escolhi não fazer.
#
# ── DOIS ESTADOS NOVOS NA C5, E ELES NÃO SÃO SINÓNIMOS DOS OUTROS ──────────
# `captions.download` e `captions.list` estavam os dois como `ROUTE_NOT_ALLOWED`,
# e isso dizia uma coisa falsa sobre eles: que a casa PODIA e ESCOLHEU não. Não
# é o caso de nenhum dos dois.
#
#     ROUTE_NOT_ALLOWED         eu podia, e decidi não fazer.
#     REQUIRES_OWNER_PERMISSION o dono do vídeo teria de me autorizar.
#     REQUIRES_AUTHORIZATION    falta-me credencial mais forte (OAuth), não decisão.
#
# A diferença é quem tem a chave da porta. Colapsá-los faria a casa carregar a
# culpa de uma recusa que não é dela — e, pior, esconderia que UM DELES ABRE se
# alguém der uma autorização, enquanto o outro depende de terceiros.
#
#     «EU NÃO QUIS» E «NÃO ME DEIXAM» NÃO SE ESCREVEM COM A MESMA PALAVRA.
# `PARTIAL` entrou na C10.8B-LIVE, e entrou DECLARADO. A rota `apify:transcricao`
# correu de ponta a ponta pelo caminho canônico — executor, roteador, adaptador,
# dono pago — com 1 POST, cap US$0,10 e `SUCCEEDED`, e o objeto voltou sem a
# carga da capacidade. Nem `PROVED` (não entregou) nem `POSSIBLE_NOT_PROVED`
# (já não é verdade que não se saiba se corre).
#
#     PROVIDER REACHED != CAPABILITY DELIVERED.
#
# A lista continua FECHADA, e continua a ser conferida por `test_c5`. Estender
# um vocabulário fechado é uma decisão que se escreve; deixá-lo aberto para não
# ter de a escrever é que seria o atalho.
ESTADOS = ('PROVED', 'PARTIAL', 'POSSIBLE_NOT_PROVED', 'BLOCKED',
           'ROUTE_NOT_ALLOWED', 'REQUIRES_OWNER_PERMISSION', 'REQUIRES_AUTHORIZATION',
           'CREDENTIAL_MISSING', 'NOT_APPLICABLE', 'UNKNOWN')

# Vocabulário fechado do fallback pago. "porque a Apify já estava configurada"
# não está aqui, e é justamente por isso que a lista é fechada.
MOTIVOS_PAGOS = ('FREE_ROUTE_UNAVAILABLE', 'FREE_ROUTE_INSUFFICIENT_CAPABILITY',
                 'FREE_ROUTE_UNHEALTHY', 'AUTHORIZATION_BLOCK', 'ROUTE_NOT_ALLOWED')

CAPACIDADES = (
    'DISCOVER_ACCOUNT', 'DISCOVER_POST', 'SEARCH_KEYWORD', 'SEARCH_HASHTAG',
    'FETCH_PROFILE', 'FETCH_POST', 'FETCH_VIDEO_METADATA', 'FETCH_VIDEO_BYTES',
    'FETCH_COMMENTS', 'FETCH_METRICS', 'FETCH_TRANSCRIPT', 'INCREMENTAL',
)


def r(nome, classe, permitida, estado, custo, nota, evidencia=None):
    """Uma rota candidata. `permitida` é SIM | NAO | CONDICIONAL."""
    return {
        'ROTA': nome, 'CLASSE': classe, 'PRIORIDADE': CLASSES[classe],
        'PERMITIDA': permitida, 'ESTADO': estado, 'CUSTO': custo,
        'NOTA': nota, 'EVIDENCIA': evidencia, 'MEDIDO_EM': MEDIDO_EM,
    }


# ══════════════════════════════════════════════════════════════════════════
# A MATRIZ. Uma entrada por PLATAFORMA × CAPACIDADE, com a escada de rotas.
# ══════════════════════════════════════════════════════════════════════════
MATRIZ = {
    'YOUTUBE': {
        '_NOTA': ('As três rotas gratuitas foram MEDIDAS funcionando nesta máquina em '
                  '2026-09-08 e as três estão em caminho `Disallow` do robots.txt. '
                  'A única rota permitida é a Data API v3.'),
        'SEARCH_KEYWORD': [
            r('youtube-data-api-v3:search.list', 'OFFICIAL_API_FREE', 'SIM',
              'CREDENTIAL_MISSING', '1 unidade/chamada, bucket próprio de 100 buscas/dia',
              'quota diária 10.000 unidades; search.list ganhou bucket próprio em 2026-06-01',
              'https://developers.google.com/youtube/v3/determine_quota_cost'),
            r('yt-dlp:ytsearch', 'LOCAL_EXECUTOR', 'NAO', 'ROUTE_NOT_ALLOWED', 'zero',
              'MEDIDO: 8 resultados italianos em 1,6 s, achou Bayer Crop Science Italia e '
              'Corteva. Passa por /results e /youtubei/, ambos Disallow.',
              'https://www.youtube.com/robots.txt'),
        ],
        'INCREMENTAL': [
            r('youtube-data-api-v3:playlistItems.list', 'OFFICIAL_API_FREE', 'SIM',
              'CREDENTIAL_MISSING', '1 unidade/chamada',
              'uploads do canal conhecido — a rota barata de MONITORAMENTO; SEARCH serve '
              'descoberta, não vigilância diária',
              'https://developers.google.com/youtube/v3/determine_quota_cost'),
            r('feeds/videos.xml', 'PUBLIC_NATIVE', 'NAO', 'ROUTE_NOT_ALLOWED', 'zero',
              'MEDIDO no canal Bayer Crop Science Italia: 15 uploads, com videoId, data '
              'exata, título, descrição INTEIRA (586-1148 chars) e views. Excelente e '
              'proibido: `Disallow: /feeds/videos.xml`.',
              'https://www.youtube.com/robots.txt'),
        ],
        'FETCH_VIDEO_METADATA': [
            r('youtube-data-api-v3:videos.list', 'OFFICIAL_API_FREE', 'SIM',
              'CREDENTIAL_MISSING', '1 unidade/chamada', 'até 50 IDs por chamada',
              'https://developers.google.com/youtube/v3/determine_quota_cost'),
            r('youtube:oembed', 'PUBLIC_NATIVE', 'CONDICIONAL', 'PROVED', 'zero',
              'MEDIDO 200 OK: devolve título, autor e thumbnail. NÃO devolve data, '
              'métricas nem descrição. /oembed não está em Disallow, mas o §3 dos Termos '
              'cobre acesso automatizado — por isso CONDICIONAL, não SIM.',
              'https://www.youtube.com/t/terms'),
            r('yt-dlp:extract_info', 'LOCAL_EXECUTOR', 'NAO', 'BLOCKED', 'zero',
              'MEDIDO: "Sign in to confirm you are not a bot" deste IP de datacenter. '
              'Duplamente fora: bloqueada de facto E em caminho Disallow.',
              'https://www.youtube.com/robots.txt'),
        ],
        'FETCH_COMMENTS': [
            r('youtube-data-api-v3:commentThreads.list', 'OFFICIAL_API_FREE', 'SIM',
              'CREDENTIAL_MISSING', '1 unidade/chamada', 'barato; cada página custa de novo',
              'https://developers.google.com/youtube/v3/determine_quota_cost'),
        ],
        'FETCH_TRANSCRIPT': [
            # Reconferido na C5 contra a documentação VIVA, 2026-09-11. A frase
            # continua lá, palavra por palavra: «This method is requires the user to
            # have permission to edit the video.»
            r('youtube-data-api-v3:captions.download', 'OFFICIAL_API_FREE', 'NAO',
              'REQUIRES_OWNER_PERMISSION', '200 unidades',
              'SÓ O DONO DO VÍDEO. A doc exige "permission to edit the video", e devolve '
              '403 `forbidden` sem ela. Para canal de terceiro NÃO HÁ rota oficial de '
              'legenda — e isto não é limite de chave, é limite de PERMISSÃO.',
              'https://developers.google.com/youtube/v3/docs/captions/download'),
            # Listar não é baixar, e por isso tem linha própria. Medido na C5: exige
            # OAuth (a chave de API sozinha NÃO serve) e custa 50 unidades. Mesmo que
            # listasse, o conteúdo continuaria atrás da `captions.download`.
            r('youtube-data-api-v3:captions.list', 'OFFICIAL_API_FREE', 'NAO',
              'REQUIRES_AUTHORIZATION', '50 unidades',
              'PRECISA DE OAUTH — `YOUTUBE_DATA_API_KEY` não autentica este método. E a '
              'resposta NÃO traz o texto da legenda: só a ficha da faixa. Listar uma '
              'faixa nunca foi o mesmo que poder lê-la.',
              'https://developers.google.com/youtube/v3/docs/captions/list'),
            # ⚠️ A NOTA ANTIGA CITAVA O DISALLOW ERRADO — corrigido na C5, 2026-09-11.
            # Ela dizia «`/timedtext_video` está em Disallow», e está — mas NÃO é esse
            # o caminho que o código chamaria. A `baseUrl` que sai de `captionTracks`
            # aponta para `/api/timedtext`, e quem a cobre é o `Disallow: /api/`.
            #
            #     O VEREDITO ESTAVA CERTO E A PROVA ESTAVA TROCADA.
            #     Uma citação errada cai no dia em que alguém a confere.
            #
            # E há duas autoridades ACIMA do robots.txt, medidas na C5:
            #
            #   ToS §Permissions and Restrictions: proíbe «access the Service using any
            #   automated means (such as robots, botnets or scrapers)» salvo motor de
            #   busca público conforme robots.txt, ou permissão escrita prévia. Esta
            #   casa não é motor de busca e não tem permissão escrita.
            #
            #   Developer Policies III.D.7 e III.E.6: quem usa a API «must not use
            #   undocumented APIs without express permission» e «must not ... scrape
            #   YouTube Applications». O SINTONIA usa a Data API — logo está preso a
            #   estas, e não só ao robots.txt.
            r('timedtext', 'DIRECT_HTTP', 'NAO', 'ROUTE_NOT_ALLOWED', 'zero',
              'ToS proíbe meio automatizado sem permissão escrita; `Disallow: /api/` '
              'cobre a `baseUrl` real; Developer Policies III.D.7 (API não documentada) '
              'e III.E.6 (scraping). Tecnicamente também não fecha: a página /watch '
              'devolveu 429+CAPTCHA de IP de datacenter em 2026-09-03, e timedtext sem '
              'assinatura devolve corpo vazio.',
              'https://www.youtube.com/t/terms · https://www.youtube.com/robots.txt · '
              'https://developers.google.com/youtube/terms/developer-policies'),
            r('apify:transcricao', 'APIFY', 'CONDICIONAL', 'PARTIAL', 'por minuto',
              'ÚNICA rota restante para legenda de canal de terceiro. Motivo canônico: '
              'ROUTE_NOT_ALLOWED nas rotas livres. PARTIAL e nao PROVED: a C10.8B-LIVE '
              'correu-a de ponta a ponta pelo caminho canonico — executor, roteador, '
              'adaptador, dono pago — com 1 POST, cap US$0,10 e status SUCCEEDED, e o '
              'objeto voltou SEM transcricao nos campos que o adaptador le. '
              'PROVIDER REACHED != CAPABILITY DELIVERED.',
              'docs/sintonia-scrap/C10-8B-LIVE-PRIMEIRA-ROTA-PAGA.md'),
        ],
    },

    'MASTODON': {
        '_NOTA': ('A única plataforma desta missão que entrega busca pública, sem chave, '
                  'sem aprovação e sem cláusula contrária — e com instância italiana.'),
        'SEARCH_HASHTAG': [
            r('mastodon:/api/v1/timelines/tag', 'PUBLIC_NATIVE', 'SIM', 'PROVED', 'zero',
              'MEDIDO em mastodon.uno (instância italiana), tag "agricoltura": 5 posts, com '
              'autor, data e conteúdo. Trouxe matéria do valori.it sobre pesticidas. A doc '
              'oficial marca o endpoint "Public", com a ressalva de que a instância pode '
              'desligar a prévia pública — então cada servidor precisa ser sondado, e 401 é '
              'resposta esperada, não defeito. Limite: 300 requisições / 5 min por IP.',
              'https://docs.joinmastodon.org/methods/timelines/'),
        ],
        'SEARCH_KEYWORD': [
            r('mastodon:/api/v2/search', 'PUBLIC_NATIVE', 'SIM', 'POSSIBLE_NOT_PROVED',
              'zero',
              'Desde a v4.0.0 NÃO exige token de usuário; sem token perdem-se apenas os '
              'parâmetros `resolve` e `offset`. A ressalva da prévia pública por instância '
              'vale aqui também.', 'https://docs.joinmastodon.org/methods/search/'),
        ],
        'FETCH_PROFILE': [
            r('mastodon:/api/v1/accounts/lookup', 'PUBLIC_NATIVE', 'SIM',
              'POSSIBLE_NOT_PROVED', 'zero', 'perfil público por handle', None),
        ],
        'INCREMENTAL': [
            r('mastodon:/api/v1/accounts/{id}/statuses', 'PUBLIC_NATIVE', 'SIM',
              'POSSIBLE_NOT_PROVED', 'zero', 'posts recentes de conta conhecida', None),
        ],
    },

    'BLUESKY': {
        '_NOTA': 'robots.txt diz `Allow: /`. A AppView pública responde sem autenticação.',
        'DISCOVER_ACCOUNT': [
            r('bsky:app.bsky.actor.searchActors', 'PUBLIC_NATIVE', 'SIM', 'PROVED', 'zero',
              'MEDIDO 200 OK, 3.460 bytes, busca por "agricoltura", sem token',
              'https://bsky.app/robots.txt'),
        ],
        'SEARCH_KEYWORD': [
            r('bsky:app.bsky.feed.searchPosts', 'PUBLIC_NATIVE', 'SIM', 'BLOCKED', 'zero',
              'MEDIDO 403 deste IP — e o corpo é página de borda do BunnyCDN, não o JSON '
              '`AuthMissing` do XRPC: é bloqueio de CDN, não recusa de protocolo. Confirmado '
              'de forma independente pela pesquisa desta missão, e há defeito aberto no '
              'atproto com o mesmo sintoma. A rota é permitida; o HOST está barrado — por '
              'isso BLOCKED, não ROUTE_NOT_ALLOWED. Tratar como não confiável sem auth.',
              'https://github.com/bluesky-social/atproto/issues/2838'),
        ],
        'FETCH_PROFILE': [
            r('bsky:app.bsky.actor.getProfile', 'PUBLIC_NATIVE', 'SIM',
              'POSSIBLE_NOT_PROVED', 'zero', None, None),
        ],
        'INCREMENTAL': [
            r('bsky:app.bsky.feed.getAuthorFeed', 'PUBLIC_NATIVE', 'SIM',
              'POSSIBLE_NOT_PROVED', 'zero', 'posts recentes de conta conhecida', None),
        ],
    },

    'TELEGRAM': {
        '_NOTA': ('t.me/robots.txt tem 30 bytes e nenhuma restrição. A prévia pública de '
                  'canal é feita para ser lida por qualquer um.'),
        'INCREMENTAL': [
            r('telegram:t.me/s/{canal}', 'PUBLIC_NATIVE', 'SIM', 'PROVED', 'zero',
              'MEDIDO: 20 mensagens extraídas de um canal público real. Os quatro handles '
              'agrícolas italianos que tentei NÃO EXISTEM — a ROTA está provada, os ALVOS '
              'ainda não foram descobertos. É superfície pública oficial (a prévia que o '
              'Telegram serve a quem não tem conta), mas é PÁGINA, não API documentada: '
              'não há promessa de estabilidade de formato. t.me não publica robots.txt.',
              'https://core.telegram.org/api'),
            r('telegram:Bot API', 'OFFICIAL_API_FREE', 'NAO', 'NOT_APPLICABLE', 'zero',
              'a FAQ oficial é explícita: o bot recebe "all messages from channels where '
              'they are a member". Não há endpoint que aceite um @canal arbitrário. Não '
              'serve para vigilância pública.', 'https://core.telegram.org/bots/faq'),
            r('telegram:MTProto/TDLib', 'LOCAL_EXECUTOR', 'CONDICIONAL', 'UNKNOWN', 'zero',
              'rota oficialmente suportada, mas exige CONTA DE USUÁRIO (api_id/api_hash). Se '
              'conta automatizada para coleta em massa é permitida pelos Termos: NÃO ESTÁ '
              'CLARO na doc, e contas assim são banidas na prática. Não adotar sem decisão '
              'humana.', 'https://core.telegram.org/api'),
        ],
    },

    'THREADS': {
        '_NOTA': ('Surpresa boa da pesquisa: a Meta publica um endpoint de busca por '
                  'palavra-chave em conteúdo público de terceiros. É o único da família '
                  'Meta desenhado para isso.'),
        'SEARCH_KEYWORD': [
            r('threads:/v1.0/keyword_search', 'OFFICIAL_API_FREE', 'CONDICIONAL',
              'CREDENTIAL_MISSING', 'zero dentro da quota',
              'search_mode=KEYWORD|TAG, search_type=TOP|RECENT, limite 100/página, '
              '2.200 consultas por usuário por 24 h. SEM aprovação da permissão '
              '`threads_keyword_search` devolve SÓ os posts do próprio usuário — com ela, '
              'busca todo o público. É App Review, não chave.',
              'https://developers.facebook.com/docs/threads/keyword-search'),
        ],
        'SEARCH_HASHTAG': [
            r('threads:/v1.0/keyword_search?search_mode=TAG', 'OFFICIAL_API_FREE',
              'CONDICIONAL', 'CREDENTIAL_MISSING', 'zero dentro da quota',
              'mesmo endpoint, outro modo — não é rota separada',
              'https://developers.facebook.com/docs/threads/keyword-search'),
        ],
    },

    'FACEBOOK': {
        '_NOTA': ('`robots.txt` do facebook.com é `Disallow: /` para todo agente. Não '
                  'existe rota de HTTP direto permitida. Tudo passa por App Review.'),
        'DISCOVER_ACCOUNT': [
            r('graph:/pages/search', 'OFFICIAL_API_FREE', 'CONDICIONAL', 'CREDENTIAL_MISSING',
              'zero dentro da quota',
              'exige Page Public Metadata Access: App Review + verificação de negócio. '
              'Devolve id, name, location, link. (`/search?type=page` é a forma legada.)',
              'https://developers.facebook.com/docs/pages/searching/'),
        ],
        'FETCH_POST': [
            r('graph:/{page-id}/posts', 'OFFICIAL_API_FREE', 'CONDICIONAL',
              'CREDENTIAL_MISSING', 'zero dentro da quota',
              'exige Page Public Content Access: App Review + verificação de negócio. '
              'Em modo de desenvolvimento só funciona em Página que o app já administra.',
              'https://developers.facebook.com/docs/features-reference/page-public-content-access'),
            r('apify:facebook', 'APIFY', 'CONDICIONAL', 'POSSIBLE_NOT_PROVED', 'por item',
              'motivo canônico enquanto o App Review não sair: AUTHORIZATION_BLOCK', None),
        ],
        'FETCH_PROFILE': [
            r('graph:/{page-id}?fields=...', 'OFFICIAL_API_FREE', 'CONDICIONAL',
              'CREDENTIAL_MISSING', 'zero dentro da quota',
              'campos públicos básicos com app token; o resto atrás de PPMA/PPCA',
              'https://developers.facebook.com/docs/graph-api/reference/page/'),
        ],
        'FETCH_VIDEO_METADATA': [
            r('graph:/{page-id}/videos', 'OFFICIAL_API_FREE', 'CONDICIONAL',
              'CREDENTIAL_MISSING', 'zero dentro da quota', 'atrás de PPCA', None),
        ],
    },

    'INSTAGRAM': {
        '_NOTA': ('Estrada MADURA nesta casa — `instagram_janela.py` já mede a rota do '
                  'navegador público e `instagram_transcrever.py` já transcreve local. '
                  'Esta missão NÃO reescreve nada disso; só declara onde a Apify sobra.'),
        'FETCH_PROFILE': [
            r('instagram_janela.py:embed', 'PUBLIC_BROWSER', 'CONDICIONAL', 'PROVED', 'zero',
              'já medido nesta casa em 2026-09-02: bio, seguidores, denominador de posts',
              'scripts/instagram_janela.py'),
            r('graph:business_discovery', 'OFFICIAL_API_FREE', 'CONDICIONAL',
              'CREDENTIAL_MISSING', 'zero dentro da quota',
              'exige conta Business/Creator ligada a Página; alvo também precisa ser '
              'Business/Creator. Isento do rate limit do Business Use Case.',
              'https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/reference/ig-user/business_discovery/'),
        ],
        'INCREMENTAL': [
            r('instagram_janela.py:grade', 'PUBLIC_BROWSER', 'CONDICIONAL', 'PROVED', 'zero',
              'já medido: os 12 itens mais recentes, legenda inteira, data exata, curtidas; '
              'em reel, visualizações e duração', 'scripts/instagram_janela.py'),
        ],
        'FETCH_TRANSCRIPT': [
            # ── DECISÃO HUMANA, C10.5D · 2026-09-11 ──────────────────────────
            # Esta linha deixou de ser `SIM`. O que mudou NÃO foi a capacidade:
            # foi a leitura do `robots.txt` VIVO de `instagram.com`, medida pelo
            # portão desta casa e confirmada lendo o ficheiro — 6.256 bytes, e o
            # bloco que nos serve é `User-agent: *` / `Disallow: /`. O agente
            # desta coleta não aparece nomeado em lado nenhum.
            #
            #     ROTA QUE FUNCIONA NÃO É ROTA PERMITIDA.
            #
            # E a rota que esta linha nomeia NÃO é um motor local: ela baixa o
            # MP4 INTEIRO da CDN da Meta antes de reconhecer a fala. É por isso
            # que o `NAO` lhe pertence — não por causa do `faster-whisper`.
            #
            # O QUE ESTE `NAO` **NÃO** DIZ:
            #     · não diz que o reconhecedor local está proibido;
            #     · não diz que os bytes já preservados nesta casa não podem
            #       voltar a ser processados;
            #     · não rebaixa a capacidade medida — `instagram.reel.transcribe`
            #       continua `PROVEN` em `scrap_capacidades.py`, e tem de
            #       continuar.
            #
            #     CAN DO != MAY DO != DID DO.   REUSAR != ADQUIRIR.
            #
            # Quem faz valer esta decisão é o portão que vive no ponto onde o
            # socket abre (`ferramentas/reel_transcricao.py`), e é por viver lá
            # que ele recusa a aquisição sem recusar o reprocessamento.
            r('instagram_transcrever.py:faster-whisper', 'LOCAL_EXECUTOR', 'NAO',
              'ROUTE_NOT_ALLOWED',
              'zero dólar, ~6 h/1.000 vídeos no modelo small',
              'A ROTA SAI PARA A PLATAFORMA: baixa o MP4 inteiro da CDN da Meta e '
              'só depois transcreve. O `robots.txt` vivo de instagram.com responde '
              '`Disallow: /` ao agente desta casa — medido na C10.5. O motor local '
              'continua provado e os bytes já preservados continuam reprocessáveis; '
              'o que está recusado é SAIR para buscar mídia nova.',
              'docs/sintonia-scrap/C10-5-FLUXO-DA-COLLECTION.md'),
        ],
        'FETCH_COMMENTS': [
            r('apify:comments', 'APIFY', 'CONDICIONAL', 'PROVED', 'por item',
              'O ÚNICO buraco real medido: a rota grátis dá o NÚMERO de comentários, nunca '
              'o TEXTO. Motivo canônico: FREE_ROUTE_INSUFFICIENT_CAPABILITY.',
              'scripts/instagram_janela.py'),
        ],
        'FETCH_POST': [
            r('instagram_janela.py:embed', 'PUBLIC_BROWSER', 'CONDICIONAL', 'PROVED', 'zero',
              'cobre os 12 mais recentes', 'scripts/instagram_janela.py'),
            r('apify:instagram-scraper', 'APIFY', 'CONDICIONAL', 'PROVED', 'por item',
              'O SEGUNDO buraco: qualquer coisa ALÉM dos 12 itens mais recentes. Motivo '
              'canônico: FREE_ROUTE_INSUFFICIENT_CAPABILITY.', 'scripts/instagram_janela.py'),
        ],
    },

    'LINKEDIN': {
        '_NOTA': ('PRIORIDADE DE NEGÓCIO com a rota mais estreita da missão. O robots.txt '
                  'abre com "The use of robots or other automated means to access LinkedIn '
                  'without the express permission of LinkedIn is strictly prohibited." '
                  'Só `LinkedInBot` tem `Allow: /`. Portanto: DESCOBERTA INDIRETA, e '
                  'nenhum acesso automatizado ao linkedin.com.'),
        'DISCOVER_ACCOUNT': [
            r('descoberta-indireta:site-da-organizacao', 'DIRECT_HTTP', 'SIM',
              'POSSIBLE_NOT_PROVED', 'zero',
              'A URL do LinkedIn colhida do SITE DA PRÓPRIA ORGANIZAÇÃO (rodapé, "seguici su"), '
              'nunca do linkedin.com e nunca de buscador. O §8.2 do User Agreement proíbe as '
              'DUAS coisas: raspar o serviço E "copy, use, display or distribute any '
              'information obtained from the Services, whether directly or through third '
              'parties (such as search tools or data aggregators or brokers)". Ler o site da '
              'própria empresa não é obter informação do LinkedIn — é obter da empresa. '
              'Guarda DISCOVERY_SOURCE, DISCOVERED_URL, TARGET_TYPE, DISCOVERED_AT, e nunca '
              'conteúdo de post fabricado.',
              'https://www.linkedin.com/legal/user-agreement'),
        ],
        'FETCH_POST': [
            r('linkedin:Community Management API', 'OFFICIAL_API_PAID', 'NAO',
              'ROUTE_NOT_ALLOWED', 'programa de parceiro',
              '`r_organization_social` é "restricted to organizations in which the '
              'authenticated member has ADMINISTRATOR / DIRECT_SPONSORED_CONTENT_POSTER / '
              'CONTENT_ADMIN". Lê a Página que o app ADMINISTRA — a nossa, não a do '
              'concorrente. Não existe API que leia post público de organização de terceiro. '
              'Para vigilância ampla de concorrente: NÃO EXISTE ROTA PERMITIDA. Isto é uma '
              'resposta, não uma pendência.',
              'https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/posts-api'),
            r('apify:harvestapi~linkedin-*', 'APIFY', 'NAO', 'ROUTE_NOT_ALLOWED',
              'US$ 4,03/1.000 medido nesta casa',
              'RISCO REGISTRADO, NÃO ENDOSSADO: esta casa JÁ gastou US$ 0,484 em 120 perfis '
              'por esta rota. O §8.2 alcança explicitamente dado obtido "through third '
              'parties (such as data aggregators or brokers)" — o intermediário não muda a '
              'cláusula. A missão manda NÃO remover Apify agora; então fica declarado como '
              'dependência legada com risco jurídico aberto, para decisão humana.',
              'https://www.linkedin.com/legal/user-agreement'),
        ],
    },

    'X': {
        '_NOTA': ('x.com e cdn.syndication.twimg.com têm os dois `User-agent: *` → '
                  '`Disallow: /`. Só sobra a API oficial, que é paga por volume.'),
        'SEARCH_KEYWORD': [
            r('x-api:recent-search', 'OFFICIAL_API_PAID', 'SIM', 'CREDENTIAL_MISSING',
              'US$ 0,005 por post lido = US$ 5,00 por 1.000',
              'As faixas Basic/Pro ACABARAM: desde 2026-02-06 a X API é pay-per-usage pura, '
              'sem assinatura e SEM faixa gratuita de leitura. Teto de 3 milhões de posts '
              'por ciclo. Contra o preço medido desta casa na Apify (US$ 1,86/1.000), a API '
              'oficial custa ~2,7x MAIS por objeto — e mesmo assim é a única rota permitida, '
              'porque x.com e o CDN de sindicância são os dois `Disallow: /`. '
              'DISCOVERY-FIRST: estreitar a consulta ANTES de comprar.',
              'https://docs.x.com/x-api/getting-started/pricing'),
            r('cdn.syndication.twimg.com', 'DIRECT_HTTP', 'NAO', 'ROUTE_NOT_ALLOWED', 'zero',
              'MEDIDO 200 OK com métricas completas do post. E o robots do próprio host é '
              '`Disallow: /`. Funciona e não pode.',
              'https://cdn.syndication.twimg.com/robots.txt'),
        ],
    },

    'TIKTOK': {
        '_NOTA': ('O robots.txt do TikTok nomeia ClaudeBot, Claude-User, Claude-SearchBot e '
                  'anthropic-ai num bloco `Disallow: /`. E a Research API — a única que dá '
                  'dado público rico — EXCLUI empresa por desenho: exige instituição '
                  'acadêmica ou sem fins lucrativos, com revisão ética e independência de '
                  'interesse comercial. A ADAMA não é elegível. Sobra o oEmbed.'),
        'FETCH_VIDEO_METADATA': [
            r('tiktok:oembed', 'PUBLIC_NATIVE', 'CONDICIONAL', 'POSSIBLE_NOT_PROVED', 'zero',
              'Produto DOCUMENTADO pela TikTok, sem chave e sem login. MEDIDO: responde 200 '
              'e valida (400 em id inventado). Devolve título, autor, thumbnail — e NENHUMA '
              'métrica. Só serve para URL JÁ CONHECIDA: não é descoberta. O §5 dos Termos '
              'proíbe "use automated scripts to collect information", por isso CONDICIONAL.',
              'https://developers.tiktok.com/doc/embed-videos/'),
        ],
        'DISCOVER_ACCOUNT': [
            r('tiktok:perfil-html', 'DIRECT_HTTP', 'NAO', 'ROUTE_NOT_ALLOWED', 'zero',
              'MEDIDO: 3 handles diferentes devolveram 367 KB do MESMO tamanho — é a casca '
              'de JavaScript, sem dado. Bloqueada de facto E proibida por robots.',
              'https://www.tiktok.com/robots.txt'),
        ],
        'FETCH_VIDEO_BYTES': [
            r('marcar:MEDIA_FETCH_UNAVAILABLE', 'PUBLIC_NATIVE', 'SIM', 'NOT_APPLICABLE',
              'zero', 'guardar URL + metadata e declarar a ausência. NÃO cair para Apify '
              'automaticamente — a missão proíbe.', None),
        ],
    },

    'REDDIT': {
        '_NOTA': ('Fechou a última porta anônima em 2026. Prioridade BAIXA para a Itália: '
                  'a conversa agrícola italiana não mora aqui.'),
        'SEARCH_KEYWORD': [
            r('reddit:/r/{sub}/.json', 'PUBLIC_NATIVE', 'NAO', 'BLOCKED', 'zero',
              'MEDIDO 403 deste IP em www E em oauth.reddit.com. As rotas `.json` sem token '
              'foram depreciadas por volta de 2026-05-28 e passaram a devolver 403. '
              'EVIDÊNCIA SECUNDÁRIA: os domínios do Reddit recusaram também o pesquisador '
              'desta missão, então isto precisa de conferência humana num navegador antes '
              'de virar decisão.', None),
            r('reddit:OAuth Data API', 'OFFICIAL_API_FREE', 'CONDICIONAL',
              'CREDENTIAL_MISSING', 'faixa gratuita ~100 consultas/min, NÃO comercial',
              'uso comercial exige contrato à parte; registro de app virou aprovação manual. '
              'Preço empresarial não publicado.', None),
        ],
    },
}


# ══════════════════════════════════════════════════════════════════════════
# QUOTA — A REGRA DECLARATIVA, COM UM DONO SÓ
# ══════════════════════════════════════════════════════════════════════════
# Por que ela mora AQUI e não no executor: em 2026-09-08 esta matriz já registrava
# o modelo de dois buckets do YouTube enquanto `youtube_oficial.py` mantinha uma
# tabela própria com o número antigo (`search.list = 100 unidades`). Duas tabelas,
# duas verdades, e a errada era a que executava.
#
#     A MATRIZ NÃO PODE SABER UMA COISA E O EXECUTOR OUTRA.
#
# A divisão é: aqui vive a REGRA (método -> bucket, custo, limite padrão do
# projeto); no executor vive a MECÂNICA (contar, aplicar teto, parar). Regra é
# declaração e tem um dono; mecânica é código e pode ter vários.
#
# `LIMITE_PADRAO_PROJETO` é o que o Google concede a um projeto NOVO — não o que
# este projeto tem. Se alguém pedir aumento, isto aqui deixa de valer e precisa
# ser remedido. Por isso ele se chama PADRÃO, e não LIMITE.
QUOTA_MODEL_VERSION = '2026-09-08:two-buckets'
QUOTA_BASIS = ('documentação oficial lida em 2026-09-08: "The search.list and '
               'videos.insert methods have their own quota buckets" e "100 '
               'search.list calls, 100 videos.insert calls, and 10,000 units per '
               'day combined for all other endpoints"')
QUOTA_FONTE = 'https://developers.google.com/youtube/v3/determine_quota_cost'

QUOTA_METODO = {
    'YOUTUBE': {
        # método               (bucket,    custo por chamada)
        'search.list':         ('SEARCH', 1),
        'channels.list':       ('GENERAL', 1),
        'playlistItems.list':  ('GENERAL', 1),
        'videos.list':         ('GENERAL', 1),
        'commentThreads.list': ('GENERAL', 1),
        'comments.list':       ('GENERAL', 1),
    },
}

LIMITE_PADRAO_PROJETO = {
    'YOUTUBE': {'SEARCH': 100, 'GENERAL': 10000},
}


def quota_de(platform, metodo):
    """(bucket, custo) do método. Levanta se o método não for declarado.

    Levantar é deliberado: um método sem regra de quota declarada não pode ser
    chamado, porque a chamada sairia da conta sem ninguém perceber.
    """
    tabela = QUOTA_METODO.get(platform.upper())
    if not tabela or metodo not in tabela:
        raise KeyError('método sem quota declarada nesta matriz: %s/%s'
                       % (platform, metodo))
    return tabela[metodo]


def buckets_de(platform):
    return tuple(sorted(LIMITE_PADRAO_PROJETO.get(platform.upper(), {})))


def capacidade_declarada(platform, capability):
    """A matriz declara esta capacidade para esta plataforma? Sim/não, sem opinião."""
    return capability.upper() in (MATRIZ.get(platform.upper()) or {})


def rota_declarada(platform, capability, auth_mode):
    """A rota declarada para (plataforma, capacidade, auth_mode) — ou None.

    Existe porque a política de sessão estava respondendo por conta própria, e
    inventava capacidade: perguntada por `TIKTOK/SEARCH_KEYWORD/OFFICIAL_API`,
    respondia USABLE mesmo sem NENHUMA linha declarada aqui.

        API OFICIAL EXISTIR NÃO É ESTA CAPACIDADE EXISTIR.

    A matriz é o dono único dessa verdade. Quem quiser saber pergunta aqui —
    ninguém mantém uma segunda tabela em paralelo.
    """
    rotas = (MATRIZ.get(platform.upper()) or {}).get(capability.upper())
    if not rotas:
        return None
    for r in rotas:
        if AUTH_MODE_DA_CLASSE.get(r['CLASSE']) == auth_mode:
            return r
    return None


# ══════════════════════════════════════════════════════════════════════════
# A DECISÃO, PARA QUEM PRECISA DELA ANTES DE TOCAR A REDE
# ══════════════════════════════════════════════════════════════════════════
#: O que a política responde. Três palavras, e nenhuma cobre a outra.
NAO_DECLARADA = 'NOT_DECLARED'
NAO_PERMITIDA = 'ROUTE_NOT_ALLOWED'
PERMITIDA_SIM = 'ALLOWED'


def decisao(platform, capability):
    """A decisão desta matriz para (plataforma, capacidade). LÊ — não decide.

    Existe porque quem adquire precisa perguntar ANTES de sair para a rede, e
    até aqui só o roteador sabia perguntar. Quem não passava pelo roteador não
    tinha a quem perguntar, e uma pergunta que não tem dono é uma pergunta que
    não se faz.

        PERGUNTAR DEPOIS DE BAIXAR É CONFERIR O BILHETE DEPOIS DA VIAGEM.

    Esta função não escreve `PERMITIDA` nenhuma. Ela devolve o que já está
    escrito na `MATRIZ`, traduzido para três palavras que NÃO são sinónimos:

        NOT_DECLARED       ninguém mediu esta capacidade nesta plataforma.
        ROUTE_NOT_ALLOWED  mediram, e nenhuma rota viável sobrou.
        ALLOWED            há rota declarada, permitida e viável.

    Colapsar a primeira na segunda faria a casa dizer «não pode» onde a
    verdade é «ninguém sabe», e é assim que uma ausência de medição vira uma
    proibição que ninguém decidiu — ou, virando ao contrário, uma autorização
    que ninguém deu.

        NÃO DECLARADO NÃO É PROIBIDO, E MUITO MENOS É PERMITIDO.
    """
    plat, capac = (platform or '').upper(), (capability or '').upper()
    veredicto = {'PLATFORM': plat, 'CAPABILITY': capac, 'DECISAO': NAO_DECLARADA,
                 'ROTA': None, 'CLASSE': None, 'PERMITIDA': None, 'ESTADO': None,
                 'AUTH_MODE': None, 'PORQUE': None}
    rotas = (MATRIZ.get(plat) or {}).get(capac)
    if not rotas:
        veredicto['PORQUE'] = ('a matriz nao declara %s para %s. Ninguem mediu '
                               'esta porta.' % (capac, plat))
        return veredicto
    escolhida = _rota_padrao(rotas)
    if escolhida is None:
        veredicto['DECISAO'] = NAO_PERMITIDA
        veredicto['PORQUE'] = ('%s/%s tem %d rota(s) declarada(s) e nenhuma '
                               'viavel' % (plat, capac, len(rotas)))
        return veredicto
    veredicto.update({'DECISAO': PERMITIDA_SIM, 'ROTA': escolhida['ROTA'],
                      'CLASSE': escolhida['CLASSE'],
                      'PERMITIDA': escolhida['PERMITIDA'],
                      'ESTADO': escolhida['ESTADO'],
                      'AUTH_MODE': auth_mode(escolhida),
                      'PORQUE': escolhida['NOTA']})
    return veredicto


def _rota_padrao(rotas):
    """A rota DEFAULT: PERMITIDA primeiro, BARATA depois, PROVADA por último.

    A ordem importa e já esteve errada. A versão anterior ordenava só por preço,
    e com isso escolhia uma rota `CONDICIONAL` PROVADA na frente de uma rota `SIM`
    ainda sem credencial — medido em `YOUTUBE/FETCH_VIDEO_METADATA`, onde o
    `oembed` (que devolve só título, autor e thumbnail, e cujo uso automatizado
    está coberto pelo §3 dos Termos) ganhava do `videos.list` oficial.

        PERMITIDA -> BARATA -> CAPAZ. Nessa ordem.

    Uma rota que precisa de revisão não é a rota padrão de nada enquanto existir
    uma permitida ao lado: `CREDENTIAL_MISSING` é um estado que a casa conserta,
    e `CONDICIONAL` é uma dúvida que ela não conserta sozinha.
    """
    viaveis = [x for x in rotas if x['PERMITIDA'] in ('SIM', 'CONDICIONAL')
               and x['ESTADO'] not in ('ROUTE_NOT_ALLOWED',)]
    if not viaveis:
        return None
    return sorted(viaveis, key=lambda x: (x['PERMITIDA'] != 'SIM',
                                          x['PRIORIDADE'],
                                          x['ESTADO'] != 'PROVED'))[0]


def resumo():
    """Conta capacidades por estado, sem inventar denominador."""
    total = com_rota_livre = so_apify = sem_rota = 0
    for plat, caps in MATRIZ.items():
        for cap, rotas in caps.items():
            if cap.startswith('_'):
                continue
            total += 1
            d = _rota_padrao(rotas)
            if d is None:
                sem_rota += 1
            elif d['CLASSE'] == 'APIFY':
                so_apify += 1
            elif d['CLASSE'] in ('OFFICIAL_API_PAID',):
                pass
            else:
                com_rota_livre += 1
    return {'CAPACIDADES_DECLARADAS': total, 'COM_ROTA_NAO_APIFY': com_rota_livre,
            'DEFAULT_E_APIFY': so_apify, 'SEM_ROTA_PERMITIDA': sem_rota}


def imprimir(filtro=None):
    for plat, caps in MATRIZ.items():
        if filtro and plat != filtro.upper():
            continue
        print('\n' + '═' * 78)
        print(plat)
        if caps.get('_NOTA'):
            print('  · ' + caps['_NOTA'])
        print('═' * 78)
        for cap, rotas in caps.items():
            if cap.startswith('_'):
                continue
            d = _rota_padrao(rotas)
            print('\n  %s   →  DEFAULT: %s' % (cap, d['ROTA'] if d else 'NENHUMA ROTA PERMITIDA'))
            for x in rotas:
                marca = '►' if x is d else ' '
                print('    %s %-46s %-18s permitida=%-11s %s'
                      % (marca, x['ROTA'][:46], x['ESTADO'], x['PERMITIDA'], x['CUSTO']))
                if x['NOTA']:
                    for linha in _quebrar(x['NOTA'], 68):
                        print('        %s' % linha)
                if x['EVIDENCIA']:
                    print('        evidência: %s' % x['EVIDENCIA'])


def _quebrar(texto, larg):
    palavras, linha, saida = texto.split(), '', []
    for p in palavras:
        if len(linha) + len(p) + 1 > larg:
            saida.append(linha)
            linha = p
        else:
            linha = (linha + ' ' + p).strip()
    if linha:
        saida.append(linha)
    return saida


def gap_apify():
    """Onde a Apify continua sendo a rota padrão — e com que motivo canônico."""
    linhas = []
    for plat, caps in MATRIZ.items():
        for cap, rotas in caps.items():
            if cap.startswith('_'):
                continue
            d = _rota_padrao(rotas)
            tem_apify = any(x['CLASSE'] == 'APIFY' for x in rotas)
            if d and d['CLASSE'] == 'APIFY':
                motivo = ('ROUTE_NOT_ALLOWED' if plat == 'YOUTUBE'
                          else 'AUTHORIZATION_BLOCK' if plat == 'FACEBOOK'
                          else 'FREE_ROUTE_INSUFFICIENT_CAPABILITY')
                linhas.append((plat, cap, 'APIFY NECESSÁRIA', motivo))
            elif d is None:
                # Nem livre, nem paga, nem Apify: a capacidade não tem rota permitida.
                # Este é o caso do LinkedIn, e ele é uma RESPOSTA — não um buraco a
                # tapar com a primeira rota que funcionar.
                linhas.append((plat, cap, 'SEM ROTA PERMITIDA',
                               'nenhuma rota permitida, Apify inclusive'))
            elif tem_apify:
                linhas.append((plat, cap, 'APIFY DISPENSÁVEL', 'rota livre cobre: %s' % d['ROTA']))
    return linhas


def main():
    args = [a for a in sys.argv[1:]]
    if '--json' in args:
        print(json.dumps({'MEDIDO_EM': MEDIDO_EM, 'RESUMO': resumo(), 'MATRIZ': MATRIZ},
                         ensure_ascii=False, indent=1))
        return
    if '--gap' in args:
        print('\nAPIFY DEPENDENCY MATRIX  ·  medido em %s\n' % MEDIDO_EM)
        for plat, cap, veredito, motivo in gap_apify():
            print('  %-10s %-22s %-18s %s' % (plat, cap, veredito, motivo))
        print()
        return
    imprimir(args[0] if args else None)
    print('\n' + '═' * 78)
    for k, v in resumo().items():
        print('  %-26s %s' % (k, v))
    print('═' * 78)


if __name__ == '__main__':
    main()
