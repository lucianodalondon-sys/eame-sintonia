#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A DEMANDA DE DADOS DA INTELLIGENCE — ITÁLIA. Mede, não opina.

    MISSAO   C-INT-DATA-DEMAND-IT-01
    ESPECIE  MEDIDOR DE ESTUDO — LE, CONTA E IMPRIME. NAO ESCREVE NADA.

    python3 provas/demanda_de_dados_da_italia.py
    python3 provas/demanda_de_dados_da_italia.py --json

A PERGUNTA QUE ESTE FICHEIRO RESPONDE, E MAIS NENHUMA
-----------------------------------------------------
    QUE CRUZAMENTO A MATERIA-PRIMA ITALIANA DE HOJE SUSTENTA, E QUAL CHAVE
    FALTA PARA OS QUE ELA NAO SUSTENTA?

Ele não decide arquitetura. Os cruzamentos vivem em
`research/intelligence/AGRO-CROSSING-GRAPH-V1.md`, os requisitos em
`AGRO-INTELLIGENCE-INPUT-REQUIREMENTS-V1.md` e os papéis em
`AGRO-INTELLIGENCE-TOOL-ROLES-V1.md`. Este ficheiro só mede a Itália contra eles.

    DADO QUE EXISTE != DADO QUE CRUZA != DADO QUE SUSTENTA DECISAO.

E a diferença entre os três é o produto desta medição.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
CLIENTE = RAIZ / "italia-portale" / "client"

# NAO SEI e um VALOR, nao uma ausencia. Uma familia que diz «nao sei» em 17 de
# 17 linhas nao tem zero linhas: tem 17 linhas que nao cruzam.
IGNORANCIA = {
    None, "", "-", "—", "NAO SEI", "NÃO SEI", "NAO_SEI", "UNKNOWN",
    "NOT_KNOWN", "NOT_APPLICABLE", "N/A", "null", "None",
}


def _carrega(ficheiro: str, variavel: str) -> dict:
    texto = (CLIENTE / ficheiro).read_text(encoding="utf-8")
    marca = variavel + " = "
    return json.loads(texto[texto.index(marca) + len(marca):texto.rindex("}") + 1])


def pacote_v21() -> dict:
    return _carrega("italy-v21.js", "window.ITALY_HANDOFF_V21")


def sabe(registo: dict, chave: str) -> bool:
    """A chave esta preenchida com algo que nao e ignorancia declarada."""
    valor = registo.get(chave)
    if isinstance(valor, list):
        return bool([x for x in valor if x not in IGNORANCIA])
    if isinstance(valor, str) and valor.strip().upper().startswith("NAO SEI"):
        return False
    return valor not in IGNORANCIA


def valores(linhas: list, chave: str) -> set:
    saida = set()
    for r in linhas:
        v = r.get(chave)
        for x in (v if isinstance(v, list) else [v]):
            if x not in IGNORANCIA:
                saida.add(str(x))
    return saida


# Uma regiao nao e um pais. REGION_IDS = GEO_ITALY diz «Italia», e Italia nao
# distingue Puglia de Veneto — logo nao serve a nenhum cruzamento regional.
def regioes(linhas: list) -> set:
    return {v for v in valores(linhas, "REGION_IDS") if v.startswith("REGION_")}


def densidade(linhas: list) -> dict:
    n = len(linhas)
    if not n:
        return {}
    return {
        "N": n,
        "CROP_IDS": sum(sabe(r, "CROP_IDS") for r in linhas),
        "ISSUE_IDS": sum(sabe(r, "ISSUE_IDS") for r in linhas),
        "REGION_SUBNACIONAL": sum(
            1 for r in linhas
            if any(str(x).startswith("REGION_") for x in (r.get("REGION_IDS") or []))
        ),
        "REFERENCE_DATE": sum(sabe(r, "REFERENCE_DATE") for r in linhas),
        "SOURCE_IDS": sum(sabe(r, "SOURCE_IDS") for r in linhas),
    }


# ---------------------------------------------------------------- cruzamentos
# Cada cruzamento declara a pergunta que responde (INT-LAW-090) e as chaves que
# o instanciam (INT-LAW-091). Sem chave, o estado e NOT_POSSIBLE — nunca
# closest-match silencioso.
CRUZAMENTOS = (
    dict(ID="X-FIELD-x-SCIENCE",
         PERGUNTA="o que a ciencia diz sobre o problema que o campo esta a ver, aqui?",
         A="fieldSignals", B="science", CHAVES=("CROP_IDS", "ISSUE_IDS")),
    dict(ID="X-FIELD-x-CLIMA",
         PERGUNTA="as condicoes favoreceram o problema que o boletim reportou?",
         A="fieldSignals", B="agromet", CHAVES=("REGION_IDS", "ISSUE_IDS")),
    dict(ID="X-FIELD-x-JANELA",
         PERGUNTA="o que o campo reporta cai dentro de alguma janela de aplicacao?",
         A="fieldSignals", B="windows", CHAVES=("CROP_IDS", "ISSUE_IDS", "REGION_IDS")),
    dict(ID="X-JANELA-x-PORTFOLIO",
         PERGUNTA="a ADAMA tem uso registado para a janela que esta aberta?",
         A="windows", B="products.relationships", CHAVES=("CROP_IDS", "ISSUE_IDS")),
    dict(ID="X-FIELD-x-PORTFOLIO",
         PERGUNTA="a ADAMA tem resposta registada para o que o campo esta a ver?",
         A="fieldSignals", B="products.relationships", CHAVES=("CROP_IDS", "ISSUE_IDS")),
    dict(ID="X-CONCORRENCIA-x-PORTFOLIO",
         PERGUNTA="quem mais tem resposta registada para este par cultura x alvo?",
         A="competitors", B="products.relationships", CHAVES=("CROP_IDS", "ISSUE_IDS")),
    dict(ID="X-CONCORRENCIA-x-CAMPO",
         PERGUNTA="a comunicacao do concorrente coincide com o que o campo reporta?",
         A="competitors", B="fieldSignals", CHAVES=("CROP_IDS", "ISSUE_IDS", "REGION_IDS")),
    dict(ID="X-MERCADO-x-CULTURA",
         PERGUNTA="o preco desta cultura mudou onde o problema esta a acontecer?",
         A="market", B="fieldSignals", CHAVES=("CROP_IDS", "REGION_IDS")),
    dict(ID="X-REGULATORIO-x-PORTFOLIO",
         PERGUNTA="que produtos ADAMA sao atingidos por uma decisao de substancia?",
         A="regulatoryFutureFacts", B="products.activeIngredients",
         CHAVES=("ACTIVE_INGREDIENT_ID",)),
    dict(ID="X-VOZ-x-CAMPO",
         PERGUNTA="a voz publica confirma o que o boletim oficial reportou?",
         A="voices", B="fieldSignals", CHAVES=("CROP_IDS", "ISSUE_IDS", "REGION_IDS")),
    dict(ID="X-CIENCIA-x-PORTFOLIO",
         PERGUNTA="ha trabalho publicado sobre o alvo que a ADAMA cobre?",
         A="science", B="products.relationships", CHAVES=("CROP_IDS", "ISSUE_IDS")),
    dict(ID="X-RESISTENCIA-x-PORTFOLIO",
         PERGUNTA="a resistencia confirmada toca alguma substancia do portfolio?",
         A="resistance", B="products.relationships", CHAVES=("CROP_IDS", "ISSUE_IDS")),
)


def julga(cruzamento: dict, coleccoes: dict) -> dict:
    a = coleccoes.get(cruzamento["A"]) or []
    b = coleccoes.get(cruzamento["B"]) or []
    faltam, interseccoes = [], {}
    for chave in cruzamento["CHAVES"]:
        va, vb = valores(a, chave), valores(b, chave)
        if chave == "REGION_IDS":
            va = {x for x in va if x.startswith("REGION_")}
            vb = {x for x in vb if x.startswith("REGION_")}
        if not va:
            faltam.append(f"{chave} ausente em {cruzamento['A']}")
        if not vb:
            faltam.append(f"{chave} ausente em {cruzamento['B']}")
        interseccoes[chave] = sorted(va & vb)

    # VALOR PARTILHADO != LINHA QUE ATRAVESSA. Duas pontas podem partilhar
    # «GRAPEVINE» e mesmo assim nenhuma linha carregar TODAS as chaves ao
    # mesmo tempo. Quem decide e a linha, nao o vocabulario.
    def sobrevivem(linhas):
        n = 0
        for r in linhas:
            ok = True
            for chave in cruzamento["CHAVES"]:
                v = {str(x) for x in (r.get(chave) or [])} if isinstance(
                    r.get(chave), list) else (
                    {str(r.get(chave))} if sabe(r, chave) else set())
                if chave == "REGION_IDS":
                    v = {x for x in v if x.startswith("REGION_")}
                if not (v & set(interseccoes[chave])):
                    ok = False
                    break
            n += ok
        return n

    viva_a, viva_b = sobrevivem(a), sobrevivem(b)

    if faltam:
        estado = "NOT_POSSIBLE"
    elif not all(interseccoes[k] for k in cruzamento["CHAVES"]):
        estado = "NOT_POSSIBLE"
        faltam.append("as duas pontas nao partilham um unico valor em "
                      + ", ".join(k for k in cruzamento["CHAVES"]
                                  if not interseccoes[k]))
    elif not (viva_a and viva_b):
        estado = "NOT_POSSIBLE"
        faltam.append("nenhuma linha carrega todas as chaves ao mesmo tempo")
    elif min(viva_a, viva_b) < 10:
        estado = "PARTIAL"
    else:
        estado = "POSSIBLE"

    return dict(CROSSING_ID=cruzamento["ID"], PERGUNTA=cruzamento["PERGUNTA"],
                A=cruzamento["A"], B=cruzamento["B"], N_A=len(a), N_B=len(b),
                CHAVES=list(cruzamento["CHAVES"]),
                INTERSECCAO={k: len(v) for k, v in interseccoes.items()},
                LINHAS_QUE_ATRAVESSAM={cruzamento["A"]: viva_a,
                                       cruzamento["B"]: viva_b},
                CROSSING_STATE=estado, BLOQUEIO=faltam)


def medir() -> dict:
    H = pacote_v21()
    C = {k: v for k, v in H["collections"].items() if isinstance(v, list)}
    familias = {nome: densidade(linhas) for nome, linhas in C.items() if linhas}
    julgados = [julga(x, C) for x in CRUZAMENTOS]

    # O vocabulario de problema e a chave que mais falta. Medir o buraco entre
    # o que a fonte JA CITOU e o que foi normalizado e o que separa um pedido
    # de RECOLHA de um pedido de REPROCESSAMENTO (INT-LAW-152).
    citados = set()
    for r in C.get("fieldSignals", []):
        for p in (r.get("PESTS_AND_DISEASES_CITED") or []):
            citados.add(p.strip())
    ids = valores([r for linhas in C.values() for r in linhas], "ISSUE_IDS")

    return dict(
        BUILD_ID=H.get("BUILD_ID"), REFERENCE_DATE=H.get("REFERENCE_DATE"),
        TOTAL_REGISTOS=sum(len(v) for v in C.values()),
        FAMILIAS=familias,
        VOCABULARIO_DE_PROBLEMA=dict(
            ISSUE_IDS_DISTINTOS=len(ids),
            NOMES_CITADOS_EM_TEXTO_LIVRE=len(citados),
            POR_NORMALIZAR=len(citados),
            NOTA="o nome citado ja esta no material recolhido. Falta identidade, "
                 "nao falta fonte.",
        ),
        CRUZAMENTOS=julgados,
    )


def main() -> int:
    m = medir()
    if "--json" in sys.argv:
        print(json.dumps(m, ensure_ascii=False, indent=1))
        return 0
    print(f"PACOTE {m['BUILD_ID']} · referencia {m['REFERENCE_DATE']} · "
          f"{m['TOTAL_REGISTOS']} registos")
    print()
    print(f"{'FAMILIA':28} {'N':>5} {'CROP':>6} {'ISSUE':>6} {'REGIAO':>7} "
          f"{'DATA':>6} {'FONTE':>6}")
    for nome, d in m["FAMILIAS"].items():
        print(f"{nome:28} {d['N']:5} {d['CROP_IDS']:6} {d['ISSUE_IDS']:6} "
              f"{d['REGION_SUBNACIONAL']:7} {d['REFERENCE_DATE']:6} {d['SOURCE_IDS']:6}")
    v = m["VOCABULARIO_DE_PROBLEMA"]
    print()
    print(f"VOCABULARIO DE PROBLEMA · {v['ISSUE_IDS_DISTINTOS']} ISSUE_IDs "
          f"contra {v['NOMES_CITADOS_EM_TEXTO_LIVRE']} nomes citados em texto livre")
    print()
    for c in m["CRUZAMENTOS"]:
        print(f"  {c['CROSSING_STATE']:13} {c['CROSSING_ID']:30} "
              f"{c['A']}({c['N_A']}) x {c['B']}({c['N_B']})")
        print(f"                {c['PERGUNTA']}")
        print(f"                interseccao: {c['INTERSECCAO']}")
        print(f"                linhas que atravessam: {c['LINHAS_QUE_ATRAVESSAM']}")
        for b in c["BLOQUEIO"]:
            print(f"                BLOQUEIO: {b}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
