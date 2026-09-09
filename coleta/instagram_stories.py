#!/usr/bin/env python3
"""
STORY — a classe própria. Não é post, não é reel, não é highlight.

    ESTE ARQUIVO NÃO ADQUIRE NADA. Ele diz o que É Story e o que não é.
    Quem vai buscar é `coleta/story_local.py`, pela sessão local desta casa.

Em 2026-09-09 a Apify saiu de Stories por decisão do dono do projeto, e o que
sobreviveu daquele trabalho foi justamente o que não era da Apify: a porta de
tipo e a porta do zero. Elas valem para QUALQUER rota — foi um ator pago que
serviu Reel chamando de Story, e nada impede que uma rota gratuita erre igual.

    ONE STORY CAPABILITY -> ONE CANONICAL ACQUISITION OWNER.

    STORY  conteúdo ATIVO de um perfil, que a plataforma apaga em ~24 h.

Este arquivo traduz a saída de QUALQUER rota para o envelope social que já
existe e — a parte que mais importa — decide QUAL ESTADO cada perfil recebeu.
Ele não abre conexão, não guarda chave e não conhece plataforma nenhuma por
dentro.

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
# A PORTA DE TIPO — onde o Reel morre
# ══════════════════════════════════════════════════════════════════════════
# Marcas que só existem em Reel/post do feed. Se QUALQUER uma aparece, o item
# não é Story, por mais verde que o run tenha ficado.
# ══════════════════════════════════════════════════════════════════════════
# A PORTA DE TIPO — e a medição que a consertou antes do primeiro dólar
# ══════════════════════════════════════════════════════════════════════════
# Remedindo a saída REAL do ator em 2026-09-09, antes do piloto vivo, o registro
# de Story mostrou-se muito mais parecido com um post do que a versão anterior
# desta porta supunha. Um Story de verdade TRAZ:
#
#     product_type          e o valor é 'story'
#     caption_is_edited     presente, normalmente false
#     code                  o análogo do shortcode
#     is_reel_media         presente, e normalmente TRUE
#
# A porta anterior recusava item que trouxesse `product_type`, `caption_is_edited`
# ou `shortcode`. Ou seja: ela teria recusado CEM POR CENTO dos Stories reais, e
# o piloto teria reportado CONTRACT_DRIFT em tudo — que se leria como «o ator
# mudou», quando quem estava errado era a porta.
#
#     UMA TRAVA CALIBRADA EM CIMA DE FIXTURE INVENTADA MEDE A FIXTURE.
#
# E há uma armadilha de nome que precisa ficar escrita, porque ela vai enganar
# alguém de novo: no vocabulário interno do Instagram, `is_reel_media` NÃO quer
# dizer Reel. Quer dizer «mídia da bandeja de Stories». Um Story tem
# `is_reel_media=true`. Tratar esse campo como prova de Reel inverteria a porta.
#
#     `is_reel_media` É STORY. `product_type='clips'` É REEL.
#
# Por isso a porta passou a ser POSITIVA em cima do campo certo: `product_type`
# tem de VALER 'story'. Ausência de marca de Reel nunca foi prova de Story.
PRODUTO_DE_STORY = ('story',)
PRODUTOS_QUE_NAO_SAO_STORY = ('clips', 'feed', 'igtv', 'carousel_container', 'ad')

# Métricas que só existem em conteúdo de feed. Nenhuma delas aparece no registro
# de Story medido — e a checagem é por presença COM valor, para que um campo
# nulo herdado não barre coleta boa.
MARCAS_DE_FEED = ('play_count', 'like_count', 'comment_count', 'view_count',
                  'shortcode', 'is_reel')


class NaoEStory(ValueError):
    """O ator devolveu item, e o item não é Story. Isto é CONTRACT_DRIFT."""


def _e_story(item):
    """Prova POSITIVA de Story. Ausência de marca de Reel nunca foi prova.

    Três exigências, e a ordem é a do custo de errar: o tipo declarado pela
    plataforma, o prazo de expiração, e a garantia de que não é Highlight.
    """
    prod = item.get('product_type')
    prod_s = str(prod or '').lower()
    if prod_s in PRODUTOS_QUE_NAO_SAO_STORY:
        raise NaoEStory('item com product_type=%r — isto é Reel/feed/anúncio, não Story'
                        % prod_s)
    if prod is not None and prod_s not in PRODUTO_DE_STORY:
        raise NaoEStory('item com product_type=%r, que não é `story` — classe '
                        'desconhecida não entra por omissão' % prod_s)
    for marca in MARCAS_DE_FEED:
        if item.get(marca) not in (None, '', False):
            raise NaoEStory('item traz `%s`, métrica que só existe em conteúdo de '
                            'feed — o ator devolveu outra classe' % marca)
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
        executor=route,
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
    m = manifesto or {}
    msg = str(m.get('ERROR') or m.get('ERRO') or '')
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
