#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""T2-REGUA · MONTA O GABARITO T2 A PARTIR DO INVENTARIO E DOS ROTULOS — SEM REDE.

    py scripts/regua_t2/montar_gabarito_t2.py [--dir=DIR]

Entrada (fora do Git, em DIR = %USERPROFILE%\\sintonia-gabarito\\REGUA-T2-V1):
    INVENTARIO.json   o que `inventariar_t2.py` juntou
    A-ROTULAR.json    a ordem dos textos lidos a mao
    rotulos.tsv       N \\t UNIVERSE_MATCH \\t SINTONIA_RELEVANT \\t CONTEUDO \\t PORQUE \\t TRECHO
                      (uma linha repetida mais abaixo substitui a de cima)
Saida (no Git): scripts/regua_t2/GABARITO-T2-V1.json

Os rotulos antigos (GABARITO-T2-T12-V2/V3) nao sao refeitos: YES se o conteudo
foi julgado T2 (inclui os REROUTE:T2), NO se foi julgado de outro universo ou de
nenhum. Os NAO_SEI ficam fora da conta, contados a parte.
"""
from __future__ import annotations

import json
import os
import re
import sys
from collections import Counter
from pathlib import Path

AQUI = Path(__file__).resolve().parent
CASA = Path(os.environ.get("USERPROFILE", str(Path.home())))


def _arg(nome, omissao):
    return next((a.split("=", 1)[1] for a in sys.argv[1:] if a.startswith("--%s=" % nome)), omissao)


def serie(it: dict) -> str | None:
    c = (it.get("CAMINHO") or "").replace("\\", "/").lower()
    if re.search(r"(^|[-/])agro_\d", c.rsplit("/", 1)[-1]):
        return "ARPAV-AGROMETEO-INFORMA"
    if "nheowl0530" in c:
        return "SIAS-PRECIPITAZIONI-GIORNALIERE"
    return None


def main() -> int:
    d = Path(_arg("dir", str(CASA / "sintonia-gabarito" / "REGUA-T2-V1")))
    inv = {i["TEXTO_ID"]: i for i in json.load(open(d / "INVENTARIO.json", encoding="utf-8"))["ITENS"]}
    ordem = json.load(open(d / "A-ROTULAR.json", encoding="utf-8"))
    novos = {}
    for linha in open(d / "rotulos.tsv", encoding="utf-8"):
        if not linha.strip():
            continue
        n, um, sr, cont, porque, trecho = (linha.rstrip("\n").split("\t") + [""] * 6)[:6]
        novos[ordem[int(n)]] = {"UNIVERSE_MATCH": um, "SINTONIA_RELEVANT": sr, "CONTEUDO": cont,
                                "PORQUE": porque, "TRECHO": trecho, "ROTULO_DE": "T2-REGUA-V1 (Claude)"}
    itens = []
    for tid, it in inv.items():
        r = novos.get(tid)
        if r is None and it.get("ROTULO_ANTIGO"):
            a = it["ROTULO_ANTIGO"]
            cont = a.get("UNIVERSO_DO_CONTEUDO")
            um = "YES" if cont == "T2" or a.get("ACTION") == "REROUTE:T2" else "NO"
            r = {"UNIVERSE_MATCH": um, "SINTONIA_RELEVANT": a.get("SINTONIA_RELEVANT"),
                 "CONTEUDO": cont, "PORQUE": a.get("PORQUE"), "TRECHO": None,
                 "ROTULO_DE": a.get("DE")}
        if r is None:
            continue                       # no corpus dos vizinhos, fora do gabarito
        itens.append({"TEXTO_ID": tid, "TEXTO_SHA256": it["TEXTO_SHA256"], "SOURCE_ID": it["SOURCE_ID"],
                      "ORIGEM": it["ORIGEM"], "URL": it.get("URL"),
                      "CAMINHO_FORA_DO_GIT": it["CAMINHO"], "BYTES_SHA256": it["BYTES_SHA256"],
                      "SERIE": serie(it), **r})
    c = Counter(i["UNIVERSE_MATCH"] for i in itens)
    pos = [i for i in itens if i["UNIVERSE_MATCH"] == "YES"]
    out = {"DATASET": "GABARITO-T2-V1", "PROTOCOLO": "scripts/regua_t2/PROTOCOLO-GABARITO-T2.md",
           "VALIDADO_POR_HUMANO": "NAO",
           "CONTAGEM": {"ITENS": len(itens), "YES": c["YES"], "NO": c["NO"], "NAO_SEI": c["NAO_SEI"],
                        "MINIMO": 20, "PRONTO": c["YES"] >= 20 and c["NO"] >= 20,
                        "YES_POR_SERIE": dict(Counter(i["SERIE"] or "(avulso)" for i in pos)),
                        "YES_POR_FONTE": dict(Counter(i["SOURCE_ID"] for i in pos)),
                        "YES_DE_ROTULO_ANTIGO": sum(1 for i in pos if not i["ROTULO_DE"].startswith("T2-REGUA")),
                        "SINTONIA_RELEVANT_NOS_YES": dict(Counter(i["SINTONIA_RELEVANT"] for i in pos))},
           "ITENS": sorted(itens, key=lambda i: (i["UNIVERSE_MATCH"], i["SOURCE_ID"], i["TEXTO_ID"]))}
    (AQUI / "GABARITO-T2-V1.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n",
                                              encoding="utf-8", newline="\n")
    print(json.dumps(out["CONTAGEM"], ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
