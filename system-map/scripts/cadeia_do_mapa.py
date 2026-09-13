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


def passos_a_mao() -> list:
    """Os regeneradores que nenhuma automacao corre.

    Escrevem artefatos commitados de que o mapa depende, e nenhum workflow os
    executa. Estao aqui para deixarem de ser invisiveis — nao para fingir que
    correm.

        UM ARTEFATO COMMITADO QUE NENHUMA AUTOMACAO REGENERA
        NAO ESTA ERRADO: ESTA A ENVELHECER SEM TESTEMUNHA.
    """
    return list(CADEIA.get("REGERAR_A_MAO", []))


def portoes_pos_commit() -> list:
    """OS PORTOES QUE SO TEM RESPOSTA DEPOIS DO COMMIT.

    `--conferir-carimbo` compara o carimbo do mapa COMMITADO com a arvore
    COMMITADA. Nao regenera, e nao valida conteudo: pergunta «este mapa e o
    mapa desta arvore?» — e essa pergunta e impossivel antes do commit.

        POR UM PORTAO EM REGERAR PARA ZERAR UMA LISTA E MENTIR SOBRE O
        CONTRATO DELE. PO-LO EM VALIDAR E MENTIR SOBRE QUANDO ELE CORRE.
    """
    return list(CADEIA.get("PORTOES_POS_COMMIT", []))


def outras_execucoes(papel: str = None) -> list:
    """As provas, o publicador do build e o portao de deploy.

    Elas NAO compoem o mapa — nao ha INPUTS/OUTPUTS de geracao a declarar —
    mas o workflow executa-as, e uma execucao que o workflow faz e o manifesto
    nao conhece e uma segunda cadeia a comecar.
    """
    return [x for x in CADEIA.get("OUTRAS_EXECUCOES", [])
            if papel is None or x.get("PAPEL") == papel]


def produtores_externos() -> list:
    """O que o mapa CONSOME e nao produz. Fica fora, e fica dito."""
    return list(CADEIA.get("PRODUTORES_EXTERNOS", []))


def todas_as_execucoes() -> list:
    """TUDO o que pertence ao System Map e e executado. O universo, num sitio so."""
    return (passos() + passos_a_mao() + passos_de_validar()
            + portoes_pos_commit() + outras_execucoes())


def todos_os_passos() -> list:
    """So os que COMPOEM o mapa — os que o contrato de IO do G4 governa."""
    return passos() + passos_a_mao() + passos_de_validar()


def executaveis() -> list:
    """So os caminhos, na ordem — o que o publicador e o CI correm."""
    return [p["EXECUTABLE"] for p in passos()]


def executaveis_de_validar() -> list:
    return [p["EXECUTABLE"] for p in passos_de_validar()]


def executaveis_de(categoria: str) -> list:
    """Os executaveis de UMA categoria, na ordem escrita. Sem ordenar nada."""
    tabela = {"REGERAR": passos, "REGERAR_A_MAO": passos_a_mao,
              "VALIDAR": passos_de_validar,
              "PORTOES_POS_COMMIT": portoes_pos_commit,
              "OUTRAS_EXECUCOES": outras_execucoes}
    if categoria not in tabela:
        raise KeyError("categoria desconhecida: %s (ha %s)"
                       % (categoria, sorted(tabela)))
    return [p["EXECUTABLE"] for p in tabela[categoria]()]


CATEGORIAS = ("REGERAR", "REGERAR_A_MAO", "VALIDAR",
              "PORTOES_POS_COMMIT", "OUTRAS_EXECUCOES")


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


def executavel_que_produz(caminho: str):
    """O EXECUTAVEL que materializa este caminho, ou None.

    `quem_produz` devolve o STEP_ID; quem corre o passo precisa do caminho do
    programa. Sem isto, cada consumidor reconstruia o par artefato -> produtor
    a partir do nome do ficheiro — e um par reconstruido e uma segunda verdade
    a nascer devagar.
    """
    for p in todas_as_execucoes():
        for s in saidas(p):
            if s.get("PATH") == caminho:
                return p["EXECUTABLE"]
    return None


def quem_produz(caminho: str):
    """QUE PASSO DESTE MANIFESTO materializa este caminho? None se nenhum.

    `None` nao quer dizer «ninguem produz»: ha artefatos que o mapa CONSOME e
    nao produz — `golden-path-pdf.generated.json` nasce na COLETA — e esses
    estao em PRODUTORES_EXTERNOS, com dono declarado. Quem chamar isto tem de
    saber a diferenca, e por isso a resposta e None e nunca uma invencao.
    """
    for p in todas_as_execucoes():
        for s in saidas(p):
            if s.get("PATH") == caminho:
                return p["STEP_ID"]
    return None
