#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ACOMPANHAR-FILA: as 267 candidatas da fila unica estao a entrar no trabalho do robo?

SO LEITURA do vivo (source-curator-service-v1). Mede, em cada chamada:
  robo (supervisor/worker), fila de tarefas, e para as 267 novas (CAND-0933..1199):
  ponte (BRIDGE-LEDGER), tarefas QUALIFY, estado na porta, lifecycle; e o mesmo para
  as 84 de janela D29 e os 25 perfis D24.
Acrescenta uma linha a curadoria/ACOMPANHAR-FILA-V1.jsonl e um bloco curto a
curadoria/ACOMPANHAR-FILA-V1.md. Nao escreve nada no vivo.
"""
from __future__ import annotations

import json
import re
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
VIVO = Path(r"C:/Users/London1/orca/workspaces/eame-sintonia/source-curator-service-v1")
CORR = RAIZ / "curadoria" / "FILA-UNICA-CORRESPONDENCIA-V1.json"
JSONL = RAIZ / "curadoria" / "ACOMPANHAR-FILA-V1.jsonl"
MD = RAIZ / "curadoria" / "ACOMPANHAR-FILA-V1.md"
JANELA = ("JANELA_", "BOLLETTINI_DIFESA", "BOLLETTINI_AGROMETEO", "CONSORZI_DIFESA", "SERVIZI_TECNICI")
_PROVA_D24 = re.compile(r"(PROVA_IDENTIDADE=|IDENTIDADE: a pagina oficial da pessoa )https?://\S+")


def _ler(rel):
    for _ in range(3):  # o robo pode estar a gravar: tentar de novo
        try:
            return json.loads((VIVO / rel).read_text(encoding="utf-8"))
        except (json.JSONDecodeError, PermissionError):
            import time
            time.sleep(2)
    return json.loads((VIVO / rel).read_text(encoding="utf-8"))


def medir() -> dict:
    corr = json.loads(CORR.read_text(encoding="utf-8"))
    novas = {x["CAND_NOVO"]: x["FAMILIA"] for x in corr["CORRESPONDENCIA"] if x["RESULTADO"].startswith("NOVA")}
    janela = {k for k, f in novas.items() if f.startswith(JANELA)}
    porta = {c["CANDIDATA_ID"]: c for c in _ler("candidatas/FONTES-CANDIDATAS.json")["CANDIDATAS"]}
    d24 = {k for k in novas if porta.get(k, {}).get("TIPO") in ("LINKEDIN", "INSTAGRAM")
           and _PROVA_D24.search(porta[k].get("NOTA") or "")}
    ponte = _ler("curadoria/BRIDGE-LEDGER-V1.json")["PROCESSADAS"]
    tarefas = _ler("curadoria/LIFECYCLE-QUEUE-V1.json")["TAREFAS"]
    livro = _ler("curadoria/LIFECYCLE-LEDGER-V1.json")
    trans = livro.get("TRANSICOES", livro if isinstance(livro, list) else [])
    status = _ler("curadoria/SOURCE-CURATOR-STATUS-LIVE.json")
    aloc = _ler("curadoria/SOURCE-ID-ALLOCATION-V1.json")
    sid_de = {x["CANDIDATE_ID"]: x["SOURCE_ID"] for x in aloc.get("NOVAS", []) if x.get("SOURCE_ID")}
    sem_terr = {x["CANDIDATE_ID"] for x in aloc.get("SEM_TERRITORIO_DETALHE", [])}
    estado_de: dict = {}
    for t in trans:
        estado_de[t.get("SOURCE_ID")] = t.get("NEW_STATE")
    agora = datetime.now(timezone.utc)

    def conta(ids):
        return {
            "N": len(ids),
            "NA_PONTE": sum(1 for k in ids if k in ponte),
            "DESTINO_NA_PONTE": dict(Counter(ponte[k].get("DESTINO") for k in ids if k in ponte)),
            "QUALIFY": dict(Counter(t["STATUS"] for t in tarefas if t["SOURCE_ID"] in ids)),
            "ESTADO_NA_PORTA": dict(Counter(porta[k]["ESTADO"] for k in ids if k in porta)),
            "NO_LIFECYCLE": len({t.get("SOURCE_ID") for t in trans if t.get("SOURCE_ID") in ids}),
            "COM_SOURCE_ID": sum(1 for k in ids if k in sid_de),
            "SEM_TERRITORIO": sum(1 for k in ids if k in sem_terr),
            "ESTADO_DA_FONTE": dict(Counter(estado_de.get(sid_de[k], "SEM_TRANSICAO") for k in ids if k in sid_de)),
        }

    pend = [t for t in tarefas if t["STATUS"] == "PENDING"]
    elegiveis = sum(1 for t in pend if not t.get("NEXT_ATTEMPT_AT") or t["NEXT_ATTEMPT_AT"] <= agora.isoformat())
    head = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=str(VIVO), capture_output=True, text=True).stdout.strip()
    return {
        "MEDIDO_EM": agora.isoformat(timespec="seconds"), "VIVO_HEAD": head,
        "ROBO": {k: status.get(k) for k in ("SOURCE_CURATOR_SERVICE", "SUPERVISOR_STATE", "WORKER_STATE",
                                            "CURRENT_TASK", "GERADO_EM")},
        "FILA_DE_TAREFAS": {"TOTAL": len(tarefas), "PENDING": len(pend), "ELEGIVEIS_AGORA": elegiveis,
                            "IN_PROGRESS": sum(1 for t in tarefas if t["STATUS"] == "IN_PROGRESS"),
                            "LIMIAR_DA_PONTE": 10},
        "PONTE_TOTAL": len(ponte), "PONTE_ULTIMA": max(ponte) if ponte else None,
        "NOVAS_267": conta(set(novas)), "JANELA_84": conta(janela), "PERFIS_D24": conta(d24),
    }


def escrever(m: dict, n: int) -> None:
    with JSONL.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(m, ensure_ascii=False) + "\n")
    a, j, p = m["NOVAS_267"], m["JANELA_84"], m["PERFIS_D24"]
    linhas = [
        "", "## Medida %d — %s (vivo %s)" % (n, m["MEDIDO_EM"], m["VIVO_HEAD"]),
        "- robo: %s / worker %s; tarefas pendentes %d (elegiveis %d, a correr %d; a ponte so corre com <= 10)"
        % (m["ROBO"]["SUPERVISOR_STATE"], m["ROBO"]["WORKER_STATE"], m["FILA_DE_TAREFAS"]["PENDING"],
           m["FILA_DE_TAREFAS"]["ELEGIVEIS_AGORA"], m["FILA_DE_TAREFAS"]["IN_PROGRESS"]),
        "- ponte: %d processadas, ultima %s" % (m["PONTE_TOTAL"], m["PONTE_ULTIMA"]),
        "- 267 novas: %d na ponte %s · QUALIFY %s · porta %s" % (a["NA_PONTE"], a["DESTINO_NA_PONTE"], a["QUALIFY"], a["ESTADO_NA_PORTA"]),
        "- 267 depois da qualificacao: %d com SOURCE_ID, %d sem territorio; estado da fonte %s"
        % (a["COM_SOURCE_ID"], a["SEM_TERRITORIO"], a["ESTADO_DA_FONTE"]),
        "- 84 de janela: %d na ponte · QUALIFY %s · %d com SOURCE_ID · estado %s"
        % (j["NA_PONTE"], j["QUALIFY"], j["COM_SOURCE_ID"], j["ESTADO_DA_FONTE"]),
        "- %d perfis D24: %d na ponte %s · porta %s" % (p["N"], p["NA_PONTE"], p["DESTINO_NA_PONTE"], p["ESTADO_NA_PORTA"]),
    ]
    if not MD.exists():
        MD.write_text("# ACOMPANHAR-FILA-V1 — as 267 da fila unica no trabalho do robo (so leitura do vivo)\n",
                      encoding="utf-8")
    with MD.open("a", encoding="utf-8") as fh:
        fh.write("\n".join(linhas) + "\n")


if __name__ == "__main__":
    n = sum(1 for _ in JSONL.open(encoding="utf-8")) + 1 if JSONL.exists() else 1
    m = medir()
    escrever(m, n)
    print(json.dumps({k: m[k] for k in ("MEDIDO_EM", "FILA_DE_TAREFAS", "PONTE_TOTAL", "PONTE_ULTIMA")}, ensure_ascii=False))
    print("267:", m["NOVAS_267"]["NA_PONTE"], m["NOVAS_267"]["QUALIFY"], "| janela:", m["JANELA_84"]["NA_PONTE"],
          "| D24:", m["PERFIS_D24"]["NA_PONTE"], m["PERFIS_D24"]["ESTADO_NA_PORTA"])
