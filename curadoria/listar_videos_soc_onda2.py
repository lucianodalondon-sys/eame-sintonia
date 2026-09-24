#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SOC-ONDA2 · a fase `canal-youtube` dos 11 canais novos, corrida onde a chave vive.

    py curadoria/listar_videos_soc_onda2.py            # mostra o pedido (sem rede)
    py curadoria/listar_videos_soc_onda2.py --listar   # chave NO AMBIENTE (workflow curator-youtube-soc-onda2)

A fase do contrato destes canais é `canal-youtube` (`youtube.channel.discovery`, API
oficial). A chave vive só no GitHub Actions — por isso esta metade do canário corre lá.
Guarda SÓ identidade: SOURCE_ID, channel_id, VIDEO_ID (D20: nada de título, data ou
contagem da API no repositório). Mesma forma do SOC5 (`listar_videos_canario.py`).
"""
from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
for _p in ("curadoria", "coleta", "leis", "regras", "guarda", ""):
    q = str(RAIZ / _p) if _p else str(RAIZ)
    if q not in sys.path:
        sys.path.append(q)

PEDIDO = RAIZ / "curadoria" / "PEDIDO-CANARIO-YOUTUBE-SOC-ONDA2.json"
REGISTO = RAIZ / "curadoria" / "CANARIO-YOUTUBE-SOC-ONDA2-VIDEOS.json"
POR_CANAL = 2
CAPACIDADE = "youtube.channel.discovery"
RE_VIDEO = re.compile(r"^[A-Za-z0-9_-]{11}$")


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
    canais = json.loads(PEDIDO.read_text(encoding="utf-8"))["CANAIS"]
    for c in canais:
        print("%-11s %-4s %s" % (c["SOURCE_ID"], c["TERRITORY"], c["CHANNEL_ID"]))
    if "--listar" not in argv:
        return 0
    import scrap_executor as sx
    v = sx.CHECK("YOUTUBE", CAPACIDADE)
    print("CHECK %s" % v.get("STATE"))
    if not v.get("CAN"):
        print("NAO_CORREU: a chave nao esta NESTE ambiente. Corre no workflow curator-youtube-soc-onda2.")
        return 3
    run_id = "SOC-ONDA2-LISTA-%s" % (os.environ.get("GITHUB_RUN_ID") or "local")
    linhas = listar(canais, run_id)
    REGISTO.write_text(json.dumps({
        "DATASET": "CANARIO-YOUTUBE-SOC-ONDA2-VIDEOS",
        "LISTADO_EM": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "RUN_ID": run_id,
        "LEI": "so identidade (SOURCE_ID, territorio, channel_id, VIDEO_ID); sem titulo, data ou contagem (D20)",
        "LINHAS": linhas}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("LISTADOS %d videos em %d canais" % (sum(len(l["VIDEO_IDS"]) for l in linhas), len(linhas)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
