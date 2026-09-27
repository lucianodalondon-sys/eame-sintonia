"""SCRAP-EVOLUCAO · o feed de cada fonte que o anuncia, pedido UMA vez com rede (o coordenador corre).

    py provas/scrap_evolucao/medir_feeds_com_rede.py --livros=<pasta das ondas> [--recibos=<pasta>] --saida=<pasta>

As 14 fontes vem de FEEDS-NO-ACERVO.json (o que os proprios sites escrevem no <head> das paginas guardadas).
Por fonte, pelo portao de `coleta/rota_navegador.medir`: janela de 24 h do dominio → robots vivo → 1 pedido ao
feed, com a cara do coletor (regras/ROTA-NAVEGADOR.json). Egresso IT provado UMA vez, no comeco; sem IT nada sai.
Cada fonte deixa CORPO.bin + RECIBO-ROTA-NAVEGADOR.json na sua pasta: as rodadas leem o recibo, e ⚠️ o dominio
fica 24 h fechado para a coleta a partir daqui.

Mede, por feed: HTTP, bytes, itens (<item>/<entry>), itens do proprio site, itens com data de publicacao
(pubDate/dc:date/published — `updated` nao conta). A data e PUBLICATION_TIME nivel indice, nunca FACT_TIME.
"""
import json
import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(RAIZ, "coleta"))
import rota_navegador as RN  # noqa: E402

AQUI = os.path.dirname(os.path.abspath(__file__))
RE_ITEM = re.compile(rb"<(item|entry)\b.*?</\1>", re.S | re.I)
RE_DATA = re.compile(rb"<(pubDate|dc:date|published)\b", re.I)
RE_LINK = re.compile(rb"<link\b[^>]*?href=[\"']([^\"']+)|<link>\s*(?:<!\[CDATA\[)?\s*([^<\]\s]+)", re.I)


def ler_feed(corpo: bytes, host: str) -> dict:
    itens = [m.group(0) for m in RE_ITEM.finditer(corpo)]
    do_site = 0
    for it in itens:
        m = RE_LINK.search(it)
        u = (m.group(1) or m.group(2)).decode("utf-8", "replace") if m else ""
        do_site += host.removeprefix("www.") in u
    return {"ITENS": len(itens), "ITENS_DO_SITE": do_site, "COM_DATA_DE_PUBLICACAO": sum(1 for it in itens if RE_DATA.search(it))}


def feeds(caminho=os.path.join(AQUI, "FEEDS-NO-ACERVO.json")) -> dict:
    """SOURCE_ID -> o feed do site inteiro: o mais curto que nao e de comentarios (o de um artigo e mais comprido)."""
    d = json.load(open(caminho, encoding="utf-8"))["FEEDS_POR_FONTE"]
    return {sid: min((f for f in fs if "/comments/feed" not in f) or fs, key=len) for sid, fs in d.items()}


def main(livros, recibos, saida, *, egresso=None, **injectar):
    g = (egresso or RN._egresso_do_dono)()
    res = {}
    for sid, url in sorted(feeds().items()):
        r = RN.medir(url, livros=livros, recibos=recibos, saida=os.path.join(saida, sid), egresso=lambda: g, **injectar)
        linha = {k: r.get(k) for k in ("URL", "HTTP", "BYTES", "PAROU", "PEDIDOS_POR_DOMINIO", "ROTA_HTTP")}
        if r.get("HTTP") == 200:
            with open(os.path.join(saida, sid, "CORPO.bin"), "rb") as f:
                linha.update(ler_feed(f.read(), r["HOST"]))
        res[sid] = linha
        print(sid, json.dumps(linha, ensure_ascii=False))
    with open(os.path.join(saida, "MEDIDA-FEEDS.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    return res


if __name__ == "__main__":
    a = dict(x[2:].split("=", 1) for x in sys.argv[1:] if x.startswith("--") and "=" in x)
    if "livros" not in a or "saida" not in a:
        print(__doc__)
        raise SystemExit(2)
    main(a["livros"], a.get("recibos"), a["saida"])
