#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""T1-JANELA · a lista de textos a ler, pela regra fixa do protocolo. Sem rede.

    py scripts/regua_t1/selecionar_t1.py

Escreve %USERPROFILE%/sintonia-gabarito/REGUA-T1-V1/A-LER.json (fora do Git) e
scripts/regua_t1/SELECAO-T1-V1.json (no Git: id, estrato, caminho, sha256).
"""
import hashlib
import json
import os
import random
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
CASA = Path(os.environ.get("USERPROFILE", str(Path.home())))
PASTAS = [CASA / "sintonia-gabarito" / "REGUA-T2-V1" / "textos",
          CASA / "sintonia-sala-italia" / "armazem" / "NAO_SEI" / "derivados" / "TEXT_EXTRACTION",
          CASA / "orca" / "workspaces" / "eame-sintonia" / "lote-76-v1" / "NAO_SEI" / "derivados"]
COLHEITA = re.compile(r"(?<![a-z])(vendemmia|raccolta|trebbiatura|semina|colheita|semeadura|harvest)(?![a-z])", re.I)


def main():
    corpus, vistos = [], set()
    for d in PASTAS:
        if d.is_dir():
            for p in sorted(d.rglob("*.txt")):
                t = p.read_text(encoding="utf-8", errors="replace")
                h = hashlib.sha256(t.encode("utf-8")).hexdigest()
                if h not in vistos:
                    vistos.add(h)
                    corpus.append({"ID": h[:16], "SHA256": h, "CAMINHO": str(p), "TEXTO": t})
    g3 = json.load(open(RAIZ / "scripts" / "regua_t2" / "GABARITO-T2-V3.json", encoding="utf-8"))
    yes_t2 = {i["TEXTO_SHA256"] for i in g3["ITENS"] if i["JANELA"] == "YES"}
    # o id do inventario T2 e o sha do texto normalizado; no corpus, o do ficheiro — casar pelos dois
    por_id = {c["ID"]: c for c in corpus}
    sel, usados = [], set()
    for h in sorted(yes_t2):
        c = por_id.get(h[:16]) or next((x for x in corpus if x["SHA256"] == h), None)
        if c and c["ID"] not in usados:
            usados.add(c["ID"]); sel.append(dict(c, ESTRATO="1_YES_T2"))
    col = [c for c in corpus if c["ID"] not in usados and COLHEITA.search(c["TEXTO"])]
    for c in col[:60]:
        usados.add(c["ID"]); sel.append(dict(c, ESTRATO="2_COLHEITA"))
    resto = [c for c in corpus if c["ID"] not in usados]
    for c in random.Random(24092026).sample(resto, 60):
        usados.add(c["ID"]); sel.append(dict(c, ESTRATO="3_ACASO"))
    fora = CASA / "sintonia-gabarito" / "REGUA-T1-V1"
    fora.mkdir(parents=True, exist_ok=True)
    (fora / "A-LER.json").write_text(json.dumps(sel, ensure_ascii=False), encoding="utf-8")
    meta = [{k: s[k] for k in ("ID", "SHA256", "CAMINHO", "ESTRATO")} for s in sel]
    (Path(__file__).parent / "SELECAO-T1-V1.json").write_text(json.dumps(
        {"DATASET": "SELECAO-T1-V1", "CORPUS": len(corpus), "COLHEITA_NO_CORPUS": len(col),
         "ITENS": meta}, ensure_ascii=False, indent=1) + chr(10), encoding="utf-8", newline=chr(10))
    from collections import Counter
    print(len(corpus), len(col), Counter(s["ESTRATO"] for s in sel))


if __name__ == "__main__":
    main()
