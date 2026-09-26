"""SCRAP-EVOLUCAO · quantas fontes do acervo ANUNCIAM feed RSS/Atom no <head> (sem rede, so leitura).

    py provas/scrap_evolucao/medir_feeds_no_acervo.py <pasta collection-store/italy> [saida.json]

Conta por FONTE (SOURCE_ID = a pasta de 1.o nivel) as que tem pelo menos uma pagina HTML guardada, e
dessas as que declaram <link rel="alternate" type="application/rss+xml|atom+xml" href="...">.
Nada e pedido a rede: e o que o proprio site escreveu nas paginas que ja guardamos.
"""
import json
import os
import re
import sys
from collections import defaultdict
from urllib.parse import urljoin

RE_LINK = re.compile(r"<link\b[^>]*>", re.I)
RE_ATTR = re.compile(r'([a-zA-Z-]+)\s*=\s*("([^"]*)"|\'([^\']*)\'|([^\s>]+))')
TIPOS = ("application/rss+xml", "application/atom+xml")


def feeds_do_html(html: str, base: str = "") -> list:
    out = []
    for tag in RE_LINK.findall(html[:400_000]):
        a = {m.group(1).lower(): (m.group(3) or m.group(4) or m.group(5) or "") for m in RE_ATTR.finditer(tag)}
        if "alternate" in a.get("rel", "").lower() and a.get("type", "").lower() in TIPOS and a.get("href"):
            out.append({"HREF": urljoin(base, a["href"].strip()), "TIPO": a["type"].lower(), "TITULO": a.get("title", "")})
    return out


def main(raiz, saida=None):
    fontes = defaultdict(lambda: {"PAGINAS_HTML": 0, "FEEDS": {}})
    for sid in sorted(os.listdir(raiz)):
        d = os.path.join(raiz, sid)
        if not os.path.isdir(d):
            continue
        for dp, _, fs in os.walk(d):
            for f in fs:
                p = os.path.join(dp, f)
                with open(p, "rb") as fh:
                    cab = fh.read(400_000)
                if not re.search(rb"<html|<!doctype html", cab[:4096], re.I):
                    continue
                fontes[sid]["PAGINAS_HTML"] += 1
                for x in feeds_do_html(cab.decode("utf-8", "replace")):
                    fontes[sid]["FEEDS"].setdefault(x["HREF"], x)
    com = {s: v for s, v in fontes.items() if v["FEEDS"]}
    r = {"FONTES_COM_HTML": len(fontes), "FONTES_COM_FEED": len(com),
         "FEEDS_POR_FONTE": {s: sorted(v["FEEDS"]) for s, v in com.items()},
         "SEM_FEED": sorted(s for s, v in fontes.items() if not v["FEEDS"])}
    if saida:
        with open(saida, "w", encoding="utf-8") as f:
            json.dump(r, f, ensure_ascii=False, indent=1)
    return r


if __name__ == "__main__":
    r = main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
    print("FONTES_COM_HTML=%d FONTES_COM_FEED=%d" % (r["FONTES_COM_HTML"], r["FONTES_COM_FEED"]))
    for s, fs in r["FEEDS_POR_FONTE"].items():
        print(" ", s, fs[:3])
