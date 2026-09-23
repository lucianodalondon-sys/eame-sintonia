#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OS CINCO BALDES DAS CANDIDATAS — onde esta, de facto, cada uma das 241.

    «AS 241 ESTAO PARADAS» E FALSO. O NUMERO HONESTO E OUTRO, E ESTE FICHEIRO
    CALCULA-O DO DISCO, SEMPRE QUE SE CORRE.

Medido na missao CANDIDATE-FEEDER-V1 (PASSO 1, read-only): a cadeia
candidata -> caracterizacao -> Atlas -> SOURCE_ID -> fila -> worker existe
inteira. O que secou foi a fila A MONTANTE, e nao por um feeder que falta:

    FONTES-CANDIDATAS.json (241)
        v  correr_lote.py + capturador.py       universo 172 (69 sociais nunca capturadas)
    SOURCE-CURATOR-DECISIONS-V1.json (172)      PROMOTE 124 . NEEDS_REVIEW 34 . BLOCK 6 . UNKNOWN 6 . ENDPOINT_OF 2
        v  amostrar.py                          FILTRA PROPOSED_STATE == PROMOTE
    SOURCE-CHARACTERIZATION-V1.json (124)       124 de 124 — nao parou a meio, foi filtro
        v  emparelhar_com_atlas.py              FILTRA ONBOARDING_READY == YES
        v  atribuir_source_id.py -> alimentar_fila.py -> supervisor -> worker

Cada candidata cai num, e so num, dos cinco baldes. A soma tem de dar o
total; se nao der, o script REPROVA (exit 2) em vez de publicar um numero.

    JA_COM_CONTRATO              tem SOURCE_ID e o SOURCE_ID tem contrato
    COM_SOURCE_ID_SEM_CONTRATO   tem SOURCE_ID, nao tem contrato
    SEM_TERRITORIO               caracterizada READY, sem territorio — NAO SEI deliberado
    CARACTERIZADAS_NAO_READY     caracterizada e nao chegou a SOURCE_ID novo
    NUNCA_CARACTERIZADAS         nunca entrou na caracterizacao

⚠️ O BALDE DOS «7 COM SOURCE_ID SEM CONTRATO» NAO E «PRONTAS A ENTRAR HOJE».
Medido no livro e na fila: as 7 ja passaram por BUILD_CONTRACT (T00023..T00029)
em 2026-09-20 e foram RECTIFICADAS para CAPABILITY_BLOCK. Tem
SMALL_ADAPTATION_REQUIRED = «SIM — ramo de indice»: a entrada nao lista os
itens, e o molde generico nunca os encontraria. `alimentar_fila.py` salta-as e
`worker.etapa_build_contract` devolve BLOCK, os dois por desenho. Enfileira-las
outra vez prova o bloqueio, nao a cadeia. Este ficheiro publica o estado delas
no livro para que ninguem volte a ler «7 prontas».

⚠️ AS «42 HTML NUNCA CARACTERIZADAS» NAO SAO 42 FONTES NOVAS. Duas sao
endpoints de fontes que ja existem (COL-LAW-205: endpoint novo de fonte
existente NAO e fonte nova). O trabalho novo honesto e 40 — e 33 dessas
esbarram na MESMA capacidade que trava as 7 («0 links com cara de item»).

O universo aqui e o desta arvore (241). A bancada source-discovery-v1 ja tem
271; ela nao entra nesta missao por ordem da coordenacao, e por isso este
ficheiro nao a le — diz-se, para o numero nao parecer a verdade inteira.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
CUR = RAIZ / "curadoria"

CANDIDATAS = RAIZ / "candidatas" / "FONTES-CANDIDATAS.json"
DECISOES = CUR / "SOURCE-CURATOR-DECISIONS-V1.json"
CARACT = CUR / "SOURCE-CHARACTERIZATION-V1.json"
MATCH = CUR / "CANDIDATE-TO-SOURCE-MATCH-V1.json"
ALLOC = CUR / "SOURCE-ID-ALLOCATION-V1.json"
CONTRATOS = CUR / "italy_contracts_curator.json"
LIVRO = CUR / "LIFECYCLE-LEDGER-V1.json"
FILA = CUR / "LIFECYCLE-QUEUE-V1.json"
SAIDA = CUR / "CANDIDATE-BUCKETS-V1.json"

# TIPO declarado na fila -> familia de rota. As sociais tem autenticacao,
# politica e robots proprios: tratar como HTML seria contornar politica.
SOCIAL = {"LINKEDIN", "INSTAGRAM", "FACEBOOK"}
HTML = {"ORGANIZACAO", "BASE_OFICIAL", "IMPRENSA", "CIENCIA"}


def _ler(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def calcular() -> dict:
    cands = _ler(CANDIDATAS)["CANDIDATAS"]
    decisoes = {d["CANDIDATE_ID"]: d for d in _ler(DECISOES)["DECISOES"]}
    caract = {f["CANDIDATE_ID"]: f for f in _ler(CARACT)["FONTES"]}
    match = _ler(MATCH)
    alloc = _ler(ALLOC)
    contratos = {c["SOURCE_ID"] for c in _ler(CONTRATOS)["FONTES"]}

    estado = {}
    for t in _ler(LIVRO)["TRANSICOES"]:
        estado[t["SOURCE_ID"]] = t["NEW_STATE"]
    tarefas = _ler(FILA)["TAREFAS"]

    sid_de = {n["CANDIDATE_ID"]: n["SOURCE_ID"] for n in alloc["NOVAS"]}
    sem_territorio = {s["CANDIDATE_ID"] for s in alloc["SEM_TERRITORIO_DETALHE"]}
    matched = {m["CANDIDATE_ID"]: m["MATCHED_SOURCE_ID"] for m in match["MATCHES"]}

    baldes = {k: [] for k in ("JA_COM_CONTRATO", "COM_SOURCE_ID_SEM_CONTRATO",
                              "SEM_TERRITORIO", "CARACTERIZADAS_NAO_READY",
                              "NUNCA_CARACTERIZADAS")}
    for c in cands:
        cid = c["CANDIDATA_ID"]
        sid = sid_de.get(cid)
        if sid and sid in contratos:
            baldes["JA_COM_CONTRATO"].append(cid)
        elif sid:
            baldes["COM_SOURCE_ID_SEM_CONTRATO"].append(cid)
        elif cid in sem_territorio:
            baldes["SEM_TERRITORIO"].append(cid)
        elif cid in caract:
            baldes["CARACTERIZADAS_NAO_READY"].append(cid)
        else:
            baldes["NUNCA_CARACTERIZADAS"].append(cid)

    por_id = {c["CANDIDATA_ID"]: c for c in cands}

    # Os 7: o que o livro e a fila dizem deles, para ninguem ler «prontas».
    sete = []
    for cid in baldes["COM_SOURCE_ID_SEM_CONTRATO"]:
        sid = sid_de[cid]
        f = caract.get(cid, {})
        sete.append({
            "CANDIDATE_ID": cid, "SOURCE_ID": sid,
            "NOME": por_id[cid]["NOME"],
            "SMALL_ADAPTATION_REQUIRED": f.get("SMALL_ADAPTATION_REQUIRED"),
            "ESTADO_NO_LIVRO": estado.get(sid),
            "TAREFAS_NA_FILA": [{"TASK_ID": t["TASK_ID"], "TASK_TYPE": t["TASK_TYPE"],
                                 "STATUS": t["STATUS"]}
                                for t in tarefas if t["SOURCE_ID"] == sid],
        })

    # As 27: porque nao chegaram a SOURCE_ID novo.
    nao_ready = Counter()
    for cid in baldes["CARACTERIZADAS_NAO_READY"]:
        if cid in matched:
            nao_ready["READY_MAS_JA_E_%s_NO_ATLAS" % matched[cid]] += 1
        else:
            nao_ready[caract[cid]["FINAL_STATE"]] += 1

    # As 117: sociais vs HTML, e o que a missao 02 ja tinha decidido delas.
    nunca = baldes["NUNCA_CARACTERIZADAS"]
    por_tipo = Counter(por_id[c]["TIPO"] for c in nunca)
    social = [c for c in nunca if por_id[c]["TIPO"] in SOCIAL]
    html = [c for c in nunca if por_id[c]["TIPO"] in HTML]
    fora = [c for c in nunca if por_id[c]["TIPO"] not in SOCIAL | HTML]

    def _classe_02(cid: str) -> str:
        d = decisoes.get(cid)
        if not d:
            return "NUNCA_CAPTURADA"
        if d["PROPOSED_STATE"] == "NEEDS_REVIEW" and d.get("HTTP_STATUS") == 403:
            return "NEEDS_REVIEW_HTTP_403"
        if d["PROPOSED_STATE"] == "NEEDS_REVIEW":
            return "NEEDS_REVIEW_SEM_ITEM_NO_INDICE"
        if d["PROPOSED_STATE"] == "UNKNOWN":
            return "UNKNOWN_%s" % d.get("CAPTURE_FAILURE_CLASS", "")
        return d["PROPOSED_STATE"]

    html_por_classe = Counter(_classe_02(c) for c in html)
    endpoints = [{"CANDIDATE_ID": c, "ENDPOINT_OF": decisoes[c].get("MATCHED_SOURCE_ID")}
                 for c in html if _classe_02(c) == "ENDPOINT_OF_EXISTING_SOURCE"]
    html_novas_ids = [c for c in html if _classe_02(c) != "ENDPOINT_OF_EXISTING_SOURCE"]
    html_novas = len(html_novas_ids)

    total = sum(len(v) for v in baldes.values())
    return {
        "DATASET": "CANDIDATE-BUCKETS-V1",
        "LEI": ("cada candidata cai num, e so num, dos cinco baldes; a soma tem de dar "
                "o total ou o script reprova. «241 paradas» e falso: o trabalho novo "
                "pelo caminho provado e o que esta em NUNCA_CARACTERIZADAS.HTML_NOVAS."),
        "GERADO_EM": datetime.now(timezone.utc).isoformat(),
        "UNIVERSO_DESTA_ARVORE": len(cands),
        "UNIVERSO_NOTA": ("source-discovery-v1 (56d037b3) ja tem 271 candidatas; nao entra "
                          "nesta missao por ordem da coordenacao, e por isso nao e lido aqui"),
        "SOMA_DOS_BALDES": total,
        "TOTAIS": {k: len(v) for k, v in baldes.items()},
        "COM_SOURCE_ID_SEM_CONTRATO_NAO_SAO_PRONTAS": {
            "PORQUE": ("as 7 ja passaram por BUILD_CONTRACT e foram rectificadas para "
                       "CAPABILITY_BLOCK: exigem «ramo de indice», que o molde generico "
                       "nao tem. Dono da capacidade: SCRAP ENGINEER."),
            "FONTES": sete,
        },
        "CARACTERIZADAS_NAO_READY_PORQUE": dict(nao_ready),
        "NUNCA_CARACTERIZADAS": {
            "PORQUE": ("amostrar.py so caracteriza PROPOSED_STATE == PROMOTE; estas nunca "
                       "foram PROMOTE na missao 02, ou nunca foram capturadas"),
            "POR_TIPO": dict(por_tipo),
            "SOCIAL": len(social),
            "SOCIAL_FORA_DO_ESCOPO": ("LinkedIn, Instagram e Facebook tem autenticacao, "
                                      "politica e robots proprios — divida registada, "
                                      "nao trabalho desta missao"),
            "HTML": len(html),
            "HTML_POR_DECISAO_DA_MISSAO_02": dict(html_por_classe),
            "HTML_ENDPOINTS_DE_FONTE_EXISTENTE": endpoints,
            "HTML_NOVAS": html_novas,
            "HTML_NOVAS_IDS": html_novas_ids,
            "HTML_NOVAS_NOTA": ("HTML menos os endpoints de fonte existente (COL-LAW-205). "
                                "As NEEDS_REVIEW_SEM_ITEM_NO_INDICE esbarram na mesma "
                                "capacidade que trava as 7."),
            "OUTROS_TIPOS": len(fora),
        },
        "POR_BALDE": baldes,
    }


def main() -> int:
    r = calcular()
    if r["SOMA_DOS_BALDES"] != r["UNIVERSO_DESTA_ARVORE"]:
        print("REPROVADO: a soma dos baldes (%d) nao da o universo (%d)"
              % (r["SOMA_DOS_BALDES"], r["UNIVERSO_DESTA_ARVORE"]))
        return 2
    if "--check" not in sys.argv:
        SAIDA.write_text(json.dumps(r, ensure_ascii=False, indent=1) + "\n",
                         encoding="utf-8")
    print("UNIVERSO_DESTA_ARVORE      %d" % r["UNIVERSO_DESTA_ARVORE"])
    for k, v in r["TOTAIS"].items():
        print("%-27s%d" % (k, v))
    n = r["NUNCA_CARACTERIZADAS"]
    print("  SOCIAL %d . HTML %d . HTML_NOVAS %d . OUTROS %d"
          % (n["SOCIAL"], n["HTML"], n["HTML_NOVAS"], n["OUTROS_TIPOS"]))
    print("  HTML por decisao 02: %s" % json.dumps(n["HTML_POR_DECISAO_DA_MISSAO_02"]))
    print("os 7 no livro: %s" % json.dumps(Counter(
        s["ESTADO_NO_LIVRO"] for s in r["COM_SOURCE_ID_SEM_CONTRATO_NAO_SAO_PRONTAS"]["FONTES"])))
    if "--check" not in sys.argv:
        print("escrito: %s" % SAIDA.relative_to(RAIZ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
