#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""REGUAS-T4-T5-T9 · a amostra do gabarito, pelo PROTOCOLO (estratos, semente 45945, prova cega antes).

    py scripts/regua_t4t5t9/amostrar.py [--armazem=C:/ajustes/armazem-textos]

Sem rede. Os textos ficam FORA do Git (%USERPROFILE%/sintonia-gabarito/REGUA-T4T5T9-V1/textos/<id>.txt);
no Git fica A-ROTULAR.json com id, sha256, estrato, conjunto (GABARITO | PROVA_CEGA) e origem.
"""
import hashlib
import json
import random
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
AQUI = Path(__file__).parent
CASA = Path.home()
DESTINO = CASA / "sintonia-gabarito" / "REGUA-T4T5T9-V1" / "textos"
SEMENTE = 45945
POR_ESTRATO = 40
CEGA = 0.30

SONDAS = {   # do protocolo, palavra inteira, sem acento dobrado (so minusculas)
    "SONDA-T9": r"\b(basf|bayer|syngenta|corteva|fmc|upl|nufarm|sumitomo|certis|gowan|belchim|sipcam|isagro|adama)\b",
    "SONDA-T4": r"(sostanza attiva|sostanze attive|prodotto fitosanitario|prodotti fitosanitari|\brevoca\b|"
                r"\bautorizzazione\b|\bregistrazione\b|\betichetta\b|\blmr\b|limite massimo di residuo|\bderoga\b)",
    "SONDA-T5": r"(\bsperimentazione\b|\bsperimentale\b|prova di campo|\brisultati\b|\bdoi\b|\bricerca\b|\bstudio\b|"
                r"progetto di ricerca|\btesi\b)",
}


def _arg(n, d=None):
    return next((x.split("=", 1)[1] for x in sys.argv[1:] if x.startswith("--%s=" % n)), d)


def pastas():
    return [(CASA / "sintonia-gabarito" / "REGUA-T2-V1" / "textos", "REGUA-T2-V1"),
            (CASA / "sintonia-gabarito" / "REGUA-T1-V1", "REGUA-T1-V1"),
            (Path(_arg("armazem", "C:/ajustes/armazem-textos")), "ARMAZEM-COPIA"),
            (RAIZ / "data" / "derivados" / "texto", "GIT-DERIVADOS")]


def main():
    vistos, pool = set(), []
    for d, nome in pastas():
        for p in sorted(d.rglob("*.txt")) if d.is_dir() else []:
            t = p.read_text(encoding="utf-8", errors="replace")
            h = hashlib.sha256(re.sub(r"\s+", " ", t).strip().encode("utf-8")).hexdigest()
            if h in vistos or len(t.strip()) < 200:
                continue
            vistos.add(h)
            pool.append({"ID": h[:16], "SHA256_NORMALIZADO": h, "ORIGEM": nome, "FICHEIRO": p.name, "_t": t})
    estratos = {k: [] for k in list(SONDAS) + ["ACASO"]}
    for x in pool:
        tl = x["_t"].lower()
        for k, rx in SONDAS.items():
            if re.search(rx, tl):
                estratos[k].append(x)
                break
        else:
            estratos["ACASO"].append(x)
    rnd = random.Random(SEMENTE)
    amostra = []
    for k in list(SONDAS) + ["ACASO"]:
        L = sorted(estratos[k], key=lambda x: x["ID"])
        esc = rnd.sample(L, min(POR_ESTRATO, len(L)))
        ncega = round(len(esc) * CEGA)
        for i, x in enumerate(esc):
            amostra.append(dict({k2: v for k2, v in x.items() if k2 != "_t"}, ESTRATO=k,
                                CONJUNTO="PROVA_CEGA" if i < ncega else "GABARITO",
                                DISPONIVEIS_NO_ESTRATO=len(L)))
            DESTINO.mkdir(parents=True, exist_ok=True)
            (DESTINO / (x["ID"] + ".txt")).write_text(x["_t"], encoding="utf-8")
    out = {"DATASET": "A-ROTULAR-T4T5T9-V1", "PROTOCOLO": "scripts/regua_t4t5t9/PROTOCOLO-GABARITO-T4-T5-T9.md",
           "SEMENTE": SEMENTE, "POOL": len(pool), "ESTRATOS": {k: len(v) for k, v in estratos.items()},
           "TEXTOS_FORA_DO_GIT": str(DESTINO), "ITENS": amostra}
    (AQUI / "A-ROTULAR.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({k: out[k] for k in ("POOL", "ESTRATOS")}, ensure_ascii=False),
          "amostra", len(amostra), "cega", sum(1 for a in amostra if a["CONJUNTO"] == "PROVA_CEGA"))


if __name__ == "__main__":
    main()
