#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""REPROCESSAR A CHAVE PROBLEMA DA SALA — pela porta, sem rede, a partir de uma COPIA exportada.

CHAVE-PROBLEMA (27/09). A CAP-WIN dizia «PROBLEMA NAO EXISTE no contrato 033» e todo item real saia
NOT_POSSIBLE. O contrato passou a existir (`leis/afirmacao_da_fonte.CONTRATO_PROBLEMA`, PROBLEMA/v1) e quem o
preenche e UM so (`leis/boletim_do_campo.declarar_problema`, chamado pela porta: `admissao.problema_da_chave`).
Este script da a cada linha da Sala o PROBLEMA que a porta de hoje lhe daria, e MAIS NADA:

    linha.texto -> admissao.problema_da_chave(universo) -> a janela ATUAL com a chave PROBLEMA trocada

e devolve as revisoes no formato de `sala_de_espera.rever` (`[{"CAMPO", "VALOR", "BASE"}]`, campo
`janela_declarada`, JSON com as chaves ordenadas), com o extractor, a VERSAO = sha256 do codigo, e o motivo.

    O RAW NAO MUDA. A LINHA NAO MUDA. NUNCA HA UPDATE CALADO. SO SE ACRESCENTA.

    py admissao/reprocessar_problema.py --entrada copia.json --saida revisoes.json          # SECO (omissao)
    py admissao/reprocessar_problema.py --aplicar revisoes.json [--recibo recibo.json]       # coordenador

SECO (omissao): nao abre banco nenhum. `--aplicar` le as revisoes que o seco escreveu, exige a Sala canonica
(`sala_de_espera.exigir_canonica`), recusa se o codigo mudou depois do seco (a VERSAO tem de ser a mesma), e
escreve SO pela porta `sala_de_espera.rever` — que so faz INSERT em `sala_de_espera_revisao` (migration 033) e
nao repete o que ja era assim.

A ENTRADA e JSON: uma lista (ou `{"ITENS": [...]}`) de linhas exportadas da VISTA `sala_de_espera_atual`:
    {"run_id", "ordem", "item_id", "universo", "texto", "janela_declarada"}
`janela_declarada` e a ATUAL (a vista ja da a ultima revisao): a revisao troca a janela INTEIRA, por isso sem
ela nao se reve — reescrever as outras chaves de memoria seria apagar o que outra revisao pos la.

O que NAO faz: nao abre rede; nao refaz a decisao da porta; nao mexe em CULTURA, REGIAO_DO_FATO, FASE, JANELA
nem em mais nenhuma chave; nao escreve FACT_TIME nem FACT_LOCATION; nao escolhe uma praga quando o item cita
duas (D112: NAO SEI, com os CANDIDATOS a vista); nao cunha EPPO a partir do nome comum.
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
EXTRATOR = ("admissao/reprocessar_problema.py · admissao.problema_da_chave"
            " + leis/boletim_do_campo.declarar_problema (contrato PROBLEMA/v1)")
MOTIVO = ("CHAVE-PROBLEMA (27/09): a chave PROBLEMA da janela_declarada no contrato PROBLEMA/v1 (um nome, "
          "onde esta escrito, o trecho literal), relida sem rede do texto guardado; so a chave PROBLEMA muda")
CAMPO = "janela_declarada"
BASE = ("CHAVE-PROBLEMA: so a chave PROBLEMA mudou (admissao.problema_da_chave, universo %s, contrato "
        "PROBLEMA/v1); as outras chaves sao as da janela atual, tal e qual")

#: O codigo que produz o resultado. A versao E o sha256 dele (o criterio dos outros reprocessos).
CODIGO_DA_VERSAO = ("admissao/reprocessar_problema.py", "admissao/admissao.py", "leis/boletim_do_campo.py",
                    "leis/afirmacao_da_fonte.py", "leis/estudo_chaves.py", "leis/fato_do_texto.py",
                    "leis/fato_local.py", "coleta/pesquisadores_t6.py", "motor/normalize_agro.py",
                    "data/samples/ES-T4-001/eppo-dictionary.json")


def versao_do_codigo():
    h = hashlib.sha256()
    for rel in CODIGO_DA_VERSAO:
        with open(os.path.join(RAIZ, rel), "rb") as fh:
            h.update(fh.read().replace(b"\r\n", b"\n"))   # CRLF e LF: a mesma versao
    return "chave-problema@" + h.hexdigest()[:16]


def _janela(valor):
    """A janela como dict (a copia pode trazer o JSON como texto)."""
    if isinstance(valor, str):
        valor = json.loads(valor)
    return valor


def _texto_json(valor):
    return json.dumps(valor, ensure_ascii=False, sort_keys=True)


def reprocessar(entradas: list) -> dict:
    versao = versao_do_codigo()
    conta = {"ITENS": len(entradas), "ERROS": 0, "COM_PROBLEMA": 0, "SO_CANDIDATOS": 0, "SO_AUSENTES": 0,
             "SEM_LEITOR_NO_UNIVERSO": 0, "POR_VEIO_DE": {}, "COM_EPPO": 0, "REVISOES": 0, "JA_ERAM_ASSIM": 0}
    itens = []
    for e in entradas:
        morada = {"ITEM_ID": e.get("item_id", adm.AUSENCIA), "RUN_ID": e.get("run_id", adm.AUSENCIA),
                  "ORDEM": e.get("ordem", adm.AUSENCIA)}
        erro = None
        if e.get("run_id") in (None, "") or e.get("ordem") in (None, ""):
            erro = "linha sem run_id/ordem: nao se reve linha sem morada"
        elif not isinstance(_janela(e.get("janela_declarada")), dict):
            erro = ("linha sem a janela_declarada ATUAL: a revisao troca a janela inteira, e sem a atual "
                    "apagaria as outras chaves — exporte pela vista sala_de_espera_atual")
        if erro:
            conta["ERROS"] += 1
            itens.append(dict(morada, ERRO=erro, REVISOES=[]))
            continue
        universo = e.get("universo") or adm.AUSENCIA
        atual = _janela(e["janela_declarada"])
        problema = adm.problema_da_chave({"texto": e.get("texto") or ""}, universo)
        nova = dict(atual, PROBLEMA=problema)
        if problema["VALOR"] != adm.AUSENCIA:
            conta["COM_PROBLEMA"] += 1
            conta["POR_VEIO_DE"][problema["VEIO_DE"]] = conta["POR_VEIO_DE"].get(problema["VEIO_DE"], 0) + 1
            conta["COM_EPPO"] += problema["CODIGO"].get("SISTEMA") == "EPPO"
        elif problema.get("CANDIDATOS"):
            conta["SO_CANDIDATOS"] += 1
        elif problema.get("AUSENTES"):
            conta["SO_AUSENTES"] += 1
        if universo not in adm.UNIVERSOS_DE_BOLETIM + adm.UNIVERSOS_DE_ESTUDO:
            conta["SEM_LEITOR_NO_UNIVERSO"] += 1
        revs = [{"CAMPO": CAMPO, "VALOR": _texto_json(nova), "BASE": BASE % universo}]
        if _texto_json(atual) == revs[0]["VALOR"]:
            conta["JA_ERAM_ASSIM"] += 1
            revs = []
        conta["REVISOES"] += len(revs)
        itens.append(dict(morada, UNIVERSO=universo,
                          RESUMO={"PROBLEMA": problema["VALOR"], "VEIO_DE": problema["VEIO_DE"],
                                  "CODIGO": problema["CODIGO"].get("VALOR"),
                                  "SISTEMA": problema["CODIGO"].get("SISTEMA"),
                                  "CANDIDATOS": [c["NOME"] for c in problema.get("CANDIDATOS") or []],
                                  "PORQUE": problema.get("PORQUE")},
                          REVISOES=revs))
    return {"GRAVOU_NO_BANCO": False, "VERSAO_DO_EXTRATOR": versao, "EXTRATOR": EXTRATOR, "MOTIVO": MOTIVO,
            "COMO_APLICAR": ("py admissao/reprocessar_problema.py --aplicar <este ficheiro> — so INSERT em "
                             "sala_de_espera_revisao pela porta sala_de_espera.rever (migration 033)"),
            "CONTA": conta, "ITENS": itens}


def aplicar(revisoes: dict, espera=None) -> dict:
    """Escreve o que o SECO devolveu, pela porta `rever`. So o coordenador, so na Sala canonica."""
    if espera is None:
        import sala_de_espera as espera   # noqa: PLC0415 — o seco nunca abre o banco
    espera.exigir_canonica()
    agora = versao_do_codigo()
    if revisoes.get("VERSAO_DO_EXTRATOR") != agora:
        raise SystemExit("RECUSADO: as revisoes sao de %s e o codigo de hoje e %s — corra o SECO outra vez"
                         % (revisoes.get("VERSAO_DO_EXTRATOR"), agora))
    recibo = {"APLICOU": True, "VERSAO_DO_EXTRATOR": agora, "INSERIDAS": 0, "JA_ERAM_ASSIM": 0, "LINHAS": 0}
    for it in revisoes.get("ITENS") or []:
        if not it.get("REVISOES"):
            continue
        r = espera.rever(it["RUN_ID"], it["ORDEM"], it["REVISOES"], extrator=revisoes["EXTRATOR"],
                         versao=agora, motivo=revisoes["MOTIVO"])
        recibo["LINHAS"] += 1
        recibo["INSERIDAS"] += r["INSERIDAS"]
        recibo["JA_ERAM_ASSIM"] += r["JA_ERAM_ASSIM"]
    return recibo


def ler_entrada(caminho: str) -> list:
    with open(caminho, encoding="utf-8") as fh:
        d = json.load(fh)
    if isinstance(d, dict):
        d = d.get("ITENS") or d.get("itens") or []
    if not isinstance(d, list):
        raise ValueError("a entrada tem de ser uma lista de linhas (ou {\"ITENS\": [...]})")
    return d


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    modo = ap.add_mutually_exclusive_group(required=True)
    modo.add_argument("--entrada", help="SECO: a copia exportada da vista sala_de_espera_atual (JSON)")
    modo.add_argument("--aplicar", help="as revisoes que o SECO escreveu (JSON) — so na Sala canonica")
    ap.add_argument("--seco", action="store_true", help="(omissao com --entrada) nao grava no banco")
    ap.add_argument("--saida", help="SECO: onde escrever as revisoes (JSON)")
    ap.add_argument("--recibo", help="APLICAR: onde escrever o recibo (JSON)")
    a = ap.parse_args(argv)
    if a.aplicar:
        with open(a.aplicar, encoding="utf-8") as fh:
            recibo = aplicar(json.load(fh))
        if a.recibo:
            with open(a.recibo, "w", encoding="utf-8", newline="\n") as fh:
                json.dump(recibo, fh, ensure_ascii=False, indent=1)
        print(json.dumps(recibo, ensure_ascii=False, indent=1))
        return 0
    fora = reprocessar(ler_entrada(a.entrada))
    if a.saida:
        with open(a.saida, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(fora, fh, ensure_ascii=False, indent=1)
    print(json.dumps({k: fora[k] for k in ("GRAVOU_NO_BANCO", "VERSAO_DO_EXTRATOR", "CONTA")},
                     ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
