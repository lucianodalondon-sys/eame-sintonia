#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LUGAR-DO-PUBLICADOR · o trecho de cada sede provada, para ler a mao (so leitura, sem rede).
Refaz a leitura da regra unica (curadoria/sede_da_fonte) sobre as MESMAS paginas guardadas que o achar_paginas_de_sede
usa e escreve o RECIBO (CAP, comune, sigla, paginas, trecho)."""
import collections, json, os, sys

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(RAIZ, "ferramentas", "sede37"))
import achar_paginas_de_sede as A  # noqa: E402

pag, saida = sys.argv[1], sys.argv[2]
fontes = json.load(open(pag, encoding="utf-8"))["FONTES"]
contratos = {c["SOURCE_ID"]: c for c in json.load(open(os.path.join(A.VIVO, "curadoria", "italy_contracts_curator.json"),
                                                        encoding="utf-8"))["FONTES"]}
raws = collections.defaultdict(list)
for r in json.load(open(os.path.join(A.ACERVO, "raw.json"), encoding="utf-8")):
    raws[r["source_id"]].append(r)
raizes = open(os.path.join(A.ACERVO, "raizes.txt"), encoding="utf-8").read().strip().split(";")
out = []
for f in fontes:
    if f["SEDE_SEM_REDE"]["SOURCE_LOCATION"] == A.S.NAO_SEI and not f.get("SEDE_SEM_REDE_CANDIDATA"):
        continue
    pags = A.paginas_da_fonte(f["SOURCE_ID"], raws, raizes, contratos.get(f["SOURCE_ID"]) or {})
    r = A.S.sede_das_paginas([(p[3] or p[1], p[2], p[4]) for p in pags])
    rec = r.get("RECIBO") or r.get("CANDIDATA_NAO_PROVADA") or {}
    out.append({"SOURCE_ID": f["SOURCE_ID"], "NOME": f["NOME"], "SOURCE_LOCATION": r["SOURCE_LOCATION"],
                "RECIBO": rec, "PORQUE": r["SOURCE_LOCATION_BASIS"][:200]})
    print("== %s %s -> %s\n   %s" % (f["SOURCE_ID"], f["NOME"], r["SOURCE_LOCATION"], (rec.get("TRECHO") or "")[:300]))
json.dump(out, open(saida, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
