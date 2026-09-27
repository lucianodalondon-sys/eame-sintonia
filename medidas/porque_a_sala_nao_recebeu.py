#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SALA_DELTA = 0 — E A CAUSA DE CADA ITEM, e nao «nao entrou».

    «NAO ENTROU» NAO E UMA CAUSA. E A AUSENCIA DE UMA.

⚠️ ESTE MEDIDOR NAO ESCREVE NADA. Nao promove, nao insere, nao toca na Sala.
Ele faz a pergunta da porta EM SECO, sobre itens montados em memoria, para
responder a uma coisa que so se sabe perguntando:

    SE o texto existisse, os 85 entravam?

Sem esta pergunta, «falta o derivador de HTML» e uma hipotese. Com ela, ou e
a causa unica ou aparece a segunda — e foi o que aconteceu.

O QUE ELE CORRIGE NO MEU PROPRIO RELATORIO
-------------------------------------------
Eu escrevi `DERIVED = NOT_APPLICABLE`. Estava errado, e a diferenca importa:

    NOT_APPLICABLE    a etapa nao e para este material, por contrato
    NOT_IMPLEMENTED   a etapa aplica-se, a capacidade nao existe
    MISSING_ROUTE     a capacidade existe, falta o caminho

A derivacao APLICA-SE a `text/html`: o que ela produz chama-se
`TEXT_EXTRACTED`, a porta exige `texto` para responder `legivel`, e o HTML
tem texto — provado aqui, do disco, sem rede.

SAIDA: medidas/PORQUE-A-SALA-NAO-RECEBEU-V1.json
"""

from __future__ import annotations

import json
import os
import sys
from collections import Counter

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)

import _gavetas  # noqa: E402,F401
import admissao as adm  # noqa: E402
from coleta.texto_fonte import limpar  # noqa: E402

SAIDA = os.path.join(RAIZ, "medidas", "PORQUE-A-SALA-NAO-RECEBEU-V1.json")
COORTE = os.path.join(RAIZ, "medidas", "COORTE-MICRO-COLLECTION-V1.json")


def universo_da_fonte(source_id):
    """`IT-T10-018` -> `T10`. O universo esta no proprio SOURCE_ID."""
    partes = str(source_id or "").split("-")
    return partes[1] if len(partes) > 1 else ""


def ha_regua(universo):
    """A porta tem regua para este universo? → (bool, quais existem)

    ⚠️ ESTA PERGUNTA NAO E RETORICA. `admissao.PERGUNTAS_DO_UNIVERSO` conhece
    CINCO universos, e os alvos da casa sao treze. Um universo sem regua nao
    e recusado: e respondido `NAO_SE_APLICA` com toda a educacao — e essa
    educacao esconde que ninguem escreveu a pergunta.
    """
    reguas = getattr(adm, "PERGUNTAS_DO_UNIVERSO", {}) or {}
    return universo in reguas, sorted(reguas)


def medir():
    with open(COORTE, encoding="utf-8") as fh:
        coorte = json.load(fh)
    itens = [l for l in coorte["ITENS"] if l["CORRIDA"] == "RUN1C"]

    _, reguas = ha_regua("T0")
    fora, causas = [], Counter()

    for l in itens:
        u = universo_da_fonte(l["SOURCE_ID"])
        tem_regua, _ = ha_regua(u)
        caminho = os.path.join(RAIZ, l["LOCAL_FILE"]) if l["LOCAL_FILE"] else None

        # ── 1 · o texto que o derivador em falta teria produzido ───────────
        texto, erro_texto = "", None
        if caminho and os.path.isfile(caminho):
            try:
                texto = limpar(open(caminho, "rb").read(), "text/html")
            except Exception as ex:                             # noqa: BLE001
                erro_texto = "%s: %s" % (type(ex).__name__, ex)

        # ── 2 · o item COMO A PORTA O RECEBEU DE VERDADE (sem texto) ───────
        # Reproduz o que aconteceu: artifact_type RAW, sem `texto`.
        real = {"artifact_type": "RAW", "source_id": l["SOURCE_ID"],
                "id": "obs:%s" % l["RAW_ASSET_ID"],
                "raw_asset_id": l["RAW_ASSET_ID"],
                "url": l["DETAIL_URL"], "captured_at": l["CAPTURED_AT"]
                if "CAPTURED_AT" in l else None}

        # ── 3 · o MESMO item, se o derivador existisse ─────────────────────
        hipotetico = dict(real, texto=texto)

        resultado_real = perguntar(real, u)
        resultado_hip = perguntar(hipotetico, u)

        # ── 4 · a causa, em duas camadas ───────────────────────────────────
        # ⚠️ A CAUSA PROXIMA NAO E A CAUSA RAIZ, e reportar so a proxima manda
        # quem le consertar o sitio errado.
        proxima = "ADMISSION_%s" % resultado_real["resultado"]
        if not tem_regua:
            raiz = "NO_ADMISSION_RULE_FOR_UNIVERSE"
        elif not texto and not erro_texto:
            raiz = "MISSING_ROUTE"      # ha extractor na arvore, falta o executor
        elif erro_texto:
            raiz = "FAILED"
        else:
            raiz = "MISSING_ROUTE"
        causas[(proxima, raiz)] += 1

        fora.append({
            "RUN_ID": l["RUN_ID"], "OBSERVATION_ID": l["OBSERVATION_ID"],
            "SOURCE_ID": l["SOURCE_ID"], "UNIVERSO": u,
            "RAW_ASSET_ID": l["RAW_ASSET_ID"],
            "STORAGE_OBJECT_ID": l["STORAGE_OBJECT_ID"],
            "DERIVED_ID": None, "DERIVED_PORQUE": "N/A — nenhum executor de "
                                                  "derivacao declara text/html",
            "SHA256": l["SHA256"], "MATERIAL_CLASS": "text/html",
            "UNIVERSO_TEM_REGUA": tem_regua,
            "TEXTO_EXTRAIVEL_CARACTERES": len(texto),
            "ERRO_A_EXTRAIR": erro_texto,
            "ADMISSION_REAL": resultado_real,
            "ADMISSION_SE_HOUVESSE_DERIVADOR": resultado_hip,
            "CAUSA_PROXIMA": proxima,
            "CAUSA_RAIZ": raiz,
        })

    return {
        "MEDIDOR": "medidas/porque_a_sala_nao_recebeu.py",
        "ESCREVE_ALGUMA_COISA": False,
        "REDE": "nenhuma — os bytes vem do disco e limpar() nao abre ligacao",
        "REGUAS_QUE_A_PORTA_TEM": reguas,
        "POPULACAO": len(fora),
        "PARETO_DAS_CAUSAS": [
            {"CAUSA_PROXIMA": k[0], "CAUSA_RAIZ": k[1], "ITENS": v}
            for k, v in causas.most_common()],
        "TEXTO_EXTRAIVEL": {
            "ITENS_COM_TEXTO": sum(1 for f in fora if f["TEXTO_EXTRAIVEL_CARACTERES"] > 0),
            "ITENS_SEM_TEXTO": sum(1 for f in fora if f["TEXTO_EXTRAIVEL_CARACTERES"] == 0),
            "CARACTERES_MEDIOS": (sum(f["TEXTO_EXTRAIVEL_CARACTERES"] for f in fora)
                                  // max(1, len(fora))),
            "PORQUE_ISTO_IMPORTA": "se da para extrair texto destes bytes com "
                                   "codigo que ja esta na arvore e sem rede, "
                                   "entao a derivacao APLICA-SE e a etiqueta "
                                   "NOT_APPLICABLE estava errada",
        },
        "SE_HOUVESSE_DERIVADOR": dict(Counter(
            f["ADMISSION_SE_HOUVESSE_DERIVADOR"]["resultado"] for f in fora)),
        "COMO_ESTA_HOJE": dict(Counter(f["ADMISSION_REAL"]["resultado"] for f in fora)),
        "ITENS": fora,
    }


def perguntar(item, universo):
    """A porta INTEIRA, em seco — `admissao.decidir`, o dono unico da regra.

    ⚠️ A PRIMEIRA VERSAO DESTA FUNCAO CHAMAVA SO OS PORTOES DO ESTAGIO, e
    dava `SIM 85` num sitio onde a porta de verdade nao da. Faltava-lhe o
    ultimo degrau — `_do_universo` — que e precisamente onde os 39 itens de
    T10 batem, porque nao ha regua escrita para T10.

        UMA SIMULACAO QUE SALTA UM DEGRAU NAO SIMULA A PORTA:
        SIMULA A PARTE DA PORTA QUE EU JA SABIA RESPONDER.

    Chama-se agora o dono unico. Uma segunda regua escrita aqui seria o
    defeito que esta casa ja nomeou.
    """
    d = adm.decidir(item, universo, corrida="SECO-NAO-ESCREVE")
    return {"estagio": (d.evidencia or {}).get("estagio"),
            "portao": d.regra, "resultado": d.resultado,
            "motivo": str(d.motivo)[:170]}


def main(argv):
    r = medir()
    with open(SAIDA, "w", encoding="utf-8") as fh:
        json.dump(r, fh, indent=1, ensure_ascii=False)
    print("REGUAS QUE A PORTA TEM :", r["REGUAS_QUE_A_PORTA_TEM"])
    print("POPULACAO              :", r["POPULACAO"])
    print("COMO ESTA HOJE         :", r["COMO_ESTA_HOJE"])
    print("SE HOUVESSE DERIVADOR  :", r["SE_HOUVESSE_DERIVADOR"])
    print("TEXTO EXTRAIVEL        :", {k: v for k, v in r["TEXTO_EXTRAIVEL"].items()
                                       if k != "PORQUE_ISTO_IMPORTA"})
    print("\nPARETO DAS CAUSAS:")
    for c in r["PARETO_DAS_CAUSAS"]:
        print("  %-24s <- %-32s %3d" % (c["CAUSA_PROXIMA"], c["CAUSA_RAIZ"], c["ITENS"]))
    print("\n  escrito: medidas/PORQUE-A-SALA-NAO-RECEBEU-V1.json")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
