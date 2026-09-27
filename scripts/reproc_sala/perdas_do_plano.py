#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""REPROC-SALA-PLANO — antes de escrever: quantos valores CONHECIDOS o plano poria em NAO SEI.

    py scripts/reproc_sala/perdas_do_plano.py vista-antes.json plano.json perdas.json

⚠️ Medido no ensaio de 26/09 22:26: com os caminhos em forma `/c/...` o reprocesso não achou um
único livro do coletor (80/80 sem livro, 0 com página) e o plano apagava as 38 datas de publicação
conhecidas. Um reprocesso cego não falha: grava `NAO SEI` com toda a calma. Esta conta é o travão.
Imprime `PERDAS=<n>` na última linha.
"""
import json
import sys

NAO_SEI = "NAO SEI"
CAMPOS = ("published_at", "source_location", "fact_time", "fact_location")


def main(vista_p, plano_p, saida_p):
    with open(vista_p, encoding="utf-8") as fh:
        vista = {(l["run_id"], l["ordem"]): l for l in (json.loads(fh.read().strip() or "null") or [])}
    with open(plano_p, encoding="utf-8") as fh:
        plano = json.load(fh)
    perdas = []
    for it in plano["ITENS"]:
        agora = vista.get((it["RUN_ID"], it["ORDEM"]))
        if agora is None:
            continue
        for r in it["REVISOES"]:
            c = r["CAMPO"]
            if c in CAMPOS and agora[c] != NAO_SEI and r["VALOR"] == NAO_SEI:
                perdas.append({"RUN_ID": it["RUN_ID"], "ORDEM": it["ORDEM"], "SOURCE_ID": it["SOURCE_ID"],
                               "CAMPO": c, "ANTES": agora[c], "BASE_NOVA": (r["BASE"] or "")[:300]})
    por_campo = {c: sum(p["CAMPO"] == c for p in perdas) for c in CAMPOS}
    with open(saida_p, "w", encoding="utf-8", newline="\n") as fh:
        json.dump({"POR_CAMPO": por_campo, "PERDAS": perdas}, fh, ensure_ascii=False, indent=1)
    print("   valor conhecido -> NAO SEI, pelo plano: " +
          " · ".join("%s %d" % (c, n) for c, n in por_campo.items()))
    print("PERDAS=%d" % len(perdas))
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:4]))
