"""IA-CUR: o que o agente le de cada pagina JA GUARDADA (sem rede). Imprime um resumo curto:
sha256 dos bytes, titulo, meta descricao, texto visivel (cortado) e as ligacoes agrupadas.
uso: py ler_paginas.py <ficheiro> [<url>] [--links] [--chars N]"""
import hashlib, html, re, sys, collections
from urllib.parse import urljoin, urlparse

def ler(caminho, url="", links=False, chars=1500):
    b = open(caminho, "rb").read()
    sha = hashlib.sha256(b).hexdigest()
    t = b.decode("utf-8", errors="replace")
    tit = re.search(r"<title[^>]*>(.*?)</title>", t, re.S | re.I)
    desc = re.search(r'<meta[^>]+name=["\']description["\'][^>]+content=["\'](.*?)["\']', t, re.S | re.I)
    corpo = re.sub(r"(?is)<(script|style|noscript|svg|nav|footer|header)[^>]*>.*?</\1>", " ", t)
    txt = html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", corpo))).strip()
    out = ["SHA256 %s  BYTES %d  URL %s" % (sha, len(b), url),
           "TITULO: %s" % (html.unescape(tit.group(1)).strip()[:150] if tit else "-"),
           "DESCRICAO: %s" % (html.unescape(desc.group(1)).strip()[:200] if desc else "-"),
           "TEXTO(%d): %s" % (len(txt), txt[:chars])]
    if links:
        hs = [urljoin(url, h) for h in re.findall(r'href=["\']([^"\'#]+)', t)]
        host = urlparse(url).netloc
        dentro = [h for h in hs if urlparse(h).netloc == host]
        grupos = collections.Counter("/".join(urlparse(h).path.split("/")[:3]) for h in dentro)
        out.append("LIGACOES: %d (mesmo site %d)" % (len(hs), len(dentro)))
        out.append("  seccoes: " + " | ".join("%s x%d" % (k, v) for k, v in grupos.most_common(25)))
        janela = [h for h in dict.fromkeys(dentro) if re.search(
            r"bollettin|avvis|fitosanit|difesa|notizi|news|comunicat|agrometeo|monitoragg|allert", h, re.I)]
        out.append("  de janela/noticia: " + " ".join(janela[:40]))
    return sha, "\n".join(out)

if __name__ == "__main__":
    a = sys.argv[1:]
    url = a[1] if len(a) > 1 and not a[1].startswith("--") else ""
    n = int(a[a.index("--chars") + 1]) if "--chars" in a else 1500
    print(ler(a[0], url, "--links" in a, n)[1])
