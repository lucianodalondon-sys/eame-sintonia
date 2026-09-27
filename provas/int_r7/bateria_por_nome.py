"""Bateria por NOME (INT-R7-CAPS): cada modulo de tests/ num subprocesso, rede fechada.

Uso:  python3 provas/int_r7/bateria_por_nome.py <raiz_da_arvore> <saida.json>
      python3 provas/int_r7/bateria_por_nome.py --comparar <antes.json> <depois.json>

Rede fechada: HTTP(S)_PROXY aponta para uma porta morta (127.0.0.1:9) — nenhum teste
sai para fora. Saida no mesmo formato de provas/cap_win/BATERIA-*.json
(modulo -> {CORRIDOS, FALHAS, RC}), e FALHAS_ID com Classe.metodo quando legivel.
A comparacao e pelo NOME (modulo.metodo), nunca pela contagem.
"""
import json
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

LINHA = re.compile(r"^(test\w*) \(([\w.]+)\)")
FIM = re.compile(r"^(FAIL|ERROR): (\w+) \(([\w.]+)\)")
RAN = re.compile(r"^Ran (\d+) test")


def correr_modulo(raiz, mod, timeout):
    env = dict(os.environ)
    for k in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy", "ALL_PROXY"):
        env[k] = "http://127.0.0.1:9"
    env["NO_PROXY"] = ""
    try:
        p = subprocess.run([sys.executable, "-m", "unittest", "-v", f"tests.{mod}"],
                           cwd=raiz, env=env, capture_output=True, text=True, timeout=timeout)
        saida, rc = p.stderr + p.stdout, p.returncode
    except subprocess.TimeoutExpired:
        return {"CORRIDOS": "0", "FALHAS": ["<TIMEOUT>"], "FALHAS_ID": ["<TIMEOUT>"], "RC": "TIMEOUT"}
    falhas, ids, corridos = [], [], "0"
    for linha in saida.splitlines():
        m = FIM.match(linha)
        if m:
            falhas.append(m.group(2))
            ids.append(f"{m.group(3).split('.')[-1]}.{m.group(2)}")
        m = RAN.match(linha)
        if m:
            corridos = m.group(1)
    if rc != 0 and not falhas:
        falhas, ids = ["<MODULO_NAO_CARREGOU>"], ["<MODULO_NAO_CARREGOU>"]
    return {"CORRIDOS": corridos, "FALHAS": sorted(set(falhas)),
            "FALHAS_ID": sorted(set(ids)), "RC": str(rc)}


def bateria(raiz, saida, trabalhadores=1, timeout=900):
    mods = sorted(f[:-3] for f in os.listdir(os.path.join(raiz, "tests"))
                  if f.startswith("test_") and f.endswith(".py"))
    with ThreadPoolExecutor(trabalhadores) as ex:
        res = dict(zip(mods, ex.map(lambda m: correr_modulo(raiz, m, timeout), mods)))
    with open(saida, "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1, sort_keys=True)
    return res


def nomes(res):
    return {f"{m}.{n}" for m, v in res.items() for n in v["FALHAS"]}


def comparar(a, b):
    A, B = json.load(open(a)), json.load(open(b))
    na, nb = nomes(A), nomes(B)
    tot = lambda r: sum(int(v["CORRIDOS"]) for v in r.values())
    print(f"ANTES   modulos={len(A)} testes={tot(A)} falhas={len(na)}")
    print(f"DEPOIS  modulos={len(B)} testes={tot(B)} falhas={len(nb)}")
    print("NOVAS  ", len(nb - na), sorted(nb - na))
    print("SUMIDAS", len(na - nb), sorted(na - nb))
    return 1 if nb - na else 0


if __name__ == "__main__":
    if sys.argv[1] == "--comparar":
        sys.exit(comparar(sys.argv[2], sys.argv[3]))
    t = int(os.environ.get("BATERIA_TRABALHADORES", "1"))
    r = bateria(sys.argv[1], sys.argv[2], t)
    print(len(r), "modulos;", len(nomes(r)), "falhas por nome")
