# -*- coding: utf-8 -*-
"""ALVOS-NOVOS-2 · mutacao do filtro de pagina de LISTA, numa COPIA.

    py scripts/capa_materia/mutar_lista.py <caminho-da-copia>

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
    ("filtro_desligado", "    if (ePaginaDeLista(url)) { listas++; continue; }\n", "\n"),
    # o aperto que o coordenador descreveu ao pe da letra: qualquer coisa que termine em ano
    ("qualquer_fim_em_ano", "^(?:${PALAVRA_DE_LISTA}-)*(?:19|20)", "^(?:.*-)?(?:19|20)"),
    ("ano_sozinho_nao_recusa", "^(?:${PALAVRA_DE_LISTA}-)*(?:19|20)", "^(?:${PALAVRA_DE_LISTA}-)+(?:19|20)"),
    ("paginacao_desligada", "if (/^(?:page|pagina|pag)$/i.test(antes) && /^\\d+$/.test(ultimo)) return true;", ""),
    ("etiqueta_desligada", "  if (DENTRO_DE_LISTA.test(antes)) return true;\n", "\n"),
    ("arquivo_desligado", "return SO_LISTA.test(ultimo) || LISTA_COM_ANO.test(ultimo);", "return LISTA_COM_ANO.test(ultimo);"),
    ("lista_perguntada_ao_livro_antes", "    if (ePaginaDeLista(url)) { listas++; continue; }\n    const classe = classificar(url);",
     "    const classe = classificar(url);\n    if (ePaginaDeLista(url)) { listas++; continue; }"),
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
out = {"DATASET": "MUTACAO-FILTRO-LISTA-V1", "COPIA": R, "MUTANTES": res,
       "MORTOS": sum(1 for v in res.values() if v["RESULTADO"] == "MORTO"), "TOTAL": len(res)}
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "MUTACAO-FILTRO-LISTA-V1.json"), "w",
     encoding="utf-8", newline="\n").write(json.dumps(out, ensure_ascii=False, indent=1) + "\n")
print("MORTOS", out["MORTOS"], "de", out["TOTAL"])
