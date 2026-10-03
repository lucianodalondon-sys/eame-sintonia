"""LI-ONDA · ensaio em CÓPIA: o worker corre SÓ as tarefas das candidatas semeadas (LinkedIn ou, `--tipo YOUTUBE`, YouTube).

    py curadoria/ensaio_so_linkedin.py --copia [--json SAIDA]

⚠️ PORQUE EXISTE (medido em 25/09 02:38): a fila viva tinha ~200 tarefas pendentes de
outras frentes; um `worker.correr()` sem filtro numa cópia fez 81 VALIDATE_ROUTE e 83
CANARY em 52 sites reais — trabalho do bot vivo, repetido, e acima do teto de visitas.
Aqui a fila é filtrada: só entram as QUALIFY das candidatas LinkedIn e os degraus que
elas geram (BUILD_CONTRACT, VALIDATE_ROUTE da rota do Scrap). Todos são sem rede:
o QUALIFY lê livros, o contrato é escrito a partir do molde, e a rota do Scrap é
conferida na matriz dele. Um CANARY que apareça é RECUSADO, não corrido.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
for _p in ("curadoria", "candidatas"):
    sys.path.insert(0, str(RAIZ / _p))

VIVOS = ("source-curator-service-v1", "ponte-viva")
SEM_REDE = {"QUALIFY", "BUILD_CONTRACT", "VALIDATE_ROUTE"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--copia", action="store_true")
    ap.add_argument("--json")
    ap.add_argument("--tipo", choices=("LINKEDIN", "YOUTUBE"), default="LINKEDIN")
    a = ap.parse_args()
    if not a.copia or any(v in str(RAIZ).replace("\\", "/") for v in VIVOS):
        print("RECUSADO: so numa copia (--copia)")
        return 2
    import fila as F
    import fonte_nova as FN
    import lifecycle as LC
    import worker as W
    cands = {c["CANDIDATA_ID"] for c in FN.carregar()["CANDIDATAS"] if c.get("TIPO") == a.tipo}
    antes = {n["SOURCE_ID"] for n in W._ler_alloc()["NOVAS"]}

    def nossas() -> set:
        sids = {n["SOURCE_ID"] for n in W._ler_alloc()["NOVAS"] if n.get("CANDIDATE_ID") in cands}
        return cands | sids

    original = F.elegiveis

    def so_linkedin(*args, **kw):
        ok = nossas()
        fora = []
        for t in original(*args, **kw):
            if t["SOURCE_ID"] not in ok:
                continue
            if t["TASK_TYPE"] not in SEM_REDE:
                raise RuntimeError("tarefa com rede na fila do ensaio: %s %s" % (t["TASK_TYPE"], t["SOURCE_ID"]))
            fora.append(t)
        return fora

    F.elegiveis = so_linkedin
    try:
        r = W.correr(max_tarefas=0, pausa=0, verboso=False)
    finally:
        F.elegiveis = original
    novas = [n for n in W._ler_alloc()["NOVAS"] if n["SOURCE_ID"] not in antes]
    resumo = {"TAREFAS": dict(Counter("%s:%s" % (x["TASK_TYPE"], x["RESULTADO"]) for x in r)),
              "NUMEROS_NOVOS": len(novas),
              "ESTADOS": dict(Counter(LC.estado_de(n["SOURCE_ID"]) for n in novas)),
              "TIPOS_CORRIDOS": sorted({x["TASK_TYPE"] for x in r})}
    print(json.dumps(resumo, ensure_ascii=False))
    if a.json:
        Path(a.json).write_text(json.dumps({"RESUMO": resumo, "NOVAS": novas}, ensure_ascii=False, indent=1),
                                encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
