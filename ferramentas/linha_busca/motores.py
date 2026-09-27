# -*- coding: utf-8 -*-
"""LINHA-BUSCA · 2) os MOTORES — como se pede e como se le a pagina de resultados. SEM REDE (so recebe bytes).

Cada motor diz: o endereco do pedido (`pedido(consulta)`), como se tiram os resultados dos bytes
(`resultados(bytes)`) e que especie de rota e (ROTA). Qual deles responde da VPN IT, e se o robots.txt
deles deixa, NAO SEI ate o `--medir-motores` correr com rede: a medida e a do transporte canonico
(`coleta/scrap_http`), que le o robots vivo — nada aqui o decide de cor (D91).

  DDG_HTML     html.duckduckgo.com/html/      pagina HTML sem JavaScript
  BING_HTML    www.bing.com/search            pagina HTML
  GOOGLE_HTML  www.google.com/search          pagina HTML
  GOOGLE_CSE   API oficial Programmable Search (chave+cx do dono; D91: API publica oficial)
  BRAVE_API    API oficial Brave Search (chave do dono)
  IMPORTADO    resultados de uma busca feita por fora (ex.: o motor web do Hermes do coordenador,
               BUSCA-LOTE-0), entregues num JSON: a rota fica declarada, nao se esconde.

⚠️ As formas dos resultados em HTML foram escritas pela forma PUBLICA conhecida destas paginas e testadas
contra fixtures SINTETICAS (marcadas no nome). A 1.a corrida com rede guarda a pagina de resultados real
(sha256) e a proxima versao das fixtures e essa.
"""
import base64
import json
import os
import re
import urllib.parse
from html import unescape

ENGINES_PROPRIOS = re.compile(r"(^|\.)(duckduckgo\.com|bing\.com|microsoft\.com|google\.[a-z.]+|googleusercontent\.com|"
                              r"gstatic\.com|brave\.com)$", re.I)


def _host(u: str) -> str:
    return (urllib.parse.urlsplit(u).hostname or "").lower()


def _limpos(urls: list) -> list:
    out, vistos = [], set()
    for u in urls:
        u = unescape(u).strip()
        if not u.startswith(("http://", "https://")):
            continue
        h = _host(u)
        if not h or ENGINES_PROPRIOS.search(h):
            continue
        k = u.split("#")[0].rstrip("/")
        if k in vistos:
            continue
        vistos.add(k)
        out.append(u)
    return out


# ---------------------------------------------------------------- DuckDuckGo HTML
def ddg_pedido(consulta: str) -> str:
    return "https://html.duckduckgo.com/html/?" + urllib.parse.urlencode({"q": consulta, "kl": "it-it"})


def ddg_resultados(corpo: bytes) -> list:
    t = corpo.decode("utf-8", "replace")
    urls = []
    for m in re.finditer(r'<a[^>]+class="[^"]*result__a[^"]*"[^>]+href="([^"]+)"', t):
        h = unescape(m.group(1))
        if "uddg=" in h:                               # //duckduckgo.com/l/?uddg=<endereco>&rut=...
            q = urllib.parse.parse_qs(urllib.parse.urlsplit(h if h.startswith("http") else "https:" + h).query)
            h = (q.get("uddg") or [""])[0]
        urls.append(h)
    return _limpos(urls)


# ---------------------------------------------------------------- Bing HTML
def bing_pedido(consulta: str) -> str:
    return "https://www.bing.com/search?" + urllib.parse.urlencode({"q": consulta, "setlang": "it", "cc": "IT"})


def _bing_ck(h: str) -> str:
    """bing.com/ck/a?...&u=a1<base64url> -> o endereco verdadeiro (quando vem embrulhado)."""
    q = urllib.parse.parse_qs(urllib.parse.urlsplit(h).query)
    u = (q.get("u") or [""])[0]
    if u.startswith("a1"):
        b = u[2:]
        try:
            return base64.urlsafe_b64decode(b + "=" * (-len(b) % 4)).decode("utf-8", "replace")
        except Exception:                                             # noqa: BLE001
            return ""
    return ""


def bing_resultados(corpo: bytes) -> list:
    t = corpo.decode("utf-8", "replace")
    urls = []
    for bloco in re.findall(r'<li class="b_algo".*?</li>', t, re.S):
        m = re.search(r'<h2[^>]*>\s*<a[^>]+href="([^"]+)"', bloco)
        if m:
            h = unescape(m.group(1))
            urls.append(_bing_ck(h) if "bing.com/ck/a" in h else h)
    return _limpos(urls)


# ---------------------------------------------------------------- Google HTML
def google_pedido(consulta: str) -> str:
    return "https://www.google.com/search?" + urllib.parse.urlencode({"q": consulta, "hl": "it", "gl": "it", "num": 10})


def google_resultados(corpo: bytes) -> list:
    t = corpo.decode("utf-8", "replace")
    urls = []
    for m in re.finditer(r'href="/url\?q=([^"&]+)', t):                  # forma sem JavaScript
        urls.append(urllib.parse.unquote(m.group(1)))
    for m in re.finditer(r'<a[^>]+href="(https?://[^"]+)"[^>]*>\s*(?:<[^>]+>\s*)*<h3', t):   # forma com h3
        urls.append(m.group(1))
    return _limpos(urls)


# ---------------------------------------------------------------- APIs oficiais (chave do dono)
def google_cse_pedido(consulta: str) -> str:
    k, cx = os.environ.get("SINTONIA_GOOGLE_CSE_KEY"), os.environ.get("SINTONIA_GOOGLE_CSE_CX")
    if not (k and cx):
        return ""
    return "https://www.googleapis.com/customsearch/v1?" + urllib.parse.urlencode(
        {"key": k, "cx": cx, "q": consulta, "gl": "it", "lr": "lang_it", "num": 10})


def google_cse_resultados(corpo: bytes) -> list:
    return _limpos([i.get("link", "") for i in (json.loads(corpo or b"{}").get("items") or [])])


def brave_pedido(consulta: str) -> str:
    if not os.environ.get("SINTONIA_BRAVE_KEY"):
        return ""
    return "https://api.search.brave.com/res/v1/web/search?" + urllib.parse.urlencode(
        {"q": consulta, "country": "it", "search_lang": "it", "count": 10})


def brave_resultados(corpo: bytes) -> list:
    return _limpos([r.get("url", "") for r in ((json.loads(corpo or b"{}").get("web") or {}).get("results") or [])])


MOTORES = {
    "DDG_HTML": {"PEDIDO": ddg_pedido, "RESULTADOS": ddg_resultados, "ROTA": "HTTP_HTML_SEM_JS"},
    "BING_HTML": {"PEDIDO": bing_pedido, "RESULTADOS": bing_resultados, "ROTA": "HTTP_HTML"},
    "GOOGLE_HTML": {"PEDIDO": google_pedido, "RESULTADOS": google_resultados, "ROTA": "HTTP_HTML"},
    "GOOGLE_CSE": {"PEDIDO": google_cse_pedido, "RESULTADOS": google_cse_resultados, "ROTA": "API_OFICIAL",
                   "CABECALHOS": {}},
    "BRAVE_API": {"PEDIDO": brave_pedido, "RESULTADOS": brave_resultados, "ROTA": "API_OFICIAL",
                  "CABECALHOS": {"Accept": "application/json",
                                 "X-Subscription-Token": os.environ.get("SINTONIA_BRAVE_KEY", "")}},
}
