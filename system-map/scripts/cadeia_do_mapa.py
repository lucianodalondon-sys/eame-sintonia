#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SINTONIA SYSTEM MAP · O LEITOR DA CADEIA

    O MANIFESTO E UM SO. O JEITO DE O LER TAMBEM.

`CADEIA-DO-MAPA.json` continua a ser o DONO da cadeia — este ficheiro nao
declara passo nenhum, nao guarda lista nenhuma e nao decide ordem nenhuma. Ele
so sabe INTERPRETAR o que o manifesto diz.

Existe porque o `G4` mudou a forma de cada passo:

    antes   "system-map/scripts/scan_repo.py"
    depois  {STEP_ID, EXECUTABLE, INPUTS[], OUTPUTS[]}

Quatro consumidores liam a lista antiga, cada um a seu modo — um `for ... of`,
um `list(...)`, um `.index(...)`, um `[p for p in ...]`. Se cada um aprendesse
sozinho a forma nova, a forma nova passava a ter quatro interpretacoes, e a
quinta mudanca partia tres deles em silencio.

    UM FORMATO COM QUATRO LEITORES NAO E UM FORMATO: SAO QUATRO ACORDOS
    QUE POR ENQUANTO CALHAM BATER.

O lado JavaScript tem o seu proprio leitor em `publicar_no_deploy.mjs`, porque
sao dois runtimes e nao ha como partilhar codigo — mas e UM por runtime, que e
o minimo possivel, e `test_system_map.py` prova que os dois leem o mesmo.

O QUE ESTE FICHEIRO NAO FAZ
---------------------------
Nao ordena. Nao deriva ordem de INPUTS/OUTPUTS — isso e o `G6`, e faze-lo aqui
seria implementa-lo a socapa. `passos()` devolve a ordem que esta escrita no
manifesto, e mais nada.
"""
import json
from pathlib import Path

AQUI = Path(__file__).resolve().parent
MANIFESTO = AQUI / "CADEIA-DO-MAPA.json"
CADEIA = json.loads(MANIFESTO.read_text(encoding="utf-8"))

TRACKED_SOURCE_TREE = "TRACKED_SOURCE_TREE"
TRACKED_SOURCE_FILE = "TRACKED_SOURCE_FILE"
GENERATED_ARTIFACT = "GENERATED_ARTIFACT"
CANONICAL_MANIFEST = "CANONICAL_MANIFEST"
KINDS = (TRACKED_SOURCE_TREE, TRACKED_SOURCE_FILE,
         GENERATED_ARTIFACT, CANONICAL_MANIFEST)

FORA_DO_MANIFESTO = "FORA_DO_MANIFESTO"


def passos() -> list:
    """Os passos de regeneracao, NA ORDEM ESCRITA no manifesto."""
    return list(CADEIA["REGERAR"])


def passos_de_validar() -> list:
    return list(CADEIA["VALIDAR"])


def todos_os_passos() -> list:
    return passos() + passos_de_validar()


def executaveis() -> list:
    """So os caminhos, na ordem — o que o publicador e o CI correm."""
    return [p["EXECUTABLE"] for p in passos()]


def executaveis_de_validar() -> list:
    return [p["EXECUTABLE"] for p in passos_de_validar()]


def por_id(step_id: str) -> dict:
    for p in todos_os_passos():
        if p["STEP_ID"] == step_id:
            return p
    raise KeyError(step_id)


def entradas(passo: dict, kind: str = None) -> list:
    return [e for e in passo.get("INPUTS", [])
            if kind is None or e.get("KIND") == kind]


def saidas(passo: dict) -> list:
    return list(passo.get("OUTPUTS", []))


def quem_produz(caminho: str):
    """QUE PASSO DESTE MANIFESTO materializa este caminho? None se nenhum.

    `None` nao quer dizer «ninguem produz»: treze scripts do workflow estao
    fora deste manifesto (divida do `G5`), e um artefato deles tem produtor
    real e produtor NAO DECLARADO AQUI. Quem chamar isto tem de saber a
    diferenca — e por isso a resposta e None, e nunca uma invencao.
    """
    for p in todos_os_passos():
        for s in saidas(p):
            if s.get("PATH") == caminho:
                return p["STEP_ID"]
    return None
