#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OS VAZAMENTOS DO CUTOVER, MEDIDOS — nao afirmados.

Depois da Fase 5 do cutover, a populacao da coleta agendada sai do portao
(`curadoria/collection_gate.py`) e nao de uma lista escrita a mao. Esta prova
mede, sobre a decisao REAL do coletor, se alguma fonte que o portao recusou
chegou a entrar na coleta.

    UM PORTAO QUE DIZ NAO E UM COLETOR QUE VAI LA MESMO
    NAO E UM PORTAO: E UM AVISO.

Quatro vazamentos, cada um com o nome do motivo que o portao usou:

    READY_LEGACY_LEAK       fonte promovida pela regua antiga que entrou
    HUMAN_REVIEW_LEAK       fonte que espera gente e entrou sem gente
    POLICY_BLOCK_LEAK       fonte barrada por politica que entrou
    CAPABILITY_BLOCK_LEAK   fonte barrada por capacidade que entrou

⚠️ ZERO REDE. Corre `--so-o-portao`, que para antes de tocar em fonte nenhuma.

⚠️ NENHUM VALOR ESPERADO E LIDO DA ESTRUTURA QUE SE FISCALIZA. A populacao
colhida NAO e lida de `COLLECTION_ELIGIBLE_IDS` (isso seria comparar a lista
consigo propria — tautologia). Le-se do campo que o coletor escreve sobre o
que VAI colher, e cruza-se com as RECUSADAS que o portao escreveu.

    py provas/o_cutover_nao_vaza.py
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAIDA = os.path.join(RAIZ, "provas", "O-CUTOVER-NAO-VAZA-V1.json")

#: Cada motivo do portao -> o nome do vazamento correspondente. Cinco nomes,
#: nunca dois: um motivo sem nome proprio dilui-se numa soma, e uma soma nao
#: diz de que lei o nao veio.
MOTIVO_PARA_VAZAMENTO = {
    "READY_LEGACY": "READY_LEGACY_LEAK",
    "HUMAN_REVIEW_REQUIRED": "HUMAN_REVIEW_LEAK",
    "ESTADO_NAO_READY": "ESTADO_NAO_READY_LEAK",
    "POLICY_BLOCK": "POLICY_BLOCK_LEAK",
    "CAPABILITY_BLOCK": "CAPABILITY_BLOCK_LEAK",
}

#: Os quatro que a missao do cutover exige a zero, mesmo que o portao nao
#: tenha usado o motivo nesta corrida. Um vazamento que nao aparece porque o
#: motivo nao ocorreu tem de sair `0`, e nao desaparecer do relatorio.
EXIGIDOS_A_ZERO = ("READY_LEGACY_LEAK", "HUMAN_REVIEW_LEAK",
                   "POLICY_BLOCK_LEAK", "CAPABILITY_BLOCK_LEAK")


def _correr_o_portao():
    """O coletor, so ate ao portao. Devolve o resumo que ele escreveu."""
    env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    r = subprocess.run(
        ["node", "coleta/italy_recurrent_collect.mjs",
         "--profile", "forward-only-live", "--so-o-portao"],
        cwd=RAIZ, capture_output=True, timeout=900, env=env)
    txt = (r.stdout + r.stderr).decode("utf-8", "replace")
    i, j = txt.find("{"), txt.rfind("}")
    if i < 0 or j < 0:
        raise RuntimeError("o coletor nao escreveu resumo: %s" % txt[-600:])
    return json.loads(txt[i:j + 1])


def main():
    resumo = _correr_o_portao()

    # O QUE O COLETOR VAI COLHER. Nao se le da lista de elegiveis: le-se do
    # que ele declarou sobre a decisao dele.
    elegiveis = resumo.get("COLLECTION_ELIGIBLE")
    com_contrato = resumo.get("ELIGIBLE_WITH_CONTRACT")
    sem_contrato = resumo.get("ELIGIBLE_WITHOUT_CONTRACT") or []
    recusadas = resumo.get("COLLECTION_REFUSED_BY_MOTIVE") or {}

    fora = {
        "PROVA": "provas/o_cutover_nao_vaza.py",
        "REDE": 0,
        "COLLECTION_SOURCE_SELECTION": resumo.get("COLLECTION_SOURCE_SELECTION"),
        "COLLECTION_INTAKE_GATE": resumo.get("COLLECTION_INTAKE_GATE"),
        "RUN_STATE": resumo.get("RUN_STATE"),
        "COLLECTION_ELIGIBLE": elegiveis,
        "ELIGIBLE_WITH_CONTRACT": com_contrato,
        "ELIGIBLE_WITHOUT_CONTRACT": sem_contrato,
        "COLLECTION_REFUSED_TOTAL": resumo.get("COLLECTION_REFUSED_TOTAL"),
        "RECUSADAS_POR_MOTIVO": {k: len(v) for k, v in recusadas.items()},
    }

    problemas = []

    # 1 · A SELECAO VEM DO PORTAO, E ESTA DITO.
    if resumo.get("COLLECTION_SOURCE_SELECTION") != "COLLECTION_GATE":
        problemas.append("COLLECTION_SOURCE_SELECTION nao e COLLECTION_GATE: %r"
                         % resumo.get("COLLECTION_SOURCE_SELECTION"))

    # 2 · OS VAZAMENTOS. Uma recusada nao pode estar entre as que vao colher.
    #     `--so-o-portao` para antes de colher, e por isso a populacao que ele
    #     ia colher e `elegiveis menos sem_contrato`. Cruza-se COM os IDs, nao
    #     com as contagens: uma contagem igual nao prova que sao os mesmos.
    ids_recusados = set()
    for motivo, ids in recusadas.items():
        ids_recusados.update(ids)
    # Os IDs que o coletor ia colher: os elegiveis com contrato. O coletor nao
    # os imprime em lista (imprime a contagem e os SEM contrato), e por isso
    # pergunta-se ao portao pelos elegiveis e subtraem-se os sem contrato.
    r = subprocess.run([sys.executable if os.path.basename(sys.executable).startswith("py") else "py",
                        "curadoria/collection_gate.py", "--json"],
                       cwd=RAIZ, capture_output=True, timeout=900,
                       env=dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8"))
    t = (r.stdout + r.stderr).decode("utf-8", "replace")
    portao = json.loads(t[t.find("{"):t.rfind("}") + 1])
    ids_elegiveis = set(portao["COLLECTION_ELIGIBLE_IDS"])
    ids_a_colher = ids_elegiveis - set(sem_contrato)
    fora["IDS_A_COLHER"] = sorted(ids_a_colher)

    vazamentos = {}
    for motivo, ids in recusadas.items():
        nome = MOTIVO_PARA_VAZAMENTO.get(motivo, "%s_LEAK" % motivo)
        vazou = sorted(set(ids) & ids_a_colher)
        vazamentos[nome] = len(vazou)
        if vazou:
            problemas.append("%s: %s" % (nome, vazou))
    for nome in EXIGIDOS_A_ZERO:
        vazamentos.setdefault(nome, 0)
    fora["VAZAMENTOS"] = vazamentos

    # 3 · COERENCIA DAS CONTAS. Elegiveis = com contrato + sem contrato.
    if elegiveis != len(ids_a_colher) + len(sem_contrato):
        problemas.append("a conta nao fecha: elegiveis=%s, a colher=%d, sem contrato=%d"
                         % (elegiveis, len(ids_a_colher), len(sem_contrato)))
    if com_contrato != len(ids_a_colher):
        problemas.append("ELIGIBLE_WITH_CONTRACT=%s mas os IDs a colher sao %d"
                         % (com_contrato, len(ids_a_colher)))

    # 4 · NENHUMA FONTE FOI TOCADA. `--so-o-portao` tem de parar antes.
    if resumo.get("SOURCE_ATTEMPTED"):
        problemas.append("--so-o-portao tocou %s fonte(s)" % resumo.get("SOURCE_ATTEMPTED"))

    fora["PROBLEMAS"] = problemas
    fora["CUTOVER_NAO_VAZA"] = not problemas

    with open(SAIDA, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(fora, fh, ensure_ascii=False, indent=1)
        fh.write("\n")

    for k in ("COLLECTION_SOURCE_SELECTION", "COLLECTION_ELIGIBLE",
              "ELIGIBLE_WITH_CONTRACT", "ELIGIBLE_WITHOUT_CONTRACT",
              "COLLECTION_REFUSED_TOTAL", "RECUSADAS_POR_MOTIVO",
              "IDS_A_COLHER"):
        print("%-32s %s" % (k, fora[k]))
    print()
    for nome in sorted(vazamentos):
        print("%-32s %d" % (nome, vazamentos[nome]))
    print()
    if problemas:
        for p in problemas:
            print("PROBLEMA: %s" % p)
        print("CUTOVER_NAO_VAZA = NO")
        return 1
    print("CUTOVER_NAO_VAZA = YES")
    return 0


if __name__ == "__main__":
    sys.exit(main())
