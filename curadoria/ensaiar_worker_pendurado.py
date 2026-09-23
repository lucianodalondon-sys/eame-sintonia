#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O WORKER PENDURADO PELO CANO — ensaio com o worker REAL, numa COPIA.

    uso: py <COPIA>/curadoria/ensaiar_worker_pendurado.py --sou-uma-copia [--tarefas N]

Lanca o ciclo_continuo pela PROPRIA supervisor._lancar_worker (a mesma linha
de comando e os mesmos canais de saida da producao) e NUNCA le o stdout dele —
exactamente o que o supervisor faz. Mede, a cada segundo: tarefas fechadas na
fila, ultimo heartbeat no diario, processo vivo ou nao.

Sem rede: as tarefas sao CANARY de fontes SEM contrato, que o worker barra na
hora e imprime uma linha por cada uma (o mesmo print das tarefas reais).
Recusa-se a correr num checkout git.
"""
from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))


def main() -> int:
    if "--sou-uma-copia" not in sys.argv or (RAIZ / ".git").exists():
        print("recuso: corre so numa copia (tar), nunca num checkout")
        return 2
    n_tarefas = 80
    if "--tarefas" in sys.argv:
        n_tarefas = int(sys.argv[sys.argv.index("--tarefas") + 1])
    janela = 60
    if "--janela" in sys.argv:
        janela = int(sys.argv[sys.argv.index("--janela") + 1])

    import fila as F
    import supervisor as S

    agora = datetime.now(timezone.utc).isoformat()
    F.FILA.write_text(json.dumps({"PROXIMO_ID": 80000 + n_tarefas, "TAREFAS": [
        {"TASK_ID": "T8%04d" % i, "SOURCE_ID": "IT-ENSAIO-SEM-CONTRATO-%03d" % i,
         "TASK_TYPE": F.CANARY, "PRIORITY": 60, "STATUS": F.PENDING, "ATTEMPTS": 0,
         "NEXT_ATTEMPT_AT": None, "LAST_ERROR": None, "MOTIVO": "ensaio",
         "CREATED_AT": agora, "UPDATED_AT": agora} for i in range(n_tarefas)]}),
        encoding="utf-8")
    S.DIARIO.write_text("", encoding="utf-8")
    S.PARAR.unlink(missing_ok=True)

    proc = S._lancar_worker(0.05)          # o lancamento de producao, tal e qual
    t0 = time.time()
    serie = []
    while time.time() - t0 < janela:
        time.sleep(1)
        feitas = sum(1 for t in F._ler()["TAREFAS"] if t["STATUS"] != F.PENDING)
        hb = S._ultimo_heartbeat()
        serie.append({"T": round(time.time() - t0), "FECHADAS": feitas,
                      "HB": hb.isoformat()[11:19] if hb else None,
                      "VIVO": proc.poll() is None})
        if proc.poll() is not None:
            break

    vivo_no_fim = proc.poll() is None
    # so agora se le o que o worker escreveu: quanto estava preso no cano
    if vivo_no_fim:
        proc.kill()
    preso = proc.stdout.read() if proc.stdout else ""
    proc.wait()
    evs = [json.loads(l) for l in S.DIARIO.read_text(encoding="utf-8").splitlines()
           if l.strip()]
    ultimo_avanco = max((s["T"] for s in serie
                         if s["FECHADAS"] == serie[-1]["FECHADAS"]), default=None)
    primeiro_parado = min((s["T"] for s in serie
                           if s["FECHADAS"] == serie[-1]["FECHADAS"]), default=None)
    res = {
        "DATASET": "WORKER-PENDURADO-ENSAIO-V1",
        "CANAL_STDOUT": "o de supervisor._lancar_worker (medido: %s)" % (
            "PIPE" if proc.stdout else "outro"),
        "TAREFAS": n_tarefas,
        "FECHADAS_NO_FIM": serie[-1]["FECHADAS"] if serie else 0,
        "VIVO_NO_FIM": vivo_no_fim,
        "RC": None if vivo_no_fim else proc.returncode,
        "SEGUNDO_EM_QUE_PAROU_DE_AVANCAR": primeiro_parado,
        "BYTES_DE_STDOUT_ESCRITOS": len(preso.encode("utf-8")),
        "EVENTOS_NO_DIARIO": [e.get("EVENTO") for e in evs],
        "SERIE": serie,
        "PENDURADO": vivo_no_fim and (serie[-1]["FECHADAS"] < n_tarefas),
    }
    out = RAIZ / "curadoria" / "WORKER-PENDURADO-ENSAIO-V1.json"
    out.write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in res.items() if k != "SERIE"}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
