#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""D38 · o ataque: cada peca do teto por dominio desligada, uma de cada vez, numa COPIA.

    py provas/teto_dominio_mutacao.py [--ref=HEAD]

A copia sai de `git archive <ref>` para uma pasta temporaria: o repositorio nao e
tocado (um ataque morto a meio no repo deixava o defeito gravado — ver o know-how).
Cada mutante troca UM trecho exacto de `coleta/italy_pilot_collect.mjs`; se o trecho
nao existir, o ataque falha alto (um mutante que nao muda nada nao prova nada).
MORTO = a prova local deu FALHAS > 0 ou saiu com codigo != 0.
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
ALVO = "coleta/italy_pilot_collect.mjs"
MUTANTES = [
    ("M1_NAO_GASTA_NO_LIVRO", "  gastarNaOnda(dominio);", "  /* M1 */;"),
    ("M2_TETO_IGNORA_O_LIVRO", "lerLivroDaOnda()[d] || 0", "0"),
    ("M3_DOMINIO_E_O_HOST", "export function dominioRegistavel(host) {\n",
     "export function dominioRegistavel(host) {\n  return siteDe(host);\n"),
    ("M4_MOTIVO_SEMPRE_TETO_POR_HOST", '"TETO_DOMINIO" : "TETO_POR_HOST"', '"TETO_POR_HOST" : "TETO_POR_HOST"'),
    ("M5_LIVRO_ILEGIVEL_VIRA_VAZIO", "    throw new Error(`TETO_ONDA_ILEGIVEL", "    return {}; throw new Error(`TETO_ONDA_ILEGIVEL"),
    ("M6_GOV_IT_NAO_E_SUFIXO", '"gov.it", "edu.it",', '"edu.it",'),
    ("M7_TETO_MAIOR_EM_VEZ_DE_MAIOR_OU_IGUAL", "return gasto >= CORTESIA.cfg.TETO_POR_HOST;",
     "return gasto > CORTESIA.cfg.TETO_POR_HOST;"),
]


def copia(ref, destino):
    tar = subprocess.run(["git", "-C", RAIZ, "archive", "--format=tar", ref], capture_output=True, check=True).stdout
    with tarfile.open(fileobj=io.BytesIO(tar)) as t:
        t.extractall(destino)


def correr(pasta):
    env = {k: v for k, v in os.environ.items()
           if k not in ("SINTONIA_PAUSA_POR_HOST_S", "SINTONIA_TETO_POR_HOST", "SINTONIA_TETO_ONDA")}
    env["NODE_DISABLE_COMPILE_CACHE"] = "1"
    r = subprocess.run(["node", "provas/teto_dominio_local.mjs"], cwd=pasta, env=env, capture_output=True,
                       text=True, encoding="utf-8", errors="replace", timeout=600)
    m = re.search(r"TETO_DOMINIO_LOCAL · passou=(\d+) FALHAS=(\d+)", r.stdout)
    return r.returncode, (int(m.group(1)), int(m.group(2))) if m else None, r.stdout[-600:] + r.stderr[-400:]


def main():
    ref = next((a.split("=", 1)[1] for a in sys.argv[1:] if a.startswith("--ref=")), "HEAD")
    base = tempfile.mkdtemp(prefix="teto-mutacao-")
    out = {"REF": subprocess.run(["git", "-C", RAIZ, "rev-parse", "--short", ref], capture_output=True,
                                 text=True).stdout.strip(), "MUTANTES": []}
    try:
        limpa = os.path.join(base, "limpa")
        copia(ref, limpa)
        cod, conta, _ = correr(limpa)
        out["SEM_MUTANTE"] = {"CODIGO": cod, "PASSOU_FALHAS": conta}
        if cod != 0 or not conta or conta[1] != 0:
            raise SystemExit("a copia limpa nao passa — o ataque nao tem base: %s" % json.dumps(out))
        for nome, de, para in MUTANTES:
            pasta = os.path.join(base, nome)
            shutil.copytree(limpa, pasta)
            f = os.path.join(pasta, ALVO)
            s = open(f, encoding="utf-8").read()
            if s.count(de) != 1:
                raise SystemExit("MUTANTE_SEM_ALVO %s: o trecho aparece %d vezes" % (nome, s.count(de)))
            open(f, "w", encoding="utf-8").write(s.replace(de, para))
            cod, conta, cauda = correr(pasta)
            morto = cod != 0 or conta is None or conta[1] > 0
            out["MUTANTES"].append({"MUTANTE": nome, "MORTO": morto, "CODIGO": cod, "PASSOU_FALHAS": conta,
                                    "CAUDA": None if morto else cauda})
            print(nome, "MORTO" if morto else "SOBREVIVEU", conta, flush=True)
            shutil.rmtree(pasta, ignore_errors=True)
    finally:
        shutil.rmtree(base, ignore_errors=True)
    out["MORTOS"] = sum(1 for m in out["MUTANTES"] if m["MORTO"])
    out["TOTAL"] = len(out["MUTANTES"])
    print("TETO_DOMINIO_MUTACAO · mortos=%d/%d" % (out["MORTOS"], out["TOTAL"]))
    print(json.dumps(out, ensure_ascii=False, indent=1))
    return 0 if out["MORTOS"] == out["TOTAL"] else 1


if __name__ == "__main__":
    sys.exit(main())
