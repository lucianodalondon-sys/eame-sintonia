#!/usr/bin/env python3
"""
alertas.py — emite alertas so quando ha mudanca, e nunca sem OLD e NEW.

Regra da missao: "Se nao houver mudanca: nao gerar alerta." Um alerta sem
`OLD` e `NEW` recuperaveis nao e alerta, e ruido.

CONFIDENCE nao e um numero inventado. Ele diz de onde vem a certeza:
    OFFICIAL_FIELD_DIFF  duas versoes arquivadas do documento oficial diferem neste campo
    OFFICIAL_FIELD_VALUE o valor esta no documento oficial de hoje (ex. data de validade)
    DOCUMENT_HASH_DIFF   o PDF do rotulo mudou de sha256
    READING_STATE        nao e fato regulatorio: e estado da nossa leitura
"""
import argparse, datetime, json, os, sys

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dados", default="pilot-label-intelligence/demo/IT-LABEL-INTELLIGENCE.json")
    ap.add_argument("--hoje", required=True)
    ap.add_argument("--out", default="pilot-label-intelligence/demo/IT-ALERTAS.json")
    a = ap.parse_args()
    d = json.load(open(a.dados, encoding="utf-8"))
    hoje = a.hoje
    A = []

    def add(**k):
        k.setdefault("WHEN", hoje)
        A.append(k)

    for p in d["PRODUCTS"]:
        lab = p.get("LABEL", {})
        base = f'{p["REGISTRATION_ID"]} {p["PRODUCT"]}'

        # 1. mudanca real no registro oficial, campo a campo
        for e in p["REGISTRY_CHANGES"]:
            if e.get("UNSTABLE_SOURCE"):
                continue  # texto sem significado regulatorio provado: nao vira alerta
            add(TYPE={"EXPIRY_CHANGED": "REGULATORY_CHANGE",
                      "STATUS_CHANGED": "REGULATORY_CHANGE",
                      "PRODUCT_ADDED": "NEW_LABEL",
                      "PRODUCT_REMOVED": "REGULATORY_CHANGE"}.get(e["CHANGE_TYPE"], "REGULATORY_CHANGE"),
                SUBTYPE=e["CHANGE_TYPE"],
                REGISTRATION_ID=p["REGISTRATION_ID"], PRODUCT=p["PRODUCT"],
                WHAT_CHANGED=f'{e["FIELD"]} mudou no registro oficial',
                WHEN=e["OBSERVATION_WINDOW"],
                OLD=e["BEFORE"], NEW=e["AFTER"],
                SOURCE=e["SOURCE"],
                CONFIDENCE="OFFICIAL_FIELD_DIFF",
                NOTE=("janela de OBSERVACAO, nao data do fato: sabemos quando vimos, "
                      "nao quando ocorreu"))

        # 2. o documento do rotulo mudou
        if lab.get("DOCUMENT_CHANGED") is True:
            add(TYPE="NEW_VERSION", SUBTYPE="LABEL_DOCUMENT_CHANGED",
                REGISTRATION_ID=p["REGISTRATION_ID"], PRODUCT=p["PRODUCT"],
                WHAT_CHANGED="o PDF do rotulo oficial deixou de ser o mesmo documento",
                WHEN=f'{lab.get("BASELINE_CAPTURED_AT")}..{lab.get("OBSERVED_AT")}',
                OLD=f'sha256 {lab.get("BASELINE_SHA256")}',
                NEW=f'sha256 {lab.get("SHA256")}',
                SOURCE=lab.get("URL"), CONFIDENCE="DOCUMENT_HASH_DIFF",
                NOTE="hash diferente prova documento diferente, nao diz ainda O QUE mudou dentro")

        # 3. validade
        dte = p["DAYS_TO_EXPIRY"]
        if isinstance(dte, int):
            if dte < 0:
                add(TYPE="EXPIRY_PASSED", SUBTYPE="EXPIRED_BUT_STILL_LISTED_ACTIVE",
                    REGISTRATION_ID=p["REGISTRATION_ID"], PRODUCT=p["PRODUCT"],
                    WHAT_CHANGED=(f'a validade da autorizacao passou ha {-dte} dias e o registro '
                                  f'ainda lista o produto como "{p["STATUS"]}"'),
                    OLD=f'validade {p["EXPIRY"]}', NEW=f'hoje {hoje}',
                    SOURCE=p["REGISTRY_SOURCE"], CONFIDENCE="OFFICIAL_FIELD_VALUE",
                    NOTE="EXPIRY != WITHDRAWAL. Vencer nao e ser revogado; o piloto nao decide isso.")
            elif dte <= 90:
                add(TYPE="EXPIRY_APPROACHING", SUBTYPE=f"WITHIN_{90}_DAYS",
                    REGISTRATION_ID=p["REGISTRATION_ID"], PRODUCT=p["PRODUCT"],
                    WHAT_CHANGED=f'vence em {dte} dias',
                    OLD="NOT_APPLICABLE", NEW=f'validade {p["EXPIRY"]}',
                    SOURCE=p["REGISTRY_SOURCE"], CONFIDENCE="OFFICIAL_FIELD_VALUE")

    # 4. divida de leitura — declarada como estado nosso, nunca como fato do produto
    sem = [p for p in d["PRODUCTS"] if not p["USE_ROWS"]]
    fila = {
        "TYPE": "NEEDS_REVIEW", "SUBTYPE": "USE_TABLE_NOT_READ",
        "WHAT_CHANGED": "NOT_APPLICABLE — isto nao e mudanca, e estado de leitura",
        "WHEN": hoje, "OLD": "NOT_APPLICABLE", "NEW": "NOT_APPLICABLE",
        "COUNT": len(sem), "CONFIDENCE": "READING_STATE",
        "NOTE": "PARSER_FAILURE != REGULATORY_ABSENCE. Nao afirmar que o produto nao tem uso autorizado.",
        "PRODUCTS": [{"REGISTRATION_ID": p["REGISTRATION_ID"], "PRODUCT": p["PRODUCT"]} for p in sem],
    }

    from collections import Counter
    out = {
        "DATASET": "IT-ALERTAS", "BUILT_AT": hoje,
        "REGRA": "sem mudanca, sem alerta. alerta sem OLD e NEW recuperaveis nao e alerta.",
        "TEXT_ONLY_SUPPRESSED": d.get("REGISTRY_HISTORY", {}).get("CHANGE_EVENTS_TEXT_ONLY", 0),
        "ALERTS_TOTAL": len(A),
        "BY_TYPE": dict(Counter(x["TYPE"] for x in A)),
        "ALERTS": A,
        "REVIEW_QUEUE": fila,
    }
    json.dump(out, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f'  alertas {len(A)} — {out["BY_TYPE"]}', file=sys.stderr)
    print(f'  fila de revisao: {len(sem)} produtos', file=sys.stderr)
    print(f'  escrito {a.out}', file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
