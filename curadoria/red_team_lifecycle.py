#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RED TEAM DA PROPRIA MISSAO — atacar as conclusoes antes de as entregar.

    UM NUMERO LIMPO DEMAIS EXIGE UM CONTROLO POSITIVO.

Cada flag aqui ja apanhou defeito real nalguma missao desta casa. Um flag
levantado nao e automaticamente um blocker: investiga-se, e so depois se
chama blocker — um teste mal-chaveado inventa blockers proprios.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
CUR = RAIZ / "curadoria"
sys.path.insert(0, str(CUR))

import fila as F                      # noqa: E402
import interface_collection as IC     # noqa: E402
import lifecycle as LC                # noqa: E402
import ready_split as RS              # noqa: E402

flags: list[dict] = []


def ataque(nome: str, ok: bool, detalhe: str) -> None:
    flags.append({"ATAQUE": nome, "PASS": ok, "DETALHE": detalhe})
    print("  %-46s %s  %s" % (nome, "PASS" if ok else "FLAG", detalhe[:64]))


def main() -> int:
    est = LC.snapshot()
    ready = [s for s, e in est.items() if e == LC.READY_FOR_COLLECTION]
    ready_if = IC.ready_sources()

    # 1. Toda promocao a READY tem evidencia real, e nao um placeholder.
    sem_prova = []
    for sid in ready:
        h = [t for t in LC.historia(sid) if t["NEW_STATE"] == LC.READY_FOR_COLLECTION]
        ref = h[-1].get("EVIDENCE_REF") if h else None
        if not ref or "FALSA" in str(ref) or str(ref) in ("", "NAO SEI", "None"):
            sem_prova.append(sid)
    ataque("toda promocao READY tem EVIDENCE_REF real", not sem_prova,
           "sem prova: %s" % sem_prova if sem_prova else "%d/%d com prova"
           % (len(ready), len(ready)))

    # 2. A interface concorda com o livro — MAS NAO ENTREGA TUDO O QUE ELE TEM.
    #
    # ⚠️ ESTE ATAQUE MUDOU EM 2026-09-21. Ate aqui exigia
    # `interface == livro`, e essa igualdade ERA o defeito: entregava as 87
    # READY, 77 delas da regua antiga. O que tem de bater e o INVENTARIO
    # (todas as READY, com motivo); a ENTREGA e um subconjunto, e nenhuma
    # fonte pode estar na entrega sem estar no inventario.
    inv = IC.inventario_ready()
    entregues = {r["SOURCE_ID"] for r in ready_if}
    ataque("inventario READY == READY do livro",
           sorted(r["SOURCE_ID"] for r in inv) == sorted(ready),
           "inventario=%d livro=%d" % (len(inv), len(ready)))
    ataque("entrega e subconjunto do inventario",
           entregues <= {r["SOURCE_ID"] for r in inv},
           "entrega=%d inventario=%d" % (len(entregues), len(inv)))

    # 2b. NENHUMA fonte da regua antiga atravessou o portao.
    vazou = [r["SOURCE_ID"] for r in ready_if if r["READY_RULE"] != RS.REGUA_CURRENT]
    ataque("READY_LEGACY nao entra na Collection", not vazou,
           "vazaram: %s" % vazou if vazou else "0 de %d legacy no livro"
           % sum(1 for r in inv if r["READY_RULE"] == RS.REGUA_LEGACY))

    # 2c. Nenhuma fonte que pede olho humano atravessou.
    humanas = [r["SOURCE_ID"] for r in ready_if if r["HUMAN_REVIEW_REQUIRED"]]
    ataque("fonte com revisao humana nao entra", not humanas,
           "vazaram: %s" % humanas if humanas else "0 de %d pedidos de revisao"
           % sum(1 for r in inv if r["HUMAN_REVIEW_REQUIRED"]))

    # 2d. O portao consegue dizer «nao»? Um portao que aceita tudo nao e portao.
    #     CONTROLO POSITIVO, pela regra e nunca por uma lista de IDs.
    recusadas = [r for r in inv if not r["COLLECTION_ELIGIBLE"]]
    ataque("o portao recusa alguma coisa e diz porque",
           bool(recusadas) and all(r["ELIGIBILITY_REASON"].strip() for r in recusadas),
           "%d recusadas, todas com motivo escrito" % len(recusadas))

    # 3. CONTROLO POSITIVO: o guarda de promocao consegue dizer «nao»?
    #    Um guarda que nunca recusa nao e um guarda.
    disse_nao = False
    try:
        LC.registar("IT-CONTROLO-NEGATIVO", LC.READY_FOR_COLLECTION,
                    "fonte que nunca existiu", evidence_ref="EV-X")
    except ValueError:
        disse_nao = True
    ataque("controlo positivo: o guarda diz NAO", disse_nao,
           "promocao sem canario recusada" if disse_nao
           else "PROMOVEU uma fonte inexistente")

    # 4. Nenhuma bloqueada por robots consta como READY.
    bloq = {s for s, e in est.items() if e in LC.PARADOS}
    ataque("nenhuma bloqueada aparece em READY", not (bloq & set(ready)),
           "intersecao=%s" % sorted(bloq & set(ready)) if (bloq & set(ready))
           else "%d bloqueadas, 0 em READY" % len(bloq))

    # 5. Os numeros batem com a missao 04 (de onde o estado foi importado).
    #
    # ⚠️ O UNIVERSO PODE TER MUDADO POR DECISAO, E ENTAO O TESTE E QUE ESTA
    # DESATUALIZADO. As 50 ROUTE_BLOCKED passaram a RECONCILIATION_REQUIRED
    # porque a integracao lhes deu rota nova — comparar com o numero cru da
    # missao 04 acusaria uma reconciliacao legitima como se fosse perda.
    #
    #     UM TESTE MAL-CHAVEADO INVENTA BLOCKERS PROPRIOS.
    #
    # A conservacao que interessa e: nenhuma fonte DESAPARECEU, e nenhuma
    # saiu de bloqueada para pronta sem canario novo.
    m04 = json.loads((CUR / "READY-FOR-COLLECTION-V1.json")
                     .read_text(encoding="utf-8"))["POR_ESTADO"]
    m = LC.metricas()
    bloqueio_ou_reconciliacao = (m[LC.CONTRACT_READY_ROUTE_BLOCKED]
                                 + m[LC.RECONCILIATION_REQUIRED])
    bate = (bloqueio_ou_reconciliacao >= m04["CONTRACT_READY_ROUTE_BLOCKED"]
            and m[LC.CONTRACTED_CANARY_FAILED] <= m04["CONTRACTED_CANARY_FAILED"])
    ataque("as 50 do feed nao viraram READY sem canario novo", bate,
           "block+reconciliacao %d >= %d da missao 04 · canary_failed %d <= %d"
           % (bloqueio_ou_reconciliacao, m04["CONTRACT_READY_ROUTE_BLOCKED"],
              m[LC.CONTRACTED_CANARY_FAILED], m04["CONTRACTED_CANARY_FAILED"]))

    # 5b. Nenhuma RECONCILIATION_REQUIRED escorregou para READY.
    rec = {s for s, e in est.items() if e == LC.RECONCILIATION_REQUIRED}
    ataque("nenhuma por reconciliar aparece em READY", not (rec & set(ready)),
           "%d por reconciliar, 0 em READY" % len(rec)
           if not (rec & set(ready)) else "intersecao=%s" % sorted(rec & set(ready)))

    # 6. O lifecycle nao fabrica DOCUMENT_ID. Nesta missao e sempre NAO SEI.
    txt = (CUR / "lifecycle.py").read_text(encoding="utf-8") + \
          (CUR / "fila.py").read_text(encoding="utf-8")
    ataque("nenhum DOCUMENT_ID fabricado pelo lifecycle",
           "DOCUMENT_ID" not in txt, "o cadastro de fonte nao cunha documento")

    # 7. Nenhuma tarefa ficou presa IN_PROGRESS sem dono vivo.
    q = F.metricas()
    ataque("nenhuma tarefa orfa presa em curso", q["IN_PROGRESS"] == 0,
           "IN_PROGRESS=%d" % q["IN_PROGRESS"])

    # 8. O worker nao escreve fora da pasta do Curator (scope leak).
    wtxt = (CUR / "worker.py").read_text(encoding="utf-8")
    fugas = [p for p in ("data/collection-store", "data/collection-ledger",
                         "data/colheita", "data/raw", "RUN_ID", "RAW_OBSERVATION")
             if p in wtxt and "NAO" not in wtxt.split(p)[0][-60:].upper()]
    ataque("o worker nao toca acervo nem cunha RUN_ID", not fugas,
           "fugas=%s" % fugas if fugas else "nenhuma referencia de escrita")

    # 9. A fila tem teto — uma fonte morta nao e tentada para sempre.
    ataque("o retry tem teto observavel", F.MAX_ATTEMPTS > 0,
           "MAX_ATTEMPTS=%d" % F.MAX_ATTEMPTS)

    # 10. Metricas expoem zeros (uma categoria ausente le-se «nao se aplica»).
    mo = IC.metricas_operacionais()
    ataque("metricas mostram os zeros", all(k in mo for k in
           ("DEGRADED", "REPAIRING", "POLICY_BLOCK", "AUTH_BLOCK")),
           "%d contadores" % len(mo))

    blockers = [f for f in flags if not f["PASS"]]
    print("\nRED_TEAM_BLOCKERS = %d" % len(blockers))
    (CUR / "LIFECYCLE-RED-TEAM-V1.json").write_text(json.dumps(
        {"DATASET": "LIFECYCLE-RED-TEAM-V1", "GERADO_EM": LC.agora(),
         "ATAQUES": flags, "RED_TEAM_BLOCKERS": len(blockers)},
        ensure_ascii=False, indent=1), encoding="utf-8")
    return 0 if not blockers else 1


if __name__ == "__main__":
    raise SystemExit(main())
