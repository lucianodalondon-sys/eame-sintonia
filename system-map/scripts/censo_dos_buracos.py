#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SINTONIA SYSTEM MAP · O CENSO DOS BURACOS DECLARADOS

    UM BURACO QUE SO EXISTE NUM `print` NAO EXISTE PARA NINGUEM.

O repositorio tem a disciplina de declarar o que NAO fecha. O que ele nao tinha
era uma maneira de os VER juntos — e por isso quatro buracos com nome viviam em
tres formatos diferentes:

    coleta/derivacao_forward.py        tuplo `GAPS`, legivel por AST
    system-map/data/provas-de-execucao.json   chaves com GAP no nome
    provas/o_forward_conta_se.py       ...um `print`. So texto impresso.

    TRES MANEIRAS DE DECLARAR A MESMA COISA, E UMA DELAS INVISIVEL.

ESTE FICHEIRO NAO E UM REGISTO NOVO, E ISSO E O PONTO
------------------------------------------------------
Copiar os buracos para um JSON meu criaria o QUARTO sitio, e a partir daí
nenhum deles valeria: o dia em que um agente fechasse um buraco no codigo e se
esquecesse da minha copia, o mapa passaria a mentir com confianca.

    O MAPA E DERIVADO DO REPO. UM REGISTO DE BURACOS TAMBEM TEM DE SER.

Entao ele MEDE, nos dois sitios onde o buraco ja vive, e a saida e derivada:

    1. os tuplos `GAPS = ((NOME, O_QUE_FALTA), ...)` de qualquer ficheiro .py
       rastreado, lidos por AST — nunca por regex sobre o texto;
    2. as chaves com `GAP` no nome dentro de `provas-de-execucao.json`.

Fechar um buraco e apagar a linha onde ele esta declarado. O censo seguinte
deixa de o ver, e o mapa deixa de o desenhar. Nao ha segunda coisa a actualizar.
"""

import ast
import json
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
PROVAS = RAIZ / "system-map" / "data" / "provas-de-execucao.json"
SAIDA = RAIZ / "system-map" / "data" / "buracos.generated.json"


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(RAIZ), *args],
                          capture_output=True, text=True,
                          encoding="utf-8", errors="replace").stdout.rstrip("\n")


def dos_tuplos() -> list[dict]:
    """Os `GAPS` do codigo, lidos por AST.

    AST e nao regex de proposito: um regex apanharia a palavra GAPS dentro de um
    comentario, de uma docstring ou de um teste que fala sobre buracos, e o mapa
    passaria a desenhar buracos que ninguem declarou. `ast.literal_eval` tambem
    recusa qualquer coisa que nao seja um literal — um `GAPS` montado por codigo
    nao entra, e e melhor assim: um buraco declarado por expressao muda sem o
    ficheiro mudar.
    """
    achados = []
    for caminho in git("ls-files", "*.py").splitlines():
        f = RAIZ / caminho
        try:
            arvore = ast.parse(f.read_text(encoding="utf-8"))
        except (OSError, SyntaxError):
            continue
        for no in arvore.body:
            if not isinstance(no, ast.Assign):
                continue
            if not any(getattr(a, "id", "") == "GAPS" for a in no.targets):
                continue
            try:
                valor = ast.literal_eval(no.value)
            except (ValueError, SyntaxError):
                achados.append({"NOME": "GAPS_NAO_LITERAL", "ONDE": caminho,
                                "LINHA": no.lineno, "FORMA": "tuplo",
                                "O_QUE_FALTA": "declarado por expressao: nao se "
                                               "consegue ler sem correr o ficheiro"})
                continue
            for entrada in valor:
                nome, texto = (list(entrada) + [""])[:2] if isinstance(
                    entrada, (list, tuple)) else (str(entrada), "")
                achados.append({"NOME": nome, "ONDE": caminho, "LINHA": no.lineno,
                                "FORMA": "tuplo GAPS", "O_QUE_FALTA": texto})
    return achados


def _faltas(gap: dict) -> list[dict]:
    """As FALTAS medidas dentro de um buraco — as razoes de ele estar aberto.

    ⚠️ ELAS NAO SAO CINCO BURACOS. Sao as cinco coisas que faltam para UM
    buracos fechar, e achatar as duas coisas no mesmo nivel faria a tela dizer
    treze onde ha oito.

        A RAZAO DE UM BURACO ESTAR ABERTO NAO E OUTRO BURACO.

    Reconhecem-se pela forma, como tudo aqui: um dicionario que diz o que FALTA.
    O delta `1c99a48b` acrescentou a quarta e a quinta a `MISSING_AUTHORITY` de
    `CHANNEL_IDENTITY_NOT_RESOLVED`, e este censo passa a DERIVA-LAS de onde
    elas ja vivem — copia-las para aqui seria o quarto registo, e a partir dai
    nenhum dos outros valeria.
    """
    saida = []
    for _chave, valor in gap.items():
        if not isinstance(valor, list):
            continue
        for item in valor:
            if isinstance(item, dict) and "FALTA" in item:
                saida.append({
                    "N": item.get("N"),
                    "FALTA": item.get("FALTA", ""),
                    "ONDE_DEVIA_ESTAR": item.get("ONDE_DEVIA_ESTAR"),
                    "MEDIDO": item.get("MEDIDO", ""),
                    "CASO": item.get("CASO"),
                })
    return sorted(saida, key=lambda f: (f["N"] is None, f["N"]))


def das_provas() -> list[dict]:
    """Os buracos dentro de `provas-de-execucao.json`.

    ⚠️ A PRIMEIRA VERSAO DISTO APANHAVA A PALAVRA «GAP» NO NOME DA CHAVE, e a
    medicao mostrou o erro na primeira corrida: ela devolveu `GAPS_DE_IDENTIDADE`
    — que e um CAIXOTE, nao um buraco — e PERDEU o buraco la dentro,
    `CHANNEL_IDENTITY_NOT_RESOLVED`, porque o nome dele nao tem «GAP».

        O NOME DA CHAVE NAO DIZ O QUE ELA E. A FORMA DO VALOR DIZ.

    Um buraco tem CORPO: ele diz o que falta, ou em que estado esta. Um caixote
    so tem filhos. Entao a regra passa a olhar para o valor:

        dict com ESTADO ou O_QUE_FALTA   -> e um buraco, e o nome e a chave
        texto sob uma chave com GAP      -> e um buraco declarado numa frase
        qualquer outra coisa             -> continua a descer
    """
    if not PROVAS.exists():
        return []
    d = json.loads(PROVAS.read_text(encoding="utf-8"))
    ONDE = "system-map/data/provas-de-execucao.json"
    achados = []

    def andar(o, caminho):
        if isinstance(o, dict):
            for k, v in o.items():
                sob = f"{caminho}/{k}" if caminho else k
                if isinstance(v, dict) and ("ESTADO" in v or "O_QUE_FALTA" in v):
                    achados.append({
                        "NOME": k, "ONDE": ONDE, "LINHA": None,
                        "FORMA": f"chave em {caminho or '(raiz)'}",
                        "O_QUE_FALTA": v.get("O_QUE_FALTA", ""),
                        "ESTADO": v.get("ESTADO"),
                        "FALTAS": _faltas(v),
                    })
                elif isinstance(v, str) and "GAP" in k.upper():
                    achados.append({
                        "NOME": k, "ONDE": ONDE, "LINHA": None,
                        "FORMA": f"frase em {caminho or '(raiz)'}",
                        "O_QUE_FALTA": v, "ESTADO": None,
                    })
                andar(v, sob)
        elif isinstance(o, list):
            for i, v in enumerate(o):
                andar(v, f"{caminho}[{i}]")

    andar(d, "")
    return achados


def main() -> int:
    achados = dos_tuplos() + das_provas()
    achados.sort(key=lambda a: (a["NOME"], a["ONDE"]))
    nomes = sorted({a["NOME"] for a in achados})
    dados = {
        "SCHEMA": "sintonia.system-map.buracos/1",
        "NOTA": [
            "DERIVADO. Nao editar a mao — ele e medido, nunca escrito.",
            "Fechar um buraco e apagar a linha onde ele esta DECLARADO (o tuplo",
            "`GAPS` do ficheiro, ou a chave em provas-de-execucao.json). O censo",
            "seguinte deixa de o ver. Nao ha segunda coisa a actualizar, e e por",
            "isso que este ficheiro nao e um registo.",
        ],
        "PROVENANCE": {"HEAD": git("rev-parse", "HEAD"),
                       "MEDIDO_POR": "censo_dos_buracos.py"},
        "COUNTS": {"buracos": len(achados), "nomes_distintos": len(nomes),
                   "em_codigo": sum(1 for a in achados if a["ONDE"].endswith(".py")),
                   "em_provas": sum(1 for a in achados if a["ONDE"].endswith(".json")),
                   # As FALTAS contam-se a parte dos buracos, de proposito: elas
                   # sao as razoes de um buraco estar aberto, e somar as duas
                   # coisas daria um numero que nao e nenhuma das duas.
                   "faltas_medidas": sum(len(a.get("FALTAS") or []) for a in achados)},
        "NOMES": nomes,
        "BURACOS": achados,
    }
    SAIDA.write_text(json.dumps(dados, ensure_ascii=False, indent=2) + "\n",
                     encoding="utf-8")
    print(f"BURACOS=OK · {len(achados)} declarado(s) · {len(nomes)} nome(s) · "
          f"codigo={dados['COUNTS']['em_codigo']} provas={dados['COUNTS']['em_provas']}"
          f" · faltas medidas dentro deles={dados['COUNTS']['faltas_medidas']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
