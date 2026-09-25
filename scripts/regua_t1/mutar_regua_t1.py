# -*- coding: utf-8 -*-
"""T1-JANELA · mutacao da regua T1 numa COPIA (worktree destacada).

    py scripts/regua_t1/mutar_regua_t1.py <caminho-da-copia>

Cada mutante estraga UMA decisao medida; os testes (test_regua_t1) tem de o matar.
Para `um_so_momento` corre-se tambem a medicao no gabarito: os falsos SIM tem de voltar.
PYTHONDONTWRITEBYTECODE=1; o original e reposto no fim.
"""
import json
import os
import subprocess
import sys

R = sys.argv[1]
F = os.path.join(R, "admissao", "admissao.py")
M = [
    ("um_so_momento", "        if tem_cultura and len(achadas) >= SINAIS_MINIMOS:\n",
     "        if tem_cultura and len(achadas) >= 1:\n"),
    ("cultura_dispensada", "        if tem_cultura and len(achadas) >= SINAIS_MINIMOS:\n",
     "        if len(achadas) >= SINAIS_MINIMOS:\n"),
    ("metade_vira_nao", "            return NAO_SEI, (\n                f\"{falta}: «{universo}» (D29) pede uma cultura",
     "            return NAO, (\n                f\"{falta}: «{universo}» (D29) pede uma cultura"),
    ("t1_nao_transversal", 'TRANSVERSAIS = frozenset({"T2", "T1"})', 'TRANSVERSAIS = frozenset({"T2"})'),
    ("t1_substring", 'PALAVRA_INTEIRA = frozenset({"T2", "T1"})', 'PALAVRA_INTEIRA = frozenset({"T2"})'),
    ("raccolta_solta", '"inizio della raccolta|avvio della raccolta|', '"raccolta|inizio della raccolta|avvio della raccolta|'),
    ("pero_e_pera", '"|pere|pesco|', '"|pere|pero|pesco|'),
    ("densidade_desligada", "DENSIDADE_MINIMA_DE_MOMENTO = 2.0 ", "DENSIDADE_MINIMA_DE_MOMENTO = 0.0 "),
    ("regua_t1_apagada", '    "T1": ["fenologia|fenologica|fenologico|fenologiche|fenologici|bbch|estadio fenologico",',
     '    "T1_X": ["fenologia|fenologica|fenologico|fenologiche|fenologici|bbch|estadio fenologico",'),
]
orig = open(F, encoding="utf-8", newline="").read()
nl = chr(13) + chr(10) if chr(13) + chr(10) in orig else chr(10)
env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", HTTP_PROXY="http://127.0.0.1:9",
           HTTPS_PROXY="http://127.0.0.1:9")
res = {}
try:
    for nome, a, b in M:
        a, b = a.replace(chr(10), nl), b.replace(chr(10), nl)
        assert orig.count(a) == 1, (nome, orig.count(a))
        open(F, "w", encoding="utf-8", newline="").write(orig.replace(a, b))
        p = subprocess.run([sys.executable, "-m", "unittest", "tests.test_regua_t1"], cwd=R, env=env,
                           capture_output=True, text=True, timeout=600)
        quedas = [l for l in p.stderr.splitlines() if l.startswith(("FAIL:", "ERROR:"))]
        res[nome] = {"RESULTADO": "MORTO" if quedas else "SOBREVIVEU", "QUEDAS": len(quedas)}
        print(nome, res[nome]["RESULTADO"], len(quedas), flush=True)
finally:
    open(F, "w", encoding="utf-8", newline="").write(orig)
out = {"DATASET": "MUTACAO-REGUA-T1-V1", "COPIA": R, "MUTANTES": res,
       "MORTOS": sum(1 for v in res.values() if v["RESULTADO"] == "MORTO"), "TOTAL": len(res)}
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "MUTACAO-REGUA-T1-V1.json"), "w",
     encoding="utf-8", newline="\n").write(json.dumps(out, ensure_ascii=False, indent=1) + "\n")
print("MORTOS", out["MORTOS"], "de", out["TOTAL"])
