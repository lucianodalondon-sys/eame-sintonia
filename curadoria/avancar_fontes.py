#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AVANCAR — levar cada fonte ja achada ate PRONTA (CUR-PRONTA, D28, 24/09/2026).

    «eu pensei que o robo de fontes faria todo esse trabalho pesado e levar a
     fonte ate ficar pronta, e nao ficar procurando procurando e depois ela
     para» — o dono, D28.

Medido na copia do livro vivo (24/09 09:09): 1040 fontes no livro e ZERO com
tarefa aberta na fila. O ciclo vivo (`gatilho_discovery.talvez_alimentar`)
alimenta tres coisas — REVIVER (FAILED por transporte), REVALIDAR (so as
ELEGIVEIS com prova velha) e a PONTE (candidata nova -> QUALIFY) — e depois
vai procurar fontes novas. Quem ja estava no livro e parou num estado que
nenhuma dessas tres olha, fica la para sempre. O `alimentar_fila.py` sabia
por alguns deles na fila, mas so corre a mao.

Este modulo e a lista do que AVANCA e ninguem pedia, e so isso. Cada regra
tem um estado de partida, uma tarefa que o worker JA sabe executar, e um
motivo escrito. Nada aqui vai a rede, nada promove, nada escreve no livro de
estados: so poe trabalho na fila (idempotente por fonte+tarefa aberta).

    REGRA            ESTADO / CONDICAO                               TAREFA
    READY_LEGACY     READY pela regua antiga, com contrato do robo   VALIDATE_ROUTE
    LEGACY_COLETOR   READY pela regua antiga, SEM contrato do robo,  BUILD_CONTRACT
                     mas com linha na tabela do coletor               (importa a linha)
    DEGRADADA        DEGRADED / REPAIRING, com contrato do robo      REPAIR
    DEGRADADA_COLETOR  DEGRADED sem contrato do robo, com linha na   BUILD_CONTRACT
                     tabela do coletor (as 18 da BCR-2026-09-20)      (importa a linha)
    SEM_CONTRATO     CONTRACT_PENDING                                BUILD_CONTRACT
    ADIADA           RETRY_AFTER, com contrato                       VALIDATE_ROUTE
    SOCIAL_QUALIFY   candidata YOUTUBE sem SOURCE_ID que a ponte     QUALIFY
                     nao volta a ver (caracterizada ONBOARDING_READY)

⚠️ O QUE NAO E DESTE MODULO — E TEM DONO:
  CONTRACTED_CANARY_FAILED, CANARY_PENDING sem tarefa, e as QUALIFY de YouTube
  barradas pelo texto antigo: REPARO-FONTES-V1 (R1), `reparar_contrato.py` +
  o nivel REPARAR do gatilho. Duplicar aqui daria dois donos a enfileirar a
  mesma fonte com tarefas diferentes.
  SEMANTIC_REVIEW: decisao semantica (canal DECISOES-SEMANTICAS), nao maquina.
  POLICY/AUTH/CAPABILITY/ROUTE_BLOCKED: `lifecycle.PARADOS` — saem por decisao
  ou capacidade nova, nunca por insistir.
  READY pela regua antiga com contrato YOUTUBE_CHANNEL_FEED (41 medidas): o feed
  esta em Disallow — re-medir pelo feed so as mandaria para ROUTE_BLOCKED. O
  caminho delas e a rota do Scrap (SCRAP_FASE, SOC2 bloco 4) e o canario do
  Scrap no runner; ficam contadas no FUNIL como SOCIAL_LEGACY.
  UNKNOWN / RECONCILIATION_REQUIRED: sem tarefa que as avance — buraco nomeado
  no FUNIL (`funil_do_curador.py`), nao resolvido a martelo.

UMA VOLTA NAO ESVAZIA O LIVRO: `AVANCAR_POR_VOLTA` por volta, pela ordem da
tabela acima (reparo e revalidacao antes de identidade nova), e cada fonte so
volta a entrar depois de `RETOMA_S` desde a ultima tarefa dela desse tipo.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))

import fila as F          # noqa: E402
import lifecycle as LC    # noqa: E402

# AVANCAR_POR_VOLTA = 20
#   WHY: o mesmo teto do REPARAR da R1. Uma volta do gatilho so acontece com a
#   fila elegivel <= QUEUE_LOW_WATERMARK (10); 20 tarefas de canario ~ 40
#   pedidos, abaixo de uma DISCOVERY (250).
AVANCAR_POR_VOLTA = 20
# RETOMA_S = 86400
#   WHY: o degrau do meio do ritmo «intermitente» da fila (6h/24h/72h). Uma
#   fonte cuja tarefa deste tipo acabou ha menos de um dia foi vista hoje.
RETOMA_S = 86400
# JANELA_BONUS = 15
#   WHY (D29): a fonte de janela passa a frente de toda a tarefa da mesma regra e
#   da regra de baixo (os degraus de REGRAS distam 5-25), sem passar a frente de
#   um REPAIR de degradada que nao e janela (80) com uma VALIDATE_ROUTE (55+15=70).
JANELA_BONUS = 15

TABELA_DO_COLETOR = RAIZ / "regras" / "italy_contracts_onboarded.json"
CONTRATOS = RAIZ / "curadoria" / "italy_contracts_curator.json"
CANDIDATAS = RAIZ / "candidatas" / "FONTES-CANDIDATAS.json"
CARACT = RAIZ / "curadoria" / "SOURCE-CHARACTERIZATION-V1.json"
PONTE = RAIZ / "curadoria" / "BRIDGE-LEDGER-V1.json"

_ABERTAS = frozenset({F.PENDING, F.IN_PROGRESS, F.WAITING_RETRY})

# (regra, tarefa, prioridade) — a ORDEM desta tupla e a ordem da volta.
REGRAS = (
    ("DEGRADADA", F.REPAIR, 80),
    ("DEGRADADA_COLETOR", F.BUILD_CONTRACT, 75),
    ("READY_LEGACY", F.VALIDATE_ROUTE, 55),
    ("LEGACY_COLETOR", F.BUILD_CONTRACT, 50),
    ("SEM_CONTRATO", F.BUILD_CONTRACT, 45),
    ("ADIADA", F.VALIDATE_ROUTE, 40),
    ("SOCIAL_QUALIFY", F.QUALIFY, 35),
)
_ORDEM = {r[0]: i for i, r in enumerate(REGRAS)}
_TAREFA = {r[0]: (r[1], r[2]) for r in REGRAS}


def _quando(s):
    if not s:
        return None
    try:
        d = datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    except ValueError:
        return None
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def _json(p: Path, chave: str, padrao):
    if not p.exists():
        return padrao
    return json.loads(p.read_text(encoding="utf-8")).get(chave, padrao)


def tabela_do_coletor() -> dict:
    return {x["SOURCE_ID"]: x for x in _json(TABELA_DO_COLETOR, "FONTES", [])}


def candidatas_a_avancar(agora: datetime, *, estados: dict | None = None,
                         tarefas: list | None = None, contratos: dict | None = None,
                         reguas: dict | None = None, tabela: dict | None = None,
                         candidatas: list | None = None, caract: list | None = None,
                         ponte: dict | None = None) -> list[dict]:
    """[{SOURCE_ID, REGRA, TASK_TYPE, PRIORITY, MOTIVO}] pela ordem da volta.
    Nao escreve nada. Tudo e injectavel para a prova em copia e os testes."""
    estados = estados if estados is not None else LC.snapshot()
    tarefas = tarefas if tarefas is not None else F._ler()["TAREFAS"]
    if contratos is None:
        contratos = {c["SOURCE_ID"]: c for c in _json(CONTRATOS, "FONTES", [])}
    tabela = tabela if tabela is not None else tabela_do_coletor()
    if reguas is None:
        import ready_split as RS   # noqa: E402  (lido so aqui)
        livro = LC._ler_bruto()
        ev = RS._evidencias()
        reguas = {s: RS.regua_de(s, livro=livro, evidencias=ev, contratos=contratos)
                  for s, e in estados.items() if e == LC.READY_FOR_COLLECTION}

    abertas, ultima = set(), {}
    for t in tarefas:
        sid = t["SOURCE_ID"]
        if t["STATUS"] in _ABERTAS:
            abertas.add((sid, t["TASK_TYPE"]))
            abertas.add((sid, "*"))
        u = _quando(t.get("UPDATED_AT"))
        k = (sid, t["TASK_TYPE"])
        if u and (k not in ultima or u > ultima[k]):
            ultima[k] = u

    def _livre(sid: str, tipo: str) -> bool:
        if (sid, "*") in abertas:
            return False
        u = ultima.get((sid, tipo))
        return u is None or (agora - u).total_seconds() >= RETOMA_S

    import collection_gate as CG   # noqa: E402  (so a constante da D9)
    out = []

    # CUR-PRONTA / ONDA EM CURSO: um anfitriao que a coleta esta a visitar nao
    # leva canario do Curator ao mesmo tempo (a cortesia por host vale dentro de
    # um processo, nao entre dois). A fonte espera a onda acabar; nada se perde.
    import onda_em_curso as OND    # noqa: E402
    na_onda = OND.hosts_na_onda()

    def _host_de(sid):
        c = contratos.get(sid) or tabela.get(sid) or {}
        return OND._host((c.get("ACQUISITION") or {}).get("INDEX_URL")
                         or c.get("CANONICAL_ENTRY_URL") or "")

    # D29: fonte de JANELA DE CULTURA sobe na fila (ordem da volta e prioridade
    # da tarefa). So a ordem do Curator; a agenda da Collection nao e tocada.
    import janela_de_cultura as JC   # noqa: E402

    def _por(sid, regra, motivo):
        tipo, prio = _TAREFA[regra]
        if na_onda and tipo != F.QUALIFY and _host_de(sid) in na_onda:
            return
        if _livre(sid, tipo):
            jan = JC.e_janela(sid, contratos.get(sid), tabela.get(sid))
            out.append({"SOURCE_ID": sid, "REGRA": regra, "TASK_TYPE": tipo,
                        "PRIORITY": prio + (JANELA_BONUS if jan else 0),
                        "JANELA": jan,
                        "MOTIVO": ("JANELA DE CULTURA (D29) · " if jan else "") + motivo})

    for sid in sorted(estados):
        e = estados[sid]
        c = contratos.get(sid)
        if (c or {}).get("ESTADO_CATALOGO") == CG.RETIRADA_POR_DECISAO:
            continue                  # D9: retirada por decisao nao volta por maquina
        estr = ((c or {}).get("ACQUISITION") or {}).get("STRATEGY")
        if e in (LC.DEGRADED, LC.REPAIRING):
            if c:
                _por(sid, "DEGRADADA", "degradada — reparar e canariar de novo")
            elif sid in tabela and (tabela[sid].get("ACQUISITION") or {}).get("STRATEGY"):
                _por(sid, "DEGRADADA_COLETOR", "degradada pela Collection, contrato so na "
                     "tabela do coletor: importar e re-medir")
        elif e == LC.READY_FOR_COLLECTION and reguas.get(sid) not in (None, _regua_atual()):
            if estr == "YOUTUBE_CHANNEL_FEED":
                continue              # SOCIAL_LEGACY: rota do Scrap, nao o feed (ver cabecalho)
            if estr:
                _por(sid, "READY_LEGACY", "READY pela regua antiga (%s): re-medir com a de hoje"
                     % reguas.get(sid))
            elif sid in tabela and (tabela[sid].get("ACQUISITION") or {}).get("STRATEGY"):
                _por(sid, "LEGACY_COLETOR", "READY pela regua antiga, contrato so na tabela do "
                     "coletor: importar e re-medir")
        elif e == LC.CONTRACT_PENDING:
            _por(sid, "SEM_CONTRATO", "tem identidade, falta o contrato")
        elif e == LC.RETRY_AFTER and c:
            _por(sid, "ADIADA", "adiada ha mais de %d h sem tarefa aberta" % (RETOMA_S // 3600))

    # SOCIAL_QUALIFY — candidatas YouTube que a ponte nao volta a ver.
    candidatas = candidatas if candidatas is not None else _json(CANDIDATAS, "CANDIDATAS", [])
    caract = caract if caract is not None else _json(CARACT, "FONTES", [])
    ponte = ponte if ponte is not None else _json(PONTE, "PROCESSADAS", {})
    prontas = {x.get("CANDIDATE_ID") for x in caract
               if x.get("FINAL_STATE") == "ONBOARDING_READY"}
    for c in candidatas:
        cid = c["CANDIDATA_ID"]
        if (c.get("TIPO") == "YOUTUBE" and not c.get("SOURCE_ID")
                and c.get("ESTADO") == "EM_ANALISE" and cid in prontas
                and cid not in ponte and (cid, F.QUALIFY) not in ultima):
            _por(cid, "SOCIAL_QUALIFY", "canal YouTube caracterizado ONBOARDING_READY sem "
                 "SOURCE_ID: a ponte salta-o e o alimentador so ve quem tem numero")

    out.sort(key=lambda x: (not x["JANELA"], _ORDEM[x["REGRA"]], x["SOURCE_ID"]))
    return out


def _regua_atual() -> str:
    import ready_split as RS   # noqa: E402
    return RS.REGUA_CURRENT


def avancar(agora: datetime | None = None, *, limite: int = AVANCAR_POR_VOLTA,
            **kw) -> dict:
    """Poe na fila as primeiras `limite` e devolve o que fez, sempre."""
    agora = agora or datetime.now(timezone.utc)
    cands = candidatas_a_avancar(agora, **kw)
    feitas = []
    for c in cands[:limite]:
        F.enfileirar(c["SOURCE_ID"], c["TASK_TYPE"], priority=c["PRIORITY"],
                     motivo="avancar (%s): %s" % (c["REGRA"], c["MOTIVO"]))
        feitas.append({k: c[k] for k in ("SOURCE_ID", "REGRA", "TASK_TYPE")})
    por_regra = {}
    for c in cands:
        por_regra[c["REGRA"]] = por_regra.get(c["REGRA"], 0) + 1
    return {"CANDIDATAS": len(cands), "POR_REGRA": por_regra,
            "ENFILEIRADAS": feitas}


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--aplicar", action="store_true",
                    help="enfileira; sem isto so mostra (nao escreve nada)")
    a = ap.parse_args()
    agora = datetime.now(timezone.utc)
    if a.aplicar:
        print(json.dumps(avancar(agora), ensure_ascii=False, indent=1))
    else:
        cs = candidatas_a_avancar(agora)
        por = {}
        for c in cs:
            por[c["REGRA"]] = por.get(c["REGRA"], 0) + 1
        print(json.dumps({"CANDIDATAS": len(cs), "POR_REGRA": por,
                          "PRIMEIRAS": cs[:AVANCAR_POR_VOLTA]}, ensure_ascii=False, indent=1))
