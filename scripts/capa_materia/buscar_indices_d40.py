# -*- coding: utf-8 -*-
"""ALVOS-NOVOS · 1 pedido por DOMINIO: o indice de cada fonte da 1.a onda.

    py scripts/capa_materia/buscar_indices_d40.py <pasta-de-saida>

NAO e o robo coletor (D41.3): nao ha fila, nao ha materia, nao ha escrita em livro nenhum.
So o indice, e so depois de o portao de egresso por consenso dar PASS IT.

  * 18 fontes em 14 dominios. A cia.it tem 5 fontes; pede-se SO o indice da primeira delas na
    ordem da coorte (IT-T7-112) — e a unica que, com o teto D38, chegaria a pedir materias
    (robots 1 + indice 1 + 3 materias = 5). As outras 4 ficam NAO_MEDIDO.
  * robots.txt NAO e re-pedido (para caber em 1 pedido por dominio): a 1.a onda (BC5, 24/09)
    passou pelo robots do coletor para estas 18 paginas. Declarado no resultado.
  * sem retry. Um redireccionamento conta como pedido e fica registado.
"""
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.request
from urllib.parse import urlsplit

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
sys.path.insert(0, os.path.join(RAIZ, "superficie"))
import rede  # noqa: E402

SAIDA = sys.argv[1]
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/140.0.0.0 Safari/537.36")  # o mesmo do coletor (coleta/italy_pilot_collect.mjs:75)


def dominio(host):
    partes = host.lower().split(".")
    return ".".join(partes[-2:])


coorte = json.load(open(os.path.join(RAIZ, "ferramentas", "big_collection", "COORTE-BIG-COLLECTION-V1.json"),
                        encoding="utf-8"))["COORTE"]
portao = rede.portao_de_egresso("IT")
if portao["EGRESS_GATE"] != "PASS":
    print("PORTAO FECHADO", portao.get("PORQUE_BLOQUEADO"))
    sys.exit(2)

os.makedirs(SAIDA, exist_ok=True)
vistos, res = {}, []
for f in coorte:
    sid, url = f["SOURCE_ID"], f["INDEX_URL"]
    dom = dominio(urlsplit(url).hostname)
    if dom in vistos:
        res.append({"SOURCE_ID": sid, "INDEX_URL": url, "DOMINIO": dom, "ESTADO": "NAO_MEDIDO",
                    "PORQUE": "1 pedido por dominio: o indice de %s ja foi o pedido deste dominio" % vistos[dom]})
        continue
    vistos[dom] = sid
    linha = {"SOURCE_ID": sid, "INDEX_URL": url, "DOMINIO": dom, "PEDIDO_EM": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=40) as r:
            corpo = r.read()
            linha.update({"HTTP": r.status, "URL_FINAL": r.geturl(), "REDIRECIONOU": r.geturl() != url})
    except urllib.error.HTTPError as e:
        corpo = b""
        linha.update({"HTTP": e.code, "ESTADO": "FALHOU"})
    except Exception as e:  # noqa: BLE001
        corpo = b""
        linha.update({"HTTP": None, "ESTADO": "FALHOU", "ERRO": repr(e)[:200]})
    if corpo:
        caminho = os.path.join(SAIDA, sid + ".html")
        open(caminho, "wb").write(corpo)
        linha.update({"ESTADO": "OK", "BYTES": len(corpo), "SHA256": hashlib.sha256(corpo).hexdigest(),
                      "FICHEIRO": caminho})
    res.append(linha)
    print(sid, dom, linha.get("HTTP"), linha.get("BYTES"), flush=True)
    time.sleep(2)

out = {"DATASET": "INDICES-D40-V1", "PORTAO": {k: portao.get(k) for k in
                                                ("EGRESS_GATE", "EGRESS_COUNTRY_CODE", "VOTOS_VALIDOS")},
       "PEDIDOS_POR_DOMINIO_MAX": 1, "ROBOTS": "nao re-pedido; verificado pelo coletor na 1.a onda (BC5, 24/09)",
       "FONTES": res}
open(os.path.join(AQUI, "INDICES-D40-V1.json"), "w", encoding="utf-8", newline="\n").write(
    json.dumps(out, ensure_ascii=False, indent=1) + "\n")
print("PEDIDOS", len(vistos))
