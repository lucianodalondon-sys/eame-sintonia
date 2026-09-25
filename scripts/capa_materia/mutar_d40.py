# -*- coding: utf-8 -*-
"""ALVOS-NOVOS · mutacao da escolha D40, numa COPIA.

    py scripts/capa_materia/mutar_d40.py <caminho-da-copia>

Cada mutante estraga regras/motor_de_rota.mjs; `node regras/motor_de_rota_test.mjs` tem de cair.
O original e reposto no fim.
"""
import json
import os
import subprocess
import sys

R = sys.argv[1]
F = os.path.join(R, "regras", "motor_de_rota.mjs")
M = [
    # o defeito da 1.a onda: corta primeiro, pergunta ao livro depois
    ("corta_antes_de_perguntar_ao_livro", "  for (const url of urls) {\n    const classe = classificar(url);",
     "  for (const url of urls.slice(0, ALVOS_POR_FONTE_D40)) {\n    const classe = classificar(url);"),
    ("conhecido_continua_na_lista", 'if (classe === "CONHECIDO") conhecidos++;',
     'if (classe === "CONHECIDO") { conhecidos++; novos.push(url); }'),
    ("teto_4", "export const ALVOS_POR_FONTE_D40 = 3;", "export const ALVOS_POR_FONTE_D40 = 4;"),
    ("teto_1", "export const ALVOS_POR_FONTE_D40 = 3;", "export const ALVOS_POR_FONTE_D40 = 1;"),
    ("ordem_do_indice_invertida", "[...novos, ...revisitas].slice", "[...novos.reverse(), ...revisitas].slice"),
    ("revisita_antes_do_novo", "[...novos, ...revisitas].slice", "[...revisitas, ...novos].slice"),
    ("inventa_alvo_quando_vazio", "[...novos, ...revisitas].slice",
     "(novos.length + revisitas.length ? [...novos, ...revisitas] : urls).slice"),
    ("match_url_ignora_o_livro",
     "return escolherAlvosD40(urls, classificar, (url) => nomeDoAlvo(",
     "return escolherAlvosD40(urls, () => \"NOVO\", (url) => nomeDoAlvo("),
    ("match_html_ignora_o_livro",
     'return escolherAlvosD40(urls, classificar, (url) => url.split("/").pop());',
     'return escolherAlvosD40(urls, () => "NOVO", (url) => url.split("/").pop());'),
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
out = {"DATASET": "MUTACAO-D40-V1", "COPIA": R, "MUTANTES": res,
       "MORTOS": sum(1 for v in res.values() if v["RESULTADO"] == "MORTO"), "TOTAL": len(res)}
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "MUTACAO-D40-V1.json"), "w",
     encoding="utf-8", newline="\n").write(json.dumps(out, ensure_ascii=False, indent=1) + "\n")
print("MORTOS", out["MORTOS"], "de", out["TOTAL"])
