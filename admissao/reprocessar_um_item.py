#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""REPROCESSAR UM ITEM DA SALA — o tempo, o lugar e as chaves de UM item, pela porta de revisoes.

CANARIO-1149 (28/09). O dono (D129): um item REAL coletado sozinho tem de atravessar ate ao portal. O
primeiro vermelho de `derived:1149` (CREA, T5) estava na Collection: PUBLISHED_AT, REGIAO do estudo e
PROBLEMA em NAO SEI com o texto a dize-los. As regras GERAIS foram consertadas nos donos delas; este script
leva o resultado SO a um item, sem mexer no resto da Sala:

    a linha exportada da vista sala_de_espera_atual
        -> admissao/reprocessar_tempo_lugar.ready_de      (a MESMA estrada da producao, sem rede)
        -> admissao/reprocessar_tempo_lugar.revisoes_de   (os campos que a 033 aceita rever)
        -> sala_de_espera.rever                           (SO INSERT em sala_de_espera_revisao)

    O RAW NAO MUDA. A LINHA NAO MUDA. NUNCA HA UPDATE CALADO. SO SE ACRESCENTA.

    py admissao/reprocessar_um_item.py --entrada linha.json --item derived:1149 --saida revisoes.json   # SECO
    py admissao/reprocessar_um_item.py --aplicar revisoes.json --backup prova-backup.json [--recibo r.json]

SECO (omissao): nao abre banco nenhum. Le a linha exportada (um objeto, uma lista, `{"ITENS": [...]}` ou o
export SALA_ATUAL_READ_ONLY/v1 com `LINHAS`), escolhe SO o `--item` (tem de haver exactamente um) e escreve as
revisoes, com a VERSAO = sha256 do codigo que as produziu e o sha256 do texto da linha.

APLICAR (so o coordenador, so na Sala canonica), e recusa se faltar QUALQUER uma destas:
  1. `curadoria/PARAR.flag` existe — o bot esta parado (nada escreve na Sala ao mesmo tempo);
  2. `--backup` e o recibo de `scripts/micro_coleta/provar_backup_da_sala.py` com `PROVA_VALE: true` e o dump
     no disco — o caminho de volta, provado ANTES de escrever;
  3. `sala_de_espera.exigir_canonica()` — a Sala canonica, e a falar;
  4. a VERSAO do codigo e a mesma do seco;
  5. a linha da Sala (pela vista) e a do seco: mesmo ITEM_ID na mesma (RUN_ID, ORDEM) e mesmo sha256 do texto.

⚠️ SEM O LIVRO DO COLETOR, `fact_time` e `source_location` NAO SE REVEEM. A base deles compoe o que o livro
declarou («o coletor declarou: UNKNOWN — …»); refaze-la sem o livro apagava essa procedencia. Este script nao
le livros: esses dois campos ficam como estao, e o recibo di-lo em `NAO_REVISTOS`.

O que NAO faz: nao abre rede; nao refaz a decisao da porta (quem entrou, entrou); nao toca em raw_asset,
derived_artifact nem na linha; nao escreve em mais nenhum item.
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
import reprocessar_problema as RP  # noqa: E402
import reprocessar_tempo_lugar as RTL  # noqa: E402

RAIZ = os.path.dirname(HERE)
PARAR = os.path.join(RAIZ, "curadoria", "PARAR.flag")
EXTRATOR = ("admissao/reprocessar_um_item.py · admissao/reprocessar_tempo_lugar.ready_de"
            " (italy_executor.tempo_e_lugar + leis/fato_do_texto + admissao.janela_para_o_ready)")
MOTIVO = ("CANARIO-1149 (D129): reprocessamento sem rede de UM item — publicacao, lugar do facto e chaves da "
          "janela — a partir do texto guardado; a linha original nao muda")
#: sem o livro do coletor a base destes compoe-se sem o que o livro disse: nao se reveem
SEM_LIVRO_NAO_SE_REVEEM = ("fact_time", "source_location")
#: o codigo que produz o resultado: o dos dois reprocessos que este compoe, e este
CODIGO_DA_VERSAO = tuple(dict.fromkeys(("admissao/reprocessar_um_item.py",) + RTL.CODIGO_DA_VERSAO
                                       + RP.CODIGO_DA_VERSAO))
#: coluna da vista -> nome em `reprocessar_tempo_lugar.ready_de`
_DA_VISTA = {"run_id": "RUN_ID", "ordem": "ORDEM", "item_id": "ITEM_ID", "source_id": "SOURCE_ID",
             "texto": "TEXTO", "raw_observation_id": "RAW_OBSERVATION_ID", "captured_at": "CAPTURED_AT",
             "universo": "UNIVERSO"}


def versao_do_codigo():
    h = hashlib.sha256()
    for rel in CODIGO_DA_VERSAO:
        with open(os.path.join(RAIZ, rel), "rb") as fh:
            h.update(fh.read().replace(b"\r\n", b"\n"))   # CRLF e LF: a mesma versao
    return "um-item@" + h.hexdigest()[:16]


def sha_do_texto(texto) -> str:
    return hashlib.sha256(str(texto or "").encode("utf-8")).hexdigest()


def _linhas(d) -> list:
    if isinstance(d, dict):
        if "LINHAS" in d or "ITENS" in d or "itens" in d:
            d = d.get("LINHAS") or d.get("ITENS") or d.get("itens") or []
        else:
            d = [d]
    if not isinstance(d, list):
        raise ValueError("a entrada tem de ser uma linha, uma lista de linhas ou um export com LINHAS")
    return d


def _atual(linha: dict, campo: str):
    v = linha.get(campo)
    if campo in ("janela_declarada", "completude_tempo_lugar", "tempo_lugar_evidencia") and not isinstance(v, str):
        return json.dumps(v, ensure_ascii=False, sort_keys=True)
    return v


def reprocessar(entradas: list, item: str) -> dict:
    achadas = [e for e in entradas if isinstance(e, dict) and e.get("item_id") == item]
    if len(achadas) != 1:
        raise SystemExit("RECUSADO: %d linhas com item_id %r na entrada — tem de haver exactamente uma"
                         % (len(achadas), item))
    e = achadas[0]
    falta = [c for c in _DA_VISTA if e.get(c) in (None, "")]
    if falta:
        raise SystemExit("RECUSADO: a linha exportada nao traz %s (exporte pela vista sala_de_espera_atual)"
                         % ", ".join(falta))
    linha = {n: e[c] for c, n in _DA_VISTA.items()}
    linha["SHA256"] = None
    ready = RTL.ready_de(linha, None, None)
    revisoes, nao_revistos, iguais = [], [], []
    for r in RTL.revisoes_de(ready):
        if r["CAMPO"] in SEM_LIVRO_NAO_SE_REVEEM:
            nao_revistos.append({"CAMPO": r["CAMPO"], "PORQUE": "sem o livro do coletor a base perderia o que "
                                                                 "o livro declarou: fica como esta"})
            continue
        if r["VALOR"] == _atual(e, r["CAMPO"]) and r["BASE"] == e.get(r["CAMPO"] + "_basis", r["BASE"]):
            iguais.append(r["CAMPO"])
            continue
        revisoes.append(r)
    jd = ready["JANELA_DECLARADA"]
    return {"GRAVOU_NO_BANCO": False, "VERSAO_DO_EXTRATOR": versao_do_codigo(), "EXTRATOR": EXTRATOR,
            "MOTIVO": MOTIVO, "ITEM_ID": item, "RUN_ID": e["run_id"], "ORDEM": e["ordem"],
            "TEXTO_SHA256": sha_do_texto(e["texto"]),
            "COMO_APLICAR": ("py admissao/reprocessar_um_item.py --aplicar <este ficheiro> --backup "
                             "<recibo de provar_backup_da_sala.py> — so com curadoria/PARAR.flag"),
            "RESUMO": {"PUBLISHED_AT": [e.get("published_at"), ready.get("PUBLISHED_AT", adm.AUSENCIA)],
                       "FACT_LOCATION": [e.get("fact_location"), ready.get("FACT_LOCATION", adm.AUSENCIA)],
                       "FACT_TIME": [e.get("fact_time"), ready.get("FACT_TIME", adm.AUSENCIA)],
                       "CULTURA": jd["CULTURA"]["VALOR"], "PROBLEMA": jd["PROBLEMA"]["VALOR"],
                       "AGENTES_DE_CONTROLE": [a["NOME"] for a in jd["PROBLEMA"].get("AGENTES_DE_CONTROLE") or []],
                       "REGIAO_DO_FATO": jd["REGIAO_DO_FATO"]["VALOR"]},
            "NAO_REVISTOS": nao_revistos, "JA_ERAM_ASSIM": iguais, "REVISOES": revisoes}


def _recusa(porque):
    raise SystemExit("RECUSADO: " + porque)


def aplicar(revisoes: dict, backup: dict, espera=None, parar: str = PARAR) -> dict:
    """Escreve o que o SECO devolveu, pela porta `rever`, e so com as cinco travas de pe."""
    if not os.path.exists(parar):
        _recusa("sem %s — o bot tem de estar parado antes de se escrever na Sala" % parar)
    if not isinstance(backup, dict) or backup.get("PROVA_VALE") is not True:
        _recusa("o backup nao tem PROVA_VALE: true — sem caminho de volta provado nao se escreve")
    if not backup.get("DUMP") or not os.path.exists(backup["DUMP"]):
        _recusa("o dump do backup nao esta no disco: %r" % backup.get("DUMP"))
    if espera is None:
        import sala_de_espera as espera   # noqa: PLC0415 — o seco nunca abre o banco
    espera.exigir_canonica()
    agora = versao_do_codigo()
    if revisoes.get("VERSAO_DO_EXTRATOR") != agora:
        _recusa("as revisoes sao de %s e o codigo de hoje e %s — corra o SECO outra vez"
                % (revisoes.get("VERSAO_DO_EXTRATOR"), agora))
    linhas = (espera.ler_atual(revisoes["RUN_ID"]) or {}).get("ITENS") or []
    linha = next((l for l in linhas if int(l["ORDEM"]) == int(revisoes["ORDEM"])), None)
    if linha is None or linha.get("ITEM_ID") != revisoes.get("ITEM_ID"):
        _recusa("a Sala nao tem %s em (%s, %s)" % (revisoes.get("ITEM_ID"), revisoes["RUN_ID"],
                                                   revisoes["ORDEM"]))
    if sha_do_texto(linha.get("TEXTO")) != revisoes.get("TEXTO_SHA256"):
        _recusa("o texto da linha na Sala nao e o do seco (sha256 diferente)")
    recibo = {"APLICOU": True, "VERSAO_DO_EXTRATOR": agora, "ITEM_ID": revisoes["ITEM_ID"],
              "INSERIDAS": 0, "JA_ERAM_ASSIM": 0}
    if revisoes.get("REVISOES"):
        r = espera.rever(revisoes["RUN_ID"], int(revisoes["ORDEM"]), revisoes["REVISOES"],
                         extrator=revisoes["EXTRATOR"], versao=agora, motivo=revisoes["MOTIVO"])
        recibo["INSERIDAS"], recibo["JA_ERAM_ASSIM"] = r["INSERIDAS"], r["JA_ERAM_ASSIM"]
    return recibo


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    modo = ap.add_mutually_exclusive_group(required=True)
    modo.add_argument("--entrada", help="SECO: a linha exportada da vista sala_de_espera_atual (JSON)")
    modo.add_argument("--aplicar", help="as revisoes que o SECO escreveu (JSON) — so na Sala canonica")
    ap.add_argument("--item", help="SECO: o item_id (ex.: derived:1149) — so ele")
    ap.add_argument("--saida", help="SECO: onde escrever as revisoes (JSON)")
    ap.add_argument("--backup", help="APLICAR: o recibo de provar_backup_da_sala.py (PROVA_VALE)")
    ap.add_argument("--recibo", help="APLICAR: onde escrever o recibo (JSON)")
    a = ap.parse_args(argv)
    if a.aplicar:
        if not a.backup:
            _recusa("--aplicar exige --backup (o recibo com PROVA_VALE)")
        with open(a.aplicar, encoding="utf-8") as fh:
            revs = json.load(fh)
        with open(a.backup, encoding="utf-8") as fh:
            backup = json.load(fh)
        recibo = aplicar(revs, backup)
        if a.recibo:
            with open(a.recibo, "w", encoding="utf-8", newline="\n") as fh:
                json.dump(recibo, fh, ensure_ascii=False, indent=1)
        print(json.dumps(recibo, ensure_ascii=False, indent=1))
        return 0
    if not a.item:
        _recusa("o SECO exige --item: este script reve UM item")
    with open(a.entrada, encoding="utf-8") as fh:
        fora = reprocessar(_linhas(json.load(fh)), a.item)
    if a.saida:
        with open(a.saida, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(fora, fh, ensure_ascii=False, indent=1)
    print(json.dumps({k: fora[k] for k in ("GRAVOU_NO_BANCO", "VERSAO_DO_EXTRATOR", "ITEM_ID", "RESUMO",
                                           "NAO_REVISTOS", "JA_ERAM_ASSIM")}, ensure_ascii=False, indent=1))
    print("REVISOES:", [r["CAMPO"] for r in fora["REVISOES"]])
    return 0


if __name__ == "__main__":
    sys.exit(main())
