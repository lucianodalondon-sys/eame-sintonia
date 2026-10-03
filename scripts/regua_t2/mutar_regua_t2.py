# -*- coding: utf-8 -*-
"""T2-REGUA · ataque de mutacao a regua T2, numa COPIA (worktree destacada).

    py scripts/regua_t2/mutar_regua_t2.py <caminho-da-copia>

Cada mutante estraga UMA decisao medida de admissao/admissao.py; os testes tem de o
matar (FAIL novo). Para o mutante da T2C (`sem_corpo_de_boletim`) corre-se tambem a
medicao nos 1.309 textos (medir_t2c.py na copia): os 8 errados tem de voltar a SIM e
o criterio ficar vermelho. O original e reposto no fim. PYTHONDONTWRITEBYTECODE=1.
"""
import json
import os
import subprocess
import sys

R = sys.argv[1] if len(sys.argv) > 1 else r"C:\regua-t2-base"
F = os.path.join(R, "admissao", "admissao.py")
M = [
    ("transversal_off", "if outro == universo or outro in TRANSVERSAIS:", "if outro == universo:"),
    ("e_vira_ou", "if (achadas and fortes) or via_agro:", "if (achadas or fortes) or via_agro:"),
    ("agrometeo_1_condicao", "via_agro = agro and len(achadas) >= SINAIS_MINIMOS and",
     "via_agro = agro and len(achadas) >= 1 and"),
    ("palavra_inteira_off", 'PALAVRA_INTEIRA = frozenset({"T2"})', "PALAVRA_INTEIRA = frozenset()"),
    ("casa_substring",
     'if f and re.search(r"(?<![a-z0-9])" + re.escape(f) + r"(?![a-z0-9])", texto_dobrado):',
     "if f and f in texto_dobrado:"),
    ("metade_vira_nao", "            return NAO_SEI, (\n                f\"{falta}:",
     "            return NAO, (\n                f\"{falta}:"),
    ("sem_d2", '"d2": "REROUTE_POSSIVEL" if not ancoras else None}', '"d2": None}'),
    ("ancora_en_off", 'anc = (ANCORAS_EN if lingua == "en" else ANCORAS)[universo]', "anc = ANCORAS[universo]"),
    ("regua_t2_apagada", '    "T2": ["pioggia|piogge|precipitazione|precipitazioni"',
     '    "T2_X": ["pioggia|piogge|precipitazione|precipitazioni"'),
    # T2C
    ("sem_corpo_de_boletim", " and _corpo_de_boletim(texto, anc)\n", "\n"),
    ("pagina_de_site_ignorada", '    if any(_casa(m, texto_dobrado) for m in anc.get("PAGINA_DE_SITE", ())):\n        return False\n', ""),
    ("so_cultura_sem_edicao", '    return (any(re.search(r, texto_dobrado) for r in anc.get("EDICAO", ()))\n            or ',
     "    return (False\n            or "),
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
        p = subprocess.run([sys.executable, "-m", "unittest", "tests.test_regua_t2", "tests.test_a_regra_de_t2"],
                           cwd=R, env=env, capture_output=True, text=True, timeout=600)
        falhas = [l for l in p.stderr.splitlines() if l.startswith(("FAIL:", "ERROR:"))]
        res[nome] = {"RESULTADO": "MORTO" if falhas else "SOBREVIVEU", "QUEDAS": len(falhas)}
        if nome == "sem_corpo_de_boletim":
            q = subprocess.run([sys.executable, "scripts/regua_t2/medir_t2c.py"], cwd=R, env=env,
                               capture_output=True, text=True, timeout=1500)
            med = json.load(open(os.path.join(R, "scripts", "regua_t2", "MEDICAO-T2C-V1.json"), encoding="utf-8"))
            res[nome]["MEDICAO_1309"] = {"CRITERIO": med["CRITERIO"], "T2_ANTES_DEPOIS": med["T2_ANTES_DEPOIS"],
                                         "ERRADOS_DEPOIS": med["OS_8_ERRADOS_DEPOIS"], "RC": q.returncode}
            subprocess.run(["git", "-C", R, "checkout", "--", "scripts/regua_t2/MEDICAO-T2C-V1.json"])
        print(nome, res[nome]["RESULTADO"], res[nome]["QUEDAS"], flush=True)
finally:
    open(F, "w", encoding="utf-8", newline="").write(orig)
out = {"DATASET": "MUTACAO-REGUA-T2-V3", "COPIA": R, "MUTANTES": res,
       "MORTOS": sum(1 for v in res.values() if v["RESULTADO"] == "MORTO"), "TOTAL": len(res)}
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "MUTACAO-REGUA-T2-V3.json"), "w",
     encoding="utf-8", newline="\n").write(json.dumps(out, ensure_ascii=False, indent=1) + "\n")
print("MORTOS", out["MORTOS"], "de", out["TOTAL"])
