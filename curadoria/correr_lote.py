#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CORRER O CAPTURADOR SOBRE A FILA, EM LOTES — e propor (nunca escrever) transicoes.

    ESTE FICHEIRO NAO PROMOVE NADA.

Ele le a fila, captura, classifica e grava uma PROPOSTA num ficheiro proprio.
`candidatas/FONTES-CANDIDATAS.json` NAO e aberto para escrita em lado nenhum
deste modulo — quem transiciona e `candidatas/decidir_fila_italia.py --escrever`,
e isso e uma missao a seguir.

    CAPTURAR != QUALIFICAR != PROMOVER.

A FILA E LIDA DA ARVORE DO COORDINATOR, POR `git show`
-------------------------------------------------------
A branch do Source Curator esta 12 commits atras do COORDINATOR. Ler a copia
local da fila daria uma fotografia velha sem avisar. Le-se a ref do COORDINATOR
directamente, sem checkout e sem tocar na worktree dele.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))
import capturador as CAP  # noqa: E402

COORDINATOR = "claude/contract-provenance-cutover-v1"
FILA = "candidatas/FONTES-CANDIDATAS.json"
ATLAS_DERIVADO = "system-map/data/sources.generated.json"

SAIDA = RAIZ / "curadoria" / "SOURCE-CURATOR-DECISIONS-V1.json"
INDICE = RAIZ / "curadoria" / "REAL-EXAMPLE-INDEX-V1.json"


def do_git(path: str, ref: str = COORDINATOR) -> str:
    return subprocess.run(["git", "show", "%s:%s" % (ref, path)],
                          capture_output=True, text=True, encoding="utf-8",
                          cwd=str(RAIZ)).stdout


# ─────────────────────────────────────────────────────────────────────────
# COBERTURA — de onde vem, e por que nao e opiniao
# ─────────────────────────────────────────────────────────────────────────
# ⚠️ WHY_THIS_SOURCE_MATTERS sai do TIPO que a propria fila declarou e do
# territorio do Atlas — nunca de um juizo escrito agora. E cobertura, NAO valor:
# valor para a Intelligence mede-se depois do gasto, e nao existe aqui.
COBERTURA_POR_TIPO = {
    "BASE_OFICIAL": "regulatory / official-data",
    "CIENCIA":      "science",
    "IMPRENSA":     "market / sector-communication",
    "ORGANIZACAO":  "sector-organization / technical-guidance",
    "YOUTUBE":      "competitor-and-sector communication (video)",
    "FACEBOOK":     "competitor-and-sector communication (social)",
    "LINKEDIN":     "competitor-and-sector communication (social)",
    "INSTAGRAM":    "competitor-and-sector communication (social)",
}

# Estrategia provavel de onboarding por familia de rota observada. NAO cria
# contrato: diz a proxima missao por onde comecar, em lote.
ONBOARDING = {
    "PDF_DIRECT":         ("PREDICTABLE_ROUTE", "URL_ESTAVEL", "NAO"),
    "PDF_DISCOVERY_PAGE": ("DISCOVERED_ROUTE", "URL_DO_ITEM", "SIM — ramo de indice"),
    "HTML_PUBLIC":        ("STATIC_ROUTE", "URL_DO_ITEM", "NAO"),
    "STATIC_ENDPOINT":    ("STATIC_ROUTE", "URL_ESTAVEL", "NAO"),
    "YOUTUBE_FEED":       ("APPLICATION_ROUTE", "CHANNEL_ID+VIDEO_ID",
                           "NAO — capacidade YouTube ja existe em T9"),
    "FACEBOOK_PUBLIC_SURFACE": ("BROWSER_DISCOVERED_ROUTE", "PAGE_HANDLE",
                                "SIM — exige navegador"),
}


def classificar(f: dict, endpoint_de: str | None) -> dict:
    """A DECISAO PROPOSTA. Cinco estados, e cada «nao» tem de ser provado.

    ⚠️ A regra que governa tudo aqui:
        «NAO CONSEGUI LER»  !=  «NAO SERVE».
    Nenhum caminho deste codigo devolve REJECT por falha de leitura. REJECT
    exige prova positiva de que a fonte nao serve — e nesta corrida nenhuma
    evidencia dessas foi produzida, por isso REJECT fica em zero e isso e o
    resultado correcto, nao uma omissao.
    """
    r, falha = f["CAPTURE_RESULT"], f["CAPTURE_FAILURE_CLASS"]

    # COL-LAW-205: endpoint novo de fonte existente NAO e fonte nova.
    if endpoint_de:
        return {"PROPOSED_STATE": "ENDPOINT_OF_EXISTING_SOURCE",
                "MATCHED_SOURCE_ID": endpoint_de, "RELATION": "ENDPOINT_OF",
                "REASON": ("mesmo dominio de %s ja no Atlas, endereco diferente. "
                           "COL-LAW-205: a fonte e estavel, o endpoint e substituivel. "
                           "Propor DERIVA_DE na ficha existente, nunca SOURCE_ID novo."
                           % endpoint_de)}

    if falha == "POLICY":
        return {"PROPOSED_STATE": "BLOCK", "BLOCK_KIND": "POLICY",
                "REASON": f["EVIDENCE"]}

    if r == "CAPTURED":
        tem_item = f["REAL_EXAMPLE_URL"] != "NAO SEI" and f["REAL_EXAMPLE_BYTES"]
        tem_sha = len(str(f["REAL_EXAMPLE_SHA256"])) == 64
        if tem_item and tem_sha:
            return {"PROPOSED_STATE": "PROMOTE",
                    "REASON": ("exemplo real capturado e preservado: %s · %s · %s bytes · "
                               "sha %s… · data visivel %s. E o degrau que o Atlas exige."
                               % (f["REAL_EXAMPLE_MEDIA_TYPE"], f["ROUTE_FAMILY"],
                                  f["REAL_EXAMPLE_BYTES"], f["REAL_EXAMPLE_SHA256"][:12],
                                  f["REAL_EXAMPLE_PUBLISHED_AT"]))}
        return {"PROPOSED_STATE": "NEEDS_REVIEW",
                "REASON": "capturou, e a ficha ficou incompleta — rever a mao"}

    if falha == "WALL":
        return {"PROPOSED_STATE": "BLOCK", "BLOCK_KIND": "CAPABILITY",
                "REASON": ("muro de login/consentimento no lugar do conteudo. "
                           "Isto e capability/policy, NAO juizo sobre a fonte. %s"
                           % f["EVIDENCE"])}

    if falha in ("DNS_OR_CONN", "TLS", "TIMEOUT"):
        return {"PROPOSED_STATE": "UNKNOWN",
                "REASON": ("nao se chegou la deste egresso (%s). BLOCKED/UNREACHABLE "
                           "!= DEAD: o egresso desta corrida foi provado vivo, mas uma "
                           "falha de transporte nao prova nada sobre a fonte. %s"
                           % (falha, f["EVIDENCE"]))}

    if falha == "HTTP_ERROR":
        return {"PROPOSED_STATE": "NEEDS_REVIEW",
                "REASON": ("o endereco da fila devolveu HTTP %s. Pode ser URL nao "
                           "canonica (BAD_URL) e a entidade existir noutro endereco. "
                           "Nunca converter isto em recusa." % f["HTTP_STATUS"])}

    if falha in ("NO_ITEM_FOUND", "EMPTY_BODY"):
        return {"PROPOSED_STATE": "NEEDS_REVIEW",
                "REASON": ("a entrada respondeu e nao se achou item proprio "
                           "(%s links com cara de item). Candidato a rota de "
                           "navegador ou a indice noutro caminho. %s"
                           % (f.get("ITEMS_OBSERVED_IN_INDEX"), f["EVIDENCE"]))}

    return {"PROPOSED_STATE": "UNKNOWN", "REASON": f["EVIDENCE"]}


def normalizar(u: str) -> str:
    import re
    u = (u or "").strip().lower().rstrip("/")
    u = re.sub(r"^https?://", "", u)
    u = re.sub(r"^www\.", "", u)
    return re.sub(r"^[a-z]{2}\.linkedin", "linkedin", u)


def chave_social(url: str) -> tuple | None:
    """IDENTIDADE NUMA PLATAFORMA = ANFITRIAO + HANDLE, nunca so o anfitriao.

    COL-LAW-034: `ORIGIN_ID != CHANNEL_ID`. Duas organizacoes no mesmo YouTube
    sao duas fontes; o mesmo handle em dois enderecos e uma so.
    """
    import re
    n = normalizar(url)
    m = re.search(r"(?:youtube\.com/(?:@|c/|channel/|user/)|youtu\.be/"
                  r"|instagram\.com/|facebook\.com/"
                  r"|linkedin\.com/(?:company/|in/))([^/?#]+)", n)
    if not m:
        return None
    return (CAP.dominio(url), m.group(1).lower())


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Captura REAL_EXAMPLE em lotes e propoe transicoes.")
    ap.add_argument("--familia", help="so esta familia (HTML_SITE, YOUTUBE, FACEBOOK, DIRECT_PDF)")
    ap.add_argument("--limite", type=int, default=0, help="max candidatas (0 = todas)")
    ap.add_argument("--pausa", type=float, default=0.7, help="segundos entre pedidos")
    ap.add_argument("--retomar", action="store_true", help="salta as ja capturadas")
    a = ap.parse_args(argv)

    fila = json.loads(do_git(FILA))["CANDIDATAS"]
    atlas = json.loads(do_git(ATLAS_DERIVADO))["SOURCES"]
    atlas = list(atlas.values()) if isinstance(atlas, dict) else atlas

    # dominio -> SOURCE_ID, para a regra de endpoint (COL-LAW-205)
    #
    # ⚠️ PLATAFORMA NAO E DOMINIO DE FONTE, E CONFUNDI-LOS FUNDE A PLATAFORMA
    # TODA NUM DONO SO. Medido: sem esta exclusao, as 60 candidatas YouTube
    # casavam `youtube.com` contra IT-T8-001 (@agronotizietv) e saiam todas como
    # «endpoint da mesma fonte» — 60 organizacoes italianas distintas declaradas
    # o mesmo canal. E o mesmo erro que em 14/09 fundiu tres LinkedIn de tres
    # donos diferentes por todos redirigirem para /login:
    #
    #     DEDUPLICAR PELO ANFITRIAO FUNDE TODA A PLATAFORMA NUM SO DONO.
    #
    # Em plataforma, a identidade e `anfitriao + handle` (COL-LAW-034:
    # ORIGIN_ID != CHANNEL_ID), e essa comparacao ja e feita por `chave_social`.
    PLATAFORMAS = {"youtube.com", "youtu.be", "facebook.com",
                   "linkedin.com", "instagram.com", "twitter.com", "x.com"}
    por_dominio, por_canal = {}, {}
    for s in atlas:
        d = CAP.dominio(s.get("url"))
        if not d:
            continue
        if d in PLATAFORMAS:
            k = chave_social(s.get("url"))
            if k:
                por_canal[k] = s["source_id"]
        elif d not in CAP.POLICY_BLOCKED:
            por_dominio.setdefault(d, s["source_id"])
    exatos = {normalizar(s.get("url")) for s in atlas}

    feitos = {}
    if a.retomar and INDICE.exists():
        feitos = {x["CANDIDATE_ID"]: x for x in json.loads(INDICE.read_text(encoding="utf-8"))["FICHAS"]}

    alvo = []
    for c in fila:
        fam = CAP.familia_de(c["URL"])
        if a.familia and fam != a.familia:
            continue
        alvo.append((c, fam))
    if a.limite:
        alvo = alvo[:a.limite]

    print("CONTRATO       %s" % CAP.CONTRATO)
    print("FILA_LIDA_DE   %s:%s" % (COORDINATOR, FILA))
    print("CANDIDATAS     %d de %d" % (len(alvo), len(fila)))
    print("-" * 66)

    fichas, decisoes = [], []
    conta = Counter()
    por_fam = defaultdict(Counter)

    for i, (c, fam) in enumerate(alvo, 1):
        cid = c["CANDIDATA_ID"]
        if cid in feitos:
            f = feitos[cid]
        else:
            f = CAP.capturar(c)
            if f["CAPTURE_RESULT"] != "NOT_ATTEMPTED":
                time.sleep(a.pausa)          # cortesia com a fonte (COL-LAW-026)

        nu = normalizar(c["URL"])
        d = CAP.dominio(c["URL"])
        endpoint_de = None
        if d in PLATAFORMAS:
            k = chave_social(c["URL"])
            if k and k in por_canal:                  # MESMO canal, nao mesma plataforma
                endpoint_de = por_canal[k]
        elif nu not in exatos and d in por_dominio:
            endpoint_de = por_dominio[d]

        dec = classificar(f, endpoint_de)
        est = dec["PROPOSED_STATE"]
        conta[est] += 1
        por_fam[fam][est] += 1
        conta["CAPTURED" if f["CAPTURE_RESULT"] == "CAPTURED" else "NOT_CAPTURED"] += 1

        rf = f.get("ROUTE_FAMILY")
        onb = ONBOARDING.get(rf)
        decisoes.append({
            "CANDIDATE_ID": cid,
            "NOME": c["NOME"],
            "URL": c["URL"],
            "FAMILY": fam,
            "CURRENT_STATE": c["ESTADO"],
            "PROPOSED_STATE": est,
            "REASON": dec["REASON"],
            "MATCHED_SOURCE_ID": dec.get("MATCHED_SOURCE_ID"),
            "RELATION": dec.get("RELATION"),
            "BLOCK_KIND": dec.get("BLOCK_KIND"),
            "REAL_EXAMPLE_REF": f.get("EVIDENCE") if f["CAPTURE_RESULT"] == "CAPTURED" else None,
            "REAL_EXAMPLE_SHA256": f.get("REAL_EXAMPLE_SHA256"),
            "EXPECTED_YIELD_INITIAL": f.get("EXPECTED_YIELD_INITIAL"),
            "UPDATE_FREQUENCY_OBSERVED": f.get("UPDATE_FREQUENCY_OBSERVED"),
            "WHY_THIS_SOURCE_MATTERS": COBERTURA_POR_TIPO.get(c["TIPO"], "NAO SEI"),
            "ONBOARDING_FAMILY": rf,
            "LIKELY_ROUTE_STRATEGY": onb[0] if onb else "NAO SEI",
            "LIKELY_IDENTITY_STRATEGY": onb[1] if onb else "NAO SEI",
            "SMALL_ADAPTATION_REQUIRED": onb[2] if onb else "NAO SEI",
        })
        fichas.append(f)
        print("[%3d/%3d] %-11s %-12s %-26s %s"
              % (i, len(alvo), cid, fam, est, c["NOME"][:34]))

    agora = datetime.now(timezone.utc).isoformat()
    head = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                          text=True, cwd=str(RAIZ)).stdout.strip()
    coord = subprocess.run(["git", "rev-parse", COORDINATOR], capture_output=True,
                           text=True, cwd=str(RAIZ)).stdout.strip()

    cabec = {
        "DATASET": "SOURCE-CURATOR-DECISIONS-V1",
        "O_QUE_ISTO_E": ("PROPOSTA de transicao para a fila de candidatas. NADA foi "
                         "escrito em candidatas/FONTES-CANDIDATAS.json. Quem transiciona "
                         "e decidir_fila_italia.py --escrever, noutra missao."),
        "NAO_E": ("nao e coleta, nao cunha RUN_ID, nao produz RAW_OBSERVATION, "
                  "nao entra no ingresso, nao toca a Admission nem a Sala."),
        "LEI": ("«nao consegui ler» != «nao serve». REJECT exige prova positiva de "
                "que a fonte nao serve; falha de leitura vira NEEDS_REVIEW ou UNKNOWN."),
        "GERADO_EM": agora,
        "SOURCE_CURATOR_HEAD": head,
        "FILA_LIDA_DE": "%s @ %s" % (COORDINATOR, coord),
        "EGRESSO": "medido no inicio da corrida — ver relatorio",
        "TOTAIS": dict(conta),
        "POR_FAMILIA": {k: dict(v) for k, v in por_fam.items()},
        "DECISOES": decisoes,
    }
    SAIDA.write_text(json.dumps(cabec, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    INDICE.write_text(json.dumps(
        {"DATASET": "REAL-EXAMPLE-INDEX-V1", "GERADO_EM": agora,
         "O_QUE_ISTO_E": ("evidencia de qualificacao SOBRE A FONTE. REAL_EXAMPLE != FACT: "
                          "prova que a fonte entrega alguma coisa, nao o que essa coisa diz."),
         "FICHAS": fichas}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    print("-" * 66)
    for k, v in sorted(conta.items()):
        print("  %-28s %d" % (k, v))
    print("\nescrito: %s" % SAIDA.relative_to(RAIZ))
    print("escrito: %s" % INDICE.relative_to(RAIZ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
