#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SONDA DE UM PEDIDO — o site aceita a nossa saída IT? (BLOQUEADAS-DESTRAVAR, 26/09)

Para as fontes paradas por LIGAÇÃO (Coldiretti ×5 + Unaprol: `WinError 10054`; ANGA: também TLS; CNR IT-T5-006:
«robots não pode ser lido»). NÃO é uma rota nova nem um coletor: faz **1 pedido por fonte**, ao `robots.txt` do
host da entrada do contrato — o primeiro pedido de qualquer visita honesta —, com o MESMO leitor do canário
(`canario.buscar`: UA, TLS, timeout e teto da casa). Não lê a página, não guarda bytes, não escreve em livro nenhum.

O QUE OS RECIBOS JÁ MOSTRAM (LIFECYCLE-EVIDENCE do vivo): o 1.º pedido de uma rajada passa (canário 200 OK em
22/09 17:30 e 23/09 00:26) e os seguintes, minutos depois, levam `10054` — em TODOS os hosts da Coldiretti ao
mesmo tempo. Cara de limite por organização. Por isso a sonda faz, por RONDA, no máximo 1 pedido por ORGANIZAÇÃO
(`coldiretti.it` e os subdomínios contam como uma), e espera entre rondas.

Portão de egresso IT por consenso (`superficie/rede.portao_de_egresso`) antes de cada ronda e no fim; sem PASS
não se pede nada. Rede só quando o coordenador a corre com a VPN IT.

    py curadoria/sonda_um_pedido.py --fontes=IT-T5-006,IT-T7-045,IT-T7-050,IT-T7-051,IT-T7-052,IT-T7-053,IT-T7-058 \\
        [--pausa-ronda=1200] [--saida=SONDA-UM-PEDIDO.json]

Resultado por fonte: OK (robots lido: HTTP 200 ou 404 = não publica) · RECUSA_HTTP (401/403/429/5xx) ·
FECHO_DE_LIGACAO (10054/10053/reset) · TLS · SEM_RESPOSTA (timeout/DNS) · OUTRO. Nada disto promove a fonte:
com OK, o coordenador re-enfileira a tarefa pelo caminho canónico e o canário decide.
"""
from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))
sys.path.insert(0, str(RAIZ / "superficie"))

CONTRATOS = RAIZ / "curadoria" / "italy_contracts_curator.json"
SUFIXOS_ORG = ("coldiretti.it",)          # subdomínios que são UMA organização (limite partilhado)


def organizacao(host: str) -> str:
    h = host.lower().removeprefix("www.")
    for s in SUFIXOS_ORG:
        if h == s or h.endswith("." + s):
            return s
    return h


def classificar(status: int, erro: str) -> str:
    e = (erro or "").lower()
    if status in (200, 404):
        return "OK"
    if status:
        return "RECUSA_HTTP"
    if "10054" in e or "10053" in e or "reset" in e or "cancelamento" in e or "forcibly" in e:
        return "FECHO_DE_LIGACAO"
    if "ssl" in e or "tls" in e or "handshake" in e:
        return "TLS"
    if "timed out" in e or "timeout" in e or "getaddrinfo" in e or "name or service" in e:
        return "SEM_RESPOSTA"
    return "OUTRO"


def rondas(fontes: list[dict]) -> list[list[dict]]:
    """Cada ronda tem no máximo 1 fonte por organização; a ordem de entrada mantém-se."""
    resto, out = list(fontes), []
    while resto:
        vistas, ronda, fica = set(), [], []
        for f in resto:
            (fica if f["ORGANIZACAO"] in vistas else ronda).append(f)
            vistas.add(f["ORGANIZACAO"])
        out.append(ronda)
        resto = fica
    return out


def planear(ids: list[str], contratos: dict) -> list[dict]:
    fontes = []
    for sid in ids:
        c = contratos.get(sid)
        if not c:
            raise SystemExit("sem contrato no livro: %s" % sid)
        entrada = (c.get("ACQUISITION") or {}).get("INDEX_URL") or c.get("CANONICAL_ENTRY_URL")
        p = urlparse(entrada)
        fontes.append({"SOURCE_ID": sid, "ENTRADA": entrada, "HOST": p.netloc,
                       "ORGANIZACAO": organizacao(p.netloc),
                       "PEDIDO": "%s://%s/robots.txt" % (p.scheme or "https", p.netloc)})
    return fontes


def correr(fontes, buscar, portao, dormir=time.sleep, pausa_ronda=1200.0, pausa_pedido=60.0) -> dict:
    """Executa as rondas. `buscar(url)->(status, bytes, erro)`, `portao()->dict` — injectados (testáveis sem rede)."""
    registo, vigias = [], []
    plano = rondas(fontes)
    for n, ronda in enumerate(plano):
        v = portao()
        vigias.append({"ANTES_DA_RONDA": n + 1, "EGRESS_GATE": v.get("EGRESS_GATE")})
        if v.get("EGRESS_GATE") != "PASS":
            for f in [x for r in plano[n:] for x in r]:
                registo.append(dict(f, RESULTADO="NAO_MEDIDO", PORQUE="portao de egresso sem PASS IT"))
            break
        for i, f in enumerate(ronda):
            st, b, err = buscar(f["PEDIDO"])
            registo.append(dict(f, RONDA=n + 1, AT=datetime.now(timezone.utc).isoformat(), HTTP=st,
                                ERRO=(err or "")[:160], BYTES=len(b or b""), RESULTADO=classificar(st, err)))
            if i < len(ronda) - 1:
                dormir(pausa_pedido)
        if n < len(plano) - 1:
            dormir(pausa_ronda)
    vigias.append({"NO_FIM": True, "EGRESS_GATE": portao().get("EGRESS_GATE")})
    from collections import Counter
    return {"DATASET": "SONDA-UM-PEDIDO", "PEDIDOS": sum(1 for r in registo if r.get("RESULTADO") != "NAO_MEDIDO"),
            "RONDAS": len(plano), "VIGIAS": vigias,
            "POR_RESULTADO": dict(Counter(r["RESULTADO"] for r in registo)), "FONTES": registo}


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    a = dict(x[2:].split("=", 1) for x in argv if x.startswith("--") and "=" in x)
    ids = [s for s in a.get("fontes", "").split(",") if s]
    if not ids:
        print(__doc__)
        return 2
    import canario as CAN      # noqa: E402 — o leitor da casa
    import rede                # noqa: E402 — o portão de consenso
    contratos = {c["SOURCE_ID"]: c for c in json.loads(CONTRATOS.read_text(encoding="utf-8"))["FONTES"]}
    fontes = planear(ids, contratos)
    out = correr(fontes, CAN.buscar, lambda: rede.portao_de_egresso("IT"),
                 pausa_ronda=float(a.get("pausa-ronda", 1200)))
    s = json.dumps(out, ensure_ascii=False, indent=1) + "\n"
    Path(a.get("saida", "SONDA-UM-PEDIDO.json")).write_text(s, encoding="utf-8")
    print(json.dumps({k: out[k] for k in ("PEDIDOS", "RONDAS", "POR_RESULTADO", "VIGIAS")}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
