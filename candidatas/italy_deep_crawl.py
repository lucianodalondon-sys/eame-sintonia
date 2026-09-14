#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O GRAFO DE DESCOBERTA — uma fonte boa aparece quase sempre atraves de outra.

Uma busca no Google devolve quem paga SEO. O rodape de um servico
fitossanitario devolve quem trabalha com ele: o consorcio, a universidade, a
rede de monitorizacao, a estacao experimental. Por isso este script nao busca:
ele ANDA pelos links das fontes que a casa ja conhece e anota para onde elas
apontam.

    240 hosts italianos ja conhecidos
        -> paginas de ligacao/parceiros/projetos/rede
            -> host novo, com o link que o revelou guardado (DISCOVERED_FROM)

O que sai daqui e RUIDO com endereco real. Nao e fonte, nao e candidata
qualificada: e uma pista que alguem ja provou existir, porque o HTTP respondeu.
A peneira vem depois, noutro script.

Duas leis que este ficheiro respeita:
  · pagina que nao abre fica BROKEN, nao desaparece;
  · host que aparece 200 vezes nao vale 200 — a chave e o host, nao o link.

Cache em disco: a mesma pagina nao e pedida duas vezes. Isto e educacao com o
servidor de outra pessoa, e e o que torna a rodada 2 barata.
"""

import hashlib
import json
import re
import ssl
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

TRABALHO = Path(sys.argv[1] if len(sys.argv) > 1
                else "C:/Users/London1/AppData/Local/Temp/sintonia-italy-deep")
CACHE = TRABALHO / "cache"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

# Paginas que costumam guardar a rede de uma organizacao. Nao sao "sobre nos":
# sao onde ela diz com quem trabalha e o que publica.
PISTAS_DE_REDE = [
    "link", "links", "collegamenti", "partner", "partners", "rete", "reti",
    "progetti", "progetto", "pubblicazioni", "bollettini", "bollettino",
    "notiziario", "newsletter", "avvisi", "difesa", "fitosanitario",
    "fitosanitari", "monitoraggio", "servizi", "soci", "associati", "consorzi",
    "aderenti", "ricerca", "dipartimenti", "strutture", "osservatorio",
    "agrometeo", "agrometeorologia", "dati", "documenti", "news", "notizie",
    "sperimentazione", "prove", "assistenza-tecnica", "consulenza",
    "organizzazioni-produttori", "cooperative", "elenco", "albo",
]

PALAVRA_AGRI = [
    "agricol", "agrari", "agronom", "coltur", "colture", "fitosanitar",
    "fitopatolog", "difesa", "parassit", "malatti", "infestant", "diserb",
    "vigne", "viticol", "vite", "olivo", "olivicol", "oliv", "cereal",
    "frumento", "grano", "mais", "riso", "risicol", "pomodoro", "ortic",
    "orticol", "frutticol", "frutta", "melo", "pero", "agrum", "nocciol",
    "patata", "barbabietol", "soia", "girasol", "zootecn", "irrigaz",
    "agrometeo", "meteo", "suolo", "terreno", "semina", "raccolto",
    "produttor", "coltivator", "azienda agricola", "campagna", "vivaist",
    "sementi", "concim", "fertilizz", "biologic", "bollettino", "consorzio",
    "cooperativ", "agroaliment", "agrifood", "psr", "pac ",
]

# Marcas de que a fonte PRODUZ informacao nova com regularidade — o que esta
# missao procura. Uma homepage bonita nao tem nenhuma destas.
MARCA_RECORRENTE = [
    "bollettino", "bollettini", "notiziario", "newsletter", "avviso",
    "avvisi", "allerta", "allerte", "monitoraggio", "aggiornamento",
    "aggiornato", "settimanale", "quindicinale", "mensile", "archivio",
    "rss", "feed", "comunicat", "rapporto", "report", "dati aperti",
    "open data", "statistic", "pubblicazion", "annuario", "podcast",
    "webinar", "convegno", "prove sperimentali", "risultati",
]

RE_HREF = re.compile(r'<a\b[^>]*?href\s*=\s*["\']([^"\'#][^"\']*)["\'][^>]*>(.*?)</a>',
                     re.I | re.S)
RE_TAG = re.compile(r"<[^>]+>")
RE_TITLE = re.compile(r"<title[^>]*>(.*?)</title>", re.I | re.S)
RE_RSS = re.compile(r'type\s*=\s*["\']application/(rss|atom)\+xml["\']', re.I)
RE_DATA = re.compile(r"\b(20[0-2][0-9])[-/.](0[1-9]|1[0-2])[-/.]([0-3][0-9])\b")
RE_DATA_IT = re.compile(r"\b([0-3]?[0-9])[/.\-](0?[1-9]|1[0-2])[/.\-](20[0-2][0-9])\b")

SOCIAL = {
    "INSTAGRAM": "instagram.com", "YOUTUBE": "youtube.com",
    "LINKEDIN": "linkedin.com", "FACEBOOK": "facebook.com",
    "TIKTOK": "tiktok.com", "X": "twitter.com",
}

_lock = threading.Lock()
_pedidos = {"n": 0, "bytes": 0, "erros": 0, "cache": 0}


def chave_cache(url: str) -> Path:
    return CACHE / (hashlib.sha1(url.encode("utf-8")).hexdigest() + ".json")


def buscar(url: str, timeout: int = 20, max_bytes: int = 400_000) -> dict:
    """Pede uma pagina. Guarda o resultado em disco — inclusive o erro.

    Guardar o erro tambem e de proposito: sem isso, a rodada seguinte volta a
    bater na mesma porta fechada e gasta o tempo de todos.
    """
    ck = chave_cache(url)
    if ck.exists():
        with _lock:
            _pedidos["cache"] += 1
        try:
            return json.loads(ck.read_text(encoding="utf-8"))
        except Exception:
            pass
    out = {"url": url, "status": None, "final": url, "ctype": "", "html": "",
           "erro": "", "quando": time.strftime("%Y-%m-%dT%H:%M:%S")}
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "it-IT,it;q=0.9,en;q=0.6",
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
            raw = r.read(max_bytes)
            out["status"] = r.status
            out["final"] = r.geturl()
            out["ctype"] = r.headers.get("Content-Type", "")
            enc = "utf-8"
            m = re.search(r"charset=([\w\-]+)", out["ctype"], re.I)
            if m:
                enc = m.group(1)
            try:
                out["html"] = raw.decode(enc, errors="replace")
            except LookupError:
                out["html"] = raw.decode("utf-8", errors="replace")
        with _lock:
            _pedidos["n"] += 1
            _pedidos["bytes"] += len(raw)
    except urllib.error.HTTPError as e:
        out["status"] = e.code
        out["erro"] = f"HTTP {e.code}"
        with _lock:
            _pedidos["n"] += 1
            _pedidos["erros"] += 1
    except Exception as e:
        out["erro"] = f"{type(e).__name__}: {str(e)[:120]}"
        with _lock:
            _pedidos["n"] += 1
            _pedidos["erros"] += 1
    CACHE.mkdir(parents=True, exist_ok=True)
    ck.write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
    return out


def host_de(url: str) -> str:
    try:
        h = urllib.parse.urlsplit(url).netloc.lower()
    except Exception:
        return ""
    h = h.split("@")[-1].split(":")[0]
    return h[4:] if h.startswith("www.") else h


def raiz_registavel(h: str) -> str:
    """O dono provavel. 'agraria.unina.it' e 'unina.it' sao a MESMA casa.

    Isto e heuristica, nao registro: serve para nao contar o mesmo dono
    dez vezes. O sufixo composto (.gov.it, .co.uk) e tratado a mao porque
    a lista publica de sufixos nao esta neste ambiente.
    """
    p = h.split(".")
    if len(p) <= 2:
        return h
    compostos = {"gov.it", "edu.it", "co.uk", "org.uk", "com.br", "gov.br",
                 "camcom.gov.it", "provincia.tn.it", "provincia.bz.it"}
    for n in (3, 2):
        if len(p) > n and ".".join(p[-n:]) in compostos:
            return ".".join(p[-(n + 1):])
    return ".".join(p[-2:])


def texto_limpo(h: str) -> str:
    return re.sub(r"\s+", " ", RE_TAG.sub(" ", h or "")).strip()


def medir_pagina(html: str) -> dict:
    baixo = html.lower()
    tit = ""
    m = RE_TITLE.search(html)
    if m:
        tit = texto_limpo(m.group(1))[:200]
    corpo = texto_limpo(html)
    agri = sum(1 for p in PALAVRA_AGRI if p in baixo)
    rec = sorted({p for p in MARCA_RECORRENTE if p in baixo})
    datas = RE_DATA.findall(html) + [(a[2], a[1], a[0]) for a in RE_DATA_IT.findall(html)]
    anos = sorted({int(d[0]) for d in datas if 2015 <= int(d[0]) <= 2026})
    soc = {}
    for plat, marca in SOCIAL.items():
        for mm in re.finditer(re.escape(marca) + r"/([A-Za-z0-9_.\-@]{2,40})", html, re.I):
            alvo = mm.group(1).lstrip("@")
            if alvo.lower() in ("sharer", "share", "intent", "plugins", "watch",
                                "embed", "channel", "c", "user", "profile",
                                "pages", "company", "in", "shareartic"):
                continue
            soc.setdefault(plat, set()).add(alvo)
    return {
        "titulo": tit,
        "agri_hits": agri,
        "marcas_recorrentes": rec,
        "tem_rss": bool(RE_RSS.search(html)),
        "ano_max_visto": max(anos) if anos else None,
        "anos_vistos": anos[-4:],
        "social": {k: sorted(v)[:4] for k, v in soc.items()},
        "tamanho_texto": len(corpo),
    }


def links_de(html: str, base: str):
    for m in RE_HREF.finditer(html):
        href, ancora = m.group(1), texto_limpo(m.group(2))[:140]
        if href.lower().startswith(("mailto:", "javascript:", "tel:", "data:")):
            continue
        try:
            absoluto = urllib.parse.urljoin(base, href)
        except Exception:
            continue
        if not absoluto.lower().startswith("http"):
            continue
        yield absoluto.split("#")[0], ancora


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    TRABALHO.mkdir(parents=True, exist_ok=True)

    sementes = json.loads((TRABALHO / "SEEDS.json").read_text(encoding="utf-8"))
    print(f"SEMENTES={len(sementes)}")

    # RODADA A · abrir cada semente e apanhar as suas paginas de rede
    paginas_a_ler = []
    for s in sementes:
        paginas_a_ler.append((s["url"], s, 0))

    vistos = set()
    descobertas = {}     # host -> registo
    paginas_lidas = {}   # url -> medida

    def registar_link(url: str, ancora: str, de_onde: dict, pagina_de: str):
        h = host_de(url)
        if not h or "." not in h:
            return
        r = raiz_registavel(h)
        d = descobertas.setdefault(r, {
            "host_raiz": r, "hosts": set(), "urls": {}, "ancoras": set(),
            "descoberto_de": set(), "regioes_do_descobridor": set(),
            "n_links": 0,
        })
        d["hosts"].add(h)
        d["n_links"] += 1
        d["urls"][url] = d["urls"].get(url, 0) + 1
        if ancora:
            d["ancoras"].add(ancora)
        d["descoberto_de"].add(pagina_de)
        if de_onde.get("regiao"):
            d["regioes_do_descobridor"].add(de_onde["regiao"])

    nivel = 0
    while paginas_a_ler and nivel <= 1:
        lote = [(u, s, n) for (u, s, n) in paginas_a_ler if u not in vistos]
        paginas_a_ler = []
        vistos.update(u for u, _, _ in lote)
        print(f"  RODADA nivel={nivel} paginas={len(lote)}")
        if not lote:
            break

        def trabalha(item):
            url, sem, n = item
            r = buscar(url)
            if not r.get("html"):
                return (url, sem, n, r, None, [])
            med = medir_pagina(r["html"])
            ls = list(links_de(r["html"], r.get("final") or url))
            return (url, sem, n, r, med, ls)

        with ThreadPoolExecutor(max_workers=10) as ex:
            for url, sem, n, r, med, ls in ex.map(trabalha, lote):
                paginas_lidas[url] = {
                    "status": r.get("status"), "erro": r.get("erro"),
                    "final": r.get("final"), "semente": sem.get("nome"),
                    "regiao": sem.get("regiao"), "medida": med,
                }
                if not ls:
                    continue
                hs = host_de(r.get("final") or url)
                rs = raiz_registavel(hs)
                internos = []
                for link, anc in ls:
                    hl = host_de(link)
                    if raiz_registavel(hl) == rs:
                        internos.append((link, anc))
                    else:
                        registar_link(link, anc, sem, url)
                if n < 1:
                    # so as paginas que provavelmente guardam a rede
                    escolhidas, ja = [], set()
                    for link, anc in internos:
                        alvo = (link.lower() + " " + anc.lower())
                        if any(p in alvo for p in PISTAS_DE_REDE):
                            k = link.rstrip("/")
                            if k not in ja:
                                ja.add(k)
                                escolhidas.append(link)
                        if len(escolhidas) >= 14:
                            break
                    for link in escolhidas:
                        paginas_a_ler.append((link, sem, n + 1))
        nivel += 1

    # gravar
    saida = []
    for r, d in descobertas.items():
        urls = sorted(d["urls"].items(), key=lambda kv: -kv[1])
        saida.append({
            "HOST_RAIZ": r,
            "HOSTS": sorted(d["hosts"]),
            "N_LINKS_RECEBIDOS": d["n_links"],
            "N_DESCOBRIDORES": len(d["descoberto_de"]),
            "URLS_TOP": [u for u, _ in urls[:6]],
            "ANCORAS": sorted(d["ancoras"])[:12],
            "DISCOVERED_FROM": sorted(d["descoberto_de"])[:6],
            "REGIOES_DO_DESCOBRIDOR": sorted(d["regioes_do_descobridor"]),
        })
    saida.sort(key=lambda x: -x["N_DESCOBRIDORES"])
    (TRABALHO / "CRAWL-DISCOVERIES.json").write_text(
        json.dumps(saida, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    (TRABALHO / "CRAWL-PAGES.json").write_text(
        json.dumps(paginas_lidas, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    ok = sum(1 for p in paginas_lidas.values() if p["status"] == 200)
    print(f"\nPAGINAS_LIDAS={len(paginas_lidas)} (HTTP200={ok})")
    print(f"HOSTS_RAIZ_DESCOBERTOS={len(saida)}")
    print(f"PEDIDOS_HTTP={_pedidos['n']} CACHE={_pedidos['cache']} "
          f"ERROS={_pedidos['erros']} BYTES={_pedidos['bytes']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
