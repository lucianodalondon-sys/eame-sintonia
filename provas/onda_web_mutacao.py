#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ONDA2-G3 · o ataque ao disparador: cada guarda de `onda_web.py` desligada, uma de cada vez, numa COPIA.

    py provas/onda_web_mutacao.py [--ref=HEAD]

Mesma lei de `teto_dominio_mutacao.py`: copia por `git archive`, um trecho exacto por
mutante (sem alvo, falha alto). MORTO = `tests/test_onda_web.py` deixa de passar.
"""
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ALVO = "ferramentas/big_collection/onda_web.py"
MUTANTES = [
    ("W1_REPARTIR_DEIXA_PASSAR_O_TETO", "        if resta <= 0:", "        if resta < 0:"),
    ("W2_CORRE_COORTE_PROVISORIA", '    if exigir_congelada and c.get("ESTADO") != "CONGELADA":', "    if False:"),
    ("W3_IGNORA_O_SHA256_DECLARADO", "    if sha_declarado and sha_declarado != impressao:", "    if False:"),
    ("W4_ACEITA_COORTE_MEXIDA", "    if not igual_json:", "    if False:"),
    ("W5_REAPROVEITA_LIVRO_DE_OUTRA_ONDA", ' and "--retomar" not in argv:', " and False:"),
    ("W6_DOMINIO_E_O_HOST", "o[h] = m.dominioRegistavel(h);", "o[h] = h;"),
    ("W7_FONTE_DE_DOMINIO_ESGOTADO_CORRE", '    return "TETO_DOMINIO" if ler_livro(livro).get(dominio, 0) >= TETO else None',
     "    return None"),
    ("W8_DISJUNTOR_DE_DOMINIO_DESLIGADO", "    acima = {d: v for d, v in livro_agora.items() if v > TETO}", "    acima = {}"),
]


def main():
    ref = next((a.split("=", 1)[1] for a in sys.argv[1:] if a.startswith("--ref=")), "HEAD")
    base = tempfile.mkdtemp(prefix="onda-web-mutacao-")
    out = {"REF": subprocess.run(["git", "-C", RAIZ, "rev-parse", "--short", ref], capture_output=True,
                                 text=True).stdout.strip(), "MUTANTES": []}
    tar = subprocess.run(["git", "-C", RAIZ, "archive", "--format=tar", ref], capture_output=True, check=True).stdout

    def correr(pasta):
        r = subprocess.run([sys.executable, "-m", "unittest", "tests.test_onda_web"], cwd=pasta, capture_output=True,
                           text=True, encoding="utf-8", errors="replace", timeout=600,
                           env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        m = re.search(r"Ran (\d+) test", r.stderr)
        return r.returncode, int(m.group(1)) if m else None, r.stderr[-500:]
    try:
        limpa = os.path.join(base, "limpa")
        with tarfile.open(fileobj=io.BytesIO(tar)) as t:
            t.extractall(limpa)
        cod, n, cauda = correr(limpa)
        out["SEM_MUTANTE"] = {"CODIGO": cod, "TESTES": n}
        if cod != 0:
            raise SystemExit("a copia limpa nao passa: " + cauda)
        for nome, de, para in MUTANTES:
            pasta = os.path.join(base, nome)
            shutil.copytree(limpa, pasta)
            f = os.path.join(pasta, ALVO)
            s = open(f, encoding="utf-8").read()
            if s.count(de) != 1:
                raise SystemExit("MUTANTE_SEM_ALVO %s: o trecho aparece %d vezes" % (nome, s.count(de)))
            open(f, "w", encoding="utf-8").write(s.replace(de, para))
            cod, n, cauda = correr(pasta)
            morto = cod != 0
            out["MUTANTES"].append({"MUTANTE": nome, "MORTO": morto, "CODIGO": cod, "CAUDA": None if morto else cauda})
            print(nome, "MORTO" if morto else "SOBREVIVEU", flush=True)
            shutil.rmtree(pasta, ignore_errors=True)
    finally:
        shutil.rmtree(base, ignore_errors=True)
    out["MORTOS"] = sum(1 for m in out["MUTANTES"] if m["MORTO"])
    out["TOTAL"] = len(out["MUTANTES"])
    print("ONDA_WEB_MUTACAO · mortos=%d/%d" % (out["MORTOS"], out["TOTAL"]))
    print(json.dumps(out, ensure_ascii=False, indent=1))
    return 0 if out["MORTOS"] == out["TOTAL"] else 1


if __name__ == "__main__":
    sys.exit(main())
