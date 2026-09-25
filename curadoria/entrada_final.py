# -*- coding: utf-8 -*-
"""A ENTRADA NO ENDERECO FINAL — o contrato deixa de gastar o teto em saltos (AJUSTES-MICRO, 25/09).

    py curadoria/entrada_final.py --saltos=<SALTOS.json de medir_saltos.py>
        --contratos=<italy_contracts_curator.json> --observacoes=<observations.ndjson> [--aplicar] [--saida=...]

MEDIDO no MICRO-V3 e na 2.a onda: `www.etvilloresi.it` -> `etvilloresi.it` gastou 2 dos 5 pedidos
do teto D38 em cada corrida (o robots das duas origens e o salto do indice), e a Villoresi colheu 1
materia em vez de 3. O teto conta CADA pedido — esta certo e nao se mexe. O que se corrige e a
ENTRADA do contrato: apontar ja para a origem onde o site acaba.

So se propoe com PROVA, e a prova e toda do que ja esta guardado (sem rede):
  1. SALTO DE ORIGEM medido: o transporte leu o robots de duas origens na mesma corrida
     (`medir_saltos.py`: SALTO_DE_ORIGEM, ORIGEM_FINAL);
  2. o LINK_PATTERN do contrato ACEITA pelo menos um endereco de materia JA COLHIDO nessa origem final
     (livro de observacoes do coletor) — senao a entrada nova nao acharia nada, e nao se propoe.
Aplica-se pela PORTA do reparo (`reparar_contrato.aplicar`): guarda a ACQUISITION anterior, passa pelo
validador da casa e marca PRECISA_DE_REMEDIR — o canario seguinte e que decide; isto nunca promove.
O salto no proprio robots.txt (cia.it: 2 pedidos ao robots, 404 no fim) NAO se corrige por aqui.
"""
from __future__ import annotations

import copy
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))


def _origem(u: str) -> str:
    p = urlparse(u)
    return "%s://%s" % (p.scheme, p.netloc)


def observados_por_fonte(obs_path: Path) -> dict:
    out = {}
    for l in obs_path.read_text(encoding="utf-8").splitlines():
        try:
            d = json.loads(l)
        except ValueError:
            continue
        u = d.get("SOURCE_URL")
        if d.get("SOURCE_ID") and u and d.get("DOCUMENT_ID"):
            out.setdefault(d["SOURCE_ID"], set()).add(u)
    return out


def propor(contrato: dict, medida: dict, colhidos: set) -> dict:
    """Proposta PADRAO_NOVO (so muda a INDEX_URL) ou {"DESFECHO": "SEM_PROPOSTA", "PORQUE": ...}. Pura."""
    aq = contrato.get("ACQUISITION") or {}
    iu, pad = aq.get("INDEX_URL"), aq.get("LINK_PATTERN")
    if not medida.get("SALTO_DE_ORIGEM") or not medida.get("ORIGEM_FINAL"):
        return {"DESFECHO": "SEM_PROPOSTA", "PORQUE": "sem salto de origem medido"}
    if not iu or not pad:
        return {"DESFECHO": "SEM_PROPOSTA", "PORQUE": "contrato sem INDEX_URL/LINK_PATTERN"}
    final = medida["ORIGEM_FINAL"]
    if _origem(iu) == final:
        return {"DESFECHO": "SEM_PROPOSTA", "PORQUE": "a entrada ja esta na origem final"}
    nova = final + iu[len(_origem(iu)):]
    prova = sorted(u for u in colhidos if _origem(u) == final and re.match(pad, u))
    if not prova:
        return {"DESFECHO": "SEM_PROPOSTA",
                "PORQUE": "o LINK_PATTERN nao aceita nenhum endereco ja colhido em %s — a entrada nova nao se prova sem rede" % final}
    return {"DESFECHO": "PADRAO_NOVO", "INDEX_URL": nova, "LINK_PATTERN": pad,
            "COMO": "ENTRADA_NO_ENDERECO_FINAL: salto de origem %s -> %s medido no livro de corridas; so a INDEX_URL muda"
                    % (_origem(iu), final),
            "ACQUISITION_ANTERIOR": copy.deepcopy(aq),
            "ENTRADA": nova, "ITEM_LIDO": prova[0], "ALVOS_NA_LISTAGEM": prova[:3],
            "PORQUE": "o transporte leu o robots de %s e de %s na mesma corrida; %d pedido(s) por corrida gastos no salto"
                      % (_origem(iu), final, max(medida.get("DESPERDICIO_POR_CORRIDA") or [0]))}


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    a = dict(x[2:].split("=", 1) for x in argv if x.startswith("--") and "=" in x)
    saltos = {l["SOURCE_ID"]: l for l in json.loads(Path(a["saltos"]).read_text(encoding="utf-8"))["FONTES"]}
    cpath = Path(a["contratos"])
    livro = json.loads(cpath.read_text(encoding="utf-8"))
    colhidos = observados_por_fonte(Path(a["observacoes"]))
    import reparar_contrato as RC                          # noqa: E402 — a porta do reparo
    out, novos = [], {}
    for c in livro["FONTES"]:
        m = saltos.get(c["SOURCE_ID"])
        if not m:
            continue
        p = propor(c, m, colhidos.get(c["SOURCE_ID"], set()))
        linha = {"SOURCE_ID": c["SOURCE_ID"], "INDEX_URL_ANTES": (c.get("ACQUISITION") or {}).get("INDEX_URL"),
                 **{k: p.get(k) for k in ("DESFECHO", "INDEX_URL", "PORQUE", "ITEM_LIDO")}}
        if p["DESFECHO"] == "PADRAO_NOVO":
            novos[c["SOURCE_ID"]] = RC.aplicar(c, p)                # rebenta se o validador da casa reprovar
            linha["SHA256_DEPOIS"] = novos[c["SOURCE_ID"]]["SOURCE_CONTRACT_HASH"]
        out.append(linha)
    if "--aplicar" in argv and novos:
        livro["FONTES"] = [novos.get(c["SOURCE_ID"], c) for c in livro["FONTES"]]
        tmp = cpath.with_suffix(".tmp")
        tmp.write_text(json.dumps(livro, ensure_ascii=False, indent=1), encoding="utf-8")
        tmp.replace(cpath)
    r = {"DATASET": "ENTRADA-FINAL", "APLICADO": "--aplicar" in argv and bool(novos), "CONTRATOS": str(cpath),
         "PROPOSTAS": [l for l in out if l["DESFECHO"] == "PADRAO_NOVO"],
         "SEM_PROPOSTA": [l for l in out if l["DESFECHO"] != "PADRAO_NOVO"]}
    s = json.dumps(r, ensure_ascii=False, indent=1) + "\n"
    if a.get("saida"):
        Path(a["saida"]).write_text(s, encoding="utf-8")
    print(s)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
