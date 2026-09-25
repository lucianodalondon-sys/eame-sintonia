#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ALINHAR O CONTRATO DO CURADOR COM O DO COLETOR — so por decisao, so a aquisicao.

    py curadoria/alinhar_com_o_coletor.py --decisao D44              # relatorio, nada escrito
    py curadoria/alinhar_com_o_coletor.py --decisao D44 --escrever   # grava o livro do curador

O `italy_contracts_curator.json` diz de si mesmo: «o dono do contrato continua a ser
regras/italy_contracts.mjs». Quando o coletor muda a aquisicao de uma fonte (a tabela
`regras/italy_contracts_onboarded.json`), o curador fica com a antiga: o canario dele testa
uma rota que o coletor ja nao usa, e o `onboardar_rotas_provadas` compara padroes velhos.

    O CURADOR SEGUE O COLETOR — NUNCA O CONTRARIO, E NUNCA SEM DECISAO.

Nao ha porta nova: a escrita e `reparar_contrato.aplicar` (muda so ACQUISITION, guarda a
anterior e a prova, PRECISA_DE_REMEDIR, recalcula o hash, passa `validar_contratos.validar`,
rebenta se tocar noutro campo). Aqui so se escolhe QUEM, e com que decisao.

Invariantes (se falhar um, nada e escrito, exit 4): o livro tem as mesmas fontes pela mesma
ordem; so mudam as fontes autorizadas pela decisao; nas outras, nem um byte.
Idempotente: a segunda corrida so ve JA_ALINHADA.
"""
from __future__ import annotations

import argparse
import copy
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))

import reparar_contrato as RC   # noqa: E402

LIVRO = RAIZ / "curadoria" / "italy_contracts_curator.json"
TABELA = RAIZ / "regras" / "italy_contracts_onboarded.json"

# Cada decisao autoriza estas fontes, e so estas. Uma fonte nova aqui = uma decisao nova do dono.
DECISOES = {
    "D44": {
        "FONTES": frozenset({"IT-T5-090"}),
        "MISSAO": "CONTRATOS-AJUSTE (alinhar curador)",
        "PORQUE": ("D44 (bot Luciano, 25/09): o contrato do curador da istat segue o do coletor "
                   "(CONTRATOS-AJUSTE, contratos-ajuste-v1 @ ca923030)"),
        "PROVA": {
            "INDICE": "scripts/capa_materia/INDICES-D40-V1.json (IT-T5-090, 25/09, sha256 la dentro)",
            "ITEM_LIDO": "scripts/capa_materia/CONFIRMACAO-ISTAT-V1.json (MATERIA_PROVAVEL, 19771 letras em paragrafos)",
            "MEDICAO": "scripts/capa_materia/MEDICAO-CONTRATOS-AJUSTE-HOJE-V1.json",
        },
    },
}


class InvarianteQuebrado(Exception):
    pass


def agora() -> str:
    return datetime.now(timezone.utc).isoformat()


def aquisicao_do_coletor(tabela: dict, sid: str) -> dict | None:
    for l in tabela.get("FONTES", []):
        if l.get("SOURCE_ID") == sid:
            return l.get("ACQUISITION")
    return None


def alinhar(livro: dict, tabela: dict, decisao: str, *, quando: str | None = None) -> tuple[dict, list]:
    """(livro depois, accoes). Puro: nao escreve em disco."""
    if decisao not in DECISOES:
        raise SystemExit("decisao desconhecida: %s (conhecidas: %s)" % (decisao, sorted(DECISOES)))
    D = DECISOES[decisao]
    quando = quando or agora()
    fontes = copy.deepcopy(livro["FONTES"])
    acoes, mudadas = [], set()
    for i, c in enumerate(fontes):
        sid = c.get("SOURCE_ID")
        if sid not in D["FONTES"]:
            continue
        a = {"SOURCE_ID": sid, "DECISAO": decisao}
        col = aquisicao_do_coletor(tabela, sid)
        if not col:
            acoes.append(dict(a, ACAO="SALTA", PORQUE="o coletor nao tem aquisicao para esta fonte"))
            continue
        cur = c.get("ACQUISITION") or {}
        if (cur.get("INDEX_URL"), cur.get("LINK_PATTERN")) == (col.get("INDEX_URL"), col.get("LINK_PATTERN")):
            acoes.append(dict(a, ACAO="JA_ALINHADA"))
            continue
        proposta = {"DESFECHO": "PADRAO_NOVO", "INDEX_URL": col["INDEX_URL"], "LINK_PATTERN": col["LINK_PATTERN"],
                    "COMO": D["PORQUE"], "ACQUISITION_ANTERIOR": cur,
                    "ENTRADA": col["INDEX_URL"], "ITEM_LIDO": D["PROVA"]["ITEM_LIDO"],
                    "ALVOS_NA_LISTAGEM": D["PROVA"]["MEDICAO"], "PAGINAS_LIDAS": D["PROVA"]["INDICE"]}
        fontes[i] = RC.aplicar(c, proposta, quando=quando, decisao=decisao, missao=D["MISSAO"],
                               metodo="ALINHAR-COM-O-COLETOR/v1", ferramenta="curadoria/alinhar_com_o_coletor.py")
        mudadas.add(sid)
        acoes.append(dict(a, ACAO="APLICA", ANTES=cur.get("LINK_PATTERN"), DEPOIS=col["LINK_PATTERN"]))
    depois = dict(livro, FONTES=fontes)
    invariantes(livro, depois, mudadas)
    return depois, acoes


def invariantes(antes: dict, depois: dict, mudadas: set) -> None:
    A = [c["SOURCE_ID"] for c in antes["FONTES"]]
    B = [c["SOURCE_ID"] for c in depois["FONTES"]]
    if A != B:
        raise InvarianteQuebrado("o livro ganhou, perdeu ou reordenou fontes")
    for a, b in zip(antes["FONTES"], depois["FONTES"]):
        if a != b and a["SOURCE_ID"] not in mudadas:
            raise InvarianteQuebrado("%s mudou sem autorizacao" % a["SOURCE_ID"])
    if {k: v for k, v in antes.items() if k != "FONTES"} != {k: v for k, v in depois.items() if k != "FONTES"}:
        raise InvarianteQuebrado("o cabecalho do livro mudou")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--decisao", required=True)
    ap.add_argument("--escrever", action="store_true")
    ap.add_argument("--livro", default=str(LIVRO))
    ap.add_argument("--tabela", default=str(TABELA))
    a = ap.parse_args(argv)
    texto = Path(a.livro).read_text(encoding="utf-8")
    fim = "\n" if texto.endswith("\n") else ""   # o livro real nao acaba em quebra de linha: nao se muda isso
    livro = json.loads(texto)
    tabela = json.loads(Path(a.tabela).read_text(encoding="utf-8"))
    try:
        depois, acoes = alinhar(livro, tabela, a.decisao)
    except (InvarianteQuebrado, RC.ReparoInvalido) as e:
        print("NADA ESCRITO:", e)
        return 4
    for x in acoes:
        print(json.dumps(x, ensure_ascii=False))
    if a.escrever and any(x["ACAO"] == "APLICA" for x in acoes):
        with open(a.livro, "w", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(depois, ensure_ascii=False, indent=1) + fim)
        print("escrito:", a.livro)
    return 0


if __name__ == "__main__":
    sys.exit(main())
