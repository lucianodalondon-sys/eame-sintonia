# -*- coding: utf-8 -*-
"""RECEITAS-182 · mutacao do reparo (titulos longos), numa COPIA.

    py scripts/capa_materia/mutar_titulos_longos.py <caminho-da-copia>

Cada mutante estraga curadoria/reparar_contrato.py; os testes do reparo tem de cair.
O original e reposto no fim.
"""
import json
import os
import subprocess
import sys

R = sys.argv[1]
F = os.path.join(R, "curadoria", "reparar_contrato.py")
M = [
    ("sem_versao_estrita", "            if estrito:\n", "            if False:\n"),
    ("contorna_qualquer_recusa", "if recusa.startswith(RECUSAS_POR_NAVEGACAO) else None", "if True else None"),
    ("aceita_titulos_curtos", "% (FLUXO_PALAVRAS - 1))", "% 1)"),
    ("sem_filtro_institucional", "return (padrao[:-len(fim)] + _NAO_E_TITULO", "return (padrao[:-len(fim)]"),
]
orig = open(F, encoding="utf-8", newline="").read()
nl = chr(13) + chr(10) if chr(13) + chr(10) in orig else chr(10)
res = {}
try:
    for nome, a, b in M:
        a, b = a.replace(chr(10), nl), b.replace(chr(10), nl)
        assert orig.count(a) == 1, (nome, orig.count(a))
        open(F, "w", encoding="utf-8", newline="").write(orig.replace(a, b))
        p = subprocess.run([sys.executable, "-m", "unittest", "test_reparo_titulos_longos", "test_reparar_contrato"],
                           cwd=os.path.join(R, "curadoria"), capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=300)
        quedas = [l.strip() for l in p.stderr.splitlines() if l.startswith(("FAIL:", "ERROR:"))]
        res[nome] = {"RESULTADO": "MORTO" if p.returncode != 0 else "SOBREVIVEU", "QUEDAS": quedas}
        print(nome, res[nome]["RESULTADO"], len(quedas), flush=True)
finally:
    open(F, "w", encoding="utf-8", newline="").write(orig)
out = {"DATASET": "MUTACAO-TITULOS-LONGOS-V1", "COPIA": R, "MUTANTES": res,
       "MORTOS": sum(1 for v in res.values() if v["RESULTADO"] == "MORTO"), "TOTAL": len(res)}
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "MUTACAO-TITULOS-LONGOS-V1.json"), "w",
     encoding="utf-8", newline="\n").write(json.dumps(out, ensure_ascii=False, indent=1) + "\n")
print("MORTOS", out["MORTOS"], "de", out["TOTAL"])
