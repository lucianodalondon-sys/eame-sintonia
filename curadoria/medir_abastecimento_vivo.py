#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MEDIR O ABASTECIMENTO AO VIVO — so leitura da worktree do servico.

    uso: py medir_abastecimento_vivo.py <worktree-viva> <linha-inicial> [saida.json]

Copia fila, run-log, estado e ledger para um TemporaryDirectory e mede la
dentro: nada e aberto para escrita na worktree viva. <linha-inicial> e a linha
(1-based) do run-log onde comecou a instalacao do codigo novo.

Mede: as revividas (REVIVALS na fila) por tipo/estado/motivo; eventos do
supervisor por hora; FEEDER_NOOP_TOTAL; corridas de discovery; erros repetidos
(mesma mensagem >= 3 vezes); transicoes READY no ledger desde a instalacao.
"""
from __future__ import annotations

import collections
import json
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

FICHEIROS = ("LIFECYCLE-QUEUE-V1.json", "SOURCE-CURATOR-RUN-LOG.ndjson",
             "SUPERVISOR-STATE.json", "LIFECYCLE-LEDGER-V1.json")


def medir(viva: Path, linha0: int) -> dict:
    with tempfile.TemporaryDirectory(prefix="m2b-") as td:
        t = Path(td)
        for f in FICHEIROS:
            shutil.copy(viva / "curadoria" / f, t / f)
        linhas = (t / FICHEIROS[1]).read_text(encoding="utf-8").splitlines()
        fila = json.loads((t / FICHEIROS[0]).read_text(encoding="utf-8"))["TAREFAS"]
        estado = json.loads((t / FICHEIROS[2]).read_text(encoding="utf-8"))
        ledger = json.loads((t / FICHEIROS[3]).read_text(encoding="utf-8"))

    ev = [json.loads(l) for l in linhas[linha0 - 1:] if l.strip()]
    t0 = ev[0]["AT"] if ev else None
    sup = [e for e in ev if e.get("ORIGEM") == "SUPERVISOR"]
    por_hora = collections.Counter(e["AT"][:13] for e in sup)
    realim = [e for e in ev if e.get("EVENTO") == "REALIMENTACAO"]
    disc = [{"AT": e["AT"], **(e.get("DISCOVERY") or {})} for e in realim
            if "DISCOVERY" in e.get("ACCOES", [])]

    # erro repetido: a mesma mensagem de erro >= 3 vezes desde a instalacao
    msgs = collections.Counter()
    for e in ev:
        for k in ("ERRO", "LAST_ERROR", "PORQUE", "MOTIVO"):
            v = e.get(k)
            if isinstance(v, str) and e.get("EVENTO") not in ("WORKER_RELANCADO",):
                msgs[(e.get("EVENTO"), v[:90])] += 1
    repetidos = {"%s | %s" % k: n for k, n in msgs.items() if n >= 3}

    rev = [x for x in fila if x.get("REVIVALS")]
    por_estado = collections.Counter((x["TASK_TYPE"], x["STATUS"]) for x in rev)
    motivo = collections.Counter((x["STATUS"], (x.get("LAST_ERROR") or x.get("MOTIVO") or "")[:80])
                                 for x in rev)

    trans = ledger.get("TRANSICOES") or ledger.get("TRANSITIONS") or []
    desde = [x for x in trans if t0 and str(x.get("OBSERVED_AT", "")) >= t0]
    ready = [x for x in desde if "READY" in str(x.get("NEW_STATE") or "")]
    rev_ids = {x["SOURCE_ID"] for x in rev}
    trans_rev = collections.Counter(str(x.get("NEW_STATE"))
                                    for x in desde if x.get("SOURCE_ID") in rev_ids)
    return {
        "MEDIDO_EM": datetime.now(timezone.utc).isoformat(),
        "DESDE": t0,
        "EVENTOS_DESDE_INSTALACAO": dict(collections.Counter(e.get("EVENTO") for e in ev)),
        "EVENTOS_SUPERVISOR_POR_HORA": dict(por_hora),
        "REALIMENTACAO": [{"AT": e["AT"], "ACCOES": e.get("ACCOES"),
                           "DECISAO": e.get("DECISAO")} for e in realim],
        "FEEDER": {k: estado.get(k) for k in estado if k.startswith("FEEDER")},
        "DISCOVERY": disc,
        "REVIVIDAS": {"TOTAL": len(rev),
                      "POR_TIPO_ESTADO": {"%s/%s" % k: n for k, n in por_estado.items()},
                      "POR_MOTIVO": {"%s | %s" % k: n for k, n in motivo.items()},
                      "LISTA": [{"TASK_ID": x["TASK_ID"], "SOURCE_ID": x["SOURCE_ID"],
                                 "TIPO": x["TASK_TYPE"], "STATUS": x["STATUS"],
                                 "REVIVALS": x["REVIVALS"],
                                 "ERRO": (x.get("LAST_ERROR") or "")[:120]} for x in rev]},
        "LEDGER_TRANSICOES_DAS_REVIVIDAS": dict(trans_rev),
        "LEDGER_READY_DESDE_INSTALACAO": len(ready),
        "ERROS_REPETIDOS_3_OU_MAIS": repetidos,
        "SUPERVISOR_PID": estado.get("SUPERVISOR_PID"),
        "WORKER_PID": estado.get("WORKER_PID"),
    }


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    m = medir(Path(sys.argv[1]), int(sys.argv[2]))
    txt = json.dumps(m, ensure_ascii=False, indent=1)
    if len(sys.argv) > 3:
        Path(sys.argv[3]).write_text(txt + "\n", encoding="utf-8")
    print(txt)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
