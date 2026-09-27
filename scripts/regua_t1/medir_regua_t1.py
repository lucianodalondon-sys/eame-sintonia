#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""T1-JANELA · mede a regua T1 no gabarito (por estrato) e prova os vizinhos. Sem rede.

    py scripts/regua_t1/medir_regua_t1.py [--base=REV]

1. GABARITO-T1-V1: precisao/recall de SIM, por estrato (o estrato 2 foi escolhido por
   palavra — a precisao dele e enviesada e e dada a parte). DENTRO da amostra.
2. VIZINHOS: os 1.309 textos julgados em T2 T3 T4 T5 T7 T9 T10 pela admissao ANTES
   (`--base`, por omissao 84c235da = instalado) e DEPOIS. Tem de dar 0.
3. T1 no corpus (antes NAO_SE_APLICA em tudo).
"""
import hashlib
import importlib.util as u
import json
import sys
from collections import Counter
from pathlib import Path

AQUI = Path(__file__).parent
RAIZ = AQUI.parents[1]
sp = u.spec_from_file_location("mr", RAIZ / "scripts" / "regua_t2" / "medir_regua_t2.py")
MR = u.module_from_spec(sp)
sp.loader.exec_module(MR)
sp = u.spec_from_file_location("mva", RAIZ / "scripts" / "regua_t2" / "medir_via_agrometeo.py")
MVA = u.module_from_spec(sp)
sp.loader.exec_module(MVA)
A = MR.A
VIZINHOS = ("T2", "T3", "T4", "T5", "T7", "T9", "T10")


def main():
    base = MR._arg("base", "84c235da")
    g = json.load(open(AQUI / "GABARITO-T1-V1.json", encoding="utf-8"))
    itens, sha_mau = [], []
    for it in g["ITENS"]:
        b = Path(it["CAMINHO"]).read_bytes()
        if hashlib.sha256(b.decode("utf-8", "replace").encode("utf-8")).hexdigest() != it["SHA256"]:
            sha_mau.append(it["ID"])
            continue
        r, ev = MR.julgar(A, b.decode("utf-8", "replace"), "T1")
        itens.append({"ID": it["ID"], "ESTRATO": it["ESTRATO"], "OURO": it["T1_JANELA"], "REGUA": r,
                      "PALAVRAS": ev.get("palavras"), "FALTA": ev.get("falta")})

    def conta(xs):
        o = [i for i in xs if i["OURO"] in ("YES", "NO")]
        tp = sum(1 for i in o if i["OURO"] == "YES" and i["REGUA"] == A.SIM)
        fp = sum(1 for i in o if i["OURO"] == "NO" and i["REGUA"] == A.SIM)
        fn = sum(1 for i in o if i["OURO"] == "YES" and i["REGUA"] != A.SIM)
        return {"TP": tp, "FP": fp, "FN": fn,
                "PRECISAO": round(tp / (tp + fp), 3) if tp + fp else None,
                "RECALL": round(tp / (tp + fn), 3) if tp + fn else None,
                "YES_QUE_SAIRAM_NAO": sum(1 for i in o if i["OURO"] == "YES" and i["REGUA"] == A.NAO),
                "MATRIZ": dict(sorted(Counter("%s->%s" % (i["OURO"], i["REGUA"]) for i in xs).items()))}
    por = {e: conta([i for i in itens if i["ESTRATO"] == e]) for e in sorted({i["ESTRATO"] for i in itens})}
    antes = MR.admissao_da_revisao(base)
    corpus, vistos = [], set()
    for d in MVA.PASTAS:
        if d.is_dir():
            for p in sorted(d.rglob("*.txt")):
                t = p.read_text(encoding="utf-8", errors="replace")
                h = hashlib.sha256(t.encode("utf-8")).hexdigest()
                if h not in vistos:
                    vistos.add(h)
                    corpus.append((d.name + ":" + p.name, t))
    mudou, t1 = [], Counter()
    for nome, t in corpus:
        for uv in VIZINHOS:
            a, _ = MR.julgar(antes, t, uv)
            d, _ = MR.julgar(A, t, uv)
            if a != d:
                mudou.append({"TEXTO": nome, "UNIVERSO": uv, "ANTES": a, "DEPOIS": d})
        a, _ = MR.julgar(antes, t, "T1")
        d, _ = MR.julgar(A, t, "T1")
        t1["%s->%s" % (a, d)] += 1
    out = {"DATASET": "MEDICAO-REGUA-T1-V1", "BASE": base, "VERSAO_DA_REGRA": A.VERSAO_DA_REGRA,
           "REGUA": {"MOMENTOS": A.PERGUNTAS_DO_UNIVERSO["T1"], "CULTURA": A.CULTURA_OBRIGATORIA["T1"],
                     "SINAIS_MINIMOS": A.SINAIS_MINIMOS},
           "SHA_NAO_CONFERE": sha_mau, "MEDIDO_DENTRO_DA_AMOSTRA": True,
           "T1_TOTAL": conta(itens), "T1_POR_ESTRATO": por,
           "ERROS": [i for i in itens if i["OURO"] in ("YES", "NO") and (i["OURO"] == "YES") != (i["REGUA"] == A.SIM)],
           "VIZINHOS": {"TEXTOS": len(corpus), "JULGAMENTOS": len(corpus) * len(VIZINHOS),
                        "VEREDITOS_VIZINHOS_MUDADOS": len(mudou), "MUDANCAS": mudou[:50]},
           "T1_NO_CORPUS_ANTES_DEPOIS": dict(sorted(t1.items()))}
    (AQUI / "MEDICAO-REGUA-T1-V1.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + chr(10),
                                                   encoding="utf-8", newline=chr(10))
    print(json.dumps({"TOTAL": out["T1_TOTAL"], "POR_ESTRATO": {k: {x: v[x] for x in ("TP", "FP", "FN", "PRECISAO", "RECALL")} for k, v in por.items()},
                      "SHA_MAU": len(sha_mau), "VIZINHOS": out["VIZINHOS"]["VEREDITOS_VIZINHOS_MUDADOS"],
                      "JULGAMENTOS": out["VIZINHOS"]["JULGAMENTOS"], "T1_CORPUS": out["T1_NO_CORPUS_ANTES_DEPOIS"]}, ensure_ascii=False))
    return 0 if not mudou and not sha_mau else 1


if __name__ == "__main__":
    raise SystemExit(main())
