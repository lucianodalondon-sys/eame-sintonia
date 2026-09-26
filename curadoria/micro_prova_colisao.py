#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MICRO-PROVA × ONDA — nenhum domínio da micro-prova (ou da sonda) pode estar na RODADA 1 da onda seguinte, nem ter
sido colhido pelo coletor nas últimas 24 h. Sem rede: lê ficheiros. Sai com código 1 se houver colisão.

    py curadoria/micro_prova_colisao.py --rodadas=<C2-ONDA4/rodadas.txt> --lote=<LOTE.json> [--sonda=IT-..,IT-..]

Domínio = o registável (o mesmo corte de `janelas68_medir`: `regione.veneto.it`, `fitogest.imagelinenetwork.com`
-> `imagelinenetwork.com`). «Colhido nas últimas 24 h» lê-se nas OBSERVAÇÕES do coletor
(`data/collection-ledger/italy/observations.ndjson`, CAPTURED_AT + SOURCE_URL) — NÃO em `runs.ndjson`:
medido a 26/09, 0 das 155 corridas têm `PEDIDOS_POR_HOST`, e contar por lá dava «0 domínios» às cegas.
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlparse

RAIZ = Path(__file__).resolve().parents[1]
OBS = RAIZ / "data" / "collection-ledger" / "italy" / "observations.ndjson"
CANDIDATAS = RAIZ / "candidatas" / "FONTES-CANDIDATAS.json"
CONTRATOS = RAIZ / "curadoria" / "italy_contracts_curator.json"
SUFIXOS = {"campania", "marche", "veneto", "toscana", "sardegna", "fvg", "vda", "sicilia", "umbria", "puglia",
           "lombardia", "molise", "calabria", "basilicata", "liguria", "lazio", "piemonte", "abruzzo", "trentino",
           "bz", "gov", "ra"}


def dominio(host: str) -> str:
    p = (host or "").lower().removeprefix("www.").split(".")
    return ".".join(p[-3:]) if len(p) >= 3 and p[-2] in SUFIXOS else ".".join(p[-2:])


def rodada1(texto: str) -> dict:
    m = re.search(r"RODADA 1:.*?(?=\nRODADA 2:|\Z)", texto, re.S)
    if not m:
        raise SystemExit("rodadas.txt sem RODADA 1 — nao se adivinha")
    return {dominio(x.group(1)): int(x.group(2)) for x in re.finditer(r"^\s+(\S+\.\S+)\s+(\d+)\s", m.group(0), re.M)}


def colhidos(linhas, agora: datetime, horas: int = 24) -> dict:
    lim, out = agora - timedelta(hours=horas), {}
    for l in linhas:
        try:
            o = json.loads(l)
            t = datetime.fromisoformat((o.get("CAPTURED_AT") or "").replace("Z", "+00:00"))
        except Exception:        # noqa: BLE001 — linha estragada nao conta como colheita
            continue
        if t >= lim and o.get("SOURCE_URL"):
            d = dominio(urlparse(o["SOURCE_URL"]).netloc)
            out[d] = out.get(d, 0) + 1
    return out


def verificar(alvos: dict, r1: dict, recentes: dict) -> list[dict]:
    """alvos = {id: url}. Devolve as colisões (vazio = pode correr)."""
    out = []
    for i, u in alvos.items():
        d = dominio(urlparse(u or "").netloc)
        if d in r1:
            out.append({"ID": i, "DOMINIO": d, "PORQUE": "na RODADA 1 da onda (%d pedidos previstos)" % r1[d]})
        if d in recentes:
            out.append({"ID": i, "DOMINIO": d, "PORQUE": "colhido pelo coletor nas ultimas 24 h (%d documentos)" % recentes[d]})
    return out


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    a = dict(x[2:].split("=", 1) for x in argv if x.startswith("--") and "=" in x)
    r1 = rodada1(Path(a["rodadas"]).read_text(encoding="utf-8"))
    # --vivo=<pasta>: le as observacoes e a porta DO VIVO. Sem isto le as desta arvore — numa copia antiga do
    # ramo as 24 h vinham «0 dominios» as cegas (medido no LOTE 2B: 521 linhas aqui, 678 no vivo).
    raiz = Path(a["vivo"]) if a.get("vivo") else RAIZ
    obs, cands = raiz / OBS.relative_to(RAIZ), raiz / CANDIDATAS.relative_to(RAIZ)
    linhas = obs.read_text(encoding="utf-8", errors="replace").splitlines()
    recentes = colhidos(linhas, datetime.now(timezone.utc))
    alvos = {}
    if a.get("lote"):
        lote = json.loads(Path(a["lote"]).read_text(encoding="utf-8"))
        for x in lote.get("ALVOS", []):                 # LOTE-MONITORIZACAO (medir_contagens): alvos por URL
            alvos[x["ID"]] = x["URL"]
        if lote.get("CANDIDATAS") or lote.get("FICHAS_NOVAS"):
            import colher_prova_territorio as CPT     # a mesma leitura do lote que a colheita usa (inclui FICHAS_NOVAS)
            fichas = CPT.fichas_do_lote(lote, json.loads(cands.read_text(encoding="utf-8"))["CANDIDATAS"])
            for c, f in fichas.items():
                alvos[c] = f["URL"]
    if a.get("sonda"):
        contratos = {c["SOURCE_ID"]: c for c in json.loads(CONTRATOS.read_text(encoding="utf-8"))["FONTES"]}
        sem = []
        for s in a["sonda"].split(","):
            c = contratos.get(s)
            if not c:
                sem.append({"ID": s, "DOMINIO": None, "PORQUE": "sem contrato em %s — nao se sabe o endereco" % CONTRATOS})
                continue
            alvos[s] = (c.get("ACQUISITION") or {}).get("INDEX_URL") or c.get("CANONICAL_ENTRY_URL")
    else:
        sem = []
    col = verificar(alvos, r1, recentes) + sem
    print(json.dumps({"ALVOS": len(alvos), "RODADA1_DOMINIOS": len(r1), "OBSERVACOES": "%s (%d linhas)" % (obs, len(linhas)), "COLHIDOS_24H_DOMINIOS": len(recentes),
                      "COLISOES": col, "PODE_CORRER": not col}, ensure_ascii=False, indent=1))
    return 1 if col else 0


if __name__ == "__main__":
    raise SystemExit(main())
