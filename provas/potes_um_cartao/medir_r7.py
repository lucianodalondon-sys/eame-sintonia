#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MEDICAO R7 da D125 (POTES-UM-CARTAO) sobre os dados do REPO — sem rede, sem Sala, sem livro vivo.

    python3 provas/potes_um_cartao/medir_r7.py            # escreve provas/potes_um_cartao/MEDICAO-R7.json

Dois insumos commitados, duas perguntas:
  A. docs/intelligence/r7/POTE-R7-PUBLICADO.json (o pote da R7 que foi publicado; origem
     origin/claude/casco-r7-publication-yb7nsg @60ee56b2 docs/casco/r7/POTE-R7.json):
     quantos LUGARES e quantos CARTOES? quantas copias no Arquivo? — so MEDICAO de identidade: a lei v2 de hoje
     ja nao aprova este pote (formato anterior ao contrato unico), e isso fica dito (V2_HOJE_VIOLACOES).
  B. motor/cruzamentos_max.py sobre docs/intelligence/r7/ANALISE-R7.json + a referencia pela porta:
     quantos objetos POR LINK (antes) e quantas PERGUNTAS (depois)? OLIVO x mosca da oliveira?
"""
import json
import os
import sys
from collections import Counter
from datetime import date

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401
import pote_intelligence_casco as P      # noqa: E402
import identidade_do_cruzamento as IDENT  # noqa: E402
import cruzamentos_max as XM             # noqa: E402

PUBLICADO = os.path.join(RAIZ, "docs", "intelligence", "r7", "POTE-R7-PUBLICADO.json")
SAIDA = os.path.join(RAIZ, "provas", "potes_um_cartao", "MEDICAO-R7.json")


def medir():
    b = open(PUBLICADO, "rb").read()
    v2 = json.loads(b)
    lugares = [(k, o["OBJETO_ID"]) for k, e in v2["COMPARTIMENTOS"].items() for o in e["OBJETOS"]]
    v21 = P.v21_do_v2(v2, conferir=False)
    arq = v21["COMPARTIMENTOS"]["archive"]["IDS"]
    fora = {i for k, e in v21["COMPARTIMENTOS"].items() if k != "archive" for i in e["IDS"]}
    x = [c for c in v21["CARTOES"].values() if c["ESPECIE"] == "CROSSING"]
    a = {"INSUMO": os.path.relpath(PUBLICADO, RAIZ), "SHA256": IDENT.impressao_do_pote(b),
         "INTELLIGENCE_RUN_ID": v2["INTELLIGENCE_RUN_ID"],
         "V2_HOJE_VIOLACOES": len(P.conferir_pote(v2)),
         "ANTES": {"OBJETOS_NOS_COMPARTIMENTOS": len(lugares), "IDS_DISTINTOS": len({i for _, i in lugares}),
                   "ARQUIVO_OBJETOS": len(v2["COMPARTIMENTOS"]["archive"]["OBJETOS"]),
                   "ARQUIVO_COPIAS_DE_OUTRO_COMPARTIMENTO": sum(1 for o in v2["COMPARTIMENTOS"]["archive"]["OBJETOS"]
                                                                if any(o["OBJETO_ID"] == i for k, i in lugares if k != "archive"))},
         "DEPOIS": {"CARTOES": len(v21["CARTOES"]), "LUGARES_POR_ID": v21["CONTAGEM_DE_CARTOES"]["LUGARES_NOS_COMPARTIMENTOS"],
                    "ARQUIVO_IDS": len(arq), "ARQUIVO_COPIAS": 0 if not any("OBJETOS" in e for e in v21["COMPARTIMENTOS"].values()) else "HA",
                    "ARQUIVO_IDS_QUE_TAMBEM_ESTAO_NOUTRO_POTE": sum(1 for i in arq if i in fora),
                    "POR_PREFIXO": dict(Counter(k.split("-")[0] for k in v21["CARTOES"])),
                    "PERGUNTAS_CROSSING": [{"ID": c["OBJETO_ID"], "CROSSING_KEY": c["CROSSING_KEY"], "GRUPO": c.get("GRUPO"),
                                            "ALIAS": c["ALIAS"]} for c in x],
                    "IDENTIDADE_ESTAVEL_EM_2_LEITURAS": sorted(P.v21_do_v2(json.loads(b), conferir=False)["CARTOES"]) == sorted(v21["CARTOES"])}}
    with open(XM.SAIDA, encoding="utf-8") as f:
        hoje = date.fromisoformat(json.load(f)["REFERENCIA_ADAMA"]["HOJE"])
    out = XM.correr(hoje=hoje)
    ref = XM.Referencia.da_porta(__import__("porta_da_referencia").abrir(hoje=hoje))
    res = XM.analisar(json.load(open(XM.R7, encoding="utf-8")), ref)
    por_link = XM._objetos_por_link(res, ref)["portfolio"]
    cart = out["_ITENS"]["portfolio"]
    mosca = [c for c in cart if c["CROSSING_KEY"].endswith("CROP=CROP:OLIVO|TARGET=PEST:MOSCA_OLIVO")]
    folpet = [c for c in cart if c["CROSSING_KEY"].endswith("AI=AI:FOLPET|CROP=CROP:VITE")]
    b_ = {"INSUMO": "docs/intelligence/r7/ANALISE-R7.json + referencia ADAMA pela porta (HOJE %s)" % hoje.isoformat(),
          "ANTES_OBJETOS_POR_LINK": len(por_link), "DEPOIS_PERGUNTAS": len(cart),
          "POR_FAMILIA": dict(Counter(c["FAMILIA"] for c in cart)),
          "OLIVO_X_MOSCA": {"OBJETOS_ANTES": sum(1 for o in por_link if o.get("CROSSING_KEY") == (mosca[0]["CROSSING_KEY"] if mosca else None)),
                            "CARTOES_DEPOIS": len(mosca), "LINKS": len(mosca[0]["LINKS"]) if mosca else 0,
                            "CONTAGENS": mosca[0]["CONTAGENS"] if mosca else None},
          "FOLPET_X_VITE": {"CARTOES_DEPOIS": len(folpet), "ESTADOS_DOS_LINKS": sorted(l["ESTADO_DO_LINK"] for l in folpet[0]["LINKS"]) if folpet else [],
                            "RESPOSTA": folpet[0]["RESPOSTA"] if folpet else None,
                            "RESPOSTA_DITA_POR": folpet[0]["RESPOSTA_DITA_POR"] if folpet else None},
          "IDS_REPETIDOS_DEPOIS": len(cart) - len({c["OBJETO_ID"] for c in cart}),
          "ALIAS_XMAX_GUARDADOS": sum(len(c["ALIAS"]) for c in cart)}
    return {"MISSAO": "POTES-UM-CARTAO (D125)", "REGRA_DE_IDENTIDADE": IDENT.REGRA, "VOCABULARIO": IDENT.VOCAB.carimbo(),
            "A_POTE_R7_PUBLICADO": a, "B_CRUZAMENTOS_R7_DO_REPO": b_}


def main():
    m = medir()
    with open(SAIDA, "w", encoding="utf-8") as f:
        json.dump(m, f, ensure_ascii=False, indent=1)
        f.write("\n")
    a, b = m["A_POTE_R7_PUBLICADO"], m["B_CRUZAMENTOS_R7_DO_REPO"]
    print("A · POTE-R7 publicado: %d objetos em compartimentos -> %d cartoes; arquivo %d copias -> %d IDs, 0 copias"
          % (a["ANTES"]["OBJETOS_NOS_COMPARTIMENTOS"], a["DEPOIS"]["CARTOES"], a["ANTES"]["ARQUIVO_COPIAS_DE_OUTRO_COMPARTIMENTO"],
             a["DEPOIS"]["ARQUIVO_IDS"]))
    print("B · cruzamentos R7: %d objetos por link -> %d perguntas; OLIVO x mosca %d -> %d; FOLPET x VITE -> %d"
          % (b["ANTES_OBJETOS_POR_LINK"], b["DEPOIS_PERGUNTAS"], b["OLIVO_X_MOSCA"]["OBJETOS_ANTES"],
             b["OLIVO_X_MOSCA"]["CARTOES_DEPOIS"], b["FOLPET_X_VITE"]["CARTOES_DEPOIS"]))
    print("->", os.path.relpath(SAIDA, RAIZ))
    return 0


if __name__ == "__main__":
    sys.exit(main())
