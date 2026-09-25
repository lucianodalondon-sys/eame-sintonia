# -*- coding: utf-8 -*-
"""Quantos pedidos cada fonte gasta em SALTOS (redirecionamentos) antes das materias — so leitura, sem rede.

    py ferramentas/rendimento/medir_saltos.py --runs=<runs.ndjson> --estado=<ESTADO.json>[,<ESTADO.json>...] [--saida=...]

Liga cada corrida a sua fonte pelo RUN_ID dos ficheiros de estado das ondas (BC5, MICRO, ONDA2).
Numa corrida sem desperdicio o teto gasta-se assim: 1 robots + 1 indice + N materias.
    DESPERDICIO = pedidos da corrida - (1 + 1 + DETAIL_REQUESTS)
Os saltos de ORIGEM (www.x -> x, http -> https, outro host) deixam marca propria: o transporte le o
robots de CADA origem por onde passa (`CORTESIA.ROBOTS`), por isso mais de uma origem no mesmo dominio =
o indice redireciona. A origem FINAL e a que nao e a do INDEX_URL do contrato.
Nao se pede nada a rede: o endereco final vem do que o transporte ja registou.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from urllib.parse import urlparse


def _origem(u: str) -> str:
    p = urlparse(u)
    return "%s://%s" % (p.scheme, p.netloc)


def corridas(runs_path: Path) -> dict:
    out = {}
    for l in runs_path.read_text(encoding="utf-8").splitlines():
        try:
            d = json.loads(l)
        except ValueError:
            continue
        if d.get("RUN_ID"):
            out[d["RUN_ID"]] = d
    return out


def medir_corrida(resumo: dict) -> dict:
    c = resumo.get("contadores") or {}
    cort = resumo.get("CORTESIA") or {}
    pedidos = sum((cort.get("PEDIDOS_POR_DOMINIO") or cort.get("PEDIDOS_POR_HOST") or {}).values())
    origens = sorted((cort.get("ROBOTS") or {}).keys())
    det = c.get("DETAIL_REQUESTS") or 0
    return {"PEDIDOS": pedidos, "ROBOTS_ORIGENS": origens, "DETAIL_REQUESTS": det,
            "DESPERDICIO": max(0, pedidos - 2 - det) if pedidos else 0,
            "RECUSAS_TETO": (c.get("COURTESY_REFUSALS") or {}).get("TETO_DOMINIO", 0)
            + (c.get("COURTESY_REFUSALS") or {}).get("TETO_POR_HOST", 0)}


def medir(runs: dict, estados: list[tuple[str, dict]], index_url: dict) -> dict:
    por_fonte = {}
    for onda, e in estados:
        for f in e.get("FONTES", []):
            rid = f.get("RUN_ID")
            if not rid or rid not in runs:
                continue
            m = medir_corrida(runs[rid])
            por_fonte.setdefault(f["SOURCE_ID"], []).append(dict(m, ONDA=onda, RUN_ID=rid))
    linhas = []
    for s, ms in sorted(por_fonte.items()):
        iu = index_url.get(s)
        orig_contrato = _origem(iu) if iu else None
        outras = sorted({o for m in ms for o in m["ROBOTS_ORIGENS"]} - ({orig_contrato} if orig_contrato else set()))
        salto_de_origem = bool(orig_contrato) and any(len(m["ROBOTS_ORIGENS"]) > 1 for m in ms) and len(outras) == 1
        proposta = (outras[0] + iu[len(orig_contrato):]) if salto_de_origem else None
        linhas.append({"SOURCE_ID": s, "INDEX_URL_DO_CONTRATO": iu, "CORRIDAS": ms,
                       "DESPERDICIO_POR_CORRIDA": [m["DESPERDICIO"] for m in ms],
                       "SALTO_DE_ORIGEM": salto_de_origem, "ORIGEM_FINAL": outras[0] if salto_de_origem else None,
                       "INDEX_URL_PROPOSTO": proposta,
                       "RECUSAS_TETO": sum(m["RECUSAS_TETO"] for m in ms)})
    return {"FONTES": linhas,
            "COM_SALTO_DE_ORIGEM": [l["SOURCE_ID"] for l in linhas if l["SALTO_DE_ORIGEM"]],
            "COM_DESPERDICIO_SEM_SALTO_DE_ORIGEM": [l["SOURCE_ID"] for l in linhas
                                                     if not l["SALTO_DE_ORIGEM"] and max(l["DESPERDICIO_POR_CORRIDA"]) > 0],
            "PEDIDOS_DESPERDICADOS_TOTAL": sum(sum(l["DESPERDICIO_POR_CORRIDA"]) for l in linhas)}


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    a = dict(x[2:].split("=", 1) for x in argv if x.startswith("--") and "=" in x)
    estados = [(Path(p).stem, json.loads(Path(p).read_text(encoding="utf-8"))) for p in a["estado"].split(",")]
    index_url = json.loads(Path(a["index_url"]).read_text(encoding="utf-8")) if a.get("index_url") else {}
    r = medir(corridas(Path(a["runs"])), estados, index_url)
    s = json.dumps(r, ensure_ascii=False, indent=1) + "\n"
    if a.get("saida"):
        Path(a["saida"]).write_text(s, encoding="utf-8")
    print(s)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
