# -*- coding: utf-8 -*-
"""TRAVA-CONTAR · red team dos medidores numa COPIA: cada mutante afrouxa uma conferencia; os testes tem de cair.

    py scripts/trava_contar/mutar_trava_contar.py <caminho-da-copia>
"""
import json
import os
import subprocess
import sys

R = sys.argv[1]
MED = os.path.join("system-map", "scripts", "censo_das_estradas_it.py")
RES = os.path.join("ferramentas", "big_collection", "resumo_da_onda.py")
M = [
    ("aceita_run_id_que_o_livro_nao_tem", MED, "    if c is None:\n        return False, 'RUN_ID_AUSENTE_NO_LIVRO'\n",
     "    if c is None:\n        c = {'RAW_OBJECTS_CREATED': raw}\n"),
    ("nao_compara_raw_com_o_livro", MED, "    if c.get('RAW_OBJECTS_CREATED') != raw:", "    if False:"),
    ("aceita_raw_zero", MED, "    if raw < 1 or der < 1:", "    if raw < 0 or der < 0:"),
    ("aceita_unknown", MED, "    if not (isinstance(raw, int) and isinstance(der, int)) or isinstance(raw, bool) or isinstance(der, bool):\n        return False, 'RAW_OU_DERIVED_UNKNOWN'\n",
     "    if not (isinstance(raw, int) and isinstance(der, int)):\n        raw, der = 1, 1\n"),
    ("nao_confere_a_fonte", MED, "    if x.get('SOURCE_ID') not in fontes.get(x['RUN_ID'], set()):", "    if False:"),
    ("ignora_failed_do_livro", MED, "    if c.get('FAILED'):", "    if False:"),
    ("ignora_proveniencia", MED, "            or p.get('SALA_LINHAS') != p.get('SALA_COM_CADEIA_INTEIRA'):", "            or False:"),
    ("resumo_conta_pela_pasta_de_cima", MED, "        return prova        # D59: o resumo so conta CONFERIDO", "        pass        # D59: o resumo so conta CONFERIDO"),
    ("resumo_aceita_relatorio_de_outra_corrida", RES, 'if rel.get("RUN_IDS") != [f["RUN_ID"]]:', "if False:"),
    ("resumo_inventa_zero_no_lugar_de_unknown", RES, '    return v if isinstance(v, int) and not isinstance(v, bool) else UNKNOWN', '    return v if isinstance(v, int) and not isinstance(v, bool) else 0'),
]
res = {}
for nome, rel, a, b in M:
    F = os.path.join(R, rel)
    orig = open(F, encoding="utf-8", newline="").read()
    nl = chr(13) + chr(10) if chr(13) + chr(10) in orig else chr(10)
    a2, b2 = a.replace(chr(10), nl), b.replace(chr(10), nl)
    try:
        assert orig.count(a2) == 1, (nome, orig.count(a2))
        open(F, "w", encoding="utf-8", newline="").write(orig.replace(a2, b2))
        p = subprocess.run([sys.executable, "-m", "unittest", "tests.test_trava_contar"], cwd=R, capture_output=True,
                           text=True, encoding="utf-8", errors="replace", timeout=300)
        quedas = [l.strip() for l in p.stderr.splitlines() if l.startswith(("FAIL:", "ERROR:"))]
        res[nome] = {"FICHEIRO": rel.replace(os.sep, "/"), "RESULTADO": "MORTO" if quedas else "SOBREVIVEU", "QUEDAS": quedas}
        print(nome, res[nome]["RESULTADO"], len(quedas), flush=True)
    finally:
        open(F, "w", encoding="utf-8", newline="").write(orig)
out = {"DATASET": "MUTACAO-TRAVA-CONTAR-V1", "COPIA": R, "MUTANTES": res,
       "MORTOS": sum(1 for v in res.values() if v["RESULTADO"] == "MORTO"), "TOTAL": len(res)}
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "MUTACAO-TRAVA-CONTAR-V1.json"), "w",
     encoding="utf-8", newline="\n").write(json.dumps(out, ensure_ascii=False, indent=1) + "\n")
print("MORTOS", out["MORTOS"], "de", out["TOTAL"])
