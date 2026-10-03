#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""T2C · A VIA `agrometeo` SO COM CORPO DE BOLETIM — o que muda nos 1.309 textos.

    py scripts/regua_t2/medir_t2c.py [--base=REV]

Cada texto do acervo (o mesmo de medir_via_agrometeo.py) julgado em T2, T3, T4, T5, T7,
T9 e T10 pela admissao ANTES (`--base`, por omissao 2906ae74 = a regua entregue) e DEPOIS
(a arvore). Criterio da coordenacao: os 8 boletins certos continuam SIM, as 8 paginas de
site deixam de ser SIM, e NADA MAIS muda. Sem rede. Escreve MEDICAO-T2C-V1.json.
"""
import importlib.util as u
import json
import sys
from collections import Counter
from pathlib import Path

AQUI = Path(__file__).parent
sp = u.spec_from_file_location("mr", AQUI / "medir_regua_t2.py")
MR = u.module_from_spec(sp)
sp.loader.exec_module(MR)
sp = u.spec_from_file_location("mva", AQUI / "medir_via_agrometeo.py")
MVA = u.module_from_spec(sp)
sp.loader.exec_module(MVA)
A = MR.A
UNIVERSOS = ("T2", "T3", "T4", "T5", "T7", "T9", "T10")


def main():
    base = MR._arg("base", "2906ae74")
    antes = MR.admissao_da_revisao(base)
    leitura = {l["TEXTO_ID"]: l for l in json.load(open(AQUI / "MEDICAO-VIA-AGROMETEO-V1.json",
                                                         encoding="utf-8"))["LEITURA_DOS_16_NAO_SEI_PARA_SIM"]}
    corpus, vistos = [], set()
    import hashlib
    for d in MVA.PASTAS:
        if d.is_dir():
            for p in sorted(d.rglob("*.txt")):
                t = p.read_text(encoding="utf-8", errors="replace")
                h = hashlib.sha256(t.encode("utf-8")).hexdigest()
                if h not in vistos:
                    vistos.add(h)
                    corpus.append((d.name + ":" + p.name, t))
    mudou, t2 = [], Counter()
    for nome, t in corpus:
        for uv in UNIVERSOS:
            a, _ = MR.julgar(antes, t, uv)
            d, _ = MR.julgar(A, t, uv)
            if uv == "T2":
                t2["%s->%s" % (a, d)] += 1
            if a != d:
                tid = nome.split(":", 1)[1][:-4]
                mudou.append({"TEXTO": nome, "UNIVERSO": uv, "ANTES": a, "DEPOIS": d,
                              "LEITURA_T2B": (leitura.get(tid) or {}).get("LIDO")})
    certos = [l for l in leitura.values() if l["LIDO"].startswith("CERTO")]
    errados = [l for l in leitura.values() if l["LIDO"].startswith("ERRADO")]

    def depois(tid):
        for nome, t in corpus:
            if nome.split(":", 1)[1][:-4] == tid:
                return MR.julgar(A, t, "T2")[0]
    out = {"DATASET": "MEDICAO-T2C-V1", "BASE": base, "VERSAO_DA_REGRA": A.VERSAO_DA_REGRA,
           "TEXTOS": len(corpus), "JULGAMENTOS": len(corpus) * len(UNIVERSOS),
           "T2_ANTES_DEPOIS": dict(sorted(t2.items())), "MUDANCAS": mudou,
           "OS_8_CERTOS_DEPOIS": {l["TEXTO_ID"]: depois(l["TEXTO_ID"]) for l in certos},
           "OS_8_ERRADOS_DEPOIS": {l["TEXTO_ID"]: depois(l["TEXTO_ID"]) for l in errados}}
    out["CRITERIO"] = {
        "CERTOS_CONTINUAM_SIM": all(v == A.SIM for v in out["OS_8_CERTOS_DEPOIS"].values()),
        "ERRADOS_DEIXAM_DE_SER_SIM": all(v != A.SIM for v in out["OS_8_ERRADOS_DEPOIS"].values()),
        "NADA_MAIS_MUDA": all(m["LEITURA_T2B"] and m["LEITURA_T2B"].startswith("ERRADO")
                              and m["UNIVERSO"] == "T2" for m in mudou)}
    (AQUI / "MEDICAO-T2C-V1.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + chr(10),
                                              encoding="utf-8", newline=chr(10))
    print(json.dumps({k: out[k] for k in ("TEXTOS", "JULGAMENTOS", "T2_ANTES_DEPOIS", "CRITERIO")},
                     ensure_ascii=False))
    print(len(mudou), "mudancas:", Counter((m["UNIVERSO"], m["ANTES"], m["DEPOIS"]) for m in mudou))
    return 0 if all(out["CRITERIO"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
