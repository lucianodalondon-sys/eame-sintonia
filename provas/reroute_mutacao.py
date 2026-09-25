#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""REROUTE D2 · o ataque: cada peca desligada, uma de cada vez, numa COPIA (git archive).

    py provas/reroute_mutacao.py [--ref=HEAD]

MORTO = `tests/test_reroute_d2.py` deixa de passar. Um mutante sem alvo rebenta.
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
ALVO = "admissao/admissao.py"
MUTANTES = [
    ("R1_SEM_REROUTE", "    if r in (NAO, NAO_SE_APLICA):\n        ev[\"REROUTE\"]", "    if False:\n        ev[\"REROUTE\"]"),
    ("R2_TROCA_O_UNIVERSO", 'destinos.append({"UNIVERSO": u,', 'destinos.append({"UNIVERSO": origem,'),
    ("R3_DUPLICA_OS_BYTES", '"PONTUACAO": pont, "MOTIVO": motivo})',
     '"PONTUACAO": pont, "MOTIVO": motivo, "TEXTO": item.get("texto")})'),
    ("R4_NAO_SEI_TAMBEM_REENCAMINHA", "    if r in (NAO, NAO_SE_APLICA):\n        ev[\"REROUTE\"]",
     "    if r in (NAO, NAO_SE_APLICA, NAO_SEI):\n        ev[\"REROUTE\"]"),
    ("R5_A_ORIGEM_ENTRA_NOS_DESTINOS", "        if u == origem:\n            continue\n", ""),
    ("R6_DESTINO_SEM_SER_SIM", "        if r == SIM:\n            pont", "        if r != NAO:\n            pont"),
    ("R7_O_REROUTE_MUDA_O_VEREDITO", "        ev[\"REROUTE\"] = reencaminhar(item, universo)",
     "        ev[\"REROUTE\"] = reencaminhar(item, universo)\n        r = SIM if ev[\"REROUTE\"][\"DESTINOS\"] else r"),
    # D66 (dono, 25/09): so anotar; quando ligar, so T1/T2
    ("R8_D66_POUSO_LIGADO", "REROUTE_ENTRA_NA_SALA = False\nREROUTE_GAVETAS", "REROUTE_ENTRA_NA_SALA = True\nREROUTE_GAVETAS"),
    ("R9_D66_T5_PERMITIDA", 'REROUTE_GAVETAS_PERMITIDAS = frozenset({"T1", "T2"})',
     'REROUTE_GAVETAS_PERMITIDAS = frozenset({"T1", "T2", "T5"})'),
    ("R10_D66_SEM_FILTRO_DE_GAVETA", ' if d["UNIVERSO"] in REROUTE_GAVETAS_PERMITIDAS]', "]"),
]


def main():
    ref = next((a.split("=", 1)[1] for a in sys.argv[1:] if a.startswith("--ref=")), "HEAD")
    base = tempfile.mkdtemp(prefix="reroute-mutacao-")
    tar = subprocess.run(["git", "-C", RAIZ, "archive", "--format=tar", ref], capture_output=True, check=True).stdout
    out = {"REF": subprocess.run(["git", "-C", RAIZ, "rev-parse", "--short", ref], capture_output=True,
                                 text=True).stdout.strip(), "MUTANTES": []}

    def correr(p):
        r = subprocess.run([sys.executable, "-m", "unittest", "tests.test_reroute_d2"], cwd=p, capture_output=True,
                           text=True, encoding="utf-8", errors="replace", timeout=600,
                           env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        return r.returncode, r.stderr[-400:]
    try:
        limpa = os.path.join(base, "limpa")
        with tarfile.open(fileobj=io.BytesIO(tar)) as t:
            t.extractall(limpa)
        cod, cauda = correr(limpa)
        if cod != 0:
            raise SystemExit("a copia limpa nao passa: " + cauda)
        for nome, de, para in MUTANTES:
            pasta = os.path.join(base, nome)
            shutil.copytree(limpa, pasta)
            f = os.path.join(pasta, ALVO)
            s = open(f, encoding="utf-8").read()
            if s.count(de) != 1:
                raise SystemExit("MUTANTE_SEM_ALVO %s (%d)" % (nome, s.count(de)))
            open(f, "w", encoding="utf-8").write(s.replace(de, para))
            cod, cauda = correr(pasta)
            out["MUTANTES"].append({"MUTANTE": nome, "MORTO": cod != 0, "CAUDA": None if cod != 0 else cauda})
            print(nome, "MORTO" if cod != 0 else "SOBREVIVEU", flush=True)
            shutil.rmtree(pasta, ignore_errors=True)
    finally:
        shutil.rmtree(base, ignore_errors=True)
    out["MORTOS"] = sum(m["MORTO"] for m in out["MUTANTES"])
    out["TOTAL"] = len(out["MUTANTES"])
    print("REROUTE_MUTACAO · mortos=%d/%d" % (out["MORTOS"], out["TOTAL"]))
    print(json.dumps(out, ensure_ascii=False, indent=1))
    return 0 if out["MORTOS"] == out["TOTAL"] else 1


if __name__ == "__main__":
    sys.exit(main())
