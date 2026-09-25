#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""T1-JANELA · monta GABARITO-T1-V1.json a partir da selecao e dos rotulos lidos (fora do Git:
%USERPROFILE%/sintonia-gabarito/REGUA-T1-V1/rotulos-{1,2,3}.tsv — ID \t T1_JANELA \t _ \t PORQUE).
Copia os rotulos para scripts/regua_t1/rotulos/."""
import json
import os
import shutil
from collections import Counter
from pathlib import Path

AQUI = Path(__file__).parent
FORA = Path(os.environ.get("USERPROFILE", str(Path.home()))) / "sintonia-gabarito" / "REGUA-T1-V1"


def main():
    sel = {i["ID"]: i for i in json.load(open(AQUI / "SELECAO-T1-V1.json", encoding="utf-8"))["ITENS"]}
    (AQUI / "rotulos").mkdir(exist_ok=True)
    itens = []
    for n in (1, 2, 3):
        f = FORA / ("rotulos-%d.tsv" % n)
        shutil.copyfile(f, AQUI / "rotulos" / f.name)
        for linha in open(f, encoding="utf-8"):
            if linha.strip():
                i, v, _a, porque = (linha.rstrip(chr(10)).split(chr(9)) + [""] * 4)[:4]
                itens.append(dict(sel[i], T1_JANELA=v, PORQUE=porque, ROTULO_DE="T1-JANELA (Claude)"))
    c = Counter(i["T1_JANELA"] for i in itens)
    por = {e: dict(Counter(i["T1_JANELA"] for i in itens if i["ESTRATO"] == e))
           for e in sorted({i["ESTRATO"] for i in itens})}
    out = {"DATASET": "GABARITO-T1-V1", "PROTOCOLO": "scripts/regua_t1/PROTOCOLO-GABARITO-T1.md",
           "VALIDADO_POR_HUMANO": "NAO",
           "CONTAGEM": {"ITENS": len(itens), "YES": c["YES"], "NO": c["NO"], "NAO_SEI": c["NAO_SEI"],
                        "POR_ESTRATO": por, "MINIMO": 20, "PRONTO": c["YES"] >= 20 and c["NO"] >= 20},
           "ITENS": itens}
    (AQUI / "GABARITO-T1-V1.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + chr(10),
                                              encoding="utf-8", newline=chr(10))
    print(json.dumps(out["CONTAGEM"], ensure_ascii=False))


if __name__ == "__main__":
    main()
