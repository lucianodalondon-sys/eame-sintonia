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
    SEARCH_KEYWORD          search.list         100 unidades  ← DESCOBERTA, cara
    INCREMENTAL             playlistItems.list    1 unidade   ← VIGILÂNCIA, barata
    FETCH_VIDEO_METADATA    videos.list           1 unidade   ← até 50 IDs por chamada
    FETCH_COMMENTS          commentThreads.list   1 unidade   ← 100 threads por chamada

`search.list` custa CEM vezes o `playlistItems.list`. Usar busca para vigiar canal
conhecido queima a quota do dia em 100 chamadas. Por isso são capacidades separadas:

    BUSCA DESCOBRE. PLAYLIST DE UPLOADS VIGIA.

O QUE ESTE ARQUIVO NÃO FAZ
----------------------------
Não busca legenda: `captions.download` exige permissão de EDITAR o vídeo, e para
vídeo de terceiro não existe rota permitida. Não baixa áudio nem vídeo. Não
transcreve. Não resume, não traduz e não corrige o texto de ninguém — ver abaixo.

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
sys.path.insert(0, HERE)
import falhas                        # noqa: E402
import social_envelope as env        # noqa: E402

API = 'https://www.googleapis.com/youtube/v3'

# O nome canônico da credencial. Ela vive em ambiente ou GitHub Secret, NUNCA aqui.
ENV_CHAVE = 'YOUTUBE_DATA_API_KEY'

# Custo em unidades de quota, da tabela oficial. É o que torna o orçamento real.
# https://developers.google.com/youtube/v3/determine_quota_cost
QUOTA = {
    'search.list': 100,
    'videos.list': 1,
    'channels.list': 1,
    'playlistItems.list': 1,
    'commentThreads.list': 1,
    'comments.list': 1,
}

# A quota é gratuita, e "gratuito" precisa de base declarada — não de silêncio.
COST_BASIS = 'QUOTA_GRATUITA_OFICIAL'
COST_USD = 0.0

# Teto de segurança por execução. 10.000 unidades/dia é o padrão da conta; gastar
# tudo numa rodada deixa o resto do dia sem coleta.
TETO_UNIDADES_PADRAO = int(os.environ.get('YT_TETO_UNIDADES') or 2000)


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
    """Uma execução: a credencial, o teto, o contador e o transporte.

    O transporte é injetável para que os testes exerçam quota estourada, vídeo
    apagado e comentário desativado SEM rede e SEM chave real. Um teste que
    depende da internet não roda quando mais precisa.
    """

    def __init__(self, *, api_key=None, teto_unidades=None, transporte=None):
        self.api_key = api_key or chave()
        self.teto = teto_unidades if teto_unidades is not None else TETO_UNIDADES_PADRAO
        self._transporte = transporte or _http
        self.unidades = 0
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
        custo = QUOTA[metodo]
        if self.unidades + custo > self.teto:
            raise TetoDaExecucao(
                'teto desta execução (%d unidades) seria ultrapassado por %s (+%d). '
                'Isto é decisão NOSSA, não recusa da plataforma.'
                % (self.teto, metodo, custo))
        caminho = metodo.split('.')[0]
        q = dict(params); q['key'] = self.api_key
        url = '%s/%s?%s' % (API, caminho, urllib.parse.urlencode(q, doseq=True))
        self.requests += 1
        self.unidades += custo
        d = self.por_metodo.setdefault(metodo, {'REQUESTS': 0, 'QUOTA_UNITS': 0})
        d['REQUESTS'] += 1
        d['QUOTA_UNITS'] += custo
        return self._transporte(url)

    def metricas(self):
        return {
            'REQUESTS': self.requests,
            'QUOTA_UNITS': self.unidades,
            'QUOTA_TETO': self.teto,
            'POR_METODO': self.por_metodo,
            'COST_USD': COST_USD,
            'COST_BASIS': COST_BASIS,
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
    'commentsDisabled': 'NOT_APPLICABLE',
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
# 1 · SEARCH_KEYWORD — descoberta. 100 unidades. Usar com parcimônia.
# ══════════════════════════════════════════════════════════════════════════
def buscar(*, termo, run_id, country_scope='IT', limit=25, tipo='video',
           regiao=None, idioma=None, sessao=None):
    """`search.list`. A rota CARA: 100 unidades por chamada.

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
                 'COST_BASIS': COST_BASIS,
                 # regionCode molda ranking, não prova lugar. Fica no RAW como
                 # PARÂMETRO DO PEDIDO, nunca como propriedade do objeto.
                 'REQUEST_REGION_CODE': regiao or env.DESCONHECIDO,
                 'AUTHOR_LOCATION': env.DESCONHECIDO}))
    return saida, s


# ══════════════════════════════════════════════════════════════════════════
# 2 · INCREMENTAL — vigilância barata do canal conhecido. 1 unidade.
# ══════════════════════════════════════════════════════════════════════════
def playlist_de_uploads(channel_id):
    """O truque documentado: a playlist de uploads é o ID do canal com `UC`→`UU`.

    Evita uma chamada a `channels.list` só para descobrir um ID derivável.
    """
    if channel_id and channel_id.startswith('UC'):
        return 'UU' + channel_id[2:]
    return None


def uploads_recentes(*, channel_id, run_id, country_scope='IT', limit=25,
                     conhecidos=(), sessao=None):
    """`playlistItems.list` sobre a playlist de uploads. UMA unidade por página.

    `conhecidos` implementa `newest → until known`: a API devolve do mais novo
    para o mais velho, e assim que bate num vídeo já coletado a varredura PARA.
    É o que impede varrer o histórico inteiro todo dia.

    Devolve `(novos, sessao, relatorio)`. `relatorio` separa NOVOS de REUSADOS,
    porque "nada novo hoje" é uma MEDIÇÃO — e não uma coleta que falhou.
    """
    s = sessao or Sessao()
    pl = playlist_de_uploads(channel_id)
    if not pl:
        raise ValueError('channel_id fora do formato UC…: %r' % channel_id)
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
                     'API_METHOD': 'playlistItems.list', 'COST_BASIS': COST_BASIS,
                     'AUTHOR_LOCATION': env.DESCONHECIDO}))
        token = d.get('nextPageToken')
        if parou or not token or len(novos) >= int(limit):
            break
    return novos, s, {'CHANNEL_ID': channel_id, 'UPLOADS_EXAMINED': examinados,
                      'NEW': len(novos), 'REUSED': reusados,
                      'STOPPED_AT_KNOWN': parou}


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
            'COST_BASIS': COST_BASIS,
            # A API não devolve lugar de quem comentou. Não se inventa.
            'AUTHOR_LOCATION': env.DESCONHECIDO,
        })


def comentarios(*, video_id, run_id, country_scope='IT', limite_threads=100,
                completar_respostas=True, sessao=None):
    """`commentThreads.list`, e `comments.list` quando a thread veio incompleta.

    Devolve `(objetos, sessao, relatorio)`. O relatório separa TRÊS coisas que
    parecem a mesma e não são:

        COMMENTS_DISABLED   o dono desligou. A fonte respondeu — é um FATO sobre
                            o vídeo, não uma coleta vazia e não uma falha nossa.
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
    print('  TETO         %d unidades por execução' % s.teto)
    print('\n  CUSTO EM QUOTA POR MÉTODO')
    for m, u in sorted(QUOTA.items(), key=lambda x: -x[1]):
        print('    %-22s %3d unidade%s' % (m, u, 's' if u > 1 else ''))
    print('\n  search.list custa 100x playlistItems.list.')
    print('  BUSCA DESCOBRE. PLAYLIST DE UPLOADS VIGIA.')
    if not s.disponivel():
        print('\n  ESTADO  CREDENTIAL_MISSING — e isto NÃO autoriza cair para scraping.')
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
