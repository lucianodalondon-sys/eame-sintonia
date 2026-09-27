#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""T2-REGUA · O QUE A VIA `agrometeo` ACRESCENTA, NO MESMO ACERVO DA MEDICAO (1.309 textos).

    py scripts/regua_t2/medir_via_agrometeo.py

Decisao da coordenacao (24/09): os boletins agrometeorologicos regionais sao nucleo da D29 e
ficam na regua ANTES de instalar. A regua instalavel ja os admite pela via `agrometeo` + 2
condicoes; isto mede o efeito dessa via sozinha: cada texto julgado em T2 COM a via (a regua
como esta) e SEM ela (ANCORAS["T2"]["AGROMETEO"] trocado por uma forma que nao casa em nada).
Sem rede. Escreve MEDICAO-VIA-AGROMETEO-V1.json com a transicao de cada texto e uma amostra
de 20 casos para LER (semente fixa).
"""
import hashlib
import json
import os
import random
import sys
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(RAIZ / "admissao"), str(RAIZ)]
import admissao as A  # noqa: E402

CASA = Path(os.environ.get("USERPROFILE", str(Path.home())))
PASTAS = [CASA / "sintonia-gabarito" / "REGUA-T2-V1" / "textos",
          CASA / "sintonia-sala-italia" / "armazem" / "NAO_SEI" / "derivados" / "TEXT_EXTRACTION",
          CASA / "orca" / "workspaces" / "eame-sintonia" / "lote-76-v1" / "NAO_SEI" / "derivados"]
SAIDA = Path(__file__).parent / "MEDICAO-VIA-AGROMETEO-V1.json"


def julgar(texto):
    return A._do_universo({"texto": texto}, "T2", A.PERGUNTAS_DO_UNIVERSO["T2"])


def main():
    corpus, vistos = [], set()
    for d in PASTAS:
        if d.is_dir():
            for p in sorted(d.rglob("*.txt")):
                t = p.read_text(encoding="utf-8", errors="replace")
                h = hashlib.sha256(t.encode("utf-8")).hexdigest()
                if h not in vistos:
                    vistos.add(h)
                    corpus.append((d.name + ":" + p.name, str(p), t))
    com = [julgar(t) for _n, _p, t in corpus]
    original = A.ANCORAS["T2"]["AGROMETEO"]
    A.ANCORAS["T2"]["AGROMETEO"] = "zzzz-via-desligada-zzzz"
    try:
        sem = [julgar(t) for _n, _p, t in corpus]
    finally:
        A.ANCORAS["T2"]["AGROMETEO"] = original
    trans = Counter("%s->%s" % (s[0], c[0]) for s, c in zip(sem, com))
    mudou = [{"TEXTO": n, "CAMINHO": p, "SEM_A_VIA": s[0], "COM_A_VIA": c[0],
              "PALAVRAS": c[2].get("palavras"), "ANCORAS": c[2].get("ancoras")}
             for (n, p, _t), s, c in zip(corpus, sem, com) if s[0] != c[0]]
    amostra = random.Random(24092026).sample(mudou, min(20, len(mudou)))
    out = {"DATASET": "MEDICAO-VIA-AGROMETEO-V1", "VERSAO_DA_REGRA": A.VERSAO_DA_REGRA,
           "TEXTOS_NO_CORPUS": len(corpus), "TRANSICOES_SEM_PARA_COM": dict(sorted(trans.items())),
           "MUDARAM": len(mudou), "SIM_COM_A_VIA": sum(1 for c in com if c[0] == A.SIM),
           "SIM_SEM_A_VIA": sum(1 for s in sem if s[0] == A.SIM),
           "AMOSTRA_20_PARA_LER": amostra, "TODOS_OS_QUE_MUDARAM": mudou}
    SAIDA.write_text(json.dumps(out, ensure_ascii=False, indent=1) + chr(10), encoding="utf-8", newline=chr(10))
    print(json.dumps({k: out[k] for k in ("TEXTOS_NO_CORPUS", "TRANSICOES_SEM_PARA_COM", "MUDARAM",
                                          "SIM_COM_A_VIA", "SIM_SEM_A_VIA")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
