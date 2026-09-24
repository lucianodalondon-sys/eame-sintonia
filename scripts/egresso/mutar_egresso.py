# -*- coding: utf-8 -*-
"""EGR · mutacao do portao de egresso, numa COPIA (worktree destacada).

    py scripts/egresso/mutar_egresso.py <caminho-da-copia>

Cada mutante estraga UMA regra de superficie/rede.py; os testes tem de o matar.
O ficheiro original e reposto no fim. PYTHONDONTWRITEBYTECODE=1 (um mutante do
mesmo tamanho engana o .pyc).
"""
import json
import os
import subprocess
import sys

R = sys.argv[1]
F = os.path.join(R, "superficie", "rede.py")
M = [
    ("maioria_vira_1_voto", "    passa = a_favor >= VOTOS_MINIMOS\n", "    passa = a_favor >= 1\n"),
    ("discordante_com_veto", "    passa = a_favor >= VOTOS_MINIMOS\n",
     "    passa = a_favor >= VOTOS_MINIMOS and contra == 0\n"),
    ("429_conta_como_voto", "    if status != 200:\n        v['PORQUE'] = 'HTTP %s%s'",
     "    if status not in (200, 429):\n        v['PORQUE'] = 'HTTP %s%s'"),
    ("minimo_de_votos_1", "VOTOS_MINIMOS = 2\n", "VOTOS_MINIMOS = 1\n"),
    ("empate_escolhe_o_primeiro", "    pais = fortes[0] if len(fortes) == 1 else EGRESSO_DESCONHECIDO\n",
     "    pais = fortes[0] if fortes else (c.most_common(1)[0][0] if c else EGRESSO_DESCONHECIDO)\n"),
    ("ipinfo_vota", "    ('ifconfig.co', 'https://ifconfig.co/json', 'country_iso', None),\n)",
     "    ('ifconfig.co', 'https://ifconfig.co/json', 'country_iso', None),\n    ('ipinfo.io', 'https://ipinfo.io/json', 'country', None),\n)"),
    ("sem_discordancia", "    return pais, discordancia\n", "    return pais, []\n"),
    ("cache_sem_validade", "    if not 0 <= idade < CACHE_SEGUNDOS:\n        return None\n", ""),
    ("cache_sem_chave_de_ambiente",
     "    if not isinstance(d, dict) or d.get('CHAVE_DO_AMBIENTE') != (chave or chave_do_ambiente()):",
     "    if not isinstance(d, dict):"),
    ("escrita_nao_atomica", "        os.replace(tmp, caminho)\n",
     "        import shutil\n        shutil.copyfile(tmp, caminho)\n"),
    ("servico_que_falhou_vota", "    if sucesso and d.get(sucesso[0]) != sucesso[1]:", "    if False:"),
]
orig = open(F, encoding="utf-8", newline="").read()
env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", HTTP_PROXY="http://127.0.0.1:9",
           HTTPS_PROXY="http://127.0.0.1:9")
res = {}
try:
    nl = chr(13) + chr(10) if chr(13) + chr(10) in orig else chr(10)
    for nome, a, b in M:
        a, b = a.replace(chr(10), nl), b.replace(chr(10), nl)
        assert orig.count(a) == 1, (nome, orig.count(a))
        open(F, "w", encoding="utf-8", newline="").write(orig.replace(a, b))
        p = subprocess.run([sys.executable, "-m", "unittest", "tests.test_egresso_consenso",
                            "tests.test_preflight_de_egresso"], cwd=R, env=env,
                           capture_output=True, text=True, timeout=600)
        fim = [l for l in p.stderr.splitlines() if l.startswith(("OK", "FAILED"))]
        # os 2 erros do yaml sao de base: um mutante so MORRE se houver FALHA nova
        falhas = [l for l in p.stderr.splitlines() if l.startswith("FAIL:")]
        res[nome] = {"RESULTADO": "MORTO" if falhas else "SOBREVIVEU", "SAIDA": fim[-1] if fim else "",
                     "TESTES_QUE_CAIRAM": [l[6:].split(" ")[0] for l in falhas]}
        print(nome, res[nome]["RESULTADO"], len(falhas), flush=True)
finally:
    open(F, "w", encoding="utf-8", newline="").write(orig)
out = {"DATASET": "MUTACAO-EGRESSO-CONSENSO-V1", "COPIA": R, "MUTANTES": res,
       "MORTOS": sum(1 for v in res.values() if v["RESULTADO"] == "MORTO"), "TOTAL": len(res)}
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "MUTACAO-EGRESSO-CONSENSO-V1.json"), "w",
     encoding="utf-8", newline="\n").write(json.dumps(out, ensure_ascii=False, indent=1) + "\n")
print("MORTOS", out["MORTOS"], "de", out["TOTAL"])
