#!/usr/bin/env python3
"""PORTA-DA-SALA-RENDE · replay OFFLINE do livro de decisoes com a regua PROPOSTA.

SO LE. Sem rede, sem banco, sem `adm.escrever()`. Nao toca na Sala, no livro nem no
armazem. A regua ligada nao muda: a proposta corre com a chave virada SO dentro deste
processo (`com_proposta`), e volta ao que estava no fim.

O que le (tudo versionado nesta arvore):
  data/samples/LIVRO-DE-DECISOES.json              os julgamentos (item x universo)
  data/collection-store/italy/**.html               os bytes das paginas (sha256 = pai)
  data/derivados/REGISTO-DE-ARTEFATOS.json          DERIVED-TEXT_EXTRACTION-* -> texto
  data/derivados/texto/RAW-*.txt                    o texto dos PDF
  data/collection-ledger/italy/observations.ndjson  RAW_SHA256 -> SOURCE_URL

O texto de uma pagina e o que a rota de producao guarda: `coleta/texto_fonte.limpar`
(o mesmo que `coleta/executor_texto_de_html.extrair` chama) + o retrato do detector
(`curadoria/retrato_html.retrato_do_html`). O item vai a `adm.decidir` como DOCUMENTO,
com as mesmas chaves que `orquestrador.item_documental_para_a_porta` escreve.

    py scripts/porta_sala_rende/replay_porta_sala_rende.py   -> REPLAY-PORTA-SALA-RENDE-V1.json
"""
from __future__ import annotations

import collections
import contextlib
import hashlib
import json
import os
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))
import _gavetas  # noqa: E402,F401 — as gavetas do processo no caminho

import admissao as adm  # noqa: E402
from coleta.texto_fonte import limpar  # noqa: E402

AQUI = Path(__file__).resolve().parent
SAIDA = AQUI / "REPLAY-PORTA-SALA-RENDE-V1.json"
PECAS = ("MOLDURA", "NAO_COM_DOIS_SINAIS", "T8", "T12", "SECAO")
RESULTADOS = ("SIM", "NAO", "NAO_SEI", "NAO_SE_APLICA", "ERRO")
#: os universos com regua escrita hoje (+ T8/T12 da proposta)
UNIVERSOS_HOJE = ("T1", "T2", "T3", "T4", "T5", "T7", "T9", "T10")


@contextlib.contextmanager
def com_proposta(pecas=PECAS):
    """Liga a proposta SO neste processo, com as pecas pedidas; repoe no fim."""
    antes = (adm.PORTA_SALA_RENDE_LIGADA, adm.PORTA_SALA_RENDE_PECAS)
    adm.PORTA_SALA_RENDE_LIGADA = True
    adm.PORTA_SALA_RENDE_PECAS = frozenset(pecas)
    try:
        yield
    finally:
        adm.PORTA_SALA_RENDE_LIGADA, adm.PORTA_SALA_RENDE_PECAS = antes


def _retrato():
    return adm._da_curadoria("retrato_html")


def acervo(raiz: Path = RAIZ) -> dict:
    """{sha256 do bruto: documento} — paginas HTML e textos de PDF versionados."""
    led = {}
    f = raiz / "data" / "collection-ledger" / "italy" / "observations.ndjson"
    if f.exists():
        for linha in f.read_text(encoding="utf-8").splitlines():
            if linha.strip():
                o = json.loads(linha)
                if o.get("RAW_SHA256"):
                    led[o["RAW_SHA256"]] = o
    docs = {}
    rh = _retrato()
    for p in sorted((raiz / "data" / "collection-store" / "italy").rglob("*.html")):
        b = p.read_bytes()
        s = hashlib.sha256(b).hexdigest()
        docs[s] = {"sha": s, "sid": p.relative_to(raiz / "data" / "collection-store" / "italy").parts[0],
                   "kind": "html", "file": p.relative_to(raiz).as_posix(),
                   "texto": limpar(b, "text/html"), "retrato": rh.retrato_do_html(b),
                   "url": (led.get(s) or {}).get("SOURCE_URL")}
    reg = raiz / "data" / "derivados" / "REGISTO-DE-ARTEFATOS.json"
    for a in (json.loads(reg.read_text(encoding="utf-8"))["ARTEFATOS"] if reg.exists() else []):
        t = raiz / a["STORAGE_LOCATION"]
        if not t.exists() or hashlib.sha256(t.read_bytes()).hexdigest() != a["SHA256"]:
            continue                                   # so texto com o sha do registo
        locs = (a.get("NOTES") or {}).get("PARENT_STORAGE_LOCATIONS") or []
        sid = next((x.split("/italy/")[1].split("/")[0] for x in locs if "/italy/" in x), None) \
            or (led.get(a["PARENT_SHA256"]) or {}).get("SOURCE_ID") or adm.AUSENCIA
        docs[a["PARENT_SHA256"]] = {"sha": a["PARENT_SHA256"], "sid": sid, "kind": "pdf",
                                    "file": a["STORAGE_LOCATION"], "artifact": a["ARTIFACT_ID"],
                                    "texto": t.read_text(encoding="utf-8"), "retrato": None,
                                    "url": (led.get(a["PARENT_SHA256"]) or {}).get("SOURCE_URL")}
    return docs


def doc_da_decisao(d: dict, docs: dict):
    """O documento de uma decisao: pelo ARTIFACT_ID (PDF) ou pelo sha256 do pai (HTML)."""
    for x in docs.values():
        if x.get("artifact") and x["artifact"] == d.get("item"):
            return x
    pai = (((d.get("evidencia") or {}).get("portoes") or {}).get("linhagem") or {}).get("pai") or ""
    if len(pai) >= 40:
        for s, x in docs.items():
            if s.startswith(pai):
                return x
    return None


def item_da_porta(doc: dict, item_id: str) -> dict:
    """O item como `orquestrador.item_documental_para_a_porta` o monta (DOCUMENTO)."""
    it = {"id": item_id, "texto": doc["texto"], "source_id": doc["sid"],
          "artifact_type": "DERIVED", "parent_sha256": doc["sha"]}
    if doc.get("retrato"):
        it["retrato_do_detector"] = doc["retrato"]
    if doc.get("url"):
        it["url_da_pagina"] = doc["url"]
    return it


def _curto(dec) -> dict:
    ev = dec.evidencia or {}
    return {"resultado": dec.resultado, "regra": dec.regra, "motivo": dec.motivo[:300],
            "palavras": ev.get("palavras"), "achado_noutro": ev.get("achado_noutro"),
            "trechos": ev.get("trechos"), "moldura": ev.get("moldura"), "secao": ev.get("secao")}


def _causa(fora: dict) -> str:
    """Porque continua fora — o motivo da regua, reduzido a uma etiqueta."""
    m, r = fora["motivo"], fora["resultado"]
    for etiqueta in ("UM_SO_SINAL_DE_OUTRO_UNIVERSO", "SECAO_OU_LISTAGEM", "IDIOMA_NAO_SUPORTADO",
                     "SEM_LIGACAO_AGRICOLA", "SEM_CONDICAO_DO_CAMPO", "SEM_CULTURA_NOMEADA",
                     "QUARENTENA", "SEM_TRECHO"):
        if etiqueta in m:
            return etiqueta
    if fora["regra"] == "materia":
        return "CAPA_OU_QUARENTENA_DO_DETECTOR"
    if r == "NAO":
        return "NAO_COM_PROVA_DE_OUTRO_UNIVERSO"
    if "so uma palavra" in m:
        return "UM_SO_SINAL_DESTE_UNIVERSO"
    if "nao encontrei nada" in m:
        return "NENHUM_SINAL"
    return r


def tabela(linhas: list, chave: str) -> dict:
    t = collections.defaultdict(lambda: dict.fromkeys(RESULTADOS, 0))
    for l in linhas:
        t[l["universo"]][l[chave]] += 1
    return {u: {k: v for k, v in c.items() if v} for u, c in sorted(t.items())}


def replay(livro: dict | None = None, docs: dict | None = None) -> dict:
    livro = livro or json.loads((RAIZ / "data" / "samples" / "LIVRO-DE-DECISOES.json")
                                .read_text(encoding="utf-8"))
    docs = docs if docs is not None else acervo()
    decisoes = livro["DECISOES"]
    linhas, sem_texto = [], collections.Counter()
    cache = {}
    for d in decisoes:
        x = doc_da_decisao(d, docs)
        base = {"item": d["item"], "universo": d["universo"], "livro": d["resultado"],
                "livro_regra": d["regra"], "livro_versao": d.get("versao")}
        if x is None:
            sem_texto[(d["universo"], d["resultado"], d["regra"])] += 1
            linhas.append(dict(base, hoje=d["resultado"], proposta=d["resultado"],
                               com_texto=False))
            continue
        k = (x["sha"], d["universo"])
        if k not in cache:
            item = item_da_porta(x, d["item"])
            hoje = adm.decidir(item, d["universo"], corrida="REPLAY-PSR")
            with com_proposta():
                prop = adm.decidir(item, d["universo"], corrida="REPLAY-PSR")
            por_peca = {}
            for p in PECAS:
                with com_proposta((p,)):
                    por_peca[p] = adm.decidir(item, d["universo"], corrida="REPLAY-PSR").resultado
            # SO A PERGUNTA DO UNIVERSO: o efeito da regua, sem os portoes de prontidao
            # (origem, linhagem, materia) que barram antes dela
            u = d["universo"]
            so_regua = [adm._do_universo(item, u, adm._palavras_do_universo(u))[0]]
            with com_proposta():
                so_regua.append(adm._do_universo(item, u, adm._palavras_do_universo(u))[0])
            cache[k] = (x, hoje, prop, por_peca, so_regua)
        x, hoje, prop, por_peca, so_regua = cache[k]
        linhas.append(dict(base, hoje=hoje.resultado, proposta=prop.resultado, com_texto=True,
                           regua_hoje=so_regua[0], regua_proposta=so_regua[1],
                           sid=x["sid"], sha=x["sha"], kind=x["kind"], url=x.get("url"),
                           file=x["file"], por_peca=por_peca,
                           det_hoje=_curto(hoje), det_proposta=_curto(prop)))

    # ── os pares distintos (documento x universo): a Sala guarda um por par ──
    pares = {}
    for l in linhas:
        if l["com_texto"]:
            pares[(l["sha"], l["universo"])] = l
    pares = list(pares.values())
    mudam = [dict(universo=l["universo"], sid=l["sid"], url=l["url"] or l["file"],
                  livro=l["livro"], hoje=l["hoje"], proposta=l["proposta"],
                  motivo_hoje=l["det_hoje"]["motivo"],
                  pecas_que_mudam=[p for p, r in l["por_peca"].items() if r != l["hoje"]],
                  motivo_proposta=l["det_proposta"]["motivo"],
                  trechos=l["det_proposta"]["trechos"], palavras=l["det_proposta"]["palavras"],
                  moldura=l["det_proposta"]["moldura"])
             for l in pares if l["proposta"] != l["hoje"]]
    fora = collections.Counter()
    for l in pares:
        if l["proposta"] != "SIM":
            fora[(l["universo"], _causa(l["det_proposta"]))] += 1

    # ── hipotetico: cada documento perguntado a TODAS as reguas (D2 REROUTE) ──
    todas = {"HOJE": collections.Counter(), "PROPOSTA": collections.Counter()}
    docs_com_sim = {"HOJE": 0, "PROPOSTA": 0}
    for x in docs.values():
        item = item_da_porta(x, "acervo:" + x["sha"][:16])
        sims = {"HOJE": set(), "PROPOSTA": set()}
        for u in UNIVERSOS_HOJE:
            if adm.decidir(item, u, corrida="REPLAY-PSR").resultado == "SIM":
                sims["HOJE"].add(u)
        with com_proposta():
            for u in UNIVERSOS_HOJE + ("T8", "T12"):
                if adm.decidir(item, u, corrida="REPLAY-PSR").resultado == "SIM":
                    sims["PROPOSTA"].add(u)
        for k in sims:
            todas[k].update(sims[k])
            docs_com_sim[k] += bool(sims[k])

    return {
        "DATASET": "REPLAY-PORTA-SALA-RENDE-V1",
        "SO_LEITURA": True, "REGUA_LIGADA_MUDOU": False,
        "VERSAO_DA_REGRA_HOJE": adm.VERSAO_DA_REGRA,
        "LIVRO": {"DECISOES": len(decisoes), "COM_TEXTO_NO_REPO": sum(l["com_texto"] for l in linhas),
                  "SEM_TEXTO_NO_REPO": sum(sem_texto.values()),
                  "SEM_TEXTO_POR_REGRA": {"%s|%s|%s" % k: v for k, v in sorted(sem_texto.items())},
                  "PARES_DISTINTOS_COM_TEXTO": len(pares), "DOCUMENTOS_COM_TEXTO": len(docs)},
        "TABELA_JULGAMENTOS": {"LIVRO": tabela(linhas, "livro"), "HOJE_V10": tabela(linhas, "hoje"),
                               "PROPOSTA": tabela(linhas, "proposta")},
        "TABELA_PARES": {"LIVRO": tabela(pares, "livro"), "HOJE_V10": tabela(pares, "hoje"),
                         "PROPOSTA": tabela(pares, "proposta")},
        "TABELA_PARES_SO_A_REGUA_DO_UNIVERSO": {"HOJE_V10": tabela(pares, "regua_hoje"),
                                                "PROPOSTA": tabela(pares, "regua_proposta")},
        "PORTAO_QUE_PAROU_HOJE": dict(collections.Counter(
            "%s|%s" % (l["universo"], l["det_hoje"]["regra"]) for l in pares
            if l["hoje"] != "SIM")),
        "POR_PECA_PARES_QUE_MUDAM": {p: sum(1 for l in pares if l["por_peca"][p] != l["hoje"])
                                     for p in PECAS},
        "MUDAM": sorted(mudam, key=lambda m: (m["universo"], m["hoje"], m["proposta"], m["url"])),
        "CONTINUAM_FORA": {"%s|%s" % k: v for k, v in sorted(fora.items())},
        "TODAS_AS_REGUAS_HIPOTETICO": {
            "PERGUNTA": "se cada documento do acervo fosse perguntado a TODAS as reguas (D2 "
                        "REROUTE), quantos teriam SIM em pelo menos um universo? NAO e o que o "
                        "livro fez: o universo vem do pedido. E o tamanho da decisao.",
            "DOCUMENTOS": len(docs), "COM_ALGUM_SIM": docs_com_sim,
            "SIM_POR_UNIVERSO": {k: dict(sorted(v.items())) for k, v in todas.items()}},
    }


def main():
    r = replay()
    SAIDA.write_text(json.dumps(r, ensure_ascii=False, indent=1) + "\n", encoding="utf-8",
                     newline="\n")
    print(json.dumps({k: r[k] for k in ("LIVRO", "TABELA_PARES", "POR_PECA_PARES_QUE_MUDAM",
                                        "CONTINUAM_FORA", "TODAS_AS_REGUAS_HIPOTETICO")},
                     ensure_ascii=False, indent=1))
    print("mudam:", len(r["MUDAM"]))


if __name__ == "__main__":
    main()
