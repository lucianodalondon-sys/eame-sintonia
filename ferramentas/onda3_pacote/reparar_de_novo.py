#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""REPARAR DE NOVO — pôr na fila o reparo de fontes cujo reparo já está DONE.

    O ROBÔ NÃO VOLTA SOZINHO A UMA FONTE COM O REPARO FEITO.

Medido pela ORDENS-63 v2 (25/09): o gatilho (`gatilho_discovery.candidatas_a_reparar`)
só pede REPAIR_CONTRACT para quem nunca foi reparado. Depois de instalar o conserto
WordPress da RECEITAS-182 (`receitas-182-v1`), as fontes que ele devia salvar continuam
paradas. Esta ferramenta faz SÓ o que o gatilho faria, pela mesma porta:

    fila.enfileirar(SOURCE_ID, REPAIR_CONTRACT)

O worker faz o resto (REPAIRING -> reparo -> VALIDATE_ROUTE -> CANARY -> régua). Nada
aqui promove, nem toca no contrato.

Recusa (NADA, com o porquê): fonte READY (o reparo tirava-a de READY), fonte retirada
por decisão (D9/D49/D51/D52), fonte fora do livro.

    py ferramentas/onda3_pacote/reparar_de_novo.py --fontes=IT-T3-062,IT-T5-164            # mostra
    py ferramentas/onda3_pacote/reparar_de_novo.py --fontes=IT-T3-062,IT-T5-164 --aplicar  # escreve a fila
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "curadoria"))
import fila as F                  # noqa: E402
import lifecycle as LC            # noqa: E402
import ready_split as RS          # noqa: E402
import retirar_por_decisao as RPD  # noqa: E402

MOTIVO = "REPARAR DE NOVO: conserto novo do reparo instalado (receitas-182-v1); o reparo antigo estava DONE"


def planear(ids: list[str], *, contratos: dict | None = None, estado_de=None) -> list[dict]:
    contratos = contratos if contratos is not None else RS._contratos()
    estado_de = estado_de or LC.estado_de
    out = []
    for sid in ids:
        e = estado_de(sid)
        c = contratos.get(sid)
        if e is None:
            porque = "fora do livro de estados"
        elif e == LC.READY_FOR_COLLECTION:
            porque = "READY: o reparo tirava-a de READY"
        elif RPD.retirada(c):
            porque = "retirada por decisao: %s" % ((c or {}).get("CATALOGO_D9") or {}).get("DECISAO")
        else:
            porque = ""
        out.append({"SOURCE_ID": sid, "STATE": e, "ACCAO": "NADA" if porque else "REPARAR",
                    "PORQUE": porque})
    return out


def aplicar(plano: list[dict]) -> list[dict]:
    feitas = []
    for p in plano:
        if p["ACCAO"] != "REPARAR":
            continue
        t = F.enfileirar(p["SOURCE_ID"], F.REPAIR_CONTRACT, priority=50, motivo=MOTIVO)
        feitas.append(dict(p, FEITO=True, TASK_ID=t["TASK_ID"]))
    return feitas


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    ids = []
    for a in argv:
        if a.startswith("--fontes="):
            ids = [x.strip() for x in a.split("=", 1)[1].split(",") if x.strip()]
    if not ids:
        print("uso: --fontes=ID,ID [--aplicar]", file=sys.stderr)
        return 2
    plano = planear(ids)
    for p in plano:
        print("%-8s %-10s %-26s %s" % (p["ACCAO"], p["SOURCE_ID"], p["STATE"], p["PORQUE"]))
    if "--aplicar" not in argv:
        print("MOSTRAR: nada foi escrito (use --aplicar)")
        return 0
    feitas = aplicar(plano)
    print("APLICADO: %s" % json.dumps(feitas, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
