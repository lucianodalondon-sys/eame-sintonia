#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BOLETIM-POR-SECAO · o GOLD-FIXTURE-PUGLIA-V1 contra o extrator (`leis/boletim_do_campo.ler_afirmacao`).

    py scripts/lugar_fato/gold_puglia.py            # imprime o placar por caso e por chave

O gold (docs/iab/puglia/GOLD-FIXTURE-PUGLIA-V1.json) traz, por ficha, o TRECHO com 400 letras de contexto e o
ESPERADO do dono. Nada aqui altera o gold nem o ESPERADO: onde o extrator falha, conserta-se o CODIGO.

DE ONDE VEM O TEXTO DE CADA FICHA (declarado, nao escolhido caso a caso):
  1. TEXTO_DERIVADO_REAL — um texto derivado RASTREADO no repo (data/derivados/texto, data/samples) onde o
     trecho aparece com o contexto do gold INTEIRO dos dois lados. E o boletim real, com as linhas dele.
     Havendo varias ocorrencias com o contexto inteiro (A.P.OL.: o mesmo paragrafo em 3 comprensori), usa-se a
     1.a — a do cabecalho que a ficha cita (CHAR_START 83/92/93, a 1.a secao).
  2. RECONSTRUIDO_DO_GOLD — o documento da ficha nao esta no repo (ARIF n.37/n.38, A.P.OL. n.10): monta-se
     CONTEXTO_ANTES + TRECHO + CONTEXTO_DEPOIS, e, quando a ficha cita um cabecalho ESCRITO no texto
     (FACT_LOCATION.EVIDENCE.CITACAO fora do trecho), essa linha vem antes, como no documento.
  O CANDIDATO_VISUAL da ficha (cabecalho so na imagem da pagina) entra como `cabecalhos_visuais` — e o
  extrator nunca o pode promover.

O TITULO DO DOCUMENTO, por publicador, lido no proprio gold (nao inventado):
  A.P.OL.   «MOSCA DELLE OLIVE»   (C02: CONTEXTO_DEPOIS «… 10 MOSCA DELLE OLIVE»; o dono: «o titulo do boletim»)
  ARIF      «Notiziario Agrometeorologico & Fitosanitario Regionale»   (C01: CONTEXTO_ANTES)
  Campania  «BOLLETTINO FITOSANITARIO DELLA PROVINCIA DI SALERNO»       (C09 SA-32: FACT_LOCATION.CITACAO)

AS CHAVES. So as que este extrator produz (lugar, praga, cultura, a fonte de cada uma, as aplicacoes
territoriais) sao comparadas. As outras do ESPERADO — CLASSE, FACT_TIME, PUBLISHED_AT, FICHA_FIEL/ERRO da
traducao, RELATION/CONTRADICTION entre fichas — sao de outros donos e ficam FORA_DESTE_EXTRATOR: nao contam
como passe nem como falha.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
GOLD = RAIZ / "docs" / "iab" / "puglia" / "GOLD-FIXTURE-PUGLIA-V1.json"
PASTAS_DE_TEXTO = ("data/derivados/texto", "data/samples")

TITULO_POR_PUBLICADOR = (
    ("A.P.OL.", "MOSCA DELLE OLIVE"),
    ("ARIF", "Notiziario Agrometeorologico & Fitosanitario Regionale"),
    ("Regione Campania", "BOLLETTINO FITOSANITARIO DELLA PROVINCIA DI SALERNO"),
)
# o nome do ESPERADO (pt / cientifico) -> o nome com que o extrator conta (a forma do vocabulario dele)
CULTURA_DO_ESPERADO = {"oliveira": "olivo"}
CHAVES_DO_EXTRATOR = ("FACT_LOCATION", "LOCATION_SOURCE", "LOCATION_EXPRESSION_RAW", "PONTO_NO_MAPA", "PEST",
                      "PESTS", "PEST_ENTITY_SOURCE", "CROP", "CROP_ENTITY_SOURCE", "ENTITY_SOURCE",
                      "APLICACOES_TERRITORIAIS", "INSTITUICOES_INDEPENDENTES")


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", str(s or "")).strip()


def _textos_rastreados() -> list:
    r = subprocess.run(["git", "ls-files", *PASTAS_DE_TEXTO], cwd=RAIZ, capture_output=True, text=True)
    if r.returncode == 0:
        return sorted(p for p in r.stdout.split() if p.endswith(".txt"))
    # copia sem .git (a prova de mutacao corre numa copia): os mesmos .txt, lidos do disco
    return sorted(str(f.relative_to(RAIZ)).replace(os.sep, "/") for d in PASTAS_DE_TEXTO
                  for f in (RAIZ / d).rglob("*.txt"))


_CACHE = {}


def _texto(p: str) -> str:
    if p not in _CACHE:
        _CACHE[p] = (RAIZ / p).read_text(encoding="utf-8", errors="replace")
    return _CACHE[p]


def titulo_do_documento(publicador: str) -> str:
    return next((t for k, t in TITULO_POR_PUBLICADOR if k in publicador), "")


def montar(ficha: dict, BC) -> dict:
    """O documento da ficha: {TEXTO, INICIO, FIM, TITULO, VISUAIS, ORIGEM}."""
    antes, trecho, depois = ficha["CONTEXTO_ANTES"], ficha["TRECHO"], ficha["CONTEXTO_DEPOIS"]
    na, nd = _norm(antes), _norm(depois)
    for p in _textos_rastreados():
        t = _texto(p)
        for i, f in BC._achar(t, trecho):
            if _norm(t[:i]).endswith(na) and _norm(t[f:]).startswith(nd):
                return {"TEXTO": t, "INICIO": i, "FIM": f, "ORIGEM": "TEXTO_DERIVADO_REAL %s" % p,
                        "TITULO": titulo_do_documento(ficha["PUBLISHER"]), "VISUAIS": _visuais(ficha)}
    ev = (ficha["FICHA_GRAVADA"].get("FACT_LOCATION") or {}).get("EVIDENCE") or {}
    cab = ev.get("CITACAO") or ""
    cab = cab if cab and cab not in antes + trecho + depois else ""
    pre = (cab + "\n") if cab else ""
    texto = pre + antes + trecho + depois
    i = len(pre) + len(antes)
    return {"TEXTO": texto, "INICIO": i, "FIM": i + len(trecho),
            "ORIGEM": "RECONSTRUIDO_DO_GOLD" + (" + cabecalho citado «%s»" % cab if cab else ""),
            "TITULO": titulo_do_documento(ficha["PUBLISHER"]), "VISUAIS": _visuais(ficha)}


def _visuais(ficha: dict) -> list:
    cv = (ficha["FICHA_GRAVADA"].get("FACT_LOCATION") or {}).get("CANDIDATO_VISUAL")
    if not cv:
        return []
    return [{"ROTULO": cv.get("ROTULO_NA_IMAGEM"), "PAGINA": cv.get("PAGINA_PDF"), "ENTIDADE": cv.get("ENTIDADE"),
             "PROVA": cv.get("PROVA")}]


def _cabeca(v) -> str:
    """«VISUAL_HEADER_CANDIDATE (+ …)» -> VISUAL_HEADER_CANDIDATE; «SPAN (pelo nome …)» -> SPAN."""
    return str(v).split(" (")[0].strip()


def _nome_da_praga(BC, v: str) -> str:
    return "UNKNOWN" if v == "UNKNOWN" else BC.nome_do_problema(v)


def comparar(caso: dict, lidas: dict, docs: dict, BC) -> dict:
    """Cada chave do ESPERADO: PASS | FAIL | FORA_DESTE_EXTRATOR | NAO_MEDIDO, com o que saiu."""
    esp = caso["ESPERADO"]
    f0 = caso["FICHAS"][0]["ASSERTION_ID"]
    a = lidas[f0]
    fora = {}
    for k, v in esp.items():
        if k not in CHAVES_DO_EXTRATOR:
            fora[k] = {"VEREDITO": "FORA_DESTE_EXTRATOR"}
            continue
        if k == "FACT_LOCATION":
            saiu = a["FACT_LOCATION"]["VALOR"]
            ok = saiu == v
        elif k == "LOCATION_SOURCE":
            saiu = a["FACT_LOCATION"]["LOCATION_SOURCE"]
            ok = saiu == _cabeca(v)
        elif k == "LOCATION_EXPRESSION_RAW":
            saiu = a["FACT_LOCATION"].get("LOCATION_EXPRESSION_RAW")
            ok = saiu == v
        elif k == "PONTO_NO_MAPA":
            saiu = a["FACT_LOCATION"]["PONTO_NO_MAPA"]
            ok = saiu == v
        elif k == "PEST":
            saiu = a["PRAGAS"]["VALOR"]
            ok = (saiu == "UNKNOWN") if v == "UNKNOWN" else saiu == [_nome_da_praga(BC, v)]
        elif k == "PESTS":
            saiu = a["PRAGAS"]["VALOR"]
            ok = isinstance(saiu, list) and sorted(saiu) == sorted(_nome_da_praga(BC, x) for x in v)
        elif k == "PEST_ENTITY_SOURCE":
            saiu = a["PRAGAS"]["ENTITY_SOURCE"]
            ok = saiu == _cabeca(v)
        elif k == "CROP":
            saiu = a["CULTURA"]["VALOR"]
            ok = saiu == [CULTURA_DO_ESPERADO.get(v, v)]
        elif k == "CROP_ENTITY_SOURCE":
            saiu = a["CULTURA"]["ENTITY_SOURCE"]
            ok = saiu in _cabeca(v).split("/")
        elif k == "ENTITY_SOURCE":
            saiu = {sid: lidas[sid]["PRAGAS"]["ENTITY_SOURCE"] for sid in v}
            ok = saiu == v
        elif k in ("APLICACOES_TERRITORIAIS", "INSTITUICOES_INDEPENDENTES"):
            d = docs[f0]
            if not d["ORIGEM"].startswith("TEXTO_DERIVADO_REAL"):
                fora[k] = {"VEREDITO": "NAO_MEDIDO",
                           "PORQUE": "o documento da ficha nao esta no repo; so o contexto de 400 letras "
                                     "(ver o teste do boletim real A.P.OL. n.9, mesmo paragrafo em 3 secoes)"}
                continue
            ap = BC.aplicacoes_territoriais(d["TEXTO"], caso["FICHAS"][0]["TRECHO"], titulo=d["TITULO"])
            saiu = ap[k]
            ok = saiu == v
        fora[k] = {"VEREDITO": "PASS" if ok else "FAIL", "ESPERADO": v, "SAIU": saiu}
    medidas = [x["VEREDITO"] for x in fora.values() if x["VEREDITO"] in ("PASS", "FAIL")]
    return {"CASO": caso["CASO"], "CHAVES": fora,
            "VEREDITO": ("NAO_MEDIDO" if not medidas else "PASS" if all(m == "PASS" for m in medidas) else "FAIL")}


def correr(BC, ler=None) -> dict:
    """O gold inteiro. `ler(doc)` -> leitura no formato de `ler_afirmacao` (por omissao, o proprio)."""
    ler = ler or (lambda d: BC.ler_afirmacao(d["TEXTO"], d["INICIO"], d["FIM"], titulo=d["TITULO"],
                                              cabecalhos_visuais=d["VISUAIS"]))
    gold = json.loads(GOLD.read_text(encoding="utf-8"))
    casos = []
    for caso in gold["CASOS"]:
        docs = {f["ASSERTION_ID"]: montar(f, BC) for f in caso["FICHAS"]}
        lidas = {sid: ler(d) for sid, d in docs.items()}
        r = comparar(caso, lidas, docs, BC)
        r["ORIGEM_DO_TEXTO"] = {sid: d["ORIGEM"] for sid, d in docs.items()}
        casos.append(r)
    chaves = [v["VEREDITO"] for c in casos for v in c["CHAVES"].values()]
    return {"GOLD_SET": gold["GOLD_SET"], "VERSAO": gold["VERSAO"], "CASOS": casos,
            "PLACAR": {"CASOS_PASS": sum(c["VEREDITO"] == "PASS" for c in casos),
                       "CASOS_FAIL": sum(c["VEREDITO"] == "FAIL" for c in casos),
                       "CASOS_NAO_MEDIDOS": sum(c["VEREDITO"] == "NAO_MEDIDO" for c in casos),
                       "CHAVES_PASS": chaves.count("PASS"), "CHAVES_FAIL": chaves.count("FAIL"),
                       "CHAVES_NAO_MEDIDAS": chaves.count("NAO_MEDIDO"),
                       "CHAVES_FORA_DESTE_EXTRATOR": chaves.count("FORA_DESTE_EXTRATOR")}}


def _bc():
    sys.path.insert(0, str(RAIZ / "leis"))
    import boletim_do_campo as BC  # noqa: PLC0415
    return BC


if __name__ == "__main__":
    r = correr(_bc())
    for c in r["CASOS"]:
        print(c["CASO"], c["VEREDITO"], {k: v["VEREDITO"] for k, v in c["CHAVES"].items()})
        for k, v in c["CHAVES"].items():
            if v["VEREDITO"] == "FAIL":
                print("   ", k, "esperado", v["ESPERADO"], "saiu", v["SAIU"])
    print(json.dumps(r["PLACAR"], ensure_ascii=False))
