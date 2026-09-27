# -*- coding: utf-8 -*-
"""C9-IDIOMA · mutacao numa COPIA: cada mutante estraga o detector ou a leitura do estado; os testes tem de cair.

    py scripts/micro_coleta/mutar_c9.py <caminho-da-copia>
"""
import json
import os
import subprocess
import sys

R = sys.argv[1]
F = os.path.join(R, "scripts", "micro_coleta", "micro_coleta.py")
M = [
    ("banda_curta_desligada", "if conta[lg] >= IDIOMA_MINIMO_CURTO and conta[lg] >= IDIOMA_DOMINIO * segunda:", "if False:"),
    ("sem_exigir_dominio", " and conta[lg] >= IDIOMA_DOMINIO * segunda:", ":"),
    ("minimo_curto_4", "IDIOMA_MINIMO_CURTO = 8", "IDIOMA_MINIMO_CURTO = 4"),
    ("cli_ignora_o_estado", "r = relatorio(ids, corridas=corridas, saida=saida)", "r = relatorio(ids, saida=saida)"),
    ("inventa_egresso_it", '"EGRESSO_DEPOIS": {"PAIS": eg[1] if len(eg) > 1 else None}', '"EGRESSO_DEPOIS": {"PAIS": "IT"}'),
    ("fonte_que_nao_correu_entra", 'if not f.get("RUN_ID") or (ids is not None', 'if (ids is not None'),
    ("gate_fixo", '"GATE_NO_INSTANTE": f.get("GATE")', '"GATE_NO_INSTANTE": "ELIGIBLE"'),
]
orig = open(F, encoding="utf-8", newline="").read()
res = {}
try:
    for nome, a, b in M:
        assert orig.count(a) == 1, (nome, orig.count(a))
        open(F, "w", encoding="utf-8", newline="").write(orig.replace(a, b))
        p = subprocess.run([sys.executable, "-m", "unittest", "tests.test_c9_idioma"], cwd=R, capture_output=True,
                           text=True, encoding="utf-8", errors="replace", timeout=300)
        quedas = [l.strip() for l in p.stderr.splitlines() if l.startswith(("FAIL:", "ERROR:"))]
        res[nome] = {"RESULTADO": "MORTO" if quedas else "SOBREVIVEU", "QUEDAS": quedas}
        print(nome, res[nome]["RESULTADO"], len(quedas), flush=True)
finally:
    open(F, "w", encoding="utf-8", newline="").write(orig)
out = {"DATASET": "MUTACAO-C9-IDIOMA-V1", "COPIA": R, "MUTANTES": res,
       "MORTOS": sum(1 for v in res.values() if v["RESULTADO"] == "MORTO"), "TOTAL": len(res)}
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "MUTACAO-C9-IDIOMA-V1.json"), "w",
     encoding="utf-8", newline="\n").write(json.dumps(out, ensure_ascii=False, indent=1) + "\n")
print("MORTOS", out["MORTOS"], "de", out["TOTAL"])
