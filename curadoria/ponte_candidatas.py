#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PONTE DE CANDIDATAS — curadoria/ponte_candidatas.py

Liga candidatas/FONTES-CANDIDATAS.json à fila do Source Curator.

    A PORTA ENCHE-SE. NINGUEM A ESVAZIA.

Este ficheiro fecha esse defeito. Para cada candidata que ainda não entrou no
curator, decide um de três destinos:

    LINKEDIN / INSTAGRAM  → POLICY_BLOCK  no lifecycle (barrada por TOS)
    FACEBOOK              → CAPABILITY_BLOCK no lifecycle (sem capacidade)
    BASE_OFICIAL /
    ORGANIZACAO /
    IMPRENSA /
    CIENCIA /
    YOUTUBE / OUTRO       → QUALIFY na fila (aguarda SOURCE_ID e caracterização)
    tipo não reconhecido  → UNKNOWN no ledger (não decide, não inventa)

Idempotente: correr duas vezes não cria trabalho duplicado. A guarda é o
BRIDGE-LEDGER-V1.json — uma lista append-only dos CANDIDATA_IDs já processados.

Gaveta justificada (AGENTS.md):
    A ponte faz trabalho do SOURCE CURATOR — classifica fontes no lifecycle e
    enfileira tarefas no queue. Pertence à mesma gaveta dos outros módulos do
    curator: curadoria/. O CANDIDATA_ID é usado como identificador temporário
    no lifecycle para as barradas (que nunca chegarão a ter SOURCE_ID real) e
    na fila como chave de rastreamento para QUALIFY. Não é CANDIDATA_ID
    promovido a SOURCE_ID: é uma chave de rastreamento de ciclo de vida
    distinta do formato SOURCE_ID (IT-Txx-xxx).
"""
from __future__ import annotations

import json
import os
import re
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))
sys.path.insert(0, str(RAIZ / "candidatas"))

import fila as F          # noqa: E402
import lifecycle as LC    # noqa: E402
import fonte_nova as FN   # noqa: E402

# Caminhos próprios da ponte — sobreponíveis em testes com importlib.reload
CARACT = RAIZ / "curadoria" / "SOURCE-CHARACTERIZATION-V1.json"
LEDGER = RAIZ / "curadoria" / "BRIDGE-LEDGER-V1.json"

# Muda quando a regra de decisao muda; entra na assinatura do FEEDER.
REGRA_VERSAO = "B4-2026-09-23-needs-more-sampling"

# Tipos sociais: têm barreira de política ou capacidade conhecida e documentada.
# Insistir no que a política barra não é persistência — é contorno.
# O worker já sabe disto (NAO_INSISTIR = {POLICY, AUTH, ROBOTS}); a ponte não
# pode ser a porta das traseiras.
POLITICA = frozenset({"LINKEDIN", "INSTAGRAM"})
CAPACIDADE = frozenset({"FACEBOOK"})
ENFILAVEIS = frozenset({"BASE_OFICIAL", "ORGANIZACAO", "IMPRENSA",
                        "CIENCIA", "YOUTUBE", "OUTRO"})

_MOTIVO = {
    "LINKEDIN":  ("LINKEDIN_POLICY: coleta automatizada proibida pelos TOS da "
                  "plataforma. Worker marcado NAO_INSISTIR."),
    "INSTAGRAM": ("INSTAGRAM_POLICY: coleta automatizada proibida pelos TOS da "
                  "plataforma. Worker marcado NAO_INSISTIR."),
    "FACEBOOK":  ("FACEBOOK_CAPABILITY_BLOCK: sem capacidade de coleta automatizada "
                  "para Facebook nesta instalacao."),
}


# D24 (dono real, 24/09 ~12:55, por escrito): perfis de PESSOAS do agro sao autorizados.
# Um LinkedIn/Instagram de pessoa COM prova oficial de identidade (D21/D24: pagina ou CV
# oficial que liga a pessoa ao perfil, escrita na NOTA pela porta) vai para QUALIFY como
# qualquer fonte; SEM essa prova continua POLICY_BLOCK. Mesma regra que o guarda de
# tests/test_fila_italia_decisoes.py (_PROVA_D24).
_PROVA_D24 = re.compile(r"(PROVA_IDENTIDADE=|IDENTIDADE: a pagina oficial da pessoa )https?://\S+")
MOTIVO_D24 = ("D24 (dono 24/09): perfil de pessoa com prova oficial de identidade — "
              "vai a qualificacao, nao a POLICY_BLOCK")


def tem_prova_d24(c: dict) -> bool:
    return bool(_PROVA_D24.search(c.get("NOTA") or ""))


def _agora() -> str:
    return datetime.now(timezone.utc).isoformat()


def _carregar_ledger() -> dict:
    if not LEDGER.exists():
        return {
            "DATASET": "BRIDGE-LEDGER-V1",
            "LEI": ("Registo append-only da ponte. "
                    "Garante que correr duas vezes nao cria trabalho duplicado. "
                    "Chave = CANDIDATA_ID."),
            "PROCESSADAS": {},
        }
    return json.loads(LEDGER.read_text(encoding="utf-8"))


def _gravar_ledger(d: dict) -> None:
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(LEDGER.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(json.dumps(d, ensure_ascii=False, indent=2) + "\n")
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, str(LEDGER))
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def _ja_no_curator() -> set:
    """CANDIDATA_IDs que já passaram pela caracterização E não precisam de mais trabalho.

    NEEDS_MORE_SAMPLING fica de fora: passou pela caracterização mas não chegou ao
    fim. A ponte tem de os enfileirar — alimentar_fila não os apanha (sem SOURCE_ID
    ainda) e o sinal de discovery conta-os como backlog real.

    ⚠️ GUARDA: só excluir NEEDS_MORE_SAMPLING. Qualquer outro FINAL_STATE na
    caracterização (PROMOTE, BLOCK, ENDPOINT_OF_EXISTING_SOURCE, etc.) significa
    que o curator já decidiu — a ponte não volta a tocar neles.
    """
    if not CARACT.exists():
        return set()
    data = json.loads(CARACT.read_text(encoding="utf-8"))
    return {f["CANDIDATE_ID"] for f in data.get("FONTES", [])
            if f.get("CANDIDATE_ID")
            and f.get("FINAL_STATE") != "NEEDS_MORE_SAMPLING"}


def processar() -> dict:
    """
    Corre a ponte sobre o backlog completo. Devolve métricas.

    Idempotente: a segunda chamada produz os mesmos resultados e NÃO cria
    trabalho duplicado — a guarda é o BRIDGE-LEDGER (chave = CANDIDATA_ID).

    Devolve um dict com:
      CANDIDATAS_LIDAS, ENFILEIRADAS, CLASSIFICADAS_BARRADAS, UNKNOWN,
      JA_PROCESSADAS_IGNORADAS, TAREFAS_CRIADAS, SOCIAIS_ENFILEIRADAS,
      QUEUE_DEPTH_ANTES, QUEUE_DEPTH_DEPOIS
    """
    ja_curator = _ja_no_curator()
    ledger = _carregar_ledger()
    # ⚠️ GUARDA DE IDEMPOTÊNCIA — não remover nem contornar.
    # Muter esta linha num RED TEAM deve fazer o teste de 2ª corrida REPROVAR.
    ja_ledger: set = set(ledger["PROCESSADAS"].keys())

    porta_doc = FN.carregar()
    candidatas = porta_doc["CANDIDATAS"]
    porta_modificada = False

    m: dict = {
        "CANDIDATAS_LIDAS": 0,
        "ENFILEIRADAS": 0,
        "CLASSIFICADAS_BARRADAS": 0,
        "UNKNOWN": 0,
        "JA_PROCESSADAS_IGNORADAS": 0,
        "TAREFAS_CRIADAS": 0,
        "SOCIAIS_ENFILEIRADAS": 0,
        "PESSOAS_D24_ENFILEIRADAS": 0,
        "D24_REAVALIADAS": 0,
        "QUEUE_DEPTH_ANTES": F.metricas()["QUEUE_TOTAL"],
    }

    # D24 — REAVALIACAO, uma so vez por candidata: perfis de pessoa COM prova que a ponte
    # antiga (sem D24) pos em POLICY_BLOCK saem por decisao humana escrita (D24), com a
    # transicao no livro e o bloqueio antigo guardado. O ledger passa a QUALIFY, por isso
    # a segunda corrida ja nao os ve aqui.
    for c in candidatas:
        cid = c["CANDIDATA_ID"]
        e = ledger["PROCESSADAS"].get(cid)
        if (not e or e.get("DESTINO") != "POLICY_BLOCK"
                or c.get("TIPO") not in POLITICA or not tem_prova_d24(c)):
            continue
        if LC.estado_de(cid) == LC.POLICY_BLOCK:
            LC.registar(cid, LC.QUALIFYING, MOTIVO_D24, evidence_ref="BRIDGE:D24")
        tarefa = F.enfileirar(cid, F.QUALIFY, priority=30,
                              motivo=f"bridge: {cid} ({c.get('TIPO')}) D24 — sai do "
                                     "POLICY_BLOCK, aguarda qualificacao pelo curator")
        if c.get("MOTIVO_DO_BLOQUEIO"):
            c["BLOQUEIO_ANTERIOR"] = c.pop("MOTIVO_DO_BLOQUEIO")
        c["ESTADO"] = "EM_ANALISE"
        c["MOTIVO_DO_DESBLOQUEIO"] = MOTIVO_D24
        e.update({"DESTINO": "QUALIFY", "DESTINO_ANTERIOR": "POLICY_BLOCK",
                  "REAVALIADO_D24_EM": _agora(), "MOTIVO": MOTIVO_D24,
                  "TASK_ID": tarefa.get("TASK_ID"), "TASK_STATUS": tarefa.get("STATUS")})
        porta_modificada = True
        m["D24_REAVALIADAS"] += 1

    for c in candidatas:
        cid = c["CANDIDATA_ID"]
        m["CANDIDATAS_LIDAS"] += 1

        # Já entrou no curator por outro caminho — ignorar
        if cid in ja_curator:
            m["JA_PROCESSADAS_IGNORADAS"] += 1
            continue

        # ⚠️ GUARDA DE IDEMPOTÊNCIA — já processado por esta ponte
        if cid in ja_ledger:
            m["JA_PROCESSADAS_IGNORADAS"] += 1
            continue

        tipo = c.get("TIPO", "")
        entrada: dict = {
            "CANDIDATA_ID": cid,
            "TIPO": tipo,
            "NOME": c.get("NOME", ""),
            "PROCESSADO_EM": _agora(),
        }

        if tipo in POLITICA and not tem_prova_d24(c):
            motivo = _MOTIVO[tipo]
            LC.registar(cid, LC.POLICY_BLOCK, motivo,
                        evidence_ref="BRIDGE:candidatas/FONTES-CANDIDATAS.json")
            # D15 (23/09, bot Luciano por delegacao do dono): os TOS proibem —
            # nem RECUSADA nem EM_ANALISE, POLICY_BLOCK, e a prova e o trecho dos
            # termos (endereco e data), nunca uma sonda de 429.
            c["ESTADO"] = "POLICY_BLOCK"
            c["MOTIVO_DO_BLOQUEIO"] = motivo
            ev = FN.evidencia_da_politica(tipo)
            if ev:
                if c.get("EVIDENCIA") and "TERMOS " not in c["EVIDENCIA"]:
                    c.setdefault("EVIDENCIA_HISTORICA", c["EVIDENCIA"])
                c["EVIDENCIA"] = FN.texto_da_evidencia(ev)
                c["EVIDENCIA_POLITICA"] = ev
            porta_doc.setdefault("ESTADOS", {}).setdefault("POLICY_BLOCK", FN.ESTADO_POLICY_BLOCK)
            porta_modificada = True
            entrada.update({"DESTINO": "POLICY_BLOCK", "MOTIVO": motivo})
            m["CLASSIFICADAS_BARRADAS"] += 1

        elif tipo in CAPACIDADE:
            motivo = _MOTIVO[tipo]
            LC.registar(cid, LC.CAPABILITY_BLOCK, motivo,
                        evidence_ref="BRIDGE:candidatas/FONTES-CANDIDATAS.json")
            # D13 (23/09, bot Luciano por delegacao do dono): sem capacidade NAO
            # e recusa. A fonte pode ser boa; falta-nos o adaptador. Fica com o
            # seu proprio estado, e o motivo no campo do bloqueio.
            c["ESTADO"] = "CAPABILITY_BLOCK"
            c["MOTIVO_DO_BLOQUEIO"] = motivo
            # o estado entra no vocabulario que a propria porta declara
            porta_doc.setdefault("ESTADOS", {}).setdefault(
                "CAPABILITY_BLOCK", FN.ESTADO_CAPABILITY_BLOCK)
            porta_modificada = True
            entrada.update({"DESTINO": "CAPABILITY_BLOCK", "MOTIVO": motivo})
            m["CLASSIFICADAS_BARRADAS"] += 1

        elif tipo in ENFILAVEIS or tipo in POLITICA:
            # tipo in POLITICA aqui = perfil de pessoa COM prova D24 (o ramo acima
            # apanhou os que nao a tem)
            d24 = tipo in POLITICA
            tarefa = F.enfileirar(
                cid, F.QUALIFY, priority=30,
                motivo=(f"bridge: {cid} ({tipo}) sem SOURCE_ID — "
                        "aguarda qualificacao pelo curator"
                        + (" · " + MOTIVO_D24 if d24 else "")),
            )
            if d24:
                entrada["MOTIVO"] = MOTIVO_D24
                m["PESSOAS_D24_ENFILEIRADAS"] += 1
            # Tarefa nova = criada agora pela ponte (não existia antes)
            nova = (tarefa.get("ATTEMPTS", 0) == 0
                    and tarefa.get("STATUS") == F.PENDING)
            if nova:
                m["TAREFAS_CRIADAS"] += 1
            c["ESTADO"] = "EM_ANALISE"
            porta_modificada = True
            entrada.update({
                "DESTINO": "QUALIFY",
                "TASK_ID": tarefa.get("TASK_ID"),
                "TASK_STATUS": tarefa.get("STATUS"),
            })
            m["ENFILEIRADAS"] += 1

        else:
            entrada.update({
                "DESTINO": "UNKNOWN",
                "MOTIVO": (f"tipo desconhecido: {tipo!r} — "
                           "nao e possivel decidir destino sem inventar"),
            })
            c["ESTADO"] = "EM_ANALISE"
            porta_modificada = True
            m["UNKNOWN"] += 1

        ledger["PROCESSADAS"][cid] = entrada

    _gravar_ledger(ledger)
    if porta_modificada:
        FN.gravar(porta_doc)

    m["QUEUE_DEPTH_DEPOIS"] = F.metricas()["QUEUE_TOTAL"]
    return m


def main() -> int:
    m = processar()
    print(json.dumps(m, ensure_ascii=False, indent=2))
    if m["SOCIAIS_ENFILEIRADAS"] > 0:
        print("ERRO: fontes sociais foram enfileiradas — violacao de politica",
              file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
