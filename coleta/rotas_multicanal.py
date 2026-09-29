# -*- coding: utf-8 -*-
"""AS ROTAS PUBLICAS DAS LINHAS NAO-WEB — YOUTUBE, INSTAGRAM, LINKEDIN (RELIGA-MULTICANAL, D155, 29/09/2026).

    from coleta import rotas_multicanal as RM
    RM.youtube_videos_do_canal(channel_id="UC...", buscar=RM.transporte())   -> [{URL, NOME, ...}]
    RM.instagram_reels_da_conta(handle="bayer_italia", buscar=...)          -> [{URL, ...}]
    RM.linkedin_posts_da_organizacao(pagina_url="https://www.linkedin.com/company/x/", ...)

O QUE ISTO E: as rotas que a casa JA PROVOU, escritas uma vez, para a coleta continua poder correr as
linhas nao-web no MESMO ciclo das SITES. Nao ha rota nova aqui, e nao ha rota paga: cada funcao abaixo cita
a prova que a autoriza e a decisao do dono que a abre.

    NADA AQUI INVENTA UMA ROTA. O QUE NAO ESTA PROVADO DEVOLVE ERRO COM NOME.

A PORTA E UMA SO — `coleta/scrap_http.buscar_bytes`. Por ela passam, sem excepcao e sem ordem de import:
robots vivo (D91), o portao de egresso, a lista de hosts proibidos, o orcamento de rede, a pausa de
cortesia e — por `coleta/teto_da_onda.reservar` — a RESERVA no livro de 24 h ANTES do pedido sair e o
REGISTO da resposta depois. Uma rota que abrisse a sua propria ligacao seria um segundo caminho invisivel:

    UM PEDIDO QUE NAO PASSA PELA PORTA NAO EXISTE PARA O CONTADOR.

⚠️ A ARMADILHA QUE ESTE FICHEIRO NAO PODE REPETIR (medida pelo Scrap, 28/09): `scrap_http` instala um
abridor GLOBAL do urllib. Num processo que o tenha importado, ate `urlopen` cru reserva — por CONTAGIO, nao
por ligacao. Por isso a sonda mede UMA LINHA POR PROCESSO, e por isso estas funcoes recebem o transporte
INJECTADO (`buscar`): quem testa passa o seu, e ninguem depende de quem importou o que primeiro.
"""
from __future__ import annotations

import json
import os
import re
import sys
import urllib.parse

_AQUI = os.path.dirname(os.path.abspath(__file__))
if _AQUI not in sys.path:
    sys.path.insert(0, _AQUI)


# ══════════════════════════════════════════════════════════════════════════════
# O TRANSPORTE — a porta unica, injectavel
# ══════════════════════════════════════════════════════════════════════════════
def transporte():
    """O transporte canonico: `scrap_http.buscar_bytes` -> (status, cabecalhos, bytes).

    Devolve SEMPRE um triplo, tambem quando a rota e recusada — a recusa e um resultado, e quem chama
    precisa do NOME de quem disse nao (a nossa politica? a plataforma?) para nao os confundir."""
    import scrap_http as http                                      # noqa: PLC0415

    def buscar(url, aceitar="text/html,application/xhtml+xml,*/*;q=0.5"):
        try:
            corpo, meta = http.buscar_bytes(url, aceitar=aceitar)
            return {"STATUS": meta.get("STATUS"), "BYTES": corpo, "CONTENT_TYPE": meta.get("CONTENT_TYPE"),
                    "ERRO": None}
        except http.RotaNaoPermitida as ex:                        # a NOSSA politica (robots, teto, host)
            return {"STATUS": None, "BYTES": None, "ERRO": "ROTA_NAO_PERMITIDA: %s" % ex, "QUEM_DISSE_NAO": "NOS"}
        except http.RotaBloqueada as ex:                           # a PLATAFORMA
            return {"STATUS": None, "BYTES": None, "ERRO": "ROTA_BLOQUEADA: %s" % ex, "QUEM_DISSE_NAO": "PLATAFORMA"}
    return buscar


# ══════════════════════════════════════════════════════════════════════════════
# YOUTUBE — a pagina publica do separador Videos
# ══════════════════════════════════════════════════════════════════════════════
# PORTE SEMANTICO de `claude/youtube-canonical-free-route-v1 @7857d7b79`, adapter CANAL_PUBLICO_YOUTUBE_V1
# (`coleta/adaptadores_de_aquisicao.mjs`, 11 testes, canarios IT-T8-001 e IT-T7-015 PASS). O .mjs vem junto
# nesta entrega, com os seus testes; isto e o MESMO comportamento do lado Python, que e o lado onde a coleta
# continua corre. Nao e uma segunda regra: e a mesma regra, no executor que o ciclo usa.
#
# A ROTA:  https://www.youtube.com/channel/<CHANNEL_ID>/videos
# PROVA:   ROBOTS_GATE = PASS (o portao da casa aprova esta rota; o feed `/feeds/videos.xml` esta
#          ROUTE_NOT_ALLOWED por robots — `leis/social_matriz.py`, e o molde abaixo nem o alcanca).
# CUSTO:   0 USD. Sem chave, sem cookie, sem login. A API oficial do Google NAO e requisito (D155).
#
# PORQUE NAO E UM `LINK_PATTERN`: medido — a pagina traz `videoId` = 30 e `href="/watch?v="` = 0. Os
# enderecos vivem dentro do `ytInitialData`, em JSON embutido no HTML.
#
# ⚠️ A IDENTIDADE LE-SE DO CANAL, NUNCA DO ITEM. Em `yt-dlp --flat-playlist` o `channel_id` do ITEM vem
# `NA`; uma guarda construida sobre o item compara `NA` com o pedido e nunca casa — ou, escrita para
# tolerar `NA`, APROVA SEMPRE. Uma fechadura que nunca tranca. Aqui a identidade vem do documento do
# CANAL, e `IDENTITY_MISMATCH` e falha FECHADA: zero alvos, nao «os alvos que vieram».
RE_CHANNEL_ID = re.compile(r"^UC[A-Za-z0-9_-]{22}$")
RE_VIDEO_ID = re.compile(r'"videoId":"([A-Za-z0-9_-]{11})"')
RE_CANAL_NO_HTML = re.compile(r'"(?:channelId|externalId)":"(UC[A-Za-z0-9_-]{22})"')
RE_CANONICAL = re.compile(r'<link rel="canonical" href="([^"]+)"')

ROTA_YOUTUBE = "youtube:pagina-publica-do-canal"


def youtube_videos_do_canal(*, channel_id, buscar, max_alvos=None):
    """→ {"ALVOS": [{URL, NOME}], "ROTA", "PEDIDOS", "HTML"} ou {"ERRO": ...}. Zero processo filho."""
    if not isinstance(channel_id, str) or not RE_CHANNEL_ID.match(channel_id or ""):
        return {"ERRO": "CHANNEL_ID_INVALIDO: esperado UC + 22 caracteres, veio %r" % (channel_id,), "PEDIDOS": 0}
    if max_alvos is not None and (not isinstance(max_alvos, int) or max_alvos < 1):
        return {"ERRO": "MAX_ALVOS_INVALIDO: inteiro >= 1, veio %r" % (max_alvos,), "PEDIDOS": 0}
    if not callable(buscar):
        return {"ERRO": "SEM_TRANSPORTE: esta rota nao inventa transporte", "PEDIDOS": 0}
    # A rota e construida AQUI a partir do CHANNEL_ID. O feed barrado nao e alcancavel por este molde
    # nem por engano.
    url = "https://www.youtube.com/channel/%s/videos" % channel_id
    r = buscar(url)
    if r.get("ERRO") or r.get("STATUS") != 200:
        return {"ERRO": "a pagina publica do canal nao respondeu 200 (status %s%s)"
                % (r.get("STATUS") or 0, ", " + r["ERRO"] if r.get("ERRO") else ""),
                "PEDIDOS": 1, "URL": url, "QUEM_DISSE_NAO": r.get("QUEM_DISSE_NAO")}
    html = (r.get("BYTES") or b"").decode("utf-8", "replace")
    # IDENTIDADE PRIMEIRO. So depois se olha para o conteudo: aceitar alvos de um canal e carimba-los com
    # o SOURCE_ID de outro e PIOR do que nao colher.
    declarados = set(RE_CANAL_NO_HTML.findall(html))
    canonical = RE_CANONICAL.search(html)
    bate = channel_id in declarados or bool(canonical and channel_id in canonical.group(1))
    if not bate:
        vistos = ", ".join(sorted(declarados)[:3]) or "nenhum"
        return {"ERRO": "IDENTITY_MISMATCH: pedi %s e a pagina declara %s" % (channel_id, vistos),
                "PEDIDOS": 1, "URL": url}
    ids = list(dict.fromkeys(RE_VIDEO_ID.findall(html)))
    if not ids:
        return {"ERRO": "a pagina do canal respondeu 200 e nao trouxe videoId nenhum", "PEDIDOS": 1, "URL": url}
    limite = max_alvos if max_alvos is not None else len(ids)
    return {"ALVOS": [{"URL": "https://www.youtube.com/watch?v=%s" % v, "NOME": v, "NATIVE_ID": v}
                      for v in ids[:limite]],
            "ROTA": ROTA_YOUTUBE, "PEDIDOS": 1, "URL": url, "HTML": r.get("BYTES"),
            "IDENTIDADE_CONFERIDA": channel_id, "VIDEOS_NA_PAGINA": len(ids)}


# ══════════════════════════════════════════════════════════════════════════════
# INSTAGRAM — o Reel por URL directa, e a listagem por /embed/ da conta
# ══════════════════════════════════════════════════════════════════════════════
# O QUE O DONO ABRIU, E O QUE CONTINUA FECHADO:
#   D22 (23/09)  REELS do Instagram por URL DIRECTA: autorizados. A conta Business (D19) deixa de ser
#                pre-condicao SO para Reels.
#   D19          a CONTA (listar os posts do perfil) continua POLICY_BLOCK sem conta Business do projeto.
#
# ROTA_LISTAGEM = embed_publico. A pagina publica `/<handle>/embed/` JA foi provada como rota de
# DESCOBERTA de Reels: canario CANARIO-REEL-0f525637 (23/09/2026, commit 233638e3e,
# `data/samples/CANARIO-REELS-INSTAGRAM-V1.json`): PERFIL=bayer_italia, HTTP 200, 3 Reels listados,
# 3 capturados e transcritos, 0 USD, sem login e sem conta. A matriz social
# (`leis/social_matriz.py`, MATRIZ['INSTAGRAM']) declara `instagram_janela.py:embed` PROVED.
# Decisao do coordenador (29/09) nesta missao: usar esta rota — e SO esta — como descoberta de Reels.
#
#     NAO SE LISTA PELO PERFIL LOGADO. NAO SE LISTA POR OUTRA ROTA. ZERO E ZERO LEGITIMO.
ROTA_IG_LISTAGEM = "embed_publico"
ROTA_IG_REEL = "instagram:reel-por-url-directa"
RE_IG_SHORTCODE = re.compile(r"/reel/([A-Za-z0-9_-]{5,})")
RE_IG_HANDLE = re.compile(r"^[A-Za-z0-9._]{1,30}$")


def instagram_reels_da_conta(*, handle, buscar, max_alvos=None):
    """A DESCOBERTA pela pagina publica `/embed/` (D22; canario de 23/09). → {"ALVOS": [...]} ou {"ERRO"}.

    Zero alvos NAO e falha: a conta pode nao ter Reel na pagina de embed. Devolve lista vazia e diz-lo."""
    if not isinstance(handle, str) or not RE_IG_HANDLE.match(handle or ""):
        return {"ERRO": "HANDLE_INVALIDO: %r" % (handle,), "PEDIDOS": 0}
    if not callable(buscar):
        return {"ERRO": "SEM_TRANSPORTE: esta rota nao inventa transporte", "PEDIDOS": 0}
    url = "https://www.instagram.com/%s/embed/" % handle
    r = buscar(url)
    if r.get("ERRO") or r.get("STATUS") != 200:
        return {"ERRO": "a pagina /embed/ da conta nao respondeu 200 (status %s%s)"
                % (r.get("STATUS") or 0, ", " + r["ERRO"] if r.get("ERRO") else ""),
                "PEDIDOS": 1, "URL": url, "ROTA": ROTA_IG_LISTAGEM, "QUEM_DISSE_NAO": r.get("QUEM_DISSE_NAO")}
    html = (r.get("BYTES") or b"").decode("utf-8", "replace")
    codigos = list(dict.fromkeys(RE_IG_SHORTCODE.findall(html)))
    limite = max_alvos if max_alvos is not None else len(codigos)
    return {"ALVOS": [{"URL": "https://www.instagram.com/reel/%s/" % c, "NOME": c, "NATIVE_ID": c,
                       "DESCOBERTO_POR": ROTA_IG_LISTAGEM, "CONTA": handle} for c in codigos[:limite]],
            "ROTA": ROTA_IG_LISTAGEM, "PEDIDOS": 1, "URL": url, "HTML": r.get("BYTES"),
            "REELS_NA_PAGINA": len(codigos)}


def instagram_reel(*, url, buscar):
    """UM Reel por URL DIRECTA (D22). → {"BYTES", "URL", "NATIVE_ID", "ROTA"} ou {"ERRO"}.

    A pagina `/embed/` do PROPRIO Reel e a que o canario de 23/09 usou: e publica, sem login e sem conta."""
    m = RE_IG_SHORTCODE.search(str(url or ""))
    if not m:
        return {"ERRO": "URL_NAO_E_REEL: a D22 abre o REEL por URL directa; %r nao e um /reel/" % (url,),
                "PEDIDOS": 0}
    if not callable(buscar):
        return {"ERRO": "SEM_TRANSPORTE: esta rota nao inventa transporte", "PEDIDOS": 0}
    alvo = "https://www.instagram.com/reel/%s/embed/" % m.group(1)
    r = buscar(alvo)
    if r.get("ERRO") or r.get("STATUS") != 200:
        return {"ERRO": "o Reel nao respondeu 200 (status %s%s)"
                % (r.get("STATUS") or 0, ", " + r["ERRO"] if r.get("ERRO") else ""),
                "PEDIDOS": 1, "URL": alvo, "QUEM_DISSE_NAO": r.get("QUEM_DISSE_NAO")}
    return {"BYTES": r.get("BYTES"), "URL": alvo, "URL_PUBLICA": "https://www.instagram.com/reel/%s/" % m.group(1),
            "NATIVE_ID": m.group(1), "ROTA": ROTA_IG_REEL, "PEDIDOS": 1,
            "CONTENT_TYPE": r.get("CONTENT_TYPE") or "text/html"}


# ══════════════════════════════════════════════════════════════════════════════
# LINKEDIN — SO O PROVADO, e a distincao que mais importa nesta casa
# ══════════════════════════════════════════════════════════════════════════════
# O QUE ESTA PROVADO (matriz social, medida nesta missao):
#   DISCOVER_POST  linkedin:pagina-publica-da-organizacao   PROVED
#   DISCOVER_POST  linkedin:post-publico-de-pessoa          PROVED
#   FETCH_VIDEO_BYTES  linkedin:data-sources-mp4            PROVED
# O QUE NAO ESTA, E CONTINUA FECHADO:
#   FETCH_POST     linkedin:Community Management API        ROUTE_NOT_ALLOWED
#   FETCH_POST     apify:harvestapi~linkedin-*              ROUTE_NOT_ALLOWED  (e a Apify esta fora desta
#                                                            instalacao, por ordem da D155)
#
# ⚠️ A LEITURA QUE ENGANA, E ELA JA ENGANOU:
#
#       FETCH_VIDEO_BYTES = PROVED  significa  O URL DO MP4 E DESCOBRIVEL NO POST PUBLICO.
#       NAO significa                          OS BYTES DO VIDEO FORAM BAIXADOS.
#
# Por isso o que esta linha regista e `URL_MP4_DESCOBERTA` com `VIDEO_BYTES_ACQUIRED=False`. Escrever
# «video coletado» seria contar como adquirido um endereco. O resultado honesto e aceitavel para esta
# campanha e PASS_PARCIAL_COM_CAPACIDADE_DECLARADA.
ROTA_LINKEDIN = "linkedin:pagina-publica-da-organizacao"


def linkedin_posts_da_organizacao(*, pagina_url, run_id, buscar, teto=None, country_scope="IT"):
    """A DESCOBERTA na pagina publica da ORGANIZACAO (D23). Nao adquire byte de midia nenhum.

    → {"CARTOES": [...], "ROTA", "PEDIDOS", "VIDEO_BYTES_ACQUIRED": False} ou {"ERRO"}.
    Recusa ESTATICA (zero rede) para perfil de PESSOA e ecra de login: e `adaptador_linkedin` que a faz,
    e uma proibicao que pergunta ao proibido ja fez um pedido a ele."""
    import adaptador_linkedin as LI                                # noqa: PLC0415
    import scrap_http as http                                      # noqa: PLC0415
    try:
        cartoes, contexto = LI.posts_com_video(pagina_url=pagina_url, run_id=run_id,
                                               country_scope=country_scope, teto=teto,
                                               transporte=buscar)
    except (http.RotaNaoPermitida, ValueError) as ex:
        return {"ERRO": "%s: %s" % (type(ex).__name__, ex), "PEDIDOS": 0, "ROTA": ROTA_LINKEDIN}
    except http.RotaBloqueada as ex:
        return {"ERRO": "ROTA_BLOQUEADA: %s" % ex, "PEDIDOS": 1, "ROTA": ROTA_LINKEDIN,
                "QUEM_DISSE_NAO": "PLATAFORMA"}
    achados = []
    for c in cartoes:
        achados.append({
            "URL_DO_POST": c.get("URL_DO_POST") or c.get("POST_URL"),
            "TEXTO_PUBLICO": c.get("TEXTO") or c.get("CAPTION"),
            # ⚠️ O NOME DIZ O QUE E: um ENDERECO descoberto, nao bytes tidos.
            "URL_MP4_DESCOBERTA": _mp4_do_cartao(c),
            "VIDEO_BYTES_ACQUIRED": False,
            "NATIVE_ID": c.get("ACTIVITY_ID") or c.get("URN"),
        })
    return {"CARTOES": achados, "ROTA": ROTA_LINKEDIN, "PEDIDOS": contexto.get("PEDIDOS_TOTAIS", 1),
            "SLUG": contexto.get("SLUG"), "PAGINA": pagina_url, "VIDEO_BYTES_ACQUIRED": False,
            "FETCH_POST": "ROUTE_NOT_ALLOWED (matriz social; nao se contorna)",
            "CARTOES_COM_VIDEO": contexto.get("CARTOES_COM_VIDEO")}


def _mp4_do_cartao(c):
    """O endereco do MP4 progressivo que o cartao publico declara — ou None. NUNCA baixa nada."""
    for k in ("URL_MP4", "MP4", "VIDEO_URL", "RENDICAO"):
        v = c.get(k)
        if isinstance(v, str) and ".mp4" in v:
            return v
        if isinstance(v, dict) and isinstance(v.get("URL"), str):
            return v["URL"]
    rend = c.get("RENDICOES") or c.get("DATA_SOURCES") or []
    if isinstance(rend, list):
        for r in rend:
            if isinstance(r, dict) and isinstance(r.get("URL") or r.get("src"), str):
                return r.get("URL") or r.get("src")
    return None


# ══════════════════════════════════════════════════════════════════════════════
# A sonda: UM pedido pelo caminho real de cada linha (um processo por rota)
# ══════════════════════════════════════════════════════════════════════════════
def pedir_para_sonda(url: str):
    """UM pedido pela porta destas linhas (`scrap_http.buscar_bytes`), para a sonda de comportamento medir
    a reserva ANTES e a resposta DEPOIS. E o caminho real: as tres rotas acima passam todas por aqui."""
    return transporte()(url)
