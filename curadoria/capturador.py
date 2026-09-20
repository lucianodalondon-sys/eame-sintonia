#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O CAPTURADOR DE REAL_EXAMPLE — a menor capacidade reutilizavel do Source Curator.

    UMA CANDIDATA NAO VIRA FONTE POR RESPONDER.
    VIRA FONTE QUANDO ALGUEM ABRIU UM ITEM DELA E GUARDOU A PROVA.

POR QUE ISTO EXISTE
-------------------
Medido em 2026-09-20: as 241 candidatas da fila italiana foram TODAS decididas
em 15/09 por `candidatas/decidir_fila_italia.py`, e TODAS pararam no mesmo
degrau, pela mesma razao, escrita uma vez so nesse ficheiro:

    O_QUE_FALTA = EXEMPLO_REAL_DO_ITEM      241 / 241

A sonda de 14/09 abriu o endereco de entrada, leu o titulo da pagina e parou.

    «O ENDERECO RESPONDE» NAO E «A FONTE ENTREGA ISTO».

Este ficheiro fecha exactamente esse buraco, e nada mais.

O QUE ELE NAO E
---------------
NAO e um coletor. Nao cunha RUN_ID, nao escreve no collection-store, nao
produz RAW_OBSERVATION, nao entra no ingresso e nao chega perto da Admission.
Guarda UM item por candidata, como EVIDENCIA SOBRE A FONTE.

    REAL_EXAMPLE != FACT.
    E prova de que a fonte entrega alguma coisa — nao prova do que essa coisa diz.

Por isso ele tambem nao escreve `FACT_TIME` nem `FACT_LOCATION`: a data que ele
le e a data VISIVEL no item (`SOURCE_DATE`), que e outra coisa (COL-LAW da casa:
SOURCE_LOCATION != FACT_LOCATION, e data de publicacao != tempo do facto).

A REGUA NAO FOI INVENTADA AQUI
-------------------------------
Os oito campos vem, textualmente, de `decidir_fila_italia.py::FALTA_O_ITEM`:

    «endereco proprio do item, tipo, titulo, HTTP, content-type, bytes e data
     visivel» + SHA256 (o formato MANIFEST.json das 140 ja registadas)

Reutilizar a regua existente e o ponto: uma segunda regua faria as fontes novas
entrarem no Atlas com um criterio diferente das que la estao.

⚠️ E NAO SE PROMOVE NADA AQUI
------------------------------
Este ficheiro NAO escreve em `candidatas/FONTES-CANDIDATAS.json`. Ele produz
uma PROPOSTA, num ficheiro proprio. Quem transiciona e
`decidir_fila_italia.py --escrever`, e essa e uma missao a seguir.

    CAPTURAR != QUALIFICAR != PROMOVER.
"""
from __future__ import annotations

import hashlib
import json
import re
import ssl
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse

CONTRATO = "CAPTURADOR_DE_REAL_EXAMPLE/v1"

RAIZ = Path(__file__).resolve().parents[1]
EVIDENCIA = RAIZ / "curadoria" / "evidencia"

TIMEOUT = 25
MAX_BYTES = 12 * 1024 * 1024          # 12 MB: e uma amostra, nao um acervo

# ⚠️ ESTE USER-AGENT E DELIBERADAMENTE INCOMPLETO, E ISSO ESTA MEDIDO.
# Um UA de Chrome completo — com `Safari/537.36` no fim — faz o Facebook
# devolver `HTTP 400` em TODAS as paginas, inclusive nas que existem:
#
#     facebook.com/Meta   UA completo -> 400      UA sem `Safari/...` -> 200
#     facebook.com/zuck   curl simples -> 200
#
# Sem esta medicao, as 20 candidatas Facebook sairiam todas «HTTP_ERROR» e
# alguem concluiria que a superficie publica esta fechada. Estava aberta; o
# defeito era do cliente.
#
#     UM «400» UNIFORME EM TODA UMA PLATAFORMA ACUSA O CLIENTE,
#     NAO A PLATAFORMA. Antes de culpar a fonte, provar com um controlo
#     conhecido-bom — e foi `facebook.com/Meta` que devolveu o veredito.
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0"

# ─────────────────────────────────────────────────────────────────────────
# AS FAMILIAS — derivadas do que a fila TEM, nao de uma taxonomia imaginada
# ─────────────────────────────────────────────────────────────────────────
# ⚠️ A familia decide a ESTRATEGIA de captura, nao o veredito. Duas fontes da
# mesma familia podem acabar uma PROMOTE e outra BLOCK.
FAMILIAS = {
    "HTML_SITE":  "site proprio: ler a entrada, achar um item interno com data",
    "DIRECT_PDF": "o proprio endereco ja e o documento",
    "YOUTUBE":    "canal: resolver channelId e ler o feed RSS publico",
    "FACEBOOK":   "pagina: superficie publica, sem sessao",
    "LINKEDIN":   "POLICY_BLOCK — nao se toca",
    "INSTAGRAM":  "POLICY_BLOCK — nao se toca",
}

# ⚠️ ESTAS DUAS NAO SE TOCAM, E A LISTA E EXPLICITA DE PROPOSITO.
# Medido pelo COORDINATOR: LINKEDIN_BIG_COLLECTION_ELIGIBLE = 0 e
# INSTAGRAM_REMOTE_COLLECTION_ALLOWED = 0. O Bot de Fontes nao relaxa policy:
# bloqueia, escreve porque, e segue para a proxima.
POLICY_BLOCKED = {"linkedin.com", "instagram.com"}

# Enderecos para onde uma plataforma atira quem nao esta autenticado.
# Copiado de decidir_fila_italia.py — mesma lei, mesmo padrao.
MURO_DE_LOGIN = re.compile(
    r"(?:linkedin\.com/(?:uas/)?login"
    r"|facebook\.com/(?:login|checkpoint)"
    r"|instagram\.com/accounts/login"
    r"|/login[/?]?$|/signin[/?]?$)", re.I)

# ⚠️ CLASSES DE FALHA SEPARADAS: «nao li» NUNCA vira «nao serve».
FALHAS = {
    "HTTP_ERROR":        "o servidor respondeu com erro",
    "TIMEOUT":           "nao respondeu a tempo",
    "DNS_OR_CONN":       "nao se chegou la deste egresso — pode ser a rede, nao a fonte",
    "TLS":               "certificado/handshake — a fonte pode estar viva",
    "WALL":              "muro de login/consentimento no lugar do conteudo",
    "NO_ITEM_FOUND":     "a entrada respondeu, e nao se achou um item interno",
    "EMPTY_BODY":        "respondeu 200 e o corpo nao tem conteudo",
    "POLICY":            "politica proibe — nao se tentou, de proposito",
    "TOO_LARGE":         "acima do limite de amostra",
}


# ─────────────────────────────────────────────────────────────────────────
def agora() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def dominio(url: str) -> str:
    try:
        h = (urlparse(url).hostname or "").lower()
        return h[4:] if h.startswith("www.") else h
    except Exception:
        return ""


def familia_de(url: str) -> str:
    d = dominio(url)
    if "linkedin.com" in d:
        return "LINKEDIN"
    if "instagram.com" in d:
        return "INSTAGRAM"
    if "youtube.com" in d or "youtu.be" in d:
        return "YOUTUBE"
    if "facebook.com" in d:
        return "FACEBOOK"
    if url.lower().split("?")[0].endswith(".pdf"):
        return "DIRECT_PDF"
    return "HTML_SITE"


def assinatura(b: bytes) -> str:
    """O QUE OS BYTES SAO, e nao o que o cabecalho diz que sao.

    ⚠️ Content-Type mente. Um PDF servido como text/html continua PDF, e um
    HTML de erro servido como application/pdf continua HTML. Quem decide sao
    os primeiros bytes.
    """
    if b[:4] == b"%PDF":
        return "PDF"
    if b[:5].lower() in (b"<?xml",) or b[:5].lower().startswith(b"<?xm"):
        return "XML"
    low = b[:600].lower()
    if b"<html" in low or b"<!doctype html" in low:
        return "HTML"
    if b[:1] in (b"{", b"["):
        return "JSON"
    if b[:2] == b"PK":
        return "ZIP_OU_OFFICE"
    try:
        b[:2000].decode("utf-8")
        return "TEXTO"
    except Exception:
        return "BINARIO"


class _Titulo(HTMLParser):
    def __init__(self):
        super().__init__()
        self.titulo, self._on = "", False

    def handle_starttag(self, tag, attrs):
        if tag == "title":
            self._on = True
        if tag == "meta" and not self.titulo:
            a = dict(attrs)
            if a.get("property") in ("og:title",) and a.get("content"):
                self.titulo = a["content"].strip()

    def handle_endtag(self, tag):
        if tag == "title":
            self._on = False

    def handle_data(self, data):
        if self._on and not self.titulo:
            self.titulo = data.strip()


def titulo_de(corpo: bytes) -> str:
    try:
        p = _Titulo()
        p.feed(corpo.decode("utf-8", "replace")[:200000])
        return (p.titulo or "")[:200]
    except Exception:
        return ""


# Datas visiveis, em ordem de confianca: a declarada pelo documento vence a
# que aparece solta no texto.
_DATAS = [
    re.compile(rb'<meta[^>]+(?:article:published_time|datePublished|dc\.date)[^>]+content="([^"]{8,30})"', re.I),
    re.compile(rb'"datePublished"\s*:\s*"([^"]{8,30})"', re.I),
    re.compile(rb'<time[^>]+datetime="([^"]{8,30})"', re.I),
    re.compile(rb'(\d{4}-\d{2}-\d{2})'),
    re.compile(rb'(\d{2}[/-]\d{2}[/-]\d{4})'),
]


def data_visivel(corpo: bytes) -> str:
    for rx in _DATAS:
        m = rx.search(corpo[:400000])
        if m:
            try:
                return m.group(1).decode("utf-8", "replace")[:30]
            except Exception:
                continue
    return "NAO SEI"


def buscar(url: str, aceita: str = "*/*") -> dict:
    """UM pedido HTTP. Devolve sempre um dicionario — nunca levanta.

    ⚠️ CADA MODO DE FALHAR TEM NOME PROPRIO. Achatar tudo em «falhou» faz uma
    fonte viva atras de um certificado expirado parecer uma fonte morta.
    """
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": aceita,
        "Accept-Language": "it-IT,it;q=0.9,en;q=0.6",
    })
    ctx = ssl.create_default_context()
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT, context=ctx) as r:
            corpo = r.read(MAX_BYTES + 1)
            excedeu = len(corpo) > MAX_BYTES
            corpo = corpo[:MAX_BYTES]
            return {"OK": True, "STATUS": r.status, "FINAL_URL": r.geturl(),
                    "CONTENT_TYPE": (r.headers.get("Content-Type") or "").split(";")[0].strip(),
                    "BYTES": len(corpo), "CORPO": corpo,
                    "FALHA": "TOO_LARGE" if excedeu else None}
    except urllib.error.HTTPError as e:
        try:
            corpo = e.read(200000)
        except Exception:
            corpo = b""
        return {"OK": False, "STATUS": e.code, "FINAL_URL": url,
                "CONTENT_TYPE": (e.headers.get("Content-Type") or "").split(";")[0].strip() if e.headers else "",
                "BYTES": len(corpo), "CORPO": corpo, "FALHA": "HTTP_ERROR"}
    except urllib.error.URLError as e:
        r = str(e.reason)
        cls = "TLS" if ("CERTIFICATE" in r.upper() or "SSL" in r.upper()) else (
            "TIMEOUT" if "timed out" in r.lower() else "DNS_OR_CONN")
        return {"OK": False, "STATUS": None, "FINAL_URL": url, "CONTENT_TYPE": "",
                "BYTES": 0, "CORPO": b"", "FALHA": cls, "DETALHE": r[:160]}
    except Exception as e:                                   # socket.timeout et al
        cls = "TIMEOUT" if "timed out" in str(e).lower() else "DNS_OR_CONN"
        return {"OK": False, "STATUS": None, "FINAL_URL": url, "CONTENT_TYPE": "",
                "BYTES": 0, "CORPO": b"", "FALHA": cls, "DETALHE": str(e)[:160]}


# ─────────────────────────────────────────────────────────────────────────
# ACHAR UM ITEM — a parte que distingue «a loja existe» de «a loja vende isto»
# ─────────────────────────────────────────────────────────────────────────
_HREF = re.compile(rb'href=["\']([^"\'#>]{4,400})["\']', re.I)

# Um item tem cara de item: PDF, ou um caminho com data/noticia/boletim.
_CARA_DE_ITEM = re.compile(
    r"(\.pdf$|/\d{4}/\d{2}/|/20\d\d[-/]|notizie|news|comunicat|bollettin|bolletin"
    r"|avvisi|pubblicazion|document|allegat|circolar|delibera|rapport|report"
    r"|articolo|article|post/|/p/\d|dettaglio|scheda)", re.I)

# ⚠️ E UM INDICE TAMBEM TEM. Esta e a armadilha que apanhou a primeira corrida:
# `/notizie` e `/newsdipartimenti/` casam `_CARA_DE_ITEM` e NAO sao itens — sao
# outra listagem. Guardar uma delas como REAL_EXAMPLE repetiria exactamente o
# defeito da sonda de 14/09 que esta missao existe para corrigir:
#
#     «O ENDERECO RESPONDE» NAO E «A FONTE ENTREGA ISTO»,
#     e uma LISTAGEM de itens nao e um ITEM.
#
# Um item identifica-se a si proprio: PDF, ou um slug com corpo (>=3 segmentos
# de palavra ou um id numerico). Um indice e um substantivo solto no caminho.
_SO_INDICE = re.compile(
    r"/(notizie|news|newsdipartimenti|comunicati|comunicati-stampa|bollettini"
    r"|avvisi|pubblicazioni|documenti|rapporti|report|articoli|archivio"
    r"|elenco|lista|media|press|stampa)/?$", re.I)


def parece_item(url: str) -> bool:
    """DISTINGUE UM ITEM DE UMA LISTAGEM. O `True` aqui e caro: ele autoriza
    gravar a amostra que vai sustentar uma promocao no Atlas."""
    limpo = url.split("?")[0].split("#")[0]
    if limpo.lower().endswith(".pdf"):
        return True                                  # um PDF e sempre um documento
    if _SO_INDICE.search(limpo):
        return False                                 # substantivo solto = indice
    cauda = [s for s in limpo.rstrip("/").split("/")[3:] if s]
    if not cauda:
        return False                                 # a raiz do dominio nao e item
    ultimo = cauda[-1]
    if re.search(r"\d{4,}", ultimo):                 # id numerico proprio
        return True
    if re.search(r"/\d{4}/\d{2}/", limpo):           # caminho com data
        return True
    # slug com corpo: tres ou mais palavras separadas por - ou _
    return len(re.split(r"[-_]", ultimo)) >= 3 and len(ultimo) >= 12

# Nao sao itens: navegacao, politica, redes sociais.
_NAO_E_ITEM = re.compile(
    r"(privacy|cookie|login|signin|accessibilit|mailto:|javascript:|tel:"
    r"|facebook\.com|twitter\.com|x\.com|linkedin\.com|instagram\.com|youtube\.com"
    r"|whatsapp|/feed|rss|sitemap|\.css$|\.js$|\.png$|\.jpg$|\.jpeg$|\.gif$|\.svg$"
    r"|\.ico$|/tag/|/categor|/autore|/author|#)", re.I)


def candidatos_a_item(corpo: bytes, base: str, limite: int = 14) -> list[str]:
    """Links da pagina de entrada que TEM CARA de item proprio da fonte.

    ⚠️ Ordena PDF primeiro: um PDF e inequivocamente um documento da fonte,
    enquanto uma pagina interna ainda pode ser navegacao disfarcada.
    """
    vistos, saida = set(), []
    for m in _HREF.finditer(corpo[:900000]):
        try:
            href = m.group(1).decode("utf-8", "replace").strip()
        except Exception:
            continue
        if not href or _NAO_E_ITEM.search(href):
            continue
        absoluto = urljoin(base, href)
        if not absoluto.startswith("http"):
            continue
        # ⚠️ So itens DA PROPRIA FONTE. Um PDF alojado noutro dominio e de outra
        # fonte, e registá-lo aqui atribuiria a esta candidata o que nao e dela.
        if dominio(absoluto) != dominio(base):
            continue
        if absoluto in vistos:
            continue
        if _CARA_DE_ITEM.search(absoluto) and parece_item(absoluto):
            vistos.add(absoluto)
            saida.append(absoluto)
    saida.sort(key=lambda u: (0 if u.lower().split("?")[0].endswith(".pdf") else 1, len(u)))
    return saida[:limite]


_YT_ID = re.compile(rb'"externalId"\s*:\s*"(UC[\w-]{22})"')
_YT_ID2 = re.compile(rb'"channelId"\s*:\s*"(UC[\w-]{22})"')


def youtube_channel_id(corpo: bytes) -> str:
    """O channelId DECLARADO pela propria pagina.

    ⚠️ NAO usar um regex generico `UC[\\w-]{22}` sobre o HTML todo: ele apanha
    o ID de um canal VINCULADO, e o feed desse ID responde 200 com videos
    reais — o erro atravessa calado. Ler o campo que nomeia o proprio canal.
    """
    for rx in (_YT_ID, _YT_ID2):
        m = rx.search(corpo)
        if m:
            return m.group(1).decode()
    return ""


def _tags(xml: bytes, tag: str) -> list[str]:
    return [x.decode("utf-8", "replace") for x in
            re.findall(("<%s[^>]*>(.*?)</%s>" % (tag, tag)).encode(), xml, re.S)]


# ─────────────────────────────────────────────────────────────────────────
# A CAPTURA, POR FAMILIA
# ─────────────────────────────────────────────────────────────────────────
def _ficha(cand: dict, familia: str) -> dict:
    return {
        "CONTRATO": CONTRATO,
        "CANDIDATE_ID": cand.get("CANDIDATA_ID"),
        "NOME": cand.get("NOME"),
        "URL": cand.get("URL"),
        "PUBLISHER": cand.get("NOME"),
        "COUNTRY": cand.get("PAIS"),
        "TIPO_DA_FILA": cand.get("TIPO"),
        "FAMILY": familia,
        "CAPTURED_AT": agora(),
        "FINAL_URL": "NAO SEI", "HTTP_STATUS": None,
        "OUTPUT_TYPE": "NAO SEI",
        "REAL_EXAMPLE_URL": "NAO SEI", "REAL_EXAMPLE_TITLE": "NAO SEI",
        "REAL_EXAMPLE_PUBLISHED_AT": "NAO SEI",
        "REAL_EXAMPLE_MEDIA_TYPE": "NAO SEI", "REAL_EXAMPLE_BYTES": None,
        "REAL_EXAMPLE_SHA256": "NAO SEI",
        "DISCOVERY_METHOD": "NAO SEI",
        "ROUTE_FAMILY": "NAO SEI", "IDENTITY_FAMILY": "NAO SEI",
        "BROWSER_REQUIRED": "NAO SEI", "LOGIN_REQUIRED": "NAO SEI",
        "PAID_REQUIRED": "NAO",
        "POLICY_STATUS": "OK",
        "HISTORICAL_DEPTH_OBSERVED": "NAO SEI",
        "UPDATE_FREQUENCY_OBSERVED": "NAO SEI",
        "ITEMS_OBSERVED_IN_INDEX": None,
        "EXPECTED_YIELD_INITIAL": "UNKNOWN",
        "CAPTURE_RESULT": "UNKNOWN",
        "CAPTURE_FAILURE_CLASS": None,
        "EVIDENCE": "NAO SEI",
    }


def _marcar_falha(f: dict, classe: str, detalhe: str = "") -> dict:
    f["CAPTURE_RESULT"] = "FAILED"
    f["CAPTURE_FAILURE_CLASS"] = classe
    f["EVIDENCE"] = "%s%s" % (FALHAS.get(classe, classe),
                              (" · %s" % detalhe) if detalhe else "")
    return f


def _gravar_amostra(cand_id: str, corpo: bytes, url: str) -> str:
    """Guarda os bytes da amostra. SEM isto, a captura e uma afirmacao."""
    pasta = EVIDENCIA / str(cand_id)
    pasta.mkdir(parents=True, exist_ok=True)
    nome = (urlparse(url).path.rsplit("/", 1)[-1] or "amostra")[:80]
    nome = re.sub(r"[^A-Za-z0-9._-]+", "_", nome) or "amostra"
    (pasta / nome).write_bytes(corpo)
    return str((pasta / nome).relative_to(RAIZ)).replace("\\", "/")


def capturar(cand: dict) -> dict:
    """UMA candidata → UMA ficha de REAL_EXAMPLE. Nunca levanta excecao."""
    url = (cand.get("URL") or "").strip()
    familia = familia_de(url)
    f = _ficha(cand, familia)

    # FASE 10 do enunciado, em codigo: estas nao se tocam.
    if dominio(url) in POLICY_BLOCKED or familia in ("LINKEDIN", "INSTAGRAM"):
        f["POLICY_STATUS"] = "POLICY_BLOCK"
        f["CAPTURE_RESULT"] = "NOT_ATTEMPTED"
        f["CAPTURE_FAILURE_CLASS"] = "POLICY"
        f["EVIDENCE"] = ("politica da casa: %s nao e elegivel. NAO foi feito "
                         "pedido de rede a este endereco." % dominio(url))
        return f

    try:
        if familia == "YOUTUBE":
            return _cap_youtube(f, url, cand)
        if familia == "DIRECT_PDF":
            return _cap_direto(f, url, cand)
        if familia == "FACEBOOK":
            return _cap_facebook(f, url, cand)
        return _cap_html(f, url, cand)
    except Exception as e:                                    # nunca travar o lote
        return _marcar_falha(f, "DNS_OR_CONN", "excecao inesperada: %s" % str(e)[:120])


def _cap_direto(f: dict, url: str, cand: dict) -> dict:
    r = buscar(url)
    f["HTTP_STATUS"], f["FINAL_URL"] = r["STATUS"], r["FINAL_URL"]
    if not r["OK"]:
        return _marcar_falha(f, r["FALHA"], r.get("DETALHE", "HTTP %s" % r["STATUS"]))
    if not r["BYTES"]:
        return _marcar_falha(f, "EMPTY_BODY")
    corpo = r["CORPO"]
    f["OUTPUT_TYPE"] = f["REAL_EXAMPLE_MEDIA_TYPE"] = assinatura(corpo)
    f["REAL_EXAMPLE_URL"] = r["FINAL_URL"]
    f["REAL_EXAMPLE_BYTES"] = r["BYTES"]
    f["REAL_EXAMPLE_SHA256"] = hashlib.sha256(corpo).hexdigest()
    f["REAL_EXAMPLE_TITLE"] = titulo_de(corpo) or (urlparse(url).path.rsplit("/", 1)[-1])
    f["REAL_EXAMPLE_PUBLISHED_AT"] = data_visivel(corpo)
    f["DISCOVERY_METHOD"] = "URL_DIRETA"
    f["ROUTE_FAMILY"] = "PDF_DIRECT" if f["OUTPUT_TYPE"] == "PDF" else "STATIC_ENDPOINT"
    f["IDENTITY_FAMILY"] = "URL_ESTAVEL"
    f["BROWSER_REQUIRED"] = f["LOGIN_REQUIRED"] = "NAO"
    f["CAPTURE_RESULT"] = "CAPTURED"
    f["EVIDENCE"] = _gravar_amostra(cand.get("CANDIDATA_ID"), corpo, r["FINAL_URL"])
    f["EXPECTED_YIELD_INITIAL"] = "LOW"
    f["ITEMS_OBSERVED_IN_INDEX"] = 1
    return f


def _cap_html(f: dict, url: str, cand: dict) -> dict:
    r = buscar(url, "text/html,application/xhtml+xml,*/*;q=0.8")
    f["HTTP_STATUS"], f["FINAL_URL"] = r["STATUS"], r["FINAL_URL"]
    if not r["OK"]:
        return _marcar_falha(f, r["FALHA"], r.get("DETALHE", "HTTP %s" % r["STATUS"]))
    if MURO_DE_LOGIN.search(r["FINAL_URL"] or ""):
        return _marcar_falha(f, "WALL", "redirigiu para %s" % r["FINAL_URL"][:90])
    if r["BYTES"] < 200:
        return _marcar_falha(f, "EMPTY_BODY", "%s bytes" % r["BYTES"])

    entrada = r["CORPO"]
    f["OUTPUT_TYPE"] = assinatura(entrada)

    # A entrada JA e um documento? (content-negotiation, redirect para PDF)
    if f["OUTPUT_TYPE"] in ("PDF", "JSON", "XML"):
        return _cap_direto(f, r["FINAL_URL"], cand)

    itens = candidatos_a_item(entrada, r["FINAL_URL"])
    f["ITEMS_OBSERVED_IN_INDEX"] = len(itens)
    if not itens:
        f["DISCOVERY_METHOD"] = "INDICE_HTML"
        f["BROWSER_REQUIRED"] = "TALVEZ"
        return _marcar_falha(f, "NO_ITEM_FOUND",
                             "entrada respondeu %s com %s bytes e 0 links com cara de item"
                             % (r["STATUS"], r["BYTES"]))

    # Tenta ate 3 itens: o primeiro pode estar morto sem a fonte estar.
    for alvo in itens[:3]:
        ri = buscar(alvo)
        if not ri["OK"] or not ri["BYTES"]:
            continue
        corpo = ri["CORPO"]
        f["REAL_EXAMPLE_URL"] = ri["FINAL_URL"]
        f["REAL_EXAMPLE_BYTES"] = ri["BYTES"]
        f["REAL_EXAMPLE_SHA256"] = hashlib.sha256(corpo).hexdigest()
        f["REAL_EXAMPLE_MEDIA_TYPE"] = assinatura(corpo)
        f["REAL_EXAMPLE_TITLE"] = titulo_de(corpo) or alvo.rsplit("/", 1)[-1][:120]
        f["REAL_EXAMPLE_PUBLISHED_AT"] = data_visivel(corpo)
        f["DISCOVERY_METHOD"] = "INDICE_HTML → ITEM"
        f["ROUTE_FAMILY"] = ("PDF_DISCOVERY_PAGE"
                             if f["REAL_EXAMPLE_MEDIA_TYPE"] == "PDF" else "HTML_PUBLIC")
        f["IDENTITY_FAMILY"] = "URL_DO_ITEM"
        f["BROWSER_REQUIRED"] = f["LOGIN_REQUIRED"] = "NAO"
        f["CAPTURE_RESULT"] = "CAPTURED"
        f["EVIDENCE"] = _gravar_amostra(cand.get("CANDIDATA_ID"), corpo, ri["FINAL_URL"])
        n = len(itens)
        f["EXPECTED_YIELD_INITIAL"] = "HIGH" if n >= 10 else ("MEDIUM" if n >= 4 else "LOW")
        return f

    return _marcar_falha(f, "NO_ITEM_FOUND",
                         "achei %d links com cara de item e nenhum dos 3 primeiros "
                         "devolveu corpo" % len(itens))


def _entradas(xml: bytes) -> list[dict]:
    """As <entry> do feed, cada uma com o SEU titulo, data e link.

    ⚠️ NAO SE LEEM AS TAGS GLOBALMENTE. O feed do YouTube tem `<title>` e
    `<published>` ao NIVEL DO FEED — nome do canal e data de CRIACAO do canal —
    antes de qualquer `<entry>`. Uma varredura global devolve esses primeiro, e
    entao:

        o «item» fica com a data de nascimento do canal (medido: 2015-02-10
        num video de 2026), e a cadencia calcula-se sobre uma lista que
        comeca com um outlier de dez anos — dando «mediana 0d — DIARIA».

    Duas medidas erradas de uma vez, ambas com ar de facto. Por isso a unidade
    de leitura e a ENTRY, nunca o documento.
    """
    saida = []
    for bloco in re.findall(rb"<entry>(.*?)</entry>", xml, re.S):
        t = _tags(bloco, "title")
        p = _tags(bloco, "published")
        link = re.search(rb'<link[^>]+href="([^"]+watch\?v=[^"]+)"', bloco)
        saida.append({
            "TITULO": (t[0] if t else "NAO SEI")[:200],
            "PUBLICADO": (p[0] if p else "")[:30],
            "URL": link.group(1).decode() if link else "",
        })
    return saida


def _cap_youtube(f: dict, url: str, cand: dict) -> dict:
    r = buscar(url, "text/html,*/*;q=0.8")
    f["HTTP_STATUS"], f["FINAL_URL"] = r["STATUS"], r["FINAL_URL"]
    if not r["OK"]:
        return _marcar_falha(f, r["FALHA"], r.get("DETALHE", "HTTP %s" % r["STATUS"]))
    cid = youtube_channel_id(r["CORPO"])
    if not cid:
        f["BROWSER_REQUIRED"] = "TALVEZ"
        return _marcar_falha(f, "NO_ITEM_FOUND",
                             "a pagina respondeu %s e nao declarou externalId/channelId"
                             % r["STATUS"])
    feed = "https://www.youtube.com/feeds/videos.xml?channel_id=%s" % cid
    rf = buscar(feed, "application/atom+xml,*/*")
    if not rf["OK"] or not rf["BYTES"]:
        return _marcar_falha(f, rf.get("FALHA") or "NO_ITEM_FOUND",
                             "channelId=%s mas o feed nao devolveu corpo" % cid)
    xml = rf["CORPO"]
    entradas = [e for e in _entradas(xml) if e["URL"]]
    if not entradas:
        return _marcar_falha(f, "NO_ITEM_FOUND", "feed sem entradas de video")

    primeira = entradas[0]
    f["REAL_EXAMPLE_URL"] = primeira["URL"]
    f["REAL_EXAMPLE_TITLE"] = primeira["TITULO"]
    f["REAL_EXAMPLE_PUBLISHED_AT"] = primeira["PUBLICADO"] or "NAO SEI"
    f["REAL_EXAMPLE_MEDIA_TYPE"] = "VIDEO_METADATA"
    f["REAL_EXAMPLE_BYTES"] = rf["BYTES"]
    f["REAL_EXAMPLE_SHA256"] = hashlib.sha256(xml).hexdigest()
    f["OUTPUT_TYPE"] = "XML_FEED"
    f["DISCOVERY_METHOD"] = "externalId → feed RSS publico"
    f["ROUTE_FAMILY"] = "YOUTUBE_FEED"
    f["IDENTITY_FAMILY"] = "CHANNEL_ID+VIDEO_ID"
    f["BROWSER_REQUIRED"] = f["LOGIN_REQUIRED"] = "NAO"
    f["CAPTURE_RESULT"] = "CAPTURED"
    f["EVIDENCE"] = _gravar_amostra(cand.get("CANDIDATA_ID"), xml, feed)
    f["CHANNEL_ID"] = cid
    f["ITEMS_OBSERVED_IN_INDEX"] = len(entradas)

    # ⚠️ CADENCIA MEDIDA, nao declarada: as datas das ENTRIES, e so delas.
    datas = [e["PUBLICADO"] for e in entradas if e["PUBLICADO"]]
    f["UPDATE_FREQUENCY_OBSERVED"], f["EXPECTED_YIELD_INITIAL"] = _cadencia(datas)
    if len(datas) >= 2:
        ordenadas = sorted(datas)
        f["HISTORICAL_DEPTH_OBSERVED"] = "%s … %s (%d entradas no feed)" % (
            ordenadas[0][:10], ordenadas[-1][:10], len(datas))
    return f


def _cadencia(datas: list[str]) -> tuple[str, str]:
    """Intervalo MEDIANO entre publicacoes + RECENCIA. Devolve (frequencia, yield).

    ⚠️ MEDIANA SOZINHA MENTE SOBRE UM CANAL PARADO. Medido ao vivo: um canal
    cujo ultimo video e de Julho publicou tudo em rajada (varios no mesmo dia),
    e a mediana deu 0 dias — «DIARIA/QUASE». Estava parado ha meses.

        UMA RAJADA ANTIGA E UMA CADENCIA ALTA SAO INDISTINGUIVEIS
        SE SO SE OLHAR PARA O ESPACO ENTRE PUBLICACOES.

    Por isso a leitura tem DOIS eixos, e o silencio recente rebaixa o yield
    independentemente do ritmo historico. `CADENCIA` e `ACTIVIDADE` nao se
    colapsam num numero so.
    """
    ds = []
    for d in datas[:15]:
        try:
            ds.append(datetime.fromisoformat(d.replace("Z", "+00:00")))
        except Exception:
            continue
    if len(ds) < 3:
        return "NAO SEI — menos de 3 datas legiveis", "UNKNOWN"
    ds.sort(reverse=True)
    gaps = sorted((ds[i] - ds[i + 1]).days for i in range(len(ds) - 1))
    med = gaps[len(gaps) // 2]
    dias_desde = (datetime.now(timezone.utc) - ds[0]).days

    if med <= 2:
        ritmo = "RAJADA/DIARIA (mediana %dd)" % med
    elif med <= 9:
        ritmo = "SEMANAL (mediana %dd)" % med
    elif med <= 40:
        ritmo = "MENSAL (mediana %dd)" % med
    else:
        ritmo = "ESPARSA (mediana %dd)" % med

    # A recencia e que decide o yield: um canal silencioso ha meses nao rende
    # agora, por muito denso que tenha sido o passado.
    if dias_desde <= 14:
        y = "HIGH" if med <= 9 else ("MEDIUM" if med <= 40 else "LOW")
    elif dias_desde <= 60:
        y = "MEDIUM" if med <= 40 else "LOW"
    elif dias_desde <= 365:
        y = "LOW"
    else:
        y = "DORMANT"

    return ("cadencia observada: %s · ultimo item ha %dd" % (ritmo, dias_desde)), y


def _cap_facebook(f: dict, url: str, cand: dict) -> dict:
    """Facebook: mede-se o que a superficie publica devolve, e nada mais.

    ⚠️ NAO se contorna muro. Se a resposta for um muro de consentimento ou de
    login, isso e CAPABILITY/POLICY — nunca «a fonte nao serve».
    """
    r = buscar(url, "text/html,*/*;q=0.8")
    f["HTTP_STATUS"], f["FINAL_URL"] = r["STATUS"], r["FINAL_URL"]
    f["ROUTE_FAMILY"] = "FACEBOOK_PUBLIC_SURFACE"
    f["IDENTITY_FAMILY"] = "PAGE_HANDLE"
    if not r["OK"]:
        return _marcar_falha(f, r["FALHA"], r.get("DETALHE", "HTTP %s" % r["STATUS"]))
    corpo, low = r["CORPO"], r["CORPO"][:250000].lower()
    if MURO_DE_LOGIN.search(r["FINAL_URL"] or "") or b"login" in low[:4000] \
            or b"cookie" in low[:4000] and b"accetta" in low[:20000]:
        f["LOGIN_REQUIRED"] = "SIM"
        f["BROWSER_REQUIRED"] = "SIM"
        return _marcar_falha(f, "WALL",
                             "superficie publica devolve muro (HTTP %s, %s bytes) — "
                             "capability/policy, NAO juizo sobre a fonte"
                             % (r["STATUS"], r["BYTES"]))
    f["OUTPUT_TYPE"] = f["REAL_EXAMPLE_MEDIA_TYPE"] = assinatura(corpo)
    titulo = titulo_de(corpo) or ""

    # ⚠️ UM TITULO GENERICO E UM MURO COM HTTP 200. Medido: 19 das 20 paginas
    # devolveram «<entidade> | <cidade>» e UMA devolveu apenas «Facebook» —
    # com 200 e 326 KB de corpo. Aceitar essa seria registar como prova de
    # entrega a pagina de porta da plataforma.
    #
    #     `PLATFORM_GENERIC_TITLE` ja tinha custado caro a esta casa em 14/09,
    #     quando dez recusas assentaram nele. A licao ali foi «nao li != nao
    #     serve»; a licao aqui e a gemea: «li a plataforma != li a fonte».
    if titulo.strip().lower() in ("facebook", "log in or sign up", "log into facebook"):
        f["LOGIN_REQUIRED"] = "TALVEZ"
        f["BROWSER_REQUIRED"] = "SIM"
        return _marcar_falha(f, "WALL",
                             "HTTP 200 com %s bytes, e o titulo lido foi o nome da "
                             "plataforma (%r) — nao o da fonte. Capability, nao juizo "
                             "sobre a fonte." % (r["BYTES"], titulo))

    f["REAL_EXAMPLE_URL"] = r["FINAL_URL"]
    f["REAL_EXAMPLE_TITLE"] = titulo or "NAO SEI"
    f["REAL_EXAMPLE_BYTES"] = r["BYTES"]
    f["REAL_EXAMPLE_SHA256"] = hashlib.sha256(corpo).hexdigest()
    f["REAL_EXAMPLE_PUBLISHED_AT"] = data_visivel(corpo)
    f["DISCOVERY_METHOD"] = "SUPERFICIE_PUBLICA"
    f["CAPTURE_RESULT"] = "CAPTURED"
    f["EVIDENCE"] = _gravar_amostra(cand.get("CANDIDATA_ID"), corpo, r["FINAL_URL"])
    f["EXPECTED_YIELD_INITIAL"] = "UNKNOWN"
    return f


if __name__ == "__main__":
    print("CONTRATO %s" % CONTRATO)
    print("familias: %s" % ", ".join(sorted(FAMILIAS)))
    print("classes de falha: %s" % ", ".join(sorted(FALHAS)))
    print("POLICY_BLOCKED (nunca tocadas): %s" % ", ".join(sorted(POLICY_BLOCKED)))
    if len(sys.argv) > 1:
        print(json.dumps(capturar({"CANDIDATA_ID": "CLI", "URL": sys.argv[1],
                                   "NOME": "cli", "PAIS": "IT", "TIPO": "?"}),
                         ensure_ascii=False, indent=1))
