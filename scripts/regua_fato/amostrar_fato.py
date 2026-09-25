#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""REGUA-DO-TIPO-DE-FATO · a amostra do gabarito, pelo PROTOCOLO (semente 62062, prova cega antes de ler).

    py scripts/regua_fato/amostrar_fato.py [--sala=C:/Users/London1/lugar-fato/sala-78.json]

Sem rede, sem banco. Sala = a copia so-leitura das 78 linhas (um texto por sha256 normalizado, com as
linhas que o partilham). Acervo = 100 do mesmo acervo da REGUAS-T4-T5-T9, sem os textos da Sala.
Os textos ficam FORA do Git (%USERPROFILE%/sintonia-gabarito/REGUA-FATO-V1/textos/<id>.txt).
"""
import hashlib
import json
import random
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
AQUI = Path(__file__).parent
sys.path.insert(0, str(RAIZ / "scripts" / "regua_t4t5t9"))
import amostrar as AT  # noqa: E402  (as mesmas pastas do acervo)

DESTINO = Path.home() / "sintonia-gabarito" / "REGUA-FATO-V1" / "textos"
SEMENTE = 62062
N_ACERVO = 100
CEGA = 0.30


def _h(t):
    return hashlib.sha256(re.sub(r"\s+", " ", t).strip().encode("utf-8")).hexdigest()


def main():
    sala_f = Path(AT._arg("sala", "C:/Users/London1/lugar-fato/sala-78.json"))
    linhas = json.loads(sala_f.read_text(encoding="utf-8"))
    sala = {}
    for l in linhas:
        h = _h(l["texto"])
        s = sala.setdefault(h, {"ID": h[:16], "SHA256_NORMALIZADO": h, "ORIGEM": "SALA-78", "LINHAS": [],
                                "_t": l["texto"]})
        s["LINHAS"].append({"item_id": l["item_id"], "source_id": l["source_id"], "universo": l["universo"]})
    acervo, vistos = [], set(sala)
    for d, nome in AT.pastas():
        for p in sorted(d.rglob("*.txt")) if d.is_dir() else []:
            t = p.read_text(encoding="utf-8", errors="replace")
            h = _h(t)
            if h in vistos or len(t.strip()) < 200:
                continue
            vistos.add(h)
            acervo.append({"ID": h[:16], "SHA256_NORMALIZADO": h, "ORIGEM": nome, "FICHEIRO": p.name, "_t": t})
    rnd = random.Random(SEMENTE)
    conj = {"SALA": sorted(sala.values(), key=lambda x: x["ID"]),
            "ACERVO": rnd.sample(sorted(acervo, key=lambda x: x["ID"]), N_ACERVO)}
    itens = []
    for nome, L in conj.items():
        L = list(L)
        rnd.shuffle(L)
        ncega = round(len(L) * CEGA)
        for i, x in enumerate(L):
            DESTINO.mkdir(parents=True, exist_ok=True)
            (DESTINO / (x["ID"] + ".txt")).write_text(x["_t"], encoding="utf-8")
            itens.append(dict({k: v for k, v in x.items() if k != "_t"}, CONJUNTO_ORIGEM=nome,
                              CONJUNTO="PROVA_CEGA" if i < ncega else "GABARITO"))
    out = {"DATASET": "A-ROTULAR-FATO-V1", "PROTOCOLO": "scripts/regua_fato/PROTOCOLO-GABARITO-FATO.md",
           "SEMENTE": SEMENTE, "SALA_COPIA": str(sala_f),
           "SALA_COPIA_SHA256": hashlib.sha256(sala_f.read_bytes()).hexdigest(),
           "SALA_LINHAS": len(linhas), "SALA_TEXTOS_UNICOS": len(sala), "ACERVO_POOL": len(acervo),
           "TEXTOS_FORA_DO_GIT": str(DESTINO), "ITENS": itens}
    (AQUI / "A-ROTULAR-FATO.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    from collections import Counter
    print(json.dumps({k: out[k] for k in ("SALA_LINHAS", "SALA_TEXTOS_UNICOS", "ACERVO_POOL", "SALA_COPIA_SHA256")}),
          dict(Counter((x["CONJUNTO_ORIGEM"], x["CONJUNTO"]) for x in itens)))


if __name__ == "__main__":
    main()
