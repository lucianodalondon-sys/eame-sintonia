#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Constroi a AMOSTRA REPRESENTATIVA e caracteriza cada fonte promovivel.

    O INDICE DIZ QUANTOS E QUANDO.  O ITEM DIZ O QUE.

Amostragem adaptativa: comeca em 3, para quando o padrao estabiliza, sobe ate
10 so quando ha heterogeneidade. Fonte pequena usa o universo inteiro.

NAO baixa video nem audio. NAO usa login. NAO contorna muro. NAO escreve na
fila operacional. O `CANONICAL_EXAMPLE` da missao 02 e reaproveitado como
primeiro item da amostra — nao se repete rede sem necessidade.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))
import capturador as CAP        # noqa: E402
import caracterizador as CH     # noqa: E402
import correr_lote as L         # noqa: E402

EVID = RAIZ / "curadoria" / "evidencia"
AMOSTRAS = RAIZ / "curadoria" / "amostras"


def _item(url: str, corpo: bytes, publicado: str, titulo: str, origem: str) -> dict:
    txt = CH.texto_de(corpo)
    return {
        "ITEM_URL": url,
        "ITEM_TYPE": CAP.assinatura(corpo),
        "PUBLISHED_AT": publicado or "NAO SEI",
        "TITLE": (titulo or "NAO SEI")[:160],
        "BYTES": len(corpo),
        "TOPICS": CH.temas_de(txt),
        "GEOGRAPHIES": CH.geografias_de(txt),
        "CROPS": CH.culturas_de(txt),
        "LANGUAGE": CH.lingua_de(txt),
        "CONTENT_SIGNAL": ("texto legivel: %d caracteres" % len(txt)) if len(txt) > 400
                          else "pouco texto legivel (%d caracteres)" % len(txt),
        "EVIDENCE": origem,
    }


# ─────────────────────────────────────────────────────────────────────────
def amostrar_youtube(f: dict, cand: dict) -> dict:
    """O feed JA tem a amostra: ate 15 entradas, cada uma com data e titulo.

    ⚠️ NAO SE BAIXA VIDEO NEM AUDIO. A caracterizacao usa metadados, que e o
    que a capability autorizada entrega. E a identidade e o `channel_id`,
    nunca `youtube.com` (COL-LAW-034).
    """
    caminho = RAIZ / f["EVIDENCE"]
    if not caminho.exists():
        return {"ERRO": "amostra do feed ausente", "ITENS": []}
    xml = caminho.read_bytes()
    entradas = [e for e in CAP._entradas(xml) if e["URL"]]
    itens = []
    for e in entradas[:CH.AMOSTRA_TECTO]:
        # o "corpo" de um video e o seu metadado: titulo. Nao ha download.
        corpo = ("%s %s" % (e["TITULO"], e["TITULO"])).encode("utf-8")
        itens.append(_item(e["URL"], corpo, (e["PUBLICADO"] or "")[:10],
                           e["TITULO"], f["EVIDENCE"]))
    return {
        "ITENS": itens,
        "ITEMS_VISIBLE": len(entradas),
        "UNIVERSO_COMPLETO": len(entradas) <= CH.AMOSTRA_TECTO,
        "CHANNEL_ID": f.get("CHANNEL_ID"),
        "DATAS_DO_INDICE": [e["PUBLICADO"][:10] for e in entradas if e["PUBLICADO"]],
    }


def amostrar_facebook(f: dict, cand: dict) -> dict:
    """A superficie publica devolve UMA pagina. E o universo disponivel sem
    login — e nao se usa login. A amostra e 1, e diz-se isso."""
    caminho = RAIZ / f["EVIDENCE"]
    if not caminho.exists():
        return {"ERRO": "amostra ausente", "ITENS": []}
    corpo = caminho.read_bytes()
    txt = CH.texto_de(corpo)
    datas = CH.datas_de(txt)
    return {
        "ITENS": [_item(f["REAL_EXAMPLE_URL"], corpo,
                        f.get("REAL_EXAMPLE_PUBLISHED_AT", "NAO SEI"),
                        f.get("REAL_EXAMPLE_TITLE"), f["EVIDENCE"])],
        "ITEMS_VISIBLE": 1,
        "UNIVERSO_COMPLETO": True,
        "LIMITE": ("superficie publica sem sessao entrega UMA pagina. Nao se usou "
                   "login, nao se contornou muro: a amostra e o universo acessivel."),
        "DATAS_DO_INDICE": datas[-12:],
    }


def amostrar_html(f: dict, cand: dict, pausa: float,
                  tecto: int | None = None, permitido=None) -> dict:
    """Volta ao indice, colhe ate ao tecto, e PARA quando o padrao estabiliza.

    ⚠️ O indice serve para contar e datar; o conteudo vem dos ITENS. Misturar
    os dois foi o bug da missao 02.

    `tecto` e `permitido` sao para quem chama a peca dentro do servico (o
    QUALIFY): um tecto de pedidos por site e o robots lido na hora. Sem eles,
    a peca faz o que sempre fez.
    """
    tecto = CH.AMOSTRA_TECTO if tecto is None else tecto
    if permitido and not permitido(cand["URL"]):
        return {"ERRO": "robots nao permite o indice", "ITENS": []}
    r = CAP.buscar(cand["URL"], "text/html,application/xhtml+xml,*/*;q=0.8")
    if not r["OK"]:
        return {"ERRO": "indice nao respondeu (%s)" % (r.get("FALHA")), "ITENS": []}
    indice = r["CORPO"]
    links = CAP.candidatos_a_item(indice, r["FINAL_URL"], limite=CH.AMOSTRA_TECTO * 2)
    datas_indice = CH.datas_de(CH.texto_de(indice))

    itens, vistos = [], set()

    # o CANONICAL_EXAMPLE da missao 02 entra primeiro, sem repetir rede
    canon = RAIZ / f["EVIDENCE"] if f.get("EVIDENCE") else None
    if canon and canon.exists():
        b = canon.read_bytes()
        itens.append(_item(f["REAL_EXAMPLE_URL"], b,
                           f.get("REAL_EXAMPLE_PUBLISHED_AT", "NAO SEI"),
                           f.get("REAL_EXAMPLE_TITLE"), f["EVIDENCE"]))
        vistos.add(f["REAL_EXAMPLE_URL"])

    for url in links:
        if len(itens) >= tecto:
            break
        if url in vistos:
            continue
        if permitido and not permitido(url):
            continue
        # para de pedir assim que aprendeu: o tecto e limite, nao meta
        if len(itens) >= CH.AMOSTRA_INICIAL:
            estavel, _ = CH.padrao_estavel(itens)
            if estavel == "SIM":
                break
        ri = CAP.buscar(url)
        time.sleep(pausa)
        if not ri["OK"] or ri["BYTES"] < 200:
            continue
        b = ri["CORPO"]
        vistos.add(url)
        pasta = AMOSTRAS / cand["CANDIDATA_ID"]
        pasta.mkdir(parents=True, exist_ok=True)
        nome = re.sub(r"[^A-Za-z0-9._-]+", "_",
                      (url.rsplit("/", 1)[-1] or "item"))[:70] or "item"
        (pasta / nome).write_bytes(b)
        itens.append(_item(ri["FINAL_URL"], b,
                           CAP.data_visivel(b), CAP.titulo_de(b),
                           str((pasta / nome).relative_to(RAIZ)).replace("\\", "/")))

    return {
        "ITENS": itens,
        "ITEMS_VISIBLE": len(links),
        "UNIVERSO_COMPLETO": len(links) <= len(itens),
        "DATAS_DO_INDICE": datas_indice[-15:],
    }


# ─────────────────────────────────────────────────────────────────────────
def caracterizar(f: dict, cand: dict, dec: dict, pausa: float,
                 tecto: int | None = None, permitido=None) -> dict:
    fam = f["FAMILY"]
    if fam == "YOUTUBE":
        a = amostrar_youtube(f, cand)
    elif fam == "FACEBOOK":
        a = amostrar_facebook(f, cand)
    else:
        a = amostrar_html(f, cand, pausa, tecto=tecto, permitido=permitido)

    itens = a.get("ITENS", [])
    n = len(itens)
    estavel, porque_estavel = CH.padrao_estavel(itens)

    datas_itens = [i["PUBLISHED_AT"][:10] for i in itens
                   if i["PUBLISHED_AT"] != "NAO SEI" and re.match(r"20\d\d-\d\d-\d\d", i["PUBLISHED_AT"])]
    datas = sorted(set(datas_itens) | set(a.get("DATAS_DO_INDICE", [])))
    act, porque_act = CH.actividade(datas, n)
    cad, porque_cad = CH.cadencia_inicial(act, fam)

    temas = [t for i in itens for t in i["TOPICS"] if t != "UNKNOWN"]
    geos = sorted({g for i in itens for g in i["GEOGRAPHIES"]})
    crops = sorted({c for i in itens for c in i["CROPS"]})
    langs = sorted({i["LANGUAGE"] for i in itens if i["LANGUAGE"] != "NAO SEI"})
    rel, porque_rel = CH.relevancia(list(dict.fromkeys(temas)) or ["UNKNOWN"],
                                    geos, crops, act)

    com_data = sum(1 for i in itens if i["PUBLISHED_AT"] != "NAO SEI")
    com_geo = sum(1 for i in itens if i["GEOGRAPHIES"])
    tam = [i["BYTES"] for i in itens]

    # ⚠️ A IDENTIDADE DECLARADA CONFERE COM O QUE A FONTE PUBLICA?
    # Uma captura perfeita nao acusa uma aquisicao: o endereco responde, o
    # conteudo e real, e a ficha fala de outra empresa.
    id_bate, porque_id = CH.identidade_bate(
        cand["NOME"], cand["URL"], [i["TITLE"] for i in itens])

    # EXPECTED YIELD — producao, nunca valor
    itens_semana = itens_mes = "NAO SEI"
    if len(datas) >= 3:
        try:
            ds = sorted(datetime.strptime(d, "%Y-%m-%d") for d in datas)
            span = max((ds[-1] - ds[0]).days, 1)
            por_dia = len(ds) / span
            itens_semana = round(por_dia * 7, 2)
            itens_mes = round(por_dia * 30, 2)
        except Exception:
            pass

    return {
        "CANDIDATE_ID": cand["CANDIDATA_ID"],
        "NOME": cand["NOME"],
        "URL": cand["URL"],
        "FAMILY": fam,
        "MATCHED_SOURCE_ID": dec.get("MATCHED_SOURCE_ID"),

        "CONNECTIVITY_PROVEN": "YES",
        "CANONICAL_EXAMPLE": f.get("EVIDENCE"),
        "CANONICAL_EXAMPLE_SHA256": f.get("REAL_EXAMPLE_SHA256"),

        "REPRESENTATIVE_SAMPLE_COUNT": n,
        "SAMPLE_PERIOD_START": datas[0] if datas else "NAO SEI",
        "SAMPLE_PERIOD_END": datas[-1] if datas else "NAO SEI",
        "SAMPLE_IS_FULL_AVAILABLE_UNIVERSE": a.get("UNIVERSO_COMPLETO", False),
        "SAMPLE_BUDGET_REACHED": n >= CH.AMOSTRA_TECTO,
        "SAMPLE_LIMIT_NOTE": a.get("LIMITE"),

        "CONTENT_TYPES": sorted({i["ITEM_TYPE"] for i in itens}) or ["NAO SEI"],
        "TOPICS_OBSERVED": [t for t, _ in Counter(temas).most_common(5)] or ["UNKNOWN"],
        "GEOGRAPHIES_OBSERVED": geos,
        "CROPS_OBSERVED": crops,
        "LANGUAGES_OBSERVED": langs or ["NAO SEI"],

        "DATE_PRESENT_COUNT": com_data,
        "DATE_PRESENT_RATE": round(com_data / n, 2) if n else None,
        "LOCATION_PRESENT_COUNT": com_geo,
        "LOCATION_PRESENT_RATE": round(com_geo / n, 2) if n else None,

        "ITEMS_VISIBLE": a.get("ITEMS_VISIBLE"),
        "ITEM_SIZE_RANGE": [min(tam), max(tam)] if tam else None,
        "HISTORICAL_DEPTH_OBSERVED": ("%s … %s (%d datas)" % (datas[0], datas[-1], len(datas)))
                                     if len(datas) >= 2 else "NAO SEI",

        "ACTIVITY": act, "ACTIVITY_REASON": porque_act,
        "UPDATE_PATTERN": porque_act,
        "EXPECTED_ITEMS_PER_WEEK": itens_semana,
        "EXPECTED_ITEMS_PER_MONTH": itens_mes,
        "EXPECTED_YIELD": (f.get("EXPECTED_YIELD_INITIAL") or "UNKNOWN"),
        "LAST_CONTENT_AT": datas[-1] if datas else "NAO SEI",

        "INITIAL_COLLECTION_CADENCE": cad,
        "CADENCE_REASON": porque_cad + " · sem entrada de VALOR: a Intelligence "
                          "ainda nao existe e nao opina aqui",

        "ROUTE_FAMILY": f.get("ROUTE_FAMILY"),
        "IDENTITY_FAMILY": f.get("IDENTITY_FAMILY"),
        "BROWSER_REQUIRED": f.get("BROWSER_REQUIRED"),
        "LOGIN_REQUIRED": f.get("LOGIN_REQUIRED"),
        "PAID_REQUIRED": f.get("PAID_REQUIRED"),
        "POLICY_STATUS": f.get("POLICY_STATUS"),

        "SOURCE_PATTERN_STABLE": estavel,
        "STABILITY_REASON": porque_estavel,

        "DECLARED_IDENTITY_MATCHES_CONTENT": id_bate,
        "IDENTITY_REASON": porque_id,

        "CONTENT_VALUE_TYPE": [t for t, _ in Counter(temas).most_common(3)] or ["UNKNOWN"],
        "RELEVANT_TO_SINTONIA": rel,
        "WHY_RELEVANT": porque_rel,
        "RELEVANT_TOPICS": list(dict.fromkeys(temas))[:5],
        "RELEVANT_GEOGRAPHIES": geos,

        "SAMPLE_ITEMS": itens,
        "SAMPLE_ERROR": a.get("ERRO"),
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--familia")
    ap.add_argument("--limite", type=int, default=0)
    ap.add_argument("--pausa", type=float, default=0.4)
    ap.add_argument("--saida", default="_carac.json")
    a = ap.parse_args(argv)

    D = json.loads((RAIZ / "curadoria" / "SOURCE-CURATOR-DECISIONS-V1.json")
                   .read_text(encoding="utf-8"))["DECISOES"]
    F = {x["CANDIDATE_ID"]: x for x in json.loads(
        (RAIZ / "curadoria" / "REAL-EXAMPLE-INDEX-V1.json").read_text(encoding="utf-8"))["FICHAS"]}
    fila = {c["CANDIDATA_ID"]: c for c in json.loads(L.do_git(L.FILA))["CANDIDATAS"]}

    alvo = [d for d in D if d["PROPOSED_STATE"] == "PROMOTE"]
    if a.familia:
        alvo = [d for d in alvo if d["FAMILY"] == a.familia]
    if a.limite:
        alvo = alvo[:a.limite]

    print("TARGET %d" % len(alvo))
    saida = []
    for i, dec in enumerate(alvo, 1):
        cid = dec["CANDIDATE_ID"]
        c = CH_ = caracterizar(F[cid], fila[cid], dec, a.pausa)
        saida.append(c)
        print("[%3d/%3d] %-11s %-10s n=%-2d %-22s %-8s %s"
              % (i, len(alvo), cid, c["FAMILY"], c["REPRESENTATIVE_SAMPLE_COUNT"],
                 c["ACTIVITY"], c["SOURCE_PATTERN_STABLE"], c["RELEVANT_TO_SINTONIA"]))

    p = RAIZ / "curadoria" / a.saida
    p.write_text(json.dumps(saida, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("escrito: %s (%d)" % (p.name, len(saida)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
