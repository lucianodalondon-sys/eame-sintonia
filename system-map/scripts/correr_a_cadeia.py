#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SINTONIA SYSTEM MAP · O CORREDOR DA CADEIA

    python3 system-map/scripts/correr_a_cadeia.py REGERAR
    python3 system-map/scripts/correr_a_cadeia.py VALIDAR
    python3 system-map/scripts/correr_a_cadeia.py PORTOES_POS_COMMIT
    python3 system-map/scripts/correr_a_cadeia.py --listar REGERAR

O WORKFLOW TINHA A SEGUNDA LISTA. Ela estava escrita em YAML, dezanove linhas
seguidas, e ninguem a comparava com o manifesto — pior: os dois jobs do mesmo
ficheiro tinham listas DIFERENTES. O job `mapa` corria dezanove scripts; o job
`regras` corria sete.

    DOIS SITIOS COM A LISTA DOS PASSOS NAO SAO UMA LISTA REPETIDA:
    SAO DUAS CADEIAS, E UMA DELAS ESTA SEMPRE ERRADA SEM NINGUEM SABER.

Este ficheiro NAO tem lista nenhuma. Ele le `CADEIA-DO-MAPA.json` em runtime,
pede a categoria ao leitor canonico e corre o que estiver la, PELA ORDEM
ESCRITA. Se alguem acrescentar um passo ao manifesto, ele corre no dia
seguinte sem ninguem editar YAML; se alguem o tirar, deixa de correr.

O QUE ELE NAO FAZ
-----------------
Nao ordena. Nao deriva ordem de INPUTS/OUTPUTS — isso e o `G6`. A ordem e a que
esta escrita, e um `sort` aqui dentro seria o G6 implementado a socapa dentro
de um corredor.

Nao decide o que e cadeia: quem decide e o manifesto.
"""
import subprocess
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
sys.path.insert(0, str(AQUI))
import cadeia_do_mapa as CAD                               # noqa: E402


def correr(categoria: str, listar: bool = False) -> int:
    passos = {
        "REGERAR": CAD.passos, "VALIDAR": CAD.passos_de_validar,
        "PORTOES_POS_COMMIT": CAD.portoes_pos_commit,
        "OUTRAS_EXECUCOES": CAD.outras_execucoes,
    }[categoria]()
    if listar:
        for p in passos:
            print(p["EXECUTABLE"])
        return 0
    print("CADEIA · %s · %d passo(s), pela ordem do manifesto" % (categoria, len(passos)))
    for i, p in enumerate(passos, 1):
        exe = p["EXECUTABLE"]
        # UM PASSO PODE PRECISAR DE ARGUMENTOS, E ELES VEM DO MANIFESTO.
        # O portao pos-commit e `--conferir-carimbo`: se o argumento vivesse no
        # YAML, a segunda lista voltava pela porta dos parametros.
        args = list(p.get("ARGUMENTOS") or [])
        motor = ["node"] if exe.endswith((".mjs", ".js")) else [sys.executable]
        print("  %2d/%d · %s%s" % (i, len(passos), exe,
                                   (" " + " ".join(args)) if args else ""))
        r = subprocess.run(motor + [exe] + args, cwd=str(RAIZ))
        if r.returncode != 0:
            print("CADEIA=FALHOU · %s saiu com %d" % (exe, r.returncode),
                  file=sys.stderr)
            return r.returncode
    print("CADEIA=OK · %s" % categoria)
    return 0


def main(argv: list) -> int:
    listar = "--listar" in argv
    resto = [a for a in argv if a != "--listar"]
    if len(resto) != 1 or resto[0] not in CAD.CATEGORIAS:
        print("uso: correr_a_cadeia.py [--listar] {%s}"
              % "|".join(CAD.CATEGORIAS), file=sys.stderr)
        return 2
    return correr(resto[0], listar)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
