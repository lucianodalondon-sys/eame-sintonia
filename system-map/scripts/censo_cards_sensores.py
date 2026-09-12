#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O CENSO DOS CARDS E DOS SENSORES — e a matriz entre os dois.

    python3 system-map/scripts/censo_cards_sensores.py

POR QUE ISTO É UM GERADOR E NÃO UM DOCUMENTO ESCRITO À MÃO
-----------------------------------------------------------
Cada número aqui já tem dono noutro sítio: o casco conta as ferramentas, o
censo dos executores conta os executores, o atlas conta as fontes, o ledger
conta as corridas. Escrever esses números à mão num documento criaria um
SEGUNDO dono de cada contagem — e dois donos divergem no dia em que um deles
mede outra vez.

    UM NUMERO COPIADO A MAO E UM NUMERO QUE VAI ENVELHECER EM SILENCIO.

Este ficheiro não mede nada de novo. Ele **junta** o que já foi medido e faz a
única pergunta que ninguém tinha feito de uma vez só:

    QUE CARD PRECISA DE QUE SENSOR, E ATE ONDE O DADO CHEGA?

AS CINCO PROVAS, QUE NÃO SE EMPRESTAM
--------------------------------------
    EXISTE      há ficheiro
    CORRE       é chamável sem rede/pago/produção
    RODOU       deixou rastro de execução
    PRODUZIU    o rastro tem saída
    ENTROU      a saída atravessou a cadeia canónica

Um `YES` numa não empresta `YES` à seguinte. O censo dos executores já separa
as duas primeiras; o ledger de execução separa a terceira; o ledger de fluxo a
quarta; e a fronteira da coleta a quinta.

SAIDA: data/derivados/MATRIZ-CARDS-SENSORES-V1.json
"""
import json
import os
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DADOS = os.path.join(RAIZ, "system-map", "data")
SAIDA = os.path.join(RAIZ, "data", "derivados", "MATRIZ-CARDS-SENSORES-V1.json")


def ler(nome):
    with open(os.path.join(DADOS, nome), encoding="utf-8") as f:
        return json.load(f)


def head():
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=RAIZ,
                              capture_output=True, text=True).stdout.strip()
    except Exception:                                        # noqa: BLE001
        return "NAO SEI"


# ─────────────────────────────────────────────────────────────────────────
# 1 · OS CARDS — as ferramentas do casco, e só elas
#
# ⚠️ «CARD» TEM TRES SIGNIFICADOS NESTA ARVORE, e confundi-los foi o primeiro
# risco desta missão:
#
#     1. as PEÇAS do System Map        `censo_da_topologia.py` chama-lhes
#                                      `CARD_ID`. São módulos de arquitetura.
#     2. as FERRAMENTAS do portal      as onze telas com contrato de bloco.
#     3. os blocos VISUAIS             marcação sem contrato de dados.
#
# O censo mede a espécie 2: é a única que tem contrato, consumidor e pergunta
# de negócio. A 1 é o mapa do código e já tem censo próprio; a 3 é marcação.
# ─────────────────────────────────────────────────────────────────────────
def cards():
    casco = ler("casco.generated.json")
    fora = []
    for f in casco["FERRAMENTAS"]:
        camadas = f.get("camadas") or {}
        tipos = sorted({c.get("tipo") for c in camadas.values() if isinstance(c, dict)})
        fora.append({
            "CARD_ID": f.get("vista"),
            "NOME": f.get("nome"),
            "ESPECIE": "COLLECTION_CONTRACT" if f.get("de_onde_vem") == "REAL"
                       else ("UNKNOWN" if f.get("de_onde_vem") == "NAO SEI"
                             else "INTELLIGENCE_OUTPUT"),
            "DE_ONDE_VEM": f.get("de_onde_vem"),
            "CAMADAS": sorted(camadas),
            "TIPOS_DE_CAMADA": tipos,
            "REGISTOS_CITADOS": f.get("registos_citados") or [],
            "FICHEIROS": f.get("ficheiros") or [],
            "RISCOS": len(f.get("riscos") or []),
            "PERGUNTAS_ABERTAS": len(f.get("perguntas_abertas") or []),
            "CONFISSOES": len(f.get("confissoes") or []),
            # ESTADO não é opinião: sai da mistura de camadas medida.
            "ESTADO": estado_do_card(camadas, tipos, f.get("confissoes") or []),
        })
    return fora


def estado_do_card(camadas, tipos, confissoes):
    """De onde vem o que a tela mostra — e o degrau onde a prova acaba.

    ⚠️ ESTA ESCADA JÁ ESTEVE ERRADA, e o erro era do tipo que este censo
    existe para não cometer. A primeira versão terminava em
    `else ALIMENTADO_POR_REAL`, o que dava «real» a qualquer tela cujas
    camadas não fossem fixture — INCLUSIVE às que citam uma camada que
    ninguém classificou. O Polso di Mercato saía REAL por ITALY_MARKET, uma
    camada de tipo `NAO SEI`.

        UM `else` NO FIM DE UMA ESCADA DE PROVA INVENTA A PROVA QUE FALTA.

    O degrau `NAO_SEI_SE_E_REAL` existe para que a ausência de prova tenha
    nome próprio em vez de ser absorvida pelo caso mais favorável. E a
    confissão do contrato («100% legacy fixture») pesa como fixture, porque
    o contrato sabe mais sobre a tela do que a minha contagem de nomes.
    """
    efetivos = set(tipos) | ({"FIXTURE"} if confissoes else set())
    if not camadas and not confissoes:
        return "SEM_FONTE_DECLARADA"
    if efetivos == {"FIXTURE"}:
        return "ALIMENTADO_POR_FIXTURE"
    if "FIXTURE" in efetivos:
        return "MISTURA_REAL_E_FIXTURE"
    if "NAO SEI" in efetivos:
        return "NAO_SEI_SE_E_REAL"
    return "ALIMENTADO_POR_REAL"


# ─────────────────────────────────────────────────────────────────────────
# 2 · OS SENSORES — tudo o que observa uma fonte e entrega evidência
#
# «Sensor» aqui NÃO é o que tem `sensor` no nome. São dois ficheiros só
# (`regras/sensor_*.py`) e seriam uma resposta errada. A espécie certa é o
# EXECUTOR: quem vai à fonte e traz. O censo dos executores já os enumera e já
# separa CAN RUN de DID RUN.
# ─────────────────────────────────────────────────────────────────────────
def sensores(fronteira):
    ex = ler("executores.generated.json")
    provas = ler("provas-de-execucao.json")["PROVADOS"]
    fluxo = ler("fluxo.generated.json")
    # QUINTA PROVA — «ENTROU NA CADEIA»: a saida atravessou a fronteira
    # canonica (COL-LAW-043, a Sala de Espera). Ela NAO se deduz da quarta.
    #
    # Esta e a unica das cinco que nao se mede por sensor, e a razao e um
    # facto e nao uma limitacao minha: o ledger de fluxo diz
    # `POR_EXECUTOR = NOT_INSTRUMENTED` — ele guarda a observacao e nao quem
    # a produziu. Perguntar «este sensor entrou na cadeia?» a este ledger nao
    # tem resposta possivel.
    #
    # O que SE mede e o degrau em si: o destino da fronteira nao existe e
    # nao tem consumidor. Logo nenhuma saida atravessou — e isso vale para
    # os 58 de uma vez, por medicao da fronteira e nao por cada sensor.
    #
    # ⚠️ ESTA LINHA JA EXIGIU CONSUMIDOR, e isso tornava a prova impossivel de
    # passar enquanto a arquitetura estivesse CERTA:
    #
    #     atravessou = bool(DESTINO_EXISTE) and bool(CONSUMIDORES)
    #
    # `READY CONSUMER = 0` e o alvo de fechamento declarado (know-how, seccao
    # 24). Com o `and`, `ENTROU` so subia acima de zero no dia em que alguem
    # violasse a fronteira.
    #
    #     UMA MEDIDA QUE NAO CONSEGUE REPORTAR SUCESSO QUANDO O SISTEMA ESTA
    #     CORRECTO ESTA PARTIDA, INDEPENDENTEMENTE DO SISTEMA.
    #
    # ENTROU pergunta «a saida ATRAVESSOU a fronteira», e atravessar e sair —
    # nao e ser apanhada do outro lado. Mede-se producao.
    atravessou = bool(fronteira["READY_PRODUZIDO"])
    porque = ("a fronteira %s nunca produziu um READY: o destino declarado nao "
              "existe nesta arvore" % fronteira["LEI"]) if not atravessou else None
    fora = []
    for e in ex["EXECUTORES"]:
        cam = e.get("EXECUTOR_ID") or ""
        p = provas.get(cam) or {}
        fora.append({
            "SENSOR_ID": cam,
            "GAVETA": e.get("GAVETA"),
            "PAPEIS": e.get("PAPEIS") or [],
            "ESTADO_DE_INSTRUMENTACAO": e.get("STATE"),
            # AS CINCO PROVAS, SEPARADAS
            "EXISTE": True,
            "CORRE_OFFLINE": bool(e.get("CAN_RUN_OFFLINE")),
            "REDE": bool(e.get("NETWORK_REQUIRED")),
            "PAGO": bool(e.get("PAID")),
            "PRODUCAO": bool(e.get("PRODUCTION_REQUIRED")),
            "RODOU_COM_PROVA": bool(p),
            "PRODUZIU": (p.get("ETAPAS_OBSERVADAS") or []) if p else [],
            "PROVA": p.get("PROVA") if p else None,
            "MODO": p.get("EXECUTION_MODE") if p else None,
            "TEM_PORTA": bool(e.get("TEM_PORTA")),
            "USA_CONTRATO_ARTEFATO": bool(e.get("USA_CONTRATO_ARTEFATO")),
            "USA_TELEMETRIA": bool(e.get("USA_TELEMETRIA")),
            "ENTROU_NA_CADEIA": atravessou,
            "PORQUE_NAO_ENTROU": porque,
        })
    return fora, fluxo


# ─────────────────────────────────────────────────────────────────────────
# 3 · A MATRIZ — e a razão de ela ser pequena
#
# Uma matriz card × sensor com 11 × 58 células daria 638 entradas e a sensação
# de um mapa. Seria falsa: as arestas que EXISTEM são as que o contrato de
# bloco declara, e elas apontam para CAMADAS do portal — nunca para um
# executor. Essa é a descoberta, e a matriz tem de a mostrar em vez de a
# esconder atrás de células vazias.
#
#     CARD -> CAMADA DO PORTAL -> (quem a produz?) -> SENSOR
#                                  ^
#                                  aqui a corrente parte
# ─────────────────────────────────────────────────────────────────────────
def matriz(cs, geradores):
    fora = []
    for c in cs:
        for camada in c["CAMADAS"] or ["(nenhuma)"]:
            g = geradores.get(camada)
            fora.append({
                "CARD_ID": c["CARD_ID"],
                "CAMADA": camada,
                "GERADOR_NO_REPO": g,
                # A CLASSIFICAÇÃO DA ARESTA, e ela não é generosa.
                "ARESTA": ("MISSING" if camada == "(nenhuma)"
                           else "PROVEN" if g
                           else "BROKEN"),
                "PORQUE": ("o card nao declara camada nenhuma"
                           if camada == "(nenhuma)"
                           else "a camada tem gerador versionado nesta arvore"
                           if g else
                           "a camada e um ficheiro COMMITADO sem gerador nesta "
                           "arvore: nenhum sensor a reescreve"),
            })
    return fora


def geradores_das_camadas():
    """Quem, NESTA árvore, escreve cada camada do portal.

    ⚠️ Procura-se quem ESCREVE, e não quem MENCIONA. `harness.mjs` e
    `checks.mjs` citam todas as camadas — eles AUDITAM-nas. Contar uma
    auditoria como geração diria que o ficheiro é reescrito quando ele só é
    lido, e a matriz inteira ficaria verde por causa do auditor.
    """
    casco = ler("casco.generated.json")
    fora = {}
    for camada, ficheiros in casco["CAMADAS_PUBLICADAS"].items():
        dono = None
        for f in ficheiros:
            base = os.path.basename(f)
            r = subprocess.run(
                ["grep", "-rIl", "--include=*.py", "--include=*.mjs",
                 "--include=*.sh", base, "superficie", "coleta", "guarda",
                 "motor", "orquestrador", "medidas", "regras"],
                cwd=RAIZ, capture_output=True, text=True)
            achados = [x for x in r.stdout.split() if x]
            # Um gerador ESCREVE. Procura-se a escrita, e não a mencao.
            for a in achados:
                try:
                    corpo = open(os.path.join(RAIZ, a), encoding="utf-8",
                                 errors="ignore").read()
                except OSError:
                    continue
                if base in corpo and ("write_text" in corpo or "open(" in corpo
                                      or "writeFileSync" in corpo):
                    dono = a
                    break
            if dono:
                break
        fora[camada] = dono
    return fora


def main():
    casco = ler("casco.generated.json")
    ex = ler("executores.generated.json")
    fontes = ler("sources.generated.json")
    fronteira = ler("fronteira.observada.json")
    congel = ler("congelamento.generated.json")
    issues = ler("SYSTEM-MAP-COLLECTION-ISSUES.json")

    cs = cards()
    ss, fluxo = sensores(fronteira)
    ger = geradores_das_camadas()
    mx = matriz(cs, ger)

    d = {
        "SCHEMA": "sintonia.censo-cards-sensores/1",
        "O_QUE_ISTO_E": (
            "A matriz CARD x SENSOR do SINTONIA, montada a partir dos censos "
            "que ja existem. Nenhum numero e medido aqui: cada um tem dono "
            "noutro ficheiro, e este junta-os para fazer a pergunta que "
            "nenhum deles fazia sozinho."),
        "PROVENANCE": {
            "HEAD": head(),
            "LIDO_DE": ["casco.generated.json", "executores.generated.json",
                        "sources.generated.json", "fluxo.generated.json",
                        "fronteira.observada.json",
                        "congelamento.generated.json",
                        "provas-de-execucao.json",
                        "SYSTEM-MAP-COLLECTION-ISSUES.json"],
        },
        "CONTAGENS": {
            "CARDS_TOTAL": len(cs),
            "CARDS_POR_ESTADO": _contar(cs, "ESTADO"),
            "CARDS_POR_ORIGEM": casco["COUNTS"]["por_origem"],
            "SENSORES_TOTAL": len(ss),
            "SENSORES_POR_INSTRUMENTACAO": ex["POR_ESTADO"],
            "SENSORES_COM_CORRIDA_PROVADA": sum(1 for s in ss if s["RODOU_COM_PROVA"]),
            "SENSORES_QUE_CORREM_OFFLINE": sum(1 for s in ss if s["CORRE_OFFLINE"]),
            "FONTES_NO_ATLAS": fontes["COUNTS"]["sources"],
            "FONTES_COM_CONTRATO": fontes["COUNTS"]["with_contract"],
            "FONTES_JA_COLETADAS": fontes["COUNTS"]["fontes_ja_coletadas"],
            "FONTES_NUNCA_COLETADAS": fontes["COUNTS"]["fontes_nunca_coletadas"],
            "FONTES_POR_PAIS": fontes["COUNTS"]["by_country"],
            "CORRIDAS_NO_LEDGER": len(fluxo["POR_CORRIDA"]),
            "OBSERVACOES_NO_LEDGER": fluxo["OBSERVACOES"],
            "OBSERVACOES_POR_FONTE": fluxo["POR_FONTE"],
            "ARTEFATOS_DE_INTELIGENCIA_CONGELADOS":
                len(congel["FROZEN_INTELLIGENCE_ARTIFACTS"]),
            "CAMADAS_DO_PORTAL": len(ger),
            "CAMADAS_COM_GERADOR": sum(1 for g in ger.values() if g),
            "ARESTAS_POR_CLASSE": _contar(mx, "ARESTA"),
            "ISSUES_DA_COLETA": issues["COUNTS"],
        },
        # AS CINCO PROVAS, uma por degrau, e o numero que sobreviveu a cada
        # uma. Nenhum degrau empresta o seu YES ao seguinte: e por isso que
        # isto e uma escada com cinco numeros e nao um so.
        "AS_CINCO_PROVAS": [
            {"PROVA": "EXISTE", "PERGUNTA": "ha ficheiro?",
             "SENSORES": sum(1 for s in ss if s["EXISTE"]),
             "MEDIDO_POR": "system-map/data/executores.generated.json"},
            {"PROVA": "CORRE", "PERGUNTA": "e chamavel sem rede, sem pago, sem producao?",
             "SENSORES": sum(1 for s in ss if s["CORRE_OFFLINE"]),
             "MEDIDO_POR": "system-map/data/executores.generated.json"},
            {"PROVA": "RODOU", "PERGUNTA": "deixou rastro de execucao?",
             "SENSORES": sum(1 for s in ss if s["RODOU_COM_PROVA"]),
             "MEDIDO_POR": "system-map/data/provas-de-execucao.json"},
            {"PROVA": "PRODUZIU", "PERGUNTA": "o rastro tem saida com etapa observada?",
             "SENSORES": sum(1 for s in ss if s["PRODUZIU"]),
             "MEDIDO_POR": "system-map/data/provas-de-execucao.json"},
            {"PROVA": "ENTROU", "PERGUNTA": "a saida atravessou a fronteira canonica?",
             "SENSORES": sum(1 for s in ss if s["ENTROU_NA_CADEIA"]),
             "MEDIDO_POR": "system-map/data/fronteira.observada.json"},
        ],
        "A_FRONTEIRA": {
            "CONTRATO": fronteira["LEI"],
            "DONO": fronteira["DONO"],
            "PRODUTORES_EM_RUNTIME": fronteira["PRODUTORES_EM_RUNTIME"],
            "CONSUMIDORES": fronteira["CONSUMIDORES"],
            "DESTINO_EXISTE": fronteira["DESTINO_EXISTE"],
            "READY_PRODUZIDO": fronteira["READY_PRODUZIDO"],
            "GAP": fronteira["GAP"],
        },
        "CARDS": cs,
        "SENSORES": ss,
        "MATRIZ": mx,
        "GERADORES_DAS_CAMADAS": ger,
    }
    os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
    with open(SAIDA, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("=== CENSO CARDS x SENSORES ===")
    for pr in d["AS_CINCO_PROVAS"]:
        print("  %-10s %-52s %s" % (pr["PROVA"], pr["PERGUNTA"], pr["SENSORES"]))
    print()
    for k, v in d["CONTAGENS"].items():
        print("  %-42s %s" % (k, json.dumps(v, ensure_ascii=False)[:78]))
    print("\n  escrito em %s" % os.path.relpath(SAIDA, RAIZ))
    return 0


def _contar(lista, campo):
    fora = {}
    for x in lista:
        fora[x[campo]] = fora.get(x[campo], 0) + 1
    return dict(sorted(fora.items()))


if __name__ == "__main__":
    sys.exit(main())
