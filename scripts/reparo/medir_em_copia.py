#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""R1 · MEDIR O REPARO NUMA COPIA DO LIVRO VIVO — nunca no vivo.

    py scripts/reparo/medir_em_copia.py --banca <pasta com a arvore + livros copiados>

A banca e uma arvore inteira (git archive + os ficheiros deste ramo) com os
livros do bot vivo copiados por cima (curadoria/*.json e
candidatas/FONTES-CANDIDATAS.json). Corre-se A PARTIR da banca: o worker e o
gatilho escrevem na RAIZ deles, que e a banca.

O ciclo e o do supervisor, sem discovery e sem ponte (nao se procura fonte
nova numa medicao de reparo):

    gatilho.reparar_encalhadas  ->  worker.correr  ->  repetir ate nada mudar

Escreve <banca>/curadoria/R1-MEDICAO-EM-COPIA.json com ANTES/DEPOIS por estado,
e as transicoes feitas nesta corrida por motivo.
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

VIVO = "source-curator-service-v1"


def _fatiar(GD, F, W, k: int, n: int) -> None:
    """Cada banca so ve as fontes da sua fatia (por anfitriao, sha256 estavel).
    As QUALIFY (YouTube / territorio) ficam so na fatia 0."""
    import hashlib
    from urllib.parse import urlparse
    livro = json.loads(W.CONTRATOS.read_text(encoding="utf-8"))["FONTES"]
    url = {c["SOURCE_ID"]: (c.get("ACQUISITION") or {}).get("INDEX_URL") or c.get("CANONICAL_ENTRY_URL")
           for c in livro}
    for x in json.loads(W.ALLOCATION.read_text(encoding="utf-8")).get("NOVAS", []):
        url.setdefault(x["SOURCE_ID"], x.get("URL"))

    def fatia(sid: str) -> int:
        h = urlparse(url.get(sid) or sid).netloc.lower().removeprefix("www.") or sid
        return int(hashlib.sha256(h.encode()).hexdigest(), 16) % n

    orig = GD.candidatas_a_reparar
    GD.candidatas_a_reparar = lambda agora, **kw: [c for c in orig(agora, **kw)
                                                   if fatia(c["SOURCE_ID"]) == k]
    if k != 0:
        GD.requalificar_se_a_prova_mudou = lambda agora: []
        F.recuperar_bloqueadas_por_defeito = lambda *a, **kw: []


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--banca", required=True)
    ap.add_argument("--voltas", type=int, default=200)
    ap.add_argument("--particao", default="0/1",
                    help="k/n: so as fontes cujo anfitriao cai na fatia k de n (bancas em paralelo; "
                         "o mesmo anfitriao fica sempre na mesma banca — cortesia e guarda DUPLICADA)")
    a = ap.parse_args(argv)
    banca = Path(a.banca).resolve()
    if VIVO in str(banca).replace("\\", "/"):
        print("RECUSO: a banca aponta para o bot vivo (%s)" % banca)
        return 2
    if Path(__file__).resolve().parents[2] != banca:
        print("corre-se a partir da banca: py <banca>/scripts/reparo/medir_em_copia.py --banca <banca>")
        return 2
    sys.path.insert(0, str(banca / "curadoria"))
    import fila as F                 # noqa: E402
    import gatilho_discovery as GD   # noqa: E402
    import lifecycle as LC           # noqa: E402
    import worker as W               # noqa: E402
    assert Path(F.FILA).resolve().is_relative_to(banca), F.FILA
    assert Path(LC.LIVRO).resolve().is_relative_to(banca), LC.LIVRO

    k, n = (int(x) for x in a.particao.split("/"))
    if n > 1:
        _fatiar(GD, F, W, k, n)
    n0 = len(json.loads(LC.LIVRO.read_text(encoding="utf-8"))["TRANSICOES"])
    antes = collections.Counter(LC.snapshot().values())
    inicio = datetime.now(timezone.utc).isoformat()
    print("ANTES", dict(antes), flush=True)
    voltas = []
    for i in range(a.voltas):
        rp = GD.reparar_encalhadas(datetime.now(timezone.utc))
        feitos = W.correr(pausa=0.3, verboso=True)
        voltas.append({"VOLTA": i + 1, "ENFILEIRADAS": len(rp["ENFILEIRADAS"]),
                       "RESTAM": rp["RESTAM"], "TAREFAS": len(feitos),
                       "YT": rp["QUALIFY_REQUALIFICADAS"]})
        print("VOLTA", voltas[-1], flush=True)
        if not rp["ENFILEIRADAS"] and not feitos and not rp["QUALIFY_REQUALIFICADAS"]:
            break
    depois = collections.Counter(LC.snapshot().values())
    novas = json.loads(LC.LIVRO.read_text(encoding="utf-8"))["TRANSICOES"][n0:]
    fim = datetime.now(timezone.utc).isoformat()
    out = {"DATASET": "R1-MEDICAO-EM-COPIA", "BANCA": str(banca), "PARTICAO": a.particao, "INICIO": inicio, "FIM": fim,
           "ANTES": dict(antes), "DEPOIS": dict(depois),
           "READY_ANTES": antes[LC.READY_FOR_COLLECTION], "READY_DEPOIS": depois[LC.READY_FOR_COLLECTION],
           "VOLTAS": voltas, "TRANSICOES_NOVAS": len(novas),
           "FILA": F.metricas()}
    (banca / "curadoria" / "R1-MEDICAO-EM-COPIA.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print("DEPOIS", dict(depois))
    print("READY %d -> %d" % (out["READY_ANTES"], out["READY_DEPOIS"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
