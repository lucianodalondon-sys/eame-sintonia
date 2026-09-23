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
    # O som de um video NAO e o video, e nao e a legenda. Nasceu com o C13:
    # `youtube.public_audio` foi provado ponta a ponta e precisava de uma porta
    # grossa propria. `FETCH_VIDEO_BYTES` implicaria video — e o video nunca foi
    # adquirido; `FETCH_TRANSCRIPT` e texto, e o que foi adquirido sao bytes de
    # som. O nome segue o paralelo ja existente.
    'FETCH_AUDIO_BYTES',
)


# ══════════════════════════════════════════════════════════════════════════
# OS EIXOS QUE A `PERMITIDA` NAO CONSEGUE SEPARAR
# ══════════════════════════════════════════════════════════════════════════
# `PERMITIDA` responde «esta porta esta aberta?». Historicamente responde as
# DUAS perguntas de uma vez: a plataforma permite? e a casa decidiu usar? Onde
# as duas coincidem ninguem nota. Onde divergem — o dono autoriza o que a
# plataforma proibe — um campo so obriga a escolher qual das duas apagar.
#
#     COLAPSAR OS DOIS EIXOS OBRIGA A APAGAR UM DELES.
#
# Por isso uma rota que precisa de os manter separados declara-os em campos
# proprios, e so entao `PERMITIDA` passa a significar a decisao do PROJETO.
#
#     AUSENTE = NAO DECLARADO. E NAO DECLARADO NAO AUTORIZA.
#
# As rotas ANTIGAS nao se migram: continuam a ler-se como sempre se leram, e a
# ambiguidade fica nomeada no seu lugar em vez de espalhada por uma migracao.
# Quem quiser a separacao, declara-a — e o validador exige-a inteira.
OWNER_AUTHORIZED = ('SIM', 'NAO')                    # decisao do PROJETO
PLATFORM_POLICY_STATUS = ('ALLOWED', 'DISALLOWED', 'NOT_MEASURED')  # evidencia da PLATAFORMA
LIMITES = ('PUBLIC_AUDIO_ONLY',
           # ── O LIMITE DA DESCOBERTA DE PERFIL PUBLICO (C14-C) ────────────
           # ⚠️ AMPLIAR ESTE VOCABULARIO E DECISAO DE DONO, E FOI-O.
           # `PUBLIC_AUDIO_ONLY` nasceu para o som do YouTube e descreve
           # BYTES DE MIDIA. `instagram.profile.discovery` nao adquire midia
           # nenhuma: localiza um perfil publico e transporta os metadados
           # estritamente necessarios a descoberta. Reutilizar o limite do
           # audio para isso faria o limite prometer o que nao trava.
           #
           #     UM LIMITE QUE NAO DESCREVE O QUE A ROTA FAZ NAO E UM LIMITE.
           #
           # O QUE ELE PERMITE: localizar/identificar o perfil publico e os
           # metadados publicos necessarios a descoberta.
           #
           # O QUE ELE NAO PERMITE, e a lista e fechada de proposito:
           #   conteudo publicado pelo perfil · midia · comentarios ·
           #   historico · perfil privado · autenticacao ou bypass.
           #
           # E NAO SE HERDA. Uma cadeia que peca internamente outra especie
           # nao ganha esta autorizacao por passar por aqui — a lei da C14-B
           # continua a valer, e o `LIMITE` e da ROTA, nao do pedido.
           'PUBLIC_PROFILE_DISCOVERY_ONLY',
           # ── O LIMITE DO VIDEO DE ORGANIZACAO NO LINKEDIN (D23) ──────────
           # ⚠️ AMPLIAR ESTE VOCABULARIO E DECISAO DE DONO, E ELE TOMOU-A.
           # O DONO REAL autorizou, por escrito, a aquisicao de VIDEO (e da
           # legenda que vem com ele) de paginas de ORGANIZACOES no LinkedIn,
           # assumindo o risco: `DECISOES-DONO-2026-09-23.md` -> D23.
           #
           #     OWNER_AUTHORIZED = SIM  +  PLATFORM_POLICY_STATUS = DISALLOWED
           #
           # Nenhum dos dois limites acima descreve isto, e reusar um deles
           # faria o limite prometer o que nao trava:
           #   · `PUBLIC_AUDIO_ONLY` descreve BYTES DE SOM publicos e nasceu
           #     para o YouTube; aqui o que se adquire e VIDEO e TEXTO.
           #   · `PUBLIC_PROFILE_DISCOVERY_ONLY` NAO adquire midia nenhuma.
           #
           # O QUE ELE PERMITE, e a lista e fechada:
           #   · descobrir as publicacoes que uma pagina de ORGANIZACAO serve
           #     publicamente, sem autenticacao;
           #   · os BYTES do video que essa publicacao serve (MP4 progressivo);
           #   · a FAIXA DE LEGENDA que a propria publicacao declara
           #     (`data-captions-url`), com a especie do texto preservada;
           #   · o texto que a organizacao escreveu na propria publicacao.
           #
           # O QUE ELE NAO PERMITE, e a lista e fechada de proposito:
           #   conteudo de PERFIL DE PESSOA · autenticacao, conta, cookie de
           #   sessao · contornar login wall, CAPTCHA ou bloqueio · texto de
           #   comentarios · lista de quem reagiu · rota paga · escrita,
           #   publicacao ou interacao de qualquer especie.
           #
           # E NAO SE HERDA: `fetch_post` (post publico fora de pagina de
           # organizacao, ou por busca) continua `ROUTE_NOT_ALLOWED`, e nada
           # nesta rota ganha aquela permissao por passar por aqui.
           #
           #     UM LIMITE QUE NAO DESCREVE O QUE A ROTA FAZ NAO E UM LIMITE.
           'PUBLIC_ORG_VIDEO_ONLY',
           # ── O LIMITE DO VIDEO DE PESSOA DO AGRO (D24) ───────────────────
           # ⚠️ AMPLIAR ESTE VOCABULARIO E DECISAO DE DONO, E ELE TOMOU-A.
           # O DONO REAL autorizou, POR ESCRITO, a aquisicao de VIDEO (e da
           # legenda/transcricao e dos metadados publicos do proprio post) de
           # PESSOAS do agro — pesquisador, doutor agronomo, perito agrario,
           # agrotecnico, creator, influencer — em qualquer plataforma desta
           # matriz, assumindo o risco: `DECISOES-DONO-2026-09-23.md` -> D24.
           #
           #     OWNER_AUTHORIZED = SIM  +  PLATFORM_POLICY_STATUS = DISALLOWED
           #
           # Nenhum dos limites acima descreve isto. `PUBLIC_ORG_VIDEO_ONLY`
           # fala de PAGINA DE ORGANIZACAO, e uma pessoa nao tem pagina de
           # organizacao; `PUBLIC_PROFILE_DISCOVERY_ONLY` nao adquire midia.
           #
           # O QUE ELE PERMITE, e a lista e fechada:
           #   · descobrir e ler publicacoes PUBLICAS de pessoa do agro que
           #     sejam servidas sem autenticacao;
           #   · os BYTES do video dessas publicacoes;
           #   · a FAIXA DE LEGENDA que a propria publicacao declara, com a
           #     especie do texto preservada (nunca como prova da fala original);
           #   · o texto que a propria pessoa escreveu na publicacao, e a
           #     identidade PUBLICA dela como PUBLICADOR.
           #
           # O QUE ELE NAO PERMITE, e a lista e fechada de proposito:
           #   CONTATOS · SEGUIDORES · MENSAGENS (DM) · COMENTARIOS DE
           #   TERCEIROS · lista de quem reagiu · perfil privado · conteudo de
           #   perfil que exija autenticacao · contornar login wall, CAPTCHA ou
           #   bloqueio · rota paga · pontuar, ranquear ou classificar a pessoa
           #   (`PERSONAL_SCORING`) · escrita, publicacao ou interacao.
           #
           # E O QUE ELE NAO REABRE, dito com o nome de quem decide:
           #   `NAMED_RESEARCHER_PUBLIC_SCREEN` continua BLOCKED_PENDING_LEGAL_REVIEW
           #   em `docs/regras/LIMITES-DE-DADO-PESSOAL-EAME.md`. Aquele bloqueio
           #   e de TELA — o produto nao lista pessoas nomeadas. Autorizar a
           #   AQUISICAO de um video publico nao autoriza nenhuma tela a listar
           #   quem o publicou, e as duas coisas vivem em donos diferentes.
           #
           #     AUTORIZAR A COLETA NAO VIRA CONFORMIDADE JURIDICA.
           #     O dono assumiu o risco da COLETA; a revisao juridica da ADAMA
           #     continua a ser quem decide a TELA.
           'PUBLIC_PERSON_VIDEO_ONLY')

#: Os tres campos, na ordem em que se leem. Uma rota declara-os TODOS ou nenhum.
EIXOS = ('OWNER_AUTHORIZED', 'PLATFORM_POLICY_STATUS', 'LIMITE')


class RotaInvalida(ValueError):
    """A rota nao respeita o vocabulario fechado dos eixos."""


def _declara_eixos(rota):
    return [k for k in EIXOS if k in rota]


def conferir_matriz():
    """Levanta `RotaInvalida` na primeira rota que nao respeite a lei.

    Corre no fim deste modulo: uma matriz invalida rebenta ao importar, nao no
    dia em que alguem colhe. E fail-closed onde importa — uma rota que a
    plataforma proibe e que ninguem autorizou nao fica disponivel por omissao.
    """
    for plat, caps in MATRIZ.items():
        if plat.startswith('_'):
            continue
        for cap, rotas in caps.items():
            if cap.startswith('_') or not isinstance(rotas, list):
                continue
            if cap not in CAPACIDADES:
                raise RotaInvalida(
                    '%s/%s: capacidade grossa fora do vocabulario fechado' % (plat, cap))
            for rota in rotas:
                eixos = _declara_eixos(rota)
                if not eixos:
                    continue
                if len(eixos) != len(EIXOS):
                    raise RotaInvalida(
                        '%s/%s/%s: declaracao PARCIAL dos eixos (%s). Ou se declaram '
                        'os tres, ou nenhum.' % (plat, cap, rota.get('ROTA'),
                                                 ', '.join(eixos)))
                if rota['OWNER_AUTHORIZED'] not in OWNER_AUTHORIZED:
                    raise RotaInvalida('%s/%s/%s: OWNER_AUTHORIZED %r fora do vocabulario'
                                       % (plat, cap, rota.get('ROTA'), rota['OWNER_AUTHORIZED']))
                if rota['PLATFORM_POLICY_STATUS'] not in PLATFORM_POLICY_STATUS:
                    raise RotaInvalida('%s/%s/%s: PLATFORM_POLICY_STATUS %r fora do vocabulario'
                                       % (plat, cap, rota.get('ROTA'), rota['PLATFORM_POLICY_STATUS']))
                if rota['LIMITE'] not in LIMITES:
                    raise RotaInvalida('%s/%s/%s: LIMITE %r fora do vocabulario'
                                       % (plat, cap, rota.get('ROTA'), rota['LIMITE']))
                if (rota['PLATFORM_POLICY_STATUS'] == 'DISALLOWED'
                        and rota['OWNER_AUTHORIZED'] != 'SIM'):
                    raise RotaInvalida(
                        '%s/%s/%s: a plataforma PROIBE e o dono nao autorizou. Uma '
                        'proibicao nao vira permissao por a rota existir.'
                        % (plat, cap, rota.get('ROTA')))
                if (rota['LIMITE'] == 'PUBLIC_AUDIO_ONLY'
                        and rota['CLASSE'] == 'LOCAL_SESSION'):
                    # `LOCAL_SESSION` e, por definicao desta matriz, «navegador
                    # local JA LOGADO». Alvo publico e sessao autenticada nao
                    # cabem no mesmo limite: aceitar os dois faria o limite
                    # prometer o que nao trava.
                    raise RotaInvalida(
                        '%s/%s/%s: LIMITE=PUBLIC_AUDIO_ONLY com CLASSE=LOCAL_SESSION. '
                        'Sessao autenticada nao cabe num limite de alvo publico.'
                        % (plat, cap, rota.get('ROTA')))
    return True


def r(nome, classe, permitida, estado, custo, nota, evidencia=None, *,
      owner_authorized=None, platform_policy=None, limite=None):
    """Uma rota candidata. `permitida` é SIM | NAO | CONDICIONAL.

    OS EIXOS SAO OPCIONAIS, E A AUSENCIA DELES E O QUE MANTEM AS ROTAS ANTIGAS
    INTACTAS. Sem eixos, esta funcao devolve exactamente o dicionario que
    devolvia antes — mesmas chaves, mesmos valores. Com eixos, a rota ganha tres
    campos a mais e `PERMITIDA` passa a significar a decisao do PROJETO, com a
    evidencia da PLATAFORMA preservada ao lado, sem se apagar.

        OWNER_AUTHORIZED = SIM  +  PLATFORM_POLICY_STATUS = DISALLOWED

    As duas frases convivem: o dono autoriza o risco do projeto, e a plataforma
    continua a proibir. O que a casa NAO pode e escrever uma sem a outra.
    """
    rota = {
        'ROTA': nome, 'CLASSE': classe, 'PRIORIDADE': CLASSES[classe],
        'PERMITIDA': permitida, 'ESTADO': estado, 'CUSTO': custo,
        'NOTA': nota, 'EVIDENCIA': evidencia, 'MEDIDO_EM': MEDIDO_EM,
    }
    if any(v is not None for v in (owner_authorized, platform_policy, limite)):
        rota.update({'OWNER_AUTHORIZED': owner_authorized,
                     'PLATFORM_POLICY_STATUS': platform_policy,
                     'LIMITE': limite})
    return rota


# ══════════════════════════════════════════════════════════════════════════
# A MATRIZ. Uma entrada por PLATAFORMA × CAPACIDADE, com a escada de rotas.
# ══════════════════════════════════════════════════════════════════════════
MATRIZ = {
    'YOUTUBE': {
        '_NOTA': ('As três rotas gratuitas foram MEDIDAS funcionando nesta máquina em '
                  '2026-09-08 e as três estão em caminho `Disallow` do robots.txt. '
                  'A única rota permitida é a Data API v3. '
                  '⚠️ D24 (2026-09-23): o dono autorizou por escrito o VÍDEO (e o áudio, a '
                  'legenda e os metadados públicos) de PESSOAS do agro — pesquisador, '
                  'agrônomo, creator, influencer. Aqui isso NÃO move nenhum estado, e vale '
                  'dizê-lo: o que barra as rotas do YouTube é CREDENCIAL e ROBOTS, não o '
                  'eixo da pessoa. Um canal pessoal nunca foi recusado por ser pessoal; o '
                  'que a D24 acrescenta é que ele também está AUTORIZADO — e o canal '
                  'pessoal passa a ter rota declarada, com o `yt-dlp:public_audio` a valer '
                  'para ele como vale para qualquer canal público.'),
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
        # ── O SOM DE UM VIDEO PUBLICO — ROTA PROPRIA, EIXOS PROPRIOS ────────
        # Nao entra por FETCH_VIDEO_BYTES (isso seria dizer que o VIDEO foi
        # adquirido) nem por FETCH_TRANSCRIPT (isso seria dizer que o que veio
        # foi TEXTO). O que foi medido foram BYTES DE SOM.
        #
        # E e a unica rota desta matriz que declara os tres eixos, porque e a
        # unica onde os dois ultimos divergem: o dono autorizou por escrito, e a
        # plataforma continua a proibir. `PERMITIDA = SIM` aqui significa a
        # decisao do PROJETO — e a evidencia da PLATAFORMA sobrevive inteira ao
        # lado, em vez de ser apagada.
        #
        #     OWNER_AUTHORIZED = SIM  +  PLATFORM_POLICY_STATUS = DISALLOWED
        'FETCH_AUDIO_BYTES': [
            r('yt-dlp:public_audio', 'LOCAL_EXECUTOR', 'SIM', 'PROVED', 'zero',
              'ROTA PROVADA em 2026-09-18 (C13), ponta a ponta: bytes de som de '
              'video PUBLICO, com SHA256, ffprobe (1 fluxo de som, 0 de imagem) e '
              'transcricao real. Executor: `ferramentas/youtube_transcrever.py` '
              '(`_audio`), que chama `yt-dlp -f bestaudio/best`; nenhum '
              'descarregador novo. FRONTEIRA: so alvo publico — sem conta, sem '
              'cookie de terceiro, sem CAPTCHA, sem token de sessao, sem contornar '
              'paywall ou acesso privado. NAO e rota de video (`youtube.media` '
              'continua BLOCKED) e NAO e rota de legenda (`FETCH_TRANSCRIPT` '
              'continua na rota paga). A plataforma proibe: Developer Policies '
              'III.E.1.a (download/cache de conteudo audiovisual), III.I.7 '
              '(separar os componentes de audio) e ToS §Permissions and '
              'Restrictions (acesso por meio automatizado) — preservados aqui '
              'porque apaga-los seria reescrever a evidencia.',
              'docs/sintonia-scrap/C13-YOUTUBE-PUBLIC-AUDIO.md',
              owner_authorized='SIM',
              platform_policy='DISALLOWED',
              limite='PUBLIC_AUDIO_ONLY'),
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
                  'Meta desenhado para isso. '
                  '⚠️ D24 (2026-09-23): o dono autorizou o VÍDEO de PESSOAS do agro nesta '
                  'família também. A busca por palavra-chave continua a ser a rota oficial '
                  'e o eixo da pessoa não a trava; nenhum estado muda por causa do D24.'),
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
                  'existe rota de HTTP direto permitida. Tudo passa por App Review. '
                  '⚠️ D24 (2026-09-23): o dono autorizou o VÍDEO de PESSOAS do agro '
                  'também aqui. O eixo da pessoa deixa de ser impedimento; o impedimento '
                  'que resta é o da PLATAFORMA (robots `Disallow: /` medido, e as rotas '
                  'oficiais atrás de App Review) — e por isso nenhuma rota desta '
                  'plataforma muda de estado por causa do D24.'),
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
                  'Esta missão NÃO reescreve nada disso; só declara onde a Apify sobra. '
                  '⚠️ D24 (2026-09-23): o dono autorizou TAMBÉM o VÍDEO de PESSOAS do agro '
                                    '— e a D22 já tinha autorizado os Reels por URL directa, substituindo a '
                                    'D19. A leitura ANTERIOR parava o Reel de pessoa ANTES da rede e '
                                    'colapsava os DOIS eixos num só: dizia «a plataforma proíbe» e escondia '
                                    'que o dono já tinha assumido esse risco — como o assumiu no áudio do '
                                    'YouTube (D17.4/C13) e no vídeo de organização do LinkedIn (D23). O eixo '
                                    'da PLATAFORMA continua MEDIDO e escrito ao lado de cada rota: o '
                                    '`robots.txt` vivo do `instagram.com` proíbe a coleta automatizada sem '
                                    'permissão escrita da plataforma. A autorização do dono é sobre o RISCO '
                                    'DO PROJETO; ela NÃO É a «express written permission» da plataforma, e '
                                    'nenhuma das duas se troca pela outra. '
                                    'O QUE CONTINUA FECHADO, e não por efeito lateral: o PERFIL '
                                    '(999/authwall medido, e o muro de login da grade por HTTP), login, '
                                    'conta, cookie de sessão, contornar login wall/CAPTCHA/bloqueio, '
                                    'CONTATOS, SEGUIDORES, MENSAGENS (DM), COMENTÁRIOS DE TERCEIROS, rota '
                                    'paga, `PERSONAL_SCORING` e a TELA de pessoas nomeadas '
                                    '(`NAMED_RESEARCHER_PUBLIC_SCREEN` — dono: revisão jurídica). '
                                    'PONTEIRO: `docs/sintonia-scrap/D24-VIDEO-DE-PESSOA.md` §6.'),
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
            # ── DECISÃO DO DONO, C14-C · 2026-09-19 ──────────────────────────
            # Esta rota era a ÚNICA capacidade remota do Instagram que chegava
            # a `DECISAO = ALLOWED` sem declarar os três eixos. Medido: um
            # `COLLECT(instagram.profile.discovery)` lançava o navegador num
            # SUBPROCESSO — e um bloqueio de socket no processo-pai não o
            # alcança. O portão existia (`adaptador_instagram.politica()`) e
            # barrava as outras três capacidades; esta passava ao lado dele.
            #
            #     `PERMITIDA = CONDICIONAL` DESCREVE UMA CONDIÇÃO DO AMBIENTE.
            #     TRADUZI-LA COMO `ALLOWED` TRANSFORMA UMA LIMITAÇÃO TÉCNICA
            #     NUMA AUTORIZAÇÃO DE NEGÓCIO.
            #
            # Os três eixos, e cada um tem um dono diferente:
            #
            #   OWNER_AUTHORIZED = SIM        — decisão do dono do projeto,
            #     ESTRITA: descobrir perfis PUBLICAMENTE VISÍVEIS, limitada à
            #     identificação/localização e aos metadados públicos
            #     necessários à descoberta. NÃO autoriza perfil privado,
            #     login, bypass, posts, mídia, reels, stories, comentários,
            #     histórico, mensagens, nem capacidades vizinhas.
            #
            #   PLATFORM_POLICY_STATUS = NOT_MEASURED — e fica assim. O
            #     `robots.txt` vivo do `instagram.com` já foi medido para
            #     FETCH_TRANSCRIPT (C10.5D), mas ninguém o mediu para ESTA
            #     rota. Escrever `ALLOWED` por analogia seria fabricar prova.
            #
            #   LIMITE = PUBLIC_PROFILE_DISCOVERY_ONLY — o limite novo, que
            #     descreve o que esta rota faz e nada além.
            #
            # O RESULTADO É FAIL-CLOSED, E ISSO É O PONTO: autorização interna
            # existe, limite está escrito, e a rede continua fechada porque a
            # política da plataforma ainda não foi provada.
            #
            #     AUTORIZAR NÃO É MEDIR. E SEM MEDIR, NÃO SAI.
            r('instagram_janela.py:grade', 'PUBLIC_BROWSER', 'CONDICIONAL', 'PROVED', 'zero',
              'já medido: os 12 itens mais recentes, legenda inteira, data exata, curtidas; '
              'em reel, visualizações e duração', 'scripts/instagram_janela.py',
              owner_authorized='SIM', platform_policy='NOT_MEASURED',
              limite='PUBLIC_PROFILE_DISCOVERY_ONLY'),
        ],
        'FETCH_TRANSCRIPT': [
                    # ── C10.5D (2026-09-11) mandou PARAR; D22/D24 (2026-09-23) mandaram
                    #    ANDAR — e o que separa as duas não é a capacidade, é o EIXO.
                    #
                    # A C10.5D leu o `robots.txt` VIVO de `instagram.com` — 6.256 bytes, o
                    # bloco `User-agent: *` / `Disallow: /` — e escreveu `NAO`. Isso estava
                    # certo enquanto a casa lia UM eixo só: dizia «a plataforma proíbe» e
                    # deixava por dizer quem tinha assumido o risco.
                    #
                    #     UMA LEITURA DE UM EIXO SÓ NÃO É UMA DECISÃO: É METADE DELA.
                    #
                    # A D22 (dono real) autorizou os Reels por URL directa, substituindo a
                    # D19; a D24 (o mesmo dono, por escrito) autorizou o VÍDEO de PESSOAS do
                    # agro. As duas trazem a mesma forma que a casa já usava no áudio do
                    # YouTube (D17.4/C13) e no vídeo de organização do LinkedIn (D23):
                    #
                    #     OWNER_AUTHORIZED = SIM  +  PLATFORM_POLICY_STATUS = DISALLOWED
                    #
                    # A plataforma continua a PROIBIR — isso está medido, e fica escrito ao
                    # lado em vez de apagado. Quem mudou foi o dono do risco.
                    #
                    # O QUE ESTA ABERTURA **NÃO** ABRE, e cada linha disto tem prova:
                    #   · PERFIL — 999/`authwall` medido; e a grade por HTTP devolve o muro
                    #     de login. Não se contorna;
                    #   · login, conta, cookie de sessão, CAPTCHA, bloqueio — nada disso;
                    #   · CONTATOS · SEGUIDORES · MENSAGENS (DM) · COMENTÁRIOS DE TERCEIROS;
                    #   · rota paga (D17.1) e `PERSONAL_SCORING`;
                    #   · a TELA de pessoas nomeadas — `NAMED_RESEARCHER_PUBLIC_SCREEN`
                    #     continua com a revisão jurídica, que é outro dono.
                    #
                    #     AUTORIZAR A COLETA NÃO VIRA CONFORMIDADE JURÍDICA.
                    #
                    # E O LIMITE NOMEIA O ALVO QUE FOI MEDIDO: `PUBLIC_PERSON_VIDEO_ONLY`.
                    # Um Reel de ORGANIZAÇÃO no Instagram não é este limite — a D22 fala
                    # deles, e quem os abrir declara o limite próprio. O vocabulário é
                    # fechado e cresce declarado, nunca por analogia.
                    r('instagram_transcrever.py:faster-whisper', 'LOCAL_EXECUTOR', 'SIM',
                      'PROVED',
                      'zero dólar, ~6 h/1.000 vídeos no modelo small',
                      'A ROTA SAI PARA A PLATAFORMA: baixa a mídia pública do Reel por URL '
                      'directa e só depois reconhece a fala. '
                      'MEDIDO em 2026-09-23, egresso IT (AS212238 · Palermo) nas DUAS pontas '
                      'da corrida, sem conta, sem login, sem cookie e sem contornar muro: um '
                      'Reel PÚBLICO de uma PESSOA do agro italiano (@dr.agricultura — '
                      'Alessandro Giglietti, dottore agronomo) foi adquirido por URL directa '
                      'em AQUISIÇÃO SÓ DE ÁUDIO — `MEDIA_STATE = MEDIA_OK`, '
                      '`AUDIO_ONLY_ACQUISITION = PROVEN`, 696 245 bytes, sha256 `ea372eeb…`, '
                      'e DUAS corridas independentes devolveram o MESMO sha256. A '
                      '`CAPTION_TEXT` (731 caracteres) viaja marcada como legenda, nunca como '
                      'fala. O alvo foi descoberto pela JANELA PÚBLICA da própria casa (grade '
                      'do perfil, deslogada) — nenhum buscador. '
                      'A PLATAFORMA PROÍBE (o `robots.txt` vivo responde `Disallow: /`); o '
                      'dono autorizou por escrito (D22/D24), e as duas frases andam juntas. '
                      'A página de PERFIL continua FECHADA (999/`authwall`, medido) e não se '
                      'contorna.',
                      'docs/sintonia-scrap/D24-VIDEO-DE-PESSOA.md',
                      owner_authorized='SIM', platform_policy='DISALLOWED',
                      limite='PUBLIC_PERSON_VIDEO_ONLY'),
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
                  'nenhum acesso automatizado ao linkedin.com — COM UMA EXCEÇÃO DECLARADA. '
                  '⚠️ D23 (2026-09-23): o DONO REAL autorizou, por escrito e com o risco '
                  'assumido, a aquisição de VÍDEO e da legenda que vem com ele em páginas '
                  'de ORGANIZAÇÕES. Essa autorização vive nas três rotas com eixos '
                  '(`DISCOVER_POST`, `FETCH_VIDEO_BYTES`, `FETCH_TRANSCRIPT`), e ela NÃO '
                  'se espalha: as rotas de `FETCH_POST` continuam `ROUTE_NOT_ALLOWED`, e '
                  'perfis de PESSOAS continuam fora. A plataforma continua a PROIBIR — '
                  'isso está medido e escrito em cada rota; quem mudou foi o dono do '
                  'risco, e não a lei da plataforma. '
                  '⚠️ D24 (2026-09-23): o MESMO dono autorizou, também por escrito, o '
                  'VÍDEO de PESSOAS do agro (pesquisador, agrônomo, creator, influencer). '
                  'Isso SUBSTITUI a frase «perfis de PESSOAS fora» da D23 — e só para '
                  'vídeo/legenda/metadados públicos do próprio post. O que a medição '
                  'mostrou, e que fica escrito: a PÁGINA DE PERFIL (`/in/<slug>/`) responde '
                  '999 com `authwall`, com a nossa UA E com UA de navegador (medido, '
                  'egresso IT/datacenter) — essa porta continua FECHADA e NÃO se contorna; '
                  'a PÁGINA DO POST público de uma pessoa responde 200 a convidado (medido '
                  'em agrônomos italianos), e é por ali que o vídeo pode ser lido. '
                  'O QUE A D24 NÃO REABRE: contatos, seguidores, mensagens, comentários de '
                  'terceiros, `PERSONAL_SCORING` e o `NAMED_RESEARCHER_PUBLIC_SCREEN` '
                  '(este é de TELA, e o dono dele é a revisão jurídica).'),
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
            r('linkedin:perfil-publico-de-pessoa', 'DIRECT_HTTP', 'NAO', 'BLOCKED',
              'zero',
              'MEDIDO 2026-09-23, e é o resultado que o D24 manda registar em vez de '
              'contornar: `https://www.linkedin.com/in/<slug>/` responde HTTP 999 com '
              '`authwall` no corpo — com a UA desta casa E com UA de navegador (Chrome), '
              'egresso IT/datacenter, sem cookie e sem conta. Os três perfis italianos '
              'testados deram o mesmo: 999, 1 530 bytes, sem um único `urn:li:activity`. '
              'A MESMA UA, no mesmo egresso e no mesmo minuto, recebeu 200 na página de '
              'ORGANIZAÇÃO — logo a recusa é da ROTA, e não do nosso robô. '
              'NÃO SE CONTOURA: nem login wall, nem CAPTCHA, nem bloqueio. '
              'A autorização do dono (D24) existe, e não muda o que a plataforma serve.',
              'docs/sintonia-scrap/D24-VIDEO-DE-PESSOA.md',
              owner_authorized='SIM', platform_policy='DISALLOWED',
              limite='PUBLIC_PERSON_VIDEO_ONLY'),
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
        # ═══════════════════════════════════════════════════════════════════
        # D23 · A PÁGINA PÚBLICA DE ORGANIZAÇÃO — a porta que o dono abriu
        # ═══════════════════════════════════════════════════════════════════
        # MEDIDO em 2026-09-23, desta máquina, egresso IT/datacenter
        # (AS212238, Palermo), sem conta, sem cookie, sem login, sem navegador
        # e sem rota paga:
        #
        #     /company/<slug>/                        200 · 10 a 18 activity ids
        #     <video data-sources="…">                 MP4 progressivo declarado
        #     MP4 em dms.licdn.com                     206 · video/mp4 · 7,4 MB
        #     data-captions-url                        200 · WebVTT e SRT reais
        #
        # E A POLÍTICA DA PLATAFORMA FOI MEDIDA, NÃO SE ESCONDE:
        #
        #     PLATFORM_POLICY_STATUS = DISALLOWED
        #     (o robots.txt do LinkedIn abre com «The use of robots or other
        #      automated means to access LinkedIn without the express
        #      permission of LinkedIn is strictly prohibited.»)
        #
        # O que mudou NÃO foi a política da plataforma — foi o DONO. Ele
        # autorizou, por escrito, com o risco assumido: D23,
        # `DECISOES-DONO-2026-09-23.md`. É o mesmo desenho do
        # `yt-dlp:public_audio` (C13/D17.4), e pela mesma razão:
        #
        #     AUTORIZAR NÃO É MEDIR. E AS DUAS COISAS FICAM ESCRITAS.
        #
        # Uma leitura apressada diria «o LinkedIn proíbe, então não se faz».
        # A leitura certa é a que a casa já escreveu nos eixos: a plataforma
        # proíbe, o dono assumiu o risco, e o dado viaja com as duas frases.
        'DISCOVER_POST': [
            r('linkedin:pagina-publica-da-organizacao', 'DIRECT_HTTP', 'SIM',
              'PROVED', 'zero',
              'MEDIDO 2026-09-23: a landing pública da organização responde 200 a '
              'convidado e serve os cartões das publicações recentes, com o '
              'activity id, o endereço canónico do post, o texto do autor e — '
              'quando existe — o `<video data-sources>` com o MP4 e a legenda. '
              'MEDIDO em 18 páginas de organizações italianas: 10 a 18 activity '
              'ids cada, 9 delas com pelo menos um vídeo. O teto conhecido é a '
              'PROFUNDIDADE: a página não expõe endereço de página seguinte. '
              'PLATAFORMA PROÍBE (DISALLOWED); dono autorizou (D23).',
              'docs/sintonia-scrap/D23-LINKEDIN-ORG-VIDEO.md',
              owner_authorized='SIM', platform_policy='DISALLOWED',
              limite='PUBLIC_ORG_VIDEO_ONLY'),
            r('linkedin:post-publico-de-pessoa', 'DIRECT_HTTP', 'SIM', 'PROVED',
              'zero',
              'MEDIDO 2026-09-23: a PÁGINA DO POST de uma pessoa responde 200 a '
              'convidado, e é a porta que resta quando a página de perfil está fechada. '
              'Quatro posts de agrônomos italianos medidos um a um: 200 · 93 752 a '
              '115 946 bytes · título e texto servidos em italiano (ex.: «Si è appena '
              'concluso il corso di formazione sulla potatura e sulla gestione '
              'dell\'olivo»). A D24 autoriza este alvo; e a descoberta NÃO usa buscador: os endereços saem do acervo '
              'que a casa já tem, e a regra da D23 vale inteira — a URL vem de '
              'propriedade ou de acervo próprio, nunca de serviço que revende LinkedIn. '
              'A página de PERFIL continua 999 (rota declarada ao lado, `BLOCKED`).',
              'docs/sintonia-scrap/D24-VIDEO-DE-PESSOA.md',
              owner_authorized='SIM', platform_policy='DISALLOWED',
              limite='PUBLIC_PERSON_VIDEO_ONLY'),
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
              'RISCO REGISTADO, NÃO ENDOSSADO: esta casa JÁ gastou US$ 0,484 em 120 perfis '
              'por esta rota. O §8.2 alcança explicitamente dado obtido "through third '
              'parties (such as data aggregators or brokers)" — o intermediário não muda a '
              'cláusula. A missão manda NÃO remover Apify agora; então fica declarado como '
              'dependência legada com risco jurídico aberto, para decisão humana.',
              'https://www.linkedin.com/legal/user-agreement'),
        ],
        'FETCH_VIDEO_BYTES': [
            r('linkedin:data-sources-mp4', 'DIRECT_HTTP', 'SIM', 'PROVED', 'zero',
              'MEDIDO 2026-09-23: a página pública da publicação declara o endereço '
              'progressivo no atributo `data-sources` da etiqueta `<video>`, e o CDN '
              '`dms.licdn.com` serve os bytes a convidado — HTTP 206, `video/mp4`, '
              '7 464 653 e 14 687 975 bytes medidos em dois vídeos. O endereço traz '
              '`e=2147483647`, e isso é `LONG_LIVED_OBSERVED` — uma observação, não '
              'uma garantia documental. É MP4 PROGRESSIVO: nem HLS, nem DASH, logo '
              'não há manifesto nem segmentos a remontar. PLATAFORMA PROÍBE '
              '(DISALLOWED); dono autorizou (D23).',
              'docs/sintonia-scrap/D23-LINKEDIN-ORG-VIDEO.md',
              owner_authorized='SIM', platform_policy='DISALLOWED',
              limite='PUBLIC_ORG_VIDEO_ONLY'),
            r('linkedin:data-sources-mp4-de-pessoa', 'DIRECT_HTTP', 'SIM',
              'PROVED', 'zero',
              'A D24 autoriza este alvo. A MESMA técnica da D23, aplicada à página '
              'pública do post de uma pessoa — e MEDIDA: o canário de 2026-09-23 '
              'adquiriu, de um post público de pessoa, MP4 de 6 935 096 bytes '
              '(`video/mp4`, sha `bff909e5…`) e legenda WebVTT de 1 371 bytes '
              '(sha `09712870…`), US$ 0, sem conta e sem cookie. '
              'E O CAMINHO ATÉ LÁ FICA ESCRITO, porque ele é o resultado: numa amostra '
              'de 15 posts públicos de PESSOA, TODOS responderam 200 e apenas UM trazia '
              'vídeo — e nenhum dos quatro posts de agrônomo ITALIANO medidos trazia. '
              'Vídeo em post de pessoa é MINORIA, e um vídeo não encontrado é '
              'resultado, não permissão inventada.',
              'docs/sintonia-scrap/D24-VIDEO-DE-PESSOA.md',
              owner_authorized='SIM', platform_policy='DISALLOWED',
              limite='PUBLIC_PERSON_VIDEO_ONLY'),
        ],
        'FETCH_TRANSCRIPT': [
            r('linkedin:data-captions-url', 'DIRECT_HTTP', 'SIM', 'PROVED', 'zero',
              'MEDIDO 2026-09-23: quando o vídeo tem faixa automática, a MESMA '
              'etiqueta `<video>` declara o endereço dela em `data-captions-url`. '
              'O endereço diz o formato em claro — `video-auto-caption-srt-…` ou '
              '`video-auto-caption-webvtt-…` — e os bytes confirmam: 4 legenda(s) '
              'obtidas, `text/vtt` e `text/plain`, 529 a 3 587 bytes, texto italiano '
              'e inglês legível. É legenda AUTOMÁTICA: ASR de outra casa, mais '
              'barata e não melhor — e por isso viaja com a espécie declarada, '
              'nunca como se fosse prova da fala original. NÃO EXISTE EM TODO VÍDEO: '
              'medido, 2 dos 5 vídeos de uma organização e nenhum dos 2 de outra. '
              'Ausência de legenda é resultado, e não falha. PLATAFORMA PROÍBE '
              '(DISALLOWED); dono autorizou (D23).',
              'docs/sintonia-scrap/D23-LINKEDIN-ORG-VIDEO.md',
              owner_authorized='SIM', platform_policy='DISALLOWED',
              limite='PUBLIC_ORG_VIDEO_ONLY'),
            r('linkedin:data-captions-url-de-pessoa', 'DIRECT_HTTP', 'SIM',
              'PROVED', 'zero',
              'A D24 autoriza este alvo, e vale o mesmo: a etiqueta declara '
              '`data-captions-url` quando o vídeo tem faixa automática, e a espécie do '
              'texto viaja declarada (ASR do provedor, nunca a fala original). '
              'MEDIDA no mesmo canário: 1 371 bytes, `text/vtt`, WebVTT real, com o '
              'formato declarado no endereço a bater com os BYTES. E a legenda do post '
              'de pessoa reproduz o que a D23 já tinha medido na organização: a '
              'plataforma DECLARA uma língua no `data-language` e serve o texto '
              'noutra — o campo guarda o que ela declarou, e a nota da divergência '
              'viaja no objeto.',
              'docs/sintonia-scrap/D24-VIDEO-DE-PESSOA.md',
              owner_authorized='SIM', platform_policy='DISALLOWED',
              limite='PUBLIC_PERSON_VIDEO_ONLY'),
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
                  'interesse comercial. A ADAMA não é elegível. Sobra o oEmbed. '
                  '⚠️ D24 (2026-09-23): o dono autorizou o VÍDEO de PESSOAS do agro também '
                  'aqui. O eixo da pessoa deixa de ser impedimento; o que resta é a '
                  'PLATAFORMA, que nomeia agentes automatizados num bloco `Disallow: /` — '
                  'e por isso nenhuma rota desta plataforma muda de estado por causa do '
                  'D24.'),
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
    # OS EIXOS SO APARECEM QUANDO A ROTA OS DECLARA. Sem eles, este dicionario
    # e exactamente o que era antes — e e isso que prova que nenhuma decisao
    # antiga mudou de forma nem de valor.
    #
    #     AUSENTE = NAO DECLARADO, e quem le sabe que nao foi declarado.
    veredicto.update({k: escolhida[k] for k in EIXOS if k in escolhida})
    return veredicto


def actor_proibido(plataforma, actor):
    """Esta matriz NOMEIA este ator, e só em rotas proibidas? → (bool, porquê).

    ⚠️ NASCEU DE UM CAMINHO LATERAL MEDIDO NA LINKEDIN-OP-01 e fechado na
    SCRAP-RC-01. `regras/sensor_coleta.py` configura quatro atores HarvestAPI do
    LinkedIn e chama a porta paga DIRETAMENTE, sem passar pelo roteador. Ele
    ficava parado pela autorização de gasto — e isso não chega:

        SPEND_AUTHORIZATION != ROUTE_POLICY.

    Uma autorização financeira futura não pode transformar uma rota proibida
    numa rota permitida. A pergunta «esta rota é permitida?» tem dono, e o dono
    é este ficheiro; o que faltava era alguém fazer-lhe a pergunta antes do POST.

    A POLARIDADE IMPORTA, E É FAIL-CLOSED SÓ SOBRE O QUE ESTÁ NOMEADO
    -----------------------------------------------------------------
    Responde `True` quando a matriz nomeia o ator numa rota `PERMITIDA = NAO` e
    **não** o nomeia em nenhuma permitida. Um ator que a matriz não nomeia não é
    proibido por omissão: seria recusar por ausência de declaração, e a maior
    parte dos atores desta casa é nomeada pela CAPACIDADE, não pelo id — o
    `apify:transcricao` do YouTube é exactamente isso.

        DECLARADO PROIBIDO != NÃO DECLARADO.
        O SILÊNCIO DA MATRIZ NÃO PROÍBE, E TAMBÉM NÃO AUTORIZA.

    O nome da rota pode trazer glob (`apify:harvestapi~linkedin-*`), porque é
    assim que a matriz já escreve uma família de atores numa linha só.
    """
    import fnmatch
    alvo = str(actor or '').strip()
    if not alvo:
        return False, ''
    caps = MATRIZ.get(str(plataforma or '').upper()) or {}
    proibidas, permitidas = [], []
    for capac, rotas in caps.items():
        if capac.startswith('_') or not isinstance(rotas, list):
            continue
        for r in rotas:
            nome = str(r.get('ROTA') or '')
            padrao = nome.split(':', 1)[1] if ':' in nome else nome
            if not (fnmatch.fnmatch(alvo, padrao) or alvo == padrao):
                continue
            (permitidas if r.get('PERMITIDA') in ('SIM', 'CONDICIONAL')
             else proibidas).append((capac, nome, r.get('NOTA') or ''))
    if proibidas and not permitidas:
        capac, nome, nota = proibidas[0]
        return True, ('%s/%s declara a rota «%s» como PERMITIDA = NAO%s'
                      % (plataforma, capac, nome,
                         (' — ' + nota[:160]) if nota else ''))
    return False, ''


def _autorizada_pelo_projeto(rota):
    """Rota que declara os eixos so e viavel com decisao explicita do projeto.

    FAIL-CLOSED, e o silencio nao autoriza:

        OWNER_AUTHORIZED ausente  ->  rota indisponivel, nao permissao implicita

    Rota ANTIGA (sem eixos nenhuns) continua exactamente como era: esta funcao
    responde `True` e nada muda no caminho que ja corria.

    ⚠️ E NAO BASTA O DONO AUTORIZAR — A POLITICA TEM DE TER SIDO MEDIDA.
    Esta funcao lia SO `OWNER_AUTHORIZED`, e isso bastava enquanto a unica
    rota com eixos era `yt-dlp:public_audio`, cuja `PLATFORM_POLICY_STATUS`
    JA estava medida (`DISALLOWED`) e cujo dono assumiu esse risco com todas
    as letras. `NOT_MEASURED` e um terceiro estado, e nao se le como os
    outros dois:

        DISALLOWED   = mediu-se, e a plataforma proibe.   O dono pode assumir.
        ALLOWED      = mediu-se, e a plataforma permite.
        NOT_MEASURED = NINGUEM MEDIU. Nao ha risco assumido — ha risco por
                       conhecer, e nao se assume o que nao se conhece.

            AUTORIZAR NAO E MEDIR. E SEM MEDIR, NAO SAI.

    Por isso `NOT_MEASURED` fecha a porta mesmo com o dono a dizer SIM. A
    autorizacao interna fica escrita e viva — no dia em que alguem medir a
    politica, muda-se UM campo e a rota abre sem se tocar em autorizacao
    nenhuma. O contrario — abrir agora e medir depois — e coletar primeiro e
    perguntar a seguir.
    """
    if not _declara_eixos(rota):
        return True
    if rota.get('OWNER_AUTHORIZED') != 'SIM':
        return False
    return rota.get('PLATFORM_POLICY_STATUS') != 'NOT_MEASURED'


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

    E uma rota que declara os eixos só entra se o DONO a autorizou — a plataforma
    proibir nao a tira daqui, mas o dono nao autorizar tira.
    """
    viaveis = [x for x in rotas if x['PERMITIDA'] in ('SIM', 'CONDICIONAL')
               and x['ESTADO'] not in ('ROUTE_NOT_ALLOWED',)
               and _autorizada_pelo_projeto(x)]
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


# ── A LEI CONFERE-SE AO IMPORTAR ────────────────────────────────────────────
# Uma matriz invalida rebenta aqui, e nao no dia em que alguem colhe. E onde a
# rota nova depende da declaracao, a ausencia dela FALHA FECHADO.
conferir_matriz()


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
