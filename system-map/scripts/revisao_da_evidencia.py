#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A REVISAO DA EVIDENCIA EMPRESTADA — aresta a aresta, com o porque.

    py system-map/scripts/revisao_da_evidencia.py

POR QUE ISTO EXISTE
-------------------
O G1 do contrato de confianca fechou duas coisas ao mesmo tempo, porque sao a
mesma: publicar cada afirmacao no seu plano, e ligar cada evidencia a afirmacao
que ela realmente sustenta.

    UMA LINHA NAO PROVA DUAS AFIRMACOES DIFERENTES
    SO POR ESTAR PERTO DAS DUAS.

Este ficheiro nao decide nada: ele ENUMERA a decisao que o gerador tomou para
cada aresta tocada por uma linha partilhada, com a razao escrita ao lado. Uma
decisao sem porque nao e uma decisao — e uma escolha que ninguem pode discutir
depois.

O QUE ELE NAO FAZ
-----------------
Nao procura outra linha para manter o mapa verde. Onde a evidencia nao sustenta
a afirmacao, o plano cai para UNKNOWN — e UNKNOWN nao e NO: nao ter prova nao e
ter prova de que nao existe.

SAIDA: data/derivados/SYSTEM-MAP-EVIDENCE-BINDING-REVIEW-V1.json
"""

import json
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
ESTADO = RAIZ / "system-map" / "data" / "state.generated.json"
SAIDA = RAIZ / "data" / "derivados" / "SYSTEM-MAP-EVIDENCE-BINDING-REVIEW-V1.json"

sys.path.insert(0, str(AQUI))
import impressao_da_arvore as IMPRESSAO          # noqa: E402

# O mesmo criterio do gerador, lido de la — nao reescrito aqui.
from generate_system_map import TIPOS_MEDIDOS     # noqa: E402,F401


def git(*a: str) -> str:
    return subprocess.run(["git", "-C", str(RAIZ), *a],
                          capture_output=True, text=True).stdout.strip()


def medir() -> dict:
    S = json.loads(ESTADO.read_text(encoding="utf-8"))
    E = S["EDGES"]

    # que arestas partilham cada linha de evidencia
    onde = defaultdict(list)
    for i, e in enumerate(E):
        for ev in e.get("evidence", []):
            onde[(ev.get("file"), ev.get("line"))].append(i)
    partilhadas = {k: v for k, v in onde.items() if len(v) > 1}
    entre_tipos = {k: v for k, v in partilhadas.items()
                   if len({E[i]["type"] for i in v}) > 1}
    afectadas = sorted({i for v in partilhadas.values() for i in v})

    linhas = []
    for i in afectadas:
        e = E[i]
        apoiadas = [ev for ev in e.get("evidence", []) if ev.get("SUPPORTS") == "YES"]
        naos = [ev for ev in e.get("evidence", []) if ev.get("SUPPORTS") == "NO"]
        ambig = [ev for ev in e.get("evidence", []) if ev.get("SUPPORTS") == "AMBIGUOUS"]
        decisao = ("SUPPORTED" if apoiadas else
                   "AMBIGUOUS" if ambig else "UNSUPPORTED")
        motivo = next((ev["WHY"] for ev in (apoiadas or ambig or naos)), "")
        linhas.append({
            "EDGE_ID": f'{e["from"]}--{e["type"]}-->{e["to"]}',
            "FROM": e["from"], "TO": e["to"],
            "RELATION_TYPE": e["type"],
            "RAW_TYPE_MEDIDO": e.get("raw_type"),
            "OLD_EVIDENCE": [{"file": ev.get("file"), "line": ev.get("line"),
                              "SUPPORTS": ev.get("SUPPORTS")}
                             for ev in e.get("evidence", [])],
            "ASSERTION_SUPPORTED": next(
                (ev.get("ASSERTION_SUPPORTED") for ev in apoiadas), None),
            "DECISION": decisao,
            "DECLARED_AFTER": e["DECLARED"],
            "CODE_AFTER": e["CODE"],
            "OBSERVED_AFTER": e["OBSERVED"],
            "PROVEN_AFTER": e["PROVEN"],
            "PROVEN_PLANE_AFTER": e["PROVEN_PLANE"],
            "WHY": motivo,
        })
    linhas.sort(key=lambda x: x["EDGE_ID"])

    impressao, _n, _a = IMPRESSAO.do_disco()
    sem_porque = [x["EDGE_ID"] for x in linhas if not x["WHY"]]

    return {
        "SCHEMA": "sintonia.system-map.revisao-da-evidencia/1",
        "O_QUE_ISTO_E": [
            "A revisao das arestas tocadas por evidencia partilhada, uma a uma.",
            "Nenhuma decisao entra aqui sem WHY.",
            "UNKNOWN nao e NO: nao ter prova nao e ter prova de que nao existe.",
        ],
        "PROVENANCE": {
            "HEAD": git("rev-parse", "HEAD"),
            "BRANCH": git("rev-parse", "--abbrev-ref", "HEAD"),
            "GENERATED_AT": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "SOURCE_TREE_FINGERPRINT": impressao,
        },
        "CARIMBOS_NAO_COMPARAVEIS": ["HEAD", "GENERATED_AT",
                                     "SOURCE_TREE_FINGERPRINT"],
        "BLOCOS_NAO_COMPARAVEIS": ["PROVENANCE"],
        "RESUMO": {
            "ARESTAS_TOTAL": len(E),
            "LINHAS_PARTILHADAS": len(partilhadas),
            "LINHAS_PARTILHADAS_ENTRE_TIPOS": len(entre_tipos),
            "ARESTAS_REVISTAS": len(linhas),
            "SUPPORTED": sum(1 for x in linhas if x["DECISION"] == "SUPPORTED"),
            "AMBIGUOUS": sum(1 for x in linhas if x["DECISION"] == "AMBIGUOUS"),
            "UNSUPPORTED": sum(1 for x in linhas if x["DECISION"] == "UNSUPPORTED"),
            "SEM_PORQUE": sem_porque,
            "POR_DECISAO_E_TIPO": {
                f"{d}·{t}": n for (d, t), n in sorted(
                    Counter((x["DECISION"], x["RELATION_TYPE"])
                            for x in linhas).items())},
        },
        "SENTINELA_APIFY": [
            {k: x[k] for k in ("EDGE_ID", "RELATION_TYPE", "DECISION",
                               "CODE_AFTER", "PROVEN_AFTER", "WHY")}
            for x in linhas if x["FROM"] == "C-APIFY-POOL"],
        "ARESTAS": linhas,
    }


def main() -> int:
    d = medir()
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n",
                     encoding="utf-8")
    r = d["RESUMO"]
    print("A REVISAO DA EVIDENCIA EMPRESTADA\n" + "=" * 66)
    for k in ("ARESTAS_TOTAL", "LINHAS_PARTILHADAS",
              "LINHAS_PARTILHADAS_ENTRE_TIPOS", "ARESTAS_REVISTAS",
              "SUPPORTED", "AMBIGUOUS", "UNSUPPORTED"):
        print(f"  {str(r[k]).rjust(5)}  {k.replace('_', ' ').lower()}")
    print(f"\n  sem porque: {r['SEM_PORQUE'] or 'nenhuma'}")
    print("\n  POR DECISAO E TIPO:")
    for k, v in r["POR_DECISAO_E_TIPO"].items():
        print(f"    {str(v).rjust(4)}  {k}")
    print("\n  SENTINELA APIFY:")
    for x in d["SENTINELA_APIFY"]:
        print(f"    {x['EDGE_ID'][:54]:<54} {x['DECISION']:<12} CODE={x['CODE_AFTER']}")
    print(f"\n  escrito em {SAIDA.relative_to(RAIZ).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
