#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SOC5 · OS VÍDEOS DO CANÁRIO — 5 canais já roteados ao Scrap, 2 vídeos cada.

    py curadoria/listar_videos_canario.py            # a escolha dos canais (sem rede)
    py curadoria/listar_videos_canario.py --listar   # pede os 2 vídeos mais recentes (chave NO AMBIENTE)

Os 50 canais da tabela do coletor passaram a ser colhidos pelo Scrap (SOC2/SOC4). Um
canário real precisa de vídeos concretos, e listar os vídeos de um canal é uma
capacidade QUE O SCRAP JÁ TEM — `youtube.channel.discovery` (`playlistItems.list`,
API oficial, 1 unidade). A chave vive no GitHub Actions; por isso a lista faz-se lá
(workflow `curator-youtube-canario`) e o resto do canário (áudio público, ASR,
Admissão) faz-se nesta máquina, pela VPN IT, com um banco descartável.

A ESCOLHA: um canal por território, nos territórios que TÊM régua de Admissão nesta
linha (a régua T8 vive noutra branch, `youtube-regua-t8-v1`), o primeiro SOURCE_ID de
cada um. Escolha fixa, sem sorteio: o mesmo comando dá a mesma lista.

O QUE SE GUARDA: só identidade — SOURCE_ID, território, channel_id e os VIDEO_ID.
Títulos, datas e contagens são dado da API (regra dos 30 dias, D20) e não entram aqui.
"""
from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
for _p in ("curadoria", "candidatas", "coleta", "leis", "admissao", "regras", "ferramentas",
           "medidas", "guarda", "pedido", "orquestrador", ""):
    q = str(RAIZ / _p) if _p else str(RAIZ)
    if q not in sys.path:
        sys.path.append(q)

TABELA = RAIZ / "regras" / "italy_contracts_onboarded.json"
REGISTO = RAIZ / "curadoria" / "CANARIO-YOUTUBE-SOC5-VIDEOS.json"
TERRITORIOS = ("T2", "T5", "T7", "T10", "T12")
POR_CANAL = 2
CAPACIDADE = "youtube.channel.discovery"
RE_VIDEO = re.compile(r"^[A-Za-z0-9_-]{11}$")


def escolher(tabela: dict | None = None) -> list[dict]:
    d = json.loads(TABELA.read_text(encoding="utf-8")) if tabela is None else tabela
    canais = sorted((x for x in d["FONTES"] if x.get("SOURCE_NATIVE_ID_KIND") == "YOUTUBE_CHANNEL_ID"),
                    key=lambda x: (x["TERRITORY"], x["SOURCE_ID"]))
    fora = []
    for t in TERRITORIOS:
        c = next((x for x in canais if x["TERRITORY"] == t), None)
        if c:
            fora.append({"SOURCE_ID": c["SOURCE_ID"], "TERRITORY": t, "CHANNEL_ID": c["SOURCE_NATIVE_ID"]})
    return fora


def _video_id(o: dict) -> str | None:
    for k in ("NATIVE_ID", "VIDEO_ID", "video_id"):
        v = o.get(k)
        if isinstance(v, str) and RE_VIDEO.match(v):
            return v
    m = re.search(r"[?&]v=([A-Za-z0-9_-]{11})", str(o.get("URL") or ""))
    return m.group(1) if m else None


def listar(canais: list[dict], run_id: str, collect=None) -> list[dict]:
    if collect is None:
        import scrap_executor as sx
        collect = sx.COLLECT
    fora = []
    for c in canais:
        objetos, trace = collect(platform="YOUTUBE", capability=CAPACIDADE, run_id=run_id,
                                 channel_id=c["CHANNEL_ID"], limit=POR_CANAL)
        ids = [v for v in (_video_id(o) for o in (objetos or [])) if v][:POR_CANAL]
        fora.append(dict(c, VIDEO_IDS=ids, ESTADO="LISTADO" if ids else "VAZIO",
                         PORQUE=(trace or {}).get("WHY") or (trace or {}).get("RESULT")))
    return fora


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    canais = escolher()
    for c in canais:
        print("%-11s %-4s %s" % (c["SOURCE_ID"], c["TERRITORY"], c["CHANNEL_ID"]))
    if "--listar" not in argv:
        return 0
    import scrap_executor as sx
    v = sx.CHECK("YOUTUBE", CAPACIDADE)
    print("CHECK %s" % v.get("STATE"))
    if not v.get("CAN"):
        print("NAO_CORREU: a chave nao esta NESTE ambiente. Corre no workflow curator-youtube-canario.")
        return 3
    run_id = "SOC5-LISTA-%s" % (os.environ.get("GITHUB_RUN_ID") or "local")
    linhas = listar(canais, run_id)
    REGISTO.write_text(json.dumps({
        "DATASET": "CANARIO-YOUTUBE-SOC5-VIDEOS",
        "LISTADO_EM": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "RUN_ID": run_id,
        "LEI": "so identidade (SOURCE_ID, territorio, channel_id, VIDEO_ID); sem titulo, data ou contagem (D20)",
        "LINHAS": linhas}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("LISTADOS %d videos em %d canais" % (sum(len(l["VIDEO_IDS"]) for l in linhas), len(linhas)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
