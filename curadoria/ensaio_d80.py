#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ENSAIO D80 — numa CÓPIA do vivo (worktree + livros sujos do vivo), NUNCA no vivo.

    py curadoria/ensaio_d80.py --saida=<ENSAIO-D80-V1.json> [--referencia=<copia do vivo intocada>]

Faz, pela ordem do plano: a seco -> --aplicar (i) + reabrir -> o robô corre SÓ as QUALIFY
reabertas e os BUILD_CONTRACT que elas enfileirarem -> lista final por fonte -> --reverter
e confere que as fichas voltam ao que eram (contra a --referencia). Rede FECHADA: qualquer
ligação conta e falha (proxy morto + socket barrado).
"""
from __future__ import annotations

import json
import os
import socket
import sys
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
VIVO = Path("C:/Users/London1/orca/workspaces/eame-sintonia/source-curator-service-v1")
if RAIZ.resolve() == VIVO.resolve():
    raise SystemExit("RECUSADO: o ensaio nao corre no vivo")
sys.path.insert(0, str(RAIZ / "curadoria"))
sys.path.insert(0, str(RAIZ / "candidatas"))
os.environ.update(HTTP_PROXY="http://127.0.0.1:9", HTTPS_PROXY="http://127.0.0.1:9", NO_PROXY="")

REDE = []
_orig_conn = socket.create_connection


def _sem_rede(addr, *a, **k):
    REDE.append(str(addr))
    raise OSError("ensaio D80: rede fechada (%s)" % (addr,))


socket.create_connection = _sem_rede

import aplicar_d80 as A     # noqa: E402
import fila as F            # noqa: E402
import fonte_nova as FN     # noqa: E402
import lifecycle as LC      # noqa: E402
import worker as W          # noqa: E402


def _ficha(cid):
    return next((c for c in FN.carregar()["CANDIDATAS"] if c["CANDIDATA_ID"] == cid), None)


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    a = dict(x[2:].split("=", 1) for x in argv if x.startswith("--") and "=" in x)
    saida = Path(a["saida"])
    recibos = saida.parent
    alloc0 = json.loads(W.ALLOCATION.read_text(encoding="utf-8"))
    n_novas0 = len(alloc0.get("NOVAS", []))
    qualify_antes = {t["TASK_ID"]: t for t in F._ler()["TAREFAS"] if t["TASK_TYPE"] == F.QUALIFY}

    A.main(["--recibo=%s" % (recibos / "D80-RECIBO-A-SECO.json")])
    A.main(["--aplicar", "--recibo=%s" % (recibos / "D80-RECIBO-APLICAR.json")])
    aplicado = json.loads((recibos / "D80-RECIBO-APLICAR.json").read_text(encoding="utf-8"))

    # O robô: so as QUALIFY reabertas agora, e o que elas enfileirarem (BUILD_CONTRACT).
    reabertas = [t["TASK_ID"] for t in F._ler()["TAREFAS"]
                 if t["TASK_TYPE"] == F.QUALIFY and t["STATUS"] == F.PENDING
                 and qualify_antes.get(t["TASK_ID"], {}).get("STATUS") == F.BLOCKED]
    ids_bc0 = {t["TASK_ID"] for t in F._ler()["TAREFAS"] if t["TASK_TYPE"] == F.BUILD_CONTRACT}
    resultados = []
    contratos = W._contratos()
    por_id = {t["TASK_ID"]: t for t in F._ler()["TAREFAS"]}
    for tid in reabertas:
        resultados.append(W.executar_uma(por_id[tid], contratos))
    novas_bc = [t for t in F._ler()["TAREFAS"]
                if t["TASK_TYPE"] == F.BUILD_CONTRACT and t["TASK_ID"] not in ids_bc0]
    for t in novas_bc:
        r = W.executar_uma(t, W._contratos())
        resultados.append(r)

    alloc = json.loads(W.ALLOCATION.read_text(encoding="utf-8"))
    novas = alloc.get("NOVAS", [])[n_novas0:]
    fora = alloc.get("NOVAS_FORA_DE_IT", [])
    bc = {r["SOURCE_ID"]: r for r in resultados if r["TASK_TYPE"] == F.BUILD_CONTRACT}
    q = {r["SOURCE_ID"]: r for r in resultados if r["TASK_TYPE"] == F.QUALIFY}

    lista = []
    for l in aplicado["LINHAS"]:
        f = _ficha(l["CANDIDATA_ID"])
        lista.append({"PARTE": "(i)", "CANDIDATA_ID": l["CANDIDATA_ID"], "NOME": l["NOME"], "URL": l["URL"],
                      "DECISAO": "RECUSADA" if f and f["ESTADO"] == "RECUSADA" and f.get("RECUSADA_POR") == "D80(i)"
                      else ("NAO SEI" if l["ACAO"] == "NAO_SEI" else "NAO APLICADA (%s)" % l["AGORA"]),
                      "DUPLICADA_DE": f.get("DUPLICADA_DE") if f else None,
                      "MOTIVO": l.get("MOTIVO") or l.get("PORQUE"),
                      "QUALIFY_NO_ENSAIO": (q.get(l["CANDIDATA_ID"]) or {}).get("PORQUE", "")[:120] or None})
    for n in fora:
        lista.append({"PARTE": "(ii)", "CANDIDATA_ID": n["CANDIDATE_ID"], "NOME": n["NOME"], "URL": n["URL"],
                      "DECISAO": "NUMERO %s (para: sem contrato, nunca READY automatico)" % n["SOURCE_ID"],
                      "SOURCE_ID": n["SOURCE_ID"], "TERRITORIO": n["TERRITORY"], "PAIS": n["PAIS"],
                      "ESTADO_NO_LIVRO": LC.estado_de(n["CANDIDATE_ID"])})
    for n in novas:
        h = n.get("MESMA_ORGANIZACAO") or {}
        b = bc.get(n["SOURCE_ID"]) or {}
        lista.append({"PARTE": "(iii)" if h.get("REGRA") == "D80(iii)" else "OUTRA_REGRA",
                      "CANDIDATA_ID": n["CANDIDATE_ID"], "NOME": n["NOME"], "URL": n["URL"],
                      "DECISAO": "NUMERO %s (%s)" % (n["SOURCE_ID"], n["TERRITORY"]),
                      "SOURCE_ID": n["SOURCE_ID"], "TERRITORIO": n["TERRITORY"],
                      "SITE": h.get("HOST"), "FONTES_DO_SITE": h.get("SOURCE_IDS_DO_SITE"),
                      "BUILD_CONTRACT": b.get("RESULTADO"), "BUILD_CONTRACT_PORQUE": (b.get("PORQUE") or "")[:160],
                      "ESTADO_NO_LIVRO": LC.estado_de(n["SOURCE_ID"])})
    continuam = Counter()
    for r in resultados:
        if r["TASK_TYPE"] == F.QUALIFY and r["RESULTADO"] == "BLOCK":
            p = r["PORQUE"]
            chave = ("RECUSADA pela porta" if p.startswith("RECUSADA") else
                     "D80(ii) numero cunhado, para" if p.startswith("D80(ii)") else
                     "fora de IT: site ja tem numero" if "ja tem numero" in p else
                     "territorio indeterminado (continua NAO SEI)" if "indeterminado" in p else p[:60])
            continuam[chave] += 1

    # REVERTER e conferir contra a referencia (a copia intocada do vivo)
    A.main(["--reverter", "--recibo=%s" % (recibos / "D80-RECIBO-REVERTER.json")])
    conf = None
    if a.get("referencia"):
        ref = {c["CANDIDATA_ID"]: c for c in json.loads(
            (Path(a["referencia"]) / "candidatas" / "FONTES-CANDIDATAS.json").read_text(encoding="utf-8"))["CANDIDATAS"]}
        agora = {c["CANDIDATA_ID"]: c for c in FN.carregar()["CANDIDATAS"]}
        diferentes = []
        for cid, c in agora.items():
            x = {k: v for k, v in c.items() if k != "RECUSAS_REVERTIDAS"}
            if x != ref.get(cid):
                diferentes.append(cid)
        conf = {"FICHAS": len(agora), "IGUAIS_A_REFERENCIA_TIRANDO_O_RASTO": len(agora) - len(diferentes),
                "DIFERENTES": diferentes[:20],
                "COM_RASTO_DA_REVERSAO": sum(1 for c in agora.values() if c.get("RECUSAS_REVERTIDAS"))}

    out = {"DATASET": "ENSAIO-D80-V1", "COPIA": str(RAIZ), "REDE_TENTATIVAS": len(REDE), "REDE": REDE[:10],
           "APLICAR": {k: aplicado[k] for k in ("POR_AGORA", "A_RECUSAR", "QUALIFY_A_REABRIR", "QUALIFY_REABERTAS")},
           "RECUSADAS": len(aplicado["RECUSADAS"]),
           "QUALIFY_CORRIDAS": len(reabertas), "QUALIFY_RESULTADOS": dict(Counter(
               r["RESULTADO"] for r in resultados if r["TASK_TYPE"] == F.QUALIFY)),
           "QUALIFY_BLOQUEADAS_POR": dict(continuam),
           "NUMEROS_NOVOS_IT": len(novas), "NUMEROS_FORA_DE_IT": [n["SOURCE_ID"] for n in fora],
           "BUILD_CONTRACT": dict(Counter(r["RESULTADO"] for r in resultados if r["TASK_TYPE"] == F.BUILD_CONTRACT)),
           "READY_NOVAS": sum(1 for x in lista if x.get("ESTADO_NO_LIVRO") == LC.READY_FOR_COLLECTION),
           "REVERSAO": conf, "LISTA_FINAL_POR_FONTE": lista}
    saida.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "LISTA_FINAL_POR_FONTE"}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
