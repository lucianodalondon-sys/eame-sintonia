#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""REPROCESSAR AS CHAVES DOS ESTUDOS T5 — pela porta, sem rede e SEM BANCO.

ESTUDOS-CHAVES (27/09). Medido na Sala real: os 100 estudos T5 (EU-T5-001, OpenAlex) com a
`janela_declarada` toda NAO SEI. Este script refaz SO a `janela_declarada` de cada estudo, a partir do
texto que a linha guardou (titulo + resumo), pelo MESMO dono da producao:

    item.texto -> admissao.janela_para_o_ready (universo T5) -> leis/estudo_chaves.chaves_do_estudo

e DEVOLVE as revisoes no formato de `sala_de_espera.rever` (`[{"CAMPO", "VALOR", "BASE"}]`, com o extractor,
a VERSAO = sha256 do codigo, e o motivo) — como `admissao/reprocessar_tempo_lugar.py`:

    O RAW NAO MUDA. A LINHA NAO MUDA. NUNCA HA UPDATE CALADO. SO SE ACRESCENTA.

⚠️ ESTE SCRIPT NAO GRAVA NO BANCO. Nao tem `--aplicar`: quem aplica e o coordenador, localmente, com a
Sala canonica, pela porta `sala_de_espera.rever` (que so faz INSERT em `sala_de_espera_revisao`).

    py admissao/reprocessar_estudos_chaves.py --entrada estudos.json --saida revisoes.json

A ENTRADA e JSON: uma lista (ou `{"ITENS": [...]}`) de
    {"item_id": ..., "texto": ..., "published_at": ...}
e, opcionais, os que a linha da Sala ja tem e que o reprocesso NAO deve apagar:
    "run_id", "ordem", "universo" (omissao T5), "fact_location", "fact_location_basis", "fact_time",
    "fact_time_basis", "captured_at", "janela_declarada" (a atual: igual = JA_ERA_ASSIM, nao se repete).

O que NAO faz: nao abre rede; nao refaz a decisao da porta (quem entrou, entrou); nao le afiliacao;
nao transforma PUBLISHED_AT em periodo (a JANELA continua NAO SEI sem FACT_TIME); nao escreve
FACT_LOCATION nem FACT_TIME; nao escreve incidencia de campo (CAP-SCI).
"""
import argparse
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))   # a raiz
import _gavetas  # noqa: E402,F401 — poe as gavetas do processo no caminho

import admissao as adm  # noqa: E402

RAIZ = os.path.dirname(HERE)
EXTRATOR = ("admissao/reprocessar_estudos_chaves.py · admissao.janela_para_o_ready"
            " + leis/estudo_chaves.chaves_do_estudo")
MOTIVO = ("ESTUDOS-CHAVES (27/09): reprocessamento sem rede da janela_declarada dos estudos T5 a partir "
          "do texto guardado (titulo + resumo); a linha original nao muda")
CAMPO = "janela_declarada"

#: O codigo que produz o resultado. A versao E o sha256 dele (o mesmo criterio do reproc tempo-lugar).
CODIGO_DA_VERSAO = ("admissao/reprocessar_estudos_chaves.py", "admissao/admissao.py",
                    "leis/estudo_chaves.py", "leis/boletim_do_campo.py", "leis/fato_local.py",
                    "coleta/pesquisadores_t6.py")

OPCIONAIS = ("fact_location", "fact_location_basis", "fact_time", "fact_time_basis", "captured_at")


def versao_do_codigo():
    h = hashlib.sha256()
    for rel in CODIGO_DA_VERSAO:
        with open(os.path.join(RAIZ, rel), "rb") as fh:
            h.update(fh.read().replace(b"\r\n", b"\n"))   # CRLF e LF: a mesma versao
    return "estudos-chaves@" + h.hexdigest()[:16]


def _texto_json(valor):
    """A janela como a Sala a guarda: JSON com as chaves ORDENADAS (o mesmo texto para o mesmo codigo)."""
    if isinstance(valor, str):
        try:
            valor = json.loads(valor)
        except json.JSONDecodeError:
            return valor
    return json.dumps(valor, ensure_ascii=False, sort_keys=True)


def janela_de(entrada: dict) -> dict:
    """A `janela_declarada` que a estrada de hoje daria a este estudo — sem rede e sem banco."""
    item = {"texto": entrada.get("texto") or "", "published_at": entrada.get("published_at")}
    for k in OPCIONAIS:
        if entrada.get(k) is not None:
            item[k] = entrada[k]
    universo = entrada.get("universo") or "T5"
    # a linha JA foi admitida: a decisao nao se refaz, so a janela
    d = adm.Decisao(item=str(entrada.get("item_id")), universo=universo, resultado=adm.SIM,
                    regra="reprocessamento estudos-chaves", motivo=MOTIVO, evidencia={},
                    versao=adm.VERSAO_DA_REGRA)
    return adm.janela_para_o_ready(item, d)


def revisoes_de(janela: dict, universo: str) -> list:
    return [{"CAMPO": CAMPO, "VALOR": _texto_json(janela),
             "BASE": ("admissao.janela_para_o_ready (universo %s) + leis/estudo_chaves (ESTUDOS-CHAVES, D112 "
                      "ENTITY_SOURCE=SPAN) sobre o texto guardado; a admissao da linha nao muda" % universo)}]


def reprocessar(entradas: list) -> dict:
    versao = versao_do_codigo()
    conta = {"ITENS": len(entradas), "SEM_ITEM_ID": 0, "SEM_TEXTO": 0, "COM_CULTURA": 0,
             "COM_PROBLEMA": 0, "COM_REGIAO_DO_ESTUDO": 0, "SO_FORMAS_AMBIGUAS": 0,
             "REVISOES": 0, "JA_ERAM_ASSIM": 0}
    itens = []
    for e in entradas:
        if e.get("item_id") in (None, ""):
            conta["SEM_ITEM_ID"] += 1
            itens.append({"ITEM_ID": adm.AUSENCIA, "ERRO": "entrada sem item_id: nao se reve linha sem morada"})
            continue
        if not str(e.get("texto") or "").strip():
            conta["SEM_TEXTO"] += 1
        janela = janela_de(e)
        for chave, n in (("CULTURA", "COM_CULTURA"), ("PROBLEMA", "COM_PROBLEMA"),
                         ("REGIAO_DO_FATO", "COM_REGIAO_DO_ESTUDO")):
            conta[n] += janela[chave]["VALOR"] != adm.AUSENCIA
        conta["SO_FORMAS_AMBIGUAS"] += (janela["CULTURA"]["VALOR"] == adm.AUSENCIA
                                        and bool(janela["CULTURA"].get("AMBIGUAS")))
        revs = revisoes_de(janela, e.get("universo") or "T5")
        if e.get("janela_declarada") is not None and _texto_json(e["janela_declarada"]) == revs[0]["VALOR"]:
            conta["JA_ERAM_ASSIM"] += 1
            revs = []
        conta["REVISOES"] += len(revs)
        itens.append({"ITEM_ID": e["item_id"], "RUN_ID": e.get("run_id", adm.AUSENCIA),
                      "ORDEM": e.get("ordem", adm.AUSENCIA),
                      "RESUMO": {c: janela[c]["VALOR"] for c in ("CULTURA", "PROBLEMA", "REGIAO_DO_FATO")},
                      "REVISOES": revs})
    return {"GRAVOU_NO_BANCO": False, "VERSAO_DO_EXTRATOR": versao, "EXTRATOR": EXTRATOR, "MOTIVO": MOTIVO,
            "COMO_APLICAR": ("sala_de_espera.rever(RUN_ID, ORDEM, REVISOES, extrator=EXTRATOR, "
                             "versao=VERSAO_DO_EXTRATOR, motivo=MOTIVO) — so INSERT (migration 033)"),
            "CONTA": conta, "ITENS": itens}


def ler_entrada(caminho: str) -> list:
    with open(caminho, encoding="utf-8") as fh:
        d = json.load(fh)
    if isinstance(d, dict):
        d = d.get("ITENS") or d.get("itens") or []
    if not isinstance(d, list):
        raise ValueError("a entrada tem de ser uma lista de itens (ou {\"ITENS\": [...]})")
    return d


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--entrada", required=True, help="JSON com [{item_id, texto, published_at}, ...]")
    ap.add_argument("--saida", help="onde escrever as revisoes (JSON); sem isto so imprime a conta")
    a = ap.parse_args(argv)
    fora = reprocessar(ler_entrada(a.entrada))
    if a.saida:
        with open(a.saida, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(fora, fh, ensure_ascii=False, indent=1)
    print(json.dumps({k: fora[k] for k in ("GRAVOU_NO_BANCO", "VERSAO_DO_EXTRATOR", "CONTA")},
                     ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
