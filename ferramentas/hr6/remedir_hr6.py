#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""HR-6 · RE-MEDIR PELO CAMINHO CANONICO as READY que o portao manda a olho humano.

    NINGUEM MARCA «VISTO POR PESSOA». O CANARIO MEDE DE NOVO E O PORTAO DECIDE.

O portao (`collection_gate`) poe HUMAN_REVIEW_REQUIRED quando o item que a
promocao abriu tem cara de SECCAO (ultimo segmento com < 4 palavras e sem
digitos). O canario abria sempre o 1.o alvo por ordem alfabetica, e re-medir
abria o mesmo endereco. Com `canario.escolher_alvo` (HR-6) ele tenta primeiro o
item mais fundo; se esse nao passar, abre o 1.o, como antes.

Esta ferramenta faz SO o que `ready_split.remedir` faz, com o motivo certo:

    READY_FOR_COLLECTION -> CANARY_PENDING (motivo escrito no livro)
    + tarefa VALIDATE_ROUTE na fila

Quem promove e o worker (VALIDATE_ROUTE -> CANARY -> regua dos 4 passos). Nada
aqui promove, nem toca no contrato.

So aceita fonte que o portao ve AGORA como READY + HUMAN_REVIEW_REQUIRED.

    py ferramentas/hr6/remedir_hr6.py --fontes=IT-T7-170,IT-T7-174            # mostra
    py ferramentas/hr6/remedir_hr6.py --fontes=IT-T7-170,IT-T7-174 --aplicar  # escreve
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "curadoria"))
import collection_gate as G      # noqa: E402
import fila as F                 # noqa: E402
import lifecycle as LC           # noqa: E402

MOTIVO = ("HR-6: re-medir pelo canario com item mais fundo (canario.escolher_alvo); "
          "o READY antigo abriu um endereco com cara de seccao (HUMAN_REVIEW_REQUIRED)")
EVIDENCE_REF = "HR-6:canario.escolher_alvo"


def planear(ids: list[str], *, ctx: dict | None = None) -> list[dict]:
    ctx = ctx if ctx is not None else G._contexto()
    out = []
    for sid in ids:
        v = G.avaliar(sid, **ctx)
        ok = v["STATE"] == LC.READY_FOR_COLLECTION and v["MOTIVO"] == G.HUMAN_REVIEW_REQUIRED
        out.append({"SOURCE_ID": sid, "STATE": v["STATE"], "MOTIVO": v["MOTIVO"],
                    "ITEM_DA_PROMOCAO": G.url_do_item_aberto(
                        sid, livro=ctx["livro"], evidencias=ctx["evidencias"]),
                    "ACCAO": "REMEDIR" if ok else "NADA",
                    "PORQUE": "" if ok else "so se re-mede READY com HUMAN_REVIEW_REQUIRED"})
    return out


def aplicar(plano: list[dict]) -> list[dict]:
    feitas = []
    for p in plano:
        if p["ACCAO"] != "REMEDIR":
            continue
        # o estado pode ter mudado entre o plano e agora: mede-se outra vez
        if LC.estado_de(p["SOURCE_ID"]) != LC.READY_FOR_COLLECTION:
            feitas.append(dict(p, FEITO=False, PORQUE="deixou de estar READY"))
            continue
        LC.registar(p["SOURCE_ID"], LC.CANARY_PENDING, MOTIVO, evidence_ref=EVIDENCE_REF)
        t = F.enfileirar(p["SOURCE_ID"], F.VALIDATE_ROUTE, priority=55,
                         motivo="HR-6: re-medir com item mais fundo")
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
    print(json.dumps(plano, ensure_ascii=False, indent=1))
    if "--aplicar" not in argv:
        print("MOSTRAR: nada foi escrito (use --aplicar)")
        return 0
    feitas = aplicar(plano)
    print("APLICADO: %s" % json.dumps(feitas, ensure_ascii=False))
    return 0 if all(f["FEITO"] for f in feitas) else 1


if __name__ == "__main__":
    raise SystemExit(main())
