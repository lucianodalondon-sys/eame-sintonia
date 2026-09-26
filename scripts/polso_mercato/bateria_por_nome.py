#!/usr/bin/env python3
"""POLSO-DI-MERCATO · a bateria POR NOME, antes e depois do extrator de preco (leis/preco_de_mercado.py).

    py scripts/polso_mercato/bateria_por_nome.py <raiz da arvore> <saida.json>
    py scripts/polso_mercato/bateria_por_nome.py <raiz> <saida.json> --parte leve|mapa
    py scripts/polso_mercato/bateria_por_nome.py --comparar antes.json depois.json

`--parte leve` corre so os modulos de tests/ (leve: roda fora da LOCK-PESADO); `--parte mapa` so os testes do
System Map (um deles corre a cadeia num clone: pesado, so com a LOCK-PESADO). Sem --parte, os dois.

Mesma forma de `scripts/lugar_fato/bateria_por_nome.py` (D70), com outra lista: os testes das leis de
tempo/lugar do facto que o extrator de preco toca de perto (le o mesmo italiano), o do proprio extrator,
e os testes do System Map (o mapa e regerado no fim). Rede fechada (proxy para uma porta morta).
Um modulo ausente fica «AUSENTE»; nao e falha nem verde.
"""
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

MODULOS = (
    "tests.test_preco_de_mercado", "tests.test_fato_do_texto", "tests.test_lugar_do_fato",
    "tests.test_artefato_tempo_do_fato", "tests.test_admissao_multilingue",
    "tests.test_social_bruto_leva_a_evidencia",
)
DESCOBRIR = ("system-map/tests",)
RX = re.compile(r"^(test\w+) \(([\w.]+)\)(?:\s*\n?.*?)? \.\.\. (ok|FAIL|ERROR|skipped.*|expected failure|unexpected success)$",
                re.M)


def ambiente():
    e = dict(os.environ)
    for k in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy", "ALL_PROXY"):
        e[k] = "http://127.0.0.1:9"
    e["NO_PROXY"] = e["no_proxy"] = ""
    e["PYTHONIOENCODING"] = "utf-8"
    return e


def _ler(res, brutos, rotulo, p):
    brutos[rotulo] = hashlib.sha256(p.stderr.encode("utf-8")).hexdigest()
    achados = RX.findall(p.stderr)
    for nome, classe, veredito in achados:
        res["%s::%s" % (classe, nome)] = "SKIP" if veredito.startswith("skipped") else veredito.upper()
    if not achados:
        res["%s::(modulo)" % rotulo] = "SEM_TESTES_LIDOS rc=%d" % p.returncode


def correr(raiz, parte=None):
    raiz = Path(raiz)
    res, brutos = {}, {}
    for m in (MODULOS if parte in (None, "leve") else ()):
        if not (raiz / (m.replace(".", "/") + ".py")).exists():
            res["%s::(modulo)" % m] = "AUSENTE"
            continue
        p = subprocess.run([sys.executable, "-m", "unittest", "-v", m], cwd=raiz, env=ambiente(),
                           capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=1800)
        _ler(res, brutos, m, p)
    for d in (DESCOBRIR if parte in (None, "mapa") else ()):
        p = subprocess.run([sys.executable, "-m", "unittest", "discover", "-v", "-s", d, "-p", "test_*.py", "-t", d],
                           cwd=raiz, env=ambiente(), capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=3600)
        _ler(res, brutos, d, p)
    return res, brutos


def main():
    if sys.argv[1] == "--comparar":
        a = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))["TESTES"]
        d = json.loads(Path(sys.argv[3]).read_text(encoding="utf-8"))["TESTES"]
        mau = lambda v: v not in ("OK", "SKIP", "AUSENTE")
        novas = sorted(k for k in d if mau(d[k]) and not mau(a.get(k, "OK")))
        curadas = sorted(k for k in a if mau(a[k]) and not mau(d.get(k, "AUSENTE")))
        print(json.dumps({"NEW_FAILURES_BY_NAME": novas, "CURADAS": curadas,
                          "SO_ANTES": sorted(set(a) - set(d)), "SO_DEPOIS": len(set(d) - set(a)),
                          "VERMELHOS_ANTES": sorted(k for k in a if mau(a[k])),
                          "VERMELHOS_DEPOIS": sorted(k for k in d if mau(d[k])),
                          "TESTES_ANTES": len(a), "TESTES_DEPOIS": len(d)}, ensure_ascii=False, indent=1))
        return
    parte = sys.argv[sys.argv.index("--parte") + 1] if "--parte" in sys.argv else None
    res, brutos = correr(sys.argv[1], parte)
    out = {"DATASET": "BATERIA-POLSO-MERCATO-POR-NOME-V1", "TESTES": dict(sorted(res.items())),
           "SHA256_DA_SAIDA_BRUTA": brutos}
    Path(sys.argv[2]).write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    mau = sum(v not in ("OK", "SKIP", "AUSENTE") for v in res.values())
    print("%d testes, %d nao-verdes -> %s" % (len(res), mau, sys.argv[2]))


if __name__ == "__main__":
    main()
