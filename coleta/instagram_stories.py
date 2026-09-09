#!/usr/bin/env python3
"""
STORY — a classe própria. Não é post, não é reel, não é highlight.

    STORY  conteúdo ATIVO de um perfil, que a plataforma apaga em ~24 h.

Este arquivo é o dono da capacidade `INSTAGRAM/FETCH_STORIES`: ele conhece o
contrato do ator, traduz a saída para o envelope social que já existe e — a
parte que mais importa — decide QUAL ESTADO cada perfil recebeu. Ele não abre
conexão, não guarda chave e não é um scraper novo: a porta paga continua sendo
`coletor.executar`, e o pool de chaves continua sendo `apify_pool`.

POR QUE STORY NÃO PODE SER `POST`
-----------------------------------
Se Story entrasse no envelope como `CONTENT_TYPE=POST`, a primeira consulta que
perguntasse "o que esta conta publicou?" somaria duas coisas com prazo de
validade diferente. Post continua lá amanhã; Story não. Uma delas precisa ser
recoletável e a outra é irrecuperável depois de 24 h — e é justamente a
irrecuperável que exige capturar o bruto AGORA.

    URL EXISTE HOJE != EVIDÊNCIA EXISTE AMANHÃ.

O ENUM QUE MENTIU, E POR ISSO ESTE ARQUIVO CHECA O TIPO
---------------------------------------------------------
O ator oficial `apify/instagram-scraper` publicou por muito tempo um
`resultsType` com o valor `stories`. Ele devolvia REELS. O valor foi depreciado
pelo próprio publisher com essa justificativa. Ou seja: durante meses, um run
verde, com itens, com custo cobrado, entregava a classe ERRADA de conteúdo — e
nada no run dizia isso.

    ENUM EXISTE != CAPACIDADE FUNCIONA.
    RUN VERDE != CLASSE CERTA.

Por isso `normalizar()` recusa item que não se prove Story, e a recusa é um
estado (`CONTRACT_DRIFT`), nunca um descarte silencioso. Um ator que comece a
devolver Reel amanhã é BARRADO na porta, não absorvido no acervo.

ZERO NÃO É AUSÊNCIA ATÉ QUE ALGUÉM PROVE QUE OLHOU
-----------------------------------------------------
`NO_ACTIVE_STORIES` é uma afirmação forte: diz que a conta foi olhada e não
tinha nada. Um ator que falhou também devolve zero linha. As duas coisas são
indistinguíveis no dataset e completamente diferentes no significado — uma é
medição, a outra é cegueira.

    ZERO LINHA DE ATOR QUE FALHOU NÃO É «NÃO POSTOU».

Então `classificar()` só concede `NO_ACTIVE_STORIES` quando a execução chegou a
estado terminal de sucesso E o perfil foi reconhecidamente processado. Fora
disso, `UNKNOWN_ERROR` ou `ACTOR_FAILED` — que custam uma investigação, e é o
preço certo a pagar por não inventar ausência.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(HERE)
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401
import social_envelope as env   # noqa: E402

# ══════════════════════════════════════════════════════════════════════════
# O ATOR ESCOLHIDO, E OS QUE FORAM RECUSADOS — COM O MOTIVO
# ══════════════════════════════════════════════════════════════════════════
# Medido em 2026-09-09 lendo a página viva de cada ator. Preço é o publicado;
# nenhum foi executado nesta missão, e por isso nada aqui é `PROVED`.
ATOR = 'datavoyantlab/advanced-instagram-stories-scraper'
ATOR_START_USD = 0.099            # taxa fixa por execução
ATOR_POR_USERNAME_USD = 0.003     # US$ 3,00 por 1.000 usernames

ATOR_FALLBACK = 'muhammetakkurtt/instagram-scraper'   # resultsType='stories'
FALLBACK_POR_ITEM_USD = 0.001     # US$ 1,00 por 1.000 itens salvos

# Recusados, e o motivo fica escrito para ninguém "redescobrir" daqui a três meses:
RECUSADOS = {
    'automation-lab/instagram-stories-scraper': (
        'exige `sessionCookie` — o cookie `sessionid` de uma conta real, tirado do '
        'DevTools. Entregar sessão humana a um ator de terceiro está fora desta '
        'arquitetura, e nenhuma vantagem de preço compra isso de volta.'),
    'apify/instagram-scraper': (
        '`resultsType=stories` devolvia REELS e foi depreciado pelo próprio publisher. '
        'É a prova histórica de que enum não é capacidade.'),
}

# Teto do lado da plataforma. Vale mesmo que este arquivo tenha um defeito.
TETO_USD_POR_RUN = 0.50

MAX_PERFIS_POR_RUN = 25   # trava NOSSA, não do ator: piloto não é vigilância

# ══════════════════════════════════════════════════════════════════════════
# ENTRADA
# ══════════════════════════════════════════════════════════════════════════


class EntradaInvalida(ValueError):
    """O pedido não serve. Recusado ANTES de acender execução paga."""


def entrada(usernames):
    """Monta a entrada do ator. Recusa antes de gastar, nunca depois."""
    if not usernames:
        raise EntradaInvalida('nenhum username: um run vazio custa a taxa de partida '
                              'de US$ %.3f e não traz nada' % ATOR_START_USD)
    limpos = []
    for u in usernames:
        u = str(u or '').strip().lstrip('@')
        if not u:
            raise EntradaInvalida('username vazio na lista')
        if '/' in u or ' ' in u:
            raise EntradaInvalida('username com forma de URL ou com espaço: %r. '
                                  'Este ator pede o handle, não o endereço.' % u)
        limpos.append(u)
    if len(limpos) > MAX_PERFIS_POR_RUN:
        raise EntradaInvalida('%d perfis num run; o teto desta casa é %d. '
                              'PILOTO NÃO É MONITORAMENTO EM MASSA.'
                              % (len(limpos), MAX_PERFIS_POR_RUN))
    return {'usernames': limpos}


def custo_estimado(n_usernames):
    """O que UM run com N perfis custa, pelo preço publicado do ator."""
    return round(ATOR_START_USD + n_usernames * ATOR_POR_USERNAME_USD, 6)


# ══════════════════════════════════════════════════════════════════════════
# A PORTA DE TIPO — onde o Reel morre
# ══════════════════════════════════════════════════════════════════════════
# Marcas que só existem em Reel/post do feed. Se QUALQUER uma aparece, o item
# não é Story, por mais verde que o run tenha ficado.
MARCAS_DE_REEL = ('product_type', 'is_reel', 'play_count', 'comment_count',
                  'like_count', 'caption_is_edited', 'shortcode')
PRODUTOS_QUE_NAO_SAO_STORY = ('clips', 'feed', 'igtv', 'carousel_container')


class NaoEStory(ValueError):
    """O ator devolveu item, e o item não é Story. Isto é CONTRACT_DRIFT."""


def _e_story(item):
    """Prova positiva de Story, não ausência de prova de Reel.

    Exigir a marca do Story (`expiring_at`) em vez de só recusar a marca do Reel
    é o que faz esta porta sobreviver a um formato novo: um Reel com campos
    renomeados passaria por uma lista de proibições, e não passa por uma
    exigência.
    """
    prod = str(item.get('product_type') or '').lower()
    if prod in PRODUTOS_QUE_NAO_SAO_STORY:
        raise NaoEStory('item com product_type=%r — isto é Reel/feed, não Story' % prod)
    for marca in MARCAS_DE_REEL:
        if marca in item and item.get(marca) not in (None, ''):
            raise NaoEStory('item traz `%s`, campo que Story não tem — o ator devolveu '
                            'outra classe de conteúdo' % marca)
    if item.get('is_highlight') or item.get('highlight_id') or item.get('highlightId'):
        raise NaoEStory('item é HIGHLIGHT, não Story ativo. Highlight é permanente; '
                        'Story expira. Não são a mesma evidência.')
    if not item.get('expiring_at') and not item.get('expiresAt'):
        raise NaoEStory('item sem `expiring_at` — sem prazo de expiração não há prova '
                        'de que isto seja conteúdo efêmero')
    return True


# ══════════════════════════════════════════════════════════════════════════
# NORMALIZAÇÃO
# ══════════════════════════════════════════════════════════════════════════
def _iso(ts):
    """Unix -> ISO 8601 UTC. Nada de adivinhar fuso."""
    if ts in (None, ''):
        return None
    import datetime
    try:
        return datetime.datetime.fromtimestamp(
            int(ts), datetime.timezone.utc).isoformat(timespec='seconds')
    except (TypeError, ValueError, OSError, OverflowError):
        return None


def _midia(item):
    """(MEDIA_TYPE, MEDIA_URL, dimensões). O tipo vem do ator, nunca da extensão."""
    tipo = 'VIDEO' if (item.get('video_versions') or item.get('media_type') == 2) else 'IMAGE'
    url = None
    if tipo == 'VIDEO':
        vs = item.get('video_versions') or []
        url = (vs[0] or {}).get('url') if vs else None
    if not url:
        cands = ((item.get('image_versions2') or {}).get('candidates') or [])
        url = (cands[0] or {}).get('url') if cands else None
    return tipo, url, (item.get('original_width'), item.get('original_height'))


def normalizar(item, *, username, run_id, country_scope, route, cost_usd=0.0,
               raw_reference=None):
    """Um item do ator -> um envelope social com CONTENT_TYPE=STORY.

    Levanta `NaoEStory` para qualquer coisa que não se prove Story. O chamador
    traduz isso em CONTRACT_DRIFT — nunca em descarte silencioso.
    """
    _e_story(item)
    nid = item.get('pk') or item.get('id') or item.get('storyId')
    if not nid:
        raise NaoEStory('item sem identidade nativa (`pk`/`id`): sem ID estável não há '
                        'dedupe possível, e sem dedupe a mesma Story vira duas')
    tipo, media_url, dims = _midia(item)
    publicado = _iso(item.get('taken_at'))
    expira = _iso(item.get('expiring_at')) or item.get('expiresAt')

    o = env.envelope(
        platform='INSTAGRAM',
        native_id=nid,
        url='https://www.instagram.com/stories/%s/%s/' % (username, nid),
        content_type='STORY',
        route=route,
        executor=ATOR,
        run_id=run_id,
        country_scope=country_scope,
        source_account=username,
        published_at=publicado,
        # A conta é italiana? Não sabemos, e o ator não diz. UNKNOWN é o dado.
        language=None,
        source_location=None,
        cost_usd=cost_usd,
        raw_reference=raw_reference,
        text=item.get('caption') if isinstance(item.get('caption'), str) else None,
        raw=item,
    )
    # ── O BLOCO EFÊMERO ────────────────────────────────────────────────────
    # `EXPIRES_AT` vem da plataforma ou não vem. Calcular `publicado + 24 h`
    # produziria um número com cara de fato e origem de chute; se um dia for
    # preciso calcular, o campo diz DERIVED e quem ler decide se aceita.
    o['EXPIRES_AT'] = expira or env.DESCONHECIDO
    o['EXPIRES_AT_SOURCE'] = 'PLATFORM' if expira else env.DESCONHECIDO
    o['MEDIA_TYPE'] = tipo
    o['MEDIA_URL'] = media_url or env.DESCONHECIDO
    o['MEDIA_DIMENSIONS'] = ('%sx%s' % dims) if all(dims) else env.DESCONHECIDO
    # A URL do CDN é assinada e morre em horas. Ela é PISTA para buscar o byte,
    # nunca a evidência em si.
    o['MEDIA_URL_DURABILITY'] = 'TEMPORARY_CDN_SIGNED_URL'
    # OBSERVED != COLLECTED. Hoje as duas coincidem porque o ator observa e
    # entrega no mesmo run; separadas agora, elas divergem sem quebrar contrato
    # no dia em que houver fila entre observar e baixar.
    o['OBSERVED_AT'] = o['COLLECTED_AT']
    # E os três que o SCRAP NÃO tem o direito de preencher.
    o['FACT_TIME'] = env.DESCONHECIDO
    o['FACT_LOCATION'] = env.DESCONHECIDO
    o['ACCOUNT_LOCATION'] = env.DESCONHECIDO
    o['DATA_CLASS'] = 'PERSONAL_DATA_POSSIBLE'
    o['LEGAL_INTERPRETATION_REQUIRED'] = True
    return o


# ══════════════════════════════════════════════════════════════════════════
# O ESTADO DE CADA PERFIL
# ══════════════════════════════════════════════════════════════════════════
def classificar(manifesto, itens, pedidos):
    """Um estado canônico POR PERFIL pedido. Zero nunca vira ausência sozinho.

    `manifesto` é o que `coletor.executar` devolveu sobre a execução inteira;
    `itens` é o dataset cru; `pedidos` são os usernames que mandamos.
    """
    status = (manifesto or {}).get('STATUS')
    msg = str((manifesto or {}).get('ERRO') or '')
    baixo = msg.lower()

    # A execução inteira falhou: NENHUM perfil foi medido. Dizer
    # `NO_ACTIVE_STORIES` aqui seria inventar 25 ausências de uma vez.
    if status != 'SUCCESS':
        if 'rate' in baixo or '429' in baixo:
            geral = 'RATE_LIMITED'
        elif 'login' in baixo or 'session' in baixo or 'auth' in baixo:
            geral = 'LOGIN_REQUIRED'
        elif 'maxtotalcharge' in baixo or 'budget' in baixo or 'charge limit' in baixo:
            geral = 'BUDGET_EXHAUSTED'
        elif status == 'FAILED':
            geral = 'ACTOR_FAILED'
        else:
            # PARTIAL inclui o caso medido de SUCCEEDED-com-zero-itens, que é
            # degradação disfarçada de sucesso. Não é ausência de Story.
            geral = 'UNKNOWN_ERROR'
        return {u: {'ESTADO': geral, 'STORIES': 0, 'PORQUE': msg[:200]} for u in pedidos}

    por_conta = {}
    for it in itens or []:
        u = (it.get('user') or {}).get('username') or it.get('username')
        if u:
            por_conta.setdefault(str(u).lower(), []).append(it)

    saida = {}
    for u in pedidos:
        chave = str(u).lower().lstrip('@')
        linhas = por_conta.get(chave, [])
        if linhas:
            privadas = [l for l in linhas if l.get('is_private') or l.get('private')]
            if privadas and not [l for l in linhas if not (l.get('is_private') or l.get('private'))]:
                saida[u] = {'ESTADO': 'PRIVATE_PROFILE', 'STORIES': 0,
                            'PORQUE': 'o ator alcançou a conta e ela é privada'}
            else:
                saida[u] = {'ESTADO': 'OK', 'STORIES': len(linhas), 'PORQUE': ''}
        else:
            # A execução foi bem e este perfil não trouxe linha. Só agora
            # `NO_ACTIVE_STORIES` é uma afirmação sustentada: houve run terminal
            # com sucesso, e outros perfis do mesmo run responderam.
            #
            # Se NENHUM perfil respondeu, a execução inteira é suspeita: um ator
            # que devolve zero para todo mundo não provou que olhou para alguém.
            if por_conta:
                saida[u] = {'ESTADO': 'NO_ACTIVE_STORIES', 'STORIES': 0,
                            'PORQUE': 'run terminal com sucesso; a conta não tem Story ativo'}
            else:
                saida[u] = {'ESTADO': 'UNKNOWN_ERROR', 'STORIES': 0,
                            'PORQUE': ('zero linha para TODOS os perfis do run — o ator não '
                                       'provou que processou nenhum. Ausência não medida '
                                       'não é ausência.')}
    return saida
