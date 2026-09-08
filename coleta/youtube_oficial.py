#!/usr/bin/env python3
"""
YOUTUBE DATA API v3 — a estrada oficial, e o maior custo Apify desta casa.

Medido no acervo: US$ 12,33 de US$ 12,81 de gasto Apify histórico é YouTube, e
US$ 7,73 disso é UM ator só, de comentários. Este arquivo existe para que aquele
gasto não precise acontecer de novo.

    ESTE ARQUIVO NÃO É UM MOTOR NOVO.

É um `route executor` do executor composto que já existe. Ele não decide se pode
rodar — quem decide é `social_rotas` consultando `social_matriz` e a política.
Ele recebe a permissão já dada e executa, contando quota.

AS QUATRO CAPACIDADES, E POR QUE ELAS NÃO SÃO A MESMA
-------------------------------------------------------
    SEARCH_KEYWORD          search.list         bucket SEARCH   1 chamada
    INCREMENTAL             playlistItems.list  bucket GENERAL  1 unidade
    FETCH_VIDEO_METADATA    videos.list         bucket GENERAL  1 unidade (até 50 IDs)
    FETCH_COMMENTS          commentThreads.list bucket GENERAL  1 unidade (100 threads)

DOIS BUCKETS, E SOMAR OS DOIS É ERRADO
----------------------------------------
A versão anterior deste arquivo declarava `search.list = 100 unidades` e afirmava que
uma busca custava CEM vezes um `playlistItems.list`. **Isso estava desatualizado, e a
matriz desta casa já dizia o contrário** — `social_matriz.py` registra, desde a
medição de 2026-09-08, "1 unidade/chamada, bucket próprio de 100 buscas/dia".

    A MATRIZ SABIA E O ADAPTADOR NÃO PERGUNTOU.

Confirmado hoje na documentação oficial: *"The search.list and videos.insert methods
have their own quota buckets"* e *"Projects that enable the YouTube Data API have a
default quota allocation of 100 search.list calls, 100 videos.insert calls, and
10,000 units per day combined for all other endpoints."*

    SEARCH BUCKET      100 chamadas/dia por projeto
    GENERAL BUCKET   10.000 unidades/dia por projeto

    1 SEARCH CALL NÃO É 100 GENERAL UNITS.
    E 4 buscas + 37 unidades NÃO são 41 de nada — são dois números.

A busca continua sendo o recurso ESCASSO, mas por outro motivo: são 100 por dia, e
acabaram. O `playlistItems.list` cabe 10.000 vezes. A conclusão prática não mudou:

    BUSCA DESCOBRE. PLAYLIST DE UPLOADS VIGIA.

O QUE ESTE ARQUIVO NÃO FAZ
----------------------------
Não busca legenda: `captions.download` exige permissão de EDITAR o vídeo, e para
vídeo de terceiro não existe rota permitida. Não baixa áudio nem vídeo. Não
transcreve. Não resume, não traduz e não corrige o texto de ninguém — ver abaixo.
E não escreve nada: `videos.insert` tem bucket próprio e esta casa nunca publica.

O COMENTÁRIO É EVIDÊNCIA
--------------------------
O texto vai para o artefato como a API o entrega, em `textOriginal`. Sem resumo,
sem tradução por cima, sem correção de ortografia, sem tirar gíria, emoji,
abreviação ou dialeto. Um dia isso vira FIELD VOICES, e o que faz aquilo valer é
exatamente o que uma limpeza apagaria.

    COMO O CAMPO FALA É O DADO. NÃO É RUÍDO.

E a estrutura da conversa é preservada: `PARENT_ID` distingue comentário de topo
de resposta, e a thread continua reconstruível sem recoletar.

GEOGRAFIA NÃO SE ADIVINHA
---------------------------
`COUNTRY_SCOPE=IT` é o recorte do PEDIDO. Não é propriedade do objeto. A API não
devolve localização de quem comentou, então `AUTHOR_LOCATION` sai `UNKNOWN` —
sempre. Idioma também não prova lugar: italiano se fala fora da Itália.
"""
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(HERE)
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401 — poe as gavetas do processo no caminho
import falhas                        # noqa: E402
import social_envelope as env        # noqa: E402
import social_matriz as mz           # noqa: E402  — DONO da regra de quota

API = 'https://www.googleapis.com/youtube/v3'

# O nome canônico da credencial. Ela vive em ambiente ou GitHub Secret, NUNCA aqui.
ENV_CHAVE = 'YOUTUBE_DATA_API_KEY'

# Os dois buckets. A REGRA vive em `social_matriz`; aqui fica só a MECÂNICA.
#
# Esta separação existe por um defeito real: até 2026-09-08 este arquivo mantinha a
# própria tabela de quota, com `search.list = 100 unidades`, enquanto a matriz já
# registrava o modelo certo. Duas tabelas, duas verdades — e a errada era a que
# executava. Agora não há segunda tabela para divergir.
#
#     A MATRIZ NÃO PODE SABER UMA COISA E O EXECUTOR OUTRA.
SEARCH = 'SEARCH'
GENERAL = 'GENERAL'
BUCKETS = (SEARCH, GENERAL)

PLATAFORMA = 'YOUTUBE'

# Espelhos de leitura. Não são declarações: são a matriz, lida.
QUOTA = dict(mz.QUOTA_METODO[PLATAFORMA])
LIMITE_PADRAO = dict(mz.LIMITE_PADRAO_PROJETO[PLATAFORMA])
QUOTA_MODEL_VERSION = mz.QUOTA_MODEL_VERSION
QUOTA_BASIS = mz.QUOTA_BASIS
QUOTA_FONTE = mz.QUOTA_FONTE

# A quota é gratuita, e "gratuito" precisa de base declarada — não de silêncio.
COST_BASIS = 'QUOTA_GRATUITA_OFICIAL'
COST_USD = 0.0

# Tetos de segurança POR EXECUÇÃO, um por bucket. Um teto só sobre os dois somados
# faria uma rodada de comentários consumir o orçamento de busca do dia, ou o
# contrário — e nenhuma das duas coisas tem sentido, porque as quotas não se falam.
#
# Os padrões deixam margem de propósito: 20 de 100 buscas e 2.000 de 10.000 unidades
# é um quinto do dia. Uma execução não é o dia inteiro.
TETO_SEARCH_PADRAO = int(os.environ.get('YT_TETO_SEARCH_CALLS') or 20)
TETO_GERAL_PADRAO = int(os.environ.get('YT_TETO_GENERAL_UNITS') or 2000)


class SemCredencial(RuntimeError):
    """Não há chave. Isto NÃO autoriza cair para scraping."""


class QuotaEstourada(RuntimeError):
    """A quota da credencial acabou. Diferente de teto NOSSO."""


class TetoDaExecucao(RuntimeError):
    """O teto desta execução acabou. Decisão da casa, não da plataforma."""


def chave(env_=None):
    e = env_ if env_ is not None else os.environ
    v = (e.get(ENV_CHAVE) or '').strip()
    return v or None


# ══════════════════════════════════════════════════════════════════════════
# O CONTADOR — toda chamada passa por aqui, e nenhuma escapa da conta
# ══════════════════════════════════════════════════════════════════════════
class Sessao:
    """Uma execução: a credencial, DOIS orçamentos, o contador e o transporte.

    Dois orçamentos porque são duas quotas. Um contador único faria a busca comer
    o orçamento de comentários — e, pior, faria o relatório somar dois números que
    não se somam.

    O transporte é injetável para que os testes exerçam quota estourada, vídeo
    apagado e comentário desativado SEM rede e SEM chave real. Um teste que
    depende da internet não roda quando mais se precisa.
    """

    def __init__(self, *, api_key=None, teto_search=None, teto_geral=None,
                 transporte=None, teto_unidades=None):
        self.api_key = api_key or chave()
        # `teto_unidades` sobrevive como apelido do teto GERAL para não quebrar
        # quem já chamava com o nome antigo. Ele nunca governou a busca de verdade.
        self.teto = {
            SEARCH: teto_search if teto_search is not None else TETO_SEARCH_PADRAO,
            GENERAL: (teto_geral if teto_geral is not None
                      else (teto_unidades if teto_unidades is not None
                            else TETO_GERAL_PADRAO)),
        }
        self._transporte = transporte or _http
        self.usado = {SEARCH: 0, GENERAL: 0}
        self.requests = 0
        self.por_metodo = {}
        self.erros = []

    def disponivel(self):
        return self.api_key is not None

    def chamar(self, metodo, params):
        """Uma chamada à API. Devolve o JSON. Levanta erro TIPADO, nunca genérico."""
        if not self.api_key:
            raise SemCredencial(
                'sem %s no ambiente. Isto é CREDENTIAL_MISSING — a rota liga no dia '
                'em que a chave existir, e NÃO se cai para scraping por causa disso.'
                % ENV_CHAVE)
        # Consulta a matriz NA HORA. O espelho `QUOTA` serve para leitura e para
        # o mapa; a decisão que gasta quota pergunta ao dono.
        bucket, custo = mz.quota_de(PLATAFORMA, metodo)
        if self.usado[bucket] + custo > self.teto[bucket]:
            raise TetoDaExecucao(
                'teto do bucket %s nesta execução (%d) seria ultrapassado por %s '
                '(+%d, usado %d). Isto é decisão NOSSA, não recusa da plataforma — e '
                'o bucket %s continua intacto.'
                % (bucket, self.teto[bucket], metodo, custo, self.usado[bucket],
                   [b for b in BUCKETS if b != bucket][0]))
        caminho = metodo.split('.')[0]
        q = dict(params); q['key'] = self.api_key
        url = '%s/%s?%s' % (API, caminho, urllib.parse.urlencode(q, doseq=True))
        self.requests += 1
        self.usado[bucket] += custo
        d = self.por_metodo.setdefault(metodo, {'REQUESTS': 0, 'BUCKET': bucket,
                                                'UNITS': 0})
        d['REQUESTS'] += 1
        d['UNITS'] += custo
        return self._transporte(url)

    def metricas(self):
        """Os dois buckets, SEPARADOS. Nunca um total somado.

        `REMAINING` não aparece: a API não devolve saldo, e ninguém consultou o
        Console. Inventar um saldo seria pior que não ter — daria a alguém a
        confiança de gastar contra um número imaginado.
        """
        return {
            'REQUESTS': self.requests,
            'SEARCH_CALLS_USED': self.usado[SEARCH],
            'SEARCH_CALLS_RUN_LIMIT': self.teto[SEARCH],
            'SEARCH_CALLS_PROJECT_LIMIT_DEFAULT': LIMITE_PADRAO[SEARCH],
            'GENERAL_UNITS_USED': self.usado[GENERAL],
            'GENERAL_UNITS_RUN_LIMIT': self.teto[GENERAL],
            'GENERAL_UNITS_PROJECT_LIMIT_DEFAULT': LIMITE_PADRAO[GENERAL],
            'SEARCH_CALLS_REMAINING': 'UNKNOWN',
            'GENERAL_UNITS_REMAINING': 'UNKNOWN',
            'POR_METODO': self.por_metodo,
            'COST_USD': COST_USD,
            'COST_BASIS': COST_BASIS,
            'QUOTA_BASIS': QUOTA_BASIS,
            'QUOTA_MODEL_VERSION': QUOTA_MODEL_VERSION,
        }


def _http(url):
    req = urllib.request.Request(url, headers={'Accept': 'application/json'})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode('utf-8', 'replace'))


# ══════════════════════════════════════════════════════════════════════════
# TRADUÇÃO DO ERRO DA API PARA A LÍNGUA ÚNICA
# ══════════════════════════════════════════════════════════════════════════
# A API do YouTube devolve 403 para coisas MUITO diferentes: quota acabou, chave
# inválida e comentário desativado. Ler os três como "403" seria juntar uma falha
# de credencial, um teto e um FATO SOBRE O VÍDEO no mesmo balde.
RAZOES = {
    'quotaExceeded': 'QUOTA_EXHAUSTED',
    'dailyLimitExceeded': 'QUOTA_EXHAUSTED',
    'rateLimitExceeded': 'RATE_LIMITED',
    'userRateLimitExceeded': 'RATE_LIMITED',
    'keyInvalid': 'AUTH_EXPIRED',
    'ipRefererBlocked': 'AUTH_EXPIRED',
    'forbidden': 'BLOCKED',
    # NÃO é NOT_APPLICABLE: a capacidade EXISTE no YouTube e está desligada NESTE
    # vídeo. E não é ZERO_RESULTS: zero é ausência de fala observada; desligado é
    # ausência de superfície de fala. Para o FIELD VOICES futuro não é a mesma
    # evidência, e juntar as duas hoje apaga a diferença para sempre.
    'commentsDisabled': 'FEATURE_DISABLED',
    'videoNotFound': 'SOURCE_GONE',
    'channelNotFound': 'SOURCE_GONE',
    'playlistNotFound': 'SOURCE_GONE',
    'processingFailure': 'SOURCE_UNAVAILABLE',
    'backendError': 'SOURCE_UNAVAILABLE',
}


def razao_de(e):
    """Extrai a razão declarada do corpo do erro. Sem adivinhar."""
    try:
        corpo = json.loads(e.read().decode('utf-8', 'replace'))
        return (corpo.get('error', {}).get('errors') or [{}])[0].get('reason')
    except Exception:                                            # noqa: BLE001
        return None


def estado_do_erro(e):
    """(estado canônico, razão nativa). O código HTTP é o último recurso."""
    razao = razao_de(e) if hasattr(e, 'read') else None
    if razao and razao in RAZOES:
        return RAZOES[razao], razao
    return falhas.classificar(http=getattr(e, 'code', None)), razao


# ══════════════════════════════════════════════════════════════════════════
# CHECKPOINT — E QUEM É O DONO DELE
# ══════════════════════════════════════════════════════════════════════════
# A versão anterior deste arquivo gravava `YOUTUBE-CHECKPOINT.json` em
# `data/samples/SOCIAL-IT/`, e o workflow fazia `git add -A` naquela pasta depois
# de cada piloto. Isso fazia do Git a memória operacional da coleta: o estado que
# decide o que a PRÓXIMA execução vai buscar entrava no repositório e crescia a
# cada corrida.
#
#     GIT NÃO É BANCO OPERACIONAL.
#
# A lei já estava medida em `docs/operacao/P-011-DADO-OPERACIONAL-NO-GIT.md`: o
# que pode ficar no Git é schema, contrato, código e amostra justificada — não
# checkpoint, não run state, não ledger operacional. E a casa já tem um dono de
# durabilidade: `coleta/coleta_checkpoint.py`, com `checkpoint_coleta` no Postgres,
# `SEM_CHECKPOINT_NAO_GASTEI` e `JA_CONCLUIDO_NAO_PAGAR_DUAS_VEZES`.
#
#     REUTILIZAR UMA FUNÇÃO DO CHECKPOINT CANÔNICO
#     NÃO É REUTILIZAR O CHECKPOINT CANÔNICO.
#
# Reusar `identidade_valida()` e escrever num JSON ao lado era exatamente isso: a
# lei emprestada, a durabilidade em outro dono. Agora a durabilidade é dele.
CHECKPOINT_LIVE = 'CHECKPOINT_CANONICAL_LIVE'
CHECKPOINT_NOT_LIVE = 'CHECKPOINT_CANONICAL_NOT_LIVE'

# A identidade de um canal no checkpoint canônico. Estável entre execuções.
CAMPOS_DA_IDENTIDADE = ('PLATFORM', 'CHANNEL_ID', 'CAPABILITY')

ENV_DSN = 'SUPABASE_DB_URL'


def _identidade(channel_id, capability='INCREMENTAL'):
    import coleta_checkpoint as cc
    ok, ruins = cc.identidade_valida(CAMPOS_DA_IDENTIDADE)
    if not ok:
        raise ValueError('identidade do checkpoint contém campo proibido: %s' % ruins)
    return cc.hash_da_entrada({'PLATFORM': PLATAFORMA, 'CHANNEL_ID': channel_id,
                               'CAPABILITY': capability})


def checkpoint_disponivel(env_=None):
    """(estado, banco_ou_None). NUNCA inventa um checkpoint de sistema de ficheiros.

    Sem DSN não há retomada — e a resposta certa é dizer isso, não abrir um
    segundo dono durável em JSON. Um piloto ainda pode rodar, mas ONE-SHOT: sem
    alegar retomada, e sem prometer que a próxima execução sabe onde esta parou.
    """
    e = env_ if env_ is not None else os.environ
    dsn = (e.get(ENV_DSN) or '').strip()
    if not dsn:
        return CHECKPOINT_NOT_LIVE, None
    import coleta_checkpoint as cc
    return CHECKPOINT_LIVE, cc.Banco(dsn)


# A UNIDADE DE TRABALHO, e por que ela inclui a JANELA
# -----------------------------------------------------
# `checkpoint_coleta` é UNIQUE (collection_target, input_hash), e um checkpoint
# CONCLUIDO recusa gasto novo — `JA_CONCLUIDO_NAO_PAGAR_DUAS_VEZES`. Isso está
# certo para a MESMA unidade e seria desastroso para monitoramento recorrente:
# um canal vigiado hoje ficaria trancado para sempre.
#
#     A UNIDADE NÃO É O CANAL. É O CANAL NUMA JANELA DE OBSERVAÇÃO.
#
# Por isso a janela entra na ENTRADA, e portanto no `input_hash`. Amanhã é outra
# unidade, outro checkpoint, e a trava continua valendo dentro de cada dia.
# `RUN_ID` e `CAPTURED_AT` continuam FORA — retomar por outra execução tem de
# reencontrar a mesma linha, e é a lei que `identidade_valida()` já impõe.
def unidade_de_trabalho(channel_id, janela, capability='INCREMENTAL'):
    """A entrada REAL da unidade. Muda com a janela; NUNCA com a execução."""
    return {'PLATFORM': PLATAFORMA, 'CHANNEL_ID': channel_id,
            'CAPABILITY': capability, 'JANELA': janela}


def janela_de_hoje():
    """A janela de observação. Um dia é o grão do monitoramento diário."""
    return _agora()[:10]


def conhecidos_do_canal(banco, video_ids):
    """O que já está SALVO — a marca de parada do incremental.

        «VI NA API» NÃO TORNA UM VÍDEO CONHECIDO.

    Delegado ao dono canônico: quem sabe o que foi persistido é quem guarda.
    """
    import coleta_checkpoint as cc
    return cc.conteudo_persistido(banco, platform=PLATAFORMA,
                                  external_ids=video_ids)


def preflight_banco(banco):
    """O schema canônico está de pé? (ok, [(nome, veredito)]). Só booleanos.

    Nunca devolve host, usuário, senha nem DSN — só se o objeto existe. Uma
    medição externa disse SIM para os três; esta função é como a casa reproduz
    isso por conta própria, no runner, antes de gastar quota.
    """
    checagens = [
        ('checkpoint_coleta existe',
         "select to_regclass('public.checkpoint_coleta') is not null"),
        ('pode_gastar(text,text) existe',
         "select to_regprocedure('public.pode_gastar(text,text)') is not null"),
        ('collection_run.checkpoint_id existe',
         "select exists (select 1 from information_schema.columns "
         "where table_schema='public' and table_name='collection_run' "
         "and column_name='checkpoint_id')"),
        ('conteudo existe (marca de CONHECIDO)',
         "select to_regclass('public.conteudo') is not null"),
    ]
    saida, tudo_ok = [], True
    for nome, sql in checagens:
        try:
            r = banco.executa(sql)
            v = (r and r[0] and r[0][0] == 't')
        except Exception:                                         # noqa: BLE001
            v = False
        tudo_ok = tudo_ok and bool(v)
        saida.append((nome, 'SIM' if v else 'NÃO'))
    return tudo_ok, saida


def cache_da_execucao():
    """Cache de playlists válido SÓ DENTRO desta execução. NÃO é checkpoint.

    CACHE EM RAM NÃO É CHECKPOINT PERSISTENTE.

    Existe para não repetir `channels.list` do mesmo canal duas vezes na mesma
    corrida. Morre com o processo, de propósito — o que sobrevive ao desligamento
    é assunto do dono canônico, e não deste dicionário.
    """
    return {}


# ══════════════════════════════════════════════════════════════════════════
# 1 · SEARCH_KEYWORD — descoberta. 1 chamada do bucket SEARCH, e são 100 por dia.
# ══════════════════════════════════════════════════════════════════════════
def buscar(*, termo, run_id, country_scope='IT', limit=25, tipo='video',
           regiao=None, idioma=None, sessao=None):
    """`search.list`. O recurso ESCASSO — mas por ser 100 por DIA, não por ser cara.

    Custa 1 chamada do bucket SEARCH. Não toca no bucket GERAL.

    `regionCode` e `relevanceLanguage` moldam o RANKING do resultado. Eles NÃO
    provam que o autor está na Itália — por isso o objeto sai com
    `SOURCE_LOCATION=UNKNOWN` mesmo com `regionCode=IT`.
    """
    s = sessao or Sessao()
    p = {'part': 'snippet', 'q': termo, 'type': tipo,
         'maxResults': min(int(limit), 50), 'order': 'relevance'}
    if regiao:
        p['regionCode'] = regiao
    if idioma:
        p['relevanceLanguage'] = idioma
    d = s.chamar('search.list', p)
    corpo = json.dumps(d, ensure_ascii=False)
    raw = env.guardar_raw('YOUTUBE', 'search-%s' % termo, corpo)
    saida = []
    for it in (d.get('items') or []):
        ident = it.get('id') or {}
        sn = it.get('snippet') or {}
        vid = ident.get('videoId')
        cid = ident.get('channelId')
        if vid:
            nid, url, ctype = vid, 'https://www.youtube.com/watch?v=%s' % vid, 'VIDEO'
        elif cid:
            nid, url, ctype = cid, 'https://www.youtube.com/channel/%s' % cid, 'CHANNEL'
        else:
            continue
        saida.append(env.envelope(
            platform='YOUTUBE', native_id=nid, url=url, content_type=ctype,
            route='youtube-data-api-v3:search.list',
            executor='youtube_oficial.buscar', run_id=run_id,
            country_scope=country_scope, source_account=sn.get('channelId'),
            published_at=sn.get('publishedAt'), title=sn.get('title'),
            text=sn.get('description'), cost_usd=COST_USD, raw_reference=raw,
            raw={'CHANNEL_TITLE': sn.get('channelTitle'),
                 'CHANNEL_ID': sn.get('channelId'),
                 'QUERY': termo, 'API_METHOD': 'search.list',
                 'COST_BASIS': COST_BASIS, 'QUOTA_BUCKET': SEARCH,
                 # regionCode molda ranking, não prova lugar. Fica no RAW como
                 # PARÂMETRO DO PEDIDO, nunca como propriedade do objeto.
                 'REQUEST_REGION_CODE': regiao or env.DESCONHECIDO,
                 'AUTHOR_LOCATION': env.DESCONHECIDO}))
    return saida, s


# ══════════════════════════════════════════════════════════════════════════
# 2 · INCREMENTAL — vigilância barata do canal conhecido. 1 unidade.
# ══════════════════════════════════════════════════════════════════════════
def uploads_derivado(channel_id):
    """PALPITE, não contrato: `UC…` → `UU…`.

    A troca de prefixo funciona hoje na maioria dos canais e NÃO é a rota
    documentada. Ela fica como reserva declarada, com esse nome, para que ninguém
    a confunda com a resposta oficial.

        HEURÍSTICA NÃO SUBSTITUI A ROTA OFICIAL
        QUANDO A API JÁ DÁ O DADO CANÔNICO.

    Quem quer o dado canônico chama `uploads_playlist()`, que pergunta à API.
    """
    if channel_id and channel_id.startswith('UC'):
        return 'UU' + channel_id[2:]
    return None


DERIVED_HINT = 'DERIVED_HINT:UC_TO_UU'
OFICIAL = 'youtube-data-api-v3:channels.list#contentDetails.relatedPlaylists.uploads'


def resolver_handle(*, handle, sessao=None, cache=None):
    """`@handle` -> (channel_id, uploads_playlist, procedencia). UMA unidade GERAL.

    Existe para não gastar busca. O acervo desta casa guarda 45 canais agrícolas
    italianos como HANDLE (`@agronotizietv`), não como `channelId` — eles vieram da
    coleta paga de 2026-08. Resolver handle por `search.list` custaria uma das 100
    buscas do dia; `channels.list?forHandle` custa 1 unidade das 10.000.

        O BALDE CERTO É PARTE DA ROTA CERTA.

    Devolve a playlist de uploads junto porque `part=contentDetails` já a traz —
    pedir as duas coisas em chamadas separadas seria pagar duas vezes pelo mesmo.
    """
    h = handle if handle.startswith('@') else '@' + handle
    cache = cache if cache is not None else {}
    for cid, c in cache.items():
        if c.get('HANDLE') == h and c.get('PROVENANCE') == OFICIAL:
            return cid, c['UPLOADS_PLAYLIST_ID'], dict(c, REUSED=True)
    s = sessao or Sessao()
    d = s.chamar('channels.list', {'part': 'contentDetails,snippet', 'forHandle': h})
    itens = d.get('items') or []
    if not itens:
        raise CanalNaoEncontrado(
            'channels.list não devolveu nada para %s — handle inexistente, trocado '
            'ou canal encerrado. NÃO é "canal sem vídeos".' % h)
    it = itens[0]
    cid = it.get('id')
    pl = (((it.get('contentDetails') or {}).get('relatedPlaylists') or {})
          .get('uploads'))
    if not cid or not pl:
        raise CanalNaoEncontrado('%s existe e não declara id/uploads' % h)
    proc = {'CHANNEL_ID': cid, 'HANDLE': h, 'UPLOADS_PLAYLIST_ID': pl,
            'CHANNEL_TITLE': (it.get('snippet') or {}).get('title'),
            'PROVENANCE': OFICIAL, 'RESOLVED_AT': _agora(), 'REUSED': False}
    cache[cid] = dict(proc)
    return cid, pl, proc


def uploads_playlist(*, channel_id, sessao=None, cache=None):
    """A playlist de uploads, pela rota OFICIAL: `channels.list part=contentDetails`.

    Devolve `(playlist_id, procedencia)`. A procedência importa tanto quanto o ID:
    ela diz que aquilo veio da API, e isso segue para o artefato.

    ESTA FUNÇÃO NÃO TEM RESERVA, E ISSO É O CONSERTO
    --------------------------------------------------
    A versão anterior terminava em `except Exception: if permitir_derivado: usa
    UC→UU`. Isso engolia — e transformava em palpite utilizável — TUDO o que não
    fosse falta de credencial ou teto: timeout de rede, chave inválida, quota
    esgotada, canal inexistente, e a nossa própria `KeyError` quando o JSON
    mudasse de forma. Seis falhas de naturezas diferentes viravam o mesmo
    "a API não respondeu, então chutei".

        FALHA DA ROTA OFICIAL NÃO TRANSFORMA HEURÍSTICA EM FATO.

    Agora ela levanta a falha REAL, e quem chamou decide o que fazer. Quem quiser
    o palpite pede por ele, pelo nome, em `uploads_hint()` — e tem de dizer por quê.

    ECONOMIA: `cache` é `{channel_id: {...}}` e vem do checkpoint entre execuções.
    Canal já resolvido NÃO gasta unidade. Descobrir é o custo; vigiar não é.
    """
    cache = cache if cache is not None else {}
    guardado = cache.get(channel_id)
    if guardado and guardado.get('UPLOADS_PLAYLIST_ID'):
        # Só reutiliza o que foi resolvido OFICIALMENTE. Um palpite guardado numa
        # execução passada não vira fato por ter envelhecido no disco.
        if guardado.get('PROVENANCE') == OFICIAL:
            return guardado['UPLOADS_PLAYLIST_ID'], dict(guardado, REUSED=True)
    s = sessao or Sessao()
    d = s.chamar('channels.list', {'part': 'contentDetails', 'id': channel_id})
    itens = d.get('items') or []
    if not itens:
        # Pedido nominalmente e não devolvido. Isso é o canal, não a rota.
        raise CanalNaoEncontrado(
            'channels.list não devolveu %s — canal inexistente, encerrado ou '
            'fora desta região. NÃO é "canal sem uploads".' % channel_id)
    pl = (((itens[0].get('contentDetails') or {}).get('relatedPlaylists') or {})
          .get('uploads'))
    if not pl:
        raise CanalNaoEncontrado(
            '%s existe e não declara `relatedPlaylists.uploads`' % channel_id)
    proc = {'CHANNEL_ID': channel_id, 'UPLOADS_PLAYLIST_ID': pl,
            'PROVENANCE': OFICIAL, 'RESOLVED_AT': _agora(), 'REUSED': False}
    cache[channel_id] = dict(proc)
    return pl, proc


# Motivos que NÃO bastam para usar o palpite. São exatamente as desculpas que a
# versão anterior aceitava sozinha, e aceitar de novo seria reabrir a brecha
# pela porta da frente.
_DESCULPAS = ('api falhou', 'api nao respondeu', 'api não respondeu', 'deu erro',
              'erro na api', 'timeout', 'falhou', 'nao funcionou', 'não funcionou',
              'channels.list falhou', 'oficial falhou')


def uploads_hint(*, channel_id, porque):
    """O palpite `UC…`→`UU…`, pedido pelo NOME e com motivo declarado.

    Nunca é chamado por engano: não há caminho automático até aqui. Quem usa
    assume, por escrito, que está dirigindo coleta com um ID que ninguém confirmou.

        HEURÍSTICA NÃO SUBSTITUI A ROTA OFICIAL
        QUANDO A API JÁ DÁ O DADO CANÔNICO.

    `porque` não aceita "a API falhou": isso é a descrição do problema, não uma
    razão para trocar fato por chute. Uma razão aceitável diz o que se ganha
    apesar do risco — por exemplo, um levantamento exploratório descartável cujo
    resultado não vai virar acervo.
    """
    limpo = (porque or '').strip()
    if len(limpo) < 25:
        raise ValueError('uploads_hint exige um motivo escrito, não um rótulo: %r'
                         % porque)
    if any(d in limpo.lower() for d in _DESCULPAS) and len(limpo) < 80:
        raise ValueError(
            '"%s" descreve a falha, não justifica o palpite. A rota oficial falhar '
            'NÃO autoriza transformar heurística em fato — diga o que se ganha '
            'apesar de o ID não estar confirmado.' % limpo)
    pl = uploads_derivado(channel_id)
    if not pl:
        raise ValueError('%r não tem a forma UC… — não há palpite a dar' % channel_id)
    return pl, {'CHANNEL_ID': channel_id, 'UPLOADS_PLAYLIST_ID': pl,
                'PROVENANCE': DERIVED_HINT, 'RESOLVED_AT': _agora(),
                'REUSED': False, 'WHY_DERIVED_HINT_USED': limpo,
                'AVISO': 'ID NÃO CONFIRMADO pela API — isto é palpite, não fato'}


class CanalNaoEncontrado(RuntimeError):
    """O canal foi pedido nominalmente e negado nominalmente."""


def _agora():
    import datetime
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')


def uploads_recentes(*, channel_id, run_id, country_scope='IT', limit=25,
                     conhecidos=(), sessao=None, cache=None):
    """`playlistItems.list` sobre a playlist de uploads. UMA unidade por página.

    `conhecidos` implementa `newest → until known`: a API devolve do mais novo
    para o mais velho, e assim que bate num vídeo já coletado a varredura PARA.
    É o que impede varrer o histórico inteiro todo dia.

    Devolve `(novos, sessao, relatorio)`. `relatorio` separa NOVOS de REUSADOS,
    porque "nada novo hoje" é uma MEDIÇÃO — e não uma coleta que falhou.
    """
    s = sessao or Sessao()
    pl, proc = uploads_playlist(channel_id=channel_id, sessao=s, cache=cache)
    ja = set(conhecidos or ())
    novos, reusados, examinados, parou = [], 0, 0, False
    token = None
    while True:
        p = {'part': 'snippet,contentDetails', 'playlistId': pl,
             'maxResults': min(int(limit), 50)}
        if token:
            p['pageToken'] = token
        d = s.chamar('playlistItems.list', p)
        corpo = json.dumps(d, ensure_ascii=False)
        raw = env.guardar_raw('YOUTUBE', 'uploads-%s' % channel_id, corpo)
        for it in (d.get('items') or []):
            examinados += 1
            cd = it.get('contentDetails') or {}
            sn = it.get('snippet') or {}
            vid = cd.get('videoId')
            if not vid:
                continue
            if vid in ja:
                reusados += 1
                parou = True
                break
            novos.append(env.envelope(
                platform='YOUTUBE', native_id=vid,
                url='https://www.youtube.com/watch?v=%s' % vid,
                content_type='VIDEO', route='youtube-data-api-v3:playlistItems.list',
                executor='youtube_oficial.uploads_recentes', run_id=run_id,
                country_scope=country_scope, source_account=channel_id,
                published_at=cd.get('videoPublishedAt') or sn.get('publishedAt'),
                title=sn.get('title'), text=sn.get('description'),
                cost_usd=COST_USD, raw_reference=raw,
                raw={'CHANNEL_ID': channel_id, 'UPLOADS_PLAYLIST': pl,
                     'UPLOADS_PLAYLIST_PROVENANCE': proc['PROVENANCE'],
                     'API_METHOD': 'playlistItems.list', 'COST_BASIS': COST_BASIS,
                     'QUOTA_BUCKET': GENERAL,
                     'AUTHOR_LOCATION': env.DESCONHECIDO}))
        token = d.get('nextPageToken')
        if parou or not token or len(novos) >= int(limit):
            break
    return novos, s, {'CHANNEL_ID': channel_id, 'UPLOADS_EXAMINED': examinados,
                      'NEW': len(novos), 'REUSED': reusados,
                      'STOPPED_AT_KNOWN': parou,
                      'UPLOADS_PLAYLIST_ID': pl,
                      'UPLOADS_PLAYLIST_PROVENANCE': proc['PROVENANCE'],
                      'UPLOADS_PLAYLIST_REUSED': proc.get('REUSED', False)}


# ══════════════════════════════════════════════════════════════════════════
# 3 · FETCH_VIDEO_METADATA — 1 unidade para até 50 IDs.
# ══════════════════════════════════════════════════════════════════════════
def metadata(*, video_ids, run_id, country_scope='IT', sessao=None):
    """`videos.list` em lote de 50. Devolve `(objetos, sessao, relatorio)`.

    O relatório traz `MISSING` — os IDs pedidos que a API não devolveu. Isso é
    detecção de remoção de graça: pedido nominalmente e não devolvido é diferente
    de ausente numa varredura.
    """
    s = sessao or Sessao()
    pedidos = [v for v in dict.fromkeys(video_ids) if v]
    saida, vistos = [], set()
    for i in range(0, len(pedidos), 50):
        lote = pedidos[i:i + 50]
        d = s.chamar('videos.list', {
            'part': 'snippet,statistics,contentDetails,status', 'id': ','.join(lote)})
        corpo = json.dumps(d, ensure_ascii=False)
        raw = env.guardar_raw('YOUTUBE', 'videos-%s' % lote[0], corpo)
        for it in (d.get('items') or []):
            vid = it.get('id')
            sn = it.get('snippet') or {}
            st = it.get('statistics') or {}
            cdt = it.get('contentDetails') or {}
            vistos.add(vid)
            saida.append(env.envelope(
                platform='YOUTUBE', native_id=vid,
                url='https://www.youtube.com/watch?v=%s' % vid,
                content_type='VIDEO', route='youtube-data-api-v3:videos.list',
                executor='youtube_oficial.metadata', run_id=run_id,
                country_scope=country_scope, source_account=sn.get('channelId'),
                published_at=sn.get('publishedAt'), title=sn.get('title'),
                text=sn.get('description'),
                # `defaultAudioLanguage` é DECLARAÇÃO do canal sobre o áudio.
                # Não é prova de lugar, e nunca vira SOURCE_LOCATION.
                language=sn.get('defaultAudioLanguage') or sn.get('defaultLanguage'),
                cost_usd=COST_USD, raw_reference=raw,
                raw={'CHANNEL_ID': sn.get('channelId'),
                     'CHANNEL_TITLE': sn.get('channelTitle'),
                     'VIEW_COUNT': st.get('viewCount'),
                     'LIKE_COUNT': st.get('likeCount'),
                     'COMMENT_COUNT': st.get('commentCount'),
                     'DURATION': cdt.get('duration'),
                     'TAGS': sn.get('tags') or [],
                     'API_METHOD': 'videos.list', 'COST_BASIS': COST_BASIS,
                     'QUOTA_BUCKET': GENERAL,
                     'AUTHOR_LOCATION': env.DESCONHECIDO}))
    faltando = [v for v in pedidos if v not in vistos]
    return saida, s, {'IDS_REQUESTED': len(pedidos), 'RETURNED': len(saida),
                      'MISSING': faltando}


# ══════════════════════════════════════════════════════════════════════════
# 4 · FETCH_COMMENTS — a prioridade. US$ 7,73 do gasto histórico é isto.
# ══════════════════════════════════════════════════════════════════════════
def _comentario(c, *, video_id, parent_id, run_id, country_scope, raw_ref, canal):
    """Um comentário vira envelope. O texto vai INTEIRO, como a API entregou."""
    sn = c.get('snippet') or {}
    autor = (sn.get('authorChannelId') or {}).get('value')
    cid = c.get('id')
    return env.envelope(
        platform='YOUTUBE', native_id=cid,
        url='https://www.youtube.com/watch?v=%s&lc=%s' % (video_id, cid),
        content_type='COMMENT', route='youtube-data-api-v3:commentThreads.list',
        executor='youtube_oficial.comentarios', run_id=run_id,
        country_scope=country_scope, source_account=autor or env.DESCONHECIDO,
        published_at=sn.get('publishedAt'),
        # O ORIGINAL vem primeiro. `textDisplay` traz HTML e links reescritos
        # pela plataforma; `textOriginal` é o que a pessoa digitou.
        text=sn.get('textOriginal') if sn.get('textOriginal') is not None
        else sn.get('textDisplay'),
        cost_usd=COST_USD, raw_reference=raw_ref,
        raw={
            'COMMENT_ID': cid,
            'PARENT_ID': parent_id,                 # None = comentário de topo
            'IS_REPLY': parent_id is not None,
            'VIDEO_ID': video_id,
            'CHANNEL_ID': canal,
            'AUTHOR_CHANNEL_ID': autor or env.DESCONHECIDO,
            'AUTHOR_DISPLAY_NAME': sn.get('authorDisplayName'),
            'TEXT_ORIGINAL': sn.get('textOriginal'),
            'TEXT_DISPLAY': sn.get('textDisplay'),
            'PUBLISHED_AT': sn.get('publishedAt'),
            'UPDATED_AT': sn.get('updatedAt'),
            'LIKE_COUNT': sn.get('likeCount'),
            'API_METHOD': 'commentThreads.list' if parent_id is None else 'comments.list',
            'COST_BASIS': COST_BASIS, 'QUOTA_BUCKET': GENERAL,
            # A API não devolve lugar de quem comentou. Não se inventa.
            'AUTHOR_LOCATION': env.DESCONHECIDO,
        })


def comentarios(*, video_id, run_id, country_scope='IT', limite_threads=100,
                completar_respostas=True, sessao=None):
    """`commentThreads.list`, e `comments.list` quando a thread veio incompleta.

    Devolve `(objetos, sessao, relatorio)`. O relatório separa TRÊS coisas que
    parecem a mesma e não são:

        FEATURE_DISABLED    o dono desligou os comentários. A fonte respondeu, a
                            rota funcionou, o nosso código funcionou. É um FATO
                            sobre o vídeo — nem coleta vazia, nem falha nossa.
        ZERO_LEGITIMATE     respondeu, comentários ligados, ninguém comentou.
        <erro canônico>     não conseguimos olhar.

    Transformar as três em `ZERO_RESULTS` seria apagar a diferença entre
    "não tinha o que colher" e "não me deixaram colher".
    """
    s = sessao or Sessao()
    rel = {'VIDEO_ID': video_id, 'THREADS': 0, 'COMMENTS': 0, 'REPLIES': 0,
           'PAGES': 0, 'REPLIES_COMPLETED': 0, 'REPLIES_MISSING': 0,
           'STATE': None, 'NATIVE_REASON': None}
    saida, token = [], None
    try:
        while True:
            p = {'part': 'snippet,replies', 'videoId': video_id,
                 'maxResults': min(int(limite_threads), 100), 'textFormat': 'plainText',
                 'order': 'time'}
            if token:
                p['pageToken'] = token
            d = s.chamar('commentThreads.list', p)
            rel['PAGES'] += 1
            corpo = json.dumps(d, ensure_ascii=False)
            raw = env.guardar_raw('YOUTUBE', 'comments-%s-p%d' % (video_id, rel['PAGES']),
                                  corpo)
            for th in (d.get('items') or []):
                rel['THREADS'] += 1
                sn = th.get('snippet') or {}
                canal = sn.get('channelId')
                topo = sn.get('topLevelComment') or {}
                saida.append(_comentario(topo, video_id=video_id, parent_id=None,
                                         run_id=run_id, country_scope=country_scope,
                                         raw_ref=raw, canal=canal))
                total = int(sn.get('totalReplyCount') or 0)
                trazidas = (th.get('replies') or {}).get('comments') or []
                for r in trazidas:
                    saida.append(_comentario(r, video_id=video_id,
                                             parent_id=topo.get('id'), run_id=run_id,
                                             country_scope=country_scope,
                                             raw_ref=raw, canal=canal))
                rel['REPLIES'] += len(trazidas)
                # O envelope inicial NÃO garante a thread inteira. Quando a API diz
                # que há mais respostas do que trouxe, buscar o resto — senão a
                # conversa fica truncada no acervo e ninguém percebe.
                if completar_respostas and total > len(trazidas):
                    extras, faltou = _completar(s, topo.get('id'), video_id=video_id,
                                                run_id=run_id, canal=canal,
                                                country_scope=country_scope,
                                                ja=len(trazidas), total=total)
                    saida.extend(extras)
                    rel['REPLIES'] += len(extras)
                    rel['REPLIES_COMPLETED'] += 1
                    rel['REPLIES_MISSING'] += faltou
            token = d.get('nextPageToken')
            if not token or len(saida) >= int(limite_threads) * 5:
                break
    except urllib.error.HTTPError as e:
        estado, razao = estado_do_erro(e)
        rel['STATE'] = estado
        rel['NATIVE_REASON'] = razao
        rel['RECOVERY_ACTION'] = falhas.recuperacao(estado, razao)
        if razao == 'commentsDisabled':
            rel['COMMENTS_DISABLED'] = True
            rel['FEATURE'] = 'COMMENTS'
        return saida, s, rel
    rel['COMMENTS'] = len(saida)
    rel['STATE'] = 'OK' if saida else 'ZERO_RESULTS'
    if not saida:
        rel['ZERO_LEGITIMATE'] = True
    return saida, s, rel


def _completar(s, parent_id, *, video_id, run_id, canal, country_scope, ja, total):
    """`comments.list(parentId=…)` até fechar a thread. Registra o que faltou."""
    achados, token = [], None
    while True:
        p = {'part': 'snippet', 'parentId': parent_id, 'maxResults': 100,
             'textFormat': 'plainText'}
        if token:
            p['pageToken'] = token
        try:
            d = s.chamar('comments.list', p)
        except (urllib.error.HTTPError, TetoDaExecucao, QuotaEstourada):
            break
        corpo = json.dumps(d, ensure_ascii=False)
        raw = env.guardar_raw('YOUTUBE', 'replies-%s' % parent_id, corpo)
        for c in (d.get('items') or []):
            achados.append(_comentario(c, video_id=video_id, parent_id=parent_id,
                                       run_id=run_id, country_scope=country_scope,
                                       raw_ref=raw, canal=canal))
        token = d.get('nextPageToken')
        if not token:
            break
    # `comments.list` devolve TODAS as respostas, não só as que faltavam.
    obtidas = len(achados) if achados else ja
    return achados, max(0, total - obtidas)


def main():
    s = Sessao()
    print('YOUTUBE DATA API v3 — estrada oficial')
    print('  CREDENCIAL   %s (%s)' % ('PRESENTE' if s.disponivel() else 'AUSENTE', ENV_CHAVE))
    print('  COST_BASIS   %s · COST_USD %.2f' % (COST_BASIS, COST_USD))
    print('  QUOTA MODEL  %s' % QUOTA_MODEL_VERSION)
    print('\n  DOIS BUCKETS — e eles NÃO se somam')
    print('    %-10s padrão do projeto %6s/dia · teto desta execução %6s'
          % (SEARCH, LIMITE_PADRAO[SEARCH], s.teto[SEARCH]))
    print('    %-10s padrão do projeto %6s/dia · teto desta execução %6s'
          % (GENERAL, LIMITE_PADRAO[GENERAL], s.teto[GENERAL]))
    print('\n  MÉTODO                 BUCKET   CUSTO')
    for m, (b, u) in sorted(QUOTA.items(), key=lambda x: (x[1][0], x[0])):
        print('    %-22s %-8s %d' % (m, b, u))
    print('\n  1 SEARCH CALL NÃO É 100 GENERAL UNITS.')
    print('  A busca é escassa por ser 100/dia — não por ser cara.')
    print('  BUSCA DESCOBRE. PLAYLIST DE UPLOADS VIGIA.')
    print('\n  SALDO RESTANTE: UNKNOWN — a API não devolve, e ninguém leu o Console.')
    if not s.disponivel():
        print('\n  ESTADO  CREDENTIAL_MISSING — e isto NÃO autoriza cair para scraping.')
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
