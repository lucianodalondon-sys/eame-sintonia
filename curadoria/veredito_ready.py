#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O veredito final: quem chega a READY_FOR_COLLECTION, e quem nao chega porque.

    CONNECTIVITY != CHARACTERIZED != CONTRACTED != READY_FOR_COLLECTION

Quatro degraus, e cada um so se sobe com prova propria:

    CONNECTIVITY      a fonte respondeu                    (missao 02)
    CHARACTERIZED     sabe-se o que publica                (missao 03)
    CONTRACTED        existe contrato valido               (esta missao)
    READY             o contrato resolveu contra a rede    (esta missao)

⚠️ READY NAO E «TEM CONTRATO». E «O CONTRATO FOI EXECUTADO E TROUXE UM
DOCUMENTO COM IDENTIDADE». Um contrato que passa nas quatro portas de
validacao e ainda assim devolve EMPTY_LIST contra o site real nao esta
pronto — esta escrito. A diferenca entre as duas coisas e o canario.

    FONTE PRONTA != FONTE COLETADA.
    Isto entrega fontes prontas. Nao coletou nada, e nao devia.
"""
from __future__ import annotations

import json
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]


def main() -> int:
    car = json.loads((RAIZ / "curadoria" / "SOURCE-CHARACTERIZATION-V1.json")
                     .read_text(encoding="utf-8"))
    alloc = json.loads((RAIZ / "curadoria" / "SOURCE-ID-ALLOCATION-V1.json")
                       .read_text(encoding="utf-8"))
    contr = json.loads((RAIZ / "curadoria" / "italy_contracts_curator.json")
                       .read_text(encoding="utf-8"))
    val = json.loads((RAIZ / "curadoria" / "CONTRACT-VALIDATION-V1.json")
                     .read_text(encoding="utf-8"))

    canarios = {}
    for lote in ("LOTE-YOUTUBE-FEED", "LOTE-HTML-ARTIGO"):
        p = RAIZ / "curadoria" / ("CANARY-%s.json" % lote)
        if p.exists():
            for r in json.loads(p.read_text(encoding="utf-8"))["RESULTADOS"]:
                canarios[r["SOURCE_ID"]] = r

    porcand = {c["CANDIDATE_ID"]: c for c in car["FONTES"]}
    porsid = {n["SOURCE_ID"]: n for n in alloc["NOVAS"]}
    contratados = {c["SOURCE_ID"]: c for c in contr["FONTES"]}
    invalidos = {f["SOURCE_ID"] for f in val["FALHAS"]}

    fontes, conta = [], Counter()
    for sid, c in contratados.items():
        n = porsid[sid]
        f = porcand[n["CANDIDATE_ID"]]
        can = canarios.get(sid)

        if sid in invalidos:
            estado, porque = "CONTRACT_INVALID", "reprovou na validacao deterministica"
        elif can is None:
            # ⚠️ NAO CORRIDO != FALHADO. Uma fonte que ninguem testou nao e uma
            # fonte que falhou — e uma fonte sem medida.
            estado, porque = "CONTRACTED_NOT_CANARIED", ("contrato valido, canario "
                                                         "nao corrido nesta missao")
        elif can["PASS"]:
            estado = "READY_FOR_COLLECTION"
            porque = ("canario resolveu e trouxe documento com identidade: %s"
                      % can.get("DOCUMENT_ID", "")[:60])
        else:
            estado = "CONTRACTED_CANARY_FAILED"
            porque = "%s — %s" % (can["CLASSE"], can.get("PORQUE", "")[:70])

        conta[estado] += 1
        fontes.append({
            "SOURCE_ID": sid,
            "CANDIDATE_ID": n["CANDIDATE_ID"],
            "NAME": c["NAME"],
            "TERRITORY": c["TERRITORY"],
            "BATCH_ID": c["BATCH_ID"],
            "STATE": estado,
            "REASON": porque,
            "CONNECTIVITY_PROVEN": "YES",
            "SOURCE_CHARACTERIZED": f["SOURCE_CHARACTERIZED"],
            "CONTRACT_VALID": "NO" if sid in invalidos else "YES",
            "CANARY": (can["CLASSE"] if can else "NOT_RUN"),
            "ACTIVITY_STATE": f["ACTIVITY"],
            "INITIAL_COLLECTION_CADENCE": f["INITIAL_COLLECTION_CADENCE"],
            "EXPECTED_ITEMS_PER_WEEK": f["EXPECTED_ITEMS_PER_WEEK"],
            "SOURCE_CONTRACT_HASH": c["SOURCE_CONTRACT_HASH"],
            "CANONICAL_EXAMPLE": f["CANONICAL_EXAMPLE"],
        })

    ready = [f for f in fontes if f["STATE"] == "READY_FOR_COLLECTION"]
    head = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                          text=True, cwd=str(RAIZ)).stdout.strip()

    saida = {
        "DATASET": "READY-FOR-COLLECTION-V1",
        "LEI": ("CONNECTIVITY != CHARACTERIZED != CONTRACTED != READY. "
                "READY exige canario que resolveu contra a rede real. "
                "FONTE PRONTA != FONTE COLETADA: nada aqui foi coletado."),
        "GERADO_EM": datetime.now(timezone.utc).isoformat(),
        "SOURCE_CURATOR_HEAD": head,
        "FUNIL": {
            "CANDIDATES_INPUT": len(car["FONTES"]),
            "ONBOARDING_READY_ENTRADA": sum(
                1 for c in car["FONTES"] if c["ONBOARDING_READY"] == "YES"),
            "SOURCE_ID_ATRIBUIDOS": alloc["ATRIBUIDOS"],
            "SEM_TERRITORIO": alloc["SEM_TERRITORIO"],
            "CONTRACTS_CREATED": len(contratados),
            "CONTRACTS_VALID": val["VALID"],
            "CONTRACTS_INVALID": val["INVALID"],
            "CANARY_ATTEMPTED": len(canarios),
            "CANARY_PASS": sum(1 for r in canarios.values() if r["PASS"]),
            "CANARY_FAIL": sum(1 for r in canarios.values() if not r["PASS"]),
            "READY_FOR_COLLECTION": len(ready),
        },
        "POR_ESTADO": dict(conta),
        "READY_POR_LOTE": dict(Counter(f["BATCH_ID"] for f in ready)),
        "READY_POR_TERRITORIO": dict(sorted(Counter(f["TERRITORY"] for f in ready).items())),
        "READY_POR_CADENCIA": dict(Counter(f["INITIAL_COLLECTION_CADENCE"] for f in ready)),
        "READY_POR_ACTIVIDADE": dict(Counter(f["ACTIVITY_STATE"] for f in ready)),
        "NAO_TOCADO": {
            "FACEBOOK_CAPABILITY_BLOCK": 14,
            "VALAGRO_SYNGENTA_SEMANTIC_REVIEW": 1,
            "NEEDS_MORE_SAMPLING": 11,
            "LINKEDIN_POLICY": 44, "INSTAGRAM_POLICY": 25,
        },
        "FONTES": fontes,
    }
    p = RAIZ / "curadoria" / "READY-FOR-COLLECTION-V1.json"
    p.write_text(json.dumps(saida, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    for k, v in saida["FUNIL"].items():
        print("%-28s%s" % (k, v))
    print("-" * 46)
    print("por estado       %s" % dict(conta))
    print("READY por lote   %s" % saida["READY_POR_LOTE"])
    print("READY cadencia   %s" % saida["READY_POR_CADENCIA"])
    print("escrito: %s" % p.relative_to(RAIZ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
