#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""JANELAS-68 · passo 2: que ramo JA resolve cada uma das 68, pelo que esses ramos mediram e guardaram.

Sem rede. Le por `git show` os resultados gravados nos ramos:
  janela-formas-v1  provas/janela_formas/CANARIO-RECEITA-PDF-tentativa2.json, CONTRATOS-RECEITA-PDF.json,
                    CANARIO-PAGINA-BOLETIM.json
  t2-boletins-v1    provas/janela_formas/cjs/INDICE.json, provas/t2_boletins/* (ARPAE, Umbria)
  receitas-182-v1   scripts/receitas_182/CLASSIFICACAO-182-V1.json, MEDICAO-COM-REDE-V1.json
e cruza com curadoria/JANELAS-68-FORMAS-V1.json (passo 1).
"""
from __future__ import annotations

import json
import subprocess
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
FORMAS = RAIZ / "curadoria" / "JANELAS-68-FORMAS-V1.json"
SAIDA = RAIZ / "curadoria" / "JANELAS-68-CRUZAMENTO-V1.json"
JF, T2B, R182 = "origin/janela-formas-v1", "t2-boletins-v1", "origin/receitas-182-v1"


def g(ref, p):
    try:
        return json.loads(subprocess.run(["git", "show", "%s:%s" % (ref, p)], cwd=str(RAIZ), capture_output=True,
                                         text=True, encoding="utf-8", check=True).stdout)
    except Exception:
        return None


def _lista(x):
    return x if isinstance(x, list) else list((x or {}).values())


def cruzar() -> dict:
    minhas = json.loads(FORMAS.read_text(encoding="utf-8"))["FONTES"]
    r182 = {f["SOURCE_ID"]: f for f in _lista((g(R182, "scripts/receitas_182/CLASSIFICACAO-182-V1.json") or {}).get("FONTES"))}
    med = {f["SOURCE_ID"]: f for f in _lista((g(R182, "scripts/receitas_182/MEDICAO-COM-REDE-V1.json") or {}).get("FONTES"))}
    pdf_can = {f["SOURCE_ID"]: f for f in _lista((g(JF, "provas/janela_formas/CANARIO-RECEITA-PDF-tentativa2.json") or {}).get("FONTES"))}
    pdf_ctr = g(JF, "provas/janela_formas/CONTRATOS-RECEITA-PDF.json") or {}
    pb = g(JF, "provas/janela_formas/CANARIO-PAGINA-BOLETIM.json") or {}
    pb_formas = pb.get("FORMAS_LIDAS") or {}
    cjs = json.dumps(g(T2B, "provas/janela_formas/cjs/INDICE.json") or {}, ensure_ascii=False)
    linhas = []
    for m in minhas:
        sid = m["SOURCE_ID"]
        v = []
        if sid in pdf_can:
            cn = pdf_can[sid].get("CANARIO") or {}
            v.append(("janela-formas-v1", "RECEITA_PDF", "PASS" if cn.get("PASS") else "FAIL",
                      "canario real: %s" % (cn.get("PORQUE") or "DETAIL %s" % cn.get("DETAIL_ENUMERATED"))))
        elif sid in pdf_ctr:
            v.append(("janela-formas-v1", "RECEITA_PDF", "CONTRATO_SEM_CANARIO", "contrato PDF escrito, sem canario"))
        if sid in pb_formas:
            f = pb_formas[sid]
            passa = f.get("FORMA") == "PAGINA_E_BOLETIM" and sid in json.dumps(pb.get("LAMMA") or {})
            v.append(("janela-formas-v1", "PAGINA_E_BOLETIM", "PASS" if passa else "NAO_E_ESTA_FORMA",
                      "%s: %s" % (f.get("FORMA"), (f.get("PORQUE") or "")[:90])))
        if sid in cjs:
            v.append(("t2-boletins-v1", "JS_API", "SO_ESTUDO", "estudo C-JS/D46: saida publica procurada, contrato so proposto"))
        if sid in med:
            d = med[sid]
            v.append(("receitas-182-v1", "REPARO_FAMILIA", "PASS" if d.get("DESFECHO") == "PADRAO_NOVO" and (d.get("CANARIO") or {}).get("PASS") else "FAIL",
                      "%s %s" % (d.get("DESFECHO"), (d.get("MOTIVO") or d.get("PORQUE") or "")[:80])))
        rf = r182.get(sid, {})
        resolve = [x for x in v if x[2] == "PASS"]
        linhas.append({"SOURCE_ID": sid, "NOME": m["NOME"], "URL": m["URL"], "MINHA_FORMA": m["FORMA"],
                       "FORMA_R182": rf.get("FORMA"), "REGRA_R182": rf.get("REGRA"),
                       "VEREDITOS": [dict(zip(("RAMO", "ROTA", "RESULTADO", "PORQUE"), x)) for x in v],
                       "RESOLVIDA_POR": sorted({x[0] for x in resolve}) or None})
    out = {"DATASET": "JANELAS-68-CRUZAMENTO-V1",
           "RAMOS": {r: subprocess.run(["git", "rev-parse", "--short", r], cwd=str(RAIZ), capture_output=True,
                                       text=True).stdout.strip() for r in (JF, T2B, R182)},
           "N": len(linhas),
           "RESOLVIDAS_POR_RAMO": dict(Counter(r for l in linhas for r in (l["RESOLVIDA_POR"] or []))),
           "SEM_RAMO": sum(1 for l in linhas if not l["RESOLVIDA_POR"]),
           "TOCADAS_POR_ALGUM_RAMO": sum(1 for l in linhas if l["VEREDITOS"]),
           "CONCORDANCIA_DE_FORMA": dict(Counter("%s | %s" % (l["MINHA_FORMA"], l["FORMA_R182"]) for l in linhas).most_common()),
           "FONTES": linhas}
    SAIDA.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    return out


if __name__ == "__main__":
    r = cruzar()
    for k in ("RAMOS", "N", "RESOLVIDAS_POR_RAMO", "SEM_RAMO", "TOCADAS_POR_ALGUM_RAMO"):
        print(k, r[k])
    for l in r["FONTES"]:
        if l["VEREDITOS"]:
            print(l["SOURCE_ID"], l["MINHA_FORMA"], "|", "; ".join("%s %s %s" % (v["RAMO"][:14], v["ROTA"], v["RESULTADO"]) for v in l["VEREDITOS"]))
    print("CONCORDANCIA (minha, receitas-182):")
    for k, n in r["CONCORDANCIA_DE_FORMA"].items():
        print("  ", n, k)
