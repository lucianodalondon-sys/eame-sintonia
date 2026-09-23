"""Canario das fontes do desbloqueio G1 — a peca da M3, sem copia e sem escrever o ficheiro dela.

    py scripts/desbloqueio/canario_desbloqueio.py --contratos=<copia do livro vivo> [--escrever]

Carrega `medidas/canario_rotas_elegiveis.py` (da arvore, ou de origin/rotas-elegiveis-v1
por `git show`, executado em memoria com o __file__ da arvore) e chama `provar(sid, contrato)`
com o contrato que o PACOTE vai deixar (receita V1/V2 aplicada EM MEMORIA). MAX_ALVOS = 1:
robots + indice + 1 alvo = 3 pedidos por site. Egresso IT medido antes de cada site; BR = PARA.
Escreve scripts/desbloqueio/CANARIO-DESBLOQUEIO-V1.json (nunca o ROTAS-ELEGIVEIS-V1.json da M3).
"""
import copy
import json
import subprocess
import sys
import types
from datetime import datetime, timezone
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
SAIDA = AQUI / "CANARIO-DESBLOQUEIO-V1.json"
FONTES = ["IT-T10-026", "IT-T7-100", "IT-T10-022"]


def peca_da_m3():
    alvo = RAIZ / "medidas" / "canario_rotas_elegiveis.py"
    if alvo.exists():
        src, origem = alvo.read_text(encoding="utf-8"), "arvore"
    else:
        r = subprocess.run(["git", "show", "origin/rotas-elegiveis-v1:medidas/canario_rotas_elegiveis.py"],
                           cwd=RAIZ, capture_output=True)
        if r.returncode:
            raise SystemExit("a peca do canario da M3 nao esta disponivel")
        src, origem = r.stdout.decode("utf-8"), "origin/rotas-elegiveis-v1"
    m = types.ModuleType("canario_rotas_elegiveis")
    m.__file__ = str(alvo)
    exec(compile(src, str(alvo), "exec"), m.__dict__)
    m.MAX_ALVOS = 1
    return m, origem


def egresso():
    r = subprocess.run(["curl", "-s", "-m", "15", "https://ipinfo.io/json"], capture_output=True, text=True)
    try:
        d = json.loads(r.stdout)
        return {"PAIS": d.get("country"), "IP": d.get("ip"), "CIDADE": d.get("city")}
    except ValueError:
        return {"PAIS": "NAO SEI"}


def contrato_depois(sid, c):
    """O contrato como o PACOTE o deixa: V1/V2 por cima, em memoria."""
    c = copy.deepcopy(c)
    for nome in ("PROPOSTA-RECEITAS-V1.json", "PROPOSTA-RECEITAS-V2.json"):
        f = RAIZ / "curadoria" / nome
        if f.exists():
            for l in json.loads(f.read_text(encoding="utf-8"))["FONTES"]:
                if l["SOURCE_ID"] == sid:
                    for p in l["PROPOSTAS"]:
                        c["ACQUISITION"][p["CAMPO"].split(".", 1)[1]] = p["DEPOIS"]
    return c


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    livro = Path(next(a.split("=", 1)[1] for a in argv if a.startswith("--contratos=")))
    C = {c["SOURCE_ID"]: c for c in json.loads(livro.read_text(encoding="utf-8"))["FONTES"]}
    m, origem = peca_da_m3()
    linhas = []
    for sid in FONTES:
        eg = egresso()
        if eg.get("PAIS") != "IT":
            linhas.append({"SOURCE_ID": sid, "VEREDITO": "NAO_CORREU", "CAUSA": "egresso nao IT", "EGRESSO": eg})
            break
        c = contrato_depois(sid, C[sid])
        l = m.provar(sid, c)
        l["EGRESSO"] = eg
        l["ACQUISITION_PROVADA"] = c["ACQUISITION"]
        linhas.append(l)
        print(sid, l["VEREDITO"], l.get("PEDIDOS"), str(l.get("CAUSA"))[:120], flush=True)
    d = {"DATASET": "CANARIO-DESBLOQUEIO-V1", "GERADO_EM": datetime.now(timezone.utc).isoformat(),
         "PECA": f"medidas/canario_rotas_elegiveis.provar ({origem}), MAX_ALVOS=1",
         "CONTRATOS_LIDOS_DE": str(livro), "LINHAS": linhas}
    if "--escrever" in argv:
        SAIDA.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
