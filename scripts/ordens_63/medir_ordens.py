# -*- coding: utf-8 -*-
"""ORDENS-63 · 1 pedido por DOMINIO (+ robots pela casa) para ver se as ordens de agronomos publicam
algo datado e com corpo. NAO e o robo (D41.3): sem fila, sem livro.

    py scripts/ordens_63/medir_ordens.py <pasta-fora-do-git>

  conaf.it (54 ordens + 5 federacoes, o MESMO sistema): o feed de UMA ordem com posts datados
  (ordinelivorno; a prova guardada mostra /2026/04/01/pasqua-2026/). O feed traz data e texto: da
  frequencia E tamanho de cada post num pedido so.
  agronomiforestalipalermo.it: o feed (a P3 de 23/09 mediu-o).
  agronomienna.it, agronomimessina.it, agronomiragusa.it: a pagina inicial.
So depois do portao de egresso por consenso dar PASS IT. Escreve MEDIDA-ORDENS-V1.json ao lado.
"""
import hashlib
import html
import json
import re
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))
sys.path.insert(0, str(RAIZ / "superficie"))
import rede                      # noqa: E402
import reparar_contrato as RC    # noqa: E402
import gate_de_rota as GATE      # noqa: E402

ALVOS = [
    ("conaf.it", "https://ordinelivorno.conaf.it/feed/", "FEED"),
    ("agronomiforestalipalermo.it", "https://www.agronomiforestalipalermo.it/feed/", "FEED"),
    ("agronomienna.it", "http://www.agronomienna.it/", "HTML"),
    ("agronomimessina.it", "https://www.agronomimessina.it/", "HTML"),
    ("agronomiragusa.it", "http://www.agronomiragusa.it/", "HTML"),
]


def texto(s: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()


def ler_feed(b: bytes) -> list[dict]:
    t = b.decode("utf-8", "replace")
    itens = []
    for it in re.findall(r"<item>(.*?)</item>", t, re.S):
        def campo(nome):
            m = re.search(r"<%s>(.*?)</%s>" % (nome, nome), it, re.S)
            v = m.group(1) if m else ""
            return re.sub(r"^<!\[CDATA\[(.*)\]\]>$", r"\1", v.strip(), flags=re.S)
        corpo = campo("content:encoded") or campo("description")
        itens.append({"TITULO": texto(campo("title"))[:120], "LINK": campo("link"), "DATA": campo("pubDate"),
                      "CATEGORIAS": [texto(c) for c in re.findall(r"<category>(.*?)</category>", it, re.S)][:4],
                      "LETRAS_NO_CORPO": len(texto(corpo)), "SO_RESUMO": not campo("content:encoded")})
    return itens


def ler_html(b: bytes, url: str) -> dict:
    t = b.decode("utf-8", "replace")
    hrefs = sorted({h for h in re.findall(r'href=["\']([^"\']+)["\']', t)})
    datados = [h for h in hrefs if re.search(r"/20\d\d/\d\d/", h)]
    noticias = [h for h in hrefs if re.search(r"news|notizi|avvis|comunicat|eventi|blog", h, re.I)]
    return {"LIGACOES": len(hrefs), "DATADAS": datados[:15], "COM_VOCABULARIO_DE_NOTICIA": noticias[:25],
            "RETRATO": {k: v for k, v in RC.RH.retrato_do_html(b).items() if k != "TEXT_SHA256"}}


def main():
    saida = Path(sys.argv[1])
    saida.mkdir(parents=True, exist_ok=True)
    portao = rede.portao_de_egresso("IT")
    if portao["EGRESS_GATE"] != "PASS":
        print("PORTAO FECHADO", portao.get("PORQUE_BLOQUEADO"))
        return 2
    linhas = []
    for dom, url, tipo in ALVOS:
        host = urlparse(url).netloc
        l = {"DOMINIO": dom, "URL": url, "TIPO": tipo, "PEDIDOS": 0}
        try:
            rp, txt = GATE.robots_de(host)
            l["PEDIDOS"] += 1
            l["ROBOTS"] = "PERMITE" if GATE.permitido(url, rp) else "PROIBE"
        except Exception as e:   # noqa: BLE001
            l.update({"ROBOTS": "ILEGIVEL", "ERRO": repr(e)[:160]})
        if l["ROBOTS"] != "PERMITE":
            linhas.append(l)
            continue
        time.sleep(2)
        st, b, err, destino = RC.buscar_com_destino(url)
        l["PEDIDOS"] += 1
        l.update({"HTTP": st, "ERRO": err or None, "DESTINO": destino if destino != url else None, "BYTES": len(b or b"")})
        if b:
            nome = re.sub(r"[^a-z0-9]+", "_", dom) + (".xml" if tipo == "FEED" else ".html")
            (saida / nome).write_bytes(b)
            l.update({"FICHEIRO": nome, "SHA256": hashlib.sha256(b).hexdigest()})
            if tipo == "FEED" and b"<item>" in b:
                l["POSTS"] = ler_feed(b)
            else:
                l["PAGINA"] = ler_html(b, destino or url)
        linhas.append(l)
        print(dom, l.get("ROBOTS"), l.get("HTTP"), l.get("BYTES"), len(l.get("POSTS") or []), flush=True)
        time.sleep(2)
    out = {"DATASET": "MEDIDA-ORDENS-V1", "EM": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "PORTAO": {k: portao.get(k) for k in ("EGRESS_GATE", "EGRESS_COUNTRY_CODE", "VOTOS_VALIDOS")},
           "PASTA_DOS_BYTES": str(saida), "ALVOS": linhas, "PEDIDOS_TOTAL": sum(x["PEDIDOS"] for x in linhas)}
    (AQUI / "MEDIDA-ORDENS-V1.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("pedidos", out["PEDIDOS_TOTAL"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
