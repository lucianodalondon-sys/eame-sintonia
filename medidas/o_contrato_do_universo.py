#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O CONTRATO DE UM UNIVERSO — descoberto nos que já existem, não inventado.

    NÃO HÁ REGRA ESCRITA DO QUE CONTA COMO «T10».
    SEM REGRA, ESTA PORTA NÃO INVENTA UMA.

Era isto que `admissao/admissao.py` respondia a 39 documentos italianos reais,
e era a resposta CERTA para a pergunta errada: ninguém tinha escrito a
pergunta. Este medidor responde a três coisas, antes de alguém escrever régua
nenhuma:

    T10_REQUIRED_FIELDS    que campos uma régua de universo precisa de ler
    T10_AVAILABLE_FIELDS   que campos os 39 itens reais trazem de verdade
    T10_MISSING_FIELDS     a diferença — e ela não se preenche para melhorar
                           a estatística

E separa as duas famílias de critério, que nesta porta são de donos
diferentes:

    UNIVERSAL   os portões do ESTÁGIO (`legivel`, `origem`, `linhagem`,
                `identidade`). São os mesmos para T3, T4, T5, T7, T9 e T10, e
                não dependem de universo nenhum.
    ESPECIFICO  o léxico de `PERGUNTAS_DO_UNIVERSO[universo]`, lido por
                `_do_universo` com a régua dos `SINAIS_MINIMOS`.

⚠️ ESTE MEDIDOR NÃO ESCREVE NADA NA SALA. Ele monta os itens em memória, com o
texto que o derivador de HTML produz dos bytes que já estão no disco, e faz a
pergunta ao DONO ÚNICO — `admissao.decidir`. Uma segunda régua escrita aqui
seria o defeito que esta casa já nomeou.

E mede o EFEITO COLATERAL, que é real e tem de aparecer: `_do_universo`
percorre TODOS os universos quando não acha nenhum do pedido — logo acrescentar
T10 pode mudar a resposta de um item de T7 ou T5, de `NAO_SEI` para `NAO`.

    UMA RÉGUA NOVA NÃO MUDA SÓ O UNIVERSO DELA.

SAIDA: medidas/O-CONTRATO-DO-UNIVERSO-V1.json
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
import territorios as terr  # noqa: E402
from coleta.texto_fonte import limpar  # noqa: E402

SAIDA = os.path.join(RAIZ, "medidas", "O-CONTRATO-DO-UNIVERSO-V1.json")
COORTE = os.path.join(RAIZ, "medidas", "COORTE-MICRO-COLLECTION-V1.json")

#: Os campos que `_do_universo` junta antes de procurar as palavras. Lidos da
#: função — se ela mudar, este medidor tem de ser mudado à mão, e isso é
#: melhor do que um medidor que concorda consigo próprio para sempre.
CAMPOS_DO_UNIVERSO = ("texto", "title", "nome", "topics", "crops", "resumo")


def universo_da_fonte(source_id):
    """`IT-T10-018` -> `T10`. O universo está no próprio SOURCE_ID."""
    partes = str(source_id or "").split("-")
    return partes[1] if len(partes) > 1 else ""


def o_texto_do_disco(caminho_relativo):
    """O texto que o derivador de HTML produz. Do disco, e sem rede."""
    caminho = os.path.join(RAIZ, caminho_relativo or "")
    if not caminho_relativo or not os.path.isfile(caminho):
        return None
    with open(caminho, "rb") as fh:
        return limpar(fh.read(), "text/html")


def item_de(linha, texto):
    """O item como a rota canónica o entrega à porta, e nada mais."""
    # ⚠️ `parent_sha256` NÃO É DECORAÇÃO DO MEDIDOR: sem ele o portão
    # `linhagem` responde `NAO_SEI` a TODOS os 85 e o universo nunca chega a
    # ser perguntado. A primeira corrida deste medidor deu exactamente isso —
    # 85 `NAO_SEI` por `linhagem` — e o número mede o medidor, não a porta.
    #
    #     UM ITEM MAL MONTADO PARA A PORTA MEDE QUEM O MONTOU.
    #
    # O valor é o `sha256` do BRUTO, que é o que a rota canónica lá põe
    # (`derived_artifact.parent_sha256`, lido da linha que o dono escreveu).
    item = {"artifact_type": "DERIVED",
            "source_id": linha["SOURCE_ID"],
            "id": "obs:%s" % linha["RAW_ASSET_ID"],
            "raw_asset_id": linha["RAW_ASSET_ID"],
            "parent_sha256": linha.get("SHA256"),
            "url": linha["DETAIL_URL"],
            "captured_at": linha.get("CAPTURED_AT")}
    if texto is not None:
        item["texto"] = texto
    return item


def medir():
    with open(COORTE, encoding="utf-8") as fh:
        itens = [l for l in json.load(fh)["ITENS"] if l["CORRIDA"] == "RUN1C"]

    reguas = dict(adm.PERGUNTAS_DO_UNIVERSO)
    universais = [n for n, _ in adm.perguntas_do_estagio(adm.DOCUMENTO)]

    fora, por_universo = [], Counter()
    campos_presentes = Counter()
    for l in itens:
        u = universo_da_fonte(l["SOURCE_ID"])
        texto = o_texto_do_disco(l.get("LOCAL_FILE"))
        item = item_de(l, texto)
        for c in CAMPOS_DO_UNIVERSO:
            if str(item.get(c) or "").strip():
                campos_presentes["%s|%s" % (u, c)] += 1
        d = adm.decidir(item, u, corrida="SECO-CONTRATO-DO-UNIVERSO")
        ev = d.evidencia or {}
        por_universo[(u, d.resultado)] += 1
        fora.append({
            "RAW_ASSET_ID": l["RAW_ASSET_ID"],
            "SOURCE_ID": l["SOURCE_ID"], "UNIVERSO": u,
            "TEM_REGUA": u in reguas,
            "CARACTERES": len(texto or ""),
            "RESULTADO": d.resultado, "REGRA": d.regra,
            "MOTIVO": str(d.motivo)[:200],
            "PALAVRAS": (ev.get("palavras") or [])[:8],
            "SINAIS": ev.get("sinais"),
            "ACHADO_NOUTRO": ev.get("achado_noutro"),
        })

    t10 = [f for f in fora if f["UNIVERSO"] == "T10"]
    disponiveis = sorted({c.split("|")[1] for c in campos_presentes
                          if c.startswith("T10|")})
    return {
        "MEDIDOR": "medidas/o_contrato_do_universo.py",
        "ESCREVE_ALGUMA_COISA": False,
        "REDE": "nenhuma — os bytes vem do disco e limpar() nao abre ligacao",
        "AUTORIDADE_DA_TAXONOMIA": {
            "T10_EXISTE_NO_ATLAS": terr.existe("T10"),
            "T10_E_CANONICO": terr.e_canonico("T10"),
            "T10_NOME": terr.nome("T10"),
            "T10_APELIDOS": sorted(k for k, v in terr.APELIDOS.items()
                                   if v == "T10"),
        },
        "CRITERIOS": {
            "UNIVERSAIS": {
                "QUAIS": universais,
                "DONO": "admissao.perguntas_do_estagio(DOCUMENTO)",
                "PORQUE": ("nao dependem de universo nenhum: sao os mesmos "
                           "para T3, T4, T5, T7, T9 e T10"),
            },
            "ESPECIFICO": {
                "QUAL": "pertence ao universo",
                "DONO": "admissao.PERGUNTAS_DO_UNIVERSO[universo]",
                "REGUA": "SINAIS_MINIMOS = %d termos DISTINTOS"
                         % adm.SINAIS_MINIMOS,
                "UNIVERSOS_COM_REGUA": sorted(reguas),
                "TERMOS_POR_UNIVERSO": {u: len(t) for u, t in
                                        sorted(reguas.items())},
            },
        },
        "T10_REQUIRED_FIELDS": {
            "QUAIS": list(CAMPOS_DO_UNIVERSO),
            "PORQUE": ("sao os campos que `_do_universo` junta antes de "
                       "procurar as palavras. Nenhum e obrigatorio sozinho: "
                       "o que a regua exige e que ALGUM deles traga texto"),
            "MAIS_OS_UNIVERSAIS": universais,
        },
        "T10_AVAILABLE_FIELDS": disponiveis,
        "T10_MISSING_FIELDS": [c for c in CAMPOS_DO_UNIVERSO
                               if c not in disponiveis],
        "T10_POPULACAO": len(t10),
        "POR_UNIVERSO": [{"UNIVERSO": k[0], "RESULTADO": k[1], "ITENS": v}
                         for k, v in sorted(por_universo.items())],
        "TOTAL_POR_RESULTADO": dict(Counter(f["RESULTADO"] for f in fora)),
        "ITENS": fora,
    }


def main(argv):
    r = medir()
    with open(SAIDA, "w", encoding="utf-8") as fh:
        json.dump(r, fh, indent=1, ensure_ascii=False)
    print("UNIVERSOS COM REGUA   :", r["CRITERIOS"]["ESPECIFICO"]
          ["UNIVERSOS_COM_REGUA"])
    print("CRITERIOS UNIVERSAIS  :", r["CRITERIOS"]["UNIVERSAIS"]["QUAIS"])
    print("T10_REQUIRED_FIELDS   :", r["T10_REQUIRED_FIELDS"]["QUAIS"])
    print("T10_AVAILABLE_FIELDS  :", r["T10_AVAILABLE_FIELDS"])
    print("T10_MISSING_FIELDS    :", r["T10_MISSING_FIELDS"])
    print("TOTAL POR RESULTADO   :", r["TOTAL_POR_RESULTADO"])
    print("\nPOR UNIVERSO:")
    for x in r["POR_UNIVERSO"]:
        print("  %-4s %-14s %3d" % (x["UNIVERSO"], x["RESULTADO"], x["ITENS"]))
    print("\n  escrito: medidas/O-CONTRATO-DO-UNIVERSO-V1.json")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
