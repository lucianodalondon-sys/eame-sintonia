#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""T1B · o aperto de «pagina de site» da T2C aplicado a T1 — medido, NAO aplicado.

    py scripts/regua_t1/medir_aperto_site.py

Reutiliza a lista da T2C (`ANCORAS["T2"]["PAGINA_DE_SITE"]`) e o `_casa` da porta.
Variante A: T1 SIM com qualquer marca de pagina de site -> NAO_SEI.
Variante B: so quando a pagina de site tem o MINIMO de momentos (SINAIS_MINIMOS).
Mede no gabarito T1-V1 e nos 1.309 textos (transicoes de T1). Sem rede.
"""
import hashlib
import importlib.util as u
import json
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
MARCAS = A.ANCORAS["T2"]["PAGINA_DE_SITE"]


def variantes(texto):
    r, _m, ev = A._do_universo({"texto": texto}, "T1", A.PERGUNTAS_DO_UNIVERSO["T1"])
    if r != A.SIM:
        return r, r, r, []
    d = A._dobrar(texto)
    site = [m for m in MARCAS if A._casa(m, d)]
    a = A.NAO_SEI if site else r
    b = A.NAO_SEI if site and len(ev["palavras"]) <= A.SINAIS_MINIMOS else r
    return r, a, b, site


def main():
    g = json.load(open(AQUI / "GABARITO-T1-V1.json", encoding="utf-8"))["ITENS"]
    res = {"ATUAL": Counter(), "A_LISTA_INTEIRA": Counter(), "B_SO_NO_MINIMO": Counter()}
    afetados = []
    for i in g:
        t = Path(i["CAMINHO"]).read_text(encoding="utf-8", errors="replace")
        r, a, b, site = variantes(t)
        for k, v in (("ATUAL", r), ("A_LISTA_INTEIRA", a), ("B_SO_NO_MINIMO", b)):
            res[k]["%s->%s" % (i["T1_JANELA"], v)] += 1
        if r != a or r != b:
            afetados.append({"ID": i["ID"], "OURO": i["T1_JANELA"], "ATUAL": r, "A": a, "B": b, "MARCAS": site,
                             "INICIO": " ".join(t.split())[:90]})
    corpus, vistos = [], set()
    for d in MVA.PASTAS:
        if d.is_dir():
            for p in sorted(d.rglob("*.txt")):
                t = p.read_text(encoding="utf-8", errors="replace")
                h = hashlib.sha256(t.encode("utf-8")).hexdigest()
                if h not in vistos:
                    vistos.add(h)
                    corpus.append(t)
    trans = {"A_LISTA_INTEIRA": Counter(), "B_SO_NO_MINIMO": Counter()}
    for t in corpus:
        r, a, b, _s = variantes(t)
        trans["A_LISTA_INTEIRA"]["%s->%s" % (r, a)] += 1
        trans["B_SO_NO_MINIMO"]["%s->%s" % (r, b)] += 1

    def resumo(c):
        tp, fp, fn = c["YES->SIM"], c["NO->SIM"], c["YES->NAO_SEI"] + c["YES->NAO"]
        return {"TP": tp, "FP": fp, "FN": fn, "PRECISAO": round(tp / (tp + fp), 3), "RECALL": round(tp / (tp + fn), 3)}
    out = {"DATASET": "MEDICAO-APERTO-SITE-T1-V1", "APLICADO": False,
           "GABARITO": {k: resumo(v) for k, v in res.items()}, "AFETADOS_NO_GABARITO": afetados,
           "ACERVO_1309_T1_ATUAL_PARA_VARIANTE": {k: dict(v) for k, v in trans.items()}}
    (AQUI / "MEDICAO-APERTO-SITE-T1-V1.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + chr(10),
                                                         encoding="utf-8", newline=chr(10))
    print(json.dumps({k: out[k] for k in ("GABARITO", "ACERVO_1309_T1_ATUAL_PARA_VARIANTE")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
