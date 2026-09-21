#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O CICLO DE VIDA DE UMA FONTE — estados, transicoes e o livro que os guarda.

    DESCOBERTA != QUALIFICACAO != CONTRATO != CANARIO != READY != COLETA

Este modulo e o DONO do estado de uma fonte dentro do SOURCE CURATOR. Nao
coleta, nao cunha RUN_ID, nao escreve RAW, nao toca Admission nem Sala.

    QUEM PROMOVE PARA READY E O CURATOR. SO ELE.

A Collection consome READY_FOR_COLLECTION e devolve SOURCE_REPAIR_NEEDED.
Nao promove, nao repara, nao constroi contrato. Essa fronteira esta gravada
em `transicao_permitida()` e um teste tenta viola-la.

---------------------------------------------------------------------------
PORQUE O LIVRO E APPEND-ONLY

O estado de uma fonte e uma CONSEQUENCIA das transicoes, nunca um campo que
alguem sobrescreve. Guardar so o estado atual perde a razao pela qual ele
mudou — e a razao e o que permite auditar uma promocao meses depois.

    ESTADO ATUAL = ultima transicao aplicada, relida do livro.

Cada linha carrega: SOURCE_ID, PREVIOUS_STATE, NEW_STATE, REASON,
EVIDENCE_REF, OBSERVED_AT, OWNER, VERSION. Sem EVIDENCE_REF nao ha promocao
a READY: uma promocao sem prova e uma opiniao com carimbo.
"""
from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
LIVRO = RAIZ / "curadoria" / "LIFECYCLE-LEDGER-V1.json"

CONTRATO = "SOURCE_LIFECYCLE/v1"
OWNER_CURATOR = "SOURCE_CURATOR"
OWNER_COLLECTION = "COLLECTION"


# ---------------------------------------------------------------------------
# OS ESTADOS
#
# Nomes reaproveitados do vocabulario que a missao 04 ja escreveu em
# READY-FOR-COLLECTION-V1.json (CONTRACT_READY_ROUTE_BLOCKED,
# READY_FOR_COLLECTION, CONTRACTED_CANARY_FAILED). Nao se inventou sinonimo
# para conceito que ja tinha palavra nesta casa.
# ---------------------------------------------------------------------------
DISCOVERED = "DISCOVERED"
QUALIFYING = "QUALIFYING"
CONTRACT_PENDING = "CONTRACT_PENDING"
CANARY_PENDING = "CANARY_PENDING"
RETRY_AFTER = "RETRY_AFTER"
READY_FOR_COLLECTION = "READY_FOR_COLLECTION"

DEGRADED = "DEGRADED"
REPAIRING = "REPAIRING"

POLICY_BLOCK = "POLICY_BLOCK"
AUTH_BLOCK = "AUTH_BLOCK"
CAPABILITY_BLOCK = "CAPABILITY_BLOCK"
CONTRACT_READY_ROUTE_BLOCKED = "CONTRACT_READY_ROUTE_BLOCKED"
CONTRACTED_CANARY_FAILED = "CONTRACTED_CANARY_FAILED"
SEMANTIC_REVIEW = "SEMANTIC_REVIEW"
UNKNOWN = "UNKNOWN"

# ⚠️ O ESTADO MEDIDO CONTRA UMA ROTA QUE JA NAO E A ROTA.
#
# Medido: as 50 fontes YouTube foram marcadas CONTRACT_READY_ROUTE_BLOCKED
# porque `feeds/videos.xml` esta em Disallow. Entretanto a integracao
# (5920d77d) deu-lhes uma rota NOVA — CANAL_PUBLICO_YOUTUBE_V1, que nao usa
# o feed. O bloqueio continua verdadeiro sobre a rota velha e passou a ser
# irrelevante sobre a fonte.
#
#     UM VEREDITO ENVELHECE QUANDO A PERGUNTA MUDA.
#
# Declarar READY seria promover com dado obsoleto; manter BLOCKED seria
# condenar por uma rota que ninguem ja usa. Nenhuma das duas e verdade, e
# por isso existe um terceiro nome: precisa de ser remedida contra a rota
# de hoje. Nao e um bloqueio nem uma prontidao — e uma divida de medicao.
RECONCILIATION_REQUIRED = "RECONCILIATION_REQUIRED"

ESTADOS = frozenset({
    DISCOVERED, QUALIFYING, CONTRACT_PENDING, CANARY_PENDING, RETRY_AFTER,
    READY_FOR_COLLECTION, DEGRADED, REPAIRING, POLICY_BLOCK, AUTH_BLOCK,
    CAPABILITY_BLOCK, CONTRACT_READY_ROUTE_BLOCKED, CONTRACTED_CANARY_FAILED,
    SEMANTIC_REVIEW, UNKNOWN, RECONCILIATION_REQUIRED,
})

# Estados terminais para o worker: nao geram trabalho automatico novo.
# BLOQUEADO NAO E MORTO. Sai daqui por decisao humana ou capacidade nova,
# nunca por o worker tentar outra vez a mesma coisa.
PARADOS = frozenset({
    POLICY_BLOCK, AUTH_BLOCK, CAPABILITY_BLOCK,
    CONTRACT_READY_ROUTE_BLOCKED, SEMANTIC_REVIEW,
})

# Os unicos estados a partir dos quais se pode PROMOVER para READY.
# Uma fonte nao salta de DISCOVERED para READY: teria de existir um canario
# que ninguem correu.
PODEM_PROMOVER = frozenset({CANARY_PENDING, REPAIRING})


def agora() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# A FRONTEIRA DE OWNER — a lei que esta missao existe para gravar
# ---------------------------------------------------------------------------
def transicao_permitida(anterior: str, novo: str, owner: str) -> tuple[bool, str]:
    """Quem pode mover uma fonte, de onde, para onde.

        A COLLECTION NAO PROMOVE FONTE. NUNCA.

    A Collection so tem UM verbo neste livro: sinalizar que uma fonte que
    lhe foi entregue como READY falhou na mao dela. Tudo o resto e Curator.
    """
    if novo not in ESTADOS:
        return False, "estado desconhecido: %s" % novo
    if anterior is not None and anterior not in ESTADOS:
        return False, "estado anterior desconhecido: %s" % anterior

    if owner == OWNER_COLLECTION:
        if anterior == READY_FOR_COLLECTION and novo == DEGRADED:
            return True, "a Collection reporta falha de uma fonte que era READY"
        return False, ("a Collection so pode marcar READY_FOR_COLLECTION -> "
                       "DEGRADED; pediu %s -> %s" % (anterior, novo))

    if owner != OWNER_CURATOR:
        return False, "owner desconhecido: %s" % owner

    if novo == READY_FOR_COLLECTION and anterior not in PODEM_PROMOVER:
        return False, ("READY exige canario: so se promove a partir de %s, "
                       "e veio de %s" % (sorted(PODEM_PROMOVER), anterior))

    # REPARO EXIGE NOVO CANARIO: de DEGRADED nao se volta direto a READY.
    if anterior == DEGRADED and novo == READY_FOR_COLLECTION:
        return False, "uma fonte degradada volta por REPAIRING + canario, nao por decreto"

    return True, "ok"


def _ler_bruto() -> dict:
    if not LIVRO.exists():
        return {"DATASET": "LIFECYCLE-LEDGER-V1", "CONTRATO": CONTRATO,
                "LEI": ("append-only. O estado de uma fonte e a ultima transicao, "
                        "nunca um campo sobrescrito. A Collection nao promove."),
                "TRANSICOES": []}
    return json.loads(LIVRO.read_text(encoding="utf-8"))


def _gravar(d: dict) -> None:
    """Escrita atomica: temporario na mesma filesystem, fsync, os.replace.

    Um worker que morre a meio de uma escrita nao pode deixar o livro
    truncado — seria perder o trabalho que a FASE 3 exige preservar.
    """
    LIVRO.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(LIVRO.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(d, fh, ensure_ascii=False, indent=1)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, LIVRO)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def estado_de(source_id: str, livro: dict | None = None) -> str | None:
    """O estado atual: a ultima transicao registada. None = fonte desconhecida."""
    d = livro if livro is not None else _ler_bruto()
    ultimo = None
    for t in d["TRANSICOES"]:
        if t["SOURCE_ID"] == source_id:
            ultimo = t
    return ultimo["NEW_STATE"] if ultimo else None


# As oito chaves que TODA a linha tem. `extra` nunca as sobrescreve: a
# proveniencia da reconciliacao (RECONCILIACAO-V1) vive ao lado delas, nao
# em cima delas.
CHAVES_CANONICAS = frozenset({
    "SOURCE_ID", "PREVIOUS_STATE", "NEW_STATE", "REASON", "EVIDENCE_REF",
    "OBSERVED_AT", "OWNER", "VERSION", "NEXT_ATTEMPT_AT",
})


def registar(source_id: str, novo: str, reason: str, *,
             owner: str = OWNER_CURATOR, evidence_ref: str | None = None,
             next_attempt_at: str | None = None,
             extra: dict | None = None) -> dict:
    """Move uma fonte de estado. Devolve a linha gravada.

    Levanta ValueError quando a transicao e proibida — falhar fechado, nunca
    gravar uma transicao ilegal com um aviso ao lado.

    `extra`: campos de proveniencia (ex.: IMPORTADO_DE, RECONCILIACAO) que
    ficam NA MESMA LINHA, ao lado das chaves canonicas. Uma chave canonica em
    `extra` e recusada — o trilho nao reescreve o que a linha ja diz.
    """
    d = _ler_bruto()
    anterior = estado_de(source_id, d)

    ok, porque = transicao_permitida(anterior, novo, owner)
    if not ok:
        raise ValueError("TRANSICAO RECUSADA [%s]: %s" % (source_id, porque))

    # READY SEM PROVA NAO E READY.
    if novo == READY_FOR_COLLECTION and not evidence_ref:
        raise ValueError("TRANSICAO RECUSADA [%s]: READY exige EVIDENCE_REF "
                         "(o canario que resolveu)" % source_id)

    linha = {
        "SOURCE_ID": source_id,
        "PREVIOUS_STATE": anterior,
        "NEW_STATE": novo,
        "REASON": reason,
        "EVIDENCE_REF": evidence_ref,
        "OBSERVED_AT": agora(),
        "OWNER": owner,
        "VERSION": CONTRATO,
    }
    if next_attempt_at:
        linha["NEXT_ATTEMPT_AT"] = next_attempt_at
    if extra:
        colisao = sorted(set(extra) & CHAVES_CANONICAS)
        if colisao:
            raise ValueError("TRANSICAO RECUSADA [%s]: `extra` tenta sobrescrever "
                             "chave canonica %s" % (source_id, colisao))
        linha.update(extra)

    d["TRANSICOES"].append(linha)
    _gravar(d)
    return linha


def snapshot() -> dict:
    """Estado atual de todas as fontes conhecidas: {SOURCE_ID: ESTADO}."""
    d = _ler_bruto()
    est: dict[str, str] = {}
    for t in d["TRANSICOES"]:
        est[t["SOURCE_ID"]] = t["NEW_STATE"]
    return est


def metricas() -> dict:
    """FASE 13 — contadores por estado, com os zeros visiveis.

    Um estado ausente da tabela le-se como «nao se aplica». Pre-semear todos
    a 0 para que se leia «mediu-se, e deu zero».
    """
    est = snapshot()
    m = {e: 0 for e in sorted(ESTADOS)}
    for e in est.values():
        m[e] = m.get(e, 0) + 1
    m["SOURCES_TOTAL"] = len(est)
    return m


def historia(source_id: str) -> list[dict]:
    return [t for t in _ler_bruto()["TRANSICOES"] if t["SOURCE_ID"] == source_id]
