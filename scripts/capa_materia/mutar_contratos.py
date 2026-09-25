# -*- coding: utf-8 -*-
"""CONTRATOS-AJUSTE · mutacao dos dois ajustes de contrato, numa COPIA.

    py scripts/capa_materia/mutar_contratos.py <caminho-da-copia>

Cada mutante estraga regras/italy_contracts_onboarded.json; `node regras/motor_de_rota_test.mjs` tem de cair.
O original e reposto no fim.
"""
import json
import os
import subprocess
import sys

R = sys.argv[1]
F = os.path.join(R, "regras", "italy_contracts_onboarded.json")
NOVO = r'"LINK_PATTERN": "^https?://(www\\.)?istat\\.it/(?:comunicato-stampa|notizia)/'
M = [
    # volta o padrao generico do molde (o que a 1.a onda usou)
    ("istat_padrao_antigo", NOVO + '[a-z0-9]+(?:-[a-z0-9]+)+/?$"',
     r'"LINK_PATTERN": "^https?://(www\\.)?istat\\.it/(?:[^?#]*/)?[a-z0-9]+(?:-[a-z0-9]+)+/?$"'),
    ("istat_aceita_comunicati_e_analisi", NOVO, NOVO.replace("notizia)", "notizia|comunicati-e-analisi)")),
    ("istat_perde_notizia", NOVO, NOVO.replace("|notizia)", ")")),
    ("balsamico_sem_prazo", '"TTL_SECONDS": 259200,\n    "PORQUE": "RECOLLECTION-V1 2026-09-22: 7 documentos',
     '"TTL_SECONDS": null,\n    "PORQUE": "RECOLLECTION-V1 2026-09-22: 7 documentos'),
    # o numero do coordenador lido como prazo de revisita: 28 dias
    ("balsamico_prazo_28_dias", '"TTL_SECONDS": 259200,\n    "PORQUE": "RECOLLECTION-V1 2026-09-22: 7 documentos',
     '"TTL_SECONDS": 2419200,\n    "PORQUE": "RECOLLECTION-V1 2026-09-22: 7 documentos'),
    ("balsamico_deixa_de_mudar", '"DETAIL_CONTENT": "MUTABLE",\n    "TTL_SECONDS": 259200,\n    "PORQUE": "RECOLLECTION-V1 2026-09-22: 7 documentos',
     '"DETAIL_CONTENT": "IMMUTABLE",\n    "TTL_SECONDS": 259200,\n    "PORQUE": "RECOLLECTION-V1 2026-09-22: 7 documentos'),
]
orig = open(F, encoding="utf-8", newline="").read()
nl = chr(13) + chr(10) if chr(13) + chr(10) in orig else chr(10)
res = {}
try:
    for nome, a, b in M:
        a, b = a.replace(chr(10), nl), b.replace(chr(10), nl)
        assert orig.count(a) == 1, (nome, orig.count(a))
        open(F, "w", encoding="utf-8", newline="").write(orig.replace(a, b))
        p = subprocess.run(["node", "regras/motor_de_rota_test.mjs"], cwd=R, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=300)
        quedas = [l.strip() for l in p.stdout.splitlines() if l.strip().startswith("FAIL")]
        res[nome] = {"RESULTADO": "MORTO" if quedas else "SOBREVIVEU", "QUEDAS": quedas}
        print(nome, res[nome]["RESULTADO"], len(quedas), flush=True)
finally:
    open(F, "w", encoding="utf-8", newline="").write(orig)
out = {"DATASET": "MUTACAO-CONTRATOS-AJUSTE-V1", "COPIA": R, "MUTANTES": res,
       "MORTOS": sum(1 for v in res.values() if v["RESULTADO"] == "MORTO"), "TOTAL": len(res)}
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "MUTACAO-CONTRATOS-AJUSTE-V1.json"), "w",
     encoding="utf-8", newline="\n").write(json.dumps(out, ensure_ascii=False, indent=1) + "\n")
print("MORTOS", out["MORTOS"], "de", out["TOTAL"])
