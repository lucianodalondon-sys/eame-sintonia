"""SOC-ONDA2 · A RÉGUA DO CANÁRIO SOCIAL — o recibo da corrida do Scrap decide READY.

    py curadoria/regua_social.py --corridas RESULTADOS.json [--banco-raw RAW.json]
    py curadoria/regua_social.py --corridas RESULTADOS.json --aplicar --copia

O canário de uma rota do Scrap (`SCRAP_FASE`) NÃO é do worker: é uma corrida do
orquestrador (`scrap-colheita`), a mesma porta que a onda vai usar (D28). O worker
pára em CANARY_PENDING. Faltava quem LESSE o recibo dessa corrida e dissesse ao
livro o que ele prova — e isso é este ficheiro. Não corre nada; lê.

A RÉGUA (uma fonte, uma corrida da fase do SEU contrato, com o SEU SOURCE_ID):

    READY       o envelope diz RESULT=OK e traz >= 1 item de COLHEITA em que
                cada item tem NATIVE_ID (a identidade da plataforma), PUBLISHED_AT,
                OWNER_AUTHORIZED=SIM e PLATFORM_POLICY_STATUS escrito — e o banco
                da corrida tem >= 1 linha RAW (o bruto foi guardado, não só visto).
    ZERO        RESULT=ZERO_RESULTS: a rota abriu e não havia item público.
                Zero legítimo NÃO é falha nem é prontidão: fica CANARY_PENDING,
                com a prova escrita, para voltar a medir.
    FALHA       o resto (erro, muro de login, item sem identidade, RAW 0 com
                colheita > 0): CONTRACTED_CANARY_FAILED, com o porquê.

    UMA FONTE SOCIAL SÓ É PRONTA QUANDO A PORTA QUE A VAI COLHER A COLHEU.

D53 · A ROTA VIDEO (canal YouTube): além disso, CADA item prova as quatro coisas do
vídeo — a página pública do vídeo (o endereço nomeia o NATIVE_ID), o título, a data
de publicação e o canal do CONTRATO. Falta uma, FALHA com o nome dela. A transcrição
não é exigida nem inventada: só conta se o Scrap a trouxe. Esta régua é o único
juiz da rota YouTube do Curator — o Curator não vai ao YouTube (SEPARAR-A-B, 25/09).

D36 -> SOCIAL-ATE-A-SALA (27/09): quando a fase da corrida nao e a do contrato
(`audio-youtube`, `captura-reel`, `video-linkedin` contra um contrato de outra fase), o
veredito e das PROVAS do item — conta de origem, data de publicacao, OWNER_AUTHORIZED e
a ligacao conta->publicacao->midia (`provas_sociais`) — e NUNCA do nome da fase.

⚠️ O envelope de uma corrida cuja fonte o Atlas não conhece traz COLHEITA 0 com a
razão escrita — isso é FALHA do registo, não ZERO da plataforma, e a régua separa.
⚠️ `--aplicar` recusa a árvore do bot vivo e a ponte viva.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))

VIVOS = ("source-curator-service-v1", "ponte-viva")
READY, ZERO, FALHA = "READY", "ZERO", "FALHA"
CAMPOS_DO_ITEM = ("NATIVE_ID", "PUBLISHED_AT", "OWNER_AUTHORIZED", "PLATFORM_POLICY_STATUS")


RE_LOCALE = re.compile(r"^https?://([a-z]{2,3})\.linkedin\.com/", re.I)
RE_SLUG = re.compile(r"linkedin\.com/(?:company|showcase)/([^/?#]+)", re.I)
RE_PALAVRA = re.compile(r"[a-zà-ú]{4,}", re.I)
VAZIAS = {"linkedin", "ufficiale", "youtube", "canale", "official", "italia", "italy", "della", "delle",
          "degli", "dell", "per", "and", "the"}


def _palavras(t: str) -> set:
    return {w.lower() for w in RE_PALAVRA.findall(t or "")} - VAZIAS


def autor(it: dict) -> tuple[str, str]:
    raw = (it.get("OBSERVACAO") or {}).get("RAW") or {}
    return raw.get("CREATOR_NAME") or "", raw.get("CREATOR_URL") or ""


def conferir_autor(itens: list, slug: str | None, nome_da_fonte: str | None) -> tuple[list, str | None]:
    """→ (itens publicados PELA PROPRIA pagina, divergencia de identidade ou None).

    Medido em 24/09: uma pagina LinkedIn devolve tambem videos REPUBLICADOS de
    outras organizacoes (ASSAM Marche -> «ABC Interreg»); e uma candidata com o
    endereco cortado no registo («company/societ») apontava para uma empresa do
    CANADA. Nome parecido nunca PROVA identidade (D21) — mas nome que nao partilha
    uma unica palavra com a fonte, ou uma pagina servida de outro pais, e sinal
    bastante para parar e chamar um humano. Parar e barato; colher a empresa
    errada e caro.
    """
    if not slug:
        return itens, None
    proprios = []
    for it in itens:
        nome, url = autor(it)
        m = RE_SLUG.search(url)
        if m and m.group(1).lower().rstrip("/") == slug.lower():
            proprios.append(it)
    if not proprios:
        return [], None
    nome, url = autor(proprios[0])
    loc = RE_LOCALE.match(url)
    if loc and loc.group(1).lower() not in ("it", "www"):
        return proprios, "a pagina serve-se como %s.linkedin.com (%s): outro pais?" % (loc.group(1), nome)
    if nome_da_fonte and not (_palavras(nome) & _palavras(nome_da_fonte)):
        return proprios, "quem publica chama-se «%s» e a fonte «%s»: nenhuma palavra em comum" % (
            nome, nome_da_fonte[:60])
    return proprios, None


def _resultado(env: dict) -> str | None:
    for s in env.get("SUPORTE") or []:
        if s.get("ESPECIE") == "RUN_RECEIPT":
            return (s.get("RESUMO") or {}).get("RESULT")
    return None


# --- D36 -> SOCIAL-ATE-A-SALA · A FASE DIFERENTE JULGA-SE PELAS PROVAS DO ITEM ------
# O contrato pede uma fase e a corrida declara outra. A D36 (bot Luciano, 25/09 02:20)
# aceitou UM par enumerado (canal-youtube <- audio-youtube) com quatro provas no item.
# A missao SOCIAL-ATE-A-SALA (coordenador, 27/09, sobre a decisao delegada) generaliza
# a regra e tira-lhe o NOME: um envelope de `audio-youtube`, `captura-reel` ou
# `video-linkedin` (ou de outra fase qualquer) satisfaz o contrato SO quando cada item
# prova as quatro coisas — e reprova, dizendo qual, quando falta uma.
#
#     NUNCA PELO NOME DA FASE. Nem para passar, nem para reprovar.
#
# (b) continua recusada pelo dono: uma lista de contas nao e uma observacao delas — e
# uma lista nao traz midia, por isso reprova na 4.a prova, sem precisar do nome.
PROVAS_SOCIAIS = (
    "CONTA_DE_ORIGEM",                 # 1. de que canal/conta veio
    "DATA_DE_PUBLICACAO",              # 2. quando foi publicado (com precisao declarada)
    "AUTORIZACAO_DO_DONO",             # 3. OWNER_AUTHORIZED=SIM (D17.4/D22-D24/D106)
    "LIGACAO_CONTA_PUBLICACAO_MIDIA",  # 4. conta -> publicacao -> midia, no MESMO item
)
# O YouTube conserva os nomes da D36 (quem ja os le continua a le-los): e o CONTRATO que
# diz qual e a conta (CHANNEL_ID), e nunca a fase da corrida.
NOMES_DO_YOUTUBE = {"CONTA_DE_ORIGEM": "CANAL_DE_ORIGEM",
                    "LIGACAO_CONTA_PUBLICACAO_MIDIA": "LIGACAO_CANAL_VIDEO_AUDIO"}

# Onde cada adaptador do Scrap escreve cada facto — lidos, nunca derivados:
#   · `adaptador_youtube.youtube_audio_publico`  CHANNEL_ID, SOURCE_URL, AUDIO_SHA256/BYTES/REFERENCE
#   · `reel_transcricao.transcrever_reel`        REEL.{POST_ID, ACCOUNT_*, PUBLISHED_AT, SOURCE_URL},
#                                                RAW.{SHA256, BYTES, STORAGE_LOCATION}
#   · `adaptador_linkedin._adquirir_um`          NATIVE_ID, URL, RAW.{CREATOR_URL, VIDEO_SHA256,
#                                                VIDEO_BYTES, VIDEO_STORAGE_LOCATION}
# A conta le-se SO nos campos que o dono da plataforma declara como conta de origem (o
# YouTube nos da D36: CHANNEL_ID/CHANNEL_URL do bloco A; o bruto nao conta como prova).
CAMPOS_DA_CONTA = {
    "YOUTUBE": ("CHANNEL_ID", "CHANNEL_URL"),
    "LINKEDIN": ("RAW.CREATOR_URL",),
    "INSTAGRAM": ("REEL.ACCOUNT_ID", "REEL.ACCOUNT_URL", "REEL.ACCOUNT_HANDLE_FROM_URL",
                  "ACCOUNT_ID", "ACCOUNT_URL"),
}
CAMPOS_DA_PUBLICACAO = ("NATIVE_ID", "REEL.POST_ID", "RAW.ACTIVITY_ID")
CAMPOS_DA_PAGINA = ("URL", "SOURCE_URL", "PARENT.SOURCE_URL", "REEL.SOURCE_URL", "RAW.POST_URL")
CAMPOS_DA_DATA = ("PUBLISHED_AT", "REEL.PUBLISHED_AT", "RAW.PUBLISHED_AT")
CAMPOS_DA_PRECISAO = ("PUBLISHED_AT_PRECISION", "REEL.PUBLISHED_AT_PRECISION", "RAW.PUBLISHED_AT_PRECISION")
CAMPOS_DA_AUTORIZACAO = ("OWNER_AUTHORIZED", "RAW.OWNER_AUTHORIZED")
CAMPOS_DA_POLITICA = ("PLATFORM_POLICY_STATUS", "RAW.PLATFORM_POLICY_STATUS")
# (sha256, bytes, onde ficou) — o par vem SEMPRE do mesmo dono; nunca se mistura um sha
# de um sitio com o tamanho de outro.
MIDIAS = (("AUDIO_SHA256", "AUDIO_BYTES", "AUDIO_REFERENCE"),
          ("RAW.VIDEO_SHA256", "RAW.VIDEO_BYTES", "RAW.VIDEO_STORAGE_LOCATION"),
          ("RAW.SHA256", "RAW.BYTES", "RAW.STORAGE_LOCATION"))
# As confissoes de ausencia nos dialectos dos donos (a camada do Reel escreve NOT_KNOWN).
AUSENTES_DO_SCRAP = ("", "NAO SEI", "NAO_SEI", "UNKNOWN", "NOT_KNOWN")
RE_HANDLE_IG = re.compile(r"instagram\.com/([A-Za-z0-9_.]+)", re.I)
RE_CANAL_YT = re.compile(r"youtube\.com/channel/(UC[A-Za-z0-9_-]{22})", re.I)


def _valor(ob: dict, caminho: str):
    """O valor em `A.B` (dicionarios aninhados), ou None quando e uma confissao de ausencia."""
    v = ob
    for parte in caminho.split("."):
        if not isinstance(v, dict):
            return None
        v = v.get(parte)
    return None if v is None or str(v).strip() in AUSENTES_DO_SCRAP else v


def _primeiro(ob: dict, caminhos) -> object:
    for c in caminhos:
        v = _valor(ob, c)
        if v is not None:
            return v
    return None


def conta_do_contrato(contrato: dict | None) -> tuple[str | None, str | None]:
    """→ (especie, valor) da conta que o CONTRATO nomeia. O item prova-se contra isto."""
    aq = (contrato or {}).get("ACQUISITION") or {}
    if aq.get("CHANNEL_ID"):
        return "YOUTUBE", str(aq["CHANNEL_ID"])
    if aq.get("LINKEDIN_SLUG"):
        return "LINKEDIN", str(aq["LINKEDIN_SLUG"]).lower().rstrip("/")
    if aq.get("INSTAGRAM_HANDLE"):
        return "INSTAGRAM", str(aq["INSTAGRAM_HANDLE"]).lower().lstrip("@").rstrip("/")
    return None, None


def _contas_do_item(ob: dict, especie: str | None) -> set[str]:
    """As identidades de conta que o item DECLARA, na forma da especie do contrato."""
    out = set()
    campos = CAMPOS_DA_CONTA.get(especie) or tuple(c for cs in CAMPOS_DA_CONTA.values() for c in cs)
    for c in campos:
        v = _valor(ob, c)
        if v is None:
            continue
        s = str(v).strip()
        if especie == "YOUTUBE":
            m = RE_CANAL_YT.search(s)
            out.add(m.group(1) if m else s)
        elif especie == "LINKEDIN":
            m = RE_SLUG.search(s)
            if m:
                out.add(m.group(1).lower().rstrip("/"))
        elif especie == "INSTAGRAM":
            m = RE_HANDLE_IG.search(s)
            out.add((m.group(1) if m else s.lstrip("@")).lower().rstrip("/"))
        else:
            out.add(s)
    return out


def provas_sociais(ob: dict, contrato: dict | None) -> list[str]:
    """As provas de PROVAS_SOCIAIS que FALTAM neste item. Lista vazia = provado.

    Le o item e o contrato. Nao recebe a fase — e por isso nao a pode usar.
    """
    especie, conta = conta_do_contrato(contrato)
    nome = (lambda p: NOMES_DO_YOUTUBE.get(p, p)) if especie == "YOUTUBE" else (lambda p: p)
    lig = nome("LIGACAO_CONTA_PUBLICACAO_MIDIA")
    falta = []
    contas = _contas_do_item(ob, especie)
    if not contas:
        falta.append("%s (o item nao diz de que canal/conta veio)" % nome("CONTA_DE_ORIGEM"))
    pub = _primeiro(ob, CAMPOS_DA_DATA)
    if pub is None:
        falta.append("DATA_DE_PUBLICACAO (sem PUBLISHED_AT)")
    elif _primeiro(ob, CAMPOS_DA_PRECISAO) is None:
        falta.append("DATA_DE_PUBLICACAO (data sem precisao declarada)")
    if _primeiro(ob, CAMPOS_DA_AUTORIZACAO) != "SIM":
        falta.append("AUTORIZACAO_DO_DONO (OWNER_AUTHORIZED != SIM)")
    # 4 · conta -> publicacao -> midia
    if not conta:
        falta.append("%s (o contrato nao declara %s)" % (
            lig, "CHANNEL_ID" if especie in (None, "YOUTUBE") else "a conta"))
    elif contas and contas != {conta}:
        falta.append("%s (conta %s != %r do contrato)" % (lig, sorted(contas), conta))
    pubid = _primeiro(ob, CAMPOS_DA_PUBLICACAO)
    if pubid is None:
        falta.append("%s (sem a publicacao, NATIVE_ID)" % lig)
    else:
        pagina = _primeiro(ob, CAMPOS_DA_PAGINA)
        if pagina is None or str(pubid) not in str(pagina):
            falta.append("%s (a pagina da publicacao nao nomeia %s)" % (lig, pubid))
    midia = next(((s, b, r) for s, b, r in MIDIAS
                  if _valor(ob, s) and isinstance(_valor(ob, b), (int, float)) and _valor(ob, b) > 0), None)
    if midia is None:
        falta.append("%s (sem a midia adquirida: sha256 + bytes)" % lig)
    elif pubid is not None and str(pubid) not in str(_valor(ob, midia[2]) or ""):
        falta.append("%s (%s)" % (lig, "o audio guardado nao nomeia o video" if especie == "YOUTUBE"
                                  else "a midia guardada nao nomeia a publicacao"))
    return falta


def provas_da_equivalencia(env: dict, fase: str, contrato: dict | None) -> list[str]:
    """As provas que FALTAM para este envelope poder satisfazer a fase do contrato.

    Lista vazia = provado. `fase` fica na assinatura (quem ja chama continua a chamar),
    mas nada aqui a compara com a do envelope: o veredito e do item e do contrato.
    """
    itens = env.get("COLHEITA") if isinstance(env.get("COLHEITA"), list) else []
    if not itens:
        return ["COLHEITA_VAZIA"]
    falta = []
    for i, it in enumerate(itens):
        falta += ["item %d: %s" % (i, f) for f in provas_sociais(it.get("OBSERVACAO") or {}, contrato)]
    return falta


# --- D53 · A ROTA VIDEO: AS QUATRO PROVAS DO VIDEO, NO ITEM QUE O SCRAP TROUXE -------
# O dono da rota YouTube e o Scrap (fase `canal-youtube`, `rota_do_scrap_youtube`); o
# Curator nao busca paginas do YouTube, le o recibo. A prova minima da D53 le-se nos
# campos que os adaptadores do Scrap ja escrevem — com os nomes de cada um deles:
#   · `youtube_oficial.uploads_recentes`  URL, TITLE, SOURCE_ACCOUNT, RAW.CHANNEL_ID
#   · `adaptador_youtube` (audio publico) SOURCE_URL, RAW.TITLE, CHANNEL_ID
FASES_VIDEO = frozenset({"canal-youtube"})
PROVAS_DO_VIDEO = ("PAGINA_DO_VIDEO", "TITULO", "DATA_DE_PUBLICACAO", "CANAL")
RE_ID_DO_VIDEO = re.compile(r"^[A-Za-z0-9_-]{11}$")
# A API devolve estes titulos no lugar de um video que ja nao e publico.
TITULOS_SEM_VIDEO = frozenset({"private video", "deleted video"})
AUSENTE = ("", "NAO SEI", "UNKNOWN")


def _pagina_do_video(ob: dict) -> str:
    return str(ob.get("URL") or ob.get("SOURCE_URL") or (ob.get("PARENT") or {}).get("SOURCE_URL") or "")


def _nomeia_o_video(url: str, vid: str) -> bool:
    return bool(re.match(r"^https://(www\.|m\.)?youtube\.com/(watch\?v=%s(&|$)|shorts/%s([/?]|$))|"
                         r"^https://youtu\.be/%s([/?]|$)" % ((re.escape(vid),) * 3), url))


def provas_do_video(ob: dict, canal_do_contrato: str | None) -> list[str]:
    """As provas da D53 que FALTAM neste item. Lista vazia = o video esta provado."""
    raw = ob.get("RAW") or {}
    falta = []
    vid = str(ob.get("NATIVE_ID") or "")
    if not RE_ID_DO_VIDEO.match(vid) or not _nomeia_o_video(_pagina_do_video(ob), vid):
        falta.append("PAGINA_DO_VIDEO")
    titulo = str(ob.get("TITLE") or raw.get("TITLE") or "").strip()
    if titulo in AUSENTE or titulo.lower() in TITULOS_SEM_VIDEO:
        falta.append("TITULO")
    if str(ob.get("PUBLISHED_AT") or "") in AUSENTE:
        falta.append("DATA_DE_PUBLICACAO")
    canal = ob.get("CHANNEL_ID") or raw.get("CHANNEL_ID") or ob.get("SOURCE_ACCOUNT")
    if not canal_do_contrato or canal != canal_do_contrato:
        falta.append("CANAL")
    return falta


# Cada campo de CAMPOS_DO_ITEM, nos sitios onde os donos o escrevem (o primeiro e o de sempre).
ONDE_ESTA = {"NATIVE_ID": CAMPOS_DA_PUBLICACAO, "PUBLISHED_AT": CAMPOS_DA_DATA,
             "OWNER_AUTHORIZED": CAMPOS_DA_AUTORIZACAO, "PLATFORM_POLICY_STATUS": CAMPOS_DA_POLITICA}



def _campo_do_item(ob: dict, k: str):
    """O campo no topo, com a semantica de sempre; so quando o topo NAO o tem, nos sitios
    onde o dono da plataforma o escreve (o Reel guarda-o em REEL.*, o LinkedIn em RAW.*)."""
    if k in ob:
        v = ob.get(k)
        return None if not v or v == "NAO SEI" else v
    return _primeiro(ob, ONDE_ESTA[k][1:])


def julgar(env: dict, sid: str, fase: str, raw_no_banco: int | None,
           slug: str | None = None, nome_da_fonte: str | None = None,
           contrato: dict | None = None) -> tuple[str, str]:
    """→ (READY | ZERO | FALHA, porquê). Puro: sem disco, sem rede.

    D36 + SOCIAL-ATE-A-SALA: a fase declarada pela corrida pode satisfazer a fase do
    contrato SO com as quatro provas (`PROVAS_SOCIAIS`) em cada item — conta de origem,
    data de publicacao, autorizacao do dono e a ligacao conta->publicacao->midia. O nome
    da fase nunca decide: falta uma prova, reprova com o nome dela.
    """
    if env.get("SOURCE_ID_DO_PEDIDO") != sid:
        return FALHA, "o envelope e de %r, nao de %s" % (env.get("SOURCE_ID_DO_PEDIDO"), sid)
    if env.get("FASE") != fase:
        falta = provas_da_equivalencia(env, fase, contrato)
        if falta:
            return FALHA, ("o envelope e da fase %r e o contrato pede %s; o item nao prova: %s"
                           % (env.get("FASE"), fase, "; ".join(falta[:6])))

    res = _resultado(env)
    col = env.get("COLHEITA")
    itens = col if isinstance(col, list) else []
    if not itens:
        if env.get("PORQUE_ZERO_COLHEITA", "").startswith("o pedido nomeou uma fonte que o atlas"):
            return FALHA, "o Atlas nao conhece %s: a corrida nao pode ancorar nada" % sid
        if res == "ZERO_RESULTS":
            return ZERO, "a rota abriu e nao havia item publico (ZERO_RESULTS): zero legitimo, nao prontidao"
        return FALHA, "colheita vazia com RESULT=%s: %s" % (res, (env.get("PORQUE_ZERO_COLHEITA") or "")[:120])
    if res != "OK":
        return FALHA, "colheita com RESULT=%s" % res
    for i, it in enumerate(itens):
        ob = it.get("OBSERVACAO") or {}
        falta = [k for k in CAMPOS_DO_ITEM if _campo_do_item(ob, k) is None]
        if falta:
            return FALHA, "item %d sem %s" % (i, ", ".join(falta))
        if _campo_do_item(ob, "OWNER_AUTHORIZED") != "SIM":
            return FALHA, "item %d sem autorizacao do dono escrita" % i
    if fase in FASES_VIDEO:
        canal = ((contrato or {}).get("ACQUISITION") or {}).get("CHANNEL_ID")
        for i, it in enumerate(itens):
            falta = provas_do_video(it.get("OBSERVACAO") or {}, canal)
            if falta:
                return FALHA, "D53: o item %d nao prova %s (video %r)" % (
                    i, ", ".join(falta), (it.get("OBSERVACAO") or {}).get("NATIVE_ID"))
    proprios, diverge = conferir_autor(itens, slug, nome_da_fonte)
    if not proprios:
        return FALHA, ("%d itens e NENHUM publicado pela propria pagina (%s): republicacoes de "
                       "outras organizacoes nao provam a fonte" % (len(itens), slug))
    if diverge:
        return FALHA, "IDENTIDADE A CONFERIR POR HUMANO: " + diverge
    if not raw_no_banco:
        return FALHA, "%d itens vistos e 0 linhas RAW no banco da corrida: visto nao e guardado" % len(itens)
    video = ("; D53: cada video com pagina, titulo, data e canal (transcricao nao exigida)"
             if fase in FASES_VIDEO else "")
    return READY, ("canario do Scrap (%s): %d itens (%d da propria pagina) com identidade da "
                   "plataforma e data, autorizacao do dono e politica escritas; %d linhas RAW no banco%s"
                   % (fase, len(itens), len(proprios), raw_no_banco, video))


def fase_do_contrato(c: dict) -> str | None:
    """A fase que a régua exige é a do CONTRATO da fonte, nunca a que a corrida
    declara de si própria. Medido em 24/09: comparar com a fase da corrida deixava
    passar um canário de `audio-youtube` para um contrato de `canal-youtube`."""
    return (c.get("ACQUISITION") or {}).get("FASE")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corridas", required=True, help="resultados.json do canario (SOURCE_ID, FASE, RUN_ID, MEDIDA.RAW)")
    ap.add_argument("--envelopes", default=str(RAIZ / "data" / "colheita" / "scrap"))
    ap.add_argument("--aplicar", action="store_true")
    ap.add_argument("--copia", action="store_true")
    ap.add_argument("--vivo", action="store_true",
                    help="aplicar no vivo: so com o bot parado (curadoria/PARAR.flag presente)")
    ap.add_argument("--json")
    a = ap.parse_args()
    corridas = json.loads(Path(a.corridas).read_text(encoding="utf-8"))
    contratos = {c["SOURCE_ID"]: c for c in json.loads(
        (RAIZ / "curadoria" / "italy_contracts_curator.json").read_text(encoding="utf-8"))["FONTES"]}
    linhas = []
    for x in corridas.values():
        env_p = Path(a.envelopes) / str(x.get("RUN_ID")) / "ENVELOPE.json"
        env = json.loads(env_p.read_text(encoding="utf-8")) if env_p.exists() else {}
        med = x.get("MEDIDA") if isinstance(x.get("MEDIDA"), dict) else {}
        c = contratos.get(x["SOURCE_ID"]) or {}
        slug = (c.get("ACQUISITION") or {}).get("LINKEDIN_SLUG")
        v, porque = julgar(env, x["SOURCE_ID"], fase_do_contrato(c),
                           len(med.get("RAW") or []) if med else None,
                           slug=slug, nome_da_fonte=c.get("NAME"), contrato=c)
        linhas.append({"SOURCE_ID": x["SOURCE_ID"], "FASE": fase_do_contrato(c),
                       "FASE_DA_CORRIDA": x.get("FASE"), "RUN_ID": x.get("RUN_ID"),
                       "VEREDITO": v, "PORQUE": porque})
    print(dict(Counter(l["VEREDITO"] for l in linhas)))
    if a.aplicar:
        no_vivo = any(v in str(RAIZ).replace("\\", "/") for v in VIVOS)
        parado = (RAIZ / "curadoria" / "PARAR.flag").exists()
        if no_vivo and not (a.vivo and parado):
            print("RECUSADO: no vivo so com --vivo E o bot parado (curadoria/PARAR.flag)")
            return 2
        if not no_vivo and not a.copia:
            print("RECUSADO: fora do vivo, declare --copia")
            return 2
        import lifecycle as LC
        import worker as W
        for l in linhas:
            sid = l["SOURCE_ID"]
            ref = W._guardar_evidencia(sid, "CANARY_SOCIAL", l)
            de = LC.estado_de(sid)
            if l["VEREDITO"] == READY and de in LC.PODEM_PROMOVER:
                LC.registar(sid, LC.READY_FOR_COLLECTION, l["PORQUE"][:200], evidence_ref=ref)
            elif l["VEREDITO"] == FALHA and de != LC.CONTRACTED_CANARY_FAILED:
                LC.registar(sid, LC.CONTRACTED_CANARY_FAILED, l["PORQUE"][:200], evidence_ref=ref)
            l["ESTADO_DEPOIS"] = LC.estado_de(sid)
        print("estados depois:", dict(Counter(l["ESTADO_DEPOIS"] for l in linhas)))
    if a.json:
        Path(a.json).write_text(json.dumps({"DATASET": "SOC-ONDA2-REGUA-SOCIAL-V1", "LINHAS": linhas},
                                           ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
