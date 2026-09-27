#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LOTE7-INTEGRA · medida da REGRA DE GRAO NA PORTA: quantos SIM caem para A_CONFIRMAR.

    python3 provas/lote7_integra/medir_grao_na_porta.py [saida.json]

ANTES  = a porta de `c551062` (single-reference-gateway), lida do git — nao simulada.
DEPOIS = a porta desta arvore (motor/porta_da_referencia.py, `autorizacao_do_uso`).
HOJE   = 2026-09-27, o mesmo dia declarado em docs/intelligence/r7/CRUZAMENTOS-MAX.json.

Mede tres coisas, e so estas:
  1. os 2030 usos (AUTHORIZED-USES): o estado de cada uso nas respostas de `autorizados`, e as
     perguntas cultura x alvo cujo ESTADO muda;
  2. os 14 pares cultura x praga do PORTFOLIO da R7, perguntados a porta (antes x depois);
  3. o cruzamentos-max inteiro (86 REFEITOS + 14 PORTFOLIO) recorrido com a porta nova, contra o
     JSON commitado (feito com a porta antiga).
Nao escreve nada no repositorio, salvo o JSON pedido.
"""
import importlib.util
import json
import subprocess
import sys
import tempfile
from collections import Counter
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))
import _gavetas  # noqa: E402,F401

import porta_da_referencia as NOVA  # noqa: E402
import cruzamentos_max as XM        # noqa: E402

BASE = "c551062"
HOJE = date(2026, 9, 27)


def porta_antiga():
    src = subprocess.run(["git", "-C", str(RAIZ), "show", BASE + ":motor/porta_da_referencia.py"],
                         capture_output=True, text=True, check=True).stdout
    d = tempfile.mkdtemp()
    p = Path(d) / "porta_antiga.py"
    p.write_text(src.replace("RAIZ = Path(__file__).resolve().parents[1]", "RAIZ = Path(%r)" % str(RAIZ)),
                 encoding="utf-8")
    spec = importlib.util.spec_from_file_location("porta_antiga", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def usos(P, ref):
    out, perguntas = {}, {}
    pares = sorted({(u["CROP_ON_LABEL"], u["TARGET_ON_LABEL"]) for u in P.livro(ref, "AUTHORIZED-USES")})
    for c, a in pares:
        x = P.autorizados(ref, c, a)
        perguntas[(c, a)] = x["ESTADO"]
        for p in x["PRODUTOS"]:
            out[p["USE_ID"]] = (p["ESTADO"], p["LINK_LEVEL"])
    return out, perguntas


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    V = porta_antiga()
    rv, rn = V.abrir(hoje=HOJE), NOVA.abrir(hoje=HOJE)
    assert rv["CARIMBO"]["IMPRESSAO_DOS_LIVROS"] == rn["CARIMBO"]["IMPRESSAO_DOS_LIVROS"], "livros diferentes"
    total = len(NOVA.livro(rn, "AUTHORIZED-USES"))
    uv, qv = usos(V, rv)
    un, qn = usos(NOVA, rn)
    caem = sorted(k for k in un if uv[k][0] == NOVA.AUTORIZADO_NA_BULA_LIDA and un[k][0] == NOVA.A_CONFIRMAR)
    q_caem = sorted(k for k in qn if qv[k] == NOVA.AUTORIZADO_NA_BULA_LIDA and qn[k] == NOVA.A_CONFIRMAR)
    res = {
        "BASE_ANTES": BASE, "HOJE": HOJE.isoformat(),
        "EDICAO": rn["REGISTRO"]["EDICAO"], "ESTADO_FRESCOR": rn["REGISTRO"]["ESTADO_FRESCOR"],
        "USOS": {
            "TOTAL": total, "RESPONDIDOS": len(un),
            "POR_LINK_LEVEL": dict(Counter(v[1] for v in un.values())),
            "ANTES": dict(Counter(v[0] for v in uv.values())),
            "DEPOIS": dict(Counter(v[0] for v in un.values())),
            "SIM_QUE_CAEM_PARA_A_CONFIRMAR": len(caem),
            "OS_QUE_CAEM_SAO_TODOS_DECLARACAO": all(un[k][1] == NOVA.DECLARACAO_DE_PRODUTO for k in caem),
        },
        "PERGUNTAS_CULTURA_X_ALVO": {
            "TOTAL": len(qn), "ANTES": dict(Counter(qv.values())), "DEPOIS": dict(Counter(qn.values())),
            "SIM_QUE_CAEM_PARA_A_CONFIRMAR": len(q_caem),
            "EXEMPLOS": ["%s x %s" % k for k in q_caem[:12]],
        },
    }
    # ── R7: os 14 pares do PORTFOLIO, perguntados a porta ────────────────────
    comm = json.loads((RAIZ / "docs/intelligence/r7/CRUZAMENTOS-MAX.json").read_text(encoding="utf-8"))
    pv, pn = [], []
    for pm in comm["PORTFOLIO"]:
        b = pm["PAR_DO_BOLETIM"]
        pv.append(V.autorizados(rv, b["CULTURA"], b["PRAGA"])["ESTADO"])
        pn.append(NOVA.autorizados(rn, b["CULTURA"], b["PRAGA"])["ESTADO"])
    res["R7_PORTFOLIO_PELA_PORTA"] = {
        "PARES": len(pv), "ANTES": dict(Counter(pv)), "DEPOIS": dict(Counter(pn)),
        "SIM_QUE_CAEM_PARA_A_CONFIRMAR": sum(1 for a, b in zip(pv, pn)
                                            if a == NOVA.AUTORIZADO_NA_BULA_LIDA and b == NOVA.A_CONFIRMAR)}
    # ── R7: o cruzamentos-max inteiro, recorrido com a porta nova ────────────
    novo = XM.correr(hoje=HOJE, referencia=rn)
    ant = {r["OBJETO_ID"]: (r["DEPOIS"], str(r["FINAL"])) for r in comm["REFEITOS"]}
    dep = {r["OBJETO_ID"]: (r["DEPOIS"], str(r["FINAL"])) for r in novo["REFEITOS"]}
    sim = (XM.CONFIRMED_YES, XM.YES_A_CONFIRMAR)
    res["R7_CRUZAMENTOS_MAX"] = {
        "REFEITOS": len(dep), "DEPOIS_ANTES": dict(Counter(v[0] for v in ant.values())),
        "DEPOIS_AGORA": dict(Counter(v[0] for v in dep.values())),
        "ESTADOS_QUE_MUDARAM": sorted(k for k in dep if dep[k] != ant.get(k)),
        "SIM_ANTES": sum(1 for v in ant.values() if v[0] in sim),
        "SIM_AGORA": sum(1 for v in dep.values() if v[0] in sim),
        "PORTFOLIO_ANTES": dict(Counter(p["ESTADO"] for p in comm["PORTFOLIO"])),
        "PORTFOLIO_AGORA": dict(Counter(p["ESTADO"] for p in novo["PORTFOLIO"])),
        "NOTA": "os 86 REFEITOS perguntam SUBSTANCIA x CULTURA (sem alvo): a declaracao de produto prova a "
                "cultura e a regra de grao (cultura x alvo) nao os toca. O PORTFOLIO (cultura x praga) ja "
                "usava NIVEIS_FORTES; agora le-os da porta.",
    }
    print(json.dumps(res, ensure_ascii=False, indent=1))
    if argv:
        Path(argv[0]).write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
