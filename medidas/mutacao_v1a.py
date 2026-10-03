#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V1A — PYTHON MUTATION LAW: cada mutante tem de fazer a suite da V1A reprovar.

Aplica um mutante de cada vez, corre `tests.test_v1a_v1_ligada` sem bytecode
(PYTHONDONTWRITEBYTECODE, -B: um mutante do mesmo tamanho engana o .pyc) e
RESTAURA o ficheiro no `finally`, byte a byte. Sem rede.
"""
import os
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
MUTANTES = [
    ("V1 desligada (Python)", "curadoria/retrato_html.py", "V1_LIGADA = True", "V1_LIGADA = False"),
    ("V1 aplicada a fonte que NAO passa os 4 passos", "curadoria/retrato_html.py",
     "if V1_LIGADA and regua_a_mandar is True and url", "if V1_LIGADA and url"),
    ("V1 desligada so no Node", "coleta/retrato_html.mjs", "export const V1_LIGADA = true;",
     "export const V1_LIGADA = false;"),
    ("Node aplica a V1 sem a regua", "coleta/retrato_html.mjs",
     "opcoes.reguaAMandar === true && opcoes.url", "opcoes.url"),
    ("a porta nao passa o endereco", "admissao/admissao.py", "k = rh.veredito(retrato, url=url,",
     "k = rh.veredito(retrato, url=None,"),
    ("a porta da a regua por mandar sempre", "admissao/admissao.py",
     "                    regua_a_mandar=regua)", "                    regua_a_mandar=True)"),
    ("o item perde o endereco", "orquestrador/orquestrador.py",
     'item["url_da_pagina"] = estruturado["SOURCE_URL"]', 'pass'),
    ("a regua do dono diz sempre que manda", "curadoria/ready_split.py",
     "return regua_de(source_id) == REGUA_CURRENT\n    except", "return True\n    except"),
    ("o canario da a regua por mandar sempre", "curadoria/canario.py",
     "regua_a_mandar=_regua_manda(c.get(\"SOURCE_ID\"))", "regua_a_mandar=True"),
    ("a observacao perde o source_url", "guarda/preservar_coleta.py",
     '"SOURCE_URL": linha.get("source_url"),', '"SOURCE_URL": None,'),
    ("a unidade perde o source_url", "coleta/ingresso.py",
     '"SOURCE_URL": o.get("SOURCE_URL"),', '"SOURCE_URL": None,'),
]


def correr() -> bool:
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    r = subprocess.run([sys.executable, "-B", "-m", "unittest", "tests.test_v1a_v1_ligada"],
                       cwd=RAIZ, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.returncode == 0


def main() -> int:
    mortos = 0
    for nome, rel, de, para in MUTANTES:
        f = RAIZ / rel
        orig = f.read_bytes()
        t = orig.decode("utf-8")
        nl = "\r\n" if "\r\n" in t else "\n"
        de_, para_ = de.replace("\n", nl), para.replace("\n", nl)
        if t.count(de_) != 1:
            print("ANCORA NAO CASA (%d): %s" % (t.count(de_), nome))
            continue
        try:
            f.write_bytes(t.replace(de_, para_).encode("utf-8"))
            verde = correr()
        finally:
            f.write_bytes(orig)
        mortos += not verde
        print("%-8s %s" % ("MORTO" if not verde else "SOBREVIVE", nome), flush=True)
    print("MUTATION %d/%d" % (mortos, len(MUTANTES)))
    print("BASE VERDE:", correr())
    return 0 if mortos == len(MUTANTES) else 1


if __name__ == "__main__":
    raise SystemExit(main())
