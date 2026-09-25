#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""D49 — AS DUPLICADAS SAEM COM O MOTIVO, PELA MARCA DE CATALOGO QUE O PORTAO JA LE.

    DUPLICADA NAO E DEFEITO DA FONTE: E DUAS FICHAS PARA OS MESMOS DOCUMENTOS.

Decisao D49 (bot Luciano, 25/09, sobre a CONTRATO-44 v2): FICAM IT-T2-051 (os dois
seletores de lingua da ARPAE), IT-T7-043, IT-T8-021 + as 7 seccoes da Terra e Vita,
e IT-T7-112 (temporario). SAEM como DUPLICADA, motivo DUPLICADA_POR_SOBREPOSICAO_DE_ROTA,
sem apagar nada e sem fundir historicos: IT-T2-056, IT-T2-106, IT-T7-100, IT-T8-068.
(IT-T7-115 NAO e duplicada: CONFLITO_DE_ROTA/CONTRATO_GENERICO — fica fora ate ao reparo.)

Decisao D51.1 (bot Luciano, 25/09, sobre a HR-6): IT-T7-170 (CONAF, pagina inicial) sai
como DUPLICADA da IT-T7-174 (CONAF, comunicados): o canario do coletor abriu a MESMA
noticia nas duas. Mesma porta, mesma marca; a linha diz D51.

A PORTA: a mesma da D9 (`scripts/desbloqueio/aplicar_desbloqueio.py`, bloco 2) — o
contrato do Curator ganha `ESTADO_CATALOGO = RETIRADA_POR_DECISAO` e `CATALOGO_D9`
com a decisao, o motivo e quem fica. O portao (`collection_gate.avaliar`) e o coletor
(`regras/italy_contracts.mjs`) ja recusam essa marca, com o motivo escrito:
«retirada do universo por decisao (D9: D49 · DUPLICADA_POR_SOBREPOSICAO_DE_ROTA: fica ...)».
«D9» ai e o nome do mecanismo (a marca de catalogo); a decisao vem logo a seguir.
Nao ha estado DUPLICADA no livro de estados (vocabulario fechado) e nao se inventa um:
o livro de estados nao muda; a fonte fica READY e o portao recusa-a por decisao.

REVERSIVEL: tirar a marca devolve a fonte ao circuito do Curator.

    POR OMISSAO SO MOSTRA. `--aplicar` escreve o livro de contratos (e so ele).
"""
from __future__ import annotations

import copy
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
CONTRATOS = RAIZ / "curadoria" / "italy_contracts_curator.json"
TABELA = RAIZ / "regras" / "italy_contracts_onboarded.json"

RETIRADA = "RETIRADA_POR_DECISAO"
MOTIVO = "DUPLICADA_POR_SOBREPOSICAO_DE_ROTA"
PROVA_D49 = "ferramentas/contrato44/PERGUNTA-DUPLICADAS-BOT-LUCIANO.md"
PROVA_D51 = "ferramentas/hr6/RELATORIO-E-PLANO-HR6.md"
# fonte que sai -> (fonte que fica, porque, decisao, ficheiro da prova)
D49 = {
    "IT-T2-056": ("IT-T2-051", "seletor de lingua da arpae: mesmo site e mesmo padrao que IT-T2-051", "D49", PROVA_D49),
    "IT-T2-106": ("IT-T2-051", "seletor de lingua da arpae: a prova de rota abriu o MESMO documento que IT-T2-056", "D49", PROVA_D49),
    "IT-T7-100": ("IT-T7-043", "a prova de rota abriu o MESMO documento que IT-T7-043", "D49", PROVA_D49),
    "IT-T8-068": ("IT-T8-021", "revista inteira com o padrao generico: sobrepoe IT-T8-021 e as seccoes da Terra e Vita", "D49", PROVA_D49),
    "IT-T7-170": ("IT-T7-174", "CONAF pagina inicial: o canario do coletor abriu a MESMA noticia que IT-T7-174 (3 noticias contra 29)", "D51", PROVA_D51),
}
CAMPOS = ("ESTADO_CATALOGO", "CATALOGO_D9")


class InvarianteQuebrado(Exception):
    pass


def planear(livro: dict, *, quando: str | None = None) -> tuple[dict, list[dict]]:
    """(livro depois, accoes). Puro: nao escreve."""
    quando = quando or datetime.now(timezone.utc).isoformat()
    por = {c["SOURCE_ID"]: c for c in livro["FONTES"]}
    novo = copy.deepcopy(por)
    acoes = []
    for sid, (fica, prova, decisao, ficheiro) in sorted(D49.items()):
        a = {"SOURCE_ID": sid, "DECISAO": decisao, "FICA": fica}
        c = novo.get(sid)
        if not c:
            acoes.append(dict(a, ACAO="SALTA", PORQUE="a fonte nao esta no livro"))
            continue
        f = novo.get(fica)
        if not f or f.get("ESTADO_CATALOGO") == RETIRADA:
            acoes.append(dict(a, ACAO="SALTA", PORQUE="a ficha que fica (%s) nao esta no livro ou esta retirada" % fica))
            continue
        if c.get("ESTADO_CATALOGO") == RETIRADA and (c.get("CATALOGO_D9") or {}).get("DECISAO") == decisao:
            acoes.append(dict(a, ACAO="JA_APLICADA"))
            continue
        if c.get("ESTADO_CATALOGO") == RETIRADA:
            acoes.append(dict(a, ACAO="SALTA", PORQUE="ja retirada por outra decisao: %s"
                              % (c.get("CATALOGO_D9") or {}).get("DECISAO")))
            continue
        c["ESTADO_CATALOGO"] = RETIRADA
        c["CATALOGO_D9"] = {"DECISAO": decisao, "ACCAO": "RETIRAR_DUPLICADA", "MOTIVO": MOTIVO, "FICA": fica,
                            "PORQUE": "%s · %s: fica %s (%s)" % (decisao, MOTIVO, fica, prova),
                            "PROVA": ficheiro,
                            "APLICADO_EM": quando, "REVERSIVEL": True,
                            "NOTA": "sem apagar nada e sem fundir historicos; tirar a marca devolve a fonte ao Curator"}
        acoes.append(dict(a, ACAO="APLICA"))
    depois = dict(livro, FONTES=[novo[c["SOURCE_ID"]] for c in livro["FONTES"]])
    invariantes(livro, depois)
    return depois, acoes


def invariantes(antes: dict, depois: dict) -> None:
    A = {c["SOURCE_ID"]: c for c in antes["FONTES"]}
    D = {c["SOURCE_ID"]: c for c in depois["FONTES"]}
    if list(A) != list(D):
        raise InvarianteQuebrado("o livro ganhou, perdeu ou reordenou fontes")
    for s in A:
        a, d = copy.deepcopy(A[s]), copy.deepcopy(D[s])
        if s in D49:
            for k in CAMPOS:
                a.pop(k, None)
                d.pop(k, None)
        if a != d:
            raise InvarianteQuebrado("%s: mudou um campo que a D49 nao pode mudar" % s)


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    livro = json.loads(CONTRATOS.read_text(encoding="utf-8"))
    depois, acoes = planear(livro)
    tabela = json.loads(TABELA.read_text(encoding="utf-8")) if TABELA.exists() else {"FONTES": []}
    na_tabela = {c.get("SOURCE_ID") for c in tabela.get("FONTES", [])}
    for a in acoes:
        print("%-12s %-10s fica %s %s%s" % (a["ACAO"], a["SOURCE_ID"], a["FICA"], a.get("PORQUE", ""),
                                          " · ⚠️ esta na tabela do coletor" if a["SOURCE_ID"] in na_tabela else ""))
    if "--aplicar" in argv and any(a["ACAO"] == "APLICA" for a in acoes):
        CONTRATOS.write_text(json.dumps(depois, ensure_ascii=False, indent=1), encoding="utf-8")
        print("livro de contratos escrito")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
