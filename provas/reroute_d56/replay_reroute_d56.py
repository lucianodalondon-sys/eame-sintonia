#!/usr/bin/env python3
"""REROUTE-D56 · replay OFFLINE do acervo versionado e do livro de decisoes com a porta D56.

SO LE. Sem rede, sem banco, sem `adm.escrever()`, sem Sala. Nao toca no livro nem no armazem.

O que le (tudo versionado nesta arvore; nada e escrito la):
  data/samples/LIVRO-DE-DECISOES.json              os julgamentos (item x universo do PEDIDO)
  data/collection-store/italy/**.html               os bytes das paginas (sha256 = pai)
  data/derivados/REGISTO-DE-ARTEFATOS.json          DERIVED-TEXT_EXTRACTION-* -> texto
  data/derivados/texto/RAW-*.txt                    o texto dos PDF
  data/collection-ledger/italy/observations.ndjson  RAW_SHA256 -> SOURCE_URL (so leitura)

`acervo()`, `doc_da_decisao()` e `item_da_porta()` vem da PORTA-DA-SALA-RENDE
(`origin/claude/porta-sala-rende-k4gunr:scripts/porta_sala_rende/replay_porta_sala_rende.py`), copiados
sem mudar a regra: o texto de uma pagina e o que a rota de producao guarda (`coleta/texto_fonte.limpar`)
+ o retrato do detector (`curadoria/retrato_html.retrato_do_html`); o item vai a porta como DOCUMENTO.

A SALA NO REPLAY: um item por DOCUMENTO (sha256 do bruto), como a Sala da D56 (dedup por documento).
    ANTES  = cada par (documento, universo do PEDIDO) que deu SIM -> uma linha nesse universo
             (a Sala de antes da D56 guardava um por par: o mesmo documento noutro pedido era outra linha)
    DEPOIS = `decidir_todas` para cada pedido que o livro fez ao documento; o documento e UM item, e as
             gavetas sao a uniao dos SIM (pedido + reroute)

    py provas/reroute_d56/replay_reroute_d56.py   -> REPLAY-REROUTE-D56.json + NOVOS-SIM-D56.json
"""
from __future__ import annotations

import collections
import hashlib
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))
import _gavetas  # noqa: E402,F401 — as gavetas do processo no caminho

import admissao as adm  # noqa: E402
from coleta.texto_fonte import limpar  # noqa: E402

AQUI = Path(__file__).resolve().parent
SAIDA = AQUI / "REPLAY-REROUTE-D56.json"
NOVOS = AQUI / "NOVOS-SIM-D56.json"


def acervo(raiz: Path = RAIZ) -> dict:
    """{sha256 do bruto: documento} — paginas HTML e textos de PDF versionados (PORTA-DA-SALA-RENDE)."""
    led = {}
    f = raiz / "data" / "collection-ledger" / "italy" / "observations.ndjson"
    if f.exists():
        for linha in f.read_text(encoding="utf-8").splitlines():
            if linha.strip():
                o = json.loads(linha)
                if o.get("RAW_SHA256"):
                    led[o["RAW_SHA256"]] = o
    docs = {}
    rh = adm._da_curadoria("retrato_html")
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


def doc_da_decisao(d: dict, docs: dict, por_artefato: dict):
    """O documento de uma decisao: pelo ARTIFACT_ID (PDF) ou pelo sha256 do pai (HTML)."""
    if d.get("item") in por_artefato:
        return por_artefato[d["item"]]
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


def _territorio(sid: str):
    p = str(sid or "").split("-")
    return p[1] if len(p) >= 3 and p[1].startswith("T") else None


def _por_gaveta(itens: dict) -> dict:
    c = collections.Counter()
    for g in itens.values():
        c.update(g)
    return {u: c[u] for u in sorted(c, key=adm._ordem_no_atlas)}


def _julgar(docs_e_pedidos: dict, docs: dict) -> tuple:
    """{sha: [pedidos]} -> (antes {sha: set}, depois {sha: set}, detalhes dos novos SIM, contagens)."""
    antes, depois, novos = {}, {}, []
    reroute = collections.defaultdict(collections.Counter)
    parou = collections.Counter()
    apertos = collections.Counter()
    so_por_reroute = 0
    for sha, pedidos in sorted(docs_e_pedidos.items()):
        x = docs[sha]
        a, dep = set(), set()
        detalhe = {}
        for pedido in sorted(pedidos, key=adm._ordem_no_atlas):
            item = item_da_porta(x, "replay:%s" % sha[:16])
            ds = adm.decidir_todas(item, pedido, corrida="REPLAY-D56")
            if ds[0].resultado == adm.SIM:
                a.add(pedido)
            if ds[0].regra != adm.REGRA_DA_PERTENCA:
                parou[ds[0].regra] += 1
            p = adm.principal(ds)
            for g in adm.gavetas_para_a_sala(ds):
                dep.add(g["UNIVERSO"])
            for d in ds[1:]:
                reroute[d.universo][d.resultado] += 1
                for aperto in ("REROUTE_REGUA_SEM_MEDIDA", "T9_SEM_CONCORRENTE_NOMEADO",
                               "CORPO_NAO_SEPARAVEL", "SEM_TRECHO"):
                    if d.motivo.startswith(aperto):
                        apertos["%s|%s" % (aperto, d.universo)] += 1
            for d in ds:
                if d.resultado == adm.SIM and d.universo not in detalhe:
                    detalhe[d.universo] = d
            if p is not None and p is not ds[0]:
                so_por_reroute += 1
        antes[sha], depois[sha] = a, dep
        for u in sorted(dep - a, key=adm._ordem_no_atlas):
            d = detalhe[u]
            ev = d.evidencia or {}
            novos.append({"SHA256": sha, "SOURCE_ID": x["sid"], "KIND": x["kind"],
                          "URL_OU_FICHEIRO": x.get("url") or x["file"],
                          "PEDIDOS_DO_LIVRO": sorted(pedidos, key=adm._ordem_no_atlas),
                          "UNIVERSO": u, "PONTUACAO": adm.pontuacao(d),
                          "PALAVRAS": ev.get("palavras"), "ANCORAS": ev.get("ancoras"),
                          "CONCORRENTES": ev.get("concorrentes"),
                          "TEXTO_JULGADO": ev.get("texto_julgado"),
                          "MOTIVO": d.motivo[:300], "TRECHOS": ev.get("trechos")})
    return antes, depois, novos, {"REROUTE_POR_UNIVERSO": {u: dict(reroute[u]) for u in
                                                             sorted(reroute, key=adm._ordem_no_atlas)},
                                  "PEDIDO_PAROU_NUM_PORTAO": dict(parou),
                                  "APERTOS_DO_REROUTE": dict(sorted(apertos.items())),
                                  "PEDIDOS_QUE_SO_ENTRAM_POR_REROUTE": so_por_reroute}


def _resumo(antes: dict, depois: dict) -> dict:
    linhas_antes = sum(len(v) for v in antes.values())
    return {"ANTES": {"LINHAS_NA_SALA": linhas_antes,
                      "DOCUMENTOS_DISTINTOS": sum(1 for v in antes.values() if v),
                      "POR_UNIVERSO": _por_gaveta(antes)},
            "DEPOIS": {"ITENS_NA_SALA": sum(1 for v in depois.values() if v),
                       "GAVETAS": sum(len(v) for v in depois.values()),
                       "ITENS_COM_MAIS_DE_UMA_GAVETA": sum(1 for v in depois.values() if len(v) > 1),
                       "POR_GAVETA": _por_gaveta(depois)},
            "SIM_PERDIDOS": sorted("%s|%s" % (s[:16], u) for s in antes for u in antes[s] - depois[s])}


def replay(livro: dict | None = None, docs: dict | None = None) -> dict:
    livro = livro or json.loads((RAIZ / "data" / "samples" / "LIVRO-DE-DECISOES.json")
                                .read_text(encoding="utf-8"))
    docs = docs if docs is not None else acervo()
    por_artefato = {x["artifact"]: x for x in docs.values() if x.get("artifact")}
    pedidos_do_livro = collections.defaultdict(set)
    sem_texto = 0
    for d in livro["DECISOES"]:
        x = doc_da_decisao(d, docs, por_artefato)
        if x is None:
            sem_texto += 1
            continue
        pedidos_do_livro[x["sha"]].add(d["universo"])

    a, dep, novos, extra = _julgar(pedidos_do_livro, docs)
    # hipotese: o acervo inteiro, cada documento pedido pelo territorio da SUA fonte
    todos = {s: {_territorio(x["sid"])} for s, x in docs.items() if _territorio(x["sid"])}
    ha, hd, hnovos, hextra = _julgar(todos, docs)
    return {
        "DATASET": "REPLAY-REROUTE-D56-V1",
        "SO_LEITURA": True, "VERSAO_DA_REGRA": adm.VERSAO_DA_REGRA,
        "VERSAO_DO_REROUTE": adm.VERSAO_DO_REROUTE,
        "REROUTE_ENTRA_NA_SALA": adm.REROUTE_ENTRA_NA_SALA,
        "LIVRO": {"DECISOES": len(livro["DECISOES"]), "SEM_TEXTO_NO_REPO": sem_texto,
                  "DOCUMENTOS_COM_TEXTO": len(pedidos_do_livro),
                  "PARES_DOCUMENTO_PEDIDO": sum(len(v) for v in pedidos_do_livro.values()),
                  "SALA": _resumo(a, dep), **extra, "NOVOS_SIM": len(novos)},
        "ACERVO_INTEIRO_HIPOTESE": {
            "PERGUNTA": ("cada documento versionado pedido pelo territorio da SUA fonte (IT-T7-... -> T7), "
                         "e reencaminhado pela D56. NAO e o que o livro fez; e o tamanho da materia."),
            "DOCUMENTOS": len(todos), "SALA": _resumo(ha, hd), **hextra, "NOVOS_SIM": len(hnovos)},
    }, novos, hnovos


def main():
    r, novos, hnovos = replay()
    SAIDA.write_text(json.dumps(r, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    NOVOS.write_text(json.dumps({"DO_LIVRO": novos, "DO_ACERVO_INTEIRO": hnovos},
                                ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({k: r[k]["SALA"] for k in ("LIVRO", "ACERVO_INTEIRO_HIPOTESE")},
                     ensure_ascii=False, indent=1))
    print("novos SIM: livro %d · acervo %d" % (len(novos), len(hnovos)))


if __name__ == "__main__":
    main()
