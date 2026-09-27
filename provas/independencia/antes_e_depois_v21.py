"""INDEPENDENCIA-V1 — o motor de oportunidades V2.1 ANTES (base 69b0e23f) e DEPOIS, sobre o MESMO pacote real
(o ZIP versionado em build/). Nao escreve no pacote: so le, e imprime/grava a comparacao.
uso: py provas/independencia/antes_e_depois_v21.py [saida.json]"""
import json
import os
import shutil
import subprocess
import sys
import types

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, RAIZ)
sys.path.insert(0, os.path.join(RAIZ, "motor"))
sys.path.insert(0, os.path.join(RAIZ, "tests"))
from test_completude_oportunidade import _prepara_ingest, ING  # noqa: E402

BASE = "278cd489"


def carregar(nome, fonte):
    m = types.ModuleType(nome)
    m.__file__ = os.path.join(RAIZ, "motor", "v21_oportunidades.py")
    exec(compile(fonte, m.__file__, "exec"), m.__dict__)
    return m


def resumo(M):
    brutos = M.main()[0]
    regs = M.gravar(brutos, *M.main()[2:4])[0]
    return {r["ID"]: r for r in regs}


ok, limpar = _prepara_ingest()
if not ok:
    print("NAO SEI: DESIGN-INGEST indisponivel (sem ZIP)")
    sys.exit(2)
try:
    antes_src = subprocess.run(["git", "-C", RAIZ, "show", f"{BASE}:motor/v21_oportunidades.py"],
                               capture_output=True, text=True, encoding="utf-8", check=True).stdout
    A = resumo(carregar("v21_antes", antes_src))
    D = resumo(carregar("v21_depois", open(os.path.join(RAIZ, "motor", "v21_oportunidades.py"),
                                           encoding="utf-8").read()))
finally:
    if limpar:
        shutil.rmtree(os.path.dirname(ING), ignore_errors=True)

linhas = []
for oid in sorted(set(A) | set(D)):
    a, d = A.get(oid), D.get(oid)
    g = (d or {}).get("DEPENDENCY_GRAPH") or {}
    linhas.append({
        "ID": oid, "ARCHETYPE": (d or a)["ARCHETYPE"],
        "MULTI_SOURCE_ANTES": a and a["SCORE_DIMENSIONS"]["MULTI_SOURCE"],
        "MULTI_SOURCE_DEPOIS": d and d["SCORE_DIMENSIONS"]["MULTI_SOURCE"],
        "SCORE_ANTES": a and a["OPPORTUNITY_SCORE"], "SCORE_DEPOIS": d and d["OPPORTUNITY_SCORE"],
        "ESTADO_ANTES": a and a["OPPORTUNITY_STATE"], "ESTADO_DEPOIS": d and d["OPPORTUNITY_STATE"],
        "CONFIANCA_ANTES": a and a["CONFIDENCE"], "CONFIANCA_DEPOIS": d and d["CONFIDENCE"],
        "EVIDENCE_COUNT": d and d["EVIDENCE_COUNT"],
        "EXTERNAL_SIGNAL_COUNT": g.get("EXTERNAL_SIGNAL_COUNT"),
        "EVIDENCE_BASE_COUNT": g.get("EVIDENCE_BASE_COUNT"),
        "INDEPENDENT_SOURCE_COUNT": g.get("INDEPENDENT_SOURCE_COUNT"),
        "STRUCTURAL_VALIDATION_COUNT": g.get("STRUCTURAL_VALIDATION_COUNT"),
        "DOMINANT_SOURCE": g.get("DOMINANT_SOURCE"), "DOMINANT_SOURCE_SHARE_PCT": g.get("DOMINANT_SOURCE_SHARE_PCT"),
        "CONVERGENCE": g.get("CONVERGENCE"),
    })
mud = [x for x in linhas if x["MULTI_SOURCE_ANTES"] != x["MULTI_SOURCE_DEPOIS"]]
tot = {
    "BASE": BASE, "OPORTUNIDADES": len(linhas),
    "IDS_IGUAIS": sorted(A) == sorted(D),
    "MULTI_SOURCE_BAIXOU": len(mud),
    "SCORE_BAIXOU": sum(1 for x in linhas if (x["SCORE_DEPOIS"] or 0) < (x["SCORE_ANTES"] or 0)),
    "SCORE_SUBIU": sum(1 for x in linhas if (x["SCORE_DEPOIS"] or 0) > (x["SCORE_ANTES"] or 0)),
    "ESTADO_MUDOU": sum(1 for x in linhas if x["ESTADO_ANTES"] != x["ESTADO_DEPOIS"]),
    "CONFIANCA_MUDOU": sum(1 for x in linhas if x["CONFIANCA_ANTES"] != x["CONFIANCA_DEPOIS"]),
    "CONVERGENCIA": {k: sum(1 for x in linhas if x["CONVERGENCE"] == k) for k in ("CONVERGE", "NAO_CONVERGE", "NAO SEI")},
    "EVIDENCIA_DUPLICADA": sum(1 for x in linhas if (x["EXTERNAL_SIGNAL_COUNT"] or 0) > (x["EVIDENCE_BASE_COUNT"] or 0)),
}
print(json.dumps(tot, ensure_ascii=False, indent=1))
for x in mud:
    print(x["ID"], x["ARCHETYPE"], "MULTI", x["MULTI_SOURCE_ANTES"], "->", x["MULTI_SOURCE_DEPOIS"],
          "score", x["SCORE_ANTES"], "->", x["SCORE_DEPOIS"], "fontes", x["INDEPENDENT_SOURCE_COUNT"],
          "dominante", x["DOMINANT_SOURCE"], x["DOMINANT_SOURCE_SHARE_PCT"], x["CONFIANCA_ANTES"], "->", x["CONFIANCA_DEPOIS"])
if len(sys.argv) > 1:
    with open(sys.argv[1], "w", encoding="utf-8", newline="\n") as f:
        json.dump({"TOTAIS": tot, "LINHAS": linhas}, f, ensure_ascii=False, indent=1)
        f.write("\n")
