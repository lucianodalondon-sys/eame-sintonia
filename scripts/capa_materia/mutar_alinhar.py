# -*- coding: utf-8 -*-
"""D44 · mutacao de curadoria/alinhar_com_o_coletor.py, numa COPIA.

    py scripts/capa_materia/mutar_alinhar.py <caminho-da-copia>

Cada mutante estraga o script; `py -m unittest test_alinhar_com_o_coletor` (em curadoria/) tem de
cair. O original e reposto no fim.
"""
import json
import os
import subprocess
import sys

R = sys.argv[1]
F = os.path.join(R, "curadoria", "alinhar_com_o_coletor.py")
M = [
    ("alinha_qualquer_fonte", "        if sid not in D[\"FONTES\"]:\n            continue\n", "\n"),
    ("sem_ja_alinhada", "            acoes.append(dict(a, ACAO=\"JA_ALINHADA\"))\n            continue\n", "            pass\n"),
    ("invariante_cego", "        if a != b and a[\"SOURCE_ID\"] not in mudadas:", "        if False:"),
    ("escreve_sem_ordem", "    if a.escrever and any(", "    if True and any("),
    ("decisao_errada_no_livro", "quando=quando, decisao=decisao,", "quando=quando, decisao=\"R1\","),
]
orig = open(F, encoding="utf-8", newline="").read()
nl = chr(13) + chr(10) if chr(13) + chr(10) in orig else chr(10)
res = {}
try:
    for nome, a, b in M:
        a, b = a.replace(chr(10), nl), b.replace(chr(10), nl)
        assert orig.count(a) == 1, (nome, orig.count(a))
        open(F, "w", encoding="utf-8", newline="").write(orig.replace(a, b))
        p = subprocess.run([sys.executable, "-m", "unittest", "test_alinhar_com_o_coletor"],
                           cwd=os.path.join(R, "curadoria"), capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=300)
        quedas = [l.strip() for l in p.stderr.splitlines() if l.startswith(("FAIL:", "ERROR:"))]
        res[nome] = {"RESULTADO": "MORTO" if p.returncode != 0 else "SOBREVIVEU", "QUEDAS": quedas}
        print(nome, res[nome]["RESULTADO"], len(quedas), flush=True)
finally:
    open(F, "w", encoding="utf-8", newline="").write(orig)
out = {"DATASET": "MUTACAO-ALINHAR-D44-V1", "COPIA": R, "MUTANTES": res,
       "MORTOS": sum(1 for v in res.values() if v["RESULTADO"] == "MORTO"), "TOTAL": len(res)}
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "MUTACAO-ALINHAR-D44-V1.json"), "w",
     encoding="utf-8", newline="\n").write(json.dumps(out, ensure_ascii=False, indent=1) + "\n")
print("MORTOS", out["MORTOS"], "de", out["TOTAL"])
