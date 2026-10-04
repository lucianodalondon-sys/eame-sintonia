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
Nao ordena — e isto continua verdade depois do G6. Quem ordena e o leitor
canonico, porque a ordem e propriedade do manifesto e nao do veiculo. Um `sort`
aqui dentro poria a ordem a depender de QUEM corre a cadeia, e a Vercel corre-a
por outro caminho.

Nao decide o que e cadeia: quem decide e o manifesto.

O QUE ELE PASSOU A FAZER (G6)
-----------------------------
Recusa-se a correr quando a ordem ESCRITA no manifesto contradiz a ordem que as
dependencias derivam. A execucao estaria certa de qualquer maneira — `passos()`
devolve a derivada — mas o ficheiro estaria a dizer uma coisa e a maquina a
fazer outra, e o leitor JavaScript le o ficheiro.

    UM FICHEIRO QUE MENTE SOBRE A ORDEM NAO E INOFENSIVO SO PORQUE
    O PYTHON O CORRIGE: O OUTRO RUNTIME ACREDITA NELE.
"""
import subprocess
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
sys.path.insert(0, str(AQUI))
import cadeia_do_mapa as CAD                               # noqa: E402


def conferir_a_ordem() -> int:
    """A ORDEM ESCRITA TEM DE SER A ORDEM DERIVADA. Senao, para."""
    escrita = [p["STEP_ID"] for p in CAD.ordem_escrita()]
    derivada = CAD.ordem_derivada()
    if escrita == derivada:
        return 0
    print("CADEIA=FALHOU · a ordem escrita no manifesto contradiz as "
          "dependencias declaradas", file=sys.stderr)
    for i, (e, d) in enumerate(zip(escrita, derivada), 1):
        if e != d:
            print("  #%-2d escrito %-28s derivado %s" % (i, e, d), file=sys.stderr)
    print("  corrige o manifesto (ou a declaracao de INPUTS que o contradiz); "
          "a lei vive em LEI_DA_ORDEM", file=sys.stderr)
    return 3


def correr(categoria: str, listar: bool = False) -> int:
    if categoria == "REGERAR":
        mau = conferir_a_ordem()
        if mau:
            return mau
    # ⚠️ REGERAR_A_MAO FALTAVA AQUI. `CATEGORIAS` anunciava-a, `main()` aceitava-a
    # e esta tabela nao a tinha — logo `correr_a_cadeia.py REGERAR_A_MAO` morria
    # com KeyError em vez de correr os tres regeneradores declarados. Ninguem deu
    # por isso porque ninguem lhes chama: e exactamente a categoria dos passos que
    # nao tem testemunha.
    #
    #     A CATEGORIA QUE NINGUEM CORRE E A QUE PODE ESTAR PARTIDA HA MESES.
    tabela = {
        "REGERAR": CAD.passos, "REGERAR_A_MAO": CAD.passos_a_mao,
        "VALIDAR": CAD.passos_de_validar,
        "PORTOES_POS_COMMIT": CAD.portoes_pos_commit,
        "OUTRAS_EXECUCOES": CAD.outras_execucoes,
    }
    faltam = [c for c in CAD.CATEGORIAS if c not in tabela]
    if faltam:
        print("CADEIA=FALHOU · categorias sem corredor: %s" % faltam, file=sys.stderr)
        return 4
    passos = tabela[categoria]()
    if listar:
        for p in passos:
            print(p["EXECUTABLE"])
        return 0
    print("CADEIA · %s · %d passo(s), pela ordem que as dependencias derivam" % (categoria, len(passos)))
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
