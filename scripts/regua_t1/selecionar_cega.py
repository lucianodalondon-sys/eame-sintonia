#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""T1B · PROVA CEGA — a escolha dos 30 textos, por regra fixa, ANTES de olhar e ANTES da regua.

    py scripts/regua_t1/selecionar_cega.py

Regra (commitada antes de correr):
  * universo: os 1.309 textos do acervo MENOS os 181 do gabarito T1-V1 (os que serviram
    para escolher as palavras);
  * 15 ao acaso entre os que nomeiam uma cultura (CULTURA_OBRIGATORIA["T1"], palavra
    inteira) — sem isso uma amostra ao acaso quase nao teria janela nenhuma. ⚠️ A cultura
    e METADE da regua: este estrato enriquece em positivos e isso fica dito;
  * 15 ao acaso entre os restantes;
  * semente 25092026. Textos com menos de 400 caracteres (so titulo) ficam fora da sorte.
Escreve %USERPROFILE%/sintonia-gabarito/REGUA-T1-V1/CEGA-A-LER.json (sem veredito da regua)
e scripts/regua_t1/SELECAO-CEGA-T1-V1.json (id, estrato, caminho, sha256).
"""
import hashlib
import json
import os
import random
import sys
from pathlib import Path

AQUI = Path(__file__).parent
RAIZ = AQUI.parents[1]
sys.path[:0] = [str(RAIZ / "admissao"), str(RAIZ)]
import admissao as A  # noqa: E402
CASA = Path(os.environ.get("USERPROFILE", str(Path.home())))
PASTAS = [CASA / "sintonia-gabarito" / "REGUA-T2-V1" / "textos",
          CASA / "sintonia-sala-italia" / "armazem" / "NAO_SEI" / "derivados" / "TEXT_EXTRACTION",
          CASA / "orca" / "workspaces" / "eame-sintonia" / "lote-76-v1" / "NAO_SEI" / "derivados"]


def main():
    usados = {i["ID"] for i in json.load(open(AQUI / "SELECAO-T1-V1.json", encoding="utf-8"))["ITENS"]}
    corpus, vistos = [], set()
    for d in PASTAS:
        if d.is_dir():
            for p in sorted(d.rglob("*.txt")):
                t = p.read_text(encoding="utf-8", errors="replace")
                h = hashlib.sha256(t.encode("utf-8")).hexdigest()
                if h not in vistos and h[:16] not in usados and len(" ".join(t.split())) >= 400:
                    vistos.add(h)
                    corpus.append({"ID": h[:16], "SHA256": h, "CAMINHO": str(p), "TEXTO": t})
    cult = A.CULTURA_OBRIGATORIA["T1"]
    com = [c for c in corpus if A._casa(cult, A._dobrar(c["TEXTO"]))]
    sem = [c for c in corpus if c not in com]
    rnd = random.Random(25092026)
    sel = [dict(c, ESTRATO="C_COM_CULTURA") for c in rnd.sample(com, 15)] + \
          [dict(c, ESTRATO="S_SEM_CULTURA") for c in rnd.sample(sem, 15)]
    fora = CASA / "sintonia-gabarito" / "REGUA-T1-V1"
    (fora / "CEGA-A-LER.json").write_text(json.dumps(sel, ensure_ascii=False), encoding="utf-8")
    (AQUI / "SELECAO-CEGA-T1-V1.json").write_text(json.dumps(
        {"DATASET": "SELECAO-CEGA-T1-V1", "UNIVERSO_FORA_DO_GABARITO": len(corpus), "COM_CULTURA": len(com),
         "ITENS": [{k: s[k] for k in ("ID", "SHA256", "CAMINHO", "ESTRATO")} for s in sel]},
        ensure_ascii=False, indent=1) + chr(10), encoding="utf-8", newline=chr(10))
    print(len(corpus), len(com), len(sel))


if __name__ == "__main__":
    main()
