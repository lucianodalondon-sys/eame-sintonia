#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""R1 · JUNTAR AS BANCAS — o ANTES/DEPOIS por fonte e por causa.

    py scripts/reparo/juntar_bancas.py --foto <copia do vivo> --banca <b0> --banca <b1> ... --saida <json>

Cada banca mediu uma fatia de anfitrioes (medir_em_copia.py --particao). Uma
fonte so muda na banca da sua fatia; se mudar em mais de uma (a tarefa que ja
estava na fila da foto corre em todas), fica a transicao mais recente e a fonte
entra em DUPLAS, dita.

Causa de cada fonte (o estado da foto e o caminho que a levou):
  B_RECANARIO   estava CANARY_PENDING sem tarefa; so voltou a canariar
  A_REPARO      passou por REPAIR_CONTRACT (contrato reescrito ou recusado)
  C_QUALIFY     era CAND-... (QUALIFY desbloqueada)
  OUTRA         mudou por outro caminho
"""
from __future__ import annotations

import argparse
import collections
import json
import re
from pathlib import Path


def _livro(p: Path) -> list:
    return json.loads(p.read_text(encoding="utf-8"))["TRANSICOES"]


def _estado(trans: list) -> dict:
    e = {}
    for t in trans:
        e[t["SOURCE_ID"]] = t
    return e


def _motivo(reason: str) -> str:
    m = re.match(r"REPARO_RECUSADO: ([A-Z_]+)", reason or "")
    if m:
        return "REPARO_RECUSADO:" + m.group(1)
    if "EMPTY_LIST" in (reason or ""):
        return "EMPTY_LIST"
    if "CAPA_NAO_E_MATERIA" in (reason or ""):
        return "CAPA_NAO_E_MATERIA"
    if "regua dos quatro passos nao promove" in (reason or ""):
        return "PASS_PARCIAL (regua)"
    if (reason or "").startswith("canario resolveu, abriu um item real"):
        return "READY pela regua"
    return re.sub(r"\d+", "N", (reason or ""))[:60]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--foto", required=True)
    ap.add_argument("--banca", action="append", required=True)
    ap.add_argument("--saida", required=True)
    a = ap.parse_args(argv)
    foto = Path(a.foto)
    t0 = _livro(foto / "LIFECYCLE-LEDGER-V1.json")
    antes = _estado(t0)
    n0 = len(t0)
    depois, novas, duplas = dict(antes), collections.defaultdict(list), set()
    reparadas = set()
    for b in a.banca:
        tb = _livro(Path(b) / "curadoria" / "LIFECYCLE-LEDGER-V1.json")
        assert [x["OBSERVED_AT"] for x in tb[:n0]] == [x["OBSERVED_AT"] for x in t0], \
            "a banca %s nao parte da mesma foto" % b
        for t in tb[n0:]:
            novas[t["SOURCE_ID"]].append(dict(t, BANCA=Path(b).name))
        fila = json.loads((Path(b) / "curadoria" / "LIFECYCLE-QUEUE-V1.json").read_text(encoding="utf-8"))
        reparadas |= {t["SOURCE_ID"] for t in fila["TAREFAS"] if t["TASK_TYPE"] == "REPAIR_CONTRACT"}
    for sid, ts in novas.items():
        if len({t["BANCA"] for t in ts}) > 1:
            duplas.add(sid)
        depois[sid] = max(ts, key=lambda t: t["OBSERVED_AT"])

    def causa(sid: str) -> str:
        if sid.startswith("CAND-"):
            return "C_QUALIFY"
        if sid in reparadas:
            return "A_REPARO"
        if antes.get(sid, {}).get("NEW_STATE") == "CANARY_PENDING":
            return "B_RECANARIO"
        return "OUTRA"

    ea = collections.Counter(t["NEW_STATE"] for t in antes.values())
    ed = collections.Counter(t["NEW_STATE"] for t in depois.values())
    por_causa = collections.defaultdict(collections.Counter)
    ready_novas = []
    for sid in novas:
        c = causa(sid)
        de, para = antes.get(sid, {}).get("NEW_STATE"), depois[sid]["NEW_STATE"]
        por_causa[c]["%s -> %s" % (de, para)] += 1
        if para == "READY_FOR_COLLECTION" and de != "READY_FOR_COLLECTION":
            ready_novas.append({"SOURCE_ID": sid, "CAUSA": c, "DE": de,
                                "RAZAO": depois[sid]["REASON"][:160]})
    motivos = collections.defaultdict(collections.Counter)
    for sid in novas:
        motivos[causa(sid)][_motivo(depois[sid]["REASON"])] += 1
    out = {"DATASET": "R1-ANTES-DEPOIS-EM-COPIA", "FOTO": str(foto), "BANCAS": a.banca,
           "READY_ANTES": ea["READY_FOR_COLLECTION"], "READY_DEPOIS": ed["READY_FOR_COLLECTION"],
           "ESTADOS_ANTES": dict(ea), "ESTADOS_DEPOIS": dict(ed),
           "FONTES_QUE_MUDARAM": len(novas), "DUPLAS": sorted(duplas),
           "POR_CAUSA": {k: dict(v) for k, v in por_causa.items()},
           "MOTIVO_FINAL_POR_CAUSA": {k: dict(v.most_common()) for k, v in motivos.items()},
           "READY_NOVAS": sorted(ready_novas, key=lambda x: x["SOURCE_ID"])}
    Path(a.saida).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print("READY %d -> %d" % (out["READY_ANTES"], out["READY_DEPOIS"]))
    for k, v in out["POR_CAUSA"].items():
        print(k, v)
    print("DUPLAS", out["DUPLAS"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
