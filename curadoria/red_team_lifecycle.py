#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RED TEAM DA PROPRIA MISSAO — atacar as conclusoes antes de as entregar.

Corre sobre o livro DA CASA (leitura) e escreve so o seu proprio recibo.

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

    # 2. A interface concorda com o livro. Se divergir, um dos dois mente.
    ataque("READY da interface == READY do livro",
           sorted(r["SOURCE_ID"] for r in ready_if) == sorted(ready),
           "interface=%d livro=%d" % (len(ready_if), len(ready)))

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

    # 5. O livro bate com o ESTADO ACTUAL, nao com a fotografia: toda fonte
    #    READY no livro e executavel no registo de hoje, e nenhuma das 50
    #    YouTube esta parada pela rota velha. (Antes este ataque comparava com
    #    a missao 04 — e a missao 04 e exactamente a fotografia que envelheceu.)
    actual = json.loads((CUR / "ESTADO-ACTUAL-DAS-FONTES-V1.json")
                        .read_text(encoding="utf-8"))
    reg = {f["SOURCE_ID"]: f for f in actual["FONTES"]}
    ready_nao_exec = [s for s in ready if s in reg and not reg[s]["EXECUTAVEL"]]
    ready_sem_reg = [s for s in ready if s not in reg]
    ataque("toda READY do livro e executavel no registo actual",
           not ready_nao_exec and not ready_sem_reg,
           "nao executaveis=%s fora do registo=%s" % (ready_nao_exec, ready_sem_reg)
           if (ready_nao_exec or ready_sem_reg) else "%d/%d executaveis" % (len(ready), len(ready)))
    yt = [s for s, f in reg.items() if f.get("ADAPTER_ID") == "CANAL_PUBLICO_YOUTUBE_V1"]
    yt_parados = [s for s in yt if est.get(s) in LC.PARADOS]
    ataque("nenhuma YouTube parada pela rota velha", not yt_parados,
           "paradas=%s" % yt_parados if yt_parados else "%d YouTube, 0 em PARADOS" % len(yt))

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
