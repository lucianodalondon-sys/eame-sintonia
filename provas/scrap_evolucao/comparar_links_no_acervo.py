"""SCRAP-EVOLUCAO · peca 3 — o extrator de ligacoes da prova de territorio, ANTES e DEPOIS, nas paginas do acervo.

    py provas/scrap_evolucao/comparar_links_no_acervo.py <raiz do vivo> [saida.json]

Sem rede, so leitura. Cada pagina HTML guardada em data/collection-store/italy e lida com o endereco de onde veio
(RAW_SHA256 -> SOURCE_URL no livro de observacoes, para que as ligacoes relativas se resolvam como no dia).
Pagina cujo endereco o livro nao conhece fica de fora e e contada.

Mede, por pagina: ligacoes do extrator antigo (a copia fiel do de dc0de726, abaixo) e do novo; as que so o antigo
via, e porque (<link>, <use>, variante do mesmo endereco); as que so o novo ve; e — o que conta para o teto — se a
ESCOLHA da prova muda: a pagina institucional e as duas primeiras de conteudo que `colher` pediria.
"""
import hashlib
import json
import os
import re
import sys
from collections import Counter
from urllib.parse import urljoin

RAIZ_REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(RAIZ_REPO, "curadoria"))
import colher_prova_territorio as C  # noqa: E402


def links_antigos(html: bytes, base: str) -> list:
    """Copia fiel de colher_prova_territorio._links em dc0de726."""
    s = html.decode("utf-8", "replace")
    vistos, out = set(), []
    for h in re.findall(r'href\s*=\s*["\']([^"\'#]+)', s, re.I):
        u = urljoin(base, h.strip())
        if u.startswith(("http://", "https://")) and C._mesmo_site(u, base) and u not in vistos:
            vistos.add(u)
            out.append(u)
    return out


RE_TAG_DO_HREF = re.compile(r"<(\w+)\b[^>]*?\bhref\s*=\s*[\"']([^\"'#]+)", re.I | re.S)


def escolha(links, base):
    inst = next((u for u in links if C._INSTITUCIONAL.search(C.urlparse(u).path)), None)
    cont = [u for u in links if C._parece_conteudo(u, base)][:2]
    return inst, cont


def main(raiz_vivo, saida=None):
    store = os.path.join(raiz_vivo, "data", "collection-store", "italy")
    obs = os.path.join(raiz_vivo, "data", "collection-ledger", "italy", "observations.ndjson")
    url_do_sha = {}
    with open(obs, encoding="utf-8") as f:
        for linha in f:
            try:
                o = json.loads(linha)
            except ValueError:
                continue
            if o.get("RAW_SHA256") and o.get("SOURCE_URL"):
                url_do_sha.setdefault(o["RAW_SHA256"], o["SOURCE_URL"])
    c = Counter()
    so_antigo_porque, exemplos = Counter(), {}
    mudou = []
    for dp, _, fs in os.walk(store):
        for nome in fs:
            p = os.path.join(dp, nome)
            with open(p, "rb") as fh:
                b = fh.read()
            if not re.search(rb"<html|<!doctype html", b[:4096], re.I):
                continue
            c["PAGINAS_HTML"] += 1
            base = url_do_sha.get(hashlib.sha256(b).hexdigest())
            if not base:
                c["SEM_ENDERECO_NO_LIVRO"] += 1
                continue
            c["PAGINAS_MEDIDAS"] += 1
            a, n = links_antigos(b, base), C._links(b, base)
            c["LIGACOES_ANTES"] += len(a)
            c["LIGACOES_DEPOIS"] += len(n)
            canon_n = set(n)
            tag_de = {}
            for m in RE_TAG_DO_HREF.finditer(b.decode("utf-8", "replace")):
                tag_de.setdefault(urljoin(base, m.group(2).strip()), m.group(1).lower())
            for u in a:
                if u in canon_n:
                    continue
                t = tag_de.get(u, "?")
                if "&amp;" in u:
                    k = "&amp; nao desfeito (o antigo pedia um endereco que nao existe)"
                elif t in ("link", "use"):
                    k = "<%s> (nao e pagina)" % t
                elif C.canonico(u) in canon_n:
                    k = "variante do mesmo endereco (fica uma so)"
                else:
                    k = "outra (<%s>)" % t
                so_antigo_porque[k] += 1
                exemplos.setdefault(k, (base, u))
            for u in n:
                if u not in set(a) and u not in {C.canonico(x) for x in a}:
                    c["SO_NO_NOVO"] += 1
                    exemplos.setdefault("so no novo", (base, u))
            ea, en = escolha(a, base), escolha(n, base)
            if (ea[0] and C.canonico(ea[0]), [C.canonico(x) for x in ea[1]]) != (en[0], en[1]):
                gasto = [u for u in ([ea[0]] if ea[0] else []) + ea[1] if tag_de.get(u) in ("link", "use")]
                mudou.append({"PAGINA": base, "ANTES": ea, "DEPOIS": en, "ANTES_GASTAVA_EM_NAO_PAGINA": gasto})
                c["ESCOLHA_ANTIGA_GASTAVA_PEDIDO_EM_NAO_PAGINA"] += bool(gasto)
    r = {**c, "SO_NO_ANTIGO_PORQUE": dict(so_antigo_porque), "ESCOLHA_DA_PROVA_MUDOU": len(mudou),
         "FONTES_COM_ESCOLHA_MUDADA": sorted({m["PAGINA"].split("/")[2] for m in mudou}), "MUDANCAS": mudou, "EXEMPLOS": exemplos}
    if saida:
        with open(saida, "w", encoding="utf-8") as f:
            json.dump(r, f, ensure_ascii=False, indent=1)
    return r


if __name__ == "__main__":
    r = main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
    print(json.dumps({k: v for k, v in r.items() if k not in ("MUDANCAS", "EXEMPLOS")}, ensure_ascii=False, indent=1))
