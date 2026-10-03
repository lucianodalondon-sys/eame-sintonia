#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FASE 14 — AUTONOMIA, PROVADA COM UM PROCESSO QUE MORRE MESMO.

    `os._exit(97)` NAO DESENROLA PILHA, NAO CORRE `finally`, NAO CORRE
    `atexit`. Quem responde a seguir e OUTRO PROCESSO, que so ve o disco.

Uma suite que apanha excecoes prova que o `try` funciona. Isto prova que o
TRABALHO SOBREVIVE — que e outra coisa, e e a que interessa quando o bot
corre de madrugada sem ninguem a olhar.

Sequencia medida:

    processo 1: pega A, adia A (429), faz B, pega C e MORRE a meio de C
    processo 2: abre o disco, recupera C, faz C e D
    relogio +1h: A volta sozinha a ser elegivel
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from datetime import timedelta
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
CUR = RAIZ / "curadoria"

FILHO = r'''
import os, sys
sys.path.insert(0, r"{cur}")
import fila as F
F.FILA = __import__("pathlib").Path(r"{fila}")
fase = sys.argv[1]

if fase == "P1":
    for s in ("A", "B", "C", "D"):
        F.enfileirar("SRC-" + s, F.CANARY)
    t = F.proxima()                      # A
    F.adiar(t["TASK_ID"], retry_after_s=3600, erro="HTTP 429")
    t = F.proxima()                      # B
    F.concluir(t["TASK_ID"], "feita pelo processo 1")
    t = F.proxima()                      # C -> IN_PROGRESS no disco
    print("P1_MORREU_EM=" + t["SOURCE_ID"], flush=True)
    os._exit(97)                         # morte real, sem finally

if fase == "P2":
    rec = F.recuperar_orfas(limite_s=0)
    print("P2_RECUPERADAS=" + ",".join(r["SOURCE_ID"] for r in rec), flush=True)
    feitas = []
    while True:
        t = F.proxima()
        if t is None:
            break
        feitas.append(t["SOURCE_ID"])
        F.concluir(t["TASK_ID"], "feita pelo processo 2")
    print("P2_FEZ=" + ",".join(feitas), flush=True)
'''


def main() -> int:
    tmp = tempfile.TemporaryDirectory()
    fila = Path(tmp.name) / "QUEUE.json"
    script = Path(tmp.name) / "filho.py"
    script.write_text(FILHO.format(cur=str(CUR), fila=str(fila)), encoding="utf-8")

    r1 = subprocess.run([sys.executable, str(script), "P1"],
                        capture_output=True, text=True)
    morreu_em = [l for l in r1.stdout.splitlines() if l.startswith("P1_MORREU")]
    print("processo 1: exit=%d  %s" % (r1.returncode, morreu_em[0] if morreu_em else "?"))
    assert r1.returncode == 97, "o processo 1 nao morreu de verdade (exit %d)" % r1.returncode

    # O que o disco sabe entre os dois processos
    d = json.loads(fila.read_text(encoding="utf-8"))
    estados = {t["SOURCE_ID"]: t["STATUS"] for t in d["TAREFAS"]}
    print("disco entre processos: %s" % json.dumps(estados, ensure_ascii=False))

    r2 = subprocess.run([sys.executable, str(script), "P2"],
                        capture_output=True, text=True)
    saida = dict(l.split("=", 1) for l in r2.stdout.splitlines() if "=" in l)
    print("processo 2: recuperadas=%s  fez=%s" % (saida.get("P2_RECUPERADAS"),
                                                  saida.get("P2_FEZ")))

    import importlib
    sys.path.insert(0, str(CUR))
    import fila as F
    importlib.reload(F)
    F.FILA = fila
    agora = F.agora_utc()
    adiada_agora = [t["SOURCE_ID"] for t in F.elegiveis(agora)]
    adiada_depois = [t["SOURCE_ID"] for t in F.elegiveis(agora + timedelta(minutes=61))]
    print("A elegivel agora=%s  daqui a 61min=%s" % (adiada_agora, adiada_depois))

    checks = {
        "PROCESSO_MORREU_MESMO": r1.returncode == 97,
        "TAREFA_EM_CURSO_FICOU_NO_DISCO": estados.get("SRC-C") == "IN_PROGRESS",
        "NENHUMA_TAREFA_SE_PERDEU": len(estados) == 4,
        "PROCESSO_2_RECUPEROU_A_ORFA": saida.get("P2_RECUPERADAS") == "SRC-C",
        "PROCESSO_2_CONTINUOU_O_TRABALHO":
            sorted((saida.get("P2_FEZ") or "").split(",")) == ["SRC-C", "SRC-D"],
        "ADIADA_NAO_BLOQUEOU_NEM_CORREU": adiada_agora == [],
        "ADIADA_VOLTOU_SOZINHA": adiada_depois == ["SRC-A"],
    }
    print()
    for k, v in checks.items():
        print("  %-36s %s" % (k, "PASS" if v else "FAIL"))
    ok = all(checks.values())
    print("\nAUTONOMIA = %s (%d/%d)" % ("PASS" if ok else "FAIL",
                                        sum(checks.values()), len(checks)))
    (CUR / "LIFECYCLE-AUTONOMY-V1.json").write_text(json.dumps({
        "DATASET": "LIFECYCLE-AUTONOMY-V1",
        "LEI": "processo morto com os._exit(97). Nao e excecao apanhada.",
        "EXIT_CODE_DO_PROCESSO_1": r1.returncode,
        "DISCO_ENTRE_PROCESSOS": estados,
        "RECUPERADAS": saida.get("P2_RECUPERADAS"),
        "FEITAS_PELO_PROCESSO_2": saida.get("P2_FEZ"),
        "CHECKS": checks, "PASS": ok,
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    tmp.cleanup()
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
