# -*- coding: utf-8 -*-
"""CONTRATOS-AJUSTE · 1 pedido a istat.it para confirmar que o novo alvo e MATERIA.

    py scripts/capa_materia/confirmar_istat.py <pasta-de-saida>

NAO e o robo coletor (D41.3): 1 endereco, sem fila, sem livro. So depois do portao de egresso
por consenso dar PASS IT. O retrato (capa ou materia) e feito depois, sem rede, pelo mesmo
`retratoDoHtml` que o coletor usa (coleta/retrato_html.mjs).
"""
import hashlib
import json
import os
import sys
import time
import urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
sys.path.insert(0, os.path.join(RAIZ, "superficie"))
import rede  # noqa: E402

URL = "https://www.istat.it/comunicato-stampa/linnovazione-nelle-imprese-anni-2022-2024/"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/140.0.0.0 Safari/537.36")
SAIDA = sys.argv[1]

portao = rede.portao_de_egresso("IT")
if portao["EGRESS_GATE"] != "PASS":
    print("PORTAO FECHADO", portao.get("PORQUE_BLOQUEADO"))
    sys.exit(2)
os.makedirs(SAIDA, exist_ok=True)
with urllib.request.urlopen(urllib.request.Request(URL, headers={"User-Agent": UA}), timeout=40) as r:
    corpo, status, final = r.read(), r.status, r.geturl()
caminho = os.path.join(SAIDA, "istat-comunicato.html")
open(caminho, "wb").write(corpo)
out = {"DATASET": "CONFIRMACAO-ISTAT-V1", "PEDIDO_EM": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
       "PORTAO": {k: portao.get(k) for k in ("EGRESS_GATE", "EGRESS_COUNTRY_CODE", "VOTOS_VALIDOS")},
       "PEDIDOS": 1, "URL": URL, "HTTP": status, "URL_FINAL": final, "BYTES": len(corpo),
       "SHA256": hashlib.sha256(corpo).hexdigest(), "FICHEIRO": caminho}
open(os.path.join(AQUI, "CONFIRMACAO-ISTAT-V1.json"), "w", encoding="utf-8", newline="\n").write(
    json.dumps(out, ensure_ascii=False, indent=1) + "\n")
print(status, len(corpo), final)
