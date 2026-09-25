#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RETIRAR POR DECISAO — a marca de catalogo da D9, aplicada fonte a fonte, com volta.

    py curadoria/retirar_por_decisao.py --decisao D52                         # relatorio, nada escrito
    py curadoria/retirar_por_decisao.py --decisao D52 --escrever              # marca no livro do curador
    py curadoria/retirar_por_decisao.py --decisao D52 --reverter --escrever   # tira a marca que ESTA decisao pos
    [--livro <italy_contracts_curator.json>]   (por omissao, o desta arvore)

A MARCA E A DA D9, NAO UMA NOVA. `ESTADO_CATALOGO = RETIRADA_POR_DECISAO` e `CATALOGO_D9` (decisao,
accao, porque, prova, reversivel) no contrato do curador — o que o pacote G1 escreveu para a D9
(`scripts/desbloqueio/aplicar_desbloqueio.py:391`) e o que ja se le em
  · `curadoria/collection_gate.py:144`   a fonte nao entra no portao da coleta;
  · `regras/italy_contracts.mjs:677`     uma linha retirada nao vira contrato do coletor;
  · `scripts/coorte_micro/funil.py:185`  a fonte nao entra na micro-coleta;
  · `curadoria/gatilho_discovery.py`     (D52) o robo nao volta a pedir reparo/validacao dela;
  · `curadoria/alimentar_fila.py`        (D52) a alimentacao a mao tambem a salta.
O G1 aplicou-se uma vez, no cutover; esta porta e a mesma marca para decisoes seguintes.

POR SOURCE_ID, NUNCA POR DOMINIO. A lista e a do ficheiro da decisao (cada fonte com a SUA prova).
Uma fonte que ja tenha OUTRA marca de catalogo nao e tocada (SALTA, com motivo).

REVERSIVEL. `--reverter` tira as duas chaves so das fontes cuja marca e DESTA decisao; como a marca so se
poe onde nao havia nenhuma, o contrato volta byte a byte ao que era. Nada e apagado em nenhum sentido.

Invariantes (se falhar um, nada e escrito, exit 4): as mesmas fontes pela mesma ordem; so as fontes da
decisao mudam; nelas so mudam `ESTADO_CATALOGO` e `CATALOGO_D9`; o cabecalho do livro nao muda.
Idempotente: a 2.a corrida so ve JA_APLICADA (ou JA_REVERTIDA).
"""
from __future__ import annotations

import argparse
import copy
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
LIVRO = RAIZ / "curadoria" / "italy_contracts_curator.json"
RETIRADA = "RETIRADA_POR_DECISAO"
CHAVES = ("ESTADO_CATALOGO", "CATALOGO_D9")
DECISOES = {"D52": RAIZ / "curadoria" / "DECISAO-D52-RETIRAR-V1.json"}


class InvarianteQuebrado(Exception):
    pass


def retirada(contrato: dict | None) -> bool:
    """A leitura unica da marca, para quem enfileira trabalho."""
    return (contrato or {}).get("ESTADO_CATALOGO") == RETIRADA


def ler_decisao(decisao: str) -> dict:
    if decisao not in DECISOES:
        raise SystemExit("decisao desconhecida: %s (conhecidas: %s)" % (decisao, sorted(DECISOES)))
    d = json.loads(DECISOES[decisao].read_text(encoding="utf-8"))
    if d.get("DECISAO") != decisao:
        raise SystemExit("o ficheiro da decisao nao e da %s" % decisao)
    return d


def aplicar(livro: dict, dec: dict, *, quando: str | None = None) -> tuple[dict, list]:
    quando = quando or datetime.now(timezone.utc).isoformat()
    alvo = {f["SOURCE_ID"]: f for f in dec["FONTES"]}
    fontes, acoes, mudadas = copy.deepcopy(livro["FONTES"]), [], set()
    vistos = set()
    for c in fontes:
        sid = c.get("SOURCE_ID")
        if sid not in alvo:
            continue
        vistos.add(sid)
        a = {"SOURCE_ID": sid, "DECISAO": dec["DECISAO"]}
        if c.get("ESTADO_CATALOGO") == RETIRADA and (c.get("CATALOGO_D9") or {}).get("DECISAO") == dec["DECISAO"]:
            acoes.append(dict(a, ACAO="JA_APLICADA"))
            continue
        if c.get("ESTADO_CATALOGO") or c.get("CATALOGO_D9"):
            acoes.append(dict(a, ACAO="SALTA", PORQUE="ja tem outra marca de catalogo: %s" % c.get("ESTADO_CATALOGO")))
            continue
        f = alvo[sid]
        c["ESTADO_CATALOGO"] = RETIRADA
        c["CATALOGO_D9"] = {"DECISAO": dec["DECISAO"], "ACCAO": "RETIRAR_DO_UNIVERSO", "PORQUE": f["PORQUE"],
                            "PROVA": f["PROVA"].get("EVIDENCE_REF"), "REVERSIVEL": True, "APLICADO_EM": quando,
                            "NOTA": dec.get("VOLTA", "pode voltar pelo circuito do Curator")}
        mudadas.add(sid)
        acoes.append(dict(a, ACAO="APLICA", PROVA=f["PROVA"].get("EVIDENCE_REF")))
    for sid in sorted(set(alvo) - vistos):
        acoes.append({"SOURCE_ID": sid, "DECISAO": dec["DECISAO"], "ACAO": "SALTA", "PORQUE": "nao esta no livro"})
    depois = dict(livro, FONTES=fontes)
    invariantes(livro, depois, mudadas)
    return depois, acoes


def reverter(livro: dict, dec: dict) -> tuple[dict, list]:
    alvo = {f["SOURCE_ID"] for f in dec["FONTES"]}
    fontes, acoes, mudadas = copy.deepcopy(livro["FONTES"]), [], set()
    for c in fontes:
        sid = c.get("SOURCE_ID")
        if sid not in alvo:
            continue
        if (c.get("CATALOGO_D9") or {}).get("DECISAO") != dec["DECISAO"]:
            acoes.append({"SOURCE_ID": sid, "DECISAO": dec["DECISAO"], "ACAO": "JA_REVERTIDA"})
            continue
        for k in CHAVES:
            c.pop(k, None)
        mudadas.add(sid)
        acoes.append({"SOURCE_ID": sid, "DECISAO": dec["DECISAO"], "ACAO": "REVERTE"})
    depois = dict(livro, FONTES=fontes)
    invariantes(livro, depois, mudadas)
    return depois, acoes


def invariantes(antes: dict, depois: dict, mudadas: set) -> None:
    if [c["SOURCE_ID"] for c in antes["FONTES"]] != [c["SOURCE_ID"] for c in depois["FONTES"]]:
        raise InvarianteQuebrado("o livro ganhou, perdeu ou reordenou fontes")
    for a, b in zip(antes["FONTES"], depois["FONTES"]):
        if a == b:
            continue
        if a["SOURCE_ID"] not in mudadas:
            raise InvarianteQuebrado("%s mudou sem estar na decisao" % a["SOURCE_ID"])
        if {k: v for k, v in a.items() if k not in CHAVES} != {k: v for k, v in b.items() if k not in CHAVES}:
            raise InvarianteQuebrado("%s: mudou um campo alem da marca de catalogo" % a["SOURCE_ID"])
    if {k: v for k, v in antes.items() if k != "FONTES"} != {k: v for k, v in depois.items() if k != "FONTES"}:
        raise InvarianteQuebrado("o cabecalho do livro mudou")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--decisao", required=True)
    ap.add_argument("--livro", default=str(LIVRO))
    ap.add_argument("--reverter", action="store_true")
    ap.add_argument("--escrever", action="store_true")
    a = ap.parse_args(argv)
    dec = ler_decisao(a.decisao)
    bruto = Path(a.livro).read_bytes()
    # o livro vivo e gravado pelo worker com `write_text` no Windows (CRLF, sem quebra final): a porta
    # devolve-o no MESMO estilo — reverter tem de dar os mesmos bytes, nao so o mesmo conteudo
    quebra = "\r\n" if b"\r\n" in bruto else "\n"
    texto = bruto.decode("utf-8").replace("\r\n", "\n")
    fim = "\n" if texto.endswith("\n") else ""
    livro = json.loads(texto)
    try:
        depois, acoes = (reverter if a.reverter else aplicar)(livro, dec)
    except InvarianteQuebrado as e:
        print("NADA ESCRITO:", e)
        return 4
    from collections import Counter
    print(dict(Counter(x["ACAO"] for x in acoes)))
    for x in acoes:
        if x["ACAO"] == "SALTA":
            print(json.dumps(x, ensure_ascii=False))
    if a.escrever and any(x["ACAO"] in ("APLICA", "REVERTE") for x in acoes):
        with open(a.livro, "w", encoding="utf-8", newline=quebra) as f:
            f.write(json.dumps(depois, ensure_ascii=False, indent=1) + fim)
        print("escrito:", a.livro)
    return 0


if __name__ == "__main__":
    sys.exit(main())
