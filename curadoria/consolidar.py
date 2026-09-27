#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Consolida os lotes num so artefato de PROPOSTA, e mede o funil do Curator.

    ISTO NAO TOCA A REDE E NAO ESCREVE NA FILA.

Le as fichas de REAL_EXAMPLE ja capturadas, reaplica `classificar()` e produz:

    curadoria/SOURCE-CURATOR-DECISIONS-V1.json   a proposta
    curadoria/REAL-EXAMPLE-INDEX-V1.json         a evidencia
    curadoria/FUNIL-DO-CURATOR-V1.json           a telemetria do proprio Bot

Reclassificar a partir das fichas (em vez de guardar a decisao de cada lote)
garante que os 172 passam pela MESMA versao da regra — os lotes correram com
o codigo a ser corrigido pelo meio, e uma proposta com duas reguas dentro nao
e auditavel.
"""
from __future__ import annotations

import json
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))
import capturador as CAP      # noqa: E402
import correr_lote as L       # noqa: E402

LOTES = ["_lote_youtube.json", "_lote_facebook.json", "_lote_html.json"]


def main() -> int:
    fichas = {}
    for nome in LOTES:
        p = RAIZ / "curadoria" / nome
        for f in json.loads(p.read_text(encoding="utf-8"))["FICHAS"]:
            fichas[f["CANDIDATE_ID"]] = f

    fila = json.loads(L.do_git(L.FILA))["CANDIDATAS"]
    porid = {c["CANDIDATA_ID"]: c for c in fila}
    atlas = json.loads(L.do_git(L.ATLAS_DERIVADO))["SOURCES"]
    atlas = list(atlas.values()) if isinstance(atlas, dict) else atlas

    PLATAFORMAS = {"youtube.com", "youtu.be", "facebook.com",
                   "linkedin.com", "instagram.com", "twitter.com", "x.com"}
    por_dominio, por_canal = {}, {}
    for s in atlas:
        d = CAP.dominio(s.get("url"))
        if not d:
            continue
        if d in PLATAFORMAS:
            k = L.chave_social(s.get("url"))
            if k:
                por_canal[k] = s["source_id"]
        elif d not in CAP.POLICY_BLOCKED:
            por_dominio.setdefault(d, s["source_id"])
    exatos = {L.normalizar(s.get("url")) for s in atlas}

    decisoes = []
    conta, por_fam, falhas = Counter(), defaultdict(Counter), Counter()
    yield_por_fam = defaultdict(Counter)

    for cid, f in fichas.items():
        c = porid[cid]
        d = CAP.dominio(c["URL"])
        endpoint_de = None
        if d in PLATAFORMAS:
            k = L.chave_social(c["URL"])
            if k and k in por_canal:
                endpoint_de = por_canal[k]
        elif L.normalizar(c["URL"]) not in exatos and d in por_dominio:
            endpoint_de = por_dominio[d]

        dd = L.classificar(f, endpoint_de)
        est, fam = dd["PROPOSED_STATE"], f["FAMILY"]
        conta[est] += 1
        por_fam[fam][est] += 1
        conta["REAL_EXAMPLE_CAPTURED" if f["CAPTURE_RESULT"] == "CAPTURED"
              else "REAL_EXAMPLE_FAILED"] += 1
        if f["CAPTURE_FAILURE_CLASS"]:
            falhas[f["CAPTURE_FAILURE_CLASS"]] += 1
        yield_por_fam[fam][f.get("EXPECTED_YIELD_INITIAL") or "UNKNOWN"] += 1

        rf = f.get("ROUTE_FAMILY")
        onb = L.ONBOARDING.get(rf)
        decisoes.append({
            "CANDIDATE_ID": cid, "NOME": c["NOME"], "URL": c["URL"], "FAMILY": fam,
            "CURRENT_STATE": c["ESTADO"], "PROPOSED_STATE": est,
            "REASON": dd["REASON"],
            "MATCHED_SOURCE_ID": dd.get("MATCHED_SOURCE_ID"),
            "RELATION": dd.get("RELATION"), "BLOCK_KIND": dd.get("BLOCK_KIND"),
            "REAL_EXAMPLE_REF": f.get("EVIDENCE") if f["CAPTURE_RESULT"] == "CAPTURED" else None,
            "REAL_EXAMPLE_URL": f.get("REAL_EXAMPLE_URL"),
            "REAL_EXAMPLE_SHA256": f.get("REAL_EXAMPLE_SHA256"),
            "REAL_EXAMPLE_PUBLISHED_AT": f.get("REAL_EXAMPLE_PUBLISHED_AT"),
            "EXPECTED_YIELD_INITIAL": f.get("EXPECTED_YIELD_INITIAL"),
            "UPDATE_FREQUENCY_OBSERVED": f.get("UPDATE_FREQUENCY_OBSERVED"),
            "HISTORICAL_DEPTH_OBSERVED": f.get("HISTORICAL_DEPTH_OBSERVED"),
            "WHY_THIS_SOURCE_MATTERS": L.COBERTURA_POR_TIPO.get(c["TIPO"], "NAO SEI"),
            "ONBOARDING_FAMILY": rf,
            "LIKELY_ROUTE_STRATEGY": onb[0] if onb else "NAO SEI",
            "LIKELY_IDENTITY_STRATEGY": onb[1] if onb else "NAO SEI",
            "SMALL_ADAPTATION_REQUIRED": onb[2] if onb else "NAO SEI",
        })

    decisoes.sort(key=lambda x: (x["PROPOSED_STATE"], x["FAMILY"], x["CANDIDATE_ID"]))
    agora = datetime.now(timezone.utc).isoformat()
    head = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                          text=True, cwd=str(RAIZ)).stdout.strip()
    coord = subprocess.run(["git", "rev-parse", L.COORDINATOR], capture_output=True,
                           text=True, cwd=str(RAIZ)).stdout.strip()

    # ⚠️ As 69 bloqueadas por politica NAO foram tocadas e por isso NAO aparecem
    # nas decisoes. Declara-las aqui e o que impede o leitor de somar 172 + 69 e
    # achar que houve 241 tentativas.
    lk = sum(1 for c in fila if CAP.familia_de(c["URL"]) == "LINKEDIN")
    ig = sum(1 for c in fila if CAP.familia_de(c["URL"]) == "INSTAGRAM")

    saida = {
        "DATASET": "SOURCE-CURATOR-DECISIONS-V1",
        "O_QUE_ISTO_E": ("PROPOSTA de transicao. NADA foi escrito em "
                         "candidatas/FONTES-CANDIDATAS.json. Quem transiciona e "
                         "candidatas/decidir_fila_italia.py --escrever, noutra missao."),
        "NAO_E": ("nao e coleta: nao cunha RUN_ID, nao produz RAW_OBSERVATION, nao "
                  "entra no ingresso, nao toca Admission nem Sala. REAL_EXAMPLE e "
                  "evidencia SOBRE A FONTE, nao um facto."),
        "LEI": ("«nao consegui ler» != «nao serve». REJECT exige prova positiva de que "
                "a fonte nao serve — por isso REJECT = 0, e isso e o resultado correcto."),
        "GERADO_EM": agora,
        "SOURCE_CURATOR_HEAD": head,
        "FILA_LIDA_DE": "%s @ %s" % (L.COORDINATOR, coord),
        "EGRESSO_DA_CORRIDA": "205.147.30.6 · Milano, IT · AS208172 Proton AG",
        "UNIVERSO": {
            "TOTAL_CANDIDATES": len(fila),
            "AUTO_DECIDIBLE_ATTEMPTED": len(fichas),
            "POLICY_BLOCKED_LINKEDIN_UNTOUCHED": lk,
            "POLICY_BLOCKED_INSTAGRAM_UNTOUCHED": ig,
            "NOTA": ("as %d bloqueadas por politica nao receberam UM pedido de rede. "
                     "Nao estao nas decisoes abaixo." % (lk + ig)),
        },
        "TOTAIS": dict(conta),
        "POR_FAMILIA": {k: dict(v) for k, v in por_fam.items()},
        "CAPTURE_FAILURE_CLASSES": dict(falhas),
        "EXPECTED_YIELD_POR_FAMILIA": {k: dict(v) for k, v in yield_por_fam.items()},
        "DECISOES": decisoes,
    }
    (RAIZ / "curadoria" / "SOURCE-CURATOR-DECISIONS-V1.json").write_text(
        json.dumps(saida, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    (RAIZ / "curadoria" / "REAL-EXAMPLE-INDEX-V1.json").write_text(
        json.dumps({"DATASET": "REAL-EXAMPLE-INDEX-V1", "GERADO_EM": agora,
                    "O_QUE_ISTO_E": ("evidencia de qualificacao SOBRE A FONTE. "
                                     "REAL_EXAMPLE != FACT."),
                    "TOTAL": len(fichas),
                    "FICHAS": list(fichas.values())},
                   ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    funil = {
        "DATASET": "FUNIL-DO-CURATOR-V1",
        "O_QUE_ISTO_E": "a primeira medida do desempenho do proprio Source Curator.",
        "GERADO_EM": agora,
        "CANDIDATES_ATTEMPTED": len(fichas),
        "REAL_EXAMPLE_CAPTURED": conta["REAL_EXAMPLE_CAPTURED"],
        "REAL_EXAMPLE_FAILED": conta["REAL_EXAMPLE_FAILED"],
        "PROPOSED_PROMOTE": conta["PROMOTE"],
        "PROPOSED_REJECT": conta["REJECT"],
        "PROPOSED_BLOCK": conta["BLOCK"],
        "ENDPOINT_OF_EXISTING_SOURCE": conta["ENDPOINT_OF_EXISTING_SOURCE"],
        "NEEDS_REVIEW": conta["NEEDS_REVIEW"],
        "UNKNOWN": conta["UNKNOWN"],
        "POR_FAMILIA": {k: dict(v) for k, v in por_fam.items()},
        "CAPTURE_FAILURE_CLASSES": dict(falhas),
        "EXPECTED_YIELD_POR_FAMILIA": {k: dict(v) for k, v in yield_por_fam.items()},
        "LINKEDIN_UNTOUCHED": lk, "INSTAGRAM_UNTOUCHED": ig,
    }
    (RAIZ / "curadoria" / "FUNIL-DO-CURATOR-V1.json").write_text(
        json.dumps(funil, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    print("CANDIDATES_ATTEMPTED    %d" % len(fichas))
    for k in ("REAL_EXAMPLE_CAPTURED", "REAL_EXAMPLE_FAILED"):
        print("%-24s%d" % (k, conta[k]))
    print("-" * 46)
    for k in ("PROMOTE", "ENDPOINT_OF_EXISTING_SOURCE", "BLOCK",
              "NEEDS_REVIEW", "UNKNOWN", "REJECT"):
        print("%-24s%d" % (k, conta[k]))
    print("-" * 46)
    for fam, cc in sorted(por_fam.items()):
        print("%-12s %s" % (fam, dict(cc)))
    print("-" * 46)
    print("falhas: %s" % dict(falhas))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
