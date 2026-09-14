#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O ESTADO FINAL DAS 23 — e o CSV de auditoria.

CADA UMA TERMINA EM EXATAMENTE UM ESTADO, E A SOMA FECHA EM 23
--------------------------------------------------------------
    REGISTERED_NEW      virou ficha com SOURCE_ID novo
    ALREADY_REGISTERED  ja' e' ficha em algum atlas da casa
    TRUE_DUPLICATE      a mesma rota, duas vezes, na mesma lista
    BLOCKED_IDENTITY    passaria, e NAO HA COMO DAR-LHE NUMERO
    BLOCKED_EVIDENCE    tem numero possivel e NAO TEM PROVA suficiente
    REVIEW              precisa de olho humano antes de decidir
    UNKNOWN             nao sei

QUAL CONSTRANGIMENTO SE ESCREVE QUANDO HA DOIS
----------------------------------------------
Marcar as 20 todas como BLOCKED_IDENTITY seria verdade e seria inutil: perdia
a informacao de quais delas TAMBEM falhariam por prova. Por isso escreve-se o
constrangimento que MORDE PRIMEIRO na ordem de trabalho:

    ja' registada        -> nao ha o que fazer
    prova insuficiente   -> BLOCKED_EVIDENCE, e conserta-se abrindo o arquivo
    identidade           -> BLOCKED_IDENTITY, e conserta-se reconciliando os
                            tres atlas — decisao de gente, nao de missao

Assim a lista diz o que fazer a seguir, fonte por fonte.
"""

import csv
import json
import sys
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
TRAB = Path("C:/Users/London1/AppData/Local/Temp/sintonia-promover")
SAIDA = RAIZ / "candidatas" / "ITALY-SOURCE-REGISTRATION-AUDIT-2026-09-14.csv"

DED = json.loads((TRAB / "DEDUPE.json").read_text(encoding="utf-8"))
EVI = json.loads((TRAB / "EVIDENCIA.json").read_text(encoding="utf-8"))

# ── O MOTIVO DO BLOQUEIO DE IDENTIDADE, escrito uma vez ────────────────────
PORQUE_IDENTIDADE = (
    "BLOCKED_SOURCE_ID_ASSIGNMENT. O atlas declara-se dono do SOURCE_ID, mas a "
    "populacao de IDs vive em QUATRO sitios, em TRES branches paralelas que nao "
    "se contem: atlas desta branch (42 IDs), ITALY-SOURCE-MASTER-V1.json desta "
    "mesma branch (62), atlas de italy-source-qualification-v1 (182) e atlas de "
    "passport-tags-italy-v1 (74). Uniao = 245 IDs distintos, e o atlas desta "
    "branch conhece 42 deles — 17%. A lei do know-how §119 diz «aloca-se contra "
    "a populacao inteira, nunca contra o dono declarado»; medido contra a uniao, "
    "alocar por este atlas daria numero JA EM USO em 11 dos 12 territorios. E "
    "nao ha detetor: scan_sources.py indexa por fora[SOURCE_ID], logo uma "
    "colisao SOBRESCREVE EM SILENCIO e aparece como fonte que desapareceu, nao "
    "como erro. Escrever aqui criaria um QUARTO registo divergente.")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ev = {l["INPUT_SOURCE"]: l for l in EVI["LINHAS"]}
    linhas = []
    for d in DED["DEDUPE"]:
        e = ev.get(d["INPUT_SOURCE"], {})
        grau = e.get("EVIDENCE_GRADE", "INSUFICIENTE")
        dedupe = d["DEDUPE_RESULT"]

        if dedupe == "ALREADY_REGISTERED":
            final = "ALREADY_REGISTERED"
            razao = (f"rota exata ja' e' ficha: {d['BATE_COM']}. Nao se cria "
                     "identidade nova para quem ja' tem uma — o §119 diz que o "
                     "ID, uma vez atribuido, nao e' reciclado.")
        elif grau == "INSUFICIENTE":
            final = "BLOCKED_EVIDENCE"
            razao = (f"a prova nao fecha o gate: {e.get('EVIDENCE_GRADE_PORQUE', '')} "
                     "Conserta-se abrindo o arquivo da fonte e guardando uma "
                     "edicao datada — nao depende da reconciliacao de IDs.")
        else:
            final = "BLOCKED_IDENTITY"
            razao = PORQUE_IDENTIDADE

        linhas.append({
            "INPUT_SOURCE": d["INPUT_SOURCE"],
            "OWNER": d["OWNER"],
            "URL_CANONICAL": d["URL_CANONICAL"],
            "PREVIOUS_STATUS": "READY_TO_REGISTER (missao f055fc87)",
            "DEDUPE_RESULT": dedupe,
            "DEDUPE_BATE_COM": d["BATE_COM"],
            "DEDUPE_BATE_ONDE": d["BATE_ONDE"],
            "SOURCE_ID": "",
            "SOURCE_ID_PROOF": ("nenhum atribuido — ver SOURCE_ID_STATUS"
                                if final != "ALREADY_REGISTERED"
                                else f"ja' existe: {d['BATE_COM']}"),
            "SOURCE_ID_STATUS": ("JA_TEM" if final == "ALREADY_REGISTERED"
                                 else "BLOCKED_SOURCE_ID_ASSIGNMENT"),
            "TERRITORY": d["TERRITORIES"],
            "COUNTRY": "IT",
            "SCOPE": "",
            "EXAMPLE_REAL": e.get("EXAMPLE_TITLE", ""),
            "EXAMPLE_TYPE": e.get("EXAMPLE_TYPE", ""),
            "EXAMPLE_URL": e.get("EXAMPLE_URL", ""),
            "EVIDENCE_GRADE": grau,
            "EVIDENCE_GRADE_PORQUE": e.get("EVIDENCE_GRADE_PORQUE", ""),
            "EVIDENCE_PATH": e.get("EVIDENCE_PATH", ""),
            "EVIDENCE_SHA256": e.get("SHA256", ""),
            "OBSERVED_AT": e.get("OBSERVED_AT", ""),
            "ROTA_DE_SAIDA": EVI["ROTA_DE_SAIDA"],
            "RECORRENCIA_ESTADO": d.get("RECORRENCIA_ESTADO", ""),
            "RAW_NEEDS_SUPPORTED": d.get("RAW_NEEDS_SUPPORTED", ""),
            "TOOLS_SUPPORTED": d.get("TOOLS_SUPPORTED", ""),
            "GAP_CLOSURE_VALUE": d.get("GAP_CLOSURE_VALUE", ""),
            "PRIMARY_OR_SECONDARY": d.get("PRIMARY_OR_SECONDARY", ""),
            "ATLAS_STATUS": ("FICHA EXISTE noutra branch"
                             if final == "ALREADY_REGISTERED"
                             else "NAO ESCRITA — bloqueada"),
            "DATABASE_STATUS": ("NAO ESCRITA — fonte_externa existe em migration "
                                "020 mas nao e' aplicada daqui: as credenciais "
                                "do Supabase sao segredo do GitHub Actions"),
            "FINAL_STATUS": final,
            "REASON": razao})

    cab = list(linhas[0])
    with open(SAIDA, "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cab, delimiter=";")
        w.writeheader()
        w.writerows(linhas)

    c = Counter(l["FINAL_STATUS"] for l in linhas)
    print("O ESTADO FINAL DAS 23")
    print("=" * 100)
    for l in sorted(linhas, key=lambda x: (x["FINAL_STATUS"],
                                           x["EVIDENCE_GRADE"])):
        print(f"  {l['FINAL_STATUS']:20s} {l['EVIDENCE_GRADE']:18s} "
              f"{l['INPUT_SOURCE'][:48]}")
    print("=" * 100)
    for k, v in sorted(c.items(), key=lambda x: -x[1]):
        print(f"  {k:22s} {v}")
    print(f"  {'SOMA':22s} {sum(c.values())}  "
          f"{'✓ fecha em 23' if sum(c.values()) == 23 else '✗ NAO FECHA'}")
    print()
    print("  grau de evidencia:",
          dict(Counter(l["EVIDENCE_GRADE"] for l in linhas)))
    print(f"\ngravado: {SAIDA.relative_to(RAIZ)}  ({len(linhas)} linhas, "
          f"{len(cab)} colunas)")
    if sum(c.values()) != 23:
        sys.exit(1)


if __name__ == "__main__":
    main()
