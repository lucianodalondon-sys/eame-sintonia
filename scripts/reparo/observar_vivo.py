#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""R1 · OBSERVAR O VIVO DEPOIS DA INSTALACAO — so le ficheiros, zero rede, zero escrita no vivo.

    py scripts/reparo/observar_vivo.py [--vivo <pasta do bot>] [--desde <ISO>]

Diz, a partir dos livros do bot: READY agora, READY novas desde --desde (por
classe da revisao R1), tarefas REPAIR_CONTRACT na fila (por estado), e as
transicoes com REVISAO_R1 / REVISAO_PENDENTE / TEMA_A_CONFIRMAR / ACESSO_PARCIAL.
Le os livros por copia em memoria (read_bytes) — nunca os abre para escrita.
"""
from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path

VIVO = Path("C:/Users/London1/orca/workspaces/eame-sintonia/source-curator-service-v1")
RAIZ = Path(__file__).resolve().parents[2]


def _json(p: Path) -> dict:
    return json.loads(p.read_bytes().decode("utf-8"))


def medir(vivo: Path, desde: str | None) -> dict:
    livro = _json(vivo / "curadoria" / "LIFECYCLE-LEDGER-V1.json")["TRANSICOES"]
    fila = _json(vivo / "curadoria" / "LIFECYCLE-QUEUE-V1.json")["TAREFAS"]
    rev_p = vivo / "curadoria" / "REVISAO-READY-V1.json"
    classe = {x["SOURCE_ID"]: x["CLASSE"] for x in _json(rev_p)["FONTES"]} if rev_p.exists() else {}
    estado = {}
    for t in livro:
        estado[t["SOURCE_ID"]] = t["NEW_STATE"]
    novas = [t for t in livro if desde and t["OBSERVED_AT"] >= desde]
    ready_novas = sorted({t["SOURCE_ID"] for t in novas if t["NEW_STATE"] == "READY_FOR_COLLECTION"})
    marcas = collections.Counter()
    for t in novas:
        for m in ("REVISAO_R1", "REVISAO_PENDENTE", "TEMA_A_CONFIRMAR", "ACESSO_PARCIAL", "REPARO_RECUSADO"):
            if m in (t.get("REASON") or ""):
                marcas[m] += 1
    return {"READY_AGORA": sum(1 for e in estado.values() if e == "READY_FOR_COLLECTION"),
            "REVISAO_INSTALADA": rev_p.exists(),
            "DESDE": desde, "TRANSICOES_DESDE": len(novas),
            "READY_NOVAS_DESDE": len(ready_novas),
            "READY_NOVAS_POR_CLASSE": dict(collections.Counter(classe.get(s, "FORA_DA_REVISAO") for s in ready_novas)),
            "SUSPEITAS_READY": sorted(s for s in ready_novas
                                      if classe.get(s) not in (None, "LIMPA", "ACESSO_PARCIAL")),
            "MARCAS_NO_LIVRO_DESDE": dict(marcas),
            "REPAIR_CONTRACT_NA_FILA": dict(collections.Counter(t["STATUS"] for t in fila
                                                                if t["TASK_TYPE"] == "REPAIR_CONTRACT"))}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--vivo", default=str(VIVO))
    ap.add_argument("--desde")
    a = ap.parse_args(argv)
    print(json.dumps(medir(Path(a.vivo), a.desde), ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
