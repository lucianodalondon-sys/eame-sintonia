# -*- coding: utf-8 -*-
"""ORDENS-63 v2 · mutacao da D52 numa COPIA: cada mutante estraga uma trava; os testes tem de cair.

    py scripts/ordens_63/mutar_d52.py <caminho-da-copia>

O original de cada ficheiro e reposto no fim, mesmo se um mutante rebentar.
"""
import json
import os
import subprocess
import sys

R = sys.argv[1]
C = os.path.join(R, "curadoria")
M = [
    ("gatilho_sem_trava", "gatilho_discovery.py", "        if RPD.retirada(c):\n            continue\n", ""),
    ("alimentar_revalida_retiradas", "alimentar_fila.py",
     "and sid in contratos and sid not in retiradas:", "and sid in contratos:"),
    ("alimentar_repara_retiradas", "alimentar_fila.py",
     "(LC.DEGRADED, LC.REPAIRING) and sid not in retiradas:", "(LC.DEGRADED, LC.REPAIRING):"),
    ("pisa_outra_marca", "retirar_por_decisao.py", 'if c.get("ESTADO_CATALOGO") or c.get("CATALOGO_D9"):', "if False:"),
    ("reverte_marca_alheia", "retirar_por_decisao.py",
     'if (c.get("CATALOGO_D9") or {}).get("DECISAO") != dec["DECISAO"]:', "if False:"),
    ("invariante_cego", "retirar_por_decisao.py", 'if a["SOURCE_ID"] not in mudadas:', "if False:"),
    ("reverte_para_lf", "retirar_por_decisao.py", 'newline=quebra) as f:', 'newline="\\n") as f:'),
    ("marca_com_outro_nome", "retirar_por_decisao.py", 'c["ESTADO_CATALOGO"] = RETIRADA', 'c["ESTADO_CATALOGO"] = "RETIRADA"'),
]
res = {}
for nome, fich, a, b in M:
    F = os.path.join(C, fich)
    orig = open(F, encoding="utf-8", newline="").read()
    nl = chr(13) + chr(10) if chr(13) + chr(10) in orig else chr(10)
    a2, b2 = a.replace(chr(10), nl), b.replace(chr(10), nl)
    try:
        assert orig.count(a2) == 1, (nome, orig.count(a2))
        open(F, "w", encoding="utf-8", newline="").write(orig.replace(a2, b2))
        p = subprocess.run([sys.executable, "-m", "unittest", "test_retirar_por_decisao"], cwd=C,
                           capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300)
        quedas = [l.strip() for l in p.stderr.splitlines() if l.startswith(("FAIL:", "ERROR:"))]
        res[nome] = {"FICHEIRO": fich, "RESULTADO": "MORTO" if p.returncode != 0 else "SOBREVIVEU", "QUEDAS": quedas}
        print(nome, res[nome]["RESULTADO"], len(quedas), flush=True)
    finally:
        open(F, "w", encoding="utf-8", newline="").write(orig)
out = {"DATASET": "MUTACAO-D52-V1", "COPIA": R, "MUTANTES": res,
       "MORTOS": sum(1 for v in res.values() if v["RESULTADO"] == "MORTO"), "TOTAL": len(res)}
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "MUTACAO-D52-V1.json"), "w",
     encoding="utf-8", newline="\n").write(json.dumps(out, ensure_ascii=False, indent=1) + "\n")
print("MORTOS", out["MORTOS"], "de", out["TOTAL"])
