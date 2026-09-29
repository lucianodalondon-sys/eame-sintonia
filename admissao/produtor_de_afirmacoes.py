#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O PRODUTOR DE AFIRMACOES — o comando que corre a lei sobre uma cópia da Sala (D158).

    py admissao/produtor_de_afirmacoes.py <SALA_ATUAL.json> <SAIDA.json> [--item <ITEM_ID>]

O QUE ELE FAZ
-------------
Le uma copia SO-LEITURA da Sala de Espera (a mesma que o export da Intelligence escreve),
corre `leis/afirmacao_do_documento.afirmacoes_do_item` em cada linha e escreve UM artefato
com as afirmacoes, ao lado do proprio export. Cada afirmacao e CONFERIDA contra o texto de
onde saiu antes de ser escrita: trecho igual a texto[inicio:fim], sha do trecho, ancoras
dentro da seccao, papel do tempo dentro do vocabulario. Afirmacao que nao passa na
conferencia nao viaja — fica na lista das REPROVADAS, com o motivo.

O QUE ELE NAO FAZ (e e de proposito)
------------------------------------
· NAO abre banco, nem rede, nem coletor: le um ficheiro e escreve um ficheiro.
· NAO cria tabela, coluna nem migration. As afirmacoes moram no artefato, ao lado do item.
· NAO decide relevancia, oportunidade, ligacao ADAMA nem LIBERACAO. Quem decide o que a
  Intelligence faz com uma afirmacao e a Intelligence (INT-LAW-030/031).
· NAO escreve na Sala. A Sala e so leitura aqui.

A SAIDA
-------
    {"CONTRATO": "AFIRMACOES_DA_SALA/v1", "ENTRADA": {...}, "FUNIL": {...},
     "ITENS": [{"PROVENIENCIA": {...}, "AFIRMACOES": [...], "REPROVADAS": [...]}]}
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

_RAIZ = Path(__file__).resolve().parent.parent
for _p in (str(_RAIZ), str(_RAIZ / "leis")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import afirmacao_do_documento as AD   # noqa: E402

CONTRATO = "AFIRMACOES_DA_SALA/v1"


def sha_do_ficheiro(caminho) -> str:
    return hashlib.sha256(Path(caminho).read_bytes()).hexdigest()


def produzir(linhas, *, so_item=None) -> dict:
    """As afirmacoes de cada linha da Sala, ja conferidas contra o texto de onde sairam."""
    itens, total, reprovadas, funil = [], 0, 0, {}
    for linha in linhas:
        if so_item and linha.get("item_id") != so_item:
            continue
        r = AD.afirmacoes_do_item(linha)
        texto = linha.get("texto") or ""
        boas, mas = [], []
        for af in r["AFIRMACOES"]:
            v = AD.conferir_afirmacao(af, texto, raw_sha256=linha.get("raw_sha256"))
            (boas if not v else mas).append(af if not v else
                                            {"ASSERTION_ID": af.get("ASSERTION_ID"),
                                             "POSICAO": af.get("POSICAO"), "VIOLACOES": v})
        total += len(boas)
        reprovadas += len(mas)
        for k, n in r["FUNIL"].items():
            funil[k] = funil.get(k, 0) + n
        itens.append({"PROVENIENCIA": r["PROVENIENCIA"], "FUNIL": r["FUNIL"],
                      "AFIRMACOES": boas, "REPROVADAS": mas})
    funil["ITENS"] = len(itens)
    funil["AFIRMACOES_CONFERIDAS"] = total
    funil["AFIRMACOES_REPROVADAS"] = reprovadas
    return {"CONTRATO": CONTRATO, "FUNIL": funil, "ITENS": itens}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="produz as AFIRMACOES de uma copia so-leitura da Sala")
    ap.add_argument("sala", help="o export da Sala (JSON: lista de linhas READY)")
    ap.add_argument("saida", help="onde escrever o artefato das afirmacoes")
    ap.add_argument("--item", default=None, help="so este ITEM_ID")
    a = ap.parse_args(argv)
    entrada = Path(a.sala)
    linhas = json.loads(entrada.read_text(encoding="utf-8"))
    if not isinstance(linhas, list):
        print("a entrada tem de ser a LISTA de linhas da Sala", file=sys.stderr)
        return 2
    r = produzir(linhas, so_item=a.item)
    r["ENTRADA"] = {"FICHEIRO": entrada.name, "SHA256": sha_do_ficheiro(entrada),
                    "LINHAS": len(linhas), "SO_LEITURA": "a Sala nao foi escrita por este comando"}
    r["LEI"] = AD.contrato()
    saida = Path(a.saida)
    saida.parent.mkdir(parents=True, exist_ok=True)
    saida.write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(r["FUNIL"], ensure_ascii=False))
    print("%s sha256 %s" % (saida.name, sha_do_ficheiro(saida)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
