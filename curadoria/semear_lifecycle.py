#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SEMEAR O LIFECYCLE a partir do ESTADO REAL DE HOJE — nunca da fotografia.

    NAO SE INVENTA ESTADO. IMPORTA-SE O QUE JA FOI MEDIDO.
    E MEDIDO QUER DIZER: MEDIDO HOJE, CONTRA O REGISTO QUE A COLLECTION EXECUTA.

A primeira versao deste ficheiro (SOURCE CURATOR, `ef06d75e`) semeava a partir
de `READY-FOR-COLLECTION-V1.json`. Esse ficheiro estava certo no dia dele e
ficou obsoleto no dia seguinte: classifica 50 fontes YouTube como
CONTRACT_READY_ROUTE_BLOCKED pela rota `/feeds/videos.xml`, e a
BIG-COLLECTION-RELEASE provou depois a rota `/channel/<ID>/videos` — 50/50
PASS, e 41 delas colheram. Semear daquele ficheiro hoje destruiria essa prova.

    FOTOGRAFIA ANTIGA CERTA NO SEU DIA  !=  VERDADE DE HOJE
    ESTADOS ANTIGOS NAO VENCEM EVIDENCIA ATUAL.

Por isso este resemeador le UMA entrada: `ESTADO-ACTUAL-DAS-FONTES-V1.json`,
materializado por `estado_actual_das_fontes.mjs` a partir de:

    identidade + contrato + rota   regras/italy_contracts.mjs (motor de rota)
    ficha                          docs/fontes/ATLAS-DE-FONTES-EAME.md
    capacidade                     pedido/receitas.py (territorio com executor)
    canario mais recente           YOUTUBE-CANARIO-50 · SONDAGEM da tabela
    resultado da Big Collection    RUN-MANIFEST (BCR-2026-09-20)

E traduz cada linha para transicoes do livro, com a razao e a prova ao lado.

---------------------------------------------------------------------------
A TRADUCAO — vocabulario fechado de `lifecycle.ESTADOS`, nenhum termo novo

  contrato sem bloco executavel             -> CONTRACT_PENDING
  executavel, sem ficha no Atlas            -> SEMANTIC_REVIEW   (decisao humana)
  executavel + ficha + territorio, c/ prova -> CANARY_PENDING -> READY_FOR_COLLECTION
  ... e depois, o que a Big Collection viu:
      ROUTE_FAILURE   -> DEGRADED (owner COLLECTION) + REPAIR na fila
      CAPABILITY_GAP  -> DEGRADED (COLLECTION) -> CAPABILITY_BLOCK (CURATOR: e defeito da casa, B1)
      429             -> continua READY (esperar != avariar; a prova fica registada)
      SUCCESS         -> continua READY, e a corrida e a prova mais recente
  fonte so na fotografia (sem contrato aqui) -> CANARY_PENDING -> CONTRACTED_CANARY_FAILED
                                                (historia da missao 04, dita como historia)

UNKNOWN continua UNKNOWN: uma fonte sem prova de canario NAO e promovida —
fica CANARY_PENDING com CANARY na fila. Nada vira PASS nem BLOCK por omissao.

⚠️ Este script NAO le o campo STATE da fotografia para nenhuma fonte do
registo. Um teste garante isso.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))

import evidencia as EV    # noqa: E402
import fila as F          # noqa: E402
import lifecycle as LC    # noqa: E402

ESTADO_ACTUAL = RAIZ / "curadoria" / "ESTADO-ACTUAL-DAS-FONTES-V1.json"
RELATORIO_BCR = "RELATORIO-BIG-COLLECTION-RELEASE.md"

# O 429 e a plataforma a pedir tempo. Uma fonte READY que apanhou 429 numa
# corrida continua READY: a rota resolve, o portao permite, 41 irmas colheram.
# O que fica e a PROVA de que aconteceu, para quem decidir a repeticao (B10).
CLASSES_QUE_NAO_MUDAM_READY = {"SUCCESS", "RATE_LIMITED_429"}


def _head() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=str(RAIZ),
                              capture_output=True, text=True).stdout.strip() or "NAO SEI"
    except Exception:
        return "NAO SEI"


def _prova_mais_recente(f: dict) -> tuple[str | None, str]:
    """(evidence_ref, descricao) da prova mais recente de que a rota resolve.

    Preferencia: a corrida real da Big Collection com sucesso (e a prova mais
    forte e a mais recente); senao, o canario mais recente com PASS. Sem
    nenhuma das duas, nao ha prova — e sem prova nao ha READY.
    """
    bc = f.get("BIG_COLLECTION") or {}
    if bc.get("CLASSE") == "SUCCESS":
        return ("BCR-2026-09-20:%s" % bc["RUN_ID"],
                "corrida real com sucesso na Big Collection (%d observacoes, %d HEALTHY)"
                % (bc.get("OBSERVACOES", 0), bc.get("HEALTHY", 0)))
    can = f.get("CANARIO_MAIS_RECENTE") or {}
    if can.get("RESULTADO") == "PASS":
        return ("%s@%s" % (can.get("ORIGEM", "NAO SEI"), can.get("MEDIDO_EM", "NAO SEI")),
                "canario mais recente com PASS (%s)" % can.get("ORIGEM", "NAO SEI"))
    return None, "sem prova de canario nesta arvore"


def semear_uma(f: dict, head: str) -> str:
    """Traduz UMA fonte do registo actual em transicoes. Devolve o estado final."""
    sid = f["SOURCE_ID"]
    ref_registo = "regras/italy_contracts.mjs@%s" % head

    if not f["EXECUTAVEL"]:
        LC.registar(sid, LC.CONTRACT_PENDING, f["PORQUE_EXECUTAVEL"][:200],
                    evidence_ref=ref_registo)
        return LC.CONTRACT_PENDING

    if not f["FICHA_NO_ATLAS"]:
        LC.registar(sid, LC.SEMANTIC_REVIEW,
                    "contrato executavel sem ficha no Atlas — decisao humana, "
                    "nao do worker", evidence_ref="docs/fontes/ATLAS-DE-FONTES-EAME.md@%s" % head)
        return LC.SEMANTIC_REVIEW

    if f.get("TERRITORIO_COM_EXECUTOR") is False:
        LC.registar(sid, LC.CAPABILITY_BLOCK,
                    "territorio %s sem executor em pedido/receitas.py" % f["TERRITORY"],
                    evidence_ref="pedido/receitas.py@%s" % head)
        return LC.CAPABILITY_BLOCK

    LC.registar(sid, LC.CANARY_PENDING,
                "contrato executavel (motor de rota), ficha no Atlas, territorio com executor",
                evidence_ref=ref_registo)

    ref, porque = _prova_mais_recente(f)
    if not ref:
        # A casa contava-a como READY pela regra (contrato + ficha + executor),
        # mas nesta arvore nao ha prova de canario com PASS — e a Big Collection
        # viu-a falhar. Sem prova nao ha READY; fica a espera do canario, com a
        # observacao da Collection guardada para quem for reparar.
        bc = f.get("BIG_COLLECTION") or {}
        if bc:
            EV.guardar(sid, "BIG_COLLECTION", {
                "RUN_ID": bc.get("RUN_ID"), "CLASSE": bc.get("CLASSE"),
                "MOTIVO": bc.get("MOTIVO", ""),
                "DECISAO": "nao promovida: sem canario PASS nesta arvore; CANARY na fila"})
        F.enfileirar(sid, F.CANARY, priority=50,
                     motivo="sem prova de canario nesta arvore%s" % (
                         "; a Big Collection viu %s" % bc.get("CLASSE") if bc else ""))
        return LC.CANARY_PENDING

    LC.registar(sid, LC.READY_FOR_COLLECTION, porque, evidence_ref=ref)

    bc = f.get("BIG_COLLECTION") or {}
    classe = bc.get("CLASSE")
    if not classe or classe in CLASSES_QUE_NAO_MUDAM_READY:
        if classe == "RATE_LIMITED_429":
            EV.guardar(sid, "BIG_COLLECTION", {
                "RUN_ID": bc["RUN_ID"], "CLASSE": classe, "MOTIVO": bc.get("MOTIVO", ""),
                "DECISAO": "continua READY: 429 e espera, nao avaria (RELATORIO §9 B10)"})
        return LC.READY_FOR_COLLECTION

    # A Collection VIU a fonte falhar. Na nova divisao isso e SOURCE_REPAIR_NEEDED:
    # a Collection so tem um verbo, e este e ele.
    LC.registar(sid, LC.DEGRADED,
                "Collection reportou %s em BCR-2026-09-20: %s" % (classe, bc.get("MOTIVO", "")[:140]),
                owner=LC.OWNER_COLLECTION, evidence_ref="BCR-2026-09-20:%s" % bc["RUN_ID"])

    if classe == "CAPABILITY_GAP":
        # O Curator faz a triagem: o defeito e da casa (pasta com `?` no
        # Windows, B1), nao da fonte. Parada ate haver capacidade nova.
        ref2 = EV.guardar(sid, "TRIAGEM", {
            "RUN_ID": bc["RUN_ID"], "CLASSE": classe, "MOTIVO": bc.get("MOTIVO", ""),
            "DONO": "colector italiano (pastaDoDocumento)", "REFERENCIA": RELATORIO_BCR + " §9 B1"})
        LC.registar(sid, LC.CAPABILITY_BLOCK,
                    "defeito da casa, nao da fonte: DOCUMENT_ID com `?` nao vira pasta no "
                    "Windows (B1). Sai daqui por capacidade nova, nao por tentar de novo",
                    evidence_ref=ref2)
        return LC.CAPABILITY_BLOCK

    F.enfileirar(sid, F.REPAIR, priority=80,
                 motivo="degradada na Collection (%s): %s" % (classe, bc.get("MOTIVO", "")[:100]))
    return LC.DEGRADED


def semear_so_na_foto(s: dict) -> str:
    """Fonte que o curator contratou e canariou, mas que NAO esta no registo
    da Collection. Importa-se a HISTORIA, dita como historia, e nada mais."""
    sid = s["SOURCE_ID"]
    ref = "HISTORIA:%s" % s["ORIGEM"]
    LC.registar(sid, LC.CANARY_PENDING, "contrato do curator (fora do registo da Collection)",
                evidence_ref=ref)
    if s["ESTADO_NA_FOTO"] == "CONTRACTED_CANARY_FAILED":
        LC.registar(sid, LC.CONTRACTED_CANARY_FAILED,
                    "canario da missao 04 nao trouxe item com identidade; sem contrato "
                    "no registo da Collection, o worker nao a pode canariar aqui",
                    evidence_ref=ref)
        return LC.CONTRACTED_CANARY_FAILED
    # Qualquer outro estado da fotografia NAO se importa como vigente: fica
    # CANARY_PENDING, que e a verdade — falta medir hoje.
    return LC.CANARY_PENDING


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--recomecar", action="store_true",
                    help="apaga LIVRO, FILA e EVIDENCIA antes de semear (recalculo total)")
    a = ap.parse_args()

    if not ESTADO_ACTUAL.exists():
        print("ESTADO_ACTUAL ausente: node curadoria/estado_actual_das_fontes.mjs")
        return 2
    d = json.loads(ESTADO_ACTUAL.read_text(encoding="utf-8"))
    head = d.get("HEAD") or _head()

    if a.recomecar:
        for p in (LC.LIVRO, F.FILA, EV.EVIDENCIA):
            if p.exists():
                p.unlink()

    ja = LC.snapshot()
    novas, saltadas, finais = 0, 0, {}
    for f in d["FONTES"]:
        if f["SOURCE_ID"] in ja:
            saltadas += 1
            continue
        finais[f["SOURCE_ID"]] = semear_uma(f, head)
        novas += 1
    for s in d.get("SO_NA_FOTO", []):
        if s["SOURCE_ID"] in ja:
            saltadas += 1
            continue
        finais[s["SOURCE_ID"]] = semear_so_na_foto(s)
        novas += 1

    print("ESTADO_ACTUAL_HEAD = %s" % head)
    print("SEMEADAS   = %d" % novas)
    print("JA_EXISTIAM= %d" % saltadas)
    print("FONTES     = %s" % json.dumps(
        {k: v for k, v in LC.metricas().items() if v}, ensure_ascii=False))
    print("FILA       = %s" % json.dumps(F.metricas(), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
